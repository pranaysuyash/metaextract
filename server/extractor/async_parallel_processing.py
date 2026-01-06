"""
Async/await-based Parallel Processing Framework for MetaExtract

Replaces threading-based parallel execution with async/await pattern
to eliminate thread synchronization bottlenecks and improve performance.

Key improvements:
- Async/await pattern instead of threading
- Connection pooling for ExifTool subprocess execution
- Batch operation optimization
- Proper error handling and fallback mechanisms
- Integration with caching system
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import concurrent.futures
import subprocess
import threading
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class ExecutionModel(Enum):
    """Execution models for parallel extraction."""
    ASYNC_IO = "async_io"              # Pure async I/O
    ASYNC_WITH_POOL = "async_pool"     # Async with process pool for CPU-bound tasks
    BATCH_ASYNC = "batch_async"        # Batch processing with async


@dataclass
class AsyncExtractionTask:
    """Async extraction task configuration."""
    task_id: str
    file_path: str
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    retries: int = 0
    max_retries: int = 3
    timeout: int = 300  # seconds
    
    def __lt__(self, other: 'AsyncExtractionTask') -> bool:
        """For priority queue ordering."""
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.created_at < other.created_at


@dataclass
class AsyncExtractionResult:
    """Result of async extraction task."""
    task_id: str
    file_path: str
    success: bool
    metadata: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    cache_hit: bool = False
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


@dataclass
class AsyncParallelConfig:
    """Configuration for async parallel extraction."""
    execution_model: ExecutionModel = ExecutionModel.ASYNC_WITH_POOL
    max_concurrent_tasks: int = 10  # Max concurrent async tasks
    max_process_workers: int = 4    # Max process pool workers for CPU-bound tasks
    chunk_size: int = 10            # Tasks per batch
    enable_caching: bool = True
    enable_connection_pooling: bool = True
    exiftool_pool_size: int = 5     # ExifTool connection pool size
    timeout_per_file: int = 300     # seconds
    retry_failed: bool = True
    retry_delay: float = 1.0
    batch_optimization: bool = True


class ExifToolConnectionPool:
    """Connection pool for ExifTool subprocess execution."""
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.connections: List[subprocess.Popen] = []
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(pool_size)
        self._initialized = False
        
    async def initialize(self):
        """Initialize the connection pool."""
        if self._initialized:
            return
            
        async with self.lock:
            if self._initialized:
                return
                
            try:
                # Create ExifTool connections
                for i in range(self.pool_size):
                    conn = await self._create_connection()
                    if conn:
                        self.connections.append(conn)
                
                self._initialized = True
                logger.info(f"ExifTool connection pool initialized with {len(self.connections)} connections")
                
            except Exception as e:
                logger.error(f"Failed to initialize ExifTool connection pool: {e}")
                await self.cleanup()
                raise
    
    async def _create_connection(self) -> Optional[subprocess.Popen]:
        """Create a single ExifTool connection."""
        try:
            # Start ExifTool in server mode
            process = subprocess.Popen(
                ['exiftool', '-stay_open', 'True', '-@', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
        except Exception as e:
            logger.error(f"Failed to create ExifTool connection: {e}")
            return None
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using a pooled connection."""
        async with self.semaphore:
            if not self._initialized:
                await self.initialize()
            
            # Get available connection
            conn = None
            async with self.lock:
                if self.connections:
                    conn = self.connections.pop()
            
            if not conn:
                raise RuntimeError("No available ExifTool connections")
            
            try:
                # Execute command
                start_time = time.time()
                conn.stdin.write(command + '\n')
                conn.stdin.write('-execute\n')
                conn.stdin.flush()
                
                # Read response
                output = []
                while True:
                    line = conn.stdout.readline()
                    if line.strip() == '{ready}':
                        break
                    output.append(line)
                
                processing_time = time.time() - start_time
                
                # Parse JSON output
                result = ''.join(output)
                try:
                    metadata = json.loads(result) if result.strip() else {}
                except json.JSONDecodeError:
                    metadata = {"raw_output": result}
                
                return {
                    "metadata": metadata,
                    "processing_time": processing_time,
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"ExifTool command failed: {e}")
                return {
                    "metadata": {},
                    "processing_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                }
            finally:
                # Return connection to pool
                async with self.lock:
                    self.connections.append(conn)
    
    async def cleanup(self):
        """Clean up all connections in the pool."""
        async with self.lock:
            for conn in self.connections:
                try:
                    if conn.poll() is None:  # Process is still running
                        conn.stdin.write('-stay_open\nFalse\n')
                        conn.stdin.flush()
                        conn.terminate()
                        conn.wait(timeout=5)
                except Exception as e:
                    logger.error(f"Error closing ExifTool connection: {e}")
            
            self.connections.clear()
            self._initialized = False
            logger.info("ExifTool connection pool cleaned up")


class AsyncParallelExtractor:
    """Async-based parallel extraction orchestrator."""
    
    def __init__(self, config: Optional[AsyncParallelConfig] = None, 
                 extraction_fn: Optional[Callable] = None):
        """
        Initialize async parallel extractor.
        
        Args:
            config: Configuration for async parallel extraction
            extraction_fn: Function to extract metadata from single file
        """
        self.config = config or AsyncParallelConfig()
        self.extraction_fn = extraction_fn
        self.exiftool_pool: Optional[ExifToolConnectionPool] = None
        self.results: Dict[str, AsyncExtractionResult] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        self._process_pool: Optional[concurrent.futures.ProcessPoolExecutor] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize the extractor."""
        if self.config.enable_connection_pooling:
            self.exiftool_pool = ExifToolConnectionPool(self.config.exiftool_pool_size)
            await self.exiftool_pool.initialize()
        
        if self.config.execution_model == ExecutionModel.ASYNC_WITH_POOL:
            self._process_pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.config.max_process_workers
            )
    
    async def cleanup(self):
        """Clean up resources."""
        if self.exiftool_pool:
            await self.exiftool_pool.cleanup()
        
        if self._process_pool:
            self._process_pool.shutdown(wait=True)
    
    def set_extraction_function(self, fn: Callable):
        """Set the extraction function."""
        self.extraction_fn = fn
    
    def add_task(self, task: AsyncExtractionTask):
        """Add extraction task to queue."""
        self.task_queue.put_nowait(task)
        logger.debug(f"Added async task {task.task_id} for {task.file_path}")
    
    def add_tasks_batch(self, file_paths: List[str], 
                       priorities: Optional[List[int]] = None) -> List[str]:
        """Add multiple tasks at once."""
        task_ids = []
        for idx, file_path in enumerate(file_paths):
            priority = priorities[idx] if priorities else 0
            task_id = f"async_task_{int(time.time() * 1000)}_{idx}"
            task = AsyncExtractionTask(
                task_id=task_id,
                file_path=file_path,
                priority=priority
            )
            self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    async def extract_batch_async(self, file_paths: List[str]) -> Tuple[List[AsyncExtractionResult], Dict[str, Any]]:
        """
        Extract metadata from multiple files using async processing.
        
        Args:
            file_paths: List of file paths to extract
            
        Returns:
            Tuple of (results, metrics)
        """
        start_time = time.time()
        
        # Add all tasks
        task_ids = self.add_tasks_batch(file_paths)
        
        # Process tasks
        results = await self._process_all_tasks()
        
        # Calculate metrics
        total_time = time.time() - start_time
        metrics = {
            "total_files": len(file_paths),
            "successful_extractions": sum(1 for r in results if r.success),
            "failed_extractions": sum(1 for r in results if not r.success),
            "cache_hits": sum(1 for r in results if r.cache_hit),
            "total_time": total_time,
            "throughput_files_per_sec": len(file_paths) / total_time if total_time > 0 else 0,
            "avg_processing_time": sum(r.processing_time for r in results) / len(results) if results else 0
        }
        
        return results, metrics
    
    async def _process_all_tasks(self) -> List[AsyncExtractionResult]:
        """Process all tasks in the queue."""
        tasks = []
        results = []
        
        # Collect all tasks from queue
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                tasks.append(task)
            except asyncio.QueueEmpty:
                break
        
        logger.info(f"Processing {len(tasks)} async tasks")
        
        # Process tasks based on execution model
        if self.config.execution_model == ExecutionModel.ASYNC_IO:
            # Pure async processing
            results = await self._process_tasks_pure_async(tasks)
            
        elif self.config.execution_model == ExecutionModel.ASYNC_WITH_POOL:
            # Async with process pool for CPU-bound tasks
            results = await self._process_tasks_with_pool(tasks)
            
        elif self.config.execution_model == ExecutionModel.BATCH_ASYNC:
            # Batch processing with async
            results = await self._process_tasks_batch_async(tasks)
        
        return results
    
    async def _process_tasks_pure_async(self, tasks: List[AsyncExtractionTask]) -> List[AsyncExtractionResult]:
        """Process tasks using pure async I/O."""
        # Create async tasks
        async_tasks = []
        for task in tasks:
            async_task = self._execute_single_task_async(task)
            async_tasks.append(async_task)
        
        # Wait for all to complete
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Task failed with exception
                error_result = AsyncExtractionResult(
                    task_id=tasks[i].task_id,
                    file_path=tasks[i].file_path,
                    success=False,
                    metadata={},
                    error=f"Task failed with exception: {str(result)}"
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_tasks_with_pool(self, tasks: List[AsyncExtractionTask]) -> List[AsyncExtractionResult]:
        """Process tasks using async with process pool for CPU-bound operations."""
        if not self._process_pool:
            # Fallback to pure async
            return await self._process_tasks_pure_async(tasks)
        
        results = []
        
        # Process in chunks to avoid overwhelming the process pool
        chunk_size = self.config.chunk_size
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i:i + chunk_size]
            chunk_results = await self._process_chunk_with_pool(chunk)
            results.extend(chunk_results)
        
        return results
    
    async def _process_chunk_with_pool(self, tasks: List[AsyncExtractionTask]) -> List[AsyncExtractionResult]:
        """Process a chunk of tasks using process pool."""
        loop = asyncio.get_event_loop()
        
        # Submit tasks to process pool
        futures = []
        for task in tasks:
            future = loop.run_in_executor(
                self._process_pool,
                self._execute_task_sync,
                task
            )
            futures.append(future)
        
        # Wait for all to complete
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = AsyncExtractionResult(
                    task_id=tasks[i].task_id,
                    file_path=tasks[i].file_path,
                    success=False,
                    metadata={},
                    error=f"Process pool task failed: {str(result)}"
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_tasks_batch_async(self, tasks: List[AsyncExtractionTask]) -> List[AsyncExtractionResult]:
        """Process tasks using batch async optimization."""
        # Group tasks by file type for batch optimization
        tasks_by_type = defaultdict(list)
        for task in tasks:
            file_type = Path(task.file_path).suffix.lower()
            tasks_by_type[file_type].append(task)
        
        # Process each batch
        all_results = []
        for file_type, type_tasks in tasks_by_type.items():
            batch_results = await self._process_tasks_pure_async(type_tasks)
            all_results.extend(batch_results)
        
        return all_results
    
    async def _execute_single_task_async(self, task: AsyncExtractionTask) -> AsyncExtractionResult:
        """Execute a single task asynchronously."""
        async with self._semaphore:
            result = AsyncExtractionResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                metadata={}
            )
            
            try:
                if not self.extraction_fn:
                    raise ValueError("Extraction function not set")
                
                start_time = time.time()
                
                # Use connection pool if available
                if self.exiftool_pool and task.file_path.endswith(('.jpg', '.jpeg', '.tiff', '.tif', '.png', '.gif', '.bmp')):
                    # Use ExifTool with connection pool
                    command = f"-j {task.file_path}"
                    exiftool_result = await self.exiftool_pool.execute_command(command)
                    
                    if exiftool_result["success"]:
                        result.metadata = exiftool_result["metadata"]
                        result.success = True
                    else:
                        result.error = exiftool_result.get("error", "ExifTool execution failed")
                    
                    result.processing_time = exiftool_result["processing_time"]
                else:
                    # Use regular extraction function
                    metadata = await asyncio.get_event_loop().run_in_executor(
                        None, self.extraction_fn, task.file_path
                    )
                    result.metadata = metadata
                    result.success = True
                    result.processing_time = time.time() - start_time
                
                result.end_time = time.time()
                
                logger.debug(f"Successfully extracted {task.file_path} in {result.processing_time:.2f}s")
                
            except Exception as e:
                result.error = str(e)
                result.end_time = time.time()
                result.processing_time = time.time() - start_time
                
                logger.error(f"Error extracting {task.file_path}: {e}")
                
                # Check if we should retry
                if self.config.retry_failed and task.retries < task.max_retries:
                    task.retries += 1
                    logger.info(f"Retrying {task.task_id} (attempt {task.retries})")
                    await asyncio.sleep(self.config.retry_delay)
                    return await self._execute_single_task_async(task)
            
            return result
    
    def _execute_task_sync(self, task: AsyncExtractionTask) -> AsyncExtractionResult:
        """Execute a single task synchronously (for process pool)."""
        result = AsyncExtractionResult(
            task_id=task.task_id,
            file_path=task.file_path,
            success=False,
            metadata={}
        )
        
        try:
            if not self.extraction_fn:
                raise ValueError("Extraction function not set")
            
            start_time = time.time()
            metadata = self.extraction_fn(task.file_path)
            result.metadata = metadata
            result.success = True
            result.processing_time = time.time() - start_time
            result.end_time = time.time()
            
            logger.debug(f"Process pool extracted {task.file_path} in {result.processing_time:.2f}s")
            
        except Exception as e:
            result.error = str(e)
            result.end_time = time.time()
            result.processing_time = time.time() - start_time
            
            logger.error(f"Process pool error extracting {task.file_path}: {e}")
            
            # Check if we should retry
            if self.config.retry_failed and task.retries < task.max_retries:
                task.retries += 1
                logger.info(f"Process pool retrying {task.task_id} (attempt {task.retries})")
                time.sleep(self.config.retry_delay)
                return self._execute_task_sync(task)
        
        return result


# Convenience functions
async def create_async_parallel_extractor(
    extraction_fn: Callable,
    max_concurrent_tasks: int = 10,
    execution_model: ExecutionModel = ExecutionModel.ASYNC_WITH_POOL
) -> AsyncParallelExtractor:
    """Create configured async parallel extractor."""
    config = AsyncParallelConfig(
        max_concurrent_tasks=max_concurrent_tasks,
        execution_model=execution_model
    )
    extractor = AsyncParallelExtractor(config, extraction_fn)
    await extractor.initialize()
    return extractor


async def extract_files_async_parallel(
    file_paths: List[str],
    extraction_fn: Callable,
    max_concurrent_tasks: int = 10
) -> Tuple[List[AsyncExtractionResult], Dict[str, Any]]:
    """
    Convenience function for async parallel extraction.
    
    Example:
        results, metrics = await extract_files_async_parallel(
            ['file1.jpg', 'file2.png'],
            extraction_function,
            max_concurrent_tasks=10
        )
        print(f"Processed {metrics['successful_extractions']} files successfully")
    """
    extractor = await create_async_parallel_extractor(
        extraction_fn, max_concurrent_tasks
    )
    
    try:
        results, metrics = await extractor.extract_batch_async(file_paths)
        return results, metrics
    finally:
        await extractor.cleanup()


if __name__ == "__main__":
    # Test the async parallel extractor
    async def test_async_extractor():
        """Test the async parallel extractor."""
        
        # Mock extraction function
        def mock_extract(filepath: str) -> Dict[str, Any]:
            import time
            import random
            
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            return {
                "file": filepath,
                "size": 1024,
                "processing_time": processing_time,
                "extracted_fields": random.randint(10, 50)
            }
        
        # Test files
        test_files = [f"test_file_{i}.jpg" for i in range(10)]
        
        print("Testing async parallel extractor...")
        start_time = time.time()
        
        results, metrics = await extract_files_async_parallel(
            test_files,
            mock_extract,
            max_concurrent_tasks=5
        )
        
        total_time = time.time() - start_time
        
        print(f"Results:")
        print(f"  Successful: {metrics['successful_extractions']}")
        print(f"  Failed: {metrics['failed_extractions']}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {metrics['throughput_files_per_sec']:.2f} files/s")
        print(f"  Average processing time: {metrics['avg_processing_time']:.3f}s")
        
        return results, metrics
    
    # Run the test
    results, metrics = asyncio.run(test_async_extractor())
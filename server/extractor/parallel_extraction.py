"""
MetaExtract Parallel Extraction Framework v1.0

Enables parallel metadata extraction for multiple files and batches:
- Thread-pool and process-pool execution
- Queue-based work distribution
- Load balancing and work stealing
- Progress tracking and result aggregation
- Error handling and retry logic

Author: MetaExtract Team
"""

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Executor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
import time
from queue import Queue, PriorityQueue, Empty
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class ExecutionModel(Enum):
    """Execution models for parallel extraction."""
    THREAD_POOL = "thread_pool"      # I/O bound work
    PROCESS_POOL = "process_pool"    # CPU bound work
    ASYNC_IO = "async_io"             # Pure async I/O
    HYBRID = "hybrid"                 # Mix of thread and process pools


class LoadBalancingStrategy(Enum):
    """Strategies for load balancing."""
    FIFO = "fifo"                     # First in, first out
    PRIORITY = "priority"             # Priority-based
    LEAST_LOADED = "least_loaded"    # Assign to least loaded worker
    FILE_TYPE_AWARE = "file_type_aware"  # Group by file type
    SIZE_AWARE = "size_aware"         # Assign based on file size


@dataclass
class ExtractionTask:
    """Single extraction task."""
    task_id: str
    file_path: str
    priority: int = 0  # Higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    retries: int = 0
    max_retries: int = 3
    
    def __lt__(self, other: 'ExtractionTask') -> bool:
        """For priority queue ordering."""
        if self.priority != other.priority:
            return self.priority > other.priority  # Higher priority first
        return self.created_at < other.created_at  # Then FIFO


@dataclass
class ExtractionResult:
    """Result of extraction task."""
    task_id: str
    file_path: str
    success: bool
    metadata: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


@dataclass
class ParallelExtractionConfig:
    """Configuration for parallel extraction."""
    execution_model: ExecutionModel = ExecutionModel.THREAD_POOL
    max_workers: int = 4
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    timeout_per_file: int = 300  # seconds
    chunk_size: int = 10  # tasks per chunk
    enable_progress: bool = True
    enable_metrics: bool = True
    retry_failed: bool = True
    retry_delay: float = 1.0  # seconds between retries


@dataclass
class ParallelMetrics:
    """Metrics for parallel extraction."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    successful_tasks: int = 0
    total_bytes: int = 0
    start_time: float = field(default_factory=time.time)
    worker_stats: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    file_type_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        if self.completed_tasks == 0:
            return 0
        return (self.successful_tasks / self.completed_tasks) * 100
    
    @property
    def throughput_files_per_sec(self) -> float:
        if self.elapsed_time == 0:
            return 0
        return self.completed_tasks / self.elapsed_time


class ParallelExtractor:
    """Orchestrates parallel extraction of multiple files."""
    
    def __init__(self, config: Optional[ParallelExtractionConfig] = None, 
                 extraction_fn: Optional[Callable] = None):
        """
        Initialize parallel extractor.
        
        Args:
            config: Configuration for parallel extraction
            extraction_fn: Function to extract metadata from single file
        """
        self.config = config or ParallelExtractionConfig()
        self.extraction_fn = extraction_fn
        self.metrics = ParallelMetrics()
        self.results: Dict[str, ExtractionResult] = {}
        self.task_queue: PriorityQueue[ExtractionTask] = PriorityQueue()
        self.worker_queues: Dict[int, Queue[ExtractionTask]] = {}
        self.executor: Optional[Executor] = None
        self.lock = threading.RLock()
        self._futures: Dict[str, Any] = {}
        self._cancelled = False
    
    def set_extraction_function(self, fn: Callable):
        """Set the extraction function."""
        self.extraction_fn = fn
    
    def add_task(self, task: ExtractionTask) -> None:
        """Add extraction task to queue."""
        with self.lock:
            self.metrics.total_tasks += 1
            self.task_queue.put(task)
            logger.debug(f"Added task {task.task_id} for {task.file_path}")
    
    def add_tasks_batch(self, file_paths: List[str], 
                       priorities: Optional[List[int]] = None) -> List[str]:
        """
        Add multiple tasks at once.
        
        Returns:
            List of task IDs
        """
        task_ids = []
        for idx, file_path in enumerate(file_paths):
            priority = priorities[idx] if priorities else 0
            task_id = f"task_{int(time.time() * 1000)}_{idx}"
            task = ExtractionTask(
                task_id=task_id,
                file_path=file_path,
                priority=priority
            )
            self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    def _select_executor(self) -> Executor:
        """Select appropriate executor based on config."""
        if self.config.execution_model == ExecutionModel.THREAD_POOL:
            return ThreadPoolExecutor(max_workers=self.config.max_workers)
        elif self.config.execution_model == ExecutionModel.PROCESS_POOL:
            return ProcessPoolExecutor(max_workers=self.config.max_workers)
        else:
            # Default to thread pool
            return ThreadPoolExecutor(max_workers=self.config.max_workers)
    
    def _extract_wrapper(self, task: ExtractionTask) -> ExtractionResult:
        """Wrapper around extraction function with error handling."""
        result = ExtractionResult(
            task_id=task.task_id,
            file_path=task.file_path,
            success=False,
            metadata={}
        )
        
        try:
            if not self.extraction_fn:
                raise ValueError("Extraction function not set")
            
            start = time.time()
            metadata = self.extraction_fn(task.file_path)
            result.metadata = metadata
            result.success = True
            result.end_time = time.time()
            result.processing_time = result.end_time - result.start_time
            
            logger.info(f"Successfully extracted {task.file_path} in {result.processing_time:.2f}s")
            
        except Exception as e:
            result.error = str(e)
            result.end_time = time.time()
            result.processing_time = result.end_time - result.start_time
            
            logger.error(f"Error extracting {task.file_path}: {e}")
            
            # Check if we should retry
            if self.config.retry_failed and task.retries < task.max_retries:
                task.retries += 1
                logger.info(f"Retrying {task.task_id} (attempt {task.retries})")
                time.sleep(self.config.retry_delay)
                return self._extract_wrapper(task)
        
        return result
    
    async def extract_parallel(self, file_paths: List[str]) -> Tuple[List[ExtractionResult], ParallelMetrics]:
        """
        Extract metadata from multiple files in parallel.
        
        Args:
            file_paths: List of file paths to extract
        
        Returns:
            Tuple of (results, metrics)
        """
        # Add all tasks
        task_ids = self.add_tasks_batch(file_paths)
        
        # Create executor
        self.executor = self._select_executor()
        results = []
        
        try:
            # Convert blocking extraction to async
            loop = asyncio.get_event_loop()
            
            with self.executor as executor:
                coros = []
                
                # Get all tasks from queue
                tasks = []
                while not self.task_queue.empty():
                    try:
                        task = self.task_queue.get_nowait()
                        tasks.append(task)
                    except Empty:
                        break
                
                # Create async coroutines for each task
                for task in tasks:
                    coro = loop.run_in_executor(executor, self._extract_wrapper, task)
                    coros.append(coro)
                
                # Wait for all to complete
                completed = await asyncio.gather(*coros, return_exceptions=True)
                
                # Process results
                for item in completed:
                    try:
                        if isinstance(item, Exception):
                            logger.error(f"Task failed with exception: {item}")
                            self.metrics.failed_tasks += 1
                            continue
                        
                        result = item
                        results.append(result)
                        
                        with self.lock:
                            self.results[result.task_id] = result
                            self.metrics.completed_tasks += 1
                            if result.success:
                                self.metrics.successful_tasks += 1
                            else:
                                self.metrics.failed_tasks += 1
                            
                            # Update file type stats
                            file_type = Path(result.file_path).suffix.lower()
                            if file_type not in self.metrics.file_type_stats:
                                self.metrics.file_type_stats[file_type] = {
                                    'count': 0,
                                    'success': 0,
                                    'total_time': 0
                                }
                            self.metrics.file_type_stats[file_type]['count'] += 1
                            if result.success:
                                self.metrics.file_type_stats[file_type]['success'] += 1
                            self.metrics.file_type_stats[file_type]['total_time'] += result.processing_time
                        
                        logger.debug(f"Completed task {result.task_id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing result: {e}")
                        self.metrics.failed_tasks += 1
        
        except Exception as e:
            logger.error(f"Error in parallel extraction: {e}")
            raise
        
        return results, self.metrics
    
    def extract_parallel_sync(self, file_paths: List[str]) -> Tuple[List[ExtractionResult], ParallelMetrics]:
        """
        Synchronous version of parallel extraction (blocking).
        
        Args:
            file_paths: List of file paths
        
        Returns:
            Tuple of (results, metrics)
        """
        # Add all tasks
        self.add_tasks_batch(file_paths)
        
        # Create executor
        self.executor = self._select_executor()
        results = []
        
        try:
            with self.executor as executor:
                futures = {}
                
                # Get all tasks from queue
                while not self.task_queue.empty():
                    try:
                        task = self.task_queue.get_nowait()
                        future = executor.submit(self._extract_wrapper, task)
                        futures[future] = task.task_id
                    except Empty:
                        break
                
                # Wait for all to complete
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=self.config.timeout_per_file)
                        results.append(result)
                        
                        with self.lock:
                            self.results[result.task_id] = result
                            self.metrics.completed_tasks += 1
                            if result.success:
                                self.metrics.successful_tasks += 1
                            else:
                                self.metrics.failed_tasks += 1
                        
                    except Exception as e:
                        logger.error(f"Error getting result: {e}")
                        self.metrics.failed_tasks += 1
        
        finally:
            if self.executor:
                self.executor.shutdown(wait=True)
        
        return results, self.metrics
    
    def get_results(self) -> Dict[str, ExtractionResult]:
        """Get all extraction results."""
        with self.lock:
            return dict(self.results)
    
    def get_metrics(self) -> ParallelMetrics:
        """Get extraction metrics."""
        return self.metrics
    
    def cancel_all(self):
        """Cancel all pending tasks."""
        self._cancelled = True
        logger.info("Cancelled all pending extraction tasks")


class LoadBalancer:
    """Distributes work across workers."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.strategy = strategy
        self.worker_loads: Dict[int, int] = defaultdict(int)
        self.lock = threading.Lock()
    
    def assign_worker(self, task: ExtractionTask, num_workers: int) -> int:
        """
        Assign task to worker.
        
        Args:
            task: Task to assign
            num_workers: Total number of workers
        
        Returns:
            Worker ID
        """
        with self.lock:
            if self.strategy == LoadBalancingStrategy.FIFO:
                return 0  # Always use first worker
            
            elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
                # Find worker with least load
                min_load = min(
                    self.worker_loads.get(i, 0) for i in range(num_workers)
                )
                for i in range(num_workers):
                    if self.worker_loads.get(i, 0) == min_load:
                        self.worker_loads[i] += 1
                        return i
            
            elif self.strategy == LoadBalancingStrategy.FILE_TYPE_AWARE:
                # Assign based on file type (simplified)
                suffix = Path(task.file_path).suffix.lower()
                return hash(suffix) % num_workers
            
            elif self.strategy == LoadBalancingStrategy.SIZE_AWARE:
                # Assign based on file size
                try:
                    size = Path(task.file_path).stat().st_size
                    return (size % (1024 * 1024)) % num_workers
                except:
                    return 0
            
            # Default
            return 0
    
    def update_load(self, worker_id: int, decrement: bool = False):
        """Update worker load."""
        with self.lock:
            if decrement:
                self.worker_loads[worker_id] = max(0, self.worker_loads[worker_id] - 1)
            else:
                self.worker_loads[worker_id] += 1


# Convenience functions
def create_parallel_extractor(
    extraction_fn: Callable,
    max_workers: int = 4,
    execution_model: ExecutionModel = ExecutionModel.THREAD_POOL
) -> ParallelExtractor:
    """Create configured parallel extractor."""
    config = ParallelExtractionConfig(
        max_workers=max_workers,
        execution_model=execution_model
    )
    extractor = ParallelExtractor(config, extraction_fn)
    return extractor


async def extract_files_parallel(
    file_paths: List[str],
    extraction_fn: Callable,
    max_workers: int = 4
) -> Tuple[List[ExtractionResult], ParallelMetrics]:
    """
    Convenience function for parallel extraction.
    
    Example:
        results, metrics = await extract_files_parallel(
            ['file1.h5', 'file2.h5'],
            extraction_function,
            max_workers=4
        )
        print(f"Processed {metrics.successful_tasks} files successfully")
    """
    extractor = create_parallel_extractor(extraction_fn, max_workers)
    return await extractor.extract_parallel(file_paths)

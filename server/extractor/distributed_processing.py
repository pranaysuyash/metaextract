"""
MetaExtract Distributed Processing Framework v1.0

Enables distributed metadata extraction across multiple machines:
- Task distribution via message queues
- Worker pool coordination
- Result aggregation and caching
- Fault tolerance and recovery
- Load balancing across nodes

Author: MetaExtract Team
"""

import asyncio
import logging
import json
import threading
import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import uuid
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    """Worker node status."""
    IDLE = "idle"
    BUSY = "busy"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class MessageType(Enum):
    """Types of messages in distributed system."""
    TASK = "task"
    RESULT = "result"
    HEARTBEAT = "heartbeat"
    ACK = "ack"
    ERROR = "error"
    REGISTER = "register"
    DEREGISTER = "deregister"


@dataclass
class DistributedTask:
    """Task for distributed execution."""
    task_id: str
    file_path: str
    priority: int = 0
    retries: int = 0
    max_retries: int = 3
    assigned_worker: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            'task_id': self.task_id,
            'file_path': self.file_path,
            'priority': self.priority,
            'retries': self.retries,
            'max_retries': self.max_retries
        }


@dataclass
class DistributedResult:
    """Result from distributed task execution."""
    task_id: str
    worker_id: str
    success: bool
    metadata: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            'task_id': self.task_id,
            'worker_id': self.worker_id,
            'success': self.success,
            'metadata': self.metadata,
            'error': self.error,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp
        }


@dataclass
class WorkerNode:
    """Represents a worker node in the cluster."""
    worker_id: str
    hostname: str
    port: int
    status: WorkerStatus = WorkerStatus.IDLE
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_task: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    capacity: int = 1  # Tasks it can handle simultaneously
    
    @property
    def is_healthy(self) -> bool:
        """Check if worker is responsive."""
        elapsed = time.time() - self.last_heartbeat
        return elapsed < 60  # 60 second timeout
    
    @property
    def utilization(self) -> float:
        """Get worker utilization percentage."""
        return (1 if self.current_task else 0) / self.capacity


@dataclass
class DistributedMetrics:
    """Metrics for distributed extraction."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    successful_tasks: int = 0
    total_bytes: int = 0
    start_time: float = field(default_factory=time.time)
    worker_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    network_overhead_ms: float = 0
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        if self.completed_tasks == 0:
            return 0
        return (self.successful_tasks / self.completed_tasks) * 100


class MessageQueue(ABC):
    """Abstract message queue interface."""
    
    @abstractmethod
    async def send(self, message_type: MessageType, data: Dict[str, Any]) -> None:
        """Send message to queue."""
        pass
    
    @abstractmethod
    async def receive(self, timeout: int = 30) -> Optional[Tuple[MessageType, Dict[str, Any]]]:
        """Receive message from queue."""
        pass
    
    @abstractmethod
    async def acknowledge(self, message_id: str) -> None:
        """Acknowledge message processing."""
        pass


class InMemoryQueue(MessageQueue):
    """In-memory message queue for local testing."""
    
    def __init__(self):
        self.queues: Dict[str, List[Tuple[str, MessageType, Dict]]] = defaultdict(list)
        self.lock = threading.RLock()
    
    async def send(self, message_type: MessageType, data: Dict[str, Any], destination: str = 'default') -> None:
        """Send message."""
        with self.lock:
            msg_id = str(uuid.uuid4())
            self.queues[destination].append((msg_id, message_type, data))
    
    async def receive(self, timeout: int = 30, source: str = 'default') -> Optional[Tuple[MessageType, Dict[str, Any]]]:
        """Receive message."""
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if self.queues[source]:
                    msg_id, msg_type, data = self.queues[source].pop(0)
                    return (msg_type, data)
            await asyncio.sleep(0.1)
        return None
    
    async def acknowledge(self, message_id: str) -> None:
        """Acknowledge message."""
        pass


class DistributedCoordinator:
    """Coordinates distributed extraction across worker nodes."""
    
    def __init__(self, num_workers: int = 4, queue: Optional[MessageQueue] = None):
        """
        Initialize distributed coordinator.
        
        Args:
            num_workers: Number of worker nodes
            queue: Message queue implementation
        """
        self.num_workers = num_workers
        self.queue = queue or InMemoryQueue()
        self.workers: Dict[str, WorkerNode] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.results: Dict[str, DistributedResult] = {}
        self.metrics = DistributedMetrics()
        self.lock = threading.RLock()
        self._running = False
    
    def register_worker(self, worker_id: str, hostname: str, port: int) -> None:
        """Register a worker node."""
        with self.lock:
            worker = WorkerNode(
                worker_id=worker_id,
                hostname=hostname,
                port=port
            )
            self.workers[worker_id] = worker
            logger.info(f"Registered worker {worker_id} at {hostname}:{port}")
    
    def get_healthy_workers(self) -> List[WorkerNode]:
        """Get list of healthy workers."""
        with self.lock:
            return [w for w in self.workers.values() if w.is_healthy]
    
    def get_best_worker(self) -> Optional[WorkerNode]:
        """Select best worker based on utilization."""
        healthy = self.get_healthy_workers()
        if not healthy:
            return None
        
        # Return worker with lowest utilization
        return min(healthy, key=lambda w: w.utilization)
    
    async def add_task(self, task: DistributedTask) -> None:
        """Add task to distributed queue."""
        with self.lock:
            self.metrics.total_tasks += 1
        
        # Use negative priority for max-heap behavior
        await self.task_queue.put((-task.priority, task.task_id, task))
    
    async def add_tasks_batch(self, file_paths: List[str]) -> List[str]:
        """Add batch of tasks."""
        task_ids = []
        for file_path in file_paths:
            task_id = f"dtask_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
            task = DistributedTask(task_id=task_id, file_path=file_path)
            await self.add_task(task)
            task_ids.append(task_id)
        return task_ids
    
    async def process_tasks(self, extraction_fn: Callable) -> Tuple[List[DistributedResult], DistributedMetrics]:
        """
        Process all tasks in distributed manner.
        
        Args:
            extraction_fn: Function to extract metadata
        
        Returns:
            Tuple of (results, metrics)
        """
        self._running = True
        results = []
        
        try:
            # Simulate distributed processing
            while not self.task_queue.empty() and self._running:
                try:
                    # Get next task
                    _, task_id, task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                    
                    # Find best worker
                    worker = self.get_best_worker()
                    if not worker:
                        logger.warning("No healthy workers available")
                        # Put task back in queue
                        await self.add_task(task)
                        await asyncio.sleep(1)
                        continue
                    
                    # Assign task to worker
                    task.assigned_worker = worker.worker_id
                    task.started_at = time.time()
                    worker.current_task = task.task_id
                    worker.status = WorkerStatus.BUSY
                    
                    # Execute task (simulated)
                    try:
                        start = time.time()
                        metadata = extraction_fn(task.file_path)
                        processing_time = time.time() - start
                        
                        # Create result
                        result = DistributedResult(
                            task_id=task.task_id,
                            worker_id=worker.worker_id,
                            success=True,
                            metadata=metadata,
                            processing_time=processing_time
                        )
                        
                        results.append(result)
                        with self.lock:
                            self.results[task.task_id] = result
                            self.metrics.completed_tasks += 1
                            self.metrics.successful_tasks += 1
                            
                            # Update worker stats
                            if worker.worker_id not in self.metrics.worker_stats:
                                self.metrics.worker_stats[worker.worker_id] = {
                                    'completed': 0,
                                    'failed': 0,
                                    'total_time': 0
                                }
                            self.metrics.worker_stats[worker.worker_id]['completed'] += 1
                            self.metrics.worker_stats[worker.worker_id]['total_time'] += processing_time
                        
                        worker.tasks_completed += 1
                        logger.info(f"Task {task.task_id} completed on worker {worker.worker_id}")
                        
                    except Exception as e:
                        logger.error(f"Task {task.task_id} failed: {e}")
                        
                        # Retry logic
                        if task.retries < task.max_retries:
                            task.retries += 1
                            task.assigned_worker = None
                            await self.add_task(task)
                        else:
                            result = DistributedResult(
                                task_id=task.task_id,
                                worker_id=worker.worker_id,
                                success=False,
                                metadata={},
                                error=str(e)
                            )
                            results.append(result)
                            with self.lock:
                                self.results[task.task_id] = result
                                self.metrics.completed_tasks += 1
                                self.metrics.failed_tasks += 1
                            worker.tasks_failed += 1
                    
                    finally:
                        # Release worker
                        worker.current_task = None
                        worker.status = WorkerStatus.IDLE if worker.is_healthy else WorkerStatus.UNHEALTHY
                
                except asyncio.TimeoutError:
                    continue
        
        finally:
            self._running = False
        
        return results, self.metrics
    
    def get_results(self) -> Dict[str, DistributedResult]:
        """Get all results."""
        with self.lock:
            return dict(self.results)
    
    def get_metrics(self) -> DistributedMetrics:
        """Get metrics."""
        return self.metrics
    
    def shutdown(self):
        """Shutdown coordinator."""
        self._running = False
        logger.info("Distributed coordinator shutdown")


class ResultCache:
    """Cache for extraction results to avoid reprocessing."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize result cache.
        
        Args:
            ttl: Time-to-live for cached results in seconds
        """
        self.cache: Dict[str, Tuple[DistributedResult, float]] = {}
        self.ttl = ttl
        self.lock = threading.RLock()
    
    def get_key(self, file_path: str) -> str:
        """Generate cache key from file path."""
        # Use file path and modification time as key
        try:
            mtime = Path(file_path).stat().st_mtime
            content = f"{file_path}:{mtime}"
        except:
            content = file_path
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, file_path: str) -> Optional[DistributedResult]:
        """Get cached result."""
        with self.lock:
            key = self.get_key(file_path)
            if key in self.cache:
                result, cached_at = self.cache[key]
                if time.time() - cached_at < self.ttl:
                    return result
                else:
                    del self.cache[key]
            return None
    
    def set(self, file_path: str, result: DistributedResult) -> None:
        """Cache result."""
        with self.lock:
            key = self.get_key(file_path)
            self.cache[key] = (result, time.time())
    
    def clear(self):
        """Clear cache."""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                'size': len(self.cache),
                'ttl': self.ttl
            }


class AdaptiveScheduler:
    """Adaptive task scheduling based on worker performance."""
    
    def __init__(self):
        self.worker_performance: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
    
    def record_performance(self, worker_id: str, processing_time: float) -> None:
        """Record task processing time for worker."""
        with self.lock:
            self.worker_performance[worker_id].append(processing_time)
            
            # Keep only last 100 measurements
            if len(self.worker_performance[worker_id]) > 100:
                self.worker_performance[worker_id] = self.worker_performance[worker_id][-100:]
    
    def estimate_task_time(self, worker_id: str, file_size: int) -> float:
        """Estimate task completion time for worker."""
        with self.lock:
            if worker_id not in self.worker_performance:
                return 0
            
            times = self.worker_performance[worker_id]
            if not times:
                return 0
            
            # Use average of recent measurements
            avg_time = sum(times[-10:]) / len(times[-10:])
            
            # Scale by file size (rough estimate)
            size_factor = max(0.1, file_size / (10 * 1024 * 1024))  # 10MB baseline
            return avg_time * size_factor
    
    def select_best_worker(self, workers: List[WorkerNode], file_size: int) -> Optional[str]:
        """Select worker with estimated shortest completion time."""
        if not workers:
            return None
        
        best_worker = None
        best_time = float('inf')
        
        for worker in workers:
            est_time = self.estimate_task_time(worker.worker_id, file_size)
            if est_time < best_time:
                best_time = est_time
                best_worker = worker.worker_id
        
        return best_worker


# Convenience functions
async def extract_distributed(
    file_paths: List[str],
    extraction_fn: Callable,
    num_workers: int = 4
) -> Tuple[List[DistributedResult], DistributedMetrics]:
    """
    Extract metadata from multiple files using distributed processing.
    
    Example:
        results, metrics = await extract_distributed(
            files, extraction_function, num_workers=4
        )
    """
    coordinator = DistributedCoordinator(num_workers=num_workers)
    
    # Register workers
    for i in range(num_workers):
        coordinator.register_worker(
            worker_id=f"worker_{i}",
            hostname="localhost",
            port=5000 + i
        )
    
    # Add tasks
    await coordinator.add_tasks_batch(file_paths)
    
    # Process
    return await coordinator.process_tasks(extraction_fn)

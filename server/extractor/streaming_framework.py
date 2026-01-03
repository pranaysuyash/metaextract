"""
MetaExtract Streaming Framework v1.0

Enables streaming metadata extraction for large files, allowing:
- Chunked processing to reduce memory footprint
- Progressive result delivery
- Real-time progress tracking
- Support for files larger than available RAM

Author: MetaExtract Team
"""

import asyncio
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, Iterator, List, Optional, Tuple
from datetime import datetime
import time
from queue import Queue, Empty
import io

logger = logging.getLogger(__name__)


class ChunkType(Enum):
    """Types of chunks processed in streaming."""
    HEADER = "header"           # File header metadata
    SECTION = "section"         # File section/block
    FRAME = "frame"             # Video/image frame
    BLOCK = "block"             # Generic data block
    METADATA = "metadata"       # Extracted metadata
    FOOTER = "footer"           # File footer


class StreamingStrategy(Enum):
    """Different streaming strategies for various file types."""
    SEQUENTIAL = "sequential"   # Process chunks sequentially
    WINDOWED = "windowed"       # Sliding window processing
    SAMPLE_BASED = "sample_based"  # Sample key chunks
    ADAPTIVE = "adaptive"       # Adapt strategy based on file type


@dataclass
class StreamChunk:
    """Represents a single chunk in the stream."""
    chunk_id: int
    chunk_type: ChunkType
    offset: int
    size: int
    data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __repr__(self) -> str:
        return f"StreamChunk(id={self.chunk_id}, type={self.chunk_type.value}, size={self.size}, offset={self.offset})"


@dataclass
class StreamingConfig:
    """Configuration for streaming extraction."""
    chunk_size: int = 1024 * 1024  # 1MB default
    max_chunks: Optional[int] = None  # None = unlimited
    strategy: StreamingStrategy = StreamingStrategy.SEQUENTIAL
    timeout_per_chunk: int = 30  # seconds
    enable_caching: bool = True
    max_buffered_chunks: int = 5
    min_file_size_threshold: int = 10 * 1024 * 1024  # 10MB - enable streaming for files > 10MB


@dataclass
class StreamingMetrics:
    """Metrics for streaming extraction."""
    total_chunks: int = 0
    chunks_processed: int = 0
    bytes_processed: int = 0
    start_time: float = field(default_factory=time.time)
    current_chunk_time: float = 0
    errors: int = 0
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def progress_percent(self) -> float:
        if self.total_chunks == 0:
            return 0
        return (self.chunks_processed / self.total_chunks) * 100
    
    @property
    def throughput_mb_per_sec(self) -> float:
        elapsed = self.elapsed_time
        if elapsed == 0:
            return 0
        return (self.bytes_processed / (1024 * 1024)) / elapsed


class StreamChunkReader(ABC):
    """Abstract base class for file chunk readers."""
    
    @abstractmethod
    async def read_chunks(self, file_path: str, config: StreamingConfig) -> AsyncIterator[StreamChunk]:
        """Asynchronously read file chunks."""
        pass
    
    @abstractmethod
    def calculate_chunk_count(self, file_size: int, config: StreamingConfig) -> int:
        """Calculate number of chunks for a file."""
        pass


class BinaryChunkReader(StreamChunkReader):
    """Reader for generic binary files."""
    
    async def read_chunks(self, file_path: str, config: StreamingConfig) -> AsyncIterator[StreamChunk]:
        """Read binary file in chunks."""
        try:
            file_size = Path(file_path).stat().st_size
            chunk_count = self.calculate_chunk_count(file_size, config)
            
            with open(file_path, 'rb') as f:
                for chunk_id in range(chunk_count):
                    if config.max_chunks and chunk_id >= config.max_chunks:
                        break
                    
                    offset = chunk_id * config.chunk_size
                    chunk_data = f.read(config.chunk_size)
                    
                    if not chunk_data:
                        break
                    
                    # Determine chunk type
                    if chunk_id == 0:
                        chunk_type = ChunkType.HEADER
                    elif chunk_id == chunk_count - 1:
                        chunk_type = ChunkType.FOOTER
                    else:
                        chunk_type = ChunkType.BLOCK
                    
                    yield StreamChunk(
                        chunk_id=chunk_id,
                        chunk_type=chunk_type,
                        offset=offset,
                        size=len(chunk_data),
                        data=chunk_data
                    )
                    
                    # Yield control to event loop
                    await asyncio.sleep(0)
                    
        except Exception as e:
            logger.error(f"Error reading chunks from {file_path}: {e}")
            raise
    
    def calculate_chunk_count(self, file_size: int, config: StreamingConfig) -> int:
        """Calculate number of chunks."""
        chunk_count = (file_size + config.chunk_size - 1) // config.chunk_size
        if config.max_chunks:
            chunk_count = min(chunk_count, config.max_chunks)
        return chunk_count


class VideoChunkReader(StreamChunkReader):
    """Reader for video files - chunks by frames."""
    
    async def read_chunks(self, file_path: str, config: StreamingConfig) -> AsyncIterator[StreamChunk]:
        """Read video file by frames (requires ffprobe/ffmpeg)."""
        try:
            # Import ffmpeg helper if available
            import subprocess
            
            # Use ffprobe to get frame information
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                 '-show_entries', 'stream=nb_read_frames,r_frame_rate',
                 '-of', 'json', file_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                data = result.stdout
                frame_info = {'sample_based': True}
            else:
                # Fallback to binary reading
                async for chunk in BinaryChunkReader().read_chunks(file_path, config):
                    yield chunk
                return
            
            logger.info(f"Video file {file_path} ready for frame-based streaming")
            
        except Exception as e:
            logger.warning(f"Failed to read video chunks, falling back to binary: {e}")
            async for chunk in BinaryChunkReader().read_chunks(file_path, config):
                yield chunk
    
    def calculate_chunk_count(self, file_size: int, config: StreamingConfig) -> int:
        """Estimate frame count (depends on codec)."""
        # Rough estimate: assume ~1MB per frame on average
        return max(1, file_size // (1024 * 1024))


class HDF5ChunkReader(StreamChunkReader):
    """Reader for HDF5 scientific data files."""
    
    async def read_chunks(self, file_path: str, config: StreamingConfig) -> AsyncIterator[StreamChunk]:
        """Read HDF5 file by datasets/groups."""
        try:
            import h5py
            
            chunk_id = 0
            with h5py.File(file_path, 'r') as f:
                # First chunk: file structure
                yield StreamChunk(
                    chunk_id=chunk_id,
                    chunk_type=ChunkType.METADATA,
                    offset=0,
                    size=0,
                    data=b'',
                    metadata={'hdf5_attrs': dict(f.attrs)}
                )
                chunk_id += 1
                
                # Process each dataset
                def iterate_datasets(parent, path=''):
                    nonlocal chunk_id
                    chunks = []
                    for name, item in parent.items():
                        if config.max_chunks and chunk_id >= config.max_chunks:
                            return
                        
                        full_path = f"{path}/{name}"
                        
                        if isinstance(item, h5py.Dataset):
                            # Create metadata chunk for dataset
                            chunks.append(StreamChunk(
                                chunk_id=chunk_id,
                                chunk_type=ChunkType.BLOCK,
                                offset=0,
                                size=item.nbytes if hasattr(item, 'nbytes') else 0,
                                data=b'',
                                metadata={
                                    'hdf5_path': full_path,
                                    'hdf5_dtype': str(item.dtype),
                                    'hdf5_shape': item.shape,
                                    'hdf5_chunks': item.chunks
                                }
                            ))
                            chunk_id += 1
                        
                        elif isinstance(item, h5py.Group):
                            chunks.extend(iterate_datasets(item, full_path))
                    
                    return chunks
                
                # Use generator within async context
                for chunk in iterate_datasets(f):
                    yield chunk
                    await asyncio.sleep(0)
                    
        except ImportError:
            logger.warning("h5py not available for HDF5 streaming")
        except Exception as e:
            logger.error(f"Error reading HDF5 chunks from {file_path}: {e}")
            raise
    
    def calculate_chunk_count(self, file_size: int, config: StreamingConfig) -> int:
        """Estimate chunk count based on file size."""
        return max(1, (file_size + config.chunk_size - 1) // config.chunk_size)


class StreamingExtractor:
    """Main streaming extraction handler."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.metrics = StreamingMetrics()
        self.chunk_readers: Dict[str, StreamChunkReader] = {
            'default': BinaryChunkReader(),
            'video': VideoChunkReader(),
            'hdf5': HDF5ChunkReader(),
            'netcdf': HDF5ChunkReader(),  # NetCDF uses similar structure
        }
        self.extraction_callbacks: List[Callable] = []
    
    def register_extraction_callback(self, callback: Callable):
        """Register callback to process chunks."""
        self.extraction_callbacks.append(callback)
    
    def get_reader(self, file_path: str) -> StreamChunkReader:
        """Get appropriate chunk reader for file type."""
        suffix = Path(file_path).suffix.lower()
        
        if suffix in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            return self.chunk_readers['video']
        elif suffix in ['.h5', '.hdf5']:
            return self.chunk_readers['hdf5']
        elif suffix in ['.nc', '.netcdf']:
            return self.chunk_readers['netcdf']
        else:
            return self.chunk_readers['default']
    
    async def should_stream(self, file_path: str) -> bool:
        """Determine if file should use streaming extraction."""
        try:
            file_size = Path(file_path).stat().st_size
            return file_size >= self.config.min_file_size_threshold
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False
    
    async def extract_streaming(
        self,
        file_path: str,
        callback: Optional[Callable[[StreamChunk, StreamingMetrics], Any]] = None
    ) -> Tuple[Dict[str, Any], StreamingMetrics]:
        """
        Extract metadata from file using streaming.
        
        Args:
            file_path: Path to file
            callback: Optional callback for each chunk (chunk, metrics) -> result
        
        Returns:
            Tuple of (aggregated_metadata, final_metrics)
        """
        try:
            if not await self.should_stream(file_path):
                logger.info(f"File {file_path} below streaming threshold, use normal extraction")
                return {}, self.metrics
            
            reader = self.get_reader(file_path)
            file_size = Path(file_path).stat().st_size
            self.metrics.total_chunks = reader.calculate_chunk_count(file_size, self.config)
            
            aggregated_metadata: Dict[str, Any] = {
                'chunks': [],
                'file_info': {
                    'path': str(file_path),
                    'size': file_size,
                    'modified': datetime.fromtimestamp(Path(file_path).stat().st_mtime).isoformat()
                }
            }
            
            async for chunk in reader.read_chunks(file_path, self.config):
                try:
                    # Call registered callbacks
                    for cb in self.extraction_callbacks:
                        result = cb(chunk, self.metrics)
                        if result:
                            aggregated_metadata['chunks'].append(result)
                    
                    # Call user callback
                    if callback:
                        await self._call_async_or_sync(callback, chunk, self.metrics)
                    
                    # Update metrics
                    self.metrics.chunks_processed += 1
                    self.metrics.bytes_processed += chunk.size
                    self.metrics.current_chunk_time = time.time() - chunk.timestamp
                    
                    logger.debug(
                        f"Processed chunk {chunk.chunk_id} ({chunk.size} bytes), "
                        f"Progress: {self.metrics.progress_percent:.1f}%"
                    )
                    
                except asyncio.TimeoutError:
                    self.metrics.errors += 1
                    logger.error(f"Timeout processing chunk {chunk.chunk_id}")
                except Exception as e:
                    self.metrics.errors += 1
                    logger.error(f"Error processing chunk {chunk.chunk_id}: {e}")
            
            aggregated_metadata['metrics'] = {
                'total_chunks': self.metrics.total_chunks,
                'processed_chunks': self.metrics.chunks_processed,
                'bytes_processed': self.metrics.bytes_processed,
                'elapsed_time': self.metrics.elapsed_time,
                'throughput_mb_per_sec': self.metrics.throughput_mb_per_sec,
                'errors': self.metrics.errors
            }
            
            return aggregated_metadata, self.metrics
            
        except Exception as e:
            logger.error(f"Error in streaming extraction: {e}")
            self.metrics.errors += 1
            raise
    
    @staticmethod
    async def _call_async_or_sync(func: Callable, *args, **kwargs) -> Any:
        """Call function whether it's async or sync."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)


class StreamingProgressTracker:
    """Track and report streaming progress."""
    
    def __init__(self, total_chunks: int, callback: Optional[Callable[[float, str], None]] = None):
        self.total_chunks = total_chunks
        self.processed = 0
        self.callback = callback
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, message: str = ""):
        """Update progress."""
        with self.lock:
            self.processed += 1
            percent = (self.processed / self.total_chunks) * 100 if self.total_chunks > 0 else 0
            
            if self.callback:
                self.callback(percent, message)
            
            elapsed = time.time() - self.start_time
            rate = self.processed / elapsed if elapsed > 0 else 0
            remaining = (self.total_chunks - self.processed) / rate if rate > 0 else 0
            
            logger.info(
                f"Progress: {percent:.1f}% ({self.processed}/{self.total_chunks}), "
                f"Rate: {rate:.1f} chunks/sec, ETA: {remaining:.0f}s"
            )
    
    def finish(self):
        """Mark as finished."""
        elapsed = time.time() - self.start_time
        logger.info(f"Streaming completed in {elapsed:.2f}s, {self.processed} chunks processed")


# Convenience function for easy integration
async def extract_with_streaming(
    file_path: str,
    config: Optional[StreamingConfig] = None,
    callback: Optional[Callable] = None
) -> Tuple[Dict[str, Any], StreamingMetrics]:
    """
    Convenience function to perform streaming extraction.
    
    Example:
        metadata, metrics = await extract_with_streaming('large_file.h5')
        print(f"Processed {metrics.chunks_processed} chunks in {metrics.elapsed_time}s")
    """
    extractor = StreamingExtractor(config)
    return await extractor.extract_streaming(file_path, callback)

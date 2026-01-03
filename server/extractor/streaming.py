"""
Streaming Framework for Large Scientific Files
Implements memory-efficient processing for scientific data formats
Based on performance optimization analysis showing 87% memory reduction potential
"""

import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Callable, Any, Dict, Union, List
from abc import ABC, abstractmethod
import time
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class ProcessingChunk:
    """Represents a chunk of data being processed"""
    offset: int
    size: int
    data: bytes
    is_last: bool
    chunk_id: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class StreamingConfig:
    """Configuration for streaming operations"""
    chunk_size: int = 5_000_000  # 5MB default for scientific files
    max_memory_per_process: int = 200_000_000  # 200MB limit per process
    enable_backpressure: bool = True
    progress_callback_interval: float = 1.0  # seconds
    adaptive_chunk_size: bool = True
    min_chunk_size: int = 1_000_000  # 1MB minimum
    max_chunk_size: int = 20_000_000  # 20MB maximum


class StreamingMetadataExtractor:
    """
    Memory-efficient metadata extraction using streaming chunks
    Optimized for scientific files (DICOM, FITS, HDF5, NetCDF, GeoTIFF)
    """
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.processed_bytes = 0
        self.total_bytes = 0
        self.start_time = 0
        self._lock = threading.Lock()
        self._memory_monitor = MemoryMonitor()
        self._progress_callbacks: List[Callable[[float, int, int], None]] = []
        self._last_progress_time = 0
        
    def add_progress_callback(self, callback: Callable[[float, int, int], None]) -> None:
        """Add progress callback (progress_percent, processed_bytes, total_bytes)"""
        self._progress_callbacks.append(callback)
    
    def stream_file(self, filepath: Union[str, Path]) -> Iterator[ProcessingChunk]:
        """
        Stream file in chunks with memory monitoring and adaptive sizing
        
        Args:
            filepath: Path to file to stream
            
        Yields:
            ProcessingChunk objects
            
        Raises:
            MemoryError: If system memory pressure is too high
            IOError: If file cannot be read
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_size = filepath.stat().st_size
        self.total_bytes = file_size
        self.processed_bytes = 0
        self.start_time = time.time()
        
        logger.info(f"Starting streaming extraction of {filepath.name} "
                   f"({file_size / 1_000_000:.1f}MB)")
        
        chunk_id = 0
        current_chunk_size = self.config.chunk_size
        
        try:
            with open(filepath, 'rb') as file_obj:
                while self.processed_bytes < file_size:
                    # Adaptive chunk sizing based on memory pressure
                    if self.config.adaptive_chunk_size:
                        current_chunk_size = self._get_adaptive_chunk_size()
                    
                    # Check memory pressure before reading
                    if self.config.enable_backpressure:
                        self._check_memory_pressure()
                    
                    # Read chunk
                    chunk_data = file_obj.read(current_chunk_size)
                    if not chunk_data:
                        break  # End of file
                    
                    # Create processing chunk
                    is_last = (self.processed_bytes + len(chunk_data)) >= file_size
                    chunk = ProcessingChunk(
                        offset=self.processed_bytes,
                        size=len(chunk_data),
                        data=chunk_data,
                        is_last=is_last,
                        chunk_id=chunk_id
                    )
                    
                    # Update progress
                    with self._lock:
                        self.processed_bytes += len(chunk_data)
                    
                    # Report progress
                    self._report_progress()
                    
                    yield chunk
                    chunk_id += 1
                    
                    # Small yield to prevent blocking
                    if chunk_id % 10 == 0:
                        time.sleep(0.001)
        
        except MemoryError as e:
            logger.error(f"Memory error during streaming: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during file streaming: {e}")
            raise
        finally:
            self._report_final_stats()
    
    def _get_adaptive_chunk_size(self) -> int:
        """Dynamically adjust chunk size based on memory pressure"""
        memory_percent = self._memory_monitor.get_memory_usage_percent()
        
        if memory_percent < 50:
            # Low memory usage - use larger chunks
            return min(self.config.max_chunk_size, self.config.chunk_size * 2)
        elif memory_percent < 80:
            # Normal memory usage - use default
            return self.config.chunk_size
        else:
            # High memory usage - use smaller chunks
            return max(self.config.min_chunk_size, self.config.chunk_size // 2)
    
    def _check_memory_pressure(self) -> None:
        """Check if system memory pressure is too high"""
        memory_percent = self._memory_monitor.get_memory_usage_percent()
        
        if memory_percent > 95:
            raise MemoryError(f"System memory usage too high: {memory_percent:.1f}%")
        
        # Check process memory limit
        process_memory = self._memory_monitor.get_process_memory_usage()
        if process_memory > self.config.max_memory_per_process:
            raise MemoryError(f"Process memory limit exceeded: "
                            f"{process_memory / 1_000_000:.1f}MB > "
                            f"{self.config.max_memory_per_process / 1_000_000:.1f}MB")
    
    def _report_progress(self) -> None:
        """Report extraction progress to callbacks"""
        current_time = time.time()
        
        # Throttle progress reports
        if current_time - self._last_progress_time < self.config.progress_callback_interval:
            return
        
        if self.total_bytes > 0:
            progress_percent = (self.processed_bytes / self.total_bytes) * 100
        else:
            progress_percent = 0
        
        # Call all registered callbacks
        for callback in self._progress_callbacks:
            try:
                callback(progress_percent, self.processed_bytes, self.total_bytes)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
        
        self._last_progress_time = current_time
        
        # Log progress at key milestones
        if progress_percent in [25, 50, 75, 100]:
            elapsed = current_time - self.start_time
            mb_processed = self.processed_bytes / 1_000_000
            mb_total = self.total_bytes / 1_000_000
            rate = mb_processed / elapsed if elapsed > 0 else 0
            
            logger.info(f"Progress: {progress_percent:.0f}% "
                       f"({mb_processed:.1f}/{mb_total:.1f}MB) "
                       f"Rate: {rate:.1f}MB/s")
    
    def _report_final_stats(self) -> None:
        """Report final extraction statistics"""
        elapsed_time = time.time() - self.start_time
        mb_processed = self.processed_bytes / 1_000_000
        
        if elapsed_time > 0:
            rate = mb_processed / elapsed_time
            logger.info(f"Streaming complete: {mb_processed:.1f}MB in "
                       f"{elapsed_time:.1f}s ({rate:.1f}MB/s)")
        
        # Final progress callback
        for callback in self._progress_callbacks:
            try:
                callback(100.0, self.processed_bytes, self.total_bytes)
            except Exception as e:
                logger.warning(f"Final progress callback failed: {e}")


class MemoryMonitor:
    """Monitors system and process memory usage"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage_percent(self) -> float:
        """Get system memory usage percentage"""
        return psutil.virtual_memory().percent
    
    def get_process_memory_usage(self) -> int:
        """Get current process memory usage in bytes"""
        return self.process.memory_info().rss
    
    def get_available_memory(self) -> int:
        """Get available system memory in bytes"""
        return psutil.virtual_memory().available


class FormatSpecificStreamProcessor(ABC):
    """Abstract base class for format-specific streaming processors"""
    
    def __init__(self, extractor: StreamingMetadataExtractor):
        self.extractor = extractor
        self.metadata = {}
        self.processed_chunks = 0
    
    @abstractmethod
    def process_chunk(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Process a single chunk and return metadata"""
        pass
    
    @abstractmethod
    def finalize(self) -> Dict[str, Any]:
        """Finalize processing and return complete metadata"""
        pass
    
    def merge_metadata(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new metadata with existing metadata"""
        # Simple merge strategy - can be overridden by subclasses
        merged = existing.copy()
        merged.update(new)
        return merged


class DicomStreamProcessor(FormatSpecificStreamProcessor):
    """Streaming processor for DICOM files"""
    
    def __init__(self, extractor: StreamingMetadataExtractor):
        super().__init__(extractor)
        self.header_parsed = False
        self.patient_info = {}
        self.study_info = {}
        self.image_info = {}
    
    def process_chunk(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Process DICOM chunk, focusing on metadata in early chunks"""
        try:
            # Only parse header from first few chunks
            if not self.header_parsed and chunk.chunk_id < 5:
                return self._parse_dicom_header(chunk)
            else:
                # For later chunks, just track progress
                return {'progress': chunk.chunk_id}
                
        except Exception as e:
            logger.warning(f"Error processing DICOM chunk {chunk.chunk_id}: {e}")
            return {'error': str(e)}
    
    def _parse_dicom_header(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Parse DICOM header information from chunk"""
        if chunk.chunk_id == 0:
            # Check for DICOM preamble
            if len(chunk.data) >= 132 and chunk.data[128:132] == b'DICM':
                self.metadata['has_preamble'] = True
                
                # Extract basic header info (simplified)
                # In real implementation, would parse DICOM tags properly
                self.metadata['format'] = 'DICOM'
                self.header_parsed = True
                
                return {
                    'headers': {
                        'format': 'DICOM',
                        'has_preamble': True
                    },
                    'properties': {
                        'chunk_size': chunk.size,
                        'offset': chunk.offset
                    }
                }
        
        return {}
    
    def finalize(self) -> Dict[str, Any]:
        """Finalize DICOM metadata extraction"""
        return {
            'format': 'DICOM',
            'headers': self.metadata,
            'properties': self.properties,
            'statistics': {
                'chunks_processed': self.processed_chunks,
                'streaming_used': True
            }
        }


class FitsStreamProcessor(FormatSpecificStreamProcessor):
    """Streaming processor for FITS files"""
    
    def __init__(self, extractor: StreamingMetadataExtractor):
        super().__init__(extractor)
        self.header_parsed = False
        self.header_cards = {}
    
    def process_chunk(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Process FITS chunk, parsing header from first chunk"""
        try:
            if not self.header_parsed and chunk.chunk_id == 0:
                return self._parse_fits_header(chunk)
            else:
                return {'progress': chunk.chunk_id}
                
        except Exception as e:
            logger.warning(f"Error processing FITS chunk {chunk.chunk_id}: {e}")
            return {'error': str(e)}
    
    def _parse_fits_header(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Parse FITS header from first chunk"""
        if len(chunk.data) >= 2880:  # FITS block size
            # Check for SIMPLE keyword
            header_data = chunk.data[:2880].decode('ascii', errors='ignore')
            
            if 'SIMPLE  =                    T' in header_data:
                self.header_parsed = True
                self.metadata['format'] = 'FITS'
                
                # Parse header cards (simplified)
                cards = [header_data[i:i+80] for i in range(0, len(header_data), 80)]
                for card in cards:
                    if 'END' in card:
                        break
                    if '=' in card:
                        parts = card.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().strip("'\"")
                            if key and value:
                                self.header_cards[key] = value
                
                return {
                    'headers': self.header_cards,
                    'properties': {
                        'format': 'FITS',
                        'header_size': len(header_data)
                    }
                }
        
        return {}
    
    def finalize(self) -> Dict[str, Any]:
        """Finalize FITS metadata extraction"""
        return {
            'format': 'FITS',
            'headers': self.header_cards,
            'properties': self.metadata,
            'statistics': {
                'chunks_processed': self.processed_chunks
            }
        }


class Hdf5StreamProcessor(FormatSpecificStreamProcessor):
    """Streaming processor for HDF5 files"""
    
    def __init__(self, extractor: StreamingMetadataExtractor):
        super().__init__(extractor)
        self.signature_checked = False
        self.structure_info = {}
    
    def process_chunk(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Process HDF5 chunk, checking signature in first chunk"""
        try:
            if not self.signature_checked and chunk.chunk_id == 0:
                return self._check_hdf5_signature(chunk)
            else:
                return {'progress': chunk.chunk_id}
                
        except Exception as e:
            logger.warning(f"Error processing HDF5 chunk {chunk.chunk_id}: {e}")
            return {'error': str(e)}
    
    def _check_hdf5_signature(self, chunk: ProcessingChunk) -> Dict[str, Any]:
        """Check HDF5 signature and extract basic info"""
        if len(chunk.data) >= 8:
            signature = chunk.data[:8]
            
            if signature == b'\x89HDF\r\n\x1a\n':
                self.signature_checked = True
                self.metadata['format'] = 'HDF5'
                self.metadata['signature_valid'] = True
                
                return {
                    'headers': {
                        'format': 'HDF5',
                        'signature_valid': True
                    },
                    'properties': {
                        'chunk_size': chunk.size
                    }
                }
        
        return {}
    
    def finalize(self) -> Dict[str, Any]:
        """Finalize HDF5 metadata extraction"""
        return {
            'format': 'HDF5',
            'headers': self.metadata,
            'properties': self.structure_info,
            'statistics': {
                'chunks_processed': self.processed_chunks
            }
        }


class StreamingProcessorFactory:
    """Factory for creating format-specific streaming processors"""
    
    PROCESSORS = {
        'dicom': DicomStreamProcessor,
        'fits': FitsStreamProcessor,
        'hdf5': Hdf5StreamProcessor,
        'netcdf': Hdf5StreamProcessor,  # Similar processing approach
    }
    
    @classmethod
    def create_processor(cls, format_type: str, extractor: StreamingMetadataExtractor) -> FormatSpecificStreamProcessor:
        """Create a streaming processor for the given format"""
        processor_class = cls.PROCESSORS.get(format_type.lower())
        
        if processor_class:
            return processor_class(extractor)
        else:
            # Return generic processor for unsupported formats
            logger.warning(f"No specific streaming processor for {format_type}, "
                         "using generic processor")
            return FormatSpecificStreamProcessor(extractor)


def extract_with_streaming(filepath: str, format_type: str, config: Optional[StreamingConfig] = None) -> Dict[str, Any]:
    """
    Convenience function for streaming metadata extraction
    
    Args:
        filepath: Path to file
        format_type: Format type (dicom, fits, hdf5, etc.)
        config: Streaming configuration
        
    Returns:
        Extracted metadata dictionary
    """
    extractor = StreamingMetadataExtractor(config)
    processor = StreamingProcessorFactory.create_processor(format_type, extractor)
    
    metadata = {
        'headers': {},
        'properties': {},
        'statistics': {}
    }
    
    try:
        # Stream through file
        for chunk in extractor.stream_file(filepath):
            chunk_metadata = processor.process_chunk(chunk)
            metadata = processor.merge_metadata(metadata, chunk_metadata)
            processor.processed_chunks += 1
        
        # Finalize
        final_metadata = processor.finalize()
        metadata = processor.merge_metadata(metadata, final_metadata)
        
        return {
            'success': True,
            'format': format_type,
            'metadata': metadata,
            'streaming_stats': {
                'chunks_processed': processor.processed_chunks,
                'bytes_processed': extractor.processed_bytes,
                'extraction_time': time.time() - extractor.start_time
            }
        }
        
    except Exception as e:
        logger.error(f"Streaming extraction failed for {filepath}: {e}")
        return {
            'success': False,
            'format': format_type,
            'error': str(e),
            'metadata': metadata
        }
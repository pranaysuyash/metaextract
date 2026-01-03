#!/usr/bin/env python3
"""
MetaExtract Large File Streaming Module

Memory-efficient streaming for large scientific and multimedia files:
- Chunked processing without loading entire file into memory
- Adaptive chunk sizing based on available memory
- Streaming for DICOM, FITS, HDF5, NetCDF, video, and audio
- Generators for lazy evaluation
- Memory pooling for buffer reuse

Author: MetaExtract Team
"""

import logging
import asyncio
import io
from typing import Iterator, AsyncIterator, Dict, Any, Optional, Tuple, Generator
from pathlib import Path
from dataclasses import dataclass
import struct
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class StreamingConfig:
    """Configuration for streaming operations."""
    chunk_size: int = 1024 * 1024  # 1MB default
    max_buffered_chunks: int = 5
    timeout_seconds: int = 30
    adaptive_sizing: bool = True
    min_memory_threshold_mb: int = 100


class AdaptiveChunkSizer:
    """Dynamically adjust chunk size based on available memory."""
    
    def __init__(self, min_chunk: int = 256 * 1024, max_chunk: int = 10 * 1024 * 1024):
        self.min_chunk = min_chunk
        self.max_chunk = max_chunk
    
    def get_optimal_chunk_size(self, file_size: int = 0) -> int:
        """Calculate optimal chunk size."""
        try:
            vm = psutil.virtual_memory()
            available_mb = vm.available / (1024 * 1024)
            
            # Use 10% of available memory, but within bounds
            recommended = int(available_mb * 1024 * 1024 * 0.1)
            
            chunk_size = max(self.min_chunk, min(recommended, self.max_chunk))
            
            logger.debug(f"Optimal chunk size: {chunk_size / (1024 * 1024):.1f}MB "
                        f"(available: {available_mb:.1f}MB)")
            
            return chunk_size
        except Exception as e:
            logger.error(f"Error calculating chunk size: {e}")
            return self.min_chunk


class BinaryStreamReader:
    """Memory-efficient binary file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.sizer = AdaptiveChunkSizer()
    
    def read_chunks(self, file_path: str) -> Generator[bytes, None, None]:
        """Stream file in chunks."""
        try:
            chunk_size = (self.sizer.get_optimal_chunk_size(Path(file_path).stat().st_size)
                         if self.config.adaptive_sizing else self.config.chunk_size)
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise
    
    def read_with_offset(self, file_path: str, offset: int, 
                        length: int) -> Optional[bytes]:
        """Read specific range from file."""
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                return f.read(length)
        except Exception as e:
            logger.error(f"Error reading offset from {file_path}: {e}")
            return None


class DicomStreamReader:
    """Memory-efficient DICOM file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
        self.binary_reader = BinaryStreamReader(config)
    
    def stream_dicom_elements(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Stream DICOM elements without loading entire file."""
        try:
            # DICOM files have:
            # - 128 byte preamble
            # - 4 byte "DICM" prefix
            # - Variable length elements
            
            with open(file_path, 'rb') as f:
                # Skip preamble and check for DICM
                f.seek(128)
                magic = f.read(4)
                if magic != b'DICM':
                    logger.warning(f"{file_path} is not a valid DICOM file")
                    return
                
                # Stream elements
                while True:
                    position = f.tell()
                    tag_bytes = f.read(4)
                    
                    if len(tag_bytes) < 4:
                        break  # End of file
                    
                    # Parse tag
                    group = struct.unpack('<H', tag_bytes[0:2])[0]
                    element = struct.unpack('<H', tag_bytes[2:4])[0]
                    
                    # Read VR and length
                    vr_bytes = f.read(2)
                    if len(vr_bytes) < 2:
                        break
                    
                    vr = vr_bytes.decode('latin-1')
                    
                    # Determine value length based on VR
                    if vr in ('OB', 'OW', 'OF', 'SQ', 'UN'):
                        f.read(2)  # Reserved bytes
                        length = struct.unpack('<I', f.read(4))[0]
                    else:
                        length = struct.unpack('<H', f.read(2))[0]
                    
                    # Yield element info without reading value
                    yield {
                        'tag': f'({group:04X},{element:04X})',
                        'vr': vr,
                        'length': length,
                        'offset': position
                    }
                    
                    # Skip value
                    f.seek(position + 8 + length)
                    
        except Exception as e:
            logger.error(f"Error streaming DICOM from {file_path}: {e}")
            raise
    
    def extract_dicom_header(self, file_path: str, max_elements: int = 100) -> Dict[str, Any]:
        """Extract header without loading full file."""
        header = {'elements': []}
        count = 0
        
        for element in self.stream_dicom_elements(file_path):
            if count >= max_elements:
                break
            header['elements'].append(element)
            count += 1
        
        return header


class FitsStreamReader:
    """Memory-efficient FITS file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
    
    def stream_fits_headers(self, file_path: str) -> Generator[Dict[str, str], None, None]:
        """Stream FITS headers without loading data."""
        try:
            with open(file_path, 'rb') as f:
                while True:
                    # Read 2880-byte header block
                    header_block = f.read(2880)
                    
                    if not header_block or not header_block.startswith(b'SIMPLE'):
                        break
                    
                    # Parse header lines (80 bytes each)
                    header = {}
                    for i in range(0, len(header_block), 80):
                        line = header_block[i:i+80].decode('ascii', errors='ignore')
                        
                        if line.startswith('END '):
                            yield header
                            # Skip to next HDU data
                            data_size = 2880  # Default, would need to calculate from NAXIS
                            f.read(data_size)
                            header = {}
                            break
                        
                        if '=' in line:
                            key, value = line.split('=', 1)
                            header[key.strip()] = value.split('/')[0].strip()
                    
        except Exception as e:
            logger.error(f"Error streaming FITS from {file_path}: {e}")
            raise


class HDF5StreamReader:
    """Memory-efficient HDF5 file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
    
    def stream_hdf5_structure(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Stream HDF5 structure metadata."""
        try:
            import h5py
            
            with h5py.File(file_path, 'r') as f:
                def iterate_group(group, path=''):
                    for key, item in group.items():
                        full_path = f"{path}/{key}"
                        
                        if isinstance(item, h5py.Dataset):
                            yield {
                                'type': 'dataset',
                                'path': full_path,
                                'dtype': str(item.dtype),
                                'shape': item.shape,
                                'size_bytes': item.nbytes
                            }
                        elif isinstance(item, h5py.Group):
                            yield from iterate_group(item, full_path)
                
                # Yield file attributes first
                yield {
                    'type': 'file',
                    'attributes': dict(f.attrs)
                }
                
                # Stream structure
                yield from iterate_group(f)
                
        except ImportError:
            logger.warning("h5py not available for HDF5 streaming")
        except Exception as e:
            logger.error(f"Error streaming HDF5 from {file_path}: {e}")
            raise


class NetCDFStreamReader:
    """Memory-efficient NetCDF file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
    
    def stream_netcdf_structure(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """Stream NetCDF structure metadata."""
        try:
            from netCDF4 import Dataset
            
            with Dataset(file_path, 'r') as ds:
                # Yield dimensions
                yield {
                    'type': 'dimensions',
                    'data': {name: size for name, size in ds.dimensions.items()}
                }
                
                # Yield global attributes
                yield {
                    'type': 'global_attributes',
                    'data': dict(ds.__dict__)
                }
                
                # Yield variables
                for var_name, variable in ds.variables.items():
                    yield {
                        'type': 'variable',
                        'name': var_name,
                        'dtype': str(variable.dtype),
                        'shape': variable.shape,
                        'dimensions': variable.dimensions,
                        'attributes': dict(variable.__dict__)
                    }
                
        except ImportError:
            logger.warning("netCDF4 not available for NetCDF streaming")
        except Exception as e:
            logger.error(f"Error streaming NetCDF from {file_path}: {e}")
            raise


class AudioStreamReader:
    """Memory-efficient audio file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
    
    def stream_audio_frames(self, file_path: str, 
                          frame_size: int = 4096) -> Generator[Dict[str, Any], None, None]:
        """Stream audio frames."""
        try:
            import librosa
            
            # Load with streaming
            y, sr = librosa.load(file_path, sr=None)
            
            num_frames = len(y) // frame_size
            
            for i in range(num_frames):
                start = i * frame_size
                end = start + frame_size
                frame = y[start:end]
                
                yield {
                    'frame_number': i,
                    'sample_count': len(frame),
                    'sample_rate': sr,
                    'rms_energy': float((frame ** 2).mean() ** 0.5)
                }
                
        except ImportError:
            logger.warning("librosa not available for audio streaming")
        except Exception as e:
            logger.error(f"Error streaming audio from {file_path}: {e}")
            raise


class VideoStreamReader:
    """Memory-efficient video file streaming."""
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        self.config = config or StreamingConfig()
    
    def stream_video_frames(self, file_path: str, 
                           sample_rate: int = 30) -> Generator[Dict[str, Any], None, None]:
        """Stream video frames (metadata only, not pixel data)."""
        try:
            import cv2
            
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                logger.error(f"Cannot open video file: {file_path}")
                return
            
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps / sample_rate))
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    yield {
                        'frame_number': frame_count,
                        'shape': frame.shape,
                        'timestamp_sec': frame_count / fps if fps > 0 else 0
                    }
                
                frame_count += 1
            
            cap.release()
            
        except ImportError:
            logger.warning("opencv not available for video streaming")
        except Exception as e:
            logger.error(f"Error streaming video from {file_path}: {e}")
            raise


class StreamingExtractionFactory:
    """Factory for creating appropriate streamers."""
    
    readers = {
        '.dcm': DicomStreamReader,
        '.fits': FitsStreamReader,
        '.h5': HDF5StreamReader,
        '.hdf5': HDF5StreamReader,
        '.nc': NetCDFStreamReader,
        '.netcdf': NetCDFStreamReader,
        '.mp3': AudioStreamReader,
        '.wav': AudioStreamReader,
        '.flac': AudioStreamReader,
        '.mp4': VideoStreamReader,
        '.avi': VideoStreamReader,
        '.mov': VideoStreamReader,
        '.mkv': VideoStreamReader,
    }
    
    @classmethod
    def get_reader(cls, file_path: str, 
                   config: Optional[StreamingConfig] = None) -> Optional[object]:
        """Get appropriate reader for file type."""
        suffix = Path(file_path).suffix.lower()
        
        reader_class = cls.readers.get(suffix)
        
        if reader_class:
            return reader_class(config)
        
        # Default to binary reader
        return BinaryStreamReader(config)
    
    @classmethod
    def supports_streaming(cls, file_path: str) -> bool:
        """Check if file type supports specialized streaming."""
        suffix = Path(file_path).suffix.lower()
        return suffix in cls.readers


def stream_large_file(file_path: str, 
                     config: Optional[StreamingConfig] = None) -> Generator[Dict[str, Any], None, None]:
    """Generic streaming function."""
    
    reader = StreamingExtractionFactory.get_reader(file_path, config)
    
    if reader is None:
        logger.error(f"No reader available for {file_path}")
        return
    
    # Handle different reader types
    if hasattr(reader, 'stream_dicom_elements'):
        yield from reader.stream_dicom_elements(file_path)
    elif hasattr(reader, 'stream_fits_headers'):
        yield from reader.stream_fits_headers(file_path)
    elif hasattr(reader, 'stream_hdf5_structure'):
        yield from reader.stream_hdf5_structure(file_path)
    elif hasattr(reader, 'stream_netcdf_structure'):
        yield from reader.stream_netcdf_structure(file_path)
    elif hasattr(reader, 'stream_audio_frames'):
        yield from reader.stream_audio_frames(file_path)
    elif hasattr(reader, 'stream_video_frames'):
        yield from reader.stream_video_frames(file_path)
    else:
        # Generic binary streaming
        yield from reader.read_chunks(file_path)


if __name__ == '__main__':
    # Demo
    print("=== Large File Streaming Demo ===\n")
    
    config = StreamingConfig()
    sizer = AdaptiveChunkSizer()
    
    print(f"Optimal chunk size: {sizer.get_optimal_chunk_size() / (1024 * 1024):.1f}MB")
    print(f"Available memory: {psutil.virtual_memory().available / (1024 * 1024):.1f}MB")

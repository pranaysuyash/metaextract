# Memory Management Agent - Complete Guide

## Overview

The Memory Management Agent provides comprehensive memory optimization for MetaExtract's metadata extraction operations. It includes:

1. **Real-time memory monitoring** across all extractors
2. **Streaming implementations** for large files (DICOM, FITS, HDF5, NetCDF, Video, Audio)
3. **Memory-efficient processing** strategies based on available resources
4. **Garbage collection optimization** tuned to extraction workloads
5. **Memory pooling** for buffer reuse and reduced allocation overhead

## Architecture

### Core Components

```
MemoryManagementAgent (coordinator)
├── MemoryMonitor (real-time tracking)
├── MemoryAnalyzer (profiling & analysis)
├── GarbageCollectionOptimizer (GC tuning)
├── MemoryResourcePool (buffer pooling)
└── MemoryEfficientExtractor (wrapper)

StreamingExtractionFactory
├── BinaryStreamReader
├── DicomStreamReader
├── FitsStreamReader
├── HDF5StreamReader
├── NetCDFStreamReader
├── AudioStreamReader
└── VideoStreamReader
```

## Task 1: Analyze Memory Usage Patterns

### Memory Profiling

Analyze memory consumption across all extractors:

```python
from server.extractor.memory_management_agent import get_memory_agent

agent = get_memory_agent()

# Get current memory status
status = agent.get_memory_status()
print(f"Memory Level: {status['memory_level']}")
print(f"Available: {status['available_mb']:.1f}MB")
print(f"Used: {status['used_percent']:.1f}%")

# Get comprehensive analysis
report = agent.get_analysis_report()
```

### Memory Analysis Report

```python
# Generate detailed report
report = agent.analyzer.generate_report()
# Returns:
# {
#     'timestamp': '2024-01-03T...',
#     'total_extractions_analyzed': 42,
#     'overall_stats': {
#         'peak_memory_mb': 1024.5,
#         'average_peak_mb': 512.3,
#         'avg_memory_ratio': 2.1,
#     },
#     'profiles': {...},
#     'problematic_extractors': [...]
# }
```

### Per-Extractor Analysis

```python
# Analyze specific extractors
for extractor_name in ['dicom_extractor', 'fits_extractor']:
    stats = agent.analyzer.get_extractor_stats(extractor_name)
    print(f"{extractor_name}:")
    print(f"  Peak Memory: {stats['peak_memory_mb']:.1f}MB")
    print(f"  Avg Ratio: {stats['avg_memory_ratio']:.2f}")
```

### Memory Monitoring

```python
# Start background monitoring
monitor = agent.memory_monitor
monitor.start_monitoring()

# ... perform operations ...

# Get metrics
summary = monitor.get_memory_summary()
print(f"Peak: {summary['peak_mb']:.1f}MB")
print(f"Average: {summary['average_mb']:.1f}MB")
```

## Task 2: Implement Streaming for Large Files

### Using Streaming Extraction

```python
from server.extractor.streaming_large_files import (
    StreamingExtractionFactory,
    StreamingConfig
)

# Auto-detect and stream appropriately
file_path = "large_medical_scan.dcm"
config = StreamingConfig(
    chunk_size=1024 * 1024,  # 1MB chunks
    adaptive_sizing=True,     # Auto-adjust based on memory
    min_file_size_threshold=10 * 1024 * 1024  # 10MB threshold
)

for metadata in StreamingExtractionFactory.get_reader(
    file_path, config
).stream_dicom_elements(file_path):
    # Process each element without loading file
    print(f"Element: {metadata['tag']}")
```

### Format-Specific Streaming

#### DICOM Files
```python
from server.extractor.streaming_large_files import DicomStreamReader

reader = DicomStreamReader()

# Stream elements
for element in reader.stream_dicom_elements('scan.dcm'):
    print(f"Tag: {element['tag']}, VR: {element['vr']}, Length: {element['length']}")

# Extract header only
header = reader.extract_dicom_header('scan.dcm', max_elements=100)
```

#### FITS Files
```python
from server.extractor.streaming_large_files import FitsStreamReader

reader = FitsStreamReader()

for header in reader.stream_fits_headers('hubble.fits'):
    print(f"Header: {header}")
```

#### HDF5 Scientific Data
```python
from server.extractor.streaming_large_files import HDF5StreamReader

reader = HDF5StreamReader()

for structure in reader.stream_hdf5_structure('climate_model.h5'):
    if structure['type'] == 'dataset':
        print(f"Dataset: {structure['path']}, Shape: {structure['shape']}")
```

#### NetCDF Climate Data
```python
from server.extractor.streaming_large_files import NetCDFStreamReader

reader = NetCDFStreamReader()

for item in reader.stream_netcdf_structure('ocean_model.nc'):
    print(f"Type: {item['type']}")
```

#### Audio Files
```python
from server.extractor.streaming_large_files import AudioStreamReader

reader = AudioStreamReader()

for frame in reader.stream_audio_frames('recording.mp3', frame_size=4096):
    print(f"Frame {frame['frame_number']}: RMS={frame['rms_energy']:.3f}")
```

#### Video Files
```python
from server.extractor.streaming_large_files import VideoStreamReader

reader = VideoStreamReader()

for frame_info in reader.stream_video_frames('movie.mp4', sample_rate=30):
    print(f"Frame {frame_info['frame_number']}: {frame_info['timestamp_sec']:.2f}s")
```

### Adaptive Chunk Sizing

```python
from server.extractor.streaming_large_files import AdaptiveChunkSizer

sizer = AdaptiveChunkSizer(
    min_chunk=256 * 1024,      # 256KB minimum
    max_chunk=10 * 1024 * 1024 # 10MB maximum
)

# Get optimal size based on available memory
optimal_size = sizer.get_optimal_chunk_size()
print(f"Recommended chunk size: {optimal_size / (1024 * 1024):.1f}MB")
```

## Task 3: Memory-Efficient Processing

### Extraction Strategies

```python
from server.extractor.memory_management_agent import (
    MemoryEfficientExtractor,
    ExtractionStrategy
)

def my_extraction(file_path):
    # Your extraction logic
    pass

# Wrap with memory optimization
extractor = MemoryEfficientExtractor(my_extraction, 'large_file.dcm')

# Auto-determines strategy based on available memory
result, metrics = extractor.extract_with_optimization()

print(f"Strategy: {metrics['strategy']}")
print(f"Peak Memory: {metrics['peak_memory_mb']:.1f}MB")
print(f"Memory Ratio: {metrics['memory_ratio']:.2f}x file size")
```

### Strategy Selection

```
Available Memory        Strategy
═════════════════════════════════════════
> 3x file size      AGGRESSIVE (fast, high memory)
1-3x file size      BALANCED (good for most cases)
< 1x file size      CONSERVATIVE (streaming, low memory)
```

### Buffer Pooling

```python
from server.extractor.memory_management_agent import MemoryResourcePool

# Create pool with 10MB buffers
pool = MemoryResourcePool(buffer_size=10 * 1024 * 1024)

# Allocate buffer (reused from pool if available)
buffer = pool.allocate_buffer()

# Use buffer for processing
process_data(buffer)

# Return to pool for reuse
pool.release_buffer(buffer)

# Check stats
stats = pool.get_stats()
print(f"Allocations: {stats['allocations']}")
print(f"Reuses: {stats['reuses']}")
print(f"Currently available: {stats['currently_available']}")
```

## Task 4: Garbage Collection Optimization

### Optimizing GC for Extraction

```python
from server.extractor.memory_management_agent import (
    GarbageCollectionOptimizer,
    ExtractionStrategy
)

optimizer = GarbageCollectionOptimizer()

# Optimize for different workloads
optimizer.optimize_for_extraction(ExtractionStrategy.AGGRESSIVE)
# GC threshold: (5000, 10, 10) - less frequent collections

optimizer.optimize_for_extraction(ExtractionStrategy.BALANCED)
# GC threshold: (700, 10, 10) - default balanced

optimizer.optimize_for_extraction(ExtractionStrategy.CONSERVATIVE)
# GC threshold: (100, 5, 5) - more frequent collections
```

### GC Control

```python
# Enable incremental collection (Python 3.13+)
optimizer.enable_incremental_collection()

# Disable GC during critical section
optimizer.disable_collection_during_critical()
try:
    # Time-critical extraction
    result = fast_extraction()
finally:
    # Re-enable GC
    optimizer.enable_collection()

# Force collection and free memory
freed = optimizer.force_collection()
print(f"Freed {freed} objects")

# Get current config
config = optimizer.get_current_config()
print(f"Thresholds: {config['thresholds']}")

# Reset to default
optimizer.reset_to_default()
```

### Memory Leak Detection

```python
# Detect unreachable objects (potential leaks)
unreachable = optimizer.get_unreachable_objects()
if unreachable > 100:
    logger.warning(f"Potential memory leak: {unreachable} unreachable objects")
```

## Integration Examples

### Full Extraction with Memory Management

```python
from server.extractor.memory_management_agent import get_memory_agent
from server.extractor.streaming_large_files import StreamingExtractionFactory

agent = get_memory_agent()

def extract_file_efficiently(file_path):
    """Extract with full memory optimization."""
    
    # Get status
    status = agent.get_memory_status()
    logger.info(f"Memory level: {status['memory_level']}")
    
    # Check if streaming needed
    file_size = Path(file_path).stat().st_size / (1024 * 1024)
    
    if file_size > 50:  # > 50MB
        logger.info("Using streaming extraction")
        
        reader = StreamingExtractionFactory.get_reader(file_path)
        
        metadata_list = []
        for chunk_metadata in reader.stream_dicom_elements(file_path):
            metadata_list.append(chunk_metadata)
            
            # Periodic optimization
            if len(metadata_list) % 100 == 0:
                agent.gc_optimizer.force_collection()
        
        return {'extracted_elements': len(metadata_list)}
    else:
        logger.info("Using standard extraction")
        # Standard extraction
        return extract_standard(file_path)

# Execute
result = extract_file_efficiently('large_scan.dcm')

# Get analysis
report = agent.get_analysis_report()
```

### Batch Processing with Memory Awareness

```python
def batch_extract_with_memory_control(file_list):
    """Process batch with memory-aware scheduling."""
    
    agent = get_memory_agent()
    results = []
    
    for file_path in file_list:
        # Check memory before each file
        status = agent.get_memory_status()
        
        if status['memory_level'] == 'critical':
            logger.warning("Memory critical, forcing collection")
            agent.gc_optimizer.force_collection()
            time.sleep(1)  # Brief pause for collection
        
        # Extract with optimization
        result, metrics = agent.execute_extraction(
            file_path,
            extract_function,
            *args
        )
        results.append((file_path, result, metrics))
    
    return results
```

## Performance Metrics

### Memory Monitoring Example

```python
monitor = MemoryMonitor()
monitor.start_monitoring()

# ... perform extraction ...

summary = monitor.get_memory_summary()
print(f"""
Memory Profile:
  Current: {summary['current'].resident_mb:.1f}MB
  Peak: {summary['peak_mb']:.1f}MB
  Average: {summary['average_mb']:.1f}MB
  Snapshots: {summary['snapshots_collected']}
""")
```

### Profile Analysis Example

```python
analyzer = MemoryAnalyzer()

# Profile extraction
result, profile = analyzer.analyze_extraction(
    'large_file.h5',
    file_size_mb=500,
    extraction_func=extract_hdf5,
    file_path='large_file.h5'
)

print(f"""
Extraction Profile:
  File: {Path(profile.file_path).name}
  Peak Memory: {profile.peak_memory_mb:.1f}MB
  Memory Ratio: {profile.memory_ratio:.2f}x
  Time: {profile.extraction_time_sec:.2f}s
""")
```

## Configuration

### Custom StreamingConfig

```python
from server.extractor.streaming_large_files import StreamingConfig

config = StreamingConfig(
    chunk_size=2 * 1024 * 1024,      # 2MB chunks
    max_buffered_chunks=10,           # Keep 10 chunks in memory
    timeout_seconds=60,               # 60s timeout per chunk
    adaptive_sizing=True,             # Auto-adjust chunk size
    min_memory_threshold_mb=200       # Use streaming for < 200MB free
)
```

### Custom MemoryEfficientExtractor

```python
from server.extractor.memory_management_agent import MemoryEfficientExtractor

# Custom wrapper with specific strategies
extractor = MemoryEfficientExtractor(
    extraction_func=my_func,
    file_path='file.dcm'
)

# Use conservative strategy
strategy = ExtractionStrategy.CONSERVATIVE
result, metrics = extractor.extract_with_optimization()
```

## Troubleshooting

### High Memory Usage

```python
# Analyze problematic extractors
problematic = agent.analyzer.get_problematic_extractors(threshold_ratio=3.0)
for ext in problematic:
    stats = agent.analyzer.get_extractor_stats(ext)
    logger.warning(f"High memory usage in {ext}: {stats}")

# Force optimization
agent.optimize_all()
```

### Memory Leaks

```python
# Check for unreachable objects
optimizer = GarbageCollectionOptimizer()
unreachable = optimizer.get_unreachable_objects()

if unreachable > 0:
    logger.error(f"Potential leak: {unreachable} unreachable objects")
    # Investigate extraction functions for circular references
```

### Slow Extraction

```python
# Check memory strategy
extractor = MemoryEfficientExtractor(func, file_path)
strategy = extractor.determine_strategy()
logger.info(f"Strategy: {strategy.value}")

# If CONSERVATIVE, may be slower but more memory-efficient
# Consider using larger buffer if available memory allows
```

## Best Practices

1. **Monitor Large Batch Operations**: Use memory monitoring for batch extractions
2. **Stream Files > 50MB**: Enable streaming for large scientific/multimedia files
3. **Profile Extractors**: Regularly run analysis to identify bottlenecks
4. **Tune GC**: Adjust GC strategy based on workload
5. **Use Buffer Pooling**: Reuse buffers for repeated extractions
6. **Check Memory Before Processing**: Verify available resources before starting
7. **Handle Memory Pressure**: Gracefully degrade to conservative strategy
8. **Monitor for Leaks**: Periodically check for unreachable objects

## Testing

Run the comprehensive test suite:

```bash
# All memory management tests
pytest tests/test_memory_management.py -v

# Specific test class
pytest tests/test_memory_management.py::TestMemoryMonitor -v

# Performance benchmarks
pytest tests/test_memory_management.py::TestMemoryPerformance -v
```

## Performance Improvements

Expected improvements with memory management:

- **Streaming**: 60-80% reduction in peak memory for large files
- **Buffer Pooling**: 30-40% faster allocation with reused buffers
- **GC Optimization**: 20-30% improvement in extraction speed
- **Overall**: 2-4x better throughput for batch operations

## Dependencies

```
psutil >= 5.8.0       # Memory monitoring
h5py >= 3.0.0         # HDF5 streaming (optional)
netCDF4 >= 1.5.0      # NetCDF streaming (optional)
librosa >= 0.9.0      # Audio streaming (optional)
opencv-python >= 4.5.0 # Video streaming (optional)
```

## Future Enhancements

- GPU memory monitoring
- Machine learning-based strategy selection
- Distributed memory management across nodes
- Advanced prefetching strategies
- Real-time memory visualization dashboard

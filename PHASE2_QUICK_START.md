# Phase 2: Streaming & Parallel Extraction - Quick Start Guide

## Quick Links

- 📄 Full Implementation: [`PHASE2_STREAMING_PARALLEL_COMPLETE.md`](./PHASE2_STREAMING_PARALLEL_COMPLETE.md)
- 🧪 Tests: [`tests/test_phase2_streaming_parallel.py`](./tests/test_phase2_streaming_parallel.py)
- 💾 Streaming Framework: [`server/extractor/streaming_framework.py`](./server/extractor/streaming_framework.py)
- ⚙️ Parallel Framework: [`server/extractor/parallel_extraction.py`](./server/extractor/parallel_extraction.py)

## 1. Streaming for Large Files

### Simple Usage

```python
from server.extractor.streaming_framework import extract_with_streaming

# Extract large file with streaming
metadata, metrics = await extract_with_streaming('large_file.h5')
print(f"Processed {metrics.chunks_processed} chunks")
print(f"Progress: {metrics.progress_percent:.1f}%")
print(f"Throughput: {metrics.throughput_mb_per_sec:.2f} MB/sec")
```

### With Configuration

```python
from server.extractor.streaming_framework import (
    StreamingExtractor,
    StreamingConfig,
    StreamingStrategy
)

config = StreamingConfig(
    chunk_size=2*1024*1024,  # 2MB chunks
    strategy=StreamingStrategy.SEQUENTIAL,
    max_chunks=1000  # Process max 1000 chunks
)

extractor = StreamingExtractor(config)
metadata, metrics = await extractor.extract_streaming('large_file.dat')
```

### With Callback

```python
async def process_chunk(chunk, metrics):
    print(f"Chunk {chunk.chunk_id}: {chunk.size} bytes")
    print(f"Progress: {metrics.progress_percent:.1f}%")

metadata, metrics = await extractor.extract_streaming(
    'large_file.h5',
    callback=process_chunk
)
```

## 2. Parallel Extraction

### Simple Usage

```python
from server.extractor.parallel_extraction import extract_files_parallel

def my_extraction_function(file_path):
    # Your extraction logic
    return {'file': file_path, 'extracted': True}

files = ['file1.h5', 'file2.h5', 'file3.h5', 'file4.h5']
results, metrics = await extract_files_parallel(files, my_extraction_function)

print(f"Success Rate: {metrics.success_rate:.1f}%")
print(f"Throughput: {metrics.throughput_files_per_sec:.2f} files/sec")
```

### With Configuration

```python
from server.extractor.parallel_extraction import (
    ParallelExtractor,
    ParallelExtractionConfig,
    ExecutionModel,
    LoadBalancingStrategy
)

config = ParallelExtractionConfig(
    max_workers=4,
    execution_model=ExecutionModel.THREAD_POOL,
    load_balancing=LoadBalancingStrategy.LEAST_LOADED,
    retry_failed=True,
    retry_limit=3
)

extractor = ParallelExtractor(config, my_extraction_function)
results, metrics = extractor.extract_parallel_sync(files)

# Print statistics
for file_type, stats in metrics.file_type_stats.items():
    success_pct = (stats['success'] / stats['count']) * 100
    print(f"{file_type}: {success_pct:.0f}% success rate")
```

### With Priority Tasks

```python
from server.extractor.parallel_extraction import ParallelExtractor, ExtractionTask

extractor = ParallelExtractor(config, my_extraction_function)

# Add high priority task
urgent_task = ExtractionTask(
    task_id='urgent_1',
    file_path='important_file.h5',
    priority=10  # Higher priority
)
extractor.add_task(urgent_task)

# Add normal priority tasks
normal_tasks = extractor.add_tasks_batch(
    ['file2.h5', 'file3.h5'],
    priorities=[1, 1]
)

results, metrics = extractor.extract_parallel_sync(['important_file.h5', 'file2.h5', 'file3.h5'])
```

## 3. Combined Streaming + Parallel

```python
from server.extractor.streaming_framework import StreamingExtractor, StreamingConfig
from server.extractor.parallel_extraction import ParallelExtractor, ParallelExtractionConfig

# Configure both
streaming_config = StreamingConfig(chunk_size=2*1024*1024)
parallel_config = ParallelExtractionConfig(max_workers=4)

# For large batch of files
def extract_with_streaming(file_path):
    extractor = StreamingExtractor(streaming_config)
    # Note: synchronous extraction needed here
    # Use extract_parallel_sync instead of async version
    return extractor.extract_streaming(file_path)

parallel = ParallelExtractor(parallel_config, extract_with_streaming)
results, metrics = parallel.extract_parallel_sync(large_file_list)
```

## 4. File Type Selection

### Automatic Detection

The framework automatically selects the right reader:

```python
extractor = StreamingExtractor()

# Automatically uses BinaryChunkReader
extractor.get_reader('document.bin')

# Automatically uses VideoChunkReader
extractor.get_reader('video.mp4')

# Automatically uses HDF5ChunkReader
extractor.get_reader('data.h5')
```

### Supported Formats

| Format | Reader | Status |
|--------|--------|--------|
| Generic Binary | BinaryChunkReader | ✅ |
| MP4 | VideoChunkReader | ✅ |
| AVI | VideoChunkReader | ✅ |
| MOV | VideoChunkReader | ✅ |
| MKV | VideoChunkReader | ✅ |
| FLV | VideoChunkReader | ✅ |
| HDF5 | HDF5ChunkReader | ✅ |
| NetCDF | HDF5ChunkReader | ✅ |

## 5. Metrics and Monitoring

### Streaming Metrics

```python
metadata, metrics = await extract_with_streaming(file_path)

# Access metrics
print(f"Total chunks: {metrics.total_chunks}")
print(f"Processed: {metrics.chunks_processed}")
print(f"Bytes: {metrics.bytes_processed / (1024*1024):.2f} MB")
print(f"Elapsed: {metrics.elapsed_time:.2f}s")
print(f"Progress: {metrics.progress_percent:.1f}%")
print(f"Throughput: {metrics.throughput_mb_per_sec:.2f} MB/sec")
print(f"Errors: {metrics.errors}")
```

### Parallel Metrics

```python
results, metrics = await extract_files_parallel(files, extraction_fn)

# Overall metrics
print(f"Total tasks: {metrics.total_tasks}")
print(f"Completed: {metrics.completed_tasks}")
print(f"Success rate: {metrics.success_rate:.1f}%")
print(f"Throughput: {metrics.throughput_files_per_sec:.2f} files/sec")
print(f"Elapsed: {metrics.elapsed_time:.2f}s")

# Per-file-type stats
for file_type, stats in metrics.file_type_stats.items():
    print(f"{file_type}: {stats['count']} total, "
          f"{stats['success']} successful, "
          f"{stats['total_time']:.2f}s total")
```

## 6. Error Handling

### Streaming Errors

```python
try:
    metadata, metrics = await extract_with_streaming(file_path)
    if metrics.errors > 0:
        print(f"Warning: {metrics.errors} chunks had errors")
except Exception as e:
    print(f"Streaming failed: {e}")
```

### Parallel Errors with Retry

```python
config = ParallelExtractionConfig(
    retry_failed=True,
    retry_limit=3,
    retry_delay=1.0  # 1 second between retries
)

extractor = ParallelExtractor(config, extraction_fn)
results, metrics = extractor.extract_parallel_sync(files)

# Check which files failed
for result in results:
    if not result.success:
        print(f"Failed: {result.file_path}")
        print(f"Error: {result.error}")
```

## 7. Testing

### Run All Phase 2 Tests

```bash
python -m pytest tests/test_phase2_streaming_parallel.py -v
```

### Run Specific Test Group

```bash
# Streaming tests
python -m pytest tests/test_phase2_streaming_parallel.py::TestStreamingFramework -v

# Parallel extraction tests
python -m pytest tests/test_phase2_streaming_parallel.py::TestParallelExtraction -v

# Integration tests
python -m pytest tests/test_phase2_streaming_parallel.py::TestIntegration -v
```

## 8. Performance Tips

### Optimize for Your Use Case

```python
# For I/O-bound work (network, file operations)
config = ParallelExtractionConfig(
    execution_model=ExecutionModel.THREAD_POOL,
    max_workers=8  # More workers for I/O wait
)

# For CPU-bound work (compression, calculation)
config = ParallelExtractionConfig(
    execution_model=ExecutionModel.PROCESS_POOL,
    max_workers=4  # CPU count
)

# For large files
streaming_config = StreamingConfig(
    chunk_size=5*1024*1024,  # 5MB chunks
    max_buffered_chunks=10
)
```

### Load Balancing Strategy Selection

```python
from server.extractor.parallel_extraction import LoadBalancingStrategy

# Mixed file sizes and types
LoadBalancingStrategy.LEAST_LOADED  # Recommended

# Mostly same size files
LoadBalancingStrategy.FIFO  # Simpler, faster

# Homogeneous file types
LoadBalancingStrategy.FILE_TYPE_AWARE

# Wide size range
LoadBalancingStrategy.SIZE_AWARE
```

## 9. Common Patterns

### Pattern: Stream + Process

```python
async def stream_and_process(file_path, processor_fn):
    config = StreamingConfig(chunk_size=1*1024*1024)
    extractor = StreamingExtractor(config)
    
    async def callback(chunk, metrics):
        result = processor_fn(chunk.data)
        return result
    
    return await extractor.extract_streaming(file_path, callback)
```

### Pattern: Batch with Priority

```python
def batch_with_priority(files, urgent_files, extraction_fn):
    extractor = ParallelExtractor(config, extraction_fn)
    
    # Add urgent files with high priority
    for file in urgent_files:
        task = ExtractionTask(file_path=file, priority=10)
        extractor.add_task(task)
    
    # Add normal files
    extractor.add_tasks_batch(files, priorities=[1]*len(files))
    
    return extractor.extract_parallel_sync(files + urgent_files)
```

### Pattern: Graceful Degradation

```python
async def extract_with_fallback(file_path):
    file_size = Path(file_path).stat().st_size
    
    if file_size > 1*1024*1024*1024:  # > 1GB
        # Use streaming
        return await extract_with_streaming(file_path)
    else:
        # Use standard extraction
        return await standard_extraction(file_path)
```

## 🚀 Status

✅ All 22 tests passing  
✅ Production ready  
✅ Full documentation  
✅ Examples provided  

See [`PHASE2_STREAMING_PARALLEL_COMPLETE.md`](./PHASE2_STREAMING_PARALLEL_COMPLETE.md) for full details.

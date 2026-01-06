# Redis Caching System Integration Guide

## Overview

The Redis caching system provides comprehensive caching for metadata extraction results to address performance bottlenecks identified in profiling. The system caches:

1. **Complete extraction results** - Avoid re-running entire extraction pipelines
2. **Individual module results** - Cache results from specific extractors (491 modules)
3. **Geocoding results** - Enhanced caching for GPS → address conversions
4. **Perceptual hash calculations** - Cache CPU-intensive hash calculations (2.8% of time)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cache Manager                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Unified Cache Interface                │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                 │
│  ┌──────────┬─────────────┼─────────────┬────────────────┐    │
│  │          │             │             │                │    │
│  ▼          ▼             ▼             ▼                ▼    │
│┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐ │
││Extraction││  Module  ││Geocoding ││Perceptual││  Redis   │ │
││  Cache   ││  Cache   ││  Cache   ││  Cache   ││ Client   │ │
│└──────────┘└──────────┘└──────────┘└──────────┘└──────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                  ┌─────────▼──────────┐
                  │   Extraction       │
                  │   Orchestrator     │
                  └────────────────────┘
```

## Usage

### Basic Usage

```python
from server.cache.cache_manager import get_cache_manager
from server.extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor

# Enable caching extractor
extractor = NewComprehensiveMetadataExtractor(enable_caching=True)

# Extract with automatic caching
result = extractor.extract_comprehensive_metadata("/path/to/file.jpg", tier="premium")

# Check if result was cached
if result.get('extraction_info', {}).get('cache_hit'):
    print("Result served from cache!")
```

### Advanced Usage

```python
from server.cache.cache_manager import get_cache_manager

# Get cache manager for manual operations
cache_manager = get_cache_manager()

# Get cached extraction result
cached_result = cache_manager.get_extraction_result("/path/to/file.jpg", tier="premium")

# Cache module result manually
cache_manager.cache_module_result(
    module_result={"gps": {"latitude": 40.7128, "longitude": -74.0060}},
    module_name="gps_extractor",
    file_path="/path/to/file.jpg",
    execution_time_ms=150
)

# Invalidate cache for a file
invalidated_count = cache_manager.invalidate_file("/path/to/file.jpg")
print(f"Invalidated {invalidated_count} cache entries")
```

### Geocoding with Enhanced Caching

```python
from server.cache.geocoding_cache import GeocodingCache

# Use enhanced geocoding with Redis caching
from server.extractor.modules.geocoding_cached import reverse_geocode_cached

result = reverse_geocode_cached(40.7128, -74.0060, use_cache=True)

# Batch geocoding with caching
from server.extractor.modules.geocoding_cached import batch_reverse_geocode

coordinates = [(40.7128, -74.0060), (34.0522, -118.2437)]
results = batch_reverse_geocode(coordinates, use_cache=True)
```

### Perceptual Hash Caching

```python
from server.extractor.modules.perceptual_hashes_cached import extract_perceptual_hashes_cached

# Extract with caching
result = extract_perceptual_hashes_cached("/path/to/image.jpg", enable_cache=True)

# Batch processing with caching
from server.extractor.modules.perceptual_hashes_cached import batch_extract_perceptual_hashes

file_paths = ["/path/to/image1.jpg", "/path/to/image2.jpg"]
results = batch_extract_perceptual_hashes(file_paths, enable_cache=True)
```

## Cache Configuration

### TTL Values

- **Extraction results**: 1 hour (adjustable by tier)
  - Free tier: 1 hour
  - Premium tier: 1.5 hours
  - Super tier: 2 hours
  
- **Module results**: 2-4 hours (based on execution time)
  - Fast modules (< 100ms): 2 hours
  - Moderate modules (100-1000ms): 3 hours
  - Expensive modules (> 1000ms): 4 hours
  
- **Geocoding results**: 24 hours (configurable)
  
- **Perceptual hashes**: 6-12 hours (based on calculation time)
  - Fast calculations (< 1s): 6 hours
  - Expensive calculations (> 1s): 9-12 hours

### Cache Keys

Cache keys are generated using:
- File content hash (SHA256 of file content/size/mtime)
- Extraction tier
- Module name (for module caching)
- Algorithm parameters (for perceptual hashes)
- Coordinates (for geocoding, with precision handling)

Example keys:
- `extraction:a1b2c3d4_premium`
- `module:exif_a1b2c3d4`
- `geocoding:40.712800_-74.006000_nominatim_en`
- `perceptual:phash_a1b2c3d4_8`

## Integration Points

### 1. Extraction Orchestrator

The `CachingExtractionOrchestrator` extends the base orchestrator with:

```python
class CachingExtractionOrchestrator(ExtractionOrchestrator):
    def extract_metadata(self, filepath, tier="free", parallel=True, 
                        max_workers=4, force_refresh=False):
        # Check cache first
        cached_result = self.cache_manager.get_extraction_result(filepath, tier)
        if cached_result:
            return cached_result
        
        # Perform extraction and cache result
        result = super().extract_metadata(filepath, tier, parallel, max_workers)
        self.cache_manager.cache_extraction_result(result, filepath, tier)
        return result
```

### 2. Module Integration

Individual modules can use caching:

```python
def extract_with_caching(filepath, enable_cache=True):
    if enable_cache:
        cached_result = cache_manager.get_module_result("module_name", filepath)
        if cached_result:
            return cached_result
    
    # Perform extraction
    result = perform_extraction(filepath)
    
    if enable_cache:
        cache_manager.cache_module_result(result, "module_name", filepath)
    
    return result
```

### 3. Geocoding Integration

Enhanced geocoding module:

```python
def reverse_geocode_cached(lat, lon, use_cache=True):
    if use_cache:
        cached_result = cache_manager.get_geocoding_result(lat, lon)
        if cached_result:
            return cached_result
    
    # Perform geocoding
    result = perform_geocoding(lat, lon)
    
    if use_cache:
        cache_manager.cache_geocoding_result(result, lat, lon)
    
    return result
```

## Performance Benefits

Based on profiling data:

1. **Complete extraction caching**: Avoids 491 module executions per file
   - Time saved: 2-5 seconds per cached extraction
   - Hit rate: Expected 60-80% for typical usage patterns

2. **Module caching**: Avoids re-running expensive individual modules
   - Geocoding: ~200ms saved per cached lookup
   - Perceptual hashes: ~2-5 seconds saved per cached calculation
   - Complex analysis modules: Variable savings based on complexity

3. **Geocoding caching**: 24-hour TTL for stable location data
   - Typical usage: Multiple files from same location
   - Network latency saved: ~100-500ms per lookup

4. **Perceptual hash caching**: CPU-intensive operations cached
   - 2.8% of total processing time eliminated for cached hits
   - Batch processing improvements for image similarity workflows

## Monitoring and Statistics

### Get Cache Statistics

```python
# Get comprehensive stats
stats = cache_manager.get_stats()
print(f"Overall hit rate: {stats['overall_stats']['overall_hit_rate_percent']}%")

# Get performance summary
perf_summary = cache_manager.get_performance_summary()
print(f"Time saved: {perf_summary['cache_effectiveness']['time_saved_hours']} hours")

# Get health status
health = cache_manager.health_check()
print(f"Cache health: {health['overall_status']}")
```

### Expensive Operations Tracking

```python
# Find expensive modules
expensive_modules = cache_manager.module_cache.get_expensive_modules(threshold_ms=1000)

# Find expensive perceptual calculations
expensive_calcs = cache_manager.perceptual_cache.get_expensive_calculations(threshold_ms=1000)
```

## Cache Invalidation

### Automatic Invalidation

Cache entries are automatically invalidated when:
- File content changes (based on file hash)
- File modification time changes
- Module parameters change

### Manual Invalidation

```python
# Invalidate specific file
invalidate_file_caches("/path/to/file.jpg")

# Invalidate specific coordinates
cache_manager.invalidate_coordinates(40.7128, -74.0060)

# Clear all caches
cache_manager.clear_all_caches()
```

## Error Handling

The caching system includes comprehensive error handling:

1. **Redis connection failures**: Graceful fallback to no caching
2. **Serialization errors**: Fallback to original extraction
3. **Cache corruption**: Automatic invalidation and re-extraction
4. **Network timeouts**: Configurable timeouts with retries

## Configuration

### Environment Variables

```bash
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional

# Cache behavior
CACHE_ENABLED=true
CACHE_TTL_HOURS=24
CACHE_COMPRESSION=true
```

### Cache Manager Configuration

```python
# Create cache manager with custom settings
cache_manager = CacheManager()
cache_manager.cache_enabled = True
cache_manager.auto_invalidation = True
cache_manager.performance_monitoring = True
```

## Testing

Run the comprehensive test suite:

```bash
python test_caching_system.py
```

The test suite validates:
- Redis connectivity
- All cache types (extraction, module, geocoding, perceptual)
- Integration with extraction pipeline
- Performance monitoring
- Cache invalidation
- Error handling

## Migration Guide

### From Existing System

1. **Update imports**:
   ```python
   # Old
   from server.extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor
   
   # New (caching enabled by default)
   from server.extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor
   extractor = NewComprehensiveMetadataExtractor(enable_caching=True)
   ```

2. **Update geocoding calls**:
   ```python
   # Old
   from server.extractor.modules.geocoding import reverse_geocode
   
   # New
   from server.extractor.modules.geocoding_cached import reverse_geocode_cached
   ```

3. **Update perceptual hash calls**:
   ```python
   # Old
   from server.extractor.modules.perceptual_hashes import extract_perceptual_hashes
   
   # New
   from server.extractor.modules.perceptual_hashes_cached import extract_perceptual_hashes_cached
   ```

### Backward Compatibility

The caching system maintains full backward compatibility:
- Original function signatures preserved
- Optional caching (can be disabled)
- Fallback to original modules if caching fails
- Same response format and structure

## Troubleshooting

### Common Issues

1. **Redis connection failed**:
   - Check Redis server is running
   - Verify connection parameters
   - Check firewall/network settings

2. **Cache not working**:
   - Verify `enable_caching=True` in extractor initialization
   - Check Redis connectivity
   - Review logs for cache-related warnings

3. **Performance not improved**:
   - Check cache hit rates in statistics
   - Verify files are not being modified between requests
   - Consider cache warming for frequently accessed files

### Debug Logging

Enable debug logging:

```python
import logging
logging.getLogger("metaextract.cache").setLevel(logging.DEBUG)
```

## Future Enhancements

- **Distributed caching**: Multi-node Redis cluster support
- **Cache warming**: Pre-populate cache for known files
- **Smart invalidation**: More sophisticated invalidation strategies
- **Compression**: Optional compression for large metadata results
- **Analytics**: Detailed usage analytics and optimization suggestions
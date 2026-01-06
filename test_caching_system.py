#!/usr/bin/env python3
"""
Test script for the Redis caching system

Tests all caching functionality including:
- Extraction result caching
- Module result caching
- Geocoding caching
- Perceptual hash caching
- Cache invalidation
- Performance monitoring
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Import cache components
from server.cache.cache_manager import get_cache_manager, invalidate_file_caches
from server.cache.extraction_cache import ExtractionCache
from server.cache.module_cache import ModuleCache
from server.cache.geocoding_cache import GeocodingCache
from server.cache.perceptual_cache import PerceptualHashCache
from server.cache.redis_client import get_redis_client

# Import test utilities
from server.extractor.core.comprehensive_engine import NewComprehensiveMetadataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_redis_connection():
    """Test Redis connection."""
    print("=== Testing Redis Connection ===")
    
    try:
        redis_client = get_redis_client()
        if redis_client.is_connected:
            print("✓ Redis connected successfully")
            info = redis_client.info()
            if info:
                print(f"✓ Redis version: {info.get('redis_version', 'unknown')}")
                print(f"✓ Used memory: {info.get('used_memory_human', 'unknown')}")
            return True
        else:
            print("✗ Redis not connected")
            return False
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False


def test_cache_manager():
    """Test cache manager initialization."""
    print("\n=== Testing Cache Manager ===")
    
    try:
        cache_manager = get_cache_manager()
        print("✓ Cache manager initialized successfully")
        
        # Test health check
        health = cache_manager.health_check()
        print(f"✓ Cache health: {health.get('overall_status', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"✗ Cache manager failed: {e}")
        return False


def test_extraction_cache():
    """Test extraction result caching."""
    print("\n=== Testing Extraction Cache ===")
    
    try:
        cache = ExtractionCache()
        
        # Create a mock extraction result
        mock_result = {
            "metadata": {
                "test_field": "test_value",
                "processing_time": 1000
            },
            "extraction_info": {
                "status": "success",
                "extractors_used": 5
            }
        }
        
        # Test file path
        test_file = "/tmp/test_image.jpg"
        
        # Cache the result
        cache_success = cache.cache_result(mock_result, test_file, tier="premium", processing_time_ms=1000)
        print(f"✓ Cache result: {'success' if cache_success else 'failed'}")
        
        # Retrieve from cache
        cached_result = cache.get_cached_result(test_file, tier="premium")
        if cached_result:
            print("✓ Cache retrieval successful")
            print(f"  - Cache hit: {cached_result.get('cache_info', {}).get('hit', False)}")
            print(f"  - Test field: {cached_result.get('metadata', {}).get('test_field')}")
        else:
            print("✗ Cache retrieval failed")
        
        # Test cache stats
        stats = cache.get_stats()
        print(f"✓ Cache stats: hits={stats['stats']['hits']}, misses={stats['stats']['misses']}")
        
        # Cleanup
        cache.invalidate_file(test_file)
        
        return True
    except Exception as e:
        print(f"✗ Extraction cache test failed: {e}")
        return False


def test_module_cache():
    """Test module result caching."""
    print("\n=== Testing Module Cache ===")
    
    try:
        cache = ModuleCache()
        
        # Test module caching
        module_name = "test_module"
        test_file = "/tmp/test_file.jpg"
        module_result = {"test_field": "module_value", "confidence": 0.95}
        
        # Cache module result
        cache_success = cache.cache_result(
            module_result, module_name, test_file, execution_time_ms=500
        )
        print(f"✓ Module cache result: {'success' if cache_success else 'failed'}")
        
        # Retrieve module result
        cached_result = cache.get_cached_result(module_name, test_file)
        if cached_result:
            print("✓ Module cache retrieval successful")
            print(f"  - Cache hit: {cached_result.get('cache_info', {}).get('hit', False)}")
            print(f"  - Module result: {cached_result.get('result', {}).get('test_field')}")
        else:
            print("✗ Module cache retrieval failed")
        
        # Test module stats
        stats = cache.get_module_stats(module_name)
        print(f"✓ Module stats: keys={stats.get('module_keys', 0)}")
        
        # Cleanup
        cache.invalidate_module(module_name, test_file)
        
        return True
    except Exception as e:
        print(f"✗ Module cache test failed: {e}")
        return False


def test_geocoding_cache():
    """Test geocoding result caching."""
    print("\n=== Testing Geocoding Cache ===")
    
    try:
        cache = GeocodingCache()
        
        # Test coordinates (New York City)
        test_lat, test_lon = 40.7128, -74.0060
        
        # Create mock geocoding result
        mock_geocode = {
            "display_name": "New York City, NY, USA",
            "address": {
                "city": "New York City",
                "state": "New York",
                "country": "United States"
            }
        }
        
        # Cache the result
        cache_success = cache.cache_result(mock_geocode, test_lat, test_lon)
        print(f"✓ Geocoding cache result: {'success' if cache_success else 'failed'}")
        
        # Retrieve from cache
        cached_result = cache.get_cached_result(test_lat, test_lon)
        if cached_result:
            print("✓ Geocoding cache retrieval successful")
            print(f"  - Cache hit: {cached_result.get('cache_info', {}).get('hit', False)}")
            print(f"  - Location: {cached_result.get('display_name', 'unknown')}")
        else:
            print("✗ Geocoding cache retrieval failed")
        
        # Test proximity caching
        proximity_result = cache.get_proximity_results(test_lat, test_lon, radius_meters=1000)
        if proximity_result:
            print("✓ Proximity cache working")
        
        # Cleanup
        cache.invalidate_coordinates(test_lat, test_lon)
        
        return True
    except Exception as e:
        print(f"✗ Geocoding cache test failed: {e}")
        return False


def test_perceptual_hash_cache():
    """Test perceptual hash caching."""
    print("\n=== Testing Perceptual Hash Cache ===")
    
    try:
        cache = PerceptualHashCache()
        
        # Test file path
        test_file = "/tmp/test_image.jpg"
        
        # Create mock hash
        mock_hash = "a1b2c3d4e5f6"
        
        # Cache the hash
        cache_success = cache.cache_result(
            mock_hash, test_file, algorithm="phash", execution_time_ms=2000
        )
        print(f"✓ Perceptual hash cache result: {'success' if cache_success else 'failed'}")
        
        # Retrieve from cache
        cached_result = cache.get_cached_result(test_file, algorithm="phash")
        if cached_result:
            print("✓ Perceptual hash cache retrieval successful")
            print(f"  - Cache hit: {cached_result.get('cache_info', {}).get('hit', False)}")
            print(f"  - Hash value: {cached_result.get('hash_value', 'unknown')}")
        else:
            print("✗ Perceptual hash cache retrieval failed")
        
        # Test hash comparison caching
        hash1, hash2 = "a1b2c3d4", "a1b2c3d5"
        similarity = 0.95
        
        comparison_success = cache.cache_comparison_result(
            similarity, hash1, hash2, algorithm="phash"
        )
        print(f"✓ Hash comparison cache result: {'success' if comparison_success else 'failed'}")
        
        # Retrieve comparison
        cached_similarity = cache.get_cached_comparison(hash1, hash2, algorithm="phash")
        if cached_similarity is not None:
            print(f"✓ Hash comparison cache retrieval: similarity={cached_similarity}")
        else:
            print("✗ Hash comparison cache retrieval failed")
        
        # Cleanup
        cache.invalidate_file(test_file)
        
        return True
    except Exception as e:
        print(f"✗ Perceptual hash cache test failed: {e}")
        return False


def test_full_integration():
    """Test full integration with actual extraction."""
    print("\n=== Testing Full Integration ===")
    
    try:
        # Create a simple test image
        test_image_path = "/tmp/test_caching_image.jpg"
        
        # Create a simple test image using PIL if available
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple test image
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(test_image_path)
            
            print(f"✓ Created test image: {test_image_path}")
            
        except ImportError:
            # If PIL/numpy not available, skip image creation
            print("⚠ PIL/numpy not available, skipping image creation")
            return True
        
        # Test extraction with caching
        print("Testing extraction with caching...")
        extractor = NewComprehensiveMetadataExtractor(enable_caching=True)
        
        # First extraction (should be cache miss)
        start_time = time.time()
        result1 = extractor.extract_comprehensive_metadata(test_image_path, tier="free")
        time1 = (time.time() - start_time) * 1000
        
        cache_info1 = result1.get('extraction_info', {}).get('cache_hit', False)
        print(f"✓ First extraction: {time1:.2f}ms (cache hit: {cache_info1})")
        
        # Second extraction (should be cache hit)
        start_time = time.time()
        result2 = extractor.extract_comprehensive_metadata(test_image_path, tier="free")
        time2 = (time.time() - start_time) * 1000
        
        cache_info2 = result2.get('extraction_info', {}).get('cache_hit', False)
        print(f"✓ Second extraction: {time2:.2f}ms (cache hit: {cache_info2})")
        
        # Compare results
        if result1.get('metadata') == result2.get('metadata'):
            print("✓ Cached result matches original")
        else:
            print("⚠ Cached result differs from original")
        
        # Performance improvement
        if time2 < time1:
            improvement = ((time1 - time2) / time1) * 100
            print(f"✓ Performance improvement: {improvement:.1f}%")
        else:
            print("⚠ No performance improvement detected")
        
        # Test cache stats
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        print(f"✓ Overall cache hit rate: {stats['overall_stats']['overall_hit_rate_percent']:.1f}%")
        
        # Cleanup
        invalidate_file_caches(test_image_path)
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_monitoring():
    """Test performance monitoring capabilities."""
    print("\n=== Testing Performance Monitoring ===")
    
    try:
        cache_manager = get_cache_manager()
        
        # Get performance summary
        perf_summary = cache_manager.get_performance_summary()
        print("✓ Performance summary retrieved")
        
        # Check cache effectiveness
        effectiveness = perf_summary.get('cache_effectiveness', {})
        print(f"✓ Cache hit rate: {effectiveness.get('hit_rate_percent', 0):.1f}%")
        print(f"✓ Time saved: {effectiveness.get('time_saved_hours', 0):.2f} hours")
        
        # Check expensive operations
        expensive_ops = perf_summary.get('expensive_operations', {})
        expensive_modules = expensive_ops.get('expensive_modules', [])
        expensive_calcs = expensive_ops.get('expensive_perceptual_calculations', [])
        
        print(f"✓ Expensive modules found: {len(expensive_modules)}")
        print(f"✓ Expensive perceptual calculations: {len(expensive_calcs)}")
        
        # Health check
        health = cache_manager.health_check()
        print(f"✓ Cache health: {health.get('overall_status', 'unknown')}")
        
        return True
    except Exception as e:
        print(f"✗ Performance monitoring test failed: {e}")
        return False


def test_cache_invalidation():
    """Test cache invalidation functionality."""
    print("\n=== Testing Cache Invalidation ===")
    
    try:
        cache_manager = get_cache_manager()
        
        # Create test data
        test_file = "/tmp/test_invalidation.jpg"
        
        # Mock extraction result
        mock_result = {
            "metadata": {"test": "data"},
            "extraction_info": {"status": "success"}
        }
        
        # Cache the result
        cache_manager.cache_extraction_result(mock_result, test_file, "free")
        
        # Verify it's cached
        cached_result = cache_manager.get_extraction_result(test_file, "free")
        if cached_result:
            print("✓ Test data cached successfully")
        else:
            print("✗ Failed to cache test data")
            return False
        
        # Invalidate the cache
        invalidated_count = invalidate_file_caches(test_file)
        print(f"✓ Invalidated {invalidated_count} cache entries")
        
        # Verify it's gone
        cached_result = cache_manager.get_extraction_result(test_file, "free")
        if not cached_result:
            print("✓ Cache invalidation successful")
        else:
            print("✗ Cache invalidation failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Cache invalidation test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Starting Redis Caching System Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Cache Manager", test_cache_manager),
        ("Extraction Cache", test_extraction_cache),
        ("Module Cache", test_module_cache),
        ("Geocoding Cache", test_geocoding_cache),
        ("Perceptual Hash Cache", test_perceptual_hash_cache),
        ("Full Integration", test_full_integration),
        ("Performance Monitoring", test_performance_monitoring),
        ("Cache Invalidation", test_cache_invalidation),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    # Final cache stats
    try:
        cache_manager = get_cache_manager()
        final_stats = cache_manager.get_stats()
        print(f"\nFinal Cache Stats:")
        print(f"  - Overall hit rate: {final_stats['overall_stats']['overall_hit_rate_percent']:.1f}%")
        print(f"  - Total hits: {final_stats['overall_stats']['total_hits']}")
        print(f"  - Total requests: {final_stats['overall_stats']['total_requests']}")
        
        # Performance summary
        perf_summary = cache_manager.get_performance_summary()
        time_saved = perf_summary.get('cache_effectiveness', {}).get('time_saved_hours', 0)
        print(f"  - Time saved: {time_saved:.2f} hours")
        
    except Exception as e:
        print(f"\nFailed to get final stats: {e}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
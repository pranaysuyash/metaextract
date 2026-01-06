"""
Enhanced Geocoding Module with Redis Caching for MetaExtract

Extends the existing geocoding functionality with comprehensive Redis caching.
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import timedelta

# Import the original module for fallback
from . import geocoding

# Import cache manager
try:
    from ...cache.cache_manager import get_cache_manager
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    get_cache_manager = None

logger = logging.getLogger("metaextract.modules.geocoding_cached")

# Import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


def reverse_geocode_cached(latitude: float, longitude: float, 
                          api_key: Optional[str] = None, 
                          use_cache: bool = True, 
                          cache_ttl_hours: int = 24,
                          provider: str = "nominatim") -> Dict[str, Any]:
    """
    Enhanced reverse geocoding with Redis caching.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        api_key: API key (not required for OSM)
        use_cache: Whether to use cached results
        cache_ttl_hours: Cache TTL in hours
        provider: Geocoding provider (nominatim, google, etc.)
        
    Returns:
        Dictionary with location information and cache status
    """
    if not REQUESTS_AVAILABLE:
        logger.warning("requests library not available, falling back to original module")
        return geocoding.reverse_geocode(latitude, longitude, api_key, use_cache, cache_ttl_hours)
    
    # Initialize cache manager
    cache_manager = None
    if use_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    start_time = time.time()
    
    try:
        # Check cache first
        if cache_manager:
            cached_result = cache_manager.get_geocoding_result(latitude, longitude, provider)
            if cached_result:
                logger.debug(f"Geocoding cache hit: ({latitude}, {longitude})")
                
                # Add cache information
                cached_result['cache_info'] = {
                    'hit': True,
                    'source': 'redis_cache',
                    'provider': provider
                }
                
                return cached_result
        
        # Cache miss, perform geocoding
        logger.debug(f"Performing reverse geocoding: ({latitude}, {longitude})")
        
        # Use original geocoding function
        result = geocoding.reverse_geocode(latitude, longitude, api_key, use_cache=False)
        
        # Add timing information
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = processing_time
        
        # Cache the result
        if cache_manager and 'error' not in result:
            cache_success = cache_manager.cache_geocoding_result(
                result, latitude, longitude, provider
            )
            
            if cache_success:
                logger.debug(f"Cached geocoding result: ({latitude}, {longitude})")
        
        # Add cache information
        result['cache_info'] = {
            'hit': False,
            'source': 'fresh_geocoding',
            'provider': provider
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced geocoding failed: {e}")
        
        # Fallback to original module
        try:
            return geocoding.reverse_geocode(latitude, longitude, api_key, use_cache, cache_ttl_hours)
        except Exception as fallback_error:
            return {
                "error": f"Enhanced geocoding failed: {e}, fallback failed: {fallback_error}",
                "latitude": latitude,
                "longitude": longitude
            }


def batch_reverse_geocode(coordinates: list, 
                         api_key: Optional[str] = None,
                         use_cache: bool = True,
                         provider: str = "nominatim") -> Dict[str, Any]:
    """
    Batch reverse geocode multiple coordinates with caching.
    
    Args:
        coordinates: List of (latitude, longitude) tuples
        api_key: API key (not required for OSM)
        use_cache: Whether to use cached results
        provider: Geocoding provider
        
    Returns:
        Dictionary with batch results
    """
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not available"}
    
    # Initialize cache manager
    cache_manager = None
    if use_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    results = {
        "batch_results": [],
        "cache_stats": {
            "hits": 0,
            "misses": 0,
            "total": len(coordinates)
        }
    }
    
    # Check cache for all coordinates first
    uncached_coordinates = []
    
    for lat, lon in coordinates:
        if cache_manager:
            cached_result = cache_manager.get_geocoding_result(lat, lon, provider)
            if cached_result:
                results["batch_results"].append(cached_result)
                results["cache_stats"]["hits"] += 1
                continue
        
        uncached_coordinates.append((lat, lon))
        results["cache_stats"]["misses"] += 1
    
    # Process uncached coordinates
    if uncached_coordinates:
        # Process in batches to avoid rate limiting
        batch_size = 1  # Nominatim doesn't support batch requests, process one by one
        
        for i in range(0, len(uncached_coordinates), batch_size):
            batch = uncached_coordinates[i:i + batch_size]
            
            for lat, lon in batch:
                try:
                    # Add delay to respect rate limits
                    if i > 0:
                        time.sleep(1.1)  # Nominatim rate limit
                    
                    result = reverse_geocode_cached(
                        lat, lon, api_key, use_cache=False, provider=provider
                    )
                    results["batch_results"].append(result)
                    
                except Exception as e:
                    logger.error(f"Batch geocoding failed for ({lat}, {lon}): {e}")
                    results["batch_results"].append({
                        "error": f"Geocoding failed: {e}",
                        "latitude": lat,
                        "longitude": lon
                    })
    
    return results


def geocode_address(address: str, 
                   api_key: Optional[str] = None,
                   use_cache: bool = True,
                   provider: str = "nominatim") -> Dict[str, Any]:
    """
    Forward geocode an address to coordinates with caching.
    
    Args:
        address: Address string to geocode
        api_key: API key (not required for OSM)
        use_cache: Whether to use cached results
        provider: Geocoding provider
        
    Returns:
        Dictionary with coordinates and location information
    """
    if not REQUESTS_AVAILABLE:
        return {"error": "requests library not available"}
    
    # Initialize cache manager
    cache_manager = None
    if use_cache and CACHING_AVAILABLE:
        cache_manager = get_cache_manager()
    
    start_time = time.time()
    
    try:
        # Create cache key for address
        import hashlib
        address_hash = hashlib.md5(address.encode()).hexdigest()
        cache_key = f"geocode_address:{address_hash}:{provider}"
        
        # Check cache
        if cache_manager:
            cached_result = cache_manager.redis_client.get_json(cache_key)
            if cached_result:
                logger.debug(f"Address geocoding cache hit: {address[:50]}...")
                cached_result['cache_info'] = {
                    'hit': True,
                    'source': 'redis_cache',
                    'provider': provider
                }
                return cached_result
        
        # Perform forward geocoding
        logger.debug(f"Performing forward geocoding: {address[:50]}...")
        
        headers = {
            "User-Agent": "MetaExtract/1.0 (https://github.com/pranaysuyash/metaextract)"
        }
        
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        
        if provider == "nominatim":
            url = "https://nominatim.openstreetmap.org/search"
        else:
            return {"error": f"Unsupported provider: {provider}"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            location = data[0]
            result = {
                "latitude": float(location["lat"]),
                "longitude": float(location["lon"]),
                "display_name": location.get("display_name", address),
                "address_components": location.get("address", {}),
                "importance": location.get("importance", 0),
                "provider": provider
            }
            
            # Add reverse geocoding result for consistency
            reverse_result = reverse_geocode_cached(
                result["latitude"], result["longitude"], 
                api_key=api_key, use_cache=use_cache, provider=provider
            )
            
            if "error" not in reverse_result:
                result.update(reverse_result)
            
        else:
            result = {
                "error": "No results found",
                "address": address
            }
        
        # Add timing information
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = processing_time
        
        # Cache the result
        if cache_manager and "error" not in result:
            # Use shorter TTL for address geocoding (1 hour)
            cache_manager.redis_client.set_json(cache_key, result, ex=3600)
            logger.debug(f"Cached address geocoding result: {address[:50]}...")
        
        # Add cache information
        result['cache_info'] = {
            'hit': False,
            'source': 'fresh_geocoding',
            'provider': provider
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Forward geocoding failed: {e}")
        return {
            "error": f"Forward geocoding failed: {e}",
            "address": address
        }


def get_geocoding_stats() -> Dict[str, Any]:
    """
    Get geocoding cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    if not CACHING_AVAILABLE:
        return {"error": "Caching not available"}
    
    try:
        cache_manager = get_cache_manager()
        return cache_manager.geocoding_cache.get_stats()
    except Exception as e:
        logger.error(f"Failed to get geocoding stats: {e}")
        return {"error": str(e)}


def invalidate_geocoding_cache(lat: float, lon: float, 
                              provider: Optional[str] = None) -> int:
    """
    Invalidate geocoding cache for specific coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        provider: Specific provider to invalidate (optional)
        
    Returns:
        Number of invalidated entries
    """
    if not CACHING_AVAILABLE:
        return 0
    
    try:
        cache_manager = get_cache_manager()
        return cache_manager.invalidate_coordinates(lat, lon, provider)
    except Exception as e:
        logger.error(f"Failed to invalidate geocoding cache: {e}")
        return 0


# Maintain compatibility with original function names
reverse_geocode = reverse_geocode_cached


# Enhanced proximity functions
def find_nearby_cached(center_lat: float, center_lon: float, 
                      radius_meters: float = 1000,
                      use_proximity_cache: bool = True) -> Dict[str, Any]:
    """
    Find cached geocoding results near a location.
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_meters: Search radius in meters
        use_proximity_cache: Whether to use proximity caching
        
    Returns:
        Dictionary with nearby cached results
    """
    if not CACHING_AVAILABLE:
        return {"error": "Caching not available"}
    
    try:
        cache_manager = get_cache_manager()
        
        if use_proximity_cache:
            # Check proximity cache
            proximity_results = cache_manager.geocoding_cache.get_proximity_results(
                center_lat, center_lon, radius_meters
            )
            
            if proximity_results:
                return {
                    "results": proximity_results.get("results", {}),
                    "cache_hit": True,
                    "distance_meters": proximity_results.get("cache_info", {}).get("distance_meters", 0)
                }
        
        # Search through all cached coordinates
        all_keys = cache_manager.redis_client.keys("geocoding:*")
        nearby_results = []
        
        for key in all_keys:
            try:
                cached_data = cache_manager.redis_client.get_json(key)
                if cached_data and isinstance(cached_data, dict):
                    lat = cached_data.get('lat')
                    lon = cached_data.get('lon')
                    
                    if lat is not None and lon is not None:
                        # Calculate distance
                        distance = cache_manager.geocoding_cache._calculate_distance(
                            center_lat, center_lon, lat, lon
                        )
                        
                        if distance <= radius_meters:
                            nearby_results.append({
                                "latitude": lat,
                                "longitude": lon,
                                "distance_meters": round(distance, 2),
                                "location_data": cached_data
                            })
            except Exception as e:
                logger.error(f"Error checking key {key}: {e}")
        
        # Sort by distance
        nearby_results.sort(key=lambda x: x["distance_meters"])
        
        return {
            "results": nearby_results,
            "cache_hit": False,
            "total_found": len(nearby_results)
        }
        
    except Exception as e:
        logger.error(f"Failed to find nearby cached results: {e}")
        return {"error": str(e)}
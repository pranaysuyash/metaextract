"""
Enhanced Geocoding Cache for MetaExtract

Extends the existing geocoding cache with Redis backend and improved performance.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Tuple, List
from datetime import timedelta

from .base_cache import BaseCache

logger = logging.getLogger("metaextract.cache.geocoding")


class GeocodingCache(BaseCache):
    """
    Enhanced geocoding cache with Redis backend.
    
    Features:
    - Coordinate-based caching with precision handling
    - Address normalization and deduplication
    - Multi-provider support
    - Geographic proximity caching
    """
    
    def __init__(self):
        """Initialize geocoding cache with 24-hour TTL."""
        super().__init__(cache_prefix="geocoding", default_ttl=86400)  # 24 hours
        self.coordinate_precision = 6  # Decimal places for coordinate rounding
    
    def _normalize_coordinates(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Normalize coordinates to consistent precision.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Normalized (lat, lon) tuple
        """
        return (
            round(float(lat), self.coordinate_precision),
            round(float(lon), self.coordinate_precision)
        )
    
    def get_cache_key(self, lat: float, lon: float, 
                     provider: str = "nominatim", language: str = "en") -> str:
        """
        Generate cache key for geocoding result.
        
        Args:
            lat: Latitude
            lon: Longitude
            provider: Geocoding provider
            language: Language for results
            
        Returns:
            Cache key string
        """
        # Normalize coordinates
        norm_lat, norm_lon = self._normalize_coordinates(lat, lon)
        
        return self._generate_cache_key(norm_lat, norm_lon, provider, language)
    
    def get_cached_result(self, lat: float, lon: float,
                         provider: str = "nominatim", language: str = "en") -> Optional[Dict[str, Any]]:
        """
        Get cached geocoding result if available.
        
        Args:
            lat: Latitude
            lon: Longitude
            provider: Geocoding provider
            language: Language for results
            
        Returns:
            Cached geocoding result or None
        """
        cache_key = self.get_cache_key(lat, lon, provider, language)
        
        cached_result = self.get(cache_key)
        if cached_result is None:
            return None
        
        # Validate cached result structure
        if not isinstance(cached_result, dict):
            logger.warning(f"Invalid cached geocoding result format")
            self.delete(cache_key)
            return None
        
        # Add cache hit information
        cached_result['cache_info'] = {
            'hit': True,
            'cached_at': cached_result.get('cached_at'),
            'cache_key': cache_key,
            'provider': provider
        }
        
        logger.debug(f"Geocoding cache hit: ({lat}, {lon}) via {provider}")
        return cached_result
    
    def cache_result(self, result: Dict[str, Any], lat: float, lon: float,
                    provider: str = "nominatim", language: str = "en") -> bool:
        """
        Cache geocoding result.
        
        Args:
            result: Geocoding result to cache
            lat: Latitude
            lon: Longitude
            provider: Geocoding provider
            language: Language for results
            
        Returns:
            True if caching was successful
        """
        cache_key = self.get_cache_key(lat, lon, provider, language)
        
        # Prepare cache data
        cache_data = result.copy()
        cache_data['lat'] = lat
        cache_data['lon'] = lon
        cache_data['provider'] = provider
        cache_data['language'] = language
        cache_data['cached_at'] = int(time.time())
        
        # Remove any existing cache info
        cache_data.pop('cache_info', None)
        
        # Set TTL (24 hours default for geocoding)
        ttl = self.default_ttl
        
        success = self.set(cache_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached geocoding result: ({lat}, {lon}) via {provider}")
        else:
            logger.warning(f"Failed to cache geocoding result: ({lat}, {lon})")
        
        return success
    
    def get_proximity_key(self, lat: float, lon: float, 
                         radius_meters: float = 100) -> str:
        """
        Generate cache key for proximity-based caching.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_meters: Proximity radius in meters
            
        Returns:
            Proximity cache key
        """
        # Create grid-based key for proximity
        # Round coordinates to approximate grid size
        grid_size = radius_meters / 111000  # Convert meters to degrees (approx)
        grid_lat = round(lat / grid_size) * grid_size
        grid_lon = round(lon / grid_size) * grid_size
        
        return self._generate_cache_key("proximity", grid_lat, grid_lon, radius_meters)
    
    def get_proximity_results(self, lat: float, lon: float, 
                            radius_meters: float = 100) -> Optional[Dict[str, Any]]:
        """
        Get cached results for nearby coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_meters: Proximity radius in meters
            
        Returns:
            Cached proximity results or None
        """
        proximity_key = self.get_proximity_key(lat, lon, radius_meters)
        
        cached_results = self.get(proximity_key)
        if cached_results is None:
            return None
        
        # Validate that requested coordinates are within cached radius
        if isinstance(cached_results, dict):
            cached_center = cached_results.get('center_coordinates')
            cached_radius = cached_results.get('radius_meters')
            
            if cached_center and cached_radius:
                # Check if requested point is within cached area
                distance = self._calculate_distance(
                    lat, lon,
                    cached_center['lat'], cached_center['lon']
                )
                
                if distance <= cached_radius:
                    cached_results['cache_info'] = {
                        'hit': True,
                        'proximity_hit': True,
                        'cached_at': cached_results.get('cached_at'),
                        'distance_meters': round(distance, 2)
                    }
                    
                    logger.debug(f"Proximity cache hit: ({lat}, {lon}) within {distance:.0f}m of cached area")
                    return cached_results
        
        return None
    
    def cache_proximity_results(self, results: Dict[str, Any], center_lat: float, 
                              center_lon: float, radius_meters: float) -> bool:
        """
        Cache results for a geographic area.
        
        Args:
            results: Geocoding results for the area
            center_lat: Center latitude
            center_lon: Center longitude
            radius_meters: Radius of cached area
            
        Returns:
            True if caching was successful
        """
        proximity_key = self.get_proximity_key(center_lat, center_lon, radius_meters)
        
        cache_data = {
            'results': results,
            'center_coordinates': {'lat': center_lat, 'lon': center_lon},
            'radius_meters': radius_meters,
            'cached_at': int(time.time())
        }
        
        # Shorter TTL for proximity caches (6 hours)
        ttl = 21600
        
        success = self.set(proximity_key, cache_data, ttl=ttl)
        
        if success:
            logger.debug(f"Cached proximity results for area around ({center_lat}, {center_lon})")
        
        return success
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in meters
        """
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in meters
        r = 6371000
        
        return c * r
    
    def invalidate_coordinates(self, lat: float, lon: float, 
                              provider: Optional[str] = None) -> int:
        """
        Invalidate cached results for specific coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            provider: Specific provider to invalidate (optional)
            
        Returns:
            Number of invalidated entries
        """
        norm_lat, norm_lon = self._normalize_coordinates(lat, lon)
        
        if provider:
            # Invalidate specific provider
            pattern = f"{norm_lat}_{norm_lon}_{provider}*"
        else:
            # Invalidate all providers for these coordinates
            pattern = f"{norm_lat}_{norm_lon}_*"
        
        count = self.invalidate_by_pattern(pattern)
        logger.info(f"Invalidated {count} geocoding cache entries for ({lat}, {lon})")
        return count
    
    def invalidate_area(self, min_lat: float, min_lon: float, 
                       max_lat: float, max_lon: float) -> int:
        """
        Invalidate all cached results within geographic bounds.
        
        Args:
            min_lat, min_lon: Southwest corner
            max_lat, max_lon: Northeast corner
            
        Returns:
            Number of invalidated entries
        """
        # This is a simplified implementation
        # In practice, you might want to use geospatial indexing
        
        all_keys = self.redis_client.keys(f"{self.cache_prefix}:*")
        count = 0
        
        for key in all_keys:
            try:
                cached_data = self.get(key)
                if cached_data and isinstance(cached_data, dict):
                    lat = cached_data.get('lat')
                    lon = cached_data.get('lon')
                    
                    if lat is not None and lon is not None:
                        if (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
                            if self.delete(key):
                                count += 1
            except Exception as e:
                logger.error(f"Error checking key {key} for area invalidation: {e}")
        
        logger.info(f"Invalidated {count} geocoding cache entries within bounds")
        return count
    
    def get_provider_stats(self, provider: str) -> Dict[str, Any]:
        """Get cache statistics for specific provider."""
        stats = self.get_stats()
        
        # Count keys for this provider
        provider_pattern = f"*_{provider}_*"
        provider_keys = self.redis_client.keys(f"{self.cache_prefix}:{provider_pattern}")
        
        stats.update({
            'provider_keys': len(provider_keys),
            'provider': provider
        })
        
        return stats
    
    def get_popular_locations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently accessed locations.
        
        Args:
            limit: Maximum number of locations to return
            
        Returns:
            List of popular location information
        """
        # This would require access tracking which isn't implemented
        # For now, return recently cached locations
        
        all_keys = self.redis_client.keys(f"{self.cache_prefix}:*")
        locations = []
        
        for key in all_keys[:limit]:  # Limit for performance
            try:
                cached_data = self.get(key)
                if cached_data and isinstance(cached_data, dict):
                    lat = cached_data.get('lat')
                    lon = cached_data.get('lon')
                    
                    if lat is not None and lon is not None:
                        locations.append({
                            'lat': lat,
                            'lon': lon,
                            'cached_at': cached_data.get('cached_at'),
                            'provider': cached_data.get('provider')
                        })
            except Exception as e:
                logger.error(f"Error reading location data from key {key}: {e}")
        
        return locations
#!/usr/bin/env python3
"""
Metadata Comparator - Compare embedded vs burned-in metadata

Detects discrepancies between:
1. Embedded metadata (EXIF/XMP/IPTC tags)
2. Burned-in metadata (OCR-extracted from image pixels)

Use cases:
- Detect metadata tampering
- Verify authenticity
- Identify photo editing apps that add overlays
- Forensic analysis
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetadataComparator:
    """Compare and analyze embedded vs burned-in metadata."""
    
    def compare(
        self,
        embedded: Dict[str, Any],
        burned: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare embedded and burned-in metadata.
        
        Args:
            embedded: Metadata from EXIF/XMP/IPTC tags
            burned: Metadata extracted via OCR from image
            
        Returns:
            Comparison analysis with discrepancies
        """
        result = {
            "has_both": False,
            "has_embedded_only": False,
            "has_burned_only": False,
            "matches": [],
            "discrepancies": [],
            "warnings": [],
            "summary": {}
        }
        
        # Check what's available
        has_embedded_gps = self._has_gps(embedded)
        has_burned_gps = burned.get("parsed_data", {}).get("gps") is not None
        
        has_embedded_location = self._has_location(embedded)
        has_burned_location = (
            "location" in burned.get("parsed_data", {}) or
            "address" in burned.get("parsed_data", {})
        )
        
        has_embedded_time = self._has_datetime(embedded)
        has_burned_time = "timestamp" in burned.get("parsed_data", {})
        
        # Determine metadata presence
        if (has_embedded_gps or has_embedded_location or has_embedded_time) and \
           (has_burned_gps or has_burned_location or has_burned_time):
            result["has_both"] = True
        elif has_embedded_gps or has_embedded_location or has_embedded_time:
            result["has_embedded_only"] = True
        elif has_burned_gps or has_burned_location or has_burned_time:
            result["has_burned_only"] = True
        
        # Compare GPS coordinates
        if has_embedded_gps and has_burned_gps:
            gps_result = self._compare_gps(embedded, burned)
            if gps_result["matches"]:
                result["matches"].append(gps_result)
            else:
                result["discrepancies"].append(gps_result)
        
        # Compare timestamps
        if has_embedded_time and has_burned_time:
            time_result = self._compare_timestamps(embedded, burned)
            if time_result["matches"]:
                result["matches"].append(time_result)
            else:
                result["discrepancies"].append(time_result)
        
        # Warnings for single-source metadata
        if result["has_embedded_only"]:
            result["warnings"].append(
                "Image has embedded metadata but no visible overlay - "
                "metadata may have been removed from display"
            )
        elif result["has_burned_only"]:
            result["warnings"].append(
                "Image has visible metadata overlay but no embedded tags - "
                "EXIF data may have been stripped"
            )
        
        # Summary
        result["summary"] = {
            "embedded_metadata_present": has_embedded_gps or has_embedded_location or has_embedded_time,
            "burned_metadata_present": has_burned_gps or has_burned_location or has_burned_time,
            "gps_comparison": self._gps_comparison_status(has_embedded_gps, has_burned_gps, result),
            "timestamp_comparison": self._time_comparison_status(has_embedded_time, has_burned_time, result),
            "overall_status": self._determine_overall_status(result)
        }
        
        return result
    
    def _has_gps(self, embedded: Dict[str, Any]) -> bool:
        """Check if embedded metadata contains GPS."""
        # Check various possible GPS field locations
        if embedded.get("gps", {}).get("latitude"):
            return True
        if embedded.get("exif", {}).get("GPSLatitude"):
            return True
        if embedded.get("location", {}).get("gps"):
            return True
        return False
    
    def _has_location(self, embedded: Dict[str, Any]) -> bool:
        """Check if embedded metadata contains location info."""
        return bool(
            embedded.get("location", {}).get("city") or
            embedded.get("location", {}).get("address") or
            embedded.get("iptc", {}).get("City")
        )
    
    def _has_datetime(self, embedded: Dict[str, Any]) -> bool:
        """Check if embedded metadata contains datetime."""
        return bool(
            embedded.get("exif", {}).get("DateTimeOriginal") or
            embedded.get("exif", {}).get("DateTime") or
            embedded.get("xmp", {}).get("CreateDate")
        )
    
    def _compare_gps(
        self,
        embedded: Dict[str, Any],
        burned: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare GPS coordinates."""
        # Extract coordinates
        emb_lat, emb_lon = self._extract_embedded_gps(embedded)
        burned_gps = burned.get("parsed_data", {}).get("gps", {})
        burn_lat = burned_gps.get("latitude")
        burn_lon = burned_gps.get("longitude")
        
        if emb_lat is None or burn_lat is None:
            return {
                "field": "gps",
                "matches": False,
                "reason": "Missing GPS data in one source"
            }
        
        # Calculate distance difference (rough approximation)
        lat_diff = abs(emb_lat - burn_lat)
        lon_diff = abs(emb_lon - burn_lon)
        
        # Allow small differences (GPS precision varies)
        tolerance = 0.001  # ~111 meters
        matches = lat_diff < tolerance and lon_diff < tolerance
        
        result = {
            "field": "gps",
            "matches": matches,
            "embedded": {"latitude": emb_lat, "longitude": emb_lon},
            "burned": {"latitude": burn_lat, "longitude": burn_lon},
            "difference": {
                "latitude_deg": lat_diff,
                "longitude_deg": lon_diff,
                "approx_meters": (lat_diff + lon_diff) * 111000
            }
        }
        
        if not matches:
            result["warning"] = "GPS coordinates differ - possible metadata tampering or different capture times"
        
        return result
    
    def _compare_timestamps(
        self,
        embedded: Dict[str, Any],
        burned: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare timestamps."""
        # Extract timestamps
        emb_time = (
            embedded.get("exif", {}).get("DateTimeOriginal") or
            embedded.get("exif", {}).get("DateTime")
        )
        burn_time = burned.get("parsed_data", {}).get("timestamp")
        
        result = {
            "field": "timestamp",
            "embedded": emb_time,
            "burned": burn_time,
            "matches": False
        }
        
        if not emb_time or not burn_time:
            result["reason"] = "Missing timestamp in one source"
            return result
        
        # Try to parse and compare (this is simplified)
        # Real implementation would need robust date parsing
        result["matches"] = self._timestamps_similar(emb_time, burn_time)
        
        if not result["matches"]:
            result["warning"] = "Timestamps differ - possible time zone issue or metadata modification"
        
        return result
    
    def _extract_embedded_gps(self, embedded: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        """Extract GPS coordinates from embedded metadata."""
        # Try various field locations
        if "gps" in embedded:
            gps = embedded["gps"]
            if "latitude" in gps and "longitude" in gps:
                return gps["latitude"], gps["longitude"]
        
        if "location" in embedded and "gps" in embedded["location"]:
            gps = embedded["location"]["gps"]
            return gps.get("latitude"), gps.get("longitude")
        
        return None, None
    
    def _timestamps_similar(self, time1: str, time2: str) -> bool:
        """Check if two timestamp strings are similar (basic comparison)."""
        # Very basic - extract date components
        # Real implementation would need proper parsing
        import re
        
        # Extract date components using regex
        date_pattern = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
        match1 = re.search(date_pattern, str(time1))
        match2 = re.search(date_pattern, str(time2))
        
        if match1 and match2:
            # Compare year, month, day
            return (
                match1.group(1) == match2.group(1) and  # year
                match1.group(2).zfill(2) == match2.group(2).zfill(2) and  # month
                match1.group(3).zfill(2) == match2.group(3).zfill(2)  # day
            )
        
        return False
    
    def _gps_comparison_status(
        self,
        has_embedded: bool,
        has_burned: bool,
        result: Dict[str, Any]
    ) -> str:
        """Determine GPS comparison status."""
        if not has_embedded and not has_burned:
            return "no_gps"
        elif has_embedded and has_burned:
            # Check if they match
            for match in result.get("matches", []):
                if match.get("field") == "gps":
                    return "match"
            for disc in result.get("discrepancies", []):
                if disc.get("field") == "gps":
                    return "mismatch"
            return "compared"
        elif has_embedded:
            return "embedded_only"
        else:
            return "burned_only"
    
    def _time_comparison_status(
        self,
        has_embedded: bool,
        has_burned: bool,
        result: Dict[str, Any]
    ) -> str:
        """Determine timestamp comparison status."""
        if not has_embedded and not has_burned:
            return "no_timestamp"
        elif has_embedded and has_burned:
            for match in result.get("matches", []):
                if match.get("field") == "timestamp":
                    return "match"
            for disc in result.get("discrepancies", []):
                if disc.get("field") == "timestamp":
                    return "mismatch"
            return "compared"
        elif has_embedded:
            return "embedded_only"
        else:
            return "burned_only"
    
    def _determine_overall_status(self, result: Dict[str, Any]) -> str:
        """Determine overall comparison status."""
        if result["has_both"] and not result["discrepancies"]:
            return "verified" if result["matches"] else "no_overlap"
        elif result["has_both"] and result["discrepancies"]:
            return "suspicious"
        elif result["has_embedded_only"]:
            return "no_overlay"
        elif result["has_burned_only"]:
            return "stripped_exif"
        else:
            return "no_metadata"


def compare_metadata(embedded: Dict[str, Any], burned: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for metadata comparison.
    
    Args:
        embedded: Embedded metadata (EXIF/XMP/IPTC)
        burned: Burned-in metadata (OCR-extracted)
        
    Returns:
        Comparison analysis
    """
    comparator = MetadataComparator()
    return comparator.compare(embedded, burned)

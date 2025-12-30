#!/usr/bin/env python3
"""
OCR-based Burned-in Metadata Extractor

Handles images/videos where metadata is visually overlaid on pixels:
- GPS map overlays (like GPS Map Camera app)
- Timestamp watermarks
- Location/address text
- Weather data overlays
- Camera app watermarks
- Social media overlays

Uses OCR (Tesseract) and pattern matching to extract burned-in data.
"""

import re
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class BurnedMetadataExtractor:
    """Extracts metadata that is visually burned into image pixels."""
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is installed."""
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def extract(self, filepath: str) -> Dict[str, Any]:
        """
        Extract burned-in metadata from image.
        
        Args:
            filepath: Path to image file
            
        Returns:
            Dictionary containing extracted burned-in metadata
        """
        result = {
            "has_burned_metadata": False,
            "ocr_available": self.tesseract_available,
            "extracted_text": None,
            "parsed_data": {},
            "confidence": "none"  # none, low, medium, high
        }
        
        if not self.tesseract_available:
            result["warning"] = "Tesseract OCR not installed - cannot extract burned-in metadata"
            return result
        
        # Extract text using OCR
        ocr_text = self._run_ocr(filepath)
        if not ocr_text:
            return result
        
        result["extracted_text"] = ocr_text
        result["has_burned_metadata"] = True
        
        # Parse extracted text for structured data
        parsed = self._parse_ocr_text(ocr_text)
        result["parsed_data"] = parsed
        
        # Determine confidence based on what we found
        result["confidence"] = self._calculate_confidence(parsed)
        
        return result
    
    def _run_ocr(self, filepath: str) -> Optional[str]:
        """Run Tesseract OCR on image."""
        try:
            # Use tesseract to extract text
            result = subprocess.run(
                ['tesseract', filepath, 'stdout'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"Tesseract failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"OCR timeout for {filepath}")
            return None
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return None
    
    def _parse_ocr_text(self, text: str) -> Dict[str, Any]:
        """Parse OCR text to extract structured metadata."""
        parsed = {}
        
        # GPS Coordinates (various formats)
        gps_patterns = [
            # "Lat 12.923974° Long 77.625419°"
            r'Lat\s+([-+]?\d+\.?\d*)[°]?\s+Long\s+([-+]?\d+\.?\d*)[°]?',
            # "12.923974, 77.625419"
            r'([-+]?\d+\.\d+)[,\s]+([-+]?\d+\.\d+)',
            # "N 12°55'26.3" E 77°37'31.5""
            r'([NS])\s*(\d+)°\s*(\d+)[\'′]\s*([\d.]+)[\"″].*?([EW])\s*(\d+)°\s*(\d+)[\'′]\s*([\d.]+)[\"″]',
        ]
        
        for pattern in gps_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed["gps"] = self._parse_gps_match(match, pattern)
                break
        
        # Location/Address
        # Look for common location patterns
        location_patterns = [
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)', 'location'),  # City, State, Country
            (r'Plus\s+Code\s*:?\s*([A-Z0-9+]+)', 'plus_code'),  # Plus Code
        ]
        
        for pattern, pattern_type in location_patterns:
            match = re.search(pattern, text)
            if match:
                if pattern_type == 'plus_code':
                    parsed["plus_code"] = match.group(1)
                elif pattern_type == 'location':
                    parsed["location"] = {
                        "city": match.group(1),
                        "state": match.group(2),
                        "country": match.group(3)
                    }
                    break
        
        # Full address (more flexible)
        if "location" not in parsed:
            # Try to find address-like text
            address_match = re.search(
                r'([A-Z]\d+[^,]+,\s*[^,]+,\s*[^,]+,\s*\d{6})',
                text
            )
            if address_match:
                parsed["address"] = address_match.group(1).strip()
        
        # Timestamp
        timestamp_patterns = [
            r'(\w+day),\s*(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)\s*GMT\s*([-+]\d{2}:\d{2})',
            r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*(AM|PM)',
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, text)
            if match:
                parsed["timestamp"] = match.group(0)
                break
        
        # Weather data
        weather_patterns = {
            "temperature": r'([-+]?\d+\.?\d*)[°]?\s*[CF]',
            "humidity": r'(\d+)%',
            "speed": r'([\d.]+)\s*km/h',
            "altitude": r'(\d+)\s*m',
        }
        
        for key, pattern in weather_patterns.items():
            match = re.search(pattern, text)
            if match:
                if "weather" not in parsed:
                    parsed["weather"] = {}
                parsed["weather"][key] = match.group(1)
        
        # Compass direction
        compass_match = re.search(r'(\d+)°\s*(N|NE|E|SE|S|SW|W|NW)', text)
        if compass_match:
            parsed["compass"] = {
                "degrees": compass_match.group(1),
                "direction": compass_match.group(2)
            }
        
        # Camera/App watermark
        camera_apps = [
            'GPS Map Camera', 'Timestamp Camera', 'GPS Camera',
            'GeoTag', 'Camera+', 'ProCamera', 'Halide'
        ]
        for app in camera_apps:
            if app.lower() in text.lower():
                parsed["camera_app"] = app
                break
        
        return parsed
    
    def _parse_gps_match(self, match, pattern_used: str) -> Dict[str, Any]:
        """Parse GPS coordinates from regex match."""
        gps = {}
        
        if 'Lat' in pattern_used:
            # Decimal format
            gps["latitude"] = float(match.group(1))
            gps["longitude"] = float(match.group(2))
        elif '[-+]?\\d+\\.\\d+' in pattern_used and 'Long' not in pattern_used:
            # Simple decimal pair
            gps["latitude"] = float(match.group(1))
            gps["longitude"] = float(match.group(2))
        elif '[NS]' in pattern_used:
            # DMS format
            lat_deg = int(match.group(2))
            lat_min = int(match.group(3))
            lat_sec = float(match.group(4))
            lat_dir = match.group(1)
            
            lon_deg = int(match.group(6))
            lon_min = int(match.group(7))
            lon_sec = float(match.group(8))
            lon_dir = match.group(5)
            
            # Convert to decimal
            lat = lat_deg + lat_min/60 + lat_sec/3600
            if lat_dir == 'S':
                lat = -lat
            
            lon = lon_deg + lon_min/60 + lon_sec/3600
            if lon_dir == 'W':
                lon = -lon
            
            gps["latitude"] = lat
            gps["longitude"] = lon
            gps["format"] = "dms"
        
        # Add Google Maps URL
        if "latitude" in gps and "longitude" in gps:
            gps["google_maps_url"] = f"https://www.google.com/maps?q={gps['latitude']},{gps['longitude']}"
        
        return gps
    
    def _calculate_confidence(self, parsed: Dict[str, Any]) -> str:
        """Calculate confidence level based on extracted data."""
        score = 0
        
        if "gps" in parsed:
            score += 3
        if "location" in parsed or "address" in parsed:
            score += 2
        if "timestamp" in parsed:
            score += 2
        if "weather" in parsed:
            score += 1
        if "camera_app" in parsed:
            score += 1
        
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        elif score >= 1:
            return "low"
        else:
            return "none"


def extract_burned_metadata(filepath: str) -> Dict[str, Any]:
    """
    Main entry point for burned-in metadata extraction.
    
    Args:
        filepath: Path to image file
        
    Returns:
        Dictionary with burned-in metadata
    """
    extractor = BurnedMetadataExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_burned_metadata(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python ocr_burned_metadata.py <image_file>")

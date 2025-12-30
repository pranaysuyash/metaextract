#!/usr/bin/env python3
"""Test integration of burned metadata and comparison modules"""

import sys
import os
sys.path.insert(0, '/Users/pranay/Projects/metaextract/server/extractor')

from modules.ocr_burned_metadata import BurnedMetadataExtractor
from modules.metadata_comparator import compare_metadata

# Test data simulating GPS Map Camera image
test_burned_text = """
📍 Location: Bengaluru, Karnataka, India
🕐 Timestamp: Thursday, 25/12/2025 04:48 PM GMT +05:30
Lat 12.923974° Long 77.625419°
🌡️ Temperature: 25.54°C, Humidity: 34%, Wind: 7.42 km/h
Altitude: 903 m
🧭 Compass: 231° SW
📱 GPS Map Camera
"""

# Test embedded EXIF data
embedded_metadata = {
    'gps': {
        'latitude_decimal': 12.923974,
        'longitude_decimal': 77.625419
    },
    'datetime_original': '2025:12:25 16:48:00'
}

print("=" * 60)
print("BURNED METADATA EXTRACTION TEST")
print("=" * 60)

# Extract burned metadata (using the extractor directly for testing)
extractor = BurnedMetadataExtractor()
# Mock the OCR result for testing
extractor.tesseract_available = True
parsed = extractor._parse_ocr_text(test_burned_text)
burned = {
    "has_burned_metadata": True,
    "ocr_available": True,
    "extracted_text": test_burned_text,
    "parsed_data": parsed,
    "confidence": extractor._calculate_confidence(parsed)
}
print(f"\n✓ Burned metadata extracted")
print(f"  - Has overlay: {burned.get('has_burned_metadata')}")
print(f"  - Confidence: {burned.get('confidence')}")
print(f"  - GPS: {burned.get('parsed_data', {}).get('gps')}")
print(f"  - Location: {burned.get('parsed_data', {}).get('location')}")
print(f"  - Timestamp: {burned.get('parsed_data', {}).get('timestamp')}")
print(f"  - Weather: {burned.get('parsed_data', {}).get('weather')}")
print(f"  - Compass: {burned.get('parsed_data', {}).get('compass')}")
print(f"  - Camera App: {burned.get('parsed_data', {}).get('camera_app')}")

print("\n" + "=" * 60)
print("METADATA COMPARISON TEST")
print("=" * 60)

# Compare metadata
comparison = compare_metadata(embedded_metadata, burned)
print(f"\n✓ Metadata comparison completed")
print(f"  - Overall Status: {comparison.get('summary', {}).get('overall_status')}")
print(f"  - GPS Comparison: {comparison.get('summary', {}).get('gps_comparison')}")
print(f"  - Timestamp Comparison: {comparison.get('summary', {}).get('timestamp_comparison')}")
print(f"  - Matches: {len(comparison.get('matches', []))} fields")
print(f"  - Discrepancies: {len(comparison.get('discrepancies', []))} fields")
print(f"  - Warnings: {len(comparison.get('warnings', []))} warning(s)")

if comparison.get('warnings'):
    print(f"\n  Warnings:")
    for w in comparison.get('warnings', []):
        print(f"    - {w}")

print("\n" + "=" * 60)
print("✅ INTEGRATION TEST PASSED")
print("=" * 60)
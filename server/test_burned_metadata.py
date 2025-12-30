#!/usr/bin/env python3
"""
Test script for burned-in metadata extraction

Demonstrates:
1. Extracting metadata from images with visual overlays
2. Comparing embedded vs burned metadata
3. Detecting potential tampering

Usage:
    python test_burned_metadata.py <image_with_overlay.jpg>
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extractor.modules.ocr_burned_metadata import extract_burned_metadata
from extractor.modules.metadata_comparator import compare_metadata
from extractor.metadata_engine import extract_metadata


def test_burned_extraction(filepath: str):
    """Test burned metadata extraction."""
    print("=" * 80)
    print("BURNED METADATA EXTRACTION TEST")
    print("=" * 80)
    print(f"\nFile: {filepath}\n")
    
    # 1. Extract burned metadata only
    print("1. Extracting burned-in metadata (OCR)...")
    print("-" * 80)
    burned = extract_burned_metadata(filepath)
    
    if not burned.get("ocr_available"):
        print("❌ Tesseract OCR not available!")
        print("   Install: brew install tesseract (macOS) or apt install tesseract-ocr (Linux)")
        return
    
    if burned.get("has_burned_metadata"):
        print("✓ Burned metadata detected!")
        print(f"  Confidence: {burned.get('confidence', 'unknown')}")
        print(f"\n  Raw OCR Text:\n  {burned.get('extracted_text', 'None')[:200]}...")
        
        parsed = burned.get("parsed_data", {})
        if parsed:
            print(f"\n  Parsed Data:")
            if "gps" in parsed:
                gps = parsed["gps"]
                print(f"    📍 GPS: {gps.get('latitude')}, {gps.get('longitude')}")
                print(f"       Maps: {gps.get('google_maps_url')}")
            
            if "location" in parsed:
                loc = parsed["location"]
                print(f"    🏙️  Location: {loc.get('city')}, {loc.get('state')}, {loc.get('country')}")
            
            if "address" in parsed:
                print(f"    📮 Address: {parsed['address']}")
            
            if "timestamp" in parsed:
                print(f"    🕐 Timestamp: {parsed['timestamp']}")
            
            if "weather" in parsed:
                weather = parsed["weather"]
                print(f"    🌡️  Weather:")
                if "temperature" in weather:
                    print(f"       Temperature: {weather['temperature']}°C")
                if "humidity" in weather:
                    print(f"       Humidity: {weather['humidity']}%")
            
            if "camera_app" in parsed:
                print(f"    📷 Camera App: {parsed['camera_app']}")
    else:
        print("❌ No burned metadata detected in image")
    
    # 2. Extract full metadata (embedded + burned)
    print("\n\n2. Extracting full metadata (embedded + burned)...")
    print("-" * 80)
    full_metadata = extract_metadata(filepath, tier="super")
    
    has_exif_gps = bool(full_metadata.get("gps", {}).get("latitude"))
    has_burned_gps = bool(burned.get("parsed_data", {}).get("gps"))
    
    print(f"  Embedded EXIF GPS: {'✓' if has_exif_gps else '✗'}")
    print(f"  Burned OCR GPS:    {'✓' if has_burned_gps else '✗'}")
    
    # 3. Compare metadata
    if has_exif_gps and has_burned_gps:
        print("\n\n3. Comparing embedded vs burned metadata...")
        print("-" * 80)
        comparison = compare_metadata(full_metadata, burned)
        
        status = comparison.get("summary", {}).get("overall_status", "unknown")
        print(f"  Overall Status: {status.upper()}")
        
        if comparison.get("matches"):
            print(f"\n  ✓ MATCHES ({len(comparison['matches'])} fields):")
            for match in comparison["matches"]:
                field = match["field"]
                print(f"    - {field}: Data verified across both sources")
                if "difference" in match and "approx_meters" in match["difference"]:
                    print(f"      (GPS difference: ~{match['difference']['approx_meters']:.1f} meters)")
        
        if comparison.get("discrepancies"):
            print(f"\n  ⚠️  DISCREPANCIES ({len(comparison['discrepancies'])} fields):")
            for disc in comparison["discrepancies"]:
                print(f"    - {disc['field']}: {disc.get('warning', 'Data mismatch')}")
        
        if comparison.get("warnings"):
            print(f"\n  ⚠️  WARNINGS:")
            for warning in comparison["warnings"]:
                print(f"    - {warning}")
        
        # Security assessment
        print("\n\n4. Security Assessment")
        print("-" * 80)
        if status == "verified":
            print("  ✓ VERIFIED: Embedded and burned metadata match")
            print("  → Image metadata appears authentic")
        elif status == "suspicious":
            print("  ⚠️  SUSPICIOUS: Metadata sources conflict")
            print("  → Possible tampering or editing detected")
        elif status == "stripped_exif":
            print("  ⚠️  EXIF STRIPPED: Only visual overlay remains")
            print("  → Someone removed embedded metadata but overlay persists")
        elif status == "no_overlay":
            print("  ℹ️  NO OVERLAY: Only embedded metadata present")
            print("  → Standard photo with EXIF data")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def save_full_json(filepath: str, output: str = None):
    """Save complete extraction to JSON file."""
    if not output:
        output = Path(filepath).stem + "_metadata.json"
    
    print(f"\nExtracting and saving to {output}...")
    result = extract_metadata(filepath, tier="super")
    
    with open(output, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"✓ Saved to {output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_burned_metadata.py <image_file> [--save]")
        print("\nExample:")
        print("  python test_burned_metadata.py photo.jpg")
        print("  python test_burned_metadata.py photo.jpg --save")
        sys.exit(1)
    
    filepath = sys.argv[1]
    save_json = "--save" in sys.argv
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Run test
    test_burned_extraction(filepath)
    
    # Save JSON if requested
    if save_json:
        save_full_json(filepath)

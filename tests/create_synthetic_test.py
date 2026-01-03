#!/usr/bin/env python3
"""
Create synthetic test files with rich metadata for persona testing
"""

import json
from datetime import datetime
from pathlib import Path

# Test directory
test_dir = Path(__file__).parent / "persona-files" / "sarah-phone-photos"
test_dir.mkdir(parents=True, exist_ok=True)

# Synthetic metadata for a perfect phone photo
perfect_photo_metadata = {
    "DateTimeOriginal": "2024-07-15 14:30:45",
    "CreateDate": "2024-07-15 14:30:45",
    "Make": "Apple",
    "Model": "iPhone 15 Pro Max",
    "Software": "iOS 17.0",
    "ExifImageWidth": 4032,
    "ExifImageHeight": 3024,
    "GPSLatitude": 37.7749,
    "GPSLongitude": -122.4194,
    "GPSLatitudeRef": "N",
    "GPSLongitudeRef": "W",
    "City": "San Francisco",
    "State": "California",
    "Country": "United States",
    "ISO": 100,
    "FNumber": 1.8,
    "ExposureTime": "1/120",
    "FocalLength": "6.86",
    "LensModel": "iPhone 15 Pro Max back triple camera 6.86mm f/1.78"
}

# Save synthetic metadata
synthetic_file = test_dir / "synthetic_iphone_photo.json"
with open(synthetic_file, 'w') as f:
    json.dump({
        "filename": "synthetic_iphone_photo.jpg",
        "description": "Synthetic iPhone photo with perfect metadata",
        "metadata": perfect_photo_metadata,
        "expected_persona_results": {
            "when_taken": "July 15, 2024 at 02:30 PM",
            "where": "San Francisco, California, United States",
            "device": "Apple iPhone 15 Pro Max",
            "authentic": "appears_authentic"
        }
    }, f, indent=2)

print(f"✅ Created synthetic test metadata: {synthetic_file}")
print(f"\n📊 Expected Results:")
print(f"   📅 When: July 15, 2024 at 02:30 PM")
print(f"   📍 Where: San Francisco, California, United States")
print(f"   📱 Device: Apple iPhone 15 Pro Max")
print(f"   ✨ Authentic: Appears authentic (high confidence)")

# Test the persona layer with synthetic data
import sys
server_dir = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_dir))

from extractor.persona_interpretation import add_persona_interpretation

print(f"\n🎭 Testing Persona Layer with Synthetic Data:")
print("=" * 50)

result = add_persona_interpretation(perfect_photo_metadata, "phone_photo_sarah")

persona = result["persona_interpretation"]
answers = persona["plain_english_answers"]

print(f"📅 When: {answers['when_taken']['answer']}")
print(f"   Confidence: {answers['when_taken']['confidence']}")
print(f"   Source: {answers['when_taken']['source']}")

print(f"\n📍 Where: {answers['location']['answer']}")
if answers['location']['has_location']:
    coords = answers['location']['coordinates']
    print(f"   Coordinates: {coords['formatted']}")

print(f"\n📱 Device: {answers['device']['answer']}")
print(f"   Type: {answers['device']['device_type']}")

print(f"\n✨ Authentic: {answers['authenticity']['answer']}")
print(f"   Score: {answers['authenticity']['score']}/100")
print(f"   Confidence: {answers['authenticity']['confidence']}")

print(f"\n🔍 KEY FINDINGS:")
for finding in persona['key_findings']:
    print(f"   {finding}")

# Save results
results_file = test_dir.parent / "test-results" / "persona-sarah" / f"synthetic_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
results_file.parent.mkdir(parents=True, exist_ok=True)

with open(results_file, 'w') as f:
    json.dump({
        "test_type": "synthetic_metadata_test",
        "timestamp": datetime.now().isoformat(),
        "input_metadata": perfect_photo_metadata,
        "persona_result": result
    }, f, indent=2)

print(f"\n📊 Results saved to: {results_file}")
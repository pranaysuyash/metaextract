#!/usr/bin/env python3
"""
Test persona interpretation directly with debugging
"""

import sys
import json
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from extractor.persona_interpretation import add_persona_interpretation

# Create test metadata that simulates what the comprehensive engine produces
test_metadata = {
    "file": {
        "mime_type": "image/jpeg"
    },
    "exif": {
        "DateTimeOriginal": "2024-07-15 14:30:45",
        "CreateDate": "2024-07-15 14:30:45",
        "Make": "Apple",
        "Model": "iPhone 15 Pro Max",
        "Software": "iOS 17.0"
    },
    "gps": {
        "GPSLatitude": 37.7749,
        "GPSLongitude": -122.4194,
        "GPSLatitudeRef": "N",
        "GPSLongitudeRef": "W"
    }
}

print(f"🧪 Testing Persona Interpretation Directly")
print("=" * 50)

try:
    result = add_persona_interpretation(test_metadata, "phone_photo_sarah")

    print(f"✅ Persona interpretation successful!")
    print(f"Result keys: {list(result.keys())}")

    if "persona_interpretation" in result:
        persona = result["persona_interpretation"]
        print(f"\n🎭 PERSONA INTERPRETATION FOUND!")
        print(f"   Persona type: {persona.get('persona', 'unknown')}")

        answers = persona.get('plain_english_answers', {})

        print(f"\n   📅 WHEN TAKEN:")
        when = answers.get('when_taken', {})
        print(f"   Answer: {when.get('answer', 'N/A')}")
        print(f"   Confidence: {when.get('confidence', 'N/A')}")

        print(f"\n   📍 WHERE:")
        location = answers.get('location', {})
        print(f"   Answer: {location.get('answer', 'N/A')}")

        print(f"\n   📱 DEVICE:")
        device = answers.get('device', {})
        print(f"   Answer: {device.get('answer', 'N/A')}")

        print(f"\n   ✨ AUTHENTICITY:")
        authenticity = answers.get('authenticity', {})
        print(f"   Answer: {authenticity.get('answer', 'N/A')}")
    else:
        print(f"❌ No persona_interpretation key found")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 50)
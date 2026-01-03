#!/usr/bin/env python3
"""
Test persona interpretation directly from the Python engine
"""

import sys
import json
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

test_file = "tests/persona-files/sarah-phone-photos/gps-map-photo.jpg"

print(f"🧪 Testing Direct Python Persona Interpretation")
print("=" * 50)
print(f"📁 Test file: {test_file}")

try:
    result = extract_comprehensive_metadata(
        filepath=test_file,
        tier="super"
    )

    print(f"✅ Extraction successful!")
    print(f"📊 Fields extracted: {result.get('extraction_info', {}).get('fields_extracted', 0)}")

    # Check for persona interpretation
    if 'persona_interpretation' in result:
        persona = result['persona_interpretation']
        print(f"\n🎭 PERSONA INTERPRETATION FOUND!")
        print(f"   Persona: {persona.get('persona', 'unknown')}")

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

        print(f"\n✅ Persona interpretation working correctly!")
    else:
        print(f"❌ No persona interpretation found")
        print(f"Available keys: {list(result.keys())}")
        print(f"\nChecking mime type...")
        mime_type = result.get("file", {}).get("mime_type", "unknown")
        print(f"Mime type: {mime_type}")
        print(f"Starts with image/: {mime_type.startswith('image/')}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 50)
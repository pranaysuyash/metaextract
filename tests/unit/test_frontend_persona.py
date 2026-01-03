#!/usr/bin/env python3
"""
Test frontend persona display with real file upload
"""

import requests
import json
from pathlib import Path

# Test file - GPS map photo with good metadata
test_file = Path("tests/persona-files/sarah-phone-photos/gps-map-photo.jpg")

if not test_file.exists():
    print(f"❌ Test file not found: {test_file}")
    exit(1)

print(f"🧪 Testing Frontend Persona Display")
print("=" * 50)
print(f"📁 Test file: {test_file}")
print(f"📏 File size: {test_file.stat().st_size} bytes")

# Upload to local server
url = "http://127.0.0.1:3000/api/images_mvp/extract"

try:
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'image/jpeg')}
        data = {'tier': 'professional'}

        print(f"\n🚀 Uploading to {url}...")
        response = requests.post(url, files=files, data=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"📊 Fields extracted: {result.get('fields_extracted', 0)}")

            # Check for persona interpretation
            if 'persona_interpretation' in result:
                persona = result['persona_interpretation']
                print(f"\n🎭 PERSONA INTERPRETATION FOUND!")
                print(f"   Persona: {persona.get('persona', 'unknown')}")
                print(f"\n   KEY FINDINGS:")
                for finding in persona.get('key_findings', []):
                    print(f"   • {finding}")

                answers = persona.get('plain_english_answers', {})

                print(f"\n   📅 WHEN TAKEN:")
                when = answers.get('when_taken', {})
                print(f"   Answer: {when.get('answer', 'N/A')}")
                print(f"   Confidence: {when.get('confidence', 'N/A')}")
                print(f"   Source: {when.get('source', 'N/A')}")

                print(f"\n   📍 WHERE:")
                location = answers.get('location', {})
                print(f"   Answer: {location.get('answer', 'N/A')}")
                if location.get('has_location'):
                    coords = location.get('coordinates', {})
                    print(f"   Coordinates: {coords.get('formatted', 'N/A')}")
                    if location.get('readable_location'):
                        print(f"   Location: {location.get('readable_location')}")

                print(f"\n   📱 DEVICE:")
                device = answers.get('device', {})
                print(f"   Answer: {device.get('answer', 'N/A')}")
                print(f"   Type: {device.get('device_type', 'N/A')}")

                print(f"\n   ✨ AUTHENTICITY:")
                authenticity = answers.get('authenticity', {})
                print(f"   Answer: {authenticity.get('answer', 'N/A')}")
                print(f"   Score: {authenticity.get('score', 0)}/100")
                print(f"   Confidence: {authenticity.get('confidence', 'N/A')}")

                print(f"\n✅ Frontend should display persona section at top of results page!")
                print(f"🌐 Check http://localhost:5174 to see the persona display")

            else:
                print(f"❌ No persona interpretation found in response")
                print(f"Available keys: {list(result.keys())}")

        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to server at {url}")
    print(f"Make sure the dev server is running: npm run dev")
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n" + "=" * 50)
print(f"🧪 Test complete!")
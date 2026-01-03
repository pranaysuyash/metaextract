#!/usr/bin/env python3
"""
Test to see what the actual server response contains
"""

import json
import subprocess
import sys
from pathlib import Path

test_file = "tests/persona-files/sarah-phone-photos/gps-map-photo.jpg"

print(f"🧪 Testing Server Response Content")
print("=" * 50)

# Call the comprehensive metadata engine directly via command line
cmd = [
    ".venv/bin/python",
    "server/extractor/comprehensive_metadata_engine.py",
    test_file,
    "--tier", "super",
    "--performance",
    "--advanced"
]

print(f"🚀 Running extraction command...")
print(f"Command: {' '.join(cmd)}")

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd="/Users/pranay/Projects/metaextract"
    )

    if result.returncode == 0:
        # Parse JSON output from stdout
        output = result.stdout.strip()
        if output:
            # Find JSON in output (it might be multi-line)
            try:
                # Try parsing the entire output as JSON
                json_output = json.loads(output)
            except json.JSONDecodeError:
                # If that fails, try to find JSON object in the output
                lines = output.split('\n')
                json_output = None
                for line in lines:
                    if line.strip().startswith('{'):
                        try:
                            json_output = json.loads(line)
                            break
                        except json.JSONDecodeError:
                            continue

            if json_output:
                print(f"✅ Extraction successful!")

                # Check for persona interpretation
                if 'persona_interpretation' in json_output:
                    persona = json_output['persona_interpretation']
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

                    print(f"\n✅ Persona interpretation is working in Python engine!")
                else:
                    print(f"❌ No persona interpretation found in Python output")
                    print(f"Available keys: {list(json_output.keys())}")
                    print(f"\nChecking file info...")
                    file_info = json_output.get("file", {})
                    mime_type = file_info.get("mime_type", "unknown")
                    print(f"Mime type: {mime_type}")
            else:
                print(f"❌ No JSON output found")
                print(f"Output preview: {output[:500]}...")
        else:
            print(f"❌ No output from command")
    else:
        print(f"❌ Command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr[:500]}")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n" + "=" * 50)
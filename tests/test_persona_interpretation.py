#!/usr/bin/env python3
"""
Test Persona Interpretation Layer
Test the new persona-friendly output with real metadata
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import sys

# Add server directory to path
server_dir = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_dir))

from extractor.persona_interpretation import add_persona_interpretation

class PersonaInterpretationTester:
    def __init__(self):
        self.test_files_dir = Path(__file__).parent / "persona-files" / "sarah-phone-photos"
        self.results_dir = Path(__file__).parent / "test-results" / "persona-sarah"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_exiftool(self, filepath: str) -> dict:
        """Run exiftool and return parsed JSON output"""
        try:
            cmd = ['exiftool', '-json', filepath]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
            return {"error": "Exiftool failed"}
        except Exception as e:
            return {"error": str(e)}

    def test_persona_interpretation(self, filename: str) -> dict:
        """Test persona interpretation on a file"""
        filepath = self.test_files_dir / filename
        print(f"\n{'='*60}")
        print(f"Testing Persona Interpretation: {filename}")
        print(f"{'='*60}")

        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        # Get raw metadata via exiftool
        raw_metadata = self.run_exiftool(str(filepath))

        if "error" in raw_metadata:
            return {"filename": filename, "error": raw_metadata["error"]}

        # Add persona interpretation
        enhanced_metadata = add_persona_interpretation(raw_metadata, "phone_photo_sarah")

        return {
            "filename": filename,
            "file_size_mb": round(filepath.stat().st_size / (1024*1024), 2),
            "raw_fields_count": len(raw_metadata),
            "persona_interpretation": enhanced_metadata.get("persona_interpretation", {}),
            "timestamp": datetime.now().isoformat()
        }

    def run_all_tests(self):
        """Run tests on all Sarah's files"""
        print("🎭 Testing Persona Interpretation Layer")
        print("=" * 60)

        test_files = [
            "IMG_20251225_164634.jpg",
            "gps-map-photo.jpg"
        ]

        results = []
        for filename in test_files:
            result = self.test_persona_interpretation(filename)
            results.append(result)

            if "error" not in result:
                interpretation = result.get("persona_interpretation", {})
                print(f"✅ Completed: {filename}")

                # Show Sarah's answers
                answers = interpretation.get("plain_english_answers", {})

                print(f"\n   📅 When: {answers.get('when_taken', {}).get('answer', 'Unknown')}")
                location = answers.get('location', {})
                if location.get('has_location'):
                    coords = location.get('coordinates', {}).get('formatted', 'Unknown')
                    print(f"   📍 Where: {coords}")
                else:
                    print(f"   📍 Where: No GPS data")
                print(f"   📱 Device: {answers.get('device', {}).get('answer', 'Unknown')}")
                print(f"   ✨ Authentic: {answers.get('authenticity', {}).get('answer', 'Unknown')}")

                # Show key findings
                findings = interpretation.get('key_findings', [])
                print(f"\n   🔍 KEY FINDINGS:")
                for finding in findings:
                    print(f"      {finding}")
            else:
                print(f"❌ Failed: {filename} - {result.get('error', 'Unknown error')}")

        # Save results
        output_file = self.results_dir / f"persona_interpretation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "persona": "Phone Photo Sarah",
                    "test_type": "persona_interpretation",
                    "total_files_tested": len(test_files)
                },
                "results": results
            }, f, indent=2)

        print(f"\n🎯 Testing complete!")
        print(f"📊 Results saved to: {output_file}")

        return results

if __name__ == "__main__":
    tester = PersonaInterpretationTester()
    results = tester.run_all_tests()
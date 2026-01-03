#!/usr/bin/env python3
"""
Test the integrated persona interpretation pipeline
Test that the persona layer works correctly when integrated into the main extraction pipeline
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add server directory to path
server_dir = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_dir))

try:
    from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
    print("✅ Successfully imported extract_comprehensive_metadata")
except ImportError as e:
    print(f"❌ Failed to import extraction engine: {e}")
    sys.exit(1)

class IntegratedPersonaTest:
    def __init__(self):
        self.test_files_dir = Path(__file__).parent / "persona-files" / "sarah-phone-photos"
        self.results_dir = Path(__file__).parent / "test-results" / "persona-sarah"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def test_full_pipeline(self, filename: str) -> dict:
        """Test the complete extraction pipeline with persona interpretation"""
        filepath = self.test_files_dir / filename
        print(f"\n{'='*60}")
        print(f"Testing Full Pipeline: {filename}")
        print(f"{'='*60}")

        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            # Use the main extraction function (now with persona layer integrated)
            print("🔧 Starting extraction...")
            result = extract_comprehensive_metadata(str(filepath), tier="free")

            # Check if persona interpretation is present
            has_persona = "persona_interpretation" in result
            print(f"📊 Persona interpretation present: {has_persona}")

            if has_persona:
                persona_data = result.get("persona_interpretation", {})
                print(f"👤 Persona: {persona_data.get('persona', 'unknown')}")
                print(f"🔍 Key findings: {len(persona_data.get('key_findings', []))} items")

                # Show Sarah's answers
                answers = persona_data.get("plain_english_answers", {})

                when = answers.get("when_taken", {})
                print(f"\n   📅 When: {when.get('answer', 'Unknown')}")
                print(f"      Source: {when.get('source', 'unknown')}")
                print(f"      Confidence: {when.get('confidence', 'unknown')}")

                location = answers.get("location", {})
                if location.get("has_location"):
                    coords = location.get("coordinates", {}).get("formatted", "Unknown")
                    print(f"   📍 Where: {coords}")
                else:
                    print(f"   📍 Where: {location.get('answer', 'Unknown')}")

                device = answers.get("device", {})
                print(f"   📱 Device: {device.get('answer', 'Unknown')}")

                authentic = answers.get("authenticity", {})
                print(f"   ✨ Authentic: {authentic.get('answer', 'Unknown')}")

                # Show key findings
                findings = persona_data.get('key_findings', [])
                print(f"\n   🔍 KEY FINDINGS:")
                for finding in findings:
                    print(f"      {finding}")
            else:
                print("⚠️ No persona interpretation found in result")

            return {
                "filename": filename,
                "extraction_success": True,
                "has_persona_interpretation": has_persona,
                "fields_extracted": result.get("extraction_info", {}).get("fields_extracted", 0),
                "persona_data": result.get("persona_interpretation", {}) if has_persona else None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            return {
                "filename": filename,
                "error": str(e),
                "extraction_success": False
            }

    def run_all_tests(self):
        """Run tests on all Sarah's files"""
        print("🚀 Testing Integrated Persona Pipeline")
        print("=" * 60)

        test_files = [
            "gps-map-photo.jpg",  # This one has good metadata
            "IMG_20251225_164634.jpg"  # This one has limited metadata
        ]

        results = []
        for filename in test_files:
            result = self.test_full_pipeline(filename)
            results.append(result)

            if result.get("extraction_success"):
                print(f"✅ Completed: {filename}")
            else:
                print(f"❌ Failed: {filename} - {result.get('error', 'Unknown error')}")

        # Save results
        output_file = self.results_dir / f"integrated_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "persona": "Phone Photo Sarah",
                    "test_type": "integrated_pipeline",
                    "total_files_tested": len(test_files)
                },
                "results": results
            }, f, indent=2)

        print(f"\n🎯 Pipeline testing complete!")
        print(f"📊 Results saved to: {output_file}")

        # Summary
        successful = [r for r in results if r.get("extraction_success")]
        with_persona = [r for r in successful if r.get("has_persona_interpretation")]

        print(f"\n📈 SUMMARY:")
        print(f"   Files tested: {len(successful)}/{len(test_files)}")
        print(f"   With persona layer: {len(with_persona)}/{len(successful)}")

        return results

if __name__ == "__main__":
    tester = IntegratedPersonaTest()
    results = tester.run_all_tests()
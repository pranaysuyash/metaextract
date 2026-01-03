#!/usr/bin/env python3
"""
Baseline Test Script for Persona 1: Phone Photo Sarah
Tests current extraction engine with Sarah's test files
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add server directory to path
server_dir = Path(__file__).parent.parent / "server"
sys.path.insert(0, str(server_dir))

from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

class Persona1BaselineTester:
    def __init__(self):
        pass  # We'll use the direct function
        self.test_files_dir = Path(__file__).parent / "persona-files" / "sarah-phone-photos"
        self.results_dir = Path(__file__).parent / "test-results" / "persona-sarah"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def test_file(self, filename: str) -> dict:
        """Test extraction on a single file"""
        filepath = self.test_files_dir / filename
        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print(f"{'='*60}")

        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            # Extract metadata
            result = extract_comprehensive_metadata(str(filepath))

            # Analyze results for Sarah's key questions
            analysis = self.analyze_for_sarah(result, filename)

            return {
                "filename": filename,
                "file_size": os.path.getsize(filepath),
                "extraction_success": result.get("success", False),
                "total_fields_extracted": len(result.get("metadata", {})),
                "sarahs_questions": analysis,
                "raw_metadata_sample": self.get_sample_fields(result.get("metadata", {})),
                "extraction_time": result.get("extraction_time", "N/A"),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "filename": filename}

    def analyze_for_sarah(self, extraction_result: dict, filename: str) -> dict:
        """Analyze extraction results to answer Sarah's key questions"""
        metadata = extraction_result.get("metadata", {})

        return {
            "question_1_when": {
                "question": "When was this photo taken?",
                "answer": self.find_when_taken(metadata),
                "ease_of_finding": "TODO - Test with actual UI"
            },
            "question_2_where": {
                "question": "Where was I when I took this?",
                "answer": self.find_where_taken(metadata),
                "ease_of_finding": "TODO - Test with actual UI"
            },
            "question_3_what_device": {
                "question": "What phone took this?",
                "answer": self.find_device_info(metadata),
                "ease_of_finding": "TODO - Test with actual UI"
            },
            "question_4_authentic": {
                "question": "Is this photo authentic?",
                "answer": self.check_authenticity(metadata),
                "ease_of_finding": "TODO - Test with actual UI"
            }
        }

    def find_when_taken(self, metadata: dict) -> dict:
        """Find when photo was taken"""
        # Look for common date fields
        date_fields = [
            "EXIF:DateTimeOriginal",
            "EXIF:CreateDate",
            "EXIF:DateTimeDigitized",
            "IPTC:DateCreated",
            "XMP:CreateDate",
            "File:FileModificationDateTime"
        ]

        found_dates = {}
        for field in date_fields:
            if field in metadata:
                found_dates[field] = metadata[field]

        return {
            "found": len(found_dates) > 0,
            "dates": found_dates,
            "most_reliable": self.get_most_reliable_date(found_dates)
        }

    def find_where_taken(self, metadata: dict) -> dict:
        """Find GPS/location info"""
        gps_fields = [
            "EXIF:GPSLatitude",
            "EXIF:GPSLongitude",
            "EXIF:GPSPosition",
            "XMP:GPSLatitude",
            "XMP:GPSLongitude",
            "IPTC:Location",
            "Composite:GPSPosition"
        ]

        found_gps = {}
        for field in gps_fields:
            if field in metadata:
                found_gps[field] = metadata[field]

        return {
            "has_gps": len(found_gps) > 0,
            "coordinates": found_gps,
            "readable_location": "NOT IMPLEMENTED - Need reverse geocoding"
        }

    def find_device_info(self, metadata: dict) -> dict:
        """Find device/camera info"""
        device_fields = [
            "EXIF:Make",
            "EXIF:Model",
            "EXIF:Software",
            "EXIF:LensModel",
            "EXIF:DeviceModel",
            "XMP:Make",
            "XMP:Model"
        ]

        found_device = {}
        for field in device_fields:
            if field in metadata:
                found_device[field] = metadata[field]

        return {
            "found": len(found_device) > 0,
            "device_info": found_device,
            "friendly_name": self.format_device_name(found_device)
        }

    def check_authenticity(self, metadata: dict) -> dict:
        """Check photo authenticity"""
        authenticity_indicators = {
            "software_detected": "EXIF:Software" in metadata,
            "editing_detected": "EXIF:Software" in metadata and metadata["EXIF:Software"] not in ["", None],
            "has_hash": "File:FileMD5" in metadata or "File:FileSHA1" in metadata,
            "exif_intact": "EXIF:DateTimeOriginal" in metadata,
            "suspicious_fields": self.check_suspicious_fields(metadata)
        }

        return authenticity_indicators

    def get_most_reliable_date(self, dates: dict) -> str:
        """Get the most reliable date from available options"""
        priority = [
            "EXIF:DateTimeOriginal",
            "EXIF:CreateDate",
            "EXIF:DateTimeDigitized"
        ]

        for field in priority:
            if field in dates:
                return dates[field]

        return dates.get(next(iter(dates)), "No date found") if dates else "No date found"

    def format_device_name(self, device_info: dict) -> str:
        """Format device name in user-friendly way"""
        make = device_info.get("EXIF:Make", "")
        model = device_info.get("EXIF:Model", "")

        if make and model:
            return f"{make} {model}"
        elif model:
            return model
        elif make:
            return make
        else:
            return "Unknown device"

    def check_suspicious_fields(self, metadata: dict) -> list:
        """Check for fields that might indicate manipulation"""
        suspicious = []

        if "EXIF:Software" in metadata:
            software = metadata["EXIF:Software"]
            if software and software.lower() not in ["", "none", "original"]:
                suspicious.append(f"Editing software detected: {software}")

        return suspicious

    def get_sample_fields(self, metadata: dict, num_samples: int = 10) -> dict:
        """Get a sample of extracted fields to understand what we have"""
        field_names = list(metadata.keys())[:num_samples]
        return {field: metadata[field] for field in field_names}

    def run_all_tests(self):
        """Run tests on all Sarah's files"""
        print("📱 Starting Persona 1 Baseline Testing: Phone Photo Sarah")
        print("=" * 60)

        test_files = [
            "IMG_20251225_164634.jpg",
            "gps-map-photo.jpg"
        ]

        results = []
        for filename in test_files:
            result = self.test_file(filename)
            results.append(result)
            print(f"\n✅ Completed: {filename}")

        # Save comprehensive results
        output_file = self.results_dir / f"baseline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "persona": "Phone Photo Sarah",
                    "test_type": "baseline",
                    "total_files_tested": len(test_files)
                },
                "results": results
            }, f, indent=2)

        print(f"\n🎯 Baseline testing complete!")
        print(f"📊 Results saved to: {output_file}")

        # Print summary
        print(f"\n📈 SUMMARY:")
        print(f"   Files tested: {len([r for r in results if 'error' not in r])}/{len(test_files)}")
        print(f"   Total fields extracted: {sum(r.get('total_fields_extracted', 0) for r in results)}")

        return results

if __name__ == "__main__":
    tester = Persona1BaselineTester()
    tester.run_all_tests()
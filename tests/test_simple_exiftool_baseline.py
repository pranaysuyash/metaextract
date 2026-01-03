#!/usr/bin/env python3
"""
Simple Baseline Test using ExifTool directly for Persona 1
This bypasses the complex backend and gives us raw metadata to understand what we're working with
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

class SimpleExiftoolTester:
    def __init__(self):
        self.test_files_dir = Path(__file__).parent / "persona-files" / "sarah-phone-photos"
        self.results_dir = Path(__file__).parent / "test-results" / "persona-sarah"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_exiftool(self, filepath: str) -> dict:
        """Run exiftool and return parsed JSON output"""
        try:
            cmd = [
                'exiftool',
                '-json',
                '-coordinateFormat', '%.6f',  # GPS in decimal format
                filepath
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # Exiftool returns array, take first element
            return {"error": "Exiftool failed or returned empty data"}

        except subprocess.TimeoutExpired:
            return {"error": "Exiftool timed out"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse exiftool JSON output"}
        except Exception as e:
            return {"error": f"Exiftool error: {str(e)}"}

    def analyze_for_sarah(self, metadata: dict, filename: str) -> dict:
        """Analyze metadata to answer Sarah's key questions"""
        return {
            "question_1_when": {
                "question": "When was this photo taken?",
                "answer": self.find_when_taken(metadata),
            },
            "question_2_where": {
                "question": "Where was I when I took this?",
                "answer": self.find_where_taken(metadata),
            },
            "question_3_what_device": {
                "question": "What phone took this?",
                "answer": self.find_device_info(metadata),
            },
            "question_4_authentic": {
                "question": "Is this photo authentic?",
                "answer": self.check_authenticity(metadata),
            }
        }

    def find_when_taken(self, metadata: dict) -> dict:
        """Find when photo was taken"""
        date_fields = [
            "DateTimeOriginal",
            "CreateDate",
            "DateTimeDigitized",
            "DateCreated",
            "ModificationDate"
        ]

        found_dates = {}
        for field in date_fields:
            if field in metadata:
                found_dates[field] = metadata[field]

        return {
            "found": len(found_dates) > 0,
            "dates": found_dates,
            "most_reliable": self.get_most_reliable_date(found_dates),
            "explanation": "DateTimeOriginal is when photo was taken, CreateDate is when it was digitized"
        }

    def find_where_taken(self, metadata: dict) -> dict:
        """Find GPS/location info"""
        gps_data = {}

        # Check for GPS coordinates
        if "GPSLatitude" in metadata and "GPSLongitude" in metadata:
            try:
                lat = metadata.get("GPSLatitude")
                lon = metadata.get("GPSLongitude")
                lat_ref = metadata.get("GPSLatitudeRef", "N")
                lon_ref = metadata.get("GPSLongitudeRef", "E")

                # Apply direction
                if lat_ref in ["S", "s"]:
                    lat = -abs(lat)
                if lon_ref in ["W", "w"]:
                    lon = -abs(lon)

                gps_data["coordinates"] = {
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{lat:.6f}, {lon:.6f}"
                }

                # Look for location name fields
                if "GPSPosition" in metadata:
                    gps_data["position"] = metadata["GPSPosition"]

                if "City" in metadata:
                    gps_data["city"] = metadata["City"]
                if "State" in metadata:
                    gps_data["state"] = metadata["State"]
                if "Country" in metadata:
                    gps_data["country"] = metadata["Country"]

            except (TypeError, ValueError) as e:
                gps_data["error"] = f"Failed to parse GPS: {str(e)}"

        return {
            "has_gps": len(gps_data) > 0,
            "gps_data": gps_data,
            "readable_location": "Need reverse geocoding implementation",
            "has_readable_location": bool("city" in gps_data or "country" in gps_data)
        }

    def find_device_info(self, metadata: dict) -> dict:
        """Find device/camera info"""
        make = metadata.get("Make", "")
        model = metadata.get("Model", "")
        software = metadata.get("Software", "")

        device_info = {
            "make": make,
            "model": model,
            "software": software,
        }

        # Lens info if available
        if "LensModel" in metadata:
            device_info["lens"] = metadata["LensModel"]
        if "LensMake" in metadata:
            device_info["lens_make"] = metadata["LensMake"]

        return {
            "found": bool(make or model),
            "device_info": device_info,
            "friendly_name": self.format_device_name(make, model),
            "is_phone_camera": self.detect_phone_camera(make, model)
        }

    def check_authenticity(self, metadata: dict) -> dict:
        """Check photo authenticity"""
        software = metadata.get("Software", "")
        has_software = bool(software)

        # Check for signs of editing
        editing_signs = []
        if has_software and software.lower() not in ["", "none", "original"]:
            editing_signs.append(f"Software detected: {software}")

        # Check if EXIF data is intact
        has_datetime = "DateTimeOriginal" in metadata
        has_gps = "GPSLatitude" in metadata

        return {
            "appears_authentic": len(editing_signs) == 0,
            "confidence": "High" if len(editing_signs) == 0 else "Medium",
            "editing_detected": len(editing_signs) > 0,
            "editing_signs": editing_signs,
            "exif_intact": has_datetime,
            "gps_intact": has_gps,
            "explanation": "Authentic photos typically have original DateTime and GPS data intact"
        }

    def get_most_reliable_date(self, dates: dict) -> str:
        """Get the most reliable date from available options"""
        priority = [
            "DateTimeOriginal",
            "CreateDate",
            "DateTimeDigitized"
        ]

        for field in priority:
            if field in dates:
                return dates[field]

        return dates.get(next(iter(dates)), "No date found") if dates else "No date found"

    def format_device_name(self, make: str, model: str) -> str:
        """Format device name in user-friendly way"""
        if make and model:
            return f"{make} {model}"
        elif model:
            return model
        elif make:
            return make
        else:
            return "Unknown device"

    def detect_phone_camera(self, make: str, model: str) -> bool:
        """Detect if this is a phone camera"""
        phone_keywords = ["iphone", "samsung", "pixel", "oneplus", "xiaomi", "oppo", "vivo", "huawei", "motorola", "nokia", "lg"]
        model_lower = model.lower() if model else ""
        return any(keyword in model_lower for keyword in phone_keywords)

    def test_file(self, filename: str) -> dict:
        """Test a single file"""
        filepath = self.test_files_dir / filename
        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print(f"{'='*60}")

        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        # Run exiftool
        metadata = self.run_exiftool(str(filepath))

        if "error" in metadata:
            return {
                "filename": filename,
                "error": metadata["error"]
            }

        # Analyze for Sarah
        analysis = self.analyze_for_sarah(metadata, filename)

        return {
            "filename": filename,
            "file_size": filepath.stat().st_size,
            "extraction_success": True,
            "total_fields_extracted": len(metadata),
            "sarahs_questions": analysis,
            "exiftool_output_sample": dict(list(metadata.items())[:20]),  # First 20 fields as sample
            "all_metadata_fields": list(metadata.keys()),
            "timestamp": datetime.now().isoformat()
        }

    def run_all_tests(self):
        """Run tests on all Sarah's files"""
        print("📱 Starting Simple ExifTool Baseline Testing: Phone Photo Sarah")
        print("=" * 60)

        test_files = [
            "IMG_20251225_164634.jpg",
            "gps-map-photo.jpg"
        ]

        results = []
        for filename in test_files:
            result = self.test_file(filename)
            results.append(result)
            if "error" not in result:
                print(f"✅ Completed: {filename} - {result['total_fields_extracted']} fields extracted")
            else:
                print(f"❌ Failed: {filename} - {result.get('error', 'Unknown error')}")

        # Save results
        output_file = self.results_dir / f"exiftool_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "persona": "Phone Photo Sarah",
                    "test_type": "exiftool_baseline",
                    "total_files_tested": len(test_files)
                },
                "results": results
            }, f, indent=2)

        print(f"\n🎯 Testing complete!")
        print(f"📊 Results saved to: {output_file}")

        # Print summary
        successful = [r for r in results if "error" not in r]
        print(f"\n📈 SUMMARY:")
        print(f"   Files tested: {len(successful)}/{len(test_files)}")
        print(f"   Total fields extracted: {sum(r.get('total_fields_extracted', 0) for r in results)}")

        return results

if __name__ == "__main__":
    tester = SimpleExiftoolTester()
    results = tester.run_all_tests()

    # Print Sarah's key findings
    print(f"\n🔍 SARAH'S KEY FINDINGS:")
    print("=" * 60)

    for result in results:
        if "error" not in result:
            print(f"\n📸 {result['filename']}:")
            questions = result.get('sarahs_questions', {})

            # Q1: When?
            when = questions.get('question_1_when', {}).get('answer', {})
            print(f"  📅 When taken: {when.get('most_reliable', 'Unknown')}")

            # Q2: Where?
            where = questions.get('question_2_where', {}).get('answer', {})
            if where.get('has_gps'):
                coords = where.get('gps_data', {}).get('coordinates', {})
                print(f"  📍 Location: {coords.get('formatted', 'Unknown GPS')}")
            else:
                print(f"  📍 Location: No GPS data")

            # Q3: What device?
            device = questions.get('question_3_what_device', {}).get('answer', {})
            print(f"  📱 Device: {device.get('friendly_name', 'Unknown')}")

            # Q4: Authentic?
            authentic = questions.get('question_4_authentic', {}).get('answer', {})
            print(f"  ✨ Authentic: {authentic.get('appears_authentic', 'Unknown')} ({authentic.get('confidence', 'Unknown')} confidence)")
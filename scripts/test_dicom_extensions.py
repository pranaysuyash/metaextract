#!/usr/bin/env python3
"""
DICOM Extensions Testing and Validation Script
Tests all implemented DICOM extensions against real medical imaging files
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add server modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "server" / "extractor" / "modules"))

from dicom_extensions import (
    get_global_registry,
    initialize_extensions,
    get_all_extensions,
    get_extension_by_specialty
)


class DICOMExtensionTester:
    """Test framework for DICOM extensions"""

    def __init__(self, test_data_dir: str = "/Users/pranay/Downloads/Anonymized_20260102"):
        self.test_data_dir = Path(test_data_dir)
        self.registry = get_global_registry()
        self.results = {
            "test_run": datetime.now().isoformat(),
            "test_directory": str(test_data_dir),
            "extensions_tested": {},
            "summary": {}
        }

    def discover_test_files(self) -> List[Path]:
        """Find all DICOM files in test directory"""
        dicom_files = []
        if self.test_data_dir.exists():
            for ext in ["*.dcm", "*.dicom", "*.dicm"]:
                dicom_files.extend(self.test_data_dir.rglob(ext))
        return dicom_files

    def test_extension(self, specialty: str, test_files: List[Path]) -> Dict[str, Any]:
        """Test a single extension against available test files"""
        print(f"\n🔍 Testing {specialty}...")

        extension = get_extension_by_specialty(specialty)
        if not extension:
            return {
                "status": "error",
                "message": f"Extension not found: {specialty}"
            }

        # Test against up to 5 sample files
        sample_files = test_files[:5] if len(test_files) > 5 else test_files
        extension_results = []

        for test_file in sample_files:
            try:
                start_time = time.time()
                result = extension.extract_specialty_metadata(str(test_file))
                extraction_time = time.time() - start_time

                extension_results.append({
                    "file": str(test_file.name),
                    "fields_extracted": result.get("fields_extracted", 0),
                    "extraction_time": extraction_time,
                    "errors": result.get("errors", []),
                    "warnings": result.get("warnings", []),
                    "success": len(result.get("errors", [])) == 0
                })

            except Exception as e:
                extension_results.append({
                    "file": str(test_file.name),
                    "fields_extracted": 0,
                    "extraction_time": 0,
                    "errors": [str(e)],
                    "warnings": [],
                    "success": False
                })

        # Calculate statistics
        successful_tests = sum(1 for r in extension_results if r["success"])
        total_fields = sum(r["fields_extracted"] for r in extension_results)
        avg_time = sum(r["extraction_time"] for r in extension_results) / len(extension_results)

        return {
            "status": "success",
            "specialty": specialty,
            "tests_run": len(extension_results),
            "successful_tests": successful_tests,
            "failed_tests": len(extension_results) - successful_tests,
            "total_fields_extracted": total_fields,
            "avg_fields_per_file": total_fields / len(extension_results) if extension_results else 0,
            "avg_extraction_time": avg_time,
            "results": extension_results
        }

    def test_all_extensions(self) -> Dict[str, Any]:
        """Test all registered extensions"""
        print("🚀 Starting DICOM Extensions Test Suite")
        print(f"📁 Test directory: {self.test_data_dir}")
        print(f"🔧 Available extensions: {len(self.registry.get_all_specialties())}")

        # Initialize extensions
        initialize_extensions()

        # Discover test files
        test_files = self.discover_test_files()
        print(f"📊 Found {len(test_files)} DICOM test files")

        if not test_files:
            print("⚠️  No test files found!")
            return self.results

        # Test each extension
        specialties = self.registry.get_all_specialties()

        for specialty in specialties:
            result = self.test_extension(specialty, test_files)
            self.results["extensions_tested"][specialty] = result

            # Print immediate results
            if result["status"] == "success":
                print(f"✅ {specialty}: {result['successful_tests']}/{result['tests_run']} tests passed")
                print(f"   Fields: {result['total_fields_extracted']} total, {result['avg_fields_per_file']:.1f} avg/file")
                print(f"   Time: {result['avg_extraction_time']:.3f}s avg")
            else:
                print(f"❌ {specialty}: {result.get('message', 'Unknown error')}")

        # Generate summary
        self._generate_summary()

        return self.results

    def _generate_summary(self) -> None:
        """Generate test summary statistics"""
        extensions_tested = self.results["extensions_tested"]

        total_tests = sum(r.get("tests_run", 0) for r in extensions_tested.values())
        successful_tests = sum(r.get("successful_tests", 0) for r in extensions_tested.values())
        total_fields = sum(r.get("total_fields_extracted", 0) for r in extensions_tested.values())

        self.results["summary"] = {
            "total_extensions": len(extensions_tested),
            "total_tests_run": total_tests,
            "total_successful_tests": successful_tests,
            "total_failed_tests": total_tests - successful_tests,
            "total_fields_extracted": total_fields,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "extensions_passed": sum(1 for r in extensions_tested.values() if r.get("status") == "success")
        }

    def print_summary(self) -> None:
        """Print test summary to console"""
        summary = self.results["summary"]

        print("\n" + "=" * 70)
        print("📋 DICOM EXTENSIONS TEST SUMMARY")
        print("=" * 70)
        print(f"Extensions Tested: {summary['total_extensions']}")
        print(f"Tests Run: {summary['total_tests_run']}")
        print(f"Tests Passed: {summary['total_successful_tests']}")
        print(f"Tests Failed: {summary['total_failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Fields Extracted: {summary['total_fields_extracted']:,}")
        print("=" * 70)

        # Performance summary
        print("\n🏆 Top Performing Extensions:")
        extensions = list(self.results["extensions_tested"].values())
        extensions.sort(key=lambda x: x.get("total_fields_extracted", 0), reverse=True)

        for ext in extensions[:5]:
            if ext.get("status") == "success":
                print(f"  {ext['specialty']:30s}: {ext['total_fields_extracted']:>4} fields, {ext['avg_extraction_time']:.3f}s avg")

    def save_results(self, output_file: str = "dicom_extension_test_results.json") -> None:
        """Save test results to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_path}")


def main():
    """Main testing function"""
    print("🏥 DICOM Extensions Testing Framework")
    print("=" * 50)

    # Initialize tester
    tester = DICOMExtensionTester()

    # Run tests
    results = tester.test_all_extensions()

    # Print summary
    tester.print_summary()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results/dicom_extension_test_{timestamp}.json"
    tester.save_results(output_file)

    # Exit with appropriate code
    summary = results["summary"]
    exit_code = 0 if summary["total_failed_tests"] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
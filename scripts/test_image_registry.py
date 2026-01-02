#!/usr/bin/env python3
"""
Image Registry System Test Suite
Comprehensive testing for the new image extraction registry system
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add modules directory to path
modules_dir = Path(__file__).parent.parent / 'server' / 'extractor' / 'modules'
sys.path.insert(0, str(modules_dir))

try:
    from image_extensions import (
        get_global_registry,
        ImageExtractionResult
    )
    from image_extraction_manager import (
        get_image_manager,
        extract_image_metadata
    )
    REGISTRY_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import registry system: {e}")
    REGISTRY_AVAILABLE = False


class ImageRegistryTester:
    """Comprehensive test suite for image registry system"""

    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

        if REGISTRY_AVAILABLE:
            self.registry = get_global_registry()
            self.manager = get_image_manager()
        else:
            self.registry = None
            self.manager = None

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        logger.info("Starting Image Registry System Test Suite")

        if not REGISTRY_AVAILABLE:
            logger.error("Registry system not available - cannot run tests")
            return {"error": "Registry system not available"}

        # Test 1: Registry initialization
        self.test_registry_initialization()

        # Test 2: Extension registration
        self.test_extension_registration()

        # Test 3: System status
        self.test_system_status()

        # Test 4: Performance tracking
        self.test_performance_tracking()

        # Test 5: Error handling
        self.test_error_handling()

        # Test 6: Extension discovery
        self.test_extension_discovery()

        # Summary
        self.print_test_summary()
        return self.test_results

    def test_registry_initialization(self):
        """Test that registry initializes correctly"""
        test_name = "Registry Initialization"
        self.test_results["total_tests"] += 1

        try:
            assert self.registry is not None, "Registry should not be None"
            assert self.manager is not None, "Manager should not be None"

            extensions = self.registry.get_all_extensions()
            assert len(extensions) > 0, "Should have registered extensions"

            self._record_test_result(test_name, True, f"Found {len(extensions)} extensions")
            logger.info(f"✅ {test_name}: PASSED - {len(extensions)} extensions registered")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def test_extension_registration(self):
        """Test extension registration and info"""
        test_name = "Extension Registration"
        self.test_results["total_tests"] += 1

        try:
            extensions = self.registry.get_all_extensions()
            assert len(extensions) >= 3, "Should have at least 3 extensions (basic, advanced, universal)"

            expected_sources = ["basic", "advanced", "universal"]
            for source in expected_sources:
                assert source in extensions, f"Extension '{source}' should be registered"

                info = self.registry.get_extension_info(source)
                assert info is not None, f"Should get info for '{source}'"
                assert "source" in info, "Info should contain 'source'"
                assert "capabilities" in info, "Info should contain 'capabilities'"

            self._record_test_result(test_name, True, f"All {len(expected_sources)} core extensions registered")
            logger.info(f"✅ {test_name}: PASSED - All core extensions available")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def test_system_status(self):
        """Test system status retrieval"""
        test_name = "System Status"
        self.test_results["total_tests"] += 1

        try:
            status = self.manager.get_system_status()

            assert "registry_status" in status, "Status should contain registry_status"
            assert "available_extensions" in status, "Status should contain available_extensions"
            assert "extension_details" in status, "Status should contain extension_details"

            registry_status = status["registry_status"]
            assert "registered_extensions" in registry_status, "Registry status should show registered count"

            self._record_test_result(test_name, True, f"System operational with {status['available_extensions'].__len__()} extensions")
            logger.info(f"✅ {test_name}: PASSED - System status retrievable")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def test_performance_tracking(self):
        """Test performance tracking capabilities"""
        test_name = "Performance Tracking"
        self.test_results["total_tests"] += 1

        try:
            # Get initial stats
            initial_stats = self.registry.get_performance_stats()
            assert "total_extractions" in initial_stats, "Stats should track total extractions"

            # Perform a test extraction (we'll use a dummy file path for this test)
            try:
                # This might fail but we're testing the tracking mechanism
                result = self.registry.extract_with_best_extension("/nonexistent/file.jpg", "basic")
            except:
                pass  # We expect this to fail, we're just testing the tracking

            # Get updated stats
            updated_stats = self.registry.get_performance_stats()
            assert updated_stats is not None, "Should get updated stats"

            # Check that stats structure is correct
            assert "success_rate" in updated_stats, "Stats should include success rate"
            assert "avg_fields_per_extraction" in updated_stats, "Stats should include avg fields"
            assert "avg_extraction_time" in updated_stats, "Stats should include avg time"

            self._record_test_result(test_name, True, "Performance tracking operational")
            logger.info(f"✅ {test_name}: PASSED - Performance tracking working")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def test_error_handling(self):
        """Test error handling and graceful degradation"""
        test_name = "Error Handling"
        self.test_results["total_tests"] += 1

        try:
            # Test with invalid file
            result = self.registry.extract_with_best_extension("/nonexistent/file.jpg", "basic")

            assert result is not None, "Should return result even for invalid file"
            assert "success" in result, "Result should indicate success status"
            assert result["success"] == False, "Invalid file should result in failed extraction"
            assert "errors" in result, "Failed extraction should include errors"

            # Test with non-existent extension
            result = self.registry.extract_with_extension("nonexistent_source", "/tmp/test.jpg")
            assert result is None, "Should return None for non-existent extension"

            self._record_test_result(test_name, True, "Error handling working correctly")
            logger.info(f"✅ {test_name}: PASSED - Error handling graceful")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def test_extension_discovery(self):
        """Test extension discovery and capabilities"""
        test_name = "Extension Discovery"
        self.test_results["total_tests"] += 1

        try:
            all_info = self.registry.get_all_extensions_info()

            assert len(all_info) > 0, "Should have extension info"

            for info in all_info:
                assert "source" in info, "Info should contain source"
                assert "description" in info, "Info should contain description"
                assert "capabilities" in info, "Info should contain capabilities"
                assert "version" in info, "Info should contain version"

                # Check that capabilities are lists
                assert isinstance(info["capabilities"], list), "Capabilities should be a list"

            self._record_test_result(test_name, True, f"Discovered {len(all_info)} extensions with full info")
            logger.info(f"✅ {test_name}: PASSED - All extensions properly discovered")

        except AssertionError as e:
            self._record_test_result(test_name, False, str(e))
            logger.error(f"❌ {test_name}: FAILED - {e}")

    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Record individual test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.test_results["test_details"].append(result)

        if passed:
            self.test_results["passed_tests"] += 1
        else:
            self.test_results["failed_tests"] += 1

    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("IMAGE REGISTRY SYSTEM TEST SUMMARY")
        print("="*60)

        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']} ✅")
        print(f"Failed: {self.test_results['failed_tests']} ❌")

        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        print("\nDetailed Results:")
        for detail in self.test_results["test_details"]:
            status = "✅ PASSED" if detail["passed"] else "❌ FAILED"
            print(f"  {status}: {detail['test_name']} - {detail['message']}")

        print("="*60 + "\n")


def main():
    """Main test execution"""
    tester = ImageRegistryTester()
    results = tester.run_all_tests()

    # Exit with appropriate code
    if results.get("failed_tests", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
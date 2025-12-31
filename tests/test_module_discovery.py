#!/usr/bin/env python3
"""
Test the dynamic module discovery system.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the server/extractor directory to the path so we can import the module discovery
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server', 'extractor'))

from module_discovery import ModuleRegistry, discover_and_register_modules, get_module_discovery_stats


class TestModuleDiscovery(unittest.TestCase):
    """Test the module discovery system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ModuleRegistry()
        self.test_modules_dir = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any test modules directory
        if self.test_modules_dir and os.path.exists(self.test_modules_dir):
            import shutil
            shutil.rmtree(self.test_modules_dir, ignore_errors=True)
    
    def test_module_registry_initialization(self):
        """Test that the module registry initializes correctly."""
        self.assertIsNotNone(self.registry)
        self.assertEqual(len(self.registry.modules), 0)
        self.assertEqual(len(self.registry.categories), 0)
        self.assertEqual(self.registry.discovered_count, 0)
        self.assertEqual(self.registry.loaded_count, 0)
        self.assertEqual(self.registry.failed_count, 0)
    
    def test_discover_modules_with_nonexistent_directory(self):
        """Test module discovery with a nonexistent directory."""
        self.registry.discover_modules("/nonexistent/directory")
        
        # Should handle gracefully with no modules discovered
        self.assertEqual(self.registry.discovered_count, 0)
        self.assertEqual(self.registry.loaded_count, 0)
        self.assertEqual(self.registry.failed_count, 0)
    
    def test_discover_modules_with_empty_directory(self):
        """Test module discovery with an empty directory."""
        # Create a temporary empty directory
        self.test_modules_dir = tempfile.mkdtemp()
        
        self.registry.discover_modules(self.test_modules_dir)
        
        # Should handle gracefully with no modules discovered
        self.assertEqual(self.registry.discovered_count, 0)
        self.assertEqual(self.registry.loaded_count, 0)
        self.assertEqual(self.registry.failed_count, 0)
    
    def test_create_test_module(self):
        """Create a simple test module for discovery testing."""
        # Create a temporary directory with a test module
        self.test_modules_dir = tempfile.mkdtemp()
        
        # Create a simple test module
        test_module_content = '''
# Test module for module discovery

def extract_test_metadata(filepath: str) -> dict:
    """Extract test metadata."""
    return {
        "test_field": "test_value",
        "filepath": filepath
    }

def detect_test_features(filepath: str, param1: str = "default") -> dict:
    """Detect test features."""
    return {
        "feature_detected": True,
        "param1": param1
    }

def analyze_test_data(filepath: str) -> dict:
    """Analyze test data."""
    return {
        "analysis_result": "success"
    }
'''
        
        test_module_path = os.path.join(self.test_modules_dir, "test_module.py")
        with open(test_module_path, 'w') as f:
            f.write(test_module_content)
        
        return test_module_path
    
    def test_discover_simple_module(self):
        """Test discovery of a simple module."""
        test_module_path = self.test_create_test_module()
        
        # Discover modules
        self.registry.discover_modules(self.test_modules_dir)
        
        # Should have discovered and loaded the test module
        self.assertEqual(self.registry.discovered_count, 1)
        self.assertEqual(self.registry.loaded_count, 1)
        self.assertEqual(self.registry.failed_count, 0)
        
        # Check that the module was registered
        self.assertIn("test_module", self.registry.modules)
        
        module_info = self.registry.modules["test_module"]
        self.assertEqual(module_info["category"], "general")  # Should be categorized as general
        self.assertTrue(module_info["enabled"])
        
        # Check that extraction functions were found
        functions = module_info["functions"]
        self.assertIn("extract_test_metadata", functions)
        self.assertIn("detect_test_features", functions)
        self.assertIn("analyze_test_data", functions)
        
        # Test getting a specific function
        func = self.registry.get_extraction_function("test_module", "extract_test_metadata")
        self.assertIsNotNone(func)
        self.assertTrue(callable(func))
    
    def test_module_categorization(self):
        """Test that modules are categorized correctly."""
        # Create modules with different names to test categorization
        self.test_modules_dir = tempfile.mkdtemp()
        
        # Create modules in different categories
        module_contents = {
            "image_processing.py": "def extract_image_data(filepath): return {}",
            "video_analysis.py": "def extract_video_data(filepath): return {}",
            "audio_extraction.py": "def extract_audio_data(filepath): return {}",
            "scientific_analysis.py": "def extract_scientific_data(filepath): return {}",
            "forensic_tools.py": "def extract_forensic_data(filepath): return {}",
            "mobile_sensors.py": "def extract_mobile_data(filepath): return {}",
            "web_metadata.py": "def extract_web_data(filepath): return {}",
            "ai_ml_models.py": "def extract_ai_data(filepath): return {}",
            "general_utils.py": "def extract_general_data(filepath): return {}"
        }
        
        for filename, content in module_contents.items():
            module_path = os.path.join(self.test_modules_dir, filename)
            with open(module_path, 'w') as f:
                f.write(content)
        
        # Discover modules
        self.registry.discover_modules(self.test_modules_dir)
        
        # Check categorization
        expected_categories = {
            "image_processing": "image",
            "video_analysis": "video", 
            "audio_extraction": "audio",
            "scientific_analysis": "scientific",
            "forensic_tools": "forensic",
            "mobile_sensors": "mobile",
            "web_metadata": "web",
            "ai_ml_models": "ai",
            "general_utils": "general"
        }
        
        for module_name, expected_category in expected_categories.items():
            if module_name in self.registry.modules:
                actual_category = self.registry.modules[module_name]["category"]
                self.assertEqual(actual_category, expected_category, 
                                f"Module {module_name} should be categorized as {expected_category}, got {actual_category}")
    
    def test_module_prioritization(self):
        """Test that modules are prioritized correctly."""
        self.test_modules_dir = tempfile.mkdtemp()
        
        # Create modules with different priority indicators
        module_contents = {
            "core_extraction.py": "def extract_core_data(filepath): return {}",
            "base_metadata.py": "def extract_base_data(filepath): return {}",
            "essential_analysis.py": "def extract_essential_data(filepath): return {}",
            "primary_processing.py": "def extract_primary_data(filepath): return {}",
            "main_extraction.py": "def extract_main_data(filepath): return {}",
            "general_utils.py": "def extract_general_data(filepath): return {}"
        }
        
        for filename, content in module_contents.items():
            module_path = os.path.join(self.test_modules_dir, filename)
            with open(module_path, 'w') as f:
                f.write(content)
        
        # Discover modules
        self.registry.discover_modules(self.test_modules_dir)
        
        # Check priorities
        high_priority_modules = ["core_extraction", "base_metadata", "essential_analysis", "primary_processing", "main_extraction"]
        
        for module_name in high_priority_modules:
            if module_name in self.registry.modules:
                priority = self.registry.modules[module_name]["priority"]
                self.assertEqual(priority, 100, f"Module {module_name} should have priority 100")
        
        # General module should have lower priority
        if "general_utils" in self.registry.modules:
            priority = self.registry.modules["general_utils"]["priority"]
            self.assertEqual(priority, 30, "General module should have priority 30")
    
    def test_module_discovery_stats(self):
        """Test the module discovery statistics."""
        # Create a few test modules
        self.test_modules_dir = tempfile.mkdtemp()
        
        # Create some valid modules
        for i in range(3):
            module_path = os.path.join(self.test_modules_dir, f"valid_module_{i}.py")
            with open(module_path, 'w') as f:
                f.write(f'def extract_data_{i}(filepath): return {{"module": "valid_{i}"}}')
        
        # Create a module without extraction functions
        module_path = os.path.join(self.test_modules_dir, "no_functions.py")
        with open(module_path, 'w') as f:
            f.write('def utility_function(): return "not an extraction function"')
        
        # Discover modules
        self.registry.discover_modules(self.test_modules_dir)
        
        # Check statistics
        stats = self.registry.get_discovery_stats()
        
        self.assertEqual(stats["discovered_count"], 4)  # 3 valid + 1 invalid
        self.assertEqual(stats["loaded_count"], 3)  # Only the 3 valid ones
        self.assertEqual(stats["failed_count"], 1)  # The one without extraction functions
        self.assertEqual(stats["total_modules"], 3)
        self.assertGreater(stats["discovery_time_seconds"], 0)
        
        # Check that categories are included
        self.assertIn("categories", stats)
        self.assertIn("general", stats["categories"])
    
    def test_module_enable_disable(self):
        """Test enabling and disabling modules."""
        # Create a test module
        test_module_path = self.test_create_test_module()
        self.registry.discover_modules(self.test_modules_dir)
        
        # Module should be enabled by default
        self.assertTrue(self.registry.modules["test_module"]["enabled"])
        
        # Disable the module
        result = self.registry.disable_module("test_module")
        self.assertTrue(result)
        self.assertFalse(self.registry.modules["test_module"]["enabled"])
        self.assertIn("test_module", self.registry.disabled_modules)
        
        # Try to disable nonexistent module
        result = self.registry.disable_module("nonexistent_module")
        self.assertFalse(result)
        
        # Enable the module again
        result = self.registry.enable_module("test_module")
        self.assertTrue(result)
        self.assertTrue(self.registry.modules["test_module"]["enabled"])
        self.assertNotIn("test_module", self.registry.disabled_modules)
    
    def test_get_extraction_functions(self):
        """Test getting extraction functions."""
        test_module_path = self.test_create_test_module()
        self.registry.discover_modules(self.test_modules_dir)
        
        # Get all extraction functions
        all_functions = self.registry.get_all_extraction_functions()
        
        self.assertIn("test_module", all_functions)
        self.assertEqual(len(all_functions["test_module"]), 3)
        
        # Get specific function
        func = self.registry.get_extraction_function("test_module", "extract_test_metadata")
        self.assertIsNotNone(func)
        self.assertTrue(callable(func))
        
        # Get nonexistent function
        func = self.registry.get_extraction_function("test_module", "nonexistent_function")
        self.assertIsNone(func)
        
        func = self.registry.get_extraction_function("nonexistent_module", "extract_test_metadata")
        self.assertIsNone(func)


class TestModuleDiscoveryIntegration(unittest.TestCase):
    """Test integration with the comprehensive metadata engine."""
    
    def test_discover_and_register_modules_function(self):
        """Test the convenience function for module discovery."""
        # Create a temporary directory with a test module
        test_modules_dir = tempfile.mkdtemp()
        
        # Create a simple test module
        test_module_content = '''
def extract_integration_test(filepath: str) -> dict:
    return {"integration": "success", "file": filepath}
'''
        
        test_module_path = os.path.join(test_modules_dir, "integration_test.py")
        with open(test_module_path, 'w') as f:
            f.write(test_module_content)
        
        # Use the convenience function
        registry = discover_and_register_modules()
        
        # Check that it returns a registry
        self.assertIsNotNone(registry)
        self.assertIsInstance(registry, ModuleRegistry)
        
        # Clean up
        import shutil
        shutil.rmtree(test_modules_dir, ignore_errors=True)
    
    def test_get_module_discovery_stats_function(self):
        """Test the function to get module discovery stats."""
        # Create a registry and populate it
        registry = ModuleRegistry()
        
        # Create a temporary directory with a test module
        test_modules_dir = tempfile.mkdtemp()
        
        test_module_content = 'def extract_stats_test(filepath): return {"stats": "test"}'
        test_module_path = os.path.join(test_modules_dir, "stats_test.py")
        with open(test_module_path, 'w') as f:
            f.write(test_module_content)
        
        registry.discover_modules(test_modules_dir)
        
        # Get stats using the function
        stats = get_module_discovery_stats()
        
        # Should return the stats from the global registry
        self.assertIsNotNone(stats)
        self.assertIn("discovered_count", stats)
        self.assertIn("loaded_count", stats)
        
        # Clean up
        import shutil
        shutil.rmtree(test_modules_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
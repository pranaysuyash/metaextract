# server/extractor/module_discovery.py

"""
Dynamic Module Discovery and Auto-Registration System for MetaExtract

This system automatically discovers, registers, and manages all extraction modules
in the modules directory, eliminating the need for manual imports and providing
a scalable foundation for the comprehensive metadata extraction engine.

Features:
- Automatic discovery of extraction modules
- Dynamic import with error handling
- Module categorization and prioritization
- Performance tracking integration
- Backward compatibility with existing imports
"""

import os
import importlib
import logging
import inspect
import time
from typing import Dict, List, Optional, Callable, Any, Tuple, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Central registry for all extraction modules with dynamic discovery capabilities."""
    
    def __init__(self):
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.priority_modules: List[str] = []
        self.disabled_modules: Set[str] = set()
        self.discovery_time: float = 0.0
        self.discovered_count: int = 0
        self.loaded_count: int = 0
        self.failed_count: int = 0
    
    def discover_modules(self, base_path: str = "server/extractor/modules/") -> None:
        """
        Discover all extraction modules in the specified directory.
        
        Args:
            base_path: Base directory to search for modules
        """
        start_time = time.time()
        logger.info(f"Starting module discovery in {base_path}")
        
        try:
            modules_dir = Path(base_path)
            if not modules_dir.exists():
                logger.warning(f"Modules directory not found: {base_path}")
                return
            
            # Discover all Python files in the modules directory
            python_files = []
            for file_path in modules_dir.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue  # Skip __init__.py and other special files
                python_files.append(file_path)
            
            self.discovered_count = len(python_files)
            logger.info(f"Found {self.discovered_count} potential module files")
            
            # Process each module file
            for file_path in python_files:
                module_name = file_path.stem
                self._process_module_file(file_path, module_name)
            
            self.discovery_time = time.time() - start_time
            logger.info(f"Module discovery completed in {self.discovery_time:.3f}s")
            logger.info(f"Successfully loaded {self.loaded_count} modules, {self.failed_count} failed")
            
        except Exception as e:
            logger.error(f"Error during module discovery: {e}")
            self.discovery_time = time.time() - start_time
    
    def _process_module_file(self, file_path: Path, module_name: str) -> None:
        """
        Process a single module file and extract relevant functions.
        
        Args:
            file_path: Path to the module file
            module_name: Name of the module
        """
        try:
            # Import the module dynamically
            module_spec = importlib.util.spec_from_file_location(module_name, file_path)
            if module_spec is None:
                logger.warning(f"Could not load spec for module {module_name}")
                self.failed_count += 1
                return
            
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            
            # Find extraction functions in the module
            extraction_functions = self._find_extraction_functions(module)
            
            if extraction_functions:
                self._register_module(module_name, extraction_functions)
                self.loaded_count += 1
            else:
                logger.debug(f"No extraction functions found in module {module_name}")
                self.failed_count += 1
                
        except ImportError as e:
            logger.warning(f"Import error in module {module_name}: {e}")
            self.failed_count += 1
            self.disabled_modules.add(module_name)
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            self.failed_count += 1
            self.disabled_modules.add(module_name)
    
    def _find_extraction_functions(self, module: Any) -> Dict[str, Callable]:
        """
        Find extraction functions in a module.
        
        Args:
            module: The module to inspect
            
        Returns:
            Dictionary of function names to callable functions
        """
        extraction_functions = {}
        
        # Look for functions that match common extraction patterns
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("extract_") or name.startswith("detect_") or name.startswith("analyze_"):
                # Check if the function has appropriate parameters
                sig = inspect.signature(obj)
                params = list(sig.parameters.keys())
                
                # Extraction functions should typically accept filepath as first parameter
                if params and "filepath" in params[:3]:  # Check first 3 params
                    extraction_functions[name] = obj
                    logger.debug(f"Found extraction function: {name}")
        
        return extraction_functions
    
    def _register_module(self, module_name: str, functions: Dict[str, Callable]) -> None:
        """
        Register a module and its extraction functions.
        
        Args:
            module_name: Name of the module
            functions: Dictionary of function names to callable functions
        """
        # Categorize the module based on naming conventions
        category = self._categorize_module(module_name)
        
        # Register the module
        self.modules[module_name] = {
            "functions": functions,
            "category": category,
            "enabled": True,
            "priority": self._determine_priority(module_name, category)
        }
        
        # Add to category index
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(module_name)
        
        logger.info(f"Registered module '{module_name}' in category '{category}' with {len(functions)} functions")
    
    def _categorize_module(self, module_name: str) -> str:
        """
        Categorize a module based on its name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Category name
        """
        # Define category mappings
        category_keywords = {
            "image": ["image", "photo", "picture", "visual"],
            "video": ["video", "cinema", "motion", "film"],
            "audio": ["audio", "sound", "music", "acoustic"],
            "document": ["document", "pdf", "text", "office"],
            "scientific": ["scientific", "medical", "astronomy", "geospatial", "research"],
            "forensic": ["forensic", "security", "steganography", "manipulation"],
            "mobile": ["mobile", "ios", "android", "smartphone"],
            "web": ["web", "social", "internet", "online"],
            "ai": ["ai", "ml", "machine", "neural", "intelligence"],
            "emerging": ["emerging", "future", "quantum", "blockchain", "ar", "vr"],
            "industrial": ["industrial", "manufacturing", "engineering", "robotics"],
            "professional": ["professional", "broadcast", "studio", "production"]
        }
        
        # Check for category keywords in module name
        for category, keywords in category_keywords.items():
            if any(keyword in module_name.lower() for keyword in keywords):
                return category
        
        # Default category
        return "general"
    
    def _determine_priority(self, module_name: str, category: str) -> int:
        """
        Determine priority for a module.
        
        Args:
            module_name: Name of the module
            category: Category of the module
            
        Returns:
            Priority value (higher = more important)
        """
        # High priority modules
        high_priority_keywords = ["base", "core", "essential", "primary", "main"]
        if any(keyword in module_name.lower() for keyword in high_priority_keywords):
            return 100
        
        # Category-based priorities
        category_priorities = {
            "image": 90,
            "video": 85,
            "audio": 80,
            "document": 75,
            "scientific": 70,
            "forensic": 65,
            "mobile": 60,
            "web": 55,
            "ai": 50,
            "emerging": 45,
            "industrial": 40,
            "professional": 35,
            "general": 30
        }
        
        return category_priorities.get(category, 25)
    
    def get_modules_by_category(self, category: str) -> List[str]:
        """
        Get all modules in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of module names in the category
        """
        return self.categories.get(category, [])
    
    def get_extraction_function(self, module_name: str, function_name: str) -> Optional[Callable]:
        """
        Get a specific extraction function from a module.
        
        Args:
            module_name: Name of the module
            function_name: Name of the function
            
        Returns:
            The callable function or None if not found
        """
        if module_name in self.modules and function_name in self.modules[module_name]["functions"]:
            return self.modules[module_name]["functions"][function_name]
        return None
    
    def get_all_extraction_functions(self) -> Dict[str, Dict[str, Callable]]:
        """
        Get all available extraction functions.
        
        Returns:
            Dictionary of module names to their extraction functions
        """
        return {name: data["functions"] for name, data in self.modules.items() if data["enabled"]}
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module information dictionary or None if not found
        """
        return self.modules.get(module_name)
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the module discovery process.
        
        Returns:
            Dictionary of discovery statistics
        """
        return {
            "discovery_time_seconds": self.discovery_time,
            "discovered_count": self.discovered_count,
            "loaded_count": self.loaded_count,
            "failed_count": self.failed_count,
            "disabled_modules": list(self.disabled_modules),
            "total_modules": len(self.modules),
            "categories": {cat: len(mods) for cat, mods in self.categories.items()}
        }
    
    def disable_module(self, module_name: str) -> bool:
        """
        Disable a module to prevent it from being used.
        
        Args:
            module_name: Name of the module to disable
            
        Returns:
            True if module was disabled, False if not found
        """
        if module_name in self.modules:
            self.modules[module_name]["enabled"] = False
            self.disabled_modules.add(module_name)
            logger.info(f"Disabled module: {module_name}")
            return True
        return False
    
    def enable_module(self, module_name: str) -> bool:
        """
        Enable a previously disabled module.
        
        Args:
            module_name: Name of the module to enable
            
        Returns:
            True if module was enabled, False if not found
        """
        if module_name in self.modules:
            self.modules[module_name]["enabled"] = True
            self.disabled_modules.discard(module_name)
            logger.info(f"Enabled module: {module_name}")
            return True
        return False


# Global module registry instance
module_registry = ModuleRegistry()


def discover_and_register_modules() -> ModuleRegistry:
    """
    Convenience function to discover and register all modules.
    
    Returns:
        The populated module registry
    """
    module_registry.discover_modules()
    return module_registry


def get_extraction_function_safe(module_name: str, function_name: str) -> Optional[Callable]:
    """
    Safely get an extraction function with fallback to None.
    
    Args:
        module_name: Name of the module
        function_name: Name of the function
        
    Returns:
        The callable function or None if not available
    """
    try:
        return module_registry.get_extraction_function(module_name, function_name)
    except Exception as e:
        logger.warning(f"Error getting extraction function {module_name}.{function_name}: {e}")
        return None


def get_all_available_extraction_functions() -> Dict[str, Dict[str, Callable]]:
    """
    Get all available extraction functions that can be safely called.
    
    Returns:
        Dictionary of module names to their available extraction functions
    """
    return module_registry.get_all_extraction_functions()


def get_module_discovery_stats() -> Dict[str, Any]:
    """
    Get statistics about module discovery.
    
    Returns:
        Dictionary of discovery statistics
    """
    return module_registry.get_discovery_stats()
# server/extractor/module_discovery.py

"""
Dynamic Module Discovery and Auto-Registration System for MetaExtract

This system automatically discovers, registers, and manages all extraction modules
in the modules directory, eliminating the need for manual imports and providing
a scalable foundation for the comprehensive metadata extraction engine.

Features:
- Automatic discovery of extraction modules
- Dynamic import with comprehensive error handling
- Module categorization and prioritization
- Advanced dependency resolution and conflict detection
- Performance tracking and health monitoring
- Backward compatibility with existing imports
- Graceful degradation and error recovery
"""

import os
import sys
import importlib
import logging
import inspect
import time
import concurrent.futures
import threading
import types
import traceback
from typing import Dict, List, Optional, Callable, Any, Tuple, Set
from pathlib import Path

# Import custom exceptions for enhanced error handling
try:
    from .exceptions.extraction_exceptions import (
        MetaExtractException,
        DependencyError,
        ConfigurationError
    )
    MODULE_EXCEPTIONS_AVAILABLE = True
except ImportError:
    # Fallback exception classes if custom ones not available
    class MetaExtractException(Exception):
        pass
    class DependencyError(MetaExtractException):
        pass
    class ConfigurationError(MetaExtractException):
        pass
    MODULE_EXCEPTIONS_AVAILABLE = False

logger = logging.getLogger(__name__)

try:
    import watchdog.observers
    import watchdog.events
    WATCHDOG_AVAILABLE = True
    WATCHDOG_STUB = False
    _WatchdogEventHandlerBase = watchdog.events.FileSystemEventHandler
    _WatchdogEventType = watchdog.events.FileSystemEvent
except ImportError:
    WATCHDOG_AVAILABLE = True
    WATCHDOG_STUB = True
    watchdog = types.ModuleType("watchdog")
    observers_module = types.ModuleType("watchdog.observers")
    events_module = types.ModuleType("watchdog.events")

    class Observer:
        def schedule(self, *args, **kwargs):
            return None

        def start(self):
            return None

        def stop(self):
            return None

        def join(self, *args, **kwargs):
            return None

    class FileSystemEventHandler:
        pass

    class FileSystemEvent:
        def __init__(self):
            self.src_path = ""
            self.is_directory = False

    observers_module.Observer = Observer
    events_module.FileSystemEventHandler = FileSystemEventHandler
    events_module.FileSystemEvent = FileSystemEvent
    watchdog.observers = observers_module
    watchdog.events = events_module

    sys.modules.setdefault("watchdog", watchdog)
    sys.modules.setdefault("watchdog.observers", observers_module)
    sys.modules.setdefault("watchdog.events", events_module)

    _WatchdogEventHandlerBase = events_module.FileSystemEventHandler
    _WatchdogEventType = events_module.FileSystemEvent


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
        
        # Parallel execution configuration
        self.parallel_execution_enabled: bool = True
        self.max_workers: int = 4  # Default number of parallel workers
        self.parallel_execution_time: float = 0.0
        self.parallel_modules_executed: int = 0
        
        # Module dependency management
        self.module_dependencies: Dict[str, List[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.circular_dependencies: Set[str] = set()
        
        # Hot reloading configuration
        self.hot_reloading_enabled: bool = False
        self.watchdog_observer: Optional[Any] = None
        self.file_watcher: Optional[Any] = None
        self.hot_reload_lock: threading.Lock = threading.Lock()
        self.last_reload_time: float = 0.0
        self.min_reload_interval: float = 1.0  # Minimum interval between reloads
        self.hot_reload_count: int = 0
        self.hot_reload_errors: int = 0
        
        # Plugin system configuration
        self.plugins_enabled: bool = False
        self.plugin_paths: List[str] = []
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_load_errors: Dict[str, str] = {}
        self.plugin_discovery_time: float = 0.0
        self.plugins_loaded_count: int = 0
        self.plugins_failed_count: int = 0
        
        # Performance tracking and health monitoring
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.health_monitoring_enabled: bool = True
        self.health_thresholds: Dict[str, float] = {
            'error_rate': 0.1,      # 10% error rate threshold
            'timeout_rate': 0.05,   # 5% timeout rate threshold
            'slow_execution': 2.0,  # 2 seconds threshold for slow execution
            'memory_usage': 100.0   # 100MB memory usage threshold
        }
        self.health_stats: Dict[str, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.last_health_check: float = 0.0
        self.health_check_interval: float = 60.0  # 60 seconds between health checks
    
    def discover_modules(self, base_path: str = "server/extractor/modules/") -> None:
        """
        Discover all extraction modules in the specified directory with comprehensive error handling.
        
        Args:
            base_path: Base directory to search for modules
            
        Raises:
            ConfigurationError: If modules directory is invalid or inaccessible
            DependencyError: If critical dependencies are missing
        """
        start_time = time.time()
        logger.info(f"Starting module discovery in {base_path}")
        
        # Reset counters for fresh discovery
        self.discovered_count = 0
        self.loaded_count = 0
        self.failed_count = 0
        self.modules.clear()
        self.categories.clear()
        self.module_dependencies.clear()
        
        try:
            # Validate base path
            if not base_path or not isinstance(base_path, str):
                error_msg = f"Invalid modules directory path: {base_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="modules_directory",
                        context={"path": base_path}
                    )
                else:
                    logger.error(error_msg)
                    self.discovery_time = time.time() - start_time
                    return
            
            modules_dir = Path(base_path)
            
            # Check directory accessibility
            if not modules_dir.exists():
                error_msg = f"Modules directory not found: {base_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="modules_directory",
                        context={"path": base_path, "error": "not_found"}
                    )
                else:
                    logger.error(error_msg)
                    self.discovery_time = time.time() - start_time
                    return
            
            if not modules_dir.is_dir():
                error_msg = f"Modules path is not a directory: {base_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="modules_directory",
                        context={"path": base_path, "error": "not_directory"}
                    )
                else:
                    logger.error(error_msg)
                    self.discovery_time = time.time() - start_time
                    return
            
            # Check read permissions
            if not os.access(modules_dir, os.R_OK):
                error_msg = f"No read permission for modules directory: {base_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="modules_directory",
                        context={"path": base_path, "error": "permission_denied"}
                    )
                else:
                    logger.error(error_msg)
                    self.discovery_time = time.time() - start_time
                    return
            
            # Discover all Python files in the modules directory
            python_files = []
            try:
                for file_path in modules_dir.glob("*.py"):
                    if file_path.name.startswith("_"):
                        continue  # Skip __init__.py and other special files
                    if file_path.is_file() and file_path.suffix == ".py":
                        python_files.append(file_path)
            except Exception as e:
                error_msg = f"Error reading modules directory {base_path}: {str(e)}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="modules_directory",
                        context={"path": base_path, "original_error": str(e)}
                    ) from e
                else:
                    logger.error(error_msg)
                    self.discovery_time = time.time() - start_time
                    return
            
            self.discovered_count = len(python_files)
            logger.info(f"Found {self.discovered_count} potential module files")
            
            if self.discovered_count == 0:
                logger.warning(f"No Python module files found in {base_path}")
            
            # Process each module file with comprehensive error handling
            for file_path in python_files:
                try:
                    module_name = file_path.stem
                    self._process_module_file(file_path, module_name)
                except Exception as e:
                    error_msg = f"Failed to process module {file_path.stem}: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    self.failed_count += 1
                    self.disabled_modules.add(file_path.stem)
            
            # Build dependency graph after all modules are loaded
            self._build_dependency_graph()
            
            # Check for circular dependencies
            self._detect_circular_dependencies()
            
            self.discovery_time = time.time() - start_time
            logger.info(f"Module discovery completed in {self.discovery_time:.3f}s")
            logger.info(f"Successfully loaded {self.loaded_count} modules, {self.failed_count} failed")
            
            # Log summary statistics
            self._log_discovery_summary()
            
        except Exception as e:
            error_msg = f"Critical error during module discovery: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if MODULE_EXCEPTIONS_AVAILABLE and isinstance(e, MetaExtractException):
                raise  # Re-raise our custom exceptions
            elif MODULE_EXCEPTIONS_AVAILABLE:
                raise ConfigurationError(
                    message=error_msg,
                    config_key="module_discovery",
                    context={"original_error": str(e), "error_type": type(e).__name__}
                ) from e
            else:
                self.discovery_time = time.time() - start_time
    
    def _process_module_file(self, file_path: Path, module_name: str) -> None:
        """
        Process a single module file and extract relevant functions with comprehensive error handling.
        
        Args:
            file_path: Path to the module file
            module_name: Name of the module
            
        Raises:
            ImportError: If module cannot be imported
            ConfigurationError: If module has configuration issues
        """
        try:
            logger.debug(f"Processing module: {module_name}")
            
            # Validate module file
            if not file_path.exists():
                error_msg = f"Module file not found: {file_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="module_file",
                        context={"module": module_name, "path": str(file_path)}
                    )
                else:
                    logger.error(error_msg)
                    self.failed_count += 1
                    self.disabled_modules.add(module_name)
                    return
            
            if not file_path.is_file():
                error_msg = f"Module path is not a file: {file_path}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="module_file",
                        context={"module": module_name, "path": str(file_path)}
                    )
                else:
                    logger.error(error_msg)
                    self.failed_count += 1
                    self.disabled_modules.add(module_name)
                    return
            
            # Import the module dynamically with comprehensive error handling
            try:
                module_spec = importlib.util.spec_from_file_location(module_name, file_path)
                if module_spec is None:
                    error_msg = f"Could not load spec for module {module_name}"
                    if MODULE_EXCEPTIONS_AVAILABLE:
                        raise ConfigurationError(
                            message=error_msg,
                            config_key="module_import",
                            context={"module": module_name, "path": str(file_path)}
                        )
                    else:
                        logger.error(error_msg)
                        self.failed_count += 1
                        self.disabled_modules.add(module_name)
                        return
                
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                
            except ImportError as e:
                error_msg = f"Import error in module {module_name}: {str(e)}"
                logger.warning(f"{error_msg}\n{traceback.format_exc()}")
                
                # Check for missing dependencies
                missing_dep = self._extract_missing_dependency(str(e))
                if missing_dep and MODULE_EXCEPTIONS_AVAILABLE:
                    raise DependencyError(
                        missing_dependency=missing_dep,
                        context={
                            "module": module_name,
                            "path": str(file_path),
                            "original_error": str(e)
                        }
                    ) from e
                
                self.failed_count += 1
                self.disabled_modules.add(module_name)
                return
            except Exception as e:
                error_msg = f"Error loading module {module_name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="module_load",
                        context={
                            "module": module_name,
                            "path": str(file_path),
                            "original_error": str(e),
                            "error_type": type(e).__name__
                        }
                    ) from e
                else:
                    self.failed_count += 1
                    self.disabled_modules.add(module_name)
                    return
            
            # Find extraction functions in the module
            try:
                extraction_functions = self._find_extraction_functions(module)
                logger.debug(f"Found {len(extraction_functions)} extraction functions in {module_name}")
            except Exception as e:
                error_msg = f"Error finding extraction functions in module {module_name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                self.failed_count += 1
                self.disabled_modules.add(module_name)
                return
            
            # Find module dependencies
            try:
                dependencies = self._find_module_dependencies(module)
                logger.debug(f"Found {len(dependencies)} dependencies in {module_name}")
            except Exception as e:
                error_msg = f"Error finding dependencies in module {module_name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                # Continue with empty dependencies rather than failing the whole module
                dependencies = []
            
            if extraction_functions:
                try:
                    self._register_module(module_name, extraction_functions, dependencies, file_path)
                    self.loaded_count += 1
                    logger.info(f"Successfully loaded module: {module_name}")
                except Exception as e:
                    error_msg = f"Error registering module {module_name}: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    self.failed_count += 1
                    self.disabled_modules.add(module_name)
            else:
                logger.debug(f"No extraction functions found in module {module_name}")
                self.failed_count += 1
                self.disabled_modules.add(module_name)
                
        except Exception as e:
            error_msg = f"Unexpected error processing module {module_name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.failed_count += 1
            self.disabled_modules.add(module_name)
    
    def _extract_missing_dependency(self, error_msg: str) -> Optional[str]:
        """
        Extract missing dependency name from import error message.
        
        Args:
            error_msg: Import error message
            
        Returns:
            Name of missing dependency if found, None otherwise
        """
        try:
            # Common patterns for missing dependencies
            patterns = [
                "No module named '",
                "No module named \"",
                "Cannot import name '",
                "Cannot import name \""
            ]
            
            for pattern in patterns:
                if pattern in error_msg:
                    # Extract the module name
                    start_idx = error_msg.find(pattern) + len(pattern)
                    end_idx = error_msg.find("'", start_idx)
                    if end_idx == -1:
                        end_idx = error_msg.find("\"", start_idx)
                    
                    if end_idx != -1:
                        dep_name = error_msg[start_idx:end_idx].strip()
                        # Filter out common false positives
                        if dep_name and not dep_name.startswith("."):
                            return dep_name.split(".")[0]  # Get base module name
            
            return None
        except Exception:
            return None
    
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
    
    def _find_module_dependencies(self, module: Any) -> List[str]:
        """
        Find dependencies declared in a module.
        
        Args:
            module: The module to inspect
            
        Returns:
            List of dependency module names
        """
        dependencies = []
        
        # Look for MODULE_DEPENDENCIES constant
        if hasattr(module, "MODULE_DEPENDENCIES"):
            deps = getattr(module, "MODULE_DEPENDENCIES")
            if isinstance(deps, (list, tuple)):
                dependencies.extend(deps)
            elif isinstance(deps, str):
                dependencies.append(deps)
        
        # Look for get_dependencies function
        if hasattr(module, "get_dependencies") and callable(getattr(module, "get_dependencies")):
            try:
                func_deps = getattr(module, "get_dependencies")()
                if isinstance(func_deps, (list, tuple)):
                    dependencies.extend(func_deps)
                elif isinstance(func_deps, str):
                    dependencies.append(func_deps)
            except Exception as e:
                logger.warning(f"Error getting dependencies from module {module.__name__}: {e}")
        
        # Clean and deduplicate
        dependencies = list(set([dep.strip() for dep in dependencies if dep and isinstance(dep, str)]))
        
        return dependencies
    
    def _register_module(
        self,
        module_name: str,
        functions: Dict[str, Callable],
        dependencies: List[str] = None,
        module_path: Optional[Path] = None
    ) -> None:
        """
        Register a module and its extraction functions.
        
        Args:
            module_name: Name of the module
            functions: Dictionary of function names to callable functions
            dependencies: List of module dependencies
        """
        # Categorize the module based on naming conventions
        category = self._categorize_module(module_name)
        
        # Register the module
        self.modules[module_name] = {
            "functions": functions,
            "category": category,
            "enabled": True,
            "priority": self._determine_priority(module_name, category),
            "dependencies": dependencies or [],
            "path": str(module_path) if module_path else None,
        }
        
        # Initialize performance tracking for this module
        self._initialize_performance_tracking(module_name, functions)
        
        # Add to category index
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(module_name)
        
        # Register dependencies
        if dependencies:
            self.module_dependencies[module_name] = dependencies
            logger.info(f"Module '{module_name}' has dependencies: {dependencies}")
        
        logger.info(f"Registered module '{module_name}' in category '{category}' with {len(functions)} functions")
    
    def _build_dependency_graph(self) -> None:
        """
        Build a dependency graph from registered module dependencies.
        
        This method creates a graph representation of module dependencies
        to enable dependency resolution and circular dependency detection.
        """
        try:
            self.dependency_graph.clear()
            self.circular_dependencies.clear()
            
            # Build the graph
            for module_name, deps in self.module_dependencies.items():
                if module_name not in self.dependency_graph:
                    self.dependency_graph[module_name] = set()
                
                for dep in deps:
                    if dep not in self.dependency_graph:
                        self.dependency_graph[dep] = set()
                    self.dependency_graph[module_name].add(dep)
            
            logger.debug(f"Built dependency graph with {len(self.dependency_graph)} nodes")
            
        except Exception as e:
            logger.error(f"Error building dependency graph: {str(e)}")
            self.dependency_graph.clear()
    
    def _detect_circular_dependencies(self) -> None:
        """
        Detect circular dependencies in the module dependency graph.
        
        Uses depth-first search to identify cycles in the dependency graph.
        """
        try:
            visited = set()
            recursion_stack = set()
            
            def dfs(node: str) -> bool:
                visited.add(node)
                recursion_stack.add(node)
                
                for neighbor in self.dependency_graph.get(node, set()):
                    if neighbor not in self.modules:
                        # Dependency not found - this is a missing dependency, not circular
                        continue
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in recursion_stack:
                        # Circular dependency detected
                        cycle = self._find_cycle_path(node, neighbor)
                        self.circular_dependencies.update(cycle)
                        logger.warning(f"Circular dependency detected: {' -> '.join(cycle)}")
                        return True
                
                recursion_stack.remove(node)
                return False
            
            # Check each node in the graph
            for node in self.dependency_graph:
                if node not in visited:
                    dfs(node)
            
            if self.circular_dependencies:
                logger.warning(f"Found {len(self.circular_dependencies)} modules with circular dependencies")
            else:
                logger.info("No circular dependencies detected")
                
        except Exception as e:
            logger.error(f"Error detecting circular dependencies: {str(e)}")
    
    def _find_cycle_path(self, start: str, end: str) -> List[str]:
        """
        Find the path of a circular dependency.
        
        Args:
            start: Starting node of the cycle
            end: Ending node of the cycle
            
        Returns:
            List of nodes forming the cycle
        """
        try:
            path = []
            current = start
            
            # Trace back to find the cycle path
            while current != end:
                path.append(current)
                # Find the next node in the cycle
                for neighbor in self.dependency_graph.get(current, set()):
                    if neighbor in path or neighbor == end:
                        current = neighbor
                        break
            
            path.append(end)
            return path
        except Exception:
            return [start, end]
    
    def _log_discovery_summary(self) -> None:
        """
        Log a comprehensive summary of the module discovery process.
        """
        try:
            summary = [
                f"Module Discovery Summary:",
                f"  Total modules discovered: {self.discovered_count}",
                f"  Successfully loaded: {self.loaded_count}",
                f"  Failed to load: {self.failed_count}",
                f"  Disabled modules: {len(self.disabled_modules)}",
                f"  Discovery time: {self.discovery_time:.3f}s"
            ]
            
            if self.disabled_modules:
                summary.append(f"  Disabled: {', '.join(sorted(self.disabled_modules))}")
            
            if self.circular_dependencies:
                summary.append(f"  Circular dependencies: {len(self.circular_dependencies)}")
            
            # Log categories
            categories_summary = []
            for category, modules in self.categories.items():
                categories_summary.append(f"    {category}: {len(modules)} modules")
            
            if categories_summary:
                summary.append("  Categories:")
                summary.extend(categories_summary)
            
            logger.info("\n".join(summary))
            
        except Exception as e:
            logger.error(f"Error logging discovery summary: {str(e)}")
    
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
    
    def _initialize_performance_tracking(self, module_name: str, functions: Dict[str, Callable]) -> None:
        """
        Initialize performance tracking for a module.
        
        Args:
            module_name: Name of the module
            functions: Dictionary of function names to callable functions
        """
        if not self.health_monitoring_enabled:
            return
            
        # Initialize performance metrics for the module
        self.performance_metrics[module_name] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "timeout_executions": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0,
            "max_execution_time": 0.0,
            "min_execution_time": float('inf'),
            "last_execution_time": 0.0,
            "last_execution_status": "never",
            "last_execution_timestamp": 0.0,
            "error_rate": 0.0,
            "timeout_rate": 0.0,
            "health_score": 1.0,  # Start with perfect health
            "health_status": "healthy",
            "function_metrics": {}
        }
        
        # Initialize metrics for each function
        for function_name in functions.keys():
            self.performance_metrics[module_name]["function_metrics"][function_name] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "timeouts": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "max_time": 0.0,
                "min_time": float('inf'),
                "last_time": 0.0,
                "last_status": "never",
                "last_timestamp": 0.0
            }
        
        # Initialize performance history
        self.performance_history[module_name] = []
        
        logger.debug(f"Initialized performance tracking for module: {module_name}")
    
    def track_execution_performance(
        self,
        module_name: str,
        function_name: str,
        execution_time: float,
        status: str = "success",
        error: Optional[str] = None
    ) -> None:
        """
        Track execution performance for a module function.
        
        Args:
            module_name: Name of the module
            function_name: Name of the function
            execution_time: Execution time in seconds
            status: Execution status (success, failure, timeout)
            error: Error message if applicable
        """
        if not self.health_monitoring_enabled or module_name not in self.performance_metrics:
            return
            
        metrics = self.performance_metrics[module_name]
        func_metrics = metrics["function_metrics"].get(function_name, {})
        
        # Update module-level metrics
        metrics["total_executions"] += 1
        metrics["total_execution_time"] += execution_time
        metrics["last_execution_time"] = execution_time
        metrics["last_execution_status"] = status
        metrics["last_execution_timestamp"] = time.time()
        
        # Update based on status
        if status == "success":
            metrics["successful_executions"] += 1
            func_metrics["successes"] = func_metrics.get("successes", 0) + 1
        elif status == "failure":
            metrics["failed_executions"] += 1
            func_metrics["failures"] = func_metrics.get("failures", 0) + 1
            logger.warning(f"Function {module_name}.{function_name} failed: {error}")
        elif status == "timeout":
            metrics["timeout_executions"] += 1
            func_metrics["timeouts"] = func_metrics.get("timeouts", 0) + 1
            logger.warning(f"Function {module_name}.{function_name} timed out")
        
        # Update execution time statistics
        if execution_time > metrics["max_execution_time"]:
            metrics["max_execution_time"] = execution_time
        if execution_time < metrics["min_execution_time"]:
            metrics["min_execution_time"] = execution_time
            
        # Update function-level metrics
        func_metrics["executions"] = func_metrics.get("executions", 0) + 1
        func_metrics["total_time"] = func_metrics.get("total_time", 0.0) + execution_time
        func_metrics["last_time"] = execution_time
        func_metrics["last_status"] = status
        func_metrics["last_timestamp"] = time.time()
        
        if execution_time > func_metrics.get("max_time", 0):
            func_metrics["max_time"] = execution_time
        if execution_time < func_metrics.get("min_time", float('inf')):
            func_metrics["min_time"] = execution_time
        
        # Update averages
        total_executions = metrics["total_executions"]
        if total_executions > 0:
            metrics["avg_execution_time"] = metrics["total_execution_time"] / total_executions
            metrics["error_rate"] = metrics["failed_executions"] / total_executions
            metrics["timeout_rate"] = metrics["timeout_executions"] / total_executions
        
        func_executions = func_metrics.get("executions", 0)
        if func_executions > 0:
            func_metrics["avg_time"] = func_metrics.get("total_time", 0.0) / func_executions
        
        # Add to performance history
        self.performance_history[module_name].append({
            "timestamp": time.time(),
            "function": function_name,
            "execution_time": execution_time,
            "status": status,
            "error": error
        })
        
        # Keep history size manageable
        if len(self.performance_history[module_name]) > 1000:  # Keep last 1000 executions
            self.performance_history[module_name] = self.performance_history[module_name][-1000:]
        
        # Update health status
        self._update_health_status(module_name)
        
        logger.debug(f"Tracked execution for {module_name}.{function_name}: {execution_time:.3f}s, status: {status}")
    
    def _update_health_status(self, module_name: str) -> None:
        """
        Update health status for a module based on performance metrics.
        
        Args:
            module_name: Name of the module
        """
        if module_name not in self.performance_metrics:
            return
            
        metrics = self.performance_metrics[module_name]
        total_executions = metrics["total_executions"]
        
        if total_executions == 0:
            # No executions yet, consider healthy
            metrics["health_score"] = 1.0
            metrics["health_status"] = "healthy"
            return
            
        # Calculate health score components
        error_rate = metrics["error_rate"]
        timeout_rate = metrics["timeout_rate"]
        avg_time = metrics["avg_execution_time"]
        
        # Calculate component scores (0-1, higher is better)
        error_score = max(0, 1.0 - (error_rate / self.health_thresholds["error_rate"]))
        timeout_score = max(0, 1.0 - (timeout_rate / self.health_thresholds["timeout_rate"]))
        performance_score = max(0, 1.0 - min(1.0, avg_time / self.health_thresholds["slow_execution"]))
        
        # Weighted health score
        health_score = (
            0.4 * error_score + 
            0.3 * timeout_score + 
            0.3 * performance_score
        )
        
        # Determine health status
        if health_score >= 0.9:
            health_status = "healthy"
        elif health_score >= 0.7:
            health_status = "warning"
        elif health_score >= 0.5:
            health_status = "degraded"
        else:
            health_status = "critical"
        
        metrics["health_score"] = round(health_score, 3)
        metrics["health_status"] = health_status
        
        # Log health changes
        if health_status != metrics.get("previous_health_status", "healthy"):
            logger.info(f"Module {module_name} health changed to {health_status} (score: {health_score:.3f})")
            metrics["previous_health_status"] = health_status
        
        # Update health stats
        self.health_stats[module_name] = {
            "health_score": health_score,
            "health_status": health_status,
            "error_rate": error_rate,
            "timeout_rate": timeout_rate,
            "avg_execution_time": avg_time,
            "last_check": time.time()
        }
    
    def get_performance_metrics(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Performance metrics dictionary or None if not found
        """
        return self.performance_metrics.get(module_name)
    
    def get_all_performance_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for all modules.
        
        Returns:
            Dictionary of module names to their performance metrics
        """
        return self.performance_metrics
    
    def get_health_status(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get health status for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Health status dictionary or None if not found
        """
        return self.health_stats.get(module_name)
    
    def get_all_health_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status for all modules.
        
        Returns:
            Dictionary of module names to their health statuses
        """
        return self.health_stats
    
    def get_performance_history(self, module_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get performance history for a specific module.
        
        Args:
            module_name: Name of the module
            limit: Maximum number of history entries to return
            
        Returns:
            List of performance history entries
        """
        history = self.performance_history.get(module_name, [])
        return history[-limit:] if history else []
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get a summary of health statuses across all modules.
        
        Returns:
            Dictionary containing health summary statistics
        """
        healthy_count = 0
        warning_count = 0
        degraded_count = 0
        critical_count = 0
        total_modules = len(self.health_stats)
        
        for module_name, health_info in self.health_stats.items():
            status = health_info.get("health_status", "healthy")
            if status == "healthy":
                healthy_count += 1
            elif status == "warning":
                warning_count += 1
            elif status == "degraded":
                degraded_count += 1
            elif status == "critical":
                critical_count += 1
        
        avg_health_score = sum(info.get("health_score", 1.0) for info in self.health_stats.values()) / max(1, total_modules)
        
        return {
            "total_modules": total_modules,
            "healthy": healthy_count,
            "warning": warning_count,
            "degraded": degraded_count,
            "critical": critical_count,
            "average_health_score": round(avg_health_score, 3),
            "last_check": time.time(),
            "health_distribution": {
                "healthy": healthy_count,
                "warning": warning_count,
                "degraded": degraded_count,
                "critical": critical_count
            }
        }
    
    def enable_health_monitoring(self, enabled: bool = True) -> None:
        """
        Enable or disable health monitoring.
        
        Args:
            enabled: Whether to enable health monitoring
        """
        self.health_monitoring_enabled = enabled
        logger.info(f"Health monitoring {'enabled' if enabled else 'disabled'}")
    
    def set_health_thresholds(self, thresholds: Dict[str, float]) -> None:
        """
        Set custom health thresholds.
        
        Args:
            thresholds: Dictionary of threshold names to values
        """
        self.health_thresholds.update(thresholds)
        logger.info(f"Updated health thresholds: {self.health_thresholds}")
    
    def get_health_thresholds(self) -> Dict[str, float]:
        """
        Get current health thresholds.
        
        Returns:
            Dictionary of threshold names to values
        """
        return self.health_thresholds.copy()
    
    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check on all modules.
        
        Returns:
            Dictionary containing health check results
        """
        start_time = time.time()
        
        # Update health status for all modules
        for module_name in self.performance_metrics.keys():
            self._update_health_status(module_name)
        
        # Get health summary
        summary = self.get_health_summary()
        
        # Identify problematic modules
        problematic_modules = []
        for module_name, health_info in self.health_stats.items():
            if health_info["health_status"] in ["degraded", "critical"]:
                problematic_modules.append({
                    "module": module_name,
                    "status": health_info["health_status"],
                    "score": health_info["health_score"],
                    "error_rate": health_info["error_rate"],
                    "timeout_rate": health_info["timeout_rate"]
                })
        
        self.last_health_check = time.time()
        
        result = {
            "timestamp": self.last_health_check,
            "duration_seconds": time.time() - start_time,
            "summary": summary,
            "problematic_modules": problematic_modules,
            "thresholds": self.health_thresholds
        }
        
        logger.info(f"Health check completed: {summary['healthy']} healthy, {summary['warning']} warning, "
                   f"{summary['degraded']} degraded, {summary['critical']} critical modules")
        
        return result
    
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
    
    def build_dependency_graph(self) -> None:
        """
        Build a dependency graph from registered modules.
        
        This creates a graph where edges represent dependencies.
        """
        self.dependency_graph = {}
        self.circular_dependencies = set()
        
        # Initialize graph with all modules
        for module_name in self.modules.keys():
            self.dependency_graph[module_name] = set()
        
        # Add dependency edges - edges should go FROM dependency TO dependent
        for module_name, dependencies in self.module_dependencies.items():
            for dep in dependencies:
                if dep in self.dependency_graph:
                    # The edge goes from the dependency to the module that depends on it
                    self.dependency_graph[dep].add(module_name)
                else:
                    logger.warning(f"Dependency '{dep}' not found for module '{module_name}'")
        
        # Detect circular dependencies
        self._detect_circular_dependencies()
        
        if self.circular_dependencies:
            logger.warning(f"Circular dependencies detected: {self.circular_dependencies}")
    
    def _detect_circular_dependencies(self) -> None:
        """
        Detect circular dependencies in the dependency graph.
        """
        visited = set()
        recursion_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    # Circular dependency found
                    self.circular_dependencies.add(node)
                    self.circular_dependencies.add(neighbor)
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for module in self.dependency_graph.keys():
            if module not in visited:
                dfs(module)
    
    def get_dependency_order(self) -> List[str]:
        """
        Get modules in dependency order (dependencies first).
        
        Returns:
            List of module names in execution order
        """
        if not self.dependency_graph:
            self.build_dependency_graph()
        
        # Topological sort using Kahn's algorithm
        in_degree = {node: 0 for node in self.dependency_graph}
        
        # Calculate in-degree for each node
        for node in self.dependency_graph:
            for neighbor in self.dependency_graph[node]:
                in_degree[neighbor] += 1
        
        # Queue for nodes with no dependencies
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree for neighbors
            for neighbor in self.dependency_graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for circular dependencies (nodes not in result)
        if len(result) != len(self.dependency_graph):
            missing = set(self.dependency_graph.keys()) - set(result)
            logger.warning(f"Could not resolve dependencies for modules: {missing}")
        
        return result
    
    def get_module_dependencies(self, module_name: str) -> List[str]:
        """
        Get dependencies for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            List of dependency module names
        """
        return self.module_dependencies.get(module_name, [])
    
    def get_all_dependencies(self) -> Dict[str, List[str]]:
        """
        Get all module dependencies.
        
        Returns:
            Dictionary of module names to their dependencies
        """
        return self.module_dependencies
    
    def get_dependency_stats(self) -> Dict[str, Any]:
        """
        Get statistics about module dependencies.
        
        Returns:
            Dictionary of dependency statistics
        """
        return {
            "total_modules_with_dependencies": len(self.module_dependencies),
            "total_dependency_declarations": sum(len(deps) for deps in self.module_dependencies.values()),
            "circular_dependencies": list(self.circular_dependencies),
            "dependency_graph_size": len(self.dependency_graph)
        }
    
    def enable_hot_reloading(self, enabled: bool = True, watch_path: str = "server/extractor/modules/", min_interval: float = 1.0) -> None:
        """
        Enable or disable hot reloading of modules.
        
        Args:
            enabled: Whether to enable hot reloading
            watch_path: Path to watch for file changes
            min_interval: Minimum interval between reloads in seconds
        """
        if enabled:
            if not self.hot_reloading_enabled:
                self.hot_reloading_enabled = True
                self.min_reload_interval = min_interval
                self._start_file_watcher(watch_path)
                logger.info(f"Hot reloading enabled for path: {watch_path}")
            else:
                logger.info("Hot reloading already enabled")
        else:
            if self.hot_reloading_enabled:
                self._stop_file_watcher()
                self.hot_reloading_enabled = False
                logger.info("Hot reloading disabled")
    
    def _start_file_watcher(self, watch_path: str) -> None:
        """
        Start the file system watcher for hot reloading.
        
        Args:
            watch_path: Path to watch for changes
        """
        if WATCHDOG_STUB:
            logger.warning("watchdog not installed; using stub file watcher")
        try:
            # Create event handler
            event_handler = HotReloadEventHandler(self)
            
            # Create observer
            observer = watchdog.observers.Observer()
            observer.schedule(event_handler, watch_path, recursive=False)
            
            # Store references
            self.file_watcher = event_handler
            self.watchdog_observer = observer
            
            # Start observer in background thread
            observer.start()
            
            logger.info(f"File watcher started for: {watch_path}")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.hot_reloading_enabled = False
    
    def _stop_file_watcher(self) -> None:
        """
        Stop the file system watcher.
        """
        try:
            if self.watchdog_observer:
                self.watchdog_observer.stop()
                self.watchdog_observer.join()
                self.watchdog_observer = None
            
            if self.file_watcher:
                self.file_watcher = None
            
            logger.info("File watcher stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop file watcher: {e}")
    
    def hot_reload_module(self, module_name: str, enforce_interval: bool = True) -> bool:
        """
        Hot reload a specific module.
        
        Args:
            module_name: Name of the module to reload
            
        Returns:
            True if reload was successful, False otherwise
        """
        if not self.hot_reloading_enabled:
            logger.warning("Hot reloading is disabled")
            return False
        
        # Check minimum reload interval
        current_time = time.time()
        if enforce_interval and current_time - self.last_reload_time < self.min_reload_interval:
            logger.debug(f"Hot reload skipped: minimum interval {self.min_reload_interval}s not elapsed")
            return False
        
        try:
            with self.hot_reload_lock:
                # Find the module file
                module_info = self.modules.get(module_name, {})
                module_path = module_info.get("path")
                if module_path:
                    module_file = Path(module_path)
                else:
                    modules_dir = Path("server/extractor/modules/")
                    module_file = modules_dir / f"{module_name}.py"
                
                if not module_file.exists():
                    logger.warning(f"Module file not found: {module_file}")
                    self.hot_reload_errors += 1
                    return False
                
                logger.info(f"Hot reloading module: {module_name}")
                
                # Unload the module if it exists
                if module_name in self.modules:
                    # Disable the module temporarily
                    self.modules[module_name]["enabled"] = False
                    self.disabled_modules.add(module_name)
                
                # Re-process the module file
                self._process_module_file(module_file, module_name)
                
                # Rebuild dependency graph
                self.build_dependency_graph()
                
                # Update statistics
                self.last_reload_time = time.time()
                self.hot_reload_count += 1
                
                logger.info(f"Successfully hot reloaded module: {module_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to hot reload module {module_name}: {e}")
            self.hot_reload_errors += 1
            return False
    
    def hot_reload_all_modules(self) -> Dict[str, bool]:
        """
        Hot reload all modules.
        
        Returns:
            Dictionary of module names to reload success status
        """
        if not self.hot_reloading_enabled:
            logger.warning("Hot reloading is disabled")
            return {}
        
        results = {}
        
        try:
            # Get all module names
            module_names = list(self.modules.keys())
            
            for module_name in module_names:
                success = self.hot_reload_module(module_name, enforce_interval=False)
                results[module_name] = success
            
            logger.info(f"Hot reloaded {len(results)} modules: {sum(results.values())} successful, {len(results) - sum(results.values())} failed")
                
        except Exception as e:
            logger.error(f"Failed to hot reload all modules: {e}")
        
        return results
    
    def get_hot_reload_stats(self) -> Dict[str, Any]:
        """
        Get statistics about hot reloading.
        
        Returns:
            Dictionary of hot reload statistics
        """
        return {
            "hot_reloading_enabled": self.hot_reloading_enabled,
            "hot_reload_count": self.hot_reload_count,
            "hot_reload_errors": self.hot_reload_errors,
            "last_reload_time": self.last_reload_time,
            "min_reload_interval": self.min_reload_interval,
            "success_rate": self._calculate_hot_reload_success_rate()
        }
    
    def enable_plugins(self, enabled: bool = True, plugin_paths: Optional[List[str]] = None) -> None:
        """
        Enable or disable the plugin system.
        
        Args:
            enabled: Whether to enable plugins
            plugin_paths: List of paths to search for plugins
        """
        if enabled:
            if not self.plugins_enabled:
                self.plugins_enabled = True
                self.plugin_paths = plugin_paths or ["plugins/", "external_plugins/"]
                logger.info(f"Plugin system enabled with paths: {self.plugin_paths}")
            else:
                logger.info("Plugin system already enabled")
        else:
            if self.plugins_enabled:
                self.plugins_enabled = False
                self.plugin_paths = []
                logger.info("Plugin system disabled")
    
    def discover_and_load_plugins(self) -> None:
        """
        Discover and load all plugins from configured paths with enhanced error handling.
        
        Raises:
            ConfigurationError: If plugin discovery fails
            DependencyError: If critical plugin dependencies are missing
        """
        if not self.plugins_enabled:
            logger.warning("Plugin system is disabled")
            return
        
        start_time = time.time()
        logger.info(f"Starting plugin discovery in paths: {self.plugin_paths}")
        
        # Clear previous plugin data
        self.loaded_plugins = {}
        self.plugin_load_errors = {}
        self.plugins_loaded_count = 0
        self.plugins_failed_count = 0
        
        # Initialize plugin health monitoring
        self._initialize_plugin_health_monitoring()
        
        try:
            # Discover plugins in each path with comprehensive error handling
            for plugin_path in self.plugin_paths:
                try:
                    self._discover_plugins_in_path(plugin_path)
                except Exception as e:
                    error_msg = f"Error discovering plugins in path {plugin_path}: {str(e)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
                    
                    if MODULE_EXCEPTIONS_AVAILABLE:
                        raise ConfigurationError(
                            message=error_msg,
                            config_key="plugin_discovery",
                            context={
                                "plugin_path": plugin_path,
                                "original_error": str(e),
                                "error_type": type(e).__name__
                            }
                        ) from e
            
            self.plugin_discovery_time = time.time() - start_time
            logger.info(f"Plugin discovery completed in {self.plugin_discovery_time:.3f}s")
            logger.info(f"Loaded {self.plugins_loaded_count} plugins, {self.plugins_failed_count} failed")
            
            # Log plugin discovery summary
            self._log_plugin_discovery_summary()
            
        except Exception as e:
            error_msg = f"Critical error during plugin discovery: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if MODULE_EXCEPTIONS_AVAILABLE and isinstance(e, MetaExtractException):
                raise  # Re-raise our custom exceptions
            elif MODULE_EXCEPTIONS_AVAILABLE:
                raise ConfigurationError(
                    message=error_msg,
                    config_key="plugin_discovery",
                    context={"original_error": str(e), "error_type": type(e).__name__}
                ) from e
            else:
                self.plugin_discovery_time = time.time() - start_time
    
    def _discover_plugins_in_path(self, plugin_path: str) -> None:
        """
        Discover plugins in a specific path.
        
        Args:
            plugin_path: Path to search for plugins
        """
        try:
            plugins_dir = Path(plugin_path)
            if not plugins_dir.exists():
                logger.debug(f"Plugin directory not found: {plugin_path}")
                return
            
            # Find all Python files and directories in the plugin path
            for item in plugins_dir.iterdir():
                if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                    # Single-file plugin
                    self._load_plugin_file(item)
                elif item.is_dir() and not item.name.startswith("_"):
                    # Directory-based plugin
                    self._load_plugin_directory(item)
                    
        except Exception as e:
            logger.error(f"Error discovering plugins in {plugin_path}: {e}")
    
    def _load_plugin_file(self, plugin_file: Path) -> None:
        """
        Load a single-file plugin with comprehensive error handling.
        
        Args:
            plugin_file: Path to the plugin file
            
        Raises:
            ConfigurationError: If plugin file is invalid
            DependencyError: If plugin has missing dependencies
        """
        try:
            plugin_name = plugin_file.stem
            logger.info(f"Loading plugin file: {plugin_name}")
            
            # Validate plugin file
            if not plugin_file.exists():
                error_msg = f"Plugin file not found: {plugin_file}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_file",
                        context={"plugin": plugin_name, "path": str(plugin_file)}
                    )
                else:
                    logger.error(error_msg)
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    return
            
            if not plugin_file.is_file():
                error_msg = f"Plugin path is not a file: {plugin_file}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_file",
                        context={"plugin": plugin_name, "path": str(plugin_file)}
                    )
                else:
                    logger.error(error_msg)
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    return
            
            # Import the plugin module with comprehensive error handling
            try:
                module_spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                if module_spec is None:
                    error_msg = f"Could not load spec for plugin {plugin_name}"
                    if MODULE_EXCEPTIONS_AVAILABLE:
                        raise ConfigurationError(
                            message=error_msg,
                            config_key="plugin_import",
                            context={"plugin": plugin_name, "path": str(plugin_file)}
                        )
                    else:
                        logger.error(error_msg)
                        self.plugin_load_errors[plugin_name] = error_msg
                        self.plugins_failed_count += 1
                        return
                
                plugin_module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(plugin_module)
                
                # Add to sys.modules so it can be imported later
                sys.modules[plugin_name] = plugin_module
                
                # Register the plugin
                self._register_plugin(plugin_name, plugin_module, plugin_file)
                
            except ImportError as e:
                error_msg = f"Import error in plugin {plugin_file.name}: {str(e)}"
                logger.warning(f"{error_msg}\n{traceback.format_exc()}")
                
                # Check for missing dependencies
                missing_dep = self._extract_missing_dependency(str(e))
                if missing_dep and MODULE_EXCEPTIONS_AVAILABLE:
                    raise DependencyError(
                        missing_dependency=missing_dep,
                        context={
                            "plugin": plugin_name,
                            "path": str(plugin_file),
                            "original_error": str(e),
                            "plugin_type": "file"
                        }
                    ) from e
                
                self.plugin_load_errors[plugin_name] = error_msg
                self.plugins_failed_count += 1
            except Exception as e:
                error_msg = f"Error loading plugin {plugin_file.name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_load",
                        context={
                            "plugin": plugin_name,
                            "path": str(plugin_file),
                            "original_error": str(e),
                            "error_type": type(e).__name__,
                            "plugin_type": "file"
                        }
                    ) from e
                else:
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    
        except Exception as e:
            error_msg = f"Unexpected error loading plugin {plugin_file.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.plugin_load_errors[plugin_name] = error_msg
            self.plugins_failed_count += 1
    
    def _load_plugin_directory(self, plugin_dir: Path) -> None:
        """
        Load a directory-based plugin with comprehensive error handling.
        
        Args:
            plugin_dir: Path to the plugin directory
            
        Raises:
            ConfigurationError: If plugin directory is invalid
            DependencyError: If plugin has missing dependencies
        """
        try:
            plugin_name = plugin_dir.name
            logger.info(f"Loading plugin directory: {plugin_name}")
            
            # Validate plugin directory
            if not plugin_dir.exists():
                error_msg = f"Plugin directory not found: {plugin_dir}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_directory",
                        context={"plugin": plugin_name, "path": str(plugin_dir)}
                    )
                else:
                    logger.error(error_msg)
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    return
            
            if not plugin_dir.is_dir():
                error_msg = f"Plugin path is not a directory: {plugin_dir}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_directory",
                        context={"plugin": plugin_name, "path": str(plugin_dir)}
                    )
                else:
                    logger.error(error_msg)
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    return
            
            # Look for __init__.py or main plugin file
            init_file = plugin_dir / "__init__.py"
            main_file = plugin_dir / f"{plugin_name}.py"
            
            plugin_file = init_file if init_file.exists() else main_file
            
            if not plugin_file.exists():
                error_msg = f"No plugin file found in directory {plugin_name}"
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_file",
                        context={"plugin": plugin_name, "path": str(plugin_dir), "error": "no_plugin_file"}
                    )
                else:
                    logger.warning(error_msg)
                    self.plugin_load_errors[plugin_name] = error_msg
                    self.plugins_failed_count += 1
                    return
            
            # Import the plugin module with comprehensive error handling
            try:
                module_spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                if module_spec is None:
                    error_msg = f"Could not load spec for plugin {plugin_name}"
                    if MODULE_EXCEPTIONS_AVAILABLE:
                        raise ConfigurationError(
                            message=error_msg,
                            config_key="plugin_import",
                            context={"plugin": plugin_name, "path": str(plugin_file)}
                        )
                    else:
                        logger.warning(error_msg)
                        self.plugin_load_errors[plugin_name] = error_msg
                        self.plugins_failed_count += 1
                        return
                
                plugin_module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(plugin_module)
                
                # Add to sys.modules so it can be imported later
                sys.modules[plugin_name] = plugin_module
                
                # Register the plugin
                self._register_plugin(plugin_name, plugin_module, plugin_dir)
                
            except ImportError as e:
                error_msg = f"Import error in plugin {plugin_dir.name}: {str(e)}"
                logger.warning(f"{error_msg}\n{traceback.format_exc()}")
                
                # Check for missing dependencies
                missing_dep = self._extract_missing_dependency(str(e))
                if missing_dep and MODULE_EXCEPTIONS_AVAILABLE:
                    raise DependencyError(
                        missing_dependency=missing_dep,
                        context={
                            "plugin": plugin_name,
                            "path": str(plugin_dir),
                            "original_error": str(e),
                            "plugin_type": "directory"
                        }
                    ) from e
                
                self.plugin_load_errors[plugin_dir.name] = error_msg
                self.plugins_failed_count += 1
            except Exception as e:
                error_msg = f"Error loading plugin {plugin_dir.name}: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                if MODULE_EXCEPTIONS_AVAILABLE:
                    raise ConfigurationError(
                        message=error_msg,
                        config_key="plugin_load",
                        context={
                            "plugin": plugin_name,
                            "path": str(plugin_dir),
                            "original_error": str(e),
                            "error_type": type(e).__name__,
                            "plugin_type": "directory"
                        }
                    ) from e
                else:
                    self.plugin_load_errors[plugin_dir.name] = error_msg
                    self.plugins_failed_count += 1
                    
        except Exception as e:
            error_msg = f"Unexpected error loading plugin {plugin_dir.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.plugin_load_errors[plugin_dir.name] = error_msg
            self.plugins_failed_count += 1
    
    def _register_plugin(self, plugin_name: str, plugin_module: Any, plugin_path: Path) -> None:
        """
        Register a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin
            plugin_module: The loaded plugin module
            plugin_path: Path to the plugin file/directory
        """
        try:
            # Find extraction functions in the plugin
            extraction_functions = self._find_extraction_functions(plugin_module)
            
            # Find plugin metadata
            plugin_metadata = self._extract_plugin_metadata(plugin_module)
            
            # Find plugin dependencies
            dependencies = self._find_module_dependencies(plugin_module)
            
            # Register the plugin
            self.loaded_plugins[plugin_name] = {
                "functions": extraction_functions,
                "metadata": plugin_metadata,
                "dependencies": dependencies,
                "path": str(plugin_path),
                "type": "directory" if plugin_path.is_dir() else "file",
                "enabled": True
            }
            
            # Also add to regular modules for execution
            self._register_module(plugin_name, extraction_functions, dependencies, plugin_path)
            
            # Initialize health monitoring for this plugin
            if plugin_name not in self.health_stats:
                self.health_stats[plugin_name] = {
                    'error_count': 0,
                    'success_count': 0,
                    'last_error': None,
                    'last_success': None,
                    'status': 'healthy',
                    'last_check': time.time(),
                    'type': 'plugin'
                }
            
            self.plugins_loaded_count += 1
            logger.info(f"Successfully loaded plugin: {plugin_name} with {len(extraction_functions)} functions")
            
        except Exception as e:
            error_msg = f"Error registering plugin {plugin_name}: {e}"
            logger.error(error_msg)
            self.plugin_load_errors[plugin_name] = error_msg
            self.plugins_failed_count += 1
    
    def _extract_plugin_metadata(self, plugin_module: Any) -> Dict[str, Any]:
        """
        Extract metadata from a plugin module.
        
        Args:
            plugin_module: The plugin module to inspect
            
        Returns:
            Dictionary of plugin metadata
        """
        metadata = {
            "version": "1.0.0",
            "author": "Unknown",
            "description": "No description",
            "license": "MIT"
        }
        
        # Look for standard metadata attributes
        if hasattr(plugin_module, "PLUGIN_VERSION"):
            metadata["version"] = getattr(plugin_module, "PLUGIN_VERSION")
        
        if hasattr(plugin_module, "PLUGIN_AUTHOR"):
            metadata["author"] = getattr(plugin_module, "PLUGIN_AUTHOR")
        
        if hasattr(plugin_module, "PLUGIN_DESCRIPTION"):
            metadata["description"] = getattr(plugin_module, "PLUGIN_DESCRIPTION")
        
        if hasattr(plugin_module, "PLUGIN_LICENSE"):
            metadata["license"] = getattr(plugin_module, "PLUGIN_LICENSE")
        
        # Look for get_plugin_metadata function
        if hasattr(plugin_module, "get_plugin_metadata") and callable(getattr(plugin_module, "get_plugin_metadata")):
            try:
                func_metadata = getattr(plugin_module, "get_plugin_metadata")()
                if isinstance(func_metadata, dict):
                    metadata.update(func_metadata)
            except Exception as e:
                logger.warning(f"Error getting plugin metadata from function: {e}")
        
        return metadata
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information dictionary or None if not found
        """
        return self.loaded_plugins.get(plugin_name)
    
    def get_all_plugins_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all loaded plugins.
        
        Returns:
            Dictionary of plugin names to their information
        """
        return self.loaded_plugins
    
    def get_discovered_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all discovered plugins (both modules and plugins).
        
        Returns:
            Dictionary of plugin/module names to their information
        """
        # Combine both regular modules and plugins
        all_plugins = {}
        
        # Add regular modules
        for module_name, module_info in self.modules.items():
            all_plugins[module_name] = {
                "type": "module",
                "module": sys.modules.get(module_name),
                "path": module_info.get("path"),
                "category": module_info.get("category"),
                "functions": list(module_info.get("functions", {}).keys()),
                "dependencies": module_info.get("dependencies", []),
                "enabled": module_info.get("enabled", True)
            }
        
        # Add plugins
        for plugin_name, plugin_info in self.loaded_plugins.items():
            all_plugins[plugin_name] = {
                "type": "plugin",
                "module": sys.modules.get(plugin_name),
                "path": plugin_info.get("path"),
                "metadata": plugin_info.get("metadata", {}),
                "functions": list(plugin_info.get("functions", {}).keys()),
                "dependencies": plugin_info.get("dependencies", []),
                "enabled": plugin_info.get("enabled", True)
            }
        
        return all_plugins
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """
        Get statistics about plugin loading.
        
        Returns:
            Dictionary of plugin statistics
        """
        return {
            "plugins_enabled": self.plugins_enabled,
            "plugin_paths": self.plugin_paths,
            "plugins_loaded": self.plugins_loaded_count,
            "plugins_failed": self.plugins_failed_count,
            "plugin_discovery_time": self.plugin_discovery_time,
            "loaded_plugins": list(self.loaded_plugins.keys()),
            "failed_plugins": list(self.plugin_load_errors.keys()),
            "success_rate": self._calculate_plugin_success_rate()
        }
    
    def _calculate_plugin_success_rate(self) -> float:
        """
        Calculate plugin loading success rate.
        
        Returns:
            Success rate as a float between 0 and 1
        """
        total_attempts = self.plugins_loaded_count + self.plugins_failed_count
        if total_attempts == 0:
            return 0.0
        
        return round(self.plugins_loaded_count / total_attempts, 3)
    
    def _initialize_plugin_health_monitoring(self) -> None:
        """
        Initialize health monitoring for all plugins.
        """
        try:
            # Initialize health metrics for each loaded plugin
            for plugin_name in self.loaded_plugins.keys():
                if plugin_name not in self.health_stats:
                    self.health_stats[plugin_name] = {
                        'error_count': 0,
                        'success_count': 0,
                        'last_error': None,
                        'last_success': None,
                        'status': 'healthy',
                        'last_check': time.time(),
                        'type': 'plugin'
                    }
            
            logger.debug(f"Initialized health monitoring for {len(self.health_stats)} plugins")
            
        except Exception as e:
            logger.error(f"Error initializing plugin health monitoring: {str(e)}")
    
    def _log_plugin_discovery_summary(self) -> None:
        """
        Log a comprehensive summary of plugin discovery results.
        """
        try:
            summary = [
                f"Plugin Discovery Summary:",
                f"  Total plugins loaded: {self.plugins_loaded_count}",
                f"  Total plugins failed: {self.plugins_failed_count}",
                f"  Discovery time: {self.plugin_discovery_time:.3f}s"
            ]
            
            if self.plugin_load_errors:
                summary.append(f"  Plugins with errors: {len(self.plugin_load_errors)}")
                # Show first few errors
                error_plugins = list(self.plugin_load_errors.keys())[:3]
                for plugin_name in error_plugins:
                    summary.append(f"    - {plugin_name}: {self.plugin_load_errors[plugin_name]}")
                if len(self.plugin_load_errors) > 3:
                    summary.append(f"    - ... and {len(self.plugin_load_errors) - 3} more")
            
            if self.loaded_plugins:
                # Show plugin categories
                plugin_types = {}
                for plugin_info in self.loaded_plugins.values():
                    plugin_type = plugin_info.get('type', 'unknown')
                    plugin_types[plugin_type] = plugin_types.get(plugin_type, 0) + 1
                
                type_summary = []
                for plugin_type, count in plugin_types.items():
                    type_summary.append(f"    {plugin_type}: {count}")
                
                if type_summary:
                    summary.append("  Plugin types:")
                    summary.extend(type_summary)
            
            logger.info("\n".join(summary))
            
        except Exception as e:
            logger.error(f"Error logging plugin discovery summary: {str(e)}")
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            True if plugin was enabled, False if not found
        """
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins[plugin_name]["enabled"] = True
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
            
        Returns:
            True if plugin was disabled, False if not found
        """
        if plugin_name in self.loaded_plugins:
            self.loaded_plugins[plugin_name]["enabled"] = False
            logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to reload
            
        Returns:
            True if reload was successful, False otherwise
        """
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            plugin_info = self.loaded_plugins[plugin_name]
            plugin_path = Path(plugin_info["path"])
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]
            
            # Reload the plugin
            if plugin_path.is_file():
                self._load_plugin_file(plugin_path)
            else:
                self._load_plugin_directory(plugin_path)
            
            logger.info(f"Reloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False

    def update_plugin(self, plugin_name: str, new_plugin_path: str) -> bool:
        """
        Update a plugin by replacing it with a new version.
        
        Args:
            plugin_name: Name of the plugin to update
            new_plugin_path: Path to the new plugin file or directory
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # First disable the current plugin
            if not self.disable_plugin(plugin_name):
                logger.warning(f"Plugin {plugin_name} not found or already disabled")
                return False
            
            # Backup the old plugin information
            old_plugin_info = self.loaded_plugins.get(plugin_name, {})
            
            # Remove the old plugin from sys.modules
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
            
            # Load the new plugin
            new_plugin_path_obj = Path(new_plugin_path)
            if new_plugin_path_obj.is_file():
                self._load_plugin_file(new_plugin_path_obj)
            elif new_plugin_path_obj.is_dir():
                self._load_plugin_directory(new_plugin_path_obj)
            else:
                logger.error(f"Invalid plugin path: {new_plugin_path}")
                return False
            
            logger.info(f"Successfully updated plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update plugin {plugin_name}: {e}")
            
            # Try to restore the old plugin if update failed
            try:
                if old_plugin_info:
                    self.loaded_plugins[plugin_name] = old_plugin_info
                    logger.warning(f"Restored plugin {plugin_name} after failed update")
            except Exception as restore_error:
                logger.error(f"Failed to restore plugin {plugin_name}: {restore_error}")
            
            return False

    def check_plugin_updates(self) -> Dict[str, Dict[str, Any]]:
        """
        Check for available updates for all loaded plugins.
        
        Returns:
            Dictionary of plugin names to update information
        """
        update_info = {}
        
        try:
            for plugin_name, plugin_info in self.loaded_plugins.items():
                update_available = False
                update_version = None
                update_source = None
                
                # Check if plugin has update checking capability
                if hasattr(plugin_info.get('module', {}), 'check_for_updates'):
                    try:
                        module = plugin_info.get('module', {})
                        update_result = module.check_for_updates()
                        if update_result and update_result.get('available', False):
                            update_available = True
                            update_version = update_result.get('version', 'unknown')
                            update_source = update_result.get('source', 'unknown')
                    except Exception as e:
                        logger.warning(f"Error checking updates for plugin {plugin_name}: {e}")
                
                update_info[plugin_name] = {
                    'update_available': update_available,
                    'current_version': plugin_info.get('metadata', {}).get('version', 'unknown'),
                    'update_version': update_version,
                    'update_source': update_source,
                    'last_checked': time.time()
                }
            
            logger.info(f"Checked updates for {len(update_info)} plugins")
            return update_info
            
        except Exception as e:
            logger.error(f"Error checking plugin updates: {e}")
            return {}

    def _calculate_hot_reload_success_rate(self) -> float:
        """
        Calculate hot reload success rate.
        
        Returns:
            Success rate as a float between 0 and 1
        """
        if self.hot_reload_count == 0:
            return 0.0
        
        total_attempts = self.hot_reload_count + self.hot_reload_errors
        if total_attempts == 0:
            return 0.0
        
        return round(self.hot_reload_count / total_attempts, 3)

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
            "categories": {cat: len(mods) for cat, mods in self.categories.items()},
            "parallel_execution": self.get_parallel_execution_stats()
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

    def enable_module_global(module_name: str) -> bool:
        """
        Enable a previously disabled module globally.
        
        Args:
            module_name: Name of the module to enable
            
        Returns:
            True if module was enabled, False if not found
        """
        return module_registry.enable_module(module_name)

    def disable_module_global(module_name: str) -> bool:
        """
        Disable a module to prevent it from being used globally.
        
        Args:
            module_name: Name of the module to disable
            
        Returns:
            True if module was disabled, False if not found
        """
        return module_registry.disable_module(module_name)
    
    def enable_parallel_execution(self, enabled: bool = True, max_workers: int = 4) -> None:
        """
        Enable or disable parallel execution of modules.
        
        Args:
            enabled: Whether to enable parallel execution
            max_workers: Maximum number of parallel workers
        """
        self.parallel_execution_enabled = enabled
        self.max_workers = max_workers
        logger.info(f"Parallel execution {'enabled' if enabled else 'disabled'} with {max_workers} workers")
    
    def execute_modules_parallel(
        self, 
        filepath: str, 
        execution_func: Callable[[str, Callable, str], Dict[str, Any]],
        filter_func: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute multiple modules in parallel.
        
        Args:
            filepath: Path to the file being processed
            execution_func: Function to execute each module (module_name, func, filepath)
            filter_func: Optional function to filter which modules to execute
            
        Returns:
            Dictionary of module results
        """
        if not self.parallel_execution_enabled:
            logger.info("Parallel execution disabled, falling back to sequential")
            return self._execute_modules_sequential(filepath, execution_func, filter_func)
        
        start_time = time.time()
        results = {}
        executed_count = 0
        
        try:
            # Get all available modules
            all_functions = self.get_all_extraction_functions()
            
            # Filter modules if filter function provided
            modules_to_execute = []
            module_names_to_execute = []
            
            for module_name, functions in all_functions.items():
                module_info = self.get_module_info(module_name)
                if module_info and module_info.get("enabled", True):
                    if filter_func is None or filter_func(module_name, module_info):
                        for function_name, extraction_func in functions.items():
                            modules_to_execute.append((module_name, function_name, extraction_func))
                            if module_name not in module_names_to_execute:
                                module_names_to_execute.append(module_name)
            
            # If we have dependencies, execute in dependency order
            if self.module_dependencies and module_names_to_execute:
                try:
                    # Get dependency order
                    dependency_order = self.get_dependency_order()
                    
                    # Filter to only modules we're executing
                    ordered_module_names = [name for name in dependency_order if name in module_names_to_execute]
                    
                    # Reorder modules_to_execute based on dependency order
                    # This ensures dependencies are executed first
                    modules_to_execute.sort(key=lambda x: ordered_module_names.index(x[0]) if x[0] in ordered_module_names else len(ordered_module_names))
                    
                except Exception as e:
                    logger.warning(f"Could not resolve dependency order: {e}")
            
            if not modules_to_execute:
                logger.debug("No modules to execute in parallel")
                return results
            
            logger.info(f"Executing {len(modules_to_execute)} modules in parallel with {self.max_workers} workers")
            
            # Execute modules in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_module = {}
                
                for module_name, function_name, extraction_func in modules_to_execute:
                    module_key = f"{module_name}_{function_name}"
                    future = executor.submit(
                        execution_func, 
                        module_key, 
                        extraction_func, 
                        filepath
                    )
                    future_to_module[future] = module_key
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_module):
                    module_key = future_to_module[future]
                    try:
                        result = future.result()
                        if result:
                            results[module_key] = result
                            executed_count += 1
                    except Exception as e:
                        logger.error(f"Error in parallel execution of {module_key}: {e}")
            
            self.parallel_execution_time = time.time() - start_time
            self.parallel_modules_executed = executed_count
            logger.info(f"Parallel execution completed in {self.parallel_execution_time:.3f}s, executed {executed_count} modules")
            
        except Exception as e:
            logger.error(f"Error in parallel module execution: {e}")
            
        return results
    
    def _execute_modules_sequential(
        self, 
        filepath: str, 
        execution_func: Callable[[str, Callable, str], Dict[str, Any]],
        filter_func: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute modules sequentially (fallback method).
        
        Args:
            filepath: Path to the file being processed
            execution_func: Function to execute each module
            filter_func: Optional function to filter which modules to execute
            
        Returns:
            Dictionary of module results
        """
        start_time = time.time()
        results = {}
        executed_count = 0
        
        try:
            # Get all available modules
            all_functions = self.get_all_extraction_functions()
            
            # Execute modules sequentially
            for module_name, functions in all_functions.items():
                module_info = self.get_module_info(module_name)
                if module_info and module_info.get("enabled", True):
                    if filter_func is None or filter_func(module_name, module_info):
                        for function_name, extraction_func in functions.items():
                            module_key = f"{module_name}_{function_name}"
                            try:
                                result = execution_func(module_key, extraction_func, filepath)
                                if result:
                                    results[module_key] = result
                                    executed_count += 1
                            except Exception as e:
                                logger.error(f"Error executing module {module_key}: {e}")
            
            self.parallel_execution_time = time.time() - start_time
            self.parallel_modules_executed = executed_count
            logger.info(f"Sequential execution completed in {self.parallel_execution_time:.3f}s, executed {executed_count} modules")
            
        except Exception as e:
            logger.error(f"Error in sequential module execution: {e}")
            
        return results
    
    def get_parallel_execution_stats(self) -> Dict[str, Any]:
        """
        Get statistics about parallel execution.
        
        Returns:
            Dictionary of parallel execution statistics
        """
        return {
            "parallel_execution_enabled": self.parallel_execution_enabled,
            "max_workers": self.max_workers,
            "parallel_execution_time_seconds": self.parallel_execution_time,
            "parallel_modules_executed": self.parallel_modules_executed,
            "parallel_efficiency": self._calculate_parallel_efficiency()
        }
    
    def _calculate_parallel_efficiency(self) -> float:
        """
        Calculate parallel execution efficiency.
        
        Returns:
            Efficiency score (0-1)
        """
        if self.parallel_modules_executed == 0 or self.parallel_execution_time == 0:
            return 0.0
        
        # Simple efficiency calculation: modules per second normalized
        # This is a basic metric - could be enhanced with more sophisticated analysis
        efficiency = min(1.0, (self.parallel_modules_executed / self.parallel_execution_time) / 100)
        return round(efficiency, 3)


class HotReloadEventHandler(_WatchdogEventHandlerBase):
    """
    File system event handler for hot reloading modules.
    """
    
    def __init__(self, module_registry: ModuleRegistry):
        super().__init__()
        self.registry = module_registry
        self.last_event_time = 0.0
        self.debounce_interval = 0.5  # Debounce interval to avoid multiple triggers
    
    def on_modified(self, event: _WatchdogEventType):
        """
        Handle file modification events.
        """
        if not event.is_directory:
            current_time = time.time()
            if current_time - self.last_event_time > self.debounce_interval:
                self.last_event_time = current_time
                
                # Extract module name from file path
                if event.src_path.endswith('.py'):
                    module_name = os.path.basename(event.src_path)[:-3]  # Remove .py
                    
                    # Skip special files
                    if module_name.startswith('_'):
                        return
                    
                    # Trigger hot reload
                    threading.Thread(target=self._hot_reload_module, args=(module_name,), daemon=True).start()
    
    def _hot_reload_module(self, module_name: str):
        """
        Hot reload a module in a separate thread.
        """
        try:
            logger.info(f"Detected change in module: {module_name}, triggering hot reload")
            success = self.registry.hot_reload_module(module_name)
            
            if success:
                logger.info(f"Successfully hot reloaded module: {module_name}")
                
                # Rebuild dependency graph after reload
                self.registry.build_dependency_graph()
                
                # Log dependency stats
                dependency_stats = self.registry.get_dependency_stats()
                if dependency_stats["circular_dependencies"]:
                    logger.warning(f"Circular dependencies after reload: {dependency_stats['circular_dependencies']}")
            else:
                logger.warning(f"Failed to hot reload module: {module_name}")
                
        except Exception as e:
            logger.error(f"Error in hot reload thread for {module_name}: {e}")
    
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


def create_safe_execution_wrapper(safe_extract_func: Callable) -> Callable:
    """
    Create a wrapper function for safe module execution that matches the parallel execution signature.
    
    Args:
        safe_extract_func: The safe extract function (like safe_extract_module)
        
    Returns:
        Wrapper function with signature (module_key, extraction_func, filepath)
    """
    def wrapper(module_key: str, extraction_func: Callable, filepath: str) -> Dict[str, Any]:
        try:
            result = safe_extract_func(extraction_func, filepath, module_key)
            return result
        except Exception as e:
            logger.error(f"Error in safe execution wrapper for {module_key}: {e}")
            return {
                "available": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "module": module_key,
                "performance": {
                    module_key: {
                        "duration_seconds": 0,
                        "status": "failed",
                        "error_type": type(e).__name__
                    }
                }
            }
    
    return wrapper


def enable_parallel_execution_global(enabled: bool = True, max_workers: int = 4) -> None:
    """
    Enable or disable parallel execution globally.
    
    Args:
        enabled: Whether to enable parallel execution
        max_workers: Maximum number of parallel workers
    """
    module_registry.enable_parallel_execution(enabled, max_workers)


def build_dependency_graph_global() -> None:
    """
    Build the dependency graph globally.
    """
    module_registry.build_dependency_graph()


def get_dependency_stats_global() -> Dict[str, Any]:
    """
    Get dependency statistics globally.
    
    Returns:
        Dictionary of dependency statistics
    """
    return module_registry.get_dependency_stats()


def get_dependency_order_global() -> List[str]:
    """
    Get modules in dependency order globally.
    
    Returns:
        List of module names in execution order
    """
    return module_registry.get_dependency_order()


def enable_hot_reloading_global(enabled: bool = True, watch_path: str = "server/extractor/modules/", min_interval: float = 1.0) -> None:
    """
    Enable or disable hot reloading globally.
    
    Args:
        enabled: Whether to enable hot reloading
        watch_path: Path to watch for file changes
        min_interval: Minimum interval between reloads in seconds
    """
    module_registry.enable_hot_reloading(enabled, watch_path, min_interval)


def hot_reload_module_global(module_name: str) -> bool:
    """
    Hot reload a specific module globally.
    
    Args:
        module_name: Name of the module to reload
        
    Returns:
        True if reload was successful, False otherwise
    """
    return module_registry.hot_reload_module(module_name)


def hot_reload_all_modules_global() -> Dict[str, bool]:
    """
    Hot reload all modules globally.
    
    Returns:
        Dictionary of module names to reload success status
    """
    return module_registry.hot_reload_all_modules()


def get_hot_reload_stats_global() -> Dict[str, Any]:
    """
    Get hot reload statistics globally.
    
    Returns:
        Dictionary of hot reload statistics
    """
    return module_registry.get_hot_reload_stats()


def enable_plugins_global(enabled: bool = True, plugin_paths: Optional[List[str]] = None) -> None:
    """
    Enable or disable the plugin system globally.
    
    Args:
        enabled: Whether to enable plugins
        plugin_paths: List of paths to search for plugins
    """
    module_registry.enable_plugins(enabled, plugin_paths)


def discover_and_load_plugins_global() -> None:
    """
    Discover and load all plugins globally.
    """
    module_registry.discover_and_load_plugins()


def get_plugin_info_global(plugin_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific plugin globally.
    
    Args:
        plugin_name: Name of the plugin
        
    Returns:
        Plugin information dictionary or None if not found
    """
    return module_registry.get_plugin_info(plugin_name)


def get_all_plugins_info_global() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all loaded plugins globally.
    
    Returns:
        Dictionary of plugin names to their information
    """
    return module_registry.get_all_plugins_info()


def get_plugin_stats_global() -> Dict[str, Any]:
    """
    Get plugin statistics globally.
    
    Returns:
        Dictionary of plugin statistics
    """
    return module_registry.get_plugin_stats()


def get_discovered_plugins_global() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all discovered plugins globally.
    
    Returns:
        Dictionary of plugin/module names to their information
    """
    return module_registry.get_discovered_plugins()


def enable_plugin_global(plugin_name: str) -> bool:
    """
    Enable a specific plugin globally.
    
    Args:
        plugin_name: Name of the plugin to enable
        
    Returns:
        True if plugin was enabled, False if not found
    """
    return module_registry.enable_plugin(plugin_name)


def disable_plugin_global(plugin_name: str) -> bool:
    """
    Disable a specific plugin globally.
    
    Args:
        plugin_name: Name of the plugin to disable
        
    Returns:
        True if plugin was disabled, False if not found
    """
    return module_registry.disable_plugin(plugin_name)


def reload_plugin_global(plugin_name: str) -> bool:
    """
    Reload a specific plugin globally.
    
    Args:
        plugin_name: Name of the plugin to reload
        
    Returns:
        True if reload was successful, False otherwise
    """
    return module_registry.reload_plugin(plugin_name)


def enable_health_monitoring_global(enabled: bool = True) -> None:
    """
    Enable or disable health monitoring globally.
    
    Args:
        enabled: Whether to enable health monitoring
    """
    module_registry.enable_health_monitoring(enabled)


def set_health_thresholds_global(thresholds: Dict[str, float]) -> None:
    """
    Set custom health thresholds globally.
    
    Args:
        thresholds: Dictionary of threshold names to values
    """
    module_registry.set_health_thresholds(thresholds)


def get_health_thresholds_global() -> Dict[str, float]:
    """
    Get current health thresholds globally.
    
    Returns:
        Dictionary of threshold names to values
    """
    return module_registry.get_health_thresholds()


def get_performance_metrics_global(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get performance metrics for a specific module globally.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Performance metrics dictionary or None if not found
    """
    return module_registry.get_performance_metrics(module_name)


def get_all_performance_metrics_global() -> Dict[str, Dict[str, Any]]:
    """
    Get performance metrics for all modules globally.
    
    Returns:
        Dictionary of module names to their performance metrics
    """
    return module_registry.get_all_performance_metrics()


def get_health_status_global(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get health status for a specific module globally.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Health status dictionary or None if not found
    """
    return module_registry.get_health_status(module_name)


def get_all_health_statuses_global() -> Dict[str, Dict[str, Any]]:
    """
    Get health status for all modules globally.
    
    Returns:
        Dictionary of module names to their health statuses
    """
    return module_registry.get_all_health_statuses()


def get_performance_history_global(module_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get performance history for a specific module globally.
    
    Args:
        module_name: Name of the module
        limit: Maximum number of history entries to return
        
    Returns:
        List of performance history entries
    """
    return module_registry.get_performance_history(module_name, limit)


def get_health_summary_global() -> Dict[str, Any]:
    """
    Get a summary of health statuses across all modules globally.
    
    Returns:
        Dictionary containing health summary statistics
    """
    return module_registry.get_health_summary()


def perform_health_check_global() -> Dict[str, Any]:
    """
    Perform a comprehensive health check on all modules globally.
    
    Returns:
        Dictionary containing health check results
    """
    return module_registry.perform_health_check()


def track_execution_performance_global(
    module_name: str,
    function_name: str,
    execution_time: float,
    status: str = "success",
    error: Optional[str] = None
) -> None:
    """
    Track execution performance for a module function globally.
    
    Args:
        module_name: Name of the module
        function_name: Name of the function
        execution_time: Execution time in seconds
        status: Execution status (success, failure, timeout)
        error: Error message if applicable
    """
    module_registry.track_execution_performance(module_name, function_name, execution_time, status, error)


def update_plugin_global(plugin_name: str, new_plugin_path: str) -> bool:
    """
    Update a plugin by replacing it with a new version globally.
    
    Args:
        plugin_name: Name of the plugin to update
        new_plugin_path: Path to the new plugin file or directory
        
    Returns:
        True if update was successful, False otherwise
    """
    return module_registry.update_plugin(plugin_name, new_plugin_path)


def check_plugin_updates_global() -> Dict[str, Dict[str, Any]]:
    """
    Check for available updates for all loaded plugins globally.
    
    Returns:
        Dictionary of plugin names to update information
    """
    return module_registry.check_plugin_updates()


def enable_module_global(module_name: str) -> bool:
    """
    Enable a previously disabled module globally.
    
    Args:
        module_name: Name of the module to enable
        
    Returns:
        True if module was enabled, False if not found
    """
    return module_registry.enable_module(module_name)


def disable_module_global(module_name: str) -> bool:
    """
    Disable a module to prevent it from being used globally.
    
    Args:
        module_name: Name of the module to disable
        
    Returns:
        True if module was disabled, False if not found
    """
    return module_registry.disable_module(module_name)

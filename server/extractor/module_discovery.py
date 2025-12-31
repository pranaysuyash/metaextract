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
import concurrent.futures
import threading
import watchdog.observers
import watchdog.events
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
        self.watchdog_observer: Optional[watchdog.observers.Observer] = None
        self.file_watcher: Optional[watchdog.events.FileSystemEventHandler] = None
        self.hot_reload_lock: threading.Lock = threading.Lock()
        self.last_reload_time: float = 0.0
        self.min_reload_interval: float = 1.0  # Minimum interval between reloads
        self.hot_reload_count: int = 0
        self.hot_reload_errors: int = 0
    
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
            
            # Find module dependencies
            dependencies = self._find_module_dependencies(module)
            
            if extraction_functions:
                self._register_module(module_name, extraction_functions, dependencies)
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
    
    def _register_module(self, module_name: str, functions: Dict[str, Callable], dependencies: List[str] = None) -> None:
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
            "dependencies": dependencies or []
        }
        
        # Add to category index
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(module_name)
        
        # Register dependencies
        if dependencies:
            self.module_dependencies[module_name] = dependencies
            logger.info(f"Module '{module_name}' has dependencies: {dependencies}")
        
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
    
    def hot_reload_module(self, module_name: str) -> bool:
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
        if current_time - self.last_reload_time < self.min_reload_interval:
            logger.debug(f"Hot reload skipped: minimum interval {self.min_reload_interval}s not elapsed")
            return False
        
        try:
            with self.hot_reload_lock:
                # Find the module file
                modules_dir = Path("server/extractor/modules/")
                module_file = modules_dir / f"{module_name}.py"
                
                if not module_file.exists():
                    logger.warning(f"Module file not found: {module_file}")
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
            with self.hot_reload_lock:
                # Get all module names
                module_names = list(self.modules.keys())
                
                for module_name in module_names:
                    success = self.hot_reload_module(module_name)
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


class HotReloadEventHandler(watchdog.events.FileSystemEventHandler):
    """
    File system event handler for hot reloading modules.
    """
    
    def __init__(self, module_registry: ModuleRegistry):
        super().__init__()
        self.registry = module_registry
        self.last_event_time = 0.0
        self.debounce_interval = 0.5  # Debounce interval to avoid multiple triggers
    
    def on_modified(self, event: watchdog.events.FileSystemEvent):
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
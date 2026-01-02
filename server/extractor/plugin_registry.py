#!/usr/bin/env python3
"""
MetaExtract Plugin Registry System

A comprehensive plugin registry that tracks all available plugins, their metadata,
and provides management capabilities for the plugin ecosystem.

Features:
- Plugin discovery and registration
- Health monitoring and performance tracking
- Usage statistics and error reporting
- Plugin lifecycle management
"""

import json
import os
import time
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class PluginStatus(Enum):
    """Plugin status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOADING = "loading"
    ERROR = "error"
    DISABLED = "disabled"
    DEGRADED = "degraded"
    WARNING = "warning"
    CRITICAL = "critical"


class PluginHealthStatus(Enum):
    """Plugin health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class PluginType(Enum):
    """Plugin type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    GENERAL = "general"
    SPECIALIZED = "specialized"


@dataclass
class PluginInfo:
    """Comprehensive plugin information"""
    name: str
    version: str
    author: str
    description: str
    license: str
    plugin_type: PluginType
    status: PluginStatus
    module_path: str
    functions: List[str]
    dependencies: List[str]
    load_time: float
    last_used: float
    usage_count: int
    error_count: int
    enabled: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Health monitoring fields
    health_status: PluginHealthStatus = PluginHealthStatus.HEALTHY
    health_score: float = 1.0
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    timeout_executions: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    last_execution_time: float = 0.0
    last_execution_status: str = "never"
    last_execution_timestamp: float = 0.0
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    function_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)


class PluginRegistry:
    """Central registry for all MetaExtract plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.registry_file: str = "plugin_registry.json"
        self.plugin_dirs: List[str] = ["plugins", "external_plugins"]
        self.loaded_count: int = 0
        self.failed_count: int = 0
        self.last_updated: float = 0.0
        
        # Health monitoring configuration
        self.health_monitoring_enabled: bool = True
        self.health_thresholds: Dict[str, float] = {
            'error_rate': 0.1,      # 10% error rate threshold
            'timeout_rate': 0.05,   # 5% timeout rate threshold
            'slow_execution': 2.0,  # 2 seconds threshold for slow execution
            'memory_usage': 100.0   # 100MB memory usage threshold
        }
        self.last_health_check: float = 0.0
        self.health_check_interval: float = 60.0  # 60 seconds between health checks
        
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover all available plugins in plugin directories"""
        discovered_plugins = []
        
        for plugin_dir in self.plugin_dirs:
            plugins_path = Path(plugin_dir)
            if not plugins_path.exists():
                continue
                
            # Find all plugin directories
            for item in plugins_path.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    plugin_info = self._load_plugin_info(item)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
        
        return discovered_plugins
    
    def _load_plugin_info(self, plugin_path: Path) -> Optional[PluginInfo]:
        """Load plugin information from directory"""
        try:
            # Check for __init__.py
            init_file = plugin_path / "__init__.py"
            if not init_file.exists():
                return None
            
            # Import the plugin module
            module_spec = importlib.util.spec_from_file_location(
                plugin_path.name, 
                init_file
            )
            if module_spec is None or module_spec.loader is None:
                return None
            
            plugin_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(plugin_module)
            
            # Extract plugin metadata
            plugin_name = plugin_path.name
            version = getattr(plugin_module, "PLUGIN_VERSION", "1.0.0")
            author = getattr(plugin_module, "PLUGIN_AUTHOR", "Unknown")
            description = getattr(plugin_module, "PLUGIN_DESCRIPTION", "No description")
            license = getattr(plugin_module, "PLUGIN_LICENSE", "MIT")
            
            # Get dynamic metadata if available
            metadata = {}
            if hasattr(plugin_module, "get_plugin_metadata"):
                metadata = plugin_module.get_plugin_metadata()
            
            # Determine plugin type
            plugin_type = self._determine_plugin_type(plugin_name, description, metadata)
            
            # Find extraction functions
            functions = []
            for name, obj in inspect.getmembers(plugin_module, inspect.isfunction):
                if name.startswith(("extract_", "analyze_", "detect_")):
                    functions.append(name)
            
            # Get dependencies
            dependencies = []
            if hasattr(plugin_module, "MODULE_DEPENDENCIES"):
                deps = getattr(plugin_module, "MODULE_DEPENDENCIES")
                if isinstance(deps, (list, tuple)):
                    dependencies = list(deps)
            
            # Create plugin info
            plugin_info = PluginInfo(
                name=plugin_name,
                version=version,
                author=author,
                description=description,
                license=license,
                plugin_type=plugin_type,
                status=PluginStatus.ACTIVE,
                module_path=str(init_file),
                functions=functions,
                dependencies=dependencies,
                load_time=time.time(),
                last_used=0.0,
                usage_count=0,
                error_count=0,
                enabled=True,
                metadata=metadata
            )
            
            return plugin_info
            
        except Exception as e:
            print(f"Error loading plugin {plugin_path.name}: {e}")
            return None
    
    def _determine_plugin_type(self, name: str, description: str, metadata: Dict[str, Any]) -> PluginType:
        """Determine plugin type based on name and metadata"""
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # Check metadata first
        if "categories" in metadata:
            categories = metadata["categories"]
            if "audio" in categories:
                return PluginType.AUDIO
            elif "video" in categories:
                return PluginType.VIDEO
            elif "image" in categories:
                return PluginType.IMAGE
            elif "document" in categories:
                return PluginType.DOCUMENT
        
        # Check name and description
        if any(keyword in name_lower for keyword in ["audio", "sound", "music"]):
            return PluginType.AUDIO
        elif any(keyword in name_lower for keyword in ["video", "cinema", "film"]):
            return PluginType.VIDEO
        elif any(keyword in name_lower for keyword in ["image", "photo", "picture"]):
            return PluginType.IMAGE
        elif any(keyword in name_lower for keyword in ["document", "pdf", "text"]):
            return PluginType.DOCUMENT
        elif any(keyword in desc_lower for keyword in ["audio", "sound", "music"]):
            return PluginType.AUDIO
        elif any(keyword in desc_lower for keyword in ["video", "cinema", "film"]):
            return PluginType.VIDEO
        elif any(keyword in desc_lower for keyword in ["image", "photo", "picture"]):
            return PluginType.IMAGE
        elif any(keyword in desc_lower for keyword in ["document", "pdf", "text"]):
            return PluginType.DOCUMENT
        else:
            return PluginType.GENERAL
    
    def _initialize_health_monitoring(self, plugin_info: PluginInfo) -> None:
        """Initialize health monitoring for a plugin"""
        if not self.health_monitoring_enabled:
            return
        
        # Initialize function metrics
        for function_name in plugin_info.functions:
            plugin_info.function_metrics[function_name] = {
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
    
    def track_execution_performance(
        self,
        plugin_name: str,
        function_name: str,
        execution_time: float,
        status: str = "success",
        error: Optional[str] = None
    ) -> None:
        """
        Track execution performance for a plugin function.
        
        Args:
            plugin_name: Name of the plugin
            function_name: Name of the function
            execution_time: Execution time in seconds
            status: Execution status (success, failure, timeout)
            error: Error message if applicable
        """
        if not self.health_monitoring_enabled or plugin_name not in self.plugins:
            return
        
        plugin_info = self.plugins[plugin_name]
        func_metrics = plugin_info.function_metrics.get(function_name, {})
        
        # Update plugin-level metrics
        plugin_info.total_executions += 1
        plugin_info.total_execution_time += execution_time
        plugin_info.last_execution_time = execution_time
        plugin_info.last_execution_status = status
        plugin_info.last_execution_timestamp = time.time()
        
        # Update based on status
        if status == "success":
            plugin_info.successful_executions += 1
            func_metrics["successes"] = func_metrics.get("successes", 0) + 1
        elif status == "failure":
            plugin_info.failed_executions += 1
            func_metrics["failures"] = func_metrics.get("failures", 0) + 1
            print(f"Function {plugin_name}.{function_name} failed: {error}")
        elif status == "timeout":
            plugin_info.timeout_executions += 1
            func_metrics["timeouts"] = func_metrics.get("timeouts", 0) + 1
            print(f"Function {plugin_name}.{function_name} timed out")
        
        # Update execution time statistics
        if execution_time > plugin_info.max_execution_time:
            plugin_info.max_execution_time = execution_time
        if execution_time < plugin_info.min_execution_time:
            plugin_info.min_execution_time = execution_time
        
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
        total_executions = plugin_info.total_executions
        if total_executions > 0:
            plugin_info.avg_execution_time = plugin_info.total_execution_time / total_executions
            plugin_info.error_rate = plugin_info.failed_executions / total_executions
            plugin_info.timeout_rate = plugin_info.timeout_executions / total_executions
        
        func_executions = func_metrics.get("executions", 0)
        if func_executions > 0:
            func_metrics["avg_time"] = func_metrics.get("total_time", 0.0) / func_executions
        
        # Add to performance history
        plugin_info.performance_history.append({
            "timestamp": time.time(),
            "function": function_name,
            "execution_time": execution_time,
            "status": status,
            "error": error
        })
        
        # Keep history size manageable
        if len(plugin_info.performance_history) > 1000:  # Keep last 1000 executions
            plugin_info.performance_history = plugin_info.performance_history[-1000:]
        
        # Update health status
        self._update_health_status(plugin_info)
        
        print(f"Tracked execution for {plugin_name}.{function_name}: {execution_time:.3f}s, status: {status}")
    
    def _update_health_status(self, plugin_info: PluginInfo) -> None:
        """Update health status for a plugin based on performance metrics"""
        total_executions = plugin_info.total_executions
        
        if total_executions == 0:
            # No executions yet, consider healthy
            plugin_info.health_score = 1.0
            plugin_info.health_status = PluginHealthStatus.HEALTHY
            return
        
        # Calculate health score components
        error_rate = plugin_info.error_rate
        timeout_rate = plugin_info.timeout_rate
        avg_time = plugin_info.avg_execution_time
        
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
            health_status = PluginHealthStatus.HEALTHY
        elif health_score >= 0.7:
            health_status = PluginHealthStatus.WARNING
        elif health_score >= 0.5:
            health_status = PluginHealthStatus.DEGRADED
        else:
            health_status = PluginHealthStatus.CRITICAL
        
        plugin_info.health_score = round(health_score, 3)
        plugin_info.health_status = health_status
        
        # Update plugin status based on health
        if health_status == PluginHealthStatus.CRITICAL:
            plugin_info.status = PluginStatus.CRITICAL
        elif health_status == PluginHealthStatus.DEGRADED:
            plugin_info.status = PluginStatus.DEGRADED
        elif health_status == PluginHealthStatus.WARNING:
            plugin_info.status = PluginStatus.WARNING
        
        # Log health changes
        if health_status != getattr(plugin_info, "previous_health_status", PluginHealthStatus.HEALTHY):
            print(f"Plugin {plugin_info.name} health changed to {health_status.value} (score: {health_score:.3f})")
            plugin_info.previous_health_status = health_status
    
    def register_plugin(self, plugin_info: PluginInfo) -> bool:
        """Register a plugin in the registry"""
        if plugin_info.name in self.plugins:
            print(f"Plugin {plugin_info.name} already registered")
            return False
        
        self.plugins[plugin_info.name] = plugin_info
        self.loaded_count += 1
        self.last_updated = time.time()
        
        print(f"Registered plugin: {plugin_info.name}")
        return True
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin from the registry"""
        if plugin_name not in self.plugins:
            print(f"Plugin {plugin_name} not found")
            return False
        
        del self.plugins[plugin_name]
        self.last_updated = time.time()
        
        print(f"Unregistered plugin: {plugin_name}")
        return True
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        self.plugins[plugin_name].enabled = True
        self.plugins[plugin_name].status = PluginStatus.ACTIVE
        self.last_updated = time.time()
        
        print(f"Enabled plugin: {plugin_name}")
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name not in self.plugins:
            return False
        
        self.plugins[plugin_name].enabled = False
        self.plugins[plugin_name].status = PluginStatus.DISABLED
        self.last_updated = time.time()
        
        print(f"Disabled plugin: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[PluginInfo]:
        """Get all registered plugins"""
        return list(self.plugins.values())
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Get plugins by type"""
        return [plugin for plugin in self.plugins.values() if plugin.plugin_type == plugin_type]
    
    def get_active_plugins(self) -> List[PluginInfo]:
        """Get all active plugins"""
        return [plugin for plugin in self.plugins.values() if plugin.enabled and plugin.status == PluginStatus.ACTIVE]
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get statistics about registered plugins"""
        return {
            "total_plugins": len(self.plugins),
            "active_plugins": len(self.get_active_plugins()),
            "disabled_plugins": len([p for p in self.plugins.values() if not p.enabled]),
            "error_plugins": len([p for p in self.plugins.values() if p.status == PluginStatus.ERROR]),
            "loaded_count": self.loaded_count,
            "failed_count": self.failed_count,
            "last_updated": self.last_updated,
            "by_type": {
                "audio": len(self.get_plugins_by_type(PluginType.AUDIO)),
                "video": len(self.get_plugins_by_type(PluginType.VIDEO)),
                "image": len(self.get_plugins_by_type(PluginType.IMAGE)),
                "document": len(self.get_plugins_by_type(PluginType.DOCUMENT)),
                "general": len(self.get_plugins_by_type(PluginType.GENERAL)),
                "specialized": len(self.get_plugins_by_type(PluginType.SPECIALIZED))
            }
        }
    
    def update_plugin_usage(self, plugin_name: str) -> bool:
        """Update plugin usage statistics"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        plugin.usage_count += 1
        plugin.last_used = time.time()
        self.last_updated = time.time()
        
        return True
    
    def report_plugin_error(self, plugin_name: str, error: str) -> bool:
        """Report plugin error"""
        if plugin_name not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_name]
        plugin.error_count += 1
        plugin.status = PluginStatus.ERROR
        self.last_updated = time.time()
        
        print(f"Error reported for plugin {plugin_name}: {error}")
        return True
    
    def save_registry(self) -> bool:
        """Save registry to file"""
        try:
            registry_data = {
                "plugins": {
                    name: {
                        "name": plugin.name,
                        "version": plugin.version,
                        "author": plugin.author,
                        "description": plugin.description,
                        "license": plugin.license,
                        "plugin_type": plugin.plugin_type.value,
                        "status": plugin.status.value,
                        "module_path": plugin.module_path,
                        "functions": plugin.functions,
                        "dependencies": plugin.dependencies,
                        "load_time": plugin.load_time,
                        "last_used": plugin.last_used,
                        "usage_count": plugin.usage_count,
                        "error_count": plugin.error_count,
                        "enabled": plugin.enabled,
                        "metadata": plugin.metadata
                    }
                    for name, plugin in self.plugins.items()
                },
                "loaded_count": self.loaded_count,
                "failed_count": self.failed_count,
                "last_updated": self.last_updated
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            print(f"Registry saved to {self.registry_file}")
            return True
            
        except Exception as e:
            print(f"Error saving registry: {e}")
            return False
    
    def load_registry(self) -> bool:
        """Load registry from file"""
        try:
            if not os.path.exists(self.registry_file):
                print("No registry file found, starting fresh")
                return False
            
            with open(self.registry_file, 'r') as f:
                registry_data = json.load(f)
            
            # Restore plugins
            for name, data in registry_data["plugins"].items():
                plugin_info = PluginInfo(
                    name=data["name"],
                    version=data["version"],
                    author=data["author"],
                    description=data["description"],
                    license=data["license"],
                    plugin_type=PluginType(data["plugin_type"]),
                    status=PluginStatus(data["status"]),
                    module_path=data["module_path"],
                    functions=data["functions"],
                    dependencies=data["dependencies"],
                    load_time=data["load_time"],
                    last_used=data["last_used"],
                    usage_count=data["usage_count"],
                    error_count=data["error_count"],
                    enabled=data["enabled"],
                    metadata=data["metadata"]
                )
                self.plugins[name] = plugin_info
            
            self.loaded_count = registry_data.get("loaded_count", 0)
            self.failed_count = registry_data.get("failed_count", 0)
            self.last_updated = registry_data.get("last_updated", 0.0)
            
            print(f"Registry loaded from {self.registry_file}")
            return True
            
        except Exception as e:
            print(f"Error loading registry: {e}")
            return False
    
    def initialize(self) -> None:
        """Initialize the plugin registry"""
        print("Initializing plugin registry...")
        
        # Load existing registry if available
        self.load_registry()
        
        # Discover new plugins
        discovered = self.discover_plugins()
        
        # Register discovered plugins
        for plugin in discovered:
            if plugin.name not in self.plugins:
                self.register_plugin(plugin)
        
        # Save updated registry
        self.save_registry()
        
        print(f"Plugin registry initialized: {len(self.plugins)} plugins registered")


# Global registry instance
plugin_registry = PluginRegistry()


def initialize_plugin_registry():
    """Initialize the global plugin registry"""
    plugin_registry.initialize()
    return plugin_registry


if __name__ == "__main__":
    # Test the registry
    registry = initialize_plugin_registry()
    
    # Print stats
    stats = registry.get_plugin_stats()
    print(f"\nPlugin Registry Stats:")
    print(f"  Total Plugins: {stats['total_plugins']}")
    print(f"  Active Plugins: {stats['active_plugins']}")
    print(f"  By Type:")
    for plugin_type, count in stats['by_type'].items():
        print(f"    {plugin_type}: {count}")
    
    # List plugins
    print(f"\nRegistered Plugins:")
    for plugin in registry.get_all_plugins():
        print(f"  - {plugin.name} ({plugin.plugin_type.value}): {len(plugin.functions)} functions")
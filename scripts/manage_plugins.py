#!/usr/bin/env python3
"""
MetaExtract Plugin Management CLI

A comprehensive command-line tool for managing MetaExtract plugins.
"""

import argparse
import sys
import os
import json
import importlib
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def import_metaextract():
    """Import MetaExtract modules with error handling"""
    try:
        from server.extractor.module_discovery import (
            enable_plugins_global,
            discover_and_load_plugins_global,
            get_discovered_plugins_global,
            get_plugin_info_global,
            get_all_plugins_info_global,
            get_plugin_stats_global,
            enable_plugin_global,
            disable_plugin_global,
            reload_plugin_global
        )
        return {
            'enable_plugins_global': enable_plugins_global,
            'discover_and_load_plugins_global': discover_and_load_plugins_global,
            'get_discovered_plugins_global': get_discovered_plugins_global,
            'get_plugin_info_global': get_plugin_info_global,
            'get_all_plugins_info_global': get_all_plugins_info_global,
            'get_plugin_stats_global': get_plugin_stats_global,
            'enable_plugin_global': enable_plugin_global,
            'disable_plugin_global': disable_plugin_global,
            'reload_plugin_global': reload_plugin_global
        }
    except ImportError as e:
        print(f"❌ Error importing MetaExtract modules: {e}")
        sys.exit(1)


def list_plugins(args):
    """List all discovered plugins"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Get plugin info
    plugins_info = functions['get_discovered_plugins_global']()
    
    if not plugins_info:
        print("❌ No plugins found")
        return 1
    
    print(f"📦 Found {len(plugins_info)} plugins/modules:")
    print("=" * 60)
    
    for i, (plugin_name, plugin_info) in enumerate(plugins_info.items(), 1):
        plugin_type = plugin_info.get('type', 'unknown')
        functions = plugin_info.get('functions', [])
        enabled = plugin_info.get('enabled', True)
        
        print(f"{i}. {plugin_name} ({plugin_type})")
        print(f"   Status: {'✅ Enabled' if enabled else '❌ Disabled'}")
        print(f"   Functions: {len(functions)}")
        
        if args.detailed:
            if plugin_type == 'plugin':
                metadata = plugin_info.get('metadata', {})
                version = metadata.get('version', 'N/A')
                author = metadata.get('author', 'N/A')
                description = metadata.get('description', 'N/A')
                license = metadata.get('license', 'N/A')
                
                print(f"   Version: {version}")
                print(f"   Author: {author}")
                print(f"   License: {license}")
                print(f"   Description: {description}")
            
            if functions:
                print(f"   Available functions:")
                for func in functions:
                    print(f"      - {func}()")
            
            dependencies = plugin_info.get('dependencies', [])
            if dependencies:
                print(f"   Dependencies: {', '.join(dependencies)}")
            
            print()
    
    return 0


def show_plugin_info(args):
    """Show detailed information about a specific plugin"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Get plugin info
    plugin_info = functions['get_plugin_info_global'](args.plugin)
    
    if not plugin_info:
        print(f"❌ Plugin '{args.plugin}' not found")
        return 1
    
    print(f"📦 Plugin: {args.plugin}")
    print("=" * 60)
    
    # Basic info
    plugin_type = plugin_info.get('type', 'unknown')
    enabled = plugin_info.get('enabled', True)
    path = plugin_info.get('path', 'N/A')
    
    print(f"Type: {plugin_type}")
    print(f"Status: {'✅ Enabled' if enabled else '❌ Disabled'}")
    print(f"Path: {path}")
    print()
    
    # Metadata
    if plugin_type == 'plugin':
        metadata = plugin_info.get('metadata', {})
        print("📋 Metadata:")
        for key, value in metadata.items():
            print(f"   {key.title()}: {value}")
        print()
    
    # Functions
    functions_list = plugin_info.get('functions', [])
    if functions_list:
        print(f"🔧 Functions ({len(functions_list)}):")
        for func in functions_list:
            print(f"   - {func}()")
        print()
    
    # Dependencies
    dependencies = plugin_info.get('dependencies', [])
    if dependencies:
        print(f"🔗 Dependencies:")
        for dep in dependencies:
            print(f"   - {dep}")
        print()
    
    return 0


def enable_plugin(args):
    """Enable a plugin"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Enable the plugin
    success = functions['enable_plugin_global'](args.plugin)
    
    if success:
        print(f"✅ Plugin '{args.plugin}' enabled successfully")
        return 0
    else:
        print(f"❌ Failed to enable plugin '{args.plugin}'")
        return 1


def disable_plugin(args):
    """Disable a plugin"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Disable the plugin
    success = functions['disable_plugin_global'](args.plugin)
    
    if success:
        print(f"✅ Plugin '{args.plugin}' disabled successfully")
        return 0
    else:
        print(f"❌ Failed to disable plugin '{args.plugin}'")
        return 1


def reload_plugin(args):
    """Reload a plugin"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Reload the plugin
    success = functions['reload_plugin_global'](args.plugin)
    
    if success:
        print(f"✅ Plugin '{args.plugin}' reloaded successfully")
        return 0
    else:
        print(f"❌ Failed to reload plugin '{args.plugin}'")
        return 1


def show_stats(args):
    """Show plugin statistics"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Get stats
    stats = functions['get_plugin_stats_global']()
    
    print("📊 Plugin Statistics")
    print("=" * 60)
    
    print(f"Plugins Enabled: {stats.get('plugins_enabled', False)}")
    print(f"Plugin Paths: {', '.join(stats.get('plugin_paths', []))}")
    print(f"Plugins Loaded: {stats.get('plugins_loaded', 0)}")
    print(f"Plugins Failed: {stats.get('plugins_failed', 0)}")
    print(f"Discovery Time: {stats.get('plugin_discovery_time', 0):.3f}s")
    print(f"Success Rate: {stats.get('success_rate', 0) * 100:.1f}%")
    
    if 'loaded_plugins' in stats:
        print(f"\nLoaded Plugins ({len(stats['loaded_plugins'])}):")
        for plugin in stats['loaded_plugins']:
            print(f"   - {plugin}")
    
    if 'failed_plugins' in stats:
        print(f"\nFailed Plugins ({len(stats['failed_plugins'])}):")
        for plugin in stats['failed_plugins']:
            print(f"   - {plugin}")
    
    return 0


def test_plugin(args):
    """Test a plugin with a file"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Get plugin info
    plugin_info = functions['get_plugin_info_global'](args.plugin)
    
    if not plugin_info:
        print(f"❌ Plugin '{args.plugin}' not found")
        return 1
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ File '{args.file}' not found")
        return 1
    
    module = plugin_info.get('module')
    if not module:
        print(f"❌ Plugin '{args.plugin}' module not loaded")
        return 1
    
    print(f"🧪 Testing plugin '{args.plugin}' with file '{args.file}'")
    print("=" * 60)
    
    # Test all functions
    functions_list = plugin_info.get('functions', [])
    success_count = 0
    total_count = 0
    
    for func_name in functions_list:
        if func_name == 'get_plugin_metadata':
            continue
            
        try:
            func = getattr(module, func_name)
            result = func(args.file)
            
            if isinstance(result, dict):
                print(f"✅ {func_name}(): {len(result)} fields")
                success_count += 1
            else:
                print(f"⚠️  {func_name}(): Unexpected return type {type(result)}")
            
            total_count += 1
            
        except Exception as e:
            print(f"❌ {func_name}(): {e}")
            total_count += 1
    
    print(f"\n📊 Results: {success_count}/{total_count} functions successful")
    
    if total_count > 0:
        success_rate = (success_count / total_count) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    return 0 if success_count == total_count else 1


def create_plugin_skeleton(args):
    """Create a new plugin skeleton"""
    plugin_name = args.name
    plugin_dir = f"plugins/{plugin_name}"
    
    # Check if plugin already exists
    if os.path.exists(plugin_dir):
        print(f"❌ Plugin '{plugin_name}' already exists")
        return 1
    
    # Create plugin directory
    os.makedirs(plugin_dir)
    print(f"📁 Created plugin directory: {plugin_dir}")
    
    # Create __init__.py
    init_content = f"""# {plugin_name.capitalize()} Plugin for MetaExtract
# {args.description or 'Plugin description'}

{plugin_name.capitalize()} Plugin - {args.description or 'Plugin description'}

This plugin provides {args.description or 'functionality'} for MetaExtract.
"""

# Plugin metadata
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "{args.author or 'Your Name'}"
PLUGIN_DESCRIPTION = "{args.description or 'Plugin description'}"
PLUGIN_LICENSE = "MIT"

# Optional: Dynamic metadata function
def get_plugin_metadata():
    return {{
        "version": PLUGIN_VERSION,
        "author": PLUGIN_AUTHOR,
        "description": PLUGIN_DESCRIPTION,
        "license": PLUGIN_LICENSE,
        "website": "https://metaextract.com",
        "documentation": "https://metaextract.com/docs/plugins/{plugin_name}"
    }}


def extract_{plugin_name}_metadata(filepath: str) -> dict:
    """
    Extract metadata from files.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing extracted metadata
    """
    import os
    import time
    from pathlib import Path
    
    file_path = Path(filepath)
    
    # Extract basic metadata
    metadata = {{
        "{plugin_name}_analysis": {{
            "processed": True,
            "timestamp": time.time(),
            "file_size": os.path.getsize(filepath),
            "file_extension": file_path.suffix,
            "file_name": file_path.name,
            "plugin_version": PLUGIN_VERSION,
            "processing_time_ms": 10.0
        }}
    }}
    
    return metadata


def analyze_{plugin_name}_quality(filepath: str) -> dict:
    """
    Analyze quality metrics.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing quality analysis
    """
    analysis = {{
        "{plugin_name}_quality": {{
            "quality_score": 0.85,
            "analysis_type": "basic",
            "confidence": 0.9
        }}
    }}
    
    return analysis


def detect_{plugin_name}_features(filepath: str) -> dict:
    """
    Detect special features.
    
    Args:
        filepath: Path to the file being processed
        
    Returns:
        Dictionary containing detected features
    """
    features = {{
        "{plugin_name}_features": {{
            "has_metadata": True,
            "has_quality_info": True,
            "is_processed": True,
            "plugin_compatible": True
        }}
    }}
    
    return features


# Optional: You can declare dependencies on other modules
# This ensures your plugin runs after its dependencies
MODULE_DEPENDENCIES = ["base_metadata"]  # Depends on base metadata module
"""
    
    with open(f"{plugin_dir}/__init__.py", 'w') as f:
        f.write(init_content)
    
    # Create README.md
    readme_content = f"""# {plugin_name.capitalize()} Plugin for MetaExtract

## Overview

The {plugin_name.capitalize()} Plugin provides {args.description or 'comprehensive functionality'} for MetaExtract.

## Plugin Structure

{plugin_name}/
- __init__.py          # Main plugin file
- README.md           # This documentation

## Installation

1. Place the plugin in the plugins directory
2. Enable plugins in your code:
   ```python
   from server.extractor.module_discovery import enable_plugins_global
   enable_plugins_global(True)
   ```

3. Load plugins automatically:
   ```python
   from server.extractor.module_discovery import discover_and_load_plugins_global
   discover_and_load_plugins_global()
   ```

## Plugin Metadata

```python
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "{args.author or 'Your Name'}"
PLUGIN_DESCRIPTION = "{args.description or 'Plugin description'}"
PLUGIN_LICENSE = "MIT"
```

## Extraction Functions

1. extract_{plugin_name}_metadata() - Extracts comprehensive metadata
2. analyze_{plugin_name}_quality() - Performs quality analysis
3. detect_{plugin_name}_features() - Detects special features

## Dependencies

```python
MODULE_DEPENDENCIES = ["base_metadata"]
```

## Integration

The plugin integrates seamlessly with MetaExtract:
- Automatic discovery during system initialization
- Dependency-aware execution
- Parallel execution support

## Usage Example

```python
from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Create extractor (automatically loads plugins)
extractor = ComprehensiveMetadataExtractor()

# Extract metadata (includes plugin results)
result = extractor.extract_comprehensive_metadata("test.ext", "super")

# Access plugin results
plugin_data = result.get("{plugin_name}_analysis", {{}})
print(f"Plugin processed: {{plugin_data.get('processed')}}")
```

## Benefits

- Extensibility: Add custom functionality
- Isolation: Plugins run in their own context
- Maintainability: Easy to update
- Performance: Parallel execution support
- Compatibility: Works with all MetaExtract features
"""
    
    with open(f"{plugin_dir}/README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"📝 Created README.md")
    print(f"✅ Plugin skeleton created successfully!")
    print(f"\n💡 Next steps:")
    print(f"   1. Edit {plugin_dir}/__init__.py to add your custom logic")
    print(f"   2. Update {plugin_dir}/README.md with specific details")
    print(f"   3. Test your plugin with: python manage_plugins.py test {plugin_name} <test_file>")
    print(f"   4. Enable your plugin in production")
    
    return 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='MetaExtract Plugin Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_plugins.py list
  python manage_plugins.py info audio_analysis_plugin
  python manage_plugins.py enable audio_analysis_plugin
  python manage_plugins.py disable audio_analysis_plugin
  python manage_plugins.py reload audio_analysis_plugin
  python manage_plugins.py stats
  python manage_plugins.py test audio_analysis_plugin test.mp3
  python manage_plugins.py create my_plugin --description "My custom plugin"
  
  # Health Monitoring Commands:
  python manage_plugins.py health
  python manage_plugins.py performance --detailed
  python manage_plugins.py check
  python manage_plugins.py history example_plugin --limit 20
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all plugins')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    list_parser.set_defaults(func=list_plugins)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show plugin information')
    info_parser.add_argument('plugin', help='Plugin name')
    info_parser.set_defaults(func=show_plugin_info)
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a plugin')
    enable_parser.add_argument('plugin', help='Plugin name')
    enable_parser.set_defaults(func=enable_plugin)
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a plugin')
    disable_parser.add_argument('plugin', help='Plugin name')
    disable_parser.set_defaults(func=disable_plugin)
    
    # Reload command
    reload_parser = subparsers.add_parser('reload', help='Reload a plugin')
    reload_parser.add_argument('plugin', help='Plugin name')
    reload_parser.set_defaults(func=reload_plugin)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show plugin statistics')
    stats_parser.set_defaults(func=show_stats)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a plugin with a file')
    test_parser.add_argument('plugin', help='Plugin name')
    test_parser.add_argument('file', help='File to test with')
    test_parser.set_defaults(func=test_plugin)
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new plugin skeleton')
    create_parser.add_argument('name', help='Plugin name')
    create_parser.add_argument('--author', default='Your Name', help='Plugin author')
    create_parser.add_argument('--description', default='Plugin description', help='Plugin description')
    create_parser.set_defaults(func=create_plugin_skeleton)
    
    # Health status command
    health_parser = subparsers.add_parser('health', help='Show health status of all plugins/modules')
    health_parser.set_defaults(func=show_health_status)
    
    # Performance metrics command
    perf_parser = subparsers.add_parser('performance', help='Show performance metrics for plugins/modules')
    perf_parser.add_argument('--detailed', action='store_true', help='Show detailed function-level metrics')
    perf_parser.set_defaults(func=show_performance_metrics)
    
    # Health check command
    check_parser = subparsers.add_parser('check', help='Perform a comprehensive health check')
    check_parser.set_defaults(func=perform_health_check)
    
    # Performance history command
    history_parser = subparsers.add_parser('history', help='Show performance history for a specific module')
    history_parser.add_argument('module', help='Module name')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of history entries to show')
    history_parser.set_defaults(func=show_module_performance_history)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


def show_health_status(args):
    """Show health status of all plugins/modules"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    # Get health summary
    try:
        from server.extractor.module_discovery import get_health_summary_global
        health_summary = get_health_summary_global()
        
        print("🏥 Plugin Health Summary")
        print("=" * 60)
        print(f"Total Modules: {health_summary.get('total_modules', 0)}")
        print(f"Average Health Score: {health_summary.get('average_health_score', 0.0)}")
        print(f"Last Check: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health_summary.get('last_check', 0)))}")
        print()
        
        # Health distribution
        dist = health_summary.get('health_distribution', {})
        print("📊 Health Distribution:")
        print(f"   🟢 Healthy: {dist.get('healthy', 0)}")
        print(f"   🟡 Warning: {dist.get('warning', 0)}")
        print(f"   🟠 Degraded: {dist.get('degraded', 0)}")
        print(f"   🔴 Critical: {dist.get('critical', 0)}")
        print()
        
        # Detailed health status
        try:
            from server.extractor.module_discovery import get_all_health_statuses_global
            health_statuses = get_all_health_statuses_global()
            
            if health_statuses:
                print("🩺 Module Health Details:")
                for module_name, health_info in health_statuses.items():
                    status = health_info.get('health_status', 'unknown')
                    score = health_info.get('health_score', 0.0)
                    error_rate = health_info.get('error_rate', 0.0)
                    timeout_rate = health_info.get('timeout_rate', 0.0)
                    avg_time = health_info.get('avg_execution_time', 0.0)
                    
                    # Status emoji
                    if status == "healthy":
                        emoji = "🟢"
                    elif status == "warning":
                        emoji = "🟡"
                    elif status == "degraded":
                        emoji = "🟠"
                    else:
                        emoji = "🔴"
                    
                    print(f"   {emoji} {module_name}:")
                    print(f"      Status: {status} (Score: {score:.3f})")
                    print(f"      Error Rate: {error_rate:.3%}")
                    print(f"      Timeout Rate: {timeout_rate:.3%}")
                    print(f"      Avg Execution Time: {avg_time:.3f}s")
                    print()
        except ImportError:
            print("⚠️  Health monitoring functions not available")
            
    except ImportError as e:
        print(f"❌ Health monitoring not available: {e}")
        return 1
    
    return 0


def show_performance_metrics(args):
    """Show performance metrics for plugins/modules"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    try:
        from server.extractor.module_discovery import get_all_performance_metrics_global
        performance_metrics = get_all_performance_metrics_global()
        
        if not performance_metrics:
            print("❌ No performance metrics available")
            return 1
        
        print("📈 Plugin Performance Metrics")
        print("=" * 60)
        
        for module_name, metrics in performance_metrics.items():
            print(f"📦 {module_name}:")
            print(f"   Total Executions: {metrics.get('total_executions', 0)}")
            print(f"   Successful: {metrics.get('successful_executions', 0)}")
            print(f"   Failed: {metrics.get('failed_executions', 0)}")
            print(f"   Timeouts: {metrics.get('timeout_executions', 0)}")
            print(f"   Avg Execution Time: {metrics.get('avg_execution_time', 0.0):.3f}s")
            print(f"   Max Execution Time: {metrics.get('max_execution_time', 0.0):.3f}s")
            print(f"   Min Execution Time: {metrics.get('min_execution_time', float('inf')):.3f}s")
            print(f"   Error Rate: {metrics.get('error_rate', 0.0):.3%}")
            print(f"   Timeout Rate: {metrics.get('timeout_rate', 0.0):.3%}")
            print()
            
            # Function-level metrics
            if args.detailed and 'function_metrics' in metrics:
                print(f"   🔧 Function Metrics:")
                for func_name, func_metrics in metrics['function_metrics'].items():
                    print(f"      {func_name}():")
                    print(f"         Executions: {func_metrics.get('executions', 0)}")
                    print(f"         Avg Time: {func_metrics.get('avg_time', 0.0):.3f}s")
                    print(f"         Max Time: {func_metrics.get('max_time', 0.0):.3f}s")
                    print(f"         Success Rate: {func_metrics.get('successes', 0) / max(1, func_metrics.get('executions', 1)):.3%}")
                print()
        
    except ImportError as e:
        print(f"❌ Performance metrics not available: {e}")
        return 1
    
    return 0


def perform_health_check(args):
    """Perform a comprehensive health check"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    try:
        from server.extractor.module_discovery import perform_health_check_global
        
        print("🩺 Performing Comprehensive Health Check...")
        print("=" * 60)
        
        health_check_result = perform_health_check_global()
        
        print(f"📅 Check completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health_check_result.get('timestamp', 0)))}")
        print(f"⏱️  Duration: {health_check_result.get('duration_seconds', 0.0):.3f}s")
        print()
        
        # Summary
        summary = health_check_result.get('summary', {})
        print("📊 Health Summary:")
        print(f"   Total Modules: {summary.get('total_modules', 0)}")
        print(f"   Average Health Score: {summary.get('average_health_score', 0.0)}")
        print(f"   🟢 Healthy: {summary.get('healthy', 0)}")
        print(f"   🟡 Warning: {summary.get('warning', 0)}")
        print(f"   🟠 Degraded: {summary.get('degraded', 0)}")
        print(f"   🔴 Critical: {summary.get('critical', 0)}")
        print()
        
        # Problematic modules
        problematic = health_check_result.get('problematic_modules', [])
        if problematic:
            print("⚠️  Problematic Modules:")
            for module_info in problematic:
                print(f"   {module_info['module']} ({module_info['status']}):")
                print(f"      Health Score: {module_info['score']:.3f}")
                print(f"      Error Rate: {module_info['error_rate']:.3%}")
                print(f"      Timeout Rate: {module_info['timeout_rate']:.3%}")
                print()
        else:
            print("✅ All modules are healthy!")
        
        # Thresholds
        thresholds = health_check_result.get('thresholds', {})
        print("📏 Health Thresholds:")
        for threshold_name, threshold_value in thresholds.items():
            print(f"   {threshold_name}: {threshold_value}")
        
    except ImportError as e:
        print(f"❌ Health check functions not available: {e}")
        return 1
    
    return 0


def show_module_performance_history(args):
    """Show performance history for a specific module"""
    functions = import_metaextract()
    
    # Enable and discover plugins
    functions['enable_plugins_global'](True)
    functions['discover_and_load_plugins_global']()
    
    try:
        from server.extractor.module_discovery import get_performance_history_global
        
        history = get_performance_history_global(args.module, limit=args.limit)
        
        if not history:
            print(f"❌ No performance history available for module '{args.module}'")
            return 1
        
        print(f"📊 Performance History for {args.module} (Last {len(history)} executions)")
        print("=" * 60)
        
        for i, entry in enumerate(history, 1):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['timestamp']))
            status_emoji = "✅" if entry['status'] == 'success' else "❌" if entry['status'] == 'failure' else "⏱️"
            
            print(f"{i}. [{timestamp}] {status_emoji} {entry['function']}()")
            print(f"   Execution Time: {entry['execution_time']:.3f}s")
            print(f"   Status: {entry['status']}")
            if entry.get('error'):
                print(f"   Error: {entry['error']}")
            print()
        
    except ImportError as e:
        print(f"❌ Performance history functions not available: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

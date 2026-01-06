#!/usr/bin/env python3
"""
MetaExtract Plugin Marketplace and Remote Management System

This system provides comprehensive plugin marketplace integration including:
- Remote plugin discovery and browsing
- Secure plugin installation and updates
- Plugin repository management
- Remote plugin administration
"""

import os
import sys
import json
import logging
import time
import hashlib
import tempfile
import shutil
import urllib.request
import urllib.error
import ssl
import zipfile
import tarfile
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Configure logging
logger = logging.getLogger(__name__)

# Import custom exceptions
try:
    from .exceptions.extraction_exceptions import (
        MetaExtractException,
        PluginMarketplaceException,
        PluginInstallationException,
        PluginSecurityException
    )
    MARKETPLACE_EXCEPTIONS_AVAILABLE = True
except ImportError:
    # Fallback exception classes
    class MetaExtractException(Exception):
        pass
    
    class PluginMarketplaceException(MetaExtractException):
        pass
    
    class PluginInstallationException(MetaExtractException):
        pass
    
    class PluginSecurityException(MetaExtractException):
        pass
    
    MARKETPLACE_EXCEPTIONS_AVAILABLE = False

# Import module discovery for integration
try:
    from .module_discovery import (
        module_registry,
        enable_plugin_global,
        disable_plugin_global,
        reload_plugin_global,
        update_plugin_global,
        get_plugin_info_global,
        get_all_plugins_info_global
    )
    MODULE_DISCOVERY_AVAILABLE = True
except ImportError:
    MODULE_DISCOVERY_AVAILABLE = False
    logger.warning("Module discovery not available, marketplace integration will be limited")


class PluginMarketplace:
    """
    Main plugin marketplace class for remote plugin management.
    """
    
    def __init__(self):
        # Marketplace configuration
        self.repositories: List[Dict[str, Any]] = []
        self.installed_plugins: Dict[str, Dict[str, Any]] = {}
        self.available_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_cache: Dict[str, Dict[str, Any]] = {}
        self.update_cache: Dict[str, Dict[str, Any]] = {}
        self.security_settings: Dict[str, Any] = {
            'verify_ssl': True,
            'verify_signatures': True,
            'allowed_sources': [],
            'blocked_sources': [],
            'timeout_seconds': 30,
            'max_download_size_mb': 50
        }
        
        # Cache configuration
        self.cache_enabled: bool = True
        self.cache_directory: str = "plugin_cache/"
        self.cache_expiration_days: int = 7
        self.max_cache_size_mb: int = 500
        
        # Initialize marketplace
        self._initialize_marketplace()
    
    def _initialize_marketplace(self) -> None:
        """Initialize the plugin marketplace system."""
        try:
            # Create cache directory if it doesn't exist
            cache_path = Path(self.cache_directory)
            cache_path.mkdir(exist_ok=True)
            
            # Load default repositories
            self._load_default_repositories()
            
            # Load installed plugins info
            self._load_installed_plugins()
            
            logger.info("Plugin marketplace initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize plugin marketplace: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if MARKETPLACE_EXCEPTIONS_AVAILABLE:
                raise PluginMarketplaceException(
                    message=error_msg,
                    context={"phase": "initialization", "error": str(e)}
                ) from e
    
    def _load_default_repositories(self) -> None:
        """Load default plugin repositories."""
        try:
            # Default MetaExtract official repository
            default_repos = [
                {
                    "name": "MetaExtract Official Repository",
                    "url": "https://plugins.metaextract.com/api/v1",
                    "type": "official",
                    "priority": 1,
                    "enabled": True,
                    "description": "Official MetaExtract plugins with full support",
                    "last_checked": 0,
                    "last_success": 0
                },
                {
                    "name": "MetaExtract Community Repository",
                    "url": "https://community-plugins.metaextract.com/api/v1",
                    "type": "community",
                    "priority": 2,
                    "enabled": True,
                    "description": "Community-contributed plugins with basic validation",
                    "last_checked": 0,
                    "last_success": 0
                }
            ]
            
            # Add default repositories
            for repo in default_repos:
                self.add_repository(repo)
            
            logger.info(f"Loaded {len(default_repos)} default repositories")
            
        except Exception as e:
            logger.error(f"Error loading default repositories: {str(e)}")
    
    def _load_installed_plugins(self) -> None:
        """Load information about installed plugins."""
        try:
            if MODULE_DISCOVERY_AVAILABLE:
                installed_plugins = get_all_plugins_info_global()
                for plugin_name, plugin_info in installed_plugins.items():
                    self.installed_plugins[plugin_name] = {
                        "name": plugin_name,
                        "version": plugin_info.get("metadata", {}).get("version", "unknown"),
                        "enabled": plugin_info.get("enabled", True),
                        "source": "local",
                        "install_date": time.time(),
                        "last_updated": time.time()
                    }
                
                logger.info(f"Loaded {len(self.installed_plugins)} installed plugins")
            else:
                logger.warning("Module discovery not available, cannot load installed plugins")
                
        except Exception as e:
            logger.error(f"Error loading installed plugins: {str(e)}")
    
    def add_repository(self, repository: Dict[str, Any]) -> bool:
        """
        Add a plugin repository to the marketplace.
        
        Args:
            repository: Repository configuration dictionary
            
        Returns:
            True if repository was added successfully, False otherwise
        """
        try:
            # Validate repository configuration
            required_fields = ["name", "url", "type"]
            for field in required_fields:
                if field not in repository:
                    error_msg = f"Repository missing required field: {field}"
                    logger.error(error_msg)
                    return False
            
            # Check for duplicate repository
            for existing_repo in self.repositories:
                if existing_repo["url"] == repository["url"]:
                    logger.warning(f"Repository already exists: {repository['name']}")
                    return False
            
            # Set default values
            repository.setdefault("priority", len(self.repositories) + 1)
            repository.setdefault("enabled", True)
            repository.setdefault("description", "")
            repository.setdefault("last_checked", 0)
            repository.setdefault("last_success", 0)
            
            # Add repository
            self.repositories.append(repository)
            self.repositories.sort(key=lambda x: x["priority"])
            
            logger.info(f"Added repository: {repository['name']} ({repository['url']})")
            return True
            
        except Exception as e:
            error_msg = f"Failed to add repository {repository.get('name', 'unknown')}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return False
    
    def remove_repository(self, repository_name: str) -> bool:
        """
        Remove a plugin repository from the marketplace.
        
        Args:
            repository_name: Name of the repository to remove
            
        Returns:
            True if repository was removed successfully, False otherwise
        """
        try:
            # Find repository by name
            repo_to_remove = None
            for repo in self.repositories:
                if repo["name"] == repository_name:
                    repo_to_remove = repo
                    break
            
            if not repo_to_remove:
                logger.warning(f"Repository not found: {repository_name}")
                return False
            
            # Remove repository
            self.repositories.remove(repo_to_remove)
            logger.info(f"Removed repository: {repository_name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to remove repository {repository_name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return False
    
    def enable_repository(self, repository_name: str, enabled: bool = True) -> bool:
        """
        Enable or disable a plugin repository.
        
        Args:
            repository_name: Name of the repository
            enabled: Whether to enable or disable the repository
            
        Returns:
            True if repository status was updated successfully, False otherwise
        """
        try:
            # Find repository by name
            for repo in self.repositories:
                if repo["name"] == repository_name:
                    repo["enabled"] = enabled
                    status = "enabled" if enabled else "disabled"
                    logger.info(f"Repository {repository_name} {status}")
                    return True
            
            logger.warning(f"Repository not found: {repository_name}")
            return False
            
        except Exception as e:
            error_msg = f"Failed to update repository {repository_name} status: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return False
    
    def get_repositories(self) -> List[Dict[str, Any]]:
        """
        Get all configured repositories.
        
        Returns:
            List of repository configurations
        """
        return self.repositories.copy()
    
    def get_enabled_repositories(self) -> List[Dict[str, Any]]:
        """
        Get all enabled repositories.
        
        Returns:
            List of enabled repository configurations
        """
        return [repo for repo in self.repositories if repo.get("enabled", True)]
    
    def refresh_plugin_list(self, force: bool = False) -> Dict[str, Any]:
        """
        Refresh the list of available plugins from all repositories.
        
        Args:
            force: Whether to force refresh (ignore cache)
            
        Returns:
            Dictionary containing refresh results and statistics
        """
        try:
            start_time = time.time()
            
            # Clear cache if forced
            if force:
                self.available_plugins = {}
                self.plugin_cache = {}
                logger.info("Cleared plugin cache for forced refresh")
            
            # Get enabled repositories
            enabled_repos = self.get_enabled_repositories()
            if not enabled_repos:
                logger.warning("No enabled repositories available for refresh")
                return {
                    "success": False,
                    "message": "No enabled repositories",
                    "plugins_refreshed": 0,
                    "repositories_checked": 0,
                    "duration_seconds": time.time() - start_time
                }
            
            # Refresh from each repository
            total_plugins = 0
            successful_repos = 0
            failed_repos = 0
            
            for repo in enabled_repos:
                try:
                    repo_start_time = time.time()
                    
                    # Check if we should use cache
                    use_cache = not force and self.cache_enabled
                    cache_key = f"{repo['url']}_plugins"
                    
                    if use_cache and cache_key in self.plugin_cache:
                        # Use cached data
                        cached_data = self.plugin_cache[cache_key]
                        if time.time() - cached_data['timestamp'] < (self.cache_expiration_days * 24 * 3600):
                            plugins = cached_data['plugins']
                            logger.debug(f"Using cached plugin list for {repo['name']}")
                        else:
                            # Cache expired, refresh
                            use_cache = False
                    
                    if not use_cache:
                        # Fetch fresh data from repository
                        plugins = self._fetch_plugin_list_from_repository(repo)
                        
                        # Update cache
                        if self.cache_enabled:
                            self.plugin_cache[cache_key] = {
                                'plugins': plugins,
                                'timestamp': time.time(),
                                'repository': repo['name']
                            }
                    
                    # Merge plugins into available list
                    for plugin_name, plugin_info in plugins.items():
                        # Add repository source information
                        plugin_info['_source_repository'] = repo['name']
                        plugin_info['_source_url'] = repo['url']
                        plugin_info['_source_type'] = repo['type']
                        
                        # Update or add plugin
                        if plugin_name in self.available_plugins:
                            # Keep the highest version
                            existing_version = self.available_plugins[plugin_name].get('version', '0.0.0')
                            new_version = plugin_info.get('version', '0.0.0')
                            if self._compare_versions(new_version, existing_version) > 0:
                                self.available_plugins[plugin_name] = plugin_info
                                logger.debug(f"Updated plugin {plugin_name} from {repo['name']} (v{existing_version} -> v{new_version})")
                        else:
                            self.available_plugins[plugin_name] = plugin_info
                            logger.debug(f"Added plugin {plugin_name} from {repo['name']}")
                    
                    total_plugins += len(plugins)
                    successful_repos += 1
                    
                    # Update repository stats
                    repo['last_checked'] = time.time()
                    repo['last_success'] = time.time()
                    
                    logger.info(f"Refreshed {len(plugins)} plugins from {repo['name']} in {time.time() - repo_start_time:.2f}s")
                    
                except Exception as repo_error:
                    failed_repos += 1
                    repo['last_checked'] = time.time()
                    # Don't update last_success on failure
                    
                    error_msg = f"Failed to refresh plugins from {repo['name']}: {str(repo_error)}"
                    logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            duration = time.time() - start_time
            
            result = {
                "success": successful_repos > 0,
                "message": f"Refreshed {total_plugins} plugins from {successful_repos} repositories",
                "plugins_refreshed": total_plugins,
                "repositories_checked": len(enabled_repos),
                "repositories_successful": successful_repos,
                "repositories_failed": failed_repos,
                "duration_seconds": duration,
                "available_plugins": len(self.available_plugins),
                "timestamp": time.time()
            }
            
            logger.info(f"Plugin refresh completed: {result['message']} in {duration:.2f}s")
            return result
            
        except Exception as e:
            error_msg = f"Failed to refresh plugin list: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            if MARKETPLACE_EXCEPTIONS_AVAILABLE:
                raise PluginMarketplaceException(
                    message=error_msg,
                    context={"phase": "plugin_refresh", "error": str(e)}
                ) from e
            
            return {
                "success": False,
                "message": error_msg,
                "plugins_refreshed": 0,
                "repositories_checked": 0,
                "duration_seconds": time.time() - start_time
            }
    
    def _fetch_plugin_list_from_repository(self, repository: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch plugin list from a specific repository.
        
        Args:
            repository: Repository configuration
            
        Returns:
            Dictionary of plugins from the repository
            
        Raises:
            PluginMarketplaceException: If fetch fails
        """
        try:
            # Build API endpoint URL
            base_url = repository['url'].rstrip('/')
            api_endpoint = f"{base_url}/plugins"
            
            logger.info(f"Fetching plugin list from {api_endpoint}")
            
            # Create request with timeout
            request = urllib.request.Request(
                api_endpoint,
                headers={
                    'User-Agent': 'MetaExtract-PluginMarketplace/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Set SSL context based on security settings
            ssl_context = None
            if repository['url'].startswith('https') and self.security_settings['verify_ssl']:
                ssl_context = ssl.create_default_context()
            
            # Send request with timeout
            with urllib.request.urlopen(
                request,
                timeout=self.security_settings['timeout_seconds'],
                context=ssl_context
            ) as response:
                # Check response status
                if response.status != 200:
                    error_msg = f"Repository returned status {response.status}: {response.reason}"
                    logger.error(error_msg)
                    raise PluginMarketplaceException(
                        message=error_msg,
                        context={"repository": repository['name'], "status": response.status}
                    )
                
                # Read and parse response
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    error_msg = f"Unexpected content type: {content_type}"
                    logger.error(error_msg)
                    raise PluginMarketplaceException(
                        message=error_msg,
                        context={"repository": repository['name'], "content_type": content_type}
                    )
                
                response_data = response.read()
                max_size = self.security_settings['max_download_size_mb'] * 1024 * 1024
                if len(response_data) > max_size:
                    error_msg = f"Response size exceeds maximum: {len(response_data)} > {max_size} bytes"
                    logger.error(error_msg)
                    raise PluginMarketplaceException(
                        message=error_msg,
                        context={"repository": repository['name'], "size": len(response_data)}
                    )
                
                # Parse JSON response
                try:
                    plugins_data = json.loads(response_data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse JSON response: {str(e)}"
                    logger.error(error_msg)
                    raise PluginMarketplaceException(
                        message=error_msg,
                        context={"repository": repository['name'], "error": str(e)}
                    ) from e
                
                # Validate response structure
                if not isinstance(plugins_data, dict) or 'plugins' not in plugins_data:
                    error_msg = "Invalid plugin list format: expected {'plugins': {...}}"
                    logger.error(error_msg)
                    raise PluginMarketplaceException(
                        message=error_msg,
                        context={"repository": repository['name']}
                    )
                
                # Validate each plugin
                validated_plugins = {}
                for plugin_name, plugin_info in plugins_data['plugins'].items():
                    try:
                        validated_plugin = self._validate_plugin_metadata(plugin_name, plugin_info, repository)
                        if validated_plugin:
                            validated_plugins[plugin_name] = validated_plugin
                    except Exception as e:
                        logger.warning(f"Skipping invalid plugin {plugin_name} from {repository['name']}: {str(e)}")
                        continue
                
                logger.info(f"Successfully fetched {len(validated_plugins)} valid plugins from {repository['name']}")
                return validated_plugins
                
        except urllib.error.URLError as e:
            error_msg = f"URL error fetching plugins from {repository['name']}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise PluginMarketplaceException(
                message=error_msg,
                context={"repository": repository['name'], "error": str(e)}
            ) from e
        except Exception as e:
            error_msg = f"Error fetching plugins from {repository['name']}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise PluginMarketplaceException(
                message=error_msg,
                context={"repository": repository['name'], "error": str(e)}
            ) from e
    
    def _validate_plugin_metadata(self, plugin_name: str, plugin_info: Dict[str, Any], repository: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate plugin metadata from a repository.
        
        Args:
            plugin_name: Name of the plugin
            plugin_info: Plugin metadata from repository
            repository: Repository information
            
        Returns:
            Validated plugin metadata or None if invalid
        """
        try:
            # Check required fields
            required_fields = ['version', 'description', 'download_url']
            for field in required_fields:
                if field not in plugin_info:
                    logger.warning(f"Plugin {plugin_name} missing required field: {field}")
                    return None
            
            # Validate version format
            version = plugin_info['version']
            if not self._validate_version_format(version):
                logger.warning(f"Plugin {plugin_name} has invalid version format: {version}")
                return None
            
            # Validate download URL
            download_url = plugin_info['download_url']
            if not download_url.startswith(('http://', 'https://')):
                logger.warning(f"Plugin {plugin_name} has invalid download URL: {download_url}")
                return None
            
            # Set default values
            plugin_info.setdefault('author', 'Unknown')
            plugin_info.setdefault('license', 'MIT')
            plugin_info.setdefault('min_metaextract_version', '1.0.0')
            plugin_info.setdefault('max_metaextract_version', '99.99.99')
            plugin_info.setdefault('dependencies', [])
            plugin_info.setdefault('categories', [])
            plugin_info.setdefault('tags', [])
            plugin_info.setdefault('rating', 0.0)
            plugin_info.setdefault('downloads', 0)
            plugin_info.setdefault('last_updated', '')
            plugin_info.setdefault('created', '')
            
            # Add repository-specific information
            plugin_info['_repository_name'] = repository['name']
            plugin_info['_repository_url'] = repository['url']
            plugin_info['_repository_type'] = repository['type']
            plugin_info['_validation_timestamp'] = time.time()
            
            return plugin_info
            
        except Exception as e:
            logger.warning(f"Error validating plugin {plugin_name}: {str(e)}")
            return None
    
    def _validate_version_format(self, version: str) -> bool:
        """
        Validate plugin version format.
        
        Args:
            version: Version string to validate
            
        Returns:
            True if version format is valid, False otherwise
        """
        try:
            # Simple semantic version validation (X.Y.Z)
            pattern = r'^\d+\.\d+\.\d+($|-.*)'
            return bool(re.match(pattern, version))
        except Exception:
            return False
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            # Split versions into components
            v1_parts = version1.split('.')
            v2_parts = version2.split('.')
            
            # Pad with zeros for comparison
            max_length = max(len(v1_parts), len(v2_parts))
            v1_parts += ['0'] * (max_length - len(v1_parts))
            v2_parts += ['0'] * (max_length - len(v2_parts))
            
            # Compare each component
            for i in range(max_length):
                try:
                    v1_num = int(v1_parts[i])
                    v2_num = int(v2_parts[i])
                    if v1_num < v2_num:
                        return -1
                    elif v1_num > v2_num:
                        return 1
                except ValueError:
                    # If not numeric, compare as strings
                    if v1_parts[i] < v2_parts[i]:
                        return -1
                    elif v1_parts[i] > v2_parts[i]:
                        return 1
            
            return 0
            
        except Exception:
            # If comparison fails, consider them equal
            return 0
    
    def search_plugins(self, query: str = "", category: str = "", min_rating: float = 0.0, limit: int = 50) -> Dict[str, Any]:
        """
        Search available plugins with filters.
        
        Args:
            query: Search query string
            category: Category filter
            min_rating: Minimum rating filter
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            start_time = time.time()
            
            # Refresh plugin list if empty
            if not self.available_plugins:
                self.refresh_plugin_list()
            
            # Apply filters
            results = []
            for plugin_name, plugin_info in self.available_plugins.items():
                
                # Query filter
                if query:
                    query_lower = query.lower()
                    if (query_lower not in plugin_name.lower() and
                        query_lower not in plugin_info.get('description', '').lower() and
                        query_lower not in plugin_info.get('author', '').lower()):
                        continue
                
                # Category filter
                if category:
                    categories = plugin_info.get('categories', [])
                    if category.lower() not in [c.lower() for c in categories]:
                        continue
                
                # Rating filter
                if plugin_info.get('rating', 0.0) < min_rating:
                    continue
                
                # Add to results
                results.append({
                    'name': plugin_name,
                    'version': plugin_info.get('version', 'unknown'),
                    'description': plugin_info.get('description', ''),
                    'author': plugin_info.get('author', 'unknown'),
                    'rating': plugin_info.get('rating', 0.0),
                    'downloads': plugin_info.get('downloads', 0),
                    'categories': plugin_info.get('categories', []),
                    'tags': plugin_info.get('tags', []),
                    'repository': plugin_info.get('_repository_name', 'unknown'),
                    'repository_type': plugin_info.get('_repository_type', 'unknown'),
                    'installed': plugin_name in self.installed_plugins,
                    'installed_version': self.installed_plugins.get(plugin_name, {}).get('version', None),
                    'update_available': self._check_plugin_update_available(plugin_name, plugin_info)
                })
            
            # Sort results by rating (descending)
            results.sort(key=lambda x: x['rating'], reverse=True)
            
            # Apply limit
            results = results[:limit]
            
            duration = time.time() - start_time
            
            return {
                'success': True,
                'query': query,
                'category': category,
                'min_rating': min_rating,
                'results': results,
                'total_results': len(results),
                'total_available': len(self.available_plugins),
                'duration_seconds': duration,
                'timestamp': time.time()
            }
            
        except Exception as e:
            error_msg = f"Error searching plugins: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return {
                'success': False,
                'error': error_msg,
                'results': [],
                'total_results': 0,
                'duration_seconds': 0.0
            }
    
    def _check_plugin_update_available(self, plugin_name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        Check if an update is available for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            plugin_info: Plugin information from marketplace
            
        Returns:
            True if update is available, False otherwise
        """
        try:
            if plugin_name not in self.installed_plugins:
                return False
            
            installed_version = self.installed_plugins[plugin_name].get('version', '0.0.0')
            available_version = plugin_info.get('version', '0.0.0')
            
            return self._compare_versions(available_version, installed_version) > 0
            
        except Exception as e:
            logger.warning(f"Error checking update for {plugin_name}: {str(e)}")
            return False
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin information dictionary or None if not found
        """
        try:
            # Check installed plugins first
            if plugin_name in self.installed_plugins:
                installed_info = self.installed_plugins[plugin_name]
            else:
                installed_info = None
            
            # Check available plugins
            if plugin_name in self.available_plugins:
                available_info = self.available_plugins[plugin_name]
            else:
                available_info = None
            
            # Combine information
            if available_info or installed_info:
                result = {
                    'name': plugin_name,
                    'installed': installed_info is not None,
                    'available': available_info is not None,
                    'update_available': False,
                    'metadata': {}
                }
                
                # Add installed information
                if installed_info:
                    result['metadata']['installed'] = {
                        'version': installed_info.get('version', 'unknown'),
                        'source': installed_info.get('source', 'unknown'),
                        'install_date': installed_info.get('install_date', 0),
                        'last_updated': installed_info.get('last_updated', 0),
                        'enabled': installed_info.get('enabled', True)
                    }
                
                # Add available information
                if available_info:
                    result['metadata']['available'] = {
                        'version': available_info.get('version', 'unknown'),
                        'description': available_info.get('description', ''),
                        'author': available_info.get('author', 'unknown'),
                        'license': available_info.get('license', 'unknown'),
                        'download_url': available_info.get('download_url', ''),
                        'rating': available_info.get('rating', 0.0),
                        'downloads': available_info.get('downloads', 0),
                        'categories': available_info.get('categories', []),
                        'tags': available_info.get('tags', []),
                        'dependencies': available_info.get('dependencies', []),
                        'min_metaextract_version': available_info.get('min_metaextract_version', '1.0.0'),
                        'max_metaextract_version': available_info.get('max_metaextract_version', '99.99.99'),
                        'repository': available_info.get('_repository_name', 'unknown'),
                        'repository_type': available_info.get('_repository_type', 'unknown'),
                        'last_updated': available_info.get('last_updated', ''),
                        'created': available_info.get('created', '')
                    }
                    
                    # Check for updates
                    if installed_info and available_info:
                        result['update_available'] = self._check_plugin_update_available(plugin_name, available_info)
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting plugin info for {plugin_name}: {str(e)}")
            return None


# Global marketplace instance
_plugin_marketplace = None


def get_plugin_marketplace() -> PluginMarketplace:
    """
    Get the global plugin marketplace instance.
    
    Returns:
        PluginMarketplace instance
    """
    global _plugin_marketplace
    if _plugin_marketplace is None:
        _plugin_marketplace = PluginMarketplace()
    return _plugin_marketplace


# Convenience functions for global access

def refresh_plugin_list_global(force: bool = False) -> Dict[str, Any]:
    """Refresh plugin list from all repositories."""
    return get_plugin_marketplace().refresh_plugin_list(force)


def search_plugins_global(query: str = "", category: str = "", min_rating: float = 0.0, limit: int = 50) -> Dict[str, Any]:
    """Search available plugins."""
    return get_plugin_marketplace().search_plugins(query, category, min_rating, limit)


def get_plugin_info_global(plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a plugin."""
    return get_plugin_marketplace().get_plugin_info(plugin_name)


def get_marketplace_stats_global() -> Dict[str, Any]:
    """Get marketplace statistics."""
    return get_plugin_marketplace().get_marketplace_stats()
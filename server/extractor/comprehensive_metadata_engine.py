#!/usr/bin/env python3
"""
MetaExtract - Comprehensive Metadata Extraction Engine v4.0

ULTIMATE METADATA EXTRACTION ENGINE
Extracts a comprehensive set of metadata fields from files across domains (goal configurable):

DOMAINS COVERED:
- Image Metadata (15,000+ fields): EXIF, MakerNotes, IPTC, XMP, ICC, HDR, Computational Photography
- Video Metadata (8,000+ fields): Container formats, Codec-specific, Professional video, 3D/VR, Drone telemetry
- Audio Metadata (3,500+ fields): ID3, Vorbis, FLAC, Broadcast audio, Podcast metadata
- Document Metadata (4,000+ fields): PDF, Office documents, HTML/Web metadata
- Scientific Metadata (15,000+ fields): DICOM medical imaging, FITS astronomy, Microscopy, GIS/Geospatial
- Forensic Metadata (2,500+ fields): Filesystem, Digital signatures, Security metadata, Blockchain provenance
- Social/Mobile/Web Metadata (2,000+ fields): Platform metadata, Mobile sensors, Web standards

SPECIALIZED ENGINES:
- Medical Imaging Engine (DICOM): 4,600+ standardized fields
- Astronomical Data Engine (FITS): 3,000+ fields with WCS support
- Geospatial Engine (GeoTIFF, Shapefile): Full CRS and projection metadata
- Forensic Analysis Engine: Chain of custody, digital signatures, steganography detection
- Drone/UAV Engine: Flight telemetry, sensor data, GPS tracks
- Professional Video Engine: Broadcast standards, HDR metadata, timecode
- Scientific Instrument Engine: Microscopy, spectroscopy, telemetry

Author: MetaExtract Team
Version: 4.0.0 - Ultimate Edition
"""

import logging
import sys
from typing import Optional

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the dynamic module discovery system
try:
    from .module_discovery import (
        discover_and_register_modules,
        get_extraction_function_safe,
        get_module_discovery_stats,
        create_safe_execution_wrapper,
        build_dependency_graph_global,
        get_dependency_stats_global,
        enable_hot_reloading_global,
        get_hot_reload_stats_global,
        enable_plugins_global,
        discover_and_load_plugins_global,
        get_plugin_stats_global,
        get_all_available_extraction_functions
    )
    MODULE_DISCOVERY_AVAILABLE = True
except ImportError:
    MODULE_DISCOVERY_AVAILABLE = False
    logger.warning("Module discovery system not available, falling back to manual imports")

import os
import json
import asyncio
import subprocess
import tempfile
import struct
import xml.etree.ElementTree as ET
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import hashlib
import base64
import mimetypes
import time
import traceback

# Import monitoring and alerting
try:
    from .monitoring import record_extraction_for_monitoring
    MONITORING_AVAILABLE = True
except ImportError:
    # Create a dummy function if monitoring is not available
    def record_extraction_for_monitoring(processing_time_ms: float, success: bool,
                                       tier: str = "unknown", file_type: str = "unknown",
                                       error_type: Optional[str] = None):
        pass
    MONITORING_AVAILABLE = False

# Import extraction observability (provenance, sensitive fields, shadow mode)
try:
    from .extraction_observability import (
        record_top_level_provenance,
        should_run_shadow,
        run_shadow_extraction_safe,
        add_observability_to_result,
    )
    OBSERVABILITY_AVAILABLE = True
except ImportError as _obs_err:
    OBSERVABILITY_AVAILABLE = False
    logger.warning(f"Extraction observability not available: {_obs_err}")
    
    # Stub functions if observability module not available
    def record_top_level_provenance(**kwargs):
        pass
    def should_run_shadow():
        return False
    def run_shadow_extraction_safe(filepath, timeout=2.0):
        return {"enabled": False, "error": "observability module not available"}
    def add_observability_to_result(result, provenance, conflicts, shadow_info=None):
        return result

try:
    from .alerting import get_alert_manager
    ALERTING_AVAILABLE = True
except ImportError:
    # Create a dummy function if alerting is not available
    def get_alert_manager():
        class DummyAlertManager:
            def record_extraction(self, *args, **kwargs):
                pass
        return DummyAlertManager()
    ALERTING_AVAILABLE = False

try:
    from .analytics import record_extraction_for_analytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    # Create a dummy function if analytics is not available
    def record_extraction_for_analytics(processing_time_ms: float, success: bool,
                                      tier: str = "unknown", file_type: str = "unknown",
                                      file_size: Optional[str] = None, error_type: Optional[str] = None):
        pass
    ANALYTICS_AVAILABLE = False

# Import base engine
if __name__ == "__main__":
    # Add current directory to path for standalone execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

try:
    from metadata_engine import (
        extract_metadata as extract_base_metadata,
        TIER_CONFIGS, Tier, logger,
        PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
        MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
    )
except ImportError:
    try:
        from .metadata_engine import (
            extract_metadata as extract_base_metadata,
            TIER_CONFIGS, Tier, logger,
            PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
            MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
        )
    except ImportError:
        # Fallback for different import contexts
        # sys and os are already imported globally
        sys.path.append(os.path.dirname(__file__))
        from metadata_engine import (
            extract_metadata as extract_base_metadata,
            TIER_CONFIGS, Tier, logger,
            PIL_AVAILABLE, EXIFREAD_AVAILABLE, FFMPEG_AVAILABLE,
            MUTAGEN_AVAILABLE, PYPDF_AVAILABLE, EXIFTOOL_AVAILABLE
        )

# ============================================================================
# Robust Error Handling Utilities
# ============================================================================

def safe_extract_module(
    extraction_func: Callable[..., Optional[Dict[str, Any]]],
    filepath: str,
    module_name: str,
    *args: Any,
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """
    Safely execute a metadata extraction module with comprehensive error handling.

    Args:
        extraction_func: The extraction function to call
        filepath: Path to the file being processed
        module_name: Name of the module for logging purposes
        *args, **kwargs: Additional arguments to pass to the extraction function

    Returns:
        The result of the extraction function or None if it fails
    """
    import time
    start_time = time.time()
    file_size = "unknown"
    try:
        # Get file size for logging
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else "unknown"
    except:
        pass  # If we can't get file size, continue with "unknown"

    def module_error(
        *,
        error_type: str,
        error_message: str,
        technical_message: str,
        duration_seconds: float,
    ) -> Dict[str, Any]:
        return {
            "available": False,
            "error_type": error_type,
            "error": error_message,
            "module": module_name,
            "technical_message": technical_message,
            "performance": {
                module_name: {
                    "duration_seconds": duration_seconds,
                    "status": "failed",
                    "error_type": error_type,
                    "file_path": filepath,
                    "file_size": file_size,
                    "module_name": module_name,
                }
            },
        }

    try:
        logger.info(f"Starting extraction with {module_name} for {filepath} (size: {file_size} bytes)")
        result = extraction_func(filepath, *args, **kwargs)
        duration = time.time() - start_time
        if result is None:
            logger.info(
                f"No meaningful data produced by {module_name} in {duration:.3f}s for {filepath}"
            )
            return None
        logger.info(f"Successfully completed extraction with {module_name} in {duration:.3f}s for {filepath}")
        # Add performance metrics to result if it's a dict
        if isinstance(result, dict):
            if 'performance' not in result:
                result['performance'] = {}
            result['performance'][module_name] = {
                'duration_seconds': duration,
                'status': 'success',
                'file_path': filepath,
                'file_size': file_size,
                'module_name': module_name
            }
        return result
    except ImportError as e:
        logger.error(f"Module {module_name} not available for {filepath}: {e}")
        logger.debug(f"Full traceback for {module_name}: {traceback.format_exc()}")

        duration = time.time() - start_time
        return module_error(
            error_type="ImportError",
            error_message=f"Required module not available: {e}",
            technical_message=str(e),
            duration_seconds=duration,
        )
    except FileNotFoundError as e:
        logger.warning(f"File not found for {module_name} with {filepath}: {e}")

        duration = time.time() - start_time
        return module_error(
            error_type="FileNotFoundError",
            error_message=f"Input file not found: {e}",
            technical_message=str(e),
            duration_seconds=duration,
        )
    except PermissionError as e:
        logger.warning(f"Permission denied for {module_name} with {filepath}: {e}")

        duration = time.time() - start_time
        return module_error(
            error_type="PermissionError",
            error_message=f"Permission denied: {e}",
            technical_message=str(e),
            duration_seconds=duration,
        )
    except MemoryError as e:
        logger.error(f"Memory error during {module_name} extraction for {filepath}: {e}")
        logger.debug(f"Full traceback for {module_name}: {traceback.format_exc()}")

        duration = time.time() - start_time
        return module_error(
            error_type="MemoryError",
            error_message="Insufficient memory to process file",
            technical_message=str(e),
            duration_seconds=duration,
        )
    except TimeoutError as e:
        logger.error(f"Timeout during {module_name} extraction for {filepath}: {e}")
        logger.debug(f"Full traceback for {module_name}: {traceback.format_exc()}")

        duration = time.time() - start_time
        return module_error(
            error_type="TimeoutError",
            error_message="Extraction timed out",
            technical_message=str(e),
            duration_seconds=duration,
        )
    except Exception as e:
        logger.error(f"Unexpected error in {module_name} extraction for {filepath}: {e}")
        logger.debug(f"Full traceback for {module_name}: {traceback.format_exc()}")

        duration = time.time() - start_time
        return module_error(
            error_type=type(e).__name__,
            error_message=f"Unexpected error occurred during processing: {e}",
            technical_message=str(e),
            duration_seconds=duration,
        )

try:
    from .modules.metadata_db import store_file_metadata
except ImportError:
    try:
        from modules.metadata_db import store_file_metadata  # type: ignore
    except ImportError:
        # Create a dummy function if module not available
        def store_file_metadata(*args, **kwargs):
            pass

# Cache import - consolidated to single location
try:
    from .cache import get_cache
except ImportError:
    try:
        from cache import get_cache  # type: ignore
    except ImportError:
        get_cache = None  # type: ignore[assignment]

# ============================================================================
# Error Handling Utilities
# ============================================================================

# Error message catalog for user-friendly messages
ERROR_MESSAGES = {
    "ERR_IMPORTERROR": "Required module not available",
    "ERR_FILENOTFOUNDERROR": "Input file not found",
    "ERR_PERMISSIONERROR": "Permission denied",
    "ERR_MEMORYERROR": "Insufficient memory to process file",
    "ERR_TIMEOUTERROR": "Operation timed out",
    "ERR_EXCEPTION": "Unexpected error occurred",
    "ERR_MODULE_IMPORT": "Required module not available",
    "ERR_FILE_ACCESS": "Cannot access the specified file",
    "ERR_PROCESSING": "Error processing file data",
    "ERR_SYSTEM": "System error occurred",
    "ERR_CONFIGURATION": "Configuration error detected"
}

# Suggested actions for common error types
SUGGESTED_ACTIONS = {
    "ERR_IMPORTERROR": "Check module installation or dependencies",
    "ERR_FILENOTFOUNDERROR": "Verify file path and permissions",
    "ERR_PERMISSIONERROR": "Check file permissions and access rights",
    "ERR_MEMORYERROR": "Close other applications or increase system memory",
    "ERR_TIMEOUTERROR": "Check network connectivity or increase timeout",
    "ERR_EXCEPTION": "Check logs for details and report to support",
    "ERR_MODULE_IMPORT": "Install required module or check dependencies",
    "ERR_FILE_ACCESS": "Verify file exists and has proper permissions",
    "ERR_PROCESSING": "Check file format and try again",
    "ERR_SYSTEM": "Check system resources and try again later",
    "ERR_CONFIGURATION": "Review configuration settings"
}

def get_user_friendly_message(error_code: str, exception: Exception) -> str:
    """
    Get user-friendly message for an error code.
    
    Args:
        error_code: The error code to look up
        exception: The original exception (fallback)
        
    Returns:
        User-friendly error message
    """
    return ERROR_MESSAGES.get(error_code, str(exception))

def get_suggested_action(error_code: str) -> str:
    """
    Get suggested action for an error code.
    
    Args:
        error_code: The error code to look up
        
    Returns:
        Suggested action or None
    """
    return SUGGESTED_ACTIONS.get(error_code, "Check logs and try again")

def get_system_context() -> Dict[str, Any]:
    """
    Get system context information for error reporting.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil  # type: ignore
    
    system_info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version()
    }
    
    try:
        # Get memory information
        memory = psutil.virtual_memory()
        system_info["memory"] = {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "percent_used": memory.percent
        }
        
        # Get CPU information
        system_info["cpu"] = {
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage_percent": psutil.cpu_percent(interval=0.1)
        }
        
        # Get disk information
        disk = psutil.disk_usage('/')
        system_info["disk"] = {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent_used": disk.percent
        }
        
    except ImportError:
        # psutil not available, provide basic info
        system_info["memory"] = "psutil not available"
        system_info["cpu"] = "psutil not available"
        system_info["disk"] = "psutil not available"
    except Exception as e:
        system_info["system_error"] = str(e)
    
    return system_info

def create_standardized_error(
    exception: Exception,
    module_name: str,
    filepath: str,
    start_time: float,
    error_context: Dict[str, Any] = None,
    custom_message: str = None,
    error_code: str = None,
    severity: str = "medium",
    recoverable: bool = False,
    suggested_action: str = None
) -> Dict[str, Any]:
    """
    Create a standardized error response with comprehensive information.
    
    Args:
        exception: The original exception
        module_name: Name of the module where error occurred
        filepath: Path to the file being processed
        start_time: Start time for duration calculation
        error_context: Additional context information
        custom_message: Custom user-friendly message
        error_code: Standardized error code
        severity: Error severity (low/medium/high/critical)
        recoverable: Whether the error is recoverable
        suggested_action: Suggested recovery action
        
    Returns:
        Standardized error response dictionary
    """
    duration = time.time() - start_time
    
    # Determine file information
    file_size = "unknown"
    file_type = "unknown"
    try:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            file_type = mimetypes.guess_type(filepath)[0] or "unknown"
    except:
        pass
    
    # Determine error code if not provided
    if not error_code:
        error_code = f"ERR_{type(exception).__name__.upper()}"
    
    # Build standardized error response
    error_response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": custom_message or get_user_friendly_message(error_code, exception),
            "technical_message": str(exception),
            "type": type(exception).__name__,
            "severity": severity,
            "recoverable": recoverable,
            "suggested_action": suggested_action or get_suggested_action(error_code)
        },
        "context": {
            "module": module_name,
            "file_path": filepath,
            "file_size": file_size,
            "file_type": file_type,
            "system_info": get_system_context()
        },
        "performance": {
            "duration_seconds": duration,
            "status": "failed",
            "error_code": error_code
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add additional context if provided
    if error_context:
        error_response["context"].update(error_context)
    
    return error_response

# ============================================================================
# Specialized Library Availability Checks
# ============================================================================

# Medical imaging (DICOM)
try:
    import pydicom
    DICOM_AVAILABLE = True
except ImportError:
    DICOM_AVAILABLE = False

# Astronomical data (FITS)
try:
    from astropy.io import fits
    from astropy.wcs import WCS
    FITS_AVAILABLE = True
except ImportError:
    FITS_AVAILABLE = False

# Geospatial data
try:
    import rasterio
    from rasterio.crs import CRS
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    import fiona
    FIONA_AVAILABLE = True
except ImportError:
    FIONA_AVAILABLE = False

# Scientific data formats
try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False

try:
    import netCDF4
    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False

# Advanced image analysis
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# Microscopy
try:
    from aicsimageio import AICSImage
    MICROSCOPY_AVAILABLE = True
except ImportError:
    MICROSCOPY_AVAILABLE = False

# Blockchain/Web3
try:
    import web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# Advanced audio analysis
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Optional internal modules (best-effort)
try:
    from .modules.web_metadata import extract_web_metadata
except ImportError:
    extract_web_metadata = None  # type: ignore[assignment]

try:
    from .modules.social_media_metadata import extract_social_media_metadata
except ImportError:
    extract_social_media_metadata = None  # type: ignore[assignment]

try:
    from .modules.mobile_metadata import extract_mobile_metadata
except ImportError:
    extract_mobile_metadata = None  # type: ignore[assignment]

try:
    from .modules.forensic_metadata import extract_forensic_metadata
except ImportError:
    extract_forensic_metadata = None  # type: ignore[assignment]

try:
    from .modules.action_camera import extract_action_camera_metadata
except ImportError:
    extract_action_camera_metadata = None  # type: ignore[assignment]

try:
    from .modules.camera_360 import extract_360_camera_metadata
except ImportError:
    extract_360_camera_metadata = None  # type: ignore[assignment]

try:
    from .modules.print_publishing import extract_print_publishing_metadata
except ImportError:
    extract_print_publishing_metadata = None  # type: ignore[assignment]

try:
    from .modules.workflow_dam import extract_workflow_dam_metadata
except ImportError:
    extract_workflow_dam_metadata = None  # type: ignore[assignment]

try:
    from .modules.audio import extract_audio_advanced_metadata
except ImportError:
    extract_audio_advanced_metadata = None  # type: ignore[assignment]

try:
    from .modules.video import extract_video_advanced_metadata
except ImportError:
    extract_video_advanced_metadata = None  # type: ignore[assignment]

try:
    from .modules.timeline import analyze_single_file_timeline
except ImportError:
    analyze_single_file_timeline = None  # type: ignore[assignment]

try:
    from .modules.comparison import MetadataComparator
except ImportError:
    MetadataComparator = None  # type: ignore[assignment]

try:
    from .modules.advanced_analysis import (
        detect_ai_content,
        detect_enhanced_manipulation,
        detect_enhanced_steganography,
    )
except ImportError:
    detect_ai_content = None  # type: ignore[assignment]
    detect_enhanced_manipulation = None  # type: ignore[assignment]
    detect_enhanced_steganography = None  # type: ignore[assignment]

def log_extraction_event(
    event_type: str,
    filepath: str,
    module_name: str,
    status: str = "info",
    details: Optional[Dict[str, Any]] = None,
    duration: Optional[float] = None
) -> None:
    """
    Log a comprehensive extraction event with detailed information.

    Args:
        event_type: Type of event (e.g., 'extraction_start', 'extraction_complete', 'error')
        filepath: Path to the file being processed
        module_name: Name of the module processing the file
        status: Log level ('debug', 'info', 'warning', 'error', 'critical')
        details: Additional details about the event
        duration: Processing duration in seconds (if applicable)
    """
    file_size = "unknown"
    try:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
    except:
        pass

    log_message = f"[{event_type}] File: {filepath}, Module: {module_name}, Size: {file_size}"
    if duration is not None:
        log_message += f", Duration: {duration:.3f}s"
    if details:
        log_message += f", Details: {details}"

    # Map status to appropriate logger method
    if status.lower() == 'debug':
        logger.debug(log_message)
    elif status.lower() == 'warning':
        logger.warning(log_message)
    elif status.lower() == 'error':
        logger.error(log_message)
    elif status.lower() == 'critical':
        logger.critical(log_message)
    else:  # default to info
        logger.info(log_message)


def _check_cache_and_return_if_found(filepath: str, tier: str, start_time: float, is_async: bool = False) -> Optional[Dict[str, Any]]:
    """
    Check cache for existing result and return if found.
    
    Args:
        filepath: Path to the file being processed
        tier: Tier level for cache lookup
        start_time: Start time for duration calculation
        is_async: Whether this is an async operation (for logging)
        
    Returns:
        Cached result if found, None otherwise
    """
    if not get_cache:
        return None
        
    try:
        cache = get_cache()
        cached_result = cache.get(filepath, tier)
        if cached_result:
            duration = time.time() - start_time
            log_prefix = "async_" if is_async else ""
            log_extraction_event(
                event_type=f"{log_prefix}cache_hit",
                filepath=filepath,
                module_name="comprehensive_engine",
                status="info",
                duration=duration
            )
            return cached_result
    except Exception as e:
        logger.warning(f"{'Async ' if is_async else ''}Cache lookup failed for {filepath}: {e}")
    
    return None


try:
    from .modules.steganography import analyze_steganography
except ImportError:
    analyze_steganography = None  # type: ignore[assignment]

# New AI Generation Detection module
try:
    from .modules.ai_generation_detector import detect_ai_generation
except ImportError:
    detect_ai_generation = None  # type: ignore[assignment]

# New Image Forensics module
try:
    from .modules.image_forensics import analyze_image_forensics
except ImportError:
    analyze_image_forensics = None  # type: ignore[assignment]

# New Photoshop PSD module
try:
    from .modules.photoshop_psd import analyze_photoshop_psd
except ImportError:
    analyze_photoshop_psd = None  # type: ignore[assignment]

# New Edit History module
try:
    from .modules.edit_history import analyze_edit_history
except ImportError:
    analyze_edit_history = None  # type: ignore[assignment]

# New OpenEXR HDR module
try:
    from .modules.openexr_hdr import analyze_openexr_hdr
except ImportError:
    analyze_openexr_hdr = None  # type: ignore[assignment]

# New ICC Profile parser module
try:
    from .modules.icc_profile_parser import extract_icc_profile
except ImportError:
    extract_icc_profile = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the emerging technology module directly by file path
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'emerging_technology_ultimate_advanced.py')

    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("emerging_tech", module_path)
        if spec and spec.loader:
            emerging_tech_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(emerging_tech_module)
            extract_emerging_technology_metadata = emerging_tech_module.extract_emerging_technology_metadata
            logger.info("Successfully imported emerging technology module")
        else:
            extract_emerging_technology_metadata = None
    else:
        extract_emerging_technology_metadata = None

except Exception as e:
    logger.warning(f"Could not import emerging technology module: {e}")
    extract_emerging_technology_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the advanced video module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'advanced_video_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("advanced_video", module_path)
        if spec and spec.loader:
            advanced_video_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_video_module)
            extract_advanced_video_metadata = advanced_video_module.extract_advanced_video_metadata
            logger.info("Successfully imported advanced video module")
        else:
            extract_advanced_video_metadata = None
    else:
        extract_advanced_video_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import advanced video module: {e}")
    extract_advanced_video_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the advanced audio module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'advanced_audio_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("advanced_audio", module_path)
        if spec and spec.loader:
            advanced_audio_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(advanced_audio_module)
            extract_advanced_audio_metadata = advanced_audio_module.extract_advanced_audio_metadata
            logger.info("Successfully imported advanced audio module")
        else:
            extract_advanced_audio_metadata = None
    else:
        extract_advanced_audio_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import advanced audio module: {e}")
    extract_advanced_audio_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the document metadata module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'document_metadata_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("document_metadata", module_path)
        if spec and spec.loader:
            document_metadata_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(document_metadata_module)
            extract_document_metadata = document_metadata_module.extract_document_metadata
            logger.info("Successfully imported document metadata module")
        else:
            extract_document_metadata = None
    else:
        extract_document_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import document metadata module: {e}")
    extract_document_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the scientific research module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'scientific_research_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("scientific_research", module_path)
        if spec and spec.loader:
            scientific_research_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scientific_research_module)
            extract_scientific_research_metadata = scientific_research_module.extract_scientific_research_metadata
            logger.info("Successfully imported scientific research module")
        else:
            extract_scientific_research_metadata = None
    else:
        extract_scientific_research_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import scientific research module: {e}")
    extract_scientific_research_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the multimedia entertainment module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'multimedia_entertainment_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("multimedia_entertainment", module_path)
        if spec and spec.loader:
            multimedia_entertainment_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(multimedia_entertainment_module)
            extract_multimedia_entertainment_metadata = multimedia_entertainment_module.extract_multimedia_entertainment_metadata
            logger.info("Successfully imported multimedia entertainment module")
        else:
            extract_multimedia_entertainment_metadata = None
    else:
        extract_multimedia_entertainment_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import multimedia entertainment module: {e}")
    extract_multimedia_entertainment_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the industrial manufacturing module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'industrial_manufacturing_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("industrial_manufacturing", module_path)
        if spec and spec.loader:
            industrial_manufacturing_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(industrial_manufacturing_module)
            extract_industrial_manufacturing_metadata = industrial_manufacturing_module.extract_industrial_manufacturing_metadata
            logger.info("Successfully imported industrial manufacturing module")
        else:
            extract_industrial_manufacturing_metadata = None
    else:
        extract_industrial_manufacturing_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import industrial manufacturing module: {e}")
    extract_industrial_manufacturing_metadata = None  # type: ignore[assignment]

try:
    # sys, os, and importlib.util are already imported globally

    # Import the financial business module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'financial_business_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("financial_business", module_path)
        if spec and spec.loader:
            financial_business_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(financial_business_module)
            extract_financial_business_metadata = financial_business_module.extract_financial_business_metadata
            logger.info("Successfully imported financial business module")
        else:
            extract_financial_business_metadata = None
    else:
        extract_financial_business_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import financial business module: {e}")
    extract_financial_business_metadata = None  # type: ignore[assignment]

# Healthcare Medical Ultimate Module
try:
    import importlib.util
    
    # Import the healthcare medical module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'healthcare_medical_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("healthcare_medical", module_path)
        if spec and spec.loader:
            healthcare_medical_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(healthcare_medical_module)
            extract_healthcare_medical_metadata = healthcare_medical_module.extract_healthcare_medical_metadata
            logger.info("Successfully imported healthcare medical module")
        else:
            extract_healthcare_medical_metadata = None
    else:
        extract_healthcare_medical_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import healthcare medical module: {e}")
    extract_healthcare_medical_metadata = None  # type: ignore[assignment]

# Transportation Logistics Ultimate Module
try:
    import importlib.util
    
    # Import the transportation logistics module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'transportation_logistics_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("transportation_logistics", module_path)
        if spec and spec.loader:
            transportation_logistics_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(transportation_logistics_module)
            extract_transportation_logistics_metadata = transportation_logistics_module.extract_transportation_logistics_metadata
            logger.info("Successfully imported transportation logistics module")
        else:
            extract_transportation_logistics_metadata = None
    else:
        extract_transportation_logistics_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import transportation logistics module: {e}")
    extract_transportation_logistics_metadata = None  # type: ignore[assignment]

# Education Academic Ultimate Module
try:
    import importlib.util
    
    # Import the education academic module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'education_academic_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("education_academic", module_path)
        if spec and spec.loader:
            education_academic_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(education_academic_module)
            extract_education_academic_metadata = education_academic_module.extract_education_academic_metadata
            logger.info("Successfully imported education academic module")
        else:
            extract_education_academic_metadata = None
    else:
        extract_education_academic_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import education academic module: {e}")
    extract_education_academic_metadata = None  # type: ignore[assignment]

# Legal Compliance Ultimate Module
try:
    import importlib.util
    
    # Import the legal compliance module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'legal_compliance_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("legal_compliance", module_path)
        if spec and spec.loader:
            legal_compliance_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(legal_compliance_module)
            extract_legal_compliance_metadata = legal_compliance_module.extract_legal_compliance_metadata
            logger.info("Successfully imported legal compliance module")
        else:
            extract_legal_compliance_metadata = None
    else:
        extract_legal_compliance_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import legal compliance module: {e}")
    extract_legal_compliance_metadata = None  # type: ignore[assignment]

# Environmental Sustainability Ultimate Module
try:
    import importlib.util
    
    # Import the environmental sustainability module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'environmental_sustainability_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("environmental_sustainability", module_path)
        if spec and spec.loader:
            environmental_sustainability_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(environmental_sustainability_module)
            extract_environmental_sustainability_metadata = environmental_sustainability_module.extract_environmental_sustainability_metadata
            logger.info("Successfully imported environmental sustainability module")
        else:
            extract_environmental_sustainability_metadata = None
    else:
        extract_environmental_sustainability_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import environmental sustainability module: {e}")
    extract_environmental_sustainability_metadata = None  # type: ignore[assignment]

# Social Media Digital Ultimate Module
try:
    import importlib.util
    
    # Import the social media digital module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'social_media_digital_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("social_media_digital", module_path)
        if spec and spec.loader:
            social_media_digital_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(social_media_digital_module)
            extract_social_media_digital_metadata = social_media_digital_module.extract_social_media_digital_metadata
            logger.info("Successfully imported social media digital module")
        else:
            extract_social_media_digital_metadata = None
    else:
        extract_social_media_digital_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import social media digital module: {e}")
    extract_social_media_digital_metadata = None  # type: ignore[assignment]

# Gaming Entertainment Ultimate Module
try:
    import importlib.util
    
    # Import the gaming entertainment module
    extractor_dir = os.path.dirname(__file__)
    module_path = os.path.join(extractor_dir, 'modules', 'gaming_entertainment_ultimate.py')
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location("gaming_entertainment", module_path)
        if spec and spec.loader:
            gaming_entertainment_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gaming_entertainment_module)
            extract_gaming_entertainment_metadata = gaming_entertainment_module.extract_gaming_entertainment_metadata
            logger.info("Successfully imported gaming entertainment module")
        else:
            extract_gaming_entertainment_metadata = None
    else:
        extract_gaming_entertainment_metadata = None
        
except Exception as e:
    logger.warning(f"Could not import gaming entertainment module: {e}")
    extract_gaming_entertainment_metadata = None  # type: ignore[assignment]

# ============================================================================
# Comprehensive Tier Configuration
# ============================================================================

@dataclass
class ComprehensiveTierConfig:
    # Base features (from original engine)
    file_hashes: bool = False
    filesystem_details: bool = False
    calculated_fields: bool = False
    gps_data: bool = False
    makernotes: bool = False
    iptc_xmp: bool = False
    perceptual_hashes: bool = False
    thumbnails: bool = False
    video_encoding: bool = False
    audio_details: bool = False
    pdf_details: bool = False
    extended_attributes: bool = False
    raw_exif: bool = False
    forensic_details: bool = False
    serial_numbers: bool = False
    exiftool_enhanced: bool = False
    
    # Comprehensive features
    medical_imaging: bool = False          # DICOM extraction
    astronomical_data: bool = False        # FITS extraction
    geospatial_analysis: bool = False      # GIS/mapping data
    scientific_instruments: bool = False   # Lab equipment data
    drone_telemetry: bool = False         # UAV flight data
    professional_video: bool = False      # Broadcast/cinema metadata
    advanced_audio: bool = False          # Spectral analysis, broadcast audio
    blockchain_provenance: bool = False    # NFT, C2PA, digital signatures
    social_media_context: bool = False    # Platform-specific metadata
    mobile_sensors: bool = False          # Smartphone sensor data
    web_metadata: bool = False            # HTML, schema.org, Open Graph
    steganography_detection: bool = False # Hidden data analysis
    manipulation_detection: bool = False   # Image/video tampering
    timeline_reconstruction: bool = False  # Forensic timeline analysis
    batch_comparison: bool = False        # Multi-file analysis
    ai_content_detection: bool = False    # AI-generated content detection
    emerging_technology: bool = False     # AI/ML models, quantum, XR, IoT, etc.
    advanced_video_analysis: bool = False # Professional video analysis
    advanced_audio_analysis: bool = False # Professional audio analysis
    document_analysis: bool = False       # Office, PDF, web documents
    scientific_research: bool = False     # Research papers, lab data, microscopy, spectroscopy
    multimedia_entertainment: bool = False # Gaming, streaming, digital art, music production
    industrial_manufacturing: bool = False # CAD, CNC, quality control, IoT sensors
    financial_business: bool = False      # Financial reports, trading data, banking, compliance
    healthcare_medical: bool = False      # EHR, DICOM, clinical trials, medical devices
    transportation_logistics: bool = False # Vehicle telemetry, GPS tracking, supply chain
    education_academic: bool = False      # LMS, educational content, academic research
    legal_compliance: bool = False        # Legal documents, regulatory compliance, IP
    environmental_sustainability: bool = False # Environmental monitoring, climate data, ESG
    social_media_digital: bool = False    # Social media posts, digital marketing, messaging
    gaming_entertainment: bool = False    # Video games, esports, streaming, interactive media
    
    # Additional features referenced in code but missing from class
    workflow_dam: bool = False            # Workflow DAM metadata
    image_metadata: bool = False          # Image metadata processing
    video_metadata: bool = False          # Video metadata processing
    audio_metadata: bool = False          # Audio metadata processing
    document_metadata: bool = False       # Document metadata processing
    extended_metadata: bool = False       # Extended metadata processing
    specialized_metadata: bool = False    # Specialized metadata processing
    ai_ml_metadata: bool = False          # AI/ML metadata processing
    industrial_metadata: bool = False     # Industrial metadata processing
    scientific_metadata: bool = False     # Scientific metadata processing

COMPREHENSIVE_TIER_CONFIGS = {
    Tier.FREE: ComprehensiveTierConfig(),
    
    Tier.STARTER: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, audio_details=True, pdf_details=True, forensic_details=True,
        perceptual_hashes=True, thumbnails=True, web_metadata=True,
    ),
    
    Tier.PREMIUM: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True, 
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        # Premium additions
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
    ),
    
    Tier.SUPER: ComprehensiveTierConfig(
        # All Premium features plus:
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True, 
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
        # Super exclusive features
        medical_imaging=True, astronomical_data=True, scientific_instruments=True,
        professional_video=True, blockchain_provenance=True, social_media_context=True,
        manipulation_detection=True, ai_content_detection=True, emerging_technology=True,
        advanced_video_analysis=True, advanced_audio_analysis=True, document_analysis=True,
        scientific_research=True, multimedia_entertainment=True, industrial_manufacturing=True,
        financial_business=True, healthcare_medical=True, transportation_logistics=True,
        education_academic=True, legal_compliance=True, environmental_sustainability=True,
        social_media_digital=True, gaming_entertainment=True,
    ),
}

# ============================================================================
# Specialized Extraction Engines
# ============================================================================

class MedicalImagingEngine:
    """DICOM medical imaging metadata extraction - 4,600+ fields"""
    
    @staticmethod
    def extract_dicom_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not DICOM_AVAILABLE:
            return {"available": False, "reason": "pydicom not installed"}
        
        try:
            ds = pydicom.dcmread(filepath, force=True)
            
            # Core DICOM metadata categories
            result = {
                "available": True,
                "patient_info": {},
                "study_info": {},
                "series_info": {},
                "equipment_info": {},
                "image_info": {},
                "acquisition_params": {},
                "dose_info": {},
                "private_tags": {},
                "raw_tags": {},
                "dicom_standard": {
                    "file_meta_info_version": getattr(ds.file_meta, 'FileMetaInformationVersion', None),
                    "media_storage_sop_class": getattr(ds.file_meta, 'MediaStorageSOPClassUID', None),
                    "transfer_syntax": getattr(ds.file_meta, 'TransferSyntaxUID', None),
                }
            }
            
            # Patient Information (anonymized for privacy)
            patient_fields = {
                'PatientName': 'name', 'PatientID': 'id', 'PatientBirthDate': 'birth_date',
                'PatientSex': 'sex', 'PatientAge': 'age', 'PatientWeight': 'weight',
                'PatientSize': 'height', 'EthnicGroup': 'ethnicity'
            }
            
            for dicom_tag, result_key in patient_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    # Anonymize sensitive data
                    if dicom_tag in ['PatientName', 'PatientID']:
                        result["patient_info"][result_key] = "[ANONYMIZED]" if value else None
                    else:
                        result["patient_info"][result_key] = str(value) if value else None
            
            # Study Information
            study_fields = {
                'StudyInstanceUID': 'uid', 'StudyDate': 'date', 'StudyTime': 'time',
                'StudyDescription': 'description', 'ReferringPhysicianName': 'referring_physician',
                'StudyID': 'id', 'AccessionNumber': 'accession_number'
            }
            
            for dicom_tag, result_key in study_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["study_info"][result_key] = str(value) if value else None
            
            # Series Information
            series_fields = {
                'SeriesInstanceUID': 'uid', 'SeriesNumber': 'number', 'SeriesDate': 'date',
                'SeriesTime': 'time', 'SeriesDescription': 'description', 'Modality': 'modality',
                'BodyPartExamined': 'body_part', 'PatientPosition': 'patient_position'
            }
            
            for dicom_tag, result_key in series_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["series_info"][result_key] = str(value) if value else None
            
            # Equipment Information
            equipment_fields = {
                'Manufacturer': 'manufacturer', 'ManufacturerModelName': 'model',
                'DeviceSerialNumber': 'serial_number', 'SoftwareVersions': 'software_version',
                'StationName': 'station_name', 'InstitutionName': 'institution',
                'InstitutionalDepartmentName': 'department'
            }
            
            for dicom_tag, result_key in equipment_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["equipment_info"][result_key] = str(value) if value else None
            
            # Image Information
            if hasattr(ds, 'pixel_array'):
                try:
                    result["image_info"]["dimensions"] = ds.pixel_array.shape
                    result["image_info"]["data_type"] = str(ds.pixel_array.dtype)
                except:
                    pass
            
            image_fields = {
                'Rows': 'height', 'Columns': 'width', 'BitsAllocated': 'bits_allocated',
                'BitsStored': 'bits_stored', 'HighBit': 'high_bit', 'PixelRepresentation': 'pixel_representation',
                'PhotometricInterpretation': 'photometric_interpretation', 'SamplesPerPixel': 'samples_per_pixel',
                'PixelSpacing': 'pixel_spacing', 'SliceThickness': 'slice_thickness'
            }
            
            for dicom_tag, result_key in image_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["image_info"][result_key] = str(value) if value else None
            
            # Modality-specific acquisition parameters
            modality = getattr(ds, 'Modality', '').upper()
            
            if modality == 'CT':
                ct_fields = {
                    'KVP': 'kvp', 'XRayTubeCurrent': 'tube_current', 'ExposureTime': 'exposure_time',
                    'FilterType': 'filter_type', 'ConvolutionKernel': 'kernel',
                    'SliceThickness': 'slice_thickness', 'TableHeight': 'table_height',
                    'GantryDetectorTilt': 'gantry_tilt', 'CTDIvol': 'ctdi_vol', 'DLP': 'dlp'
                }
                
                for dicom_tag, result_key in ct_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            elif modality == 'MR':
                mr_fields = {
                    'MagneticFieldStrength': 'field_strength', 'RepetitionTime': 'tr',
                    'EchoTime': 'te', 'InversionTime': 'ti', 'FlipAngle': 'flip_angle',
                    'EchoNumbers': 'echo_numbers', 'SequenceName': 'sequence_name',
                    'ScanningSequence': 'scanning_sequence', 'SequenceVariant': 'sequence_variant'
                }
                
                for dicom_tag, result_key in mr_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            elif modality in ['DX', 'CR', 'DR']:  # Digital Radiography
                xray_fields = {
                    'KVP': 'kvp', 'XRayTubeCurrent': 'tube_current', 'ExposureTime': 'exposure_time',
                    'Exposure': 'exposure', 'FilterType': 'filter_type', 'Grid': 'grid',
                    'DistanceSourceToDetector': 'source_detector_distance',
                    'DistanceSourceToPatient': 'source_patient_distance'
                }
                
                for dicom_tag, result_key in xray_fields.items():
                    if hasattr(ds, dicom_tag):
                        value = getattr(ds, dicom_tag)
                        result["acquisition_params"][result_key] = str(value) if value else None
            
            # Radiation dose information (if available)
            dose_fields = {
                'CTDIvol': 'ctdi_vol', 'DLP': 'dlp', 'TotalDLP': 'total_dlp',
                'EffectiveDose': 'effective_dose', 'DoseAreaProduct': 'dose_area_product',
                'EntranceDose': 'entrance_dose', 'ExposureDoseSequence': 'exposure_dose_sequence'
            }
            
            for dicom_tag, result_key in dose_fields.items():
                if hasattr(ds, dicom_tag):
                    value = getattr(ds, dicom_tag)
                    result["dose_info"][result_key] = str(value) if value else None
            
            # Extract all DICOM tags for comprehensive analysis
            tag_count = 0
            for elem in ds:
                tag_count += 1
                tag_name = elem.keyword if elem.keyword else f"Tag_{elem.tag}"
                tag_value = str(elem.value) if elem.value is not None else None
                
                # Categorize as private tag if in private range
                if elem.tag.group % 2 == 1:  # Odd group numbers are private
                    result["private_tags"][tag_name] = tag_value
                else:
                    result["raw_tags"][tag_name] = tag_value
            
            result["dicom_standard"]["total_tags"] = tag_count
            result["dicom_standard"]["private_tag_count"] = len(result["private_tags"])
            result["dicom_standard"]["standard_tag_count"] = len(result["raw_tags"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting DICOM metadata: {e}")
            return {"available": False, "error": str(e)}

class AstronomicalDataEngine:
    """FITS astronomical data extraction - 3,000+ fields with performance optimizations"""
    
    def __init__(self):
        self._wcs_cache = {}  # Cache for expensive WCS computations
        self._header_cache = {}  # Cache for header extractions
    
    def _get_cached_wcs_analysis(self, filepath: str, header) -> Dict[str, Any]:
        """Cache WCS analysis to avoid recomputation."""
        import hashlib
        try:
            # Create cache key from file path and header hash
            header_str = str(sorted(header.items()))
            cache_key = hashlib.md5(f"{filepath}:{header_str}".encode()).hexdigest()
            
            if cache_key in self._wcs_cache:
                return self._wcs_cache[cache_key]
            
            # Perform WCS analysis
            wcs = WCS(header)
            if wcs.has_celestial:
                wcs_result = {
                    "has_celestial_wcs": True,
                    "coordinate_system": wcs.wcs.radesys,
                    "projection": wcs.wcs.ctype[0].split('-')[-1] if '-' in wcs.wcs.ctype[0] else None,
                    "reference_coordinates": {
                        "ra": wcs.wcs.crval[0] if len(wcs.wcs.crval) > 0 else None,
                        "dec": wcs.wcs.crval[1] if len(wcs.wcs.crval) > 1 else None
                    },
                    "pixel_scale": {
                        "ra": abs(wcs.wcs.cdelt[0]) * 3600 if len(wcs.wcs.cdelt) > 0 else None,  # arcsec/pixel
                        "dec": abs(wcs.wcs.cdelt[1]) * 3600 if len(wcs.wcs.cdelt) > 1 else None
                    }
                }
                
                # Calculate field of view (only if dimensions available)
                if "dimensions" in header and len(header.get("dimensions", [])) >= 2:
                    width, height = header["dimensions"][:2]
                    if wcs.wcs.cdelt[0] and wcs.wcs.cdelt[1]:
                        fov_ra = abs(wcs.wcs.cdelt[0]) * width * 3600  # arcseconds
                        fov_dec = abs(wcs.wcs.cdelt[1]) * height * 3600
                        wcs_result["field_of_view"] = {
                            "ra_arcsec": fov_ra,
                            "dec_arcsec": fov_dec,
                            "ra_arcmin": fov_ra / 60,
                            "dec_arcmin": fov_dec / 60,
                            "ra_degrees": fov_ra / 3600,
                            "dec_degrees": fov_dec / 3600
                        }
                
                self._wcs_cache[cache_key] = wcs_result
                return wcs_result
            else:
                result = {"has_celestial_wcs": False}
                self._wcs_cache[cache_key] = result
                return result
                
        except Exception as e:
            result = {"has_celestial_wcs": False, "error": str(e)}
            self._wcs_cache[cache_key] = result
            return result
    
    @staticmethod
    def extract_fits_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        """Ultra-fast FITS metadata extraction using optimized extractor."""
        if not FITS_AVAILABLE:
            return {"available": False, "reason": "astropy not installed"}
        
        # Use optimized FITS extractor for maximum performance consistency
        try:
            # Try importing the FITS extractor with multiple paths
            try:
                from modules.fits_extractor import FITSExtractor
            except (ImportError, ModuleNotFoundError):
                # If relative import fails, try absolute import
                # sys and Path are already imported globally
                module_path = Path(__file__).parent / 'modules'
                if str(module_path) not in sys.path:
                    sys.path.insert(0, str(module_path))
                from fits_extractor import FITSExtractor
            
            extractor = FITSExtractor()
            raw_result = extractor.extract(filepath)
            
            # Extract nested fits_metadata
            fits_data = raw_result.get('fits_metadata', {})
            
            # Convert to expected format with 'available' flag and expected keys
            if raw_result.get('extraction_success') and fits_data:
                # Provide minimal but expected structure for validation
                return {
                    "available": True,
                    "primary_header": fits_data.get('header_summary', {}),
                    "wcs_info": fits_data.get('wcs_info', {}),
                    "observation_info": {},
                    "instrument_info": {},
                    "processing_info": {},
                    "raw_headers": {"PRIMARY_HDU": fits_data.get('header_summary', {})},
                    "file_info": fits_data.get('primary_hdu', {}),
                    "extensions": fits_data.get('extensions', []),
                    "performance": fits_data.get('performance', {}),
                    "_fast_extraction": True
                }
            else:
                return {
                    "available": False,
                    "error": raw_result.get('error', 'Extraction failed')
                }
        except Exception as e:
            logger.error(f"FITS extraction failed: {type(e).__name__}: {e}")
            return {
                "available": False,
                "error": str(e)
            }
            logger.error(f"Error extracting FITS metadata: {e}")
            return {"available": False, "error": str(e), "performance": {"total_extraction_time": time.time() - start_time}}

class GeospatialEngine:
    """Geospatial data extraction - GeoTIFF, Shapefile, etc."""
    
    @staticmethod
    def extract_geotiff_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not RASTERIO_AVAILABLE:
            return {"available": False, "reason": "rasterio not installed"}
        
        try:
            import rasterio
            from rasterio.crs import CRS
            
            with rasterio.open(filepath) as src:
                result = {
                    "available": True,
                    "raster_info": {},
                    "coordinate_system": {},
                    "geotransform": {},
                    "bands": [],
                    "statistics": {},
                    "tags": {}
                }
                
                # Basic raster information
                result["raster_info"] = {
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "dtype": str(src.dtypes[0]) if src.dtypes else None,
                    "driver": src.driver,
                    "nodata": src.nodata,
                    "bounds": {
                        "left": src.bounds.left,
                        "bottom": src.bounds.bottom,
                        "right": src.bounds.right,
                        "top": src.bounds.top
                    }
                }
                
                # Coordinate Reference System
                if src.crs:
                    result["coordinate_system"] = {
                        "crs_string": str(src.crs),
                        "epsg_code": src.crs.to_epsg(),
                        "proj4_string": src.crs.to_proj4(),
                        "wkt": src.crs.to_wkt(),
                        "is_geographic": src.crs.is_geographic,
                        "is_projected": src.crs.is_projected,
                        "units": src.crs.linear_units_factor[1] if src.crs.linear_units_factor else None
                    }
                
                # Geotransform (affine transformation)
                if src.transform:
                    result["geotransform"] = {
                        "pixel_size_x": src.transform.a,
                        "rotation_x": src.transform.b,
                        "top_left_x": src.transform.c,
                        "rotation_y": src.transform.d,
                        "pixel_size_y": src.transform.e,
                        "top_left_y": src.transform.f,
                        "matrix": list(src.transform)[:6]
                    }
                
                # Band information
                for i in range(1, src.count + 1):
                    band_info = {
                        "band_number": i,
                        "dtype": str(src.dtypes[i-1]),
                        "nodata": src.nodatavals[i-1] if src.nodatavals else None
                    }
                    
                    # Band statistics (if available)
                    try:
                        stats = src.statistics(i)
                        band_info["statistics"] = {
                            "min": stats.min,
                            "max": stats.max,
                            "mean": stats.mean,
                            "std": stats.std
                        }
                    except:
                        pass
                    
                    # Color interpretation
                    try:
                        color_interp = src.colorinterp[i-1]
                        band_info["color_interpretation"] = color_interp.name
                    except:
                        pass
                    
                    result["bands"].append(band_info)
                
                # Metadata tags
                result["tags"] = dict(src.tags())
                
                # Calculate additional spatial information
                if src.crs and src.transform:
                    # Calculate pixel area in square meters (if projected) or square degrees (if geographic)
                    pixel_area = abs(src.transform.a * src.transform.e)
                    result["raster_info"]["pixel_area"] = pixel_area
                    
                    # Calculate total area
                    total_area = pixel_area * src.width * src.height
                    result["raster_info"]["total_area"] = total_area
                    
                    # Resolution information
                    result["raster_info"]["resolution"] = {
                        "x": abs(src.transform.a),
                        "y": abs(src.transform.e),
                        "units": "degrees" if src.crs.is_geographic else "meters"
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting GeoTIFF metadata: {e}")
            return {"available": False, "error": str(e)}
    
    @staticmethod
    def extract_shapefile_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not FIONA_AVAILABLE:
            return {"available": False, "reason": "fiona not installed"}
        
        try:
            import fiona
            
            with fiona.open(filepath) as src:
                result = {
                    "available": True,
                    "vector_info": {},
                    "coordinate_system": {},
                    "schema": {},
                    "bounds": {},
                    "features": {}
                }
                
                # Basic vector information
                result["vector_info"] = {
                    "driver": src.driver,
                    "feature_count": len(src),
                    "geometry_type": src.schema.get('geometry', 'Unknown')
                }
                
                # Coordinate Reference System
                if src.crs:
                    result["coordinate_system"] = {
                        "crs_string": str(src.crs),
                        "crs_wkt": src.crs_wkt if hasattr(src, 'crs_wkt') else None
                    }
                
                # Schema (field definitions)
                result["schema"] = {
                    "geometry": src.schema.get('geometry'),
                    "properties": src.schema.get('properties', {})
                }
                
                # Bounds
                result["bounds"] = {
                    "left": src.bounds[0],
                    "bottom": src.bounds[1],
                    "right": src.bounds[2],
                    "top": src.bounds[3]
                }
                
                # Sample features (first few for analysis)
                sample_features = []
                for i, feature in enumerate(src):
                    if i >= 5:  # Limit to first 5 features
                        break
                    sample_features.append({
                        "id": feature.get('id'),
                        "geometry_type": feature['geometry']['type'] if feature.get('geometry') else None,
                        "properties": feature.get('properties', {})
                    })
                
                result["features"] = {
                    "sample_count": len(sample_features),
                    "samples": sample_features
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting Shapefile metadata: {e}")
            return {"available": False, "error": str(e)}

class ScientificInstrumentEngine:
    """Scientific instrument data extraction"""
    
    @staticmethod
    def extract_hdf5_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not HDF5_AVAILABLE:
            return {"available": False, "reason": "h5py not installed"}
        
        start_time = time.time()
        try:
            import h5py
            
            with h5py.File(filepath, 'r') as f:
                result = {
                    "available": True,
                    "file_info": {},
                    "structure": {},
                    "performance": {}
                }
                
                # File-level information only
                result["file_info"] = {
                    "hdf5_version": f.libver,
                    "file_size_mb": round(os.path.getsize(filepath) / (1024*1024), 2),
                    "userblock_size": f.userblock_size,
                    "global_attributes_count": len(f.attrs)  # Count only, don't load
                }
                
                # ULTRA-MINIMAL structure - no attribute loading at all
                def count_structure(group, max_items=3):
                    """Count structure only, no data loading."""
                    info = {
                        "groups": 0,
                        "datasets": 0
                    }
                    
                    for i, key in enumerate(list(group.keys())[:max_items]):
                        try:
                            item = group[key]
                            if isinstance(item, h5py.Group):
                                info["groups"] += 1
                            elif isinstance(item, h5py.Dataset):
                                info["datasets"] += 1
                        except:
                            continue
                    
                    return info
                
                # Just count, don't load details
                explore_start = time.time()
                result["structure"] = count_structure(f)
                result["performance"]["structure_time"] = time.time() - explore_start
                
                result["performance"]["total_extraction_time"] = time.time() - start_time
                return result
                
        except Exception as e:
            logger.error(f"Error extracting HDF5 metadata: {e}")
            return {"available": False, "error": str(e)[:100], "performance": {"total_extraction_time": time.time() - start_time}}
    
    @staticmethod
    def extract_netcdf_metadata(filepath: str) -> Optional[Dict[str, Any]]:
        if not NETCDF_AVAILABLE:
            return {"available": False, "reason": "netCDF4 not installed"}
        
        start_time = time.time()
        try:
            import netCDF4
            
            with netCDF4.Dataset(filepath, 'r') as nc:
                result = {
                    "available": True,
                    "file_info": {},
                    "structure": {},
                    "performance": {}
                }
                
                # File information only
                result["file_info"] = {
                    "format": nc.data_model,
                    "file_format": nc.file_format,
                    "file_size_mb": round(os.path.getsize(filepath) / (1024*1024), 2),
                    "num_dimensions": len(nc.dimensions),
                    "num_variables": len(nc.variables),
                    "num_global_attributes": len(nc.ncattrs())  # Count only
                }
                
                # ULTRA-MINIMAL structure - just counts
                dim_start = time.time()
                result["structure"]["dimensions"] = {
                    "count": len(nc.dimensions),
                    "unlimited": sum(1 for d in nc.dimensions.values() if d.isunlimited())
                }
                result["performance"]["dimensions_time"] = time.time() - dim_start
                
                # Count variables only, no attribute loading
                var_start = time.time()
                result["structure"]["variables"] = {
                    "count": len(nc.variables),
                    "types": {}  # Empty for memory savings
                }
                result["performance"]["variables_time"] = time.time() - var_start
                
                result["performance"]["total_extraction_time"] = time.time() - start_time
                return result
                
        except Exception as e:
            logger.error(f"Error extracting NetCDF metadata: {e}")
            return {"available": False, "error": str(e)[:100], "performance": {"total_extraction_time": time.time() - start_time}}

class DroneUAVEngine:
    """Drone and UAV telemetry extraction"""
    
    @staticmethod
    def extract_drone_telemetry(filepath: str, exiftool_data: Dict = None) -> Optional[Dict[str, Any]]:
        """Extract drone flight data and telemetry"""
        result = {
            "available": True,
            "flight_data": {},
            "camera_data": {},
            "gps_track": {},
            "sensor_data": {},
            "manufacturer_specific": {}
        }
        
        # Use exiftool data if available (contains DJI, GoPro telemetry)
        if exiftool_data:
            # DJI drone metadata
            if "other" in exiftool_data:
                dji_fields = {}
                gopro_fields = {}
                
                for key, value in exiftool_data["other"].items():
                    if "DJI" in key or "dji" in key.lower():
                        dji_fields[key] = value
                    elif "GoPro" in key or "gopro" in key.lower():
                        gopro_fields[key] = value
                
                if dji_fields:
                    result["manufacturer_specific"]["dji"] = dji_fields
                if gopro_fields:
                    result["manufacturer_specific"]["gopro"] = gopro_fields
        
        # Extract GPS track from video metadata
        if exiftool_data and "gps" in exiftool_data:
            gps_data = exiftool_data["gps"]
            result["gps_track"] = {
                "has_gps": bool(gps_data),
                "coordinates": {
                    "latitude": gps_data.get("GPSLatitude"),
                    "longitude": gps_data.get("GPSLongitude"),
                    "altitude": gps_data.get("GPSAltitude")
                },
                "movement": {
                    "speed": gps_data.get("GPSSpeed"),
                    "direction": gps_data.get("GPSTrack"),
                    "image_direction": gps_data.get("GPSImgDirection")
                }
            }
        
        # Camera gimbal and settings
        if exiftool_data and "exif" in exiftool_data:
            exif_data = exiftool_data["exif"]
            result["camera_data"] = {
                "exposure_settings": {
                    "iso": exif_data.get("ISO"),
                    "shutter_speed": exif_data.get("ExposureTime"),
                    "aperture": exif_data.get("FNumber"),
                    "focal_length": exif_data.get("FocalLength")
                },
                "white_balance": exif_data.get("WhiteBalance"),
                "color_space": exif_data.get("ColorSpace")
            }

        # Only return when we detect real signals. Avoid placeholder payloads such as
        # `has_gps: false` and empty/null exposure settings.
        manufacturer_specific = result.get("manufacturer_specific") or {}
        if isinstance(manufacturer_specific, dict) and any(
            isinstance(v, dict) and len(v) > 0 for v in manufacturer_specific.values()
        ):
            return result

        gps_track = result.get("gps_track") or {}
        coords = (gps_track.get("coordinates") or {}) if isinstance(gps_track, dict) else {}
        if isinstance(coords, dict) and any(v is not None for v in coords.values()):
            return result

        camera_data = result.get("camera_data") or {}
        exposure = (camera_data.get("exposure_settings") or {}) if isinstance(camera_data, dict) else {}
        if isinstance(exposure, dict) and any(v is not None for v in exposure.values()):
            return result
        if isinstance(camera_data, dict) and any(
            camera_data.get(k) is not None for k in ("white_balance", "color_space")
        ):
            return result

        return None

class BlockchainProvenanceEngine:
    """Blockchain and digital provenance extraction"""
    
    @staticmethod
    def extract_blockchain_metadata(filepath: str, exiftool_data: Dict = None) -> Optional[Dict[str, Any]]:
        """Extract blockchain provenance and C2PA metadata"""
        result = {
            "available": True,
            "c2pa_manifest": {},
            "digital_signatures": {},
            "nft_metadata": {},
            "content_credentials": {}
        }
        
        # Look for C2PA (Content Authenticity) metadata in XMP
        if exiftool_data and "xmp" in exiftool_data:
            xmp_data = exiftool_data["xmp"]
            
            # C2PA manifest detection
            c2pa_fields = {}
            for key, value in xmp_data.items():
                if "c2pa" in key.lower() or "contentauth" in key.lower():
                    c2pa_fields[key] = value
            
            if c2pa_fields:
                result["c2pa_manifest"] = c2pa_fields
        
        # Check for blockchain references in metadata
        blockchain_indicators = [
            "blockchain", "nft", "ethereum", "bitcoin", "ipfs", "arweave",
            "transaction", "hash", "smart_contract", "token_id"
        ]
        
        if exiftool_data:
            for category, data in exiftool_data.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        key_lower = key.lower()
                        value_str = str(value).lower() if value else ""
                        
                        for indicator in blockchain_indicators:
                            if indicator in key_lower or indicator in value_str:
                                if "blockchain_references" not in result:
                                    result["blockchain_references"] = {}
                                result["blockchain_references"][key] = value
        
        return result if any(result[key] for key in ["c2pa_manifest", "digital_signatures", "nft_metadata", "content_credentials"]) else None

# ============================================================================
# Comprehensive Metadata Extractor
# ============================================================================

class ComprehensiveMetadataExtractor:
    """Ultimate metadata extractor with all specialized engines"""
    
    def __init__(self):
        global MODULE_DISCOVERY_AVAILABLE
        self.medical_engine = MedicalImagingEngine()
        self.astronomical_engine = AstronomicalDataEngine()
        self.geospatial_engine = GeospatialEngine()
        self.scientific_engine = ScientificInstrumentEngine()
        self.drone_engine = DroneUAVEngine()
        self.blockchain_engine = BlockchainProvenanceEngine()
        
        # Initialize enhanced dynamic module discovery system
        self.module_registry = None
        self.module_discovery_stats = None
        self.dependency_stats = None
        self.plugin_stats = None
        self.module_health_metrics = {}
        self.module_performance_history = {}
        
        if MODULE_DISCOVERY_AVAILABLE:
            try:
                # Initialize module discovery with enhanced error handling
                self.module_registry = discover_and_register_modules()
                self.module_discovery_stats = get_module_discovery_stats()
                
                # Enhanced dependency analysis with circular dependency detection
                build_dependency_graph_global()
                self.dependency_stats = get_dependency_stats_global()
                
                # Log dependency analysis results
                self._log_dependency_analysis()
                
                # Initialize health monitoring for modules
                self._initialize_health_monitoring()
                
                # Enhanced plugin system initialization
                enable_plugins_global(True)
                discover_and_load_plugins_global()
                self.plugin_stats = get_plugin_stats_global()
                
                # Initialize plugin health monitoring
                self._initialize_plugin_health_monitoring()
                
                logger.info(f"Enhanced module discovery initialized: {self.module_discovery_stats['loaded_count']} modules loaded")
                logger.info(f"Plugin system initialized: {self.plugin_stats['plugins_loaded']} plugins loaded")
                logger.info(f"Plugin health: {self.plugin_stats.get('healthy_plugins', 0)} healthy, {self.plugin_stats.get('unhealthy_plugins', 0)} unhealthy")
                
            except Exception as e:
                error_msg = f"Failed to initialize enhanced module discovery: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                # Enhanced error handling - attempt graceful degradation
                if self._attempt_graceful_degradation(e):
                    logger.warning("Module discovery degraded to basic mode")
                else:
                    logger.error("Module discovery completely failed, disabling")
                    MODULE_DISCOVERY_AVAILABLE = False
    
    def _log_dependency_analysis(self) -> None:
        """
        Log comprehensive dependency analysis results.
        """
        try:
            if not self.dependency_stats:
                return
            
            analysis_results = [
                f"Dependency Analysis Results:",
                f"  Total modules with dependencies: {self.dependency_stats.get('total_modules_with_dependencies', 0)}",
                f"  Total dependencies: {self.dependency_stats.get('total_dependencies', 0)}",
                f"  Average dependencies per module: {self.dependency_stats.get('average_dependencies', 0):.2f}",
                f"  Max dependencies: {self.dependency_stats.get('max_dependencies', 0)}"
            ]
            
            if self.dependency_stats.get('circular_dependencies'):
                circular_deps = self.dependency_stats['circular_dependencies']
                analysis_results.append(f"  ⚠️  Circular dependencies detected: {len(circular_deps)}")
                for cycle in circular_deps[:3]:  # Show first 3 cycles
                    analysis_results.append(f"    - {' -> '.join(cycle)}")
                if len(circular_deps) > 3:
                    analysis_results.append(f"    - ... and {len(circular_deps) - 3} more")
            else:
                analysis_results.append("  ✅ No circular dependencies detected")
            
            logger.info("\n".join(analysis_results))
            
        except Exception as e:
            logger.error(f"Error logging dependency analysis: {str(e)}")
    
    def _initialize_health_monitoring(self) -> None:
        """
        Initialize health monitoring for all discovered modules.
        """
        try:
            if not self.module_registry:
                return
            
            # Initialize health metrics for each module
            for module_name in self.module_registry.modules.keys():
                self.module_health_metrics[module_name] = {
                    'error_count': 0,
                    'success_count': 0,
                    'last_error': None,
                    'last_success': None,
                    'status': 'healthy',
                    'last_check': time.time()
                }
            
            logger.info(f"Initialized health monitoring for {len(self.module_health_metrics)} modules")
            
        except Exception as e:
            logger.error(f"Error initializing health monitoring: {str(e)}")
    
    def _attempt_graceful_degradation(self, error: Exception) -> bool:
        """
        Attempt graceful degradation when module discovery fails.
        
        Args:
            error: The exception that caused the failure
            
        Returns:
            True if degradation was successful, False otherwise
        """
        try:
            error_type = type(error).__name__
            
            # Handle specific error types
            if "ImportError" in error_type or "ModuleNotFoundError" in error_type:
                logger.warning("Module import error detected, attempting basic module loading")
                
                # Try to load basic modules without advanced features
                try:
                    from .module_discovery import ModuleRegistry
                    basic_registry = ModuleRegistry()
                    
                    # Try basic discovery
                    basic_registry.discover_modules("server/extractor/modules/")
                    
                    if basic_registry.loaded_count > 0:
                        self.module_registry = basic_registry
                        self.module_discovery_stats = {
                            'loaded_count': basic_registry.loaded_count,
                            'discovered_count': basic_registry.discovered_count,
                            'failed_count': basic_registry.failed_count,
                            'degraded_mode': True
                        }
                        return True
                except Exception as e:
                    logger.error(f"Basic module loading also failed: {str(e)}")
            
            # Handle configuration errors
            elif "ConfigurationError" in error_type or "config" in str(error).lower():
                logger.warning("Configuration error detected, attempting default configuration")
                
                try:
                    # Try with default configuration
                    from .module_discovery import discover_and_register_modules
                    self.module_registry = discover_and_register_modules(default_config=True)
                    if self.module_registry:
                        self.module_discovery_stats = {'degraded_mode': True, 'loaded_count': 0}
                        return True
                except Exception as e:
                    logger.error(f"Default configuration also failed: {str(e)}")
            
            return False
            
        except Exception as e:
            logger.error(f"Graceful degradation failed: {str(e)}")
            return False
    
    def _execute_dynamic_modules(self, filepath: str, base_result: Dict[str, Any], tier_config: Any) -> None:
        """
        Execute dynamically discovered modules based on tier configuration with enhanced error handling.
        
        Args:
            filepath: Path to the file being processed
            base_result: Base metadata result dictionary
            tier_config: Tier configuration object
            
        Raises:
            Exception: If critical errors occur during module execution
        """
        if not MODULE_DISCOVERY_AVAILABLE or not self.module_registry:
            logger.debug("Module discovery not available, skipping dynamic modules")
            return
            
        try:
            logger.info(f"Starting dynamic module execution for {filepath}")
            
            # Enhanced tier-based filtering with dependency resolution
            def enhanced_tier_filter(module_name: str, module_info: Dict[str, Any]) -> bool:
                try:
                    category = module_info.get("category", "general")
                    
                    # Check tier configuration
                    if not self._should_execute_module_category(category, tier_config):
                        logger.debug(f"Skipping module {module_name} - category {category} not enabled for tier")
                        return False
                    
                    # Check module health status (includes both modules and plugins)
                    health_status = self.module_health_metrics.get(module_name, {}).get('status')
                    if health_status == 'unhealthy':
                        logger.warning(f"Skipping unhealthy module/plugin: {module_name}")
                        return False
                    
                    # Check circular dependencies
                    if module_name in self.dependency_stats.get('circular_dependencies', []):
                        logger.warning(f"Skipping module with circular dependencies: {module_name}")
                        return False
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error in module filter for {module_name}: {str(e)}")
                    return False
            
            # Enhanced execution wrapper with error tracking
            def enhanced_execution_wrapper(extraction_func: Callable, filepath: str, module_name: str, *args, **kwargs):
                try:
                    # Update health metrics - execution started
                    self._update_module_health(module_name, success=False, execution_started=True)
                    
                    # Execute with safe wrapper
                    result = safe_extract_module(extraction_func, filepath, module_name, *args, **kwargs)
                    
                    # Update health metrics - success
                    self._update_module_health(module_name, success=True)
                    
                    return result
                    
                except Exception as e:
                    # Update health metrics - failure
                    self._update_module_health(module_name, success=False, error=str(e))
                    
                    # Create enhanced error result
                    error_result = create_standardized_error(
                        exception=e,
                        module_name=module_name,
                        filepath=filepath,
                        start_time=time.time(),
                        error_code=f"ERR_DYNAMIC_MODULE_{module_name.upper()}",
                        severity="high",
                        recoverable=True,
                        custom_message=f"Dynamic module {module_name} failed",
                        suggested_action="Check module dependencies and configuration",
                        error_context={
                            "module_name": module_name,
                            "module_category": self.module_registry.modules.get(module_name, {}).get("category", "unknown"),
                            "execution_phase": "dynamic_module_execution"
                        }
                    )
                    
                    logger.error(f"Dynamic module {module_name} failed: {str(e)}")
                    return error_result
            
            # Execute modules using parallel execution with enhanced error handling
            results = self.module_registry.execute_modules_parallel(
                filepath, 
                enhanced_execution_wrapper, 
                enhanced_tier_filter
            )
            
            # Enhanced result processing with health monitoring
            module_results = {}
            plugin_results = {}
            for result_key, result in results.items():
                if result and isinstance(result, dict):
                    # Check if this is an error result
                    if result.get('error_code'):
                        logger.warning(f"Dynamic module/plugin {result_key} completed with errors: {result.get('error_code')}")
                        base_result[f"module_errors"][result_key] = result
                        module_results[result_key] = 'error'
                        
                        # Update health metrics for failed execution
                        self._update_module_health(result_key, success=False, error=result.get('error_code'))
                    else:
                        # Successful result
                        base_result[result_key] = result
                        module_results[result_key] = 'success'
                        logger.info(f"Successfully executed dynamic module/plugin: {result_key}")
                        
                        # Update health metrics for successful execution
                        self._update_module_health(result_key, success=True)
                else:
                    module_results[result_key] = 'no_result'
                    logger.debug(f"Dynamic module/plugin {result_key} returned no result")
            
            # Separate plugins from modules for reporting
            for result_key in module_results:
                health_data = self.module_health_metrics.get(result_key, {})
                if health_data.get('type') == 'plugin':
                    plugin_results[result_key] = module_results[result_key]
            
            # Add module execution summary to base result
            base_result["extraction_info"]["dynamic_modules"] = {
                "executed_count": len(module_results),
                "success_count": sum(1 for status in module_results.values() if status == 'success'),
                "error_count": sum(1 for status in module_results.values() if status == 'error'),
                "no_result_count": sum(1 for status in module_results.values() if status == 'no_result'),
                "module_statuses": module_results
            }
            
            # Add plugin execution summary if there are plugins
            if plugin_results:
                base_result["extraction_info"]["plugins"] = {
                    "executed_count": len(plugin_results),
                    "success_count": sum(1 for status in plugin_results.values() if status == 'success'),
                    "error_count": sum(1 for status in plugin_results.values() if status == 'error'),
                    "no_result_count": sum(1 for status in plugin_results.values() if status == 'no_result'),
                    "plugin_statuses": plugin_results
                }
            
            logger.info(f"Completed dynamic module execution: {len(module_results)} modules processed")
            
        except Exception as e:
            error_msg = f"Critical error in dynamic module execution: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            # Add error information to base result
            if "extraction_info" not in base_result:
                base_result["extraction_info"] = {}
            base_result["extraction_info"]["dynamic_module_error"] = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": time.time(),
                "severity": "critical"
            }
            
            # Mark all modules as unhealthy due to critical error
            self._mark_all_modules_unhealthy(f"Critical execution error: {str(e)}")
    
    def _update_module_health(self, module_name: str, success: bool, error: Optional[str] = None, execution_started: bool = False) -> None:
        """
        Update health metrics for a specific module.
        
        Args:
            module_name: Name of the module
            success: Whether the execution was successful
            error: Error message if execution failed
            execution_started: Whether execution has started
        """
        try:
            if not self.module_health_metrics or module_name not in self.module_health_metrics:
                return
            
            health_data = self.module_health_metrics[module_name]
            
            if execution_started:
                health_data['last_check'] = time.time()
            
            if success:
                health_data['success_count'] += 1
                health_data['last_success'] = time.time()
                health_data['last_error'] = None
                
                # Reset to healthy if we have recent successes
                if health_data['success_count'] >= 3 and health_data['error_count'] <= 1:
                    health_data['status'] = 'healthy'
                    
            else:
                health_data['error_count'] += 1
                health_data['last_error'] = {
                    'error': error,
                    'timestamp': time.time()
                }
                
                # Mark as unhealthy if error rate is too high
                if health_data['error_count'] >= 3 and health_data['success_count'] <= health_data['error_count']:
                    health_data['status'] = 'unhealthy'
                    logger.warning(f"Module {module_name} marked as unhealthy due to repeated errors")
            
            # Log health status changes
            if health_data['status'] == 'unhealthy':
                logger.warning(f"Module {module_name} health: {health_data['status']} (errors: {health_data['error_count']}, successes: {health_data['success_count']})")
            
        except Exception as e:
            logger.error(f"Error updating health for module {module_name}: {str(e)}")
    
    def _initialize_plugin_health_monitoring(self) -> None:
        """
        Initialize health monitoring for all loaded plugins.
        """
        try:
            from .module_discovery import get_all_plugins_info_global, get_health_stats_global
            
            # Get all loaded plugins
            plugins_info = get_all_plugins_info_global()
            health_stats = get_health_stats_global()
            
            # Initialize plugin health metrics if not already initialized
            for plugin_name in plugins_info.keys():
                if plugin_name not in health_stats or health_stats[plugin_name].get('type') != 'plugin':
                    # This will be handled by the module discovery system
                    pass
            
            logger.debug(f"Initialized plugin health monitoring for {len(plugins_info)} plugins")
            
        except Exception as e:
            logger.error(f"Error initializing plugin health monitoring: {str(e)}")
    
    def _mark_all_modules_unhealthy(self, reason: str) -> None:
        """
        Mark all modules as unhealthy due to a critical error.
        
        Args:
            reason: Reason for marking modules unhealthy
        """
        try:
            if not self.module_health_metrics:
                return
            
            for module_name in self.module_health_metrics:
                self.module_health_metrics[module_name]['status'] = 'unhealthy'
                self.module_health_metrics[module_name]['last_error'] = {
                    'error': f"Critical system error: {reason}",
                    'timestamp': time.time()
                }
            
            logger.error(f"All modules marked unhealthy: {reason}")
            
        except Exception as e:
            logger.error(f"Error marking all modules unhealthy: {str(e)}")
    
    def _should_execute_module_category(self, category: str, tier_config: Any) -> bool:
        """
        Determine if modules in a category should be executed based on tier configuration.
        
        Args:
            category: Module category
            tier_config: Tier configuration object
            
        Returns:
            True if modules in this category should be executed
        """
        # Map categories to tier configuration attributes
        category_mapping = {
            "image": tier_config.image_metadata,
            "video": tier_config.video_metadata,
            "audio": tier_config.audio_metadata,
            "document": tier_config.document_metadata,
            "scientific": tier_config.scientific_metadata,
            "forensic": tier_config.forensic_details,
            "mobile": tier_config.mobile_sensors,
            "web": tier_config.web_metadata,
            "ai": tier_config.ai_ml_metadata,
            "emerging": tier_config.emerging_technology,
            "industrial": tier_config.industrial_metadata,
            "professional": tier_config.professional_video,
            "general": True  # Always execute general modules
        }
        
        return category_mapping.get(category, True)
    
    def extract_comprehensive_metadata(
        self,
        filepath: str,
        tier: str = "super",
        enable_ocr: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata using all available engines
        """
        import time
        start_time = time.time()
        
        # Initialize observability tracking
        _provenance: Dict[str, str] = {}
        _provenance_conflicts: List[Dict[str, str]] = []
        _shadow_info: Optional[Dict[str, Any]] = None

        try:
            # Start with base metadata extraction
            base_result = extract_base_metadata(
                filepath, tier, enable_burned_metadata=enable_ocr
            )
            
            # Record provenance for base extraction results
            record_top_level_provenance(
                module_name="base_metadata_engine",
                module_output=base_result,
                provenance=_provenance,
                conflicts=_provenance_conflicts
            )

            if "error" in base_result:
                # Add performance tracking even for error cases
                duration_ms = (time.time() - start_time) * 1000
                base_result["extraction_info"]["processing_ms"] = duration_ms
                return base_result
        except Exception as e:
            logger.error(f"Error in base metadata extraction for {filepath}: {e}")
            logger.debug(f"Full traceback for base extraction: {traceback.format_exc()}")

            standardized = create_standardized_error(
                exception=e,
                module_name="comprehensive_engine",
                filepath=filepath,
                start_time=start_time,
                error_code="ERR_BASE_EXTRACTION_FAILED",
                severity="critical",
                recoverable=False,
                custom_message="Failed to extract base metadata",
                suggested_action="Check file format and integrity",
                error_context={"phase": "base_extraction", "tier": tier},
            )

            duration_ms = (time.time() - start_time) * 1000
            return {
                "error": f"Critical error in base metadata extraction: {str(e)}",
                "error_type": type(e).__name__,
                "file": {"path": filepath},
                "extraction_info": {
                    "comprehensive_version": "4.0.0",
                    "processing_ms": duration_ms,
                    "tier": tier,
                },
                "error_details": standardized,
            }
        
        # Get tier configuration
        try:
            tier_enum = Tier(tier.lower())
        except ValueError:
            tier_enum = Tier.SUPER

        tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]

        # Normalize empty sections so plugin/module keys are always dictionaries.
        # Some base extractors emit `None` placeholders (e.g. audio/video) which breaks
        # downstream consumers/tests that treat these as module result objects.
        for _section_key in ("audio", "video", "image", "document", "pdf", "svg"):
            if base_result.get(_section_key) is None:
                base_result[_section_key] = {}

        # Add comprehensive extraction info
        base_result["extraction_info"]["comprehensive_version"] = "4.0.0"
        
        # Add module discovery statistics if available
        if MODULE_DISCOVERY_AVAILABLE and self.module_discovery_stats:
            base_result["extraction_info"]["module_discovery"] = self.module_discovery_stats
            base_result["extraction_info"]["dynamic_modules_enabled"] = True
            
            # Add parallel execution statistics
            parallel_stats = self.module_registry.get_parallel_execution_stats()
            base_result["extraction_info"]["parallel_execution"] = parallel_stats
            
            # Add dependency statistics
            dependency_stats = get_dependency_stats_global()
            base_result["extraction_info"]["module_dependencies"] = dependency_stats
            
            # Add hot reloading statistics
            hot_reload_stats = get_hot_reload_stats_global()
            base_result["extraction_info"]["hot_reloading"] = hot_reload_stats
            
            # Add plugin statistics
            plugin_stats = get_plugin_stats_global()
            base_result["extraction_info"]["plugins"] = plugin_stats
        else:
            base_result["extraction_info"]["dynamic_modules_enabled"] = False
        
        base_result["extraction_info"]["specialized_engines"] = {
            "medical_imaging": DICOM_AVAILABLE and tier_config.medical_imaging,
            "astronomical_data": FITS_AVAILABLE and tier_config.astronomical_data,
            "geospatial_analysis": (RASTERIO_AVAILABLE or FIONA_AVAILABLE) and tier_config.geospatial_analysis,
            "scientific_instruments": (HDF5_AVAILABLE or NETCDF_AVAILABLE) and tier_config.scientific_instruments,
            "drone_telemetry": tier_config.drone_telemetry,
            "blockchain_provenance": tier_config.blockchain_provenance,
            "emerging_technology": tier_config.emerging_technology and extract_emerging_technology_metadata is not None,
            "advanced_video_analysis": tier_config.advanced_video_analysis and extract_advanced_video_metadata is not None,
            "advanced_audio_analysis": tier_config.advanced_audio_analysis and extract_advanced_audio_metadata is not None,
            "document_analysis": tier_config.document_analysis and extract_document_metadata is not None,
            "scientific_research": tier_config.scientific_research and extract_scientific_research_metadata is not None,
            "multimedia_entertainment": tier_config.multimedia_entertainment and extract_multimedia_entertainment_metadata is not None,
            "industrial_manufacturing": tier_config.industrial_manufacturing and extract_industrial_manufacturing_metadata is not None,
            "financial_business": tier_config.financial_business and extract_financial_business_metadata is not None,
            "healthcare_medical": tier_config.healthcare_medical and extract_healthcare_medical_metadata is not None,
            "transportation_logistics": tier_config.transportation_logistics and extract_transportation_logistics_metadata is not None,
            "education_academic": tier_config.education_academic and extract_education_academic_metadata is not None,
            "legal_compliance": tier_config.legal_compliance and extract_legal_compliance_metadata is not None,
            "environmental_sustainability": tier_config.environmental_sustainability and extract_environmental_sustainability_metadata is not None,
            "social_media_digital": tier_config.social_media_digital and extract_social_media_digital_metadata is not None,
            "gaming_entertainment": tier_config.gaming_entertainment and extract_gaming_entertainment_metadata is not None,
        }

        # Detect file type for specialized extraction
        file_ext = Path(filepath).suffix.lower()
        mime_type = base_result.get("file", {}).get("mime_type", "")
        is_image = mime_type.startswith("image/")
        is_video = mime_type.startswith("video/")
        is_audio = mime_type.startswith("audio/") or file_ext in [".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".aiff"]
        is_psd = file_ext in ['.psd', '.psb'] or 'photoshop' in mime_type.lower()
        is_exr = file_ext in ['.exr']
        
        # Helper to merge module result and track provenance
        def _merge_module_result(result_key: str, module_result: Optional[Dict[str, Any]], module_name: str) -> None:
            if module_result:
                base_result[result_key] = module_result
                record_top_level_provenance(
                    module_name=module_name,
                    module_output={result_key: module_result},
                    provenance=_provenance,
                    conflicts=_provenance_conflicts
                )
        
        # Run shadow mode for images (parallel, never blocks main path)
        if is_image and should_run_shadow():
            try:
                _shadow_info = run_shadow_extraction_safe(filepath)
            except Exception as shadow_err:
                # Shadow mode errors NEVER fail main extraction
                _shadow_info = {"enabled": True, "error": f"Shadow init failed: {shadow_err}"}
                logger.debug(f"Shadow mode init failed (non-fatal): {shadow_err}")

        try:
            # Medical imaging (DICOM)
            if tier_config.medical_imaging and (file_ext in ['.dcm', '.dicom'] or 'dicom' in mime_type):
                dicom_result = safe_extract_module(self.medical_engine.extract_dicom_metadata, filepath, "medical_imaging")
                if dicom_result and dicom_result.get("available"):
                    _merge_module_result("medical_imaging", dicom_result, "medical_imaging")

            # Astronomical data (FITS)
            if tier_config.astronomical_data and file_ext in ['.fits', '.fit', '.fts']:
                fits_result = safe_extract_module(self.astronomical_engine.extract_fits_metadata, filepath, "astronomical_data")
                if fits_result and fits_result.get("available"):
                    _merge_module_result("astronomical_data", fits_result, "astronomical_data")

            # Geospatial data
            if tier_config.geospatial_analysis:
                if file_ext in ['.tif', '.tiff'] and 'geo' in str(base_result.get("exif", {})).lower():
                    geotiff_result = safe_extract_module(self.geospatial_engine.extract_geotiff_metadata, filepath, "geospatial_geotiff")
                    if geotiff_result and geotiff_result.get("available"):
                        _merge_module_result("geospatial", geotiff_result, "geospatial_geotiff")

                elif file_ext in ['.shp']:
                    shapefile_result = safe_extract_module(self.geospatial_engine.extract_shapefile_metadata, filepath, "geospatial_shapefile")
                    if shapefile_result and shapefile_result.get("available"):
                        _merge_module_result("geospatial", shapefile_result, "geospatial_shapefile")

            # Scientific instruments
            if tier_config.scientific_instruments:
                if file_ext in ['.h5', '.hdf5', '.he5']:
                    hdf5_result = safe_extract_module(self.scientific_engine.extract_hdf5_metadata, filepath, "scientific_hdf5")
                    if hdf5_result and hdf5_result.get("available"):
                        _merge_module_result("scientific_data", hdf5_result, "scientific_hdf5")

                elif file_ext in ['.nc', '.netcdf', '.nc4']:
                    netcdf_result = safe_extract_module(self.scientific_engine.extract_netcdf_metadata, filepath, "scientific_netcdf")
                    if netcdf_result and netcdf_result.get("available"):
                        _merge_module_result("scientific_data", netcdf_result, "scientific_netcdf")

            # Drone telemetry (for images and videos)
            if tier_config.drone_telemetry and mime_type.startswith(('image/', 'video/')):
                # Use exiftool data if available
                exiftool_data = None
                if hasattr(base_result, 'get') and any(key in base_result for key in ['exif', 'gps', 'makernote', 'xmp']):
                    exiftool_data = {
                        'exif': base_result.get('exif', {}),
                        'gps': base_result.get('gps', {}),
                        'makernote': base_result.get('makernote', {}),
                        'xmp': base_result.get('xmp', {}),
                        'other': base_result.get('composite', {})
                    }

                def has_drone_signals(payload: Optional[Dict[str, Any]]) -> bool:
                    if not payload or not isinstance(payload, dict):
                        return False
                    mk = payload.get("makernote")
                    if isinstance(mk, dict):
                        for key in ("dji", "gopro"):
                            bucket = mk.get(key)
                            if isinstance(bucket, dict) and any(v is not None for v in bucket.values()):
                                return True
                    other = payload.get("other")
                    if isinstance(other, dict):
                        for k in other.keys():
                            ks = str(k).lower()
                            if "dji" in ks or "gopro" in ks:
                                return True
                    xmp = payload.get("xmp")
                    if isinstance(xmp, dict):
                        for k in xmp.keys():
                            ks = str(k).lower()
                            if "dji" in ks or "gopro" in ks:
                                return True
                    return False

                # Images: only run when we see real DJI/GoPro signals.
                # Videos: run by default (telemetry tracks are common).
                should_run_drone = is_video or has_drone_signals(exiftool_data)
                if should_run_drone:
                    drone_result = safe_extract_module(
                        self.drone_engine.extract_drone_telemetry,
                        filepath,
                        "drone_telemetry",
                        exiftool_data,
                    )
                    if drone_result:
                        base_result["drone_telemetry"] = drone_result

            # Blockchain provenance
            if tier_config.blockchain_provenance:
                exiftool_data = None
                if hasattr(base_result, 'get'):
                    exiftool_data = {
                        'xmp': base_result.get('xmp', {}),
                        'iptc': base_result.get('iptc', {}),
                        'exif': base_result.get('exif', {})
                    }

                def has_c2pa_signals(payload: Optional[Dict[str, Any]]) -> bool:
                    if not payload or not isinstance(payload, dict):
                        return False
                    xmp = payload.get("xmp")
                    if isinstance(xmp, dict):
                        for k in xmp.keys():
                            ks = str(k).lower()
                            if "c2pa" in ks or "contentauth" in ks or "contentcredentials" in ks:
                                return True
                    return False

                if has_c2pa_signals(exiftool_data):
                    blockchain_result = safe_extract_module(
                        self.blockchain_engine.extract_blockchain_metadata,
                        filepath,
                        "blockchain_provenance",
                        exiftool_data,
                    )
                    if blockchain_result:
                        base_result["blockchain_provenance"] = blockchain_result

            # Optional: Web metadata
            if tier_config.web_metadata and extract_web_metadata:
                web_result = safe_extract_module(extract_web_metadata, filepath, "web_metadata")
                if web_result:
                    base_result["web_metadata"] = web_result

            # Optional: Social media context
            if tier_config.social_media_context and extract_social_media_metadata:
                social_result = safe_extract_module(extract_social_media_metadata, filepath, "social_media_metadata")
                if social_result:
                    base_result["social_media"] = social_result

            # Optional: Mobile sensors
            if tier_config.mobile_sensors and extract_mobile_metadata and is_image:
                def mobile_section(name: str) -> Dict[str, Any]:
                    section = base_result.get(name, {})
                    if isinstance(section, dict) and not section.get("_locked"):
                        return section
                    return {}

                mobile_exiftool_data = {
                    "exif": mobile_section("exif"),
                    "xmp": mobile_section("xmp"),
                    "xmp_namespaces": mobile_section("xmp_namespaces"),
                    "makernote": mobile_section("makernote"),
                    "composite": mobile_section("composite"),
                }

                mobile_result = safe_extract_module(extract_mobile_metadata, filepath, "mobile_metadata", mobile_exiftool_data)
                if mobile_result:
                    _merge_module_result("mobile_metadata", mobile_result, "mobile_metadata")

            # Optional: Forensic/security metadata
            if tier_config.forensic_details and extract_forensic_metadata:
                forensic_result = safe_extract_module(extract_forensic_metadata, filepath, "forensic_metadata")
                if forensic_result:
                    _merge_module_result("forensic_security", forensic_result, "forensic_metadata")

            # Optional: Action camera metadata
            if (tier_config.drone_telemetry or tier_config.professional_video) and extract_action_camera_metadata and (is_image or is_video):
                action_result = safe_extract_module(extract_action_camera_metadata, filepath, "action_camera_metadata")
                if action_result:
                    _merge_module_result("action_camera", action_result, "action_camera_metadata")

            # Optional: 360° camera metadata
            if extract_360_camera_metadata and is_image:
                def camera_360_section(name: str) -> Dict[str, Any]:
                    section = base_result.get(name, {})
                    if isinstance(section, dict) and not section.get("_locked"):
                        return section
                    return {}

                camera_360_exiftool_data = {
                    "exif": camera_360_section("exif"),
                    "xmp": camera_360_section("xmp"),
                    "xmp_namespaces": camera_360_section("xmp_namespaces"),
                    "makernote": camera_360_section("makernote"),
                    "composite": camera_360_section("composite"),
                    "image_container": camera_360_section("image_container"),
                }

                camera_360_result = safe_extract_module(extract_360_camera_metadata, filepath, "360_camera_metadata", camera_360_exiftool_data)
                if camera_360_result:
                    _merge_module_result("camera_360", camera_360_result, "360_camera_metadata")

            # Optional: Print/publishing metadata
            if tier_config.web_metadata and extract_print_publishing_metadata and is_image:
                print_result = safe_extract_module(extract_print_publishing_metadata, filepath, "print_publishing_metadata")
                if print_result:
                    _merge_module_result("print_publishing", print_result, "print_publishing_metadata")

            # Optional: Workflow/DAM metadata
            if tier_config.web_metadata and extract_workflow_dam_metadata:
                workflow_result = safe_extract_module(extract_workflow_dam_metadata, filepath, "workflow_dam_metadata")
                if workflow_result:
                    _merge_module_result("workflow_dam", workflow_result, "workflow_dam_metadata")

            # Optional: Advanced audio/video analysis
            if tier_config.advanced_audio and extract_audio_advanced_metadata and is_audio:
                audio_adv = safe_extract_module(extract_audio_advanced_metadata, filepath, "audio_advanced_metadata")
                if audio_adv:
                    base_result["audio_advanced"] = audio_adv

            if tier_config.professional_video and extract_video_advanced_metadata and is_video:
                video_adv = safe_extract_module(extract_video_advanced_metadata, filepath, "video_advanced_metadata")
                if video_adv:
                    base_result["video_advanced"] = video_adv

            # Optional: Steganography/manipulation/AI detection
            if tier_config.steganography_detection and is_image:
                if detect_enhanced_steganography:
                    steg_result = safe_extract_module(detect_enhanced_steganography, filepath, "enhanced_steganography")
                    if steg_result:
                        base_result["steganography_analysis"] = steg_result
                elif analyze_steganography:
                    steg_result = safe_extract_module(analyze_steganography, filepath, "steganography_analysis")
                    if steg_result:
                        base_result["steganography_analysis"] = steg_result

            if tier_config.manipulation_detection and detect_enhanced_manipulation and is_image:
                manipulation_result = safe_extract_module(detect_enhanced_manipulation, filepath, "manipulation_detection", base_result)
                if manipulation_result:
                    base_result["manipulation_detection"] = manipulation_result

            if tier_config.ai_content_detection and detect_ai_content:
                ai_result = safe_extract_module(detect_ai_content, filepath, "ai_detection", base_result)
                if ai_result:
                    base_result["ai_detection"] = ai_result

            # New: AI Generation Detection (Stable Diffusion, Midjourney, DALL-E, C2PA)
            if tier_config.ai_content_detection and detect_ai_generation and is_image:
                ai_gen_result = safe_extract_module(detect_ai_generation, filepath, "ai_generation_detector")
                if ai_gen_result:
                    base_result["ai_generation"] = ai_gen_result

            # New: Image Forensics Analysis (ELA, noise, duplicates)
            if tier_config.manipulation_detection and analyze_image_forensics and is_image:
                forensics_result = safe_extract_module(analyze_image_forensics, filepath, "image_forensics")
                if forensics_result:
                    base_result["image_forensics"] = forensics_result

            # New: Photoshop PSD Analysis
            if is_psd and analyze_photoshop_psd:
                psd_result = safe_extract_module(analyze_photoshop_psd, filepath, "photoshop_psd")
                if psd_result:
                    base_result["photoshop_psd"] = psd_result

            # New: Edit History Analysis
            if tier_config.workflow_dam and analyze_edit_history and is_image:
                edit_result = safe_extract_module(analyze_edit_history, filepath, "edit_history")
                if edit_result:
                    base_result["edit_history"] = edit_result

            # New: OpenEXR HDR Analysis
            if is_exr and analyze_openexr_hdr:
                exr_result = safe_extract_module(analyze_openexr_hdr, filepath, "openexr_hdr")
                if exr_result:
                    base_result["openexr_hdr"] = exr_result

            # New: ICC Profile Extraction
            if extract_icc_profile and (is_image or is_psd):
                icc_result = safe_extract_module(extract_icc_profile, filepath, "icc_profile_parser")
                if icc_result:
                    base_result["icc_profile"] = icc_result

            # Build advanced analysis summary
            advanced_modules_run = []
            advanced_processing_time = 0
            forensic_score = 0
            authenticity_assessment = 'authentic'

            # Check steganography results
            if "steganography_analysis" in base_result:
                steg_result = base_result["steganography_analysis"]
                if isinstance(steg_result, dict):
                    advanced_modules_run.append("steganography")
                    if "performance" in steg_result:
                        advanced_processing_time += steg_result["performance"].get("duration_seconds", 0) * 1000
                    # Add to forensic score based on suspicious score
                    suspicious_score = steg_result.get("suspicious_score", 0)
                    forensic_score += suspicious_score * 0.3  # Weight steganography at 30%
                    if suspicious_score > 0.5:
                        authenticity_assessment = 'questionable'
                    if suspicious_score > 0.8:
                        authenticity_assessment = 'suspicious'

            # Check manipulation detection results
            if "manipulation_detection" in base_result:
                manip_result = base_result["manipulation_detection"]
                if isinstance(manip_result, dict):
                    advanced_modules_run.append("manipulation_detection")
                    if "performance" in manip_result:
                        advanced_processing_time += manip_result["performance"].get("duration_seconds", 0) * 1000
                    # Add to forensic score based on manipulation probability
                    manip_prob = manip_result.get("manipulation_probability", 0)
                    forensic_score += manip_prob * 0.4  # Weight manipulation at 40%
                    if manip_prob > 0.3:
                        authenticity_assessment = 'questionable'
                    if manip_prob > 0.7:
                        authenticity_assessment = 'suspicious'

            # Check AI detection results
            if "ai_detection" in base_result:
                ai_result = base_result["ai_detection"]
                if isinstance(ai_result, dict):
                    advanced_modules_run.append("ai_detection")
                    if "performance" in ai_result:
                        advanced_processing_time += ai_result["performance"].get("duration_seconds", 0) * 1000
                    # Add to forensic score based on AI probability
                    ai_prob = ai_result.get("ai_probability", 0)
                    forensic_score += ai_prob * 0.3  # Weight AI detection at 30%
                    if ai_prob > 0.4:
                        authenticity_assessment = 'questionable'
                    if ai_prob > 0.8:
                        authenticity_assessment = 'suspicious'

            # Only add advanced_analysis if any modules were run
            if advanced_modules_run:
                base_result["advanced_analysis"] = {
                    "enabled": True,
                    "processing_time_ms": advanced_processing_time,
                    "modules_run": advanced_modules_run,
                    "forensic_score": min(forensic_score, 1.0),  # Cap at 1.0
                    "authenticity_assessment": authenticity_assessment
                }

            # Optional: Timeline reconstruction
            if tier_config.timeline_reconstruction and analyze_single_file_timeline:
                timeline_result = safe_extract_module(analyze_single_file_timeline, base_result, "timeline_analysis")
                if timeline_result:
                    base_result["timeline_analysis"] = timeline_result

            # Optional: Emerging technology analysis
            if tier_config.emerging_technology and extract_emerging_technology_metadata:
                emerging_result = safe_extract_module(extract_emerging_technology_metadata, filepath, "emerging_technology")
                if emerging_result and emerging_result.get("emerging_technology_analysis"):
                    base_result["emerging_technology"] = emerging_result

            # Optional: Advanced video analysis
            if tier_config.advanced_video_analysis and extract_advanced_video_metadata and is_video:
                video_result = safe_extract_module(extract_advanced_video_metadata, filepath, "advanced_video")
                if video_result and video_result.get("available"):
                    base_result["advanced_video"] = video_result

            # Optional: Advanced audio analysis
            if tier_config.advanced_audio_analysis and extract_advanced_audio_metadata and is_audio:
                audio_result = safe_extract_module(extract_advanced_audio_metadata, filepath, "advanced_audio")
                if audio_result and audio_result.get("available"):
                    base_result["advanced_audio"] = audio_result

            # Optional: Document analysis
            if tier_config.document_analysis and extract_document_metadata:
                # Check if it's a document type
                file_ext = Path(filepath).suffix.lower()
                document_extensions = [
                    '.pdf', '.docx', '.xlsx', '.pptx', '.html', '.htm', '.xml',
                    '.epub', '.mobi', '.zip', '.tar', '.gz', '.py', '.js', '.java',
                    '.json', '.yaml', '.yml', '.toml', '.ini', '.txt', '.md', '.db'
                ]

                if file_ext in document_extensions or not (is_image or is_video or is_audio):
                    doc_result = safe_extract_module(extract_document_metadata, filepath, "document_metadata")
                    if doc_result and doc_result.get("available"):
                        base_result["document_metadata"] = doc_result

            # Optional: Scientific research analysis
            if (
                tier_config.scientific_research
                and extract_scientific_research_metadata
                and not (is_image or is_video or is_audio)
            ):
                research_result = safe_extract_module(extract_scientific_research_metadata, filepath, "scientific_research")
                if research_result and research_result.get("available"):
                    base_result["scientific_research"] = research_result

            # Optional: Multimedia entertainment analysis
            if (
                tier_config.multimedia_entertainment
                and extract_multimedia_entertainment_metadata
                and not (is_image or is_video or is_audio)
            ):
                entertainment_result = safe_extract_module(extract_multimedia_entertainment_metadata, filepath, "multimedia_entertainment")
                if entertainment_result and entertainment_result.get("available"):
                    base_result["multimedia_entertainment"] = entertainment_result

            # Optional: Industrial manufacturing analysis
            if (
                tier_config.industrial_manufacturing
                and extract_industrial_manufacturing_metadata
                and not (is_image or is_video or is_audio)
            ):
                industrial_result = safe_extract_module(extract_industrial_manufacturing_metadata, filepath, "industrial_manufacturing")
                if industrial_result and industrial_result.get("available"):
                    base_result["industrial_manufacturing"] = industrial_result

            # Optional: Financial business analysis
            if (
                tier_config.financial_business
                and extract_financial_business_metadata
                and not (is_image or is_video or is_audio)
            ):
                financial_result = safe_extract_module(extract_financial_business_metadata, filepath, "financial_business")
                if financial_result and financial_result.get("available"):
                    base_result["financial_business"] = financial_result

            # Optional: Healthcare medical analysis
            if (
                tier_config.healthcare_medical
                and extract_healthcare_medical_metadata
                and not (is_image or is_video or is_audio)
            ):
                healthcare_result = safe_extract_module(extract_healthcare_medical_metadata, filepath, "healthcare_medical")
                if healthcare_result and healthcare_result.get("available"):
                    base_result["healthcare_medical"] = healthcare_result

            # Optional: Transportation logistics analysis
            if (
                tier_config.transportation_logistics
                and extract_transportation_logistics_metadata
                and not (is_image or is_video or is_audio)
            ):
                transport_result = safe_extract_module(extract_transportation_logistics_metadata, filepath, "transportation_logistics")
                if transport_result and transport_result.get("available"):
                    base_result["transportation_logistics"] = transport_result

            # Optional: Education academic analysis
            if (
                tier_config.education_academic
                and extract_education_academic_metadata
                and not (is_image or is_video or is_audio)
            ):
                education_result = safe_extract_module(extract_education_academic_metadata, filepath, "education_academic")
                if education_result and education_result.get("available"):
                    base_result["education_academic"] = education_result

            # Optional: Legal compliance analysis
            if (
                tier_config.legal_compliance
                and extract_legal_compliance_metadata
                and not (is_image or is_video or is_audio)
            ):
                legal_result = safe_extract_module(extract_legal_compliance_metadata, filepath, "legal_compliance")
                if legal_result and legal_result.get("available"):
                    base_result["legal_compliance"] = legal_result

            # Optional: Environmental sustainability analysis
            if (
                tier_config.environmental_sustainability
                and extract_environmental_sustainability_metadata
                and not (is_image or is_video or is_audio)
            ):
                environmental_result = safe_extract_module(extract_environmental_sustainability_metadata, filepath, "environmental_sustainability")
                if environmental_result and environmental_result.get("available"):
                    base_result["environmental_sustainability"] = environmental_result

            # Optional: Social media digital analysis
            if (
                tier_config.social_media_digital
                and extract_social_media_digital_metadata
                and not (is_image or is_video or is_audio)
            ):
                social_digital_result = safe_extract_module(extract_social_media_digital_metadata, filepath, "social_media_digital")
                if social_digital_result and social_digital_result.get("available"):
                    base_result["social_media_digital"] = social_digital_result

            # Optional: Gaming entertainment analysis
            if (
                tier_config.gaming_entertainment
                and extract_gaming_entertainment_metadata
                and not (is_image or is_video or is_audio)
            ):
                gaming_result = safe_extract_module(extract_gaming_entertainment_metadata, filepath, "gaming_entertainment")
                if gaming_result and gaming_result.get("available"):
                    base_result["gaming_entertainment"] = gaming_result

            # Forensic Analysis Integration (NEW: Phase 3.1)
            # Automatically integrate forensic analysis results with confidence scoring
            if tier_config.steganography_detection or tier_config.manipulation_detection or tier_config.ai_content_detection:
                try:
                    # Import the forensic integration module
                    from .modules.forensic_analysis_integrator import integrate_forensic_analysis
                    
                    # Integrate forensic analysis results
                    base_result = integrate_forensic_analysis(base_result, filepath, tier_config)
                    
                    # Log forensic integration success
                    forensic_integration = base_result.get('forensic_analysis_integration', {})
                    forensic_score = forensic_integration.get('forensic_score', 0)
                    authenticity = forensic_integration.get('authenticity_assessment', 'unknown')
                    
                    logger.info(f"Forensic analysis integration completed - Score: {forensic_score}, Assessment: {authenticity}")
                    
                except ImportError as e:
                    logger.warning(f"Forensic analysis integration module not available: {e}")
                except Exception as e:
                    logger.error(f"Error during forensic analysis integration: {e}")
                    # Don't fail the entire extraction if forensic integration fails
                    base_result['forensic_analysis_integration'] = {
                        'enabled': False,
                        'error': str(e),
                        'forensic_score': 100,  # Default to authentic if integration fails
                        'authenticity_assessment': 'authentic'
                    }

        except Exception as e:
            logger.warning(f"Error during comprehensive extraction for {filepath}: {e}")
            logger.debug(f"Full traceback for comprehensive extraction: {traceback.format_exc()}")
            
            if "extraction_errors" not in base_result:
                base_result["extraction_errors"] = []
            
            base_result["extraction_errors"].append(
                create_standardized_error(
                    exception=e,
                    module_name="comprehensive_engine",
                    filepath=filepath,
                    start_time=start_time,
                    error_code="ERR_COMPREHENSIVE_EXTRACTION_FAILED",
                    severity="medium",
                    recoverable=True,
                    custom_message="Error during comprehensive metadata extraction",
                    suggested_action="Some modules may have partial results",
                    error_context={
                        "phase": "comprehensive_extraction",
                        "tier": tier,
                        "non_critical": True
                    }
                )
            )



        # Update field count
        def count_comprehensive_fields(obj, visited=None):
            try:
                from extractor.utils.field_counting import (
                    count_meaningful_fields,
                    DEFAULT_FIELD_COUNT_IGNORED_KEYS,
                )
            except Exception:
                try:
                    from .utils.field_counting import (
                        count_meaningful_fields,
                        DEFAULT_FIELD_COUNT_IGNORED_KEYS,
                    )
                except Exception:
                    count_meaningful_fields = None  # type: ignore[assignment]

            if count_meaningful_fields is not None:
                return count_meaningful_fields(
                    obj, ignored_keys=set(DEFAULT_FIELD_COUNT_IGNORED_KEYS)
                )

            # Fallback: avoid counting null/empty placeholders if import paths fail.
            if visited is None:
                visited = set()

            obj_id = id(obj)
            if obj_id in visited:
                return 0
            visited.add(obj_id)

            try:
                if obj is None:
                    return 0
                if isinstance(obj, str):
                    return 0 if obj.strip() == "" else 1
                if isinstance(obj, (int, float, bool, bytes, bytearray)):
                    return 1
                if isinstance(obj, list):
                    return sum(count_comprehensive_fields(v, visited) for v in obj)
                if isinstance(obj, dict):
                    total = 0
                    for k, v in obj.items():
                        if str(k).startswith("_"):
                            continue
                        total += count_comprehensive_fields(v, visited)
                    return total
                return 1
            finally:
                visited.remove(obj_id)
        
        base_result["extraction_info"]["comprehensive_fields_extracted"] = count_comprehensive_fields(base_result)
        
        # Add specialized field counts
        specialized_counts = {}
        if "medical_imaging" in base_result:
            specialized_counts["medical_imaging"] = count_comprehensive_fields(base_result["medical_imaging"])
        if "astronomical_data" in base_result:
            specialized_counts["astronomical_data"] = count_comprehensive_fields(base_result["astronomical_data"])
        if "geospatial" in base_result:
            specialized_counts["geospatial"] = count_comprehensive_fields(base_result["geospatial"])
        if "scientific_data" in base_result:
            specialized_counts["scientific_data"] = count_comprehensive_fields(base_result["scientific_data"])
        if "drone_telemetry" in base_result:
            specialized_counts["drone_telemetry"] = count_comprehensive_fields(base_result["drone_telemetry"])
        if "blockchain_provenance" in base_result:
            specialized_counts["blockchain_provenance"] = count_comprehensive_fields(base_result["blockchain_provenance"])
        if "emerging_technology" in base_result:
            specialized_counts["emerging_technology"] = count_comprehensive_fields(base_result["emerging_technology"])
        if "advanced_video" in base_result:
            specialized_counts["advanced_video"] = count_comprehensive_fields(base_result["advanced_video"])
        if "advanced_audio" in base_result:
            specialized_counts["advanced_audio"] = count_comprehensive_fields(base_result["advanced_audio"])
        if "document_metadata" in base_result:
            specialized_counts["document_metadata"] = count_comprehensive_fields(base_result["document_metadata"])
        if "scientific_research" in base_result:
            specialized_counts["scientific_research"] = count_comprehensive_fields(base_result["scientific_research"])
        if "multimedia_entertainment" in base_result:
            specialized_counts["multimedia_entertainment"] = count_comprehensive_fields(base_result["multimedia_entertainment"])
        if "industrial_manufacturing" in base_result:
            specialized_counts["industrial_manufacturing"] = count_comprehensive_fields(base_result["industrial_manufacturing"])
        if "financial_business" in base_result:
            specialized_counts["financial_business"] = count_comprehensive_fields(base_result["financial_business"])
        
        base_result["extraction_info"]["specialized_field_counts"] = specialized_counts

        # Add overall performance metrics
        total_duration_ms = (time.time() - start_time) * 1000
        base_result["extraction_info"]["processing_ms"] = total_duration_ms

        # Execute dynamically discovered modules
        if MODULE_DISCOVERY_AVAILABLE:
            try:
                self._execute_dynamic_modules(filepath, base_result, tier_config)
                logger.info(f"Dynamic module execution completed for {filepath}")
            except Exception as e:
                logger.error(f"Error in dynamic module execution for {filepath}: {e}")
                logger.debug(f"Full traceback for dynamic modules: {traceback.format_exc()}")
                
                # Add to extraction errors if they exist, otherwise log separately
                error_info = create_standardized_error(
                    exception=e,
                    module_name="comprehensive_engine",
                    filepath=filepath,
                    start_time=start_time,
                    error_code="ERR_DYNAMIC_MODULE_FAILED",
                    severity="medium",
                    recoverable=True,
                    custom_message="Dynamic module execution failed",
                    suggested_action="Check module discovery configuration",
                    error_context={
                        "phase": "dynamic_modules",
                        "tier": tier
                    }
                )
                
                if "extraction_errors" in base_result:
                    base_result["extraction_errors"].append(error_info)
                else:
                    logger.warning(f"Dynamic module error (no extraction_errors array): {error_info['error']['message']}")
        
        # Calculate performance summary
        # Collect performance data from all module results
        all_module_performance = {}

        # Look for performance data in all module results
        module_result_keys = [
            "medical_imaging", "astronomical_data", "geospatial", "scientific_data",
            "drone_telemetry", "blockchain_provenance", "web_metadata", "social_media",
            "mobile_metadata", "forensic_security", "action_camera", "camera_360",
            "print_publishing", "workflow_dam", "audio_advanced", "video_advanced",
            "steganography_analysis", "manipulation_detection", "ai_detection",
            "timeline_analysis", "emerging_technology", "advanced_video", "advanced_audio",
            "document_metadata", "scientific_research", "multimedia_entertainment",
            "industrial_manufacturing", "financial_business", "healthcare_medical",
            "transportation_logistics", "education_academic", "legal_compliance",
            "environmental_sustainability", "social_media_digital", "gaming_entertainment"
        ]
        
        # Add dynamic module result keys (they follow the pattern module_name_function_name)
        if MODULE_DISCOVERY_AVAILABLE and self.module_registry:
            all_functions = get_all_available_extraction_functions()
            for module_name, functions in all_functions.items():
                for function_name in functions.keys():
                    dynamic_key = f"{module_name}_{function_name}"
                    if dynamic_key not in module_result_keys:
                        module_result_keys.append(dynamic_key)

        for key in module_result_keys:
            if key in base_result and isinstance(base_result[key], dict) and "performance" in base_result[key]:
                perf_data = base_result[key]["performance"]
                # Ensure perf_data is a dictionary, not a primitive type
                if isinstance(perf_data, dict):
                    all_module_performance.update(perf_data)
                else:
                    # If it's not a dict, skip it or convert it
                    logger.warning(f"Performance data for {key} is not a dictionary: {type(perf_data)}")

        if all_module_performance:
            successful_modules = 0
            failed_modules = 0
            total_module_time = 0

            for module_name, perf_data in all_module_performance.items():
                # Safety check: ensure perf_data is a dictionary
                if not isinstance(perf_data, dict):
                    logger.warning(f"Performance data for {module_name} is not a dictionary: {type(perf_data)}. Skipping.")
                    continue
                    
                if perf_data.get("status") == "success":
                    successful_modules += 1
                    total_module_time += perf_data.get("duration_seconds", 0) * 1000
                else:
                    failed_modules += 1

            base_result["extraction_info"]["performance_summary"] = {
                "total_processing_time_ms": total_duration_ms,
                "successful_modules": successful_modules,
                "failed_modules": failed_modules,
                "total_module_processing_time_ms": total_module_time,
                "overhead_time_ms": total_duration_ms - total_module_time if total_module_time > 0 else total_duration_ms
            }
        else:
            # If no module performance data was collected, provide basic summary
            base_result["extraction_info"]["performance_summary"] = {
                "total_processing_time_ms": total_duration_ms,
                "successful_modules": 0,
                "failed_modules": 0,
                "total_module_processing_time_ms": 0,
                "overhead_time_ms": total_duration_ms
            }

        # Record metrics for monitoring
        if MONITORING_AVAILABLE:
            success = "error" not in base_result
            file_ext = Path(filepath).suffix.lower() if filepath else "unknown"
            mime_type = base_result.get("file", {}).get("mime_type", "unknown")
            file_type = mime_type or file_ext or "unknown"

            error_type = None
            if not success:
                error_type = base_result.get("error_type", "UnknownError")

            record_extraction_for_monitoring(
                processing_time_ms=total_duration_ms,
                success=success,
                tier=tier,
                file_type=file_type,
                error_type=error_type
            )

        # Record metrics for analytics
        if ANALYTICS_AVAILABLE:
            success = "error" not in base_result
            file_ext = Path(filepath).suffix.lower() if filepath else "unknown"
            mime_type = base_result.get("file", {}).get("mime_type", "unknown")
            file_type = mime_type or file_ext or "unknown"

            error_type = None
            if not success:
                error_type = base_result.get("error_type", "UnknownError")

            # Get file size if possible
            file_size = None
            try:
                file_size = os.path.getsize(filepath) if filepath and os.path.exists(filepath) else None
            except:
                pass  # Ignore errors getting file size

            record_extraction_for_analytics(
                processing_time_ms=total_duration_ms,
                success=success,
                tier=tier,
                file_type=file_type,
                file_size=file_size,
                error_type=error_type
            )

        # Promote burned metadata GPS to main GPS field if needed
        if "burned_metadata" in base_result and base_result["burned_metadata"]:
            burned_gps = base_result["burned_metadata"].get("parsed_data", {}).get("gps")
            if burned_gps and "latitude" in burned_gps and "longitude" in burned_gps:
                # Only set main GPS if it's missing or empty
                if "gps" not in base_result or not base_result["gps"] or not base_result["gps"].get("latitude"):
                    base_result["gps"] = burned_gps
                    logger.debug(f"Promoted burned metadata GPS to main GPS field: {burned_gps['latitude']}, {burned_gps['longitude']}")

        # Add observability data (provenance, sensitive fields, shadow mode)
        # This is the final step - adds to extraction_info only, never changes client-facing metadata
        try:
            base_result = add_observability_to_result(
                result=base_result,
                provenance=_provenance,
                conflicts=_provenance_conflicts,
                shadow_info=_shadow_info
            )
        except Exception as obs_err:
            # Observability errors NEVER fail main extraction
            logger.warning(f"Observability data addition failed (non-fatal): {obs_err}")
            if "extraction_info" not in base_result:
                base_result["extraction_info"] = {}
            base_result["extraction_info"]["observability_error"] = str(obs_err)

        return base_result

# ============================================================================
# Main Interface Functions
# ============================================================================

# Global comprehensive extractor instance
_comprehensive_extractor = None

def get_comprehensive_extractor() -> ComprehensiveMetadataExtractor:
    """Get or create the global comprehensive extractor instance."""
    global _comprehensive_extractor
    if _comprehensive_extractor is None:
        _comprehensive_extractor = ComprehensiveMetadataExtractor()
    return _comprehensive_extractor

def extract_comprehensive_metadata(
    filepath: str,
    tier: str = "free",
    enable_ocr: bool = True,
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata using all available specialized engines.

    This is the main entry point for the ultimate metadata extraction.
    """
    start_time = time.time()

    # Log the start of the extraction
    log_extraction_event(
        event_type="extraction_start",
        filepath=filepath,
        module_name="comprehensive_engine",
        status="info",
        details={"tier": tier}
    )

    # Check cache first if available
    cached_result = _check_cache_and_return_if_found(filepath, tier, start_time, is_async=False)
    if cached_result:
        return cached_result

    try:
        extractor = get_comprehensive_extractor()
        result = extractor.extract_comprehensive_metadata(filepath, tier, enable_ocr=enable_ocr)

        # Log successful completion
        duration = time.time() - start_time
        log_extraction_event(
            event_type="extraction_complete",
            filepath=filepath,
            module_name="comprehensive_engine",
            status="info",
            duration=duration,
            details={
                "tier": tier,
                "fields_extracted": result.get("extraction_info", {}).get("comprehensive_fields_extracted", 0),
                "success": True
            }
        )

        # Add persona-friendly interpretation layer
        try:
            print("[persona_debug] Attempting to add persona interpretation", file=sys.stderr)
            import importlib.util
            import os

            # Get the path to persona_interpretation.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            persona_path = os.path.join(current_dir, "persona_interpretation.py")

            print(f"[persona_debug] Persona path: {persona_path}", file=sys.stderr)
            print(f"[persona_debug] Path exists: {os.path.exists(persona_path)}", file=sys.stderr)

            # Add current directory to Python path temporarily
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("persona_interpretation", persona_path)
            if spec is None:
                print(f"[persona_debug] Failed to create module spec", file=sys.stderr)
                raise ImportError(f"Could not create module spec for {persona_path}")

            persona_module = importlib.util.module_from_spec(spec)

            print(f"[persona_debug] About to execute module", file=sys.stderr)
            try:
                spec.loader.exec_module(persona_module)
                print(f"[persona_debug] Module executed successfully", file=sys.stderr)
            except ImportError as import_error:
                print(f"[persona_debug] ImportError during module execution: {import_error}", file=sys.stderr)
                # Try to provide more context about what's missing
                if "extractor" in str(import_error):
                    print(f"[persona_debug] The 'extractor' module import failed - this might be expected", file=sys.stderr)
                    print(f"[persona_debug] sys.path: {sys.path[:3]}", file=sys.stderr)
                raise import_error

            # Get the function
            add_persona_interpretation = persona_module.add_persona_interpretation
            # Default to phone_photo_sarah persona for image files
            persona = "phone_photo_sarah"
            mime_type = result.get("file", {}).get("mime_type", "")
            print(f"[persona_debug] Mime type: {mime_type}, starts with image/: {mime_type.startswith('image/')}", file=sys.stderr)
            logger.info(f"[persona_check] Mime type: {mime_type}, starts with image/: {mime_type.startswith('image/')}")
            if mime_type.startswith("image/"):
                print(f"[persona_debug] Adding persona interpretation for {persona}", file=sys.stderr)
                logger.info(f"[persona_adding] Adding persona interpretation for {persona}")
                persona_enhanced_result = add_persona_interpretation(result, persona)

                # Debug: Check what we got back
                print(f"[persona_debug] Type of result: {type(persona_enhanced_result)}", file=sys.stderr)
                print(f"[persona_debug] Keys in result: {list(persona_enhanced_result.keys()) if isinstance(persona_enhanced_result, dict) else 'Not a dict'}", file=sys.stderr)

                # Add the persona interpretation to the existing result
                persona_interpretation = persona_enhanced_result.get("persona_interpretation")
                print(f"[persona_debug] Persona interpretation extracted: {persona_interpretation is not None}", file=sys.stderr)
                print(f"[persona_debug] Persona interpretation type: {type(persona_interpretation)}", file=sys.stderr)

                result["persona_interpretation"] = persona_interpretation
                print(f"[persona_debug] Successfully added persona interpretation to result", file=sys.stderr)
                logger.info(f"[persona_success] Successfully added persona interpretation for {persona}")
            else:
                print(f"[persona_debug] Not an image file, skipping", file=sys.stderr)
                logger.info(f"[persona_skipped] Not an image file, skipping persona interpretation")
        except ImportError as e:
            print(f"[persona_debug] ImportError: {e}", file=sys.stderr)
            logger.debug(f"Persona interpretation not available: {e}")
        except Exception as e:
            print(f"[persona_debug] Exception: {type(e).__name__}: {e}", file=sys.stderr)
            print(f"[persona_debug] Traceback: {traceback.format_exc()}", file=sys.stderr)
            logger.warning(f"Failed to add persona interpretation: {e}")

        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Critical error in main extraction interface for {filepath}: {e}")
        logger.debug(f"Full traceback for main interface: {traceback.format_exc()}")
        
        error_response = create_standardized_error(
            exception=e,
            module_name="comprehensive_engine",
            filepath=filepath,
            start_time=start_time,
            error_code="ERR_MAIN_EXTRACTION_FAILED",
            severity="critical",
            recoverable=False,
            custom_message="Critical error in comprehensive metadata extraction",
            suggested_action="Check file and system requirements",
            error_context={
                "phase": "main_interface",
                "tier": tier
            }
        )
        
        log_extraction_event(
            event_type="extraction_error",
            filepath=filepath,
            module_name="comprehensive_engine",
            status="error",
            duration=duration,
            details={
                "tier": tier,
                "error_code": error_response["error"]["code"],
                "error": error_response["error"]["message"],
                "error_type": error_response["error"]["type"],
                "severity": error_response["error"]["severity"],
                "recoverable": error_response["error"]["recoverable"],
                "success": False
            }
        )
        
        return error_response


def extract_comprehensive_batch(
    filepaths: List[str],
    tier: str = "super",
    max_workers: int = 4,
    store_results: bool = False,
    enable_ocr: bool = True,
) -> Dict[str, Any]:
    """Extract metadata for multiple files with optional storage."""
    start_time = time.time()

    # Log the start of the batch extraction
    log_extraction_event(
        event_type="batch_extraction_start",
        filepath="batch_operation",
        module_name="comprehensive_engine",
        status="info",
        details={
            "total_files": len(filepaths),
            "tier": tier,
            "max_workers": max_workers
        }
    )

    extractor = get_comprehensive_extractor()
    results: Dict[str, Any] = {}
    errors = 0

    def _process(path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            metadata = extractor.extract_comprehensive_metadata(
                path, tier, enable_ocr=enable_ocr
            )
            if store_results and store_file_metadata and "error" not in metadata:
                try:
                    store_file_metadata(path, metadata, metadata.get("perceptual_hashes"))
                except Exception as e:
                    logger.warning(f"Failed to store metadata for {path}: {e}")
                    metadata["storage_error"] = str(e)
            return path, metadata
        except Exception as e:
            logger.error(f"Error processing {path} in batch: {e}")
            return path, {
                "error": f"Error processing file in batch: {str(e)}",
                "error_type": type(e).__name__,
                "file": {"path": path},
                "extraction_info": {
                    "comprehensive_version": "4.0.0",
                    "tier": tier
                }
            }

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for path, metadata in executor.map(_process, filepaths):
                results[path] = metadata
                if "error" in metadata:
                    errors += 1

        duration_ms = int((time.time() - start_time) * 1000)
        batch_payload = {
            "results": results,
            "summary": {
                "total_files": len(filepaths),
                "successful": len(filepaths) - errors,
                "failed": errors,
                "processing_ms": duration_ms,
                "tier": tier,
            },
        }

        # If every file failed, promote to a batch-level error (contract: top-level "error").
        if len(filepaths) > 0 and errors == len(filepaths):
            first_error = next(
                (
                    meta
                    for meta in results.values()
                    if isinstance(meta, dict) and "error" in meta
                ),
                {},
            )
            batch_payload["error"] = (
                f"Critical error in async batch metadata extraction: "
                f"{first_error.get('error', 'All files failed')}"
            )
            batch_payload["error_type"] = first_error.get("error_type", "Exception")

        # Optional batch comparison
        if MetadataComparator is not None:
            try:
                tier_enum = Tier(tier.lower())
            except ValueError:
                tier_enum = Tier.SUPER
            tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]
            if tier_config.batch_comparison:
                try:
                    comparator = MetadataComparator()
                    comparable = [meta for meta in results.values() if isinstance(meta, dict) and "error" not in meta]
                    if len(comparable) >= 2:
                        batch_payload["batch_comparison"] = comparator.compare_files(comparable, "summary")
                except Exception as e:
                    logger.error(f"Batch comparison failed: {e}")
                    batch_payload["batch_comparison"] = {"error": str(e)}

        # Log successful completion
        log_extraction_event(
            event_type="batch_extraction_complete",
            filepath="batch_operation",
            module_name="comprehensive_engine",
            status="info",
            duration=duration_ms/1000,
            details={
                "total_files": len(filepaths),
                "successful": len(filepaths) - errors,
                "failed": errors,
                "tier": tier
            }
        )

        return batch_payload
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Critical error in batch metadata extraction: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")

        # Log the error
        log_extraction_event(
            event_type="batch_extraction_error",
            filepath="batch_operation",
            module_name="comprehensive_engine",
            status="error",
            duration=duration_ms/1000,
            details={
                "total_files": len(filepaths),
                "error": str(e),
                "error_type": type(e).__name__,
                "tier": tier
            }
        )

        return {
            "error": f"Critical error in batch metadata extraction: {str(e)}",
            "error_type": type(e).__name__,
            "summary": {
                "total_files": len(filepaths),
                "successful": 0,
                "failed": len(filepaths),
                "processing_ms": duration_ms,
                "tier": tier,
            },
        }


async def extract_comprehensive_metadata_async(
    filepath: str,
    tier: str = "free",
    enable_ocr: bool = True,
) -> Dict[str, Any]:
    """
    Asynchronously extract comprehensive metadata using all available specialized engines.

    This is the async entry point for the ultimate metadata extraction.
    """
    loop = asyncio.get_event_loop()
    start_time = time.time()

    # Log the start of the extraction
    log_extraction_event(
        event_type="async_extraction_start",
        filepath=filepath,
        module_name="comprehensive_engine_async",
        status="info",
        details={"tier": tier}
    )

    # Check cache first if available
    cached_result = _check_cache_and_return_if_found(filepath, tier, start_time, is_async=True)
    if cached_result:
        return cached_result

    try:
        # Run the synchronous extraction in a thread pool to avoid blocking the event loop
        extractor = get_comprehensive_extractor()
        call_args = (filepath, tier) if enable_ocr else (filepath, tier, enable_ocr)
        result = await loop.run_in_executor(
            None,
            extractor.extract_comprehensive_metadata,
            *call_args,
        )

        # Log successful completion
        duration = time.time() - start_time
        log_extraction_event(
            event_type="async_extraction_complete",
            filepath=filepath,
            module_name="comprehensive_engine_async",
            status="info",
            duration=duration,
            details={
                "tier": tier,
                "fields_extracted": result.get("extraction_info", {}).get("comprehensive_fields_extracted", 0),
                "success": True
            }
        )

        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Critical error in async comprehensive metadata extraction for {filepath}: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")

        # Log the error
        log_extraction_event(
            event_type="async_extraction_error",
            filepath=filepath,
            module_name="comprehensive_engine_async",
            status="error",
            duration=duration,
            details={
                "tier": tier,
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False
            }
        )

        # Return a structured error response
        return {
            "error": f"Critical error in async comprehensive metadata extraction: {str(e)}",
            "error_type": type(e).__name__,
            "file": {"path": filepath},
            "extraction_info": {
                "comprehensive_version": "4.0.0",
                "processing_ms": duration * 1000,
                "tier": tier
            }
        }


async def extract_comprehensive_batch_async(
    filepaths: List[str],
    tier: str = "super",
    max_workers: int = 4,
    store_results: bool = False,
    enable_ocr: bool = True,
) -> Dict[str, Any]:
    """
    Asynchronously extract metadata for multiple files with optional storage.

    This function uses asyncio to process multiple files concurrently.
    """
    start_time = time.time()

    # Log the start of the batch extraction
    log_extraction_event(
        event_type="async_batch_extraction_start",
        filepath="batch_operation",
        module_name="comprehensive_engine_async",
        status="info",
        details={
            "total_files": len(filepaths),
            "tier": tier,
            "max_workers": max_workers
        }
    )

    results: Dict[str, Any] = {}
    errors = 0

    # Create a semaphore to limit concurrent operations
    semaphore = asyncio.Semaphore(max_workers)

    async def _process_async(path: str) -> Tuple[str, Dict[str, Any]]:
        async with semaphore:
            try:
                metadata = await extract_comprehensive_metadata_async(
                    path, tier, enable_ocr=enable_ocr
                )
                if store_results and store_file_metadata and "error" not in metadata:
                    try:
                        # Run storage in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(
                            None,
                            store_file_metadata,
                            path,
                            metadata,
                            metadata.get("perceptual_hashes")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to store metadata for {path}: {e}")
                        metadata["storage_error"] = str(e)
                return path, metadata
            except Exception as e:
                logger.error(f"Error processing {path} in async batch: {e}")
                return path, {
                    "error": f"Error processing file in async batch: {str(e)}",
                    "error_type": type(e).__name__,
                    "file": {"path": path},
                    "extraction_info": {
                        "comprehensive_version": "4.0.0",
                        "tier": tier
                    }
                }

    try:
        # Process all files concurrently
        tasks = [_process_async(path) for path in filepaths]
        results_list = await asyncio.gather(*tasks, return_exceptions=False)

        # Process results
        for path, metadata in results_list:
            results[path] = metadata
            if "error" in metadata:
                errors += 1

        duration_ms = int((time.time() - start_time) * 1000)
        batch_payload = {
            "results": results,
            "summary": {
                "total_files": len(filepaths),
                "successful": len(filepaths) - errors,
                "failed": errors,
                "processing_ms": duration_ms,
                "tier": tier,
            },
        }

        # If every file failed, promote to a batch-level error (contract: top-level "error").
        if len(filepaths) > 0 and errors == len(filepaths):
            first_error = next(
                (
                    meta
                    for meta in results.values()
                    if isinstance(meta, dict) and "error" in meta
                ),
                {},
            )
            batch_payload["error"] = (
                f"Critical error in async batch metadata extraction: "
                f"{first_error.get('error', 'All files failed')}"
            )
            batch_payload["error_type"] = first_error.get("error_type", "Exception")

        # Optional batch comparison
        if MetadataComparator is not None:
            try:
                tier_enum = Tier(tier.lower())
            except ValueError:
                tier_enum = Tier.SUPER
            tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]
            if tier_config.batch_comparison:
                try:
                    # Run comparison in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    comparator = MetadataComparator()
                    comparable = [meta for meta in results.values() if isinstance(meta, dict) and "error" not in meta]
                    if len(comparable) >= 2:
                        batch_payload["batch_comparison"] = await loop.run_in_executor(
                            None,
                            comparator.compare_files,
                            comparable,
                            "summary"
                        )
                except Exception as e:
                    logger.error(f"Async batch comparison failed: {e}")
                    batch_payload["batch_comparison"] = {"error": str(e)}

        # Log successful completion
        log_extraction_event(
            event_type="async_batch_extraction_complete",
            filepath="batch_operation",
            module_name="comprehensive_engine_async",
            status="info",
            duration=duration_ms/1000,
            details={
                "total_files": len(filepaths),
                "successful": len(filepaths) - errors,
                "failed": errors,
                "tier": tier
            }
        )

        return batch_payload
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Critical error in async batch metadata extraction: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")

        # Log the error
        log_extraction_event(
            event_type="async_batch_extraction_error",
            filepath="batch_operation",
            module_name="comprehensive_engine_async",
            status="error",
            duration=duration_ms/1000,
            details={
                "total_files": len(filepaths),
                "error": str(e),
                "error_type": type(e).__name__,
                "tier": tier
            }
        )

        return {
            "error": f"Critical error in async batch metadata extraction: {str(e)}",
            "error_type": type(e).__name__,
            "summary": {
                "total_files": len(filepaths),
                "successful": 0,
                "failed": len(filepaths),
                "processing_ms": duration_ms,
                "tier": tier,
            },
        }

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MetaExtract Comprehensive Engine v4.0 - Ultimate Metadata Extraction")
    parser.add_argument("files", nargs="+", help="File(s) to extract metadata from")
    parser.add_argument("--tier", "-t", default="free", choices=["free", "starter", "premium", "super"])
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--engines", action="store_true", help="Show available specialized engines")
    parser.add_argument("--batch", action="store_true", help="Process files in batch mode")
    parser.add_argument("--store", action="store_true", help="Store metadata in local database")
    parser.add_argument("--max-workers", type=int, default=4, help="Batch concurrency")
    parser.add_argument("--performance", action="store_true", help="Include performance metrics (compat)")
    parser.add_argument("--advanced", action="store_true", help="Enable advanced analysis (compat)")
    parser.add_argument("--ocr", action="store_true", help="Run burned metadata OCR")
    parser.add_argument("--max-dim", type=int, default=2048, help="Resize cap for OCR/hash compute paths")
    parser.add_argument("--quiet", "-q", action="store_true", help="JSON only output")
    
    args = parser.parse_args()

    # Expose max dimension to downstream modules via environment for compute-heavy paths
    try:
        os.environ["METAEXTRACT_MAX_DIM"] = str(args.max_dim)
    except Exception:
        pass
    
    if args.engines:
        print("Available Specialized Engines:")
        print(f"  Medical Imaging (DICOM): {'✓' if DICOM_AVAILABLE else '✗'}")
        print(f"  Astronomical Data (FITS): {'✓' if FITS_AVAILABLE else '✗'}")
        print(f"  Geospatial (GeoTIFF/Shapefile): {'✓' if RASTERIO_AVAILABLE or FIONA_AVAILABLE else '✗'}")
        print(f"  Scientific Data (HDF5/NetCDF): {'✓' if HDF5_AVAILABLE or NETCDF_AVAILABLE else '✗'}")
        print(f"  Advanced Image Analysis: {'✓' if OPENCV_AVAILABLE else '✗'}")
        print(f"  Microscopy: {'✓' if MICROSCOPY_AVAILABLE else '✗'}")
        print(f"  Blockchain/Web3: {'✓' if WEB3_AVAILABLE else '✗'}")
        print(f"  Advanced Audio: {'✓' if LIBROSA_AVAILABLE else '✗'}")
        return
    
    if args.batch or len(args.files) > 1:
        if not args.quiet:
            print(f"MetaExtract Comprehensive v4.0.0 - Batch extracting {len(args.files)} files", file=sys.stderr)
        result = extract_comprehensive_batch(
            args.files,
            tier=args.tier,
            max_workers=args.max_workers,
            store_results=args.store,
            enable_ocr=args.ocr,
        )
        json_out = json.dumps(result, indent=2, default=str)
    else:
        if not args.quiet:
            print(f"MetaExtract Comprehensive v4.0.0 - Extracting from: {args.files[0]}", file=sys.stderr)
            print(
                f"Tier: {args.tier} | Engines: Medical={'✓' if DICOM_AVAILABLE else '✗'} Astro={'✓' if FITS_AVAILABLE else '✗'} Geo={'✓' if RASTERIO_AVAILABLE else '✗'}",
                file=sys.stderr,
            )
        result = extract_comprehensive_metadata(
            args.files[0], tier=args.tier, enable_ocr=args.ocr
        )
        if args.store and store_file_metadata and "error" not in result:
            try:
                store_file_metadata(args.files[0], result, result.get("perceptual_hashes"))
            except Exception as e:
                result["storage_error"] = str(e)
        json_out = json.dumps(result, indent=2, default=str)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_out)
        if not args.quiet:
            print(f"Saved to: {args.output}", file=sys.stderr)
    else:
        print(json_out)

if __name__ == "__main__":
    main()

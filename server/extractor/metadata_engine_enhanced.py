#!/usr/bin/env python3
"""
MetaExtract - Enhanced Metadata Extraction Engine v3.2

Performance-optimized version with caching, parallel processing, monitoring,
and advanced forensic analysis capabilities.
"""

import os
import sys
import json
import asyncio
import concurrent.futures
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional, List, Tuple

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import original engine
from .metadata_engine import (
    extract_metadata as _extract_metadata_original,
    TIER_CONFIGS,
    Tier,
    logger as base_logger
)

# Import comprehensive engine
from .comprehensive_metadata_engine import (
    extract_comprehensive_metadata,
    COMPREHENSIVE_TIER_CONFIGS,
    ComprehensiveMetadataExtractor
)


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

# Import advanced analysis modules
from .modules.advanced_analysis import (
    detect_ai_content,
    detect_enhanced_manipulation,
    detect_enhanced_steganography
)

# Import performance utilities
from .utils.cache import (
    get_file_hash_quick,
    get_from_cache,
    set_cache,
    REDIS_AVAILABLE
)
from .utils.performance import (
    PerformanceMonitor,
    optimize_for_file_size,
    check_system_resources
)

# Import advanced analysis modules
try:
    from .modules.steganography import analyze_steganography
    STEGANOGRAPHY_AVAILABLE = True
except ImportError:
    STEGANOGRAPHY_AVAILABLE = False
    logger.warning("Steganography analysis module not available")

try:
    from .modules.manipulation_detection import analyze_manipulation
    MANIPULATION_AVAILABLE = True
except ImportError:
    MANIPULATION_AVAILABLE = False
    logger.warning("Manipulation detection module not available")

try:
    from .modules.comparison import compare_metadata_files, compare_two_metadata_files
    COMPARISON_AVAILABLE = True
except ImportError:
    COMPARISON_AVAILABLE = False
    logger.warning("Comparison module not available")

try:
    from .modules.timeline import reconstruct_timeline, analyze_single_file_timeline
    TIMELINE_AVAILABLE = True
except ImportError:
    TIMELINE_AVAILABLE = False
    logger.warning("Timeline reconstruction module not available")

class EnhancedMetadataExtractor:
    """Enhanced metadata extractor with performance optimizations and advanced analysis."""
    
    def __init__(self, enable_cache: bool = True, max_workers: int = 4):
        self.enable_cache = enable_cache and REDIS_AVAILABLE
        self.max_workers = max_workers
        self.performance_monitor = PerformanceMonitor()
        
        logger.info(f"Enhanced extractor v3.2 initialized (cache: {self.enable_cache}, workers: {max_workers})")
        logger.info(f"Advanced modules: Steganography={STEGANOGRAPHY_AVAILABLE}, Manipulation={MANIPULATION_AVAILABLE}, Comparison={COMPARISON_AVAILABLE}, Timeline={TIMELINE_AVAILABLE}")
    
    def extract_metadata(
        self,
        filepath: str,
        tier: str = "super",
        include_performance_metrics: bool = False,
        enable_advanced_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Extract metadata with performance optimizations and optional advanced analysis.

        Args:
            filepath: Path to file
            tier: Pricing tier
            include_performance_metrics: Include performance data in response
            enable_advanced_analysis: Enable advanced forensic analysis

        Returns:
            Enhanced metadata dictionary with optional advanced analysis
        """
        start_time = datetime.now()

        # Log the start of the extraction
        log_extraction_event(
            event_type="extraction_start",
            filepath=filepath,
            module_name="enhanced_engine",
            status="info",
            details={"tier": tier, "advanced_analysis": enable_advanced_analysis}
        )

        try:
            with self.performance_monitor.measure("total_extraction"):
                result = self._extract_with_optimizations(
                    filepath, tier, include_performance_metrics, enable_advanced_analysis
                )

                # Log successful completion
                duration = (datetime.now() - start_time).total_seconds()
                log_extraction_event(
                    event_type="extraction_complete",
                    filepath=filepath,
                    module_name="enhanced_engine",
                    status="info",
                    duration=duration,
                    details={
                        "tier": tier,
                        "success": True,
                        "advanced_analysis": enable_advanced_analysis
                    }
                )

                return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Critical error in enhanced metadata extraction for {filepath}: {e}")
            logger.debug(f"Full traceback: {sys.exc_info()}")

            # Log the error
            log_extraction_event(
                event_type="extraction_error",
                filepath=filepath,
                module_name="enhanced_engine",
                status="error",
                duration=duration,
                details={
                    "tier": tier,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "success": False,
                    "advanced_analysis": enable_advanced_analysis
                }
            )

            # Return a structured error response
            return {
                "error": f"Critical error in enhanced metadata extraction: {str(e)}",
                "error_type": type(e).__name__,
                "file": {"path": filepath},
                "extraction_info": {
                    "engine_version": "3.2.0",
                    "processing_ms": duration * 1000,
                    "tier": tier
                }
            }
    
    def _extract_with_optimizations(
        self,
        filepath: str,
        tier: str,
        include_performance_metrics: bool,
        enable_advanced_analysis: bool = False
    ) -> Dict[str, Any]:
        """Internal extraction with all optimizations and advanced analysis applied."""

        # Check system resources
        with self.performance_monitor.measure("resource_check"):
            try:
                resources = check_system_resources()
                if not resources["sufficient_memory"]:
                    logger.warning("Low memory detected, disabling cache")
                    self.enable_cache = False
            except Exception as e:
                logger.warning(f"Resource check failed: {e}, continuing with cache enabled")

        # Get file info and optimization settings
        with self.performance_monitor.measure("file_analysis"):
            try:
                file_size = os.path.getsize(filepath)
                optimization_settings = optimize_for_file_size(file_size)
            except Exception as e:
                logger.error(f"Error analyzing file {filepath}: {e}")
                return {"error": f"File analysis failed: {e}", "file": {"path": filepath}}

        # Advanced analysis is controlled by the flag
        advanced_analysis_allowed = enable_advanced_analysis

        # Try cache first (but not for advanced analysis requests)
        cache_key = None
        if self.enable_cache and optimization_settings["use_cache"] and not advanced_analysis_allowed:
            with self.performance_monitor.measure("cache_lookup"):
                try:
                    file_hash = get_file_hash_quick(filepath)
                    cache_key = f"metadata:v4.0:{file_hash}:{tier}"
                    cached_result = get_from_cache(cache_key)

                    if cached_result:
                        logger.info(f"Cache hit for {filepath}")
                        cached_result["extraction_info"]["cache_hit"] = True
                        cached_result["extraction_info"]["processing_ms"] = 0

                        if include_performance_metrics:
                            cached_result["performance_metrics"] = self.performance_monitor.get_metrics()

                        return cached_result
                except Exception as e:
                    logger.warning(f"Cache lookup failed for {filepath}: {e}")

        # Extract metadata using comprehensive engine (v4.0)
        with self.performance_monitor.measure("metadata_extraction"):
            try:
                result = extract_comprehensive_metadata(filepath, tier)

                if "error" in result:
                    logger.warning(f"Comprehensive extraction returned error for {filepath}: {result['error']}")
                    return result

            except Exception as e:
                logger.error(f"Comprehensive metadata extraction failed for {filepath}: {e}")
                return {"error": f"Metadata extraction failed: {e}", "file": {"path": filepath}}

        # Enhance result with performance data
        with self.performance_monitor.measure("result_enhancement"):
            try:
                result = self._enhance_result(result, optimization_settings)
            except Exception as e:
                logger.error(f"Result enhancement failed for {filepath}: {e}")
                # Continue with original result but add error info
                if "processing_errors" not in result:
                    result["processing_errors"] = []
                result["processing_errors"].append({
                    "component": "result_enhancement",
                    "error": str(e),
                    "error_type": type(e).__name__
                })

        # Perform advanced analysis if enabled and allowed
        if advanced_analysis_allowed:
            with self.performance_monitor.measure("advanced_analysis"):
                try:
                    result = self._perform_advanced_analysis(result, filepath, tier)
                except Exception as e:
                    logger.error(f"Advanced analysis failed for {filepath}: {e}")
                    # Add error info to result but continue
                    if "advanced_analysis" not in result:
                        result["advanced_analysis"] = {}
                    result["advanced_analysis"]["error"] = f"Advanced analysis failed: {str(e)}"
                    result["advanced_analysis"]["error_type"] = type(e).__name__

        # Cache the result (but not advanced analysis results due to size)
        if cache_key and self.enable_cache and not advanced_analysis_allowed:
            with self.performance_monitor.measure("cache_storage"):
                try:
                    # Don't cache errors or very large results
                    result_size = len(json.dumps(result, default=str))
                    if result_size < 1024 * 1024:  # 1MB limit
                        set_cache(cache_key, result, ttl_hours=24)
                    else:
                        logger.warning(f"Result too large to cache: {result_size} bytes for {filepath}")
                except Exception as e:
                    logger.warning(f"Cache storage failed for {filepath}: {e}")

        # Add performance metrics if requested
        if include_performance_metrics:
            try:
                result["performance_metrics"] = self.performance_monitor.get_metrics()
                self.performance_monitor.log_performance_summary()
            except Exception as e:
                logger.warning(f"Performance metrics collection failed for {filepath}: {e}")
                if "processing_errors" not in result:
                    result["processing_errors"] = []
                result["processing_errors"].append({
                    "component": "performance_metrics",
                    "error": str(e),
                    "error_type": type(e).__name__
                })

        return result
    
    def _perform_advanced_analysis(self, result: Dict[str, Any], filepath: str, tier: str) -> Dict[str, Any]:
        """Perform advanced forensic analysis on the extracted metadata."""
        start_time = datetime.now()

        log_extraction_event(
            event_type="advanced_analysis_start",
            filepath=filepath,
            module_name="enhanced_engine_advanced",
            status="info",
            details={"tier": tier}
        )

        try:
            advanced_analysis = {
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_tier": tier,
                "modules_available": {
                    "steganography": STEGANOGRAPHY_AVAILABLE,
                    "manipulation_detection": MANIPULATION_AVAILABLE,
                    "comparison": COMPARISON_AVAILABLE,
                    "timeline": TIMELINE_AVAILABLE,
                    "ai_content_detection": True,  # New in v4.0
                    "enhanced_steganography": True,  # Enhanced in v4.0
                    "enhanced_manipulation": True   # Enhanced in v4.0
                },
                "results": {}
            }

            # Determine file type for appropriate analysis
            file_extension = Path(filepath).suffix.lower()
            is_image = file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
            is_video = file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']

            # AI Content Detection (images and videos)
            if tier == "super" and (is_image or is_video):
                try:
                    logger.info(f"Performing AI content detection for {filepath}...")
                    ai_result = detect_ai_content(filepath, result)
                    advanced_analysis["results"]["ai_content_detection"] = ai_result
                except Exception as e:
                    logger.error(f"AI content detection failed for {filepath}: {e}")
                    advanced_analysis["results"]["ai_content_detection"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Enhanced Steganography analysis (images only)
            if is_image:
                try:
                    logger.info(f"Performing enhanced steganography analysis for {filepath}...")
                    stego_result = detect_enhanced_steganography(filepath)
                    advanced_analysis["results"]["enhanced_steganography"] = stego_result
                except Exception as e:
                    logger.error(f"Enhanced steganography analysis failed for {filepath}: {e}")
                    advanced_analysis["results"]["enhanced_steganography"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Enhanced Manipulation detection (images only)
            if is_image:
                try:
                    logger.info(f"Performing enhanced manipulation detection for {filepath}...")
                    manipulation_result = detect_enhanced_manipulation(filepath, result)
                    advanced_analysis["results"]["enhanced_manipulation_detection"] = manipulation_result
                except Exception as e:
                    logger.error(f"Enhanced manipulation detection failed for {filepath}: {e}")
                    advanced_analysis["results"]["enhanced_manipulation_detection"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Legacy steganography analysis (for compatibility)
            if STEGANOGRAPHY_AVAILABLE and is_image:
                try:
                    logger.info(f"Performing legacy steganography analysis for {filepath}...")
                    stego_result = analyze_steganography(filepath)
                    advanced_analysis["results"]["steganography"] = stego_result
                except Exception as e:
                    logger.error(f"Legacy steganography analysis failed for {filepath}: {e}")
                    advanced_analysis["results"]["steganography"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Legacy manipulation detection (for compatibility)
            if MANIPULATION_AVAILABLE and is_image:
                try:
                    logger.info(f"Performing legacy manipulation detection for {filepath}...")
                    manipulation_result = analyze_manipulation(filepath, result)
                    advanced_analysis["results"]["manipulation_detection"] = manipulation_result
                except Exception as e:
                    logger.error(f"Legacy manipulation detection failed for {filepath}: {e}")
                    advanced_analysis["results"]["manipulation_detection"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Timeline analysis (single file)
            if TIMELINE_AVAILABLE:
                try:
                    logger.info(f"Performing timeline analysis for {filepath}...")
                    timeline_result = analyze_single_file_timeline(result)
                    advanced_analysis["results"]["timeline_analysis"] = timeline_result
                except Exception as e:
                    logger.error(f"Timeline analysis failed for {filepath}: {e}")
                    advanced_analysis["results"]["timeline_analysis"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }

            # Add advanced analysis to result
            result["advanced_analysis"] = advanced_analysis

            # Update extraction info
            if "extraction_info" in result:
                result["extraction_info"]["advanced_analysis_enabled"] = True
                result["extraction_info"]["analysis_modules"] = len([
                    k for k, v in advanced_analysis["results"].items()
                    if "error" not in v
                ])
                result["extraction_info"]["engine_version"] = "4.0.0"  # Updated version

            duration = (datetime.now() - start_time).total_seconds()
            log_extraction_event(
                event_type="advanced_analysis_complete",
                filepath=filepath,
                module_name="enhanced_engine_advanced",
                status="info",
                duration=duration,
                details={
                    "tier": tier,
                    "modules_executed": len(advanced_analysis["results"]),
                    "success": True
                }
            )

            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Advanced analysis failed for {filepath}: {e}")
            logger.debug(f"Full traceback: {sys.exc_info()}")

            log_extraction_event(
                event_type="advanced_analysis_error",
                filepath=filepath,
                module_name="enhanced_engine_advanced",
                status="error",
                duration=duration,
                details={
                    "tier": tier,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "success": False
                }
            )

            result["advanced_analysis"] = {
                "error": f"Advanced analysis failed: {str(e)}",
                "error_type": type(e).__name__,
                "analysis_timestamp": datetime.now().isoformat()
            }
            return result
    
    def _enhance_result(
        self,
        result: Dict[str, Any],
        optimization_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance the result with additional computed fields."""
        
        # Add processing performance info
        if "extraction_info" in result:
            result["extraction_info"]["cache_hit"] = False
            result["extraction_info"]["optimization_settings"] = optimization_settings
            result["extraction_info"]["redis_available"] = REDIS_AVAILABLE
        
        # Add file analysis insights
        if "filesystem" in result and result["filesystem"]:
            file_size = result["filesystem"].get("size_bytes", 0)
            
            # Add file size category
            if file_size < 1024 * 1024:  # < 1MB
                size_category = "small"
            elif file_size < 50 * 1024 * 1024:  # < 50MB
                size_category = "medium"
            elif file_size < 500 * 1024 * 1024:  # < 500MB
                size_category = "large"
            else:
                size_category = "very_large"
            
            result["filesystem"]["size_category"] = size_category
        
        # Add processing recommendations
        recommendations = []
        
        if optimization_settings.get("parallel_processing"):
            recommendations.append("File size suitable for parallel processing")
        
        if not optimization_settings.get("use_cache"):
            recommendations.append("File too large for effective caching")
        
        if recommendations:
            result["processing_recommendations"] = recommendations
        
        return result
    
    async def extract_batch(
        self,
        filepaths: List[str],
        tier: str = "super",
        max_concurrent: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from multiple files concurrently.

        Args:
            filepaths: List of file paths
            tier: Pricing tier
            max_concurrent: Maximum concurrent extractions

        Returns:
            Dictionary mapping filepath to metadata result
        """
        start_time = datetime.now()

        log_extraction_event(
            event_type="batch_extraction_start",
            filepath="batch_operation",
            module_name="enhanced_engine_batch",
            status="info",
            details={
                "total_files": len(filepaths),
                "tier": tier,
                "max_concurrent": max_concurrent
            }
        )

        if max_concurrent is None:
            max_concurrent = min(self.max_workers, len(filepaths))

        logger.info(f"Starting batch extraction: {len(filepaths)} files, {max_concurrent} concurrent")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def extract_single(filepath: str) -> Tuple[str, Dict[str, Any]]:
            async with semaphore:
                try:
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        result = await loop.run_in_executor(
                            executor,
                            self.extract_metadata,
                            filepath,
                            tier,
                            False  # Don't include performance metrics for batch
                        )
                    return filepath, result
                except Exception as e:
                    logger.error(f"Error processing {filepath} in batch: {e}")
                    return filepath, {
                        "error": f"Error processing file in batch: {str(e)}",
                        "error_type": type(e).__name__,
                        "file": {"path": filepath},
                        "extraction_info": {
                            "engine_version": "3.2.0",
                            "tier": tier
                        }
                    }

        # Execute all extractions concurrently
        tasks = [extract_single(fp) for fp in filepaths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        batch_results: Dict[str, Any] = {}
        successful = 0
        failed = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch extraction error: {result}")
                failed += 1
            else:
                filepath, metadata = result
                batch_results[filepath] = metadata
                if "error" not in metadata:
                    successful += 1
                else:
                    failed += 1

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Batch extraction complete: {successful} successful, {failed} failed")

        # Log completion
        log_extraction_event(
            event_type="batch_extraction_complete",
            filepath="batch_operation",
            module_name="enhanced_engine_batch",
            status="info",
            duration=duration,
            details={
                "total_files": len(filepaths),
                "successful": successful,
                "failed": failed,
                "tier": tier
            }
        )

        return {
            "results": batch_results,
            "summary": {
                "total_files": len(filepaths),
                "successful": successful,
                "failed": failed,
                "processing_time_ms": self.performance_monitor.get_metrics()["total_runtime_ms"]
            }
        }
    
    async def compare_batch_metadata(
        self,
        filepaths: List[str],
        tier: str = "super",
        comparison_mode: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Compare metadata from multiple files with advanced analysis.

        Args:
            filepaths: List of file paths to compare
            tier: Pricing tier (premium+ required for comparison)
            comparison_mode: "detailed", "summary", or "differences_only"

        Returns:
            Comprehensive comparison results
        """
        start_time = datetime.now()

        log_extraction_event(
            event_type="batch_comparison_start",
            filepath="batch_comparison_operation",
            module_name="enhanced_engine_comparison",
            status="info",
            details={
                "total_files": len(filepaths),
                "tier": tier,
                "comparison_mode": comparison_mode
            }
        )

        if not COMPARISON_AVAILABLE:
            error_result = {"error": "Comparison module not available"}
            log_extraction_event(
                event_type="batch_comparison_error",
                filepath="batch_comparison_operation",
                module_name="enhanced_engine_comparison",
                status="error",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": "Comparison module not available"}
            )
            return error_result

        if tier not in ["premium", "super"]:
            error_result = {"error": "Comparison analysis requires Premium or Super tier"}
            log_extraction_event(
                event_type="batch_comparison_error",
                filepath="batch_comparison_operation",
                module_name="enhanced_engine_comparison",
                status="error",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": "Comparison analysis requires Premium or Super tier"}
            )
            return error_result

        try:
            logger.info(f"Starting batch comparison: {len(filepaths)} files")

            # Extract metadata from all files first
            metadata_list: List[Dict[str, Any]] = []
            for filepath in filepaths:
                metadata = self.extract_metadata(filepath, tier, False, False)
                if "error" not in metadata:
                    metadata_list.append(metadata)
                else:
                    logger.warning(f"Failed to extract metadata from {filepath}: {metadata.get('error')}")

            if len(metadata_list) < 2:
                error_result = {"error": "At least 2 valid files required for comparison"}
                log_extraction_event(
                    event_type="batch_comparison_error",
                    filepath="batch_comparison_operation",
                    module_name="enhanced_engine_comparison",
                    status="error",
                    duration=(datetime.now() - start_time).total_seconds(),
                    details={"error": "At least 2 valid files required for comparison"}
                )
                return error_result

            # Perform comparison
            comparison_result = compare_metadata_files(metadata_list, comparison_mode)

            # Add batch info
            comparison_result["batch_comparison_info"] = {
                "files_processed": len(metadata_list),
                "files_failed": len(filepaths) - len(metadata_list),
                "comparison_mode": comparison_mode,
                "tier": tier,
                "timestamp": datetime.now().isoformat()
            }

            duration = (datetime.now() - start_time).total_seconds()
            log_extraction_event(
                event_type="batch_comparison_complete",
                filepath="batch_comparison_operation",
                module_name="enhanced_engine_comparison",
                status="info",
                duration=duration,
                details={
                    "files_processed": len(metadata_list),
                    "files_failed": len(filepaths) - len(metadata_list),
                    "comparison_mode": comparison_mode,
                    "tier": tier
                }
            )

            return comparison_result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Batch comparison failed: {e}")
            logger.debug(f"Full traceback: {sys.exc_info()}")

            log_extraction_event(
                event_type="batch_comparison_error",
                filepath="batch_comparison_operation",
                module_name="enhanced_engine_comparison",
                status="error",
                duration=duration,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )

            return {"error": f"Batch comparison failed: {str(e)}"}
    
    async def reconstruct_batch_timeline(
        self,
        filepaths: List[str],
        tier: str = "super",
        analysis_mode: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Reconstruct timeline from multiple files' metadata.

        Args:
            filepaths: List of file paths for timeline reconstruction
            tier: Pricing tier (premium+ required for timeline analysis)
            analysis_mode: "comprehensive", "forensic", or "simple"

        Returns:
            Timeline reconstruction results
        """
        start_time = datetime.now()

        log_extraction_event(
            event_type="timeline_reconstruction_start",
            filepath="timeline_reconstruction_operation",
            module_name="enhanced_engine_timeline",
            status="info",
            details={
                "total_files": len(filepaths),
                "tier": tier,
                "analysis_mode": analysis_mode
            }
        )

        if not TIMELINE_AVAILABLE:
            error_result = {"error": "Timeline reconstruction module not available"}
            log_extraction_event(
                event_type="timeline_reconstruction_error",
                filepath="timeline_reconstruction_operation",
                module_name="enhanced_engine_timeline",
                status="error",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": "Timeline reconstruction module not available"}
            )
            return error_result

        if tier not in ["premium", "super"]:
            error_result = {"error": "Timeline reconstruction requires Premium or Super tier"}
            log_extraction_event(
                event_type="timeline_reconstruction_error",
                filepath="timeline_reconstruction_operation",
                module_name="enhanced_engine_timeline",
                status="error",
                duration=(datetime.now() - start_time).total_seconds(),
                details={"error": "Timeline reconstruction requires Premium or Super tier"}
            )
            return error_result

        try:
            logger.info(f"Starting timeline reconstruction: {len(filepaths)} files")

            # Extract metadata from all files first
            metadata_list: List[Dict[str, Any]] = []
            for filepath in filepaths:
                metadata = self.extract_metadata(filepath, tier, False, False)
                if "error" not in metadata:
                    metadata_list.append(metadata)
                else:
                    logger.warning(f"Failed to extract metadata from {filepath}: {metadata.get('error')}")

            if len(metadata_list) == 0:
                error_result = {"error": "No valid files for timeline reconstruction"}
                log_extraction_event(
                    event_type="timeline_reconstruction_error",
                    filepath="timeline_reconstruction_operation",
                    module_name="enhanced_engine_timeline",
                    status="error",
                    duration=(datetime.now() - start_time).total_seconds(),
                    details={"error": "No valid files for timeline reconstruction"}
                )
                return error_result

            # Perform timeline reconstruction
            timeline_result = reconstruct_timeline(metadata_list, analysis_mode)

            # Add batch info
            timeline_result["batch_timeline_info"] = {
                "files_processed": len(metadata_list),
                "files_failed": len(filepaths) - len(metadata_list),
                "analysis_mode": analysis_mode,
                "tier": tier,
                "timestamp": datetime.now().isoformat()
            }

            duration = (datetime.now() - start_time).total_seconds()
            log_extraction_event(
                event_type="timeline_reconstruction_complete",
                filepath="timeline_reconstruction_operation",
                module_name="enhanced_engine_timeline",
                status="info",
                duration=duration,
                details={
                    "files_processed": len(metadata_list),
                    "files_failed": len(filepaths) - len(metadata_list),
                    "analysis_mode": analysis_mode,
                    "tier": tier
                }
            )

            return timeline_result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Timeline reconstruction failed: {e}")
            logger.debug(f"Full traceback: {sys.exc_info()}")

            log_extraction_event(
                event_type="timeline_reconstruction_error",
                filepath="timeline_reconstruction_operation",
                module_name="enhanced_engine_timeline",
                status="error",
                duration=duration,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )

            return {"error": f"Timeline reconstruction failed: {str(e)}"}

async def extract_metadata_enhanced_async(
    filepath: str,
    tier: str = "super",
    include_performance_metrics: bool = False,
    enable_advanced_analysis: bool = False
) -> Dict[str, Any]:
    """
    Asynchronously extract enhanced metadata with performance optimizations.

    This is the async entry point for the enhanced extraction engine.
    """
    loop = asyncio.get_event_loop()
    start_time = datetime.now()

    # Log the start of the extraction
    log_extraction_event(
        event_type="async_extraction_start",
        filepath=filepath,
        module_name="enhanced_engine_async",
        status="info",
        details={"tier": tier, "advanced_analysis": enable_advanced_analysis}
    )

    try:
        # Run the synchronous extraction in a thread pool to avoid blocking the event loop
        extractor = get_enhanced_extractor()
        result = await loop.run_in_executor(
            None,
            extractor.extract_metadata,
            filepath,
            tier,
            include_performance_metrics,
            enable_advanced_analysis
        )

        # Log successful completion
        duration = (datetime.now() - start_time).total_seconds()
        log_extraction_event(
            event_type="async_extraction_complete",
            filepath=filepath,
            module_name="enhanced_engine_async",
            status="info",
            duration=duration,
            details={
                "tier": tier,
                "success": True,
                "advanced_analysis": enable_advanced_analysis
            }
        )

        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Critical error in async enhanced metadata extraction for {filepath}: {e}")
        logger.debug(f"Full traceback: {sys.exc_info()}")

        # Log the error
        log_extraction_event(
            event_type="async_extraction_error",
            filepath=filepath,
            module_name="enhanced_engine_async",
            status="error",
            duration=duration,
            details={
                "tier": tier,
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False,
                "advanced_analysis": enable_advanced_analysis
            }
        )

        # Return a structured error response
        return {
            "error": f"Critical error in async enhanced metadata extraction: {str(e)}",
            "error_type": type(e).__name__,
            "file": {"path": filepath},
            "extraction_info": {
                "engine_version": "3.2.0",
                "processing_ms": duration * 1000,
                "tier": tier
            }
        }


# Global enhanced extractor instance
_enhanced_extractor = None

def get_enhanced_extractor() -> EnhancedMetadataExtractor:
    """Get or create the global enhanced extractor instance."""
    global _enhanced_extractor
    if _enhanced_extractor is None:
        _enhanced_extractor = EnhancedMetadataExtractor()
    return _enhanced_extractor

def extract_metadata_enhanced(
    filepath: str,
    tier: str = "super",
    include_performance_metrics: bool = False
) -> Dict[str, Any]:
    """
    Enhanced metadata extraction with performance optimizations.
    
    This is the main entry point for the enhanced extraction engine.
    """
    extractor = get_enhanced_extractor()
    return extractor.extract_metadata(filepath, tier, include_performance_metrics)

async def extract_batch_metadata(
    filepaths: List[str],
    tier: str = "super",
    max_concurrent: int = 4
) -> Dict[str, Any]:
    """
    Extract metadata from multiple files concurrently.
    """
    extractor = get_enhanced_extractor()
    return await extractor.extract_batch(filepaths, tier, max_concurrent)


async def extract_batch_metadata_async(
    filepaths: List[str],
    tier: str = "super",
    max_concurrent: int = 4
) -> Dict[str, Any]:
    """
    Asynchronously extract metadata from multiple files with enhanced error handling and logging.
    """
    start_time = datetime.now()

    log_extraction_event(
        event_type="async_batch_extraction_start",
        filepath="batch_operation",
        module_name="enhanced_engine_async_batch",
        status="info",
        details={
            "total_files": len(filepaths),
            "tier": tier,
            "max_concurrent": max_concurrent
        }
    )

    try:
        extractor = get_enhanced_extractor()
        result = await extractor.extract_batch(filepaths, tier, max_concurrent)

        duration = (datetime.now() - start_time).total_seconds()
        log_extraction_event(
            event_type="async_batch_extraction_complete",
            filepath="batch_operation",
            module_name="enhanced_engine_async_batch",
            status="info",
            duration=duration,
            details={
                "total_files": len(filepaths),
                "successful": result.get("summary", {}).get("successful", 0),
                "failed": result.get("summary", {}).get("failed", 0),
                "tier": tier
            }
        )

        return result
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Critical error in async batch metadata extraction: {e}")
        logger.debug(f"Full traceback: {sys.exc_info()}")

        log_extraction_event(
            event_type="async_batch_extraction_error",
            filepath="batch_operation",
            module_name="enhanced_engine_async_batch",
            status="error",
            duration=duration,
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
                "processing_ms": duration * 1000,
                "tier": tier,
            },
        }

async def compare_batch_metadata(
    filepaths: List[str],
    tier: str = "super",
    comparison_mode: str = "detailed"
) -> Dict[str, Any]:
    """
    Compare metadata from multiple files with advanced analysis.
    """
    extractor = get_enhanced_extractor()
    return await extractor.compare_batch_metadata(filepaths, tier, comparison_mode)

async def reconstruct_batch_timeline(
    filepaths: List[str],
    tier: str = "super",
    analysis_mode: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Reconstruct timeline from multiple files' metadata.
    """
    extractor = get_enhanced_extractor()
    return await extractor.reconstruct_batch_timeline(filepaths, tier, analysis_mode)

def extract_metadata_enhanced_with_analysis(
    filepath: str,
    tier: str = "super",
    include_performance_metrics: bool = False,
    enable_advanced_analysis: bool = True
) -> Dict[str, Any]:
    """
    Enhanced metadata extraction with advanced forensic analysis.
    
    This function enables advanced analysis features for Premium+ tiers.
    """
    extractor = get_enhanced_extractor()
    return extractor.extract_metadata(filepath, tier, include_performance_metrics, enable_advanced_analysis)

if __name__ == "__main__":
    # CLI interface for enhanced extractor
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced MetaExtract Engine v3.2")
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("--tier", default="super", choices=["free", "starter", "premium", "super"])
    parser.add_argument("--batch", action="store_true", help="Process files in batch mode")
    parser.add_argument("--performance", action="store_true", help="Include performance metrics")
    parser.add_argument("--advanced", action="store_true", help="Enable advanced forensic analysis")
    parser.add_argument("--compare", action="store_true", help="Compare metadata between files (Premium+ only)")
    parser.add_argument("--timeline", action="store_true", help="Reconstruct timeline from files (Premium+ only)")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    if args.compare and len(args.files) > 1:
        # Metadata comparison
        async def main():
            results = await compare_batch_metadata(args.files, args.tier)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            else:
                print(json.dumps(results, indent=2, default=str))
        
        asyncio.run(main())
        
    elif args.timeline and len(args.files) > 0:
        # Timeline reconstruction
        async def main():
            analysis_mode = "forensic" if args.tier == "super" else "comprehensive"
            results = await reconstruct_batch_timeline(args.files, args.tier, analysis_mode)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            else:
                print(json.dumps(results, indent=2, default=str))
        
        asyncio.run(main())
        
    elif args.batch and len(args.files) > 1:
        # Batch processing
        async def main():
            results = await extract_batch_metadata(args.files, args.tier)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            else:
                print(json.dumps(results, indent=2, default=str))
        
        asyncio.run(main())
    else:
        # Single file processing
        for filepath in args.files:
            if args.advanced:
                result = extract_metadata_enhanced_with_analysis(
                    filepath, 
                    args.tier, 
                    args.performance,
                    True
                )
            else:
                result = extract_metadata_enhanced(
                    filepath, 
                    args.tier, 
                    args.performance
                )
            
            if args.output:
                output_file = args.output if len(args.files) == 1 else f"{args.output}_{Path(filepath).stem}.json"
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            else:
                print(json.dumps(result, indent=2, default=str))

"""
Caching-Enabled Extraction Orchestrator for MetaExtract

Extends the base orchestrator with comprehensive caching support.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

from .orchestrator import ExtractionOrchestrator
from .base_engine import ExtractionContext, ExtractionResult, ExtractionStatus
from server.cache.cache_manager import get_cache_manager

logger = logging.getLogger("metaextract.core.caching_orchestrator")


class CachingExtractionOrchestrator(ExtractionOrchestrator):
    """
    Enhanced orchestrator with comprehensive caching support.
    
    Features:
    - Complete extraction result caching
    - Individual module result caching
    - Geocoding result caching
    - Perceptual hash caching
    - Automatic cache invalidation
    - Performance tracking
    """
    
    def __init__(self, extractors: List = None, enable_caching: bool = True):
        """
        Initialize caching orchestrator.
        
        Args:
            extractors: List of extractors to use
            enable_caching: Whether to enable caching
        """
        super().__init__(extractors)
        self.enable_caching = enable_caching
        self.cache_manager = get_cache_manager() if enable_caching else None
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, filepath: str, tier: str = "free", 
                        parallel: bool = True, max_workers: int = 4,
                        force_refresh: bool = False) -> Dict[str, Any]:
        """
        Extract metadata with caching support.
        
        Args:
            filepath: Path to the file
            tier: User tier level
            parallel: Whether to run extractors in parallel
            max_workers: Maximum number of parallel workers
            force_refresh: Force cache refresh
            
        Returns:
            Aggregated metadata result
        """
        start_time = time.time()
        
        try:
            # Check cache first (unless force refresh)
            if self.enable_caching and not force_refresh:
                cached_result = self.cache_manager.get_extraction_result(filepath, tier)
                if cached_result:
                    # Add cache information
                    cached_result['extraction_info']['cache_hit'] = True
                    cached_result['extraction_info']['cache_source'] = 'extraction_cache'
                    
                    processing_time = (time.time() - start_time) * 1000
                    cached_result['extraction_info']['cache_lookup_time_ms'] = processing_time
                    
                    self.logger.info(f"Cache hit for {filepath} (tier: {tier})")
                    return cached_result
            
            # File validation
            if not Path(filepath).exists():
                return self._create_error_result(
                    f"File not found: {filepath}",
                    "FILE_NOT_FOUND",
                    0
                )
            
            # Perform extraction
            self.logger.info(f"Cache miss, extracting metadata for {filepath}")
            
            # Call parent method for actual extraction
            extraction_result = super().extract_metadata(filepath, tier, parallel, max_workers)
            
            # Cache the result if extraction was successful
            if (self.enable_caching and 
                extraction_result.get('status') != 'error' and
                extraction_result.get('metadata')):
                
                processing_time = extraction_result['extraction_info'].get('total_processing_ms', 0)
                file_format = extraction_result.get('processing_summary', {}).get('file_type')
                
                cache_success = self.cache_manager.cache_extraction_result(
                    extraction_result, filepath, tier, file_format, processing_time
                )
                
                if cache_success:
                    self.logger.debug(f"Cached extraction result for {filepath}")
                else:
                    self.logger.warning(f"Failed to cache extraction result for {filepath}")
            
            # Add cache information
            extraction_result['extraction_info']['cache_hit'] = False
            extraction_result['extraction_info']['cache_source'] = 'fresh_extraction'
            
            return extraction_result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Caching orchestration failed: {str(e)}"
            self.logger.error(error_msg)
            
            return self._create_error_result(
                error_msg,
                "CACHING_ORCHESTRATION_FAILED",
                processing_time
            )
    
    def _execute_sequential(self, extractors: List, context: ExtractionContext) -> List[ExtractionResult]:
        """Execute extractors sequentially with module caching."""
        results = []
        
        for extractor in extractors:
            try:
                # Check if this specific extractor result is cached
                if self.enable_caching:
                    module_result = self.cache_manager.get_module_result(
                        extractor.name, context.filepath
                    )
                    if module_result is not None:
                        # Create a cached extraction result
                        cached_extraction_result = ExtractionResult(
                            metadata=module_result,
                            status=ExtractionStatus.SUCCESS,
                            processing_time_ms=0,  # Instant from cache
                            extraction_info={"extractor": extractor.name, "cache_hit": True}
                        )
                        results.append(cached_extraction_result)
                        self.logger.debug(f"Module cache hit for {extractor.name}")
                        continue
                
                # Execute extractor normally
                module_start_time = time.time()
                result = extractor.extract(context)
                module_processing_time = (time.time() - module_start_time) * 1000
                
                # Cache successful module results
                if (self.enable_caching and 
                    result.status == ExtractionStatus.SUCCESS and 
                    result.metadata):
                    
                    cache_success = self.cache_manager.cache_module_result(
                        result.metadata, extractor.name, context.filepath,
                        execution_time_ms=module_processing_time
                    )
                    
                    if cache_success:
                        self.logger.debug(f"Cached module result for {extractor.name}")
                
                results.append(result)
                
                if result.status == ExtractionStatus.SUCCESS:
                    self.logger.debug(f"Extractor {extractor.name} succeeded")
                else:
                    self.logger.warning(f"Extractor {extractor.name} failed: {result.error_message}")
                    
            except Exception as e:
                self.logger.error(f"Extractor {extractor.name} threw exception: {e}")
                failed_result = ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.FAILED,
                    processing_time_ms=0,
                    error_message=f"Exception in {extractor.name}: {str(e)}"
                )
                results.append(failed_result)
        
        return results
    
    def _execute_parallel(self, extractors: List, context: ExtractionContext, max_workers: int) -> List[ExtractionResult]:
        """Execute extractors in parallel with module caching."""
        results = []
        
        # First, check for cached module results
        uncached_extractors = []
        cached_results = []
        
        for extractor in extractors:
            if self.enable_caching:
                module_result = self.cache_manager.get_module_result(
                    extractor.name, context.filepath
                )
                if module_result is not None:
                    # Create cached extraction result
                    cached_extraction_result = ExtractionResult(
                        metadata=module_result,
                        status=ExtractionStatus.SUCCESS,
                        processing_time_ms=0,  # Instant from cache
                        extraction_info={"extractor": extractor.name, "cache_hit": True}
                    )
                    cached_results.append(cached_extraction_result)
                    self.logger.debug(f"Module cache hit for {extractor.name}")
                    continue
            
            uncached_extractors.append(extractor)
        
        # Execute uncached extractors in parallel
        if uncached_extractors:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_extractor = {
                    executor.submit(self._execute_single_extractor, extractor, context): extractor 
                    for extractor in uncached_extractors
                }
                
                for future in as_completed(future_to_extractor):
                    extractor = future_to_extractor[future]
                    try:
                        result = future.result(timeout=30)
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"Parallel extractor {extractor.name} failed: {e}")
                        failed_result = ExtractionResult(
                            metadata={},
                            status=ExtractionStatus.FAILED,
                            processing_time_ms=0,
                            error_message=f"Exception in parallel {extractor.name}: {str(e)}"
                        )
                        results.append(failed_result)
        
        # Combine cached and fresh results
        return cached_results + results
    
    def _execute_single_extractor(self, extractor, context: ExtractionContext) -> ExtractionResult:
        """Execute a single extractor with caching support."""
        try:
            module_start_time = time.time()
            result = extractor.extract(context)
            module_processing_time = (time.time() - module_start_time) * 1000
            
            # Cache successful module results
            if (self.enable_caching and 
                result.status == ExtractionStatus.SUCCESS and 
                result.metadata):
                
                cache_success = self.cache_manager.cache_module_result(
                    result.metadata, extractor.name, context.filepath,
                    execution_time_ms=module_processing_time
                )
                
                if cache_success:
                    self.logger.debug(f"Cached module result for {extractor.name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Extractor {extractor.name} failed: {e}")
            return ExtractionResult(
                metadata={},
                status=ExtractionStatus.FAILED,
                processing_time_ms=0,
                error_message=f"Exception in {extractor.name}: {str(e)}"
            )
    
    def invalidate_file_cache(self, filepath: str) -> int:
        """
        Invalidate all cached results for a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Number of invalidated cache entries
        """
        if not self.enable_caching:
            return 0
        
        try:
            count = self.cache_manager.invalidate_file(filepath)
            self.logger.info(f"Invalidated {count} cache entries for {filepath}")
            return count
        except Exception as e:
            self.logger.error(f"Error invalidating cache for {filepath}: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Cache statistics
        """
        if not self.enable_caching:
            return {"caching_enabled": False}
        
        try:
            return self.cache_manager.get_stats()
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary showing cache effectiveness.
        
        Returns:
            Performance summary
        """
        if not self.enable_caching:
            return {"caching_enabled": False}
        
        try:
            return self.cache_manager.get_performance_summary()
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on caching system.
        
        Returns:
            Health check results
        """
        if not self.enable_caching:
            return {"caching_enabled": False}
        
        try:
            return self.cache_manager.health_check()
        except Exception as e:
            self.logger.error(f"Error performing health check: {e}")
            return {"error": str(e)}
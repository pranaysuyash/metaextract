"""
Extraction orchestrator for MetaExtract.

Coordinates multiple extractors and manages the overall extraction process,
including tier-based configuration, parallel execution, and result aggregation.
"""

import logging
import time
import asyncio
import traceback
from typing import Any, Dict, List, Optional, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .base_engine import BaseExtractor, ExtractionContext, ExtractionResult, ExtractionStatus
from ..exceptions.extraction_exceptions import ExtractionOrchestratorError

logger = logging.getLogger(__name__)


class ExtractionOrchestrator:
    """
    Orchestrates metadata extraction across multiple extractors.
    
    Manages the extraction process, including extractor selection,
    parallel execution, result aggregation, and error handling.
    """
    
    def __init__(self, extractors: List[BaseExtractor] = None):
        """
        Initialize the orchestrator.
        
        Args:
            extractors: List of extractors to use (optional)
        """
        self.extractors = extractors or []
        self.logger = logging.getLogger(__name__)
        self._executor = None
    
    def add_extractor(self, extractor: BaseExtractor) -> None:
        """
        Add an extractor to the orchestrator.
        
        Args:
            extractor: Extractor to add
        """
        self.extractors.append(extractor)
        self.logger.info(f"Added extractor: {extractor.name}")
    
    def remove_extractor(self, extractor_name: str) -> bool:
        """
        Remove an extractor by name.
        
        Args:
            extractor_name: Name of the extractor to remove
            
        Returns:
            True if extractor was found and removed
        """
        initial_count = len(self.extractors)
        self.extractors = [e for e in self.extractors if e.name != extractor_name]
        removed = len(self.extractors) < initial_count
        if removed:
            self.logger.info(f"Removed extractor: {extractor_name}")
        return removed
    
    def get_suitable_extractors(self, filepath: str, tier: str = "free") -> List[BaseExtractor]:
        """
        Get extractors suitable for the given file and tier.
        
        Args:
            filepath: Path to the file
            tier: User tier level
            
        Returns:
            List of suitable extractors
        """
        suitable = []
        
        for extractor in self.extractors:
            # Check if extractor can handle this file type
            if not extractor.can_extract(filepath):
                continue
                
            # For specialized extractors, check availability
            from .base_engine import SpecializedExtractor
            if isinstance(extractor, SpecializedExtractor):
                if not extractor.is_available():
                    continue
            
            suitable.append(extractor)
        
        # Sort by priority (more specific extractors first)
        suitable.sort(key=lambda e: len(e.supported_formats) if e.supported_formats else 0, reverse=True)
        
        return suitable
    
    def extract_metadata(self, filepath: str, tier: str = "free", 
                        parallel: bool = True, max_workers: int = 4) -> Dict[str, Any]:
        """
        Extract metadata from a file using suitable extractors.
        
        Args:
            filepath: Path to the file
            tier: User tier level
            parallel: Whether to run extractors in parallel
            max_workers: Maximum number of parallel workers
            
        Returns:
            Aggregated metadata result
        """
        start_time = time.time()
        
        try:
            # Validate file exists
            if not Path(filepath).exists():
                return self._create_error_result(
                    f"File not found: {filepath}",
                    "FILE_NOT_FOUND",
                    0
                )
            
            # Create extraction context
            context = self._create_extraction_context(filepath, tier)
            
            # Get suitable extractors
            suitable_extractors = self.get_suitable_extractors(filepath, tier)
            if not suitable_extractors:
                return self._create_error_result(
                    f"No suitable extractors found for file: {filepath}",
                    "NO_SUITABLE_EXTRACTORS",
                    0
                )
            
            self.logger.info(f"Using {len(suitable_extractors)} extractors for {filepath}")
            
            # Execute extractors
            if parallel and len(suitable_extractors) > 1:
                results = self._execute_parallel(suitable_extractors, context, max_workers)
            else:
                results = self._execute_sequential(suitable_extractors, context)
            
            # Aggregate results
            aggregated_result = self._aggregate_results(results, context)
            
            # Add timing information
            total_time = (time.time() - start_time) * 1000
            aggregated_result["extraction_info"]["total_processing_ms"] = total_time
            aggregated_result["extraction_info"]["extractors_used"] = len(suitable_extractors)
            
            return aggregated_result
            
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            error_msg = f"Orchestration failed: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return self._create_error_result(
                error_msg,
                "ORCHESTRATION_FAILED",
                total_time
            )
    
    def _create_extraction_context(self, filepath: str, tier: str) -> ExtractionContext:
        """Create extraction context for a file."""
        file_path = Path(filepath)
        file_size = file_path.stat().st_size
        file_extension = file_path.suffix.lower()
        
        # Simple MIME type detection
        mime_type = self._detect_mime_type(file_extension)
        
        return ExtractionContext(
            filepath=filepath,
            file_size=file_size,
            file_extension=file_extension,
            mime_type=mime_type,
            tier=tier,
            processing_options={},
            execution_stats={}
        )
    
    def _detect_mime_type(self, file_extension: str) -> str:
        """Simple MIME type detection based on file extension."""
        mime_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        return mime_mapping.get(file_extension.lower(), 'application/octet-stream')
    
    def _execute_sequential(self, extractors: List[BaseExtractor], 
                           context: ExtractionContext) -> List[ExtractionResult]:
        """Execute extractors sequentially."""
        results = []
        
        for extractor in extractors:
            try:
                result = extractor.extract(context)
                results.append(result)
                
                if result.status == ExtractionStatus.SUCCESS:
                    self.logger.debug(f"Extractor {extractor.name} succeeded")
                else:
                    self.logger.warning(f"Extractor {extractor.name} failed: {result.error_message}")
                    
            except Exception as e:
                self.logger.error(f"Extractor {extractor.name} threw exception: {e}")
                # Create a failed result for this extractor
                failed_result = ExtractionResult(
                    metadata={},
                    status=ExtractionStatus.FAILED,
                    processing_time_ms=0,
                    error_message=f"Exception in {extractor.name}: {str(e)}"
                )
                results.append(failed_result)
        
        return results
    
    def _execute_parallel(self, extractors: List[BaseExtractor], 
                         context: ExtractionContext, max_workers: int) -> List[ExtractionResult]:
        """Execute extractors in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all extraction tasks
            future_to_extractor = {
                executor.submit(extractor.extract, context): extractor 
                for extractor in extractors
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_extractor):
                extractor = future_to_extractor[future]
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                    
                    if result.status == ExtractionStatus.SUCCESS:
                        self.logger.debug(f"Parallel extractor {extractor.name} succeeded")
                    else:
                        self.logger.warning(f"Parallel extractor {extractor.name} failed: {result.error_message}")
                        
                except Exception as e:
                    self.logger.error(f"Parallel extractor {extractor.name} failed with exception: {e}")
                    failed_result = ExtractionResult(
                        metadata={},
                        status=ExtractionStatus.FAILED,
                        processing_time_ms=0,
                        error_message=f"Exception in parallel {extractor.name}: {str(e)}"
                    )
                    results.append(failed_result)
        
        return results
    
    def _aggregate_results(self, results: List[ExtractionResult], 
                          context: ExtractionContext) -> Dict[str, Any]:
        """Aggregate results from multiple extractors."""
        aggregated_metadata = {}
        extraction_info = {
            "orchestrator_version": "1.0.0",
            "extractor_results": [],
            "total_extractors": len(results),
            "successful_extractors": 0,
            "failed_extractors": 0,
            "skipped_extractors": 0
        }
        
        warnings = []
        total_processing_time = 0
        
        # Aggregate metadata and statistics
        for result in results:
            total_processing_time += result.processing_time_ms
            
            # Add metadata to aggregated result
            if result.metadata:
                # Use extractor name as namespace to avoid conflicts
                if result.status == ExtractionStatus.SUCCESS:
                    aggregated_metadata.update(result.metadata)
                else:
                    # For failed extractions, store under a separate key
                    extractor_name = result.extraction_info.get("extractor", "unknown")
                    aggregated_metadata[f"failed_{extractor_name}"] = result.metadata
            
            # Update statistics
            if result.status == ExtractionStatus.SUCCESS:
                extraction_info["successful_extractors"] += 1
            elif result.status == ExtractionStatus.FAILED:
                extraction_info["failed_extractors"] += 1
            elif result.status == ExtractionStatus.SKIPPED:
                extraction_info["skipped_extractors"] += 1
            
            # Collect warnings and error messages
            if result.warnings:
                warnings.extend(result.warnings)
            
            # Store individual extractor result info
            extractor_info = {
                "extractor": result.extraction_info.get("extractor", "unknown"),
                "status": result.status.value,
                "processing_time_ms": result.processing_time_ms
            }
            
            if result.error_message:
                extractor_info["error"] = result.error_message
            
            extraction_info["extractor_results"].append(extractor_info)
        
        # Determine overall status
        if extraction_info["successful_extractors"] > 0:
            overall_status = "success"
        elif extraction_info["failed_extractors"] > 0:
            overall_status = "partial_success"
        else:
            overall_status = "failed"
        
        return {
            "metadata": aggregated_metadata,
            "extraction_info": extraction_info,
            "status": overall_status,
            "warnings": warnings if warnings else None,
            "processing_summary": {
                "total_processing_time_ms": total_processing_time,
                "file_type": context.file_extension,
                "tier": context.tier
            }
        }
    
    def _create_error_result(self, error_message: str, error_code: str, 
                           processing_time_ms: float) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "metadata": {},
            "extraction_info": {
                "orchestrator_version": "1.0.0",
                "error": True,
                "error_code": error_code,
                "error_message": error_message,
                "processing_time_ms": processing_time_ms
            },
            "status": "error",
            "error": {
                "code": error_code,
                "message": error_message,
                "processing_time_ms": processing_time_ms
            }
        }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor') and self._executor:
            self._executor.shutdown(wait=False)
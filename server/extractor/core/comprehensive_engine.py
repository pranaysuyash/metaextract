"""
New Comprehensive Metadata Engine - Refactored Version

This is the refactored version of the comprehensive metadata engine that uses
the new extractor architecture with proper separation of concerns.
"""

import logging
import time
import os
from pathlib import Path
from typing import Any, Dict, Optional, List

from .orchestrator import ExtractionOrchestrator
from .base_engine import ExtractionContext
from ..extractors.image_extractor import ImageExtractor
from ..exceptions.extraction_exceptions import MetaExtractException

logger = logging.getLogger(__name__)


class NewComprehensiveMetadataExtractor:
    """
    Refactored comprehensive metadata extractor using the new architecture.
    
    This class serves as a compatibility layer while we transition from the
    old monolithic engine to the new modular architecture.
    """
    
    def __init__(self):
        """Initialize the new comprehensive extractor."""
        self.orchestrator = ExtractionOrchestrator()
        self._setup_extractors()
        self.logger = logging.getLogger(__name__)
    
    def _setup_extractors(self):
        """Set up the extractors for the orchestrator."""
        # Add image extractor
        self.orchestrator.add_extractor(ImageExtractor())
        
        # TODO: Add other extractors as they are created
        # self.orchestrator.add_extractor(VideoExtractor())
        # self.orchestrator.add_extractor(AudioExtractor())
        # self.orchestrator.add_extractor(DocumentExtractor())
        # self.orchestrator.add_extractor(ScientificExtractor())
    
    def extract_comprehensive_metadata(self, filepath: str, tier: str = "super") -> Dict[str, Any]:
        """
        Extract comprehensive metadata using the new architecture.
        
        Args:
            filepath: Path to the file
            tier: User tier level
            
        Returns:
            Dictionary containing extracted metadata
        """
        start_time = time.time()
        
        try:
            # Use the orchestrator to extract metadata
            result = self.orchestrator.extract_metadata(filepath, tier=tier, parallel=True)
            
            # Add registry summary for frontend compatibility
            result = self._add_registry_summary(result)
            
            # Add compatibility layer information
            processing_time = (time.time() - start_time) * 1000
            
            # Ensure the result has the expected structure
            if "extraction_info" not in result:
                result["extraction_info"] = {}
            
            result["extraction_info"].update({
                "engine_version": "4.1.0-refactored",
                "architecture": "modular",
                "processing_time_ms": processing_time,
                "compatibility_mode": True
            })
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            error_msg = f"Comprehensive extraction failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "metadata": {},
                "extraction_info": {
                    "error": True,
                    "error_message": error_msg,
                    "error_type": type(e).__name__,
                    "processing_time_ms": processing_time,
                    "engine_version": "4.1.0-refactored"
                },
                "status": "error"
            }
    
    def get_extractor_info(self) -> Dict[str, Any]:
        """Get information about the extractors."""
        extractors_info = []
        for extractor in self.orchestrator.extractors:
            extractors_info.append(extractor.get_extraction_info())
        
        return {
            "engine_version": "4.1.0-refactored",
            "architecture": "modular",
            "extractors": extractors_info,
            "orchestrator_available": True
        }
    
    def _add_registry_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add registry summary for frontend compatibility.
        
        Args:
            result: The extraction result
            
        Returns:
            Updated result with registry summary
        """
        metadata = result.get('metadata', {})
        
        # Create registry summary for different file types
        registry_summary = {}
        
        # Image registry summary
        if any(key in metadata for key in ['exif', 'iptc', 'xmp', 'pil']):
            registry_summary['image'] = {
                'exif': len(metadata.get('exif', {})),
                'iptc': len(metadata.get('iptc', {})),
                'xmp': len(metadata.get('xmp', {})),
                'mobile': 0,  # Will be populated when mobile extractor is added
                'perceptual_hashes': 0,  # Will be populated when hash extractor is added
            }
        
        # Video registry summary (when video extractor is added)
        if 'video' in metadata:
            registry_summary['video'] = {
                'format': len(metadata.get('video', {})),
                'codec': 0,
                'telemetry': 0,
            }
        
        # Audio registry summary (when audio extractor is added)
        if 'audio' in metadata:
            registry_summary['audio'] = {
                'id3': len(metadata.get('audio', {})),
                'codec': 0,
                'broadcast': 0,
            }
        
        # Add registry summary to result
        if registry_summary:
            result['registry_summary'] = registry_summary
        
        return result


# Compatibility function that matches the original API
def extract_comprehensive_metadata_new(filepath: str, tier: str = "super") -> Dict[str, Any]:
    """
    Extract comprehensive metadata using the new refactored engine.
    
    This function provides compatibility with the original API while
    using the new modular architecture.
    
    Args:
        filepath: Path to the file
        tier: User tier level
        
    Returns:
        Dictionary containing extracted metadata
    """
    extractor = NewComprehensiveMetadataExtractor()
    return extractor.extract_comprehensive_metadata(filepath, tier)


# Create a singleton instance for efficiency
_default_extractor = None

def get_default_extractor() -> NewComprehensiveMetadataExtractor:
    """Get the default comprehensive extractor instance."""
    global _default_extractor
    if _default_extractor is None:
        _default_extractor = NewComprehensiveMetadataExtractor()
    return _default_extractor


def extract_comprehensive_metadata(filepath: str, tier: str = "super") -> Dict[str, Any]:
    """
    Convenience function using the default extractor.
    
    Args:
        filepath: Path to the file
        tier: User tier level
        
    Returns:
        Dictionary containing extracted metadata
    """
    extractor = get_default_extractor()
    return extractor.extract_comprehensive_metadata(filepath, tier)
"""
Extension Mapper for Unified Field Registry

This module provides integration between the field registry and
the existing extension system (DICOM, Image, Audio, Video extensions).
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from unified_field_registry import FieldRegistryCore, FieldRegistryError
from field_definitions import FieldDefinition, FieldSource

logger = logging.getLogger(__name__)


@dataclass
class ExtensionInfo:
    """Information about an extension"""
    extension_id: str
    name: str
    description: str
    version: str = "1.0.0"
    supported_fields: List[str] = None
    file_types: List[str] = None
    priority: int = 0
    is_active: bool = True
    
    def __post_init__(self):
        if self.supported_fields is None:
            self.supported_fields = []
        if self.file_types is None:
            self.file_types = []


class ExtensionMapper:
    """
    Maps fields to their compatible extraction extensions.
    
    Integrates with the existing extension registry system to:
    - Track which extensions support which fields
    - Find the best extension for a given field
    - Generate coverage reports
    - Validate extension compatibility
    """
    
    def __init__(self, field_registry: Optional[FieldRegistryCore] = None):
        """
        Initialize the extension mapper.
        
        Args:
            field_registry: Optional field registry instance
        """
        self.registry = field_registry
        self._extension_field_map: Dict[str, List[str]] = {}
        self._extension_info: Dict[str, ExtensionInfo] = {}
        self._field_extension_map: Dict[str, List[str]] = {}
        self._init_builtin_extensions()
    
    def _init_builtin_extensions(self) -> None:
        """Initialize built-in extension mappings"""
        
        # Image extensions
        self._register_extension(
            extension_id="image_basic",
            name="Basic Image",
            description="Basic image metadata extraction",
            version="1.0.0",
            file_types=[".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            supported_fields=[
                "width", "height", "format", "mode", "has_transparency"
            ],
            priority=10
        )
        
        self._register_extension(
            extension_id="image_advanced",
            name="Advanced Image",
            description="Advanced image metadata with EXIF/IPTC/XMP",
            version="1.0.0",
            file_types=[".jpg", ".jpeg", ".png", ".tiff", ".webp"],
            supported_fields=[
                "Make", "Model", "DateTimeOriginal", "ExposureTime", "FNumber",
                "ISOSpeedRatings", "FocalLength", "GPSLatitude", "GPSLongitude",
                "Software", "Artist", "Copyright", "ImageDescription",
                "Keywords", "Headline", "Caption-Abstract"
            ],
            priority=20
        )
        
        self._register_extension(
            extension_id="image_enhanced",
            name="Enhanced Image",
            description="Enhanced image analysis with perceptual hashes",
            version="1.0.0",
            file_types=[".jpg", ".jpeg", ".png", ".webp"],
            supported_fields=[
                "perceptual_hash", "ahash", "phash", "dhash", "whash",
                "color_histogram", "dominant_colors", "quality_score"
            ],
            priority=30
        )
        
        self._register_extension(
            extension_id="image_master",
            name="Image Master",
            description="Comprehensive image extraction combining all modules",
            version="1.0.0",
            file_types=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            supported_fields=[],  # Will aggregate from all image extensions
            priority=50
        )
        
        # DICOM extensions
        self._register_extension(
            extension_id="dicom_base",
            name="DICOM Base",
            description="Basic DICOM metadata extraction",
            version="1.0.0",
            file_types=[".dcm", ".dicom"],
            supported_fields=[
                "PatientName", "PatientID", "StudyDate", "Modality",
                "StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID",
                "Rows", "Columns", "BitsAllocated"
            ],
            priority=10
        )
        
        self._register_extension(
            extension_id="dicom_cardiology",
            name="DICOM Cardiology",
            description="Cardiology-specific DICOM fields",
            version="1.0.0",
            file_types=[".dcm", ".dicom"],
            supported_fields=[
                "HeartRate", "LVEF", "CardiacCyclePosition",
                "AcquisitionDate", "AcquisitionTime"
            ],
            priority=20
        )
        
        self._register_extension(
            extension_id="dicom_neurology",
            name="DICOM Neurology",
            description="Neurology-specific DICOM fields",
            version="1.0.0",
            file_types=[".dcm", ".dicom"],
            supported_fields=[
                "BrainVolume", "SliceThickness", "SequenceName"
            ],
            priority=20
        )
        
        self._register_extension(
            extension_id="dicom_radiology",
            name="DICOM Radiology",
            description="Radiology-specific DICOM fields",
            version="1.0.0",
            file_types=[".dcm", ".dicom"],
            supported_fields=[
                "BodyPartExamined", "ProtocolName", "StudyID",
                "SeriesNumber", "InstanceNumber"
            ],
            priority=20
        )
        
        # Audio extensions
        self._register_extension(
            extension_id="audio_basic",
            name="Basic Audio",
            description="Basic audio metadata extraction",
            version="1.0.0",
            file_types=[".mp3", ".wav", ".flac", ".aac", ".ogg"],
            supported_fields=[
                "Duration", "SampleRate", "Channels", "BitDepth",
                "BitRate", "Format", "Codec"
            ],
            priority=10
        )
        
        self._register_extension(
            extension_id="audio_id3",
            name="Audio ID3",
            description="ID3 tag extraction for MP3 files",
            version="1.0.0",
            file_types=[".mp3"],
            supported_fields=[
                "Title", "Artist", "Album", "Year", "TrackNumber",
                "Genre", "Comment", "AlbumArt", "Compilation"
            ],
            priority=15
        )
        
        self._register_extension(
            extension_id="audio_vorbis",
            name="Audio Vorbis",
            description="Vorbis comment extraction",
            version="1.0.0",
            file_types=[".ogg", ".oga"],
            supported_fields=[
                "TITLE", "ARTIST", "ALBUM", "DATE", "TRACKNUMBER",
                "GENRE", "DESCRIPTION", "METADATA_BLOCK_PICTURE"
            ],
            priority=15
        )
        
        # Video extensions
        self._register_extension(
            extension_id="video_basic",
            name="Basic Video",
            description="Basic video metadata extraction",
            version="1.0.0",
            file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
            supported_fields=[
                "Duration", "Width", "Height", "FrameRate", "BitRate",
                "Codec", "Format", "Profile", "Level"
            ],
            priority=10
        )
        
        self._register_extension(
            extension_id="video_quicktime",
            name="QuickTime",
            description="QuickTime/MP4 specific metadata",
            version="1.0.0",
            file_types=[".mp4", ".mov", ".m4v"],
            supported_fields=[
                "TrackDuration", "MediaDuration", "GraphicsMode",
                "OpColor", "CompressorName", "PixelAspectRatio"
            ],
            priority=15
        )
        
        # Document extensions
        self._register_extension(
            extension_id="document_pdf",
            name="PDF Document",
            description="PDF document metadata extraction",
            version="1.0.0",
            file_types=[".pdf"],
            supported_fields=[
                "Title", "Author", "Subject", "Keywords", "Creator",
                "Producer", "CreationDate", "ModificationDate",
                "PageCount", "PDFVersion"
            ],
            priority=10
        )
        
        # Container/General extensions
        self._register_extension(
            extension_id="container_general",
            name="General Container",
            description="Generic container format extraction",
            version="1.0.0",
            file_types=[".mkv", ".webm", ".mp4", ".avi", ".mov"],
            supported_fields=[
                "ContainerType", "Duration", "TrackCount", "FileSize"
            ],
            priority=5
        )
        
        logger.info(f"Initialized {len(self._extension_info)} built-in extensions")
    
    def _register_extension(
        self,
        extension_id: str,
        name: str,
        description: str,
        version: str,
        file_types: List[str],
        supported_fields: List[str],
        priority: int
    ) -> None:
        """Register a built-in extension"""
        info = ExtensionInfo(
            extension_id=extension_id,
            name=name,
            description=description,
            version=version,
            file_types=file_types,
            supported_fields=supported_fields,
            priority=priority
        )
        
        self._extension_info[extension_id] = info
        self._extension_field_map[extension_id] = supported_fields.copy()
        
        for field_name in supported_fields:
            if field_name not in self._field_extension_map:
                self._field_extension_map[field_name] = []
            if extension_id not in self._field_extension_map[field_name]:
                self._field_extension_map[field_name].append(extension_id)
    
    def register_extension(
        self,
        extension_id: str,
        name: str,
        description: str,
        supported_fields: List[str],
        file_types: Optional[List[str]] = None,
        version: str = "1.0.0",
        priority: int = 0
    ) -> None:
        """
        Register a custom extension.
        
        Args:
            extension_id: Unique identifier for extension
            name: Human-readable name
            description: Description of extension
            supported_fields: List of field names this extension supports
            file_types: List of supported file extensions
            version: Extension version
            priority: Priority for extension selection (higher = preferred)
        """
        if extension_id in self._extension_info:
            logger.warning(f"Extension '{extension_id}' already registered, updating")
        
        info = ExtensionInfo(
            extension_id=extension_id,
            name=name,
            description=description,
            version=version,
            file_types=file_types or [],
            supported_fields=supported_fields,
            priority=priority
        )
        
        self._extension_info[extension_id] = info
        self._extension_field_map[extension_id] = supported_fields.copy()
        
        for field_name in supported_fields:
            if field_name not in self._field_extension_map:
                self._field_extension_map[field_name] = []
            if extension_id not in self._field_extension_map[field_name]:
                self._field_extension_map[field_name].append(extension_id)
        
        if self.registry:
            self._sync_with_registry(extension_id, supported_fields)
        
        logger.info(f"Registered extension: {extension_id} ({name})")
    
    def unregister_extension(self, extension_id: str) -> bool:
        """
        Unregister an extension.
        
        Args:
            extension_id: Extension to unregister
            
        Returns:
            True if extension was removed
        """
        if extension_id not in self._extension_info:
            return False
        
        del self._extension_info[extension_id]
        
        supported_fields = self._extension_field_map.pop(extension_id, [])
        
        for field_name in supported_fields:
            if field_name in self._field_extension_map:
                if extension_id in self._field_extension_map[field_name]:
                    self._field_extension_map[field_name].remove(extension_id)
        
        logger.info(f"Unregistered extension: {extension_id}")
        return True
    
    def _sync_with_registry(
        self,
        extension_id: str,
        supported_fields: List[str]
    ) -> None:
        """Sync extension fields with registry"""
        if not self.registry:
            return
        
        for field_name in supported_fields:
            field = self.registry.get_field(field_name)
            if field and extension_id not in field.compatible_extensions:
                field.compatible_extensions.append(extension_id)
    
    def get_extension_for_field(self, field_name: str) -> List[str]:
        """Get extensions that can extract a given field"""
        return self._field_extension_map.get(field_name, [])
    
    def get_fields_for_extension(self, extension_id: str) -> List[str]:
        """Get all fields supported by an extension"""
        return self._extension_field_map.get(extension_id, [])
    
    def get_extension_info(self, extension_id: str) -> Optional[ExtensionInfo]:
        """Get information about an extension"""
        return self._extension_info.get(extension_id)
    
    def get_all_extensions(self) -> Dict[str, ExtensionInfo]:
        """Get all registered extensions"""
        return self._extension_info.copy()
    
    def get_active_extensions(self) -> Dict[str, ExtensionInfo]:
        """Get all active extensions"""
        return {
            ext_id: info
            for ext_id, info in self._extension_info.items()
            if info.is_active
        }
    
    def get_best_extension(
        self,
        field_name: str,
        file_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the best extension for extracting a field.
        
        Args:
            field_name: Name of the field
            file_type: Optional file type to filter by
            
        Returns:
            Extension ID or None
        """
        extensions = self.get_extension_for_field(field_name)
        if not extensions:
            return None
        
        candidates = []
        for ext_id in extensions:
            info = self._extension_info.get(ext_id)
            if not info or not info.is_active:
                continue
            
            if file_type:
                file_ext = file_type.lower()
                if not any(file_ext in ft.lower() for ft in info.file_types):
                    continue
            
            candidates.append((info.priority, ext_id))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1]
    
    def get_extensions_for_file(
        self,
        file_type: str
    ) -> List[str]:
        """
        Get all extensions that support a file type.
        
        Args:
            file_type: File extension (e.g., '.jpg', '.dcm')
            
        Returns:
            List of extension IDs
        """
        file_ext = file_type.lower()
        extensions = []
        
        for ext_id, info in self._extension_info.items():
            if not info.is_active:
                continue
            
            if any(file_ext in ft.lower() for ft in info.file_types):
                extensions.append(ext_id)
        
        extensions.sort(
            key=lambda x: self._extension_info[x].priority,
            reverse=True
        )
        
        return extensions
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Generate a comprehensive coverage report"""
        report = {
            "extensions": {},
            "field_coverage": {},
            "gaps": [],
            "summary": {}
        }
        
        if not self.registry:
            report["error"] = "No registry available"
            return report
        
        all_fields = set(self.registry.get_all_field_names())
        covered_fields = set()
        
        for ext_id, info in self._extension_info.items():
            fields = self.get_fields_for_extension(ext_id)
            
            report["extensions"][ext_id] = {
                "name": info.name,
                "description": info.description,
                "version": info.version,
                "field_count": len(fields),
                "file_types": info.file_types,
                "priority": info.priority,
                "is_active": info.is_active
            }
            
            covered_fields.update(fields)
        
        report["field_coverage"] = {
            "total_fields_in_registry": len(all_fields),
            "fields_with_extensions": len(covered_fields),
            "coverage_percent": round(
                len(covered_fields) / len(all_fields) * 100, 2
            ) if all_fields else 0
        }
        
        for field_name in sorted(all_fields):
            field = self.registry.get_field(field_name)
            if not field:
                continue
            
            extensions = self.get_extension_for_field(field_name)
            
            report["field_coverage"][field_name] = {
                "source": field.source.value,
                "type": field.field_type.value,
                "tier": field.tier.value,
                "extensions": extensions,
                "has_coverage": len(extensions) > 0
            }
        
        uncovered = all_fields - covered_fields
        for field_name in uncovered:
            field = self.registry.get_field(field_name)
            if field and not field.is_deprecated:
                report["gaps"].append({
                    "field": field_name,
                    "source": field.source.value,
                    "type": field.field_type.value,
                    "tier": field.tier.value,
                    "priority": self._calculate_gap_priority(field)
                })
        
        report["gaps"].sort(key=lambda x: x["priority"], reverse=True)
        
        report["summary"] = {
            "total_extensions": len(self._extension_info),
            "active_extensions": len(self.get_active_extensions()),
            "total_fields": len(all_fields),
            "covered_fields": len(covered_fields),
            "uncovered_fields": len(uncovered),
            "coverage_percent": report["field_coverage"]["coverage_percent"]
        }
        
        return report
    
    def _calculate_gap_priority(self, field: FieldDefinition) -> float:
        """Calculate priority score for a field gap"""
        priority = 0.0
        
        # High priority for free/professional tier
        if field.tier.value in ["free", "professional"]:
            priority += 3.0
        
        # Priority for common sources
        if field.source.value in ["EXIF", "IPTC", "XMP"]:
            priority += 2.0
        
        # Priority for commonly used types
        if field.field_type.value in ["string", "integer", "datetime"]:
            priority += 1.0
        
        return priority
    
    def suggest_extension_for_gap(
        self,
        field_name: str,
        file_types: List[str]
    ) -> List[str]:
        """
        Suggest extensions to create for filling a gap.
        
        Args:
            field_name: Missing field name
            file_types: Target file types
            
        Returns:
            List of suggested extension IDs
        """
        suggestions = []
        
        for ext_id, info in self._extension_info.items():
            if not info.is_active:
                continue
            
            matching_types = [
                ft for ft in info.file_types
                if any(ft.lower() in ft2.lower() or ft2.lower() in ft.lower()
                      for ft2 in file_types)
            ]
            
            if matching_types:
                suggestions.append(ext_id)
        
        suggestions.sort(
            key=lambda x: self._extension_info[x].priority,
            reverse=True
        )
        
        return suggestions
    
    def validate_extension_coverage(
        self,
        extension_id: str
    ) -> Dict[str, Any]:
        """
        Validate that an extension's declared fields are valid.
        
        Args:
            extension_id: Extension to validate
            
        Returns:
            Validation report
        """
        result = {
            "extension_id": extension_id,
            "valid": True,
            "fields": {},
            "errors": [],
            "warnings": []
        }
        
        info = self._extension_info.get(extension_id)
        if not info:
            result["valid"] = False
            result["errors"].append(f"Extension '{extension_id}' not found")
            return result
        
        for field_name in info.supported_fields:
            field_result = {
                "exists": False,
                "in_registry": False,
                "compatible": False
            }
            
            if self.registry:
                field = self.registry.get_field(field_name)
                field_result["in_registry"] = field is not None
                
                if field:
                    field_result["exists"] = True
                    field_result["compatible"] = (
                        extension_id in field.compatible_extensions
                    )
                    
                    if not field_result["compatible"]:
                        result["warnings"].append(
                            f"Field '{field_name}' not marked as compatible "
                            f"with '{extension_id}'"
                        )
            else:
                field_result["exists"] = self._check_field_exists(field_name)
            
            result["fields"][field_name] = field_result
        
        result["valid"] = len(result["errors"]) == 0
        return result
    
    def _check_field_exists(self, field_name: str) -> bool:
        """Check if field exists in any known location"""
        # Check against known field definitions
        known_fields = self._get_known_fields()
        return field_name in known_fields
    
    def _get_known_fields(self) -> Set[str]:
        """Get all known field names from extensions"""
        fields = set()
        for ext_fields in self._extension_field_map.values():
            fields.update(ext_fields)
        return fields
    
    def attach_registry(self, registry: FieldRegistryCore) -> None:
        """Attach a field registry to the mapper"""
        self.registry = registry
        
        for ext_id in self._extension_field_map:
            self._sync_with_registry(
                ext_id,
                self._extension_field_map[ext_id]
            )
    
    def detach_registry(self) -> None:
        """Detach the current registry"""
        self.registry = None


# Global extension mapper instance
_extension_mapper: Optional[ExtensionMapper] = None


def get_extension_mapper() -> ExtensionMapper:
    """Get the global extension mapper instance"""
    global _extension_mapper
    if _extension_mapper is None:
        _extension_mapper = ExtensionMapper()
    return _extension_mapper


def create_extension_mapper(
    registry: Optional[FieldRegistryCore] = None
) -> ExtensionMapper:
    """Create a new extension mapper instance"""
    return ExtensionMapper(field_registry=registry)


# Export classes and functions
__all__ = [
    "ExtensionMapper",
    "ExtensionInfo",
    "get_extension_mapper",
    "create_extension_mapper",
]

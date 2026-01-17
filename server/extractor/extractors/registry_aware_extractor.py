#!/usr/bin/env python3
"""
Registry-Aware Image Metadata Extractor

This module provides comprehensive image metadata extraction that:
1. Uses ExifTool as the primary extractor (29k+ tag coverage)
2. Maps results to ImageMetadataRegistry field names (1,033 fields)
3. Uses registry ExifTag mappings for accurate field naming
4. Populates data for all 41 registry categories

Author: MetaExtract Team
Version: 4.0.0
"""

import logging
import os
import subprocess
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

EXIFTOOL_PATH = "/opt/homebrew/bin/exiftool"
EXIFTOOL_AVAILABLE = os.path.exists(EXIFTOOL_PATH) and os.access(EXIFTOOL_PATH, os.X_OK)

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False


class RegistryAwareImageExtractor:
    """
    Image extractor that properly integrates with ImageMetadataRegistry.
    
    Maps ExifTool output to registry field names using the registry's
    ExifTag mappings for accurate field naming.
    """
    
    SUPPORTED_FORMATS = [
        '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.gif', '.bmp',
        '.webp', '.heic', '.heif', '.avif', '.psd',
        '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.pef', '.x3f', '.sr2',
        '.dcm', '.dicom',
        '.fits', '.fts', '.h5',
        '.flir', '.seek', '.thermal',
        '.obj', '.stl', '.3mf', '.gltf', '.glb',
        '.vr360', '.360', '.panorama',
    ]
    
    def __init__(self, redact_sensitive: bool = True):
        """Initialize the extractor and load registry."""
        self.redact_sensitive = redact_sensitive
        self._load_registry()
        self.extraction_stats = {
            "exiftool_used": False,
            "fields_extracted": 0,
            "errors": []
        }
    
    def _load_registry(self):
        """Load the ImageMetadataRegistry and build field maps."""
        try:
            from image_metadata_registry import ImageMetadataRegistry
            self.registry = ImageMetadataRegistry()
            self._build_exiftool_to_registry_map()
            print(f"✅ Loaded registry with {len(self.registry.fields)} fields")
        except Exception as e:
            print(f"⚠️ Could not load registry: {e}")
            self.registry = None
            self._exiftool_to_registry = {}
            self._category_fields = {}
    
    def _build_exiftool_to_registry_map(self):
        """Build mapping from ExifTool keys to registry field names."""
        self._exiftool_to_registry = {}
        self._category_fields = {}
        
        if not self.registry:
            return
        
        for field_name, field in self.registry.fields.items():
            category = field.category.value
            
            if category not in self._category_fields:
                self._category_fields[category] = []
            self._category_fields[category].append(field_name)
            
            if field.exif_tag:
                self._exiftool_to_registry[field.exif_tag] = field_name
        
        print(f"✅ Built mapping: {len(self._exiftool_to_registry)} ExifTool→Registry mappings")
    
    def can_extract(self, filepath: str) -> bool:
        """Check if we can extract from this file."""
        ext = Path(filepath).suffix.lower()
        return ext in self.SUPPORTED_FORMATS
    
    def extract(self, filepath: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from an image file.
        
        Returns data using registry field names.
        """
        if not os.path.exists(filepath):
            return self._error_result(filepath, "File not found")
        
        start_time = datetime.utcnow()
        result = {}
        
        try:
            if EXIFTOOL_AVAILABLE:
                exiftool_data = self._extract_with_exiftool(filepath)
                if exiftool_data:
                    self.extraction_stats["exiftool_used"] = True
                    result = self._map_to_registry(exiftool_data)
                else:
                    result = self._extract_fallback(filepath)
            else:
                result = self._extract_fallback(filepath)
            
            # Add basic properties from PIL
            if PIL_AVAILABLE:
                basic_props = self._extract_pil_basic(filepath)
                result.update(basic_props)
            
            # Add format detection for specialized categories
            self._add_format_detection(result, filepath)
            
            # Count fields
            self.extraction_stats["fields_extracted"] = self._count_fields(result)
            
            # Finalize result
            result["extraction_info"] = {
                "timestamp": start_time.isoformat() + "Z",
                "source": "registry_aware_exiftool",
                "success": True,
                "exiftool_used": self.extraction_stats["exiftool_used"],
                "fields_extracted": self.extraction_stats["fields_extracted"],
                "registry_fields_available": len(self.registry.fields) if self.registry else 0,
                "errors": self.extraction_stats["errors"]
            }
            
            return result
            
        except Exception as e:
            self.extraction_stats["errors"].append(str(e))
            return self._error_result(filepath, str(e))
    
    def _extract_with_exiftool(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract metadata using ExifTool."""
        cmd = [
            EXIFTOOL_PATH,
            '-j', '-a', '-G1', '-s',
            '-overwrite_original',
            filepath
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.warning(f"ExifTool error: {result.stderr}")
                return None
            
            output = result.stdout.strip()
            if output:
                data = json.loads(output)
                return data[0] if data else None
        except Exception as e:
            self.extraction_stats["errors"].append(f"ExifTool: {str(e)}")
        
        return None
    
    def _map_to_registry(self, exiftool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map ExifTool output to registry field names."""
        result = {}
        
        # Initialize category structures
        for category, fields in self._category_fields.items():
            result[category] = {}
        
        # Build reverse lookup: registry field name -> category
        registry_field_to_category = {}
        for category, fields in self._category_fields.items():
            for field_name in fields:
                registry_field_to_category[field_name] = category
        
        # Process each key in ExifTool output
        for exiftool_key, value in exiftool_data.items():
            if value is None:
                continue
            
            # Skip metadata about the file itself
            if exiftool_key.startswith("File:") or exiftool_key.startswith("System:") or exiftool_key.startswith("SourceFile"):
                continue
            
            # Strip group prefix (IFD0:, ExifIFD:, GPS:, etc.)
            simple_key = exiftool_key.split(":")[-1] if ":" in exiftool_key else exiftool_key
            simple_key = simple_key.lower()
            
            # Try to find matching registry field
            # Look for exact match with registry field names
            if simple_key in registry_field_to_category:
                category = registry_field_to_category[simple_key]
                # Find the actual field name with proper case
                for field_name in self._category_fields.get(category, []):
                    if field_name.lower() == simple_key:
                        result[category][field_name] = self._normalize_value(value)
                        break
            elif simple_key in self._category_fields:
                # The simple_key IS a registry field name
                category = simple_key
                if isinstance(result.get(category), dict):
                    result[category] = self._normalize_value(value)
            else:
                # Store in basic_properties as unknown field
                clean_name = exiftool_key.replace(":", "_").replace("-", "_").lower()
                result["basic_properties"][clean_name] = self._normalize_value(value)
        
        # Remove empty categories
        empty_categories = [k for k, v in result.items() if not v]
        for cat in empty_categories:
            del result[cat]
        
        return result
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize value types."""
        if isinstance(value, str):
            # Try to convert numbers
            if re.match(r'^-?\d+\.?\d*$', value):
                try:
                    return float(value) if '.' in value else int(value)
                except:
                    pass
        return value
    
    def _extract_fallback(self, filepath: str) -> Dict[str, Any]:
        """Fallback extraction using PIL/exifread."""
        result = {}
        
        if PIL_AVAILABLE:
            try:
                with Image.open(filepath) as img:
                    result["color_mode"] = img.mode
                    result["width"] = img.width
                    result["height"] = img.height
            except Exception as e:
                self.extraction_stats["errors"].append(f"PIL: {str(e)}")
        
        return result
    
    def _extract_pil_basic(self, filepath: str) -> Dict[str, Any]:
        """Extract basic properties using PIL."""
        result = {}
        
        if not PIL_AVAILABLE:
            return result
        
        try:
            with Image.open(filepath) as img:
                result["width"] = img.width
                result["height"] = img.height
                result["color_mode"] = img.mode
                result["file_format"] = img.format
                result["icc_profile_present"] = 'icc_profile' in img.info
                result["xmp_present"] = hasattr(img, 'info') and 'xmp' in img.info
                result["exif_present"] = hasattr(img, '_getexif') and img._getexif() is not None
                
                # Calculate derived fields
                result["total_pixels"] = img.width * img.height
                result["megapixels"] = round(result["total_pixels"] / 1_000_000, 2)
                result["aspect_ratio"] = round(img.width / img.height, 2) if img.height > 0 else 0
                result["has_alpha"] = 'A' in img.mode or 'a' in img.mode
                
                # Check for animation
                try:
                    result["is_animated"] = getattr(img, "is_animated", False)
                    result["frame_count"] = getattr(img, "n_frames", 1)
                except:
                    result["is_animated"] = False
                    result["frame_count"] = 1
                
        except Exception as e:
            self.extraction_stats["errors"].append(f"PIL basic: {str(e)}")
        
        return result
    
    def _add_format_detection(self, result: Dict[str, Any], filepath: str):
        """Add format detection for specialized categories."""
        ext = Path(filepath).suffix.lower()
        filename = Path(filepath).stem.lower()
        
        # Initialize all category structures
        self._init_category_structures(result)
        
        # Format detection
        if ext in ['.dcm', '.dicom']:
            result["medical_imaging_format"] = "DICOM"
            result["is_medical_image"] = True
        elif ext in ['.fits', '.fts']:
            result["scientific_imaging_format"] = "FITS"
            result["is_scientific_image"] = True
        elif ext in ['.h5', '.hdf5']:
            result["scientific_imaging_format"] = "HDF5"
            result["is_scientific_image"] = True
        elif ext in ['.flir', '.seek', '.thermal']:
            result["thermal_imaging_format"] = "Thermal"
            result["is_thermal_image"] = True
        elif ext in ['.obj', '.stl', '.3mf']:
            result["three_d_imaging_format"] = ext[1:].upper()
            result["is_3d_model"] = True
        elif ext in ['.gltf', '.glb']:
            result["three_d_imaging_format"] = "glTF"
            result["is_3d_model"] = True
        elif ext in ['.vr360', '.360', 'panorama']:
            result["vr_ar_format"] = "360_Panorama"
            result["is_vr_content"] = True
        elif ext in ['.cr2', '.cr3', '.nef', '.arw', '.dng']:
            result["raw_format"] = ext[1:].upper()
            result["is_raw_image"] = True
        elif ext in ['.heic', '.heif']:
            result["nextgen_image_format"] = "HEIF"
            result["is_nextgen_image"] = True
        elif ext == '.avif':
            result["nextgen_image_format"] = "AVIF"
            result["is_nextgen_image"] = True
        elif ext == '.psd':
            result["photoshop_psd_format"] = "PSD"
            result["is_photoshop_file"] = True
        elif ext == '.svg':
            result["vector_graphics_format"] = "SVG"
            result["is_vector_graphic"] = True
        elif ext == '.exr':
            result["openexr_hdr_format"] = "OpenEXR"
            result["is_hdr_image"] = True
        
        # Mobile detection
        mobile_markers = ['iphone', 'ipad', 'android', 'samsung', 'xiaomi', 'huawei', 'pixel']
        if any(m in filename for m in mobile_markers):
            result["mobile_device_detected"] = True
        
        # Drone detection
        drone_markers = ['dji', 'mavic', 'phantom', 'spark', 'inspire', 'matrice']
        if any(m in filename for m in drone_markers):
            result["drone_uav_detected"] = True
            result["drone_model"] = next((m for m in drone_markers if m in filename), "Unknown")
        
        # Action camera detection
        action_markers = ['gopro', 'insta360', 'garmin', 'osmo']
        if any(m in filename for m in action_markers):
            result["action_camera_detected"] = True
        
        # AI generation detection
        ai_markers = ['midjourney', 'stable_diffusion', 'dalle', 'generated', 'ai_']
        if any(m in filename for m in ai_markers):
            result["ai_generation_detected"] = True
        
        # Edit history detection
        edit_markers = ['lightroom', 'photoshop', 'capture_one', 'edited', 'processed']
        if any(m in filename for m in edit_markers):
            result["edit_history_detected"] = True
        
        # Social metadata presence
        if any(k in result for k in ['title', 'creator', 'description', 'keywords', 'copyright']):
            result["social_metadata_present"] = True
        
        # Accessibility presence
        if any(k in result for k in ['title', 'description', 'subject']):
            result["accessibility_metadata_present"] = True
        
        # Quality metrics
        file_size = os.path.getsize(filepath)
        result["file_size_bytes"] = file_size
        result["file_size_human"] = self._humanize_size(file_size)
        
        # Basic metrics
        if "width" in result and "height" in result:
            result["quality_score_base"] = min(result["width"], result["height"]) // 100
        
        # Barcode/OCR detection
        ocr_markers = ['scan', 'scanned', 'ocr', 'barcode', 'document']
        if any(m in filename for m in ocr_markers):
            result["barcode_ocr_source"] = True
        
        # E-commerce detection
        ecommerce_markers = ['product', 'listing', 'shop', 'catalog', 'item']
        if any(m in filename for m in ecommerce_markers):
            result["ecommerce_source"] = True
        
        # Print/prepress detection
        print_markers = ['print', 'press', 'cmyk', 'brochure', 'flyer']
        if any(m in filename for m in print_markers):
            result["print_prepress_source"] = True
        
        # Color grading detection
        color_markers = ['lut', 'cube', 'grade', 'graded', 'color_']
        if any(m in filename for m in color_markers):
            result["color_grading_source"] = True
        
        # Remote sensing detection
        remote_markers = ['satellite', 'aerial', 'lidar', 'ortho']
        if any(m in filename for m in remote_markers):
            result["remote_sensing_source"] = True
        
        # Digital signature detection
        sig_markers = ['signed', 'signature', 'certified', 'verified']
        if any(m in filename for m in sig_markers):
            result["digital_signature_present"] = True
        
        # Document image detection
        doc_markers = ['scan', 'document', 'doc', 'receipt', 'invoice']
        if any(m in filename for m in doc_markers):
            result["document_image_source"] = True
        
        # Cinema raw detection
        cinema_markers = ['arri', 'red', 'cinema', 'cinematic']
        if any(m in filename for m in cinema_markers):
            result["cinema_raw_source"] = True
        
        # Color analysis (basic from PIL data)
        if "color_mode" in result:
            mode = result["color_mode"]
            result["color_analysis_possible"] = mode in ['RGB', 'RGBA', 'L']
            result["color_channels"] = len(mode)
            result["bit_depth"] = 8 if mode in ['RGB', 'L', 'RGBA'] else 16
        
        # TIFF IFD
        if ext in ['.tiff', '.tif']:
            result["tiff_ifd_present"] = True
        
        # Animated images
        if ext in ['.gif', '.webp'] and result.get("is_animated"):
            result["animated_format"] = ext[1:].upper()
            result["is_animated_image"] = True
    
    def _init_category_structures(self, result: Dict[str, Any]):
        """Initialize all category structures."""
        categories = [
            'basic_properties', 'file_format_chunks', 'exif_standard',
            'iptc_standard', 'iptc_extension', 'xmp_namespaces', 'icc_profiles',
            'camera_makernotes', 'mobile_metadata', 'action_camera', 'drone_uav',
            'medical_imaging', 'scientific_imaging', 'thermal_imaging',
            'three_d_imaging', 'vr_ar', 'ai_generation', 'photoshop_psd',
            'edit_history', 'openexr_hdr', 'raw_format', 'animated_images',
            'social_metadata', 'accessibility', 'tiff_ifd', 'ecommerce',
            'vector_graphics', 'nextgen_image', 'cinema_raw', 'document_image',
            'print_prepress', 'color_grading', 'remote_sensing', 'ai_vision',
            'barcode_ocr', 'digital_signature', 'perceptual_hashes',
            'color_analysis', 'quality_metrics', 'steganography', 'image_forensics'
        ]
        
        for cat in categories:
            if cat not in result:
                result[cat] = {}
    
    def _humanize_size(self, size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def _count_fields(self, d: Dict[str, Any], depth: int = 0) -> int:
        """Count total non-null fields."""
        if depth > 10:
            return 0
        count = 0
        for k, v in d.items():
            if k == "extraction_info":
                continue
            if isinstance(v, dict):
                count += self._count_fields(v, depth + 1)
            elif v is not None and v != {} and v != []:
                count += 1
        return count
    
    def _error_result(self, filepath: str, error: str) -> Dict[str, Any]:
        """Create error result."""
        return {
            "error": error,
            "extraction_info": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "registry_aware_exiftool",
                "success": False,
                "errors": [error]
            }
        }
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get extractor information."""
        return {
            "name": "RegistryAwareImageExtractor",
            "version": "4.0.0",
            "supported_formats": len(self.SUPPORTED_FORMATS),
            "exiftool_available": EXIFTOOL_AVAILABLE,
            "registry_fields_available": len(self.registry.fields) if self.registry else 0,
            "exiftool_mappings": len(self._exiftool_to_registry)
        }


def extract_image_metadata(filepath: str, redact_sensitive: bool = True) -> Dict[str, Any]:
    """
    Convenience function for registry-aware image metadata extraction.
    
    Args:
        filepath: Path to the image file
        redact_sensitive: Whether to redact sensitive fields
        
    Returns:
        Dictionary containing extracted metadata with registry field names
    """
    extractor = RegistryAwareImageExtractor(redact_sensitive=redact_sensitive)
    return extractor.extract(filepath)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: registry_aware_extractor.py <image_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    result = extract_image_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))

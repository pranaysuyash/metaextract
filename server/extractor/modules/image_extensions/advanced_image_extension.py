"""
Advanced Image Extension
Wraps the existing image_master.py module with standardized extension interface
"""

import logging
import sys
import os
from typing import Dict, Any, List
from pathlib import Path

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


class AdvancedImageExtension(ImageExtensionBase):
    """
    Advanced image metadata extraction using image_master module.

    Integrates multiple specialized image analysis capabilities including
    EXIF, IPTC/XMP, perceptual hashes, colors, quality metrics, and mobile metadata.
    """

    SOURCE = "advanced"
    FIELD_COUNT = 1130  # Combined from all sub-modules
    DESCRIPTION = "Advanced image analysis with multiple specialized modules"
    VERSION = "1.0.0"
    CAPABILITIES = [
        "basic_properties",
        "iptc_xmp_metadata",
        "exif_data",
        "perceptual_hashes",
        "color_analysis",
        "quality_metrics",
        "mobile_metadata"
    ]

    def __init__(self):
        super().__init__()
        self.image_master_available = False
        self.image_master_module = None
        self._load_image_master()

    def _load_image_master(self):
        """Try to load the image_master module"""
        try:
            # Add the modules directory to path
            modules_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(modules_dir))

            # Import image_master
            import image_master
            self.image_master_module = image_master
            self.image_master_available = True
            logger.info("Successfully loaded image_master module")

        except Exception as e:
            logger.warning(f"Could not load image_master module: {e}")
            self.image_master_available = False

    def get_field_definitions(self) -> List[str]:
        """Get list of advanced image field names from all sub-modules"""
        return [
            # Basic properties (from basic extension)
            "format", "mode", "width", "height", "aspect_ratio", "megapixels",
            "has_transparency", "is_animated", "n_frames", "dpi_x", "dpi_y",

            # IPTC/XMP fields
            "iptc", "xmp", "iptc_raw", "xmp_raw",

            # EXIF fields
            "exif_data", "exif_raw",

            # Perceptual hashes
            "perceptual_hashes", "ahash", "phash", "dhash", "whash",

            # Color analysis
            "color_palette", "dominant_colors", "color_histogram",

            # Quality metrics
            "quality_metrics", "sharpness", "brightness", "contrast",

            # Mobile metadata
            "mobile_metadata", "device_info", "camera_settings"
        ]

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract advanced image metadata from image file.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing extraction results
        """
        result = ImageExtractionResult(self.SOURCE, filepath)

        try:
            # Validate image file
            if not self.validate_image_file(filepath):
                result.add_warning("File may not be a valid image format")

            # Extract basic file info
            file_info = get_image_file_info(filepath)
            if "error" not in file_info:
                result.add_metadata("file_info", file_info)

            # Check if image_master is available
            if not self.image_master_available or not self.image_master_module:
                result.add_warning("image_master module not available, using fallback extraction")
                return self._fallback_extraction(filepath, result)

            # Use image_master for comprehensive extraction
            try:
                master_data = self.image_master_module.extract_image_master(filepath)

                if master_data.get("image_master_available"):
                    # Process results from image_master
                    modules_data = master_data.get("modules", {})

                    # Basic image properties
                    if "basic_image" in modules_data:
                        result.add_metadata_dict(modules_data["basic_image"])
                        result.add_metadata("basic_image_available", True)
                    else:
                        result.add_metadata("basic_image_available", False)

                    # IPTC/XMP metadata
                    if "iptc_xmp" in modules_data:
                        result.add_metadata_dict(modules_data["iptc_xmp"])
                        result.add_metadata("iptc_xmp_available", True)
                    else:
                        result.add_metadata("iptc_xmp_available", False)

                    # EXIF data
                    if "exif_data" in modules_data:
                        result.add_metadata_dict(modules_data["exif_data"])
                        result.add_metadata("exif_data_available", True)
                    else:
                        result.add_metadata("exif_data_available", False)

                    # Perceptual hashes
                    if "perceptual_hashes" in modules_data:
                        result.add_metadata_dict(modules_data["perceptual_hashes"])
                        result.add_metadata("perceptual_hashes_available", True)
                    else:
                        result.add_metadata("perceptual_hashes_available", False)

                    # Color analysis
                    if "colors" in modules_data:
                        result.add_metadata_dict(modules_data["colors"])
                        result.add_metadata("color_analysis_available", True)
                    else:
                        result.add_metadata("color_analysis_available", False)

                    # Quality metrics
                    if "quality" in modules_data:
                        result.add_metadata_dict(modules_data["quality"])
                        result.add_metadata("quality_metrics_available", True)
                    else:
                        result.add_metadata("quality_metrics_available", False)

                    # Mobile metadata
                    if "mobile" in modules_data:
                        result.add_metadata_dict(modules_data["mobile"])
                        result.add_metadata("mobile_metadata_available", True)
                    else:
                        result.add_metadata("mobile_metadata_available", False)

                    # Add total fields count
                    total_fields = master_data.get("total_fields_extracted", 0)
                    result.add_metadata("total_modules_fields_extracted", total_fields)

                    # Check for errors in modules
                    for key, value in modules_data.items():
                        if key.endswith("_error"):
                            result.add_warning(f"Module error: {value}")

                else:
                    result.add_warning("image_master reported as unavailable")

                final_result = result.finalize()
                self.log_extraction_summary(final_result)
                return final_result

            except Exception as e:
                logger.error(f"image_master extraction failed: {e}")
                result.add_warning(f"image_master extraction failed: {str(e)[:100]}")
                return self._fallback_extraction(filepath, result)

        except Exception as e:
            logger.error(f"Advanced image extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

    def _fallback_extraction(self, filepath: str, result: ImageExtractionResult) -> Dict[str, Any]:
        """
        Fallback extraction using basic PIL when image_master is unavailable.

        Args:
            filepath: Path to image file
            result: Current ImageExtractionResult object

        Returns:
            Extraction result dictionary
        """
        try:
            from PIL import Image

            with Image.open(filepath) as img:
                # Extract basic properties
                result.add_metadata("format", img.format)
                result.add_metadata("mode", img.mode)
                result.add_metadata("width", img.width)
                result.add_metadata("height", img.height)

                if img.height > 0:
                    aspect_ratio = round(img.width / img.height, 4)
                    result.add_metadata("aspect_ratio", aspect_ratio)

                megapixels = round((img.width * img.height) / 1_000_000, 2)
                result.add_metadata("megapixels", megapixels)

                result.add_metadata("fallback_mode", True)
                result.add_metadata("fallback_reason", "image_master unavailable")

            return result.finalize()

        except Exception as e:
            return result.to_error_result(f"Fallback extraction also failed: {str(e)[:200]}")
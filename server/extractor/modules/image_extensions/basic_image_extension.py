"""
Basic Image Extension
Wraps the existing images.py module with standardized extension interface
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


class BasicImageExtension(ImageExtensionBase):
    """
    Basic image metadata extraction using Pillow.

    Extracts fundamental image properties like dimensions, format, color mode, etc.
    """

    SOURCE = "basic"
    FIELD_COUNT = 18
    DESCRIPTION = "Basic image properties extraction using Pillow"
    VERSION = "1.0.0"
    CAPABILITIES = [
        "image_dimensions",
        "color_mode",
        "format_detection",
        "transparency",
        "animation_detection",
        "dpi_info"
    ]

    # Basic image field definitions
    BASIC_FIELDS = [
        "format",
        "mode",
        "width",
        "height",
        "aspect_ratio",
        "megapixels",
        "has_transparency",
        "is_animated",
        "n_frames",
        "dpi_x",
        "dpi_y",
        "horiz_dpi_unit",
        "vert_dpi_unit",
        "iccp",
        "icc_profile_name",
        "exif",
        "gps"
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of basic image field names"""
        return self.BASIC_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract basic image metadata from image file.

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

            # Import PIL here to avoid dependency issues
            try:
                from PIL import Image, ImageCms
            except ImportError:
                return result.to_error_result("Pillow library not available")

            # Extract basic file info
            file_info = get_image_file_info(filepath)
            if "error" not in file_info:
                result.add_metadata("file_info", file_info)

            # Open image and extract properties
            with Image.open(filepath) as img:
                # Basic properties
                result.add_metadata("format", img.format)
                result.add_metadata("mode", img.mode)

                # Dimensions
                width, height = img.size
                result.add_metadata("width", width)
                result.add_metadata("height", height)

                if height > 0:
                    aspect_ratio = round(width / height, 4)
                    result.add_metadata("aspect_ratio", aspect_ratio)

                megapixels = round((width * height) / 1_000_000, 2)
                result.add_metadata("megapixels", megapixels)

                # Transparency
                has_transparency = (
                    img.mode == 'RGBA' or
                    img.mode == 'LA' or
                    img.mode == 'PA' or
                    'transparency' in img.info
                )
                result.add_metadata("has_transparency", has_transparency)

                # Animation
                is_animated = getattr(img, "is_animated", False)
                n_frames = getattr(img, "n_frames", 1)

                result.add_metadata("is_animated", is_animated)
                result.add_metadata("n_frames", n_frames)

                # DPI information
                dpi_info = img.info.get('dpi', (0, 0))
                if dpi_info and isinstance(dpi_info, tuple) and len(dpi_info) >= 2:
                    result.add_metadata("dpi_x", dpi_info[0])
                    result.add_metadata("dpi_y", dpi_info[1])

                # DPI units
                if hasattr(img, 'horiz_dpi_unit'):
                    result.add_metadata("horiz_dpi_unit", str(img.horiz_dpi_unit))
                if hasattr(img, 'vert_dpi_unit'):
                    result.add_metadata("vert_dpi_unit", str(img.vert_dpi_unit))

                # ICC Profile
                if 'icc_profile' in img.info:
                    icc_data = img.info['icc_profile']
                    result.add_metadata("iccp", True)
                    result.add_metadata("icc_profile_size_bytes", len(icc_data))

                    # Try to get ICC profile name
                    try:
                        if hasattr(ImageCms, 'Profile'):
                            profile = ImageCms.Profile(io.BytesIO(icc_data))
                            result.add_metadata("icc_profile_name", profile.profile_name)
                    except Exception:
                        result.add_metadata("icc_profile_name", "Unknown ICC Profile")

                # EXIF data
                try:
                    from PIL.ExifTags import TAGS, GPSTAGS

                    exif_data = img._getexif()
                    if exif_data:
                        exif_dict = {}
                        gps_dict = {}

                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)

                            # Handle different value types
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)[:100]

                            # Separate GPS data
                            if tag == "GPSInfo":
                                for gps_tag_id, gps_value in value.items():
                                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                                    gps_dict[str(gps_tag)] = str(gps_value)
                            else:
                                exif_dict[str(tag)] = str(value) if not isinstance(value, (int, float, bool)) else value

                        if exif_dict:
                            result.add_metadata("exif", exif_dict)
                        if gps_dict:
                            result.add_metadata("gps", gps_dict)

                except Exception as e:
                    result.add_warning(f"Could not extract EXIF data: {str(e)[:100]}")

                # Add warnings for uncommon modes
                if img.mode not in ['RGB', 'RGBA', 'L', 'LA', 'P', 'PA']:
                    result.add_warning(f"Uncommon image mode: {img.mode}")

            final_result = result.finalize()
            self.log_extraction_summary(final_result)
            return final_result

        except Exception as e:
            logger.error(f"Basic image extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")
"""
Universal Image Extension
Wraps the existing universal_metadata_extractor.py module with standardized extension interface
"""

import logging
import sys
import os
from typing import Dict, Any, List
from pathlib import Path

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


class UniversalImageExtension(ImageExtensionBase):
    """
    Universal image metadata extraction using universal_metadata_extractor module.

    Provides basic extraction capabilities with file signature detection
    and binary analysis as fallback.
    """

    SOURCE = "universal"
    FIELD_COUNT = 50  # Basic fields plus binary analysis
    DESCRIPTION = "Universal image extraction with binary analysis fallback"
    VERSION = "1.0.0"
    CAPABILITIES = [
        "format_detection",
        "file_signature_analysis",
        "basic_image_properties",
        "binary_analysis",
        "hash_calculation",
        "entropy_analysis"
    ]

    def __init__(self):
        super().__init__()
        self.universal_extractor = None
        self._load_universal_extractor()

    def _load_universal_extractor(self):
        """Try to load the universal_metadata_extractor module"""
        try:
            # Add the modules directory to path
            modules_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(modules_dir))

            # Import universal_metadata_extractor
            import universal_metadata_extractor
            self.universal_extractor = universal_metadata_extractor
            logger.info("Successfully loaded universal_metadata_extractor module")

        except Exception as e:
            logger.warning(f"Could not load universal_metadata_extractor module: {e}")

    def get_field_definitions(self) -> List[str]:
        """Get list of universal image field names"""
        return [
            # File metadata
            "filename", "extension", "size_bytes", "size_mb",
            "created", "modified", "is_file", "is_readable",

            # Format specific
            "format", "mode", "size", "width", "height", "exif",

            # Binary analysis
            "file_size", "md5_hash", "sha256_hash", "header_hex",
            "file_signatures", "entropy_score",

            # Strings extracted
            "strings_extracted"
        ]

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract universal image metadata from image file.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing extraction results
        """
        result = ImageExtractionResult(self.SOURCE, filepath)

        try:
            # Try to use universal_metadata_extractor if available
            if self.universal_extractor:
                try:
                    universal_data = self.universal_extractor.extract_metadata(filepath)

                    # Process file metadata
                    file_metadata = universal_data.get("file_metadata", {})
                    if file_metadata and "error" not in file_metadata:
                        result.add_metadata_dict(file_metadata)

                    # Process format-specific metadata
                    format_specific = universal_data.get("format_specific", {})
                    if format_specific and "error" not in format_specific:
                        result.add_metadata_dict(format_specific)

                    # Process binary analysis
                    binary_analysis = universal_data.get("binary_analysis", {})
                    if binary_analysis and "error" not in binary_analysis:
                        result.add_metadata_dict(binary_analysis)

                    # Process extracted strings
                    strings_extracted = universal_data.get("strings_extracted", [])
                    if strings_extracted:
                        result.add_metadata("strings_extracted", strings_extracted[:10])  # Limit to 10

                    # Add extraction metadata
                    result.add_metadata("extraction_method", universal_data.get("extraction_method", "unknown"))
                    result.add_metadata("universal_fields_extracted", universal_data.get("fields_extracted", 0))

                    # Check for errors
                    if "error" in universal_data:
                        result.add_warning(f"Universal extractor error: {universal_data['error']}")

                    final_result = result.finalize()
                    self.log_extraction_summary(final_result)
                    return final_result

                except Exception as e:
                    logger.error(f"Universal extractor failed: {e}")
                    result.add_warning(f"Universal extractor failed: {str(e)[:100]}")

            # Fallback to basic extraction
            return self._basic_extraction(filepath, result)

        except Exception as e:
            logger.error(f"Universal image extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

    def _basic_extraction(self, filepath: str, result: ImageExtractionResult) -> Dict[str, Any]:
        """
        Basic extraction using PIL when universal extractor is unavailable.

        Args:
            filepath: Path to image file
            result: Current ImageExtractionResult object

        Returns:
            Extraction result dictionary
        """
        try:
            import hashlib

            # Extract basic file info
            file_info = get_image_file_info(filepath)
            if "error" not in file_info:
                result.add_metadata_dict(file_info)

            # Calculate file hashes
            try:
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                    result.add_metadata("md5_hash", hashlib.md5(file_content).hexdigest())
                    result.add_metadata("sha256_hash", hashlib.sha256(file_content).hexdigest()[:32])

                    # Detect file signature
                    header = file_content[:32]
                    result.add_metadata("header_hex", header.hex())

                    signatures = self._detect_signatures(header)
                    if signatures:
                        result.add_metadata("detected_signatures", signatures)

            except Exception as e:
                result.add_warning(f"Could not calculate hashes: {str(e)[:100]}")

            # Try to extract basic image properties with PIL
            try:
                from PIL import Image

                with Image.open(filepath) as img:
                    result.add_metadata("format", img.format)
                    result.add_metadata("mode", img.mode)
                    result.add_metadata("width", img.width)
                    result.add_metadata("height", img.height)

                    if img.height > 0:
                        aspect_ratio = round(img.width / img.height, 4)
                        result.add_metadata("aspect_ratio", aspect_ratio)

            except Exception as e:
                result.add_warning(f"Could not extract PIL properties: {str(e)[:100]}")

            result.add_metadata("fallback_mode", True)
            result.add_metadata("fallback_reason", "universal_extractor unavailable")

            return result.finalize()

        except Exception as e:
            return result.to_error_result(f"Basic extraction also failed: {str(e)[:200]}")

    def _detect_signatures(self, header: bytes) -> List[str]:
        """Detect file signatures in header bytes"""
        signatures = []

        magic_bytes = {
            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'PNG',
            b'\xFF\xD8\xFF': 'JPEG',
            b'\x47\x49\x46\x38': 'GIF',
            b'\x49\x49\x2A\x00': 'TIFF_little',
            b'\x4D\x4D\x00\x2A': 'TIFF_big',
            b'\x00\x00\x01\x00': 'ICO',
        }

        for magic, format_name in magic_bytes.items():
            if header.startswith(magic):
                signatures.append(format_name)

        return signatures
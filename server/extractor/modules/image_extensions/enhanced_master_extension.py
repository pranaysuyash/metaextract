"""
Enhanced Master Image Extension
Combines all registry capabilities into one comprehensive extension
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


class EnhancedMasterExtension(ImageExtensionBase):
    """
    Enhanced master extension combining all registry capabilities.

    This extension provides:
    - Complete GPS extraction with OCR and filename fallback
    - Comprehensive EXIF/IPTC/XMP data
    - All 21 specialized modules
    - Advanced analysis capabilities
    - Performance optimization
    """

    SOURCE = "enhanced_master"
    FIELD_COUNT = 300  # Master capability count
    DESCRIPTION = "Enhanced master extension with all capabilities combined"
    VERSION = "1.0.0"
    CAPABILITIES = [
        "complete_gps",
        "comprehensive_exif",
        "advanced_iptc",
        "advanced_xmp",
        "mobile_metadata",
        "forensic_analysis",
        "ocr_burned_text",
        "all_specialized_modules",
        "performance_optimized",
        "enhanced_accuracy"
    ]

    def __init__(self):
        super().__init__()
        # Load other extensions for delegation
        from . import get_global_registry
        self.registry = get_global_registry()

        # Smart caching system to avoid redundant operations
        self._cache_lock = threading.Lock()
        self._image_cache = {}  # Cache for basic image data
        self._exif_cache = {}  # Cache for EXIF data
        self._cache_hits = 0
        self._cache_misses = 0

    def _get_cached_image_data(self, filepath: str):
        """Get cached basic image data or extract and cache it"""
        with self._cache_lock:
            if filepath in self._image_cache:
                self._cache_hits += 1
                return self._image_cache[filepath]

            self._cache_misses += 1

            # Extract basic image data
            try:
                from PIL import Image
                with Image.open(filepath) as img:
                    image_data = {
                        "format": img.format,
                        "mode": img.mode,
                        "width": img.width,
                        "height": img.height,
                        "megapixels": round((img.width * img.height) / 1_000_000, 2),
                        "has_icc": hasattr(img, 'info') and 'icc_profile' in img.info,
                        "has_exif": hasattr(img, '_getexif'),
                        "size_bytes": len(open(filepath, 'rb').read())
                    }

                    self._image_cache[filepath] = image_data
                    return image_data
            except Exception as e:
                logger.warning(f"Failed to cache image data: {e}")
                return None

    def _get_cached_exif_data(self, filepath: str):
        """Get cached EXIF data or extract and cache it"""
        with self._cache_lock:
            if filepath in self._exif_cache:
                self._cache_hits += 1
                return self._exif_cache[filepath]

            self._cache_misses += 1

            # Extract EXIF data
            try:
                from PIL import Image
                with Image.open(filepath) as img:
                    exif = img._getexif()
                    if exif:
                        from PIL.ExifTags import TAGS
                        exif_dict = {}
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)[:100]
                            exif_dict[str(tag)] = value

                        self._exif_cache[filepath] = exif_dict
                        return exif_dict
                    else:
                        self._exif_cache[filepath] = {}
                        return {}
            except Exception as e:
                logger.warning(f"Failed to cache EXIF data: {e}")
                return {}

    def get_field_definitions(self) -> List[str]:
        """Get list of all enhanced master field names"""
        return [
            # Core GPS
            "gps", "gps_coordinates", "gps_accuracy", "gps_source",

            # Basic image properties
            "format", "mode", "width", "height", "megapixels", "aspect_ratio",

            # Comprehensive EXIF
            "exif", "exif_comprehensive", "camera_settings", "exposure_settings",
            "lens_information", "shooting_settings",

            # Advanced metadata
            "iptc", "xmp", "iptc_raw", "xmp_raw", "icc_profile",

            # Mobile and device
            "mobile_metadata", "device_info", "camera_app",

            # Forensic
            "forensic", "file_integrity", "file_hashes", "timestamps",

            # Specialized modules (all 21)
            "drone_telemetry", "emerging_technology", "scientific_research",
            "industrial_manufacturing", "financial_business", "healthcare_medical",
            "transportation_logistics", "education_academic", "legal_compliance",
            "environmental_sustainability", "social_media_digital", "gaming_entertainment",
            "medical_imaging", "astronomical_data", "geospatial_analysis",
            "scientific_instruments", "blockchain_provenance",
            "advanced_video_analysis", "advanced_audio_analysis", "document_analysis",
            "multimedia_entertainment",

            # Performance and analysis
            "extraction_performance", "field_coverage", "data_quality_score"
        ]

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata using enhanced master capabilities with parallel execution.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing enhanced master extraction results
        """
        result = ImageExtractionResult(self.SOURCE, filepath)
        start_time = time.time()

        try:
            # Validate image file
            if not self.validate_image_file(filepath):
                result.add_warning("File may not be a valid image format")

            # Step 1: Use cached data for basic image info (FAST)
            cached_image = self._get_cached_image_data(filepath)
            if cached_image:
                result.add_metadata("format", cached_image.get("format"))
                result.add_metadata("mode", cached_image.get("mode"))
                result.add_metadata("width", cached_image.get("width"))
                result.add_metadata("height", cached_image.get("height"))
                result.add_metadata("megapixels", cached_image.get("megapixels"))

            # Step 2: Use cached EXIF data (FAST)
            cached_exif = self._get_cached_exif_data(filepath)
            if cached_exif:
                result.add_metadata("exif", cached_exif)

            # Step 3: Parallel execution of independent extractions
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}

                # Submit GPS extraction (high priority)
                gps_future = executor.submit(self._extract_with_extension, "complete_gps", filepath)
                futures['gps'] = gps_future

                # Submit specialized modules (can run in parallel)
                specialized_future = executor.submit(self._extract_with_extension, "specialized_modules", filepath)
                futures['specialized'] = specialized_future

                # Submit advanced analysis
                analysis_future = executor.submit(self._add_advanced_analysis_fast, filepath, result)
                futures['analysis'] = analysis_future

                # Submit perceptual hashing
                hash_future = executor.submit(self._add_perceptual_hashes_fast, filepath, result)
                futures['hashing'] = hash_future

                # Submit AI/ML scene recognition and quality assessment
                ai_future = executor.submit(self._add_ai_ml_analysis, filepath, result)
                futures['ai_ml'] = ai_future

                # Collect results as they complete
                for future_name, future in futures.items():
                    try:
                        if future_name == 'gps':
                            gps_result = future.result(timeout=5)
                            if gps_result and gps_result.get("success"):
                                gps_metadata = gps_result.get("metadata", {})
                                for key, value in gps_metadata.items():
                                    if key != 'exif':  # Don't duplicate cached EXIF
                                        result.add_metadata(key, value)
                                logger.info("Enhanced master: Parallel GPS extraction complete")

                        elif future_name == 'specialized':
                            specialized_result = future.result(timeout=5)
                            if specialized_result and specialized_result.get("success"):
                                specialized_metadata = specialized_result.get("metadata", {})
                                for key, value in specialized_metadata.items():
                                    if key not in result.metadata:  # Don't override GPS data
                                        result.add_metadata(key, value)
                                logger.info("Enhanced master: Parallel specialized modules complete")

                        elif future_name == 'analysis':
                            analysis_result = future.result(timeout=3)
                            # Analysis was added directly to result

                        elif future_name == 'hashing':
                            hashing_result = future.result(timeout=3)
                            # Hashing was added directly to result

                        elif future_name == 'ai_ml':
                            ai_result = future.result(timeout=3)
                            # AI/ML analysis was added directly to result
                            logger.info("Enhanced master: Parallel AI/ML analysis complete")
                            # Hashing was added directly to result

                    except Exception as e:
                        logger.warning(f"Parallel extraction failed for {future_name}: {e}")

            # Step 4: Add advanced EXIF lens data using cached EXIF (FAST)
            if cached_exif:
                self._add_advanced_exif_lens_data_fast(cached_exif, result)

            # Step 5: Calculate performance metrics
            extraction_time = time.time() - start_time

            # Cache statistics
            cache_total = self._cache_hits + self._cache_misses
            cache_hit_rate = (self._cache_hits / cache_total * 100) if cache_total > 0 else 0

            performance_data = {
                "extraction_time_seconds": round(extraction_time, 4),
                "fields_extracted": len(result.metadata),
                "field_coverage_percent": round((len(result.metadata) / self.FIELD_COUNT) * 100, 1),
                "extraction_method": "enhanced_master_parallel",
                "extensions_used": ["complete_gps", "specialized_modules", "advanced_analysis", "perceptual_hashing"],
                "performance_score": self._calculate_performance_score(result.metadata, extraction_time),
                "cache_hit_rate": round(cache_hit_rate, 1),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses
            }
            result.add_metadata("extraction_performance", performance_data)

            final_result = result.finalize()
            self.log_extraction_summary(final_result)
            return final_result

        except Exception as e:
            logger.error(f"Enhanced master extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

    def _add_advanced_analysis_fast(self, filepath: str, result: ImageExtractionResult):
        """Fast version of advanced analysis using cached data"""
        try:
            # Use cached image data if available
            cached_image = self._get_cached_image_data(filepath)
            if not cached_image:
                return

            # Image quality analysis
            quality_analysis = {
                "resolution_quality": self._assess_resolution_quality(cached_image.get("width", 0), cached_image.get("height", 0)),
                "file_size_optimized": self._check_file_size_optimization_fast(cached_image.get("size_bytes", 0), cached_image.get("width", 0) * cached_image.get("height", 0)),
                "color_depth": self._get_color_depth_fast(cached_image.get("mode", "unknown")),
                "compression_estimated": self._estimate_compression_fast(cached_image.get("format", "unknown"))
            }
            result.add_metadata("image_quality_analysis", quality_analysis)

            # Data completeness score
            has_gps = 'gps' in result.metadata and result.metadata['gps'].get('latitude')
            has_exif = 'exif' in result.metadata
            has_camera = 'exif' in result.metadata and any(key in result.metadata['exif'] for key in ['Make', 'Model', 'make', 'model'])

            completeness = {
                "gps_data_complete": bool(has_gps),
                "exif_data_complete": bool(has_exif),
                "camera_data_complete": bool(has_camera),
                "overall_completeness": round((sum([bool(has_gps), bool(has_exif), bool(has_camera)]) / 3) * 100, 1)
            }
            result.add_metadata("data_completeness", completeness)

        except Exception as e:
            result.add_warning(f"Fast advanced analysis failed: {str(e)[:100]}")

    def _add_perceptual_hashes_fast(self, filepath: str, result: ImageExtractionResult):
        """Ultra-fast version of perceptual hashing - only 1 hash"""
        try:
            from PIL import Image
            import imagehash

            with Image.open(filepath) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img_rgb = img.convert('RGB')
                else:
                    img_rgb = img

                # Calculate only perceptual hash (best balance of speed/accuracy)
                try:
                    phash = imagehash.phash(img_rgb)

                    perceptual_hashes = {
                        "perceptual_hash": str(phash),
                        "hashing_success": True,
                        "hash_count": 1,
                        "ultra_fast_mode": True
                    }

                    result.add_metadata("perceptual_hashes", perceptual_hashes)

                except Exception as e:
                    result.add_warning(f"Ultra-fast perceptual hashing failed: {str(e)[:100]}")

        except ImportError:
            # Skip hashing if library not available
            pass
        except Exception as e:
            # Skip hashing on error to avoid breaking extraction
            pass

    def _add_advanced_exif_lens_data_fast(self, cached_exif: Dict[str, Any], result: ImageExtractionResult):
        """Fast version using cached EXIF data"""
        try:
            lens_data = {}
            shooting_data = {}
            camera_data = {}

            # Key EXIF tags for lens/camera data
            lens_tags = {
                'LensModel': 'lens_model',
                'LensSerialNumber': 'lens_serial_number',
                'FocalLengthIn35mmFilm': 'focal_length_35mm_format',
                'FocalLength': 'focal_length',
                'FNumber': 'fnumber',
            }

            camera_tags = {
                'Make': 'make',
                'Model': 'model',
                'Software': 'software',
            }

            # Extract from cached EXIF
            for exif_key, value in cached_exif.items():
                if exif_key in lens_tags:
                    lens_data[lens_tags[exif_key]] = value
                elif exif_key in camera_tags:
                    camera_data[camera_tags[exif_key]] = value

            # Add categorized data
            if lens_data:
                result.add_metadata("lens_data", lens_data)
            if camera_data:
                result.add_metadata("camera_data", camera_data)

        except Exception as e:
            result.add_warning(f"Fast EXIF lens data extraction failed: {str(e)[:100]}")

    def _check_file_size_optimization_fast(self, file_size: int, pixels: int) -> bool:
        """Fast file size optimization check"""
        if pixels == 0:
            return False
        bytes_per_pixel = file_size / pixels
        return 0.5 <= bytes_per_pixel <= 5.0

    def _get_color_depth_fast(self, mode: str) -> str:
        """Fast color depth detection"""
        mode_mapping = {
            'RGB': '24-bit',
            'RGBA': '32-bit',
            'CMYK': '32-bit',
            'L': '8-bit grayscale',
            'LA': '16-bit grayscale',
            'P': '8-bit palette'
        }
        return mode_mapping.get(mode, 'unknown')

    def _estimate_compression_fast(self, format_type: str) -> str:
        """Fast compression estimation"""
        format_mapping = {
            'JPEG': 'lossy JPEG',
            'PNG': 'lossless PNG',
            'GIF': 'lossless GIF',
            'WEBP': 'modern WEBP'
        }
        return format_mapping.get(format_type, 'unknown')

    def _extract_with_extension(self, extension_name: str, filepath: str) -> Dict[str, Any]:
        """Helper to extract using a specific extension"""
        try:
            extension = self.registry.get_extension(extension_name)
            if extension:
                return extension.extract_specialty_metadata(filepath)
        except Exception as e:
            logger.warning(f"Extension {extension_name} failed: {e}")
        return None

    def _extract_comprehensive_exif_enhanced(self, filepath: str, result: ImageExtractionResult):
        """Extract comprehensive EXIF with enhanced coverage"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            with Image.open(filepath) as img:
                # Basic properties with additional calculations
                result.add_metadata("format", img.format)
                result.add_metadata("mode", img.mode)
                result.add_metadata("width", img.width)
                result.add_metadata("height", img.height)

                if img.height > 0:
                    megapixels = round((img.width * img.height) / 1_000_000, 2)
                    result.add_metadata("megapixels", megapixels)

                    # Calculate aspect ratio
                    from fractions import Fraction
                    try:
                        aspect_ratio = Fraction(img.width, img.height)
                        result.add_metadata("aspect_ratio", f"{aspect_ratio.numerator}:{aspect_ratio.denominator}")
                    except:
                        result.add_metadata("aspect_ratio", f"{img.width}:{img.height}")

                # Enhanced EXIF extraction
                exif_data = img._getexif()
                if exif_data:
                    exif_enhanced = {}
                    camera_settings = {}
                    exposure_settings = {}

                    for tag_id, value in exif_data.items():
                        try:
                            tag = TAGS.get(tag_id, tag_id)

                            # Handle bytes values
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)[:100]

                            # Categorize EXIF data
                            if tag in ["Make", "Model", "Software", "LensModel", "LensMake"]:
                                camera_settings[str(tag).lower()] = str(value)
                                exif_enhanced[str(tag).lower()] = str(value)

                            elif tag in ["ExposureTime", "FNumber", "ISOSpeedRatings",
                                        "ShutterSpeedValue", "ApertureValue", "BrightnessValue"]:
                                exposure_settings[str(tag).lower()] = value
                                exif_enhanced[str(tag).lower()] = value

                            elif tag in ["DateTimeOriginal", "DateTime", "CreateDate"]:
                                exif_enhanced[str(tag).lower()] = str(value)

                            else:
                                exif_enhanced[str(tag)] = value if not isinstance(value, bytes) else str(value)[:100]

                        except Exception as e:
                            logger.debug(f"Error processing EXIF tag {tag_id}: {e}")

                    if exif_enhanced:
                        result.add_metadata("exif", exif_enhanced)
                    if camera_settings:
                        result.add_metadata("camera_settings", camera_settings)
                    if exposure_settings:
                        result.add_metadata("exposure_settings", exposure_settings)

        except Exception as e:
            result.add_warning(f"Enhanced EXIF extraction failed: {str(e)[:100]}")

    def _add_advanced_analysis(self, filepath: str, result: ImageExtractionResult):
        """Add advanced analysis categories"""
        try:
            # Image quality analysis
            from PIL import Image
            import os

            with Image.open(filepath) as img:
                quality_analysis = {
                    "resolution_quality": self._assess_resolution_quality(img.width, img.height),
                    "file_size_optimized": self._check_file_size_optimization(filepath, img),
                    "color_depth": self._get_color_depth(img),
                    "compression_estimated": self._estimate_compression(img)
                }
                result.add_metadata("image_quality_analysis", quality_analysis)

            # Data completeness score
            completeness = {
                "gps_data_complete": bool(result.metadata.get('gps', {}).get('latitude')),
                "exif_data_complete": bool(result.metadata.get('exif')),
                "camera_data_complete": bool(result.metadata.get('camera_settings')),
                "specialized_modules_complete": bool(result.metadata.get('drone_telemetry')),
                "overall_completeness": round((sum([
                    bool(result.metadata.get('gps', {}).get('latitude')),
                    bool(result.metadata.get('exif')),
                    bool(result.metadata.get('camera_settings')),
                    bool(result.metadata.get('drone_telemetry'))
                ]) / 4) * 100, 1)
            }
            result.add_metadata("data_completeness", completeness)

        except Exception as e:
            result.add_warning(f"Advanced analysis failed: {str(e)[:100]}")

    def _calculate_performance_score(self, metadata: Dict[str, Any], extraction_time: float) -> float:
        """Calculate overall performance score"""
        try:
            field_count = len(metadata)
            time_efficiency = max(0, 1 - (extraction_time / 10))  # Normalize to 0-1
            field_efficiency = min(1, field_count / self.FIELD_COUNT)

            return round((time_efficiency * 0.4 + field_efficiency * 0.6) * 100, 1)
        except:
            return 0.0

    def _assess_resolution_quality(self, width: int, height: int) -> str:
        """Assess image resolution quality"""
        total_pixels = width * height
        if total_pixels >= 20_000_000:  # 20MP+
            return "excellent"
        elif total_pixels >= 12_000_000:  # 12MP+
            return "high"
        elif total_pixels >= 8_000_000:  # 8MP+
            return "good"
        elif total_pixels >= 4_000_000:  # 4MP+
            return "medium"
        else:
            return "basic"

    def _check_file_size_optimization(self, filepath: str, img) -> bool:
        """Check if file size is optimized for resolution"""
        try:
            import os
            file_size = os.path.getsize(filepath)
            pixels = img.width * img.height
            bytes_per_pixel = file_size / pixels

            # Reasonable compression: 0.5 - 5 bytes per pixel
            return 0.5 <= bytes_per_pixel <= 5.0
        except:
            return False

    def _get_color_depth(self, img) -> str:
        """Get color depth information"""
        if hasattr(img, 'mode'):
            mode_mapping = {
                'RGB': '24-bit',
                'RGBA': '32-bit',
                'CMYK': '32-bit',
                'L': '8-bit grayscale',
                'LA': '16-bit grayscale',
                'P': '8-bit palette'
            }
            return mode_mapping.get(img.mode, 'unknown')
        return 'unknown'

    def _estimate_compression(self, img) -> str:
        """Estimate compression type"""
        if hasattr(img, 'format'):
            if img.format == 'JPEG':
                return 'lossy JPEG'
            elif img.format == 'PNG':
                return 'lossless PNG'
            elif img.format == 'GIF':
                return 'lossless GIF'
            elif img.format == 'WEBP':
                return 'modern WEBP'
        return 'unknown'

    def _add_perceptual_hashes(self, filepath: str, result: ImageExtractionResult):
        """Add perceptual hashing for duplicate detection"""
        try:
            from PIL import Image
            import imagehash
            import io

            with Image.open(filepath) as img:
                perceptual_hashes = {}

                # Convert to RGB if necessary for hashing
                if img.mode != 'RGB':
                    img_rgb = img.convert('RGB')
                else:
                    img_rgb = img

                # Calculate different perceptual hashes
                try:
                    # Average hash - fast, good for exact duplicates
                    ahash = imagehash.average_hash(img_rgb)
                    perceptual_hashes["average_hash"] = str(ahash)

                    # Perceptual hash - better for similar images
                    phash = imagehash.phash(img_rgb)
                    perceptual_hashes["perceptual_hash"] = str(phash)

                    # Difference hash - good for modified images
                    dhash = imagehash.dhash(img_rgb)
                    perceptual_hashes["difference_hash"] = str(dhash)

                    # Wavelet hash - most robust
                    whash = imagehash.whash(img_rgb)
                    perceptual_hashes["wavelet_hash"] = str(whash)

                    # Color hash - for color-based similarity
                    chash = imagehash.colorhash(img_rgb)
                    perceptual_hashes["color_hash"] = str(chash)

                    perceptual_hashes["hashing_success"] = True

                except Exception as e:
                    perceptual_hashes = {
                        "hashing_success": False,
                        "hashing_error": str(e)[:100]
                    }

                # Add hash information
                perceptual_hashes["hash_count"] = len([k for k in perceptual_hashes.keys() if k.endswith('_hash')])
                perceptual_hashes["note"] = "Perceptual hashes useful for duplicate detection and image similarity"

                if perceptual_hashes:
                    result.add_metadata("perceptual_hashes", perceptual_hashes)

        except ImportError:
            # imagehash not available
            result.add_warning("imagehash library not available for perceptual hashing")
        except Exception as e:
            result.add_warning(f"Perceptual hashing failed: {str(e)[:100]}")

    def _add_advanced_exif_lens_data(self, filepath: str, result: ImageExtractionResult):
        """Add advanced EXIF lens and camera data"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            with Image.open(filepath) as img:
                exif = img._getexif()
                if not exif:
                    return

                lens_data = {}
                camera_data = {}
                shooting_data = {}

                # Advanced EXIF tag mappings
                exif_mappings = {
                    # Lens data
                    0xA434: 'lens_model',
                    0xA435: 'lens_serial_number',
                    0xA405: 'focal_length_35mm_format',
                    0xA432: 'lens_specification',
                    0xA406: 'subject_distance',
                    0x9205: 'max_aperture_value',
                    0xA433: 'lens_make',

                    # Camera settings
                    0x8822: 'exposure_program',
                    0x8824: 'spectral_sensitivity',
                    0x8827: 'iso_speed',
                    0x8828: 'oecf',
                    0x8829: 'interlace',
                    0x882A: 'time_zone_offset',
                    0x882B: 'self_timer_mode',
                    0x9201: 'shutter_speed_value',
                    0x9202: 'aperture_value',
                    0x9203: 'brightness_value',
                    0x9204: 'exposure_bias_value',
                    0x9206: 'subject_distance_range',
                    0x9207: 'metering_mode',
                    0x9208: 'light_source',
                    0x9209: 'flash',
                    0x920A: 'focal_length',
                    0x920B: 'flash_energy',
                    0x920C: 'subject_area',
                    0x920D: 'maker_note',

                    # Image data
                    0x0100: 'image_width',
                    0x0101: 'image_height',
                    0x0112: 'orientation',
                    0x0128: 'resolution_unit',
                    0x0213: 'ycbcr_coefficients',
                    0x8769: 'exif_offset',
                    0x8825: 'gps_info',

                    # Shooting info
                    0x9000: 'exif_version',
                    0x9003: 'datetime_original',
                    0x9004: 'datetime_digitized',
                    0x9290: 'subsec_time',
                    0x9291: 'subsec_time_original',
                    0x9292: 'subsec_time_digitized',
                    0xA000: 'flashpix_version',
                    0xA001: 'color_space',
                    0xA002: 'pixel_x_dimension',
                    0xA003: 'pixel_y_dimension',
                    0xA004: 'related_sound_file',
                    0xA005: 'interoperability_offset',
                }

                # Extract and categorize EXIF data
                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    mapped_name = exif_mappings.get(tag_id, tag_name)

                    # Process value
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)[:100]

                    # Categorize
                    if mapped_name:
                        if 'lens' in mapped_name.lower() or tag_id in [0xA434, 0xA435, 0xA405, 0xA432, 0xA433]:
                            lens_data[mapped_name] = value
                        elif 'focal_length' in mapped_name or 'aperture' in mapped_name or 'exposure' in mapped_name:
                            shooting_data[mapped_name] = value
                        elif 'shutter' in mapped_name or 'iso' in mapped_name or 'flash' in mapped_name or 'metering' in mapped_name:
                            shooting_data[mapped_name] = value
                        elif 'make' in mapped_name or 'model' in mapped_name or 'camera' in mapped_name:
                            camera_data[mapped_name] = value

                # Add categorized data to result
                if lens_data:
                    result.add_metadata("lens_data", lens_data)
                if shooting_data:
                    result.add_metadata("shooting_data", shooting_data)
                if camera_data:
                    result.add_metadata("camera_data", camera_data)

        except Exception as e:
            result.add_warning(f"Advanced EXIF extraction failed: {str(e)[:100]}")
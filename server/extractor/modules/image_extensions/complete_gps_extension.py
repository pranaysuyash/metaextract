"""
Complete GPS Image Extension
Full GPS extraction using exifread for comprehensive location data
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

from .base import ImageExtensionBase, ImageExtractionResult, safe_extract_image_field, get_image_file_info

logger = logging.getLogger(__name__)


def dms_to_decimal(dms_list, ref):
    """Convert DMS (degrees, minutes, seconds) to decimal degrees"""
    try:
        degrees = float(dms_list[0])
        minutes = float(dms_list[1])
        seconds = float(dms_list[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if ref in ['S', 'W']:
            decimal = -decimal

        return round(decimal, 6)
    except:
        return None


def format_dms(decimal_degrees, is_latitude):
    """Format decimal degrees to DMS string"""
    try:
        degrees = int(decimal_degrees)
        minutes_decimal = (decimal_degrees - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60

        direction = ''
        if is_latitude:
            direction = 'N' if decimal_degrees >= 0 else 'S'
        else:
            direction = 'E' if decimal_degrees >= 0 else 'W'

        return f"{abs(degrees)}°{abs(minutes)}'{abs(seconds):.2f}\"{direction}"
    except:
        return str(decimal_degrees)


class CompleteGPSImageExtension(ImageExtensionBase):
    """
    Complete GPS image metadata extraction using exifread.

    Provides comprehensive GPS coordinate extraction including:
    - Latitude/longitude in multiple formats
    - Altitude and GPS accuracy
    - GPS timestamps and satellites
    - Speed, direction, and tracking data
    - Map URLs and location formatting
    """

    SOURCE = "complete_gps"
    FIELD_COUNT = 200  # Comprehensive GPS + all image metadata
    DESCRIPTION = "Complete GPS extraction with comprehensive location data"
    VERSION = "3.0.0"
    CAPABILITIES = [
        "gps_coordinates",
        "gps_altitude",
        "gps_accuracy",
        "gps_tracking",
        "comprehensive_exif",
        "mobile_metadata",
        "basic_forensic"
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of complete GPS field names"""
        return [
            # GPS Coordinates
            "latitude", "longitude", "altitude",
            "latitude_decimal", "longitude_decimal",
            "latitude_dms", "longitude_dms",
            "coordinates", "google_maps_url", "openstreetmap_url",

            # GPS Accuracy & Timing
            "gps_timestamp", "gps_datestamp", "gps_altitude_ref",
            "gps_satellites", "gps_status", "gps_measure_mode",

            # GPS Movement
            "gps_speed", "gps_speed_ref", "gps_track", "gps_track_ref",
            "gps_img_direction", "gps_img_direction_ref",

            # GPS Technical
            "gps_map_datum", "gps_differential", "gps_h_positioning_error",

            # Basic image properties
            "format", "mode", "width", "height", "megapixels",

            # EXIF fields
            "make", "model", "datetime_original", "iso", "exposure_time",
            "fnumber", "focal_length", "white_balance", "flash",

            # Mobile metadata
            "device_manufacturer", "device_model", "camera_app",

            # Forensic
            "file_hash_md5", "file_hash_sha256", "file_created", "file_modified"
        ]

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract complete GPS and image metadata from image file.

        Args:
            filepath: Path to image file

        Returns:
            Dictionary containing complete extraction results
        """
        result = ImageExtractionResult(self.SOURCE, filepath)

        try:
            # Validate image file
            if not self.validate_image_file(filepath):
                result.add_warning("File may not be a valid image format")

            # Ultra-fast path: Extract GPS metadata using exifread (single file read)
            if EXIFREAD_AVAILABLE:
                self._extract_gps_with_exifread(filepath, result)
            else:
                result.add_warning("exifread not available, GPS extraction limited")

            # Batch extract all metadata in a single PIL operation
            self._extract_all_metadata_optimized(filepath, result)

            final_result = result.finalize()
            self.log_extraction_summary(final_result)
            return final_result

        except Exception as e:
            logger.error(f"Complete GPS extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

    def _extract_all_metadata_optimized(self, filepath: str, result: ImageExtractionResult):
        """Extract all metadata in a single optimized PIL operation"""
        try:
            from PIL import Image
            import time

            start_time = time.time()

            # Single PIL operation for all metadata
            with Image.open(filepath) as img:
                # Extract comprehensive EXIF
                self._extract_comprehensive_exif_fast(filepath, result, img)

                # Extract mobile metadata (fast)
                self._extract_mobile_metadata_fast(filepath, result, img)

                # Extract forensic metadata (fast)
                self._extract_forensic_metadata_fast(filepath, result, img)

                # Extract ICC color profile (fast)
                self._extract_icc_profile_fast(filepath, result, img)

                # Extract IPTC metadata (fast)
                self._extract_iptc_metadata_fast(filepath, result, img)

                # Extract XMP metadata (fast)
                self._extract_xmp_metadata_fast(filepath, result, img)

                # Skip thumbnail and OCR in optimized mode for speed
                # These can be enabled later if needed

                # Add filename-based GPS as fallback (no OCR)
                self._extract_gps_from_filename(filepath, result)

            processing_time = time.time() - start_time
            result.add_metadata("extraction_performance", {
                "total_processing_time": round(processing_time, 6),
                "optimized_mode": True,
                "single_pil_operation": True,
                "ocr_disabled": True,
                "thumbnail_disabled": True
            })

        except Exception as e:
            logger.error(f"Optimized batch extraction failed: {e}")
            # Fallback to individual extractions
            self._extract_comprehensive_exif(filepath, result)
            self._extract_mobile_metadata(filepath, result)
            self._extract_forensic_metadata(filepath, result)
            self._extract_icc_profile(filepath, result)
            self._extract_iptc_metadata(filepath, result)
            self._extract_xmp_metadata(filepath, result)
            self._extract_gps_from_filename(filepath, result)

    def _extract_gps_with_exifread(self, filepath: str, result: ImageExtractionResult):
        """Extract GPS data using exifread"""
        try:
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f, details=False)

            gps_data = {}

            # Extract latitude
            if "GPS GPSLatitude" in tags and "GPS GPSLatitudeRef" in tags:
                lat = dms_to_decimal(tags["GPS GPSLatitude"].values, str(tags["GPS GPSLatitudeRef"]))
                if lat:
                    gps_data["latitude_decimal"] = lat
                    gps_data["latitude_dms"] = format_dms(lat, True)
                    gps_data["latitude"] = lat  # Primary field

            # Extract longitude
            if "GPS GPSLongitude" in tags and "GPS GPSLongitudeRef" in tags:
                lon = dms_to_decimal(tags["GPS GPSLongitude"].values, str(tags["GPS GPSLongitudeRef"]))
                if lon:
                    gps_data["longitude_decimal"] = lon
                    gps_data["longitude_dms"] = format_dms(lon, False)
                    gps_data["longitude"] = lon  # Primary field

            # Create formatted coordinates and URLs
            if "latitude" in gps_data and "longitude" in gps_data:
                lat, lon = gps_data["latitude"], gps_data["longitude"]
                gps_data["coordinates"] = f"{lat:.6f}, {lon:.6f}"
                gps_data["google_maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
                gps_data["openstreetmap_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"

            # Extract altitude
            if "GPS GPSAltitude" in tags:
                try:
                    altitude = float(tags["GPS GPSAltitude"].values[0])
                    gps_data["altitude"] = altitude
                    if "GPS GPSAltitudeRef" in tags:
                        alt_ref = str(tags["GPS GPSAltitudeRef"])
                        gps_data["altitude_ref"] = alt_ref
                except:
                    pass

            # Extract GPS timestamp
            if "GPS GPSTimeStamp" in tags:
                gps_data["gps_timestamp"] = str(tags["GPS GPSTimeStamp"])
            if "GPS GPSDateStamp" in tags:
                gps_data["gps_datestamp"] = str(tags["GPS GPSDateStamp"])

            # Extract additional GPS data
            gps_fields = {
                "GPS GPSSatellites": "gps_satellites",
                "GPS GPSStatus": "gps_status",
                "GPS GPSMeasureMode": "gps_measure_mode",
                "GPS GPSDOP": "gps_dop",
                "GPS GPSSpeed": "gps_speed",
                "GPS GPSSpeedRef": "gps_speed_ref",
                "GPSTrack": "gps_track",
                "GPS GPSTrackRef": "gps_track_ref",
                "GPS GPSImgDirection": "gps_img_direction",
                "GPS GPSImgDirectionRef": "gps_img_direction_ref",
                "GPS GPSMapDatum": "gps_map_datum",
                "GPS GPSDifferential": "gps_differential",
                "GPS GPSHPositioningError": "gps_h_positioning_error"
            }

            for tag, field in gps_fields.items():
                if tag in tags:
                    gps_data[field] = str(tags[tag])

            if gps_data:
                result.add_metadata("gps", gps_data)

        except Exception as e:
            result.add_warning(f"GPS extraction failed: {str(e)[:100]}")

    def _extract_comprehensive_exif(self, filepath: str, result: ImageExtractionResult):
        """Extract comprehensive EXIF data using PIL"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            with Image.open(filepath) as img:
                # Basic properties
                result.add_metadata("format", img.format)
                result.add_metadata("mode", img.mode)
                result.add_metadata("width", img.width)
                result.add_metadata("height", img.height)

                if img.height > 0:
                    megapixels = round((img.width * img.height) / 1_000_000, 2)
                    result.add_metadata("megapixels", megapixels)

                # Comprehensive EXIF
                exif_data = img._getexif()
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        try:
                            tag = TAGS.get(tag_id, tag_id)

                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)[:100]

                            # Map common EXIF fields to simplified names
                            if tag == "Make":
                                exif_dict["make"] = str(value)
                                result.add_metadata("make", str(value))
                            elif tag == "Model":
                                exif_dict["model"] = str(value)
                                result.add_metadata("model", str(value))
                            elif tag == "DateTimeOriginal":
                                exif_dict["datetime_original"] = str(value)
                                result.add_metadata("datetime_original", str(value))
                            elif tag == "ISO":
                                exif_dict["iso"] = int(value) if isinstance(value, int) else value
                                result.add_metadata("iso", exif_dict["iso"])
                            elif tag == "ExposureTime":
                                exif_dict["exposure_time"] = str(value)
                                result.add_metadata("exposure_time", str(value))
                            elif tag == "FNumber":
                                exif_dict["fnumber"] = float(value) if isinstance(value, (int, float)) else value
                                result.add_metadata("fnumber", exif_dict["fnumber"])
                            elif tag == "FocalLength":
                                exif_dict["focal_length"] = str(value)
                                result.add_metadata("focal_length", str(value))
                            elif tag == "WhiteBalance":
                                exif_dict["white_balance"] = str(value)
                                result.add_metadata("white_balance", str(value))
                            elif tag == "Flash":
                                exif_dict["flash"] = str(value)
                                result.add_metadata("flash", str(value))
                            else:
                                exif_dict[str(tag)] = str(value) if not isinstance(value, (int, float, bool)) else value

                        except Exception as e:
                            logger.debug(f"Error processing EXIF tag {tag_id}: {e}")

                    if exif_dict:
                        result.add_metadata("exif", exif_dict)

        except Exception as e:
            result.add_warning(f"EXIF extraction failed: {str(e)[:100]}")

    def _extract_mobile_metadata(self, filepath: str, result: ImageExtractionResult):
        """Extract mobile/smartphone metadata"""
        try:
            mobile_dict = {}

            # Get data from already extracted EXIF if available
            if "make" in result.metadata or "model" in result.metadata:
                make = result.metadata.get("make", "")
                model = result.metadata.get("model", "")

                if make:
                    mobile_dict["device_manufacturer"] = make
                if model:
                    mobile_dict["device_model"] = model

                    # Detect camera app
                    if "GPS Map Camera" in model or "Camera" in model:
                        mobile_dict["camera_app"] = "GPS Map Camera"

            if mobile_dict:
                result.add_metadata("mobile_metadata", mobile_dict)

        except Exception as e:
            result.add_warning(f"Mobile metadata extraction failed: {str(e)[:100]}")

    def _extract_forensic_metadata(self, filepath: str, result: ImageExtractionResult):
        """Extract forensic metadata"""
        try:
            import hashlib
            import os

            forensic_dict = {}

            # File timestamps
            stat = os.stat(filepath)
            forensic_dict["file_created"] = stat.st_ctime
            forensic_dict["file_modified"] = stat.st_mtime
            forensic_dict["file_size"] = stat.st_size

            # File hashes
            with open(filepath, 'rb') as f:
                file_content = f.read()
                forensic_dict["file_hash_md5"] = hashlib.md5(file_content).hexdigest()
                forensic_dict["file_hash_sha256"] = hashlib.sha256(file_content).hexdigest()

            forensic_dict["is_authenticated"] = False
            forensic_dict["security_flags"] = ["unauthenticated_content"]

            result.add_metadata("forensic", forensic_dict)

        except Exception as e:
            result.add_warning(f"Forensic extraction failed: {str(e)[:100]}")

    def _extract_burned_gps_text(self, filepath: str, result: ImageExtractionResult):
        """Extract GPS coordinates from burned-in text using OCR"""
        try:
            from PIL import Image
            import re

            # Try to use OCR if available
            try:
                import pytesseract
                ocr_available = True
            except ImportError:
                ocr_available = False

            if not ocr_available:
                # Fallback: check filename for GPS patterns
                return self._extract_gps_from_filename(filepath, result)

            # Open image and extract text
            with Image.open(filepath) as img:
                # Extract text using OCR
                text = pytesseract.image_to_string(img)

                # Look for GPS coordinate patterns
                gps_patterns = [
                    r'Lat\s*([+-]?\d+\.?\d*)\s*[°d]?\s*Long\s*([+-]?\d+\.?\d*)\s*[°d]?',
                    r'Latitude[:\s]+([+-]?\d+\.?\d*)\s*Longitude[:\s]+([+-]?\d+\.?\d*)',
                    r'GPS[:\s]+([+-]?\d+\.?\d*)[,:\s]+([+-]?\d+\.?\d*)',
                    r'(\d{1,3})[°d]\s*(\d+\.?\d*)?[\'m]?\s*([NS])[\s,]+(\d{1,3})[°d]\s*(\d+\.?\d*)?[\'m]?\s*([EW])'
                ]

                for pattern in gps_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            if len(match.groups()) == 2:  # Decimal format
                                lat = float(match.group(1))
                                lon = float(match.group(2))
                            elif len(match.groups()) == 6:  # DMS format
                                lat_deg = float(match.group(1))
                                lat_min = float(match.group(2))
                                lat_dir = match.group(3)
                                lon_deg = float(match.group(4))
                                lon_min = float(match.group(5))
                                lon_dir = match.group(6)

                                lat = lat_deg + (lat_min / 60.0)
                                lon = lon_deg + (lon_min / 60.0)

                                if lat_dir.upper() == 'S':
                                    lat = -lat
                                if lon_dir.upper() == 'W':
                                    lon = -lon

                            # Validate coordinates
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                # Only set if GPS not already populated
                                existing_gps = result.metadata.get('gps', {})
                                if not existing_gps.get('latitude') or not existing_gps.get('longitude'):
                                    gps_data = {
                                        "latitude": round(lat, 6),
                                        "longitude": round(lon, 6),
                                        "source": "burned_text_ocr",
                                        "confidence": "high"
                                    }

                                    # Add Google Maps URL
                                    gps_data["google_maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
                                    gps_data["openstreetmap_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"

                                    result.add_metadata("gps", gps_data)
                                    logger.info(f"Extracted GPS from burned text: {lat}, {lon}")
                                    return

                        except (ValueError, IndexError) as e:
                            logger.debug(f"Failed to parse GPS pattern {pattern}: {e}")
                            continue

        except Exception as e:
            result.add_warning(f"Burned GPS extraction failed: {str(e)[:100]}")

    def _extract_gps_from_filename(self, filepath: str, result: ImageExtractionResult):
        """Extract GPS from filename patterns (fallback method)"""
        try:
            import re
            from pathlib import Path

            filename = Path(filepath).name

            # Common GPS Map Camera patterns: 12_923974_77_625419
            gps_pattern = r'(\d{1,3})_(\d{3,6})_(\d{1,3})_(\d{3,6})'
            match = re.search(gps_pattern, filename)

            if match:
                try:
                    lat_deg = int(match.group(1))
                    lat_dec = int(match.group(2))
                    lon_deg = int(match.group(3))
                    lon_dec = int(match.group(4))

                    # Combine degrees and decimals
                    lat = float(f"{lat_deg}.{lat_dec}")
                    lon = float(f"{lon_deg}.{lon_dec}")

                    # Validate coordinates
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        # Only set if GPS not already populated
                        existing_gps = result.metadata.get('gps', {})
                        if not existing_gps.get('latitude') or not existing_gps.get('longitude'):
                            gps_data = {
                                "latitude": round(lat, 6),
                                "longitude": round(lon, 6),
                                "source": "filename_pattern",
                                "confidence": "medium"
                            }

                            # Add Google Maps URL
                            gps_data["google_maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
                            gps_data["openstreetmap_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15"

                            result.add_metadata("gps", gps_data)
                            logger.info(f"Extracted GPS from filename: {lat}, {lon}")

                except (ValueError, IndexError) as e:
                    logger.debug(f"Failed to parse filename GPS: {e}")

        except Exception as e:
            logger.debug(f"Filename GPS extraction failed: {e}")

    def _extract_icc_profile(self, filepath: str, result: ImageExtractionResult):
        """Extract ICC color profile information"""
        try:
            from PIL import Image
            import io

            with Image.open(filepath) as img:
                icc_profile = {}

                # Check for ICC profile
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    icc_data = img.info['icc_profile']

                    try:
                        from PIL import ImageCms
                        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_data))

                        icc_profile = {
                            "profile_name": profile.profile.profile_name if hasattr(profile.profile, 'profile_name') else 'Unknown',
                            "profile_class": profile.profile.profile_class if hasattr(profile.profile, 'profile_class') else 'Unknown',
                            "color_space": profile.profile.color_space if hasattr(profile.profile, 'color_space') else 'Unknown',
                            "pcs_illuminant": profile.profile.pcs_illuminant if hasattr(profile.profile, 'pcs_illuminant') else 'Unknown',
                            "creator": profile.profile.creator if hasattr(profile.profile, 'creator') else 'Unknown',
                            "has_icc": True,
                            "icc_size_bytes": len(icc_data)
                        }

                        # Add rendering intent if available
                        if hasattr(profile, 'rendering_intent'):
                            rendering_intents = {
                                0: 'perceptual',
                                1: 'relative',
                                2: 'saturation',
                                3: 'absolute'
                            }
                            icc_profile["rendering_intent"] = rendering_intents.get(profile.rendering_intent, 'unknown')

                    except ImportError:
                        # PIL doesn't have ImageCms, provide basic info
                        icc_profile = {
                            "has_icc": True,
                            "icc_size_bytes": len(icc_data),
                            "profile_name": "ICC Profile (detailed analysis requires PIL.ImageCms)"
                        }
                else:
                    icc_profile = {
                        "has_icc": False,
                        "note": "No embedded ICC profile found"
                    }

                # Add color space info
                if hasattr(img, 'mode'):
                    icc_profile["image_mode"] = img.mode
                    color_space_map = {
                        'RGB': 'sRGB',
                        'RGBA': 'sRGB with alpha',
                        'CMYK': 'CMYK',
                        'L': 'Grayscale',
                        'LA': 'Grayscale with alpha',
                        'P': 'Palette-based',
                        'LAB': 'CIELAB',
                        'HSV': 'HSV'
                    }
                    icc_profile["color_space_detected"] = color_space_map.get(img.mode, img.mode)

                if icc_profile:
                    result.add_metadata("icc_profile", icc_profile)

        except Exception as e:
            result.add_warning(f"ICC profile extraction failed: {str(e)[:100]}")

    def _extract_iptc_metadata(self, filepath: str, result: ImageExtractionResult):
        """Extract IPTC metadata"""
        try:
            from PIL import Image
            from PIL import IptcImagePlugin

            with Image.open(filepath) as img:
                iptc_data = {}

                # Try to get IPTC data from image info
                if hasattr(img, 'info') and 'iptc' in img.info:
                    iptc_raw = img.info['iptc']

                    # Parse IPTC data
                    try:
                        iptc_dict = IptcImagePlugin.getiptc(img)
                        if iptc_dict:
                            # Map common IPTC tags to readable names
                            iptc_mapping = {
                                (2, 5): 'object_name',
                                (2, 25): 'keywords',
                                (2, 120): 'caption',
                                (2, 122): 'caption_writer',
                                (2, 105): 'headline',
                                (2, 110): 'credit',
                                (2, 115): 'source',
                                (2, 116): 'copyright_notice',
                                (2, 90): 'city',
                                (2, 92): 'sublocation',
                                (2, 95): 'province_state',
                                (2, 101): 'country',
                                (2, 103): 'original_transmission_reference',
                                (2, 15): 'category',
                                (2, 20): 'supplemental_categories',
                                (2, 40): 'special_instructions',
                                (2, 80): 'byline',
                                (2, 85): 'byline_title',
                                (2, 100): 'affiliation',
                            }

                            for (tag_group, tag_key), value in iptc_dict.items():
                                field_name = iptc_mapping.get((tag_group, tag_key), f'iptc_{tag_group}_{tag_key}')

                                # Decode bytes if needed
                                if isinstance(value, bytes):
                                    try:
                                        value = value.decode('utf-8', errors='ignore')
                                    except:
                                        value = str(value)[:100]

                                iptc_data[field_name] = value

                    except Exception as e:
                        # Fallback to basic IPTC data
                        iptc_data = {
                            "has_iptc": True,
                            "iptc_raw_size": len(iptc_raw) if iptc_raw else 0,
                            "note": "IPTC data present but parsing failed",
                            "error": str(e)[:100]
                        }

                else:
                    iptc_data = {
                        "has_iptc": False,
                        "note": "No IPTC metadata found"
                    }

                if iptc_data:
                    result.add_metadata("iptc", iptc_data)

        except ImportError:
            # IptcImagePlugin not available, use basic detection
            result.add_warning("IPTC plugin not available in this PIL version")
        except Exception as e:
            result.add_warning(f"IPTC extraction failed: {str(e)[:100]}")

    def _extract_xmp_metadata(self, filepath: str, result: ImageExtractionResult):
        """Extract XMP metadata"""
        try:
            from PIL import Image

            with Image.open(filepath) as img:
                xmp_data = {}

                # Try to get XMP data
                if hasattr(img, 'info') and 'xmp' in img.info:
                    xmp_raw = img.info['xmp']

                    # Parse XMP data
                    if isinstance(xmp_raw, bytes):
                        try:
                            xmp_string = xmp_raw.decode('utf-8', errors='ignore')
                        except:
                            xmp_string = str(xmp_raw)
                    else:
                        xmp_string = str(xmp_raw)

                    # Extract common XMP fields
                    xmp_fields = {
                        'CreatorTool': 'creator_tool',
                        'CreateDate': 'creation_date',
                        'ModifyDate': 'modification_date',
                        'MetadataDate': 'metadata_date',
                        'Format': 'format',
                        'Rating': 'rating',
                        'Label': 'label',
                        'Rights::Certificate': 'rights_certificate',
                        'Rights::Marked': 'copyright_status',
                        'Rights::WebStatement': 'copyright_url',
                        'Rights::UsageTerms': 'usage_terms',
                        'Adobe::JobRef': 'job_reference',
                        'Photoshop::AuthorsPosition': 'author_position',
                        'Photoshop::CaptionWriter': 'caption_writer',
                        'Photoshop::City': 'city',
                        'Photoshop::Country': 'country',
                        'Photoshop::Credit': 'credit',
                        'Photoshop::Source': 'source',
                        'Photoshop::Headline': 'headline',
                        'Photoshop::Instructions': 'instructions',
                        'Photoshop::State': 'state_province',
                        'Photoshop::TransmissionReference': 'transmission_reference',
                    }

                    for xmp_field, field_name in xmp_fields.items():
                        # Look for patterns like "FieldName: Value"
                        pattern = f'{xmp_field}="([^"]*)"'
                        import re
                        match = re.search(pattern, xmp_string)
                        if match:
                            xmp_data[field_name] = match.group(1)

                    # Add raw XMP data for reference
                    xmp_data['raw_xmp_length'] = len(xmp_string)
                    xmp_data['has_xmp'] = True

                else:
                    xmp_data = {
                        "has_xmp": False,
                        "note": "No XMP metadata found"
                    }

                if xmp_data:
                    result.add_metadata("xmp", xmp_data)

        except Exception as e:
            result.add_warning(f"XMP extraction failed: {str(e)[:100]}")

    def _extract_thumbnail(self, filepath: str, result: ImageExtractionResult):
        """Extract embedded thumbnail information"""
        try:
            from PIL import Image
            import io

            with Image.open(filepath) as img:
                thumbnail_info = {}

                # Check for EXIF thumbnail
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        # Thumbnail offset and length
                        from PIL.ExifTags import TAGS
                        thumb_offset = exif.get(0x0201)  # JPEGInterchangeFormat
                        thumb_length = exif.get(0x0202)  # JPEGInterchangeFormatLength

                        if thumb_offset and thumb_length:
                            thumbnail_info = {
                                "has_thumbnail": True,
                                "thumbnail_offset": thumb_offset,
                                "thumbnail_length": thumb_length,
                                "thumbnail_size_kb": round(thumb_length / 1024, 2)
                            }

                            # Try to extract the thumbnail
                            try:
                                # Read thumbnail data
                                with open(filepath, 'rb') as f:
                                    f.seek(thumb_offset)
                                    thumb_data = f.read(thumb_length)

                                    # Try to load thumbnail
                                    thumb_img = Image.open(io.BytesIO(thumb_data))
                                    thumbnail_info.update({
                                        "thumbnail_width": thumb_img.width,
                                        "thumbnail_height": thumb_img.height,
                                        "thumbnail_format": thumb_img.format,
                                        "thumbnail_mode": thumb_img.mode
                                    })
                            except Exception as e:
                                thumbnail_info["thumbnail_extraction_error"] = str(e)[:100]

                # Check for PIL thumbnail
                if not thumbnail_info:
                    try:
                        # PIL has a built-in thumbnail extraction method
                        thumb = img.thumbnail((128, 128))  # This modifies in place
                        thumbnail_info = {
                            "has_thumbnail": False,
                            "note": "No embedded EXIF thumbnail found"
                        }
                    except:
                        thumbnail_info = {
                            "has_thumbnail": False,
                            "note": "No thumbnail data found"
                        }

                if thumbnail_info:
                    result.add_metadata("thumbnail", thumbnail_info)

        except Exception as e:
            result.add_warning(f"Thumbnail extraction failed: {str(e)[:100]}")

    # ============================================================================
    # Fast Optimization Methods (avoid re-opening image files)
    # ============================================================================

    def _extract_comprehensive_exif_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast EXIF extraction using already-opened image"""
        try:
            from PIL.ExifTags import TAGS

            # Basic properties
            result.add_metadata("format", img.format)
            result.add_metadata("mode", img.mode)
            result.add_metadata("width", img.width)
            result.add_metadata("height", img.height)

            if img.height > 0:
                megapixels = round((img.width * img.height) / 1_000_000, 2)
                result.add_metadata("megapixels", megapixels)

            # Comprehensive EXIF (fast path)
            exif_data = img._getexif()
            if exif_data:
                exif_dict = {}
                for tag_id, value in exif_data.items():
                    try:
                        tag = TAGS.get(tag_id, tag_id)
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)
                        exif_dict[tag] = value
                    except:
                        continue

                if exif_dict:
                    result.add_metadata("exif", exif_dict)

        except Exception as e:
            result.add_warning(f"Fast EXIF extraction failed: {str(e)[:100]}")

    def _extract_mobile_metadata_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast mobile metadata extraction using already-opened image"""
        try:
            from PIL.ExifTags import TAGS

            exif_data = img._getexif()
            if not exif_data:
                return

            mobile_fields = {}
            mobile_tags = {
                'Make': 'make',
                'Model': 'model',
                'Software': 'software',
                'DateTimeOriginal': 'datetime_original',
                'CreateDate': 'create_date',
                'Orientation': 'orientation',
                'XResolution': 'x_resolution',
                'YResolution': 'y_resolution'
            }

            for tag, field in mobile_tags.items():
                tag_id = None
                for tid, name in TAGS.items():
                    if name == tag:
                        tag_id = tid
                        break

                if tag_id and tag_id in exif_data:
                    mobile_fields[field] = exif_data[tag_id]

            if mobile_fields:
                result.add_metadata("mobile_metadata", mobile_fields)

        except Exception as e:
            result.add_warning(f"Fast mobile extraction failed: {str(e)[:100]}")

    def _extract_forensic_metadata_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast forensic metadata extraction using already-opened image"""
        try:
            forensic_data = {
                "format": img.format,
                "mode": img.mode,
                "dimensions": f"{img.width}x{img.height}",
                "has_transparency": img.mode in ('RGBA', 'LA', 'PA'),
                "bits_per_channel": getattr(img, 'bits', 8),
                "size_bytes": len(img.tobytes()) if img.width * img.height < 10_000_000 else "large_image"
            }
            result.add_metadata("forensic", forensic_data)

        except Exception as e:
            result.add_warning(f"Fast forensic extraction failed: {str(e)[:100]}")

    def _extract_icc_profile_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast ICC profile extraction using already-opened image"""
        try:
            icc_profile = None
            if hasattr(img, 'info'):
                icc_profile = img.info.get('icc_profile')

            icc_data = {
                "has_icc_profile": icc_profile is not None,
                "icc_profile_size": len(icc_profile) if icc_profile else 0,
                "color_space": img.mode
            }
            result.add_metadata("icc_profile", icc_data)

        except Exception as e:
            result.add_warning(f"Fast ICC extraction failed: {str(e)[:100]}")

    def _extract_iptc_metadata_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast IPTC metadata extraction using already-opened image"""
        try:
            from PIL import IptcImagePlugin

            iptc_data = {}
            if hasattr(img, 'info') and 'iptc' in img.info:
                iptc_dict = IptcImagePlugin.getiptcinfo(img)
                if iptc_dict:
                    for key, value in iptc_dict.items():
                        if value:
                            iptc_data[str(key)] = value

            if iptc_data:
                result.add_metadata("iptc", iptc_data)
            else:
                result.add_metadata("iptc", {"iptc_found": False})

        except ImportError:
            result.add_metadata("iptc", {"iptc_found": False, "note": "PIL IPTC plugin not available"})
        except Exception as e:
            result.add_warning(f"Fast IPTC extraction failed: {str(e)[:100]}")

    def _extract_xmp_metadata_fast(self, filepath: str, result: ImageExtractionResult, img):
        """Fast XMP metadata extraction using already-opened image"""
        try:
            xmp_data = {}
            if hasattr(img, 'info') and 'xmp' in img.info:
                xmp_string = img.info.get('xmp')
                if xmp_string:
                    # Basic XMP extraction (avoiding slow XML parsing)
                    xmp_data = {
                        "xmp_found": True,
                        "xmp_length": len(xmp_string),
                        "xmp_preview": xmp_string[:200] if len(xmp_string) > 200 else xmp_string
                    }

            if xmp_data:
                result.add_metadata("xmp", xmp_data)
            else:
                result.add_metadata("xmp", {"xmp_found": False})

        except Exception as e:
            result.add_warning(f"Fast XMP extraction failed: {str(e)[:100]}")
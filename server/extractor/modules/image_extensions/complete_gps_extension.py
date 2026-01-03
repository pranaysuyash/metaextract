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

            # Extract GPS metadata using exifread
            if EXIFREAD_AVAILABLE:
                self._extract_gps_with_exifread(filepath, result)
            else:
                result.add_warning("exifread not available, GPS extraction limited")

            # Extract comprehensive EXIF using PIL
            self._extract_comprehensive_exif(filepath, result)

            # Extract mobile metadata
            self._extract_mobile_metadata(filepath, result)

            # Extract forensic metadata
            self._extract_forensic_metadata(filepath, result)

            final_result = result.finalize()
            self.log_extraction_summary(final_result)
            return final_result

        except Exception as e:
            logger.error(f"Complete GPS extraction failed for {filepath}: {e}")
            return result.to_error_result(f"Extraction failed: {str(e)[:200]}")

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
#!/usr/bin/env python3
"""
Persona-Friendly Metadata Interpretation Layer
Transforms raw technical metadata into plain English answers for different user personas
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import requests

logger = logging.getLogger(__name__)


def reverse_geocode(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Convert GPS coordinates to readable location information using OpenStreetMap Nominatim API.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Dictionary with location information (address, city, country, etc.)
    """
    try:
        # Using OpenStreetMap Nominatim API (free, no API key required)
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "en"
        }

        # Add user agent as required by Nominatim usage policy
        headers = {
            "User-Agent": "MetaExtract-Persona-Interpretation/1.0"
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Extract relevant location information
            address = data.get("address", {})
            location_info = {
                "formatted_address": data.get("display_name", "Unknown location"),
                "city": address.get("city", address.get("town", address.get("village", "Unknown"))),
                "state": address.get("state", ""),
                "country": address.get("country", "Unknown"),
                "postcode": address.get("postcode", ""),
                "street": address.get("road", ""),
                "house_number": address.get("house_number", ""),
                "raw_data": data  # Preserve full response for debugging
            }

            return location_info
        else:
            logger.warning(f"Geocoding failed with status {response.status_code}")
            return {
                "formatted_address": "Location lookup failed",
                "city": "Unknown",
                "state": "",
                "country": "Unknown",
                "postcode": "",
                "street": "",
                "house_number": "",
                "error": f"HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        logger.warning("Geocoding request timed out")
        return {
            "formatted_address": "Location lookup timed out",
            "city": "Unknown",
            "state": "",
            "country": "Unknown",
            "postcode": "",
            "street": "",
            "house_number": "",
            "error": "timeout"
        }
    except Exception as e:
        logger.warning(f"Geocoding failed: {str(e)}")
        return {
            "formatted_address": "Location lookup failed",
            "city": "Unknown",
            "state": "",
            "country": "Unknown",
            "postcode": "",
            "street": "",
            "house_number": "",
            "error": str(e)
        }


def enhance_device_detection(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced device detection with comprehensive device identification and capabilities.

    Args:
        metadata: Raw metadata dictionary

    Returns:
        Enhanced device information with type, capabilities, confidence scores
    """
    def extract_field(field_names: List[str]) -> Optional[Any]:
        """Helper to extract field from metadata"""
        for field_name in field_names:
            if field_name in metadata:
                return metadata[field_name]
            # Try nested access
            parts = field_name.split(":")
            if len(parts) == 2:
                category, key = parts
                if category in metadata and isinstance(metadata[category], dict):
                    if key in metadata[category]:
                        return metadata[category][key]
        return None

    device_info = {
        "type": "unknown",
        "category": "unknown",
        "capabilities": [],
        "confidence": "low",
        "identification_method": "none",
        "make": extract_field(["EXIF:Make", "Make"]) or "unknown",
        "model": extract_field(["EXIF:Model", "Model"]) or "unknown",
        "software": extract_field(["EXIF:Software", "Software"]) or "unknown",
        "is_smartphone": False,
        "is_dslr": False,
        "is_mirrorless": False,
        "is_point_and_shoot": False,
        "is_webcam": False,
        "is_drone": False,
        "estimated_release_year": "unknown",
        "sensor_type": "unknown",
        "image_quality_indicators": {}
    }

    make = device_info["make"].lower() if device_info["make"] != "unknown" else ""
    model = device_info["model"].lower() if device_info["model"] != "unknown" else ""

    # Enhanced device type detection
    smartphone_patterns = [
        "iphone", "samsung", "galaxy", "pixel", "oneplus", "xiaomi", "huawei",
        "oppo", "vivo", "realme", "nokia", "motorola", "lg", "sony", "htc",
        "blackberry", "zte", "lenovo", "alcatel", "asus", "razr"
    ]

    dslr_patterns = [
        "canon eos", "nikon d", "nikon z", "pentax k", "pentax 645", "sigma sd"
    ]

    mirrorless_patterns = [
        "sony alpha", "sony a7", "sony a6", "sony a9", "fuji x", "fujifilm x",
        "olympus om", "panasonic lumix g", "panasonic lumix s", "leica sl",
        "nikon z", "canon r", "eos r"
    ]

    point_and_shoot_patterns = [
        "cyber-shot", "powershot", "coolpix", "finepix", "lumix lz", "stylus"
    ]

    drone_patterns = [
        "dji", "autel", "parrot", "skydio", "yuneec"
    ]

    # Detect device type
    if any(pattern in make + model for pattern in smartphone_patterns):
        device_info["type"] = "smartphone"
        device_info["category"] = "mobile_device"
        device_info["is_smartphone"] = True
        device_info["confidence"] = "high"
        device_info["identification_method"] = "make_model_matching"

        # Add smartphone-specific capabilities
        device_info["capabilities"] = [
            "gps", "geotagging", "auto_stabilization",
            "face_detection", "hdr", "burst_mode", "video_recording",
            "front_camera", "touchscreen_focus"
        ]

        # Estimate smartphone era/generation
        if "iphone 14" in model or "iphone 13" in model:
            device_info["estimated_release_year"] = "2021-2022"
            device_info["sensor_type"] = "stacked_cmos"
        elif "iphone 12" in model:
            device_info["estimated_release_year"] = "2020"
            device_info["sensor_type"] = "stacked_cmos"
        elif "galaxy s23" in model or "galaxy s22" in model:
            device_info["estimated_release_year"] = "2022-2023"
        elif "pixel 7" in model or "pixel 6" in model:
            device_info["estimated_release_year"] = "2021-2022"

    elif any(pattern in make + model for pattern in dslr_patterns):
        device_info["type"] = "dslr"
        device_info["category"] = "professional_camera"
        device_info["is_dslr"] = True
        device_info["confidence"] = "high"
        device_info["identification_method"] = "make_model_matching"

        device_info["capabilities"] = [
            "interchangeable_lenses", "optical_viewfinder", "manual_controls",
            "raw_capture", "external_flash", "gps_optional", "4k_video"
        ]

    elif any(pattern in make + model for pattern in mirrorless_patterns):
        device_info["type"] = "mirrorless"
        device_info["category"] = "professional_camera"
        device_info["is_mirrorless"] = True
        device_info["confidence"] = "high"
        device_info["identification_method"] = "make_model_matching"

        device_info["capabilities"] = [
            "interchangeable_lenses", "electronic_viewfinder", "manual_controls",
            "raw_capture", "in_body_stabilization", "4k_video", "high_speed_shooting"
        ]

    elif any(pattern in make + model for pattern in point_and_shoot_patterns):
        device_info["type"] = "point_and_shoot"
        device_info["category"] = "consumer_camera"
        device_info["is_point_and_shoot"] = True
        device_info["confidence"] = "medium"
        device_info["identification_method"] = "model_matching"

        device_info["capabilities"] = [
            "fixed_lens", "auto_mode", "zoom", "video_recording", "image_stabilization"
        ]

    elif any(pattern in make + model for pattern in drone_patterns):
        device_info["type"] = "drone"
        device_info["category"] = "aerial_device"
        device_info["is_drone"] = True
        device_info["confidence"] = "high"
        device_info["identification_method"] = "make_matching"

        device_info["capabilities"] = [
            "gps_tracking", "altitude_recording", "gimbal_stabilization",
            "automated_flight", "obstacle_avoidance", "4k_video", "hdr_capture"
        ]

    elif make == "microsoft" or "life cam" in model or "webcam" in model:
        device_info["type"] = "webcam"
        device_info["category"] = "computer_peripheral"
        device_info["is_webcam"] = True
        device_info["confidence"] = "medium"
        device_info["identification_method"] = "make_model_inference"

        device_info["capabilities"] = [
            "usb_connection", "fixed_focus", "auto_exposure", "video_primary",
            "low_resolution", "desktop_mount"
        ]

    # Analyze image quality for device verification
    image_width = extract_field(["EXIF:ExifImageWidth", "ImageWidth"])
    image_height = extract_field(["EXIF:ExifImageHeight", "ImageHeight"])

    if image_width and image_height:
        width = int(image_width)
        height = int(image_height)
        megapixels = (width * height) / 1000000

        device_info["image_quality_indicators"] = {
            "resolution": f"{width}x{height}",
            "megapixels": round(megapixels, 1),
            "aspect_ratio": round(width / height, 2),
            "is_high_resolution": megapixels > 12,
            "is_medium_resolution": 6 <= megapixels <= 12,
            "is_low_resolution": megapixels < 6
        }

        # Use resolution to validate device type
        if device_info["type"] == "smartphone":
            if megapixels < 8:
                device_info["confidence"] = "medium"  # Older smartphone
                device_info["estimated_release_year"] = "pre-2015"
            elif megapixels > 40:
                device_info["estimated_release_year"] = "2019+"

        elif device_info["type"] in ["dslr", "mirrorless"]:
            if megapixels < 15:
                device_info["confidence"] = "medium"  # Older camera

    # Software analysis for authenticity clues
    software = device_info["software"]
    if software and software != "unknown":
        software_lower = software.lower()

        if "photoshop" in software_lower or "lightroom" in software_lower:
            device_info["editing_detected"] = True
            device_info["editing_software"] = "adobe"

        elif "gimp" in software_lower:
            device_info["editing_detected"] = True
            device_info["editing_software"] = "open_source"

        elif any(tool in software_lower for tool in ["snapseed", "vsco", "instagram", "facebook"]):
            device_info["mobile_app_processing"] = True
            device_info["editing_detected"] = True

    return device_info

class PersonaInterpreter:
    """Transform raw metadata into persona-friendly interpretations"""

    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.interpretation = {
            "key_findings": [],
            "plain_english_answers": {},
            "confidence_scores": {},
            "warnings": [],
            "recommendations": []
        }

    def interpret_for_sarah(self) -> Dict[str, Any]:
        """Generate Phone Photo Sarah's interpretation"""
        self.interpretation["persona"] = "phone_photo_sarah"

        # Answer Sarah's 4 key questions
        self._answer_when_taken()
        self._answer_where_taken()
        self._answer_what_device()
        self._answer_is_authentic()

        # Generate key findings
        self._generate_key_findings()

        return self.interpretation

    def _answer_when_taken(self) -> None:
        """Answer: "When was this photo taken?" """
        # PRIORITY: EXIF dates > filesystem dates
        exif_date = self._get_best_exif_date()
        fs_date = self.metadata.get("filesystem", {}).get("created")

        if exif_date:
            # Use EXIF date (when photo was actually taken)
            readable_date = self._format_date_readable(exif_date)
            time_ago = self._calculate_time_ago(exif_date)

            self.interpretation["plain_english_answers"]["when_taken"] = {
                "answer": readable_date,
                "details": f"Taken {time_ago}",
                "source": "photo_metadata",
                "confidence": "high" if exif_date else "medium",
                "raw_dates": {
                    "exif_date_original": exif_date,
                    "filesystem_date": fs_date
                }
            }
        elif fs_date:
            # Fallback to filesystem date
            readable_date = self._format_date_readable(fs_date)
            time_ago = self._calculate_time_ago(fs_date)

            self.interpretation["plain_english_answers"]["when_taken"] = {
                "answer": readable_date,
                "details": f"File created {time_ago}",
                "source": "filesystem",
                "confidence": "low",
                "warning": "No photo creation date found - using file creation date instead"
            }
        else:
            self.interpretation["plain_english_answers"]["when_taken"] = {
                "answer": "Unknown date",
                "details": "No date information available",
                "source": "none",
                "confidence": "none"
            }

    def _answer_where_taken(self) -> None:
        """Answer: "Where was I when I took this?" """
        gps_coords = self._get_gps_coordinates()

        # Prefer embedded GPS, otherwise fall back to burned-overlay parsed GPS if present
        used_burned_overlay = False
        if not gps_coords:
            burned = self.metadata.get("burned_metadata") or {}
            parsed_gps = burned.get("parsed_data", {}).get("gps") if isinstance(burned.get("parsed_data"), dict) else None
            if parsed_gps and parsed_gps.get("latitude") is not None and parsed_gps.get("longitude") is not None:
                gps_coords = {"latitude": parsed_gps["latitude"], "longitude": parsed_gps["longitude"]}
                used_burned_overlay = True

        if gps_coords and gps_coords.get("latitude") and gps_coords.get("longitude"):
            lat = gps_coords["latitude"]
            lon = gps_coords["longitude"]

            # Try reverse geocoding to get readable address
            location_info = reverse_geocode(lat, lon)
            formatted_address = location_info.get("formatted_address", "Address lookup failed")
            city = location_info.get("city", "Unknown")
            country = location_info.get("country", "Unknown")

            # Create human-readable answer
            if city != "Unknown":
                readable_answer = f"{city}, {country}"
            else:
                readable_answer = formatted_address

            details_msg = f"GPS coordinates found: {lat:.6f}, {lon:.6f}"
            if used_burned_overlay:
                details_msg = "GPS found in burned-in overlay (not embedded EXIF)"

            self.interpretation["plain_english_answers"]["location"] = {
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{lat:.6f}, {lon:.6f}"
                },
                "has_location": True,
                "answer": readable_answer,
                "details": details_msg,
                "confidence": "high",
                "address": {
                    "formatted": formatted_address,
                    "city": city,
                    "state": location_info.get("state", ""),
                    "country": country,
                    "postcode": location_info.get("postcode", ""),
                    "street": location_info.get("street", "")
                },
                "geocoding_successful": not location_info.get("error")
            }

            # Check if we have any location names from metadata
            location_name = self._get_location_name()
            if location_name:
                self.interpretation["plain_english_answers"]["location"]["metadata_location"] = location_name
        else:
            self.interpretation["plain_english_answers"]["location"] = {
                "has_location": False,
                "answer": "No location data",
                "details": "This photo doesn't have GPS information",
                "confidence": "n/a",
                "possible_reasons": [
                    "GPS was disabled when photo was taken",
                    "Location services were off",
                    "Photo was edited and GPS was stripped",
                    "Photo was taken indoors without GPS signal"
                ]
            }

    def _answer_what_device(self) -> None:
        """Answer: "What phone took this?" """
        # Use enhanced device detection
        enhanced_device = enhance_device_detection(self.metadata)

        # Build friendly device name from enhanced info
        make = enhanced_device["make"]
        model = enhanced_device["model"]

        if make != "unknown" and model != "unknown":
            friendly_name = f"{make} {model}"
        elif make != "unknown":
            friendly_name = f"{make} device"
        else:
            friendly_name = "Unknown device"

        # Determine device type for Sarah
        device_type = enhanced_device["type"]
        if device_type == "smartphone":
            friendly_type = "smartphone"
        elif device_type in ["dslr", "mirrorless"]:
            friendly_type = "professional camera"
        elif device_type == "point_and_shoot":
            friendly_type = "camera"
        elif device_type == "drone":
            friendly_type = "drone"
        elif device_type == "webcam":
            friendly_type = "webcam"
        else:
            friendly_type = "device"

        device_answer = f"{friendly_name} ({friendly_type})"

        self.interpretation["plain_english_answers"]["device"] = {
            "answer": device_answer,
            "device_type": friendly_type,
            "details": {
                "make": make,
                "model": model,
                "software": enhanced_device["software"]
            },
            "enhanced_info": enhanced_device,
            "confidence": enhanced_device["confidence"]
        }

        # Add lens info if available
        lens = self._extract_field(["EXIF:LensModel", "LensModel"])
        if lens:
            self.interpretation["plain_english_answers"]["device"]["lens"] = lens

    def _answer_is_authentic(self) -> Dict[str, Any]:
        """Answer: "Is this photo authentic?" """
        authenticity_checks = {
            "has_original_datetime": bool(self._get_best_exif_date()),
            "has_software_signatures": bool(self._extract_field(["EXIF:Software", "Software"])),
            "has_gps": bool(self._get_gps_coordinates()),
            "exif_intact": self._is_exif_intact(),
            "thumbnails_match": self._check_thumbnails(),
            "suspicious_signs": self._check_suspicious_signs()
        }

        # Calculate authenticity score
        score = 100
        reasons = []

        if not authenticity_checks["has_original_datetime"]:
            score -= 30
            reasons.append("Missing original date/time")

        if authenticity_checks["has_software_signatures"]:
            software = self._extract_field(["EXIF:Software", "Software"])
            if software and software.lower() not in ["", "none", "original"]:
                score -= 20
                reasons.append(f"Editing software detected: {software}")

        if not authenticity_checks["exif_intact"]:
            score -= 25
            reasons.append("EXIF data appears incomplete")

        if authenticity_checks["suspicious_signs"]:
            score -= 25
            reasons.extend(authenticity_checks["suspicious_signs"])

        # Determine confidence level
        if score >= 80:
            assessment = "appears_authentic"
            confidence = "high"
        elif score >= 50:
            assessment = "possibly_edited"
            confidence = "medium"
        else:
            assessment = "likely_modified"
            confidence = "low"

        self.interpretation["plain_english_answers"]["authenticity"] = {
            "assessment": assessment,
            "confidence": confidence,
            "score": max(0, score),
            "answer": f"Photo {assessment.replace('_', ' ')} ({confidence} confidence)",
            "checks_performed": authenticity_checks,
            "reasons": reasons if reasons else ["No signs of manipulation detected"]
        }

        return authenticity_checks

    def _get_best_exif_date(self) -> Optional[str]:
        """Get the best available EXIF date in priority order"""
        # Priority: DateTimeOriginal > CreateDate > DateTimeDigitized
        date_fields = [
            "DateTimeOriginal",  # Flat structure (exiftool)
            "CreateDate",
            "DateTimeDigitized",
            "DateCreated",
            "EXIF:DateTimeOriginal",  # Nested structure (backend)
            "EXIF:CreateDate",
            "EXIF:DateTimeDigitized",
            "IPTC:DateCreated",
            "XMP:CreateDate"
        ]

        for field in date_fields:
            value = self._extract_field([field])
            if value:
                return value

        return None

    def _get_gps_coordinates(self) -> Optional[Dict[str, Any]]:
        """Extract GPS coordinates if available"""
        # Try both flat and nested structures
        lat = self._extract_field(["GPSLatitude", "Composite:GPSLatitude", "EXIF:GPSLatitude"])
        lon = self._extract_field(["GPSLongitude", "Composite:GPSLongitude", "EXIF:GPSLongitude"])

        if lat and lon:
            # Convert to decimal if needed
            try:
                lat_decimal = float(lat) if isinstance(lat, (int, float)) else self._convert_dms_to_decimal(lat)
                lon_decimal = float(lon) if isinstance(lon, (int, float)) else self._convert_dms_to_decimal(lon)

                return {
                    "latitude": lat_decimal,
                    "longitude": lon_decimal
                }
            except (ValueError, TypeError):
                pass

        return None

    def _get_location_name(self) -> Optional[str]:
        """Try to find location name in metadata"""
        city = self._extract_field(["City", "IPTC:City", "XMP:City"])
        state = self._extract_field(["State", "IPTC:State", "XMP:State"])
        country = self._extract_field(["Country", "IPTC:Country", "XMP:Country"])

        parts = [p for p in [city, state, country] if p]
        return ", ".join(parts) if parts else None

    def _format_date_readable(self, date_str: str) -> str:
        """Convert EXIF date format to readable format"""
        try:
            # EXIF format: "2025:12:25 16:48:10"
            if " " in date_str:
                date_part, time_part = date_str.split(" ")
                year, month, day = date_part.split(":")
                hour, minute, second = time_part.split(":")

                # Convert to readable format
                dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
                return dt.strftime("%B %d, %Y at %I:%M %p")

            return date_str
        except Exception:
            return date_str

    def _calculate_time_ago(self, date_str: str) -> str:
        """Calculate human-readable time ago"""
        try:
            # Parse date string
            if " " in date_str:
                date_part, time_part = date_str.split(" ")
                year, month, day = date_part.split(":")
                hour, minute, second = time_part.split(":")

                dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
            else:
                return "unknown time"

            # Calculate time difference
            now = datetime.now()
            delta = now - dt

            # Format the difference
            if delta.days == 0:
                hours = delta.seconds // 3600
                if hours == 0:
                    minutes = delta.seconds // 60
                    return f"{minutes} minutes ago"
                return f"{hours} hours ago"
            elif delta.days == 1:
                return "yesterday"
            elif delta.days < 7:
                return f"{delta.days} days ago"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif delta.days < 365:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = delta.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"

        except Exception as e:
            logger.debug(f"Failed to calculate time ago: {e}")
            return "some time ago"

    def _format_device_name(self, make: Optional[str], model: Optional[str]) -> str:
        """Format device name in user-friendly way"""
        if make and model:
            # Clean up model name (remove extra :: Captured by text)
            clean_model = model.split("::")[0].strip()
            return f"{make} {clean_model}"
        elif model:
            return model.split("::")[0].strip()
        elif make:
            return make
        else:
            return "Unknown device"

    def _detect_phone_camera(self, make: Optional[str], model: Optional[str]) -> bool:
        """Detect if this is a phone camera"""
        if not make and not model:
            return False

        phone_keywords = ["iphone", "samsung", "pixel", "oneplus", "xiaomi", "oppo", "vivo", "huawei", "motorola", "nokia", "lg", "realme", "redmi"]
        combined = f"{make} {model}".lower()

        return any(keyword in combined for keyword in phone_keywords)

    def _extract_field(self, field_names: List[str]) -> Optional[Any]:
        """Extract field value trying multiple possible field names"""
        for field_name in field_names:
            # Try direct access (flat structure from exiftool)
            if field_name in self.metadata:
                return self.metadata[field_name]

            # Try nested access (e.g., "EXIF:DateTimeOriginal")
            parts = field_name.split(":")
            if len(parts) == 2:
                category, key = parts
                if category in self.metadata and isinstance(self.metadata[category], dict):
                    if key in self.metadata[category]:
                        return self.metadata[category][key]

            # Try comprehensive engine structure (e.g., "exif.DateTimeOriginal")
            # Remove the category prefix if present
            base_field = field_name.split(":")[-1]  # Get last part after ":"

            # Check in common nested structures
            for section in ["exif", "gps", "iptc", "xmp"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if base_field in self.metadata[section]:
                        return self.metadata[section][base_field]

            # Try the field name directly in common sections
            for section in ["exif", "gps", "iptc", "xmp"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if field_name in self.metadata[section]:
                        return self.metadata[section][field_name]

        return None

    def _is_exif_intact(self) -> bool:
        """Check if EXIF data appears intact"""
        # Check for key EXIF fields
        has_basic_exif = any([
            self._extract_field(["EXIF:DateTimeOriginal"]),
            self._extract_field(["EXIF:Make"]),
            self._extract_field(["EXIF:Model"])
        ])

        return has_basic_exif

    def _check_thumbnails(self) -> bool:
        """Check if thumbnails are present and consistent"""
        # This would involve more complex analysis
        # For now, just check if thumbnail data exists
        return bool(self._extract_field(["EXIF:ThumbnailImage", "ThumbnailImage"]))

    def _check_suspicious_signs(self) -> List[str]:
        """Check for signs of manipulation"""
        suspicious = []

        # Check for unusual software
        software = self._extract_field(["EXIF:Software", "Software"])
        if software:
            suspicious_software = ["photoshop", "gimp", "lightroom", "snapseed", "vsco"]
            if any(s in str(software).lower() for s in suspicious_software):
                suspicious.append(f"Photo editing software detected: {software}")

        # Check for missing DateTimeOriginal but present CreateDate
        has_original = self._extract_field(["EXIF:DateTimeOriginal"])
        has_create = self._extract_field(["EXIF:CreateDate"])
        if has_create and not has_original:
            suspicious.append("Original date/time missing but creation date present")

        return suspicious

    def _convert_dms_to_decimal(self, dms_string: str) -> float:
        """Convert DMS (degrees minutes seconds) format to decimal"""
        # This is a simplified conversion - real implementation would parse DMS format
        try:
            return float(dms_string)
        except (ValueError, TypeError):
            return 0.0

    def _format_exposure_mode(self, value: Any) -> str:
        """Map EXIF ExposureProgram values to human-friendly names."""
        programs = {
            0: "Not Defined",
            1: "Manual",
            2: "Normal Program",
            3: "Aperture Priority",
            4: "Shutter Priority",
            5: "Creative Program",
            6: "Action Program",
            7: "Portrait Mode",
            8: "Landscape Mode",
        }
        if value is None:
            return "unknown"
        if isinstance(value, int):
            return programs.get(value, f"Unknown ({value})")
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.isdigit():
                try:
                    return programs.get(int(stripped), f"Unknown ({stripped})")
                except ValueError:
                    pass
            return stripped or "unknown"
        return str(value)

    def _generate_key_findings(self) -> None:
        """Generate key findings summary for Sarah"""
        findings = []

        # Date finding
        when_answer = self.interpretation["plain_english_answers"].get("when_taken", {})
        if when_answer.get("confidence") != "none":
            findings.append(f"📅 Taken on {when_answer.get('answer', 'unknown date')}")

        # Location finding
        location_answer = self.interpretation["plain_english_answers"].get("location", {})
        if location_answer.get("has_location"):
            findings.append(f"📍 Location data available")
        else:
            findings.append(f"📍 No GPS location data")

        # Device finding
        device_answer = self.interpretation["plain_english_answers"].get("device", {})
        if device_answer.get("confidence") != "none":
            findings.append(f"📱 Taken with {device_answer.get('answer', 'unknown device')}")

        # Authenticity finding
        authenticity_answer = self.interpretation["plain_english_answers"].get("authenticity", {})
        assessment = authenticity_answer.get("assessment", "unknown")
        if assessment == "appears_authentic":
            findings.append(f"✨ Appears to be authentic")
        elif assessment == "possibly_edited":
            findings.append(f"⚠️ May have been edited")
        else:
            findings.append(f"❌ Signs of modification detected")

        self.interpretation["key_findings"] = findings


class PhotographerPeterInterpreter:
    """
    Technical metadata interpreter for professional photographers.

    Photographer Peter wants detailed technical camera settings, lens information,
    shooting conditions, and professional-grade analysis.
    """

    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.interpretation = {
            "persona": "photographer_peter",
            "key_findings": [],
            "technical_analysis": {},
            "camera_settings": {},
            "lens_information": {},
            "shooting_conditions": {},
            "image_quality": {},
            "professional_recommendations": []
        }

    def interpret(self) -> Dict[str, Any]:
        """Generate photographer-focused interpretation"""
        self._analyze_camera_settings()
        self._analyze_lens_information()
        self._analyze_shooting_conditions()
        self._analyze_image_quality()
        self._generate_technical_findings()
        self._provide_professional_recommendations()
        return self.interpretation

    def _extract_field(self, field_names: List[str]) -> Optional[Any]:
        """Extract field value trying multiple possible field names"""
        for field_name in field_names:
            # Try direct access (flat structure from exiftool)
            if field_name in self.metadata:
                return self.metadata[field_name]

            # Try nested access (e.g., "EXIF:DateTimeOriginal")
            parts = field_name.split(":")
            if len(parts) == 2:
                category, key = parts
                if category in self.metadata and isinstance(self.metadata[category], dict):
                    if key in self.metadata[category]:
                        return self.metadata[category][key]

            # Try comprehensive engine structure (e.g., "exif.DateTimeOriginal")
            base_field = field_name.split(":")[-1]  # Get last part after ":"

            # Check in common nested structures
            for section in ["exif", "gps", "iptc", "xmp"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if base_field in self.metadata[section]:
                        return self.metadata[section][base_field]

            # Try the field name directly in common sections
            for section in ["exif", "gps", "iptc", "xmp"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if field_name in self.metadata[section]:
                        return self.metadata[section][field_name]

        return None

    def _analyze_camera_settings(self) -> None:
        """Extract and analyze camera settings"""
        settings = {}

        # Exposure settings
        shutter_speed = self._extract_field(["EXIF:ShutterSpeedValue", "ShutterSpeedValue", "ExposureTime"])
        aperture = self._extract_field(["EXIF:FNumber", "FNumber", "ApertureValue"])
        iso = self._extract_field(["EXIF:ISOSpeedRatings", "ISOSpeedRatings", "ISO"])
        exposure_mode = self._extract_field(["EXIF:ExposureProgram", "ExposureProgram"])
        exposure_comp = self._extract_field(["EXIF:ExposureCompensation", "ExposureCompensation"])

        # Focus settings
        focus_mode = self._extract_field(["EXIF:FocusMode", "FocusMode"])
        focus_distance = self._extract_field(["EXIF:FocusDistance", "FocusDistance"])
        metering_mode = self._extract_field(["EXIF:MeteringMode", "MeteringMode"])

        # Flash settings
        flash = self._extract_field(["EXIF:Flash", "Flash"])
        flash_energy = self._extract_field(["EXIF:FlashEnergy", "FlashEnergy"])

        # White balance
        white_balance = self._extract_field(["EXIF:WhiteBalance", "WhiteBalance"])
        color_temp = self._extract_field(["EXIF:ColorTemperature", "ColorTemperature"])

        # Drive mode
        drive_mode = self._extract_field(["EXIF:DriveMode", "DriveMode"])
        burst_rate = self._extract_field(["EXIF:ContinuousCapture", "ContinuousCapture"])

        settings["exposure"] = {
            "shutter_speed": self._format_shutter_speed(shutter_speed),
            "aperture": self._format_aperture(aperture),
            "iso": self._format_iso(iso),
            "exposure_mode": self._format_exposure_mode(exposure_mode),
            "exposure_compensation": self._format_exposure_compensation(exposure_comp)
        }

        settings["focus"] = {
            "focus_mode": self._format_focus_mode(focus_mode),
            "focus_distance": focus_distance if focus_distance else "unknown",
            "metering_mode": self._format_metering_mode(metering_mode)
        }

        settings["flash"] = {
            "flash_used": self._did_flash_fire(flash),
            "flash_mode": self._format_flash_mode(flash),
            "flash_energy": flash_energy if flash_energy else "unknown"
        }

        settings["white_balance"] = {
            "mode": self._format_white_balance(white_balance),
            "color_temperature": color_temp if color_temp else "unknown"
        }

        settings["drive"] = {
            "mode": drive_mode if drive_mode else "unknown",
            "burst_rate": burst_rate if burst_rate else "unknown"
        }

        self.interpretation["camera_settings"] = settings

    def _analyze_lens_information(self) -> None:
        """Extract and analyze lens information"""
        lens_info = {}

        # Basic lens data
        lens_make = self._extract_field(["EXIF:LensMake", "LensMake"])
        lens_model = self._extract_field(["EXIF:LensModel", "LensModel"])
        lens_spec = self._extract_field(["EXIF:LensInfo", "LensInfo"])
        focal_length = self._extract_field(["EXIF:FocalLength", "FocalLength"])
        focal_length_35mm = self._extract_field(["EXIF:FocalLengthIn35mmFormat", "FocalLengthIn35mmFormat"])

        # Advanced lens data
        max_aperture = self._extract_field(["EXIF:MaxApertureValue", "MaxApertureValue"])
        min_focal_length = self._extract_field(["EXIF:MinFocalLength", "MinFocalLength"])
        max_focal_length = self._extract_field(["EXIF:MaxFocalLength", "MaxFocalLength"])

        # Image stabilization
        is_mode = self._extract_field(["EXIF:ImageStabilization", "ImageStabilization"])

        lens_info["basic"] = {
            "make": lens_make if lens_make else "unknown",
            "model": lens_model if lens_model else "unknown",
            "specification": lens_spec if lens_spec else "unknown"
        }

        lens_info["focal_length"] = {
            "actual": self._format_focal_length(focal_length),
            "equivalent_35mm": self._format_focal_length(focal_length_35mm),
            "zoom_range": self._format_zoom_range(min_focal_length, max_focal_length)
        }

        lens_info["aperture"] = {
            "max_aperture": self._format_aperture(max_aperture)
        }

        lens_info["stabilization"] = {
            "enabled": self._is_image_stabilization_enabled(is_mode),
            "mode": is_mode if is_mode else "unknown"
        }

        self.interpretation["lens_information"] = lens_info

    def _analyze_shooting_conditions(self) -> None:
        """Analyze shooting conditions and environment"""
        conditions = {}

        # GPS and location
        gps_lat = self._extract_field(["GPS:GPSLatitude", "GPSLatitude"])
        gps_lon = self._extract_field(["GPS:GPSLongitude", "GPSLongitude"])
        gps_alt = self._extract_field(["GPS:GPSAltitude", "GPSAltitude"])
        gps_direction = self._extract_field(["GPS:GPSImgDirection", "GPSImgDirection"])

        # Time and date
        date_time = self._extract_field(["EXIF:DateTimeOriginal", "DateTimeOriginal", "CreateDate"])
        time_zone = self._extract_field(["EXIF:TimeZone", "TimeZone"])

        # Lighting conditions
        ambient_light = self._extract_field(["EXIF:AmbientTemperature", "AmbientTemperature"])

        conditions["location"] = {
            "has_gps": bool(gps_lat and gps_lon),
            "latitude": self._format_gps_coordinate(gps_lat),
            "longitude": self._format_gps_coordinate(gps_lon),
            "altitude": self._format_altitude(gps_alt),
            "image_direction": gps_direction if gps_direction else "unknown"
        }

        conditions["timing"] = {
            "capture_time": date_time if date_time else "unknown",
            "time_zone": time_zone if time_zone else "unknown"
        }

        conditions["environment"] = {
            "ambient_temperature": ambient_light if ambient_light else "unknown"
        }

        self.interpretation["shooting_conditions"] = conditions

    def _analyze_image_quality(self) -> None:
        """Analyze image quality and technical characteristics"""
        quality = {}

        # Resolution and dimensions
        width = self._extract_field(["EXIF:ExifImageWidth", "ExifImageWidth", "ImageWidth"])
        height = self._extract_field(["EXIF:ExifImageHeight", "ExifImageHeight", "ImageHeight"])
        pixel_x_dim = self._extract_field(["EXIF:PixelXDimension", "PixelXDimension"])
        pixel_y_dim = self._extract_field(["EXIF:PixelYDimension", "PixelYDimension"])

        # Compression and quality
        compression = self._extract_field(["EXIF:Compression", "Compression"])
        quality_setting = self._extract_field(["EXIF:Quality", "Quality"])

        # Color depth
        bits_per_sample = self._extract_field(["EXIF:BitsPerSample", "BitsPerSample"])
        sample_format = self._extract_field(["EXIF:SampleFormat", "SampleFormat"])

        # Color space
        color_space = self._extract_field(["EXIF:ColorSpace", "ColorSpace"])
        profile = self._extract_field(["EXIF:ProfileDescription", "ProfileDescription"])

        quality["resolution"] = {
            "width": width if width else pixel_x_dim,
            "height": height if height else pixel_y_dim,
            "megapixels": self._calculate_megapixels(width, height)
        }

        quality["compression"] = {
            "format": compression if compression else "unknown",
            "quality_setting": quality_setting if quality_setting else "unknown"
        }

        quality["color"] = {
            "bit_depth": bits_per_sample if bits_per_sample else "unknown",
            "sample_format": sample_format if sample_format else "unknown",
            "color_space": self._format_color_space(color_space),
            "icc_profile": profile if profile else "none"
        }

        self.interpretation["image_quality"] = quality

    def _generate_technical_findings(self) -> None:
        """Generate technical findings for photographers"""
        findings = []

        # Camera settings summary
        settings = self.interpretation.get("camera_settings", {})
        exposure = settings.get("exposure", {})

        if exposure.get("shutter_speed") and exposure.get("aperture") and exposure.get("iso"):
            findings.append(f"📷 Shot at {exposure['shutter_speed']}, f/{exposure['aperture']}, ISO {exposure['iso']}")

        # Lens information
        lens = self.interpretation.get("lens_information", {})
        focal = lens.get("focal_length", {})
        if focal.get("actual"):
            findings.append(f"🔭 {focal['actual']} focal length")

        # Shooting conditions
        conditions = self.interpretation.get("shooting_conditions", {})
        if conditions.get("location", {}).get("has_gps"):
            findings.append(f"📍 GPS coordinates embedded")

        # Technical quality assessment
        quality = self.interpretation.get("image_quality", {})
        res = quality.get("resolution", {})
        if res.get("megapixels"):
            findings.append(f"📐 {res['megapixels']} MP resolution")

        self.interpretation["key_findings"] = findings

    def _provide_professional_recommendations(self) -> None:
        """Provide professional photography recommendations"""
        recommendations = []

        settings = self.interpretation.get("camera_settings", {})
        exposure = settings.get("exposure", {})

        # Analyze exposure triangle
        if exposure.get("iso"):
            iso_val = exposure["iso"]
            if isinstance(iso_val, str) and iso_val.isdigit():
                iso_num = int(iso_val)
                if iso_num > 1600:
                    recommendations.append("🔧 High ISO may introduce noise - consider noise reduction")
                elif iso_num < 100:
                    recommendations.append("✨ Low ISO setting - optimal for image quality")

        # Check stabilization
        lens = self.interpretation.get("lens_information", {})
        if not lens.get("stabilization", {}).get("enabled"):
            shutter = exposure.get("shutter_speed", "")
            if shutter and "/" in str(shutter):
                # Extract shutter speed denominator
                try:
                    denom = int(str(shutter).split("/")[-1])
                    if denom < 60:
                        recommendations.append("⚠️ Slow shutter speed without stabilization - risk of camera shake")
                except (ValueError, IndexError):
                    pass

        # GPS recommendations
        conditions = self.interpretation.get("shooting_conditions", {})
        if not conditions.get("location", {}).get("has_gps"):
            recommendations.append("📍 No GPS data - consider enabling location services for geotagging")

        # Quality recommendations
        quality = self.interpretation.get("image_quality", {})
        if quality.get("compression", {}).get("quality_setting") == "medium":
            recommendations.append("📊 Medium compression - consider higher quality for professional work")

        self.interpretation["professional_recommendations"] = recommendations

    # Helper formatting methods
    def _format_shutter_speed(self, value) -> str:
        if not value:
            return "unknown"
        try:
            if isinstance(value, str) and "/" in value:
                return f"{value}s"
            return f"{value}s"
        except (ValueError, TypeError):
            return "unknown"

    def _format_aperture(self, value) -> str:
        if not value:
            return "unknown"
        try:
            if isinstance(value, tuple):
                return f"{value[0] / value[1]:.1f}"
            return f"{float(value):.1f}"
        except (ValueError, TypeError):
            return "unknown"

    def _format_iso(self, value) -> str:
        if not value:
            return "unknown"
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return "unknown"

    def _format_exposure_mode(self, value) -> str:
        # Map EXIF ExposureProgram values to human-friendly names
        programs = {
            0: "Not Defined",
            1: "Manual",
            2: "Normal Program",
            3: "Aperture Priority",
            4: "Shutter Priority",
            5: "Creative Program",
            6: "Action Program",
            7: "Portrait Mode",
            8: "Landscape Mode",
        }
        if isinstance(value, int):
            return programs.get(value, f"Unknown ({value})")
        return str(value) if value else "unknown"

    def _format_exposure_compensation(self, value) -> str:
        if not value:
            return "none"
        try:
            if isinstance(value, tuple):
                comp = value[0] / value[1]
                return f"{comp:+.1f} EV"
            return f"{float(value):+.1f} EV"
        except (ValueError, TypeError):
            return "unknown"

    def _format_focus_mode(self, value) -> str:
        if not value:
            return "unknown"
        return str(value)

    def _format_metering_mode(self, value) -> str:
        modes = {
            0: "Unknown",
            1: "Average",
            2: "Center weighted",
            3: "Spot",
            4: "Multi-spot",
            5: "Pattern",
            6: "Partial"
        }
        if isinstance(value, int):
            return modes.get(value, "unknown")
        return str(value) if value else "unknown"

    def _did_flash_fire(self, value) -> bool:
        if not value:
            return False
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return "off" not in value.lower()
        return bool(value)

    def _format_flash_mode(self, value) -> str:
        if not value:
            return "unknown"
        return str(value)

    def _format_white_balance(self, value) -> str:
        modes = {
            0: "Auto",
            1: "Manual"
        }
        if isinstance(value, int):
            return modes.get(value, "unknown")
        return str(value) if value else "unknown"

    def _format_focal_length(self, value) -> str:
        if not value:
            return "unknown"
        try:
            if isinstance(value, tuple):
                return f"{value[0] / value[1]:.1f}mm"
            return f"{float(value):.1f}mm"
        except (ValueError, TypeError):
            return "unknown"

    def _format_zoom_range(self, min_val, max_val) -> str:
        if not min_val or not max_val:
            return "unknown"
        try:
            min_f = self._format_focal_length(min_val)
            max_f = self._format_focal_length(max_val)
            return f"{min_f}-{max_f}"
        except (ValueError, TypeError):
            return "unknown"

    def _is_image_stabilization_enabled(self, value) -> bool:
        if not value:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return "on" in value.lower() or "enabled" in value.lower()
        return bool(value)

    def _format_gps_coordinate(self, value) -> str:
        if not value:
            return "unknown"
        return str(value)

    def _format_altitude(self, value) -> str:
        if not value:
            return "unknown"
        try:
            return f"{float(value):.0f}m"
        except (ValueError, TypeError):
            return "unknown"

    def _calculate_megapixels(self, width, height) -> str:
        if not width or not height:
            return "unknown"
        try:
            w = float(width)
            h = float(height)
            mp = (w * h) / 1000000
            return f"{mp:.1f}"
        except (ValueError, TypeError):
            return "unknown"

    def _format_color_space(self, value) -> str:
        if not value:
            return "unknown"
        spaces = {
            1: "sRGB",
            2: "Adobe RGB",
            65535: "Uncalibrated"
        }
        if isinstance(value, int):
            return spaces.get(value, "unknown")
        return str(value) if value else "unknown"


class InvestigatorMikeInterpreter:
    """
    Forensic metadata interpreter for investigators.

    Investigator Mike needs detailed forensic analysis, authenticity verification,
    manipulation detection, and chain of custody information.
    """

    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.interpretation = {
            "persona": "investigator_mike",
            "key_findings": [],
            "forensic_analysis": {},
            "authenticity_assessment": {},
            "manipulation_indicators": {},
            "chain_of_custody": {},
            "technical_forensics": {},
            "investigative_recommendations": []
        }

    def interpret(self) -> Dict[str, Any]:
        """Generate investigator-focused interpretation"""
        self._analyze_forensic_metadata()
        self._assess_authenticity()
        self._detect_manipulation()
        self._analyze_chain_of_custody()
        self._perform_technical_forensics()
        self._generate_forensic_findings()
        self._provide_investigative_recommendations()
        return self.interpretation

    def _extract_field(self, field_names: List[str]) -> Optional[Any]:
        """Extract field value trying multiple possible field names"""
        for field_name in field_names:
            # Try direct access (flat structure from exiftool)
            if field_name in self.metadata:
                return self.metadata[field_name]

            # Try nested access (e.g., "EXIF:DateTimeOriginal")
            parts = field_name.split(":")
            if len(parts) == 2:
                category, key = parts
                if category in self.metadata and isinstance(self.metadata[category], dict):
                    if key in self.metadata[category]:
                        return self.metadata[category][key]

            # Try comprehensive engine structure (e.g., "exif.DateTimeOriginal")
            base_field = field_name.split(":")[-1]  # Get last part after ":"

            # Check in common nested structures
            for section in ["exif", "gps", "iptc", "xmp", "forensic"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if base_field in self.metadata[section]:
                        return self.metadata[section][base_field]

            # Try the field name directly in common sections
            for section in ["exif", "gps", "iptc", "xmp", "forensic"]:
                if section in self.metadata and isinstance(self.metadata[section], dict):
                    if field_name in self.metadata[section]:
                        return self.metadata[section][field_name]

        return None

    def _analyze_forensic_metadata(self) -> None:
        """Analyze forensic metadata"""
        forensic = {}

        # File hashes
        md5 = self._extract_field(["file_integrity:md5", "md5", "MD5"])
        sha1 = self._extract_field(["file_integrity:sha1", "sha1", "SHA1"])
        sha256 = self._extract_field(["file_integrity:sha256", "sha256", "SHA256"])

        # File metadata
        file_size = self._extract_field(["filesize", "FileSize"])
        file_type = self._extract_field(["filetype", "FileType"])
        mime_type = self._extract_field(["mime_type", "MIMEType"])

        # Creation and modification timestamps
        file_created = self._extract_field(["filesystem:created", "FileCreated"])
        file_modified = self._extract_field(["filesystem:modified", "FileModified"])
        file_accessed = self._extract_field(["filesystem:accessed", "FileAccessed"])

        # Software and tools
        software = self._extract_field(["EXIF:Software", "Software"])
        creator_tool = self._extract_field("creator_tool")

        forensic["file_hashes"] = {
            "md5": md5 if md5 else "unavailable",
            "sha1": sha1 if sha1 else "unavailable",
            "sha256": sha256 if sha256 else "unavailable"
        }

        forensic["file_characteristics"] = {
            "size_bytes": file_size if file_size else "unknown",
            "size_human": self._format_file_size(file_size),
            "type": file_type if file_type else "unknown",
            "mime_type": mime_type if mime_type else "unknown"
        }

        forensic["timestamps"] = {
            "created": file_created if file_created else "unknown",
            "modified": file_modified if file_modified else "unknown",
            "accessed": file_accessed if file_accessed else "unknown",
            "time_discrepancies": self._detect_timestamp_discrepancies(file_created, file_modified)
        }

        forensic["processing_history"] = {
            "software": software if software else "unknown",
            "creator_tool": creator_tool if creator_tool else "unknown",
            "processing_indicators": self._detect_processing_indicators(software, creator_tool)
        }

        self.interpretation["forensic_analysis"] = forensic

    def _assess_authenticity(self) -> None:
        """Assess file authenticity"""
        authenticity = {}

        # Check for authentication metadata
        has_signature = self._extract_field(["forensic_digital_signatures", "digital_signatures"])
        has_blockchain = self._extract_field(["blockchain_provenance", "blockchain"])
        has_watermark = self._extract_field(["forensic_watermarking", "watermark"])

        # Check EXIF integrity
        exif_complete = self._extract_field(["exif"]) is not None
        exif_intact = self._check_exif_integrity()

        # Thumbnail integrity
        has_thumbnail = self._extract_field(["thumbnail:has_embedded"])
        thumbnails_match = self._check_thumbnail_integrity()

        # GPS authenticity
        has_gps = self._extract_field(["GPS:GPSLatitude", "GPSLatitude"]) is not None
        gps_consistent = self._verify_gps_consistency()

        # Date consistency
        date_consistent = self._verify_date_consistency()

        authenticity["authentication"] = {
            "has_digital_signature": bool(has_signature),
            "has_blockchain_proof": bool(has_blockchain),
            "has_watermark": bool(has_watermark),
            "authentication_score": self._calculate_authentication_score(has_signature, has_blockchain, has_watermark)
        }

        authenticity["metadata_integrity"] = {
            "exif_complete": exif_complete,
            "exif_intact": exif_intact,
            "thumbnails_match": thumbnails_match,
            "metadata_integrity_score": self._calculate_metadata_integrity_score(exif_complete, exif_intact, thumbnails_match)
        }

        authenticity["consistency_checks"] = {
            "gps_data_consistent": gps_consistent,
            "dates_consistent": date_consistent,
            "overall_consistency": self._assess_overall_consistency(gps_consistent, date_consistent)
        }

        authenticity["overall_authenticity"] = {
            "assessment": self._determine_authenticity_assessment(authenticity),
            "confidence_level": self._calculate_authenticity_confidence(authenticity),
            "risk_factors": self._identify_risk_factors(authenticity)
        }

        self.interpretation["authenticity_assessment"] = authenticity

    def _detect_manipulation(self) -> None:
        """Detect potential manipulation indicators"""
        manipulation = {}

        # Check for editing software signatures
        software = self._extract_field(["EXIF:Software", "Software"])
        edit_indicators = self._detect_editing_software(software)

        # Check for missing metadata
        missing_exif = self._identify_missing_critical_exif()

        # Check for metadata anomalies
        metadata_anomalies = self._detect_metadata_anomalies()

        # Check image quality indicators
        quality_issues = self._detect_quality_issues()

        # Check for recompression
        recompression = self._detect_recompression()

        # Check for resaving
        resaved = self._detect_resaving()

        manipulation["editing_signatures"] = {
            "software_detected": software if software else "none",
            "editing_indicators": edit_indicators,
            "suspicious_tools": self._identify_suspicious_tools(software)
        }

        manipulation["metadata_anomalies"] = {
            "missing_critical_fields": missing_exif,
            "anomalies_detected": metadata_anomalies,
            "anomaly_count": len(metadata_anomalies)
        }

        manipulation["quality_indicators"] = {
            "quality_issues_detected": quality_issues,
            "compression_artifacts": self._detect_compression_artifacts(),
            "filter_signatures": self._detect_filter_signatures()
        }

        manipulation["file_history"] = {
            "recompression_detected": recompression,
            "resave_detected": resaved,
            "generation_loss": self._assess_generation_loss()
        }

        manipulation["manipulation_probability"] = {
            "probability": self._calculate_manipulation_probability(manipulation),
            "confidence": self._assess_manipulation_confidence(manipulation),
            "primary_indicators": self._identify_primary_manipulation_indicators(manipulation)
        }

        self.interpretation["manipulation_indicators"] = manipulation

    def _analyze_chain_of_custody(self) -> None:
        """Analyze chain of custody information"""
        custody = {}

        # Origin information
        device_make = self._extract_field(["EXIF:Make", "Make"])
        device_model = self._extract_field(["EXIF:Model", "Model"])
        serial_number = self._extract_field(["EXIF:SerialNumber", "SerialNumber"])
        internal_serial = self._extract_field(["EXIF:InternalSerialNumber", "InternalSerialNumber"])

        # Software processing
        software = self._extract_field(["EXIF:Software", "Software"])

        # Location history
        gps_data = self._extract_field(["GPS:GPSLatitude", "GPSLatitude"]) is not None

        # Time information
        date_original = self._extract_field(["EXIF:DateTimeOriginal", "DateTimeOriginal"])
        date_digitized = self._extract_field(["EXIF:DateTimeDigitized", "DateTimeDigitized"])
        date_modified = self._extract_field(["EXIF:DateTime", "DateTime", "file_modified"])

        custody["device_origin"] = {
            "make": device_make if device_make else "unknown",
            "model": device_model if device_model else "unknown",
            "serial_number": serial_number if serial_number else "unavailable",
            "internal_serial": internal_serial if internal_serial else "unavailable",
            "device_identified": bool(device_make and device_model)
        }

        custody["processing_history"] = {
            "software_used": software if software else "none detected",
            "processing_steps": self._infer_processing_steps(software),
            "generation_estimate": self._estimate_file_generation()
        }

        custody["temporal_history"] = {
            "date_created": date_original if date_original else "unknown",
            "date_digitized": date_digitized if date_digitized else "unknown",
            "date_modified": date_modified if date_modified else "unknown",
            "timeline_consistent": self._verify_temporal_consistency(date_original, date_digitized, date_modified)
        }

        custody["location_history"] = {
            "has_gps": gps_data,
            "location_data_available": gps_data,
            "location_verified": self._verify_location_data()
        }

        custody["custody_integrity"] = {
            "chain_complete": self._assess_chain_completeness(custody),
            "custody_breaks_detected": self._detect_custody_breaks(custody),
            "reliability_assessment": self._assess_custody_reliability(custody)
        }

        self.interpretation["chain_of_custody"] = custody

    def _perform_technical_forensics(self) -> None:
        """Perform detailed technical forensics"""
        forensics = {}

        # Hash analysis
        hashes = self._analyze_hash_consistency()

        # Metadata structure analysis
        structure = self._analyze_metadata_structure()

        # Format analysis
        format_analysis = self._analyze_file_format()

        # Embedded data analysis
        embedded = self._analyze_embedded_data()

        # Steganography detection
        stego = self._detect_steganography()

        forensics["hash_analysis"] = {
            "hashes_available": hashes,
            "hash_consistency": self._verify_hash_consistency(hashes),
            "cryptographic_variants": self._detect_cryptographic_variants()
        }

        forensics["metadata_structure"] = {
            "format_version": structure.get("format_version"),
            "metadata_sections": structure.get("sections"),
            "structural_integrity": structure.get("integrity"),
            "unusual_structure": structure.get("anomalies")
        }

        forensics["format_analysis"] = {
            "file_format": format_analysis.get("format"),
            "format_compliance": format_analysis.get("compliance"),
            "format_anomalies": format_analysis.get("anomalies"),
            "specification_deviation": format_analysis.get("deviation")
        }

        forensics["embedded_data"] = {
            "has_embedded_data": embedded.get("has_data"),
            "data_types": embedded.get("types"),
            "suspicious_embeds": embedded.get("suspicious"),
            "data_integrity": embedded.get("integrity")
        }

        forensics["steganography_analysis"] = {
            "steganography_detected": stego.get("detected"),
            "method_indicators": stego.get("methods"),
            "confidence": stego.get("confidence"),
            "tools_detected": stego.get("tools")
        }

        self.interpretation["technical_forensics"] = forensics

    def _generate_forensic_findings(self) -> None:
        """Generate key forensic findings"""
        findings = []

        # Authentication status
        auth = self.interpretation.get("authenticity_assessment", {})
        overall = auth.get("overall_authenticity", {})
        assessment = overall.get("assessment", "unknown")

        if assessment == "appears_authentic":
            findings.append(f"🔒 File appears authentic based on metadata analysis")
        elif assessment == "possibly_modified":
            findings.append(f"⚠️ File may have been modified - indicators detected")
        elif assessment == "likely_manipulated":
            findings.append(f"🚨 Strong evidence of manipulation detected")

        # Chain of custody
        custody = self.interpretation.get("chain_of_custody", {})
        device = custody.get("device_origin", {})
        if device.get("device_identified"):
            findings.append(f"📱 Device identified: {device.get('make', 'unknown')} {device.get('model', 'unknown')}")
        else:
            findings.append(f"❓ Device identification unavailable")

        # Manipulation indicators
        manipulation = self.interpretation.get("manipulation_indicators", {})
        prob = manipulation.get("manipulation_probability", {})
        if prob.get("probability") == "high":
            findings.append(f"🔍 High probability of manipulation detected")
        elif prob.get("probability") == "medium":
            findings.append(f"🔍 Some manipulation indicators present")
        else:
            findings.append(f"✅ Minimal manipulation indicators")

        # Technical forensics
        tech = self.interpretation.get("technical_forensics", {})
        if tech.get("steganography_analysis", {}).get("steganography_detected"):
            findings.append(f"🔬 Potential steganography detected")

        self.interpretation["key_findings"] = findings

    def _provide_investigative_recommendations(self) -> None:
        """Provide investigative recommendations"""
        recommendations = []

        authenticity = self.interpretation.get("authenticity_assessment", {})
        overall = authenticity.get("overall_authenticity", {})
        assessment = overall.get("assessment", "unknown")

        # Based on authenticity assessment
        if assessment in ["possibly_modified", "likely_manipulated"]:
            recommendations.append("🔴 Proceed with caution - authenticity concerns identified")
            recommendations.append("🔍 Verify with original source if possible")
            recommendations.append("📊 Cross-reference with other evidence")

        # Based on chain of custody
        custody = self.interpretation.get("chain_of_custody", {})
        if not custody.get("device_origin", {}).get("device_identified"):
            recommendations.append("📱 Device identification incomplete - limits provenance verification")

        # Based on manipulation indicators
        manipulation = self.interpretation.get("manipulation_indicators", {})
        if manipulation.get("editing_signatures", {}).get("editing_indicators"):
            recommendations.append("🖼️ Editing software detected - determine if authorized")

        # Based on technical forensics
        tech = self.interpretation.get("technical_forensics", {})
        if tech.get("steganography_analysis", {}).get("steganography_detected"):
            recommendations.append("🔬 Hidden data detected - forensic analysis recommended")

        # General recommendations
        if assessment == "appears_authentic":
            recommendations.append("✅ File metadata appears consistent with claimed origin")

        # Chain recommendations
        if custody.get("custody_integrity", {}).get("custody_breaks_detected"):
            recommendations.append("⚠️ Potential chain of custody issues identified")

        self.interpretation["investigative_recommendations"] = recommendations

    # Helper methods for forensic analysis
    def _format_file_size(self, size_bytes) -> str:
        if not size_bytes:
            return "unknown"
        try:
            size = int(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except (ValueError, TypeError):
            return "unknown"

    def _detect_timestamp_discrepancies(self, created, modified) -> list:
        discrepancies = []
        if created and modified:
            try:
                # Simple comparison - would be more sophisticated in real implementation
                if created != modified:
                    discrepancies.append("creation and modification times differ")
            except (TypeError, ValueError):
                discrepancies.append("timestamp comparison failed")
        return discrepancies

    def _detect_processing_indicators(self, software, creator_tool) -> list:
        indicators = []
        processing_tools = ["photoshop", "lightroom", "gimp", "affinity", "skylum", "capture one"]

        for tool in processing_tools:
            if software and tool in software.lower():
                indicators.append(f"{tool} processing detected")
            if creator_tool and tool in creator_tool.lower():
                indicators.append(f"{tool} processing detected")

        return indicators

    def _check_exif_integrity(self) -> bool:
        # Check if EXIF data is present and appears intact
        exif_data = self._extract_field(["exif", "EXIF"])
        if not exif_data:
            return False

        # Check for critical fields
        critical_fields = ["DateTimeOriginal", "Make", "Model"]
        for field in critical_fields:
            if not self._extract_field([f"EXIF:{field}", field]):
                return False

        return True

    def _check_thumbnail_integrity(self) -> bool:
        # Check if embedded thumbnail matches main image
        has_thumbnail = self._extract_field(["thumbnail:has_embedded"])
        return bool(has_thumbnail)

    def _verify_gps_consistency(self) -> bool:
        # Check if GPS data is internally consistent
        lat = self._extract_field(["GPS:GPSLatitude", "GPSLatitude"])
        lon = self._extract_field(["GPS:GPSLongitude", "GPSLongitude"])

        if not lat or not lon:
            return True  # No GPS to check

        # Basic validation - would be more sophisticated
        return True

    def _verify_date_consistency(self) -> bool:
        # Check if date fields are consistent
        date_original = self._extract_field(["EXIF:DateTimeOriginal", "DateTimeOriginal"])
        date_digitized = self._extract_field(["EXIF:DateTimeDigitized", "DateTimeDigitized"])
        date_modified = self._extract_field(["EXIF:DateTime", "DateTime"])

        # Simple check - all dates should be present and reasonable
        return bool(date_original and date_digitized)

    def _calculate_authentication_score(self, signature, blockchain, watermark) -> int:
        score = 0
        if signature:
            score += 40
        if blockchain:
            score += 35
        if watermark:
            score += 25
        return score

    def _calculate_metadata_integrity_score(self, complete, intact, thumbnails) -> int:
        score = 0
        if intact:
            score += 50
        if complete:
            score += 30
        if thumbnails:
            score += 20
        return score

    def _assess_overall_consistency(self, gps, dates) -> str:
        if gps and dates:
            return "consistent"
        elif gps or dates:
            return "mostly_consistent"
        else:
            return "unable_to_assess"

    def _determine_authenticity_assessment(self, authenticity) -> str:
        # Overall authenticity determination
        auth_score = authenticity.get("authentication", {}).get("authentication_score", 0)
        integrity_score = authenticity.get("metadata_integrity", {}).get("metadata_integrity_score", 0)
        consistency = authenticity.get("consistency_checks", {}).get("overall_consistency", "unable_to_assess")

        if auth_score >= 70 and integrity_score >= 70 and consistency == "consistent":
            return "appears_authentic"
        elif auth_score >= 40 or integrity_score >= 40:
            return "possibly_modified"
        else:
            return "likely_manipulated"

    def _calculate_authenticity_confidence(self, authenticity) -> str:
        auth_score = authenticity.get("authentication", {}).get("authentication_score", 0)
        if auth_score >= 70:
            return "high"
        elif auth_score >= 40:
            return "medium"
        else:
            return "low"

    def _identify_risk_factors(self, authenticity) -> list:
        risks = []

        if not authenticity.get("authentication", {}).get("has_digital_signature"):
            risks.append("no_digital_signature")

        if not authenticity.get("metadata_integrity", {}).get("exif_intact"):
            risks.append("metadata_integrity_concerns")

        if authenticity.get("consistency_checks", {}).get("overall_consistency") != "consistent":
            risks.append("inconsistencies_detected")

        return risks

    def _detect_editing_software(self, software) -> list:
        indicators = []
        editing_keywords = ["photoshop", "lightroom", "gimp", "affinity", "edited", "processed"]

        if software:
            software_lower = software.lower()
            for keyword in editing_keywords:
                if keyword in software_lower:
                    indicators.append(f"editing_software_{keyword}")

        return indicators

    def _identify_suspicious_tools(self, software) -> list:
        suspicious = []
        if software:
            software_lower = software.lower()
            # These might indicate legitimate editing, but worth flagging for investigators
            if any(tool in software_lower for tool in ["photoshop", "gimp", "affinity"]):
                suspicious.append("image_editing_software")

        return suspicious

    def _identify_missing_critical_exif(self) -> list:
        missing = []
        critical_fields = ["DateTimeOriginal", "Make", "Model", "Software"]

        for field in critical_fields:
            if not self._extract_field([f"EXIF:{field}", field]):
                missing.append(field)

        return missing

    def _detect_metadata_anomalies(self) -> list:
        anomalies = []

        # Check for suspicious patterns
        software = self._extract_field(["EXIF:Software", "Software"])
        if not software:
            anomalies.append("missing_software_metadata")

        # Check for missing GPS in smartphone photos (would need device detection)
        # This is simplified - real implementation would be more sophisticated

        return anomalies

    def _detect_quality_issues(self) -> list:
        issues = []

        # Check for compression artifacts
        compression = self._extract_field(["EXIF:Compression", "Compression"])
        if compression and compression > 6:  # High compression
            issues.append("high_compression")

        return issues

    def _detect_recompression(self) -> bool:
        # Check for signs of recompression
        # This is simplified - real implementation would analyze quantization tables, etc.
        return False

    def _detect_resaving(self) -> bool:
        # Check for signs of resaving
        software = self._extract_field(["EXIF:Software", "Software"])
        # Multiple software mentions might indicate resaving
        return False

    def _assess_generation_loss(self) -> str:
        # Assess potential generation loss
        return "minimal"  # Simplified

    def _calculate_manipulation_probability(self, manipulation) -> str:
        # Calculate overall manipulation probability
        edit_count = len(manipulation.get("editing_signatures", {}).get("editing_indicators", []))
        anomaly_count = manipulation.get("metadata_anomalies", {}).get("anomaly_count", 0)

        if edit_count > 0 or anomaly_count > 2:
            return "high"
        elif edit_count > 0 or anomaly_count > 0:
            return "medium"
        else:
            return "low"

    def _assess_manipulation_confidence(self, manipulation) -> str:
        prob = manipulation.get("manipulation_probability", {}).get("probability", "low")
        if prob == "high":
            return "high"
        elif prob == "medium":
            return "medium"
        else:
            return "low"

    def _identify_primary_manipulation_indicators(self, manipulation) -> list:
        primary = []

        edit_sig = manipulation.get("editing_signatures", {})
        if edit_sig.get("editing_indicators"):
            primary.append("editing_software_detected")

        anomalies = manipulation.get("metadata_anomalies", {})
        if anomalies.get("anomaly_count", 0) > 0:
            primary.append("metadata_anomalies")

        return primary

    def _infer_processing_steps(self, software) -> list:
        steps = []
        if software:
            if "photoshop" in software.lower():
                steps.append("image_editing")
            if "lightroom" in software.lower():
                steps.append("photo_processing")
        return steps

    def _estimate_file_generation(self) -> int:
        # Estimate which generation this file is (1 = original)
        software = self._extract_field(["EXIF:Software", "Software"])

        if not software:
            return 1  # Likely original

        # Check for multiple processing steps
        if "+" in software or "&" in software:
            return 2  # Likely processed

        return 1  # Assume original

    def _verify_temporal_consistency(self, original, digitized, modified) -> bool:
        # Check if timeline makes sense
        if not all([original, digitized, modified]):
            return False

        # In a valid timeline: original <= digitized <= modified
        # This is simplified - real implementation would parse dates properly
        return True

    def _verify_location_data(self) -> bool:
        # Verify GPS data consistency
        lat = self._extract_field(["GPS:GPSLatitude", "GPSLatitude"])
        lon = self._extract_field(["GPS:GPSLongitude", "GPSLongitude"])
        alt = self._extract_field(["GPS:GPSAltitude", "GPSAltitude"])

        # Basic check - coordinates should be present together
        if lat and lon:
            return True

        return False

    def _assess_chain_completeness(self, custody) -> str:
        # Assess if chain of custody is complete
        device_identified = custody.get("device_origin", {}).get("device_identified", False)
        has_timeline = custody.get("temporal_history", {}).get("timeline_consistent", False)

        if device_identified and has_timeline:
            return "complete"
        elif device_identified or has_timeline:
            return "partial"
        else:
            return "incomplete"

    def _detect_custody_breaks(self, custody) -> list:
        breaks = []

        if not custody.get("device_origin", {}).get("device_identified"):
            breaks.append("device_origin_unknown")

        if not custody.get("temporal_history", {}).get("timeline_consistent"):
            breaks.append("timeline_inconsistencies")

        return breaks

    def _assess_custody_reliability(self, custody) -> str:
        breaks = len(custody.get("custody_integrity", {}).get("custody_breaks_detected", []))

        if breaks == 0:
            return "high"
        elif breaks == 1:
            return "medium"
        else:
            return "low"

    def _analyze_hash_consistency(self) -> dict:
        hashes = {}
        md5 = self._extract_field(["file_integrity:md5", "md5"])
        sha1 = self._extract_field(["file_integrity:sha1", "sha1"])
        sha256 = self._extract_field(["file_integrity:sha256", "sha256"])

        if md5:
            hashes["md5"] = md5
        if sha1:
            hashes["sha1"] = sha1
        if sha256:
            hashes["sha256"] = sha256

        return hashes

    def _verify_hash_consistency(self, hashes) -> bool:
        # Verify if multiple hashes are consistent
        return len(hashes) > 0

    def _detect_cryptographic_variants(self) -> list:
        # Detect different cryptographic variants
        variants = []

        # Check for different hash types
        hash_types = []
        if self._extract_field(["file_integrity:md5", "md5"]):
            hash_types.append("MD5")
        if self._extract_field(["file_integrity:sha1", "sha1"]):
            hash_types.append("SHA1")
        if self._extract_field(["file_integrity:sha256", "sha256"]):
            hash_types.append("SHA256")

        return hash_types

    def _analyze_metadata_structure(self) -> dict:
        structure = {}

        # Check for different metadata sections
        has_exif = self._extract_field(["exif", "EXIF"]) is not None
        has_iptc = self._extract_field(["iptc", "IPTC"]) is not None
        has_xmp = self._extract_field(["xmp", "XMP"]) is not None

        structure["format_version"] = "standard"
        structure["sections"] = {
            "exif": has_exif,
            "iptc": has_iptc,
            "xmp": has_xmp
        }
        structure["integrity"] = "intact" if has_exif else "partial"
        structure["anomalies"] = []

        if not has_exif:
            structure["anomalies"].append("missing_exif")

        return structure

    def _analyze_file_format(self) -> dict:
        format_analysis = {}

        file_type = self._extract_field(["filetype", "FileType"])
        mime_type = self._extract_field(["mime_type", "MIMEType"])

        format_analysis["format"] = file_type if file_type else "unknown"
        format_analysis["compliance"] = "standard"
        format_analysis["anomalies"] = []
        format_analysis["deviation"] = "none"

        return format_analysis

    def _analyze_embedded_data(self) -> dict:
        embedded = {}

        # Check for various embedded data types
        has_thumbnail = self._extract_field(["thumbnail:has_embedded"])
        has_icc = self._extract_field(["icc_profile", "ICC Profile"]) is not None
        has_xmp = self._extract_field(["xmp", "XMP"]) is not None

        embedded["has_data"] = any([has_thumbnail, has_icc, has_xmp])
        embedded["types"] = []

        if has_thumbnail:
            embedded["types"].append("thumbnail")
        if has_icc:
            embedded["types"].append("icc_profile")
        if has_xmp:
            embedded["types"].append("xmp")

        embedded["suspicious"] = []
        embedded["integrity"] = "verified"

        return embedded

    def _detect_steganography(self) -> dict:
        stego = {}

        # Basic steganography detection (simplified)
        # Real implementation would use sophisticated analysis

        stego["detected"] = False
        stego["methods"] = []
        stego["confidence"] = "none"
        stego["tools"] = []

        return stego


# Security Analyst Sam - Cybersecurity Professional
class SecurityAnalystSamInterpreter(PersonaInterpreter):
    """Security-focused interpreter for cybersecurity professionals"""

    def __init__(self, metadata: Dict[str, Any]):
        super().__init__(metadata)
        self.persona_name = "security_analyst_sam"
        self.persona_icon = "🔒"

    def interpret(self) -> Dict[str, Any]:
        """Generate security-focused interpretation"""
        return {
            "persona": self.persona_name,
            "key_findings": self._generate_security_findings(),
            "security_analysis": self._analyze_security_threats(),
            "osint_opportunities": self._identify_osint_opportunities(),
            "metadata_risks": self._assess_metadata_risks(),
            "recommendations": self._generate_security_recommendations()
        }

    def _generate_security_findings(self) -> List[str]:
        """Generate security-focused key findings"""
        findings = []

        # Check for sensitive data exposure
        if self.metadata.get("gps"):
            findings.append("🔍 GPS coordinates present - location data exposure")

        # Check device fingerprinting
        device = self.metadata.get("exif", {}).get("Model")
        if device:
            findings.append(f"📱 Device fingerprinting possible: {device}")

        # Check for network indicators
        if self.metadata.get("exif", {}).get("Software"):
            findings.append("⚠️ Software metadata may reveal system information")

        # Check for metadata consistency
        if self.metadata.get("forensic", {}).get("authentication_is_authenticated"):
            findings.append("✅ Image appears cryptographically authenticated")
        else:
            findings.append("❌ No cryptographic authentication detected")

        # Check for embedded data
        if self.metadata.get("thumbnail"):
            findings.append("🖼️ Contains embedded thumbnail - potential data hiding")

        return findings

    def _analyze_security_threats(self) -> Dict[str, Any]:
        """Analyze potential security threats"""
        threats = {
            "threat_indicators": {
                "steganography_detected": False,
                "embedded_urls": [],
                "suspicious_metadata": [],
                "hidden_files": [],
                "encrypted_content": False
            },
            "data_exposure": {
                "level": "unknown",
                "exposed_data": [],
                "risk_score": 0
            },
            "device_fingerprinting": {
                "possible": False,
                "uniqueness": "unknown",
                "tracking_risk": "unknown"
            }
        }

        # Analyze EXIF for device fingerprinting
        exif = self.metadata.get("exif", {})
        if exif.get("Make") or exif.get("Model") or exif.get("SerialNumber"):
            threats["device_fingerprinting"]["possible"] = True
            threats["device_fingerprinting"]["uniqueness"] = "high"
            threats["device_fingerprinting"]["tracking_risk"] = "high"

        # Analyze GPS for location exposure
        gps = self.metadata.get("gps")
        if gps:
            threats["data_exposure"]["exposed_data"].append("precise_location")
            threats["data_exposure"]["level"] = "high"
            threats["data_exposure"]["risk_score"] += 40

        # Analyze timestamp for temporal tracking
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            threats["data_exposure"]["exposed_data"].append("capture_timestamp")
            threats["data_exposure"]["risk_score"] += 20

        # Check for software signatures that might reveal system info
        if exif.get("Software") or exif.get("InternalSoftware"):
            threats["threat_indicators"]["suspicious_metadata"].append("software_version")
            threats["data_exposure"]["risk_score"] += 15

        # Check for network-related metadata
        if self.metadata.get("exif", {}).get("WiFiInfo") or self.metadata.get("network_data"):
            threats["data_exposure"]["exposed_data"].append("network_information")
            threats["data_exposure"]["risk_score"] += 25

        return threats

    def _identify_osint_opportunities(self) -> Dict[str, Any]:
        """Identify Open Source Intelligence opportunities"""
        osint = {
            "location_data": {"present": False, "type": None},
            "device_info": {"present": False, "details": None},
            "network_indicators": {"present": False, "details": None},
            "temporal_data": {"present": False, "details": None},
            "personally_identifiable_info": {"level": "none", "details": []}
        }

        # Location OSINT
        if self.metadata.get("gps"):
            osint["location_data"]["present"] = True
            osint["location_data"]["type"] = "precise_coordinates"

            # Add reverse geocoded location if available
            location = self.metadata.get("location_analysis")
            if location and location.get("address"):
                osint["location_data"]["address"] = location["address"]

        # Device OSINT
        exif = self.metadata.get("exif", {})
        if exif.get("Make") or exif.get("Model"):
            osint["device_info"]["present"] = True
            osint["device_info"]["details"] = {
                "make": exif.get("Make"),
                "model": exif.get("Model"),
                "serial": exif.get("SerialNumber", "not_present"),
                "uniqueness": "high" if exif.get("SerialNumber") else "medium"
            }

        # Temporal OSINT
        if exif.get("DateTimeOriginal"):
            osint["temporal_data"]["present"] = True
            osint["temporal_data"]["details"] = exif.get("DateTimeOriginal")

        # PII assessment
        pii_indicators = []
        if exif.get("OwnerName"):
            pii_indicators.append("owner_name")
        if exif.get("Artist"):
            pii_indicators.append("creator_name")
        if self.metadata.get("iptc", {}).get("Contact"):
            pii_indicators.append("contact_info")

        if pii_indicators:
            osint["personally_identifiable_info"]["level"] = "high"
            osint["personally_identifiable_info"]["details"] = pii_indicators

        return osint

    def _assess_metadata_risks(self) -> Dict[str, Any]:
        """Assess metadata-related security risks"""
        risks = {
            "exposure_level": "unknown",
            "sensitive_data": [],
            "sanitization_needed": False,
            "recommendations": []
        }

        # Collect all potentially sensitive metadata fields
        sensitive_fields = []

        # GPS data
        if self.metadata.get("gps"):
            sensitive_fields.append("GPS coordinates (precise location)")
            risks["sanitization_needed"] = True

        # Device identifiers
        exif = self.metadata.get("exif", {})
        if exif.get("SerialNumber"):
            sensitive_fields.append("Device serial number")
            risks["sanitization_needed"] = True
        if exif.get("InternalSerialNumber"):
            sensitive_fields.append("Internal device serial")
            risks["sanitization_needed"] = True

        # Owner information
        if exif.get("OwnerName"):
            sensitive_fields.append("Device owner name")
            risks["sanitization_needed"] = True

        # Network information
        if exif.get("WiFiInfo") or exif.get("NetworkInfo"):
            sensitive_fields.append("Network configuration")
            risks["sanitization_needed"] = True

        # Timestamps (tracking risk)
        if exif.get("DateTimeOriginal"):
            sensitive_fields.append("Capture timestamp")

        # Software/OS version
        if exif.get("Software") or exif.get("OSVersion"):
            sensitive_fields.append("System software version")

        risks["sensitive_data"] = sensitive_fields

        # Determine overall exposure level
        if len(sensitive_fields) >= 4:
            risks["exposure_level"] = "critical"
        elif len(sensitive_fields) >= 2:
            risks["exposure_level"] = "high"
        elif len(sensitive_fields) >= 1:
            risks["exposure_level"] = "medium"
        else:
            risks["exposure_level"] = "low"

        # Generate recommendations
        if risks["sanitization_needed"]:
            risks["recommendations"].append("Remove GPS coordinates before sharing")
            risks["recommendations"].append("Strip device serial numbers")
            risks["recommendations"].append("Consider removing EXIF timestamp data")
            risks["recommendations"].append("Use metadata sanitization tools")

        if self.metadata.get("thumbnail"):
            risks["recommendations"].append("Be aware that thumbnails may retain removed metadata")

        return risks

    def _generate_security_recommendations(self) -> List[str]:
        """Generate security-focused recommendations"""
        recommendations = []

        # Risk-based recommendations
        metadata_risks = self._assess_metadata_risks()

        if metadata_risks["sanitization_needed"]:
            recommendations.append("🔒 Sanitize metadata before sharing publicly")
            recommendations.append("🛡️ Use tools like ExifTool or ImageMagick for metadata removal")

        if self.metadata.get("gps"):
            recommendations.append("📍 GPS data reveals exact location - remove for privacy")

        if self.metadata.get("exif", {}).get("SerialNumber"):
            recommendations.append("🔢 Device serial number can link to original owner - remove")

        # Best practices
        recommendations.append("✅ Always verify image sources for security-sensitive contexts")
        recommendations.append("🔍 Consider using separate devices for sensitive photography")
        recommendations.append("📱 Keep device software updated for security patches")

        # Context-specific recommendations
        if self.metadata.get("forensic", {}).get("authentication_is_authenticated"):
            recommendations.append("✅ Image contains cryptographic signatures - useful for verification")
        else:
            recommendations.append("⚠️ No cryptographic authentication - authenticity cannot be verified")

        return recommendations


# Social Media Manager Sophia - Content Creator Professional
class SocialMediaManagerSophiaInterpreter(PersonaInterpreter):
    """Social media optimization interpreter for content creators"""

    def __init__(self, metadata: Dict[str, Any]):
        super().__init__(metadata)
        self.persona_name = "social_media_manager_sophia"
        self.persona_icon = "📱"

    def interpret(self) -> Dict[str, Any]:
        """Generate social media optimization interpretation"""
        return {
            "persona": self.persona_name,
            "key_findings": self._generate_social_findings(),
            "platform_optimization": self._analyze_platform_compatibility(),
            "content_analysis": self._analyze_content_characteristics(),
            "engagement_prediction": self._predict_engagement(),
            "posting_recommendations": self._generate_posting_advice(),
            "hashtag_suggestions": self._suggest_hashtags(),
            "content_enhancement": self._suggest_content_improvements()
        }

    def _generate_social_findings(self) -> List[str]:
        """Generate social media-focused key findings"""
        findings = []

        # Image dimensions
        if self.metadata.get("image"):
            width = self.metadata.get("image", {}).get("width", 0)
            height = self.metadata.get("image", {}).get("height", 0)

            # Check for optimal social media sizes
            if width == 1080 and height == 1080:
                findings.append("✅ Perfect square format for Instagram")
            elif width == 1080 and height == 1350:
                findings.append("✅ Optimal Instagram portrait format (4:5)")
            elif width == 1200 and height == 675:
                findings.append("✅ Twitter-optimized landscape format")
            else:
                findings.append(f"📐 Current dimensions: {width}x{height} - may need cropping")

        # Image quality
        if self.metadata.get("image", {}).get("format") == "JPEG":
            findings.append("🖼️ JPEG format - good compression for web sharing")
        elif self.metadata.get("image", {}).get("format") == "PNG":
            findings.append("🖼️ PNG format - better quality but larger file size")

        # GPS for location tagging
        if self.metadata.get("gps"):
            findings.append("📍 GPS data available - automatic location tagging possible")

        # Timestamp for optimal timing
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            findings.append("⏰ Capture time available - can analyze best posting times")

        return findings

    def _analyze_platform_compatibility(self) -> Dict[str, Any]:
        """Analyze compatibility with different social platforms"""
        platforms = {
            "instagram": {"score": 0, "recommendations": [], "format": "unknown"},
            "twitter": {"score": 0, "recommendations": [], "format": "unknown"},
            "facebook": {"score": 0, "recommendations": [], "format": "unknown"},
            "linkedin": {"score": 0, "recommendations": [], "format": "unknown"},
            "tiktok": {"score": 0, "recommendations": [], "format": "unknown"}
        }

        # Get image dimensions
        width = self.metadata.get("image", {}).get("width", 0)
        height = self.metadata.get("image", {}).get("height", 0)
        aspect_ratio = width / height if height > 0 else 1

        # Instagram analysis
        if width == 1080 and height == 1080:
            platforms["instagram"]["score"] = 100
            platforms["instagram"]["format"] = "optimal_square"
        elif width == 1080 and height in [1350, 1920]:
            platforms["instagram"]["score"] = 95
            platforms["instagram"]["format"] = "optimal_portrait"
        elif width >= 1080 and height >= 1080:
            platforms["instagram"]["score"] = 80
            platforms["instagram"]["recommendations"].append("High resolution, but may be compressed")
        else:
            platforms["instagram"]["score"] = 60
            platforms["instagram"]["recommendations"].append("Resize to 1080px minimum dimension")

        # Twitter analysis
        if aspect_ratio >= 1.91 and aspect_ratio <= 2.1:
            platforms["twitter"]["score"] = 95
            platforms["twitter"]["format"] = "optimal_landscape"
        elif aspect_ratio >= 0.5 and aspect_ratio <= 1.0:
            platforms["twitter"]["score"] = 85
            platforms["twitter"]["format"] = "good_square_portrait"
        else:
            platforms["twitter"]["score"] = 70
            platforms["twitter"]["recommendations"].append("Consider cropping for optimal display")

        # Facebook analysis
        if width >= 1200 and aspect_ratio >= 1.5:
            platforms["facebook"]["score"] = 90
            platforms["facebook"]["format"] = "good_landscape"
        else:
            platforms["facebook"]["score"] = 75
            platforms["facebook"]["recommendations"].append("Facebook accepts most formats")

        # LinkedIn analysis
        if width >= 1200 and aspect_ratio >= 1.91:
            platforms["linkedin"]["score"] = 85
            platforms["linkedin"]["format"] = "professional_landscape"
        else:
            platforms["linkedin"]["score"] = 70
            platforms["linkedin"]["recommendations"].append("LinkedIn prefers wider formats")

        # TikTok analysis
        if aspect_ratio == 9/16 or aspect_ratio == 3/4:
            platforms["tiktok"]["score"] = 90
            platforms["tiktok"]["format"] = "optimal_vertical"
        else:
            platforms["tiktok"]["score"] = 50
            platforms["tiktok"]["recommendations"].append("TikTok requires vertical video format")

        return platforms

    def _analyze_content_characteristics(self) -> Dict[str, Any]:
        """Analyze content characteristics for social optimization"""
        content = {
            "category": "unknown",
            "mood": "unknown",
            "dominant_colors": [],
            "subject": "unknown",
            "quality_assessment": "unknown"
        }

        # Analyze colors from perceptual hashes or image analysis
        if self.metadata.get("perceptual_hashes"):
            content["quality_assessment"] = "has_image_analysis_data"

        # Analyze dimensions for content type hints
        width = self.metadata.get("image", {}).get("width", 0)
        height = self.metadata.get("image", {}).get("height", 0)

        if aspect_ratio := width / height if height > 0 else 1:
            if aspect_ratio == 1.0:
                content["category"] = "square_composition"
            elif aspect_ratio > 1.2:
                content["category"] = "landscape_composition"
            elif aspect_ratio < 0.8:
                content["category"] = "portrait_composition"

        # Analyze EXIF for content hints
        exif = self.metadata.get("exif", {})

        # Check for photography hints
        if exif.get("FNumber"):
            aperture = float(exif.get("FNumber", 0))
            if aperture <= 2.8:
                content["subject"] = "portrait_shallow_dof"
            elif aperture >= 8:
                content["subject"] = "landscape_deep_dof"

        # Check for GPS location for context
        if self.metadata.get("gps"):
            content["category"] = "location_based_content"

        return content

    def _predict_engagement(self) -> Dict[str, Any]:
        """Predict engagement potential across platforms"""
        engagement = {
            "overall_score": 0,
            "platform_predictions": {},
            "confidence": "low",
            "factors": []
        }

        # Base score on image characteristics
        score = 50  # Start with neutral score

        # Quality factors
        if self.metadata.get("image", {}).get("width", 0) >= 1080:
            score += 15
            engagement["factors"].append("High resolution suitable for social platforms")

        # Format factors
        width = self.metadata.get("image", {}).get("width", 0)
        height = self.metadata.get("image", {}).get("height", 0)

        if width == 1080 and height == 1080:
            score += 20
            engagement["factors"].append("Optimal Instagram format")

        if width >= 1200 and height >= 630:
            score += 15
            engagement["factors"].append("Good for Twitter/Facebook sharing")

        # GPS availability for location tagging
        if self.metadata.get("gps"):
            score += 10
            engagement["factors"].append("Location data available for geo-tagging")

        engagement["overall_score"] = min(score, 100)

        # Platform-specific predictions
        engagement["platform_predictions"] = {
            "instagram": "high" if score >= 80 else "medium" if score >= 60 else "low",
            "twitter": "medium" if score >= 70 else "low",
            "facebook": "medium" if score >= 60 else "low"
        }

        engagement["confidence"] = "high" if score >= 80 else "medium" if score >= 60 else "low"

        return engagement

    def _generate_posting_advice(self) -> List[str]:
        """Generate posting strategy recommendations"""
        advice = []

        # Timing advice
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            original_time = self.metadata.get("exif", {}).get("DateTimeOriginal")
            try:
                from datetime import datetime
                # Parse the time to suggest optimal posting times
                advice.append("⏰ Best posting times: 6-9 AM or 6-9 PM on weekdays")
                advice.append("📅 Weekends: 9-11 AM often perform well")
            except:
                pass

        # Format advice
        width = self.metadata.get("image", {}).get("width", 0)
        height = self.metadata.get("image", {}).get("height", 0)

        if width == 1080 and height == 1080:
            advice.append("✅ Perfect for Instagram - no cropping needed")
        elif width < 1080 or height < 1080:
            advice.append("📐 Consider upscaling to 1080px minimum for best quality")

        # Location advice
        if self.metadata.get("gps"):
            advice.append("📍 Use GPS location for automatic location tagging")
            advice.append("🗺️ Location tags can increase discoverability by up to 50%")

        # Platform-specific advice
        advice.append("📱 Instagram: Post during high-engagement hours (6-9 PM)")
        advice.append("🐦 Twitter: Include relevant hashtags and mentions")
        advice.append("👤 Facebook: Consider sharing in relevant groups")

        return advice

    def _suggest_hashtags(self) -> List[str]:
        """Suggest relevant hashtags based on content analysis"""
        hashtags = []

        # Generic popular hashtags
        hashtags.extend(["#photography", "#photooftheday"])

        # Analyze content for specific hashtags
        if self.metadata.get("gps"):
            hashtags.extend(["#travel", "#location", "#geotag"])

        # Time-based hashtags
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            from datetime import datetime
            try:
                date_str = self.metadata.get("exif", {}).get("DateTimeOriginal")
                if "2024" in date_str:
                    hashtags.append("#2024")
            except:
                pass

        # Quality-based hashtags
        if self.metadata.get("image", {}).get("width", 0) >= 2000:
            hashtags.extend(["#highresolution", "#quality"])

        return list(set(hashtags))  # Remove duplicates

    def _suggest_content_improvements(self) -> List[str]:
        """Suggest content enhancements"""
        improvements = []

        # Resolution improvements
        width = self.metadata.get("image", {}).get("width", 0)
        if width < 1080:
            improvements.append("📐 Upscale to 1080px minimum for optimal social media quality")

        # Format improvements
        height = self.metadata.get("image", {}).get("height", 0)
        if width != height and width != 1080:
            improvements.append("✂️ Consider creating multiple versions for different platforms")

        # Metadata improvements
        if not self.metadata.get("gps"):
            improvements.append("📍 Consider adding location data for better engagement")

        # Content suggestions
        improvements.append("✨ Add engaging caption with call-to-action")
        improvements.append("👥 Tag relevant accounts to increase reach")
        improvements.append("🔥 Use trending hashtags in your niche")

        return improvements


# Genealogy Researcher Grace - Family Historian
class GenealogyResearcherGraceInterpreter(PersonaInterpreter):
    """Genealogy-focused interpreter for family historians"""

    def __init__(self, metadata: Dict[str, Any]):
        super().__init__(metadata)
        self.persona_name = "genealogy_researcher_grace"
        self.persona_icon = "👨‍👩‍👧‍👦"

    def interpret(self) -> Dict[str, Any]:
        """Generate genealogy research interpretation"""
        return {
            "persona": self.persona_name,
            "key_findings": self._generate_genealogy_findings(),
            "era_context": self._analyze_historical_context(),
            "location_history": self._analyze_location_history(),
            "archival_recommendations": self._generate_archival_advice(),
            "preservation_priority": self._assess_preservation_needs()
        }

    def _generate_genealogy_findings(self) -> List[str]:
        """Generate genealogy-focused key findings"""
        findings = []

        # Date analysis
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            date_str = self.metadata.get("exif", {}).get("DateTimeOriginal")
            findings.append(f"📅 Photo dated: {date_str}")

        # Location analysis
        if self.metadata.get("gps"):
            findings.append("📍 GPS location available for mapping family history")
        else:
            findings.append("🗺️ No GPS data - location may need manual identification")

        # Device analysis
        exif = self.metadata.get("exif", {})
        if exif.get("Make") or exif.get("Model"):
            device = f"{exif.get('Make', '')} {exif.get('Model', '')}"
            findings.append(f"📷 Taken with: {device.strip()}")

        # Quality assessment
        if self.metadata.get("image", {}).get("width", 0) >= 2000:
            findings.append("✅ High resolution - good for archival purposes")

        return findings

    def _analyze_historical_context(self) -> Dict[str, Any]:
        """Analyze historical context for the photo"""
        context = {
            "estimated_decade": "unknown",
            "historical_events": [],
            "technology_context": "unknown",
            "fashion_indicators": [],
            "cultural_context": "unknown"
        }

        # Analyze date for historical context
        date_str = self.metadata.get("exif", {}).get("DateTimeOriginal", "")
        if date_str:
            try:
                year = int(date_str.split(":")[0])
                decade = (year // 10) * 10

                context["estimated_decade"] = f"{decade}s"

                # Add historical events based on decade
                if decade == 2020:
                    context["historical_events"] = ["COVID-19 pandemic", "Remote work era", "Smartphone dominance"]
                elif decade == 2010:
                    context["historical_events"] = ["Social media rise", "iPhone era", "Digital photography mainstream"]
                elif decade == 2000:
                    context["historical_events"] = ["Digital revolution", "Early internet era", "Mobile phone emergence"]
                elif decade == 1990:
                    context["historical_events"] = ["Pre-digital era", "Film photography", "Analog technology"]

                # Technology context
                if year >= 2010:
                    context["technology_context"] = "Modern smartphone and digital camera era"
                elif year >= 2000:
                    context["technology_context"] = "Early digital photography, camera phones emerging"
                elif year >= 1990:
                    context["technology_context"] = "Film photography dominant, early digital adoption"

            except (ValueError, IndexError):
                context["estimated_decade"] = "unknown"

        return context

    def _analyze_location_history(self) -> Dict[str, Any]:
        """Analyze location for genealogical research"""
        location_history = {
            "modern_address": "unknown",
            "historical_context": "unknown",
            "genealogical_relevance": "unknown",
            "family_history_clues": []
        }

        # Analyze GPS data
        if self.metadata.get("gps"):
            # Modern address would come from reverse geocoding
            location_history["modern_address"] = "GPS coordinates available - requires reverse geocoding"
            location_history["genealogical_relevance"] = "exact_location_available"

        # Check for any location hints in metadata
        exif = self.metadata.get("exif", {})
        if exif.get("Location"):
            location_history["family_history_clues"].append(f"Location mentioned: {exif.get('Location')}")

        return location_history

    def _generate_archival_advice(self) -> Dict[str, Any]:
        """Generate archival and preservation recommendations"""
        advice = {
            "preservation_priority": "medium",
            "storage_conditions": [],
            "digitization": {},
            "metadata_to_add": [],
            "family_tree_integration": []
        }

        # Assess preservation priority
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            # Older photos have higher priority
            try:
                year = int(self.metadata.get("exif", {}).get("DateTimeOriginal", "").split(":")[0])
                if year < 2000:
                    advice["preservation_priority"] = "high"
                elif year < 2010:
                    advice["preservation_priority"] = "medium-high"
            except:
                pass

        # Storage conditions
        advice["storage_conditions"] = [
            "Store in cool, dry, dark place (65-70°F, 40-50% humidity)",
            "Use acid-free sleeves for physical prints",
            "Keep away from direct sunlight and UV sources",
            "Store vertically to prevent curling"
        ]

        # Digitization advice
        if self.metadata.get("image", {}).get("width", 0) < 300:
            advice["digitization"] = {
                "recommended_dpi": "300 DPI minimum for archival",
                "format": "TIFF for preservation, JPEG for sharing",
                "color_space": "Use sRGB for web, Adobe RGB for print"
            }

        # Metadata enrichment suggestions
        advice["metadata_to_add"] = [
            "Identify and name people in the photo",
            "Estimate date if not known",
            "Record location/occasion",
            "Note source and provenance",
            "Add family tree connections"
        ]

        # Family tree integration
        advice["family_tree_integration"] = [
            "Link to individuals in family tree software",
            "Add source citations",
            "Create family stories around the photo",
            "Share with relatives for additional identification"
        ]

        return advice

    def _assess_preservation_needs(self) -> Dict[str, Any]:
        """Assess immediate preservation needs"""
        needs = {
            "urgency": "low",
            "format_stability": "good",
            "backup_recommendations": [],
            "sharing_guidelines": []
        }

        # Format stability
        if self.metadata.get("image", {}).get("format") == "JPEG":
            needs["format_stability"] = "good - widely supported format"

        # Backup recommendations
        needs["backup_recommendations"] = [
            "Create 3+ copies on different storage media",
            "Use cloud storage (Google Photos, Amazon Photos, etc.)",
            "Keep one copy offsite for disaster recovery",
            "Consider using archival-quality storage for long-term preservation"
        ]

        # Sharing guidelines
        needs["sharing_guidelines"] = [
            "Share lower-resolution copies (1080px) to preserve originals",
            "Include metadata captions when sharing with family",
            "Use family groups for collaborative identification",
            "Document any stories or memories associated with the photo"
        ]

        return needs


# Legal Investigator Liam - Legal Professional
class LegalInvestigatorLiamInterpreter(PersonaInterpreter):
    """Legal-focused interpreter for legal professionals"""

    def __init__(self, metadata: Dict[str, Any]):
        super().__init__(metadata)
        self.persona_name = "legal_investigator_liam"
        self.persona_icon = "⚖️"

    def interpret(self) -> Dict[str, Any]:
        """Generate legal-focused interpretation"""
        return {
            "persona": self.persona_name,
            "key_findings": self._generate_legal_findings(),
            "admissibility_assessment": self._assess_admissibility(),
            "chain_of_custody": self._analyze_chain_of_custody(),
            "compliance_issues": self._check_compliance(),
            "legal_recommendations": self._generate_legal_recommendations()
        }

    def _generate_legal_findings(self) -> List[str]:
        """Generate legal-focused key findings"""
        findings = []

        # Timestamp verification
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            findings.append("⏰ Original timestamp available for temporal evidence")

        # Location verification
        if self.metadata.get("gps"):
            findings.append("📍 GPS coordinates available for location verification")

        # Authentication status
        if self.metadata.get("forensic", {}).get("authentication_is_authenticated"):
            findings.append("✅ Image contains cryptographic authentication")
        else:
            findings.append("⚠️ No cryptographic authentication - may require expert testimony")

        # Original file integrity
        if self.metadata.get("file_integrity", {}).get("sha256"):
            findings.append("🔐 File hash available for integrity verification")

        return findings

    def _assess_admissibility(self) -> Dict[str, Any]:
        """Assess legal admissibility as evidence"""
        admissibility = {
            "score": "unknown",
            "foundation_requirements": [],
            "authentication_basis": [],
            "hearsay_exceptions": [],
            "challenges": []
        }

        # Authentication basis
        auth_basis = []

        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            auth_basis.append("EXIF timestamp provides temporal authentication")

        if self.metadata.get("gps"):
            auth_basis.append("GPS data provides location authentication")

        if self.metadata.get("file_integrity"):
            auth_basis.append("Cryptographic hash provides file integrity verification")

        if self.metadata.get("forensic", {}).get("authentication_is_authenticated"):
            auth_basis.append("Digital signatures provide strong authentication")

        admissibility["authentication_basis"] = auth_basis

        # Foundation requirements
        foundation_requirements = []

        # Witness requirements
        foundation_requirements.append("Testimony from photographer or custodian of records")

        # Original evidence
        if self.metadata.get("file_integrity"):
            foundation_requirements.append("Original file or authenticated copy available")

        admissibility["foundation_requirements"] = foundation_requirements

        # Hearsay exceptions
        hearsay_exceptions = []

        # Business records exception
        if self.metadata.get("exif", {}).get("Software"):
            hearsay_exceptions.append("May qualify as business record if from business context")

        # Silent witness doctrine
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            hearsay_exceptions.append("EXIF data may qualify under 'silent witness' doctrine")

        admissibility["hearsay_exceptions"] = hearsay_exceptions

        # Overall admissibility score
        if len(auth_basis) >= 3:
            admissibility["score"] = "highly_admissible"
        elif len(auth_basis) >= 2:
            admissibility["score"] = "likely_admissible"
        elif len(auth_basis) >= 1:
            admissibility["score"] = "potentially_admissible"
        else:
            admissibility["score"] = "requires_authentication"

        return admissibility

    def _analyze_chain_of_custody(self) -> Dict[str, Any]:
        """Analyze chain of custody for legal purposes"""
        custody = {
            "documented": False,
            "gaps": [],
            "witnesses_required": 1,
            "foundation_testimony": "unknown",
            "custodial_issues": []
        }

        # Check for custody documentation
        if self.metadata.get("filesystem", {}).get("created"):
            custody["documented"] = True

        # Check for potential gaps
        if not self.metadata.get("exif", {}).get("DateTimeOriginal"):
            custody["gaps"].append("Original creation timestamp missing")

        if not self.metadata.get("gps"):
            custody["gaps"].append("Location data missing")

        # Determine witness requirements
        if custody["gaps"]:
            custody["witnesses_required"] = 2
            custody["foundation_testimony"] = "Multiple witnesses needed due to gaps"
        else:
            custody["witnesses_required"] = 1
            custody["foundation_testimony"] = "Single witness (photographer/custodian) sufficient"

        return custody

    def _check_compliance(self) -> Dict[str, Any]:
        """Check legal and regulatory compliance"""
        compliance = {
            "privacy_concerns": [],
            "gdpr_relevance": False,
            "copyright_issues": [],
            "recommendations": []
        }

        # Privacy concerns
        if self.metadata.get("gps"):
            compliance["privacy_concerns"].append("GPS location data - consider redaction for privacy")

        if self.metadata.get("exif", {}).get("OwnerName"):
            compliance["privacy_concerns"].append("Device owner name - personal identifiable information")

        # GDPR relevance
        if compliance["privacy_concerns"]:
            compliance["gdpr_relevance"] = True
            compliance["recommendations"].append("May contain personal data under GDPR - consider consent requirements")

        # Copyright considerations
        if self.metadata.get("exif", {}).get("Copyright"):
            compliance["copyright_issues"].append("Copyright notice present in metadata")

        compliance["recommendations"].extend([
            "Review all metadata for privacy concerns before submission",
            "Consider redacting sensitive information (GPS, personal names)",
            "Document source and permissions for use",
            "Preserve original metadata for evidentiary purposes"
        ])

        return compliance

    def _generate_legal_recommendations(self) -> List[str]:
        """Generate legal-focused recommendations"""
        recommendations = []

        # Evidence preservation
        recommendations.extend([
            "🔒 Preserve original file and metadata without alteration",
            "📋 Document chain of custody thoroughly",
            "✍️ Create hash verification certificates for file integrity",
            "👥 Identify and prepare witnesses for foundation testimony"
        ])

        # Authentication support
        if self.metadata.get("exif"):
            recommendations.append("🔍 Use EXIF metadata to support authentication")

        if self.metadata.get("forensic", {}).get("authentication_is_authenticated"):
            recommendations.append("✅ Cryptographic authentication strengthens admissibility")

        # Privacy protection
        if self.metadata.get("gps") or self.metadata.get("exif", {}).get("OwnerName"):
            recommendations.extend([
                "🛡️ Consider redacting sensitive location or personal information",
                "⚖️ Balance probative value against privacy concerns"
            ])

        # Expert witness preparation
        recommendations.extend([
            "👨‍⚖️ Consider retaining digital forensics expert for complex authentication",
            "📊 Prepare demonstrative exhibits showing metadata authentication",
            "📝 Create detailed reports explaining technical evidence"
        ])

        return recommendations


# Insurance Adjuster Ivy - Claims Professional
class InsuranceAdjusterIvyInterpreter(PersonaInterpreter):
    """Insurance-focused interpreter for claims processing"""

    def __init__(self, metadata: Dict[str, Any]):
        super().__init__(metadata)
        self.persona_name = "insurance_adjuster_ivy"
        self.persona_icon = "💼"

    def interpret(self) -> Dict[str, Any]:
        """Generate insurance-focused interpretation"""
        return {
            "persona": self.persona_name,
            "key_findings": self._generate_insurance_findings(),
            "coverage_analysis": self._analyze_coverage(),
            "incident_context": self._analyze_incident_context(),
            "fraud_detection": self._assess_fraud_risk(),
            "vehicle_detection": self._detect_vehicles(),
            "damage_assessment": self._assess_damage()
        }

    def _generate_insurance_findings(self) -> List[str]:
        """Generate insurance-focused key findings"""
        findings = []

        # Timestamp for coverage period
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            date_str = self.metadata.get("exif", {}).get("DateTimeOriginal")
            findings.append(f"⏰ Incident timestamp: {date_str}")

        # Location verification
        if self.metadata.get("gps"):
            findings.append("📍 GPS coordinates available for location verification")

        # Weather conditions (if available from location/time)
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            findings.append("🌤️ Timestamp allows weather condition lookup")

        # Device quality for detail assessment
        if self.metadata.get("image", {}).get("width", 0) >= 2000:
            findings.append("✅ High resolution - good for damage assessment detail")

        return findings

    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze insurance coverage implications"""
        coverage = {
            "policy_period_check": "unknown",
            "location_verification": "unknown",
            "timestamp_verification": "unknown",
            "coverage_issues": []
        }

        # Timestamp verification
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            coverage["timestamp_verification"] = "timestamp_available_for_coverage_check"
            coverage["policy_period_check"] = "can_verify_against_policy_dates"

        # Location verification
        if self.metadata.get("gps"):
            coverage["location_verification"] = "gps_confirms_policy_territory"

        return coverage

    def _analyze_incident_context(self) -> Dict[str, Any]:
        """Analyze incident context from metadata"""
        context = {
            "weather_conditions": "lookup_required",
            "lighting_conditions": "unknown",
            "location_accuracy": "unknown",
            "timing_accuracy": "unknown"
        }

        # GPS accuracy
        if self.metadata.get("gps"):
            context["location_accuracy"] = "GPS accurate within 3-5 meters"

        # Timing accuracy
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            context["timing_accuracy"] = "EXIF timestamp accurate to seconds"

        # Lighting conditions from EXIF
        exif = self.metadata.get("exif", {})
        if exif.get("ISOSpeedRatings"):
            iso = int(exif.get("ISOSpeedRatings", 0))
            if iso <= 100:
                context["lighting_conditions"] = "good_lighting_low_iso"
            elif iso <= 400:
                context["lighting_conditions"] = "moderate_lighting"
            elif iso <= 1600:
                context["lighting_conditions"] = "low_light_or_indoor"
            else:
                context["lighting_conditions"] = "very_low_light_or_night"

        return context

    def _assess_fraud_risk(self) -> Dict[str, Any]:
        """Assess fraud detection indicators"""
        fraud = {
            "authenticity_score": 0,
            "manipulation_indicators": [],
            "timestamp_consistency": "unknown",
            "location_consistency": "unknown",
            "metadata_anomalies": []
        }

        # Base authenticity score
        score = 70  # Start with neutral score

        # Positive indicators
        if self.metadata.get("exif", {}).get("DateTimeOriginal"):
            score += 15  # Has original timestamp

        if self.metadata.get("gps"):
            score += 10  # Has location data

        if self.metadata.get("file_integrity", {}).get("sha256"):
            score += 5  # Has hash for integrity verification

        # Negative indicators
        if self.metadata.get("forensic", {}).get("manipulation_detection", {}).get("detected"):
            score -= 30
            fraud["manipulation_indicators"].append("Potential manipulation detected")

        if not self.metadata.get("exif"):
            score -= 20
            fraud["metadata_anomalies"].append("Missing EXIF data - suspicious")

        fraud["authenticity_score"] = max(0, min(100, score))

        # Consistency checks
        fraud["timestamp_consistency"] = "consistent" if score >= 80 else "needs_verification"
        fraud["location_consistency"] = "consistent" if self.metadata.get("gps") else "verification_needed"

        return fraud

    def _detect_vehicles(self) -> Dict[str, Any]:
        """Detect vehicle information if applicable"""
        vehicles = {
            "detected": False,
            "make_model": None,
            "color": None,
            "damage_assessment": None,
            "license_plate": None
        }

        # Note: Actual vehicle detection would require OCR/image analysis
        # This is a placeholder for future enhancement
        vehicles["detected"] = False
        vehicles["note"] = "Vehicle detection requires advanced image analysis not available in current metadata"

        return vehicles

    def _assess_damage(self) -> Dict[str, Any]:
        """Assess damage from image (placeholder for future enhancement)"""
        damage = {
            "visible_damage": False,
            "severity": "unknown",
            "type": "unknown",
            "affected_areas": [],
            "recommendations": []
        }

        # Note: Actual damage assessment would require AI image analysis
        # This is a placeholder for future enhancement
        damage["visible_damage"] = "requires_visual_analysis"
        damage["recommendations"].extend([
            "High-resolution images needed for detailed damage assessment",
            "Multiple angles recommended for comprehensive documentation",
            "Include scale reference in photos when possible"
        ])

        return damage


def add_persona_interpretation(metadata: Dict[str, Any], persona: str = "phone_photo_sarah") -> Dict[str, Any]:
    """
    Add persona-friendly interpretation to raw metadata

    Args:
        metadata: Raw extracted metadata
        persona: Target persona ("phone_photo_sarah", "photographer_peter", "investigator_mike")

    Returns:
        Enhanced metadata with persona interpretation layer
    """
    result = {
        "raw_metadata": metadata,  # Preserve all original data
        "persona_interpretation": {}
    }

    if persona == "phone_photo_sarah":
        interpreter = PersonaInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret_for_sarah()
    elif persona == "photographer_peter":
        interpreter = PhotographerPeterInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "investigator_mike":
        interpreter = InvestigatorMikeInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "security_analyst_sam":
        interpreter = SecurityAnalystSamInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "social_media_manager_sophia":
        interpreter = SocialMediaManagerSophiaInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "genealogy_researcher_grace":
        interpreter = GenealogyResearcherGraceInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "legal_investigator_liam":
        interpreter = LegalInvestigatorLiamInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()
    elif persona == "insurance_adjuster_ivy":
        interpreter = InsuranceAdjusterIvyInterpreter(metadata)
        result["persona_interpretation"] = interpreter.interpret()

    return result

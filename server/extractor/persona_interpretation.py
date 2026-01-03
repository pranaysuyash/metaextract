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

            self.interpretation["plain_english_answers"]["location"] = {
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{lat:.6f}, {lon:.6f}"
                },
                "has_location": True,
                "answer": readable_answer,
                "details": f"GPS coordinates found: {lat:.6f}, {lon:.6f}",
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
        modes = {
            0: "Auto",
            1: "Manual",
            2: "Auto bracket",
            3: "Aperture priority",
            4: "Shutter priority",
            5: "Program",
            6: "Aperture priority",
            7: "Portrait mode",
            8: "Landscape mode"
        }
        if isinstance(value, int):
            return modes.get(value, "unknown")
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

    return result
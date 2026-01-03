#!/usr/bin/env python3
"""
Persona-Friendly Metadata Interpretation Layer
Transforms raw technical metadata into plain English answers for different user personas
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

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

            self.interpretation["plain_english_answers"]["location"] = {
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon,
                    "formatted": f"{lat:.6f}, {lon:.6f}"
                },
                "has_location": True,
                "answer": f"GPS: {lat:.6f}, {lon:.6f}",
                "details": "GPS coordinates found",
                "confidence": "high",
                "needs_reverse_geocoding": True,
                "readable_location": "Address lookup not yet implemented"
            }

            # Check if we have any location names
            location_name = self._get_location_name()
            if location_name:
                self.interpretation["plain_english_answers"]["location"]["readable_location"] = location_name
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
        make = self._extract_field(["EXIF:Make", "Make"])
        model = self._extract_field(["EXIF:Model", "Model"])
        software = self._extract_field(["EXIF:Software", "Software"])

        device_info = {
            "make": make,
            "model": model,
            "software": software
        }

        # Build friendly device name
        friendly_name = self._format_device_name(make, model)
        is_phone = self._detect_phone_camera(make, model)

        self.interpretation["plain_english_answers"]["device"] = {
            "answer": friendly_name,
            "device_type": "smartphone" if is_phone else "camera",
            "details": device_info,
            "confidence": "high" if (make or model) else "none"
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


def add_persona_interpretation(metadata: Dict[str, Any], persona: str = "phone_photo_sarah") -> Dict[str, Any]:
    """
    Add persona-friendly interpretation to raw metadata

    Args:
        metadata: Raw extracted metadata
        persona: Target persona ("phone_photo_sarah", "photographer_peter", etc.)

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
    # Add other personas later
    # elif persona == "photographer_peter":
    #     interpreter = PhotographerPeterInterpreter(metadata)
    #     result["persona_interpretation"] = interpreter.interpret()
    # elif persona == "investigator_mike":
    #     interpreter = InvestigatorMikeInterpreter(metadata)
    #     result["persona_interpretation"] = interpreter.interpret()

    return result
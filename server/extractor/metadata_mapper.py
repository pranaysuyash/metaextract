"""
Metadata Mapper - Normalize extracted metadata into searchable fields.

Maps raw EXIF/IPTC/XMP output into consistent keys and composite fields.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple


def _normalize_key(key: str) -> str:
    key_clean = key.strip().lower()
    key_clean = re.sub(r"[^a-z0-9]+", " ", key_clean)
    return " ".join(key_clean.split())


class CameraNormalizer:
    """Normalize camera make/model for consistent search."""

    MAKE_NORMALIZATIONS = {
        "canon": "Canon",
        "nikon": "Nikon",
        "sony": "Sony",
        "fujifilm": "Fujifilm",
        "fuji": "Fujifilm",
        "olympus": "Olympus",
        "panasonic": "Panasonic",
        "leica": "Leica",
        "pentax": "Pentax",
        "ricoh": "Ricoh",
        "hasselblad": "Hasselblad",
        "mamiya": "Mamiya",
        "phase one": "Phase One",
        "apple": "Apple",
        "samsung": "Samsung",
        "huawei": "Huawei",
        "google": "Google",
        "oneplus": "OnePlus",
        "xiaomi": "Xiaomi",
        "dji": "DJI",
        "gopro": "GoPro",
        "zeiss": "Zeiss",
        "sigma": "Sigma",
        "tamron": "Tamron",
        "tokina": "Tokina",
    }

    def normalize_make(self, make: str) -> Optional[str]:
        if not make or not isinstance(make, str):
            return None
        make_clean = make.strip().lower()
        if make_clean in self.MAKE_NORMALIZATIONS:
            return self.MAKE_NORMALIZATIONS[make_clean]
        for key, normalized in self.MAKE_NORMALIZATIONS.items():
            if key in make_clean or make_clean in key:
                return normalized
        return make.strip().title()

    def normalize_model(self, model: str) -> Optional[str]:
        if not model or not isinstance(model, str):
            return None
        model_clean = model.strip()
        for make in self.MAKE_NORMALIZATIONS.values():
            if model_clean.lower().startswith(make.lower()):
                model_clean = model_clean[len(make) :].strip()
        model_clean = re.sub(
            r"^(EOS|PowerShot|Cyber-shot|ILCE|NEX|Alpha|D|Z)\s*",
            "",
            model_clean,
            flags=re.IGNORECASE,
        )
        return model_clean.strip() if model_clean else None


class LensNormalizer:
    """Normalize lens make/model names."""

    def normalize_make(self, make: str) -> Optional[str]:
        return CameraNormalizer().normalize_make(make)

    def normalize_model(self, model: str) -> Optional[str]:
        if not model or not isinstance(model, str):
            return None
        model_clean = model.strip()
        model_clean = re.sub(
            r"(\d+)-(\d+)\s*mm\s*[fF]/(\d+\.?\d*)",
            r"\1-\2mm f/\3",
            model_clean,
        )
        model_clean = re.sub(
            r"(\d+)\s*mm\s*[fF]/(\d+\.?\d*)",
            r"\1mm f/\2",
            model_clean,
        )
        for make in ["Canon", "Nikon", "Sony", "Sigma", "Tamron", "Tokina", "Zeiss"]:
            if model_clean.startswith(make):
                model_clean = model_clean[len(make) :].strip()
        return model_clean if model_clean else None


class MetadataMapper:
    """Normalize metadata into searchable fields and composites."""

    def __init__(self) -> None:
        self.camera_normalizer = CameraNormalizer()
        self.lens_normalizer = LensNormalizer()

    def map_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        mapped: Dict[str, Any] = {}

        try:
            mapped.update(self._map_camera_metadata(raw_metadata))
            mapped.update(self._map_lens_metadata(raw_metadata))
            mapped.update(self._map_exposure_metadata(raw_metadata))
            mapped.update(self._map_image_quality_metadata(raw_metadata))
            mapped.update(self._map_software_metadata(raw_metadata))
            mapped.update(self._map_copyright_metadata(raw_metadata))
            makernote_data = self._map_makernote_metadata(raw_metadata)
            mapped = self._merge_mapped_fields(mapped, makernote_data, prefer_existing=True)

            iptc_data = self._map_iptc_metadata(raw_metadata)
            mapped = self._merge_mapped_fields(mapped, iptc_data, prefer_existing=False)

            xmp_data = self._map_xmp_metadata(raw_metadata)
            mapped = self._merge_mapped_fields(mapped, xmp_data, prefer_existing=True)

            mapped.update(self._generate_composite_fields(mapped))
        except Exception as e:
            return mapped

        return mapped

    def _get_exif_fields(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        exif = raw_metadata.get("exif") or {}
        if not isinstance(exif, dict):
            return {}
        if "image" in exif or "exif" in exif:
            merged: Dict[str, Any] = {}
            for section in ("image", "exif"):
                data = exif.get(section)
                if isinstance(data, dict):
                    merged.update(data)
            return merged or exif
        return exif

    def _get_metadata_fields(self, raw_metadata: Dict[str, Any], key: str) -> Dict[str, Any]:
        section = raw_metadata.get(key) or {}
        if not isinstance(section, dict):
            return {}
        if section.get("_locked") is True or section.get("available") is False:
            return {}
        fields = section.get("fields")
        if isinstance(fields, dict):
            return fields
        return section

    def _coerce_text(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            for item in value:
                text = self._coerce_text(item)
                if text:
                    return text
            return None
        text = str(value).strip()
        return text or None

    def _coerce_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        text = str(value)
        match = re.search(r"-?\d+", text)
        if match:
            try:
                return int(match.group(0))
            except Exception as e:
                return None
        return None

    def _split_list_value(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            items: List[str] = []
            for item in value:
                items.extend(self._split_list_value(item))
            return items
        if isinstance(value, str):
            parts = [part.strip() for part in value.replace(";", ",").split(",")]
            return [part for part in parts if part]
        text = str(value).strip()
        return [text] if text else []

    def _join_list_value(self, values: List[str]) -> Optional[str]:
        if not values:
            return None
        seen = set()
        ordered: List[str] = []
        for item in values:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)
        return ", ".join(ordered) if ordered else None

    def _merge_mapped_fields(
        self,
        base: Dict[str, Any],
        updates: Dict[str, Any],
        prefer_existing: bool,
    ) -> Dict[str, Any]:
        list_fields = {"keywords", "subject_code", "scene_code", "creator"}
        for key, value in updates.items():
            if value in (None, "", []):
                continue
            if key in list_fields:
                existing = base.get(key)
                merged = self._join_list_value(
                    self._split_list_value(existing) + self._split_list_value(value)
                )
                if merged:
                    base[key] = merged
                continue
            if prefer_existing and base.get(key) not in (None, "", []):
                continue
            base[key] = value
        return base

    def _map_camera_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        camera_data: Dict[str, Any] = {}
        exif_data = self._get_exif_fields(raw_metadata)
        make = exif_data.get("Make")
        if make:
            camera_data["camera_make"] = self.camera_normalizer.normalize_make(str(make))
        model = exif_data.get("Model")
        if model:
            camera_data["camera_model"] = self.camera_normalizer.normalize_model(str(model))
        serial = exif_data.get("BodySerialNumber") or exif_data.get("SerialNumber") or exif_data.get("CameraSerialNumber")
        if serial:
            camera_data["camera_serial"] = str(serial).strip()
        return camera_data

    def _map_lens_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        lens_data: Dict[str, Any] = {}
        exif_data = self._get_exif_fields(raw_metadata)
        lens_model = exif_data.get("LensModel") or exif_data.get("LensInfo")
        if lens_model:
            lens_data["lens_model"] = self.lens_normalizer.normalize_model(str(lens_model))
        lens_make = exif_data.get("LensMake")
        if lens_make:
            lens_data["lens_make"] = self.lens_normalizer.normalize_make(str(lens_make))
        elif lens_data.get("lens_model"):
            model = lens_data["lens_model"]
            for make in ["Canon", "Nikon", "Sony", "Sigma", "Tamron", "Tokina", "Zeiss"]:
                if make.lower() in model.lower():
                    lens_data["lens_make"] = make
                    break
        lens_serial = exif_data.get("LensSerialNumber")
        if lens_serial:
            lens_data["lens_serial"] = str(lens_serial).strip()
        return lens_data

    def _map_exposure_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        exposure_data: Dict[str, Any] = {}
        exif_data = self._get_exif_fields(raw_metadata)

        iso = exif_data.get("ISOSpeedRatings") or exif_data.get("ISO")
        if iso:
            exposure_data["iso"] = self._parse_iso(iso)

        aperture = exif_data.get("FNumber") or exif_data.get("ApertureValue")
        if aperture:
            exposure_data["aperture"] = self._parse_aperture(aperture)

        shutter = exif_data.get("ExposureTime") or exif_data.get("ShutterSpeedValue")
        if shutter:
            shutter_display, shutter_decimal = self._parse_shutter_speed(shutter)
            if shutter_display:
                exposure_data["shutter_speed"] = shutter_display
                exposure_data["shutter_speed_decimal"] = shutter_decimal

        exp_comp = exif_data.get("ExposureCompensation") or exif_data.get("ExposureBiasValue")
        if exp_comp:
            exposure_data["exposure_compensation"] = self._parse_exposure_compensation(exp_comp)

        exp_mode = exif_data.get("ExposureMode") or exif_data.get("ExposureProgram")
        if exp_mode is not None:
            exposure_data["exposure_mode"] = self._parse_exposure_mode(exp_mode)

        metering = exif_data.get("MeteringMode")
        if metering:
            exposure_data["metering_mode"] = self._parse_metering_mode(metering)

        focal_length = exif_data.get("FocalLength")
        if focal_length:
            exposure_data["focal_length"] = self._parse_focal_length(focal_length)

        focal_35mm = exif_data.get("FocalLengthIn35mmFilm")
        if focal_35mm:
            exposure_data["focal_length_35mm"] = self._parse_focal_length_35mm(focal_35mm)

        flash = exif_data.get("Flash")
        if flash is not None:
            flash_used, flash_mode = self._parse_flash(flash)
            exposure_data["flash_used"] = flash_used
            if flash_mode:
                exposure_data["flash_mode"] = flash_mode

        wb = exif_data.get("WhiteBalance")
        if wb:
            exposure_data["white_balance"] = self._parse_white_balance(wb)

        color_temp = exif_data.get("ColorTemperature")
        if color_temp:
            exposure_data["color_temperature"] = self._parse_color_temperature(color_temp)

        return exposure_data

    def _map_image_quality_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        quality_data: Dict[str, Any] = {}
        image = raw_metadata.get("image") or {}
        if isinstance(image, dict):
            fmt = image.get("format")
            if fmt:
                quality_data["image_quality"] = str(fmt).upper()
            mode = image.get("mode")
            if mode:
                quality_data["bit_depth"] = self._infer_bit_depth(str(mode))
        exif_data = self._get_exif_fields(raw_metadata)
        color_space = exif_data.get("ColorSpace")
        if color_space:
            quality_data["color_space"] = self._parse_color_space(color_space)
        return quality_data

    def _map_software_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        software_data: Dict[str, Any] = {}
        exif_data = self._get_exif_fields(raw_metadata)
        software = exif_data.get("Software")
        if software:
            software_data["software"] = str(software).strip()
        processing = exif_data.get("ProcessingSoftware") or exif_data.get("HostComputer")
        if processing and processing != software:
            software_data["edit_software"] = str(processing).strip()
        return software_data

    def _map_copyright_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        copyright_data: Dict[str, Any] = {}
        exif_data = self._get_exif_fields(raw_metadata)
        copyright_info = exif_data.get("Copyright")
        if copyright_info:
            copyright_data["copyright"] = str(copyright_info).strip()
        creator = exif_data.get("Artist") or exif_data.get("Creator")
        if creator:
            copyright_data["creator"] = str(creator).strip()
        creator_tool = exif_data.get("CreatorTool")
        if creator_tool:
            copyright_data["creator_tool"] = str(creator_tool).strip()
        return copyright_data

    def _map_makernote_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        makernote = raw_metadata.get("makernote") or {}
        if not isinstance(makernote, dict) or makernote.get("_locked") is True:
            return {}

        sections: Dict[str, Dict[str, Any]] = {}
        for vendor, fields in makernote.items():
            if isinstance(fields, dict):
                sections[vendor] = fields

        if not sections:
            return {}

        normalized_sections: Dict[str, Dict[str, Any]] = {}
        for vendor, fields in sections.items():
            normalized_sections[vendor] = {
                _normalize_key(str(k)): v for k, v in fields.items()
            }

        def find_value(candidates: List[str]) -> Optional[Any]:
            for fields in normalized_sections.values():
                for candidate in candidates:
                    key = _normalize_key(candidate)
                    if key in fields:
                        return fields[key]
            return None

        data: Dict[str, Any] = {}

        shutter_count = find_value([
            "ShutterCount",
            "ShutterCount2",
            "ShutterReleaseCount",
            "TotalShutterReleases",
            "ImageCount",
            "ImageNumber",
            "FrameCount",
        ])
        shutter_count_value = self._coerce_int(shutter_count)
        if shutter_count_value is not None:
            data["shutter_count"] = shutter_count_value

        image_number = find_value(["ImageNumber", "FileNumber", "SequenceNumber", "BurstSequence"])
        image_number_value = self._coerce_int(image_number)
        if image_number_value is not None:
            data["image_number"] = image_number_value

        camera_serial = find_value(["SerialNumber", "CameraSerialNumber", "BodySerialNumber", "CameraSerial"])
        if camera_serial:
            data["camera_serial"] = str(camera_serial).strip()

        internal_serial = find_value(["InternalSerialNumber", "InternalSerial", "InternalSerialNo"])
        if internal_serial:
            data["internal_serial"] = str(internal_serial).strip()

        lens_serial = find_value(["LensSerialNumber", "LensSerial", "LensIDNumber"])
        if lens_serial:
            data["lens_serial"] = str(lens_serial).strip()

        owner_name = find_value(["OwnerName", "CameraOwnerName", "Owner"])
        if owner_name:
            data["owner_name"] = str(owner_name).strip()

        firmware_version = find_value(["FirmwareVersion", "FirmwareRevision", "Firmware", "FirmwareID"])
        if firmware_version:
            data["firmware_version"] = str(firmware_version).strip()

        lens_model = find_value(["LensModel", "LensType", "Lens"])
        if lens_model and not data.get("lens_model"):
            data["lens_model"] = str(lens_model).strip()

        focus_distance = find_value(["FocusDistance", "FocusDistanceUpper", "FocusDistanceLower"])
        if focus_distance:
            data["focus_distance"] = str(focus_distance).strip()

        af_points = find_value(["AFPointsInFocus", "AFPointsUsed", "AFPointUsed"])
        if af_points:
            data["af_points_in_focus"] = str(af_points).strip()

        af_point_selected = find_value(["AFPointSelected", "PrimaryAFPoint", "AFPoint"])
        if af_point_selected:
            data["af_point_selected"] = str(af_point_selected).strip()

        camera_temp = find_value(["CameraTemperature", "InternalTemperature", "Temperature"])
        if camera_temp:
            data["camera_temperature"] = str(camera_temp).strip()

        return data

    def _map_iptc_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        iptc_fields = self._normalize_iptc_fields(self._get_metadata_fields(raw_metadata, "iptc"))
        if not iptc_fields:
            return {}
        data: Dict[str, Any] = {}
        title = self._coerce_text(iptc_fields.get("title"))
        if title:
            data["title"] = title
        headline = self._coerce_text(iptc_fields.get("headline"))
        if headline:
            data["headline"] = headline
        description = self._coerce_text(iptc_fields.get("description"))
        if description:
            data["description"] = description
        keywords = self._join_list_value(self._split_list_value(iptc_fields.get("keywords")))
        if keywords:
            data["keywords"] = keywords
        creator = self._join_list_value(self._split_list_value(iptc_fields.get("creator")))
        if creator:
            data["creator"] = creator
        credit_line = self._coerce_text(iptc_fields.get("credit_line"))
        if credit_line:
            data["credit_line"] = credit_line
        source = self._coerce_text(iptc_fields.get("source"))
        if source:
            data["source"] = source
        instructions = self._coerce_text(iptc_fields.get("instructions"))
        if instructions:
            data["instructions"] = instructions
        rights = self._coerce_text(iptc_fields.get("rights_usage_terms"))
        if rights:
            data["rights_usage_terms"] = rights
        copyright_info = self._coerce_text(iptc_fields.get("copyright"))
        if copyright_info:
            data["copyright"] = copyright_info
        city = self._coerce_text(iptc_fields.get("location_city"))
        if city:
            data["location_city"] = city
        state = self._coerce_text(iptc_fields.get("location_state"))
        if state:
            data["location_state"] = state
        country = self._coerce_text(iptc_fields.get("location_country"))
        if country:
            data["location_country"] = country
        country_code = self._coerce_text(iptc_fields.get("location_country_code"))
        if country_code:
            data["location_country_code"] = country_code
        sublocation = self._coerce_text(iptc_fields.get("location_sublocation"))
        if sublocation:
            data["location_sublocation"] = sublocation
        event = self._coerce_text(iptc_fields.get("event"))
        if event:
            data["event"] = event
        subject_code = self._join_list_value(self._split_list_value(iptc_fields.get("subject_code")))
        if subject_code:
            data["subject_code"] = subject_code
        scene_code = self._join_list_value(self._split_list_value(iptc_fields.get("scene_code")))
        if scene_code:
            data["scene_code"] = scene_code
        genre = self._coerce_text(iptc_fields.get("intellectual_genre"))
        if genre:
            data["intellectual_genre"] = genre
        return data

    def _map_xmp_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        xmp_fields = self._normalize_xmp_fields(self._get_metadata_fields(raw_metadata, "xmp"))
        if not xmp_fields:
            return {}
        data: Dict[str, Any] = {}
        title = self._coerce_text(xmp_fields.get("title"))
        if title:
            data["title"] = title
        headline = self._coerce_text(xmp_fields.get("headline"))
        if headline:
            data["headline"] = headline
        description = self._coerce_text(xmp_fields.get("description"))
        if description:
            data["description"] = description
        keywords = self._join_list_value(self._split_list_value(xmp_fields.get("keywords")))
        if keywords:
            data["keywords"] = keywords
        creator = self._join_list_value(self._split_list_value(xmp_fields.get("creator")))
        if creator:
            data["creator"] = creator
        credit_line = self._coerce_text(xmp_fields.get("credit_line"))
        if credit_line:
            data["credit_line"] = credit_line
        source = self._coerce_text(xmp_fields.get("source"))
        if source:
            data["source"] = source
        instructions = self._coerce_text(xmp_fields.get("instructions"))
        if instructions:
            data["instructions"] = instructions
        rights = self._coerce_text(xmp_fields.get("rights_usage_terms"))
        if rights:
            data["rights_usage_terms"] = rights
        creator_tool = self._coerce_text(xmp_fields.get("creator_tool"))
        if creator_tool:
            data["creator_tool"] = creator_tool
        city = self._coerce_text(xmp_fields.get("location_city"))
        if city:
            data["location_city"] = city
        state = self._coerce_text(xmp_fields.get("location_state"))
        if state:
            data["location_state"] = state
        country = self._coerce_text(xmp_fields.get("location_country"))
        if country:
            data["location_country"] = country
        country_code = self._coerce_text(xmp_fields.get("location_country_code"))
        if country_code:
            data["location_country_code"] = country_code
        sublocation = self._coerce_text(xmp_fields.get("location_sublocation"))
        if sublocation:
            data["location_sublocation"] = sublocation
        event = self._coerce_text(xmp_fields.get("event"))
        if event:
            data["event"] = event
        subject_code = self._join_list_value(self._split_list_value(xmp_fields.get("subject_code")))
        if subject_code:
            data["subject_code"] = subject_code
        scene_code = self._join_list_value(self._split_list_value(xmp_fields.get("scene_code")))
        if scene_code:
            data["scene_code"] = scene_code
        genre = self._coerce_text(xmp_fields.get("intellectual_genre"))
        if genre:
            data["intellectual_genre"] = genre
        return data

    def _normalize_iptc_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        if not fields:
            return {}
        mapping = {
            "object name": "title",
            "headline": "headline",
            "caption abstract": "description",
            "keywords": "keywords",
            "by line": "creator",
            "credit": "credit_line",
            "source": "source",
            "copyright notice": "copyright",
            "special instructions": "instructions",
            "city": "location_city",
            "province state": "location_state",
            "country primary location name": "location_country",
            "country primary location code": "location_country_code",
            "sublocation": "location_sublocation",
            "intellectual genre": "intellectual_genre",
            "scene": "scene_code",
            "subject reference": "subject_code",
            "event": "event",
        }
        normalized = dict(fields)
        for key, value in fields.items():
            mapped = mapping.get(_normalize_key(str(key)))
            if mapped and mapped not in normalized:
                normalized[mapped] = value
        return normalized

    def _normalize_xmp_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        if not fields:
            return {}
        mapping = {
            "title": "title",
            "headline": "headline",
            "description": "description",
            "creator": "creator",
            "keywords": "keywords",
            "credit": "credit_line",
            "source": "source",
            "instructions": "instructions",
            "usage terms": "rights_usage_terms",
            "creator tool": "creator_tool",
            "city": "location_city",
            "state": "location_state",
            "country": "location_country",
            "country code": "location_country_code",
            "sublocation": "location_sublocation",
            "event": "event",
            "subject code": "subject_code",
            "scene": "scene_code",
            "intellectual genre": "intellectual_genre",
        }
        normalized = dict(fields)
        for key, value in fields.items():
            raw_key = str(key)
            if ":" in raw_key:
                raw_key = raw_key.split(":", 1)[1]
            if "." in raw_key:
                raw_key = raw_key.split(".")[-1]
            mapped = mapping.get(_normalize_key(raw_key))
            if mapped and mapped not in normalized:
                normalized[mapped] = value
        return normalized

    def _generate_composite_fields(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        composite: Dict[str, Any] = {}
        iso = mapped_data.get("iso")
        aperture = mapped_data.get("aperture")
        shutter = mapped_data.get("shutter_speed")
        if iso and aperture and shutter:
            composite["exposure_triangle"] = f"ISO {iso}, f/{aperture}, {shutter}"
        searchable_parts: List[str] = []
        for key in ["camera_make", "camera_model", "lens_model", "software", "creator"]:
            if mapped_data.get(key):
                searchable_parts.append(str(mapped_data[key]))
        if composite.get("exposure_triangle"):
            searchable_parts.append(composite["exposure_triangle"])
        for key in [
            "title",
            "headline",
            "keywords",
            "location_city",
            "location_state",
            "location_country",
            "event",
        ]:
            if mapped_data.get(key):
                searchable_parts.append(str(mapped_data[key]))
        if searchable_parts:
            composite["searchable_text"] = " ".join(searchable_parts)
        return composite

    def _parse_iso(self, iso_value: Any) -> Optional[int]:
        try:
            if isinstance(iso_value, (list, tuple)) and iso_value:
                iso_value = iso_value[0]
            return int(float(str(iso_value)))
        except (ValueError, TypeError):
            return None

    def _parse_aperture(self, aperture_value: Any) -> Optional[float]:
        try:
            if isinstance(aperture_value, str) and "/" in aperture_value:
                return float(Fraction(aperture_value))
            return float(aperture_value)
        except (ValueError, TypeError):
            return None

    def _parse_shutter_speed(self, shutter_value: Any) -> Tuple[Optional[str], Optional[float]]:
        try:
            if isinstance(shutter_value, str) and "/" in shutter_value:
                fraction = Fraction(shutter_value)
                decimal = float(fraction)
                display = f"{decimal:.1f}s" if decimal >= 1 else shutter_value
                return display, decimal
            decimal = float(shutter_value)
            if decimal >= 1:
                display = f"{decimal:.1f}s"
            else:
                display = f"1/{int(1/decimal)}"
            return display, decimal
        except (ValueError, TypeError):
            return None, None

    def _parse_exposure_compensation(self, exp_comp_value: Any) -> Optional[float]:
        try:
            if isinstance(exp_comp_value, str) and "/" in exp_comp_value:
                return float(Fraction(exp_comp_value))
            return float(exp_comp_value)
        except (ValueError, TypeError):
            return None

    def _parse_focal_length(self, focal_value: Any) -> Optional[float]:
        try:
            if isinstance(focal_value, str) and "/" in focal_value:
                return float(Fraction(focal_value))
            return float(focal_value)
        except (ValueError, TypeError):
            return None

    def _parse_focal_length_35mm(self, focal_35mm_value: Any) -> Optional[int]:
        try:
            return int(float(str(focal_35mm_value)))
        except (ValueError, TypeError):
            return None

    def _parse_exposure_mode(self, mode_value: Any) -> Optional[str]:
        mode_map = {
            "0": "Auto",
            "1": "Manual",
            "2": "Aperture Priority",
            "3": "Shutter Priority",
            "4": "Creative Program",
            "5": "Action Program",
            "6": "Portrait Program",
            "7": "Landscape Program",
        }
        mode_str = str(mode_value).strip()
        return mode_map.get(mode_str, mode_str)

    def _parse_metering_mode(self, metering_value: Any) -> Optional[str]:
        metering_map = {
            "0": "Unknown",
            "1": "Average",
            "2": "Center-weighted",
            "3": "Spot",
            "4": "Multi-spot",
            "5": "Multi-segment",
            "6": "Partial",
        }
        metering_str = str(metering_value).strip()
        return metering_map.get(metering_str, metering_str)

    def _parse_flash(self, flash_value: Any) -> Tuple[bool, Optional[str]]:
        try:
            flash_int = int(str(flash_value))
            flash_used = (flash_int & 0x01) != 0
            if flash_int & 0x08:
                mode = "Compulsory"
            elif flash_int & 0x10:
                mode = "Compulsory (no flash)"
            elif flash_int & 0x18:
                mode = "Auto"
            else:
                mode = "Auto" if flash_used else "No flash"
            return flash_used, mode
        except (ValueError, TypeError):
            return False, None

    def _parse_white_balance(self, wb_value: Any) -> Optional[str]:
        wb_map = {
            "0": "Auto",
            "1": "Manual",
            "2": "Daylight",
            "3": "Cloudy",
            "4": "Tungsten",
            "5": "Fluorescent",
            "6": "Flash",
        }
        wb_str = str(wb_value).strip()
        return wb_map.get(wb_str, wb_str)

    def _parse_color_temperature(self, temp_value: Any) -> Optional[int]:
        try:
            return int(float(str(temp_value)))
        except (ValueError, TypeError):
            return None

    def _parse_color_space(self, color_space_value: Any) -> Optional[str]:
        cs_map = {"1": "sRGB", "2": "Adobe RGB", "65535": "Uncalibrated"}
        cs_str = str(color_space_value).strip()
        return cs_map.get(cs_str, cs_str)

    def _infer_bit_depth(self, image_mode: str) -> Optional[int]:
        mode_map = {
            "1": 1,
            "L": 8,
            "P": 8,
            "RGB": 8,
            "RGBA": 8,
            "CMYK": 8,
            "YCbCr": 8,
            "LAB": 8,
            "HSV": 8,
            "I": 32,
            "F": 32,
        }
        return mode_map.get(image_mode)

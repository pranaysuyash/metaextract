#!/usr/bin/env python3
"""
Edit History Module
Extracts edit history from images including:
- Lightroom history entries from XMP
- Photoshop history and ancestors
- Capture One variant history
- Crop/rotation/transformation history
- Watermark information

Author: MetaExtract Team
Version: 1.0.0
"""

import re
import struct
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class EditHistoryAnalyzer:
    """
    Edit history analyzer for extracting editing information from images.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.xmp_data: Optional[str] = None
        self.exif_data: Optional[Dict[str, Any]] = None

    def analyze(self) -> Dict[str, Any]:
        """Main entry point - analyze edit history"""
        try:
            self._load_xmp_data()

            result = {
                "lightroom_history": None,
                "photoshop_history": None,
                "photoshop_ancestors": None,
                "capture_one_history": None,
                "transformations": {},
                "crop_applied": False,
                "rotation_applied": False,
                "watermark_applied": False,
                "edit_timestamp": None,
                "edit_software": None,
                "total_edits": 0,
            }

            lr_history = self._parse_lightroom_history()
            if lr_history:
                result["lightroom_history"] = lr_history

            ps_history = self._parse_photoshop_history()
            if ps_history:
                result["photoshop_history"] = ps_history

            ps_ancestors = self._parse_photoshop_ancestors()
            if ps_ancestors:
                result["photoshop_ancestors"] = ps_ancestors

            co_history = self._parse_capture_one_history()
            if co_history:
                result["capture_one_history"] = co_history

            transformations = self._parse_transformations()
            if transformations:
                result["transformations"] = transformations

            crop_info = self._parse_crop_info()
            if crop_info:
                result["crop_applied"] = True
                result["crop"] = crop_info

            rotation_info = self._parse_rotation_info()
            if rotation_info:
                result["rotation_applied"] = True
                result["rotation"] = rotation_info

            watermark_info = self._parse_watermark_info()
            if watermark_info:
                result["watermark_applied"] = True
                result["watermark"] = watermark_info

            result["edit_software"] = self._detect_edit_software()

            edit_count = 0
            if result["lightroom_history"]:
                edit_count += len(result["lightroom_history"])
            if result["photoshop_history"]:
                edit_count += len(result["photoshop_history"])
            if result["capture_one_history"]:
                edit_count += len(result["capture_one_history"])
            result["total_edits"] = edit_count

            return result

        except Exception as e:
            logger.error(f"Error analyzing edit history: {e}")
            return {"error": str(e)}

    def _load_xmp_data(self):
        """Load XMP data from file"""
        file_path = Path(self.filepath)
        if not file_path.exists():
            return

        try:
            if str(self.filepath).endswith('.png'):
                self._extract_xmp_from_png()
            else:
                self._try_extract_xmp()
        except Exception:
            self.xmp_data = None

    def _extract_xmp_from_png(self):
        """Extract XMP from PNG file"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()

            if len(data) < 16 or data[:8] != b'\x89PNG\r\n\x1a\n':
                return

            offset = 8
            while offset < len(data) - 12:
                length = struct.unpack('>I', data[offset:offset + 4])[0]
                chunk_type = data[offset + 4:offset + 8].decode('latin-1', errors='replace')

                if chunk_type == 'tEXt':
                    chunk_data = data[offset + 8:offset + 8 + length]
                    null_pos = chunk_data.find(b'\x00')
                    if null_pos > 0:
                        keyword = chunk_data[:null_pos].decode('latin-1', errors='replace')
                        if keyword == 'XML:com.adobe.xmp':
                            self.xmp_data = chunk_data[null_pos + 1:].decode('utf-8', errors='replace')

                offset += 12 + length
        except Exception:
            self.xmp_data = None

    def _try_extract_xmp(self):
        """Try to extract XMP from generic file"""
        import struct
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read(4096)

            xmp_start = data.find(b'<?xpacket begin=')
            if xmp_start > 0:
                xmp_end = data.find(b'</x:xmpmeta>', xmp_start)
                if xmp_end > 0:
                    self.xmp_data = data[xmp_start:xmp_end + 12].decode('utf-8', errors='replace')
        except Exception:
            self.xmp_data = None

    def _parse_lightroom_history(self) -> Optional[List[Dict[str, Any]]]:
        """Parse Lightroom edit history from XMP"""
        if not self.xmp_data:
            return None

        history_entries: List[Dict[str, Any]] = []

        history_pattern = r'<rdf:Seq[^>]*>([\s\S]*?)</rdf:Seq>'
        seq_match = re.search(history_pattern, self.xmp_data, re.IGNORECASE)

        if seq_match:
            seq_content = seq_match.group(1)
            li_matches = re.findall(r'<rdf:li[^>]*>([^<]+)</rdf:li>', seq_content)

            for i, entry in enumerate(li_matches):
                entry_clean = entry.strip()
                if entry_clean and len(entry_clean) > 2:
                    history_entries.append({
                        "step": i + 1,
                        "action": entry_clean,
                        "software": "Lightroom",
                    })

        lr_version_pattern = r'lr:versionNumber["\s]*:?\s*["\']?([^"\']+)'
        lr_version_match = re.search(lr_version_pattern, self.xmp_data)
        if lr_version_match:
            for entry in history_entries:
                entry["version"] = lr_version_match.group(1).strip()

        if history_entries:
            return history_entries

        return None

    def _parse_photoshop_history(self) -> Optional[List[Dict[str, Any]]]:
        """Parse Photoshop history from XMP"""
        if not self.xmp_data:
            return None

        history_entries: List[Dict[str, Any]] = []

        history_pattern = r'photoshop:History[\s]*:?\s*["\']?([^"\']+)'
        history_match = re.search(history_pattern, self.xmp_data, re.IGNORECASE)
        if history_match:
            history_entries.append({
                "action": history_match.group(1).strip(),
                "software": "Photoshop",
            })

        stevt_pattern = r'stEvt:action["\s]*:?\s*["\']?([^"\']+)'
        stevt_matches = re.findall(stevt_pattern, self.xmp_data, re.IGNORECASE)

        for action in stevt_matches:
            action_clean = action.strip()
            if action_clean and action_clean not in [h["action"] for h in history_entries]:
                history_entries.append({
                    "action": action_clean,
                    "software": "Photoshop",
                })

        if history_entries:
            return history_entries

        return None

    def _parse_photoshop_ancestors(self) -> Optional[List[str]]:
        """Parse Photoshop ancestors from XMP"""
        if not self.xmp_data:
            return None

        ancestors: List[str] = []

        ancestor_pattern = r'photoshop:Ancestor[\s]*:?\s*["\']?([^"\']+)'
        ancestor_matches = re.findall(ancestor_pattern, self.xmp_data, re.IGNORECASE)

        for ancestor in ancestor_matches:
            ancestor_clean = ancestor.strip()
            if ancestor_clean:
                ancestors.append(ancestor_clean)

        if ancestors:
            return ancestors

        return None

    def _parse_capture_one_history(self) -> Optional[List[Dict[str, Any]]]:
        """Parse Capture One variant history from XMP"""
        if not self.xmp_data:
            return None

        history_entries: List[Dict[str, Any]] = []

        co_patterns = [
            (r'captureone:ProcessVersion["\s]*:?\s*["\']?([^"\']+)', 'ProcessVersion'),
            (r'captureone:VariantName["\s]*:?\s*["\']?([^"\']+)', 'VariantName'),
            (r'captureone:ColorTag["\s]*:?\s*(\d+)', 'ColorTag'),
        ]

        for pattern, field in co_patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                if field == 'ColorTag':
                    history_entries.append({
                        "field": field,
                        "value": int(match.group(1)),
                    })
                else:
                    history_entries.append({
                        "field": field,
                        "value": match.group(1).strip(),
                    })

        if history_entries:
            for entry in history_entries:
                entry["software"] = "Capture One"

            return history_entries

        return None

    def _parse_transformations(self) -> Dict[str, Any]:
        """Parse transformation metadata"""
        transformations: Dict[str, Any] = {}

        if not self.xmp_data:
            return transformations

        patterns = [
            (r'crs:PerspectiveHorizontal["\s]*:?\s*([-\d.]+)', 'perspective_horizontal'),
            (r'crs:PerspectiveVertical["\s]*:?\s*([-\d.]+)', 'perspective_vertical'),
            (r'crs:PerspectiveRotate["\s]*:?\s*([-\d.]+)', 'perspective_rotate'),
            (r'crs:PerspectiveScale["\s]*:?\s*([-\d.]+)', 'perspective_scale'),
            (r'crs:StraightenAngle["\s]*:?\s*([-\d.]+)', 'straighten_angle'),
            (r'crs:KeylineAmount["\s]*:?\s*([-\d.]+)', 'keyline_amount'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                try:
                    transformations[field] = float(match.group(1))
                except ValueError:
                    pass

        return transformations

    def _parse_crop_info(self) -> Optional[Dict[str, Any]]:
        """Parse crop information"""
        if not self.xmp_data:
            return None

        crop_info: Dict[str, Any] = {}

        crop_patterns = [
            (r'crs:CropRect["\s]*:?\s*["\']?([^"\']+)', 'crop_rect'),
            (r'crs:CropUnit["\s]*:?\s*(\d+)', 'crop_unit'),
            (r'crs:CropAngle["\s]*:?\s*([-\d.]+)', 'crop_angle'),
            (r'crs:HasCrop["\s]*:?\s*(true|false)', 'has_crop'),
            (r'crs:HasCropNew["\s]*:?\s*(true|false)', 'has_crop_new'),
        ]

        for pattern, field in crop_patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                if field in ['has_crop', 'has_crop_new']:
                    crop_info[field] = match.group(1).lower() == 'true'
                elif field == 'crop_unit':
                    crop_info[field] = int(match.group(1))
                else:
                    crop_info[field] = match.group(1).strip()

        if crop_info:
            return crop_info

        return None

    def _parse_rotation_info(self) -> Optional[Dict[str, Any]]:
        """Parse rotation information"""
        if not self.xmp_data:
            return None

        rotation_info: Dict[str, Any] = {}

        patterns = [
            (r'tiff:Orientation["\s]*:?\s*(\d+)', 'orientation'),
            (r'crs:Rotate["\s]*:?\s*([-\d.]+)', 'rotate_value'),
            (r'crs:FlipH["\s]*:?\s*(true|false)', 'flip_horizontal'),
            (r'crs:FlipV["\s]*:?\s*(true|false)', 'flip_vertical'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                if field in ['flip_horizontal', 'flip_vertical']:
                    rotation_info[field] = match.group(1).lower() == 'true'
                elif field == 'orientation':
                    rotation_info[field] = int(match.group(1))
                else:
                    try:
                        rotation_info[field] = float(match.group(1))
                    except ValueError:
                        pass

        if rotation_info:
            return rotation_info

        return None

    def _parse_watermark_info(self) -> Optional[Dict[str, Any]]:
        """Parse watermark information"""
        if not self.xmp_data:
            return None

        watermark_info: Dict[str, Any] = {}

        patterns = [
            (r'crs:Watermark["\s]*:?\s*["\']?([^"\']+)', 'watermark_name'),
            (r'crs:WatermarkOpacity["\s]*:?\s*([-\d.]+)', 'watermark_opacity'),
            (r'crs:WatermarkScale["\s]*:?\s*([-\d.]+)', 'watermark_scale'),
            (r'crs:WatermarkRotation["\s]*:?\s*([-\d.]+)', 'watermark_rotation'),
            (r'crs:WatermarkPosition["\s]*:?\s*(\d+)', 'watermark_position'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data, re.IGNORECASE)
            if match:
                try:
                    watermark_info[field] = float(match.group(1))
                except ValueError:
                    watermark_info[field] = match.group(1).strip()

        if watermark_info:
            return watermark_info

        return None

    def _detect_edit_software(self) -> Optional[str]:
        """Detect editing software from XMP"""
        if not self.xmp_data:
            return None

        software_patterns = [
            (r'Lightroom[\s\d.]*', 'Lightroom'),
            (r'Adobe Photoshop[\s\d.]*', 'Photoshop'),
            (r'Capture One[\s\d.]*', 'Capture One'),
            (r'Aperture[\s\d.]*', 'Aperture'),
            (r'Darktable[\s\d.]*', 'Darktable'),
            (r'RawTherapee[\s\d.]*', 'RawTherapee'),
        ]

        for pattern, software in software_patterns:
            if re.search(pattern, self.xmp_data, re.IGNORECASE):
                return software

        return None


def analyze_edit_history(filepath: str) -> Dict[str, Any]:
    """Convenience function to analyze edit history"""
    analyzer = EditHistoryAnalyzer(filepath)
    return analyzer.analyze()


def get_edit_history_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 150

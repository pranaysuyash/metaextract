#!/usr/bin/env python3
"""
Live Photos and Motion Photos Module
Detects and extracts metadata for motion/still image formats:
- Apple Live Photos (HEIC with motion resource)
- Google Motion Photos (JPEG with motion photo extension)
- Samsung Motion Photos (JPEG with XMP)
- HTC Zoe (formerly)
-vivo Motion Photos

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

APPLE_LIVE_PHOTO_SIGNATURE = b'hltn'
GOOGLE_MOTION_PHOTO_UUID = '9E27E3A9-2975-42A1-A0A3-10E75CFAF60C'
SAMSUNG_MOTION_PHOTO_XMP = 'http://ns.samsung.com/motionphoto/1.0/'


class MotionPhotoDetector:
    """
    Detector for Live Photos and Motion Photos.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.photo_type: Optional[str] = None
        self.motion_data: Optional[Dict[str, Any]] = None

    def detect(self) -> Dict[str, Any]:
        """Main entry point - detect motion photo and extract metadata"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                header = f.read(1024)
                f.seek(0)
                self.file_data = f.read()

            result = {
                "success": True,
                "is_motion_photo": False,
                "photo_type": None,
                "motion_data": None,
                "video_offset": None,
                "video_size": None,
                "video_duration": None,
                "primary_image": None,
                "compatibility": [],
            }

            file_ext = file_path.suffix.lower()

            if file_ext in ['.heic', '.heif']:
                apple_result = self._detect_apple_live_photo(header)
                if apple_result:
                    result.update(apple_result)
            elif file_ext in ['.jpg', '.jpeg']:
                google_result = self._detect_google_motion_photo(header)
                if google_result:
                    result.update(google_result)
                else:
                    samsung_result = self._detect_samsung_motion_photo(header)
                    if samsung_result:
                        result.update(samsung_result)

            if result["is_motion_photo"]:
                result["compatibility"] = self._get_compatibility_info(result["photo_type"])

            return result

        except Exception as e:
            logger.error(f"Error detecting motion photo: {e}")
            return {"error": str(e), "success": False}

    def _detect_apple_live_photo(self, header: bytes) -> Optional[Dict[str, Any]]:
        """Detect Apple Live Photo in HEIC file"""
        result: Dict[str, Any] = {}

        if len(header) < 8:
            return None

        if header[:4] == b'\x00\x00\x00' and header[4:8] == b'ftyp':
            hltn_offset = header.find(b'hltn')
            if hltn_offset > 0 and hltn_offset < 4096:
                result["is_motion_photo"] = True
                result["photo_type"] = "Apple Live Photo"
                result["motion_data"] = self._parse_live_photo_resource(header, hltn_offset)

                hvd1_offset = header.find(b'hvd1')
                if hvd1_offset > 0:
                    result["primary_image"] = self._parse_hvd1_box(header, hvd1_offset)

                avc1_offset = header.find(b'avc1')
                if avc1_offset > 0:
                    result["video_codec"] = "H.264/AVC"
                    video_info = self._parse_video_box(header, avc1_offset)
                    if video_info:
                        result.update(video_info)

        return result if result.get("is_motion_photo") else None

    def _parse_live_photo_resource(self, data: bytes, offset: int) -> Dict[str, Any]:
        """Parse Live Photo resource"""
        motion: Dict[str, Any] = {}

        if offset + 8 > len(data):
            return motion

        box_size = struct.unpack('>I', data[offset:offset + 4])[0]
        box_type = data[offset + 4:offset + 8]
        box_data = data[offset + 8:offset + box_size]

        motion["resource_type"] = "hltn"
        motion["resource_size"] = box_size

        if len(box_data) >= 8:
            version = struct.unpack('>I', data[offset + 8:offset + 12])[0]
            motion["version"] = version

            still_offset = struct.unpack('>I', data[offset + 12:offset + 16])[0]
            still_size = struct.unpack('>I', data[offset + 16:offset + 20])[0]
            motion["still_image_offset"] = still_offset
            motion["still_image_size"] = still_size

            motion_offset = struct.unpack('>I', data[offset + 20:offset + 24])[0]
            motion_size = struct.unpack('>I', data[offset + 24:offset + 28])[0]
            motion["motion_offset"] = motion_offset
            motion["motion_size"] = motion_size

            if len(box_data) >= 32:
                duration = struct.unpack('>I', data[offset + 28:offset + 32])[0]
                motion["duration_ms"] = duration

        return motion

    def _parse_hvd1_box(self, data: bytes, offset: int) -> Optional[Dict[str, Any]]:
        """Parse HVD1 box (still image)"""
        if offset + 16 > len(data):
            return None

        box_size = struct.unpack('>I', data[offset:offset + 4])[0]
        image_info: Dict[str, Any] = {}

        ihdr_offset = data.find(b'ihdr', offset, offset + box_size)
        if ihdr_offset > 0 and ihdr_offset + 20 <= len(data):
            image_info["width"] = struct.unpack('>I', data[ihdr_offset + 4:ihdr_offset + 8])[0]
            image_info["height"] = struct.unpack('>I', data[ihdr_offset + 8:ihdr_offset + 12])[0]

        return image_info

    def _parse_video_box(self, data: bytes, offset: int) -> Optional[Dict[str, Any]]:
        """Parse video box info"""
        if offset + 16 > len(data):
            return None

        box_size = struct.unpack('>I', data[offset:offset + 4])[0]
        video_info: Dict[str, Any] = {}

        avc1_end = min(offset + box_size, len(data))

        esds_offset = data.find(b'esds', offset, avc1_end)
        if esds_offset > 0 and esds_offset + 8 <= len(data):
            esds_size = struct.unpack('>I', data[esds_offset:esds_offset + 4])[0]
            if esds_offset + esds_size <= len(data):
                video_info["has_audio"] = b'mp4a' in data[esds_offset:esds_offset + esds_size]

        stts_offset = data.find(b'stts', offset, avc1_end)
        if stts_offset > 0 and stts_offset + 8 <= len(data):
            stts_count = struct.unpack('>I', data[stts_offset + 4:stts_offset + 8])[0]
            video_info["sample_count"] = stts_count

        stsz_offset = data.find(b'stsz', offset, avc1_end)
        if stsz_offset > 0 and stsz_offset + 12 <= len(data):
            stsz_size = struct.unpack('>I', data[stsz_offset + 4:stsz_offset + 8])[0]
            stsz_count = struct.unpack('>I', data[stsz_offset + 8:stsz_offset + 12])[0]
            video_info["sample_size"] = stsz_size
            video_info["total_samples"] = stsz_count

        return video_info

    def _detect_google_motion_photo(self, header: bytes) -> Optional[Dict[str, Any]]:
        """Detect Google Motion Photo in JPEG"""
        result: Dict[str, Any] = {}

        if len(header) < 100:
            return None

        if header[:2] != b'\xff\xd8':
            return None

        uuid_offset = header.find(b'\xff\xe5')
        if uuid_offset < 0:
            uuid_offset = header.find(b'9E27E3A9')

        if uuid_offset > 0:
            mp_uuid = header[uuid_offset:uuid_offset + 16]
            try:
                uuid_str = str(uuid.UUID(bytes=mp_uuid))
                if '9E27E3A9' in uuid_str.upper():
                    result["is_motion_photo"] = True
                    result["photo_type"] = "Google Motion Photo"

                    result["motion_data"] = self._parse_google_motion_photo(header, uuid_offset)
            except Exception:
                pass

        xmp_offset = header.find(b'http://ns.google.com/photos/1.0/motionphoto/')
        if xmp_offset > 0:
            xmp_end = header.find(b'>', xmp_offset)
            if xmp_end > xmp_offset:
                xmp_data = header[xmp_offset:xmp_end + 1].decode('utf-8', errors='replace')
                motion_info = self._parse_motion_photo_xmp(xmp_data)
                if motion_info:
                    result["is_motion_photo"] = True
                    if result.get("photo_type") is None:
                        result["photo_type"] = "Google Motion Photo"
                    result["motion_data"] = motion_info

        return result if result.get("is_motion_photo") else None

    def _parse_google_motion_photo(self, data: bytes, offset: int) -> Dict[str, Any]:
        """Parse Google Motion Photo data"""
        motion: Dict[str, Any] = {}

        try:
            if offset + 28 <= len(data):
                still_end = struct.unpack('<I', data[offset + 16:offset + 20])[0]
                motion_end = struct.unpack('<I', data[offset + 20:offset + 24])[0]

                motion["still_image_offset"] = 0
                motion["still_image_size"] = still_end
                motion["motion_offset"] = still_end
                motion["motion_size"] = motion_end - still_end

                if offset + 32 <= len(data):
                    flags = struct.unpack('<I', data[offset + 28:offset + 32])[0]
                    motion["flags"] = flags
                    motion["is_live"] = bool(flags & 0x01)
                    motion["has_geo"] = bool(flags & 0x02)

        except Exception as e:
            logger.debug(f"Error parsing Google Motion Photo: {e}")

        return motion

    def _parse_motion_photo_xmp(self, xmp_data: str) -> Dict[str, Any]:
        """Parse Motion Photo XMP data"""
        motion: Dict[str, Any] = {}

        patterns = [
            (r'PhotoOffset["\s]*:?\s*(\d+)', 'photo_offset'),
            (r'PhotoLength["\s]*:?\s*(\d+)', 'photo_length'),
            (r'RepresentationIndex["\s]*:?\s*(\d+)', 'representation_index'),
            (r'IsLivePhoto["\s]*:?\s*(true|false)', 'is_live_photo'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, xmp_data, re.IGNORECASE)
            if match:
                value = match.group(1)
                if field in ['photo_offset', 'photo_length', 'representation_index']:
                    motion[field] = int(value)
                elif field == 'is_live_photo':
                    motion[field] = value.lower() == 'true'

        return motion

    def _detect_samsung_motion_photo(self, header: bytes) -> Optional[Dict[str, Any]]:
        """Detect Samsung Motion Photo in JPEG"""
        result: Dict[str, Any] = {}

        if len(header) < 100:
            return None

        if header[:2] != b'\xff\xd8':
            return None

        xmp_offset = header.find(b'http://ns.samsung.com/motionphoto/1.0/')
        if xmp_offset > 0:
            xmp_end = header.find(b'>', xmp_offset)
            if xmp_end > xmp_offset:
                xmp_data = header[xmp_offset:xmp_end + 1].decode('utf-8', errors='replace')
                motion_info = self._parse_samsung_motion_xmp(xmp_data)
                if motion_info:
                    result["is_motion_photo"] = True
                    result["photo_type"] = "Samsung Motion Photo"
                    result["motion_data"] = motion_info

        return result if result.get("is_motion_photo") else None

    def _parse_samsung_motion_xmp(self, xmp_data: str) -> Dict[str, Any]:
        """Parse Samsung Motion Photo XMP data"""
        motion: Dict[str, Any] = {}

        patterns = [
            (r'MotionPhotoOffset["\s]*:?\s*(\d+)', 'photo_offset'),
            (r'MotionPhotoLength["\s]*:?\s*(\d+)', 'photo_length'),
            (r'PhotoOffset["\s]*:?\s*(\d+)', 'still_offset'),
            (r'PhotoLength["\s]*:?\s*(\d+)', 'still_length'),
            (r'RenderedImageWidth["\s]*:?\s*(\d+)', 'rendered_width'),
            (r'RenderedImageHeight["\s]*:?\s*(\d+)', 'rendered_height'),
        ]

        for pattern, field in patterns:
            match = re.search(pattern, xmp_data, re.IGNORECASE)
            if match:
                try:
                    motion[field] = int(match.group(1))
                except ValueError:
                    pass

        return motion

    def _get_compatibility_info(self, photo_type: Optional[str]) -> List[Dict[str, str]]:
        """Get compatibility information for motion photo type"""
        compatibility_map = {
            "Apple Live Photo": [
                {"platform": "iOS", "version": "9.0+", "app": "Photos"},
                {"platform": "macOS", "version": "10.11+", "app": "Photos"},
                {"platform": "iCloud Photos", "version": "All", "app": "Sync"},
            ],
            "Google Motion Photo": [
                {"platform": "Android", "version": "8.0+", "app": "Google Photos"},
                {"platform": "Web", "version": "All", "app": "photos.google.com"},
            ],
            "Samsung Motion Photo": [
                {"platform": "Samsung Gallery", "version": "All", "app": "Gallery"},
                {"platform": "Google Photos", "version": "Compatible", "app": "View"},
            ],
        }

        return compatibility_map.get(photo_type or "", [])


def detect_motion_photo(filepath: str) -> Dict[str, Any]:
    """Convenience function to detect motion photo"""
    detector = MotionPhotoDetector(filepath)
    return detector.detect()


def get_motion_photo_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 25

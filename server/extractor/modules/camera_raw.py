#!/usr/bin/env python3
"""
Camera RAW Format Parser Module
Extracts metadata from camera RAW formats:
- Canon: CR2, CR3, CRW
- Nikon: NEF, NRW
- Sony: ARW, SR2
- Fuji: RAF
- Panasonic: RW2
- Olympus: ORF
- Leica: RWL
- Hasselblad: 3FR
- Phase One: IIQ
- Adobe: DNG
- Epson: ERF
- Konica Minolta: MRW
- Samsung: SRW

Author: MetaExtract Team
Version: 1.0.0
"""

import struct
import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

RAW_SIGNATURES = {
    b'II\x2a\x00': 'TIFF (Little Endian)',
    b'MM\x00\x2a': 'TIFF (Big Endian)',
    b'CR': 'Canon CRW/CR2',
    b'HE': 'Samsung/Google HEIC',
    b'\x89\x4a\x58\x46': 'JPEG-XR',
    b'\xff\xd8\xff\xe1': 'JPEG EXIF',
}

MAKER_TAG_RANGES = {
    'Canon': (0xC000, 0xC7FF),
    'Nikon': (0x000F, 0x0FFF),
    'Sony': (0x2000, 0x27FF),
    'Fuji': (0x0C00, 0x0CFF),
    'Panasonic': (0x0C00, 0x0CFF),
    'Olympus': (0x0200, 0x02FF),
    'Leica': (0x0C00, 0x0CFF),
    'Hasselblad': (0x0C00, 0x0CFF),
}


class CameraRAWParser:
    """
    Camera RAW format parser for extracting metadata from RAW files.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.format_type: Optional[str] = None
        self.xmp_data: Optional[str] = None

    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse RAW file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}

            self.file_size = file_path.stat().st_size

            with open(self.filepath, 'rb') as f:
                header = f.read(16)
                self.file_data = f.read()

            result = {
                "success": True,
                "file_size": self.file_size,
                "raw_format": None,
                "tiff_ifd": None,
                "makernote": None,
                "xmp": None,
                "dng_properties": None,
                "sensor_info": None,
            }

            format_info = self._detect_format(header)
            if format_info:
                result["raw_format"] = format_info
                self.format_type = format_info["type"]

            if self.file_data:
                tiff_result = self._parse_tiff_ifd(self.file_data)
                if tiff_result:
                    result["tiff_ifd"] = tiff_result

                makernote_result = self._extract_makernote(tiff_result)
                if makernote_result:
                    result["makernote"] = makernote_result

                if self.xmp_data:
                    result["xmp"] = self._parse_xmp()

                if self.format_type in ['DNG', 'CR2', 'NEF', 'ARW']:
                    dng_result = self._parse_dng_properties(tiff_result)
                    if dng_result:
                        result["dng_properties"] = dng_result

                sensor_result = self._extract_sensor_info(tiff_result)
                if sensor_result:
                    result["sensor_info"] = sensor_result

            return result

        except Exception as e:
            logger.error(f"Error parsing RAW file: {e}")
            return {"error": str(e), "success": False}

    def _detect_format(self, header: bytes) -> Optional[Dict[str, Any]]:
        """Detect RAW format type"""
        if len(header) < 8:
            return None

        if header[:4] == b'II\x2a\x00':
            endianness = "little"
        elif header[:4] == b'MM\x00\x2a':
            endianness = "big"
        else:
            endianness = "unknown"

        file_ext = Path(self.filepath).suffix.lower()

        format_map = {
            '.cr2': {'type': 'CR2', 'maker': 'Canon', 'compressed': False},
            '.cr3': {'type': 'CR3', 'maker': 'Canon', 'compressed': True},
            '.crw': {'type': 'CRW', 'maker': 'Canon', 'compressed': False},
            '.nef': {'type': 'NEF', 'maker': 'Nikon', 'compressed': False},
            '.nrw': {'type': 'NRW', 'maker': 'Nikon', 'compressed': True},
            '.arw': {'type': 'ARW', 'maker': 'Sony', 'compressed': False},
            '.sr2': {'type': 'SR2', 'maker': 'Sony', 'compressed': True},
            '.raf': {'type': 'RAF', 'maker': 'Fuji', 'compressed': False},
            '.rw2': {'type': 'RW2', 'maker': 'Panasonic', 'compressed': True},
            '.orf': {'type': 'ORF', 'maker': 'Olympus', 'compressed': False},
            '.rwl': {'type': 'RWL', 'maker': 'Leica', 'compressed': False},
            '.3fr': {'type': '3FR', 'maker': 'Hasselblad', 'compressed': False},
            '.iiq': {'type': 'IIQ', 'maker': 'Phase One', 'compressed': False},
            '.dng': {'type': 'DNG', 'maker': 'Adobe/Various', 'compressed': False},
            '.erf': {'type': 'ERF', 'maker': 'Epson', 'compressed': False},
            '.mrw': {'type': 'MRW', 'maker': 'Minolta', 'compressed': False},
            '.srw': {'type': 'SRW', 'maker': 'Samsung', 'compressed': False},
        }

        if file_ext in format_map:
            format_info = format_map[file_ext]
            format_info["endianness"] = endianness
            format_info["extension"] = file_ext
            return format_info

        if header[:2] == b'CR':
            return {"type": 'CRW/CR2', "maker": 'Canon', "compressed": False, "endianness": endianness}

        return None

    def _parse_tiff_ifd(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parse TIFF IFD structure"""
        result: Dict[str, Any] = {}

        if len(data) < 8:
            return None

        if data[:4] == b'II\x2a\x00':
            is_little = True
        elif data[:4] == b'MM\x00\x2a':
            is_little = False
        else:
            return None

        endian = '<' if is_little else '>'

        try:
            ifd_offset = struct.unpack(endian + 'I', data[4:8])[0]
            if ifd_offset >= len(data):
                return None

            num_entries = struct.unpack(endian + 'H', data[ifd_offset:ifd_offset + 2])[0]
            result["entry_count"] = num_entries

            entries = {}
            offset = ifd_offset + 2

            for _ in range(num_entries):
                if offset + 12 > len(data):
                    break

                tag = struct.unpack(endian + 'H', data[offset:offset + 2])[0]
                tag_type = struct.unpack(endian + 'H', data[offset + 2:offset + 4])[0]
                count = struct.unpack(endian + 'I', data[offset + 4:offset + 8])[0]
                value_offset = struct.unpack(endian + 'I', data[offset + 8:offset + 12])[0]

                tag_name = self._get_tag_name(tag)
                value = self._read_tag_value(data, tag, tag_type, count, value_offset, is_little, ifd_offset)

                if value is not None:
                    entries[tag_name] = value

                offset += 12

            result["entries"] = entries

            if 330 in entries:
                result["has_exif_ifd"] = True
            if 34665 in entries:
                result["has_makernote"] = True
                self._extract_makernote_offset(entries[34665], data, is_little)
            if 271 in entries:
                result["make"] = entries[271]
            if 272 in entries:
                result["model"] = entries[272]

            next_ifd = struct.unpack(endian + 'I', data[ifd_offset + 2 + num_entries * 12:ifd_offset + 6 + num_entries * 12])[0]
            if next_ifd > 0 and next_ifd < len(data):
                result["has_next_ifd"] = True

        except Exception as e:
            logger.debug(f"Error parsing TIFF IFD: {e}")

        return result

    def _get_tag_name(self, tag: int) -> str:
        """Get TIFF tag name"""
        tag_names = {
            254: "NewSubfileType",
            256: "ImageWidth",
            257: "ImageHeight",
            258: "BitsPerSample",
            259: "Compression",
            262: "PhotometricInterpretation",
            271: "Make",
            272: "Model",
            273: "StripOffsets",
            277: "SamplesPerPixel",
            278: "RowsPerStrip",
            279: "StripByteCounts",
            282: "XResolution",
            283: "YResolution",
            284: "ResolutionUnit",
            296: "ResolutionUnit",
            305: "Software",
            315: "Artist",
            316: "Copyright",
            330: "SubIFD",
            36867: "DateTimeOriginal",
            37121: "ComponentsConfiguration",
            37377: "ShutterSpeedValue",
            37378: "ApertureValue",
            37380: "ExposureBiasValue",
            37381: "ExposureProgram",
            37382: "MeteringMode",
            37383: "LightSource",
            37384: "Flash",
            37385: "ISOSpeedRatings",
            37386: "FocalLength",
            37500: "MakerNote",
            37510: "UserComment",
            40960: "FlashpixVersion",
            40961: "ColorSpace",
            40962: "PixelXDimension",
            40963: "PixelYDimension",
            41483: "FlashEnergy",
            41484: "SpatialFrequencyResponse",
            41486: "FocalPlaneXResolution",
            41487: "FocalPlaneYResolution",
            41488: "FocalPlaneResolutionUnit",
            41728: "FileSource",
            41729: "SceneType",
            41985: "CustomRendered",
            41986: "ExposureMode",
            41987: "WhiteBalance",
            41988: "DigitalZoomRatio",
            41990: "SceneCaptureType",
            41991: "GainControl",
            41992: "Contrast",
            41993: "Saturation",
            41994: "Sharpness",
            41995: "DeviceSettingDescription",
            41996: "SubjectDistanceRange",
            42016: "ImageUniqueID",
            42032: "CameraOwnerName",
            42033: "BodySerialNumber",
            42034: "LensSpecification",
            42035: "LensModel",
            42036: "LensSerialNumber",
            42240: "Gamma",
            45456: "GoogleVersion",
            45569: "GooglePlusVersion",
            50780: "DNGVersion",
            50781: "DNGBackwardVersion",
            50782: "UniqueCameraModel",
            50783: "LocalizedCameraModel",
            50784: "ColorMatrix1",
            50785: "ColorMatrix2",
            50786: "ReductionMatrix1",
            50787: "ReductionMatrix2",
            50788: "WhiteLevel",
            50789: "DefaultScale",
            50790: "DefaultCropOrigin",
            50791: "DefaultCropSize",
            50792: "ColorimetricReference",
            50827: "RawImageSegmentation",
            50879: "CalibrationIlluminant1",
            50880: "CalibrationIlluminant2",
            50881: "ColorMatrix1",
            50882: "ColorMatrix2",
            50883: "CameraCalibration1",
            50884: "CameraCalibration2",
            50885: "ReductionMatrix1",
            50886: "ReductionMatrix2",
            50887: "AnalogBalance",
            50888: "AsShotNeutral",
            50889: "AsShotWhiteXY",
            50890: "BaselineExposure",
            50891: "BaselineNoise",
            50892: "BaselineSharpness",
            50893: "BayerGreenSplit",
            50894: "LinearResponseLimit",
            50895: "ShadowScale",
            50897: "AntiAliasStrength",
            50898: "DNGPrivateData",
            50899: "MakerNoteSafety",
            50901: "RawDataUniqueID",
            50902: "OriginalRawFileName",
            50903: "ActiveArea",
            50904: "MaskedAreas",
            50905: "AsShotICCProfile",
            50906: "AsShotPreProfileMatrix",
            50907: "CurrentICCProfile",
            50908: "CurrentPreProfileMatrix",
            50931: "ColorimetricReference",
            50934: "CameraCalibrationSignature",
            50935: "ProfileCalibrationSignature",
            50936: "AsShotProfileName",
            50937: "ProfileName",
            50938: "ProfileEmbedPolicy",
            50939: "ProfileCopyright",
            51041: "ForwardMatrix1",
            51042: "ForwardMatrix2",
            51043: "SRGB ICC Profile",
            51077: "JpgFromRawStart",
            51078: "JpgFromRawEnd",
            51107: "DefaultCropSize",
        }

        return tag_names.get(tag, f"Tag_{tag}")

    def _read_tag_value(self, data: bytes, tag: int, tag_type: int, count: int,
                       value_offset: int, is_little: bool, ifd_offset: int) -> Any:
        """Read value from TIFF tag"""
        endian = '<' if is_little else '>'

        type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8}

        try:
            if tag_type == 2:
                str_offset = ifd_offset + 8 if value_offset < 4 else value_offset
                if str_offset + count <= len(data):
                    return data[str_offset:str_offset + count].decode('latin-1', errors='replace').rstrip('\x00')

            elif tag_type == 5:
                values = []
                for i in range(count):
                    offset = ifd_offset + 8 + i * 8 if value_offset < 4 else value_offset + i * 8
                    if offset + 8 <= len(data):
                        num = struct.unpack(endian + 'I', data[offset:offset + 4])[0]
                        den = struct.unpack(endian + 'I', data[offset + 4:offset + 8])[0]
                        values.append(num / den if den else 0)
                return values

            elif tag_type == 7:
                byte_offset = ifd_offset + 8 if value_offset < 4 else value_offset
                if byte_offset + count <= len(data):
                    return data[byte_offset:byte_offset + count]

            elif tag_type in type_sizes:
                type_size = type_sizes[tag_type]
                total_size = count * type_size
                value_offset_calc = ifd_offset + 8 if value_offset < 4 else value_offset
                if value_offset_calc + total_size <= len(data):
                    if count == 1:
                        if tag_type == 3:
                            return struct.unpack(endian + 'H', data[value_offset_calc:value_offset_calc + 2])[0]
                        elif tag_type == 4:
                            return struct.unpack(endian + 'I', data[value_offset_calc:value_offset_calc + 4])[0]
                    return None

        except Exception:
            pass

        return None

    def _extract_makernote_offset(self, makernote_offset: int, data: bytes, is_little: bool):
        """Extract MakerNote offset for later parsing"""
        endian = '<' if is_little else '>'
        if isinstance(makernote_offset, bytes):
            self.makernote_offset = 0
        else:
            self.makernote_offset = makernote_offset

    def _extract_makernote(self, tiff_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract MakerNote data"""
        if not tiff_result or "entries" not in tiff_result:
            return None

        entries = tiff_result["entries"]
        maker = entries.get("Make", "")
        model = entries.get("Model", "")

        maker_lower = maker.lower() if maker else ""
        model_lower = model.lower() if model else ""

        maker_info: Dict[str, Any] = {}

        if "canon" in maker_lower:
            maker_info["maker"] = "Canon"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_canon_makernote(entries)
        elif "nikon" in maker_lower:
            maker_info["maker"] = "Nikon"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_nikon_makernote(entries)
        elif "sony" in maker_lower or "minolta" in maker_lower:
            maker_info["maker"] = "Sony"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_sony_makernote(entries)
        elif "fuji" in maker_lower or "fujifilm" in maker_lower:
            maker_info["maker"] = "Fuji"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_fuji_makernote(entries)
        elif "olympus" in maker_lower or "olym" in maker_lower:
            maker_info["maker"] = "Olympus"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_olympus_makernote(entries)
        elif "panasonic" in maker_lower or "lumix" in maker_lower:
            maker_info["maker"] = "Panasonic"
            maker_info["model"] = model
            maker_info["fields"] = self._parse_panasonic_makernote(entries)
        elif "leica" in maker_lower:
            maker_info["maker"] = "Leica"
            maker_info["model"] = model
        elif "hasselblad" in maker_lower:
            maker_info["maker"] = "Hasselblad"
            maker_info["model"] = model
        else:
            maker_info["maker"] = maker
            maker_info["model"] = model

        return maker_info if maker_info.get("fields") or maker_info.get("model") else None

    def _parse_canon_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Canon MakerNote"""
        canon_data: Dict[str, Any] = {}

        canon_tags = {
            1: "CameraSettings",
            2: "FocusInfo",
            3: "LensInfo",
            4: "FocusInfo2",
            5: "Moda",
            7: "DriveInfo",
            8: "Unknown",
            9: "CustomFunctions",
            10: "PersonalFunctions",
            11: "PersonalFunctionValues",
            12: "FileInfo",
            13: "AFInfo",
            14: "ThumbnailImage",
            15: "ExifInfo",
        }

        for tag, name in canon_tags.items():
            if f"Tag_{tag}" in entries:
                canon_data[name] = entries[f"Tag_{tag}"]

        if 42035 in entries:
            canon_data["LensModel"] = entries[42035]
        if 42036 in entries:
            canon_data["LensSerialNumber"] = entries[42036]
        if 42033 in entries:
            canon_data["BodySerialNumber"] = entries[42033]
        if 42032 in entries:
            canon_data["CameraOwnerName"] = entries[42032]

        return canon_data

    def _parse_nikon_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Nikon MakerNote"""
        nikon_data: Dict[str, Any] = {}

        nikon_tags = {
            1: "Version",
            2: "ISOSpeed",
            3: "ColorMode",
            4: "Quality",
            5: "WhiteBalance",
            6: "Sharpness",
            7: "FocusMode",
            8: "FlashSetting",
            9: "FlashDevice",
            10: "BracketMode",
            11: "BracketCompensation",
            12: "AutoBracketRelease",
            13: "ExposureCompensation2",
            14: "ImageAdjustment",
            15: "ToneCompensation",
            16: "AuxiliaryLens",
            17: "LensType",
            18: "LensMinMaxFocalAperture",
            19: "FlashGNDistance",
            20: "WhiteBalanceBias",
            21: "ProgramShift",
            22: "ExposureDifference",
            23: "ISO",
            24: "ScreenOffset",
            25: "NikonFileInfo",
            26: "NikonDataDump2",
            27: "NikonDataDump3",
            28: "ShutterCount",
            29: "FlashInfo",
            30: "ImageOptimization",
            31: "VariProgram",
            32: "ImageStabilization",
            33: "AFResponse",
            34: "HighISONoiseReduction",
        }

        for tag, name in nikon_tags.items():
            if f"Tag_{tag}" in entries:
                nikon_data[name] = entries[f"Tag_{tag}"]

        return nikon_data

    def _parse_sony_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Sony MakerNote"""
        sony_data: Dict[str, Any] = {}

        sony_tags = {
            0x0100: "Version",
            0x0101: "CameraType",
            0x0102: "SerialNumber",
            0x0103: "Quality",
            0x0104: "ExposureMode",
            0x0105: "WhiteBalance",
            0x0106: "FocusMode",
            0x0107: "AFMode",
            0x0108: "AFAreaMode",
            0x0109: "FocusPosition",
            0x010A: "LensID",
            0x010B: "FlashMode",
            0x010C: "FlashStatus",
            0x010D: "ProgramAE",
            0x010E: "ISO",
            0x010F: "ISOSetting",
            0x0110: "AutoISO",
            0x0111: "BrightnessValue",
            0x0112: "ExposureCompensation",
            0x0113: "ExposureTime",
            0x0114: "FNumber",
            0x0115: "MeteringMode",
        }

        for tag, name in sony_tags.items():
            if f"Tag_{tag}" in entries:
                sony_data[name] = entries[f"Tag_{tag}"]

        return sony_data

    def _parse_fuji_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Fuji MakerNote"""
        fuji_data: Dict[str, Any] = {}

        fuji_tags = {
            0x0000: "Version",
            0x0010: "Quality",
            0x0011: "Sharpness",
            0x0012: "WhiteBalance",
            0x0013: "Color",
            0x0014: "Tone",
            0x0015: "NoiseReduction",
            0x0016: "HighISONoiseReduction",
            0x0017: "FujifilmFlashMode",
            0x0018: "FlashStrength",
            0x0019: "Macro",
            0x001A: "FocusMode",
            0x001B: "AFMode",
            0x001C: "FocusPoint",
            0x001D: "LensID",
        }

        for tag, name in fuji_tags.items():
            if f"Tag_{tag}" in entries:
                fuji_data[name] = entries[f"Tag_{tag}"]

        return fuji_data

    def _parse_olympus_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Olympus MakerNote"""
        olympus_data: Dict[str, Any] = {}

        olympus_tags = {
            0x0000: "Version",
            0x0100: "CameraSettings",
            0x0200: "RawInfo",
            0x0300: "FocusInfo",
            0x0400: "FlashInfo",
            0x0500: "WhiteBalance",
            0x0600: "ImageQuality",
            0x0700: "SpecialMode",
            0x0800: "JpegQuality",
            0x0900: "Macro",
            0x0A00: "BWMode",
            0x0B00: "DigitalZoom",
            0x0C00: "FocalPlaneDiagonal",
            0x0D00: "LensDistortion",
        }

        for tag, name in olympus_tags.items():
            if f"Tag_{tag}" in entries:
                olympus_data[name] = entries[f"Tag_{tag}"]

        return olympus_data

    def _parse_panasonic_makernote(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Panasonic MakerNote"""
        panasonic_data: Dict[str, Any] = {}

        panasonic_tags = {
            0x0001: "Version",
            0x0002: "LensType",
            0x0003: "LensSerialNumber",
            0x0004: "BodySerialNumber",
            0x0005: "LensFirmware",
            0x0006: "InternalSerialNumber",
            0x0007: "FocusMode",
            0x0008: "AFMode",
            0x0009: "PhotoStyle",
            0x000A: "FilterEffect",
            0x000B: "AspectRatio",
            0x000C: "FrameRate",
            0x000D: "FlashMode",
            0x000E: "ImageStabilization",
        }

        for tag, name in panasonic_tags.items():
            if f"Tag_{tag}" in entries:
                panasonic_data[name] = entries[f"Tag_{tag}"]

        return panasonic_data

    def _parse_xmp(self) -> Dict[str, Any]:
        """Parse XMP data"""
        if not self.xmp_data:
            return {}

        xmp_result: Dict[str, Any] = {}

        patterns = [
            (r'xmp:CreatorTool["\s]*:?\s*["\']?([^"\']+)', 'creator_tool'),
            (r'dc:format["\s]*:?\s*["\']?([^"\']+)', 'format'),
            (r'dc:title["\s]*:?\s*["\']?([^"\']+)', 'title'),
            (r'dc:description["\s]*:?\s*["\']?([^"\']+)', 'description'),
            (r'crs:Version["\s]*:?\s*["\']?([^"\']+)', 'camera_raw_version'),
            (r'crs:ProcessVersion["\s]*:?\s*["\']?([^"\']+)', 'process_version'),
            (r'crs:WhiteBalance["\s]*:?\s*["\']?([^"\']+)', 'white_balance'),
            (r'crs:Temperature["\s]*:?\s*(\d+)', 'temperature'),
            (r'crs:Tint["\s]*:?\s*([-\d.]+)', 'tint'),
            (r'crs:Exposure["\s]*:?\s*([-\d.]+)', 'exposure'),
            (r'crs:Contrast["\s]*:?\s*(\d+)', 'contrast'),
            (r'crs:Highlights["\s]*:?\s*(\d+)', 'highlights'),
            (r'crs:Shadows["\s]*:?\s*(\d+)', 'shadows'),
            (r'crs:Whites["\s]*:?\s*(\d+)', 'whites'),
            (r'crs:Blacks["\s]*:?\s*(\d+)', 'blacks'),
            (r'crs:Clarity["\s]*:?\s*(\d+)', 'clarity'),
            (r'crs:Texture["\s]*:?\s*(\d+)', 'texture'),
            (r'crs:Dehaze["\s]*:?\s*(\d+)', 'dehaze'),
            (r'crs:VignetteAmount["\s]*:?\s*([-\d.]+)', 'vignette_amount'),
        ]

        import re
        for pattern, field in patterns:
            match = re.search(pattern, self.xmp_data)
            if match:
                value = match.group(1).strip()
                if field in ['temperature', 'contrast', 'highlights', 'shadows', 'whites', 'blacks', 'clarity', 'texture', 'dehaze']:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif field in ['exposure', 'tint', 'vignette_amount']:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                xmp_result[field] = value

        return xmp_result

    def _parse_dng_properties(self, tiff_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parse DNG-specific properties"""
        if not tiff_result or "entries" not in tiff_result:
            return None

        entries = tiff_result["entries"]
        dng_props: Dict[str, Any] = {}

        dng_tags = {
            50780: ("dng_version", int),
            50781: ("dng_backward_version", int),
            50782: ("unique_camera_model", str),
            50783: ("localized_camera_model", str),
            50827: ("raw_image_segmentation", list),
            50901: ("raw_data_unique_id", str),
            50902: ("original_raw_file_name", str),
            50903: ("active_area", list),
            50904: ("masked_areas", list),
            51041: ("forward_matrix1", list),
            51042: ("forward_matrix2", list),
        }

        for tag, (field, field_type) in dng_tags.items():
            tag_name = self._get_tag_name(tag)
            if tag_name in entries:
                value = entries[tag_name]
                if field_type == int:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass
                dng_props[field] = value

        if dng_props:
            return dng_props

        return None

    def _extract_sensor_info(self, tiff_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract sensor information"""
        if not tiff_result or "entries" not in tiff_result:
            return None

        entries = tiff_result["entries"]
        sensor: Dict[str, Any] = {}

        if 256 in entries:
            sensor["width"] = entries.get("ImageWidth", entries.get("PixelXDimension"))
        if 257 in entries:
            sensor["height"] = entries.get("ImageHeight", entries.get("PixelYDimension"))
        if 258 in entries:
            bits = entries.get("BitsPerSample")
            if isinstance(bits, list):
                sensor["bits_per_sample"] = bits[0] if bits else 14
            else:
                sensor["bits_per_sample"] = bits or 14
        if 277 in entries:
            sensor["samples_per_pixel"] = entries.get("SamplesPerPixel", 1)

        if "width" in sensor and "height" in sensor:
            sensor["total_pixels"] = sensor["width"] * sensor["height"]
            sensor["megapixels"] = round(sensor["width"] * sensor["height"] / 1000000, 2)

        sensor["aspect_ratio"] = round(sensor["width"] / sensor["height"], 2) if "height" in sensor and sensor["height"] else None

        if sensor:
            return sensor

        return None


def extract_raw_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract RAW file metadata"""
    parser = CameraRAWParser(filepath)
    return parser.parse()


def get_raw_field_count() -> int:
    """Return the number of fields this module extracts"""
    return 150

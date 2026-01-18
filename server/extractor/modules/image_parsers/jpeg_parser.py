"""
JPEG Parser
============

Extracts metadata from JPEG files using ExifTool as canonical source.
Supports: EXIF, IPTC, XMP, GPS, ICC Profile, plus computed metadata.

Key additions beyond basic extraction:
- Image quality analysis
- AI-based analysis (scene, quality, color)
- Perceptual hashing
- Forensic analysis
- Technical metadata
- Data completeness scoring
"""

from . import FormatParser
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import json
import subprocess
import os


class JpegParser(FormatParser):
    """JPEG-specific metadata parser using ExifTool + computed metadata."""
    
    FORMAT_NAME = "JPEG"
    SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.jpe', '.jfif']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract JPEG metadata."""
        result = {}
        
        # Try ExifTool first (canonical for JPEG)
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Fallback to PIL for basic info
            result = self._parse_with_pil(filepath)
        
        # Add computed metadata (quality, AI, hashes, forensic, etc.)
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'JPEG'),
                mode=result.get('color_mode', 'RGB'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool JSON output into structured metadata."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = data.get('FileType') or data.get('File:FileType') or 'JPEG'
        file_size_str = data.get('FileSize') or data.get('System:FileSize')
        if isinstance(file_size_str, str):
            # Parse "106 kB" format
            if ' kB' in file_size_str:
                try:
                    metadata['file_size'] = int(float(file_size_str.replace(' kB', '')) * 1024)
                except:
                    pass
            elif ' MB' in file_size_str:
                try:
                    metadata['file_size'] = int(float(file_size_str.replace(' MB', '')) * 1024 * 1024)
                except:
                    pass
            else:
                try:
                    metadata['file_size'] = int(file_size_str)
                except:
                    pass
        else:
            metadata['file_size'] = file_size_str
            
        metadata['image_size'] = data.get('ImageSize')
        metadata['width'] = self._parse_dimension(data.get('ImageWidth') or data.get('File:ImageWidth'))
        metadata['height'] = self._parse_dimension(data.get('ImageHeight') or data.get('File:ImageHeight'))
        metadata['color_mode'] = data.get('ColorMode') or data.get('ColorType') or 'RGB'
        metadata['bits_per_sample'] = data.get('BitsPerSample') or data.get('File:BitsPerSample')
        metadata['compression'] = data.get('Compression') or data.get('File:EncodingProcess') or 'JPEG'
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # EXIF camera data
        exif = {}
        camera_fields = [
            'Make', 'Model', 'Software', 'Artist', 'Copyright',
            'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
            'LensModel', 'LensSerialNumber', 'LensInfo',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'ISO',
            'ShutterSpeedValue', 'ApertureValue', 'BrightnessValue',
            'ExposureBias', 'MeteringMode', 'Flash',
            'FocalLength', 'FocalLengthIn35mmFilm',
            'WhiteBalance', 'ExposureProgram', 'ExposureMode',
            'SceneCaptureType', 'Contrast', 'Saturation', 'Sharpness',
            'ImageDescription', 'XResolution', 'YResolution', 'ResolutionUnit'
        ]
        
        for field in camera_fields:
            # Try direct key
            if field in data and data[field] is not None:
                exif[field.lower()] = data[field]
            # Try with IFD0: prefix
            elif f'IFD0:{field}' in data and data[f'IFD0:{field}'] is not None:
                exif[field.lower()] = data[f'IFD0:{field}']
            # Try with ExifIFD: prefix
            elif f'ExifIFD:{field}' in data and data[f'ExifIFD:{field}'] is not None:
                exif[field.lower()] = data[f'ExifIFD:{field}']
        
        if exif:
            metadata['exif'] = exif
        
        # EXIF focus data
        focus = {}
        focus_fields = [
            'FocusMode', 'AFPoint', 'AFPointsInFocus', 'AFPointsSelected',
            'AFAreaMode', 'AFZone', 'AFAreaMode', 'AFPointsUsed',
            'FocusDistance', 'FocusRange', 'FocusBracketMode',
            'FaceDetected', 'FaceCount', 'FacePositions'
        ]
        
        for field in focus_fields:
            if field in data and data[field] is not None:
                key = field.lower()
                if key.startswith('af'):
                    key = key[2:]
                if key.startswith('focus'):
                    key = key[5:]
                focus[key] = data[field]
            elif f'ExifIFD:{field}' in data and data[f'ExifIFD:{field}'] is not None:
                key = field.lower()
                if key.startswith('af'):
                    key = key[2:]
                if key.startswith('focus'):
                    key = key[5:]
                focus[key] = data[f'ExifIFD:{field}']
        
        if focus:
            metadata['exif_focus'] = focus
        
        # GPS data
        gps = {}
        gps_fields = [
            'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSLatitudeRef',
            'GPSLongitudeRef', 'GPSAltitudeRef', 'GPSTimeStamp', 'GPSDateStamp',
            'GPSProcessingMethod', 'GPSVersionID'
        ]
        
        for field in gps_fields:
            if field in data and data[field] is not None:
                key = field.lower()
                if key.startswith('gps'):
                    key = key[3:]
                gps[key] = data[field]
            elif f'GPS:{field}' in data and data[f'GPS:{field}'] is not None:
                key = field.lower()
                if key.startswith('gps'):
                    key = key[3:]
                gps[key] = data[f'GPS:{field}']
        
        if gps:
            metadata['gps'] = gps
        
        # IPTC data
        iptc = {}
        iptc_fields = ['Headline', 'Caption', 'Keywords', 'Creator', 'Copyright',
                      'Title', 'Rights', 'WebStatement', 'City', 'ApplicationRecordVersion']
        
        for field in iptc_fields:
            if field in data and data[field]:
                iptc[field.lower()] = data[field]
            elif f'IPTC:{field}' in data and data[f'IPTC:{field}']:
                iptc[field.lower()] = data[f'IPTC:{field}']
        
        if iptc:
            metadata['iptc'] = iptc
        
        # XMP data
        xmp_keys = [k for k in data.keys() if k.startswith('XMP:')]
        if xmp_keys:
            xmp = {}
            for key in xmp_keys:
                xmp[key[4:].lower()] = data[key]
            if xmp:
                metadata['xmp'] = xmp
        
        # ICC Profile
        if data.get('ICCProfile') or data.get('ICC_Profile:ProfileDescription') or data.get('ColorSpaceData'):
            metadata['icc_profile'] = {
                'present': True,
                'description': data.get('ICC_Profile:ProfileDescription', data.get('ICCProfile')),
                'color_space': data.get('ColorSpaceData'),
                'profile_size': data.get('ICC_Profile:ProfileSize')
            }
        
        return metadata
    
    def _parse_with_pil(self, filepath: str) -> Dict[str, Any]:
        """Fallback: parse JPEG with PIL for basic info."""
        from PIL import Image
        
        metadata = {}
        
        try:
            with Image.open(filepath) as img:
                metadata['format'] = 'JPEG'
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['color_mode'] = img.mode
                metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                
                # Basic EXIF
                exif = {}
                if hasattr(img, '_getexif') and img._getexif():
                    from PIL.ExifTags import TAGS
                    for tag_id, value in img._getexif().items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag in ['Make', 'Model', 'DateTime', 'ExposureTime', 
                                   'FNumber', 'ISOSpeedRatings', 'FocalLength']:
                            exif[tag] = value
                if exif:
                    metadata['exif'] = exif
                    
        except Exception as e:
            logger.warning(f"PIL fallback failed for JPEG: {e}")
        
        return metadata
    
    def _parse_dimension(self, value: Any) -> Optional[int]:
        """Parse dimension value to int."""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            if ' ' in value:
                value = value.split(' ')[0]
            try:
                return int(float(value))
            except ValueError:
                pass
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real JPEG metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a JPEG."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['jpg', 'jpeg', 'jpe', 'jfif']


# Convenience function
def parse_jpeg(filepath: str) -> Dict[str, Any]:
    """Parse JPEG file and return metadata."""
    parser = JpegParser()
    return parser.parse(filepath)

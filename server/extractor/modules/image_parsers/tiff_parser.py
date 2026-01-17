"""
TIFF Parser
============

Extracts metadata from TIFF files using ExifTool.
TIFF supports: EXIF, GPS, IPTC, XMP, ICC Profile, MakerNotes.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class TiffParser(FormatParser):
    """TIFF-specific metadata parser using ExifTool."""
    
    FORMAT_NAME = "TIFF"
    SUPPORTED_EXTENSIONS = ['.tiff', '.tif', '.dng']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract TIFF metadata."""
        result = {}
        
        # Try ExifTool first
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Fallback to PIL
            result = self._parse_with_pil(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'TIFF'),
                mode=result.get('color_mode', 'RGB'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for TIFF."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = data.get('FileType', 'TIFF')
        metadata['width'] = self._parse_int(data.get('ImageWidth'))
        metadata['height'] = self._parse_int(data.get('ImageHeight'))
        metadata['color_mode'] = data.get('ColorMode', data.get('PhotometricInterpretation'))
        metadata['bit_depth'] = data.get('BitDepth')
        metadata['compression'] = data.get('Compression')
        metadata['orientation'] = data.get('Orientation')
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # EXIF camera data
        exif = {}
        exif_fields = [
            'Make', 'Model', 'Software', 'Artist', 'Copyright',
            'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
            'LensModel', 'LensSerialNumber', 'LensInfo',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings',
            'ShutterSpeedValue', 'ApertureValue', 'BrightnessValue',
            'ExposureBias', 'MeteringMode', 'Flash',
            'FocalLength', 'FocalLengthIn35mmFilm',
            'WhiteBalance', 'ExposureProgram', 'ExposureMode',
            'SceneCaptureType', 'Contrast', 'Saturation', 'Sharpness',
            'ImageDescription', 'Software'
        ]
        
        for field in exif_fields:
            if field in data and data[field] is not None:
                exif[field.lower()] = data[field]
        
        if exif:
            metadata['exif'] = exif
        
        # GPS data
        gps = {}
        gps_fields = [
            'GPSLatitude', 'GPSLongitude', 'GPSAltitude',
            'GPSLatitudeRef', 'GPSLongitudeRef', 'GPSAltitudeRef',
            'GPSTimeStamp', 'GPSDateStamp', 'GPSProcessingMethod'
        ]
        
        for field in gps_fields:
            if field in data and data[field] is not None:
                gps[field.lower().replace('gps', '').lower()] = data[field]
        
        if gps:
            metadata['gps'] = gps
        
        # IPTC
        iptc = {}
        iptc_fields = ['Headline', 'Caption', 'Keywords', 'Creator', 'Copyright']
        
        for field in iptc_fields:
            if field in data and data[field]:
                iptc[field.lower()] = data[field]
        
        if iptc:
            metadata['iptc'] = iptc
        
        # XMP
        xmp_keys = [k for k in data.keys() if k.startswith('XMP:')]
        if xmp_keys:
            xmp = {}
            for key in xmp_keys:
                xmp[key[4:].lower()] = data[key]
            if xmp:
                metadata['xmp'] = xmp
        
        # ICC Profile
        if data.get('ICCProfile'):
            metadata['icc_profile'] = {'present': True}
        
        # MakerNotes
        if data.get('MakerNote'):
            metadata['maker_notes'] = {'present': True}
        
        return metadata
    
    def _parse_with_pil(self, filepath: str) -> Dict[str, Any]:
        """Fallback: parse TIFF with PIL."""
        from PIL import Image, TiffImagePlugin
        
        metadata = {}
        
        try:
            with Image.open(filepath) as img:
                metadata['format'] = 'TIFF'
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
            logger.warning(f"PIL fallback failed for TIFF: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real TIFF metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a TIFF."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['tiff', 'tif', 'dng']


# Convenience function
def parse_tiff(filepath: str) -> Dict[str, Any]:
    """Parse TIFF file and return metadata."""
    parser = TiffParser()
    return parser.parse(filepath)

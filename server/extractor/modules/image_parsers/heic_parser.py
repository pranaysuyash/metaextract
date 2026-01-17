"""
HEIC/AVIF Parser
================

Extracts metadata from HEIC (HEIF) and AVIF files.
These use ISOBMFF/MP4 container structure.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class HeicParser(FormatParser):
    """HEIC/AVIF-specific metadata parser."""
    
    FORMAT_NAME = "HEIC"
    SUPPORTED_EXTENSIONS = ['.heic', '.heif', '.avif', '.avci', '.hevc']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract HEIC/AVIF metadata."""
        result = {}
        
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            result = self._parse_with_boxes(filepath)
        
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'HEIC'),
                mode=result.get('color_mode', 'RGBA'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for HEIC."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = data.get('FileType', data.get('Format'))
        metadata['width'] = self._parse_int(data.get('ImageWidth'))
        metadata['height'] = self._parse_int(data.get('ImageHeight'))
        metadata['compression'] = data.get('Compress', data.get('Format'))
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # Brand/container info
        if data.get('MajorBrand'):
            metadata['brand'] = data.get('MajorBrand')
        if data.get('MinorVersion'):
            metadata['version'] = data.get('MinorVersion')
        
        # EXIF data
        exif = {}
        exif_fields = [
            'Make', 'Model', 'Software', 'DateTimeOriginal',
            'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength',
            'ImageWidth', 'ImageHeight', 'Rotation', 'Flash'
        ]
        
        for field in exif_fields:
            if data.get(field):
                exif[field.lower()] = data[field]
        
        if exif:
            metadata['exif'] = exif
        
        # GPS
        gps = {}
        if data.get('GPSLatitude') or data.get('GPSLongitude'):
            gps['latitude'] = data.get('GPSLatitude')
            gps['longitude'] = data.get('GPSLongitude')
            gps['altitude'] = data.get('GPSAltitude')
        
        if gps:
            metadata['gps'] = gps
        
        # XMP
        if data.get('XMP') or data.get('ItemDimensions'):
            metadata['xmp'] = {'present': True}
        
        # Depth/Auxiliary
        if data.get('Depth') or data.get('AuxiliaryImageType'):
            metadata['auxiliary'] = {
                'depth': data.get('Depth'),
                'type': data.get('AuxiliaryImageType')
            }
        
        # Color info
        if data.get('ColorPrimaries') or data.get('TransferCharacteristics'):
            metadata['color'] = {
                'primaries': data.get('ColorPrimaries'),
                'transfer': data.get('TransferCharacteristics')
            }
        
        return metadata
    
    def _parse_with_boxes(self, filepath: str) -> Dict[str, Any]:
        """Parse HEIC using ISOBMFF box structure."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                # Read first box
                box = self._read_box(f)
                if box['type'] == 'ftyp':
                    metadata['brand'] = box.get('data', '').decode('latin-1', errors='replace')[:4]
                    metadata['format'] = 'HEIC' if b'heic' in box.get('data', b'') else 'AVIF'
                elif box['type'] == 'moov':
                    metadata = self._parse_moov_box(f, box['size'] - 8)
                    metadata['format'] = 'HEIC'
                elif box['type'] == 'avif':
                    metadata['format'] = 'AVIF'
                else:
                    # Try PIL
                    from PIL import Image
                    with Image.open(filepath) as img:
                        metadata['format'] = img.format or 'HEIC/AVIF'
                        metadata['width'] = img.width
                        metadata['height'] = img.height
                        metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                        
        except Exception as e:
            logger.warning(f"Native HEIC/AVIF parsing failed: {e}")
        
        return metadata
    
    def _read_box(self, f, max_size: int = 10_000_000) -> Dict[str, Any]:
        """Read an ISOBMFF box."""
        if f.tell() > max_size:
            return {'type': 'end'}
            
        header = f.read(8)
        if len(header) < 8:
            return {'type': 'end'}
            
        size = struct.unpack('>I', header[:4])[0]
        box_type = header[4:8].decode('latin-1')
        
        # Handle extended size
        if size == 1:
            ext_size = f.read(8)
            if len(ext_size) == 8:
                size = struct.unpack('>Q', ext_size)[0]
        
        # Handle container boxes (size includes children)
        data_size = size - 8
        if box_type in ['moov', 'trak', 'mdia', 'minf', 'dinf', 'stbl', 'udta', 'meta']:
            return {'type': box_type, 'size': size}
        
        # Read data
        data = f.read(min(data_size, 100_000))  # Limit data read
        
        return {'type': box_type, 'size': size, 'data': data}
    
    def _parse_moov_box(self, f, size: int) -> Dict[str, Any]:
        """Parse moov atom (contains metadata)."""
        metadata = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box(f)
            if box['type'] == 'mvhd':
                version = box['data'][0]
                if version == 0:
                    creation_time = struct.unpack('>I', box['data'][4:8])[0]
                    modification_time = struct.unpack('>I', box['data'][8:12])[0]
                    timescale = struct.unpack('>I', box['data'][12:16])[0]
                    duration = struct.unpack('>I', box['data'][16:20])[0]
                    metadata['duration'] = duration / timescale if timescale else None
                break
            elif box['type'] == 'udta':
                # User data
                pass
            elif box['type'] == 'meta':
                # Metadata
                self._parse_meta_box(f, box['size'] - 8)
        
        return metadata
    
    def _parse_meta_box(self, f, size: int):
        """Parse meta atom."""
        f.read(4)  # Skip version/flags
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box(f)
            if box['type'] == 'hdlr':
                handler_type = box['data'][8:12].decode('latin-1')
                if handler_type == 'pict':
                    pass  # Picture handler
            elif box['type'] == 'iloc':
                pass  # Item location
            elif box['type'] == 'iinf':
                pass  # Item info
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real HEIC metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is HEIC/AVIF."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['heic', 'heif', 'avif', 'avci', 'hevc']


# Convenience function
def parse_heic(filepath: str) -> Dict[str, Any]:
    """Parse HEIC/AVIF file and return metadata."""
    parser = HeicParser()
    return parser.parse(filepath)

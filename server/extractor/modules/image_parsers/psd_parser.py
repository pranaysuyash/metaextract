"""
PSD Parser
==========

Extracts metadata from PSD (Photoshop Document) files.
PSD supports: Image Resources (EXIF, XMP, ICC, Layer info).

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class PsdParser(FormatParser):
    """PSD-specific metadata parser."""
    
    FORMAT_NAME = "PSD"
    SUPPORTED_EXTENSIONS = ['.psd', '.psb']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract PSD metadata."""
        result = {}
        
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            result = self._parse_with_resources(filepath)
        
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'PSD'),
                mode=result.get('color_mode', 'RGB'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for PSD."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = data.get('FileType', 'PSD')
        metadata['width'] = self._parse_int(data.get('ImageWidth'))
        metadata['height'] = self._parse_int(data.get('ImageHeight'))
        metadata['color_mode'] = data.get('ColorMode')
        metadata['bit_depth'] = data.get('BitDepth')
        metadata['layers'] = data.get('LayerCount', 0)
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # EXIF
        exif = {}
        exif_fields = ['Make', 'Model', 'Software', 'DateTime', 'Copyright']
        
        for field in exif_fields:
            if data.get(field):
                exif[field.lower()] = data[field]
        
        if exif:
            metadata['exif'] = exif
        
        # XMP
        if data.get('XMP'):
            metadata['xmp'] = {'present': True}
        
        # ICC Profile
        if data.get('ICCProfile'):
            metadata['icc_profile'] = {'present': True}
        
        # Resolution
        if data.get('XResolution') and data.get('YResolution'):
            metadata['resolution'] = {
                'x': data.get('XResolution'),
                'y': data.get('YResolution'),
                'unit': data.get('ResolutionUnit', 'pixels')
            }
        
        return metadata
    
    def _parse_with_resources(self, filepath: str) -> Dict[str, Any]:
        """Parse PSD using native resource fork reading."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                # PSD signature
                signature = f.read(4)
                if signature != b'8BPS':
                    return {'error': 'Not a valid PSD'}
                
                version = struct.unpack('>H', f.read(2))[0]
                metadata['format'] = 'PSD' if version == 1 else 'PSB'
                
                # Skip to image resources
                f.read(6)  # Reserved
                resource_count = struct.unpack('>I', f.read(4))[0]
                
                # Parse image resources
                for _ in range(resource_count):
                    sig = f.read(4)
                    if sig != b'8BIM':
                        break
                    
                    resource_id = struct.unpack('>H', f.read(2))[0]
                    pascal_name = f.read(1)
                    name_len = pascal_name[0] if pascal_name else 0
                    if name_len > 0:
                        f.read(name_len + (name_len % 2))  # Pad to even
                    
                    data_len = struct.unpack('>I', f.read(4))[0]
                    data_start = f.tell()
                    
                    # Parse known resource types
                    if resource_id == 0x03ED:  # Resolution
                        x_res = struct.unpack('>I', f.read(4))[0] / 65536.0
                        y_res = struct.unpack('>I', f.read(4))[0] / 65536.0
                        unit = f.read(2)
                        metadata['resolution'] = {
                            'x': x_res,
                            'y': y_res,
                            'unit': 'dpi'
                        }
                    
                    elif resource_id == 0x0404:  # IPTC-NAA
                        iptc_data = f.read(data_len)
                        if iptc_data:
                            metadata['iptc'] = {'present': True}
                    
                    elif resource_id == 0x0408:  # XMP
                        xmp_data = f.read(data_len)
                        if xmp_data:
                            metadata['xmp'] = {'present': True}
                    
                    elif resource_id == 0x0421:  # ICC Profile
                        metadata['icc_profile'] = {'present': True}
                    
                    elif resource_id == 0x0406:  # EXIF
                        exif_data = f.read(data_len)
                        if exif_data:
                            metadata['exif'] = {'present': True}
                    
                    else:
                        f.read(data_len)
                    
                    # Pad to even
                    if data_len % 2 == 1:
                        f.read(1)
                
                # Add basic image info
                from PIL import Image
                with Image.open(filepath) as img:
                    if 'width' not in metadata:
                        metadata['width'] = img.width
                    if 'height' not in metadata:
                        metadata['height'] = img.height
                    metadata['color_mode'] = img.mode
                    metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                    
        except Exception as e:
            logger.warning(f"Native PSD parsing failed: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real PSD metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a PSD."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['psd', 'PSB']


# Convenience function
def parse_psd(filepath: str) -> Dict[str, Any]:
    """Parse PSD file and return metadata."""
    parser = PsdParser()
    return parser.parse(filepath)

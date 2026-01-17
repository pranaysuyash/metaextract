"""
PNG Parser
==========

Extracts metadata from PNG files using native chunk parsing + ExifTool.
PNG supports: tEXt/zTXt/iTXt text chunks, ICC Profile, Physical dimensions.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct
import zlib


class PngParser(FormatParser):
    """PNG-specific metadata parser using native chunk parsing + ExifTool."""
    
    FORMAT_NAME = "PNG"
    SUPPORTED_EXTENSIONS = ['.png', '.apng']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract PNG metadata."""
        result = {}
        
        # Try ExifTool first (covers all PNG metadata)
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Fallback to native chunk parsing
            result = self._parse_with_chunks(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'PNG'),
                mode=result.get('color_mode', 'RGBA'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for PNG."""
        metadata = {}
        
        # Core image properties - check both with and without PNG: prefix
        metadata['format'] = 'PNG'
        metadata['width'] = self._parse_int(
            data.get('ImageWidth') or 
            data.get('PNG:ImageWidth') or 
            data.get('File:ImageWidth')
        )
        metadata['height'] = self._parse_int(
            data.get('ImageHeight') or 
            data.get('PNG:ImageHeight') or 
            data.get('File:ImageHeight')
        )
        metadata['color_mode'] = data.get('ColorType') or data.get('PNG:ColorType') or data.get('ColorMode')
        metadata['bit_depth'] = data.get('BitDepth') or data.get('PNG:BitDepth')
        metadata['compression'] = data.get('Compression') or data.get('PNG:Compression')
        metadata['interlace'] = data.get('Interlace') or data.get('PNG:Interlace')
        
        # File size
        file_size_str = data.get('FileSize') or data.get('System:FileSize')
        if isinstance(file_size_str, str):
            if ' bytes' in file_size_str:
                try:
                    metadata['file_size'] = int(file_size_str.replace(' bytes', ''))
                except:
                    pass
            elif ' kB' in file_size_str:
                try:
                    metadata['file_size'] = int(float(file_size_str.replace(' kB', '')) * 1024)
                except:
                    pass
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # Bits per pixel
        if data.get('BitDepth') and data.get('ColorType'):
            bit_depth = int(data.get('BitDepth', 8))
            color_type = data.get('ColorType', '')
            channels = {'Grayscale': 1, 'RGB': 3, 'RGBA': 4, 'Palette': 3}.get(color_type, 1)
            metadata['bits_per_pixel'] = bit_depth * channels
        
        # Text chunks
        text_data = {}
        text_fields = ['Title', 'Author', 'Copyright', 'Software', 'Description',
                      'Comment', 'Creation Time', 'Artist']
        
        for field in text_fields:
            if data.get(field):
                text_data[field.lower().replace(' ', '_')] = data[field]
        
        if text_data:
            metadata['text_chunks'] = text_data
        
        # ICC Profile
        if data.get('ICCProfile') or data.get('ColorSpace'):
            metadata['icc_profile'] = {
                'present': True,
                'color_space': data.get('ColorSpace', data.get('ColorSpaceData'))
            }
        
        # Physical dimensions
        if data.get('PixelUnits'):
            metadata['physical_dimensions'] = {
                'units': 'meters' if data.get('PixelUnits') == 1 else 'unknown',
                'width': data.get('PixelsPerUnitX'),
                'height': data.get('PixelsPerUnitY')
            }
        
        # Transparency
        if data.get('Transparency') or data.get('HasTransparency'):
            metadata['transparency'] = {
                'present': True,
                'type': data.get('Transparency', 'unknown')
            }
        
        return metadata
    
    def _parse_with_chunks(self, filepath: str) -> Dict[str, Any]:
        """Parse PNG using native chunk reading."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                if f.read(8) != b'\x89PNG\r\n\x1a\n':
                    return {'error': 'Not a valid PNG'}
                
                while True:
                    length_data = f.read(4)
                    if len(length_data) < 4:
                        break
                    
                    length = struct.unpack('>I', length_data)[0]
                    chunk_type = f.read(4).decode('latin-1')
                    
                    if chunk_type == 'IEND':
                        break
                    
                    chunk_data = f.read(length)
                    f.read(4)
                    
                    if chunk_type == 'tEXt' and length > 0:
                        if b'\x00' in chunk_data:
                            parts = chunk_data.split(b'\x00', 1)
                            keyword = parts[0].decode('latin-1', errors='replace')
                            text = parts[1].decode('utf-8', errors='replace').strip()
                            if keyword and text:
                                metadata['text_chunks'] = metadata.get('text_chunks', {})
                                metadata['text_chunks'][keyword] = text
                    
                    elif chunk_type == 'iCCP':
                        metadata['icc_profile'] = {'present': True}
                
                from PIL import Image
                with Image.open(filepath) as img:
                    metadata['format'] = 'PNG'
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['color_mode'] = img.mode
                    metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                    
        except Exception as e:
            logger.warning(f"Native PNG parsing failed: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except:
                pass
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        ext = filepath.lower().split('.')[-1]
        return ext in ['png', 'apng']


def parse_png(filepath: str) -> Dict[str, Any]:
    parser = PngParser()
    return parser.parse(filepath)

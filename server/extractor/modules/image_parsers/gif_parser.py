"""
GIF Parser
==========

Extracts metadata from GIF files using native chunk parsing + ExifTool.
GIF supports: Application Extension, Comment Extension, Animation data.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class GifParser(FormatParser):
    """GIF-specific metadata parser."""
    
    FORMAT_NAME = "GIF"
    SUPPORTED_EXTENSIONS = ['.gif', '.gfa']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract GIF metadata."""
        result = {}
        
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            result = self._parse_with_chunks(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'GIF'),
                mode=result.get('color_mode', 'P'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for GIF."""
        metadata = {}
        
        # Core image properties - check multiple key formats
        metadata['format'] = data.get('FileType') or data.get('File:FileType') or 'GIF'
        metadata['width'] = self._parse_int(
            data.get('ImageWidth') or 
            data.get('GIF:ImageWidth') or 
            data.get('File:ImageWidth')
        )
        metadata['height'] = self._parse_int(
            data.get('ImageHeight') or 
            data.get('GIF:ImageHeight') or 
            data.get('File:ImageHeight')
        )
        metadata['color_mode'] = data.get('ColorMode') or data.get('ColorType') or data.get('GIF:ColorType') or 'indexed'
        metadata['bit_depth'] = data.get('BitDepth') or data.get('GIF:BitDepth')
        metadata['color_count'] = data.get('ColorCount') or data.get('GIF:ColorCount')
        
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
        
        # Animation info
        if data.get('LoopCount') or data.get('FrameCount') or data.get('GIF:LoopCount'):
            metadata['animation'] = {
                'animated': (data.get('FrameCount', 1) > 1),
                'frame_count': data.get('FrameCount', 1),
                'loop_count': data.get('LoopCount', data.get('GIF:LoopCount', 0))
            }
        
        if data.get('BackgroundColor') or data.get('GIF:BackgroundColor'):
            metadata['background_color_index'] = data.get('BackgroundColor') or data.get('GIF:BackgroundColor')
        
        if data.get('PixelAspectRatio') or data.get('GIF:PixelAspectRatio'):
            metadata['pixel_aspect'] = data.get('PixelAspectRatio') or data.get('GIF:PixelAspectRatio')
        
        if data.get('Comment'):
            metadata['comment'] = data.get('Comment')
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        return metadata
    
    def _parse_with_chunks(self, filepath: str) -> Dict[str, Any]:
        """Parse GIF using native chunk reading."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                if f.read(6) not in [b'GIF87a', b'GIF89a']:
                    return {'error': 'Not a valid GIF'}
                
                width, height, flags, bg_index, aspect = struct.unpack('<HHBBB', f.read(7))
                
                metadata['format'] = 'GIF89a' if f.read(6)[:6] == b'GIF89a' else 'GIF87a'
                metadata['width'] = width
                metadata['height'] = height
                metadata['megapixels'] = round(width * height / 1_000_000, 2)
                metadata['color_mode'] = 'indexed'
                metadata['bit_depth'] = (flags & 0x07) + 1
                metadata['color_count'] = 2 ** metadata['bit_depth']
                
                from PIL import Image
                with Image.open(filepath) as img:
                    metadata['format'] = img.format
                    metadata['frame_count'] = getattr(img, 'n_frames', 1)
                    if metadata['frame_count'] > 1:
                        metadata['animation'] = {
                            'animated': True,
                            'frame_count': metadata['frame_count']
                        }
                        
        except Exception as e:
            logger.warning(f"Native GIF parsing failed: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        ext = filepath.lower().split('.')[-1]
        return ext in ['gif', 'gfa']


def parse_gif(filepath: str) -> Dict[str, Any]:
    parser = GifParser()
    return parser.parse(filepath)

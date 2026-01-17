"""
WebP Parser
===========

Extracts metadata from WebP files.
WebP supports: EXIF, XMP, ICC Profile in RIFF chunks.

WebP structure:
- RIFF header
- VP8/VP8L/VP9 video data
- Extended format with metadata chunks (EXIF, XMP, ICC)

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class WebpParser(FormatParser):
    """WebP-specific metadata parser."""
    
    FORMAT_NAME = "WebP"
    SUPPORTED_EXTENSIONS = ['.webp']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract WebP metadata."""
        result = {}
        
        # Try ExifTool first
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Fallback to native RIFF parsing
            result = self._parse_with_riff(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'WebP'),
                mode=result.get('color_mode', 'RGBA'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for WebP."""
        metadata = {}
        
        # Core image properties - check multiple key formats
        metadata['format'] = data.get('FileType') or data.get('File:FileType') or 'WebP'
        metadata['width'] = self._parse_int(
            data.get('ImageWidth') or 
            data.get('RIFF:ImageWidth') or
            data.get('WebP:ImageWidth') or 
            data.get('File:ImageWidth')
        )
        metadata['height'] = self._parse_int(
            data.get('ImageHeight') or 
            data.get('RIFF:ImageHeight') or
            data.get('WebP:ImageHeight') or 
            data.get('File:ImageHeight')
        )
        metadata['compression'] = data.get('Compression') or data.get('WebP:Compression') or data.get('WebPType') or data.get('RIFF:VP8Version')
        metadata['bit_depth'] = data.get('BitDepth') or data.get('WebP:BitDepth')
        
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
        
        # Animation (for animated WebP)
        if data.get('FrameCount') or data.get('LoopCount'):
            metadata['animation'] = {
                'animated': data.get('FrameCount', 0) > 1,
                'frame_count': data.get('FrameCount', 1),
                'loop_count': data.get('LoopCount', 0)
            }
        
        # EXIF data
        exif = {}
        exif_fields = ['Make', 'Model', 'DateTime', 'ExposureTime', 'FNumber', 
                      'ISOSpeedRatings', 'FocalLength', 'Flash', 'WhiteBalance']
        
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
        
        return metadata
    
    def _parse_with_riff(self, filepath: str) -> Dict[str, Any]:
        """Parse WebP using RIFF container structure."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                # RIFF header
                riff = f.read(4)
                if riff != b'RIFF':
                    return {'error': 'Not a valid WebP (not RIFF)'}
                
                file_size = struct.unpack('<I', f.read(4))[0]
                fourcc = f.read(4).decode('latin-1')
                
                if fourcc != 'WEBP':
                    return {'error': f'Not WebP format: {fourcc}'}
                
                # Parse chunks
                while f.tell() < 8 + file_size:
                    chunk_type = f.read(4).decode('latin-1')
                    chunk_size = struct.unpack('<I', f.read(4))[0]
                    
                    if chunk_type == 'VP8X':  # Extended format
                        flags = f.read(1)
                        reserved = f.read(3)
                        width = struct.unpack('<I', f.read(3))[0] + 1
                        height = struct.unpack('<I', f.read(3))[0] + 1
                        
                        metadata['format'] = 'WebP (extended)'
                        metadata['width'] = width
                        metadata['height'] = height
                        metadata['megapixels'] = round(width * height / 1_000_000, 2)
                        metadata['animation'] = {
                            'animated': bool(flags[0] & 0x02),
                            'alpha_present': bool(flags[0] & 0x10)
                        }
                        f.read(chunk_size - 10)
                    
                    elif chunk_type == 'VP8 ':  # Lossy
                        metadata['format'] = 'WebP (lossy)'
                        f.read(chunk_size)
                        
                    elif chunk_type == 'VP8L':  # Lossless
                        metadata['format'] = 'WebP (lossless)'
                        f.read(chunk_size)
                    
                    elif chunk_type == 'EXIF':
                        metadata['exif'] = {'present': True, 'size': chunk_size}
                        f.read(chunk_size)
                    
                    elif chunk_type == 'XMP':
                        metadata['xmp'] = {'present': True, 'size': chunk_size}
                        f.read(chunk_size)
                    
                    elif chunk_type == 'ICCP':
                        metadata['icc_profile'] = {'present': True, 'size': chunk_size}
                        f.read(chunk_size)
                    
                    elif chunk_type == 'ANIM':  # Animation config
                        background = struct.unpack('<I', f.read(4))[0]
                        loop_count = struct.unpack('<H', f.read(2))[0]
                        metadata['animation'] = metadata.get('animation', {})
                        metadata['animation']['background_color'] = background
                        metadata['animation']['loop_count'] = loop_count
                        f.read(chunk_size - 6)
                    
                    elif chunk_type == 'ANMF':  # Animation frame
                        f.read(chunk_size)
                    
                    else:
                        # Skip unknown chunk
                        f.read(chunk_size)
                    
                    # Pad to even byte boundary
                    if chunk_size % 2 == 1:
                        f.read(1)
                
                # Add PIL info
                if 'width' not in metadata or 'height' not in metadata:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        metadata['format'] = img.format or 'WebP'
                        metadata['width'] = img.width
                        metadata['height'] = img.height
                        metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                        
        except Exception as e:
            logger.warning(f"Native WebP parsing failed: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real WebP metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a WebP."""
        ext = filepath.lower().split('.')[-1]
        return ext == 'webp'


# Convenience function
def parse_webp(filepath: str) -> Dict[str, Any]:
    """Parse WebP file and return metadata."""
    parser = WebpParser()
    return parser.parse(filepath)

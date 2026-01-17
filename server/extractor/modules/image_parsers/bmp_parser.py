"""
BMP Parser
==========

Extracts metadata from BMP (Windows Bitmap) files.
BMP is a simple format with minimal metadata support:
- File header (width, height, bit depth, compression)
- DIB header (dimensions, color masks)
- Optional color palette
- No EXIF/IPTC/XMP/GPS support natively

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct
import os


class BmpParser(FormatParser):
    """BMP-specific metadata parser using native parsing."""
    
    FORMAT_NAME = "BMP"
    SUPPORTED_EXTENSIONS = ['.bmp', '.dib']
    CAN_USE_EXIFTOOL = True
    
    # BMP compression types
    COMPRESSION_TYPES = {
        0: 'RGB',
        1: 'RLE8',
        2: 'RLE4',
        3: 'BITFIELDS',
        4: 'JPEG',
        5: 'PNG',
        6: 'ALPHABITFIELDS',
        7: 'CMYK',
        8: 'RLE8',
        9: 'RLE4',
        10: 'BITFIELDS',
        11: 'JPEG',
        12: 'PNG',
    }
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract BMP metadata."""
        result = {}
        
        # Try ExifTool first (may have some info)
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Native BMP parsing
            result = self._parse_with_headers(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'BMP'),
                mode=result.get('color_mode', 'RGB'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for BMP."""
        metadata = {}
        
        metadata['format'] = 'BMP'
        metadata['width'] = self._parse_int(
            data.get('ImageWidth') or 
            data.get('File:ImageWidth') or 
            data.get('BMP:ImageWidth')
        )
        metadata['height'] = self._parse_int(
            data.get('ImageHeight') or 
            data.get('File:ImageHeight') or 
            data.get('BMP:ImageHeight')
        )
        metadata['bit_depth'] = data.get('BitDepth') or data.get('File:BitDepth') or data.get('BMP:BitDepth')
        metadata['compression'] = data.get('Compression') or data.get('File:Compression') or data.get('BMP:Compression')
        metadata['bmp_version'] = data.get('BMPVersion') or data.get('File:BMPVersion')
        metadata['planes'] = data.get('Planes') or data.get('File:Planes')
        metadata['image_length'] = data.get('ImageLength') or data.get('File:ImageLength')
        metadata['pixels_per_meter_x'] = data.get('PixelsPerMeterX') or data.get('File:PixelsPerMeterX')
        metadata['pixels_per_meter_y'] = data.get('PixelsPerMeterY') or data.get('File:PixelsPerMeterY')
        
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
            elif ' MB' in file_size_str:
                try:
                    metadata['file_size'] = int(float(file_size_str.replace(' MB', '')) * 1024 * 1024)
                except:
                    pass
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # DPI calculation
        if metadata.get('pixels_per_meter_x'):
            metadata['dpi'] = round(metadata['pixels_per_meter_x'] * 0.0254, 1)
        
        # Color depth to mode mapping
        bit_depth = metadata.get('bit_depth', 24)
        if bit_depth == 32:
            metadata['color_mode'] = 'RGBA'
        elif bit_depth == 24:
            metadata['color_mode'] = 'RGB'
        elif bit_depth == 16:
            metadata['color_mode'] = 'RGB (5-6-5)'
        elif bit_depth == 8:
            metadata['color_mode'] = 'P (256 colors)'
        elif bit_depth == 4:
            metadata['color_mode'] = 'P (16 colors)'
        elif bit_depth == 1:
            metadata['color_mode'] = '1 (monochrome)'
        else:
            metadata['color_mode'] = f'{bit_depth}-bit'
        
        return metadata
    
    def _parse_with_headers(self, filepath: str) -> Dict[str, Any]:
        """Parse BMP using native header reading."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                # BMP File Header (14 bytes)
                signature = f.read(2)
                if signature != b'BM':
                    return {'error': 'Not a valid BMP file'}
                
                file_size = struct.unpack('<I', f.read(4))[0]
                reserved1 = struct.unpack('<H', f.read(2))[0]
                reserved2 = struct.unpack('<H', f.read(2))[0]
                data_offset = struct.unpack('<I', f.read(4))[0]
                
                metadata['format'] = 'BMP'
                metadata['file_size'] = file_size
                metadata['data_offset'] = data_offset
                
                # Read DIB header (BITMAPINFOHEADER or later)
                header_size = struct.unpack('<I', f.read(4))[0]
                
                if header_size == 40:  # BITMAPINFOHEADER
                    width = struct.unpack('<i', f.read(4))[0]
                    height = struct.unpack('<i', f.read(4))[0]
                    planes = struct.unpack('<H', f.read(2))[0]
                    bit_count = struct.unpack('<H', f.read(2))[0]
                    compression = struct.unpack('<I', f.read(4))[0]
                    image_size = struct.unpack('<I', f.read(4))[0]
                    x_pixels_per_meter = struct.unpack('<i', f.read(4))[0]
                    y_pixels_per_meter = struct.unpack('<i', f.read(4))[0]
                    colors_used = struct.unpack('<I', f.read(4))[0]
                    colors_important = struct.unpack('<I', f.read(4))[0]
                    
                    metadata['width'] = abs(width)
                    metadata['height'] = abs(height)
                    metadata['bit_depth'] = bit_count
                    metadata['compression'] = self.COMPRESSION_TYPES.get(compression, f'Unknown ({compression})')
                    metadata['planes'] = planes
                    metadata['image_size'] = image_size
                    metadata['colors_used'] = colors_used if colors_used else 'Maximum'
                    metadata['colors_important'] = colors_important if colors_important else 'All'
                    
                elif header_size == 108 or header_size == 124:  # BITMAPV4/V5 header
                    width = struct.unpack('<i', f.read(4))[0]
                    height = struct.unpack('<i', f.read(4))[0]
                    planes = struct.unpack('<H', f.read(2))[0]
                    bit_count = struct.unpack('<H', f.read(2))[0]
                    compression = struct.unpack('<I', f.read(4))[0]
                    image_size = struct.unpack('<I', f.read(4))[0]
                    x_pixels_per_meter = struct.unpack('<i', f.read(4))[0]
                    y_pixels_per_meter = struct.unpack('<i', f.read(4))[0]
                    alpha_mask = struct.unpack('<I', f.read(4))[0]
                    red_mask = struct.unpack('<I', f.read(4))[0]
                    green_mask = struct.unpack('<I', f.read(4))[0]
                    blue_mask = struct.unpack('<I', f.read(4))[0]
                    
                    metadata['width'] = abs(width)
                    metadata['height'] = abs(height)
                    metadata['bit_depth'] = bit_count
                    metadata['compression'] = self.COMPRESSION_TYPES.get(compression, f'Unknown ({compression})')
                    metadata['image_size'] = image_size
                    
                    # Color masks for V4/V5
                    if red_mask or green_mask or blue_mask or alpha_mask:
                        metadata['color_masks'] = {
                            'red': f'0x{red_mask:08x}',
                            'green': f'0x{green_mask:08x}',
                            'blue': f'0x{blue_mask:08x}',
                            'alpha': f'0x{alpha_mask:08x}' if alpha_mask else 'None'
                        }
                
                else:
                    # Fallback for older headers
                    width = struct.unpack('<I', f.read(4))[0]
                    height = struct.unpack('<I', f.read(4))[0]
                    planes = struct.unpack('<H', f.read(2))[0]
                    bit_count = struct.unpack('<H', f.read(2))[0]
                    
                    metadata['width'] = width
                    metadata['height'] = height
                    metadata['bit_depth'] = bit_count
                    metadata['planes'] = planes
                
                # Calculate megapixels
                if metadata.get('width') and metadata.get('height'):
                    mp = (metadata['width'] * metadata['height']) / 1_000_000
                    metadata['megapixels'] = round(mp, 2)
                
                # Color depth to mode
                bit_depth = metadata.get('bit_depth', 24)
                if bit_depth == 32:
                    metadata['color_mode'] = 'RGBA'
                elif bit_depth == 24:
                    metadata['color_mode'] = 'RGB'
                elif bit_depth == 16:
                    metadata['color_mode'] = 'RGB (5-6-5)'
                elif bit_depth == 8:
                    metadata['color_mode'] = 'P (256 colors)'
                elif bit_depth == 4:
                    metadata['color_mode'] = 'P (16 colors)'
                elif bit_depth == 1:
                    metadata['color_mode'] = '1 (monochrome)'
                else:
                    metadata['color_mode'] = f'{bit_depth}-bit'
                
                # Resolution
                if 'x_pixels_per_meter' in metadata:
                    metadata['dpi'] = round(metadata['x_pixels_per_meter'] * 0.0254, 1) if metadata['x_pixels_per_meter'] else None
                
        except Exception as e:
            logger.warning(f"Native BMP parsing failed: {e}")
        
        return metadata
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except:
                pass
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real BMP metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is a BMP."""
        ext = filepath.lower().split('.')[-1]
        return ext in ['bmp', 'dib']


# Convenience function
def parse_bmp(filepath: str) -> Dict[str, Any]:
    """Parse BMP file and return metadata."""
    parser = BmpParser()
    return parser.parse(filepath)

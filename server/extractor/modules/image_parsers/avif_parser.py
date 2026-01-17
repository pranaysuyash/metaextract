"""
AVIF Parser
===========

Extracts metadata from AVIF files.
AVIF supports: EXIF, XMP, ICC Profile in ISOBMFF/HEIF boxes.

AVIF structure:
- ISOBMFF/HEIF container (ftyp, moov, mdat boxes)
- Image items (av01)
- Metadata boxes (Exif, XMP, iprp)
- Extended format supports HDR, alpha, animation

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata
from typing import Dict, Any, Optional, List
import struct


class AvifParser(FormatParser):
    """AVIF-specific metadata parser."""
    
    FORMAT_NAME = "AVIF"
    SUPPORTED_EXTENSIONS = ['.avif']
    CAN_USE_EXIFTOOL = True
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract AVIF metadata."""
        result = {}
        
        # Try ExifTool first
        exiftool_data = self._run_exiftool(filepath)
        if exiftool_data:
            result = self._process_exiftool_output(exiftool_data)
        else:
            # Fallback to native ISOBMFF parsing
            result = self._parse_with_isobmff(filepath)
        
        # Add computed metadata
        if result.get('width') and result.get('height'):
            computed = compute_all_metadata(
                filepath=filepath,
                width=result.get('width', 0),
                height=result.get('height', 0),
                format_name=result.get('format', 'AVIF'),
                mode=result.get('color_mode', 'RGBA'),
                exif=result.get('exif', {}),
                gps=result.get('gps', {}),
                icc_profile=result.get('icc_profile', {}),
                file_size=result.get('file_size')
            )
            result.update(computed)
        
        return result
    
    def _process_exiftool_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ExifTool output for AVIF."""
        metadata = {}
        
        # Core image properties
        metadata['format'] = data.get('FileType') or data.get('File:FileType') or 'AVIF'
        metadata['width'] = self._parse_int(
            data.get('ImageWidth') or 
            data.get('AVIF:ImageWidth') or
            data.get('File:ImageWidth')
        )
        metadata['height'] = self._parse_int(
            data.get('ImageHeight') or 
            data.get('AVIF:ImageHeight') or 
            data.get('File:ImageHeight')
        )
        metadata['bit_depth'] = data.get('BitDepth') or data.get('AVIF:BitDepth')
        
        # Color space and alpha
        metadata['color_mode'] = data.get('ColorMode') or data.get('AVIF:ColorMode') or 'RGBA'
        metadata['has_alpha'] = data.get('HasAlpha') or data.get('AVIF:HasAlpha') or False
        
        # HDR information
        if data.get('HDR') or data.get('AVIF:HDR'):
            metadata['hdr'] = {
                'enabled': True,
                'transfer_function': data.get('TransferFunction') or data.get('AVIF:TransferFunction'),
                'color_primaries': data.get('ColorPrimaries') or data.get('AVIF:ColorPrimaries')
            }
        
        # Animation
        if data.get('FrameCount') and data.get('FrameCount') > 1:
            metadata['animation'] = {
                'animated': True,
                'frame_count': data.get('FrameCount'),
                'loop_count': data.get('LoopCount', 0)
            }
        
        # File size
        file_size_str = data.get('FileSize') or data.get('System:FileSize')
        if isinstance(file_size_str, str):
            metadata['file_size'] = self._parse_file_size(file_size_str)
        
        # Calculate megapixels
        if metadata.get('width') and metadata.get('height'):
            mp = (metadata['width'] * metadata['height']) / 1_000_000
            metadata['megapixels'] = round(mp, 2)
        
        # EXIF data
        exif = {}
        exif_fields = ['Make', 'Model', 'DateTime', 'ExposureTime', 'FNumber', 
                      'ISOSpeedRatings', 'FocalLength', 'Flash', 'WhiteBalance',
                      'ISOSpeedRatings', 'ExposureCompensation']
        
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
        
        # Compression type
        if data.get('CodecID') or data.get('AVIF:CodecID'):
            metadata['compression'] = data.get('CodecID') or data.get('AVIF:CodecID')
        
        return metadata
    
    def _parse_with_isobmff(self, filepath: str) -> Dict[str, Any]:
        """Parse AVIF using ISOBMFF container structure."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                # Read ftyp box
                ftyp = self._read_box_header(f)
                if ftyp.get('box_type') != b'ftyp':
                    return {'error': 'Not a valid AVIF (missing ftyp)'}
                
                # Parse file type brand
                major_brand = ftyp.get('major_brand', b'').decode('latin-1')
                compatible_brands = ftyp.get('compatible_brands', [])
                
                metadata['format'] = 'AVIF'
                metadata['brands'] = [major_brand] + [b.decode('latin-1') for b in compatible_brands]
                
                # Parse remaining boxes
                while True:
                    box = self._read_box_header(f)
                    if box is None:
                        break
                    
                    box_type = box.get('box_type')
                    box_size = box.get('box_size', 0)
                    
                    if box_type == b'moov':
                        moov_data = self._parse_moov_box(f, box_size - 8)
                        metadata.update(moov_data)
                        f.read(box_size - 8)
                    
                    elif box_type == b'Exif':
                        metadata['exif'] = {'present': True, 'size': box_size}
                        f.read(box_size - 8)
                    
                    elif box_type == b'XMP':
                        metadata['xmp'] = {'present': True, 'size': box_size}
                        f.read(box_size - 8)
                    
                    elif box_type == b'iprp':
                        f.read(box_size - 8)
                    
                    else:
                        f.read(box_size - 8)
                
                # Add PIL info as fallback
                if 'width' not in metadata or 'height' not in metadata:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        metadata['format'] = img.format or 'AVIF'
                        metadata['width'] = img.width
                        metadata['height'] = img.height
                        metadata['megapixels'] = round(img.width * img.height / 1_000_000, 2)
                        metadata['has_alpha'] = 'A' in (img.mode or '')
                        
        except Exception as e:
            logger.warning(f"Native AVIF parsing failed: {e}")
        
        return metadata
    
    def _read_box_header(self, f) -> Optional[Dict[str, Any]]:
        """Read ISOBMFF box header."""
        try:
            pos = f.tell()
            if pos >= 100_000_000:
                return None
                
            size_bytes = f.read(4)
            if len(size_bytes) < 4:
                return None
                
            box_size = struct.unpack('>I', size_bytes)[0]
            box_type = f.read(4)
            
            if box_size == 1:
                # Extended size
                extended_size = struct.unpack('>Q', f.read(8))[0]
                box_size = extended_size
            elif box_size == 0:
                # Box extends to end of file
                box_size = 0xFFFFFFFF
                
            return {
                'box_size': box_size,
                'box_type': box_type,
                'data_offset': f.tell()
            }
        except:
            return None
    
    def _parse_moov_box(self, f, size: int) -> Dict[str, Any]:
        """Parse moov box for dimensions and track info."""
        metadata = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box_header(f)
            if box is None:
                break
                
            box_type = box.get('box_type')
            box_size = box.get('box_size', 0)
            
            if box_type == b'trak':
                trak_data = self._parse_trak_box(f, box_size - 8)
                if 'width' in trak_data:
                    metadata['width'] = trak_data['width']
                if 'height' in trak_data:
                    metadata['height'] = trak_data['height']
                f.read(box_size - 8)
            
            elif box_type == b'mvhd':
                f.read(box_size - 8)
            
            else:
                f.read(box_size - 8)
        
        return metadata
    
    def _parse_trak_box(self, f, size: int) -> Dict[str, Any]:
        """Parse trak box for dimensions."""
        result = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box_header(f)
            if box is None:
                break
                
            box_type = box.get('box_type')
            box_size = box.get('box_size', 0)
            
            if box_type == b'mdia':
                mdia_data = self._parse_mdia_box(f, box_size - 8)
                result.update(mdia_data)
                f.read(box_size - 8)
            
            else:
                f.read(box_size - 8)
        
        return result
    
    def _parse_mdia_box(self, f, size: int) -> Dict[str, Any]:
        """Parse mdia box."""
        result = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box_header(f)
            if box is None:
                break
                
            box_type = box.get('box_type')
            box_size = box.get('box_size', 0)
            
            if box_type == b'hdlr':
                f.read(box_size - 8)
            
            elif box_type == b'minf':
                minf_data = self._parse_minf_box(f, box_size - 8)
                result.update(minf_data)
                f.read(box_size - 8)
            
            else:
                f.read(box_size - 8)
        
        return result
    
    def _parse_minf_box(self, f, size: int) -> Dict[str, Any]:
        """Parse minf box."""
        result = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box_header(f)
            if box is None:
                break
                
            box_type = box.get('box_type')
            box_size = box.get('box_size', 0)
            
            if box_type == b'stbl':
                stbl_data = self._parse_stbl_box(f, box_size - 8)
                result.update(stbl_data)
                f.read(box_size - 8)
            
            else:
                f.read(box_size - 8)
        
        return result
    
    def _parse_stbl_box(self, f, size: int) -> Dict[str, Any]:
        """Parse stbl box for sample dimensions."""
        result = {}
        end_pos = f.tell() + size
        
        while f.tell() < end_pos:
            box = self._read_box_header(f)
            if box is None:
                break
                
            box_type = box.get('box_type')
            box_size = box.get('box_size', 0)
            
            if box_type == b'stsd':
                stsd_data = self._parse_stsd_box(f, box_size - 8)
                result.update(stsd_data)
                f.read(box_size - 8)
            
            else:
                f.read(box_size - 8)
        
        return result
    
    def _parse_stsd_box(self, f, size: int) -> Dict[str, Any]:
        """Parse stsd box for visual sample entry."""
        result = {}
        end_pos = f.tell() + size
        
        try:
            f.read(4)  # entry_count
            while f.tell() < end_pos:
                box = self._read_box_header(f)
                if box is None:
                    break
                    
                box_type = box.get('box_type')
                box_size = box.get('box_size', 0)
                
                if box_type == b'av01':
                    data = self._parse_av01_entry(f, box_size - 8)
                    result.update(data)
                    f.read(box_size - 8)
                
                else:
                    f.read(box_size - 8)
        except:
            pass
        
        return result
    
    def _parse_av01_entry(self, f, size: int) -> Dict[str, Any]:
        """Parse AV1 visual sample entry."""
        result = {}
        start_pos = f.tell()
        
        try:
            f.read(6)  # reserved
            f.read(2)  # data_reference_index
            f.read(4)  # reserved
            f.read(4)  # reserved
            f.read(2)  # width
            f.read(2)  # height
            
            f.read(4)  # horizresolution
            f.read(4)  # vertresolution
            f.read(4)  # reserved
            f.read(2)  # frame_count
            
            f.read(32)  # compressorname
            f.read(2)  # reserved
            f.read(2)  # reserved
            
            f.read(4)  # pre_defined
            f.read(4)  # pre_defined
            f.read(4)  # pre_defined
            
            # Now in pixel structure
            if f.tell() < start_pos + size - 8:
                header = f.read(4)
                if header == b'\x00\x00\x00\x00':
                    pass
        
        except:
            pass
        
        return result
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer value."""
        if isinstance(value, (int, float)):
            return int(value)
        return None
    
    def _parse_file_size(self, value: str) -> Optional[int]:
        """Parse file size string."""
        try:
            if ' bytes' in value:
                return int(value.replace(' bytes', ''))
            elif ' kB' in value:
                return int(float(value.replace(' kB', '')) * 1024)
            elif ' MB' in value:
                return int(float(value.replace(' MB', '')) * 1024 * 1024)
        except:
            pass
        return None
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real AVIF metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is an AVIF."""
        ext = filepath.lower().split('.')[-1]
        return ext == 'avif'


# Convenience function
def parse_avif(filepath: str) -> Dict[str, Any]:
    """Parse AVIF file and return metadata."""
    parser = AvifParser()
    return parser.parse(filepath)

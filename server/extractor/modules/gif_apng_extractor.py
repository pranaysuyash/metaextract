#!/usr/bin/env python3
"""
Animated GIF and APNG Extractor
Extracts comprehensive metadata from animated GIF and APNG files.
"""

import logging
import struct
import zlib
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


GIF89A_SIGNATURE = b'GIF89a'
GIF87A_SIGNATURE = b'GIF87a'

NETSCAPE_EXT = b'NETSCAPE2.0'
APPLE_IMAGE_DESCRIPTOR = b'acTL'

COMMENT_EXT = 0xFE
GRAPHICS_EXT = 0xF9
PLAIN_TEXT_EXT = 0x01
APPLICATION_EXT = 0xFF

TRANSPARENCY_INDEX_FLAG = 0x01
DISPOSAL_METHODS = {
    0: 'none',
    1: 'do_not_dispose',
    2: 'restore_to_background',
    3: 'restore_to_previous'
}


class GIFExtractor:
    """
    Comprehensive GIF and APNG metadata extractor.
    Supports GIF89a, GIF87a, and animated PNG (APNG) formats.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.file_size = 0
        self.is_valid_gif = False
        self.is_animated = False
        self.gif_info: Dict[str, Any] = {}
        self.frames: List[Dict[str, Any]] = []
        self.loop_count: int = 0
        self.global_color_table: Optional[List[int]] = None
        self.application_data: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Main entry point - parse GIF/APNG file"""
        try:
            file_path = Path(self.filepath)
            if not file_path.exists():
                return {"error": "File not found", "success": False}
            
            self.file_size = file_path.stat().st_size
            
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 10:
                return {"error": "File too small", "success": False}
            
            signature = self.file_data[:6]
            if signature not in (GIF89A_SIGNATURE, GIF87A_SIGNATURE):
                return {"error": "Not a valid GIF file", "success": False}
            
            self.is_valid_gif = True
            self.gif_info["version"] = signature.decode('ascii')
            
            self._parse_header()
            self._parse_blocks()
            self._build_result()
            
            return self.gif_info
            
        except Exception as e:
            logger.error(f"Error parsing GIF: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_header(self):
        """Parse GIF header and logical screen descriptor"""
        if not self.file_data or len(self.file_data) < 10:
            return
        
        offset = 6
        width, height = struct.unpack('<HH', self.file_data[offset:offset + 4])
        offset += 4
        
        self.gif_info["logical_screen_width"] = width
        self.gif_info["logical_screen_height"] = height
        
        packed = self.file_data[offset]
        offset += 1
        
        self.gif_info["global_color_table_flag"] = (packed & 0x80) != 0
        self.gif_info["color_resolution"] = ((packed >> 4) & 0x07) + 1
        self.gif_info["sort_flag"] = (packed & 0x08) != 0
        self.gif_info["size_of_global_color_table"] = 2 ** ((packed & 0x07) + 1)
        
        bg_color_index = self.file_data[offset]
        self.gif_info["background_color_index"] = bg_color_index
        offset += 1
        
        pixel_aspect_ratio = self.file_data[offset]
        self.gif_info["pixel_aspect_ratio"] = pixel_aspect_ratio
        offset += 1
        
        if self.gif_info["global_color_table_flag"]:
            table_size = self.gif_info["size_of_global_color_table"]
            table_end = offset + 3 * table_size
            if table_end <= len(self.file_data):
                self.global_color_table = []
                for i in range(table_size):
                    r = self.file_data[offset + i * 3]
                    g = self.file_data[offset + i * 3 + 1]
                    b = self.file_data[offset + i * 3 + 2]
                    self.global_color_table.append((r, g, b))
    
    def _parse_blocks(self):
        """Parse all blocks in the GIF file"""
        if not self.file_data:
            return
        
        offset = 0
        signature = self.file_data[:6]
        if signature == GIF89A_SIGNATURE:
            offset = 10
        else:
            offset = 10
        
        if self.gif_info.get("global_color_table_flag"):
            table_size = self.gif_info["size_of_global_color_table"]
            offset += 3 * table_size
        
        frame_count = 0
        while offset < len(self.file_data):
            block_type = self.file_data[offset]
            offset += 1
            
            if block_type == 0x21:
                ext_type = self.file_data[offset]
                offset += 1
                offset = self._parse_extension(ext_type, offset)
            elif block_type == 0x2C:
                offset = self._parse_image_descriptor(offset)
                frame_count += 1
            elif block_type == 0x3B:
                break
            else:
                break
        
        self.gif_info["frame_count"] = frame_count
        self.is_animated = frame_count > 1
    
    def _parse_extension(self, ext_type: int, offset: int) -> int:
        """Parse GIF extension blocks"""
        if ext_type == 0xF9:
            return self._parse_graphics_extension(offset)
        elif ext_type == 0xFF:
            return self._parse_application_extension(offset)
        elif ext_type == 0xFE:
            return self._parse_comment_extension(offset)
        else:
            return self._skip_sub_blocks(offset)
    
    def _parse_graphics_extension(self, offset: int) -> int:
        """Parse graphics control extension"""
        block_size = self.file_data[offset]
        offset += 1
        
        if block_size != 4:
            return self._skip_sub_blocks(offset)
        
        packed = self.file_data[offset]
        disposal = (packed >> 2) & 0x07
        self.gif_info["disposal_method"] = DISPOSAL_METHODS.get(disposal, 'unknown')
        
        transparency_flag = (packed & 0x01) != 0
        self.gif_info["has_transparency"] = transparency_flag
        
        offset += 1
        
        delay_time = struct.unpack('<H', self.file_data[offset:offset + 2])[0]
        if 'frame_delays' not in self.gif_info:
            self.gif_info["frame_delays"] = []
        self.gif_info["frame_delays"].append(delay_time * 10)
        offset += 2
        
        transparent_color_index = self.file_data[offset]
        self.gif_info["transparent_color_index"] = transparent_color_index
        offset += 1
        
        return offset
    
    def _parse_application_extension(self, offset: int) -> int:
        """Parse application extension (NETSCAPE for looping, etc.)"""
        block_size = self.file_data[offset]
        offset += 1
        
        if block_size != 11:
            return self._skip_sub_blocks(offset)
        
        application_id = self.file_data[offset:offset + 11]
        offset += 11
        
        if application_id == NETSCAPE_EXT:
            sub_block_size = self.file_data[offset]
            offset += 1
            
            if sub_block_size == 3:
                offset += 1
                loop_count = struct.unpack('<H', self.file_data[offset:offset + 2])[0]
                self.loop_count = loop_count
                self.gif_info["loop_count"] = loop_count
                offset += 2
                return offset
        
        return self._skip_sub_blocks(offset)
    
    def _parse_comment_extension(self, offset: int) -> int:
        """Parse comment extension"""
        comment_data = bytearray()
        while offset < len(self.file_data):
            sub_block_size = self.file_data[offset]
            offset += 1
            
            if sub_block_size == 0:
                break
            
            comment_data.extend(self.file_data[offset:offset + sub_block_size])
            offset += sub_block_size
        
        if comment_data:
            try:
                comment = comment_data.decode('ascii', errors='replace')
                if 'comments' not in self.gif_info:
                    self.gif_info["comments"] = []
                self.gif_info["comments"].append(comment)
            except:
                pass
        
        return offset
    
    def _parse_image_descriptor(self, offset: int) -> int:
        """Parse image descriptor and local color table"""
        left = struct.unpack('<H', self.file_data[offset:offset + 2])[0]
        top = struct.unpack('<H', self.file_data[offset + 2:offset + 4])[0]
        img_width = struct.unpack('<H', self.file_data[offset + 4:offset + 6])[0]
        img_height = struct.unpack('<H', self.file_data[offset + 6:offset + 8])[0]
        offset += 8
        
        packed = self.file_data[offset]
        offset += 1
        
        has_local_color_table = (packed & 0x80) != 0
        interlaced = (packed & 0x40) != 0
        
        local_color_table = None
        if has_local_color_table:
            table_size = 2 ** ((packed & 0x07) + 1)
            table_end = offset + 3 * table_size
            if table_end <= len(self.file_data):
                local_color_table = []
                for i in range(table_size):
                    r = self.file_data[offset + i * 3]
                    g = self.file_data[offset + i * 3 + 1]
                    b = self.file_data[offset + i * 3 + 2]
                    local_color_table.append((r, g, b))
        
        frame_info = {
            "left": left,
            "top": top,
            "width": img_width,
            "height": img_height,
            "interlaced": interlaced,
            "has_local_color_table": has_local_color_table
        }
        self.frames.append(frame_info)
        
        offset = self._skip_sub_blocks(offset)
        
        return offset
    
    def _skip_sub_blocks(self, offset: int) -> int:
        """Skip sub-blocks in GIF format"""
        while offset < len(self.file_data):
            sub_block_size = self.file_data[offset]
            offset += 1
            
            if sub_block_size == 0:
                break
            
            offset += sub_block_size
        
        return offset
    
    def _build_result(self):
        """Build the final result dictionary"""
        self.gif_info["is_valid_gif"] = self.is_valid_gif
        self.gif_info["is_animated"] = self.is_animated
        self.gif_info["loop_count"] = self.loop_count
        self.gif_info["total_frames"] = len(self.frames)
        self.gif_info["file_size_bytes"] = self.file_size
        
        if self.frames:
            total_pixels = sum(f["width"] * f["height"] for f in self.frames)
            self.gif_info["total_pixels_all_frames"] = total_pixels
            
            if self.is_animated and self.gif_info.get("frame_delays"):
                total_duration = sum(self.gif_info["frame_delays"])
                self.gif_info["total_duration_ms"] = total_duration
        
        if self.global_color_table:
            self.gif_info["global_color_count"] = len(self.global_color_table)
        
        self.gif_info["success"] = True


class APNGExtractor:
    """
    APNG (Animated PNG) metadata extractor.
    Extends basic PNG parsing with animation control data.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file_data: Optional[bytes] = None
        self.is_valid_apng = False
        self.png_info: Dict[str, Any] = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse APNG file"""
        try:
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            
            if len(self.file_data) < 8:
                return {"error": "File too small", "success": False}
            
            if self.file_data[:8] != b'\\x89PNG\\r\\n\\x1a\\n':
                return {"error": "Not a valid PNG file", "success": False}
            
            return self._parse_chunks()
            
        except Exception as e:
            logger.error(f"Error parsing APNG: {e}")
            return {"error": str(e), "success": False}
    
    def _parse_chunks(self) -> Dict[str, Any]:
        """Parse PNG chunks"""
        offset = 8
        frame_count = 0
        animation_data: Dict[str, Any] = {}
        
        while offset < len(self.file_data):
            if offset + 8 > len(self.file_data):
                break
            
            length = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
            chunk_type = self.file_data[offset + 4:offset + 8]
            offset += 8
            
            if chunk_type == b'acTL':
                if length >= 8:
                    frame_count = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
                    num_plays = struct.unpack('>I', self.file_data[offset + 4:offset + 8])[0]
                    animation_data["frame_count"] = frame_count
                    animation_data["num_plays"] = num_plays
                    animation_data["is_animated"] = frame_count > 1
            
            elif chunk_type == b'fcTL':
                if length >= 26:
                    sequence = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
                    width = struct.unpack('>I', self.file_data[offset + 4:offset + 8])[0]
                    height = struct.unpack('>I', self.file_data[offset + 8:offset + 12])[0]
                    offset_x = struct.unpack('>H', self.file_data[offset + 12:offset + 14])[0]
                    offset_y = struct.unpack('>H', self.file_data[offset + 14:offset + 16])[0]
                    
                    if 'frames' not in animation_data:
                        animation_data["frames"] = []
                    
                    animation_data["frames"].append({
                        "sequence": sequence,
                        "width": width,
                        "height": height,
                        "offset_x": offset_x,
                        "offset_y": offset_y
                    })
            
            elif chunk_type == b'fdAT':
                if length >= 4:
                    sequence = struct.unpack('>I', self.file_data[offset:offset + 4])[0]
                    if 'frame_delays' not in animation_data:
                        animation_data["frame_delays"] = []
                    animation_data["frame_delays"].append(sequence)
            
            offset += length
            if offset + 4 > len(self.file_data):
                break
            offset += 4
        
        animation_data["success"] = True
        return animation_data

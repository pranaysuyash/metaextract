"""
GIF Parser
==========

Extracts metadata from GIF files using native chunk parsing + ExifTool.
GIF supports: Application Extension, Comment Extension, Animation data.

Plus computed metadata: quality analysis, AI analysis, hashes, forensic, etc.

Added in this version:
- Per-frame delays and disposal methods
- Source attribution from comments/app extensions
- Complexity/entropy analysis
- Frame deduplication detection
- Color palette extraction per frame
"""

from . import FormatParser, logger
from .computed_metadata import compute_all_metadata, extract_entropy_analysis
from typing import Dict, Any, Optional, List, Tuple
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
        
        # Add entropy analysis for complexity
        entropy = extract_entropy_analysis(filepath)
        if entropy:
            result['complexity_analysis'] = entropy
        
        # Add frame deduplication analysis
        if result.get('animation', {}).get('frame_count', 0) > 1:
            dup_result = self._detect_frame_duplicates(filepath)
            if dup_result:
                result['frame_analysis'] = dup_result
        
        # Add source attribution if available
        if 'comment' in result:
            source_attr = self._extract_source_attribution(result['comment'])
            if source_attr:
                result['source_attribution'] = source_attr
        
        return result
    
    def _detect_frame_duplicates(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Detect duplicate and near-duplicate frames in GIF.
        
        Uses perceptual hashing to compare frames and identify:
        - Exact duplicates
        - Near-duplicates (threshold-based)
        - Unique frames
        - Key frames (representative of similar frames)
        """
        try:
            from PIL import Image
            import imagehash
            
            with Image.open(filepath) as img:
                frame_count = getattr(img, 'n_frames', 1)
                
                if frame_count <= 1:
                    return None
                
                # Extract perceptual hashes for each frame
                frame_hashes = []
                unique_hashes = set()
                
                for i in range(frame_count):
                    img.seek(i)
                    
                    # Get frame as hash
                    frame_hash = imagehash.phash(img.convert('RGB'))
                    frame_hashes.append({
                        'frame_index': i,
                        'hash': str(frame_hash),
                        'hash_object': frame_hash
                    })
                    unique_hashes.add(str(frame_hash))
                
                # Compare frames to find duplicates
                duplicate_groups = []
                used_frames = set()
                
                for i, frame in enumerate(frame_hashes):
                    if i in used_frames:
                        continue
                    
                    group = [i]
                    for j in range(i + 1, len(frame_hashes)):
                        if j in used_frames:
                            continue
                        
                        # Calculate Hamming distance between hashes
                        hash1 = frame['hash_object']
                        hash2 = frame_hashes[j]['hash_object']
                        distance = hash1 - hash2
                        
                        # Threshold for "near duplicate" (typically 5-10 for phash)
                        if distance <= 5:
                            group.append(j)
                            used_frames.add(j)
                    
                    if len(group) > 1:
                        duplicate_groups.append({
                            'representative_frame': group[0],
                            'duplicate_frames': group[1:],
                            'similarity_score': round(100 - (distance / len(hash1.hash) * 100), 1) if 'distance' in locals() else 100.0
                        })
                    
                    used_frames.add(i)
                
                # Identify key frames (first frame of each unique group)
                key_frames = []
                seen_hashes = set()
                for frame in frame_hashes:
                    frame_hash_str = frame['hash']
                    if frame_hash_str not in seen_hashes:
                        key_frames.append(frame['frame_index'])
                        seen_hashes.add(frame_hash_str)
                
                # Calculate statistics
                unique_frame_count = len(unique_hashes)
                duplicate_frame_count = frame_count - unique_frame_count
                duplication_ratio = round(duplicate_frame_count / frame_count * 100, 1) if frame_count > 0 else 0
                
                return {
                    'total_frames': frame_count,
                    'unique_frames': unique_frame_count,
                    'duplicate_frames': duplicate_frame_count,
                    'duplication_ratio_percent': duplication_ratio,
                    'duplicate_groups': duplicate_groups,
                    'key_frames': key_frames,
                    'key_frame_count': len(key_frames),
                    'analysis_method': 'perceptual_hash',
                    'near_duplicate_threshold': 5,
                    'recommendation': self._get_duplicate_recommendation(duplication_ratio, frame_count)
                }
                
        except ImportError:
            logger.debug("imagehash not available for frame deduplication")
            return {
                'error': 'imagehash library required',
                'recommendation': 'Install imagehash for frame analysis'
            }
        except Exception as e:
            logger.debug(f"Frame deduplication failed: {e}")
            return {
                'error': str(e)
            }
    
    def _get_duplicate_recommendation(self, duplication_ratio: float, frame_count: int) -> str:
        """Get optimization recommendation based on duplication ratio."""
        if duplication_ratio > 50:
            return "High duplication detected. Consider removing duplicate frames for smaller file size."
        elif duplication_ratio > 25:
            return "Moderate duplication. Review key frames for optimization opportunities."
        elif duplication_ratio > 10:
            return "Low duplication. Animation appears well-optimized."
        else:
            return "Minimal duplication. No action needed."
    
    def _extract_frame_color_palettes(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Extract color palette information for each frame.
        
        Returns palette statistics and per-frame palette data.
        """
        try:
            from PIL import Image
            import numpy as np
            
            with Image.open(filepath) as img:
                frame_count = getattr(img, 'n_frames', 1)
                
                if frame_count <= 0:
                    return None
                
                palettes = []
                unique_colors = set()
                
                for i in range(min(frame_count, 50)):  # Limit to 50 frames for performance
                    img.seek(i)
                    
                    # Get palette if indexed
                    if img.mode == 'P':
                        palette = img.getpalette()
                        if palette:
                            # Extract unique colors from palette
                            frame_colors = []
                            for j in range(0, len(palette), 3):
                                if j + 2 < len(palette):
                                    color = (palette[j], palette[j+1], palette[j+2])
                                    frame_colors.append(color)
                                    unique_colors.add(color)
                            
                            palettes.append({
                                'frame_index': i,
                                'color_count': len([c for c in frame_colors if c != (0, 0, 0)]),
                                'unique_colors': len(set(frame_colors))
                            })
                    else:
                        # For non-indexed frames, sample colors
                        img_rgb = img.convert('RGB')
                        colors = img_rgb.getcolors(maxcolors=256)
                        if colors:
                            palette_info = sorted(colors, reverse=True)[:10]
                            palettes.append({
                                'frame_index': i,
                                'top_colors': [c[1] for c in palette_info],
                                'color_count': sum(c[0] for c in colors)
                            })
                
                return {
                    'frames_analyzed': len(palettes),
                    'total_unique_colors': len(unique_colors),
                    'frame_palettes': palettes,
                    'average_colors_per_frame': round(len(unique_colors) / len(palettes), 1) if palettes else 0
                }
                
        except Exception as e:
            logger.debug(f"Palette extraction failed: {e}")
            return None
    
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
            elif ' MB' in file_size_str:
                try:
                    metadata['file_size'] = int(float(file_size_str.replace(' MB', '')) * 1024 * 1024)
                except:
                    pass
        
        # Animation info
        frame_count = data.get('FrameCount') or data.get('GIF:FrameCount') or 1
        loop_count = data.get('LoopCount') or data.get('GIF:LoopCount') or 0
        
        if frame_count > 1 or loop_count > 0:
            frame_delays = data.get('FrameDelays') or data.get('GIF:FrameDelays') or []
            metadata['animation'] = {
                'animated': frame_count > 1,
                'frame_count': frame_count,
                'loop_count': loop_count,
                'loop_infinite': loop_count == 0,
                'total_duration_ms': self._calculate_total_duration(frame_delays),
                'average_fps': self._calculate_fps(frame_count, frame_delays),
                'frame_delays_ms': frame_delays if frame_delays else [100] * frame_count,
                'disposal_methods': self._extract_disposal_methods(data)
            }
        else:
            metadata['animation'] = {
                'animated': False,
                'frame_count': 1,
                'loop_count': 0,
                'loop_infinite': False,
                'total_duration_ms': 0,
                'average_fps': 0,
                'frame_delays_ms': [],
                'disposal_methods': []
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
        
        # Source attribution from application extension
        if data.get('Application') or data.get('GIF:Application'):
            metadata['source_attribution'] = {
                'source': data.get('Application') or data.get('GIF:Application'),
                'extraction_confidence': 'high'
            }
        
        return metadata
    
    def _calculate_total_duration(self, frame_delays: List[int]) -> int:
        """Calculate total animation duration from frame delays in centiseconds."""
        if not frame_delays:
            return 0
        return sum(frame_delays) * 10  # Convert centiseconds to milliseconds
    
    def _calculate_fps(self, frame_count: int, frame_delays: List[int]) -> float:
        """Calculate average FPS from frame count and delays."""
        if frame_count <= 1 or not frame_delays:
            return 0.0
        total_ms = sum(frame_delays) * 10
        if total_ms == 0:
            return 0.0
        return round(frame_count / (total_ms / 1000), 1)
    
    def _extract_disposal_methods(self, data: Dict[str, Any]) -> List[str]:
        """Extract disposal methods from ExifTool data."""
        disposal_methods = []
        disposal_map = {
            0: 'none',
            1: 'restore_to_background',
            2: 'restore_to_previous',
            3: 'restore_to_undetermined'
        }
        
        gif_disposal = data.get('GIF:DisposalMethod') or data.get('DisposalMethod')
        if gif_disposal:
            if isinstance(gif_disposal, list):
                for d in gif_disposal:
                    disposal_methods.append(disposal_map.get(d, 'unknown'))
            else:
                disposal_methods.append(disposal_map.get(gif_disposal, 'unknown'))
        else:
            # Default for most GIFs
            disposal_methods = ['restore_to_background'] * data.get('FrameCount', 1)
        
        return disposal_methods
    
    def _extract_source_attribution(self, comment: str) -> Optional[Dict[str, Any]]:
        """Extract source attribution from comment text."""
        if not comment:
            return None
        
        source = None
        confidence = 'low'
        
        # Check for known sources in comment
        giphy_patterns = ['giphy', 'powered by giphy', 'giphy.com']
        tenor_patterns = ['tenor', 'tenor.com']
        tenor_source = any(p in comment.lower() for p in tenor_patterns)
        if tenor_source:
            source = 'Tenor'
            confidence = 'high'
        
        giphy_source = any(p in comment.lower() for p in giphy_patterns)
        if giphy_source:
            source = 'GIPHY'
            confidence = 'high'
        
        # Check for URL patterns
        if 'giphy.com' in comment.lower():
            source = 'GIPHY'
            confidence = 'high'
        elif 'tenor.com' in comment.lower():
            source = 'Tenor'
            confidence = 'high'
        
        if source:
            return {
                'source': source,
                'extraction_confidence': confidence
            }
        
        return None
    
    def _parse_with_chunks(self, filepath: str) -> Dict[str, Any]:
        """Parse GIF using native chunk reading."""
        metadata = {}
        
        try:
            with open(filepath, 'rb') as f:
                header = f.read(6)
                if header not in [b'GIF87a', b'GIF89a']:
                    return {'error': 'Not a valid GIF'}
                
                width, height, flags, bg_index, aspect = struct.unpack('<HHBBB', f.read(7))
                
                metadata['format'] = 'GIF89a' if header == b'GIF89a' else 'GIF87a'
                metadata['width'] = width
                metadata['height'] = height
                metadata['megapixels'] = round(width * height / 1_000_000, 2)
                metadata['color_mode'] = 'indexed'
                metadata['bit_depth'] = (flags & 0x07) + 1
                metadata['color_count'] = 2 ** metadata['bit_depth']
                
                # Check for transparency
                has_transparency = bool(flags & 0x80) and (bg_index < metadata['color_count'])
                metadata['has_transparency'] = has_transparency
                metadata['transparent_index'] = bg_index if has_transparency else None
                
                # Parse animation blocks
                animation_data = self._parse_animation_blocks(f, width, height)
                metadata.update(animation_data)
                
                # Calculate average FPS
                if metadata.get('animation', {}).get('frame_count', 0) > 1:
                    fps = self._calculate_fps(
                        metadata['animation']['frame_count'],
                        metadata['animation'].get('frame_delays_ms', [])
                    )
                    metadata['animation']['average_fps'] = fps
                
        except Exception as e:
            logger.warning(f"Native GIF parsing failed: {e}")
        
        return metadata
    
    def _parse_animation_blocks(self, f, width: int, height: int) -> Dict[str, Any]:
        """Parse GIF animation blocks for frame delays and disposal methods."""
        animation = {
            'frame_count': 1,
            'loop_count': 0,
            'loop_infinite': False,
            'total_duration_ms': 0,
            'average_fps': 0.0,
            'frame_delays_ms': [],
            'disposal_methods': [],
            'animated': False
        }
        
        frame_delays = []
        disposal_methods = []
        frame_count = 0
        
        try:
            while True:
                block_type = f.read(1)
                if not block_type:
                    break
                
                block_type = block_type[0]
                
                if block_type == 0x21:  # Extension
                    ext_label = f.read(1)[0]
                    
                    if ext_label == 0xF9:  # Graphics Control Extension
                        block_size = f.read(1)[0]
                        packed = f.read(1)[0]
                        delay_cs = struct.unpack('<H', f.read(2))[0]
                        transparent_index = f.read(1)[0]
                        disposal_method = (packed >> 2) & 0x07
                        
                        frame_delays.append(delay_cs)
                        
                        disposal_map = {
                            0: 'none',
                            1: 'restore_to_background',
                            2: 'restore_to_previous',
                            3: 'restore_to_undetermined'
                        }
                        disposal_methods.append(disposal_map.get(disposal_method, 'unknown'))
                        
                        f.read(block_size - 5)  # Skip remaining bytes
                        
                    elif ext_label == 0xFF:  # Application Extension
                        block_size = f.read(1)[0]
                        app_name = f.read(11).rstrip(b'\x00')
                        
                        if app_name == b'NETSCAPE2.0':
                            sub_block = f.read(1)[0]
                            if sub_block == 3:
                                f.read(1)  # Skip
                                loop_count = struct.unpack('<H', f.read(2))[0]
                                animation['loop_count'] = loop_count
                                animation['loop_infinite'] = loop_count == 0
                            f.read(1)  # Block terminator
                        else:
                            # Skip application data
                            while True:
                                data_size = f.read(1)[0]
                                if data_size == 0:
                                    break
                                f.read(data_size)
                                
                    elif ext_label == 0xFE:  # Comment Extension
                        comment_parts = []
                        while True:
                            data_size = f.read(1)[0]
                            if data_size == 0:
                                break
                            comment_parts.append(f.read(data_size))
                        if comment_parts:
                            try:
                                animation['comment'] = b''.join(comment_parts).decode('utf-8', errors='replace')
                            except:
                                pass
                    
                    else:
                        # Skip other extensions
                        while True:
                            data_size = f.read(1)[0]
                            if data_size == 0:
                                break
                            f.read(data_size)
                
                elif block_type == 0x2C:  # Image Descriptor
                    left, top, img_width, img_height = struct.unpack('<HHHH', f.read(8))
                    img_flags = f.read(1)[0]
                    
                    # Skip LZW minimum code size
                    lzw_min = f.read(1)[0]
                    
                    # Skip image data
                    while True:
                        data_size = f.read(1)[0]
                        if data_size == 0:
                            break
                        f.read(data_size)
                    
                    frame_count += 1
                
                elif block_type == 0x3B:  # Trailer
                    break
                
                else:
                    break
        
        except Exception as e:
            logger.debug(f"Animation block parsing error: {e}")
        
        if frame_count > 1:
            animation['animated'] = True
            animation['frame_count'] = frame_count
            animation['frame_delays_ms'] = [d * 10 for d in frame_delays]  # Convert to ms
            animation['total_duration_ms'] = sum(animation['frame_delays_ms'])
            animation['disposal_methods'] = disposal_methods if disposal_methods else ['restore_to_background'] * frame_count
            if frame_count > 0 and animation['total_duration_ms'] > 0:
                animation['average_fps'] = round(frame_count / (animation['total_duration_ms'] / 1000), 1)
        
        return {'animation': animation}
    
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

"""
Video metadata extractor for MetaExtract.

Specialized extractor for video file formats including MP4, AVI, MOV, MKV,
WebM, and other video formats. Handles codec information, stream details,
container metadata, and advanced video properties.
"""

import logging
import json
import subprocess
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

from ..core.base_engine import BaseExtractor, ExtractionContext, ExtractionResult, ExtractionStatus

logger = logging.getLogger(__name__)

# Availability flags for optional libraries
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False


class VideoExtractor(BaseExtractor):
    """
    Specialized extractor for video file formats.
    
    Supports MP4, AVI, MOV, MKV, WebM, and other common video formats.
    Extracts format information, codec details, stream properties, chapters,
    and advanced video metadata using ffprobe.
    """
    
    def __init__(self):
        """Initialize the video extractor."""
        supported_formats = [
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv',
            '.m4v', '.3gp', '.mts', '.m2ts', '.ogv', '.mpg', '.mpeg',
            '.vob', '.ts', '.f4v', '.rm', '.rmvb', '.asf', '.divx'
        ]
        super().__init__("video_extractor", supported_formats)
        self.logger = logging.getLogger(__name__)
    
    def _extract_metadata(self, context: ExtractionContext) -> Dict[str, Any]:
        """
        Extract metadata from a video file.
        
        Args:
            context: Extraction context containing file information
            
        Returns:
            Dictionary containing extracted video metadata
        """
        filepath = context.filepath
        metadata = {}
        
        try:
            # Basic video properties using ffprobe
            basic_properties = self._extract_basic_properties(filepath)
            if basic_properties:
                metadata["basic_properties"] = basic_properties
            
            # Format information
            format_info = self._extract_format_info(filepath)
            if format_info:
                metadata["format"] = format_info
            
            # Stream details
            stream_info = self._extract_stream_info(filepath)
            if stream_info:
                metadata["streams"] = stream_info
            
            # Chapter information
            chapter_info = self._extract_chapter_info(filepath)
            if chapter_info:
                metadata["chapters"] = chapter_info
            
            # Codec-specific details
            codec_details = self._extract_codec_details(filepath)
            if codec_details:
                metadata["codec_details"] = codec_details
            
            # Video telemetry (drone/action camera)
            telemetry = self._extract_video_telemetry(filepath)
            if telemetry:
                metadata["telemetry"] = telemetry
            
            # Add extraction statistics
            metadata["extraction_stats"] = {
                "ffmpeg_available": FFMPEG_AVAILABLE,
                "basic_properties": bool(basic_properties),
                "format_info": bool(format_info),
                "streams": bool(stream_info),
                "chapters": bool(chapter_info),
                "codec_details": bool(codec_details),
                "telemetry": bool(telemetry)
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Video extraction failed for {filepath}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _extract_basic_properties(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract basic video properties using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", "-show_chapters", filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.logger.warning(f"ffprobe failed for {filepath}: {result.stderr}")
                return None
            
            return json.loads(result.stdout)
            
        except Exception as e:
            self.logger.warning(f"Basic video properties extraction failed for {filepath}: {e}")
            return None
    
    def _extract_format_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract container format information."""
        basic_data = self._extract_basic_properties(filepath)
        if not basic_data:
            return None
        
        format_data = basic_data.get('format', {})
        
        return {
            'container': format_data.get('format_name', 'unknown'),
            'duration_seconds': float(format_data.get('duration', 0)) if format_data.get('duration') else 0,
            'size_bytes': int(format_data.get('size', 0)) if format_data.get('size') else 0,
            'bitrate': int(format_data.get('bit_rate', 0)) if format_data.get('bit_rate') else 0,
            'tags': format_data.get('tags', {})
        }
    
    def _extract_stream_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract stream-specific information."""
        basic_data = self._extract_basic_properties(filepath)
        if not basic_data:
            return None
        
        streams = basic_data.get('streams', [])
        stream_info = {
            'video_streams': [],
            'audio_streams': [],
            'subtitle_streams': [],
            'other_streams': []
        }
        
        for stream in streams:
            codec_type = stream.get('codec_type', 'unknown')
            stream_data = {
                'index': stream.get('index'),
                'codec_name': stream.get('codec_name'),
                'codec_long_name': stream.get('codec_long_name'),
                'codec_type': codec_type,
                'duration': stream.get('duration'),
                'bit_rate': stream.get('bit_rate'),
                'tags': stream.get('tags', {})
            }
            
            if codec_type == 'video':
                stream_data.update({
                    'width': stream.get('width'),
                    'height': stream.get('height'),
                    'frame_rate': stream.get('r_frame_rate'),
                    'pixel_format': stream.get('pix_fmt'),
                    'aspect_ratio': stream.get('display_aspect_ratio'),
                    'color_space': stream.get('color_space'),
                    'color_transfer': stream.get('color_transfer'),
                    'color_primaries': stream.get('color_primaries')
                })
                stream_info['video_streams'].append(stream_data)
                
            elif codec_type == 'audio':
                stream_data.update({
                    'sample_rate': stream.get('sample_rate'),
                    'channels': stream.get('channels'),
                    'channel_layout': stream.get('channel_layout'),
                    'bits_per_sample': stream.get('bits_per_sample')
                })
                stream_info['audio_streams'].append(stream_data)
                
            elif codec_type == 'subtitle':
                stream_info['subtitle_streams'].append(stream_data)
            else:
                stream_info['other_streams'].append(stream_data)
        
        return stream_info
    
    def _extract_chapter_info(self, filepath: str) -> Optional[List[Dict[str, Any]]]:
        """Extract chapter information."""
        basic_data = self._extract_basic_properties(filepath)
        if not basic_data:
            return None
        
        chapters = basic_data.get('chapters', [])
        chapter_info = []
        
        for chapter in chapters:
            chapter_data = {
                'id': chapter.get('id'),
                'start_time': chapter.get('start_time'),
                'end_time': chapter.get('end_time'),
                'start_pts': chapter.get('start_pts'),
                'end_pts': chapter.get('end_pts'),
                'tags': chapter.get('tags', {})
            }
            chapter_info.append(chapter_data)
        
        return chapter_info if chapter_info else None
    
    def _extract_codec_details(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract codec-specific details."""
        basic_data = self._extract_basic_properties(filepath)
        if not basic_data:
            return None
        
        streams = basic_data.get('streams', [])
        codec_details = {}
        
        for stream in streams:
            codec_name = stream.get('codec_name', '').lower()
            codec_type = stream.get('codec_type')
            
            if codec_type == 'video':
                if codec_name in ['h264', 'avc']:
                    codec_details['h264'] = self._extract_h264_details(stream)
                elif codec_name in ['hevc', 'h265']:
                    codec_details['hevc'] = self._extract_hevc_details(stream)
                elif codec_name == 'vp9':
                    codec_details['vp9'] = self._extract_vp9_details(stream)
                elif codec_name == 'av1':
                    codec_details['av1'] = self._extract_av1_details(stream)
            
            elif codec_type == 'audio':
                codec_details['audio'] = self._extract_audio_codec_details(stream)
        
        return codec_details if codec_details else None
    
    def _extract_h264_details(self, stream: Dict[str, Any]) -> Dict[str, Any]:
        """Extract H.264-specific details."""
        return {
            'profile': stream.get('profile'),
            'level': stream.get('level'),
            'tier': stream.get('tier'),
            'codec_tag': stream.get('codec_tag_string'),
            'is_avc': stream.get('is_avc'),
            'nal_length': stream.get('nal_length_field'),
            'has_b_frames': stream.get('has_b_frames'),
            'refs': stream.get('refs'),
            'gop_size': stream.get('gop_size')
        }
    
    def _extract_hevc_details(self, stream: Dict[str, Any]) -> Dict[str, Any]:
        """Extract HEVC-specific details."""
        return {
            'profile': stream.get('profile'),
            'level': stream.get('level'),
            'tier': stream.get('tier'),
            'codec_tag': stream.get('codec_tag_string'),
            'bit_depth': stream.get('bits_per_raw_sample'),
            'chroma_location': stream.get('chroma_location'),
            'color_range': stream.get('color_range')
        }
    
    def _extract_vp9_details(self, stream: Dict[str, Any]) -> Dict[str, Any]:
        """Extract VP9-specific details."""
        return {
            'profile': stream.get('profile'),
            'level': stream.get('level'),
            'bit_depth': stream.get('bits_per_raw_sample'),
            'color_space': stream.get('color_space'),
            'color_transfer': stream.get('color_transfer'),
            'color_primaries': stream.get('color_primaries')
        }
    
    def _extract_av1_details(self, stream: Dict[str, Any]) -> Dict[str, Any]:
        """Extract AV1-specific details."""
        return {
            'profile': stream.get('profile'),
            'level': stream.get('level'),
            'tier': stream.get('tier'),
            'bit_depth': stream.get('bits_per_raw_sample'),
            'color_space': stream.get('color_space'),
            'color_transfer': stream.get('color_transfer'),
            'color_primaries': stream.get('color_primaries')
        }
    
    def _extract_audio_codec_details(self, stream: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audio codec details."""
        return {
            'codec_name': stream.get('codec_name'),
            'profile': stream.get('profile'),
            'sample_rate': stream.get('sample_rate'),
            'channels': stream.get('channels'),
            'channel_layout': stream.get('channel_layout'),
            'bits_per_sample': stream.get('bits_per_sample'),
            'bit_rate': stream.get('bit_rate')
        }
    
    def _extract_video_telemetry(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Extract video telemetry data (drone/action camera)."""
        # This would typically use specialized modules for drone telemetry
        # For now, we'll extract GPS data from video streams if available
        
        basic_data = self._extract_basic_properties(filepath)
        if not basic_data:
            return None
        
        telemetry = {}
        streams = basic_data.get('streams', [])
        
        for stream in streams:
            # Look for GPS data in stream tags
            tags = stream.get('tags', {})
            
            # Common GPS tags in video files
            gps_data = {}
            
            # GoPro-style GPS data
            if 'location' in tags:
                gps_data['location'] = tags['location']
            
            # DJI-style GPS data
            if 'com.dji.gps.latitude' in tags:
                gps_data['latitude'] = tags.get('com.dji.gps.latitude')
                gps_data['longitude'] = tags.get('com.dji.gps.longitude')
                gps_data['altitude'] = tags.get('com.dji.gps.altitude')
            
            # Generic GPS tags
            if 'gps_latitude' in tags:
                gps_data['latitude'] = tags.get('gps_latitude')
                gps_data['longitude'] = tags.get('gps_longitude')
            
            if gps_data:
                telemetry['gps'] = gps_data
                break
        
        return telemetry if telemetry else None
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about this extractor."""
        return {
            "name": self.name,
            "supported_formats": self.supported_formats,
            "capabilities": {
                "basic_properties": True,
                "format_info": True,
                "stream_analysis": True,
                "chapter_extraction": True,
                "codec_details": True,
                "telemetry": True,
                "ffmpeg": FFMPEG_AVAILABLE
            },
            "version": "1.0.0"
        }
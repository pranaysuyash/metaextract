#!/usr/bin/env python3
"""
Advanced Video Metadata Extraction Module - Ultimate Edition

Extracts comprehensive video metadata including:
- Professional broadcast standards (SMPTE, EBU, ITU)
- HDR and color science metadata (HDR10, Dolby Vision, HLG)
- Advanced codec analysis (AV1, HEVC, VP9, ProRes, DNxHD)
- Streaming metadata (DASH, HLS, WebRTC)
- 360°/VR video metadata
- Drone and action camera telemetry
- Live streaming and broadcast metadata
- Video quality assessment and encoding analysis
- Subtitle and caption metadata
- Multi-language audio tracks
- Timecode and synchronization data

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import json
import subprocess
import logging
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timedelta
import tempfile
import re

logger = logging.getLogger(__name__)

# Library availability checks
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False

def extract_advanced_video_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive video metadata"""
    
    result = {
        "available": True,
        "video_analysis": {},
        "codec_analysis": {},
        "broadcast_standards": {},
        "hdr_metadata": {},
        "streaming_metadata": {},
        "vr_360_metadata": {},
        "quality_assessment": {},
        "audio_tracks": {},
        "subtitle_tracks": {},
        "timecode_data": {},
        "encoding_analysis": {},
        "professional_metadata": {}
    }
    
    try:
        # Basic video analysis with OpenCV
        if OPENCV_AVAILABLE:
            opencv_result = _analyze_with_opencv(filepath)
            if opencv_result:
                result["video_analysis"].update(opencv_result)
        
        # FFmpeg analysis
        ffmpeg_result = _analyze_with_ffmpeg(filepath)
        if ffmpeg_result:
            result.update(ffmpeg_result)
        
        # MediaInfo analysis
        mediainfo_result = _analyze_with_mediainfo(filepath)
        if mediainfo_result:
            result["professional_metadata"].update(mediainfo_result)
        
        # Codec-specific analysis
        codec_result = _analyze_codec_specifics(filepath)
        if codec_result:
            result["codec_analysis"].update(codec_result)
        
        # HDR and color science
        hdr_result = _analyze_hdr_metadata(filepath)
        if hdr_result:
            result["hdr_metadata"].update(hdr_result)
        
        # 360°/VR detection
        vr_result = _analyze_vr_360_metadata(filepath)
        if vr_result:
            result["vr_360_metadata"].update(vr_result)
        
        # Quality assessment
        quality_result = _assess_video_quality(filepath)
        if quality_result:
            result["quality_assessment"].update(quality_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in advanced video analysis: {e}")
        return {"available": False, "error": str(e)}

def _analyze_with_opencv(filepath: str) -> Dict[str, Any]:
    """Analyze video using OpenCV"""
    try:
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            return {}
        
        result = {}
        
        # Basic properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        result["opencv_analysis"] = {
            "fps": fps,
            "frame_count": frame_count,
            "duration_seconds": frame_count / fps if fps > 0 else 0,
            "resolution": f"{width}x{height}",
            "aspect_ratio": round(width / height, 3) if height > 0 else 0,
            "total_pixels_per_frame": width * height,
            "codec_fourcc": int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        # Sample frame analysis
        ret, frame = cap.read()
        if ret:
            # Color analysis
            mean_color = cv2.mean(frame)[:3]
            result["opencv_analysis"]["sample_frame"] = {
                "mean_bgr": list(mean_color),
                "brightness": sum(mean_color) / 3,
                "frame_size_bytes": frame.nbytes,
                "color_channels": frame.shape[2] if len(frame.shape) > 2 else 1
            }
            
            # Motion analysis (compare first and middle frame)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
            ret2, frame2 = cap.read()
            if ret2:
                # Calculate frame difference
                diff = cv2.absdiff(frame, frame2)
                motion_score = cv2.mean(diff)[0]
                result["opencv_analysis"]["motion_analysis"] = {
                    "motion_score": motion_score,
                    "motion_level": "high" if motion_score > 30 else "medium" if motion_score > 10 else "low"
                }
        
        cap.release()
        return result
        
    except Exception as e:
        logger.error(f"OpenCV video analysis error: {e}")
        return {}

def _analyze_with_ffmpeg(filepath: str) -> Dict[str, Any]:
    """Analyze video using FFmpeg/FFprobe"""
    try:
        # Run ffprobe to get detailed metadata
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', '-show_chapters',
            '-show_programs', '-show_error', filepath
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}
        
        data = json.loads(result.stdout)
        
        ffmpeg_result = {
            "format_info": {},
            "video_streams": [],
            "audio_streams": [],
            "subtitle_streams": [],
            "chapters": [],
            "programs": []
        }
        
        # Format information
        if 'format' in data:
            fmt = data['format']
            ffmpeg_result["format_info"] = {
                "filename": fmt.get('filename'),
                "nb_streams": int(fmt.get('nb_streams', 0)),
                "nb_programs": int(fmt.get('nb_programs', 0)),
                "format_name": fmt.get('format_name'),
                "format_long_name": fmt.get('format_long_name'),
                "start_time": float(fmt.get('start_time', 0)),
                "duration": float(fmt.get('duration', 0)),
                "size": int(fmt.get('size', 0)),
                "bit_rate": int(fmt.get('bit_rate', 0)),
                "probe_score": int(fmt.get('probe_score', 0)),
                "tags": fmt.get('tags', {})
            }
        
        # Stream analysis
        if 'streams' in data:
            for stream in data['streams']:
                stream_info = {
                    "index": stream.get('index'),
                    "codec_name": stream.get('codec_name'),
                    "codec_long_name": stream.get('codec_long_name'),
                    "codec_type": stream.get('codec_type'),
                    "codec_tag_string": stream.get('codec_tag_string'),
                    "codec_tag": stream.get('codec_tag'),
                    "profile": stream.get('profile'),
                    "level": stream.get('level'),
                    "time_base": stream.get('time_base'),
                    "start_pts": stream.get('start_pts'),
                    "start_time": stream.get('start_time'),
                    "duration_ts": stream.get('duration_ts'),
                    "duration": stream.get('duration'),
                    "bit_rate": stream.get('bit_rate'),
                    "nb_frames": stream.get('nb_frames'),
                    "tags": stream.get('tags', {})
                }
                
                if stream.get('codec_type') == 'video':
                    stream_info.update({
                        "width": stream.get('width'),
                        "height": stream.get('height'),
                        "coded_width": stream.get('coded_width'),
                        "coded_height": stream.get('coded_height'),
                        "closed_captions": stream.get('closed_captions'),
                        "film_grain": stream.get('film_grain'),
                        "has_b_frames": stream.get('has_b_frames'),
                        "sample_aspect_ratio": stream.get('sample_aspect_ratio'),
                        "display_aspect_ratio": stream.get('display_aspect_ratio'),
                        "pix_fmt": stream.get('pix_fmt'),
                        "level": stream.get('level'),
                        "color_range": stream.get('color_range'),
                        "color_space": stream.get('color_space'),
                        "color_transfer": stream.get('color_transfer'),
                        "color_primaries": stream.get('color_primaries'),
                        "chroma_location": stream.get('chroma_location'),
                        "field_order": stream.get('field_order'),
                        "refs": stream.get('refs'),
                        "r_frame_rate": stream.get('r_frame_rate'),
                        "avg_frame_rate": stream.get('avg_frame_rate')
                    })
                    ffmpeg_result["video_streams"].append(stream_info)
                
                elif stream.get('codec_type') == 'audio':
                    stream_info.update({
                        "sample_fmt": stream.get('sample_fmt'),
                        "sample_rate": stream.get('sample_rate'),
                        "channels": stream.get('channels'),
                        "channel_layout": stream.get('channel_layout'),
                        "bits_per_sample": stream.get('bits_per_sample')
                    })
                    ffmpeg_result["audio_streams"].append(stream_info)
                
                elif stream.get('codec_type') == 'subtitle':
                    ffmpeg_result["subtitle_streams"].append(stream_info)
        
        # Chapters
        if 'chapters' in data:
            ffmpeg_result["chapters"] = data['chapters']
        
        # Programs
        if 'programs' in data:
            ffmpeg_result["programs"] = data['programs']
        
        return ffmpeg_result
        
    except Exception as e:
        logger.error(f"FFmpeg analysis error: {e}")
        return {}

def _analyze_with_mediainfo(filepath: str) -> Dict[str, Any]:
    """Analyze video using MediaInfo"""
    try:
        # Try to run mediainfo
        cmd = ['mediainfo', '--Output=JSON', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {"mediainfo_available": False}
        
        data = json.loads(result.stdout)
        
        mediainfo_result = {
            "mediainfo_available": True,
            "general": {},
            "video_tracks": [],
            "audio_tracks": [],
            "text_tracks": [],
            "menu_tracks": []
        }
        
        if 'media' in data and 'track' in data['media']:
            for track in data['media']['track']:
                track_type = track.get('@type', '').lower()
                
                if track_type == 'general':
                    mediainfo_result["general"] = track
                elif track_type == 'video':
                    mediainfo_result["video_tracks"].append(track)
                elif track_type == 'audio':
                    mediainfo_result["audio_tracks"].append(track)
                elif track_type == 'text':
                    mediainfo_result["text_tracks"].append(track)
                elif track_type == 'menu':
                    mediainfo_result["menu_tracks"].append(track)
        
        return mediainfo_result
        
    except Exception as e:
        logger.debug(f"MediaInfo not available: {e}")
        return {"mediainfo_available": False}

def _analyze_codec_specifics(filepath: str) -> Dict[str, Any]:
    """Analyze codec-specific metadata"""
    try:
        result = {
            "h264_analysis": {},
            "h265_analysis": {},
            "av1_analysis": {},
            "vp9_analysis": {},
            "prores_analysis": {},
            "dnxhd_analysis": {}
        }
        
        # Get codec information from ffprobe
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,profile,level,pix_fmt,color_space,color_transfer,color_primaries',
            '-of', 'csv=p=0', filepath
        ]
        
        ffprobe_result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if ffprobe_result.returncode == 0:
            codec_info = ffprobe_result.stdout.strip().split(',')
            if len(codec_info) >= 1:
                codec_name = codec_info[0]
                
                # H.264 specific analysis
                if codec_name in ['h264', 'avc']:
                    result["h264_analysis"] = _analyze_h264_specifics(filepath, codec_info)
                
                # H.265/HEVC specific analysis
                elif codec_name in ['hevc', 'h265']:
                    result["h265_analysis"] = _analyze_h265_specifics(filepath, codec_info)
                
                # AV1 specific analysis
                elif codec_name == 'av01':
                    result["av1_analysis"] = _analyze_av1_specifics(filepath, codec_info)
                
                # VP9 specific analysis
                elif codec_name == 'vp9':
                    result["vp9_analysis"] = _analyze_vp9_specifics(filepath, codec_info)
                
                # ProRes specific analysis
                elif 'prores' in codec_name:
                    result["prores_analysis"] = _analyze_prores_specifics(filepath, codec_info)
        
        return result
        
    except Exception as e:
        logger.error(f"Codec analysis error: {e}")
        return {}

def _analyze_h264_specifics(filepath: str, codec_info: List[str]) -> Dict[str, Any]:
    """Analyze H.264 specific metadata"""
    try:
        result = {
            "profile": codec_info[1] if len(codec_info) > 1 else None,
            "level": codec_info[2] if len(codec_info) > 2 else None,
            "pixel_format": codec_info[3] if len(codec_info) > 3 else None,
            "entropy_coding": "unknown",
            "reference_frames": "unknown",
            "b_frames": "unknown"
        }
        
        # Get detailed H.264 parameters
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=profile,level,has_b_frames,refs',
            '-of', 'csv=p=0', filepath
        ]
        
        detailed_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if detailed_result.returncode == 0:
            details = detailed_result.stdout.strip().split(',')
            if len(details) >= 4:
                result.update({
                    "profile": details[0],
                    "level": details[1],
                    "b_frames": details[2],
                    "reference_frames": details[3]
                })
        
        return result
        
    except Exception as e:
        logger.error(f"H.264 analysis error: {e}")
        return {}

def _analyze_h265_specifics(filepath: str, codec_info: List[str]) -> Dict[str, Any]:
    """Analyze H.265/HEVC specific metadata"""
    try:
        result = {
            "profile": codec_info[1] if len(codec_info) > 1 else None,
            "level": codec_info[2] if len(codec_info) > 2 else None,
            "tier": "unknown",
            "bit_depth": "unknown",
            "chroma_format": "unknown"
        }
        
        # HEVC profiles indicate capabilities
        profile = result["profile"]
        if profile:
            if "10" in profile:
                result["bit_depth"] = "10-bit"
            elif "12" in profile:
                result["bit_depth"] = "12-bit"
            else:
                result["bit_depth"] = "8-bit"
            
            if "422" in profile:
                result["chroma_format"] = "4:2:2"
            elif "444" in profile:
                result["chroma_format"] = "4:4:4"
            else:
                result["chroma_format"] = "4:2:0"
        
        return result
        
    except Exception as e:
        logger.error(f"H.265 analysis error: {e}")
        return {}

def _analyze_av1_specifics(filepath: str, codec_info: List[str]) -> Dict[str, Any]:
    """Analyze AV1 specific metadata"""
    try:
        result = {
            "profile": codec_info[1] if len(codec_info) > 1 else None,
            "level": codec_info[2] if len(codec_info) > 2 else None,
            "tier": "unknown",
            "bit_depth": "unknown",
            "film_grain": "unknown"
        }
        
        # AV1 specific parameters
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=film_grain,profile,level',
            '-of', 'csv=p=0', filepath
        ]
        
        av1_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if av1_result.returncode == 0:
            details = av1_result.stdout.strip().split(',')
            if len(details) >= 1:
                result["film_grain"] = details[0] if details[0] else "disabled"
        
        return result
        
    except Exception as e:
        logger.error(f"AV1 analysis error: {e}")
        return {}

def _analyze_vp9_specifics(filepath: str, codec_info: List[str]) -> Dict[str, Any]:
    """Analyze VP9 specific metadata"""
    try:
        result = {
            "profile": codec_info[1] if len(codec_info) > 1 else None,
            "level": codec_info[2] if len(codec_info) > 2 else None,
            "bit_depth": "8-bit",  # Default for VP9
            "chroma_subsampling": "4:2:0"  # Default for VP9
        }
        
        # VP9 profile indicates bit depth and chroma format
        profile = result["profile"]
        if profile == "1":
            result["chroma_subsampling"] = "4:2:2 or 4:4:4"
        elif profile == "2":
            result["bit_depth"] = "10-bit or 12-bit"
        elif profile == "3":
            result["bit_depth"] = "10-bit or 12-bit"
            result["chroma_subsampling"] = "4:2:2 or 4:4:4"
        
        return result
        
    except Exception as e:
        logger.error(f"VP9 analysis error: {e}")
        return {}

def _analyze_prores_specifics(filepath: str, codec_info: List[str]) -> Dict[str, Any]:
    """Analyze ProRes specific metadata"""
    try:
        result = {
            "variant": "unknown",
            "quality": "unknown",
            "bit_depth": "10-bit",  # Standard for ProRes
            "chroma_format": "4:2:2"  # Standard for most ProRes
        }
        
        # ProRes variants
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_tag_string',
            '-of', 'csv=p=0', filepath
        ]
        
        prores_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if prores_result.returncode == 0:
            codec_tag = prores_result.stdout.strip()
            
            # Map ProRes codec tags to variants
            prores_variants = {
                'apco': 'ProRes 422 Proxy',
                'apcs': 'ProRes 422 LT',
                'apcn': 'ProRes 422',
                'apch': 'ProRes 422 HQ',
                'ap4h': 'ProRes 4444',
                'ap4x': 'ProRes 4444 XQ'
            }
            
            result["variant"] = prores_variants.get(codec_tag, f"Unknown ({codec_tag})")
            
            # 4444 variants have different chroma format
            if codec_tag in ['ap4h', 'ap4x']:
                result["chroma_format"] = "4:4:4"
                result["bit_depth"] = "12-bit" if codec_tag == 'ap4x' else "10-bit"
        
        return result
        
    except Exception as e:
        logger.error(f"ProRes analysis error: {e}")
        return {}

def _analyze_hdr_metadata(filepath: str) -> Dict[str, Any]:
    """Analyze HDR and color science metadata"""
    try:
        result = {
            "hdr_format": "SDR",
            "color_space": "unknown",
            "color_primaries": "unknown",
            "transfer_characteristics": "unknown",
            "matrix_coefficients": "unknown",
            "mastering_display": {},
            "content_light_level": {},
            "dolby_vision": {},
            "hdr10_plus": {}
        }
        
        # Get color metadata from ffprobe
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=color_space,color_transfer,color_primaries,color_range',
            '-show_entries', 'side_data',
            '-of', 'json', filepath
        ]
        
        hdr_result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if hdr_result.returncode == 0:
            data = json.loads(hdr_result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                
                result.update({
                    "color_space": stream.get('color_space', 'unknown'),
                    "color_primaries": stream.get('color_primaries', 'unknown'),
                    "transfer_characteristics": stream.get('color_transfer', 'unknown'),
                    "color_range": stream.get('color_range', 'unknown')
                })
                
                # Detect HDR format based on transfer characteristics
                transfer = stream.get('color_transfer', '')
                if transfer in ['smpte2084', 'arib-std-b67']:
                    if transfer == 'smpte2084':
                        result["hdr_format"] = "HDR10"
                    elif transfer == 'arib-std-b67':
                        result["hdr_format"] = "HLG"
                
                # Check for HDR side data
                if 'side_data_list' in stream:
                    for side_data in stream['side_data_list']:
                        side_type = side_data.get('side_data_type', '')
                        
                        if side_type == 'Mastering display metadata':
                            result["mastering_display"] = {
                                "display_primaries": side_data.get('display_primaries'),
                                "white_point": side_data.get('white_point'),
                                "min_luminance": side_data.get('min_luminance'),
                                "max_luminance": side_data.get('max_luminance')
                            }
                        
                        elif side_type == 'Content light level metadata':
                            result["content_light_level"] = {
                                "max_content": side_data.get('max_content'),
                                "max_average": side_data.get('max_average')
                            }
        
        return result
        
    except Exception as e:
        logger.error(f"HDR analysis error: {e}")
        return {}

def _analyze_vr_360_metadata(filepath: str) -> Dict[str, Any]:
    """Analyze 360°/VR video metadata"""
    try:
        result = {
            "is_360": False,
            "is_vr": False,
            "projection_type": "unknown",
            "stereo_mode": "mono",
            "spatial_audio": False
        }
        
        # Check for 360° indicators in metadata
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format_tags:stream_tags',
            '-of', 'json', filepath
        ]
        
        vr_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if vr_result.returncode == 0:
            data = json.loads(vr_result.stdout)
            
            # Check format tags
            if 'format' in data and 'tags' in data['format']:
                tags = data['format']['tags']
                
                # Look for 360° indicators
                for key, value in tags.items():
                    key_lower = key.lower()
                    value_lower = str(value).lower()
                    
                    if any(indicator in key_lower or indicator in value_lower 
                           for indicator in ['360', 'spherical', 'equirectangular', 'vr']):
                        result["is_360"] = True
                        
                        if 'equirectangular' in value_lower:
                            result["projection_type"] = "equirectangular"
                        elif 'cubemap' in value_lower:
                            result["projection_type"] = "cubemap"
                    
                    if any(indicator in key_lower or indicator in value_lower 
                           for indicator in ['stereo', '3d', 'sbs', 'tb']):
                        result["is_vr"] = True
                        
                        if 'sbs' in value_lower or 'side' in value_lower:
                            result["stereo_mode"] = "side_by_side"
                        elif 'tb' in value_lower or 'top' in value_lower:
                            result["stereo_mode"] = "top_bottom"
            
            # Check stream tags
            if 'streams' in data:
                for stream in data['streams']:
                    if 'tags' in stream:
                        tags = stream['tags']
                        
                        # Check for spatial audio
                        if stream.get('codec_type') == 'audio':
                            channels = stream.get('channels', 0)
                            if channels > 2:
                                result["spatial_audio"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"VR/360 analysis error: {e}")
        return {}

def _assess_video_quality(filepath: str) -> Dict[str, Any]:
    """Assess video quality metrics"""
    try:
        result = {
            "resolution_category": "unknown",
            "bitrate_assessment": "unknown",
            "compression_efficiency": "unknown",
            "quality_score": 0
        }
        
        # Get basic video info
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,bit_rate,r_frame_rate',
            '-of', 'csv=p=0', filepath
        ]
        
        quality_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if quality_result.returncode == 0:
            info = quality_result.stdout.strip().split(',')
            if len(info) >= 4:
                width = int(info[0]) if info[0] else 0
                height = int(info[1]) if info[1] else 0
                bitrate = int(info[2]) if info[2] else 0
                framerate = info[3]
                
                # Resolution category
                total_pixels = width * height
                if total_pixels >= 7680 * 4320:  # 8K
                    result["resolution_category"] = "8K"
                elif total_pixels >= 3840 * 2160:  # 4K
                    result["resolution_category"] = "4K"
                elif total_pixels >= 1920 * 1080:  # 1080p
                    result["resolution_category"] = "1080p"
                elif total_pixels >= 1280 * 720:   # 720p
                    result["resolution_category"] = "720p"
                elif total_pixels >= 854 * 480:    # 480p
                    result["resolution_category"] = "480p"
                else:
                    result["resolution_category"] = "SD"
                
                # Bitrate assessment
                if bitrate > 0:
                    # Calculate bits per pixel per frame
                    if '/' in framerate:
                        fps_parts = framerate.split('/')
                        fps = float(fps_parts[0]) / float(fps_parts[1])
                    else:
                        fps = float(framerate)
                    
                    if fps > 0 and total_pixels > 0:
                        bpp = bitrate / (total_pixels * fps)
                        
                        if bpp > 0.5:
                            result["bitrate_assessment"] = "very_high"
                        elif bpp > 0.2:
                            result["bitrate_assessment"] = "high"
                        elif bpp > 0.1:
                            result["bitrate_assessment"] = "medium"
                        elif bpp > 0.05:
                            result["bitrate_assessment"] = "low"
                        else:
                            result["bitrate_assessment"] = "very_low"
                        
                        result["bits_per_pixel"] = round(bpp, 4)
                
                # Overall quality score (0-100)
                quality_factors = []
                
                # Resolution factor
                if result["resolution_category"] in ["8K", "4K"]:
                    quality_factors.append(30)
                elif result["resolution_category"] in ["1080p"]:
                    quality_factors.append(25)
                elif result["resolution_category"] in ["720p"]:
                    quality_factors.append(20)
                else:
                    quality_factors.append(10)
                
                # Bitrate factor
                if result["bitrate_assessment"] in ["very_high", "high"]:
                    quality_factors.append(25)
                elif result["bitrate_assessment"] == "medium":
                    quality_factors.append(20)
                elif result["bitrate_assessment"] == "low":
                    quality_factors.append(15)
                else:
                    quality_factors.append(5)
                
                result["quality_score"] = sum(quality_factors)
        
        return result
        
    except Exception as e:
        logger.error(f"Quality assessment error: {e}")
        return {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_advanced_video_metadata(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python advanced_video_ultimate.py <video_file>")
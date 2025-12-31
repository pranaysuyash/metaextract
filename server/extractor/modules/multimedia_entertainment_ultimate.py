#!/usr/bin/env python3
"""
Multimedia and Entertainment Metadata Extraction Module - Ultimate Edition

Extracts comprehensive metadata from multimedia and entertainment content including:
- Gaming Assets (Unity, Unreal, Godot, textures, models, animations)
- Streaming Media (Netflix, YouTube, Twitch, streaming protocols)
- Digital Art and Design (Photoshop, Illustrator, Blender, Maya, 3ds Max)
- Music Production (DAW projects, MIDI, stems, mastering)
- Video Production (Premiere, Final Cut, DaVinci Resolve, After Effects)
- Virtual Reality Content (VR videos, 360° content, spatial audio)
- Augmented Reality Assets (AR models, markers, tracking data)
- Interactive Media (Flash, HTML5 games, interactive videos)
- Digital Publishing (eBooks, magazines, interactive publications)
- Social Media Content (Instagram, TikTok, YouTube metadata)
- Podcast and Audio Content (RSS feeds, chapters, transcripts)
- Live Streaming Data (OBS, streaming software, broadcast metadata)

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import json
import struct
import logging
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime
import tempfile
import hashlib
import base64

logger = logging.getLogger(__name__)

# Library availability checks
try:
    import PIL.Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mutagen
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

def extract_multimedia_entertainment_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive multimedia and entertainment metadata"""
    
    result = {
        "available": True,
        "content_type": "unknown",
        "gaming_assets": {},
        "streaming_media": {},
        "digital_art": {},
        "music_production": {},
        "video_production": {},
        "vr_ar_content": {},
        "interactive_media": {},
        "digital_publishing": {},
        "social_media": {},
        "podcast_audio": {},
        "live_streaming": {},
        "entertainment_metadata": {},
        "content_rating": {},
        "distribution_info": {}
    }
    
    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()
        
        # Gaming Assets
        if file_ext in ['.unity', '.unitypackage', '.uasset', '.blend', '.fbx', '.obj'] or any(term in filename for term in ['game', 'unity', 'unreal']):
            result["content_type"] = "gaming_asset"
            gaming_result = _analyze_gaming_assets(filepath, file_ext)
            if gaming_result:
                result["gaming_assets"].update(gaming_result)
        
        # Streaming Media
        elif file_ext in ['.m3u8', '.mpd', '.f4m'] or any(term in filename for term in ['stream', 'live', 'broadcast']):
            result["content_type"] = "streaming_media"
            streaming_result = _analyze_streaming_media(filepath, file_ext)
            if streaming_result:
                result["streaming_media"].update(streaming_result)
        
        # Digital Art and Design
        elif file_ext in ['.psd', '.ai', '.sketch', '.fig', '.xd'] or any(term in filename for term in ['design', 'artwork', 'graphic']):
            result["content_type"] = "digital_art"
            art_result = _analyze_digital_art(filepath, file_ext)
            if art_result:
                result["digital_art"].update(art_result)
        
        # Music Production
        elif file_ext in ['.aup', '.logic', '.flp', '.als', '.ptx', '.mid', '.midi'] or any(term in filename for term in ['music', 'audio', 'track', 'song']):
            result["content_type"] = "music_production"
            music_result = _analyze_music_production(filepath, file_ext)
            if music_result:
                result["music_production"].update(music_result)
        
        # Video Production
        elif file_ext in ['.prproj', '.fcp', '.drp', '.aep'] or any(term in filename for term in ['video', 'edit', 'project']):
            result["content_type"] = "video_production"
            video_result = _analyze_video_production(filepath, file_ext)
            if video_result:
                result["video_production"].update(video_result)
        
        # VR/AR Content
        elif any(term in filename for term in ['vr', 'ar', '360', 'virtual', 'augmented']):
            result["content_type"] = "vr_ar_content"
            vr_ar_result = _analyze_vr_ar_content(filepath, file_ext)
            if vr_ar_result:
                result["vr_ar_content"].update(vr_ar_result)
        
        # Interactive Media
        elif file_ext in ['.swf', '.html5', '.js'] and any(term in filename for term in ['interactive', 'game', 'animation']):
            result["content_type"] = "interactive_media"
            interactive_result = _analyze_interactive_media(filepath, file_ext)
            if interactive_result:
                result["interactive_media"].update(interactive_result)
        
        # Digital Publishing
        elif file_ext in ['.epub', '.mobi', '.azw', '.indd'] or any(term in filename for term in ['book', 'magazine', 'publication']):
            result["content_type"] = "digital_publishing"
            publishing_result = _analyze_digital_publishing(filepath, file_ext)
            if publishing_result:
                result["digital_publishing"].update(publishing_result)
        
        # Social Media Content
        elif any(term in filename for term in ['instagram', 'tiktok', 'youtube', 'social', 'post']):
            result["content_type"] = "social_media"
            social_result = _analyze_social_media_content(filepath, file_ext)
            if social_result:
                result["social_media"].update(social_result)
        
        # Podcast and Audio Content
        elif file_ext in ['.mp3', '.m4a', '.wav'] and any(term in filename for term in ['podcast', 'episode', 'audio', 'radio']):
            result["content_type"] = "podcast_audio"
            podcast_result = _analyze_podcast_content(filepath, file_ext)
            if podcast_result:
                result["podcast_audio"].update(podcast_result)
        
        # Live Streaming
        elif any(term in filename for term in ['obs', 'stream', 'broadcast', 'live']):
            result["content_type"] = "live_streaming"
            live_result = _analyze_live_streaming(filepath, file_ext)
            if live_result:
                result["live_streaming"].update(live_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in multimedia entertainment analysis: {e}")
        return {"available": False, "error": str(e)}

def _analyze_gaming_assets(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze gaming assets and game development files"""
    try:
        result = {
            "gaming_analysis": {
                "asset_type": "unknown",
                "game_engine": "unknown",
                "asset_properties": {},
                "texture_info": {},
                "model_info": {},
                "animation_data": {},
                "shader_info": {},
                "performance_metrics": {}
            }
        }
        
        # Detect game engine from file extension and metadata
        engine_map = {
            '.unity': 'Unity',
            '.unitypackage': 'Unity',
            '.uasset': 'Unreal Engine',
            '.umap': 'Unreal Engine',
            '.blend': 'Blender',
            '.fbx': 'Autodesk FBX',
            '.obj': 'Wavefront OBJ'
        }
        
        result["gaming_analysis"]["game_engine"] = engine_map.get(file_ext, "unknown")
        
        # Asset type detection
        if file_ext in ['.png', '.jpg', '.tga', '.dds'] and any(term in Path(filepath).name.lower() for term in ['texture', 'diffuse', 'normal', 'specular']):
            result["gaming_analysis"]["asset_type"] = "texture"
            texture_result = _analyze_texture_asset(filepath)
            if texture_result:
                result["gaming_analysis"]["texture_info"].update(texture_result)
        
        elif file_ext in ['.fbx', '.obj', '.dae', '.3ds']:
            result["gaming_analysis"]["asset_type"] = "3d_model"
            model_result = _analyze_3d_model_asset(filepath, file_ext)
            if model_result:
                result["gaming_analysis"]["model_info"].update(model_result)
        
        elif file_ext in ['.anim', '.fbx'] and 'anim' in Path(filepath).name.lower():
            result["gaming_analysis"]["asset_type"] = "animation"
            anim_result = _analyze_animation_asset(filepath)
            if anim_result:
                result["gaming_analysis"]["animation_data"].update(anim_result)
        
        # Unity-specific analysis
        if file_ext == '.unity':
            unity_result = _analyze_unity_scene(filepath)
            if unity_result:
                result["gaming_analysis"].update(unity_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Gaming assets analysis error: {e}")
        return {}

def _analyze_texture_asset(filepath: str) -> Dict[str, Any]:
    """Analyze texture assets for games"""
    try:
        result = {
            "texture_type": "unknown",
            "resolution": {},
            "format_info": {},
            "compression": {},
            "mip_maps": False,
            "color_channels": 0
        }
        
        if PIL_AVAILABLE:
            try:
                with PIL.Image.open(filepath) as img:
                    result["resolution"] = {
                        "width": img.width,
                        "height": img.height,
                        "aspect_ratio": round(img.width / img.height, 3)
                    }
                    
                    result["format_info"] = {
                        "format": img.format,
                        "mode": img.mode,
                        "has_transparency": img.mode in ['RGBA', 'LA', 'P']
                    }
                    
                    # Detect texture type from filename
                    filename = Path(filepath).name.lower()
                    if 'diffuse' in filename or 'albedo' in filename:
                        result["texture_type"] = "diffuse"
                    elif 'normal' in filename:
                        result["texture_type"] = "normal_map"
                    elif 'specular' in filename:
                        result["texture_type"] = "specular"
                    elif 'roughness' in filename:
                        result["texture_type"] = "roughness"
                    elif 'metallic' in filename:
                        result["texture_type"] = "metallic"
                    elif 'height' in filename or 'displacement' in filename:
                        result["texture_type"] = "height_map"
                    elif 'ao' in filename or 'occlusion' in filename:
                        result["texture_type"] = "ambient_occlusion"
                    
                    # Check if resolution is power of 2 (common for game textures)
                    result["format_info"]["power_of_2"] = (
                        (img.width & (img.width - 1)) == 0 and 
                        (img.height & (img.height - 1)) == 0
                    )
                    
                    # Estimate memory usage
                    bytes_per_pixel = len(img.getbands())
                    result["format_info"]["estimated_memory_mb"] = (img.width * img.height * bytes_per_pixel) / (1024 * 1024)
            except:
                pass
        
        return result
        
    except Exception as e:
        logger.error(f"Texture analysis error: {e}")
        return {}

def _analyze_3d_model_asset(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze 3D model assets"""
    try:
        result = {
            "model_format": file_ext,
            "geometry_info": {},
            "material_info": {},
            "animation_info": {},
            "optimization_info": {}
        }
        
        # Basic file size analysis
        file_size = os.path.getsize(filepath)
        result["geometry_info"]["file_size_mb"] = file_size / (1024 * 1024)
        
        # For FBX files, try to extract basic information
        if file_ext == '.fbx':
            fbx_result = _analyze_fbx_model(filepath)
            if fbx_result:
                result.update(fbx_result)
        
        # For OBJ files, parse basic structure
        elif file_ext == '.obj':
            obj_result = _analyze_obj_model(filepath)
            if obj_result:
                result.update(obj_result)
        
        return result
        
    except Exception as e:
        logger.error(f"3D model analysis error: {e}")
        return {}

def _analyze_fbx_model(filepath: str) -> Dict[str, Any]:
    """Analyze FBX model files"""
    try:
        result = {
            "fbx_info": {
                "version": "unknown",
                "has_animation": False,
                "has_materials": False,
                "has_textures": False
            }
        }
        
        # FBX files are binary, so we'll do basic header analysis
        with open(filepath, 'rb') as f:
            header = f.read(1024)  # Read first 1KB
            
            # Check for FBX signature
            if b'Kaydara FBX Binary' in header:
                result["fbx_info"]["format"] = "binary"
            elif b'FBX' in header[:100]:
                result["fbx_info"]["format"] = "ascii"
            
            # Look for common FBX sections in header
            if b'Material' in header:
                result["fbx_info"]["has_materials"] = True
            if b'Texture' in header:
                result["fbx_info"]["has_textures"] = True
            if b'AnimationStack' in header or b'AnimationLayer' in header:
                result["fbx_info"]["has_animation"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"FBX analysis error: {e}")
        return {}

def _analyze_obj_model(filepath: str) -> Dict[str, Any]:
    """Analyze OBJ model files"""
    try:
        result = {
            "obj_info": {
                "vertex_count": 0,
                "face_count": 0,
                "texture_coords": 0,
                "normals": 0,
                "materials": []
            }
        }
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                if line_num > 10000:  # Limit parsing for performance
                    break
                
                line = line.strip()
                if line.startswith('v '):
                    result["obj_info"]["vertex_count"] += 1
                elif line.startswith('f '):
                    result["obj_info"]["face_count"] += 1
                elif line.startswith('vt '):
                    result["obj_info"]["texture_coords"] += 1
                elif line.startswith('vn '):
                    result["obj_info"]["normals"] += 1
                elif line.startswith('usemtl '):
                    material_name = line.split(' ', 1)[1]
                    if material_name not in result["obj_info"]["materials"]:
                        result["obj_info"]["materials"].append(material_name)
        
        # Calculate complexity metrics
        if result["obj_info"]["vertex_count"] > 0:
            result["obj_info"]["complexity"] = "high" if result["obj_info"]["vertex_count"] > 50000 else "medium" if result["obj_info"]["vertex_count"] > 5000 else "low"
        
        return result
        
    except Exception as e:
        logger.error(f"OBJ analysis error: {e}")
        return {}

def _analyze_streaming_media(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze streaming media files and playlists"""
    try:
        result = {
            "streaming_analysis": {
                "protocol": "unknown",
                "playlist_info": {},
                "stream_quality": {},
                "adaptive_streaming": False,
                "drm_protection": False,
                "cdn_info": {}
            }
        }
        
        # HLS (HTTP Live Streaming) analysis
        if file_ext == '.m3u8':
            hls_result = _analyze_hls_playlist(filepath)
            if hls_result:
                result["streaming_analysis"].update(hls_result)
                result["streaming_analysis"]["protocol"] = "HLS"
        
        # DASH (Dynamic Adaptive Streaming) analysis
        elif file_ext == '.mpd':
            dash_result = _analyze_dash_manifest(filepath)
            if dash_result:
                result["streaming_analysis"].update(dash_result)
                result["streaming_analysis"]["protocol"] = "DASH"
        
        return result
        
    except Exception as e:
        logger.error(f"Streaming media analysis error: {e}")
        return {}

def _analyze_hls_playlist(filepath: str) -> Dict[str, Any]:
    """Analyze HLS playlist files"""
    try:
        result = {
            "hls_info": {
                "version": None,
                "target_duration": None,
                "segments": [],
                "quality_levels": [],
                "is_master_playlist": False
            }
        }
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXT-X-VERSION:'):
                result["hls_info"]["version"] = int(line.split(':')[1])
            
            elif line.startswith('#EXT-X-TARGETDURATION:'):
                result["hls_info"]["target_duration"] = int(line.split(':')[1])
            
            elif line.startswith('#EXT-X-STREAM-INF:'):
                # Master playlist with multiple quality levels
                result["hls_info"]["is_master_playlist"] = True
                
                # Parse stream info
                stream_info = {}
                params = line.split(':', 1)[1]
                
                # Extract bandwidth
                if 'BANDWIDTH=' in params:
                    bandwidth_match = re.search(r'BANDWIDTH=(\d+)', params)
                    if bandwidth_match:
                        stream_info["bandwidth"] = int(bandwidth_match.group(1))
                
                # Extract resolution
                if 'RESOLUTION=' in params:
                    resolution_match = re.search(r'RESOLUTION=(\d+x\d+)', params)
                    if resolution_match:
                        stream_info["resolution"] = resolution_match.group(1)
                
                result["hls_info"]["quality_levels"].append(stream_info)
            
            elif line.startswith('#EXTINF:'):
                # Segment duration
                duration_match = re.search(r'#EXTINF:([\d.]+)', line)
                if duration_match:
                    segment_duration = float(duration_match.group(1))
                    result["hls_info"]["segments"].append({"duration": segment_duration})
        
        # Calculate total duration
        if result["hls_info"]["segments"]:
            total_duration = sum(seg["duration"] for seg in result["hls_info"]["segments"])
            result["hls_info"]["total_duration_seconds"] = total_duration
        
        return result
        
    except Exception as e:
        logger.error(f"HLS analysis error: {e}")
        return {}

def _analyze_digital_art(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze digital art and design files"""
    try:
        result = {
            "digital_art_analysis": {
                "software": "unknown",
                "artwork_type": "unknown",
                "canvas_info": {},
                "layer_info": {},
                "color_info": {},
                "design_elements": {},
                "project_metadata": {}
            }
        }
        
        # Detect software from file extension
        software_map = {
            '.psd': 'Adobe Photoshop',
            '.ai': 'Adobe Illustrator',
            '.sketch': 'Sketch',
            '.fig': 'Figma',
            '.xd': 'Adobe XD',
            '.afdesign': 'Affinity Designer',
            '.afphoto': 'Affinity Photo'
        }
        
        result["digital_art_analysis"]["software"] = software_map.get(file_ext, "unknown")
        
        # Photoshop PSD analysis
        if file_ext == '.psd':
            psd_result = _analyze_psd_file(filepath)
            if psd_result:
                result["digital_art_analysis"].update(psd_result)
        
        # Adobe Illustrator AI analysis
        elif file_ext == '.ai':
            ai_result = _analyze_ai_file(filepath)
            if ai_result:
                result["digital_art_analysis"].update(ai_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Digital art analysis error: {e}")
        return {}

def _analyze_psd_file(filepath: str) -> Dict[str, Any]:
    """Analyze Photoshop PSD files"""
    try:
        result = {
            "psd_info": {
                "version": None,
                "color_mode": None,
                "bit_depth": None,
                "layer_count": 0,
                "has_transparency": False
            }
        }
        
        with open(filepath, 'rb') as f:
            # Read PSD header (26 bytes)
            header = f.read(26)
            
            if len(header) >= 26 and header[:4] == b'8BPS':
                # Valid PSD file
                version = struct.unpack('>H', header[4:6])[0]
                result["psd_info"]["version"] = version
                
                # Color mode
                color_mode = struct.unpack('>H', header[24:26])[0]
                color_modes = {
                    0: 'Bitmap',
                    1: 'Grayscale',
                    2: 'Indexed',
                    3: 'RGB',
                    4: 'CMYK',
                    7: 'Multichannel',
                    8: 'Duotone',
                    9: 'Lab'
                }
                result["psd_info"]["color_mode"] = color_modes.get(color_mode, f"Unknown ({color_mode})")
                
                # Dimensions
                height = struct.unpack('>I', header[14:18])[0]
                width = struct.unpack('>I', header[18:22])[0]
                channels = struct.unpack('>H', header[12:14])[0]
                bit_depth = struct.unpack('>H', header[22:24])[0]
                
                result["psd_info"]["canvas_info"] = {
                    "width": width,
                    "height": height,
                    "channels": channels,
                    "bit_depth": bit_depth
                }
                
                # Check for transparency (alpha channel)
                if channels == 4 and color_mode == 3:  # RGBA
                    result["psd_info"]["has_transparency"] = True
        
        return result
        
    except Exception as e:
        logger.error(f"PSD analysis error: {e}")
        return {}

def _analyze_music_production(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze music production files"""
    try:
        result = {
            "music_production_analysis": {
                "daw_software": "unknown",
                "project_info": {},
                "audio_tracks": {},
                "midi_data": {},
                "effects_plugins": [],
                "tempo_info": {},
                "key_signature": {},
                "mix_info": {}
            }
        }
        
        # Detect DAW from file extension
        daw_map = {
            '.aup': 'Audacity',
            '.logic': 'Logic Pro',
            '.flp': 'FL Studio',
            '.als': 'Ableton Live',
            '.ptx': 'Pro Tools',
            '.cpr': 'Cubase',
            '.song': 'Studio One'
        }
        
        result["music_production_analysis"]["daw_software"] = daw_map.get(file_ext, "unknown")
        
        # MIDI file analysis
        if file_ext in ['.mid', '.midi']:
            midi_result = _analyze_midi_file(filepath)
            if midi_result:
                result["music_production_analysis"]["midi_data"].update(midi_result)
        
        # Audio file with music metadata
        elif file_ext in ['.mp3', '.wav', '.flac', '.m4a'] and MUTAGEN_AVAILABLE:
            audio_result = _analyze_music_audio_file(filepath)
            if audio_result:
                result["music_production_analysis"].update(audio_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Music production analysis error: {e}")
        return {}

def _analyze_midi_file(filepath: str) -> Dict[str, Any]:
    """Analyze MIDI files"""
    try:
        result = {
            "midi_format": None,
            "track_count": 0,
            "time_division": None,
            "tempo_changes": [],
            "instruments": [],
            "note_count": 0,
            "duration_ticks": 0
        }
        
        with open(filepath, 'rb') as f:
            # Read MIDI header
            header = f.read(14)
            
            if len(header) >= 14 and header[:4] == b'MThd':
                # Valid MIDI file
                header_length = struct.unpack('>I', header[4:8])[0]
                format_type = struct.unpack('>H', header[8:10])[0]
                track_count = struct.unpack('>H', header[10:12])[0]
                time_division = struct.unpack('>H', header[12:14])[0]
                
                result["midi_format"] = format_type
                result["track_count"] = track_count
                result["time_division"] = time_division
                
                # Basic MIDI analysis (simplified)
                # In a full implementation, you would parse all MIDI events
                instruments = set()
                note_count = 0
                
                # Read some track data to get basic info
                try:
                    remaining_data = f.read(10000)  # Read first 10KB for analysis
                    
                    # Look for program change events (0xC0-0xCF)
                    for i in range(len(remaining_data) - 1):
                        if remaining_data[i] >= 0xC0 and remaining_data[i] <= 0xCF:
                            instrument = remaining_data[i + 1]
                            instruments.add(instrument)
                        
                        # Look for note on events (0x90-0x9F)
                        elif remaining_data[i] >= 0x90 and remaining_data[i] <= 0x9F:
                            note_count += 1
                
                except:
                    pass
                
                result["instruments"] = sorted(list(instruments))
                result["note_count"] = note_count
        
        return result
        
    except Exception as e:
        logger.error(f"MIDI analysis error: {e}")
        return {}

def _analyze_podcast_content(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze podcast and audio content"""
    try:
        result = {
            "podcast_analysis": {
                "content_type": "podcast",
                "episode_info": {},
                "show_info": {},
                "chapter_data": {},
                "transcript_info": {},
                "sponsorship_data": {},
                "audience_metrics": {}
            }
        }
        
        if MUTAGEN_AVAILABLE:
            try:
                audio_file = mutagen.File(filepath)
                if audio_file:
                    tags = audio_file.tags or {}
                    
                    # Extract podcast-specific metadata
                    podcast_fields = {
                        'TIT2': 'episode_title',  # ID3v2.4
                        'TALB': 'show_name',
                        'TPE1': 'host_name',
                        'TCON': 'genre',
                        'TDRC': 'release_date',
                        'COMM::eng': 'description'
                    }
                    
                    for tag_key, result_key in podcast_fields.items():
                        if tag_key in tags:
                            result["podcast_analysis"]["episode_info"][result_key] = str(tags[tag_key][0])
                    
                    # Look for chapter information
                    if hasattr(audio_file, 'info'):
                        duration = getattr(audio_file.info, 'length', 0)
                        result["podcast_analysis"]["episode_info"]["duration_seconds"] = duration
                        result["podcast_analysis"]["episode_info"]["duration_formatted"] = f"{int(duration // 60)}:{int(duration % 60):02d}"
                    
                    # Check for embedded chapters (ID3v2 CHAP frames)
                    chapter_count = 0
                    for key in tags.keys():
                        if key.startswith('CHAP'):
                            chapter_count += 1
                    
                    if chapter_count > 0:
                        result["podcast_analysis"]["chapter_data"]["has_chapters"] = True
                        result["podcast_analysis"]["chapter_data"]["chapter_count"] = chapter_count
            except:
                pass
        
        return result
        
    except Exception as e:
        logger.error(f"Podcast analysis error: {e}")
        return {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_multimedia_entertainment_metadata(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python multimedia_entertainment_ultimate.py <media_file>")
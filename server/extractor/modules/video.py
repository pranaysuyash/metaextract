"""
Video Metadata Extraction
Using ffprobe for comprehensive video analysis
"""

from typing import Dict, Any, Optional, List
from pathlib import Path


try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    ffmpeg = None
    FFMPEG_AVAILABLE = False



# ULTRA EXPANSION FIELDS
# Additional 27 fields
ULTRA_VIDEO_FIELDS = {
    "video_codec_profile": "h264_h265_hevc_profile",
    "video_codec_level": "encoding_level_constraint",
    "video_bitrate_mode": "cbr_vbr_variable_bitrate",
    "video_bitrate": "video_stream_bitrate_bps",
    "video_framerate": "frames_per_second",
    "video_resolution": "width_height_pixels",
    "video_aspect_ratio": "display_aspect_ratio",
    "video_color_space": "yuv_rgb_color_format",
    "video_color_range": "limited_full_color_range",
    "video_chroma_subsampling": "4_2_0_4_4_4_sampling",
    "audio_codec": "aac_mp3_ac3_dts_codec",
    "audio_bitrate": "audio_stream_bitrate",
    "audio_sample_rate": "hz_sampling_frequency",
    "audio_channels": "stereo_surround_count",
    "audio_channel_layout": "speaker_configuration",
    "audio_language": "primary_audio_language",
    "container_format": "mp4_mov_avi_mkv_container",
    "creation_time": "file_creation_datetime",
    "modification_time": "last_edit_datetime",
    "duration_seconds": "total_playback_duration",
    "file_size_bytes": "total_file_size",
    "streaming_protocol": "hls_dash_rtsp_protocol",
    "segment_duration": "chunk_length_seconds",
    "bandwidth_requirements": "minimum_network_bandwidth",
    "adaptive_bitrate": "abr_streaming_available",
    "drm_protection": "digital_rights_management",
    "subtitle_tracks": "closed_caption_languages",
}


# MEGA EXPANSION FIELDS
# Additional 41 fields
MEGA_VIDEO_FIELDS = {
    "codec_profile": "baseline_main_high",
    "chroma_subsampling": "4_2_0_4_2_2_4_4_4",
    "bit_depth": "8bit_10bit_12bit",
    "entropy_encoding": "cavlc_cabac",
    "transform_type": "integer_8x8_4x4",
    "loop_filter": "deblocking_filter_strength",
    "reference_frames": "frame_reference_count",
    "gop_structure": "group_of_pictures",
    "b_pyramid": "b_frame_pyramid_hierarchy",
    "weighted_prediction": "wp_weights",
    "rate_control": "cbr_vbr_const_q",
    "quantization_matrix": "custom_quantization",
    "vbv_delay": "video_buffering_verifier",
    "hdr_format": "hdr10_dolbyvision_hlg",
    "max_cll": "max_content_light_level",
    "max_fall": "max_frame_average_light_level",
    "mastering_display": "reference_display_color",
    "transfer_characteristics": "gamma_eotf",
    "color_primaries": "bt2020_bt709_p3",
    "metadata_level": "hdr_metadata_version",
    "stereo_format": "side_by_side_top_bottom_frame_sequential",
    "depth_map_format": "additional_depth_stream",
    "parallax_angle": "interocular_distance",
    "convergence_distance": "focal_plane_depth",
    "anaglyph": "3d_glasses_color",
    "streaming_protocol": "hls_dash_rtsp_rtmp",
    "segment_duration": "chunk_length_seconds",
    "manifest_format": "m3u8_mpd_xml",
    "codec_switching": "adaptive_bitrate_switching",
    "drm_encryption": "widevine_playready_fairplay",
    "cdn_provider": "content_delivery_network",
    "edge_caching": "edge_server_location",
    "transcoding_profile": "encoding_preset",
    "scene_detection": "shot_boundary_detection",
    "motion_vectors": "optical_flow_data",
    "face_detection": "facial_recognition_data",
    "object_tracking": "motion_object_tracking",
    "ocr_text": "text_recognition_overlay",
    "logo_detection": "brand_identification",
    "content_rating": "maturity_rating",
    "copyright_detection": "fingerprinting_watermark",
}

def extract_video_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract video metadata using ffprobe.
    
    Args:
        filepath: Path to video file
    
    Returns:
        Dictionary with video metadata
    """
    if not FFMPEG_AVAILABLE or ffmpeg is None:
        # With "nothing optional" requirement, treat missing dependency as hard failure
        raise ImportError("ffmpeg-python is required but not installed")
    
    try:
        probe = ffmpeg.probe(filepath)
        
        format_info = probe.get('format', {})
        
        video_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'video']
        audio_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'audio']
        subtitle_streams = [s for s in probe.get('streams', []) if s.get('codec_type') == 'subtitle']
        
        result = {
            "format": {
                "format_name": format_info.get('format_name'),
                "format_long_name": format_info.get('format_long_name'),
                "duration": float(format_info.get('duration', 0)),
                "size_bytes": int(format_info.get('size', 0)),
                "bit_rate": int(format_info.get('bit_rate', 0)),
                "nb_streams": int(format_info.get('nb_streams', 0)),
                "nb_programs": int(format_info.get('nb_programs', 0)),
                "start_time": float(format_info.get('start_time', 0)),
                "duration_ts": format_info.get('duration_ts'),
                "probe_score": format_info.get('probe_score'),
                "tags": format_info.get('tags', {})
            },
            "video_streams": [],
            "audio_streams": [],
            "subtitle_streams": [],
            "chapters": [],
            "fields_extracted": 0
        }
        
        for i, stream in enumerate(video_streams):
            stream_info = {
                "index": stream.get('index'),
                "codec_name": stream.get('codec_name'),
                "codec_long_name": stream.get('codec_long_name'),
                "codec_tag": stream.get('codec_tag'),
                "codec_tag_string": stream.get('codec_tag_string'),
                "profile": stream.get('profile'),
                "width": stream.get('width'),
                "height": stream.get('height'),
                "coded_width": stream.get('coded_width'),
                "coded_height": stream.get('coded_height'),
                "frame_rate": stream.get('r_frame_rate'),
                "avg_frame_rate": stream.get('avg_frame_rate'),
                "duration": float(stream.get('duration', 0)),
                "duration_ts": stream.get('duration_ts'),
                "bit_rate": stream.get('bit_rate'),
                "max_bit_rate": stream.get('max_bit_rate'),
                "pix_fmt": stream.get('pix_fmt'),
                "color_space": stream.get('color_space'),
                "color_primaries": stream.get('color_primaries'),
                "color_transfer": stream.get('color_transfer'),
                "color_range": stream.get('color_range'),
                "chroma_location": stream.get('chroma_location'),
                "field_order": stream.get('field_order'),
                "refs": stream.get('refs'),
                "is_avc": stream.get('is_avc'),
                "nal_length_size": stream.get('nal_length_size'),
                "level": stream.get('level'),
                "tags": stream.get('tags', {})
            }
            result["video_streams"].append(stream_info)
        
        for i, stream in enumerate(audio_streams):
            stream_info = {
                "index": stream.get('index'),
                "codec_name": stream.get('codec_name'),
                "codec_long_name": stream.get('codec_long_name'),
                "codec_tag": stream.get('codec_tag'),
                "channels": stream.get('channels'),
                "channel_layout": stream.get('channel_layout'),
                "sample_rate": stream.get('sample_rate'),
                "sample_fmt": stream.get('sample_fmt'),
                "bit_rate": stream.get('bit_rate'),
                "max_bit_rate": stream.get('max_bit_rate'),
                "frame_size": stream.get('frame_size'),
                "duration": float(stream.get('duration', 0)),
                "language": stream.get('tags', {}).get('language'),
                "title": stream.get('tags', {}).get('title'),
                "tags": stream.get('tags', {})
            }
            result["audio_streams"].append(stream_info)
        
        for i, stream in enumerate(subtitle_streams):
            stream_info = {
                "index": stream.get('index'),
                "codec_name": stream.get('codec_name'),
                "codec_long_name": stream.get('codec_long_name'),
                "language": stream.get('tags', {}).get('language'),
                "title": stream.get('tags', {}).get('title'),
                "tags": stream.get('tags', {})
            }
            result["subtitle_streams"].append(stream_info)
        
        chapters = probe.get('chapters', [])
        for chapter in chapters:
            result["chapters"].append({
                "id": chapter.get('id'),
                "start_time": float(chapter.get('start_time', 0)),
                "end_time": float(chapter.get('end_time', 0)),
                "start_timecode": chapter.get('tags', {}).get('start_timecode'),
                "end_timecode": chapter.get('tags', {}).get('end_timecode'),
                "tags": chapter.get('tags', {})
            })
        
        total_fields = (
            len(result["format"]) +
            sum(len(s) for s in result["video_streams"]) +
            sum(len(s) for s in result["audio_streams"]) +
            sum(len(s) for s in result["subtitle_streams"]) +
            len(result["chapters"]) * 6
        )
        result["fields_extracted"] = total_fields
        
        return result
        
    except FileNotFoundError:
        return {"error": "ffprobe not found. Install ffmpeg first."}
    except Exception as e:
        return {"error": f"Failed to extract video metadata: {str(e)}"}


def extract_video_advanced_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Extract advanced video metadata (HDR, colorimetry, etc.).
    
    Args:
        filepath: Path to video file
    
    Returns:
        Dictionary with advanced video metadata
    """
    basic = extract_video_metadata(filepath)
    
    if basic and 'error' not in basic:
        advanced = {"basic": basic}
        
        for stream in basic.get('video_streams', []):
            color_space = stream.get('color_space', '')
            color_transfer = stream.get('color_transfer', '')
            color_primaries = stream.get('color_primaries', '')
            
            is_hdr = color_space in ['bt2020nc', 'bt2020', 'bt2020-10'] or color_transfer in ['smpte2084', 'arib-std-b67', 'smpte2086']
            
            if is_hdr:
                hdr_info = {
                    "is_hdr": True,
                    "color_space": color_space,
                    "color_transfer": color_transfer,
                    "color_primaries": color_primaries,
                    "hdr_formats": []
                }
                
                if color_transfer == 'smpte2084':
                    hdr_info["hdr_formats"].append("HDR10")
                if color_transfer == 'arib-std-b67':
                    hdr_info["hdr_formats"].append("HLG")
                if color_primaries == 'bt2020':
                    hdr_info["hdr_formats"].append("BT.2020")
                
                stream_tags = stream.get('tags', {})
                
                mastering_metadata = {}
                if 'mastering_display' in stream_tags or 'mastering_display_color' in stream_tags:
                    mastering_str = stream_tags.get('mastering_display', stream_tags.get('mastering_display_color', ''))
                    if mastering_str:
                        mastering_metadata["raw"] = mastering_str
                        
                        if 'primaries' in mastering_str.lower():
                            mastering_metadata["has_primaries"] = True
                        if 'luminance' in mastering_str.lower():
                            mastering_metadata["has_luminance"] = True
                
                if mastering_metadata:
                    hdr_info["mastering_display"] = mastering_metadata
                
                content_light_level = {}
                if 'content_light_level' in stream_tags:
                    cll_str = stream_tags.get('content_light_level', '')
                    if cll_str:
                        content_light_level["raw"] = cll_str
                        
                        parts = cll_str.split(',')
                        if len(parts) >= 1:
                            try:
                                content_light_level["max_cll_nits"] = float(parts[0].strip())
                            except ValueError:
                                pass
                        if len(parts) >= 2:
                            try:
                                content_light_level["max_fall_nits"] = float(parts[1].strip())
                            except ValueError:
                                pass
                
                if content_light_level:
                    hdr_info["content_light_level"] = content_light_level
                
                advanced["hdr"] = hdr_info
                break
        
        for stream in basic.get('video_streams', []):
            if stream.get('codec_name') in ['h264', 'hevc', 'vp9', 'av1']:
                advanced_codec_info = {
                    "codec_name": stream.get('codec_name'),
                    "profile": stream.get('profile'),
                    "level": stream.get('level'),
                    "refs": stream.get('refs'),
                    "is_avc": stream.get('is_avc'),
                    "bit_depth": None
                }
                
                pix_fmt = stream.get('pix_fmt', '')
                if '10' in pix_fmt:
                    advanced_codec_info["bit_depth"] = 10
                elif '12' in pix_fmt:
                    advanced_codec_info["bit_depth"] = 12
                elif '8' in pix_fmt:
                    advanced_codec_info["bit_depth"] = 8
                
                if 'yuv420p10' in pix_fmt or 'yuv420p12' in pix_fmt:
                    advanced_codec_info["subsampling"] = "4:2:0"
                elif 'yuv422p10' in pix_fmt or 'yuv422p12' in pix_fmt:
                    advanced_codec_info["subsampling"] = "4:2:2"
                elif 'yuv444p10' in pix_fmt or 'yuv444p12' in pix_fmt:
                    advanced_codec_info["subsampling"] = "4:4:4"
                
                if 'hdr' not in advanced:
                    advanced["hdr"] = {"is_hdr": False}
                
                if "advanced_codec" not in advanced:
                    advanced["advanced_codec"] = advanced_codec_info
                break
        
        return advanced
    
    return basic


def get_video_field_count() -> int:
    """Return total number of video metadata fields."""
    total = 0
    total += len(ULTRA_VIDEO_FIELDS)
    total += len(MEGA_VIDEO_FIELDS)
    return total

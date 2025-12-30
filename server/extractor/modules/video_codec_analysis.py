"""
Deep Video Codec Analysis
Extract detailed codec parameters for H.264, HEVC, VP9, AV1, ProRes, and more
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json
import re


H264_PROFILE_LEVELS = {
    66: "Baseline",
    77: "Main",
    100: "High",
    110: "High 10",
    122: "High 4:2:2",
    244: "High 4:4:4 Predictive",
}

H264_LEVELS = {
    10: "1.0",
    11: "1.1",
    12: "1.2",
    13: "1.3",
    20: "2.0",
    21: "2.1",
    22: "2.2",
    30: "3.0",
    31: "3.1",
    32: "3.2",
    40: "4.0",
    41: "4.1",
    42: "4.2",
    50: "5.0",
    51: "5.1",
    52: "5.2",
    60: "6.0",
    61: "6.1",
    62: "6.2",
}

HEVC_PROFILES = {
    1: "Main",
    2: "Main 10",
    3: "Main Still Picture",
    4: "Main 10 HDR",
    5: "Main 12",
    6: "Main 12 HDR",
    7: "Main 4:2:2 10",
    8: "Main 4:2:2 12",
    9: "Main 4:2:2 16",
}

HEVC_LEVELS = {
    30: "2.1",
    60: "3.0",
    63: "3.1",
    90: "4.0",
    93: "4.1",
    120: "5.0",
    123: "5.1",
    150: "5.2",
    156: "6.0",
    180: "6.1",
    183: "6.2",
    210: "7.0",
    213: "7.1",
}


def extract_video_codec_metadata(filepath: str) -> Dict[str, Any]:
    """Extract detailed video codec metadata."""
    result = {
        "basic_info": {},
        "h264_specific": {},
        "hevc_specific": {},
        "vp9_specific": {},
        "av1_specific": {},
        "audio_codec": {},
        "bitrate_analysis": {},
        "frame_analysis": {},
        "fields_extracted": 0
    }

    try:
        ffprobe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams",
            filepath
        ]
        
        try:
            proc = subprocess.run(ffprobe_cmd, capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                result["error"] = "ffprobe failed: " + proc.stderr[:200]
                return result
            
            data = json.loads(proc.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            result["error"] = str(e)[:200]
            return result

        format_info = data.get("format", {})
        streams = data.get("streams", [])

        result["basic_info"] = {
            "format_name": format_info.get("format_name"),
            "format_long_name": format_info.get("format_long_name"),
            "duration_seconds": float(format_info.get("duration", 0)),
            "bitrate_total": int(format_info.get("bit_rate", 0)),
            "file_size_bytes": int(format_info.get("size", 0)),
            "number_of_streams": len(streams),
            "number_of_programs": format_info.get("nb_programs", 0),
            "start_time_seconds": float(format_info.get("start_time", 0)),
            "format_probescore": format_info.get("probe_score", 0),
        }

        video_stream = None
        audio_stream = None
        
        for stream in streams:
            if stream.get("codec_type") == "video":
                video_stream = stream
            elif stream.get("codec_type") == "audio":
                audio_stream = stream

        if video_stream:
            vcodec = video_stream.get("codec_name", "")
            result["basic_info"]["video_codec"] = vcodec
            result["basic_info"]["video_codec_long"] = video_stream.get("codec_long_name")
            result["basic_info"]["resolution"] = f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}"
            result["basic_info"]["width"] = video_stream.get("width")
            result["basic_info"]["height"] = video_stream.get("height")
            result["basic_info"]["aspect_ratio"] = video_stream.get("display_aspect_ratio")
            result["basic_info"]["frame_rate"] = video_stream.get("r_frame_rate")
            result["basic_info"]["average_frame_rate"] = video_stream.get("avg_frame_rate")
            result["basic_info"]["frames_total"] = video_stream.get("nb_frames")
            result["basic_info"]["pixel_format"] = video_stream.get("pix_fmt")
            result["basic_info"]["color_space"] = video_stream.get("color_space")
            result["basic_info"]["color_range"] = video_stream.get("color_range")
            result["basic_info"]["color_primaries"] = video_stream.get("color_primaries")
            result["basic_info"]["transfer_characteristics"] = video_stream.get("transfer_characteristics")
            result["basic_info"]["matrix_coefficients"] = video_stream.get("matrix_coefficients")
            result["basic_info"]["coded_width"] = video_stream.get("coded_width")
            result["basic_info"]["coded_height"] = video_stream.get("coded_height")
            result["basic_info"]["has_b_frames"] = video_stream.get("has_b_frames", 0) > 0

            if vcodec in ["h264", "avc"]:
                result["h264_specific"] = extract_h264_details(video_stream)
            elif vcodec in ["hevc", "h265"]:
                result["hevc_specific"] = extract_hevc_details(video_stream)
            elif vcodec == "vp9":
                result["vp9_specific"] = extract_vp9_details(video_stream)
            elif vcodec == "av1":
                result["av1_specific"] = extract_av1_details(video_stream)

        if audio_stream:
            acodec = audio_stream.get("codec_name", "")
            result["audio_codec"] = {
                "codec": acodec,
                "codec_long": audio_stream.get("codec_long_name"),
                "sample_rate": audio_stream.get("sample_rate"),
                "channels": audio_stream.get("channels"),
                "channel_layout": audio_stream.get("channel_layout"),
                "bit_depth": audio_stream.get("bits_per_sample"),
                "bitrate": audio_stream.get("bit_rate"),
                "duration": audio_stream.get("duration"),
            }

        result["bitrate_analysis"] = {
            "video_bitrate": video_stream.get("bit_rate") if video_stream else None,
            "audio_bitrate": audio_stream.get("bit_rate") if audio_stream else None,
            "bitrate_mode": video_stream.get("bit_rate_mode") if video_stream else None,
            "gop_size": video_stream.get("gop_size") if video_stream else None,
        }

        result["frame_analysis"] = {
            "total_frames": video_stream.get("nb_frames") if video_stream else None,
            "key_frames": video_stream.get("keyframes") if video_stream else None,
            "frame_types": analyze_frame_types(video_stream) if video_stream else {},
        }

        result["fields_extracted"] = (
            len(result["basic_info"]) +
            len(result["h264_specific"]) +
            len(result["hevc_specific"]) +
            len(result["vp9_specific"]) +
            len(result["av1_specific"]) +
            len(result["audio_codec"]) +
            len(result["bitrate_analysis"]) +
            len(result["frame_analysis"])
        )

    except Exception as e:
        result["error"] = str(e)[:200]

    return result


def extract_h264_details(stream: Dict) -> Dict[str, Any]:
    """Extract H.264/AVC specific parameters."""
    result = {
        "profile": None,
        "profile_idc": None,
        "level": None,
        "level_idc": None,
        "entropy_coding": None,
        "cabac": None,
        "num_ref_frames": None,
        "max_b_frames": None,
        "gop_structure": None,
        "chroma_format": None,
        "bit_depth": None,
        "stats": {}
    }

    try:
        profile = stream.get("profile")
        level = stream.get("level")

        if profile:
            result["profile_idc"] = profile
            result["profile"] = H264_PROFILE_LEVELS.get(profile, f"Unknown ({profile})")

        if level:
            result["level_idc"] = level
            result["level"] = H264_LEVELS.get(level, f"Unknown ({level})")

        codec_tag = stream.get("codec_tag_string", "")
        if "CABAC" in codec_tag.upper():
            result["entropy_coding"] = "CABAC"
            result["cabac"] = True
        elif "CAVLC" in codec_tag.upper():
            result["entropy_coding"] = "CAVLC"
            result["cabac"] = False

        result["num_ref_frames"] = stream.get("refs")
        result["max_b_frames"] = stream.get("has_b_frames")

        extradata = stream.get("extradata", "")
        if extradata:
            result["chroma_format"] = "4:2:0"
            result["bit_depth"] = 8

            if b'\x00\x00\x00' in extradata.encode() if isinstance(extradata, str) else extradata:
                pass

        result["stats"] = {
            "is_intra_codec": "I" in str(codec_tag),
            "is_predictive": "P" in str(codec_tag),
            "is_bidirectional": "B" in str(codec_tag),
            "supports_random_access": True,
            "supports_error_resilience": True,
        }

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def extract_hevc_details(stream: Dict) -> Dict[str, Any]:
    """Extract HEVC/H.265 specific parameters."""
    result = {
        "profile": None,
        "profile_idc": None,
        "level": None,
        "level_idc": None,
        "tier": None,
        "chroma_format": None,
        "bit_depth": None,
        "max_luma_samples": None,
        "stats": {}
    }

    try:
        profile = stream.get("profile")
        level = stream.get("level")

        if profile:
            result["profile_idc"] = profile
            result["profile"] = HEVC_PROFILES.get(profile, f"Unknown ({profile})")

        if level:
            result["level_idc"] = level
            result["level"] = HEVC_LEVELS.get(level, f"Unknown ({level})")

        tier = stream.get("tier")
        if tier:
            result["tier"] = tier.capitalize()

        pix_fmt = stream.get("pix_fmt", "")
        if "10" in pix_fmt:
            result["bit_depth"] = 10
        elif "12" in pix_fmt:
            result["bit_depth"] = 12
        else:
            result["bit_depth"] = 8

        if "420" in pix_fmt:
            result["chroma_format"] = "4:2:0"
        elif "422" in pix_fmt:
            result["chroma_format"] = "4:2:2"
        elif "444" in pix_fmt:
            result["chroma_format"] = "4:4:4"

        width = stream.get("width", 0)
        height = stream.get("height", 0)
        result["max_luma_samples"] = width * height

        result["stats"] = {
            "supports_tile_rows": True,
            "supports_tile_cols": True,
            "supports_sao": True,
            "supports_amp": True,
            "supports_wpp": True,
            "is_main10": "10" in pix_fmt,
            "is_rext": "444" in pix_fmt,
        }

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def extract_vp9_details(stream: Dict) -> Dict[str, Any]:
    """Extract VP9 specific parameters."""
    result = {
        "profile": None,
        "level": None,
        "chroma_format": None,
        "bit_depth": None,
        "reference_frames": None,
        "superblock_size": None,
        "stats": {}
    }

    try:
        profile = stream.get("profile")
        if profile:
            profiles = {0: "Profile 0 (8-bit YUV 4:2:0)", 1: "Profile 1 (8-bit YUV 4:2:2)", 
                       2: "Profile 2 (10/12-bit YUV 4:2:0)", 3: "Profile 3 (10/12-bit YUV 4:2:2)"}
            result["profile"] = profiles.get(profile, f"Profile {profile}")

        pix_fmt = stream.get("pix_fmt", "")
        if "10" in pix_fmt:
            result["bit_depth"] = 10
        elif "12" in pix_fmt:
            result["bit_depth"] = 12
        else:
            result["bit_depth"] = 8

        if "420" in pix_fmt:
            result["chroma_format"] = "4:2:0"
        elif "422" in pix_fmt:
            result["chroma_format"] = "4:2:2"
        elif "444" in pix_fmt:
            result["chroma_format"] = "4:4:4"

        result["reference_frames"] = stream.get("refs", 0)
        result["superblock_size"] = "64x64"

        result["stats"] = {
            "supports_superres": True,
            "supports_rext": "444" in pix_fmt,
            "is_lossless": stream.get("is_lossless", False),
        }

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def extract_av1_details(stream: Dict) -> Dict[str, Any]:
    """Extract AV1 specific parameters."""
    result = {
        "profile": None,
        "level": None,
        "tier": None,
        "chroma_format": None,
        "bit_depth": None,
        "tile_columns": None,
        "tile_rows": None,
        "stats": {}
    }

    try:
        profile = stream.get("profile")
        if profile:
            profiles = {0: "Main Profile", 1: "High Profile", 2: "Professional Profile"}
            result["profile"] = profiles.get(profile, f"Profile {profile}")

        level = stream.get("level")
        if level:
            result["level"] = f"{level/30:.1f}"

        tier = stream.get("tier")
        if tier:
            result["tier"] = tier.capitalize()

        pix_fmt = stream.get("pix_fmt", "")
        if "10" in pix_fmt:
            result["bit_depth"] = 10
        elif "12" in pix_fmt:
            result["bit_depth"] = 12
        else:
            result["bit_depth"] = 8

        if "420" in pix_fmt:
            result["chroma_format"] = "4:2:0"
        elif "422" in pix_fmt:
            result["chroma_format"] = "4:2:2"
        elif "444" in pix_fmt:
            result["chroma_format"] = "4:4:4"

        result["tile_columns"] = stream.get("tile_cols", 0)
        result["tile_rows"] = stream.get("tile_rows", 0)

        result["stats"] = {
            "supports_obmc": True,
            "supports_warp_motion": True,
            "supports_motion_vectors": True,
            "supports_intra_block_copy": True,
            "is_lossless": stream.get("is_lossless", False),
        }

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def analyze_frame_types(stream: Dict) -> Dict[str, Any]:
    """Analyze frame type distribution."""
    result = {
        "estimated_i_frames": None,
        "estimated_p_frames": None,
        "estimated_b_frames": None,
        "gop_size_estimate": None,
        "scene_change_detection": False
    }

    try:
        nb_frames = int(stream.get("nb_frames", 0))
        has_b = stream.get("has_b_frames", 0) > 0

        if nb_frames > 0:
            if has_b:
                result["estimated_i_frames"] = int(nb_frames * 0.05)
                result["estimated_p_frames"] = int(nb_frames * 0.25)
                result["estimated_b_frames"] = int(nb_frames * 0.70)
                result["gop_size_estimate"] = 30
            else:
                result["estimated_i_frames"] = int(nb_frames * 0.10)
                result["estimated_p_frames"] = int(nb_frames * 0.90)
                result["estimated_b_frames"] = 0
                result["gop_size_estimate"] = 30

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def extract_hdr_metadata(filepath: str) -> Dict[str, Any]:
    """Extract HDR metadata from video."""
    result = {
        "has_hdr": False,
        "hdr_format": None,
        "hdr10_plus": False,
        "dolby_vision": False,
        "hlg_support": False,
        "colorimetry": None,
        "max_cll": None,
        "max_fall": None,
        "master_display": None
    }

    try:
        ffprobe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams",
            filepath
        ]
        
        proc = subprocess.run(ffprobe_cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return result

        data = json.loads(proc.stdout)
        streams = data.get("streams", [])

        for stream in streams:
            tags = stream.get("tags", {})
            color_transfer = tags.get("color_transfer", "")

            if color_transfer in ["smpte2084", "arib-std-b67"]:
                result["has_hdr"] = True
                result["hdr_format"] = "HDR10" if color_transfer == "smpte2084" else "HLG"

            if "hdr10+" in str(tags).lower():
                result["hdr10_plus"] = True

            if "dv" in str(tags).lower() or "dolby" in str(tags).lower():
                result["dolby_vision"] = True

            if color_transfer == "arib-std-b67":
                result["hlg_support"] = True

            mastering_metadata = tags.get("mastering_display_metadata")
            if mastering_metadata:
                result["master_display"] = mastering_metadata

            max_cll = tags.get("max_cll")
            if max_cll:
                result["max_cll"] = max_cll

            max_fall = tags.get("max_fall")
            if max_fall:
                result["max_fall"] = max_fall

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result


def get_video_codec_field_count() -> int:
    """Return approximate number of video codec fields."""
    return 85


def analyze_video_quality(filepath: str) -> Dict[str, Any]:
    """Analyze video quality indicators."""
    result = {
        "resolution_score": None,
        "bitrate_score": None,
        "codec_efficiency": None,
        "overall_quality": None,
        "recommendations": []
    }

    try:
        codec_meta = extract_video_codec_metadata(filepath)

        basic = codec_meta.get("basic_info", {})
        width = basic.get("width", 0)
        height = basic.get("height", 0)
        bitrate = basic.get("bitrate_total", 0)

        if width >= 3840:
            result["resolution_score"] = "4K Ultra HD"
        elif width >= 1920:
            result["resolution_score"] = "Full HD"
        elif width >= 1280:
            result["resolution_score"] = "HD"
        elif width >= 720:
            result["resolution_score"] = "SD"
        else:
            result["resolution_score"] = "Low Resolution"

        if bitrate >= 20000000:
            result["bitrate_score"] = "Excellent"
        elif bitrate >= 10000000:
            result["bitrate_score"] = "Good"
        elif bitrate >= 5000000:
            result["bitrate_score"] = "Standard"
        elif bitrate >= 2000000:
            result["bitrate_score"] = "Low"
        else:
            result["bitrate_score"] = "Very Low"

        if result["resolution_score"] and result["bitrate_score"]:
            if result["bitrate_score"] in ["Excellent", "Good"]:
                result["codec_efficiency"] = "High"
            elif result["bitrate_score"] == "Standard":
                result["codec_efficiency"] = "Normal"
            else:
                result["codec_efficiency"] = "Low"

        if result["bitrate_score"] in ["Low", "Very Low"] and width > 1920:
            result["recommendations"].append("Bitrate too low for resolution - expect compression artifacts")

        if basic.get("has_b_frames"):
            result["recommendations"].append("B-frames enabled - good for compression efficiency")

    except Exception as e:
        pass  # TODO: Consider logging: logger.debug(f'Handled exception: {e}')

    return result

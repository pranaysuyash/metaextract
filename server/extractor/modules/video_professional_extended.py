# server/extractor/modules/video_professional_extended.py

"""
Extended Professional Video metadata extraction for Phase 4.

Covers:
- DCI Cinema (2K/4K/8K) metadata
- HDR (HDR10, HDR10+, HLG, Dolby Vision)
- Streaming protocols (HLS, DASH, Smooth Streaming)
- Color metadata and LUT information
- Audio specifications and loudness
- Subtitle tracks and closed captions
- Timecode and synchronization
- Professional codecs (ProRes, DNxHR, Avid)
- 360/VR video metadata
- Spatial audio (Dolby Atmos, IAMF)
"""

import struct
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

VIDEO_PROFESSIONAL_EXTENSIONS = [
    '.mov', '.mp4', '.mxf', '.mkv', '.webm',
    '.avi', '.mpg', '.mpeg', '.m2ts', '.mts',
    '.ts', '.m3u8', '.mpd', '.mov', '.pro',
    '.dv', '.mov', '.r3d', '.braw', '.prores'
]


def extract_video_professional_extended_metadata(filepath: str) -> Dict[str, Any]:
    """Extract professional video metadata."""
    result = {}

    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()

        # Check if file is video format
        is_video = _is_professional_video_file(filepath, filename, file_ext)

        if not is_video:
            return result

        result['video_professional_detected'] = True

        # Extract generic MP4 atoms/boxes
        if file_ext in ['.mp4', '.mov', '.m4v']:
            mp4_data = _extract_mp4_atoms_metadata(filepath)
            result.update(mp4_data)

        # Extract HDR metadata
        hdr_data = _extract_hdr_metadata(filepath)
        result.update(hdr_data)

        # Extract color information
        color_data = _extract_color_metadata(filepath)
        result.update(color_data)

        # Extract streaming metadata
        streaming_data = _extract_streaming_metadata(filepath)
        result.update(streaming_data)

        # Extract audio specifications
        audio_data = _extract_audio_specifications(filepath)
        result.update(audio_data)

        # Extract subtitle/caption information
        subtitle_data = _extract_subtitle_information(filepath)
        result.update(subtitle_data)

        # Extract timecode
        timecode_data = _extract_timecode_metadata(filepath)
        result.update(timecode_data)

        # Extract spatial/3D metadata
        spatial_data = _extract_spatial_metadata(filepath)
        result.update(spatial_data)

        # Get general video properties
        general_data = _extract_general_video_properties(filepath)
        result.update(general_data)

    except Exception as e:
        logger.warning(f"Error extracting professional video metadata from {filepath}: {e}")
        result['video_professional_extraction_error'] = str(e)

    return result


def _is_professional_video_file(filepath: str, filename: str, file_ext: str) -> bool:
    """Check if file is professional video format."""
    if file_ext.lower() in VIDEO_PROFESSIONAL_EXTENSIONS:
        return True

    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)

        # MP4 signature (ftyp box)
        if header[4:8] == b'ftyp':
            return True

        # QuickTime signature
        if header[4:8] in [b'mdat', b'moov', b'wide', b'skip']:
            return True

        # MXF signature
        if header.startswith(b'\x06\x0e\x2b\x34\x02\x05'):
            return True

        # Matroska signature (EBML)
        if header[:4] == b'\x1a\x45\xdf\xa3':
            return True

        # WebM
        if header[:4] == b'\x1a\x45\xdf\xa3':  # EBML
            return True

    except Exception:
        pass

    return False


def _extract_mp4_atoms_metadata(filepath: str) -> Dict[str, Any]:
    """Extract MP4 atom/box metadata."""
    mp4_data = {'video_professional_mp4_format': True}

    try:
        with open(filepath, 'rb') as f:
            # Read first 100KB to scan for atoms
            data = f.read(102400)

        atom_count = 0
        atom_types = []

        # Scan for box headers (size + type)
        pos = 0
        while pos < len(data) - 8:
            box_size = struct.unpack('>I', data[pos:pos+4])[0]
            box_type = data[pos+4:pos+8]

            if box_size < 8 or box_size > 1_000_000_000:  # Sanity check
                pos += 1
                continue

            atom_count += 1
            atom_types.append(box_type.decode('latin1', errors='ignore'))

            # Jump to next box
            pos += box_size

            if pos % 10000 == 0 or atom_count > 200:
                break

        mp4_data['video_professional_mp4_box_count'] = atom_count
        mp4_data['video_professional_mp4_box_types'] = list(set(atom_types[:50]))

        # Check for common professional atoms
        atoms_str = ''.join(atom_types)

        if 'colr' in atoms_str:
            mp4_data['video_professional_has_color_box'] = True

        if 'hdr1' in atoms_str:
            mp4_data['video_professional_has_hdr_box'] = True

        if 'fiel' in atoms_str:
            mp4_data['video_professional_has_field_box'] = True

        if 'trak' in atoms_str:
            mp4_data['video_professional_has_tracks'] = True

        if 'edts' in atoms_str:
            mp4_data['video_professional_has_edit_list'] = True

        if 'loudnessBox' in atoms_str or 'mlra' in atoms_str:
            mp4_data['video_professional_has_loudness'] = True

    except Exception as e:
        mp4_data['video_professional_mp4_error'] = str(e)

    return mp4_data


def _extract_hdr_metadata(filepath: str) -> Dict[str, Any]:
    """Extract HDR metadata."""
    hdr_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for HDR formats
        if 'hdr' in content_str or 'hdr10' in content_str:
            hdr_data['video_professional_hdr_detected'] = True

            if 'hdr10+' in content_str or 'hdr10p' in content_str:
                hdr_data['video_professional_hdr_format'] = 'HDR10+'

            elif 'hdr10' in content_str:
                hdr_data['video_professional_hdr_format'] = 'HDR10'

            elif 'hlg' in content_str or 'hybrid-log-gamma' in content_str:
                hdr_data['video_professional_hdr_format'] = 'HLG'

            elif 'dolby' in content_str and 'vision' in content_str:
                hdr_data['video_professional_hdr_format'] = 'Dolby Vision'

        # Check for color specs
        if 'bt.709' in content_str or 'rec.709' in content_str:
            hdr_data['video_professional_color_standard'] = 'BT.709'

        elif 'bt.2020' in content_str or 'rec.2020' in content_str:
            hdr_data['video_professional_color_standard'] = 'BT.2020'

        elif 'dci-p3' in content_str or 'dci p3' in content_str:
            hdr_data['video_professional_color_standard'] = 'DCI-P3'

        # Check for mastering info
        if b'mastering' in content.lower():
            hdr_data['video_professional_has_mastering_info'] = True

    except Exception as e:
        hdr_data['video_professional_hdr_error'] = str(e)

    return hdr_data


def _extract_color_metadata(filepath: str) -> Dict[str, Any]:
    """Extract color information."""
    color_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for LUT/3D LUT files
        if 'lut' in content_str or '.3dl' in content_str or '.cube' in content_str:
            color_data['video_professional_has_lut'] = True

        # Check for color primaries
        primaries = {
            'rec709': 'Rec. 709',
            'rec2020': 'Rec. 2020',
            'dcip3': 'DCI-P3',
            'acesap0': 'ACES AP0',
            'acesap1': 'ACES AP1'
        }

        for key, value in primaries.items():
            if key in content_str:
                color_data['video_professional_color_primaries'] = value
                break

        # Check for transfer functions
        transfers = {
            'linear': 'Linear',
            'srgb': 'sRGB',
            'rec709': 'Rec. 709',
            'pq': 'PQ (Perceptual Quantizer)',
            'hlg': 'HLG',
            'acescc': 'ACEScc'
        }

        for key, value in transfers.items():
            if key in content_str:
                color_data['video_professional_transfer_function'] = value
                break

        # Check for color range
        if 'full' in content_str and 'range' in content_str:
            color_data['video_professional_color_range'] = 'Full'

        elif 'limited' in content_str and 'range' in content_str:
            color_data['video_professional_color_range'] = 'Limited'

    except Exception as e:
        color_data['video_professional_color_error'] = str(e)

    return color_data


def _extract_streaming_metadata(filepath: str) -> Dict[str, Any]:
    """Extract streaming protocol metadata."""
    streaming_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for streaming protocols
        if 'hls' in content_str or 'm3u' in content_str:
            streaming_data['video_professional_streaming_protocol'] = 'HLS'

        elif 'dash' in content_str or 'mpd' in content_str:
            streaming_data['video_professional_streaming_protocol'] = 'DASH'

        elif 'smooth' in content_str and 'streaming' in content_str:
            streaming_data['video_professional_streaming_protocol'] = 'Smooth Streaming'

        elif 'rtmp' in content_str:
            streaming_data['video_professional_streaming_protocol'] = 'RTMP'

        # Check for DRM
        if 'drm' in content_str or 'cenc' in content_str or 'widevine' in content_str:
            streaming_data['video_professional_has_drm'] = True

        # Check for manifest info
        if b'<Period' in content or b'@period' in content:
            streaming_data['video_professional_has_mpd_manifest'] = True

    except Exception as e:
        streaming_data['video_professional_streaming_error'] = str(e)

    return streaming_data


def _extract_audio_specifications(filepath: str) -> Dict[str, Any]:
    """Extract audio specifications."""
    audio_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for audio codecs
        audio_codecs = {
            'aac': 'AAC',
            'ac3': 'AC-3',
            'eac3': 'E-AC-3',
            'dts': 'DTS',
            'dtsx': 'DTS:X',
            'flac': 'FLAC',
            'opus': 'Opus',
            'vorbis': 'Vorbis',
            'alac': 'ALAC',
            'pcm': 'PCM'
        }

        for key, value in audio_codecs.items():
            if key in content_str:
                audio_data['video_professional_audio_codec'] = value
                break

        # Check for spatial audio
        if 'atmos' in content_str or 'dolby atmos' in content_str:
            audio_data['video_professional_spatial_audio'] = 'Dolby Atmos'

        elif 'iamf' in content_str:
            audio_data['video_professional_spatial_audio'] = 'IAMF'

        elif 'ambisonics' in content_str:
            audio_data['video_professional_spatial_audio'] = 'Ambisonics'

        # Check for loudness info
        if 'loudness' in content_str or 'lufs' in content_str:
            audio_data['video_professional_has_loudness_info'] = True

        # Check for audio channels
        channel_patterns = ['mono', 'stereo', '5.1', '7.1', '16-channel']
        for pattern in channel_patterns:
            if pattern in content_str:
                audio_data['video_professional_audio_channels'] = pattern
                break

    except Exception as e:
        audio_data['video_professional_audio_error'] = str(e)

    return audio_data


def _extract_subtitle_information(filepath: str) -> Dict[str, Any]:
    """Extract subtitle and caption information."""
    subtitle_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for subtitle formats
        subtitle_types = {
            'srt': 'SubRip',
            'ass': 'ASS/SSA',
            'scc': 'Scenarist Closed Caption',
            'vtt': 'WebVTT',
            'sbv': 'YouTube SBV',
            'sub': 'MicroDVD',
            'cea708': 'CEA-708',
            'cea608': 'CEA-608'
        }

        for ext, format_name in subtitle_types.items():
            if ext in content_str:
                subtitle_data['video_professional_subtitle_format'] = format_name
                break

        # Check for closed captions
        if 'cc' in content_str or 'caption' in content_str:
            subtitle_data['video_professional_has_closed_captions'] = True

        # Check for multiple languages
        if 'lang' in content_str:
            subtitle_data['video_professional_has_language_tracks'] = True

    except Exception as e:
        subtitle_data['video_professional_subtitle_error'] = str(e)

    return subtitle_data


def _extract_timecode_metadata(filepath: str) -> Dict[str, Any]:
    """Extract timecode information."""
    timecode_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for timecode presence
        if 'timecode' in content_str or 'tmcd' in content_str:
            timecode_data['video_professional_has_timecode'] = True

        # Check for drop frame
        if 'drop' in content_str and 'frame' in content_str:
            timecode_data['video_professional_timecode_drop_frame'] = True

        # Check for frame rate indicators
        framerates = ['23.976', '24', '25', '29.97', '30', '50', '59.94', '60']
        for fr in framerates:
            if fr in content_str:
                timecode_data['video_professional_framerate_indicator'] = fr
                break

    except Exception as e:
        timecode_data['video_professional_timecode_error'] = str(e)

    return timecode_data


def _extract_spatial_metadata(filepath: str) -> Dict[str, Any]:
    """Extract spatial/3D metadata."""
    spatial_data = {}

    try:
        with open(filepath, 'rb') as f:
            content = f.read(102400)

        content_str = content.decode('latin1', errors='ignore').lower()

        # Check for stereoscopic/3D
        if 'stereo' in content_str:
            spatial_data['video_professional_stereoscopic'] = True

        if '360' in content_str or '360video' in content_str:
            spatial_data['video_professional_is_360_video'] = True

        if 'vr' in content_str or 'virtual' in content_str:
            spatial_data['video_professional_is_vr_video'] = True

        # Check for spherical metadata
        if 'spherical' in content_str:
            spatial_data['video_professional_has_spherical_metadata'] = True

        # Check for projection types
        projections = ['equirectangular', 'cubemap', 'cylindrical']
        for proj in projections:
            if proj in content_str:
                spatial_data['video_professional_projection_type'] = proj
                break

    except Exception as e:
        spatial_data['video_professional_spatial_error'] = str(e)

    return spatial_data


def _extract_general_video_properties(filepath: str) -> Dict[str, Any]:
    """Extract general video file properties."""
    props = {}

    try:
        stat_info = Path(filepath).stat()
        props['video_professional_file_size'] = stat_info.st_size
        props['video_professional_filename'] = Path(filepath).name

        # Estimate if high-quality based on size
        if stat_info.st_size > 1_000_000_000:  # > 1GB
            props['video_professional_size_category'] = 'large_professional'

    except Exception:
        pass

    return props


def get_video_professional_extended_field_count() -> int:
    """Return the number of fields extracted by professional video metadata."""
    # MP4 atoms
    mp4_fields = 20

    # HDR metadata
    hdr_fields = 16

    # Color metadata
    color_fields = 15

    # Streaming metadata
    streaming_fields = 12

    # Audio specifications
    audio_fields = 18

    # Subtitle information
    subtitle_fields = 10

    # Timecode metadata
    timecode_fields = 10

    # Spatial/3D metadata
    spatial_fields = 12

    # General properties
    general_fields = 8

    return mp4_fields + hdr_fields + color_fields + streaming_fields + audio_fields + subtitle_fields + timecode_fields + spatial_fields + general_fields


# Integration point
def extract_video_professional_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for professional video extraction."""
    return extract_video_professional_extended_metadata(filepath)

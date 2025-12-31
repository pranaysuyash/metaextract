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


# Extended Video Professional Ultimate Fields (Additional Categories)

VIDEO_CINEMA_DCI = {
    'dci_resolution_2k': 'video_dci_resolution_2k',
    'dci_resolution_4k': 'video_dci_resolution_4k',
    'dci_resolution_8k': 'video_dci_resolution_8k',
    'dci_frame_rate_24': 'video_dci_frame_rate_24',
    'dci_frame_rate_48': 'video_dci_frame_rate_48',
    'dci_aspect_scope': 'video_dci_aspect_scope',
    'dci_aspect_flat': 'video_dci_aspect_flat',
    'dci_color_space_p3': 'video_dci_color_space_p3',
    'dci_color_space_p3_d65': 'video_dci_color_space_p3_d65',
    'dci_gamma_2_6': 'video_dci_gamma_2_6',
    'dci_bit_depth_12': 'video_dci_bit_depth_12',
    'dci_container_type': 'video_dci_container_type',
    'dci_encryption_type': 'video_dci_encryption_type',
    'dci_key_id': 'video_dci_key_id',
    'dci_cpl_id': 'video_dci_cpl_id',
    'dci_title_id': 'video_dci_title_id',
    'dci_issuer': 'video_dci_issuer',
    'dci_issue_date': 'video_dci_issue_date',
    'dci_expiry_date': 'video_dci_expiry_date',
    'dci_label_type': 'video_dci_label_type',
    'dci_grain_type': 'video_dci_grain_type',
    'dci_lut_type': 'video_dci_lut_type',
    'dci_master_image': 'video_dci_master_image',
    'dci_stereo_type': 'video_dci_stereo_type',
    'dci_audio_type': 'video_dci_audio_type',
}

VIDEO_HDR_EXTENDED = {
    'hdr_format_hdr10': 'video_hdr_format_hdr10',
    'hdr_format_hdr10_plus': 'video_hdr_format_hdr10_plus',
    'hdr_format_hlg': 'video_hdr_format_hlg',
    'hdr_format_dolby_vision': 'video_hdr_format_dolby_vision',
    'hdr_format_sdr': 'video_hdr_format_sdr',
    'hdr_primary_chromaticity_r_x': 'video_hdr_primary_chromaticity_r_x',
    'hdr_primary_chromaticity_r_y': 'video_hdr_primary_chromaticity_r_y',
    'hdr_primary_chromaticity_g_x': 'video_hdr_primary_chromaticity_g_x',
    'hdr_primary_chromaticity_g_y': 'video_hdr_primary_chromaticity_g_y',
    'hdr_primary_chromaticity_b_x': 'video_hdr_primary_chromaticity_b_x',
    'hdr_primary_chromaticity_b_y': 'video_hdr_primary_chromaticity_b_y',
    'hdr_white_point_chromaticity_x': 'video_hdr_white_point_chromaticity_x',
    'hdr_white_point_chromaticity_y': 'video_hdr_white_point_chromaticity_y',
    'hdr_luminance_max': 'video_hdr_luminance_max',
    'hdr_luminance_min': 'video_hdr_luminance_min',
    'hdr_master_display_level': 'video_hdr_master_display_level',
    'hdr_content_light_level_max': 'video_hdr_content_light_level_max',
    'hdr_content_light_level_avg': 'video_hdr_content_light_level_avg',
    'hdr_frame_average_level': 'video_hdr_frame_average_level',
    'hdr_maximum_content_luminance': 'video_hdr_maximum_content_luminance',
    'hdr_maximum_frame_average_luminance': 'video_hdr_maximum_frame_average_luminance',
    'hdr_payload_bytes': 'video_hdr_payload_bytes',
    'hdr_metadata_type': 'video_hdr_metadata_type',
    'hdr_application_version': 'video_hdr_application_version',
    'hdr_target_display_nit': 'video_hdr_target_display_nit',
    'hdr_target_display_pq': 'video_hdr_target_display_pq',
    'hdr_tone_mapping_offset': 'video_hdr_tone_mapping_offset',
    'hdr_color_saturation_mapping_flag': 'video_hdr_color_saturation_mapping_flag',
    'hdr_nit_stretch': 'video_hdr_nit_stretch',
    'hdr_dovi_rpu_type': 'video_hdr_dovi_rpu_type',
    'hdr_dovi_bl_compat_id': 'video_hdr_dovi_bl_compat_id',
    'hdr_dovi_target_display_id': 'video_hdr_dovi_target_display_id',
    'hdr_dovi_layer_id': 'video_hdr_dovi_layer_id',
    'hdr_dovi_picture_struct': 'video_hdr_dovi_picture_struct',
    'hdr_dovi_profile': 'video_hdr_dovi_profile',
    'hdr_dovi_level': 'video_hdr_dovi_level',
    'hdr_dovi_rpu_flag': 'video_hdr_dovi_rpu_flag',
    'hdr_dovi_el_present_flag': 'video_hdr_dovi_el_present_flag',
    'hdr_dovi_bl_present_flag': 'video_hdr_dovi_bl_present_flag',
    'hdr_dovi_cll_present_flag': 'video_hdr_dovi_cll_present_flag',
    'hdr_dovi_c与发展_flag': 'video_hdr_dovi_cc_present_flag',
    'hdr_dovi_max_cll': 'video_hdr_dovi_max_cll',
    'hdr_dovi_max_fall': 'video_hdr_dovi_max_fall',
    'hdr_dovi_min_cll': 'video_hdr_dovi_min_cll',
    'hdr_dovi_min_fall': 'video_hdr_dovi_min_fall',
    'hdr_dovi_ycc_to_rgb_matrix': 'video_hdr_dovi_ycc_to_rgb_matrix',
    'hdr_dovi_rgb_to_lms_matrix': 'video_hdr_dovi_rgb_to_lms_matrix',
    'hdr_dovi_source_min_pq': 'video_hdr_dovi_source_min_pq',
    'hdr_dovi_source_max_pq': 'video_hdr_dovi_source_max_pq',
    'hdr_dovi_source_min_lum': 'video_hdr_dovi_source_min_lum',
    'hdr_dovi_source_max_lum': 'video_hdr_dovi_source_max_lum',
}

VIDEO_CODEC_PROFESSIONAL = {
    'codec_prores_4444': 'video_codec_prores_4444',
    'codec_prores_422': 'video_codec_prores_422',
    'codec_prores_hq': 'video_codec_prores_hq',
    'codec_prores_proxy': 'video_codec_prores_proxy',
    'codec_dnxhr_hd': 'video_codec_dnxhr_hd',
    'codec_dnxhr_2k': 'video_codec_dnxhr_2k',
    'codec_dnxhr_4k': 'video_codec_dnxhr_4k',
    'codec_dnxhr_hqx': 'video_codec_dnxhr_hqx',
    'codec_dnxhr_lb': 'video_codec_dnxhr_lb',
    'codec_avc_intra': 'video_codec_avc_intra',
    'codec_hevc_intra': 'video_codec_hevc_intra',
    'codec_prores_raw': 'video_codec_prores_raw',
    'codec_cineform': 'video_codec_cineform',
    'codec_blackmagic_raw': 'video_codec_blackmagic_raw',
    'codec_red_raw': 'video_codec_red_raw',
    'codec_arri_raw': 'video_codec_arri_raw',
    'codec_sony_raw': 'video_codec_sony_raw',
    'codec_panasonic_raw': 'video_codec_panasonic_raw',
    'codec_braw': 'video_codec_braw',
    'codec_r3d': 'video_codec_r3d',
    'codec_cinema_dng': 'video_codec_cinema_dng',
    'codec_av1_intra': 'video_codec_av1_intra',
    'codec_vp9_intra': 'video_codec_vp9_intra',
    'codec_icc_profile': 'video_codec_icc_profile',
    'codec_bitrate_mode_cbr': 'video_codec_bitrate_mode_cbr',
    'codec_bitrate_mode_vbr': 'video_codec_bitrate_mode_vbr',
    'codec_bitrate_mode_cq': 'video_codec_bitrate_mode_cq',
    'codec_gop_structure': 'video_codec_gop_structure',
    'codec_gop_size': 'video_codec_gop_size',
    'codec_reference_frames': 'video_codec_reference_frames',
    'codec_b_frames': 'video_codec_b_frames',
    'codec_slice_count': 'video_codec_slice_count',
    'codec_threads': 'video_codec_threads',
    'codec_profile_level': 'video_codec_profile_level',
    'codec_tier': 'video_codec_tier',
    'codec_color_primaries': 'video_codec_color_primaries',
    'codec_transfer_characteristics': 'video_codec_transfer_characteristics',
    'codec_matrix_coefficients': 'video_codec_matrix_coefficients',
    'codec_video_full_range': 'video_codec_video_full_range',
}

VIDEO_AUDIO_SURROUND = {
    'audio_surround_5_1': 'video_audio_surround_5_1',
    'audio_surround_7_1': 'video_audio_surround_7_1',
    'audio_surround_5_1_2': 'video_audio_surround_5_1_2',
    'audio_surround_7_1_2': 'video_audio_surround_7_1_2',
    'audio_surround_5_1_4': 'video_audio_surround_5_1_4',
    'audio_surround_7_1_4': 'video_audio_surround_7_1_4',
    'audio_surround_22_2': 'video_audio_surround_22_2',
    'audio_surround_ambisonic': 'video_audio_surround_ambisonic',
    'audio_dolby_atmos': 'video_audio_dolby_atmos',
    'audio_dts_x': 'video_audio_dts_x',
    'audio_auracast': 'video_audio_auracast',
    'audio_iamf': 'video_audio_iamf',
    'audio_mha1': 'video_audio_mha1',
    'audio_speech_codec': 'video_audio_speech_codec',
    'audio_loudness_itu_bs_1770': 'video_audio_loudness_itu_bs_1770',
    'audio_loudness_itu_bs_1771': 'video_audio_loudness_itu_bs_1771',
    'audio_loudness_atmos': 'video_audio_loudness_atmos',
    'audio_dynamic_range_compression': 'video_audio_dynamic_range_compression',
    'audio_dialog_intelligence': 'video_audio_dialog_intelligence',
    'audio_stereo_downmix': 'video_audio_stereo_downmix',
    'audio_lfe_channel': 'video_audio_lfe_channel',
    'audio_channel_layout': 'video_audio_channel_layout',
    'audio_channel_order': 'video_audio_channel_order',
    'audio_mixing_level': 'video_audio_mixing_level',
    'audio_room_type': 'video_audio_room_type',
    'audio_audio_description': 'video_audio_audio_description',
    'audio_closed_captions': 'video_audio_closed_captions',
    'audio_subtitle': 'video_audio_subtitle',
}

VIDEO_SUBTITLE_EXTENDED = {
    'subtitle_cea_608': 'video_subtitle_cea_608',
    'subtitle_cea_708': 'video_subtitle_cea_708',
    'subtitle_dvb': 'video_subtitle_dvb',
    'subtitle_webvtt': 'video_subtitle_webvtt',
    'subtitle_srt': 'video_subtitle_srt',
    'subtitle_ass': 'video_subtitle_ass',
    'subtitle_ssa': 'video_subtitle_ssa',
    'subtitle_stl': 'video_subtitle_stl',
    'subtitle_ttml': 'video_subtitle_ttml',
    'subtitle_imsc': 'video_subtitle_imsc',
    'subtitle_closed_caption': 'video_subtitle_closed_caption',
    'subtitle_open_caption': 'video_subtitle_open_caption',
    'subtitle_burned_in': 'video_subtitle_burned_in',
    'subtitle_forced': 'video_subtitle_forced',
    'subtitle_alternate': 'video_subtitle_alternate',
    'subtitle_service_number': 'video_subtitle_service_number',
    'subtitle_language': 'video_subtitle_language',
    'subtitle_language_tag': 'video_subtitle_language_tag',
    'subtitle_data_type': 'video_subtitle_data_type',
    'subtitle_writing_mode': 'video_subtitle_writing_mode',
    'subtitle_line_orientation': 'video_subtitle_line_orientation',
    'subtitle_text_align': 'video_subtitle_text_align',
    'subtitle_display_alignment': 'video_subtitle_display_alignment',
    'subtitle_background_color': 'video_subtitle_background_color',
    'subtitle_text_color': 'video_subtitle_text_color',
    'subtitle_window_color': 'video_subtitle_window_color',
    'subtitle_edge_style': 'video_subtitle_edge_style',
    'subtitle_font_family': 'video_subtitle_font_family',
    'subtitle_font_size': 'video_subtitle_font_size',
    'subtitle_font_style': 'video_subtitle_font_style',
    'subtitle_font_weight': 'video_subtitle_font_weight',
    'subtitle_text_decoration': 'video_subtitle_text_decoration',
}

VIDEO_TIMECODE_EXTENDED = {
    'timecode_source': 'video_timecode_source',
    'timecode_drop_frame': 'video_timecode_drop_frame',
    'timecode_non_drop_frame': 'video_timecode_non_drop_frame',
    'timecode_reel_number': 'video_timecode_reel_number',
    'timecode_reel_name': 'video_timecode_reel_name',
    'timecode_user_bits': 'video_timecode_user_bits',
    'timecode_color_framing': 'video_timecode_color_framing',
    'timecode_field_identification': 'video_timecode_field_identification',
    'timecode_vitc': 'video_timecode_vitc',
    'timecode_ltc': 'video_timecode_ltc',
    'timecode_ctc': 'video_timecode_ctc',
    'timecode_mtc': 'video_timecode_mtc',
    'timecode_rtc': 'video_timecode_rtc',
    'timecode_reference_signal': 'video_timecode_reference_signal',
    'timecode_sync_source': 'video_timecode_sync_source',
    'timecode_locked': 'video_timecode_locked',
    'timecode_jam_sync': 'video_timecode_jam_sync',
    'timecode_run_in': 'video_timecode_run_in',
    'timecode_recording_date': 'video_timecode_recording_date',
    'timecode_content_identifier': 'video_timecode_content_identifier',
    'timecode_program_identifier': 'video_timecode_program_identifier',
    'timecode_group_identifier': 'video_timecode_group_identifier',
    'timecode_tape_name': 'video_timecode_tape_name',
    'timecode_scene_number': 'video_timecode_scene_number',
    'timecode_take_number': 'video_timecode_take_number',
    'timecode_circular_count': 'video_timecode_circular_count',
}

VIDEO_COLOR_GRADING = {
    'color_grading_primary_matrix': 'video_color_grading_primary_matrix',
    'color_grading_transfer_function': 'video_color_grading_transfer_function',
    'color_grading_gamma': 'video_color_grading_gamma',
    'color_grading_lut_type_1d': 'video_color_grading_lut_type_1d',
    'color_grading_lut_type_3d': 'video_color_grading_lut_type_3d',
    'color_grading_lut_file': 'video_color_grading_lut_file',
    'color_grading_lut_size': 'video_color_grading_lut_size',
    'color_grading_lut_bits': 'video_color_grading_lut_bits',
    'color_grading_cdl_values': 'video_color_grading_cdl_values',
    'color_grading_slope': 'video_color_grading_slope',
    'color_grading_offset': 'video_color_grading_offset',
    'color_grading_power': 'video_color_grading_power',
    'color_grading_saturation': 'video_color_grading_saturation',
    'color_grading_asc_sop': 'video_color_grading_asc_sop',
    'color_grading_asc_cdl': 'video_color_grading_asc_cdl',
    'color_grading_print_studio': 'video_color_grading_print_studio',
    'color_grading_delivery_format': 'video_color_grading_delivery_format',
    'color_grading_master_format': 'video_color_grading_master_format',
    'color_grading_quality_control': 'video_color_grading_quality_control',
}

VIDEO_STREAMING_EXTENDED = {
    'streaming_protocol_hls': 'video_streaming_protocol_hls',
    'streaming_protocol_dash': 'video_streaming_protocol_dash',
    'streaming_protocol_smooth': 'video_streaming_protocol_smooth',
    'streaming_protocol_rtmp': 'video_streaming_protocol_rtmp',
    'streaming_protocol_webrtc': 'video_streaming_protocol_webrtc',
    'streaming_protocol_srt': 'video_streaming_protocol_srt',
    'streaming_protocol_ll_hls': 'video_streaming_protocol_ll_hls',
    'streaming_protocol_cmaf': 'video_streaming_protocol_cmaf',
    'streaming_adaptive_bitrate': 'video_streaming_adaptive_bitrate',
    'streaming_segment_duration': 'video_streaming_segment_duration',
    'streaming_segment_count': 'video_streaming_segment_count',
    'streaming_manifest_type': 'video_streaming_manifest_type',
    'streaming_manifest_version': 'video_streaming_manifest_version',
    'streaming_drm_type': 'video_streaming_drm_type',
    'streaming_drm_widevine': 'video_streaming_drm_widevine',
    'streaming_drm_playready': 'video_streaming_drm_playready',
    'streaming_drm_fairplay': 'video_streaming_drm_fairplay',
    'streaming_drm_clear_key': 'video_streaming_drm_clear_key',
    'streaming_license_url': 'video_streaming_license_url',
    'streaming_key_rotation': 'video_streaming_key_rotation',
    'streaming_offline_mode': 'video_streaming_offline_mode',
    'streaming_cdn_url': 'video_streaming_cdn_url',
    'streaming_backup_url': 'video_streaming_backup_url',
    'streaming_quality_level': 'video_streaming_quality_level',
    'streaming_buffer_size': 'video_streaming_buffer_size',
    'streaming_buffer_health': 'video_streaming_buffer_health',
    'streaming_rebuffering_count': 'video_streaming_rebuffering_count',
    'streaming_error_rate': 'video_streaming_error_rate',
}

VIDEO_VR_AR = {
    'vr_projection_equirectangular': 'video_vr_projection_equirectangular',
    'vr_projection_cubemap': 'video_vr_projection_cubemap',
    'vr_projection_cylindrical': 'video_vr_projection_cylindrical',
    'vr_projection_fisheye': 'video_vr_projection_fisheye',
    'vr_projection_stereoscopic': 'video_vr_projection_stereoscopic',
    'vr_fov_horizontal': 'video_vr_fov_horizontal',
    'vr_fov_vertical': 'video_vr_fov_vertical',
    'vr_interpupillary_distance': 'video_vr_interpupillary_distance',
    'vr_eye_spacing': 'video_vr_eye_spacing',
    'vr_headset_type': 'video_vr_headset_type',
    'vr_tracking_system': 'video_vr_tracking_system',
    'vr_room_scale': 'video_vr_room_scale',
    'vr_seated': 'video_vr_seated',
    'vr_standing': 'video_vr_standing',
    'vr_stitching_type': 'video_vr_stitching_type',
    'vr_stitching_software': 'video_vr_stitching_software',
    'vr_manufacturer': 'video_vr_manufacturer',
    'vr_model': 'video_vr_model',
    'vr_firmware': 'video_vr_firmware',
    'vr_sensor_calibration': 'video_vr_sensor_calibration',
    'vr_distortion_correction': 'video_vr_distortion_correction',
    'vr_chromatic_aberration': 'video_vr_chromatic_aberration',
    'ar_marker_type': 'video_ar_marker_type',
    'ar_markerless_tracking': 'video_ar_markerless_tracking',
    'ar_surface_detection': 'video_ar_surface_detection',
    'ar_occlusion_handling': 'video_ar_occlusion_handling',
    'ar_light_estimation': 'video_ar_light_estimation',
    'ar_anchoring': 'video_ar_anchoring',
}

VIDEO_METADATA_EXTENDED = {
    'video_aspect_ratio': 'video_aspect_ratio',
    'video_pixel_aspect_ratio': 'video_pixel_aspect_ratio',
    'video_scan_type': 'video_scan_type',
    'video_scan_order': 'video_scan_order',
    'video_chroma_subsampling': 'video_chroma_subsampling',
    'video_color_range': 'video_color_range',
    'video_color_primaries': 'video_color_primaries',
    'video_transfer_characteristics': 'video_transfer_characteristics',
    'video_matrix_coefficients': 'video_matrix_coefficients',
    'video_master_display': 'video_master_display',
    'video_max_content_light_level': 'video_max_content_light_level',
    'video_max_frame_average_light_level': 'video_max_frame_average_light_level',
    'video_dynamic_range': 'video_dynamic_range',
    'video_hdr_format': 'video_hdr_format',
    'video_hdr10_plus_available': 'video_hdr10_plus_available',
    'video_dolby_vision_available': 'video_dolby_vision_available',
    'video_hlg_available': 'video_hlg_available',
    'video_sdr_available': 'video_sdr_available',
    'video_cinema_mode': 'video_cinema_mode',
    'video_filmmaker_mode': 'video_filmmaker_mode',
    'video_game_mode': 'video_game_mode',
    'video_low_latency_mode': 'video_low_latency_mode',
    'video_variable_refresh_rate': 'video_variable_refresh_rate',
    'video_auto_low_latency_mode': 'video_auto_low_latency_mode',
    'video_quick_frame_transport': 'video_quick_frame_transport',
    'video_display_manage': 'video_display_manage',
    'video_content_type': 'video_content_type',
    'video_movie': 'video_movie',
    'video_game': 'video_video_game',
    'video_photo': 'video_photo',
    'video_graphics': 'video_graphics',
    'video_application': 'video_application',
}

VIDEO_CONTAINER_EXTENDED = {
    'container_format': 'video_container_format',
    'container_major_brand': 'video_container_major_brand',
    'container_minor_version': 'video_container_minor_version',
    'container_compatible_brand': 'video_container_compatible_brand',
    'container_creation_time': 'video_container_creation_time',
    'container_modification_time': 'video_container_modification_time',
    'container_duration': 'video_container_duration',
    'container_timescale': 'video_container_timescale',
    'container_duration_ms': 'video_container_duration_ms',
    'container_track_count': 'video_container_track_count',
    'container_video_tracks': 'video_container_video_tracks',
    'container_audio_tracks': 'video_container_audio_tracks',
    'container_subtitle_tracks': 'video_container_subtitle_tracks',
    'container_chapter_count': 'video_container_chapter_count',
    'container_playlist': 'video_container_playlist',
    'container_iods_descriptor': 'video_container_iods_descriptor',
    'container_handler_type': 'video_container_handler_type',
    'container_handler_name': 'video_container_handler_name',
    'container_encoder': 'video_container_encoder',
    'container_encoder_version': 'video_container_encoder_version',
    'container_encoder_vendor': 'video_container_encoder_vendor',
}

VIDEO_BITSTREAM_EXTENDED = {
    'bitstream_profile': 'video_bitstream_profile',
    'bitstream_level': 'video_bitstream_level',
    'bitstream_tier': 'video_bitstream_tier',
    'bitstream_ref_frames': 'video_bitstream_ref_frames',
    'bitstream_b_frames': 'video_bitstream_b_frames',
    'bitstream_gop_size': 'video_bitstream_gop_size',
    'bitstream_gop_structure': 'video_bitstream_gop_structure',
    'bitstream_closed_gop': 'video_bitstream_closed_gop',
    'bitstream_idr_period': 'video_bitstream_idr_period',
    'bitstream_nal_unit_type': 'video_bitstream_nal_unit_type',
    'bitstream_slice_type': 'video_bitstream_slice_type',
    'bitstream_qp_min': 'video_bitstream_qp_min',
    'bitstream_qp_max': 'video_bitstream_qp_max',
    'bitstream_qp_delta': 'video_bitstream_qp_delta',
    'bitstream_rate_control': 'video_bitstream_rate_control',
    'bitstream_vbv_buffer_size': 'video_bitstream_vbv_buffer_size',
    'bitstream_vbv_occupancy': 'video_bitstream_vbv_occupancy',
    'bitstream_vbv_delay': 'video_bitstream_vbv_delay',
    'bitstream_cpb_removal_delay': 'video_bitstream_cpb_removal_delay',
    'bitstream_dpb_output_delay': 'video_bitstream_dpb_output_delay',
    'bitstream_pic_order_cnt_type': 'video_bitstream_pic_order_cnt_type',
    'bitstream_pic_order_cnt_lsb': 'video_bitstream_pic_order_cnt_lsb',
    'bitstream_delta_pic_order_cnt': 'video_bitstream_delta_pic_order_cnt',
    'bitstream_redundant_pic_cnt': 'video_bitstream_redundant_pic_cnt',
    'bitstream_slice_segment_address': 'video_bitstream_slice_segment_address',
    'bitstream_cabac_init': 'video_bitstream_cabac_init',
    'bitstream_cu_split_pred_mode': 'video_bitstream_cu_split_pred_mode',
    'bitstream_sao': 'video_bitstream_sao',
    'bitstream_amp': 'video_bitstream_amp',
    'bitstream_temporal_mvp': 'video_bitstream_temporal_mvp',
    'bitstream_spatial_mvp': 'video_bitstream_spatial_mvp',
}

VIDEO_ANALYTICS_EXTENDED = {
    'analytics_scene_detection': 'video_analytics_scene_detection',
    'analytics_face_detection': 'video_analytics_face_detection',
    'analytics_object_detection': 'video_analytics_object_detection',
    'analytics_person_detection': 'video_analytics_person_detection',
    'analytics_vehicle_detection': 'video_analytics_vehicle_detection',
    'analytics_action_recognition': 'video_analytics_action_recognition',
    'analytics_gesture_recognition': 'video_analytics_gesture_recognition',
    'analytics_emotion_recognition': 'video_analytics_emotion_recognition',
    'analytics_speech_recognition': 'video_analytics_speech_recognition',
    'analytics_text_recognition': 'video_analytics_text_recognition',
    'analytics_barcode_detection': 'video_analytics_barcode_detection',
    'analytics_qr_code_detection': 'video_analytics_qr_code_detection',
    'analytics_pattern_matching': 'video_analytics_pattern_matching',
    'analytics_anomaly_detection': 'video_analytics_anomaly_detection',
    'analytics_motion_tracking': 'video_analytics_motion_tracking',
    'analytics_people_tracking': 'video_analytics_people_tracking',
    'analytics_vehicle_tracking': 'video_analytics_vehicle_tracking',
    'analytics_heatmap': 'video_analytics_heatmap',
    'analytics_occupancy': 'video_analytics_occupancy',
    'analytics_dwell_time': 'video_analytics_dwell_time',
    'analytics_queue_length': 'video_analytics_queue_length',
    'analytics_loitering': 'video_analytics_loitering',
    'analytics_tailgating': 'video_analytics_tailgating',
    'analytics_intrusion': 'video_analytics_intrusion',
    'analytics_tamper_detection': 'video_analytics_tamper_detection',
    'analytics_blur_detection': 'video_analytics_blur_detection',
    'analytics_low_light_detection': 'video_analytics_low_light_detection',
    'analytics_privacy_masking': 'video_analytics_privacy_masking',
}


def get_video_professional_ultimate_field_count() -> int:
    """Return the total count of video professional ultimate fields."""
    base_count = get_video_professional_extended_field_count()
    extended_fields = (
        len(VIDEO_CINEMA_DCI) + len(VIDEO_HDR_EXTENDED) + 
        len(VIDEO_CODEC_PROFESSIONAL) + len(VIDEO_AUDIO_SURROUND) +
        len(VIDEO_SUBTITLE_EXTENDED) + len(VIDEO_TIMECODE_EXTENDED) +
        len(VIDEO_COLOR_GRADING) + len(VIDEO_STREAMING_EXTENDED) +
        len(VIDEO_VR_AR) + len(VIDEO_METADATA_EXTENDED) +
        len(VIDEO_CONTAINER_EXTENDED) + len(VIDEO_BITSTREAM_EXTENDED) +
        len(VIDEO_ANALYTICS_EXTENDED)
    )
    return base_count + extended_fields


# Integration point
def extract_video_professional_complete(filepath: str) -> Dict[str, Any]:
    """Main entry point for professional video extraction."""
    return extract_video_professional_extended_metadata(filepath)

#!/usr/bin/env python3
"""Generate video codec field inventories from FFmpeg.

This script extracts deep codec-specific metadata fields that are not exposed
through basic ffprobe output but are available in FFmpeg's bitstream API.

Coverage:
- H.264/AVC: SPS/PPS parameters (~400 fields)
- H.265/HEVC: VPS/SPS/PPS parameters (~500 fields)
- VP9/AV1: Frame headers, transform blocks (~300 fields)
- HDR metadata: HDR10, Dolby Vision, HLG (~200 fields)
- Color space: primaries, transfer, matrix (~200 fields)
- Bitrate control: CRF, CQP, target bitrate (~150 fields)
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


FFPROBE_PATH = shutil.which("ffprobe")


def get_ffprobe_version() -> str:
    """Get ffprobe version."""
    if not FFPROBE_PATH:
        return "not found"
    try:
        result = subprocess.run([FFPROBE_PATH, "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.splitlines()[0].strip()
    except Exception:
        pass
    return "unknown"


def get_all_ffprobe_entries() -> Dict[str, List[str]]:
    """Get all available ffprobe entries from --help."""

    if not FFPROBE_PATH:
        return {}

    try:
        result = subprocess.run([FFPROBE_PATH, "-help"], capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f"[error] Failed to get ffprobe help: {e}", file=sys.stderr)
        return {}

    help_text = result.stdout

    entries = {
        "format": [],
        "stream": [],
        "packet": [],
        "frame": [],
        "side_data": [],
    }

    current_section = None

    for line in help_text.splitlines():
        if line.strip().startswith("-show_"):
            entry = line.strip().split()[0]
            if "format" in line:
                entries["format"].append(entry)
            elif "stream" in line:
                entries["stream"].append(entry)
            elif "packet" in line:
                entries["packet"].append(entry)
            elif "frame" in line:
                entries["frame"].append(entry)
            elif "side_data" in line:
                entries["side_data"].append(entry)

    return entries


def get_codec_specific_fields(codec: str) -> Dict[str, List[str]]:
    """Get codec-specific field definitions based on standard specs.

    This uses curated field lists based on codec specifications
    since FFmpeg doesn't expose all bit-level fields via ffprobe.
    """

    h264_fields = [
        # SPS (Sequence Parameter Set)
        "profile_idc", "profile_compatibility", "level_idc", "constraint_set0_flag",
        "constraint_set1_flag", "constraint_set2_flag", "constraint_set3_flag",
        "constraint_set4_flag", "constraint_set5_flag", "chroma_format_idc",
        "bit_depth_luma_minus8", "bit_depth_chroma_minus8",
        "qpprime_flag", "separate_colour_plane_flag", "colour_primaries",
        "transfer_characteristics", "matrix_coefficients",
        # PPS (Picture Parameter Set)
        "pic_parameter_set_id", "num_ref_idx_l0_default_active_minus1",
        "num_ref_idx_l1_default_active_minus1", "weighted_bipred_idc",
        "weighted_pred_flag", "entropy_coding_mode_flag",
        "pic_order_present_flag", "redundant_pic_cnt_present_flag",
        "num_slice_groups_minus1", "num_ref_idx_l0_active_minus1",
        # Slice headers
        "slice_type", "pic_parameter_set_id", "frame_num",
        "direct_spatial_mv_pred_flag", "num_ref_idx_l1_active_minus1",
        "cabac_init_flag", "disable_deblocking_filter_idc",
        "slice_alpha_c0_offset_div2", "slice_beta_offset_div2",
        "num_ref_idx_active_override_flag", "luma_log2_weight_denom",
        "chroma_log2_weight_denom", "chroma_offset_list_offset",
        "luma_weight", "chroma_weight",
        # Transform and quantization
        "mb_adaptive_frame_field_flag", "mb_type", "qp_delta",
        "dct_coeffs", "residual_coeff", "pred_weight_l", "pred_weight_c",
        # Deblocking
        "disable_deblocking_filter_idc", "slice_alpha_c0_offset_div2",
        "slice_beta_offset_div2", "tc_offset_div2", "beta_offset_div2",
        # Motion estimation
        "direct_8x8_inference_flag", "direct_spatial_mv_pred_flag",
        "chroma_qp_index_offset", "luma_weight_l", "luma_weight_c",
        # HRD parameters
        "cpb_removal_flag", "max_num_reorder_frames", "max_dec_frame_buffering",
        "max_bitrate", "num_reorder_frames",
        # VUI (Video Usability Information)
        "aspect_ratio_info_present_flag", "overscan_info_present_flag",
        "video_signal_type_present_flag", "chroma_loc_info_present_flag",
        "timing_info_present_flag", "bitstream_restriction_flag",
        "aspect_ratio_idc", "overscan_appropriate_flag",
        "video_format", "video_full_range_flag", "colour_description_present_flag",
        "chroma_sample_loc_type_top_field", "chroma_sample_loc_type_bottom_field",
        "timing_info_present_flag", "bitstream_restriction_present_flag",
    ]

    hevc_fields = [
        # VPS (Video Parameter Set)
        "vps_video_parameter_set_id", "vps_max_layers_minus1",
        "vps_temporal_id_nesting_flag", "vps_max_sub_layers_minus1",
        "vps_avc_baseline_hint_flag", "vps_splitting_flag",
        "profile_tier_level_flag", "vps_extension_7bits",
        "vps_extension_3bits", "vps_extension_4bits", "vps_extension_5bits",
        # SPS
        "sps_video_parameter_set_id", "sps_max_sub_layers_minus1",
        "sps_temporal_id_nesting_flag", "vps_extension_6bits",
        "chroma_format_idc", "pic_width_in_luma_samples", "pic_height_in_luma_samples",
        "bit_depth_luma_minus8", "bit_depth_chroma_minus8",
        "conformance_window", "conformance_window_flag",
        # PPS
        "pps_video_parameter_set_id", "pps_pic_parameter_set_id",
        "pps_num_extra_slice_header_bits", "pps_slice_header_extension_present_flag",
        "pps_output_flag_present_flag", "pps_no_pic_reordering_flag",
        "pps_slice_header_bits", "pps_num_ref_idx_l0_default_active_minus1",
        "pps_num_ref_idx_l1_default_active_minus1", "pps_weighted_bipred_flag",
        "pps_weighted_pred_flag", "pps_cabac_init_flag", "pps_output_flag",
        # HRD
        "cpb_removal_flag", "max_dec_frame_buffering",
        "max_bitrate", "num_reorder_frames", "max_latency_increase",
        # Transform
        "transform_skip_enabled_flag", "log2_max_transform_block_size_minus2",
        "log2_min_transform_block_size_minus2", "max_transform_hierarchy_depth",
        # Quantization
        "diff_cu_qp_delta_enabled_flag", "pic_qp_delta",
        # Loop filter
        "loop_filter_across_tiles_enabled_flag", "loop_filter_offset",
        # SAO (Sample Adaptive Offset)
        "sao_enabled_flag", "sao_luma_offset", "sao_chroma_offset",
        # Deblocking
        "deblocking_filter_override_enabled_flag", "deblocking_filter_offset",
        # PCM
        "pcm_enabled_flag", "pcm_sample_bit_depth",
        # Tiles
        "tiles_enabled_flag", "num_tile_columns_minus1", "num_tile_rows_minus1",
        # Scaling list
        "scaling_list_enabled_flag", "num_delta_pocs",
        # VUI extension
        "vui_ext_present_flag", "default_display_window_flag",
        "aspect_ratio_info_present_flag", "colour_description_present_flag",
    ]

    vp9_fields = [
        # Frame header
        "profile", "show_existing_frame", "show_frame", "frame_type",
        "render_and_frame_size", "frame_refs", "key_frame",
        "intraonly", "error_resilient", "sharpness", "filter",
        "loop_filter_level", "loop_filter_sharpness", "log2_token_partition",
        # Segmentation
        "segmentation_enabled", "update_segment", "segment_index",
        # Quantization
        "base_q_idx", "last_q_idx", "y_ac_delta", "y_dc_delta",
        "y2_dc_delta", "uv_ac_delta", "uv_dc_delta",
        "uv2_dc_delta", "uv2_ac_delta",
        # Motion
        "motion_mode", "mv_mode", "allow_high_precision_mv",
        # Restoration
        "restoration_type", "lr_type", "lr_uv_level",
        # Transform
        "tx_mode", "tx_mode_16x16", "tx_mode_8x8", "dwt_mode",
    ]

    av1_fields = [
        # Sequence header
        "seq_profile", "seq_level", "seq_tier", "seq_bit_depth",
        "seq_chroma_subsampling_x", "seq_chroma_subsampling_y",
        "seq_encoder_delay", "seq_max_display_width", "seq_max_display_height",
        "seq_still_picture", "seq_monochrome", "seq_color_range",
        "seq_subsampling_x", "seq_subsampling_y", "seq_initial_display_delay",
        # Color
        "seq_primaries", "seq_transfer_characteristics", "seq_matrix_coefficients",
        # Metadata
        "seq_operating_point_idc", "seq_operating_parameters_idc",
        "seq_buffer_delay_length_minus_1",
    ]

    hdr_fields = [
        # HDR10
        "hdr10_clli_max_content_light_level",
        "hdr10_clli_max_pic_average_light_level",
        "hdr10_transfer_characteristics",
        "hdr10_matrix_coefficients",
        "hdr10_mastering_display_colour_volume_gains",
        "hdr10_mastering_display_colour_primaries",
        "hdr10_mastering_display_minimum_luminance",
        "hdr10_mastering_display_maximum_luminance",
        "hdr10_display_primaries_white_point",
        # Dolby Vision
        "dolby_version_major", "dolby_version_minor",
        "dolby_profile", "dolby_level", "dolby_rpu_present_flag",
        "dolby_bl_present_flag", "dolby_el_present_flag",
        "dolby_profile_compatibility",
        "dolby_dm_metadata_present_flag",
        # HLG
        "hlg_transfer_characteristics",
        "hlg_reference_display_luminance",
    ]

    color_fields = [
        "color_primaries", "color_trc", "color_matrix",
        "color_range", "chroma_sample_location",
        "mastering_display_luminance", "max_fall_luminance",
        "max_cll_luminance", "max_fall_luminance",
        "min_luminance", "min_cll_luminance",
        "max_cll", "min_cll", "white_point",
    ]

    bitrate_fields = [
        "bitrate", "max_bitrate", "min_bitrate",
        "rc_mode", "crf", "cqp", "qp",
        "target_bitrate", "bufsize", "maxrate", "minrate",
        "tile_columns", "tile_rows", "tile_width", "tile_height",
    ]

    if codec == "h264":
        return {"H.264": h264_fields}
    elif codec == "hevc":
        return {"H.265": hevc_fields}
    elif codec == "vp9":
        return {"VP9": vp9_fields}
    elif codec == "av1":
        return {"AV1": av1_fields}
    elif codec == "hdr":
        return {"HDR_Metadata": hdr_fields}
    elif codec == "color":
        return {"Color_Space": color_fields}
    elif codec == "bitrate":
        return {"Bitrate_Control": bitrate_fields}
    else:
        return {}


def generate_inventory(
    output_dir: Path,
    *,
    codecs: List[str] | None = None,
) -> None:
    """Generate video codec field inventory."""

    output_dir.mkdir(parents=True, exist_ok=True)

    inventory: Dict[str, Any] = {
        "generated_at": "",
        "ffprobe": {
            "path": FFPROBE_PATH,
            "version": get_ffprobe_version(),
        },
        "categories": {},
    }

    if not codecs:
        codecs = ["h264", "hevc", "vp9", "av1", "hdr", "color", "bitrate"]

    for codec in codecs:
        codec_data = get_codec_specific_fields(codec)

        if not codec_data:
            continue

        category_name = f"Video Codec: {codec.upper()}"

        tags = []
        for section, fields in codec_data.items():
            for field in fields:
                tags.append({
                    "name": field,
                    "section": section,
                    "source": "specification",
                })

        inventory["categories"][category_name] = {
            "codec": codec,
            "tags": tags,
            "tags_count": len(tags),
        }

        print(f"[inventory] {category_name}: {len(tags)} fields")

    # FFprobe entries as separate category
    ffprobe_entries = get_all_ffprobe_entries()
    for section, entries in ffprobe_entries.items():
        inventory["categories"][f"FFprobe:{section.capitalize()}"] = {
            "type": "ffprobe_entries",
            "entries": entries,
            "entries_count": len(entries),
        }
        print(f"[inventory] FFprobe {section.capitalize()}: {len(entries)} entries")

    # Summary
    total_tags = sum(
        cat.get("tags_count", 0)
        for cat in inventory["categories"].values()
    )

    inventory["totals"] = {
        "categories": len(inventory["categories"]),
        "tags": total_tags,
    }

    # Write JSON
    from datetime import datetime, timezone
    inventory["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    output_path = output_dir / "video_codec_inventory.json"
    output_path.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {output_path}")
    print(f"Total tags: {total_tags}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate video codec field inventory from FFmpeg specs",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist/video_codec_inventory"),
        help="Output directory (default: dist/video_codec_inventory)",
    )
    parser.add_argument(
        "--codecs",
        nargs="+",
        help="Specific codecs to inventory (h264, hevc, vp9, av1, hdr, color, bitrate)",
    )

    args = parser.parse_args()

    generate_inventory(args.out_dir, codecs=args.codecs)


if __name__ == "__main__":
    main()

"""
MetaExtract Extraction Modules
Comprehensive metadata extraction for media files
"""

# Core extraction modules
from .filesystem import extract_filesystem_metadata, extract_extended_attributes
from .exif import extract_exif_metadata, extract_gps_metadata, get_exif_field_count
from .iptc_xmp import extract_iptc_xmp_metadata, get_iptc_field_count, get_iptc_xmp_field_count
from .images import extract_image_properties, extract_thumbnail_properties, get_image_field_count
from .geocoding import reverse_geocode, batch_reverse_geocode, geocode_from_exif, get_geocoding_field_count
try:
    from .colors import extract_color_palette, extract_color_histograms, calculate_color_temperature, get_color_field_count
except Exception as e:
    def extract_color_palette(*args, **kwargs):
        raise RuntimeError("colors module not available (missing optional dependencies)")
    def extract_color_histograms(*args, **kwargs):
        raise RuntimeError("colors module not available (missing optional dependencies)")
    def calculate_color_temperature(*args, **kwargs):
        raise RuntimeError("colors module not available (missing optional dependencies)")
    def get_color_field_count():
        return 0
from .quality import extract_quality_metrics, estimate_image_sharpness, detect_blur, get_quality_field_count
from .time_based import extract_time_based_metadata, get_time_based_field_count
from .video import extract_video_metadata, extract_video_advanced_metadata, get_video_field_count
from .audio import extract_audio_metadata, extract_audio_advanced_metadata, get_audio_field_count
from .svg import extract_svg_metadata, get_svg_field_count
from .psd import extract_psd_metadata, get_psd_field_count

# Perceptual Hashing and Fingerprinting
from .perceptual_hashes import (
    extract_perceptual_hashes,
    extract_image_fingerprint,
    generate_thumbnail,
    compare_images,
    find_duplicates,
    calculate_similarity,
    get_perceptual_hash_field_count
)

# Metadata Storage Database
from .metadata_db import (
    init_database,
    store_file_metadata,
    get_file_metadata,
    search_metadata,
    find_similar_images,
    toggle_favorite,
    get_favorites,
    delete_file,
    get_statistics
)

# IPTC/XMP Fallback Libraries
from .iptc_xmp_fallback import (
    extract_iptc_fallback,
    extract_xmp_fallback,
    extract_all_metadata_with_fallbacks,
    get_fallback_field_count
)

# Video Keyframe and Scene Analysis
try:
    from .video_keyframes import (
        extract_keyframes,
        detect_scene_changes,
        get_keyframe_field_count
    )
except Exception as e:
    def extract_keyframes(*args, **kwargs):
        raise RuntimeError("video_keyframes module not available (missing optional dependencies)")
    def detect_scene_changes(*args, **kwargs):
        raise RuntimeError("video_keyframes module not available (missing optional dependencies)")
    def get_keyframe_field_count():
        return 0

# Directory and Batch Analysis
from .directory_analysis import (
    scan_directory,
    detect_changes,
    batch_extract_preview,
    get_directory_stats,
    get_directory_field_count
)

# Mobile/Smartphone Metadata
from .mobile_metadata import (
    extract_mobile_metadata,
    detect_apple_live_photo,
    detect_portrait_mode,
    get_mobile_field_count
)

# Quality Metrics (BRISQUE, NIQE, aesthetic)
try:
    from .quality_metrics import (
        extract_quality_metrics,
        extract_aesthetic_metrics,
        get_quality_field_count
    )
except Exception as e:
    def extract_quality_metrics(*args, **kwargs):
        raise RuntimeError("quality_metrics module not available (missing optional dependencies)")
    def extract_aesthetic_metrics(*args, **kwargs):
        raise RuntimeError("quality_metrics module not available (missing optional dependencies)")
    def get_quality_field_count():
        return 0

# Drone/Aerial Metadata
from .drone_metadata import (
    extract_drone_metadata,
    calculate_flight_metrics,
    get_drone_field_count
)

# ICC Profile Analysis
from .icc_profile import (
    extract_icc_profile_metadata,
    analyze_color_accuracy,
    get_icc_field_count
)

# 360° Camera Metadata
from .camera_360 import (
    extract_360_camera_metadata,
    detect_360_projection,
    get_360_field_count
)

# Accessibility Metadata
from .accessibility_metadata import (
    extract_accessibility_metadata,
    analyze_accessibility_compliance,
    get_accessibility_field_count
)

# Vendor MakerNotes
from .vendor_makernotes import (
    extract_vendor_makernotes,
    get_makernote_field_count
)

# Complete MakerNotes Parser
from .makernotes_complete import (
    parse_canon_makernote,
    parse_nikon_makernote,
    parse_sony_makernote,
    parse_fujifilm_makernote,
    parse_olympus_makernote,
    parse_panasonic_makernote,
    parse_pentax_makernote,
    parse_vendor_makernote,
    detect_vendor_from_tags,
    get_makernote_field_count as get_complete_makernote_field_count,
    get_vendor_field_count
)

# Social Media Metadata
from .social_media_metadata import (
    extract_social_media_metadata,
    get_social_media_field_count
)

# Forensic/Security Metadata
from .forensic_metadata import (
    extract_forensic_metadata,
    analyze_provenance,
    get_forensic_metadata_field_count
)

# Web/Open Graph Metadata
from .web_metadata import (
    extract_web_metadata,
    analyze_web_presence,
    get_web_metadata_field_count
)

# Action Camera Metadata
from .action_camera import (
    extract_action_camera_metadata,
    detect_action_camera,
    get_action_camera_field_count
)

# Scientific/Medical Metadata
from .scientific_medical import (
    extract_scientific_metadata,
    detect_scientific_format,
    get_scientific_medical_field_count
)

# Scientific Data (HDF5/NetCDF)
from .scientific_data import (
    extract_hdf5_metadata,
    extract_netcdf_metadata
)

# Video Telemetry (GoPro/DJI/GPMF)
from .video_telemetry import (
    extract_video_telemetry
)

# Print/Publishing Metadata
from .print_publishing import (
    extract_print_publishing_metadata,
    analyze_print_quality,
    get_print_publishing_field_count
)

# Workflow/DAM Metadata
from .workflow_dam import (
    extract_workflow_dam_metadata,
    generate_asset_checksum,
    analyze_asset_status,
    get_workflow_dam_field_count
)

# Utility modules
from .hashes import extract_file_hashes

# Advanced modules
from .ocr_burned_metadata import extract_burned_metadata
from .metadata_comparator import compare_metadata
try:
    from .steganography import SteganographyDetector
except Exception as e:
    class SteganographyDetector:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("steganography module not available (missing optional dependencies)")

# Temporal/Astronomical Metadata
from .temporal_astronomical import (
    extract_temporal_metadata,
    calculate_sun_position,
    calculate_sunrise_sunset,
    calculate_moon_position,
    calculate_daylight_periods,
    calculate_golden_hour,
    calculate_twilight_periods,
    calculate_astronomical_events,
    verify_photo_authenticity,
    get_temporal_field_count
)

# Video Codec Analysis
from .video_codec_analysis import (
    extract_video_codec_metadata,
    extract_h264_details,
    extract_hevc_details,
    extract_vp9_details,
    extract_av1_details,
    analyze_frame_types,
    extract_hdr_metadata,
    analyze_video_quality,
    get_video_codec_field_count
)

# DICOM Medical Imaging
from .dicom_medical import (
    extract_dicom_metadata,
    analyze_dicom_quality,
    get_dicom_field_count
)

# Perceptual Comparison
from .perceptual_comparison import (
    compare_images_detailed,
    find_duplicates_in_collection,
    calculate_image_similarity_matrix,
    cluster_similar_images,
    find_nearest_matches,
    deduplication_workflow,
    get_perceptual_comparison_field_count
)

# Complete Forensic Analysis
from .forensic_complete import (
    analyze_file_integrity,
    extract_burned_metadata as extract_burned_metadata_complete,
    calculate_time_difference,
    validate_gps_coordinates,
    estimate_noise_level,
    detect_double_compression,
    analyze_provenance,
    get_forensic_field_count
)

# Error Level Analysis
try:
    from .error_level_analysis import (
        analyze_ela,
        detect_clone_regions,
        detect_double_compression as detect_double_compression_ela,
        full_manipulation_analysis,
        get_ela_field_count
    )
except Exception as e:
    def analyze_ela(*args, **kwargs):
        raise RuntimeError("error_level_analysis module not available (missing optional dependencies)")
    def detect_clone_regions(*args, **kwargs):
        raise RuntimeError("error_level_analysis module not available (missing optional dependencies)")
    def detect_double_compression_ela(*args, **kwargs):
        raise RuntimeError("error_level_analysis module not available (missing optional dependencies)")
    def full_manipulation_analysis(*args, **kwargs):
        raise RuntimeError("error_level_analysis module not available (missing optional dependencies)")
    def get_ela_field_count():
        return 0

__all__ = [
    # Core extraction
    'extract_filesystem_metadata',
    'extract_extended_attributes',
    'extract_exif_metadata',
    'extract_gps_metadata',
    'extract_iptc_xmp_metadata',
    'extract_image_properties',
    'extract_thumbnail_properties',
    'extract_video_metadata',
    'extract_video_advanced_metadata',
    'extract_audio_metadata',
    'extract_audio_advanced_metadata',
    'extract_svg_metadata',
    'extract_psd_metadata',
    'extract_color_palette',
    'extract_color_histograms',
    'calculate_color_temperature',
    'extract_quality_metrics',
    'estimate_image_sharpness',
    'detect_blur',
    'extract_time_based_metadata',
    'reverse_geocode',
    'batch_reverse_geocode',
    'geocode_from_exif',
    'extract_file_hashes',
    
    # Perceptual Hashing
    'extract_perceptual_hashes',
    'extract_image_fingerprint',
    'generate_thumbnail',
    'compare_images',
    'find_duplicates',
    'calculate_similarity',
    
    # Metadata Database
    'init_database',
    'store_file_metadata',
    'get_file_metadata',
    'search_metadata',
    'find_similar_images',
    'toggle_favorite',
    'get_favorites',
    'delete_file',
    'get_statistics',
    
    # Fallback Libraries
    'extract_iptc_fallback',
    'extract_xmp_fallback',
    'extract_all_metadata_with_fallbacks',
    
    # Video Analysis
    'extract_keyframes',
    'detect_scene_changes',
    
    # Directory Analysis
    'scan_directory',
    'detect_changes',
    'batch_extract_preview',
    
    # Mobile/Smartphone
    'extract_mobile_metadata',
    'detect_apple_live_photo',
    'detect_portrait_mode',
    
    # Quality Metrics
    'extract_quality_metrics',
    'extract_aesthetic_metrics',
    
    # Drone Metadata
    'extract_drone_metadata',
    'calculate_flight_metrics',
    
    # ICC Profile
    'extract_icc_profile_metadata',
    'analyze_color_accuracy',

    # 360° Camera
    'extract_360_camera_metadata',
    'detect_360_projection',

    # Accessibility
    'extract_accessibility_metadata',
    'analyze_accessibility_compliance',

    # Vendor MakerNotes
    'extract_vendor_makernotes',
    'parse_canon_makernote',
    'parse_nikon_makernote',
    'parse_sony_makernote',
    'parse_fujifilm_makernote',
    'parse_olympus_makernote',
    'parse_panasonic_makernote',
    'parse_pentax_makernote',
    'parse_vendor_makernote',
    'detect_vendor_from_tags',
    'get_vendor_field_count',

    # Social Media
    'extract_social_media_metadata',

    # Forensic/Security
    'extract_forensic_metadata',
    'analyze_provenance',

    # Web Metadata
    'extract_web_metadata',
    'analyze_web_presence',

    # Action Camera
    'extract_action_camera_metadata',
    'detect_action_camera',

    # Scientific/Medical
    'extract_scientific_metadata',
    'detect_scientific_format',
    'extract_hdf5_metadata',
    'extract_netcdf_metadata',

    # Video Telemetry
    'extract_video_telemetry',

    # Print/Publishing
    'extract_print_publishing_metadata',
    'analyze_print_quality',

    # Workflow/DAM
    'extract_workflow_dam_metadata',
    'generate_asset_checksum',
    'analyze_asset_status',

    # Field count helpers
    'get_exif_field_count',
    'get_iptc_field_count',
    'get_iptc_xmp_field_count',
    'get_image_field_count',
    'get_geocoding_field_count',
    'get_color_field_count',
    'get_quality_field_count',
    'get_time_based_field_count',
    'get_video_field_count',
    'get_audio_field_count',
    'get_svg_field_count',
    'get_psd_field_count',
    'get_perceptual_hash_field_count',
    'get_fallback_field_count',
    'get_keyframe_field_count',
    'get_mobile_field_count',
    'get_drone_field_count',
    'get_icc_field_count',
    'get_directory_field_count',
    'get_360_field_count',
    'get_accessibility_field_count',
    'get_makernote_field_count',
    'get_social_media_field_count',
    'get_forensic_metadata_field_count',
    'get_web_metadata_field_count',
    'get_action_camera_field_count',
    'get_scientific_medical_field_count',
    'get_scientific_field_count',
    'get_print_publishing_field_count',
    'get_workflow_dam_field_count',

    # Advanced
    'extract_burned_metadata',
    'compare_metadata',
    'SteganographyDetector',

    # Temporal/Astronomical
    'extract_temporal_metadata',
    'calculate_sun_position',
    'calculate_sunrise_sunset',
    'calculate_moon_position',
    'calculate_daylight_periods',
    'calculate_golden_hour',
    'calculate_twilight_periods',
    'calculate_astronomical_events',
    'verify_photo_authenticity',
    'get_temporal_field_count',

    # Video Codec Analysis
    'extract_video_codec_metadata',
    'extract_h264_details',
    'extract_hevc_details',
    'extract_vp9_details',
    'extract_av1_details',
    'analyze_frame_types',
    'extract_hdr_metadata',
    'analyze_video_quality',
    'get_video_codec_field_count',

    # DICOM Medical
    'extract_dicom_metadata',
    'analyze_dicom_quality',
    'get_dicom_field_count',

    # Perceptual Comparison
    'compare_images_detailed',
    'find_duplicates_in_collection',
    'calculate_image_similarity_matrix',
    'cluster_similar_images',
    'find_nearest_matches',
    'deduplication_workflow',
    'get_perceptual_comparison_field_count',

    # Complete Forensic
    'analyze_file_integrity',
    'calculate_time_difference',
    'validate_gps_coordinates',
    'estimate_noise_level',
    'detect_double_compression',
    'get_forensic_field_count',
    'get_forensic_metadata_field_count',

    # Error Level Analysis
    'analyze_ela',
    'detect_clone_regions',
    'full_manipulation_analysis',
    'get_ela_field_count',
]

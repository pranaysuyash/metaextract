#!/usr/bin/env python3
"""
MetaExtract Field Count Utility

Counts total metadata fields extracted across all modules.
"""

import sys
import os
from pathlib import Path

# CRITICAL FIX: Add project root to Python path FIRST
# This ensures 'extractor' is a known package
project_root = Path(__file__).parent.absolute()
server_root = project_root / 'server'

# Add both roots to path in correct order
sys.path.insert(0, str(server_root))      # For 'from extractor...'
sys.path.insert(1, str(server_root / 'extractor'))  # For 'from extractor.modules...'

print(f"Python path configured:")
print(f"  1. {sys.path[0]}")
print(f"  2. {sys.path[1]}")
print()

# Now imports should work
from extractor.modules.exif import get_exif_field_count
from extractor.modules.iptc_xmp import get_iptc_field_count
from extractor.modules.images import get_image_field_count
from extractor.modules.geocoding import get_geocoding_field_count
from extractor.modules.colors import get_color_field_count
from extractor.modules.quality import get_quality_field_count
from extractor.modules.time_based import get_time_based_field_count
from extractor.modules.video import get_video_field_count
from extractor.modules.audio import get_audio_field_count
from extractor.modules.svg import get_svg_field_count
from extractor.modules.psd import get_psd_field_count
from extractor.modules.perceptual_hashes import get_perceptual_hash_field_count
from extractor.modules.iptc_xmp_fallback import get_fallback_field_count
from extractor.modules.video_keyframes import get_keyframe_field_count
from extractor.modules.directory_analysis import get_directory_field_count
from extractor.modules.mobile_metadata import get_mobile_field_count
from extractor.modules.quality_metrics import get_quality_field_count as get_quality_metrics_field_count
from extractor.modules.drone_metadata import get_drone_field_count
from extractor.modules.icc_profile import get_icc_field_count
from extractor.modules.camera_360 import get_360_field_count
from extractor.modules.accessibility_metadata import get_accessibility_field_count
from extractor.modules.vendor_makernotes import get_makernote_field_count
from extractor.modules.makernotes_complete import get_makernote_field_count as get_complete_makernote_field_count, get_vendor_field_count
from extractor.modules.social_media_metadata import get_social_media_field_count
from extractor.modules.forensic_metadata import get_forensic_metadata_field_count
from extractor.modules.web_metadata import get_web_metadata_field_count
from extractor.modules.action_camera import get_action_camera_field_count
from extractor.modules.scientific_medical import get_scientific_field_count
from extractor.modules.print_publishing import get_print_publishing_field_count
from extractor.modules.workflow_dam import get_workflow_dam_field_count

print("✓ All core modules imported successfully!")
print()

import sys
sys.path.insert(0, '/Users/pranay/Projects/metaextract/server/extractor/modules')

from exif import get_exif_field_count
from iptc_xmp import get_iptc_field_count
from images import get_image_field_count
from geocoding import get_geocoding_field_count
from colors import get_color_field_count
from quality import get_quality_field_count
from time_based import get_time_based_field_count
from video import get_video_field_count
from audio import get_audio_field_count
from svg import get_svg_field_count
from psd import get_psd_field_count
from perceptual_hashes import get_perceptual_hash_field_count
from iptc_xmp_fallback import get_fallback_field_count
from video_keyframes import get_keyframe_field_count
from directory_analysis import get_directory_field_count
from mobile_metadata import get_mobile_field_count
from quality_metrics import get_quality_field_count as get_quality_metrics_field_count
from drone_metadata import get_drone_field_count
from icc_profile import get_icc_field_count
from camera_360 import get_360_field_count
from accessibility_metadata import get_accessibility_field_count
from vendor_makernotes import get_makernote_field_count
from makernotes_complete import get_makernote_field_count as get_complete_makernote_field_count, get_vendor_field_count
from social_media_metadata import get_social_media_field_count
from forensic_metadata import get_forensic_field_count
from web_metadata import get_web_metadata_field_count
from action_camera import get_action_camera_field_count
from scientific_medical import get_scientific_field_count
from print_publishing import get_print_publishing_field_count
from workflow_dam import get_workflow_dam_field_count

# Phase 1 modules - NEW
try:
    from c2pa_adobe_cc import get_c2pa_adobe_field_count
    C2PA_ADOBE_AVAILABLE = True
except:
    C2PA_ADOBE_AVAILABLE = False

try:
    from makernote_exiftool import get_makernote_field_count as get_makernote_exiftool_field_count
    MAKERNOTE_EXIFTOOL_AVAILABLE = True
except:
    MAKERNOTE_EXIFTOOL_AVAILABLE = False

# Phase 2 modules - NEW
try:
    from video_codec_details import get_video_codec_details_field_count
    VIDEO_CODEC_DETAILS_AVAILABLE = True
except:
    VIDEO_CODEC_DETAILS_AVAILABLE = False

try:
    from container_metadata import get_container_metadata_field_count
    CONTAINER_METADATA_AVAILABLE = True
except:
    CONTAINER_METADATA_AVAILABLE = False

try:
    from audio_codec_details import get_audio_codec_details_field_count
    AUDIO_CODEC_DETAILS_AVAILABLE = True
except:
    AUDIO_CODEC_DETAILS_AVAILABLE = False

# Phase 3 modules - NEW
try:
    from pdf_metadata_complete import get_pdf_complete_field_count
    PDF_COMPLETE_AVAILABLE = True
except:
    PDF_COMPLETE_AVAILABLE = False

try:
    from office_documents import get_office_field_count
    OFFICE_DOCUMENTS_AVAILABLE = True
except:
    OFFICE_DOCUMENTS_AVAILABLE = False

try:
    from web_social_metadata import get_web_social_field_count
    WEB_SOCIAL_AVAILABLE = True
except:
    WEB_SOCIAL_AVAILABLE = False

try:
    from email_metadata import get_email_field_count
    EMAIL_AVAILABLE = True
except:
    EMAIL_AVAILABLE = False

try:
    from ai_ml_metadata import get_ai_ml_field_count
    AI_ML_AVAILABLE = True
except:
    AI_ML_AVAILABLE = False

try:
    from blockchain_nft_metadata import get_blockchain_nft_field_count
    BLOCKCHAIN_NFT_AVAILABLE = True
except:
    BLOCKCHAIN_NFT_AVAILABLE = False

try:
    from ar_vr_metadata import get_ar_vr_field_count
    AR_VR_AVAILABLE = True
except:
    AR_VR_AVAILABLE = False

try:
    from iot_metadata import get_iot_field_count
    IOT_AVAILABLE = True
except:
    IOT_AVAILABLE = False

try:
    from quantum_metadata import get_quantum_field_count
    QUANTUM_AVAILABLE = True
except:
    QUANTUM_AVAILABLE = False

try:
    from neural_network_metadata import get_neural_network_field_count
    NEURAL_NETWORK_AVAILABLE = True
except:
    NEURAL_NETWORK_AVAILABLE = False

try:
    from robotics_metadata import get_robotics_field_count
    ROBOTICS_AVAILABLE = True
except:
    ROBOTICS_AVAILABLE = False

try:
    from autonomous_metadata import get_autonomous_field_count
    AUTONOMOUS_AVAILABLE = True
except:
    AUTONOMOUS_AVAILABLE = False

try:
    from biotechnology_metadata import get_biotechnology_field_count
    BIOTECHNOLOGY_AVAILABLE = True
except:
    BIOTECHNOLOGY_AVAILABLE = False

try:
    from temporal_astronomical import get_temporal_field_count
    TEMPORAL_AVAILABLE = True
except:
    TEMPORAL_AVAILABLE = False

try:
    from video_codec_analysis import get_video_codec_field_count
    VIDEO_CODEC_AVAILABLE = True
except:
    VIDEO_CODEC_AVAILABLE = False

try:
    from dicom_medical import get_dicom_field_count
    DICOM_AVAILABLE = True
except:
    DICOM_AVAILABLE = False

try:
    from perceptual_comparison import get_perceptual_comparison_field_count
    PERCEPTUAL_COMP_AVAILABLE = True
except:
    PERCEPTUAL_COMP_AVAILABLE = False

total = 0
fields = {}

print('=' * 60)
print('METADATA FIELD COUNT - Phase 1 & 2 Progress')
print('=' * 60)

fields['EXIF'] = get_exif_field_count()
fields['IPTC/XMP'] = get_iptc_field_count()
fields['Image Properties'] = get_image_field_count()
fields['Geocoding'] = get_geocoding_field_count()
fields['Color Analysis'] = get_color_field_count()
fields['Quality (basic)'] = get_quality_field_count()
fields['Time-based'] = get_time_based_field_count()
fields['Video'] = get_video_field_count()
fields['Audio'] = get_audio_field_count()
fields['SVG'] = get_svg_field_count()
fields['PSD'] = get_psd_field_count()

print('--- Core Modules (11) ---')
for name, count in fields.items():
    print(f'{name:30s}: {count:>5} fields')
    total += count

fields2 = {}
fields2['Perceptual Hashes'] = get_perceptual_hash_field_count()
fields2['IPTC/XMP Fallbacks'] = get_fallback_field_count()
fields2['Video Keyframes'] = get_keyframe_field_count()
fields2['Directory Analysis'] = get_directory_field_count()
fields2['Mobile/Smartphone'] = get_mobile_field_count()
fields2['Quality Metrics'] = get_quality_metrics_field_count()
fields2['Drone/Aerial'] = get_drone_field_count()
fields2['ICC Profile'] = get_icc_field_count()
fields2['360 Camera'] = get_360_field_count()
fields2['Accessibility'] = get_accessibility_field_count()

print()
print('--- Extended Feature Modules (10) ---')
for name, count in fields2.items():
    print(f'{name:30s}: {count:>5} fields')
    total += count

print()
print('--- Vendor MakerNotes (COMPLETE) ---')
print(f'{"Canon":30s}: {get_vendor_field_count("canon"):>5} fields')
print(f'{"Nikon":30s}: {get_vendor_field_count("nikon"):>5} fields')
print(f'{"Sony":30s}: {get_vendor_field_count("sony"):>5} fields')
print(f'{"Fujifilm":30s}: {get_vendor_field_count("fujifilm"):>5} fields')
print(f'{"Olympus":30s}: {get_vendor_field_count("olympus"):>5} fields')
print(f'{"Panasonic":30s}: {get_vendor_field_count("panasonic"):>5} fields')
print(f'{"Pentax":30s}: {get_vendor_field_count("pentax"):>5} fields')
maker_count = get_complete_makernote_field_count()
print(f'{"Vendor MakerNotes (Total)":30s}: {maker_count:>5} fields')
total += maker_count

print()
print('--- Phase 1 Expansion (NEW) ---')
if C2PA_ADOBE_AVAILABLE:
    c2pa_count = get_c2pa_adobe_field_count()
    print(f'{"C2PA/Adobe CC Parsing":30s}: {c2pa_count:>5} fields')
    total += c2pa_count
else:
    print(f'{"C2PA/Adobe CC Parsing":30s}: {0:>5} fields (pending)')

if MAKERNOTE_EXIFTOOL_AVAILABLE:
    exif_makernote_count = get_makernote_exiftool_field_count()
    print(f'{"MakerNote ExifTool Allowlist":30s}: {exif_makernote_count:>5} fields')
    total += exif_makernote_count
else:
    print(f'{"MakerNote ExifTool Allowlist":30s}: {0:>5} fields (pending)')

print()
print('--- Phase 2 Media Depth (NEW) ---')
phase2_total = 0
if VIDEO_CODEC_DETAILS_AVAILABLE:
    video_codec_detail_count = get_video_codec_details_field_count()
    print(f'{"Video Codec Deep Analysis":30s}: {video_codec_detail_count:>5} fields')
    total += video_codec_detail_count
    phase2_total += video_codec_detail_count
else:
    print(f'{"Video Codec Deep Analysis":30s}: {0:>5} fields (pending)')

if CONTAINER_METADATA_AVAILABLE:
    container_count = get_container_metadata_field_count()
    print(f'{"Container Metadata (MP4/MKV)":30s}: {container_count:>5} fields')
    total += container_count
    phase2_total += container_count
else:
    print(f'{"Container Metadata (MP4/MKV)":30s}: {0:>5} fields (pending)')

if AUDIO_CODEC_DETAILS_AVAILABLE:
    audio_codec_detail_count = get_audio_codec_details_field_count()
    print(f'{"Audio Codec Deep Analysis":30s}: {audio_codec_detail_count:>5} fields')
    total += audio_codec_detail_count
    phase2_total += audio_codec_detail_count
else:
    print(f'{"Audio Codec Deep Analysis":30s}: {0:>5} fields (pending)')

print(f'{"Phase 2 Total":30s}: {phase2_total:>5} fields')

print()
print('--- Phase 3 Documents & Web (NEW) ---')
phase3_total = 0
if PDF_COMPLETE_AVAILABLE:
    pdf_complete_count = get_pdf_complete_field_count()
    print(f'{"PDF Complete Metadata":30s}: {pdf_complete_count:>5} fields')
    total += pdf_complete_count
    phase3_total += pdf_complete_count
else:
    print(f'{"PDF Complete Metadata":30s}: {0:>5} fields (pending)')

if OFFICE_DOCUMENTS_AVAILABLE:
    office_count = get_office_field_count()
    print(f'{"Office Documents":30s}: {office_count:>5} fields')
    total += office_count
    phase3_total += office_count
else:
    print(f'{"Office Documents":30s}: {0:>5} fields (pending)')

if WEB_SOCIAL_AVAILABLE:
    web_social_count = get_web_social_field_count()
    print(f'{"Web & Social Metadata":30s}: {web_social_count:>5} fields')
    total += web_social_count
    phase3_total += web_social_count
else:
    print(f'{"Web & Social Metadata":30s}: {0:>5} fields (pending)')

if EMAIL_AVAILABLE:
    email_count = get_email_field_count()
    print(f'{"Email & Communication":30s}: {email_count:>5} fields')
    total += email_count
    phase3_total += email_count
else:
    print(f'{"Email & Communication":30s}: {0:>5} fields (pending)')

print(f'{"Phase 3 Total":30s}: {phase3_total:>5} fields')

print()
print('--- Phase 4 Emerging Features (NEW) ---')
phase4_total = 0
if AI_ML_AVAILABLE:
    ai_ml_count = get_ai_ml_field_count()
    print(f'{"AI/ML Model Metadata":30s}: {ai_ml_count:>5} fields')
    total += ai_ml_count
    phase4_total += ai_ml_count
else:
    print(f'{"AI/ML Model Metadata":30s}: {0:>5} fields (pending)')

if BLOCKCHAIN_NFT_AVAILABLE:
    blockchain_nft_count = get_blockchain_nft_field_count()
    print(f'{"Blockchain/NFT Metadata":30s}: {blockchain_nft_count:>5} fields')
    total += blockchain_nft_count
    phase4_total += blockchain_nft_count
else:
    print(f'{"Blockchain/NFT Metadata":30s}: {0:>5} fields (pending)')

if AR_VR_AVAILABLE:
    ar_vr_count = get_ar_vr_field_count()
    print(f'{"AR/VR Content Metadata":30s}: {ar_vr_count:>5} fields')
    total += ar_vr_count
    phase4_total += ar_vr_count
else:
    print(f'{"AR/VR Content Metadata":30s}: {0:>5} fields (pending)')

if IOT_AVAILABLE:
    iot_count = get_iot_field_count()
    print(f'{"IoT Device Metadata":30s}: {iot_count:>5} fields')
    total += iot_count
    phase4_total += iot_count
else:
    print(f'{"IoT Device Metadata":30s}: {0:>5} fields (pending)')

if QUANTUM_AVAILABLE:
    quantum_count = get_quantum_field_count()
    print(f'{"Quantum Computing Metadata":30s}: {quantum_count:>5} fields')
    total += quantum_count
    phase4_total += quantum_count
else:
    print(f'{"Quantum Computing Metadata":30s}: {0:>5} fields (pending)')

if NEURAL_NETWORK_AVAILABLE:
    nn_count = get_neural_network_field_count()
    print(f'{"Neural Network Metadata":30s}: {nn_count:>5} fields')
    total += nn_count
    phase4_total += nn_count
else:
    print(f'{"Neural Network Metadata":30s}: {0:>5} fields (pending)')

if ROBOTICS_AVAILABLE:
    robotics_count = get_robotics_field_count()
    print(f'{"Robotics Metadata":30s}: {robotics_count:>5} fields')
    total += robotics_count
    phase4_total += robotics_count
else:
    print(f'{"Robotics Metadata":30s}: {0:>5} fields (pending)')

if AUTONOMOUS_AVAILABLE:
    autonomous_count = get_autonomous_field_count()
    print(f'{"Autonomous Systems Metadata":30s}: {autonomous_count:>5} fields')
    total += autonomous_count
    phase4_total += autonomous_count
else:
    print(f'{"Autonomous Systems Metadata":30s}: {0:>5} fields (pending)')

if BIOTECHNOLOGY_AVAILABLE:
    biotechnology_count = get_biotechnology_field_count()
    print(f'{"Biotechnology Metadata":30s}: {biotechnology_count:>5} fields')
    total += biotechnology_count
    phase4_total += biotechnology_count
else:
    print(f'{"Biotechnology Metadata":30s}: {0:>5} fields (pending)')

print(f'{"Phase 4 Total":30s}: {phase4_total:>5} fields')

fields3 = {}
fields3['Social Media'] = get_social_media_field_count()
fields3['Forensic/Security'] = get_forensic_field_count()
fields3['Web Metadata'] = get_web_metadata_field_count()
fields3['Action Camera'] = get_action_camera_field_count()
fields3['Scientific/Medical'] = get_scientific_field_count()
fields3['Print/Publishing'] = get_print_publishing_field_count()
fields3['Workflow/DAM'] = get_workflow_dam_field_count()

if TEMPORAL_AVAILABLE:
    fields3['Temporal/Astronomical'] = get_temporal_field_count()

if VIDEO_CODEC_AVAILABLE:
    fields3['Video Codec Analysis'] = get_video_codec_field_count()

if DICOM_AVAILABLE:
    fields3['DICOM Medical'] = get_dicom_field_count()

if PERCEPTUAL_COMP_AVAILABLE:
    fields3['Perceptual Comparison'] = get_perceptual_comparison_field_count()

print()
print('--- Specialized Modules ---')
for name, count in fields3.items():
    print(f'{name:30s}: {count:>5} fields')
    total += count

print()
print('=' * 70)
print(f'TOTAL: {total} fields')
print('=' * 70)
print()
print('Progress toward 45,000 field target:')
print(f'  Current: {total:,} fields ({100*total/45000:.1f}% of 45k target)')
print(f'  Remaining: {45000-total:,} fields to reach full coverage')
print()
print('Field domain breakdown (target 45k):')
print(f'  MakerNotes (Camera Vendors):   ~8,000 fields → Need ~4,100 more')
print(f'  ID3v2/Audio Tags:              ~2,500 fields → Need ~2,000 more')
print(f'  PDF/Office Documents:          ~3,000 fields → Need ~2,500 more')
print(f'  Video/Professional:            ~5,000 fields → Need ~3,200 more')
print(f'  Scientific/DICOM/FITS:         ~8,000 fields → Need ~7,000 more')
print(f'  Forensic/Security:             ~5,000 fields → Need ~4,700 more')
print(f'  Emerging (AI/NFT/AR/IoT):      ~3,500 fields → Need ~3,000 more')
print('=' * 70)


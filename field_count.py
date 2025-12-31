import sys
import os
sys.path.insert(0, '/Users/pranay/Projects/metaextract/server/extractor/modules')

# Configurable target: override with environment variable METAEXTRACT_TARGET_FIELDS
TARGET_FIELD_GOAL = None
try:
    _env = os.getenv('METAEXTRACT_TARGET_FIELDS')
    if _env:
        TARGET_FIELD_GOAL = int(_env)
except Exception:
    TARGET_FIELD_GOAL = None

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

try:
    from advanced_audio_ultimate import get_advanced_audio_ultimate_field_count
    ADVANCED_AUDIO_ULTIMATE_AVAILABLE = True
except:
    ADVANCED_AUDIO_ULTIMATE_AVAILABLE = False

try:
    from advanced_audio_ultimate import get_advanced_audio_ultimate_field_count
    ADVANCED_AUDIO_ULTIMATE_AVAILABLE = True
except:
    ADVANCED_AUDIO_ULTIMATE_AVAILABLE = False

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
# Phase 3 modules - COMPLETE (NEW)
try:
    from pdf_complete_ultimate import get_pdf_complete_ultimate_field_count
    PDF_COMPLETE_ULTIMATE_AVAILABLE = True
except:
    PDF_COMPLETE_ULTIMATE_AVAILABLE = False

try:
    from office_documents_complete import get_office_documents_complete_field_count
    OFFICE_DOCUMENTS_COMPLETE_AVAILABLE = True
except:
    OFFICE_DOCUMENTS_COMPLETE_AVAILABLE = False

try:
    from id3_frames_complete import get_id3_frames_field_count
    # Keep both function names available for backward compatibility
    get_id3_frames_complete_field_count = get_id3_frames_field_count
    ID3_FRAMES_COMPLETE_AVAILABLE = True
except:
    ID3_FRAMES_COMPLETE_AVAILABLE = False

try:
    from dicom_complete_ultimate import get_dicom_complete_ultimate_field_count
    DICOM_COMPLETE_ULTIMATE_AVAILABLE = True
except:
    DICOM_COMPLETE_ULTIMATE_AVAILABLE = False


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
    from medical_imaging_complete import get_medical_imaging_field_count
    MEDICAL_IMAGING_AVAILABLE = True
except:
    MEDICAL_IMAGING_AVAILABLE = False

try:
    from scientific_formats_extended import get_scientific_formats_extended_field_count
    SCIENTIFIC_FORMATS_AVAILABLE = True
except:
    SCIENTIFIC_FORMATS_AVAILABLE = False

try:
    from audio_id3_extended import get_audio_id3_extended_field_count
    AUDIO_ID3_EXTENDED_AVAILABLE = True
except:
    AUDIO_ID3_EXTENDED_AVAILABLE = False

try:
    from video_professional_extended import get_video_professional_extended_field_count
    VIDEO_PROFESSIONAL_EXTENDED_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_EXTENDED_AVAILABLE = False

try:
    from forensic_security_extended import get_forensic_security_extended_field_count
    FORENSIC_SECURITY_EXTENDED_AVAILABLE = True
except:
    FORENSIC_SECURITY_EXTENDED_AVAILABLE = False

try:
    from perceptual_comparison import get_perceptual_comparison_field_count
    PERCEPTUAL_COMP_AVAILABLE = True
except:
    PERCEPTUAL_COMP_AVAILABLE = False

try:
    from geospatial_gis import get_geospatial_gis_field_count
    GEOSPATIAL_GIS_AVAILABLE = True
except:
    GEOSPATIAL_GIS_AVAILABLE = False

try:
    from fits_complete import get_fits_complete_field_count
    FITS_COMPLETE_AVAILABLE = True
except:
    FITS_COMPLETE_AVAILABLE = False

try:
    from biometric_health import get_biometric_health_field_count
    BIOMETRIC_HEALTH_AVAILABLE = True
except:
    BIOMETRIC_HEALTH_AVAILABLE = False

try:
    from scientific_dicom_extended import get_scientific_dicom_extended_field_count
    SCIENTIFIC_DICOM_EXTENDED_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_EXTENDED_AVAILABLE = False

try:
    from environmental_climate import get_environmental_climate_field_count
    ENVIRONMENTAL_CLIMATE_AVAILABLE = True
except:
    ENVIRONMENTAL_CLIMATE_AVAILABLE = False

try:
    from materials_science import get_materials_science_field_count
    MATERIALS_SCIENCE_AVAILABLE = True
except:
    MATERIALS_SCIENCE_AVAILABLE = False

# Phase 4 modules - Advanced specialized domains
try:
    from makernotes_advanced import get_makernotes_advanced_field_count
    MAKERNOTES_ADVANCED_AVAILABLE = True
except:
    MAKERNOTES_ADVANCED_AVAILABLE = False

try:
    from video_codec_advanced import get_video_codec_advanced_field_count
    VIDEO_CODEC_ADVANCED_AVAILABLE = True
except:
    VIDEO_CODEC_ADVANCED_AVAILABLE = False

try:
    from pdf_metadata_advanced import get_pdf_metadata_advanced_field_count
    PDF_METADATA_ADVANCED_AVAILABLE = True
except:
    PDF_METADATA_ADVANCED_AVAILABLE = False

try:
    from dicom_advanced import get_dicom_advanced_field_count
    DICOM_ADVANCED_AVAILABLE = True
except:
    DICOM_ADVANCED_AVAILABLE = False

try:
    from forensic_security_advanced import get_forensic_security_advanced_field_count
    FORENSIC_SECURITY_ADVANCED_AVAILABLE = True
except:
    FORENSIC_SECURITY_ADVANCED_AVAILABLE = False

try:
    from audio_id3_advanced import get_audio_id3_advanced_field_count
    AUDIO_ID3_ADVANCED_AVAILABLE = True
except:
    AUDIO_ID3_ADVANCED_AVAILABLE = False

try:
    from scientific_advanced import get_scientific_advanced_field_count
    SCIENTIFIC_ADVANCED_AVAILABLE = True
except:
    SCIENTIFIC_ADVANCED_AVAILABLE = False

try:
    from video_professional_advanced import get_video_professional_advanced_field_count
    VIDEO_PROFESSIONAL_ADVANCED_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ADVANCED_AVAILABLE = False

try:
    from pdf_office_advanced import get_pdf_office_advanced_field_count
    PDF_OFFICE_ADVANCED_AVAILABLE = True
except:
    PDF_OFFICE_ADVANCED_AVAILABLE = False

try:
    from forensic_digital_advanced import get_forensic_digital_advanced_field_count
    FORENSIC_DIGITAL_ADVANCED_AVAILABLE = True
except:
    FORENSIC_DIGITAL_ADVANCED_AVAILABLE = False

try:
    from audio_metadata_advanced import get_audio_metadata_advanced_field_count
    AUDIO_METADATA_ADVANCED_AVAILABLE = True
except:
    AUDIO_METADATA_ADVANCED_AVAILABLE = False

try:
    from scientific_comprehensive_advanced import get_scientific_comprehensive_advanced_field_count
    SCIENTIFIC_COMPREHENSIVE_ADVANCED_AVAILABLE = True
except:
    SCIENTIFIC_COMPREHENSIVE_ADVANCED_AVAILABLE = False

try:
    from forensic_security_comprehensive_advanced import get_forensic_security_comprehensive_advanced_field_count
    FORENSIC_SECURITY_COMPREHENSIVE_ADVANCED_AVAILABLE = True
except:
    FORENSIC_SECURITY_COMPREHENSIVE_ADVANCED_AVAILABLE = False

try:
    from medical_healthcare_comprehensive_advanced import get_medical_healthcare_comprehensive_advanced_field_count
    MEDICAL_HEALTHCARE_COMPREHENSIVE_ADVANCED_AVAILABLE = True
except:
    MEDICAL_HEALTHCARE_COMPREHENSIVE_ADVANCED_AVAILABLE = False

try:
    from environmental_climate_comprehensive_advanced import get_environmental_climate_comprehensive_advanced_field_count
    ENVIRONMENTAL_CLIMATE_COMPREHENSIVE_ADVANCED_AVAILABLE = True
except:
    ENVIRONMENTAL_CLIMATE_COMPREHENSIVE_ADVANCED_AVAILABLE = False

try:
    from makernotes_ultimate_advanced import get_makernotes_ultimate_advanced_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from video_professional_ultimate_advanced import get_video_professional_ultimate_advanced_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from scientific_ultimate_advanced import get_scientific_ultimate_advanced_field_count
    SCIENTIFIC_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    SCIENTIFIC_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced import get_forensic_security_ultimate_advanced_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension import get_makernotes_ultimate_advanced_extension_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = False

try:
    from emerging_technology_ultimate_advanced import get_emerging_technology_ultimate_advanced_field_count
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from scientific_research_ultimate_advanced import get_scientific_research_ultimate_advanced_field_count
    SCIENTIFIC_RESEARCH_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    SCIENTIFIC_RESEARCH_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension import get_video_professional_ultimate_advanced_extension_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = False

try:
    from emerging_technology_ultimate_advanced_extension_ii import get_emerging_technology_ultimate_advanced_extension_ii_field_count
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced import get_scientific_dicom_fits_ultimate_advanced_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from dicom_complete_registry import get_dicom_complete_registry_field_count
    DICOM_COMPLETE_REGISTRY_AVAILABLE = True
except:
    DICOM_COMPLETE_REGISTRY_AVAILABLE = False

try:
    from gis_epsg_registry import get_gis_epsg_registry_field_count
    GIS_EPSG_REGISTRY_AVAILABLE = True
except:
    GIS_EPSG_REGISTRY_AVAILABLE = False

try:
    from fonts_complete_registry import get_fonts_complete_registry_field_count
    FONTS_COMPLETE_REGISTRY_AVAILABLE = True
except:
    FONTS_COMPLETE_REGISTRY_AVAILABLE = False

try:
    from iptc_newscodes_registry import get_iptc_newscodes_registry_field_count
    IPTC_NEWSCODES_REGISTRY_AVAILABLE = True
except:
    IPTC_NEWSCODES_REGISTRY_AVAILABLE = False

try:
    from cve_vulnerability_registry import get_cve_vulnerability_registry_field_count
    CVE_VULNERABILITY_REGISTRY_AVAILABLE = True
except:
    CVE_VULNERABILITY_REGISTRY_AVAILABLE = False

try:
    from broadcast_standards_registry import get_broadcast_standards_registry_field_count
    BROADCAST_STANDARDS_REGISTRY_AVAILABLE = True
except:
    BROADCAST_STANDARDS_REGISTRY_AVAILABLE = False

try:
    from audio_ultimate_advanced import get_audio_ultimate_advanced_field_count
    AUDIO_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    AUDIO_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from pdf_office_ultimate_advanced import get_pdf_office_ultimate_advanced_field_count
    PDF_OFFICE_ULTIMATE_ADVANCED_AVAILABLE = True
except:
    PDF_OFFICE_ULTIMATE_ADVANCED_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced_extension import get_forensic_security_ultimate_advanced_extension_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension_ii import get_makernotes_ultimate_advanced_extension_ii_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension import get_scientific_dicom_fits_ultimate_advanced_extension_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE = False

try:
    from engineering_cad_registry import get_engineering_cad_registry_field_count
    ENGINEERING_CAD_REGISTRY_AVAILABLE = True
except:
    ENGINEERING_CAD_REGISTRY_AVAILABLE = False

try:
    from financial_fintech_registry import get_financial_fintech_registry_field_count
    FINANCIAL_FINTECH_REGISTRY_AVAILABLE = True
except:
    FINANCIAL_FINTECH_REGISTRY_AVAILABLE = False

try:
    from gaming_asset_registry import get_gaming_asset_registry_field_count
    GAMING_ASSET_REGISTRY_AVAILABLE = True
except:
    GAMING_ASSET_REGISTRY_AVAILABLE = False

try:
    from legal_compliance_registry import get_legal_compliance_registry_field_count
    LEGAL_COMPLIANCE_REGISTRY_AVAILABLE = True
except:
    LEGAL_COMPLIANCE_REGISTRY_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension_ii import get_video_professional_ultimate_advanced_extension_ii_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension_iii import get_video_professional_ultimate_advanced_extension_iii_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_ii import get_scientific_dicom_fits_ultimate_advanced_extension_ii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_iii import get_scientific_dicom_fits_ultimate_advanced_extension_iii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_iv import get_scientific_dicom_fits_ultimate_advanced_extension_iv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_v import get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_V_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_V_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_vi import get_scientific_dicom_fits_ultimate_advanced_extension_vi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_vii import get_scientific_dicom_fits_ultimate_advanced_extension_vii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_viii import get_scientific_dicom_fits_ultimate_advanced_extension_viii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_ix import get_scientific_dicom_fits_ultimate_advanced_extension_ix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_x import get_scientific_dicom_fits_ultimate_advanced_extension_x_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_X_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_X_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xi import get_scientific_dicom_fits_ultimate_advanced_extension_xi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xii import get_scientific_dicom_fits_ultimate_advanced_extension_xii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xiii import get_scientific_dicom_fits_ultimate_advanced_extension_xiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xiv import get_scientific_dicom_fits_ultimate_advanced_extension_xiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xv import get_scientific_dicom_fits_ultimate_advanced_extension_xv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xvi import get_scientific_dicom_fits_ultimate_advanced_extension_xvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xvii import get_scientific_dicom_fits_ultimate_advanced_extension_xvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xviii import get_scientific_dicom_fits_ultimate_advanced_extension_xviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xix import get_scientific_dicom_fits_ultimate_advanced_extension_xix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xx import get_scientific_dicom_fits_ultimate_advanced_extension_xx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xxi import get_scientific_dicom_fits_ultimate_advanced_extension_xxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xxii import get_scientific_dicom_fits_ultimate_advanced_extension_xxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced_extension_ii import get_forensic_security_ultimate_advanced_extension_ii_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced_extension_iii import get_forensic_security_ultimate_advanced_extension_iii_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension_iii import get_makernotes_ultimate_advanced_extension_iii_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension_iv import get_makernotes_ultimate_advanced_extension_iv_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = False

try:
    from emerging_technology_ultimate_advanced_extension_iii import get_emerging_technology_ultimate_advanced_extension_iii_field_count
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = True
except:
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE = False

try:
    from emerging_technology_ultimate_advanced_extension_iv import get_emerging_technology_ultimate_advanced_extension_iv_field_count
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = True
except:
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = False

try:
    from pdf_office_ultimate_advanced_extension_ii import get_pdf_office_ultimate_advanced_extension_ii_field_count
    PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

try:
    from id3_audio_ultimate_advanced_extension_ii import get_id3_audio_ultimate_advanced_extension_ii_field_count
    ID3_AUDIO_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = True
except:
    ID3_AUDIO_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE = False

# Newly added batch imports (auto-generated)
try:
    from scientific_dicom_fits_ultimate_advanced_extension_liv import get_scientific_dicom_fits_ultimate_advanced_extension_liv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lv import get_scientific_dicom_fits_ultimate_advanced_extension_lv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lvi import get_scientific_dicom_fits_ultimate_advanced_extension_lvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lvii import get_scientific_dicom_fits_ultimate_advanced_extension_lvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lviii import get_scientific_dicom_fits_ultimate_advanced_extension_lviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lix import get_scientific_dicom_fits_ultimate_advanced_extension_lix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIX_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced_extension_xii import get_forensic_security_ultimate_advanced_extension_xii_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension_xiii import get_makernotes_ultimate_advanced_extension_xiii_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension_xii import get_video_professional_ultimate_advanced_extension_xii_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE = False

try:
    from emerging_technology_ultimate_advanced_extension_xi import get_emerging_technology_ultimate_advanced_extension_xi_field_count
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE = True
except:
    EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE = False

# Auto-generated: next batch imports
try:
    from scientific_dicom_fits_ultimate_advanced_extension_lx import get_scientific_dicom_fits_ultimate_advanced_extension_lx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxi import get_scientific_dicom_fits_ultimate_advanced_extension_lxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxii import get_scientific_dicom_fits_ultimate_advanced_extension_lxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxiii import get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxiv import get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxv import get_scientific_dicom_fits_ultimate_advanced_extension_lxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxvi import get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxvii import get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVII_AVAILABLE = False

# Auto-generated: next iteration imports
try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxviii import get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxix import get_scientific_dicom_fits_ultimate_advanced_extension_lxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxx import get_scientific_dicom_fits_ultimate_advanced_extension_lxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxi import get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxiii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxiv import get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxv import get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxvi import get_scientific_dicom_fits_ultimate_advanced_extension_lxxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxvii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxviii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxix import get_scientific_dicom_fits_ultimate_advanced_extension_lxxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxx import get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxxi import get_scientific_dicom_fits_ultimate_advanced_extension_lxxxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxxii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxxiii import get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxxiv import get_scientific_dicom_fits_ultimate_advanced_extension_lxxxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_lxxxv import get_scientific_dicom_fits_ultimate_advanced_extension_lxxxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXXV_AVAILABLE = False

try:
    from forensic_security_ultimate_advanced_extension_xv import get_forensic_security_ultimate_advanced_extension_xv_field_count
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = True
except:
    FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = False

try:
    from makernotes_ultimate_advanced_extension_xv import get_makernotes_ultimate_advanced_extension_xv_field_count
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = True
except:
    MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension_xiii import get_video_professional_ultimate_advanced_extension_xiii_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE = False

try:
    from video_professional_ultimate_advanced_extension_xiv import get_video_professional_ultimate_advanced_extension_xiv_field_count
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE = True
except:
    VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE = False

# Auto-generated: scientific XCI–C imports
try:
    from scientific_dicom_fits_ultimate_advanced_extension_xci import get_scientific_dicom_fits_ultimate_advanced_extension_xci_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcii import get_scientific_dicom_fits_ultimate_advanced_extension_xcii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xciii import get_scientific_dicom_fits_ultimate_advanced_extension_xciii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xciv import get_scientific_dicom_fits_ultimate_advanced_extension_xciv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcv import get_scientific_dicom_fits_ultimate_advanced_extension_xcv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcvi import get_scientific_dicom_fits_ultimate_advanced_extension_xcvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcvii import get_scientific_dicom_fits_ultimate_advanced_extension_xcvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcviii import get_scientific_dicom_fits_ultimate_advanced_extension_xcviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_xcix import get_scientific_dicom_fits_ultimate_advanced_extension_xcix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_c import get_scientific_dicom_fits_ultimate_advanced_extension_c_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_C_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_C_AVAILABLE = False

# Next batch imports: SCIENTIFIC DICOM FITS CI–CX
try:
    from scientific_dicom_fits_ultimate_advanced_extension_ci import get_scientific_dicom_fits_ultimate_advanced_extension_ci_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cii import get_scientific_dicom_fits_ultimate_advanced_extension_cii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_ciii import get_scientific_dicom_fits_ultimate_advanced_extension_ciii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_civ import get_scientific_dicom_fits_ultimate_advanced_extension_civ_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cv import get_scientific_dicom_fits_ultimate_advanced_extension_cv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CV_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cvi import get_scientific_dicom_fits_ultimate_advanced_extension_cvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVI_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cvii import get_scientific_dicom_fits_ultimate_advanced_extension_cvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cviii import get_scientific_dicom_fits_ultimate_advanced_extension_cviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVIII_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cix import get_scientific_dicom_fits_ultimate_advanced_extension_cix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cx import get_scientific_dicom_fits_ultimate_advanced_extension_cx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CX_AVAILABLE = True
except:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CX_AVAILABLE = False

# Next batch imports: SCIENTIFIC DICOM FITS CXI–CXX
try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxi import get_scientific_dicom_fits_ultimate_advanced_extension_cxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxii import get_scientific_dicom_fits_ultimate_advanced_extension_cxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxiii import get_scientific_dicom_fits_ultimate_advanced_extension_cxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxiv import get_scientific_dicom_fits_ultimate_advanced_extension_cxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxv import get_scientific_dicom_fits_ultimate_advanced_extension_cxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxvi import get_scientific_dicom_fits_ultimate_advanced_extension_cxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxvii import get_scientific_dicom_fits_ultimate_advanced_extension_cxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxviii import get_scientific_dicom_fits_ultimate_advanced_extension_cxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxix import get_scientific_dicom_fits_ultimate_advanced_extension_cxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxx import get_scientific_dicom_fits_ultimate_advanced_extension_cxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXX_AVAILABLE = False

# Next batch imports: SCIENTIFIC DICOM FITS CXXI–CXXX
try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxi import get_scientific_dicom_fits_ultimate_advanced_extension_cxxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxiii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxiv import get_scientific_dicom_fits_ultimate_advanced_extension_cxxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxv import get_scientific_dicom_fits_ultimate_advanced_extension_cxxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxvi import get_scientific_dicom_fits_ultimate_advanced_extension_cxxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxvii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxviii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxix import get_scientific_dicom_fits_ultimate_advanced_extension_cxxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxx import get_scientific_dicom_fits_ultimate_advanced_extension_cxxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXX_AVAILABLE = False

# Next batch imports: SCIENTIFIC DICOM FITS CXXXI–CXL
try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxi import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxiii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxiv import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxv import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxvi import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxvii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxviii import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxxxix import get_scientific_dicom_fits_ultimate_advanced_extension_cxxxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxl import get_scientific_dicom_fits_ultimate_advanced_extension_cxl_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXL_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXL_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxli import get_scientific_dicom_fits_ultimate_advanced_extension_cxli_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlii import get_scientific_dicom_fits_ultimate_advanced_extension_cxlii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxliii import get_scientific_dicom_fits_ultimate_advanced_extension_cxliii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxliv import get_scientific_dicom_fits_ultimate_advanced_extension_cxliv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlv import get_scientific_dicom_fits_ultimate_advanced_extension_cxlv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlvi import get_scientific_dicom_fits_ultimate_advanced_extension_cxlvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlvii import get_scientific_dicom_fits_ultimate_advanced_extension_cxlvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlviii import get_scientific_dicom_fits_ultimate_advanced_extension_cxlviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cxlix import get_scientific_dicom_fits_ultimate_advanced_extension_cxlix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cl import get_scientific_dicom_fits_ultimate_advanced_extension_cl_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CL_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CL_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxi import get_scientific_dicom_fits_ultimate_advanced_extension_clxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxii import get_scientific_dicom_fits_ultimate_advanced_extension_clxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxiii import get_scientific_dicom_fits_ultimate_advanced_extension_clxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxiv import get_scientific_dicom_fits_ultimate_advanced_extension_clxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxv import get_scientific_dicom_fits_ultimate_advanced_extension_clxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxvi import get_scientific_dicom_fits_ultimate_advanced_extension_clxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxvii import get_scientific_dicom_fits_ultimate_advanced_extension_clxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxviii import get_scientific_dicom_fits_ultimate_advanced_extension_clxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxix import get_scientific_dicom_fits_ultimate_advanced_extension_clxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxx import get_scientific_dicom_fits_ultimate_advanced_extension_clxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxi import get_scientific_dicom_fits_ultimate_advanced_extension_clxxi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxii import get_scientific_dicom_fits_ultimate_advanced_extension_clxxii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxiii import get_scientific_dicom_fits_ultimate_advanced_extension_clxxiii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxiv import get_scientific_dicom_fits_ultimate_advanced_extension_clxxiv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxv import get_scientific_dicom_fits_ultimate_advanced_extension_clxxv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxvi import get_scientific_dicom_fits_ultimate_advanced_extension_clxxvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxvii import get_scientific_dicom_fits_ultimate_advanced_extension_clxxvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxviii import get_scientific_dicom_fits_ultimate_advanced_extension_clxxviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxix import get_scientific_dicom_fits_ultimate_advanced_extension_clxxix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clxxx import get_scientific_dicom_fits_ultimate_advanced_extension_clxxx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cli import get_scientific_dicom_fits_ultimate_advanced_extension_cli_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clii import get_scientific_dicom_fits_ultimate_advanced_extension_clii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cliii import get_scientific_dicom_fits_ultimate_advanced_extension_cliii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_cliv import get_scientific_dicom_fits_ultimate_advanced_extension_cliv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clv import get_scientific_dicom_fits_ultimate_advanced_extension_clv_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLV_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLV_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clvi import get_scientific_dicom_fits_ultimate_advanced_extension_clvi_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVI_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVI_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clvii import get_scientific_dicom_fits_ultimate_advanced_extension_clvii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clviii import get_scientific_dicom_fits_ultimate_advanced_extension_clviii_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVIII_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVIII_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clix import get_scientific_dicom_fits_ultimate_advanced_extension_clix_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIX_AVAILABLE = False

try:
    from scientific_dicom_fits_ultimate_advanced_extension_clx import get_scientific_dicom_fits_ultimate_advanced_extension_clx_field_count
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLX_AVAILABLE = True
except Exception:
    SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLX_AVAILABLE = False

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

if ADVANCED_AUDIO_ULTIMATE_AVAILABLE:
    advanced_audio_count = get_advanced_audio_ultimate_field_count()
    print(f'{"Advanced Audio Ultimate":30s}: {advanced_audio_count:>5} fields')
    total += advanced_audio_count
    phase2_total += advanced_audio_count
else:
    print(f'{"Advanced Audio Ultimate":30s}: {0:>5} fields (pending)')
if ADVANCED_VIDEO_ULTIMATE_AVAILABLE:
    advanced_video_count = get_advanced_video_ultimate_field_count()
    print(f'{"Advanced Video Ultimate":30s}: {advanced_video_count:>5} fields')
    total += advanced_video_count
    phase2_total += advanced_video_count
else:
    print(f'{"Advanced Video Ultimate":30s}: {0:>5} fields (pending)')
if DOCUMENT_METADATA_ULTIMATE_AVAILABLE:
    document_count = get_document_metadata_ultimate_field_count()
    print(f'{"Document Metadata Ultimate":30s}: {document_count:>5} fields')
    total += document_count
    phase3_total += document_count
else:
    print(f'{"Document Metadata Ultimate":30s}: {0:>5} fields (pending)')

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
if PDF_COMPLETE_ULTIMATE_AVAILABLE:
    pdf_complete_ultimate_count = get_pdf_complete_ultimate_field_count()
    print(f'{"PDF Complete Ultimate":30s}: {pdf_complete_ultimate_count:>5} fields')
    total += pdf_complete_ultimate_count
    phase3_total += pdf_complete_ultimate_count
else:
    print(f'{"PDF Complete Ultimate":30s}: {0:>5} fields (pending)')

if OFFICE_DOCUMENTS_COMPLETE_AVAILABLE:
    office_complete_count = get_office_documents_complete_field_count()
    print(f'{"Office Documents Complete":30s}: {office_complete_count:>5} fields')
    total += office_complete_count
    phase3_total += office_complete_count
else:
    print(f'{"Office Documents Complete":30s}: {0:>5} fields (pending)')

if ID3_FRAMES_COMPLETE_AVAILABLE:
    id3_complete_count = get_id3_frames_field_count()
    print(f'{"ID3 Frames Complete":30s}: {id3_complete_count:>5} fields')
    total += id3_complete_count
    phase3_total += id3_complete_count
else:
    print(f'{"ID3 Frames Complete":30s}: {0:>5} fields (pending)')

if DICOM_COMPLETE_ULTIMATE_AVAILABLE:
    dicom_complete_count = get_dicom_complete_ultimate_field_count()
    print(f'{"DICOM Complete Ultimate":30s}: {dicom_complete_count:>5} fields')
    total += dicom_complete_count
    phase3_total += dicom_complete_count
else:
    print(f'{"DICOM Complete Ultimate":30s}: {0:>5} fields (pending)')


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

if MEDICAL_IMAGING_AVAILABLE:
    fields3['Medical Imaging (Complete)'] = get_medical_imaging_field_count()

if SCIENTIFIC_FORMATS_AVAILABLE:
    fields3['Scientific Formats (Extended)'] = get_scientific_formats_extended_field_count()

if AUDIO_ID3_EXTENDED_AVAILABLE:
    fields3['Audio ID3/Tags (Extended)'] = get_audio_id3_extended_field_count()

if VIDEO_PROFESSIONAL_EXTENDED_AVAILABLE:
    fields3['Video Professional (Extended)'] = get_video_professional_extended_field_count()

if FORENSIC_SECURITY_EXTENDED_AVAILABLE:
    fields3['Forensic/Security (Extended)'] = get_forensic_security_extended_field_count()

if PERCEPTUAL_COMP_AVAILABLE:
    fields3['Perceptual Comparison'] = get_perceptual_comparison_field_count()

if ID3_FRAMES_COMPLETE_AVAILABLE:
    fields3['ID3/Audio Tags (Complete)'] = get_id3_frames_field_count()

if GEOSPATIAL_GIS_AVAILABLE:
    fields3['Geospatial/GIS (Extended)'] = get_geospatial_gis_field_count()

if BIOMETRIC_HEALTH_AVAILABLE:
    fields3['Biometric/Health Records (Extended)'] = get_biometric_health_field_count()

if SCIENTIFIC_DICOM_EXTENDED_AVAILABLE:
    fields3['Scientific/DICOM (Extended)'] = get_scientific_dicom_extended_field_count()

if ENVIRONMENTAL_CLIMATE_AVAILABLE:
    fields3['Environmental/Climate (Extended)'] = get_environmental_climate_field_count()

if FITS_COMPLETE_AVAILABLE:
    fields3['FITS Astronomy (Complete)'] = get_fits_complete_field_count()

if MATERIALS_SCIENCE_AVAILABLE:
    fields3['Materials Science (Extended)'] = get_materials_science_field_count()

print()
print('--- Phase 4: Advanced Specialized Modules (NEW) ---')

if MAKERNOTES_ADVANCED_AVAILABLE:
    makernotes_adv_count = get_makernotes_advanced_field_count()
    fields3['MakerNotes (Advanced Vendors)'] = makernotes_adv_count
    print(f'{"MakerNotes (Advanced Vendors)":30s}: {makernotes_adv_count:>5} fields')
else:
    print(f'{"MakerNotes (Advanced Vendors)":30s}: {0:>5} fields (pending)')

if VIDEO_CODEC_ADVANCED_AVAILABLE:
    video_adv_count = get_video_codec_advanced_field_count()
    fields3['Video Codec (Advanced)'] = video_adv_count
    print(f'{"Video Codec (Advanced)":30s}: {video_adv_count:>5} fields')
else:
    print(f'{"Video Codec (Advanced)":30s}: {0:>5} fields (pending)')

if PDF_METADATA_ADVANCED_AVAILABLE:
    pdf_adv_count = get_pdf_metadata_advanced_field_count()
    fields3['PDF Metadata (Advanced)'] = pdf_adv_count
    print(f'{"PDF Metadata (Advanced)":30s}: {pdf_adv_count:>5} fields')
else:
    print(f'{"PDF Metadata (Advanced)":30s}: {0:>5} fields (pending)')

if DICOM_ADVANCED_AVAILABLE:
    dicom_adv_count = get_dicom_advanced_field_count()
    fields3['DICOM (Advanced)'] = dicom_adv_count
    print(f'{"DICOM (Advanced)":30s}: {dicom_adv_count:>5} fields')
else:
    print(f'{"DICOM (Advanced)":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ADVANCED_AVAILABLE:
    forensic_adv_count = get_forensic_security_advanced_field_count()
    fields3['Forensic/Security (Advanced)'] = forensic_adv_count
    print(f'{"Forensic/Security (Advanced)":30s}: {forensic_adv_count:>5} fields')
else:
    print(f'{"Forensic/Security (Advanced)":30s}: {0:>5} fields (pending)')

if AUDIO_ID3_ADVANCED_AVAILABLE:
    audio_adv_count = get_audio_id3_advanced_field_count()
    fields3['Audio ID3 (Advanced)'] = audio_adv_count
    print(f'{"Audio ID3 (Advanced)":30s}: {audio_adv_count:>5} fields')
else:
    print(f'{"Audio ID3 (Advanced)":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_ADVANCED_AVAILABLE:
    science_adv_count = get_scientific_advanced_field_count()
    fields3['Scientific (Advanced)'] = science_adv_count
    print(f'{"Scientific (Advanced)":30s}: {science_adv_count:>5} fields')
else:
    print(f'{"Scientific (Advanced)":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ADVANCED_AVAILABLE:
    video_prof_adv_count = get_video_professional_advanced_field_count()
    fields3['Video Professional (Advanced)'] = video_prof_adv_count
    print(f'{"Video Professional (Advanced)":30s}: {video_prof_adv_count:>5} fields')
else:
    print(f'{"Video Professional (Advanced)":30s}: {0:>5} fields (pending)')

if PDF_OFFICE_ADVANCED_AVAILABLE:
    pdf_office_adv_count = get_pdf_office_advanced_field_count()
    fields3['PDF/Office (Advanced)'] = pdf_office_adv_count
    print(f'{"PDF/Office (Advanced)":30s}: {pdf_office_adv_count:>5} fields')
else:
    print(f'{"PDF/Office (Advanced)":30s}: {0:>5} fields (pending)')

if FORENSIC_DIGITAL_ADVANCED_AVAILABLE:
    forensic_digital_adv_count = get_forensic_digital_advanced_field_count()
    fields3['Forensic Digital (Advanced)'] = forensic_digital_adv_count
    print(f'{"Forensic Digital (Advanced)":30s}: {forensic_digital_adv_count:>5} fields')
else:
    print(f'{"Forensic Digital (Advanced)":30s}: {0:>5} fields (pending)')

if AUDIO_METADATA_ADVANCED_AVAILABLE:
    audio_metadata_adv_count = get_audio_metadata_advanced_field_count()
    fields3['Audio Metadata (Advanced)'] = audio_metadata_adv_count
    print(f'{"Audio Metadata (Advanced)":30s}: {audio_metadata_adv_count:>5} fields')
else:
    print(f'{"Audio Metadata (Advanced)":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_COMPREHENSIVE_ADVANCED_AVAILABLE:
    scientific_comp_adv_count = get_scientific_comprehensive_advanced_field_count()
    fields3['Scientific Comprehensive (Advanced)'] = scientific_comp_adv_count
    print(f'{"Scientific Comprehensive (Advanced)":30s}: {scientific_comp_adv_count:>5} fields')
else:
    print(f'{"Scientific Comprehensive (Advanced)":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_COMPREHENSIVE_ADVANCED_AVAILABLE:
    forensic_sec_comp_adv_count = get_forensic_security_comprehensive_advanced_field_count()
    fields3['Forensic Security Comprehensive (Advanced)'] = forensic_sec_comp_adv_count
    print(f'{"Forensic Security Comprehensive (Advanced)":30s}: {forensic_sec_comp_adv_count:>5} fields')
else:
    print(f'{"Forensic Security Comprehensive (Advanced)":30s}: {0:>5} fields (pending)')

if MEDICAL_HEALTHCARE_COMPREHENSIVE_ADVANCED_AVAILABLE:
    medical_health_comp_adv_count = get_medical_healthcare_comprehensive_advanced_field_count()
    fields3['Medical Healthcare Comprehensive (Advanced)'] = medical_health_comp_adv_count
    print(f'{"Medical Healthcare Comprehensive (Advanced)":30s}: {medical_health_comp_adv_count:>5} fields')
else:
    print(f'{"Medical Healthcare Comprehensive (Advanced)":30s}: {0:>5} fields (pending)')

if ENVIRONMENTAL_CLIMATE_COMPREHENSIVE_ADVANCED_AVAILABLE:
    environmental_climate_comp_adv_count = get_environmental_climate_comprehensive_advanced_field_count()
    fields3['Environmental Climate Comprehensive (Advanced)'] = environmental_climate_comp_adv_count
    print(f'{"Environmental Climate Comprehensive (Advanced)":30s}: {environmental_climate_comp_adv_count:>5} fields')
else:
    print(f'{"Environmental Climate Comprehensive (Advanced)":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_AVAILABLE:
    makernotes_ultimate_adv_count = get_makernotes_ultimate_advanced_field_count()
    fields3['MakerNotes Ultimate (Advanced)'] = makernotes_ultimate_adv_count
    print(f'{"MakerNotes Ultimate (Advanced)":30s}: {makernotes_ultimate_adv_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_AVAILABLE:
    video_prof_ultimate_adv_count = get_video_professional_ultimate_advanced_field_count()
    fields3['Video Professional Ultimate (Advanced)'] = video_prof_ultimate_adv_count
    print(f'{"Video Professional Ultimate (Advanced)":30s}: {video_prof_ultimate_adv_count:>5} fields')
else:
    print(f'{"Video Professional Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_ULTIMATE_ADVANCED_AVAILABLE:
    scientific_ultimate_adv_count = get_scientific_ultimate_advanced_field_count()
    fields3['Scientific Ultimate (Advanced)'] = scientific_ultimate_adv_count
    print(f'{"Scientific Ultimate (Advanced)":30s}: {scientific_ultimate_adv_count:>5} fields')
else:
    print(f'{"Scientific Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_AVAILABLE:
    forensic_security_ultimate_adv_count = get_forensic_security_ultimate_advanced_field_count()
    fields3['Forensic Security Ultimate (Advanced)'] = forensic_security_ultimate_adv_count
    print(f'{"Forensic Security Ultimate (Advanced)":30s}: {forensic_security_ultimate_adv_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE:
    makernotes_ultimate_adv_ext_count = get_makernotes_ultimate_advanced_extension_field_count()
    fields3['MakerNotes Ultimate Advanced Extension'] = makernotes_ultimate_adv_ext_count
    print(f'{"MakerNotes Ultimate Advanced Extension":30s}: {makernotes_ultimate_adv_ext_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension":30s}: {0:>5} fields (pending)')

if EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_AVAILABLE:
    emerging_technology_ultimate_adv_count = get_emerging_technology_ultimate_advanced_field_count()
    fields3['Emerging Technology Ultimate (Advanced)'] = emerging_technology_ultimate_adv_count
    print(f'{"Emerging Technology Ultimate (Advanced)":30s}: {emerging_technology_ultimate_adv_count:>5} fields')
else:
    print(f'{"Emerging Technology Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_RESEARCH_ULTIMATE_ADVANCED_AVAILABLE:
    scientific_research_ultimate_adv_count = get_scientific_research_ultimate_advanced_field_count()
    fields3['Scientific Research Ultimate (Advanced)'] = scientific_research_ultimate_adv_count
    print(f'{"Scientific Research Ultimate (Advanced)":30s}: {scientific_research_ultimate_adv_count:>5} fields')
else:
    print(f'{"Scientific Research Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE:
    video_professional_ultimate_adv_ext_count = get_video_professional_ultimate_advanced_extension_field_count()
    fields3['Video Professional Ultimate Advanced Extension'] = video_professional_ultimate_adv_ext_count
    print(f'{"Video Professional Ultimate Advanced Extension":30s}: {video_professional_ultimate_adv_ext_count:>5} fields')
else:
    print(f'{"Video Professional Ultimate Advanced Extension":30s}: {0:>5} fields (pending)')

if EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    emerging_technology_ultimate_adv_ext_ii_count = get_emerging_technology_ultimate_advanced_extension_ii_field_count()
    fields3['Emerging Technology Ultimate Advanced Extension II'] = emerging_technology_ultimate_adv_ext_ii_count
    print(f'{"Emerging Technology Ultimate Advanced Extension II":30s}: {emerging_technology_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"Emerging Technology Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_count = get_scientific_dicom_fits_ultimate_advanced_field_count()
    fields3['Scientific DICOM FITS Ultimate (Advanced)'] = scientific_dicom_fits_ultimate_adv_count
    print(f'{"Scientific DICOM FITS Ultimate (Advanced)":30s}: {scientific_dicom_fits_ultimate_adv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if DICOM_COMPLETE_REGISTRY_AVAILABLE:
    dicom_complete_count = get_dicom_complete_registry_field_count()
    fields3['DICOM Complete Registry (Ultra)'] = dicom_complete_count
    print(f'{"DICOM Complete Registry (Ultra)":30s}: {dicom_complete_count:>5} fields')
else:
    print(f'{"DICOM Complete Registry (Ultra)":30s}: {0:>5} fields (pending)')

if GIS_EPSG_REGISTRY_AVAILABLE:
    gis_epsg_count = get_gis_epsg_registry_field_count()
    fields3['GIS EPSG Registry (Complete)'] = gis_epsg_count
    print(f'{"GIS EPSG Registry (Complete)":30s}: {gis_epsg_count:>5} fields')
else:
    print(f'{"GIS EPSG Registry (Complete)":30s}: {0:>5} fields (pending)')

if FONTS_COMPLETE_REGISTRY_AVAILABLE:
    fonts_complete_count = get_fonts_complete_registry_field_count()
    fields3['Fonts Complete Registry'] = fonts_complete_count
    print(f'{"Fonts Complete Registry":30s}: {fonts_complete_count:>5} fields')
else:
    print(f'{"Fonts Complete Registry":30s}: {0:>5} fields (pending)')

if IPTC_NEWSCODES_REGISTRY_AVAILABLE:
    iptc_newscodes_count = get_iptc_newscodes_registry_field_count()
    fields3['IPTC NewsCodes Registry'] = iptc_newscodes_count
    print(f'{"IPTC NewsCodes Registry":30s}: {iptc_newscodes_count:>5} fields')
else:
    print(f'{"IPTC NewsCodes Registry":30s}: {0:>5} fields (pending)')

if CVE_VULNERABILITY_REGISTRY_AVAILABLE:
    cve_vuln_count = get_cve_vulnerability_registry_field_count()
    fields3['CVE Vulnerability Registry'] = cve_vuln_count
    print(f'{"CVE Vulnerability Registry":30s}: {cve_vuln_count:>5} fields')
else:
    print(f'{"CVE Vulnerability Registry":30s}: {0:>5} fields (pending)')

if BROADCAST_STANDARDS_REGISTRY_AVAILABLE:
    broadcast_std_count = get_broadcast_standards_registry_field_count()
    fields3['Broadcast Standards Registry'] = broadcast_std_count
    print(f'{"Broadcast Standards Registry":30s}: {broadcast_std_count:>5} fields')
else:
    print(f'{"Broadcast Standards Registry":30s}: {0:>5} fields (pending)')

if ENGINEERING_CAD_REGISTRY_AVAILABLE:
    eng_cad_count = get_engineering_cad_registry_field_count()
    fields3['Engineering CAD Registry (BIM/IFC)'] = eng_cad_count
    print(f'{"Engineering CAD Registry (BIM/IFC)":30s}: {eng_cad_count:>5} fields')
else:
    print(f'{"Engineering CAD Registry (BIM/IFC)":30s}: {0:>5} fields (pending)')

if FINANCIAL_FINTECH_REGISTRY_AVAILABLE:
    fin_count = get_financial_fintech_registry_field_count()
    fields3['Financial/FinTech Registry (XBRL)'] = fin_count
    print(f'{"Financial/FinTech Registry (XBRL)":30s}: {fin_count:>5} fields')
else:
    print(f'{"Financial/FinTech Registry (XBRL)":30s}: {0:>5} fields (pending)')

if GAMING_ASSET_REGISTRY_AVAILABLE:
    gaming_count = get_gaming_asset_registry_field_count()
    fields3['Gaming Asset Registry (Unity/UE)'] = gaming_count
    print(f'{"Gaming Asset Registry (Unity/UE)":30s}: {gaming_count:>5} fields')
else:
    print(f'{"Gaming Asset Registry (Unity/UE)":30s}: {0:>5} fields (pending)')

if LEGAL_COMPLIANCE_REGISTRY_AVAILABLE:
    legal_count = get_legal_compliance_registry_field_count()
    fields3['Legal Compliance Registry (E-Discovery)'] = legal_count
    print(f'{"Legal Compliance Registry":30s}: {legal_count:>5} fields')
else:
    print(f'{"Legal Compliance Registry":30s}: {0:>5} fields (pending)')

if ENGINEERING_CAD_REGISTRY_AVAILABLE:
    eng_cad_count = get_engineering_cad_registry_field_count()
    fields3['Engineering CAD Registry (BIM/IFC)'] = eng_cad_count
    print(f'{"Engineering CAD Registry (BIM/IFC)":30s}: {eng_cad_count:>5} fields')
else:
    print(f'{"Engineering CAD Registry (BIM/IFC)":30s}: {0:>5} fields (pending)')

if FINANCIAL_FINTECH_REGISTRY_AVAILABLE:
    fin_count = get_financial_fintech_registry_field_count()
    fields3['Financial/FinTech Registry (XBRL)'] = fin_count
    print(f'{"Financial/FinTech Registry (XBRL)":30s}: {fin_count:>5} fields')
else:
    print(f'{"Financial/FinTech Registry (XBRL)":30s}: {0:>5} fields (pending)')

if GAMING_ASSET_REGISTRY_AVAILABLE:
    gaming_count = get_gaming_asset_registry_field_count()
    fields3['Gaming Asset Registry (Unity/UE)'] = gaming_count
    print(f'{"Gaming Asset Registry (Unity/UE)":30s}: {gaming_count:>5} fields')
else:
    print(f'{"Gaming Asset Registry (Unity/UE)":30s}: {0:>5} fields (pending)')

if LEGAL_COMPLIANCE_REGISTRY_AVAILABLE:
    legal_count = get_legal_compliance_registry_field_count()
    fields3['Legal Compliance Registry (E-Discovery)'] = legal_count
    print(f'{"Legal Compliance Registry":30s}: {legal_count:>5} fields')
else:
    print(f'{"Legal Compliance Registry":30s}: {0:>5} fields (pending)')

if AUDIO_ULTIMATE_ADVANCED_AVAILABLE:
    audio_ultimate_adv_count = get_audio_ultimate_advanced_field_count()
    fields3['Audio Ultimate (Advanced)'] = audio_ultimate_adv_count
    print(f'{"Audio Ultimate (Advanced)":30s}: {audio_ultimate_adv_count:>5} fields')
else:
    print(f'{"Audio Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if PDF_OFFICE_ULTIMATE_ADVANCED_AVAILABLE:
    pdf_office_ultimate_adv_count = get_pdf_office_ultimate_advanced_field_count()
    fields3['PDF Office Ultimate (Advanced)'] = pdf_office_ultimate_adv_count
    print(f'{"PDF Office Ultimate (Advanced)":30s}: {pdf_office_ultimate_adv_count:>5} fields')
else:
    print(f'{"PDF Office Ultimate (Advanced)":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE:
    forensic_security_ultimate_adv_ext_count = get_forensic_security_ultimate_advanced_extension_field_count()
    fields3['Forensic Security Ultimate Advanced Extension'] = forensic_security_ultimate_adv_ext_count
    print(f'{"Forensic Security Ultimate Advanced Extension":30s}: {forensic_security_ultimate_adv_ext_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate Advanced Extension":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    makernotes_ultimate_adv_ext_ii_count = get_makernotes_ultimate_advanced_extension_ii_field_count()
    fields3['MakerNotes Ultimate Advanced Extension II'] = makernotes_ultimate_adv_ext_ii_count
    print(f'{"MakerNotes Ultimate Advanced Extension II":30s}: {makernotes_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_count = get_scientific_dicom_fits_ultimate_advanced_extension_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension'] = scientific_dicom_fits_ultimate_adv_ext_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension":30s}: {scientific_dicom_fits_ultimate_adv_ext_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    video_professional_ultimate_adv_ext_ii_count = get_video_professional_ultimate_advanced_extension_ii_field_count()
    fields3['Video Professional Ultimate Advanced Extension II'] = video_professional_ultimate_adv_ext_ii_count
    print(f'{"Video Professional Ultimate Advanced Extension II":30s}: {video_professional_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"Video Professional Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE:
    video_professional_ultimate_adv_ext_iii_count = get_video_professional_ultimate_advanced_extension_iii_field_count()
    fields3['Video Professional Ultimate Advanced Extension III'] = video_professional_ultimate_adv_ext_iii_count
    print(f'{"Video Professional Ultimate Advanced Extension III":30s}: {video_professional_ultimate_adv_ext_iii_count:>5} fields')
else:
    print(f'{"Video Professional Ultimate Advanced Extension III":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_ii_count = get_scientific_dicom_fits_ultimate_advanced_extension_ii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension II'] = scientific_dicom_fits_ultimate_adv_ext_ii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension II":30s}: {scientific_dicom_fits_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_iii_count = get_scientific_dicom_fits_ultimate_advanced_extension_iii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension III'] = scientific_dicom_fits_ultimate_adv_ext_iii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension III":30s}: {scientific_dicom_fits_ultimate_adv_ext_iii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension III":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_iv_count = get_scientific_dicom_fits_ultimate_advanced_extension_iv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension IV'] = scientific_dicom_fits_ultimate_adv_ext_iv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension IV":30s}: {scientific_dicom_fits_ultimate_adv_ext_iv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension IV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_V_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_v_count = get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension V'] = scientific_dicom_fits_ultimate_adv_ext_v_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension V":30s}: {scientific_dicom_fits_ultimate_adv_ext_v_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension V":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_vi_count = get_scientific_dicom_fits_ultimate_advanced_extension_vi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension VI'] = scientific_dicom_fits_ultimate_adv_ext_vi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VI":30s}: {scientific_dicom_fits_ultimate_adv_ext_vi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_vii_count = get_scientific_dicom_fits_ultimate_advanced_extension_vii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension VII'] = scientific_dicom_fits_ultimate_adv_ext_vii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VII":30s}: {scientific_dicom_fits_ultimate_adv_ext_vii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_VIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_viii_count = get_scientific_dicom_fits_ultimate_advanced_extension_viii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension VIII'] = scientific_dicom_fits_ultimate_adv_ext_viii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_viii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension VIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_ix_count = get_scientific_dicom_fits_ultimate_advanced_extension_ix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension IX'] = scientific_dicom_fits_ultimate_adv_ext_ix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension IX":30s}: {scientific_dicom_fits_ultimate_adv_ext_ix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension IX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_X_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_x_count = get_scientific_dicom_fits_ultimate_advanced_extension_x_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension X'] = scientific_dicom_fits_ultimate_adv_ext_x_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension X":30s}: {scientific_dicom_fits_ultimate_adv_ext_x_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension X":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xi_count = get_scientific_dicom_fits_ultimate_advanced_extension_xi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XI'] = scientific_dicom_fits_ultimate_adv_ext_xi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XI":30s}: {scientific_dicom_fits_ultimate_adv_ext_xi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XII'] = scientific_dicom_fits_ultimate_adv_ext_xii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XIII'] = scientific_dicom_fits_ultimate_adv_ext_xiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_xiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XIV'] = scientific_dicom_fits_ultimate_adv_ext_xiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_xiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xv_count = get_scientific_dicom_fits_ultimate_advanced_extension_xv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XV'] = scientific_dicom_fits_ultimate_adv_ext_xv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XV":30s}: {scientific_dicom_fits_ultimate_adv_ext_xv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_xvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XVI'] = scientific_dicom_fits_ultimate_adv_ext_xvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_xvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XVII'] = scientific_dicom_fits_ultimate_adv_ext_xvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XVIII'] = scientific_dicom_fits_ultimate_adv_ext_xviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xix_count = get_scientific_dicom_fits_ultimate_advanced_extension_xix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XIX'] = scientific_dicom_fits_ultimate_adv_ext_xix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_xix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xx_count = get_scientific_dicom_fits_ultimate_advanced_extension_xx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XX'] = scientific_dicom_fits_ultimate_adv_ext_xx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XX":30s}: {scientific_dicom_fits_ultimate_adv_ext_xx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_xxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XXI'] = scientific_dicom_fits_ultimate_adv_ext_xxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_xxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XXII'] = scientific_dicom_fits_ultimate_adv_ext_xxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XXII":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    forensic_security_ultimate_adv_ext_ii_count = get_forensic_security_ultimate_advanced_extension_ii_field_count()
    fields3['Forensic Security Ultimate Advanced Extension II'] = forensic_security_ultimate_adv_ext_ii_count
    print(f'{"Forensic Security Ultimate Advanced Extension II":30s}: {forensic_security_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE:
    forensic_security_ultimate_adv_ext_iii_count = get_forensic_security_ultimate_advanced_extension_iii_field_count()
    fields3['Forensic Security Ultimate Advanced Extension III'] = forensic_security_ultimate_adv_ext_iii_count
    print(f'{"Forensic Security Ultimate Advanced Extension III":30s}: {forensic_security_ultimate_adv_ext_iii_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate Advanced Extension III":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE:
    makernotes_ultimate_adv_ext_iii_count = get_makernotes_ultimate_advanced_extension_iii_field_count()
    fields3['MakerNotes Ultimate Advanced Extension III'] = makernotes_ultimate_adv_ext_iii_count
    print(f'{"MakerNotes Ultimate Advanced Extension III":30s}: {makernotes_ultimate_adv_ext_iii_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension III":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE:
    makernotes_ultimate_adv_ext_iv_count = get_makernotes_ultimate_advanced_extension_iv_field_count()
    fields3['MakerNotes Ultimate Advanced Extension IV'] = makernotes_ultimate_adv_ext_iv_count
    print(f'{"MakerNotes Ultimate Advanced Extension IV":30s}: {makernotes_ultimate_adv_ext_iv_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension IV":30s}: {0:>5} fields (pending)')

if EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_III_AVAILABLE:
    emerging_technology_ultimate_adv_ext_iii_count = get_emerging_technology_ultimate_advanced_extension_iii_field_count()
    fields3['Emerging Technology Ultimate Advanced Extension III'] = emerging_technology_ultimate_adv_ext_iii_count
    print(f'{"Emerging Technology Ultimate Advanced Extension III":30s}: {emerging_technology_ultimate_adv_ext_iii_count:>5} fields')
else:
    print(f'{"Emerging Technology Ultimate Advanced Extension III":30s}: {0:>5} fields (pending)')

if EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE:
    emerging_technology_ultimate_adv_ext_iv_count = get_emerging_technology_ultimate_advanced_extension_iv_field_count()
    fields3['Emerging Technology Ultimate Advanced Extension IV'] = emerging_technology_ultimate_adv_ext_iv_count
    print(f'{"Emerging Technology Ultimate Advanced Extension IV":30s}: {emerging_technology_ultimate_adv_ext_iv_count:>5} fields')
else:
    print(f'{"Emerging Technology Ultimate Advanced Extension IV":30s}: {0:>5} fields (pending)')

if PDF_OFFICE_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    pdf_office_ultimate_adv_ext_ii_count = get_pdf_office_ultimate_advanced_extension_ii_field_count()
    fields3['PDF Office Ultimate Advanced Extension II'] = pdf_office_ultimate_adv_ext_ii_count
    print(f'{"PDF Office Ultimate Advanced Extension II":30s}: {pdf_office_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"PDF Office Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

if ID3_AUDIO_ULTIMATE_ADVANCED_EXTENSION_II_AVAILABLE:
    id3_audio_ultimate_adv_ext_ii_count = get_id3_audio_ultimate_advanced_extension_ii_field_count()
    fields3['ID3 Audio Ultimate Advanced Extension II'] = id3_audio_ultimate_adv_ext_ii_count
    print(f'{"ID3 Audio Ultimate Advanced Extension II":30s}: {id3_audio_ultimate_adv_ext_ii_count:>5} fields')
else:
    print(f'{"ID3 Audio Ultimate Advanced Extension II":30s}: {0:>5} fields (pending)')

# New batch: print blocks for generated modules
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_liv_count = get_scientific_dicom_fits_ultimate_advanced_extension_liv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LIV'] = scientific_dicom_fits_ultimate_adv_ext_liv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_liv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lv_count = get_scientific_dicom_fits_ultimate_advanced_extension_lv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LV'] = scientific_dicom_fits_ultimate_adv_ext_lv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LV":30s}: {scientific_dicom_fits_ultimate_adv_ext_lv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_lvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LVI'] = scientific_dicom_fits_ultimate_adv_ext_lvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_lvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LVII'] = scientific_dicom_fits_ultimate_adv_ext_lvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LVIII'] = scientific_dicom_fits_ultimate_adv_ext_lviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lix_count = get_scientific_dicom_fits_ultimate_advanced_extension_lix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LIX'] = scientific_dicom_fits_ultimate_adv_ext_lix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_lix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LIX":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE:
    forensic_security_ultimate_adv_ext_xii_count = get_forensic_security_ultimate_advanced_extension_xii_field_count()
    fields3['Forensic Security Ultimate Advanced Extension XII'] = forensic_security_ultimate_adv_ext_xii_count
    print(f'{"Forensic Security Ultimate Advanced Extension XII":30s}: {forensic_security_ultimate_adv_ext_xii_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate Advanced Extension XII":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE:
    makernotes_ultimate_adv_ext_xiii_count = get_makernotes_ultimate_advanced_extension_xiii_field_count()
    fields3['MakerNotes Ultimate Advanced Extension XIII'] = makernotes_ultimate_adv_ext_xiii_count
    print(f'{"MakerNotes Ultimate Advanced Extension XIII":30s}: {makernotes_ultimate_adv_ext_xiii_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension XIII":30s}: {0:>5} fields (pending)')

if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XII_AVAILABLE:
    video_professional_ultimate_adv_ext_xii_count = get_video_professional_ultimate_advanced_extension_xii_field_count()
    fields3['Video Professional Ultimate Advanced Extension XII'] = video_professional_ultimate_adv_ext_xii_count
    print(f'{"Video Professional Ultimate Advanced Extension XII":30s}: {video_professional_ultimate_adv_ext_xii_count:>5} fields')
else:
    print(f'{"Video Professional Ultimate Advanced Extension XII":30s}: {0:>5} fields (pending)')

if EMERGING_TECHNOLOGY_ULTIMATE_ADVANCED_EXTENSION_XI_AVAILABLE:
    emerging_technology_ultimate_adv_ext_xi_count = get_emerging_technology_ultimate_advanced_extension_xi_field_count()
    fields3['Emerging Technology Ultimate Advanced Extension XI'] = emerging_technology_ultimate_adv_ext_xi_count
    print(f'{"Emerging Technology Ultimate Advanced Extension XI":30s}: {emerging_technology_ultimate_adv_ext_xi_count:>5} fields')
else:
    print(f'{"Emerging Technology Ultimate Advanced Extension XI":30s}: {0:>5} fields (pending)')

# Next batch: print blocks (Scientific LX–LXVII, Forensic XIII, MakerNotes XIV)
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lx_count = get_scientific_dicom_fits_ultimate_advanced_extension_lx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LX'] = scientific_dicom_fits_ultimate_adv_ext_lx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LX":30s}: {scientific_dicom_fits_ultimate_adv_ext_lx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXI'] = scientific_dicom_fits_ultimate_adv_ext_lxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXII'] = scientific_dicom_fits_ultimate_adv_ext_lxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXIII'] = scientific_dicom_fits_ultimate_adv_ext_lxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXIV'] = scientific_dicom_fits_ultimate_adv_ext_lxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXV'] = scientific_dicom_fits_ultimate_adv_ext_lxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXVI'] = scientific_dicom_fits_ultimate_adv_ext_lxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXVII'] = scientific_dicom_fits_ultimate_adv_ext_lxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVII":30s}: {0:>5} fields (pending)')

# Next iteration prints for LXVIII–LXXV and Video XIII
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXVIII'] = scientific_dicom_fits_ultimate_adv_ext_lxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxix_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXIX'] = scientific_dicom_fits_ultimate_adv_ext_lxix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxx_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXX'] = scientific_dicom_fits_ultimate_adv_ext_lxx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXX":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXXI'] = scientific_dicom_fits_ultimate_adv_ext_lxxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXXII'] = scientific_dicom_fits_ultimate_adv_ext_lxxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXXIII'] = scientific_dicom_fits_ultimate_adv_ext_lxxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXXIV'] = scientific_dicom_fits_ultimate_adv_ext_lxxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_lxxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension LXXV'] = scientific_dicom_fits_ultimate_adv_ext_lxxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_lxxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension LXXV":30s}: {0:>5} fields (pending)')

# Added print blocks for Scientific DICOM FITS Ultimate Advanced Extension XCI–C
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xci_count = get_scientific_dicom_fits_ultimate_advanced_extension_xci_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCI'] = scientific_dicom_fits_ultimate_adv_ext_xci_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCI":30s}: {scientific_dicom_fits_ultimate_adv_ext_xci_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCII'] = scientific_dicom_fits_ultimate_adv_ext_xcii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xciii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xciii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCIII'] = scientific_dicom_fits_ultimate_adv_ext_xciii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xciii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xciv_count = get_scientific_dicom_fits_ultimate_advanced_extension_xciv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCIV'] = scientific_dicom_fits_ultimate_adv_ext_xciv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_xciv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcv_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCV'] = scientific_dicom_fits_ultimate_adv_ext_xcv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCV":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCVI'] = scientific_dicom_fits_ultimate_adv_ext_xcvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCVII'] = scientific_dicom_fits_ultimate_adv_ext_xcvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCVIII'] = scientific_dicom_fits_ultimate_adv_ext_xcviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XCIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_xcix_count = get_scientific_dicom_fits_ultimate_advanced_extension_xcix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension XCIX'] = scientific_dicom_fits_ultimate_adv_ext_xcix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_xcix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension XCIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_C_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_c_count = get_scientific_dicom_fits_ultimate_advanced_extension_c_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension C'] = scientific_dicom_fits_ultimate_adv_ext_c_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension C":30s}: {scientific_dicom_fits_ultimate_adv_ext_c_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension C":30s}: {0:>5} fields (pending)')

# Added print-summary blocks for SCIENTIFIC DICOM FITS CI–CX
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_ci_count = get_scientific_dicom_fits_ultimate_advanced_extension_ci_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CI'] = scientific_dicom_fits_ultimate_adv_ext_ci_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CI":30s}: {scientific_dicom_fits_ultimate_adv_ext_ci_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CII'] = scientific_dicom_fits_ultimate_adv_ext_cii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_ciii_count = get_scientific_dicom_fits_ultimate_advanced_extension_ciii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CIII'] = scientific_dicom_fits_ultimate_adv_ext_ciii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_ciii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_civ_count = get_scientific_dicom_fits_ultimate_advanced_extension_civ_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CIV'] = scientific_dicom_fits_ultimate_adv_ext_civ_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_civ_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIV":30s}: {0:>5} fields (pending)')

# Added print-summary blocks for SCIENTIFIC DICOM FITS CXI–CXX
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXI'] = scientific_dicom_fits_ultimate_adv_ext_cxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXII'] = scientific_dicom_fits_ultimate_adv_ext_cxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXIII'] = scientific_dicom_fits_ultimate_adv_ext_cxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXIV'] = scientific_dicom_fits_ultimate_adv_ext_cxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXV'] = scientific_dicom_fits_ultimate_adv_ext_cxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXVI'] = scientific_dicom_fits_ultimate_adv_ext_cxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXVII'] = scientific_dicom_fits_ultimate_adv_ext_cxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXVIII'] = scientific_dicom_fits_ultimate_adv_ext_cxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxix_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXIX'] = scientific_dicom_fits_ultimate_adv_ext_cxix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxx_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXX'] = scientific_dicom_fits_ultimate_adv_ext_cxx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXX":30s}: {0:>5} fields (pending)')

# Print-summary for SCIENTIFIC DICOM FITS CXXI–CXXX
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXI'] = scientific_dicom_fits_ultimate_adv_ext_cxxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXII'] = scientific_dicom_fits_ultimate_adv_ext_cxxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXIII'] = scientific_dicom_fits_ultimate_adv_ext_cxxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXIV'] = scientific_dicom_fits_ultimate_adv_ext_cxxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXV'] = scientific_dicom_fits_ultimate_adv_ext_cxxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXVI'] = scientific_dicom_fits_ultimate_adv_ext_cxxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXVII'] = scientific_dicom_fits_ultimate_adv_ext_cxxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXVIII'] = scientific_dicom_fits_ultimate_adv_ext_cxxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxix_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXIX'] = scientific_dicom_fits_ultimate_adv_ext_cxxix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxx_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXX'] = scientific_dicom_fits_ultimate_adv_ext_cxxx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXX":30s}: {0:>5} fields (pending)')

# Print-summary for SCIENTIFIC DICOM FITS CXXXI–CXL
if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXI'] = scientific_dicom_fits_ultimate_adv_ext_cxxxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXII'] = scientific_dicom_fits_ultimate_adv_ext_cxxxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXIII'] = scientific_dicom_fits_ultimate_adv_ext_cxxxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXIV'] = scientific_dicom_fits_ultimate_adv_ext_cxxxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXV'] = scientific_dicom_fits_ultimate_adv_ext_cxxxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXVI'] = scientific_dicom_fits_ultimate_adv_ext_cxxxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXVII'] = scientific_dicom_fits_ultimate_adv_ext_cxxxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXXXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxxxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxxxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXXXVIII'] = scientific_dicom_fits_ultimate_adv_ext_cxxxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxxxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXXXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxli_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxli_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLI'] = scientific_dicom_fits_ultimate_adv_ext_cxli_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxli_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLII'] = scientific_dicom_fits_ultimate_adv_ext_cxlii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxliii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxliii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLIII'] = scientific_dicom_fits_ultimate_adv_ext_cxliii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxliii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxliv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxliv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLIV'] = scientific_dicom_fits_ultimate_adv_ext_cxliv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxliv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLV'] = scientific_dicom_fits_ultimate_adv_ext_cxlv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLVI'] = scientific_dicom_fits_ultimate_adv_ext_cxlvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLVII'] = scientific_dicom_fits_ultimate_adv_ext_cxlvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLVIII'] = scientific_dicom_fits_ultimate_adv_ext_cxlviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CXLIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cxlix_count = get_scientific_dicom_fits_ultimate_advanced_extension_cxlix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CXLIX'] = scientific_dicom_fits_ultimate_adv_ext_cxlix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cxlix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CXLIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CL_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cl_count = get_scientific_dicom_fits_ultimate_advanced_extension_cl_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CL'] = scientific_dicom_fits_ultimate_adv_ext_cl_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CL":30s}: {scientific_dicom_fits_ultimate_adv_ext_cl_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CL":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXI'] = scientific_dicom_fits_ultimate_adv_ext_clxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXII'] = scientific_dicom_fits_ultimate_adv_ext_clxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXIII'] = scientific_dicom_fits_ultimate_adv_ext_clxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXIV'] = scientific_dicom_fits_ultimate_adv_ext_clxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXV'] = scientific_dicom_fits_ultimate_adv_ext_clxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXVI'] = scientific_dicom_fits_ultimate_adv_ext_clxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXVII'] = scientific_dicom_fits_ultimate_adv_ext_clxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXVIII'] = scientific_dicom_fits_ultimate_adv_ext_clxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxix_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXIX'] = scientific_dicom_fits_ultimate_adv_ext_clxix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxx_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXX'] = scientific_dicom_fits_ultimate_adv_ext_clxx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxi_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXI'] = scientific_dicom_fits_ultimate_adv_ext_clxxi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXI":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXII'] = scientific_dicom_fits_ultimate_adv_ext_clxxii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxiii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxiii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXIII'] = scientific_dicom_fits_ultimate_adv_ext_clxxiii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxiii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxiv_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxiv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXIV'] = scientific_dicom_fits_ultimate_adv_ext_clxxiv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxiv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxv_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXV'] = scientific_dicom_fits_ultimate_adv_ext_clxxv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXV":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXVI'] = scientific_dicom_fits_ultimate_adv_ext_clxxvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXVII'] = scientific_dicom_fits_ultimate_adv_ext_clxxvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXVIII'] = scientific_dicom_fits_ultimate_adv_ext_clxxviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxix_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXIX'] = scientific_dicom_fits_ultimate_adv_ext_clxxix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLXXX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clxxx_count = get_scientific_dicom_fits_ultimate_advanced_extension_clxxx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLXXX'] = scientific_dicom_fits_ultimate_adv_ext_clxxx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clxxx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLXXX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cli_count = get_scientific_dicom_fits_ultimate_advanced_extension_cli_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLI'] = scientific_dicom_fits_ultimate_adv_ext_cli_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cli_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLII'] = scientific_dicom_fits_ultimate_adv_ext_clii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cliii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cliii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLIII'] = scientific_dicom_fits_ultimate_adv_ext_cliii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cliii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cliv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cliv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLIV'] = scientific_dicom_fits_ultimate_adv_ext_cliv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cliv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clv_count = get_scientific_dicom_fits_ultimate_advanced_extension_clv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLV'] = scientific_dicom_fits_ultimate_adv_ext_clv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLV":30s}: {scientific_dicom_fits_ultimate_adv_ext_clv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_clvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLVI'] = scientific_dicom_fits_ultimate_adv_ext_clvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_clvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLVII'] = scientific_dicom_fits_ultimate_adv_ext_clvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_clviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLVIII'] = scientific_dicom_fits_ultimate_adv_ext_clviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_clviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clix_count = get_scientific_dicom_fits_ultimate_advanced_extension_clix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLIX'] = scientific_dicom_fits_ultimate_adv_ext_clix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CLX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_clx_count = get_scientific_dicom_fits_ultimate_advanced_extension_clx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CLX'] = scientific_dicom_fits_ultimate_adv_ext_clx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLX":30s}: {scientific_dicom_fits_ultimate_adv_ext_clx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CLX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_ciii_count = get_scientific_dicom_fits_ultimate_advanced_extension_ciii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CIII'] = scientific_dicom_fits_ultimate_adv_ext_ciii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_ciii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_civ_count = get_scientific_dicom_fits_ultimate_advanced_extension_civ_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CIV'] = scientific_dicom_fits_ultimate_adv_ext_civ_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIV":30s}: {scientific_dicom_fits_ultimate_adv_ext_civ_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CV_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cv_count = get_scientific_dicom_fits_ultimate_advanced_extension_cv_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CV'] = scientific_dicom_fits_ultimate_adv_ext_cv_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CV":30s}: {scientific_dicom_fits_ultimate_adv_ext_cv_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CV":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVI_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cvi_count = get_scientific_dicom_fits_ultimate_advanced_extension_cvi_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CVI'] = scientific_dicom_fits_ultimate_adv_ext_cvi_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVI":30s}: {scientific_dicom_fits_ultimate_adv_ext_cvi_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVI":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cvii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cvii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CVII'] = scientific_dicom_fits_ultimate_adv_ext_cvii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cvii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CVIII_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cviii_count = get_scientific_dicom_fits_ultimate_advanced_extension_cviii_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CVIII'] = scientific_dicom_fits_ultimate_adv_ext_cviii_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVIII":30s}: {scientific_dicom_fits_ultimate_adv_ext_cviii_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CVIII":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CIX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cix_count = get_scientific_dicom_fits_ultimate_advanced_extension_cix_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CIX'] = scientific_dicom_fits_ultimate_adv_ext_cix_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cix_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CIX":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_CX_AVAILABLE:
    scientific_dicom_fits_ultimate_adv_ext_cx_count = get_scientific_dicom_fits_ultimate_advanced_extension_cx_field_count()
    fields3['Scientific DICOM FITS Ultimate Advanced Extension CX'] = scientific_dicom_fits_ultimate_adv_ext_cx_count
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CX":30s}: {scientific_dicom_fits_ultimate_adv_ext_cx_count:>5} fields')
else:
    print(f'{"Scientific DICOM FITS Ultimate Advanced Extension CX":30s}: {0:>5} fields (pending)')

try:
    if VIDEO_PROFESSIONAL_ULTIMATE_ADVANCED_EXTENSION_XIII_AVAILABLE:
        video_professional_ultimate_adv_ext_xiii_count = get_video_professional_ultimate_advanced_extension_xiii_field_count()
        fields3['Video Professional Ultimate Advanced Extension XIII'] = video_professional_ultimate_adv_ext_xiii_count
        print(f'{"Video Professional Ultimate Advanced Extension XIII":30s}: {video_professional_ultimate_adv_ext_xiii_count:>5} fields')
    else:
        print(f'{"Video Professional Ultimate Advanced Extension XIII":30s}: {0:>5} fields (pending)')
except NameError:
    print(f'{"Video Professional Ultimate Advanced Extension XIII":30s}: {0:>5} fields (pending)')

if FORENSIC_SECURITY_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE:
    forensic_security_ultimate_adv_ext_xiv_count = get_forensic_security_ultimate_advanced_extension_xiv_field_count()
    fields3['Forensic Security Ultimate Advanced Extension XIV'] = forensic_security_ultimate_adv_ext_xiv_count
    print(f'{"Forensic Security Ultimate Advanced Extension XIV":30s}: {forensic_security_ultimate_adv_ext_xiv_count:>5} fields')
else:
    print(f'{"Forensic Security Ultimate Advanced Extension XIV":30s}: {0:>5} fields (pending)')

if MAKERNOTES_ULTIMATE_ADVANCED_EXTENSION_XIV_AVAILABLE:
    makernotes_ultimate_adv_ext_xiv_count = get_makernotes_ultimate_advanced_extension_xiv_field_count()
    fields3['MakerNotes Ultimate Advanced Extension XIV'] = makernotes_ultimate_adv_ext_xiv_count
    print(f'{"MakerNotes Ultimate Advanced Extension XIV":30s}: {makernotes_ultimate_adv_ext_xiv_count:>5} fields')
else:
    print(f'{"MakerNotes Ultimate Advanced Extension XIV":30s}: {0:>5} fields (pending)')

print()
print('--- All Specialized Modules Summary ---')
for name, count in fields3.items():
    print(f'{name:30s}: {count:>5} fields')
    total += count

print()
print('=' * 70)
print(f'TOTAL: {total} fields')
print('=' * 70)
print()
# Configurable progress display: use TARGET_FIELD_GOAL if set, otherwise show summary without percent/remaining
if TARGET_FIELD_GOAL:
    pct = 100.0 * total / TARGET_FIELD_GOAL if TARGET_FIELD_GOAL else 0.0
    remaining = TARGET_FIELD_GOAL - total
    print(f'Progress toward configured field target ({TARGET_FIELD_GOAL:,} fields):')
    print(f'  Current: {total:,} fields ({pct:.1f}% of target)')
    if remaining > 0:
        print(f'  Remaining: {remaining:,} fields to reach full coverage')
    else:
        print(f'  Target achieved by {-remaining:,} fields')
else:
    print('Progress summary (no fixed field target set):')
    print(f'  Current: {total:,} fields')

print()
print('Field domain breakdown (no fixed target):')
print(f'  MakerNotes (Camera Vendors):   ~8,000 fields → Need ~4,100 more')
print(f'  ID3v2/Audio Tags:              ~2,500 fields → Need ~2,000 more')
print(f'  PDF/Office Documents:          ~3,000 fields → Need ~2,500 more')
print(f'  Video/Professional:            ~5,000 fields → Need ~3,200 more')
print(f'  Scientific/DICOM/FITS:         ~8,000 fields → Need ~7,000 more')
print(f'  Forensic/Security:             ~5,000 fields → Need ~4,700 more')
print(f'  Emerging (AI/NFT/AR/IoT):      ~3,500 fields → Need ~3,000 more')
print('=' * 70)

# Master consolidation files - NEW
try:
    from audio_master import get_audio_master_field_count
    AUDIO_MASTER_AVAILABLE = True
except:
    AUDIO_MASTER_AVAILABLE = False

try:
    from video_master import get_video_master_field_count
    VIDEO_MASTER_AVAILABLE = True
except:
    VIDEO_MASTER_AVAILABLE = False

try:
    from document_master import get_document_master_field_count
    DOCUMENT_MASTER_AVAILABLE = True
except:
    DOCUMENT_MASTER_AVAILABLE = False

try:
    from scientific_master import get_scientific_master_field_count
    SCIENTIFIC_MASTER_AVAILABLE = True
except:
    SCIENTIFIC_MASTER_AVAILABLE = False

print()
print('--- Master Consolidation Files (NEW) ---')
master_total = 0

if AUDIO_MASTER_AVAILABLE:
    audio_master_count = get_audio_master_field_count()
    print(f'{"Audio Master":30s}: {audio_master_count:>5} fields')
    total += audio_master_count
    master_total += audio_master_count
else:
    print(f'{"Audio Master":30s}: {0:>5} fields (pending)')

if VIDEO_MASTER_AVAILABLE:
    video_master_count = get_video_master_field_count()
    print(f'{"Video Master":30s}: {video_master_count:>5} fields')
    total += video_master_count
    master_total += video_master_count
else:
    print(f'{"Video Master":30s}: {0:>5} fields (pending)')

if DOCUMENT_MASTER_AVAILABLE:
    document_master_count = get_document_master_field_count()
    print(f'{"Document Master":30s}: {document_master_count:>5} fields')
    total += document_master_count
    master_total += document_master_count
else:
    print(f'{"Document Master":30s}: {0:>5} fields (pending)')

if SCIENTIFIC_MASTER_AVAILABLE:
    scientific_master_count = get_scientific_master_field_count()
    print(f'{"Scientific Master":30s}: {scientific_master_count:>5} fields')
    total += scientific_master_count
    master_total += scientific_master_count
else:
    print(f'{"Scientific Master":30s}: {0:>5} fields (pending)')

print(f'{"Master Total":30s}: {master_total:>5} fields')

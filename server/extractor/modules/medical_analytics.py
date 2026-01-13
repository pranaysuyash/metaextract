"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXX - Gastroenterology Imaging II

This module provides comprehensive extraction of Gastroenterology Imaging parameters
including liver disease, pancreatic disorders, GI oncology, and 
gastroenterology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXX_AVAILABLE = True

GASTROENTEROLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x9001): "gastroenterology_assessment_date",
    (0x0010, 0x9002): "liver_diagnosis",
    (0x0010, 0x9003): "hepatitis_status",
    (0x0010, 0x9004): "hepatitis_a",
    (0x0010, 0x9005): "hepatitis_b",
    (0x0010, 0x9006): "hepatitis_c",
    (0x0010, 0x9007): "hepatitis_d",
    (0x0010, 0x9008): "hepatitis_e",
    (0x0010, 0x9009): "alcoholic_liver_disease",
    (0x0010, 0x9010): "nash_indicator",
    (0x0010, 0x9011): "nafl_indicator",
    (0x0010, 0x9012): "cirrhosis_indicator",
    (0x0010, 0x9013): "child_pugh_score",
    (0x0010, 0x9014): "child_pugh_class",
    (0x0010, 0x9015): "meld_score",
    (0x0010, 0x9016): "meld_na_score",
    (0x0010, 0x9017): "liver_function_tests",
    (0x0010, 0x9018): "alt_level",
    (0x0010, 0x9019): "ast_level",
    (0x0010, 0x9020): "alp_level",
    (0x0010, 0x9021): "ggt_level",
    (0x0010, 0x9022): "bilirubin_total",
    (0x0010, 0x9023): "bilirubin_direct",
    (0x0010, 0x9024): "albumin_level",
    (0x0010, 0x9025): "pt_level",
    (0x0010, 0x9026): "inr_value",
    (0x0010, 0x9027): "platelet_count",
    (0x0010, 0x9028): "fibrosis_score",
    (0x0010, 0x9029): "fibroscan_value",
    (0x0010, 0x9030): "liver_stiffness",
    (0x0010, 0x9031): "pancreatic_diagnosis",
    (0x0010, 0x9032): "acute_pancreatitis",
    (0x0010, 0x9033): "chronic_pancreatitis",
    (0x0010, 0x9034): "pancreatic_cancer",
    (0x0010, 0x9035): "ipmn_indicator",
    (0x0010, 0x9036): "mcn_indicator",
    (0x0010, 0x9037): "scn_indicator",
    (0x0010, 0x9038): "pnet_indicator",
    (0x0010, 0x9039): "amylase_level",
    (0x0010, 0x9040): "lipase_level",
    (0x0010, 0x9041): "egd_findings",
    (0x0010, 0x9042): "colonoscopy_findings",
    (0x0010, 0x9043): "gi_bleeding_indicator",
    (0x0010, 0x9044): "upper_gi_bleed",
    (0x0010, 0x9045): "lower_gi_bleed",
    (0x0010, 0x9046): "occult_bleeding",
    (0x0010, 0x9047): "ibd_indicator",
    (0x0010, 0x9048): "crohns_disease",
    (0x0010, 0x9049): "ulcerative_colitis",
    (0x0010, 0x9050): "ibd_location",
    (0x0010, 0x9051): "ibd_behavior",
    (0x0010, 0x9052): "ibd_complications",
    (0x0010, 0x9053): "celiac_disease",
    (0x0010, 0x9054): "gerd_indicator",
    (0x0010, 0x9055): "barretts_esophagus",
    (0x0010, 0x9056): "esophageal_varices",
    (0x0010, 0x9057): "portal_hypertension",
    (0x0010, 0x9058): "ascites_indicator",
    (0x0010, 0x9059): "hepatic_encephalopathy",
}

GI_ONCOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9101): "esophageal_cancer_indicator",
    (0x0018, 0x9102): "esophageal_cancer_type",
    (0x0018, 0x9103): "esophageal_squamous",
    (0x0018, 0x9104): "esophageal_adenocarcinoma",
    (0x0018, 0x9105): "esophageal_cancer_stage",
    (0x0018, 0x9106): "gastric_cancer_indicator",
    (0x0018, 0x9107): "gastric_adenocarcinoma",
    (0x0018, 0x9108): "gastric_linitis_plastica",
    (0x0018, 0x9109): "gastric_malt_lymphoma",
    (0x0018, 0x9110): "gastric_cancer_stage",
    (0x0018, 0x9111): "pancreatic_cancer_stage",
    (0x0018, 0x9112): "pdac_indicator",
    (0x0018, 0x9113): "ampullary_cancer",
    (0x0018, 0x9114): "distal_cholangiocarcinoma",
    (0x0018, 0x9115): "duodenal_cancer",
    (0x0018, 0x9116): "small_bowel_cancer",
    (0x0018, 0x9117): "colorectal_cancer",
    (0x0018, 0x9118): "colon_cancer",
    (0x0018, 0x9119): "rectal_cancer",
    (0x0018, 0x9120): "anal_cancer",
    (0x0018, 0x9121): "gi_stromal_tumor",
    (0x0018, 0x9122): "gist_indicator",
    (0x0018, 0x9123): "neuroendocrine_tumor",
    (0x0018, 0x9124): "carcinoid_tumor",
    (0x0018, 0x9125): "liver_metastasis",
    (0x0018, 0x9126): "peritoneal_carcinomatosis",
    (0x0018, 0x9127): "carcinoembryonic_antigen",
    (0x0018, 0x9128): "ca19_9_level",
    (0x0018, 0x9129): "ca125_level",
    (0x0018, 0x9130): "alpha_fetoprotein",
    (0x0018, 0x9131): "pvc_level",
    (0x0018, 0x9132): "ki67_index",
    (0x0018, 0x9133): "her2_status",
    (0x0018, 0x9134): "msi_status",
    (0x0018, 0x9135): "mismatch_repair",
    (0x0018, 0x9136): "kras_mutation",
    (0x0018, 0x9137): "nras_mutation",
    (0x0018, 0x9138): "braf_mutation",
    (0x0018, 0x9139): "pik3ca_mutation",
    (0x0018, 0x9140): "egfr_expression",
    (0x0018, 0x9141): "vegfa_expression",
    (0x0018, 0x9142): "pd_l1_expression",
    (0x0018, 0x9143): "tumor_mutational_burden",
    (0x0018, 0x9144): "liquid_biopsy_findings",
    (0x0018, 0x9145): "ctdna_results",
    (0x0018, 0x9146): "polyp_detection",
    (0x0018, 0x9147): "adenoma_detection",
    (0x0018, 0x9148): "serrated_lesion",
    (0x0018, 0x9149): "dysplasia_grade",
}

LIVER_IMAGING_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
    (0x0020, 0x4000): "image_comments",
    (0x0028, 0x0002): "samples_per_pixel",
    (0x0028, 0x0004): "photometric_interpretation",
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
    (0x0028, 0x0030): "pixel_spacing",
    (0x0028, 0x0100): "bits_allocated",
    (0x0028, 0x0101): "bits_stored",
    (0x0028, 0x0102): "high_bit",
    (0x0028, 0x0103): "pixel_representation",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0018, 0x9201): "liver_lesion_indicator",
    (0x0018, 0x9202): "focal_lesion_liver",
    (0x0018, 0x9203): "hemangioma_liver",
    (0x0018, 0x9204): "focal_nodular_hyperplasia",
    (0x0018, 0x9205): "hepatic_adenoma",
    (0x0018, 0x9206): "hepatocellular_carcinoma",
    (0x0018, 0x9207): "hcc_indicator",
    (0x0018, 0x9208): "hcc_size",
    (0x0018, 0x9209): "hcc_number",
    (0x0018, 0x9210): "hcc_location",
    (0x0018, 0x9211): "hcc_vascular_invasion",
    (0x0018, 0x9212): "hcc_differentiation",
    (0x0018, 0x9213): "cholangiocarcinoma",
    (0x0018, 0x9214): "klatskin_tumor",
    (0x0018, 0x9215): "hilar_cholangiocarcinoma",
    (0x0018, 0x9216): "intrahepatic_cholangiocarcinoma",
    (0x0018, 0x9217): "metastatic_liver_disease",
    (0x0018, 0x9218): "liver_cyst",
    (0x0018, 0x9219): "simple_cyst_liver",
    (0x0018, 0x9220): "complex_cyst_liver",
    (0x0018, 0x9221): "pyogenic_abscess",
    (0x0018, 0x9222): "amebic_abscess",
    (0x0018, 0x9223): "echinococcal_cyst",
    (0x0018, 0x9224): "liver_contusion",
    (0x0018, 0x9225): "liver_laceration",
    (0x0018, 0x9226): "liver_hematoma",
    (0x0018, 0x9227): "liver_fat_fraction",
    (0x0018, 0x9228): "mri_pdff",
    (0x0018, 0x9229): "iron_overload",
    (0x0018, 0x9230): "hemochromatosis",
    (0x0018, 0x9231): "secondary_iron",
    (0x0018, 0x9232): "liver_segmental_anatomy",
    (0x0018, 0x9233): "couinaud_segments",
    (0x0018, 0x9234): "liver_volumetry",
    (0x0018, 0x9235): "future_liver_remnant",
    (0x0018, 0x9236): "portal_vein_thrombosis",
    (0x0018, 0x9237): "splenic_vein_thrombosis",
    (0x0018, 0x9238): "hepatic_artery_thrombosis",
    (0x0018, 0x9239): "hepatic_vein_thrombosis",
    (0x0018, 0x9240): "budd_chiari_syndrome",
    (0x0018, 0x9241): "portal_hypertension_signs",
    (0x0018, 0x9242): "varices_presence",
    (0x0018, 0x9243): "splenomegaly",
    (0x0018, 0x9244): "collateral_vessels",
    (0x0018, 0x9245): "caput_medusae",
    (0x0018, 0x9246): "liver_transplant_status",
    (0x0018, 0x9247): "transplant_date_liver",
    (0x0018, 0x9248): "graft_function_liver",
    (0x0018, 0x9249): "rejection_liver",
}

GI_IMAGING_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x9301): "liver_ct_protocol",
    (0x0018, 0x9302): "triphasic_liver_ct",
    (0x0018, 0x9303): "arterial_phase_liver",
    (0x0018, 0x9304): "portal_venous_phase",
    (0x0018, 0x9305): "delayed_phase_liver",
    (0x0018, 0x9306): "liver_mri_protocol",
    (0x0018, 0x9307): "mri_liver_diffusion",
    (0x0018, 0x9308): "mri_hepatobiliary",
    (0x0018, 0x9309): "gadoxetate_disodium",
    (0x0018, 0x9310): "mri_liver_vascular",
    (0x0018, 0x9311): "ct_enterography",
    (0x0018, 0x9312): "mr_enterography",
    (0x0018, 0x9313): "enteric_contrast",
    (0x0018, 0x9314): "pancreas_protocol",
    (0x0018, 0x9315): "pancreas_ct",
    (0x0018, 0x9316): "pancreas_mri",
    (0x0018, 0x9317): "secretin_mri",
    (0x0018, 0x9318): "eus_protocol",
    (0x0018, 0x9319): "endoscopic_ultrasound",
    (0x0018, 0x9320): "eus_fna",
    (0x0018, 0x9321): "eus_ebus",
    (0x0018, 0x9322): "ercp_protocol",
    (0x0018, 0x9323): "mrcp_protocol",
    (0x0018, 0x9324): "mr_spectroscopy_liver",
    (0x0018, 0x9325): "elastography_liver",
    (0x0018, 0x9326): "transient_elastography",
    (0x0018, 0x9327): "shear_wave_elastography",
    (0x0018, 0x9328): "contrast_enhanced_ultrasound",
    (0x0018, 0x9329): "ceus_liver",
    (0x0018, 0x9330): "pet_ct_gi",
    (0x0018, 0x9331): "fdg_pet_gi",
    (0x0018, 0x9332): "octreotide_scan",
    (0x0018, 0x9333): "gallium_scan",
    (0x0018, 0x9334): "wbc_scan_abdomen",
    (0x0018, 0x9335): "gi_barium_study",
    (0x0018, 0x9336): "upper_gi_series",
    (0x0018, 0x9337): "small_bowel_follow",
    (0x0018, 0x9338): "barium_enema",
    (0x0018, 0x9339): "ct_colonography",
    (0x0018, 0x9340): "virtual_colonoscopy",
    (0x0018, 0x9341): "capsule_endoscopy",
    (0x0018, 0x9342): "balloon_assisted_endoscopy",
    (0x0018, 0x9343): "enteroscopy_protocol",
    (0x0018, 0x9344): "colonoscopy_protocol",
    (0x0018, 0x9345): "sigmoidoscopy_protocol",
    (0x0018, 0x9346): "egd_protocol",
    (0x0018, 0x9347): "endoscopy_protocol",
    (0x0018, 0x9348): "manometry_protocol",
    (0x0018, 0x9349): "ph_impedance",
    (0x0018, 0x9350): "bravo_ph",
}

GI_OUTCOMES_TAGS = {
    (0x0018, 0x9401): "liver_cancer_survival",
    (0x0018, 0x9402): "hcc_survival",
    (0x0018, 0x9403): "transplant_free_survival",
    (0x0018, 0x9404): "decompensation_events",
    (0x0018, 0x9405): "variceal_bleed",
    (0x0018, 0x9406): "ascites_event",
    (0x0018, 0x9407): "hepatic_encephalopathy_event",
    (0x0018, 0x9408): "jaundice_event",
    (0x0018, 0x9409): "spontaneous_bacterial_peritonitis",
    (0x0018, 0x9410): "hcc_treatment_response",
    (0x0018, 0x9411): "recist_response",
    (0x0018, 0x9412): "mrecist_response",
    (0x0018, 0x9413): "locoregional_therapy",
    (0x0018, 0x9414): "tace_response",
    (0x0018, 0x9415): "y90_response",
    (0x0018, 0x9416): "rfa_response",
    (0x0018, 0x9417): "sbrt_response",
    (0x0018, 0x9418): "systemic_therapy_response",
    (0x0018, 0x9419): "immunotherapy_response",
    (0x0018, 0x9420): "targeted_therapy_response",
    (0x0018, 0x9421): "pancreatic_cancer_survival",
    (0x0018, 0x9422): "resectability_status",
    (0x0018, 0x9423): "borderline_resectable",
    (0x0018, 0x9424): "locally_advanced",
    (0x0018, 0x9425): "metastatic_pancreas",
    (0x0018, 0x9426): "neoadjuvant_response",
    (0x0018, 0x9427): "pathologic_response",
    (0x0018, 0x9428): "colorectal_cancer_survival",
    (0x0018, 0x9429): "colon_cancer_stage",
    (0x0018, 0x9430): "rectal_cancer_response",
    (0x0018, 0x9431): "watch_and_wait",
    (0x0018, 0x9432): "complete_clinical_response",
    (0x0018, 0x9433): "ibd_outcomes",
    (0x0018, 0x9434): "remission_ibd",
    (0x0018, 0x9435): "relapse_ibd",
    (0x0018, 0x9436): "complication_ibd",
    (0x0018, 0x9437): "stricture_ibd",
    (0x0018, 0x9438): "fistula_ibd",
    (0x0018, 0x9439): "abscess_ibd",
    (0x0018, 0x9440): "surgery_ibd",
    (0x0018, 0x9441): "resection_ibd",
    (0x0018, 0x9442): "ostomy_ibd",
    (0x0018, 0x9443): "quality_of_life_gi",
    (0x0018, 0x9444): "sf36_gi",
    (0x0018, 0x9445): "cliqy_score",
    (0x0018, 0x9446): "sibdq_score",
    (0x0018, 0x9447): "pbi_score",
    (0x0018, 0x9448): "nutrition_gi",
    (0x0018, 0x9449): "sga_gi",
    (0x0018, 0x9450): "weight_change_gi",
}

TOTAL_TAGS_LXXX = {}

TOTAL_TAGS_LXXX.update(GASTROENTEROLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXX.update(GI_ONCOLOGY_TAGS)
TOTAL_TAGS_LXXX.update(LIVER_IMAGING_TAGS)
TOTAL_TAGS_LXXX.update(GI_IMAGING_PROTOCOLS)
TOTAL_TAGS_LXXX.update(GI_OUTCOMES_TAGS)


def _extract_tags_lxxx(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXX.items()}
    for tag, name in tag_names.items():
        try:
            if hasattr(ds, '__getitem__'):
                elem = ds.get(tag)
                if elem is not None:
                    try:
                        value = elem.value
                        if isinstance(value, bytes):
                            value = value.decode('utf-8', errors='replace')
                        extracted[name] = value
                    except Exception:
                        extracted[name] = str(elem)
        except Exception:
            pass
    return extracted


def _is_gastroenterology_imaging_file(file_path: str) -> bool:
    gastro_indicators = [
        'gastroenterology', 'gastro', 'liver', 'hepatology', 'pancreas',
        'pancreatic', 'gi_', 'esophageal', 'gastric', 'intestinal',
        'colon', 'colorectal', 'ibd', 'crohns', 'ulcerative_colitis',
        'hepatitis', 'cirrhosis', 'hcc', 'portal_hypertension', 'endoscopy',
        'colonoscopy', 'egd', 'ercp', 'mrcp', 'capsule_endoscopy'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in gastro_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxx(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxx_detected": False,
        "fields_extracted": 0,
        "extension_lxxx_type": "gastroenterology_imaging",
        "extension_lxxx_version": "2.0.0",
        "gastroenterology_patient_parameters": {},
        "gi_oncology": {},
        "liver_imaging": {},
        "gi_imaging_protocols": {},
        "gi_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_gastroenterology_imaging_file(file_path):
            return result

        try:
            import pydicom
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        except ImportError:
            result["extraction_errors"].append("pydicom library not available")
            return result
        except Exception as e:
            result["extraction_errors"].append(f"Failed to read file: {str(e)}")
            return result

        result["extension_lxxx_detected"] = True

        gastro_data = _extract_tags_lxxx(ds)

        patient_params_set = set(GASTROENTEROLOGY_PATIENT_PARAMETERS.keys())
        oncology_set = set(GI_ONCOLOGY_TAGS.keys())
        liver_set = set(LIVER_IMAGING_TAGS.keys())
        protocols_set = set(GI_IMAGING_PROTOCOLS.keys())
        outcomes_set = set(GI_OUTCOMES_TAGS.keys())

        for tag, value in gastro_data.items():
            if tag in patient_params_set:
                result["gastroenterology_patient_parameters"][tag] = value
            elif tag in oncology_set:
                result["gi_oncology"][tag] = value
            elif tag in liver_set:
                result["liver_imaging"][tag] = value
            elif tag in protocols_set:
                result["gi_imaging_protocols"][tag] = value
            elif tag in outcomes_set:
                result["gi_outcomes"][tag] = value

        result["fields_extracted"] = len(gastro_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_field_count() -> int:
    return len(TOTAL_TAGS_LXXX)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_description() -> str:
    return (
        "Gastroenterology Imaging II metadata extraction. Provides comprehensive coverage of "
        "liver disease parameters, pancreatic disorders, GI oncology assessment, "
        "gastroenterology-specific imaging protocols, and GI outcomes measurement."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_modalities() -> List[str]:
    return ["CT", "MR", "US", "CR", "DR", "XA", "PT", "NM", "ES", "GM"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_category() -> str:
    return "Gastroenterology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_keywords() -> List[str]:
    return [
        "gastroenterology", "liver", "hepatology", "pancreas", "pancreatic",
        "HCC", "hepatitis", "cirrhosis", "IBD", "Crohn's", "ulcerative colitis",
        "esophageal cancer", "gastric cancer", "colorectal cancer",
        "colonoscopy", "endoscopy", "ERCP", "MRCP", "portal hypertension"
    ]


# Aliases for smoke test compatibility
def extract_medical_analytics(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_lxxx."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_lxxx(file_path)

def get_medical_analytics_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_field_count()

def get_medical_analytics_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_version()

def get_medical_analytics_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_description()

def get_medical_analytics_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_supported_formats()

def get_medical_analytics_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_lxxx_modalities()

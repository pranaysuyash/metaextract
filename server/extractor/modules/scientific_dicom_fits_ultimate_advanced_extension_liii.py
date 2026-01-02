"""
Scientific DICOM/FITS Ultimate Advanced Extension LIII - Forensic Imaging

This module provides comprehensive extraction of Forensic Imaging parameters
including post-mortem imaging, identification data, trauma documentation,
evidence preservation, and legal/forensic metadata.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LIII_AVAILABLE = True

FORENSIC_CASE_PARAMETERS = {
    (0x0010, 0x1010): "decedent_age",
    (0x0010, 0x1020): "decedent_height",
    (0x0010, 0x1030): "decedent_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2203): "case_number",
    (0x0010, 0x2204): "autopsy_number",
    (0x0010, 0x2205): "jurisdiction",
    (0x0010, 0x2206): "investigating_agency",
    (0x0010, 0x2207): "medical_examiner",
    (0x0010, 0x2208): "forensic_anthropologist",
    (0x0010, 0x2209): "date_of_death",
    (0x0010, 0x2210): "time_of_death",
    (0x0010, 0x2211): "date_of_examination",
    (0x0010, 0x2212): "time_of_examination",
    (0x0010, 0x2213): "post_mortem_interval_hours",
    (0x0010, 0x2214): "body_condition",
    (0x0010, 0x2215): "decomposition_stage",
    (0x0010, 0x2216): "body_position",
    (0x0010, 0x2217): "body_location",
    (0x0010, 0x2218): "environmental_conditions",
    (0x0010, 0x2219): "scene_description",
    (0x0010, 0x2220): "witnesses_present",
    (0x0010, 0x2221): "evidence_seized",
    (0x0010, 0x2222): "chain_of_custody_status",
    (0x0010, 0x2223): "next_of_kin_notified",
    (0x0010, 0x2224): "family_contact_information",
    (0x0010, 0x2225): "identification_method",
    (0x0010, 0x2226): "dental_records_available",
    (0x0010, 0x2227): "fingerprints_available",
    (0x0010, 0x2228): "dna_sample_collected",
    (0x0010, 0x2229): "personal_effects",
    (0x0010, 0x2230): "clothing_description",
    (0x0010, 0x2231): "jewelry_description",
    (0x0010, 0x2232): "medical_implants",
    (0x0010, 0x2233): "pacemaker_present",
    (0x0010, 0x2234): "surgical_scars",
    (0x0010, 0x2235): "tattoos_marks",
    (0x0010, 0x2236): "scars_marks",
    (0x0010, 0x2237): "amputations",
    (0x0010, 0x2238): "prosthetics",
    (0x0010, 0x2239): "dental_work",
    (0x0010, 0x2240): "hair_color",
    (0x0010, 0x2241): "eye_color",
    (0x0010, 0x2242): "skin_tone",
    (0x0010, 0x2243): "ethnic_ancestry",
    (0x0010, 0x2244): "estimated_age",
    (0x0010, 0x2245): "estimated_weight",
    (0x0010, 0x2246): "estimated_height",
    (0x0010, 0x2247): "body_build",
    (0x0010, 0x2248): "facial_features",
    (0x0010, 0x2249): "nose_shape",
    (0x0010, 0x2250): "lip_shape",
    (0x0010, 0x2251): "chin_shape",
    (0x0010, 0x2252): "ear_shape",
    (0x0010, 0x2253): "hair_texture",
    (0x0010, 0x2254): "hair_pattern",
    (0x0010, 0x2255): "beard_mustache",
}

POSTMORTEM_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x0087): "echo_train_length",
    (0x0018, 0x0090): "frequency_selection_gradient_orientation",
    (0x0018, 0x0091): "magnetic_field_strength_tesla",
    (0x0018, 0x0095): "pixel_bandwidth",
    (0x0018, 0x0100): "spatial_resolution",
    (0x0018, 0x0150): "parallel_collection_mode",
    (0x0018, 0x0151): "parallel_collection_algorithm",
    (0x0018, 0x0210): "trigger_delay_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9301): "postmortem_imaging_indicator",
    (0x0018, 0x9302): "pmct_protocol_type",
    (0x0018, 0x9303): "angiography_type",
    (0x0018, 0x9304): "contrast_perfusion_type",
    (0x0018, 0x9305): "injection_site",
    (0x0018, 0x9306): "injection_volume_ml",
    (0x0018, 0x9307): "injection_rate_ml_per_sec",
    (0x0018, 0x9308): "circulation_time_seconds",
    (0x0018, 0x9309): "arterial_phase_delay",
    (0x0018, 0x9310): "venous_phase_delay",
    (0x0018, 0x9311): "capillary_phase_delay",
    (0x0018, 0x9312): "body_temperature_celsius",
    (0x0018, 0x9313): "rigor_mortis_stage",
    (0x0018, 0x9314): "livor_mortis_color",
    (0x0018, 0x9315): "livor_mortis_pattern",
    (0x0018, 0x9316): "decomposition_evidence",
    (0x0018, 0x9317): "gas_formation_evidence",
    (0x0018, 0x9318): "mummification_evidence",
    (0x0018, 0x9319): "skeletonization_evidence",
    (0x0018, 0x9320): "skull_fracture_present",
    (0x0018, 0x9321): "skull_fracture_type",
    (0x0018, 0x9322): "skull_fracture_location",
    (0x0018, 0x9323): "brain_injury_present",
    (0x0018, 0x9324): "brain_injury_type",
    (0x0018, 0x9325): "brain_injury_location",
    (0x0018, 0x9326): "hemorrhage_present",
    (0x0018, 0x9327): "hemorrhage_type",
    (0x0018, 0x9328): "hemorrhage_location",
    (0x0018, 0x9329): "hemorrhage_volume_ml",
    (0x0018, 0x9330): "organ_condition",
    (0x0018, 0x9331): "organ_weight_g",
    (0x0018, 0x9332): "pathology_present",
    (0x0018, 0x9333): "pathology_type",
    (0x0018, 0x9334): "pathology_location",
    (0x0018, 0x9335): "foreign_material_present",
    (0x0018, 0x9336): "foreign_material_type",
    (0x0018, 0x9337): "foreign_material_location",
    (0x0018, 0x9338): "bullet_trajectory",
    (0x0018, 0x9339): "knife_wound_count",
    (0x0018, 0x9340): "blunt_force_injury_count",
    (0x0018, 0x9341): "thermal_injury_present",
    (0x0018, 0x9342): "thermal_injury_degree",
    (0x0018, 0x9343): "thermal_injury_percentage",
    (0x0018, 0x9344): "chemical_injury_present",
    (0x0018, 0x9345): "electrical_injury_present",
    (0x0018, 0x9346): "drowning_evidence",
    (0x0018, 0x9347): "asphyxiation_evidence",
    (0x0018, 0x9348): "drug_toxicology_result",
    (0x0018, 0x9349): "alcohol_level_mg_dl",
    (0x0018, 0x9350): "carbon_monoxide_level",
    (0x0018, 0x9351): "cause_of_death_preliminary",
    (0x0018, 0x9352): "manner_of_death",
    (0x0018, 0x9353): "death_classification",
}

TRAUMA_DOCUMENTATION_TAGS = {
    (0x0020, 0x0010): "series_number",
    (0x0020, 0x0011): "instance_number",
    (0x0020, 0x0032): "image_position_patient",
    (0x0020, 0x0037): "image_orientation_patient",
    (0x0020, 0x0050): "location",
    (0x0020, 0x0100): "temporal_position_identifier",
    (0x0020, 0x0105): "number_of_temporal_positions",
    (0x0020, 0x0200): "temporal_reconstruction_type",
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
    (0x0028, 0x1055): "window_center_and_width_explanation",
    (0x0028, 0x2110): "lossy_image_compression",
    (0x0028, 0x2112): "lossy_image_compression_ratio",
    (0x0028, 0x2114): "lossy_image_compression_method",
    (0x0018, 0x9401): "trauma_mechanism",
    (0x0018, 0x9402): "injury_time",
    (0x0018, 0x9403): "injury_location",
    (0x0018, 0x9404): "assailant_information",
    (0x0018, 0x9405): "weapon_type",
    (0x0018, 0x9406): "weapon_description",
    (0x0018, 0x9407): "defensive_wounds_present",
    (0x0018, 0x9408): "defensive_wound_type",
    (0x0018, 0x9409): "defensive_wound_location",
    (0x0018, 0x9410): "transfer_wounds_present",
    (0x0018, 0x9411): "direction_of_force",
    (0x0018, 0x9412): "hesitation_marks_present",
    (0x0018, 0x9413): "pattern_injury_present",
    (0x0018, 0x9414): "pattern_injury_type",
    (0x0018, 0x9415): "pattern_injury_cause",
    (0x0018, 0x9416): "tire_track_pattern",
    (0x0018, 0x9417): "tool_mark_pattern",
    (0x0018, 0x9418): "bite_mark_pattern",
    (0x0018, 0x9419): "glove_prints_present",
    (0x0018, 0x9420): "fiber_evidence_present",
    (0x0018, 0x9421): "hair_evidence_present",
    (0x0018, 0x9422): "biological_stain_present",
    (0x0018, 0x9423): "biological_stain_type",
    (0x0018, 0x9424): "photograph_scale_present",
    (0x0018, 0x9425): "photograph_orientation",
    (0x0018, 0x9426): "measurement_reference",
    (0x0018, 0x9427): "injury_chronology_assessment",
    (0x0018, 0x9428): "wound_age_estimation",
    (0x0018, 0x9429): "vital_reaction_present",
    (0x0018, 0x9430): "bone_reaction_present",
}

LEGAL_EVIDENCE_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0008, 0x1060): "physician_reading_study",
    (0x0008, 0x1070): "operator_name",
    (0x0008, 0x1080): "admitting_diagnoses_description",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x0040): "tr",
    (0x0018, 0x0070): "data_collection_diameter",
    (0x0018, 0x0082): "inversion_time",
    (0x0018, 0x0084): "imaging_frequency",
    (0x0018, 0x0085): "imaged_nucleus",
    (0x0018, 0x0086): "number_of_phase_encoding_steps",
    (0x0018, 0x0160): "parallel_sampling_factor",
    (0x0018, 0x0170): "parallel_acquisition_factor",
    (0x0018, 0x0175): "water_fat_shift_pixels",
    (0x0018, 0x0180): "coil_array_type",
    (0x0018, 0x0181): "active_coil_dimension",
    (0x0018, 0x0194): "mr_acquisition_type",
    (0x0018, 0x0195): "sequence_type",
    (0x0018, 0x0120): "reconstruction_diameter",
    (0x0018, 0x0140): "distortion_correction_type",
    (0x0018, 0x1150): "exposure_time",
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "exposure",
    (0x0018, 0x1160): "filter_material",
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0x9501): "evidence_barcode",
    (0x0018, 0x9502): "evidence_seal_number",
    (0x0018, 0x9503): "collection_date_time",
    (0x0018, 0x9504): "collector_name",
    (0x0018, 0x9505): "collection_location",
    (0x0018, 0x9506): "chain_of_custody_log",
    (0x0018, 0x9507): "evidence_storage_location",
    (0x0018, 0x9508): "access_restrictions",
    (0x0018, 0x9509): "release_authorizations",
    (0x0018, 0x9510): "court_order_present",
    (0x0018, 0x9511): "subpoena_status",
    (0x0018, 0x9512): "discovery_request_status",
    (0x0018, 0x9513): "expert_witness_name",
    (0x0018, 0x9514): "expert_credentials",
    (0x0018, 0x9515): "testimony_date",
    (0x0018, 0x9516): "report_status",
    (0x0018, 0x9517): "report_date",
    (0x0018, 0x9518): "report_author",
    (0x0018, 0x9519): "conclusion_summary",
    (0x0018, 0x9520): "quality_assurance_status",
    (0x0018, 0x9521): "accreditation_status",
    (0x0018, 0x9522): "standard_compliance",
    (0x0018, 0x9523): "validation_studies",
    (0x0018, 0x9524): "proficiency_testing",
    (0x0018, 0x9525): "audit_trail_complete",
    (0x0018, 0x9526): "data_retention_period",
    (0x0018, 0x9527): "destruction_date",
    (0x0018, 0x9528): "digital_signature_present",
    (0x0018, 0x9529): "tamper_evidence_seal",
    (0x0018, 0x9530): "metadata_integrity_check",
}

IDENTIFICATION_DATA_TAGS = {
    (0x0008, 0x0018): "sop_instance_uid",
    (0x0008, 0x0060): "modality",
    (0x0008, 0x0064): "conversion_type",
    (0x0008, 0x0201): "timezone_offset_from_utc",
    (0x0010, 0x0010): "decedent_name",
    (0x0010, 0x0020): "decedent_id",
    (0x0010, 0x0021): "issuer_of_decedent_id",
    (0x0010, 0x0030): "decedent_birth_date",
    (0x0010, 0x0032): "decedent_birth_time",
    (0x0010, 0x0040): "decedent_sex",
    (0x0010, 0x1000): "other_decedent_names",
    (0x0010, 0x1001): "other_decedent_ids",
    (0x0010, 0x1002): "ethnic_group",
    (0x0010, 0x1005): "decedent_birth_name",
    (0x0010, 0x1040): "decedent_address",
    (0x0010, 0x21C0): "pregnancy_status",
    (0x0010, 0x21F0): "decedent_religious_preference",
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0020): "sequence_name",
    (0x0018, 0x9601): "fingerprint_availability",
    (0x0018, 0x9602): "fingerprint_quality",
    (0x0018, 0x9603): "palm_print_availability",
    (0x0018, 0x9604): "foot_print_availability",
    (0x0018, 0x9605): "dental_availability",
    (0x0018, 0x9606): "dental_radiographs_available",
    (0x0018, 0x9607): "dental_charting_complete",
    (0x0018, 0x9608): "dental_restorations",
    (0x0018, 0x9609): "dental_extractions",
    (0x0018, 0x9610): "dental_prosthetics",
    (0x0018, 0x9611): "dental_anomalies",
    (0x0018, 0x9612): "dental_alignment",
    (0x0018, 0x9613): "dental_wisdom_teeth",
    (0x0018, 0x9614): "dental_caries",
    (0x0018, 0x9615): "dental_periodontal_status",
    (0x0018, 0x9616): "dna_sample_available",
    (0x0018, 0x9617): "dna_sample_type",
    (0x0018, 0x9618): "dna_sample_quality",
    (0x0018, 0x9619): "dna_profile_status",
    (0x0018, 0x9620): "dna_database_match",
    (0x0018, 0x9621): "radiograph_availability",
    (0x0018, 0x9622): "radiograph_type",
    (0x0018, 0x9623): "prior_medical_conditions",
    (0x0018, 0x9624): "prior_surgical_history",
    (0x0018, 0x9625): "medication_list",
    (0x0018, 0x9626): "allergies",
    (0x0018, 0x9627): "medical_implants",
    (0x0018, 0x9628): "pacemaker_serial",
    (0x0018, 0x9629): "prosthetic_device_serial",
    (0x0018, 0x9630): "surgical_pin_serial",
    (0x0018, 0x9631): "orthopedic_implant_type",
    (0x0018, 0x9632): "dental_implant_type",
    (0x0018, 0x9633): "facial_reconstruction_available",
    (0x0018, 0x9634): "facial_comparison_status",
    (0x0018, 0x9635): "superimposition_status",
    (0x0018, 0x9636): "anthropometric_measurements",
    (0x0018, 0x9637): "morphological_features",
    (0x0018, 0x9638): "ancestry_indicator",
    (0x0018, 0x9639): "sex_indicator",
    (0x0018, 0x9640): "age_range_indicator",
    (0x0018, 0x9641): "stature_estimation",
    (0x0018, 0x9642): "body_mass_estimation",
    (0x0018, 0x9643): "identification_confidence",
    (0x0018, 0x9644): "positive_identification_status",
    (0x0018, 0x9645): "presumptive_identification_status",
    (0x0018, 0x9646): "exclusion_criteria",
    (0x0018, 0x9647): "next_of_kin_dna",
    (0x0018, 0x9648): "missing_persons_match",
    (0x0018, 0x9649): "disaster_victim_identifier",
    (0x0018, 0x9650): "mass_fatality_incident",
}

TOTAL_TAGS_LIII = (
    FORENSIC_CASE_PARAMETERS | 
    POSTMORTEM_IMAGING_TAGS | 
    TRAUMA_DOCUMENTATION_TAGS | 
    LEGAL_EVIDENCE_TAGS | 
    IDENTIFICATION_DATA_TAGS
)


def _extract_tags_liii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LIII.items():
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


def _is_forensic_imaging_file(file_path: str) -> bool:
    forensic_indicators = [
        'forensic', 'autopsy', 'postmortem', 'pmct', 'mortem',
        'decedent', 'jurisdiction', 'medical_examiner', 'coroner',
        'identification', 'chain_of_custody', 'evidence', 'trauma',
        'fingerprint', 'dental', 'dna', 'victim', 'decomposition'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in forensic_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_liii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_liii_detected": False,
        "fields_extracted": 0,
        "extension_liii_type": "forensic_imaging",
        "extension_liii_version": "2.0.0",
        "forensic_case_parameters": {},
        "postmortem_imaging": {},
        "trauma_documentation": {},
        "legal_evidence": {},
        "identification_data": {},
        "extraction_errors": [],
    }

    try:
        if not _is_forensic_imaging_file(file_path):
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

        result["extension_liii_detected"] = True

        forensic_data = _extract_tags_liii(ds)

        result["forensic_case_parameters"] = {
            k: v for k, v in forensic_data.items()
            if k in FORENSIC_CASE_PARAMETERS.values()
        }
        result["postmortem_imaging"] = {
            k: v for k, v in forensic_data.items()
            if k in POSTMORTEM_IMAGING_TAGS.values()
        }
        result["trauma_documentation"] = {
            k: v for k, v in forensic_data.items()
            if k in TRAUMA_DOCUMENTATION_TAGS.values()
        }
        result["legal_evidence"] = {
            k: v for k, v in forensic_data.items()
            if k in LEGAL_EVIDENCE_TAGS.values()
        }
        result["identification_data"] = {
            k: v for k, v in forensic_data.items()
            if k in IDENTIFICATION_DATA_TAGS.values()
        }

        result["fields_extracted"] = len(forensic_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_field_count() -> int:
    return len(TOTAL_TAGS_LIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_description() -> str:
    return (
        "Forensic Imaging metadata extraction. Provides comprehensive coverage of "
        "post-mortem imaging, identification data, trauma documentation, "
        "evidence preservation, and legal/forensic metadata for medicolegal investigations."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "XA", "RF"]


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_category() -> str:
    return "Forensic Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_liii_keywords() -> List[str]:
    return [
        "forensic imaging", "postmortem", "autopsy", "medicolegal", "identification",
        "chain of custody", "evidence", "trauma documentation", "decedent",
        "postmortem CT", "forensic anthropology", "victim identification",
        "dental forensics", "fingerprint analysis", "DNA profiling", "legal evidence"
    ]

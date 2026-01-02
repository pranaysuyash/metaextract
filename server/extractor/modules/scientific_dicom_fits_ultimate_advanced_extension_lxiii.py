"""
Scientific DICOM/FITS Ultimate Advanced Extension LXIII - Critical Care Imaging

This module provides comprehensive extraction of Critical Care Imaging parameters
including ICU monitoring, ventilator imaging, sepsis protocols, hemodynamic
monitoring, and continuous life support imaging.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXIII_AVAILABLE = True

ICU_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0x2300): "icu_admission_date",
    (0x0010, 0x2301): "icu_admission_time",
    (0x0010, 0x2302): "icu_discharge_date",
    (0x0010, 0x2303): "icu_discharge_time",
    (0x0010, 0x2304): "icu_length_of_stay_days",
    (0x0010, 0x2305): "icu_readmission_indicator",
    (0x0010, 0x2306): "icu_service_type",
    (0x0010, 0x2307): "icu_unit_type",
    (0x0010, 0x2308): "icu_admission_source",
    (0x0010, 0x2309): "icu_admissiondiagnosis",
    (0x0010, 0x2310): "icu_discharge_diagnosis",
    (0x0010, 0x2311): "apache_ii_score",
    (0x0010, 0x2312): "apache_iii_score",
    (0x0010, 0x2313): "sofa_score",
    (0x0010, 0x2314): "saps_ii_score",
    (0x0010, 0x2315): "saps_iii_score",
    (0x0010, 0x2316): "mortality_risk_score",
    (0x0010, 0x2317): "sequential_organ_failure_assessment",
    (0x0010, 0x2318): "quick_sofa_score",
    (0x0010, 0x2319): "glass_score",
    (0x0010, 0x2320): "mechanical_ventilation_days",
    (0x0010, 0x2321): "vasopressor_days",
    (0x0010, 0x2322): "vasoactive_agent_type",
    (0x0010, 0x2323): "renal_replacement_therapy",
    (0x0010, 0x2324): "ecmo_therapy",
    (0x0010, 0x2325): "intra_aortic_balloon_pump",
    (0x0010, 0x2326): "impella_device",
    (0x0010, 0x2327): "main_diagnosis",
    (0x0010, 0x2328): "secondary_diagnosis",
    (0x0010, 0x2329): "comorbidities",
    (0x0010, 0x2330): "infection_status",
    (0x0010, 0x2331): "sepsis_status",
    (0x0010, 0x2332): "septic_shock_indicator",
    (0x0010, 0x2333): "multi_organ_dysfunction",
    (0x0010, 0x2334): "dni_status",
    (0x0010, 0x2335): "dnar_status",
    (0x0010, 0x2336): "code_status",
}

VENTILATOR_IMAGING_TAGS = {
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x0080): "repetition_time",
    (0x0018, 0x0081): "echo_time",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0x9011): "ventilator_mode",
    (0x0018, 0x9012): "tidal_volume_ml",
    (0x0018, 0x9013): "respiratory_rate_set",
    (0x0018, 0x9014): "peep_cm_h2o",
    (0x0018, 0x9015): "fio2_percent",
    (0x0018, 0x9016): "peak_inspiratory_pressure",
    (0x0018, 0x9017): "plateau_pressure",
    (0x0018, 0x9018): "mean_airway_pressure",
    (0x0018, 0x9019): "minute_ventilation",
    (0x0018, 0x9020): "inspiratory_expiratory_ratio",
    (0x0018, 0x9021): "pressure_support_level",
    (0x0018, 0x9022): "pressure_control_level",
    (0x0018, 0x9023): "autopef_level",
    (0x0018, 0x9024): "ventilator_synchrony_mode",
    (0x0018, 0x9025): "lung_compliance",
    (0x0018, 0x9026): "airway_resistance",
    (0x0018, 0x9027): "dead_space_volume",
    (0x0018, 0x9028): "dynamic_hyperinflation",
    (0x0018, 0x9029): "auto_peep",
    (0x0018, 0x9030): "transpulmonary_pressure",
    (0x0018, 0x9031): "esophageal_pressure",
    (0x0018, 0x9032): "diaphragm_ultrasound_parameters",
    (0x0018, 0x9033): "lung_ultrasound_score",
    (0x0018, 0x9034): "chest_xray_ventilator_indicator",
    (0x0018, 0x9035): "prone_positioning_indicator",
    (0x0018, 0x9036): "prone_position_start_time",
    (0x0018, 0x9037): "prone_position_duration",
    (0x0018, 0x9038): "ecg_monitor_artifact",
    (0x0018, 0x9039): "ventilator_artifact",
    (0x0018, 0x9040): "endotracheal_tube_position",
    (0x0018, 0x9041): "tracheostomy_tube_position",
    (0x0018, 0x9042): "central_line_position",
    (0x0018, 0x9043): "ng_tube_position",
    (0x0018, 0x9044): "chest_tube_position",
    (0x0018, 0x9045): "pacer_wires_visualized",
    (0x0018, 0x9046): "ventilator_associated_pneumonia",
    (0x0018, 0x9047): "barotrauma_indicator",
    (0x0018, 0x9048): "volutrauma_indicator",
    (0x0018, 0x9049): "atelectasis_indicator",
    (0x0018, 0x9050): "consolidation_indicator",
}

HEMODYNAMIC_MONITORING_TAGS = {
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
    (0x0018, 0x9061): "systolic_blood_pressure",
    (0x0018, 0x9062): "diastolic_blood_pressure",
    (0x0018, 0x9063): "mean_arterial_pressure",
    (0x0018, 0x9064): "heart_rate_bpm",
    (0x0018, 0x9065): "cardiac_output_l_min",
    (0x0018, 0x9066): "cardiac_index",
    (0x0018, 0x9067): "systemic_vascular_resistance",
    (0x0018, 0x9068): "pulmonary_vascular_resistance",
    (0x0018, 0x9069): "pulmonary_capillary_wedge_pressure",
    (0x0018, 0x9070): "central_venous_pressure",
    (0x0018, 0x9071): "right_atrial_pressure",
    (0x0018, 0x9072): "right_ventricular_pressure",
    (0x0018, 0x9073): "pulmonary_artery_pressure",
    (0x0018, 0x9074): "left_atrial_pressure",
    (0x0018, 0x9075): "left_ventricular_end_diastolic_pressure",
    (0x0018, 0x9076): "mixed_venous_oxygen_saturation",
    (0x0018, 0x9077): "central_venous_oxygen_saturation",
    (0x0018, 0x9078): "arterial_oxygen_saturation",
    (0x0018, 0x9079): "arterial_co2_tension",
    (0x0018, 0x9080): "arterial_ph",
    (0x0018, 0x9081): "lactate_level",
    (0x0018, 0x9082): "base_deficit",
    (0x0018, 0x9083): "hemoglobin_g_dl",
    (0x0018, 0x9084): "hematocrit_percent",
    (0x0018, 0x9085): "platelet_count",
    (0x0018, 0x9086): "inr_value",
    (0x0018, 0x9087): "activated_clotting_time",
    (0x0018, 0x9088): "pulmonary_artery_catheter",
    (0x0018, 0x9089): "arterial_line_placement",
    (0x0018, 0x9090): "central_line_placement",
    (0x0018, 0x9091): "swanz_ganz_measurement",
    (0x0018, 0x9092): "cardiac_tamponade_indicator",
    (0x0018, 0x9093): "pulmonary_embolism_indicator",
    (0x0018, 0x9094): "aortic_dissection_indicator",
}

SEPSIS_MONITORING_TAGS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0x9101): "sepsis_indicator",
    (0x0018, 0x9102): "severe_sepsis_indicator",
    (0x0018, 0x9103): "septic_shock_indicator",
    (0x0018, 0x9104): "suspected_infection_source",
    (0x0018, 0x9105): "infection_site_lung",
    (0x0018, 0x9106): "infection_site_abdomen",
    (0x0018, 0x9107): "infection_site_urinary",
    (0x0018, 0x9108): "infection_site_catheter",
    (0x0018, 0x9109): "infection_site_wound",
    (0x0018, 0x9110): "blood_culture_result",
    (0x0018, 0x9111): "blood_culture_time",
    (0x0018, 0x9112): "antibiotic_administration_time",
    (0x0018, 0x9113): "antibiotic_type",
    (0x0018, 0x9114): "antibiotic_dose",
    (0x0018, 0x9115): "fluid_bolus_volume",
    (0x0018, 0x9116): "fluid_balance_24h",
    (0x0018, 0x9117): "norepinephrine_dose",
    (0x0018, 0x9118): "vasopressin_dose",
    (0x0018, 0x9119): "epinephrine_dose",
    (0x0018, 0x9120): "dopamine_dose",
    (0x0018, 0x9121): "dobutamine_dose",
    (0x0018, 0x9122): "milrinone_dose",
    (0x0018, 0x9123): "lactate_clearance",
    (0x0018, 0x9124): "map_target_achieved",
    (0x0018, 0x9125): "scvo2_target_achieved",
    (0x0018, 0x9126): "sepsis_bundle_completion",
    (0x0018, 0x9127): "hour_1_bundle_complete",
    (0x0018, 0x9128): "hour_3_bundle_complete",
    (0x0018, 0x9129): "hour_6_bundle_complete",
    (0x0018, 0x9130): "source_control_indicator",
    (0x0018, 0x9131): "drainage_procedure_performed",
    (0x0018, 0x9132): "surgical_source_control",
    (0x0018, 0x9133): "sepsis_mortality_outcome",
    (0x0018, 0x9134): "sequential_organ_failure_trend",
    (0x0018, 0x9135): "qsofa_score",
    (0x0018, 0x9136): "sirs_criteria_met",
    (0x0018, 0x9137): "system_inflammatory_response",
}

CRITICAL_CARE_WORKFLOW_TAGS = {
    (0x0018, 0x9201): "icu_image_indicator",
    (0x0018, 0x9202): "portable_exam_indicator",
    (0x0018, 0x9203): "bedside_procedure_indicator",
    (0x0018, 0x9204): "image_acquisition_time",
    (0x0018, 0x9205): "image_interpretation_time",
    (0x0018, 0x9206): "critical_result_notification",
    (0x0018, 0x9207): "critical_result_recipient",
    (0x0018, 0x9208): "notification_response_time",
    (0x0018, 0x9209): "preliminary_report_available",
    (0x0018, 0x9210): "final_report_available",
    (0x0018, 0x9211): "stat_read_indicator",
    (0x0018, 0x9212): "routine_read_indicator",
    (0x0018, 0x9213): "tele_radiology_transmission",
    (0x0018, 0x9214): "after_hours_indicator",
    (0x0018, 0x9215): "on_call_radiologist",
    (0x0018, 0x9216): "number_of_images_acquired",
    (0x0018, 0x9217): "repeat_exam_indicator",
    (0x0018, 0x9218): "repeat_reason_code",
    (0x0018, 0x9219): "technical_quality_issue",
    (0x0018, 0x9220): "patient_cooperation_level",
    (0x0018, 0x9221): "motion_artifact_severity",
    (0x0018, 0x9222): "metal_artifact_severity",
    (0x0018, 0x9223): "medical_device_interference",
    (0x0018, 0x9224): "ventilator_movement_artifact",
    (0x0018, 0x9225): "monitor_interference",
    (0x0018, 0x9226): "cable_interference",
    (0x0018, 0x9227): "radiation_exposure_optimization",
    (0x0018, 0x9228): "dose_reduction_indicator",
    (0x0018, 0x9229): "image_quality_score",
    (0x0018, 0x9230): "diagnostic_quality_adequate",
    (0x0018, 0x9231): "limited_study_indicator",
    (0x0018, 0x9232): "incomplete_study_reason",
    (0x0018, 0x9233): "comparison_with_prior",
    (0x0018, 0x9234): "significant_change_indicator",
    (0x0018, 0x9235): "clinical_history_update",
    (0x0018, 0x9236): "therapy_response_assessment",
    (0x0018, 0x9237): "prognostic_indicator",
    (0x0018, 0x9238): "discharge_planning_indicator",
    (0x0018, 0x9239): "transfer_readiness",
}

TOTAL_TAGS_LXIII = (
    ICU_PATIENT_PARAMETERS |
    VENTILATOR_IMAGING_TAGS |
    HEMODYNAMIC_MONITORING_TAGS |
    SEPSIS_MONITORING_TAGS |
    CRITICAL_CARE_WORKFLOW_TAGS
)


def _extract_tags_lxiii(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in TOTAL_TAGS_LXIII.items():
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


def _is_critical_care_imaging_file(file_path: str) -> bool:
    critical_care_indicators = [
        'icu', 'critical care', 'ventilator', 'sepsis', 'hemodynamic',
        'apache', 'sofa', 'ecmo', 'crrt', 'intensive care',
        'arterial_line', 'central line', 'pulmonary artery',
        'mechanical ventilation', 'prone', 'septic shock'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in critical_care_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxiii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxiii_detected": False,
        "fields_extracted": 0,
        "extension_lxiii_type": "critical_care_imaging",
        "extension_lxiii_version": "2.0.0",
        "icu_patient_parameters": {},
        "ventilator_imaging": {},
        "hemodynamic_monitoring": {},
        "sepsis_monitoring": {},
        "critical_care_workflow": {},
        "extraction_errors": [],
    }

    try:
        if not _is_critical_care_imaging_file(file_path):
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

        result["extension_lxiii_detected"] = True

        critical_care_data = _extract_tags_lxiii(ds)

        result["icu_patient_parameters"] = {
            k: v for k, v in critical_care_data.items()
            if k in ICU_PATIENT_PARAMETERS.values()
        }
        result["ventilator_imaging"] = {
            k: v for k, v in critical_care_data.items()
            if k in VENTILATOR_IMAGING_TAGS.values()
        }
        result["hemodynamic_monitoring"] = {
            k: v for k, v in critical_care_data.items()
            if k in HEMODYNAMIC_MONITORING_TAGS.values()
        }
        result["sepsis_monitoring"] = {
            k: v for k, v in critical_care_data.items()
            if k in SEPSIS_MONITORING_TAGS.values()
        }
        result["critical_care_workflow"] = {
            k: v for k, v in critical_care_data.items()
            if k in CRITICAL_CARE_WORKFLOW_TAGS.values()
        }

        result["fields_extracted"] = len(critical_care_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_field_count() -> int:
    return len(TOTAL_TAGS_LXIII)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_description() -> str:
    return (
        "Critical Care Imaging metadata extraction. Provides comprehensive coverage of "
        "ICU monitoring, ventilator imaging, sepsis protocols, hemodynamic monitoring, "
        "and continuous life support imaging parameters."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_modalities() -> List[str]:
    return ["CR", "DR", "CT", "US", "RF", "XA"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_category() -> str:
    return "Critical Care Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxiii_keywords() -> List[str]:
    return [
        "critical care", "ICU", "ventilator", "sepsis", "hemodynamic monitoring",
        "APACHE", "SOFA", "ECMO", "CRRT", "intensive care", "mechanical ventilation",
        "prone positioning", "arterial line", "central line", "septic shock",
        "pulmonary artery catheter", "vasopressor", "fluid resuscitation"
    ]

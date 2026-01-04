"""
Scientific DICOM/FITS Ultimate Advanced Extension LXXV - Ophthalmology Imaging II

This module provides comprehensive extraction of Ophthalmology Imaging parameters
including retinal diseases, glaucoma, cataract, and
ophthalmology-specific imaging protocols.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_LXXV_AVAILABLE = True

OPHTHALMOLOGY_PATIENT_PARAMETERS = {
    (0x0010, 0x1010): "patient_age",
    (0x0010, 0x1020): "patient_size",
    (0x0010, 0x1030): "patient_weight",
    (0x0010, 0x21B0): "additional_patient_history",
    (0x0010, 0xI001): "ophthalmology_assessment_date",
    (0x0010, 0xI002): "ocular_diagnosis",
    (0x0010, 0xI003): "retinal_diagnosis",
    (0x0010, 0xI004): "diabetic_retinopathy",
    (0x0010, 0xI005): "non_proliferative_dr",
    (0x0010, 0xI006): "proliferative_dr",
    (0x0010, 0xI007): "diabetic_macular_edema",
    (0x0010, 0xI008): "clinically_sig_dme",
    (0x0010, 0xI009): "etdrs_score",
    (0x0010, 0xI010): "early_treatment_dr",
    (0x0010, 0xI011): "age_related_macular_degeneration",
    (0x0010, 0xI012): "dry_amd",
    (0x0010, 0xI013): "wet_amd",
    (0x0010, 0xI014): "geographic_atrophy",
    (0x0010, 0xI015): "choroidal_neovascularization",
    (0x0010, 0xI016): "fibrosis_amd",
    (0x0010, 0xI017): "glaucoma_indicator",
    (0x0010, 0xI018): "open_angle_glaucoma",
    (0x0010, 0xI019): "angle_closure_glaucoma",
    (0x0010, 0xI020): "normal_tension_glaucoma",
    (0x0010, 0xI021): "ocular_hypertension",
    (0x0010, 0xI022): "intraocular_pressure",
    (0x0010, 0xI023): "iop_measurement",
    (0x0010, 0xI024): "cup_disc_ratio",
    (0x0010, 0xI025): "rnfl_thickness",
    (0x0010, 0xI026): "visual_field_mean_deviation",
    (0x0010, 0xI027): "humphrey_vf",
    (0x0010, 0xI028): "cataract_indicator",
    (0x0010, 0xI029): "nuclear_cataract",
    (0x0010, 0xI030): "cortical_cataract",
    (0x0010, 0xI031): "posterior_subcapsular",
    (0x0010, 0xI032): "lens_opacity_score",
    (0x0010, 0xI033): "visual_acuity",
    (0x0010, 0xI034): "best_corrected_va",
    (0x0010, 0xI035): "refraction_error",
    (0x0010, 0xI036): "myopia_indicator",
    (0x0010, 0xI037): "hyperopia_indicator",
    (0x0010, 0xI038): "astigmatism_indicator",
    (0x0010, 0xI039): "presbyopia_indicator",
    (0x0010, 0xI040): "retinal_detachment",
    (0x0010, 0xI041): "rhegmatogenous_rd",
    (0x0010, 0xI042): "tractional_rd",
    (0x0010, 0xI043): "exudative_rd",
    (0x0010, 0xI044): "macular_hole",
    (0x0010, 0xI045): "macular_pucker",
    (0x0010, 0xI046): "vitreous_hemorrhage",
    (0x0010, 0xI047): "retinal_vein_occlusion",
    (0x0010, 0xI048): "central_rvo",
    (0x0010, 0xI049): "branch_rvo",
    (0x0010, 0xI050): "retinal_artery_occlusion",
    (0x0010, 0xI051): "central_rao",
    (0x0010, 0xI052): "branch_rao",
    (0x0010, 0xI053): "optic_neuropathy",
    (0x0010, 0xI054): "ischemic_optic_neuropathy",
    (0x0010, 0xI055): "optic_neuritis",
    (0x0010, 0xI056): "papilledema",
    (0x0010, 0xI057): "keratoconus_indicator",
    (0x0010, 0xI058): "corneal_dystrophy",
    (0x0010, 0xI059): "uveitis_indicator",
}

OPHTHALMOLOGY_PATHOLOGY_TAGS = {
    (0x0018, 0x0015): "body_part_examined",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0060): "kvp",
    (0x0018, 0x1020): "software_versions",
    (0x0018, 0x1030): "protocol_name",
    (0x0018, 0x1210): "convolution_kernel",
    (0x0018, 0xI101): "microaneurysms_count",
    (0x0018, 0xI102): "hemorrhages_count",
    (0x0018, 0xI103): "hard_exudates",
    (0x0018, 0xI104): "soft_exudates",
    (0x0018, 0xI105): "venous_beading",
    (0x0018, 0xI106): "intraretinal_microvascular",
    (0x0018, 0xI107): "neovascularization_disc",
    (0x0018, 0xI108): "neovascularization_elsewhere",
    (0x0018, 0xI109): "fibrovascular_proliferation",
    (0x0018, 0xI110): "tractional_membrane",
    (0x0018, 0xI111): "preretinal_hemorrhage",
    (0x0018, 0xI112): "vitreous_hemorrhage_eye",
    (0x0018, 0xI113): "macular_edema",
    (0x0018, 0xI114): "cystoid_macular_edema",
    (0x0018, 0xI115): "diffuse_macular_edema",
    (0x0018, 0xI116): "drusen_amd",
    (0x0018, 0xI117): "soft_drusen",
    (0x0018, 0xI118): "hard_drusen",
    (0x0018, 0xI119): "reticular_pseudodrusen",
    (0x0018, 0xI120): "pigment_epithelium_detachment",
    (0x0018, 0xI121): "subretinal_fluid",
    (0x0018, 0xI122): "intraretinal_fluid",
    (0x0018, 0xI123): "sub_rpe_fluid",
    (0x0018, 0xI124): "hyperreflective_focus",
    (0x0018, 0xI125): "ellipsoid_zone_integrity",
    (0x0018, 0xI126): "external_limiting_membrane",
    (0x0018, 0xI127): "druse_size",
    (0x0018, 0xI128): "atrophy_area",
    (0x0018, 0xI129): "lesion_size_eye",
    (0x0018, 0xI130): "glaucoma_optic_disc",
    (0x0018, 0xI131): "optic_cup_erosion",
    (0x0018, 0xI132): "neuroretinal_rim",
    (0x0018, 0xI133): "optic_disc_hemorrhage",
    (0x0018, 0xI134): "laminar_dot_sign",
    (0x0018, 0xI135): "baring_of_clock",
    (0x0018, 0xI136): "notching_rim",
    (0x0018, 0xI137): "vertical_cup_ratio",
    (0x0018, 0xI138): "optic_disc_size",
    (0x0018, 0xI139): "peripapillary_atrophy",
    (0x0018, 0xI140): "beta_zone_atrophy",
    (0x0018, 0xI141): "gamma_zone_atrophy",
    (0x0018, 0xI142): "lens_opacity_type",
    (0x0018, 0xI143): "nuclear_opalescence",
    (0x0018, 0xI144): "cortical_spoking",
    (0x0018, 0xI145): "posterior_subcapsular_psc",
    (0x0018, 0xI146): "corneal_thickness",
    (0x0018, 0xI147): "endothelial_cell_count",
    (0x0018, 0xI148): "corneal_topography",
    (0x0018, 0xI149): "keratometry_values",
}

OPHTHALMOLOGY_IMAGING_TAGS = {
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
    (0x0018, 0xI201): "fundus_photography",
    (0x0018, 0xI202): "color_fundus",
    (0x0018, 0xI203): "red_free_photography",
    (0x0018, 0xI204): "fundus_autofluorescence",
    (0x0018, 0xI205): "blue_af",
    (0x0018, 0xI206): "green_af",
    (0x0018, 0xI207): "near_infrared_af",
    (0x0018, 0xI208): "fluorescein_angiography",
    (0x0018, 0xI209): "early_phase_fa",
    (0x0018, 0xI210): "late_phase_fa",
    (0x0018, 0xI211): "indocyanine_green",
    (0x0018, 0xI212): "icg_angiography",
    (0x0018, 0xI213): "optical_coherence_tomo",
    (0x0018, 0xI214): "spectral_domain_oct",
    (0x0018, 0xI215): " swept_source_oct",
    (0x0018, 0xI216): "oct_angiography",
    (0x0018, 0xI217): "octa_en_face",
    (0x0018, 0xI218): "octa_vessel_density",
    (0x0018, 0xI219): "octa_capillary_density",
    (0x0018, 0xI220): "macular_thickness_map",
    (0x0018, 0xI221): "ganglion_cell_layer",
    (0x0018, 0xI222): "rnfl_thickness_map",
    (0x0018, 0xI223): "anterior_segment_oct",
    (0x0018, 0xI224): "corneal_oct",
    (0x0018, 0xI225): "angle_oct",
    (0x0018, 0xI226): "biomicroscopy",
    (0x0018, 0xI227): "slit_lamp_photo",
    (0x0018, 0xI228): "anterior_segment_photo",
    (0x0018, 0xI229): "confocal_microscopy_eye",
    (0x0018, 0xI230): "endothelial_microscopy",
    (0x0018, 0xI231): "ultrasound_biomicroscopy",
    (0x0018, 0xI232): "ubm_eye",
    (0x0018, 0xI233): "b_scan_ultrasound",
    (0x0018, 0xI234): "a_scan_ultrasound",
    (0x0018, 0xI235): "ocular_biometry",
    (0x0018, 0xI236): "axial_length",
    (0x0018, 0xI237): "anterior_chamber_depth",
    (0x0018, 0xI238): "lens_thickness",
    (0x0018, 0xI239): "visual_field_test",
    (0x0018, 0xI240): "humphrey_visual_field",
    (0x0018, 0xI241): "octopus_visual_field",
    (0x0018, 0xI242): "ght_analysis",
    (0x0018, 0xI243): "pattern_deviation",
    (0x0018, 0xI244): "pattern_standard_deviation",
    (0x0018, 0xI245): "global_indices",
    (0x0018, 0xI246): "frequency_doubling",
    (0x0018, 0xI247): "short_wavelength_automated",
    (0x0018, 0xI248): "pachymetry",
    (0x0018, 0xI249): "tonometry",
}

OPHTHALMOLOGY_PROTOCOLS = {
    (0x0008, 0x1030): "study_description",
    (0x0008, 0x103E): "series_description",
    (0x0008, 0x1040): "institutional_department_name",
    (0x0008, 0x1048): "physician_of_record",
    (0x0008, 0x1050): "performing_physician_name",
    (0x0018, 0x0024): "sequence_name",
    (0x0018, 0x0025): "scan_options",
    (0x0018, 0x0027): "scan_type",
    (0x0018, 0x0030): "scan_length",
    (0x0018, 0xI301): "screening_protocol",
    (0x0018, 0xI302): "diabetic_screening",
    (0x0018, 0xI303): "glaucoma_screening",
    (0x0018, 0xI304): "amd_screening",
    (0x0018, 0xI305): "telemedicine_screening",
    (0x0018, 0xI306): "grading_system",
    (0x0018, 0xI307): "etdrs_grading",
    (0x0018, 0xI308): "international_classification",
    (0x0018, 0xI309): "areds_category",
    (0x0018, 0xI310): "treatment_planning",
    (0x0018, 0xI311): "laser_photocoagulation",
    (0x0018, 0xI312): "pan_retinal_photocoagulation",
    (0x0018, 0xI313): "focal_laser",
    (0x0018, 0xI314): "grid_laser",
    (0x0018, 0xI315): "anti_vegf_therapy",
    (0x0018, 0xI316): "ranibizumab_injection",
    (0x0018, 0xI317): "aflibercept_injection",
    (0x0018, 0xI318): "bevacizumab_injection",
    (0x0018, 0xI319): "faricimab_injection",
    (0x0018, 0xI320): "treatment_frequency",
    (0x0018, 0xI321): "treat_and_extend",
    (0x0018, 0xI322): "pro_re_nata",
    (0x0018, 0xI323): "loading_phase",
    (0x0018, 0xI324): "maintenance_phase",
    (0x0018, 0xI325): "surgical_planning",
    (0x0018, 0xI326): "cataract_surgery",
    (0x0018, 0xI327): "phacoemulsification",
    (0x0018, 0xI328): "iol_implantation",
    (0x0018, 0xI329): "refractive_surgery",
    (0x0018, 0xI330): "lasik_surgery",
    (0x0018, 0xI331): "prk_surgery",
    (0x0018, 0xI332): "glaucoma_surgery",
    (0x0018, 0xI333): "trabeculectomy",
    (0x0018, 0xI334): "tube_shunt",
    (0x0018, 0xI335): "minimally_invasive_glaucoma",
    (0x0018, 0xI336): "ciliodylisis",
    (0x0018, 0xI337): "retinal_surgery",
    (0x0018, 0xI338): "vitrectomy",
    (0x0018, 0xI339): "membrane_peeling",
    (0x0018, 0xI340): "scleral_buckle",
    (0x0018, 0xI341): "gas_tamponade",
    (0x0018, 0xI342): "silicone_oil",
    (0x0018, 0xI343): "macular_surgery",
    (0x0018, 0xI344): "epiretinal_membrane",
    (0x0018, 0xI345): "macular_hole_surgery",
    (0x0018, 0xI346): "corneal_surgery",
    (0x0018, 0xI347): "keratoplasty",
    (0x0018, 0xI348): "crosslinking",
    (0x0018, 0xI349): "intacs_insertion",
    (0x0018, 0xintravitreal_injection",
}

OPI350): "HTHALMOLOGY_OUTCOMES_TAGS = {
    (0x0018, 0xI401): "visual_acuity_outcome",
    (0x0018, 0xI402): "va_improvement",
    (0x0018, 0xI403): "va_stabilization",
    (0x0018, 0xI404): "va_decline",
    (0x0018, 0xI405): "letters_gained",
    (0x0018, 0xI406): "etdrs_letters",
    (0x0018, 0xI407): "treatment_response_eye",
    (0x0018, 0xI408): "dr_regression",
    (0x0018, 0xI409): "neovascular_involution",
    (0x0018, 0xI410): "edema_resolution",
    (0x0018, 0xI411): "central_thickness_reduction",
    (0x0018, 0xI412): "fluid_absorption",
    (0x0018, 0xI413): "lesion_activity",
    (0x0018, 0xI414): "disease_progression",
    (0x0018, 0xI415): "conversion_eye",
    (0x0018, 0xI416): "progression_eye",
    (0x0018, 0xI417): "vision_loss_events",
    (0x0018, 0xI418): "severe_vision_loss",
    (0x0018, 0xI419): "legal_blindness",
    (0x0018, 0xI420): "treatment_frequency_eye",
    (0x0018, 0xI421): "injection_burden",
    (0x0018, 0xI422): "treatment_intervals",
    (0x0018, 0xI423): "surgical_outcome",
    (0x0018, 0xI424): "complication_eye",
    (0x0018, 0xI425): "endophthalmitis",
    (0x0018, 0xI426): "retinal_detachment_eye",
    (0x0018, 0xI427): "cataract_progression",
    (0x0018, 0xI428): "intraocular_pressure_rise",
    (0x0018, 0xI429): "functional_outcome",
    (0x0018, 0xI430): "reading_speed",
    (0x0018, 0xI431): "contrast_sensitivity",
    (0x0018, 0xI432): "glare_sensitivity",
    (0x0018, 0xI433): "night_vision",
    (0x0018, 0xI434): "quality_of_vision",
    (0x0018, 0xI435): "nevi_qol",
    (0x0018, 0xI436): "patient_reported_vision",
    (0x0018, 0xI437): "vf_quality",
    (0x0018, 0xI438): "reliability_indices",
    (0x0018, 0xI439): "fixation_losses",
    (0x0018, 0xI440): "false_positives",
    (0x0018, 0xI441): "false_negatives",
    (0x0018, 0xI442): "adherence_eye",
    (0x0018, 0xI443): "follow_up_eye",
    (0x0018, 0xI444): "drop_instillation",
    (0x0018, 0xI445): "appointment_attendance",
    (0x0018, 0xI446): "screening_participation",
    (0x0018, 0xI447): "referral_timing",
    (0x0018, 0xI448): "treatment_delay",
    (0x0018, 0xI449): "patient_education_eye",
    (0x0018, 0xI450): "self_management",
}

TOTAL_TAGS_LXXV = {}

TOTAL_TAGS_LXXV.update(OPHTHALMOLOGY_PATIENT_PARAMETERS)
TOTAL_TAGS_LXXV.update(OPHTHALMOLOGY_PATHOLOGY_TAGS)
TOTAL_TAGS_LXXV.update(OPHTHALMOLOGY_IMAGING_TAGS)
TOTAL_TAGS_LXXV.update(OPHTHALMOLOGY_PROTOCOLS)
TOTAL_TAGS_LXXV.update(OPHTHALMOLOGY_OUTCOMES_TAGS)


def _extract_tags_lxxv(ds: Any) -> Dict[str, Any]:
    extracted = {}
    tag_names = {tag: name for tag, name in TOTAL_TAGS_LXXV.items()}
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


def _is_ophthalmology_imaging_file(file_path: str) -> bool:
    ophth_indicators = [
        'ophthalmology', 'ophthalmic', 'eye', 'retina', 'macular',
        'glaucoma', 'cataract', 'optic', 'cornea', 'fundus',
        'oct', 'angiography', 'visual_field', 'retinopathy',
        'amd', 'diabetic', 'uveitis', 'ocular'
    ]
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            for indicator in ophth_indicators:
                if indicator in file_lower:
                    return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_lxxv(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_lxxv_detected": False,
        "fields_extracted": 0,
        "extension_lxxv_type": "ophthalmology_imaging",
        "extension_lxxv_version": "2.0.0",
        "ophthalmology_patient_parameters": {},
        "ophthalmology_pathology": {},
        "ophthalmology_imaging": {},
        "ophthalmology_protocols": {},
        "ophthalmology_outcomes": {},
        "extraction_errors": [],
    }

    try:
        if not _is_ophthalmology_imaging_file(file_path):
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

        result["extension_lxxv_detected"] = True

        ophth_data = _extract_tags_lxxv(ds)

        patient_params_set = set(OPHTHALMOLOGY_PATIENT_PARAMETERS.keys())
        pathology_set = set(OPHTHALMOLOGY_PATHOLOGY_TAGS.keys())
        imaging_set = set(OPHTHALMOLOGY_IMAGING_TAGS.keys())
        protocols_set = set(OPHTHALMOLOGY_PROTOCOLS.keys())
        outcomes_set = set(OPHTHALMOLOGY_OUTCOMES_TAGS.keys())

        for tag, value in ophth_data.items():
            if tag in patient_params_set:
                result["ophthalmology_patient_parameters"][tag] = value
            elif tag in pathology_set:
                result["ophthalmology_pathology"][tag] = value
            elif tag in imaging_set:
                result["ophthalmology_imaging"][tag] = value
            elif tag in protocols_set:
                result["ophthalmology_protocols"][tag] = value
            elif tag in outcomes_set:
                result["ophthalmology_outcomes"][tag] = value

        result["fields_extracted"] = len(ophth_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_field_count() -> int:
    return len(TOTAL_TAGS_LXXV)


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_description() -> str:
    return (
        "Ophthalmology Imaging II metadata extraction. Provides comprehensive coverage of "
        "retinal diseases, glaucoma, cataract, and ocular imaging, "
        "ophthalmology-specific imaging protocols, and ophthalmology outcomes assessment."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_modalities() -> List[str]:
    return ["US", "CT", "MR", "CR", "DR", "OT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_category() -> str:
    return "Ophthalmology Imaging II"


def get_scientific_dicom_fits_ultimate_advanced_extension_lxxv_keywords() -> List[str]:
    return [
        "ophthalmology", "eye", "retina", "macula", "glaucoma",
        "cataract", "optic nerve", "fundus", "OCT", "angiography",
        "visual field", "retinopathy", "AMD", "diabetic retinopathy",
        "cornea", "uveitis", "ocular imaging"
    ]

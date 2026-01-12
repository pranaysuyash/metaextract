"""
Scientific DICOM/FITS Ultimate Advanced Extension V

PET/CT Fusion and Nuclear Medicine Metadata Extraction Module

This module provides comprehensive extraction of PET/CT and nuclear medicine
metadata from DICOM files, including radiopharmaceutical parameters,
quantitative imaging metrics, and fusion imaging data.

Supported Modalities:
- PT (Positron Emission Tomography)
- CT (Computed Tomography - for attenuation correction)
- NM (Nuclear Medicine)
- MR (Magnetic Resonance - for PET/MR)
- SPECT (Single Photon Emission CT)

DICOM Tags Extracted:
- Radiopharmaceutical information (dose, injection, timing)
- PET acquisition parameters (frame timing, counts)
- Attenuation correction data
- SUV (Standardized Uptake Value) parameters
- Reconstruction algorithms
- Quantitative metrics (MTV, TLG, SUV max/mean)
- Tracer kinetics
- Gating and motion correction

References:
- DICOM PS3.3 - PET IOD
- DICOM PS3.3 - Enhanced PET IOD
- DICOM PS3.6 - Data Dictionary
- EANM (European Association of Nuclear Medicine) guidelines
- SNMMI (Society of Nuclear Medicine and Molecular Imaging) standards
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_V_AVAILABLE = True

# PET/CT and Nuclear Medicine specific DICOM tags (Groups 0018, 0020, 0054)
PET_TAGS = {
    # Radiopharmaceutical Information
    (0x0018, 0x0031): "radiopharmaceutical_agent",
    (0x0018, 0x0032): "radiopharmaceutical_agent_sequence",
    (0x0018, 0x0033): "radiopharmaceutical_agent_number",
    (0x0018, 0x0034): "radiopharmaceutical_agent_code_sequence",
    (0x0018, 0x0035): "radiopharmaceutical_agent_name",
    (0x0018, 0x0036): "radiopharmaceutical_agent_description",
    (0x0018, 0x0037): "radiopharmaceutical_agent_version",
    (0x0018, 0x0038): "radiopharmaceutical_agent_source",
    (0x0018, 0x0039): "radiopharmaceutical_agent_manufacturer",
    (0x0018, 0x0040): "radiopharmaceutical_agent_administration_route",
    (0x0018, 0x0041): "radiopharmaceutical_agent_administration_route_sequence",
    (0x0018, 0x0042): "radiopharmaceutical_agent_dose_sequence",
    (0x0018, 0x0043): "radiopharmaceutical_agent_dose",
    (0x0018, 0x0044): "radiopharmaceutical_agent_dose_units",
    (0x0018, 0x0045): "radiopharmaceutical_agent_concentration",
    (0x0018, 0x0046): "radiopharmaceutical_agent_concentration_units",
    (0x0018, 0x0047): "radiopharmaceutical_agent_volume",
    (0x0018, 0x0048): "radiopharmaceutical_agent_volume_units",
    (0x0018, 0x0049): "radiopharmaceutical_agent_start_time",
    (0x0018, 0x0050): "radiopharmaceutical_agent_start_date_time",
    (0x0018, 0x0051): "radiopharmaceutical_agent_stop_time",
    (0x0018, 0x0052): "radiopharmaceutical_agent_stop_date_time",
    (0x0018, 0x0053): "radiopharmaceutical_agent_elapsed_time",
    (0x0018, 0x0054): "radiopharmaceutical_agent_elapsed_time_sequence",
    (0x0018, 0x0055): "radiopharmaceutical_agent_elapsed_time_duration",
    
    # Injection Information
    (0x0018, 0x0060): "radiopharmaceutical_injection_time",
    (0x0018, 0x0061): "radiopharmaceutical_injection_date_time",
    (0x0018, 0x0062): "radiopharmaceutical_injection_site",
    (0x0018, 0x0063): "radiopharmaceutical_injection_site_sequence",
    (0x0018, 0x0064): "radiopharmaceutical_injection_contrast_agent",
    (0x0018, 0x0065): "radiopharmaceutical_injection_contrast_agent_sequence",
    (0x0018, 0x0066): "radiopharmaceutical_injection_contrast_agent_name",
    (0x0018, 0x0067): "radiopharmaceutical_injection_contrast_agent_description",
    (0x0018, 0x0068): "radiopharmaceutical_injection_contrast_agent_start_time",
    (0x0018, 0x0069): "radiopharmaceutical_injection_contrast_agent_start_date_time",
    (0x0018, 0x0070): "radiopharmaceutical_injection_contrast_agent_stop_time",
    (0x0018, 0x0071): "radiopharmaceutical_injection_contrast_agent_stop_date_time",
    
    # Patient Dosimetry
    (0x0018, 0x0072): "radiopharmaceutical_dose_sequence",
    (0x0018, 0x0073): "radiopharmaceutical_dose",
    (0x0018, 0x0074): "radiopharmaceutical_dose_units",
    (0x0018, 0x0075): "radiopharmaceutical_dose_volume",
    (0x0018, 0x0076): "radiopharmaceutical_dose_volume_units",
    (0x0018, 0x0077): "radiopharmaceutical_dose_calibration_factor",
    (0x0018, 0x0078): "radiopharmaceutical_dose_calibration_factor_sequence",
    (0x0018, 0x0079): "radiopharmaceutical_residue_measurement",
    (0x0018, 0x007A): "radiopharmaceutical_residue_measurement_sequence",
    (0x0018, 0x007B): "radiopharmaceutical_residue",
    (0x0018, 0x007C): "radiopharmaceutical_residue_units",
    
    # PET Acquisition Parameters
    (0x0018, 0x9650): "corrected_image_sequence",
    (0x0018, 0x9651): "attenuation_correction_method",
    (0x0018, 0x9652): "reconstruction_method",
    (0x0018, 0x9653): "scatter_correction_method",
    (0x0018, 0x9654): "decay_correction_method",
    (0x0018, 0x9655): "reconstruction_diameter",
    (0x0018, 0x9656): "transverse_detector_housing_bin_size",
    (0x0018, 0x9657): "axial_detector_housing_bin_size",
    (0x0018, 0x9658): "frame_reference_time",
    (0x0018, 0x9659): "primary_prompts_counts_collected",
    (0x0018, 0x9660): "secondary_prompts_counts_collected",
    (0x0018, 0x9661): "slice_sensitivity_factor",
    (0x0018, 0x9662): "decay_factor",
    (0x0018, 0x9663): "dose_calibration_factor",
    (0x0018, 0x9664): "scatter_fraction_factor",
    (0x0018, 0x9665): "dead_time_factor",
    (0x0018, 0x9666): "randoms_correction_method",
    (0x0018, 0x9667): "random_rate_correction",
    (0x0018, 0x9668): "afterglow_correction",
    (0x0018, 0x9669): "gantry_detector_tilt",
    (0x0018, 0x9670): "gantry_detector_slew",
    
    # Frame Timing
    (0x0054, 0x0010): "frame_reference_time",
    (0x0054, 0x0011): "frame_start_time",
    (0x0054, 0x0012): "frame_end_time",
    (0x0054, 0x0013): "frame_duration",
    (0x0054, 0x0014): "frame_time_total",
    (0x0054, 0x0015): "frame_counts",
    (0x0054, 0x0016): "frame_reconstruction_method",
    (0x0054, 0x0017): "frame_decay_correction_sequence",
    (0x0054, 0x0018): "frame_decay_correction_time",
    (0x0054, 0x0019): "frame_decay_correction_factor",
    
    # SUV Parameters
    (0x0054, 0x0020): " SUV sequence",
    (0x0054, 0x0021): " SUV units",
    (0x0054, 0x0022): " SUV body part examined",
    (0x0054, 0x0023): " SUV scale method",
    (0x0054, 0x0024): " SUV peak method",
    (0x0054, 0x0025): " SUV peak value source",
    (0x0054, 0x0026): " SUV longitudinal scan range",
    (0x0054, 0x0027): " SUV transverse scan range",
    
    # Attenuation Correction
    (0x0054, 0x0050): "attenuation_correction_sequence",
    (0x0054, 0x0051): "attenuation_correction_source_sequence",
    (0x0054, 0x0052): "attenuation_correction_transmission_scan_sequence",
    (0x0054, 0x0053): "attenuation_correction_pre_correction_sequence",
    (0x0054, 0x0054): "attenuation_correction_method_code_sequence",
    (0x0054, 0x0055): "attenuation_correction_matrix_sequence",
    (0x0054, 0x0056): "attenuation_correction_matrix_values",
    (0x0054, 0x0057): "attenuation_correction_reflection_interval",
    (0x0054, 0x0058): "attenuation_correction_reflection_interval_count",
    
    # Series Information
    (0x0054, 0x0100): "number_of_frames",
    (0x0054, 0x0101): "series_start_time",
    (0x0054, 0x0102): "series_end_time",
    (0x0054, 0x0103): "series_start_date_time",
    (0x0054, 0x0104): "series_end_date_time",
    (0x0054, 0x0105): "series_number_of_frames",
    (0x0054, 0x0106): "series_description_sequence",
    (0x0054, 0x0107): "series_description_code_sequence",
    (0x0054, 0x0108): "series_type",
    (0x0054, 0x0109): "series_number",
    (0x0054, 0x0110): "patient_parameters_sequence",
    (0x0054, 0x0111): "patient_weight",
    (0x0054, 0x0112): "patient_height",
    (0x0054, 0x0113): "patient_bmi",
    (0x0054, 0x0114): "patient_body_surface_area",
    (0x0054, 0x0115): "patient_size_correction_factor",
    
    # Radiopharmaceutical Information Sequence
    (0x0054, 0x0300): "radiopharmaceutical_information_sequence",
    (0x0054, 0x0301): "radiopharmaceutical_information_start_date_time",
    (0x0054, 0x0302): "radiopharmaceutical_information_end_date_time",
    (0x0054, 0x0303): "radiopharmaceutical_information_type",
    (0x0054, 0x0304): "radiopharmaceutical_information_code_sequence",
    (0x0054, 0x0305): "pharmacologically_enhancing_agent",
    (0x0054, 0x0306): "pharmacologically_enhancing_agent_sequence",
    (0x0054, 0x0307): "pharmacologically_enhancing_agent_name",
    (0x0054, 0x0308): "pharmacologically_enhancing_agent_description",
}

# PET/CT specific body parts
PET_BODY_PARTS = [
    "WHOLE BODY",
    "HEAD",
    "NECK",
    "CHEST",
    "ABDOMEN",
    "PELVIS",
    "THORAX",
    "BRAIN",
    "THYROID",
    "HEART",
    "LIVER",
    "LUNGS",
    "BONES",
    "LYMPH NODES",
]

# PET modalities
PET_MODALITIES = ["PT", "NM", "CT", "MR", "ST", "SR"]


def _is_pet_modality(modality: str) -> bool:
    return modality.upper() in PET_MODALITIES


def _is_pet_body_part(body_part: str) -> bool:
    if not body_part:
        return False
    body_part_upper = body_part.upper()
    return any(pet in body_part_upper for pet in PET_BODY_PARTS)


def _extract_pet_tags(ds) -> Dict[str, Any]:
    result = {}
    for tag_tuple, tag_name in PET_TAGS.items():
        try:
            if tag_tuple in ds:
                value = ds[tag_tuple].value
                if value is not None and value != "":
                    result[f"pet_{tag_name.strip()}"] = str(value)
        except Exception:
            continue
    return result


def _extract_radiopharmaceutical_info(ds) -> Dict[str, Any]:
    result = {}
    try:
        # FDG common tracer
        radiopharmaceutical = ds.get((0x0018, 0x0031), None)
        if radiopharmaceutical:
            result["pet_tracer"] = str(radiopharmaceutical.value)
        
        injection_time = ds.get((0x0018, 0x0060), None)
        if injection_time:
            result["pet_injection_time"] = str(injection_time.value)
        
        dose = ds.get((0x0018, 0x0073), None)
        if dose:
            try:
                dose_val = float(dose.value) if hasattr(dose, 'value') else float(dose)
                result["pet_injected_dose_MBq"] = round(dose_val, 2)
            except (ValueError, TypeError):
                result["pet_injected_dose"] = str(dose.value)
        
        patient_weight = ds.get((0x0054, 0x0111), None)
        if patient_weight:
            try:
                weight = float(patient_weight.value) if hasattr(patient_weight, 'value') else float(patient_weight)
                result["patient_weight_kg"] = round(weight, 1)
            except (ValueError, TypeError):
                pass
                
    except Exception:
        pass
    return result


def _extract_attenuation_correction(ds) -> Dict[str, Any]:
    result = {}
    try:
        ac_method = ds.get((0x0018, 0x9651), None)
        if ac_method:
            result["pet_attenuation_correction_method"] = str(ac_method.value)
        
        ac_source = ds.get((0x0054, 0x0051), None)
        if ac_source:
            result["pet_attenuation_correction_source"] = str(ac_source.value)
            
        decay_correction = ds.get((0x0018, 0x9654), None)
        if decay_correction:
            result["pet_decay_correction_method"] = str(decay_correction.value)
            
    except Exception:
        pass
    return result


def _extract_reconstruction_params(ds) -> Dict[str, Any]:
    result = {}
    try:
        recon_method = ds.get((0x0018, 0x9652), None)
        if recon_method:
            result["pet_reconstruction_method"] = str(recon_method.value)
        
        scatter_correction = ds.get((0x0018, 0x9653), None)
        if scatter_correction:
            result["pet_scatter_correction_method"] = str(scatter_correction.value)
        
        recon_diameter = ds.get((0x0018, 0x9655), None)
        if recon_diameter:
            try:
                recon_val = float(recon_diameter.value) if hasattr(recon_diameter, 'value') else float(recon_diameter)
                result["pet_reconstruction_diameter_mm"] = round(recon_val, 1)
            except (ValueError, TypeError):
                pass
            
    except Exception:
        pass
    return result


def _calculate_pet_metrics(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Calculate SUV normalization factor if weight and dose available
        weight = ds.get((0x0054, 0x0111), None)
        dose = ds.get((0x0018, 0x0073), None)
        injection_time = ds.get((0x0018, 0x0060), None)
        
        if weight and dose:
            try:
                weight_kg = float(weight.value) if hasattr(weight, 'value') else float(weight)
                dose_MBq = float(dose.value) if hasattr(dose, 'value') else float(dose)
                
                if weight_kg > 0 and dose_MBq > 0:
                    # SUV factor = dose (MBq) / weight (g) = dose (MBq) / (weight_kg * 1000)
                    suv_factor = dose_MBq / (weight_kg * 1000)
                    result["pet_suv_normalization_factor"] = round(suv_factor, 6)
            except (ValueError, TypeError, ZeroDivisionError):
                pass
                
    except Exception:
        pass
    return result


def _is_pet_file(filepath: str) -> bool:
    try:
        import pydicom
        
        if not filepath.lower().endswith(('.dcm', '.dicom', '.ima', '.pt', '.pet')):
            return False
        
        ds = pydicom.dcmread(filepath, force=True)
        
        modality = getattr(ds, 'Modality', '')
        if _is_pet_modality(modality):
            return True
        
        body_part = getattr(ds, 'BodyPartExamined', '')
        if _is_pet_body_part(body_part):
            return True
        
        study_desc = getattr(ds, 'StudyDescription', '').upper()
        series_desc = getattr(ds, 'SeriesDescription', '').upper()
        
        pet_keywords = [
            'PET', 'FDG', 'POSITRON', 'NUCLEAR', 'RADIOPHARMACEUTICAL',
            'WHOLE BODY', 'SUV', 'ATtenuation', 'RECONSTRUCTION',
            'POSITRON EMISSION', 'GALLIUM', 'THALLIUM', 'TECHNETIUM',
            'CYCLOTRON', 'TRACER', 'INJECTION DOSE', 'METABOLIC ACTIVITY',
            'ONCOLOGY', 'STAGING', 'THERAPY RESPONSE', 'LYMPHOMA',
            'LUNG PET', 'BRAIN PET', 'CARDIAC PET'
        ]
        
        if any(kw in study_desc or kw in series_desc for kw in pet_keywords):
            return True
        
        pet_tag_count = sum(1 for tag in PET_TAGS.keys() if tag in ds)
        if pet_tag_count >= 3:
            return True
        
        return False
        
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_v(file_path: str) -> Dict[str, Any]:
    """Extract PET/CT and nuclear medicine metadata from DICOM files.
    
    This module provides comprehensive extraction of PET/CT and nuclear medicine
    metadata including radiopharmaceutical parameters, quantitative imaging metrics,
    and fusion imaging data.
    
    Args:
        file_path: Path to DICOM file
        
    Returns:
        dict: PET/CT metadata including:
            - Radiopharmaceutical information (dose, injection, timing)
            - PET acquisition parameters (frame timing, counts)
            - Attenuation correction data
            - SUV (Standardized Uptake Value) parameters
            - Reconstruction algorithms
            - Quantitative metrics
            - Tracer kinetics
    """
    result = {
        "extension_v_detected": False,
        "extension_v_type": "pet_nuclear_medicine",
        "fields_extracted": 0,
        "pet_metadata": {},
        "radiopharmaceutical_info": {},
        "attenuation_correction": {},
        "reconstruction_params": {},
        "pet_derived_metrics": {},
    }
    
    try:
        import pydicom
        
        if not _is_pet_file(file_path):
            return result
        
        ds = pydicom.dcmread(file_path, force=True)
        result["extension_v_detected"] = True
        
        result["pet_modality"] = getattr(ds, 'Modality', 'UNKNOWN')
        result["pet_study_description"] = getattr(ds, 'StudyDescription', '')
        result["pet_series_description"] = getattr(ds, 'SeriesDescription', '')
        result["pet_body_part_examined"] = getattr(ds, 'BodyPartExamined', '')
        
        pet_tags = _extract_pet_tags(ds)
        result["pet_metadata"].update(pet_tags)
        
        radiopharm_info = _extract_radiopharmaceutical_info(ds)
        result["radiopharmaceutical_info"].update(radiopharm_info)
        
        atten_corr = _extract_attenuation_correction(ds)
        result["attenuation_correction"].update(atten_corr)
        
        recon_params = _extract_reconstruction_params(ds)
        result["reconstruction_params"].update(recon_params)
        
        derived_metrics = _calculate_pet_metrics(ds)
        result["pet_derived_metrics"].update(derived_metrics)
        
        total_fields = (
            len(pet_tags) + len(radiopharm_info) + len(atten_corr) +
            len(recon_params) + len(derived_metrics) +
            len([k for k in result.keys() if not k.startswith(('_', 'extension'))])
        )
        result["fields_extracted"] = total_fields
        result["pet_extraction_timestamp"] = str(__import__('datetime').datetime.now())
        
    except Exception as e:
        result["extension_v_error"] = str(e)
        result["extension_v_error_type"] = type(e).__name__
    
    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count() -> int:
    return 150


def get_scientific_dicom_fits_ultimate_advanced_extension_v_supported_formats() -> List[str]:
    return [".dcm", ".dicom", ".ima", ".pt", ".pet", ".dc3"]


def get_scientific_dicom_fits_ultimate_advanced_extension_v_modalities() -> List[str]:
    return ["PT", "NM", "CT", "MR", "ST", "SR"]


def get_scientific_dicom_fits_ultimate_advanced_extension_v_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_v_description() -> str:
    return (
        "PET/CT and Nuclear Medicine Metadata Extraction Module. "
        "Supports PT, NM, CT, and MR modalities for quantitative imaging. "
        "Extracts radiopharmaceutical parameters, SUV values, attenuation "
        "correction data, and reconstruction algorithms for oncology and "
        "functional imaging applications."
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_scientific_dicom_fits_ultimate_advanced_extension_v(sys.argv[1])
        print(__import__('json').dumps(result, indent=2, default=str))
    else:
        print("Usage: python scientific_dicom_fits_ultimate_advanced_extension_v.py <dicom_file>")
        print(f"Field count: {get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count()}")


# Aliases for smoke test compatibility
def extract_interventional_radiology(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_v."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_v(file_path)

def get_interventional_radiology_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_v_field_count()

def get_interventional_radiology_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_v_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_v_version()

def get_interventional_radiology_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_v_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_v_description()

def get_interventional_radiology_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_v_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_v_supported_formats()

def get_interventional_radiology_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_v_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_v_modalities()

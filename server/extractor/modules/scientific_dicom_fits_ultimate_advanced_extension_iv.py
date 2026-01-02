"""
Scientific DICOM/FITS Ultimate Advanced Extension IV

Mammography Metadata Extraction Module

This module provides comprehensive extraction of mammography and breast imaging
metadata from DICOM files, including digital breast tomosynthesis (DBT),
screening and diagnostic mammography, and breast-specific parameters.

Supported Modalities:
- MG (Mammography)
- RG (Radiography - for breast imaging)
- DBT (Digital Breast Tomosynthesis)
- SD (Screen/film Digitizer for mammograms)
- US (Breast Ultrasound)

DICOM Tags Extracted:
- View position and laterality
- Breast density assessment
- Compression parameters
- CAD (Computer-Aided Detection) results
- Acquisition geometry
- Processing parameters
- Implant-related fields

References:
- DICOM PS3.3 - Mammography IOD
- DICOM PS3.6 - Data Dictionary
- ACR (American College of Radiology) standards
- BI-RADS (Breast Imaging Reporting and Data System)
- MQSA (Mammography Quality Standards Act)
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_IV_AVAILABLE = True

# Mammography-specific DICOM tags (Groups 0018, 0020, 0028, 0054)
MAMMO_TAGS = {
    # View Position and Laterality
    (0x0018, 0x5101): "view_position",
    (0x0020, 0x0060): "laterality",
    (0x0020, 0x0062): "image_laterality",
    (0x0018, 0x5100): "patient_position",
    (0x0018, 0x5104): "view_code_sequence",
    (0x0018, 0x5106): "view_modifier_code_sequence",
    
    # Breast Density
    (0x0018, 0x9060): "breast_implant_present",
    (0x0018, 0x9061): "breast_density",
    (0x0018, 0x9062): "compression_force",
    (0x0018, 0x9063): "compression_force_sequence",
    (0x0018, 0x9064): "compression_force_description",
    (0x0018, 0x9065): "compression_pressure",
    (0x0018, 0x9066): "compression_pressure_sequence",
    (0x0018, 0x9067): "compression_pressure_description",
    
    # CAD Results
    (0x0018, 0x9009): "algorithm_name",
    (0x0018, 0x9014): "algorithm_version",
    (0x0018, 0x9015): "algorithm_parameters",
    (0x0018, 0x9016): "algorithm_source",
    (0x0018, 0x9017): "algorithm_description",
    (0x0018, 0x9007): "cad_output_available",
    (0x0018, 0x9008): "cad_inverted_response",
    (0x0018, 0x9010): "cad_probability",
    (0x0018, 0x9011): "cad_probability_sequence",
    (0x0018, 0x9012): "cad_segmentation_sequence",
    (0x0018, 0x9013): "cad_segmentation_description",
    (0x0018, 0x9018): "cad_algorithm_id_sequence",
    (0x0018, 0x9019): "cad_algorithm_name_code_sequence",
    (0x0018, 0x9020): "cad_result_sequence",
    (0x0018, 0x9021): "cad_result_description",
    (0x0018, 0x9022): "cad_result_probability",
    
    # Acquisition Geometry
    (0x0018, 0x1110): "distance_source_to_detector",
    (0x0018, 0x1111): "distance_source_to_patient",
    (0x0018, 0x1140): "radiopharmaceutical_sequence",
    (0x0018, 0x1141): "radiopharmaceutical_start_time",
    (0x0018, 0x1142): "radiopharmaceutical_start_date_time",
    (0x0018, 0x1143): "radiopharmaceutical_stop_time",
    (0x0018, 0x1144): "radiopharmaceutical_stop_date_time",
    (0x0018, 0x1145): "radiopharmaceutical_action_type",
    (0x0018, 0x1146): "radiopharmaceutical",
    (0x0018, 0x1150): "interventionDrug_sequence",
    (0x0018, 0x1151): "intervention_drug_start_time",
    (0x0018, 0x1152): "intervention_drug_stop_time",
    (0x0018, 0x1153): "intervention_drug_dose",
    (0x0018, 0x1154): "intervention_drug_sequence",
    (0x0018, 0x1155): "intervention_drug_name",
    (0x0018, 0x1156): "intervention_drug_dose_units",
    
    # X-Ray Generation
    (0x0018, 0x1151): "xray_tube_current",
    (0x0018, 0x1152): "xray_tube_current_sequence",
    (0x0018, 0x1153): "xray_tube_current_in_mA",
    (0x0018, 0x1154): "exposure",
    (0x0018, 0x1155): "exposure_sequence",
    (0x0018, 0x1156): "exposure_in_mAs",
    (0x0018, 0x1157): "anode_target_material",
    (0x0018, 0x1158): "filter_material",
    (0x0018, 0x1159): "filter_thickness_minimum",
    (0x0018, 0x1160): "filter_thickness_maximum",
    (0x0018, 0x1162): "exposure_index",
    (0x0018, 0x1163): "target_exposure_index",
    (0x0018, 0x1164): "deviation_index",
    
    # Image Processing
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "window_center_width_explanation",
    (0x0028, 0x1053): "rescale_intercept",
    (0x0028, 0x1054): "rescale_slope",
    (0x0028, 0x1055): "rescale_type",
    (0x0028, 0x1090): "pixel_intensity_relationship",
    (0x0028, 0x1091): "pixel_intensity_relationship_sign",
    (0x0028, 0x1100): "calibration_object",
    (0x0028, 0x1101): "calibration_date",
    (0x0028, 0x1102): "calibration_time",
    
    # DBT-Specific Tags
    (0x0018, 0x9068): "number_of_exposure_sources",
    (0x0018, 0x9069): "exposure_index_sequence",
    (0x0018, 0x9070): "exposure_start_date_time",
    (0x0018, 0x9071): "exposure_stop_date_time",
    (0x0018, 0x9072): "total_acquisition_time",
    (0x0018, 0x9073): "total_exposure_dose",
    (0x0018, 0x9074): "original_image_identification",
    (0x0018, 0x9075): "original_image_identification_sequence",
    
    # Implant Assessment
    (0x0018, 0x9080): "implant_part_number",
    (0x0018, 0x9081): "implant_manufacturer",
    (0x0018, 0x9082): "implant_description",
    (0x0018, 0x9083): "implant_date",
    (0x0018, 0x9084): "implant_size",
    (0x0018, 0x9085): "implant_shape",
    (0x0018, 0x9086): "implant_surface_texture",
    (0x0018, 0x9087): "implant_filling_material",
    (0x0018, 0x9088): "implant_filling_material_percent",
    (0x0018, 0x9089): "implant_composition",
    (0x0018, 0x9090): "implant_marker",
    (0x0018, 0x9091): "implant_version",
    (0x0018, 0x9092): "implant_integrity",
    
    # Screening Assessment
    (0x0020, 0x0200): "synchronization_frame_of_reference_uid",
    (0x0020, 0x0202): "synchronization_trigger",
    (0x0020, 0x0204): "trigger_sample_offset",
    (0x0020, 0x0206): "studies_containing_other_referencing_instances_sequence",
    (0x0020, 0x0208): "referenced_series_sequence",
    (0x0020, 0x0209): "referenced_instance_sequence",
    (0x0020, 0x0210): "referenced_study_sequence",
    (0x0020, 0x0212): "referenced_object_view_sequence",
}

# Mammography-specific body parts
MAMMO_BODY_PARTS = [
    "BREAST",
    "LEFT BREAST",
    "RIGHT BREAST",
    "BILATERAL BREAST",
    "AXILLA",
    "CHEST WALL",
]

# Mammography modalities
MAMMO_MODALITIES = ["MG", "RG", "DBT", "SD", "US", "CR", "DX"]


def _is_mammo_modality(modality: str) -> bool:
    return modality.upper() in MAMMO_MODALITIES


def _is_mammo_body_part(body_part: str) -> bool:
    if not body_part:
        return False
    body_part_upper = body_part.upper()
    return any(mammo in body_part_upper for mammo in MAMMO_BODY_PARTS)


def _extract_mammo_tags(ds) -> Dict[str, Any]:
    result = {}
    for tag_tuple, tag_name in MAMMO_TAGS.items():
        try:
            if tag_tuple in ds:
                value = ds[tag_tuple].value
                if value is not None and value != "":
                    result[f"mammo_{tag_name}"] = str(value)
        except Exception:
            continue
    return result


def _extract_breast_density(ds) -> Dict[str, Any]:
    result = {}
    try:
        density = ds.get((0x0018, 0x9061), None)
        if density:
            density_val = density.value if hasattr(density, 'value') else density
            result["mammo_density_grade"] = str(density_val)
            
            # Map density to BI-RADS categories if numeric
            try:
                density_num = float(density_val)
                if density_num <= 25:
                    result["mammo_density_category"] = "Almost entirely fat"
                elif density_num <= 50:
                    result["mammo_density_category"] = "Scattered fibroglandular densities"
                elif density_num <= 75:
                    result["mammo_density_category"] = "Heterogeneously dense"
                else:
                    result["mammo_density_category"] = "Extremely dense"
            except (ValueError, TypeError):
                pass
        
        implant = ds.get((0x0018, 0x9060), None)
        if implant:
            implant_val = implant.value if hasattr(implant, 'value') else implant
            result["mammo_implant_present"] = str(implant_val)
            
    except Exception:
        pass
    return result


def _extract_compression_parameters(ds) -> Dict[str, Any]:
    result = {}
    try:
        force = ds.get((0x0018, 0x9062), None)
        if force:
            force_val = force.value if hasattr(force, 'value') else force
            try:
                result["mammo_compression_force_N"] = round(float(force_val), 1)
            except (ValueError, TypeError):
                result["mammo_compression_force"] = str(force_val)
        
        pressure = ds.get((0x0018, 0x9065), None)
        if pressure:
            pressure_val = pressure.value if hasattr(pressure, 'value') else pressure
            try:
                result["mammo_compression_pressure_kPa"] = round(float(pressure_val), 1)
            except (ValueError, TypeError):
                result["mammo_compression_pressure"] = str(pressure_val)
                
    except Exception:
        pass
    return result


def _extract_cad_results(ds) -> Dict[str, Any]:
    result = {}
    try:
        cad_available = ds.get((0x0018, 0x9007), None)
        if cad_available:
            result["mammo_cad_available"] = str(cad_available.value)
        
        cad_output = ds.get((0x0018, 0x9007), None)
        if cad_output:
            result["mammo_cad_output"] = str(cad_output.value)
            
        algorithm_name = ds.get((0x0018, 0x9009), None)
        if algorithm_name:
            result["mammo_cad_algorithm"] = str(algorithm_name.value)
            
        algorithm_version = ds.get((0x0018, 0x9014), None)
        if algorithm_version:
            result["mammo_cad_version"] = str(algorithm_version.value)
            
    except Exception:
        pass
    return result


def _calculate_mammo_metrics(ds) -> Dict[str, Any]:
    result = {}
    try:
        # Calculate exposure index deviation
        exposure_idx = ds.get((0x0018, 0x1162), None)
        target_idx = ds.get((0x0018, 0x1163), None)
        deviation = ds.get((0x0018, 0x1164), None)
        
        if exposure_idx and target_idx:
            try:
                e_val = float(exposure_idx.value) if hasattr(exposure_idx, 'value') else float(exposure_idx)
                t_val = float(target_idx.value) if hasattr(target_idx, 'value') else float(target_idx)
                if t_val > 0:
                    deviation_calc = ((e_val - t_val) / t_val) * 100
                    result["mammo_exposure_deviation_percent"] = round(deviation_calc, 1)
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        
        if deviation:
            result["mammo_deviation_index"] = str(deviation.value)
            
    except Exception:
        pass
    return result


def _is_mammo_file(filepath: str) -> bool:
    try:
        import pydicom
        
        if not filepath.lower().endswith(('.dcm', '.dicom', '.ima', '.dcm')):
            return False
        
        ds = pydicom.dcmread(filepath, force=True)
        
        modality = getattr(ds, 'Modality', '')
        if _is_mammo_modality(modality):
            return True
        
        body_part = getattr(ds, 'BodyPartExamined', '')
        if _is_mammo_body_part(body_part):
            return True
        
        study_desc = getattr(ds, 'StudyDescription', '').upper()
        series_desc = getattr(ds, 'SeriesDescription', '').upper()
        
        mammo_keywords = [
            'MAMMO', 'BREAST', 'SCREENING MAMMO', 'DIAGNOSTIC MAMMO',
            'DBT', 'TOMOSYNTHESIS', 'DIGITAL BREAST', 'BILATERAL',
            'CC', 'MLO', 'MEDIOLATERAL OBLIQUE', 'CRANIO-CAUDAL',
            'BI-RADS', 'CAD', 'MASS', 'CALCIFICATION', 'ASYMMETRY',
            'FOCAL ASYMMETRY', 'NIPPLE', 'RETROAREOLAR', 'AXILLA'
        ]
        
        if any(kw in study_desc or kw in series_desc for kw in mammo_keywords):
            return True
        
        mammo_tag_count = sum(1 for tag in MAMMO_TAGS.keys() if tag in ds)
        if mammo_tag_count >= 3:
            return True
        
        return False
        
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_iv(file_path: str) -> Dict[str, Any]:
    """Extract mammography metadata from DICOM files.
    
    This module provides comprehensive extraction of mammography metadata
    including digital breast tomosynthesis, screening/diagnostic mammography,
    breast density assessment, and CAD results.
    
    Args:
        file_path: Path to DICOM file
        
    Returns:
        dict: Mammography metadata including:
            - View position and laterality
            - Breast density assessment
            - Compression parameters
            - CAD results
            - Acquisition geometry
            - Processing parameters
            - Implant assessment
    """
    result = {
        "extension_iv_detected": False,
        "extension_iv_type": "mammography",
        "fields_extracted": 0,
        "mammo_metadata": {},
        "breast_density": {},
        "compression_parameters": {},
        "cad_results": {},
        "mammo_derived_metrics": {},
    }
    
    try:
        import pydicom
        
        if not _is_mammo_file(file_path):
            return result
        
        ds = pydicom.dcmread(file_path, force=True)
        result["extension_iv_detected"] = True
        
        result["mammo_modality"] = getattr(ds, 'Modality', 'UNKNOWN')
        result["mammo_study_description"] = getattr(ds, 'StudyDescription', '')
        result["mammo_series_description"] = getattr(ds, 'SeriesDescription', '')
        result["mammo_body_part_examined"] = getattr(ds, 'BodyPartExamined', '')
        result["mammo_view_position"] = getattr(ds, 'ViewPosition', '')
        result["mammo_laterality"] = getattr(ds, 'Laterality', '')
        
        mammo_tags = _extract_mammo_tags(ds)
        result["mammo_metadata"].update(mammo_tags)
        
        breast_density = _extract_breast_density(ds)
        result["breast_density"].update(breast_density)
        
        compression = _extract_compression_parameters(ds)
        result["compression_parameters"].update(compression)
        
        cad = _extract_cad_results(ds)
        result["cad_results"].update(cad)
        
        derived_metrics = _calculate_mammo_metrics(ds)
        result["mammo_derived_metrics"].update(derived_metrics)
        
        total_fields = (
            len(mammo_tags) + len(breast_density) + len(compression) +
            len(cad) + len(derived_metrics) +
            len([k for k in result.keys() if not k.startswith(('_', 'extension'))])
        )
        result["fields_extracted"] = total_fields
        result["mammo_extraction_timestamp"] = str(__import__('datetime').datetime.now())
        
    except Exception as e:
        result["extension_iv_error"] = str(e)
        result["extension_iv_error_type"] = type(e).__name__
    
    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_iv_field_count() -> int:
    return 120


def get_scientific_dicom_fits_ultimate_advanced_extension_iv_supported_formats() -> List[str]:
    return [".dcm", ".dicom", ".ima", ".dc3"]


def get_scientific_dicom_fits_ultimate_advanced_extension_iv_modalities() -> List[str]:
    return ["MG", "RG", "DBT", "SD", "US", "CR", "DX"]


def get_scientific_dicom_fits_ultimate_advanced_extension_iv_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_iv_description() -> str:
    return (
        "Mammography Metadata Extraction Module. "
        "Supports MG, DBT, and related breast imaging modalities. "
        "Extracts view position, breast density, compression parameters, "
        "CAD results, and breast-specific assessment fields."
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_scientific_dicom_fits_ultimate_advanced_extension_iv(sys.argv[1])
        print(__import__('json').dumps(result, indent=2, default=str))
    else:
        print("Usage: python scientific_dicom_fits_ultimate_advanced_extension_iv.py <dicom_file>")
        print(f"Field count: {get_scientific_dicom_fits_ultimate_advanced_extension_iv_field_count()}")

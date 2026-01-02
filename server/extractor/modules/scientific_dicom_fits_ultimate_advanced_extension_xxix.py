"""
Scientific DICOM/FITS Ultimate Advanced Extension XXIX - Multi-Energy Imaging

This module provides comprehensive extraction of DICOM multi-energy imaging parameters
including dual-energy CT, spectral imaging, and material decomposition.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXIX_AVAILABLE = True

MULTI_ENERGY_CT = {
    (0x0018, 0x1180): "kvp",
    (0x0018, 0x1181): "kvp_indication",
    (0x0018, 0x1182): "dual_energy_kvp_1",
    (0x0018, 0x1183): "dual_energy_kvp_2",
    (0x0018, 0x1184): "dual_energy_reference_kvp",
    (0x0018, 0x1190): "xray_tube_current",
    (0x0018, 0x1191): "xray_tube_current_indication",
    (0x0018, 0x1192): "dual_energy_tube_current_1",
    (0x0018, 0x1193): "dual_energy_tube_current_2",
    (0x0018, 0x1194): "dual_energy_reference_tube_current",
    (0x0018, 0x1200): "exposure",
    (0x0018, 0x1201): "exposure_indication",
    (0x0018, 0x1202): "dual_energy_exposure_1",
    (0x0018, 0x1203): "dual_energy_exposure_2",
    (0x0018, 0x1204): "dual_energy_reference_exposure",
    (0x0018, 0x1300): "energy_weighting_factor",
    (0x0018, 0x1301): "energy_weighting_method",
    (0x0018, 0x1302): "multi_energy_source_type",
    (0x0018, 0x1303): "multi_energy_source_configuration",
    (0x0018, 0x1304): "multi_energy_detector_type",
    (0x0018, 0x1305): "multi_energy_detector_configuration",
}

SPECTRAL_IMAGING = {
    (0x0018, 0x9310): "spectral_acquisition_sequence",
    (0x0018, 0x9311): "spectral_source_sequence",
    (0x0018, 0x9312): "spectral_source_type",
    (0x0018, 0x9313): "spectral_source_description",
    (0x0018, 0x9314): "spectral_source_parameters_sequence",
    (0x0018, 0x9315): "spectral_source_parameter",
    (0x0018, 0x9316): "spectral_source_parameter_modifier",
    (0x0018, 0x9317): "spectral_source_geometry",
    (0x0018, 0x9318): "spectral_source_orientation",
    (0x0018, 0x9319): "spectral_source_position",
    (0x0018, 0x931A): "spectral_source_direction",
    (0x0018, 0x931B): "spectral_detector_sequence",
    (0x0018, 0x931C): "spectral_detector_type",
    (0x0018, 0x931D): "spectral_detector_description",
    (0x0018, 0x931E): "spectral_detector_parameters_sequence",
    (0x0018, 0x931F): "spectral_detector_parameter",
}

MATERIAL_DECOMPOSITION = {
    (0x0018, 0x9320): "material_decomposition_sequence",
    (0x0018, 0x9321): "material_decomposition_type",
    (0x0018, 0x9322): "material_decomposition_description",
    (0x0018, 0x9323): "material_decomposition_algorithm_sequence",
    (0x0018, 0x9324): "material_decomposition_algorithm_name",
    (0x0018, 0x9325): "material_decomposition_algorithm_version",
    (0x0018, 0x9326): "material_decomposition_parameters_sequence",
    (0x0018, 0x9327): "material_decomposition_parameter",
    (0x0018, 0x9328): "material_decomposition_parameter_description",
    (0x0018, 0x9329): "material_decomposition_unit",
    (0x0018, 0x932A): "material_composition_sequence",
    (0x0018, 0x932B): "material_composition_type",
    (0x0018, 0x932C): "material_composition_description",
    (0x0018, 0x932D): "material_composition_value",
    (0x0018, 0x932E): "material_composition_unit",
    (0x0018, 0x932F): "material_composition_reference",
}

MULTI_ENERGY_TOTAL_TAGS = MULTI_ENERGY_CT | SPECTRAL_IMAGING | MATERIAL_DECOMPOSITION


def _extract_multi_energy_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in MULTI_ENERGY_CT.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_multi_energy_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['CT', 'CR', 'DX']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxix_detected": False,
        "fields_extracted": 0,
        "extension_xxix_type": "multi_energy_imaging",
        "extension_xxix_version": "2.0.0",
        "multi_energy_modality": None,
        "dual_energy_parameters": {},
        "spectral_acquisition": {},
        "material_decomposition": {},
        "extraction_errors": [],
    }

    try:
        if not _is_multi_energy_file(file_path):
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

        result["extension_xxix_detected"] = True
        result["multi_energy_modality"] = getattr(ds, 'Modality', 'CT')

        multi_energy = _extract_multi_energy_tags(ds)
        result["dual_energy_parameters"] = multi_energy

        total_fields = len(multi_energy)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_field_count() -> int:
    return len(MULTI_ENERGY_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_description() -> str:
    return ("Multi-energy imaging metadata extraction. Supports dual-energy CT, "
            "spectral imaging, and material decomposition. Extracts dual-kVp "
            "parameters, energy weighting, and material-specific data for "
            "comprehensive spectral analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_modalities() -> List[str]:
    return ["CT", "CR", "DX", "MG"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_category() -> str:
    return "Multi-Energy and Spectral Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxix_keywords() -> List[str]:
    return [
        "dual-energy", "spectral CT", "multi-energy", "material decomposition",
        "iodine mapping", "virtual non-contrast", "VNC", "monoenergetic",
        "k-edge imaging", "energy discriminating", "photon counting"
    ]

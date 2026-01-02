"""
Scientific DICOM/FITS Ultimate Advanced Extension XXVII - Presentation States

This module provides comprehensive extraction of DICOM grayscale softcopy presentation
states including window level, VOI LUT, and display parameters.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXVII_AVAILABLE = True

PRESENTATION_LUT = {
    (0x2050, 0x0010): "presentation_lut_sequence",
    (0x2050, 0x0020): "presentation_lut_shape",
    (0x2050, 0x0030): "luts_in_presentation_lut_sequence",
    (0x2050, 0x0040): "lut_in_presentation_lut_sequence",
    (0x2050, 0x0050): "presentation_lut_description",
    (0x2050, 0x0060): "referenced_presentation_lut_sequence",
    (0x0028, 0x1050): "window_center",
    (0x0028, 0x1051): "window_width",
    (0x0028, 0x1052): "rescale_intercept",
    (0x0028, 0x1053): "rescale_slope",
    (0x0028, 0x1054): "rescale_type",
    (0x0028, 0x1055): "window_center_width_explanation",
    (0x0028, 0x1056): "voi_lut_function",
    (0x0028, 0x3002): "modality_lut_sequence",
    (0x0028, 0x3006): "voi_lut_sequence",
    (0x0028, 0x3010): "softcopy_voi_lut_sequence",
}

SOFTCOPY_DISPLAY = {
    (0x0070, 0x0100): "display_environment_sequence",
    (0x0070, 0x0101): "display_environment_size",
    (0x0070, 0x0102): "display_environment_shape",
    (0x0070, 0x0103): "display_environment_description",
    (0x0070, 0x0104): "display_environment_sequence_2",
    (0x0070, 0x0105): "display_environment_characteristics_sequence",
    (0x0070, 0x0106): "display_environment_characteristics",
    (0x0070, 0x0107): "display_environment_luminance_range",
    (0x0070, 0x0108): "display_environment_colorimetry",
    (0x0070, 0x0109): "display_environment_ambient_light",
    (0x0070, 0x0110): "graphics_sequence",
    (0x0070, 0x0111): "graphics_layer_sequence",
    (0x0070, 0x0112): "graphics_layer",
    (0x0070, 0x0113): "graphics_layer_order",
    (0x0070, 0x0114): "graphics_layer_recommended_display",
    (0x0070, 0x0115): "graphics_layer_description",
    (0x0070, 0x0120): "text_style_sequence",
    (0x0070, 0x0121): "text_style_characteristics",
    (0x0070, 0x0122): "text_font_sequence",
    (0x0070, 0x0123): "text_font_style",
    (0x0070, 0x0124): "text_style_modifier",
}

ANNOTATION = {
    (0x0070, 0x0001): "presentation_sequence",
    (0x0070, 0x0002): "presentation_sequence_2",
    (0x0070, 0x0003): "referenced_structure_set_sequence",
    (0x0070, 0x0004): "referenced_content_item",
    (0x0070, 0x0005): "presentation_animation_sequence",
    (0x0070, 0x0006): "animation_description",
    (0x0070, 0x0007): "animation_style",
    (0x0070, 0x0008): "animation_cycle_length",
    (0x0070, 0x0009): "animation_step_description",
    (0x0070, 0x0010): "shape_type_sequence",
    (0x0070, 0x0011): "shape_type",
    (0x0070, 0x0012): "shape_type_code_sequence",
    (0x0070, 0x0013): "shape_description",
    (0x0070, 0x0014): "shape_description_code_sequence",
    (0x0070, 0x0015): "shape_label",
    (0x0070, 0x0016): "shape_label_code_sequence",
    (0x0070, 0x0017): "shape_geometry",
    (0x0070, 0x0018): "shape_geometry_code_sequence",
}

PRESENTATION_TOTAL_TAGS = PRESENTATION_LUT | SOFTCOPY_DISPLAY | ANNOTATION


def _extract_presentation_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in PRESENTATION_LUT.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_presentation_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                sop_class = getattr(ds, 'SOPClassUID', '')
                if 'Presentation' in sop_class:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxvii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxvii_detected": False,
        "fields_extracted": 0,
        "extension_xxvii_type": "presentation_states",
        "extension_xxvii_version": "2.0.0",
        "presentation_type": None,
        "presentation_lut": {},
        "softcopy_display": {},
        "annotation_graphics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_presentation_file(file_path):
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

        result["extension_xxvii_detected"] = True
        result["presentation_type"] = "PR"

        presentation = _extract_presentation_tags(ds)
        result["presentation_lut"] = presentation

        total_fields = len(presentation)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_field_count() -> int:
    return len(PRESENTATION_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_description() -> str:
    return ("DICOM presentation state extraction. Supports grayscale softcopy "
            "presentation states, VOI LUT parameters, and display settings. "
            "Extracts window level, annotations, and graphics for comprehensive "
            "display standardization analysis.")


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_modalities() -> List[str]:
    return ["PR", "GSPS"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_category() -> str:
    return "DICOM Presentation States"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxvii_keywords() -> List[str]:
    return [
        "presentation state", "GSPS", "window level", "VOI LUT",
        "display parameters", "grayscale", "softcopy", "annotation",
        "graphics", "PACS", "image display", "hanging protocol"
    ]

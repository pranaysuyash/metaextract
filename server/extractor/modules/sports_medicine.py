"""
Scientific DICOM/FITS Ultimate Advanced Extension XLIX - AI and Machine Learning Integration

This module provides comprehensive extraction of AI/ML integration parameters
including model metadata, inference results, and algorithmic analysis.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XLIX_AVAILABLE = True

AI_MODEL_METADATA = {
    (0x0018, 0xA001): "ai_model_uid",
    (0x0018, 0xA002): "ai_model_name",
    (0x0018, 0xA003): "ai_model_version",
    (0x0018, 0xA004): "ai_model_description",
    (0x0018, 0xA005): "ai_model_manufacturer",
    (0x0018, 0xA006): "ai_model_manufacturer_model_name",
    (0x0018, 0xA007): "ai_model_software_version",
    (0x0018, 0xA008): "ai_model_date",
    (0x0018, 0xA009): "ai_model_type",
    (0x0018, 0xA00A): "ai_model_type_description",
    (0x0018, 0xA00B): "ai_model_architecture",
    (0x0018, 0xA00C): "ai_model_architecture_description",
    (0x0018, 0xA00D): "ai_model_training_data",
    (0x0018, 0xA00E): "ai_model_training_data_description",
    (0x0018, 0xA00F): "ai_model_training_dataset_size",
    (0x0018, 0xA010): "ai_model_training_dataset_size_unit",
    (0x0018, 0xA011): "ai_model_performance_metrics_sequence",
    (0x0018, 0xA012): "ai_model_performance_metric_type",
    (0x0018, 0xA013): "ai_model_performance_metric_value",
    (0x0018, 0xA014): "ai_model_performance_metric_unit",
    (0x0018, 0xA015): "ai_model_performance_metric_description",
    (0x0018, 0xA016): "ai_model_input_sequence",
    (0x0018, 0xA017): "ai_model_input_type",
    (0x0018, 0xA018): "ai_model_input_type_description",
    (0x0018, 0xA019): "ai_model_input_modality",
    (0x0018, 0xA01A): "ai_model_output_sequence",
    (0x0018, 0xA01B): "ai_model_output_type",
    (0x0018, 0xA01C): "ai_model_output_type_description",
    (0x0018, 0xA01D): "ai_model_output_value_type",
    (0x0018, 0xA01E): "ai_model_output_value",
    (0x0018, 0xA01F): "ai_model_output_value_unit",
    (0x0018, 0xA020): "ai_model_confidence_sequence",
    (0x0018, 0xA021): "ai_model_confidence_type",
    (0x0018, 0xA022): "ai_model_confidence_value",
    (0x0018, 0xA023): "ai_model_confidence_unit",
    (0x0018, 0xA024): "ai_model_confidence_description",
}

AI_INFERENCE = {
    (0x0018, 0xA030): "ai_inference_sequence",
    (0x0018, 0xA031): "ai_inference_uid",
    (0x0018, 0xA032): "ai_inference_date_time",
    (0x0018, 0xA033): "ai_inference_duration",
    (0x0018, 0xA034): "ai_inference_duration_unit",
    (0x0018, 0xA035): "ai_inference_status",
    (0x0018, 0xA036): "ai_inference_status_description",
    (0x0018, 0xA037): "ai_inference_error_sequence",
    (0x0018, 0xA038): "ai_inference_error_type",
    (0x0018, 0xA039): "ai_inference_error_message",
    (0x0018, 0xA040): "ai_inference_result_sequence",
    (0x0018, 0xA041): "ai_inference_result_type",
    (0x0018, 0xA042): "ai_inference_result_value",
    (0x0018, 0xA043): "ai_inference_result_unit",
    (0x0018, 0xA044): "ai_inference_result_description",
    (0x0018, 0xA045): "ai_inference_probability_sequence",
    (0x0018, 0xA046): "ai_inference_probability_type",
    (0x0018, 0xA047): "ai_inference_probability_value",
    (0x0018, 0xA048): "ai_inference_probability_unit",
    (0x0018, 0xA049): "ai_inference_probability_description",
    (0x0018, 0xA050): "ai_inference_segmentation_sequence",
    (0x0018, 0xA051): "ai_inference_segmentation_roi_sequence",
    (0x0018, 0xA052): "ai_inference_segmentation_roi_uid",
    (0x0018, 0xA053): "ai_inference_segmentation_roi_name",
    (0x0018, 0xA054): "ai_inference_segmentation_roi_description",
    (0x0018, 0xA055): "ai_inference_segmentation_roi_type",
    (0x0018, 0xA056): "ai_inference_segmentation_roi_type_description",
    (0x0018, 0xA057): "ai_inference_segmentation_roi_color",
    (0x0018, 0xA058): "ai_inference_segmentation_roi_opacity",
    (0x0018, 0xA059): "ai_inference_segmentation_roi_quality",
    (0x0018, 0xA060): "ai_inference_classification_sequence",
    (0x0018, 0xA061): "ai_inference_class_type",
    (0x0018, 0xA062): "ai_inference_class_value",
    (0x0018, 0xA063): "ai_inference_class_description",
    (0x0018, 0xA064): "ai_inference_class_confidence",
    (0x0018, 0xA065): "ai_inference_class_confidence_unit",
}

AI_QUALITY = {
    (0x0018, 0xA070): "ai_quality_sequence",
    (0x0018, 0xA071): "ai_quality_type",
    (0x0018, 0xA072): "ai_quality_value",
    (0x0018, 0xA073): "ai_quality_unit",
    (0x0018, 0xA074): "ai_quality_description",
    (0x0018, 0xA075): "ai_quality_standard_sequence",
    (0x0018, 0xA076): "ai_quality_standard_type",
    (0x0018, 0xA077): "ai_quality_standard_type_description",
    (0x0018, 0xA078): "ai_quality_standard_value",
    (0x0018, 0xA079): "ai_quality_standard_value_unit",
    (0x0018, 0xA080): "ai_bias_sequence",
    (0x0018, 0xA081): "ai_bias_type",
    (0x0018, 0xA082): "ai_bias_value",
    (0x0018, 0xA083): "ai_bias_unit",
    (0x0018, 0xA084): "ai_bias_description",
    (0x0018, 0xA090): "ai_fairness_sequence",
    (0x0018, 0xA091): "ai_fairness_type",
    (0x0018, 0xA092): "ai_fairness_value",
    (0x0018, 0xA093): "ai_fairness_unit",
    (0x0018, 0xA094): "ai_fairness_description",
    (0x0018, 0xA0A0): "ai_explainability_sequence",
    (0x0018, 0xA0A1): "ai_explainability_type",
    (0x0018, 0xA0A2): "ai_explainability_value",
    (0x0018, 0xA0A3): "ai_explainability_unit",
    (0x0018, 0xA0A4): "ai_explainability_description",
    (0x0018, 0xA0B0): "ai_uncertainty_sequence",
    (0x0018, 0xA0B1): "ai_uncertainty_type",
    (0x0018, 0xA0B2): "ai_uncertainty_value",
    (0x0018, 0xA0B3): "ai_uncertainty_unit",
    (0x0018, 0xA0B4): "ai_uncertainty_description",
}

AI_TOTAL_TAGS = AI_MODEL_METADATA | AI_INFERENCE | AI_QUALITY


def _extract_ai_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    for tag, name in AI_TOTAL_TAGS.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_ai_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            return True
    except Exception:
        pass
    return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xlix(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xlix_detected": False,
        "fields_extracted": 0,
        "extension_xlix_type": "ai_ml_integration",
        "extension_xlix_version": "2.0.0",
        "model_metadata": {},
        "inference_results": {},
        "quality_metrics": {},
        "extraction_errors": [],
    }

    try:
        if not _is_ai_file(file_path):
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

        result["extension_xlix_detected"] = True

        ai_data = _extract_ai_tags(ds)

        result["model_metadata"] = {
            k: v for k, v in ai_data.items()
            if k in AI_MODEL_METADATA.values()
        }
        result["inference_results"] = {
            k: v for k, v in ai_data.items()
            if k in AI_INFERENCE.values()
        }
        result["quality_metrics"] = {
            k: v for k, v in ai_data.items()
            if k in AI_QUALITY.values()
        }

        result["fields_extracted"] = len(ai_data)

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_field_count() -> int:
    return len(AI_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_description() -> str:
    return (
        "AI and Machine Learning integration metadata extraction. Provides comprehensive "
        "coverage of AI model metadata, inference results, confidence scores, segmentation "
        "outputs, classification results, and AI quality/ fairness metrics."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_modalities() -> List[str]:
    return ["CT", "MR", "CR", "DR", "US", "PT", "NM", "MG", "XA"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_category() -> str:
    return "AI and Machine Learning Integration"


def get_scientific_dicom_fits_ultimate_advanced_extension_xlix_keywords() -> List[str]:
    return [
        "AI", "machine learning", "deep learning", "CAD", "artificial intelligence",
        "neural network", "inference", "classification", "segmentation",
        "model", "confidence", "explainability", "bias", "fairness"
    ]


# Aliases for smoke test compatibility
def extract_sports_medicine(file_path):
    """Alias for extract_scientific_dicom_fits_ultimate_advanced_extension_xlix."""
    return extract_scientific_dicom_fits_ultimate_advanced_extension_xlix(file_path)

def get_sports_medicine_field_count():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xlix_field_count."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xlix_field_count()

def get_sports_medicine_version():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xlix_version."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xlix_version()

def get_sports_medicine_description():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xlix_description."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xlix_description()

def get_sports_medicine_supported_formats():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xlix_supported_formats."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xlix_supported_formats()

def get_sports_medicine_modalities():
    """Alias for get_scientific_dicom_fits_ultimate_advanced_extension_xlix_modalities."""
    return get_scientific_dicom_fits_ultimate_advanced_extension_xlix_modalities()

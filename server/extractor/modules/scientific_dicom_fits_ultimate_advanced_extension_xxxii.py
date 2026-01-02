"""
Scientific DICOM/FITS Ultimate Advanced Extension XXXII - Genomics and Molecular Imaging

This module provides comprehensive extraction of genomics and molecular imaging
parameters including sequencing data, biomarker analysis, and molecular markers.

Author: MetaExtract Development Team
Version: 2.0.0
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SCIENTIFIC_DICOM_FITS_ULTIMATE_ADVANCED_EXTENSION_XXXII_AVAILABLE = True

SEQUENCING_PARAMETERS = {
    (0x0048, 0x1000): "sequencing_method",
    (0x0048, 0x1001): "sequencing_platform",
    (0x0048, 0x1002): "sequencing_manufacturer",
    (0x0048, 0x1003): "sequencing_model",
    (0x0048, 0x1004): "sequencing_software_version",
    (0x0048, 0x1005): "library_preparation_kit",
    (0x0048, 0x1006): "library_preparation_protocol",
    (0x0048, 0x1007): "library_layout_type",
    (0x0048, 0x1008): "library_average_fragment_length",
    (0x0048, 0x1009): "library_insert_size",
    (0x0048, 0x100A): "library_concentration",
    (0x0048, 0x100B): "sequencing_run_id",
    (0x0048, 0x100C): "sequencing_run_date_time",
    (0x0048, 0x100D): "sequencing_cycle_count",
    (0x0048, 0x100E): "read_length",
    (0x0048, 0x100F): "read_type",
    (0x0048, 0x1010): "sequencing_depth",
    (0x0048, 0x1011): "coverage_depth",
    (0x0048, 0x1012): "total_reads",
    (0x0048, 0x1013): "mapped_reads",
    (0x0048, 0x1014): "unmapped_reads",
    (0x0048, 0x1015): "quality_score_encoding",
    (0x0048, 0x1016): "mean_quality_score",
    (0x0048, 0x1017): "gc_content",
    (0x0048, 0x1018): "duplicate_reads",
    (0x0048, 0x1019): "duplicate_reads_percentage",
    (0x0048, 0x101A): "adapter_sequence",
    (0x0048, 0x101B): "adapter_trimming_status",
}

MOLECULAR_MARKERS = {
    (0x0048, 0x1100): "biomarker_name",
    (0x0048, 0x1101): "biomarker_type",
    (0x0048, 0x1102): "biomarker_value",
    (0x0048, 0x1103): "biomarker_unit",
    (0x0048, 0x1104): "biomarker_test_method",
    (0x0048, 0x1105): "biomarker_test_kit",
    (0x0048, 0x1106): "biomarker_result_reference_range",
    (0x0048, 0x1107): "biomarker_clinical_significance",
    (0x0048, 0x1108): "biomarker_mutation_type",
    (0x0048, 0x1109): "biomarker_mutation_position",
    (0x0048, 0x110A): "biomarker_allele_frequency",
    (0x0048, 0x110B): "biomarker_read_depth",
    (0x0048, 0x110C): "biomarker_gene_name",
    (0x0048, 0x110D): "biomarker_transcript_id",
    (0x0048, 0x110E): "biomarker_protein_change",
    (0x0048, 0x110F): "biomarker_pathogenic_status",
    (0x0048, 0x1110): "oncogene_panel",
    (0x0048, 0x1111): "oncogene_panel_name",
    (0x0048, 0x1112): "oncogene_panel_version",
    (0x0048, 0x1113): "genes_tested_count",
    (0x0048, 0x1114): "genes_with_variants_count",
    (0x0048, 0x1115): "variant_interpretation",
    (0x0048, 0x1116): "therapeutic_implication",
    (0x0048, 0x1117): "drug_response_prediction",
    (0x0048, 0x1118): "clinical_trial_eligibility",
    (0x0048, 0x1119): "molecular_diagnosis",
}

GENE_EXPRESSION = {
    (0x0048, 0x1200): "expression_technology",
    (0x0048, 0x1201): "expression_platform",
    (0x0048, 0x1202): "expression_normalization_method",
    (0x0048, 0x1203): "expression_reference_dataset",
    (0x0048, 0x1204): "expression_baseline",
    (0x0048, 0x1205): "differential_expression_analysis",
    (0x0048, 0x1206): "expression_fold_change",
    (0x0048, 0x1207): "expression_p_value",
    (0x0048, 0x1208): "expression_false_discovery_rate",
    (0x0048, 0x1209): "expression_significance_threshold",
    (0x0048, 0x120A): "upregulated_genes_count",
    (0x0048, 0x120B): "downregulated_genes_count",
    (0x0048, 0x120C): "pathway_enrichment_analysis",
    (0x0048, 0x120D): "gene_set_enrichment_score",
    (0x0048, 0x120E): "immune_signature_score",
    (0x0048, 0x120F): "tumor_microenvironment_score",
    (0x0048, 0x1210): "proliferation_index",
    (0x0048, 0x1211): "stemness_index",
    (0x0048, 0x1212): "differentiation_index",
    (0x0048, 0x1213): "angiogenesis_score",
    (0x0048, 0x1214): "epithelial_mesenchymal_transition_score",
    (0x0048, 0x1215): "mutation_burden",
    (0x0048, 0x1216): "tumor_mutational_burden",
    (0x0048, 0x1217): "microsatellite_instability_status",
    (0x0048, 0x1218): "mismatch_repair_status",
    (0x0048, 0x1219): "neoantigen_load",
}

PROTEOMICS = {
    (0x0048, 0x1300): "proteomics_technology",
    (0x0048, 0x1301): "mass_spectrometry_type",
    (0x0048, 0x1302): "mass_analyzer_type",
    (0x0048, 0x1303): "ionization_method",
    (0x0048, 0x1304): "mass_accuracy",
    (0x0048, 0x1305): "resolution",
    (0x0048, 0x1306): "proteomics_database",
    (0x0048, 0x1307): "protein_identification_fdr",
    (0x0048, 0x1308): "peptide_identification_fdr",
    (0x0048, 0x1309): "protein_quantification_method",
    (0x0048, 0x130A): "label_free_quantification",
    (0x0048, 0x130B): "labeled_quantification_type",
    (0x0048, 0x130C): "total_proteins_identified",
    (0x0048, 0x130D): "quantified_proteins_count",
    (0x0048, 0x130E): "differentially_expressed_proteins",
    (0x0048, 0x130F): "ptm_analysis",
    (0x0048, 0x1310): "phosphorylation_sites",
    (0x0048, 0x1311): "acetylation_sites",
    (0x0048, 0x1312): "ubiquitination_sites",
    (0x0048, 0x1313): "glycosylation_sites",
    (0x0048, 0x1314): "protein_modification_type",
    (0x0048, 0x1315): "protein_interaction_network",
    (0x0048, 0x1316): "protein_complex_identification",
}

MOLECULAR_IMAGING_RADIOPHARMACEUTICALS = {
    (0x0018, 0x1040): "contrast_bolus_agent",
    (0x0018, 0x1041): "contrast_bolus_start_time",
    (0x0018, 0x1042): "contrast_bolus_stop_time",
    (0x0018, 0x1043): "contrast_bolus_total_dose",
    (0x0018, 0x1044): "contrast_flow_rate",
    (0x0018, 0x1045): "contrast_flow_duration",
    (0x0018, 0x1046): "contrast_bolus_ingredient",
    (0x0018, 0x1047): "contrast_bolus_ingredient_concentration",
    (0x0018, 0x1048): "radiopharmaceutical",
    (0x0018, 0x1049): "radiopharmaceutical_sequence",
    (0x0018, 0x1071): "radionuclide_sequence",
    (0x0018, 0x1072): "radionuclide",
    (0x0018, 0x1073): "radionuclide_activity",
    (0x0018, 0x1074): "radionuclide_activity_dateTime",
    (0x0018, 0x1075): "radionuclide_half_life",
    (0x0018, 0x1076): "radionuclide_positron_fraction",
    (0x0018, 0x1077): "radiopharmaceutical_specific_activity",
    (0x0018, 0x1078): "radiopharmaceutical_start_dateTime",
    (0x0018, 0x1079): "radiopharmaceutical_stop_dateTime",
    (0x0018, 0x1080): "calibration_sequence",
    (0x0018, 0x1081): "system_status",
    (0x0018, 0x1082): "system_status_comment",
    (0x0018, 0x1083): "data_order_of_real_world_value_map",
    (0x0018, 0x1084): "actual_frame_duration",
    (0x0018, 0x1085): "count_rate",
    (0x0018, 0x1086): "preferred_playing_speed",
    (0x0018, 0x1088): "line_density",
    (0x0018, 0x1089): "mrt_timing_relationship_type",
}

GENEALOGY_TRACKING = {
    (0x0040, 0xA730): "content_sequence",
    (0x0040, 0xA731): "content_sequence_item",
    (0x0040, 0xA732): "content_sequence_item_uid",
    (0x0040, 0xA733): "content_sequence_parent_uid",
    (0x0040, 0xA734): "content_sequence_depth",
    (0x0040, 0xA735): "content_sequence_branch",
    (0x0040, 0xA740): "content_template_sequence",
    (0x0040, 0xA741): "template_identifier",
    (0x0040, 0xA742): "template_version",
    (0x0040, 0xA743): "template_local_version",
    (0x0040, 0xA744): "template_extension_flag",
    (0x0040, 0xA745): "template_extension_creator_uid",
    (0x0040, 0xA750): "content_sequence_alternate",
    (0x0040, 0xA751): "content_sequence_alternate_item",
    (0x0040, 0xA752): "content_sequence_alternate_parent_uid",
    (0x0040, 0xA753): "content_sequence_alternate_branch",
}

GENOMICS_TOTAL_TAGS = (
    SEQUENCING_PARAMETERS | MOLECULAR_MARKERS | GENE_EXPRESSION |
    PROTEOMICS | MOLECULAR_IMAGING_RADIOPHARMACEUTICALS | GENEALOGY_TRACKING
)


def _extract_genomics_tags(ds: Any) -> Dict[str, Any]:
    extracted = {}
    all_tags = GENOMICS_TOTAL_TAGS
    for tag, name in all_tags.items():
        try:
            if hasattr(ds, str(tag)):
                value = getattr(ds, str(tag), None)
                if value is not None:
                    extracted[name] = value
        except Exception:
            pass
    return extracted


def _is_genomics_file(file_path: str) -> bool:
    try:
        file_lower = file_path.lower()
        if file_lower.endswith('.dcm'):
            try:
                import pydicom
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = getattr(ds, 'Modality', '')
                if modality in ['PT', 'NM', 'OT', 'MR', 'CT']:
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def extract_scientific_dicom_fits_ultimate_advanced_extension_xxxii(file_path: str) -> Dict[str, Any]:
    result = {
        "extension_xxxii_detected": False,
        "fields_extracted": 0,
        "extension_xxxii_type": "genomics_molecular_imaging",
        "extension_xxxii_version": "2.0.0",
        "sequencing_parameters": {},
        "molecular_markers": {},
        "gene_expression": {},
        "proteomics": {},
        "radiopharmaceuticals": {},
        "genealogy_tracking": {},
        "extraction_errors": [],
    }

    try:
        if not _is_genomics_file(file_path):
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

        result["extension_xxxii_detected"] = True

        genomics_data = _extract_genomics_tags(ds)

        result["sequencing_parameters"] = {
            k: v for k, v in genomics_data.items()
            if k in SEQUENCING_PARAMETERS.values()
        }
        result["molecular_markers"] = {
            k: v for k, v in genomics_data.items()
            if k in MOLECULAR_MARKERS.values()
        }
        result["gene_expression"] = {
            k: v for k, v in genomics_data.items()
            if k in GENE_EXPRESSION.values()
        }
        result["proteomics"] = {
            k: v for k, v in genomics_data.items()
            if k in PROTEOMICS.values()
        }
        result["radiopharmaceuticals"] = {
            k: v for k, v in genomics_data.items()
            if k in MOLECULAR_IMAGING_RADIOPHARMACEUTICALS.values()
        }
        result["genealogy_tracking"] = {
            k: v for k, v in genomics_data.items()
            if k in GENEALOGY_TRACKING.values()
        }

        total_fields = len(genomics_data)
        result["fields_extracted"] = total_fields

    except Exception as e:
        result["extraction_errors"].append(str(e))

    return result


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_field_count() -> int:
    return len(GENOMICS_TOTAL_TAGS)


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_version() -> str:
    return "2.0.0"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_description() -> str:
    return (
        "Genomics and molecular imaging metadata extraction. Provides comprehensive "
        "coverage of sequencing parameters, molecular biomarkers, gene expression "
        "analysis, proteomics, radiopharmaceuticals, and molecular imaging for "
        "precision medicine and cancer genomics applications."
    )


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_modalities() -> List[str]:
    return ["PT", "NM", "OT", "MR", "CT"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_supported_formats() -> List[str]:
    return [".dcm", ".dicom"]


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_category() -> str:
    return "Genomics and Molecular Imaging"


def get_scientific_dicom_fits_ultimate_advanced_extension_xxxii_keywords() -> List[str]:
    return [
        "genomics", "sequencing", "molecular", "biomarkers", "gene expression",
        "proteomics", "radiopharmaceuticals", "precision medicine", "cancer genomics",
        "NGS", "PCR", "immunohistochemistry"
    ]

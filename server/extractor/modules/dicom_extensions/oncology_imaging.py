"""
Oncology Imaging DICOM Extension
Implements specialized metadata extraction for oncology and cancer imaging studies
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

from .base import (
    DICOMExtensionBase,
    safe_extract_dicom_field,
    get_dicom_file_info
)

logger = logging.getLogger(__name__)


class OncologyImagingExtension(DICOMExtensionBase):
    """
    Oncology Imaging metadata extraction.

    Extracts specialized oncology-related DICOM tags including:
    - Tumor detection and characterization
    - Cancer staging and grading
    - Treatment response assessment
    - Radiation therapy planning
    - Metastasis detection and monitoring
    - Cancer screening and surveillance
    - Quantitative imaging biomarkers
    - Molecular and functional imaging
    """

    SPECIALTY = "oncology_imaging"
    FIELD_COUNT = 92
    REFERENCE = "DICOM PS3.3 (Oncology)"
    DESCRIPTION = "Oncology Imaging specialized metadata extraction"
    VERSION = "1.0.0"

    # Oncology field definitions
    ONCOLOGY_FIELDS = [
        # Tumor identification
        "TumorIdentification",
        "TumorLabel",
        "TumorLocation",
        "TumorSite",
        "TumorLaterality",
        "PrimaryTumor",
        "MetastaticTumor",
        "RecurrentTumor",
        "TumorCount",
        "TumorSize",
        "TumorVolume",
        "TumorDimensions",
        "TumorShape",
        "TumorMargins",
        "TumorCharacteristics",

        # Cancer staging
        "TNMStaging",
        "TStage",
        "NStage",
        "MStage",
        "ClinicalStage",
        "PathologicStage",
        "AJCCStage",
        "TumorGrade",
        "HistologicGrade",
        "Differentiation",
        "WellDifferentiated",
        "ModeratelyDifferentiated",
        "PoorlyDifferentiated",
        "Undifferentiated",

        # Cancer types
        "Carcinoma",
        "Adenocarcinoma",
        "SquamousCellCarcinoma",
        "Sarcoma",
        "Lymphoma",
        "Melanoma",
        "Glioma",
        "Astrocytoma",
        "Meningioma",
        "Oligodendroglioma",
        "Medulloblastoma",

        # Organ-specific tumors
        "LungCancer",
        "BreastCancer",
        "ProstateCancer",
        "ColorectalCancer",
        "LiverCancer",
        "HepatocellularCarcinoma",
        "PancreaticCancer",
        "RenalCellCarcinoma",
        "BladderCancer",
        "BrainTumor",
        "HeadAndNeckCancer",
        "EsophagealCancer",
        "GastricCancer",
        "OvarianCancer",
        "CervicalCancer",

        # Imaging characterization
        "TumorDensity",
        "TumorEnhancement",
        "ContrastEnhancement",
        "Heterogeneity",
        "Necrosis",
        "CysticComponents",
        "SolidComponents",
        "Calcification",
        "FatContent",
        "Hemorrhage",
        "FDGUptake",
        "SUV",
        "StandardizedUptakeValue",

        # Treatment response
        "TreatmentResponse",
        "ResponseEvaluation",
        "RECIST",
        "RECISTCriteria",
        "CompleteResponse",
        "PartialResponse",
        "StableDisease",
        "ProgressiveDisease",
        "TumorShrinkage",
        "TumorGrowth",
        "ResponseAssessment",
        "TherapyResponse",

        # Chemotherapy monitoring
        "Chemotherapy",
        "NeoadjuvantChemotherapy",
        "AdjuvantChemotherapy",
        "ChemotherapyRegimen",
        "TreatmentCycles",
        "TreatmentDuration",
        "ChemotherapyResponse",
        "ToxicityAssessment",
        "DoseReduction",
        "TreatmentDelay",

        # Radiation therapy
        "RadiationTherapy",
        "ExternalBeamRadiation",
        "Brachytherapy",
        "StereotacticRadiosurgery",
        "IMRT",
        "ProtonTherapy",
        "RadiationDose",
        "TreatmentFields",
        "TreatmentPlan",
        "Simulation",
        "SetupVerification",
        "Toxicity",

        # Surgical planning
        "SurgicalPlanning",
        "Resectability",
        "SurgicalMargins",
        "TumorResection",
        "LymphNodeDissection",
        "SentinelNode",
        "Metastasectomy",
        "Debulking",
        "PalliativeSurgery",
        "MinimallyInvasive",

        # Metastasis assessment
        "Metastasis",
        "LymphNodeMetastasis",
        "DistantMetastasis",
        "HepaticMetastasis",
        "PulmonaryMetastasis",
        "BoneMetastasis",
        "BrainMetastasis",
        "PeritonealMetastasis",
        "MetastaticBurden",
        "MetastaticSites",
        "Oligometastasis",

        # Cancer screening
        "Screening",
        "CancerScreening",
        "EarlyDetection",
        "Surveillance",
        "FollowUp",
        "HighRiskScreening",
        "GeneticPredisposition",
        "FamilyHistory",
        "ScreeningInterval",
        "RecurrenceSurveillance",

        # Molecular imaging
        "MolecularImaging",
        "PETImaging",
        "PETCT",
        "PETMR",
        "Radiotracer",
        "FDG",
        "FLT",
        "Choline",
        "PSMA",
        "DOTATATE",
        "ReceptorImaging",
        "HypoxiaImaging",
        "ProliferationImaging",

        # Quantitative biomarkers
        "ImagingBiomarkers",
        "VolumetricAnalysis",
        "TextureAnalysis",
        "Radiomics",
        "MachineLearning",
        "CAD",
        "ComputerAidedDetection",
        "QuantitativeAnalysis",
        "StandardizedValues",
        "Reproducibility",

        # Additional oncology parameters
        "PerformanceStatus",
        "ECOG",
        "Karnofsky",
        "Symptoms",
        "Pain",
        "WeightLoss",
        "Cachexia",
        "Prognosis",
        "SurvivalPrediction",
        "RiskStratification",
        "MolecularMarkers",
        "Biomarkers",
        "GeneticMutations",
        "TargetedTherapy",
        "Immunotherapy",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of oncology-specific DICOM field names"""
        return self.ONCOLOGY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract oncology-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing oncology metadata extraction results
        """
        start_time = time.time()
        errors = []
        warnings = []
        metadata = {}

        try:
            import pydicom

            # Validate and read DICOM file
            if not self.validate_dicom_file(filepath):
                return {
                    "specialty": self.SPECIALTY,
                    "source_file": filepath,
                    "fields_extracted": 0,
                    "metadata": {},
                    "extraction_time": time.time() - start_time,
                    "errors": ["Invalid DICOM file"],
                    "warnings": warnings
                }

            dcm = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)

            # Extract basic file info
            file_info = get_dicom_file_info(filepath)
            if "error" not in file_info:
                metadata["file_info"] = file_info

            # Detect if this is an oncology study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_oncology = (
                "tumor" in series_desc or "tumor" in study_desc or
                "cancer" in series_desc or "cancer" in study_desc or
                "oncology" in series_desc or "oncology" in study_desc or
                "metastasis" in series_desc or "metastasis" in study_desc or
                "chemo" in series_desc or "chemotherapy" in study_desc or
                "radiation" in series_desc and "cancer" in study_desc or
                "malignancy" in series_desc or "neoplasm" in study_desc
            )

            metadata["is_oncology_study"] = is_oncology
            metadata["modality"] = modality

            # Extract oncology-specific fields
            fields_extracted = 0

            for field in self.ONCOLOGY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add tumor analysis if available
            if "TumorIdentification" in metadata or "TumorSize" in metadata:
                tumor_params = self._extract_tumor_parameters(dcm)
                metadata.update(tumor_params)
                fields_extracted += len(tumor_params)

            # Add staging analysis if available
            if "TNMStaging" in metadata or "TStage" in metadata:
                staging_params = self._extract_staging_parameters(dcm)
                metadata.update(staging_params)
                fields_extracted += len(staging_params)

            # Add response analysis if available
            if "TreatmentResponse" in metadata or "RECIST" in metadata:
                response_params = self._extract_response_parameters(dcm)
                metadata.update(response_params)
                fields_extracted += len(response_params)

            # Add treatment analysis if available
            if "Chemotherapy" in metadata or "RadiationTherapy" in metadata:
                treatment_params = self._extract_treatment_parameters(dcm)
                metadata.update(treatment_params)
                fields_extracted += len(treatment_params)

            # Add metastasis analysis if available
            if "Metastasis" in metadata or "LymphNodeMetastasis" in metadata:
                metastasis_params = self._extract_metastasis_parameters(dcm)
                metadata.update(metastasis_params)
                fields_extracted += len(metastasis_params)

            # Add molecular imaging if available
            if "PETImaging" in metadata or "Radiotracer" in metadata:
                molecular_params = self._extract_molecular_parameters(dcm)
                metadata.update(molecular_params)
                fields_extracted += len(molecular_params)

            # Add biomarker analysis if available
            if "ImagingBiomarkers" in metadata or "Radiomics" in metadata:
                biomarker_params = self._extract_biomarker_parameters(dcm)
                metadata.update(biomarker_params)
                fields_extracted += len(biomarker_params)

            # Add warnings if this doesn't appear to be an oncology study
            if not is_oncology:
                warnings.append(
                    "This file may not be an oncology study. "
                    "Consider using a different DICOM extension."
                )

            result = {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": fields_extracted,
                "metadata": metadata,
                "extraction_time": time.time() - start_time,
                "errors": errors,
                "warnings": warnings
            }

            # Log extraction summary
            self.log_extraction_summary(result)

            return result

        except Exception as e:
            logger.error(f"Oncology extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_tumor_parameters(self, dcm) -> Dict[str, Any]:
        """Extract tumor identification parameters"""
        params = {}

        # Tumor fields
        tumor_fields = [
            "TumorIdentification",
            "TumorLocation",
            "TumorSize",
            "TumorVolume",
            "TumorShape",
            "TumorMargins",
            "TumorEnhancement",
        ]

        for field in tumor_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Tumor_{field}"] = value

        return params

    def _extract_staging_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cancer staging parameters"""
        params = {}

        # Staging fields
        staging_fields = [
            "TNMStaging",
            "TStage",
            "NStage",
            "MStage",
            "ClinicalStage",
            "TumorGrade",
            "HistologicGrade",
        ]

        for field in staging_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Staging_{field}"] = value

        return params

    def _extract_response_parameters(self, dcm) -> Dict[str, Any]:
        """Extract treatment response parameters"""
        params = {}

        # Response fields
        response_fields = [
            "TreatmentResponse",
            "RECIST",
            "CompleteResponse",
            "PartialResponse",
            "TumorShrinkage",
            "ResponseAssessment",
        ]

        for field in response_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Response_{field}"] = value

        return params

    def _extract_treatment_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cancer treatment parameters"""
        params = {}

        # Treatment fields
        treatment_fields = [
            "Chemotherapy",
            "NeoadjuvantChemotherapy",
            "RadiationTherapy",
            "SurgicalPlanning",
            "TreatmentCycles",
        ]

        for field in treatment_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Treatment_{field}"] = value

        return params

    def _extract_metastasis_parameters(self, dcm) -> Dict[str, Any]:
        """Extract metastasis assessment parameters"""
        params = {}

        # Metastasis fields
        metastasis_fields = [
            "Metastasis",
            "LymphNodeMetastasis",
            "DistantMetastasis",
            "HepaticMetastasis",
            "PulmonaryMetastasis",
            "MetastaticSites",
        ]

        for field in metastasis_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Metastasis_{field}"] = value

        return params

    def _extract_molecular_parameters(self, dcm) -> Dict[str, Any]:
        """Extract molecular imaging parameters"""
        params = {}

        # Molecular fields
        molecular_fields = [
            "MolecularImaging",
            "PETImaging",
            "Radiotracer",
            "FDG",
            "ReceptorImaging",
        ]

        for field in molecular_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Molecular_{field}"] = value

        return params

    def _extract_biomarker_parameters(self, dcm) -> Dict[str, Any]:
        """Extract imaging biomarker parameters"""
        params = {}

        # Biomarker fields
        biomarker_fields = [
            "ImagingBiomarkers",
            "VolumetricAnalysis",
            "TextureAnalysis",
            "Radiomics",
            "ComputerAidedDetection",
        ]

        for field in biomarker_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Biomarker_{field}"] = value

        return params

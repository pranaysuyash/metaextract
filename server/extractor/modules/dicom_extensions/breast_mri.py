"""
Breast MRI DICOM Extension
Implements specialized metadata extraction for breast MRI studies
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


class BreastMRIExtension(DICOMExtensionBase):
    """
    Breast MRI metadata extraction.

    Extracts specialized breast MRI-related DICOM tags including:
    - Breast anatomy and tissue characterization
    - Contrast enhancement kinetics
    - Lesion detection and characterization
    - BI-RADS assessment and categorization
    - Pre-surgical planning
    - Treatment response monitoring
    - Implant assessment
    - Screening and diagnostic protocols
    """

    SPECIALTY = "breast_mri"
    FIELD_COUNT = 68
    REFERENCE = "DICOM PS3.3 (Breast MRI)"
    DESCRIPTION = "Breast MRI specialized metadata extraction"
    VERSION = "1.0.0"

    # Breast MRI field definitions
    BREAST_MRI_FIELDS = [
        # Breast anatomy and positioning
        "BreastSide",
        "BreastDensity",
        "BreastComposition",
        "BreastTissue",
        "FibroglandularTissue",
        "AdiposeTissue",
        "BreastPosition",
        "PronePosition",
        "SupinePosition",
        "BreastCoil",
        "BreastCoilType",
        "BilateralImaging",
        "UnilateralImaging",
        "AxillaryImaging",
        "ChestWallInclusion",

        # Contrast administration
        "ContrastAgent",
        "ContrastBolusAgent",
        "ContrastVolume",
        "ContrastRoute",
        "ContrastFlowRate",
        "ContrastInjection",
        "GadoliniumAgent",
        "GadoliniumDose",
        "ContrastTiming",
        "PreContrast",
        "PostContrast",
        "DynamicContrastEnhanced",
        "DCE",
        "ContrastPhases",
        "TemporalResolution",

        # Kinetic analysis
        "KineticAnalysis",
        "KineticCurve",
        "InitialPhase",
        "DelayedPhase",
        "Washout",
        "Plateau",
        "PersistentEnhancement",
        "TimeIntensityCurve",
        "CurveType",
        "Slope",
        "PeakEnhancement",
        "SignalIntensity",
        "EnhancementRate",
        "WashoutRate",

        # Lesion detection
        "LesionDetection",
        "LesionCount",
        "LesionSize",
        "LesionLocation",
        "LesionMorphology",
        "LesionShape",
        "LesionMargins",
        "LesionCharacterization",
        "MassDetection",
        "MassShape",
        "MassMargins",
        "InternalEnhancement",
        "NonMassEnhancement",
        "NME",

        # BI-RADS assessment
        "BIRADS",
        "BIRADSCategory",
        "BIRADSAssessment",
        "MalignancyPotential",
        "SuspiciousFeatures",
        "BenignFeatures",
        "ACRCategorization",
        "ManagementRecommendation",
        "FollowUpRecommendation",
        "BiopsyRecommendation",

        # Tissue characterization
        "TissueCharacterization",
        "DiffusionWeightedImaging",
        "DWI",
        "ADC",
        "ApparentDiffusionCoefficient",
        "T1Mapping",
        "T2Mapping",
        "ProtonDensityFatFraction",
        "MRSpectroscopy",
        "CholinePeak",

        # Pre-surgical planning
        "SurgicalPlanning",
        "TumorExtent",
        "Multifocality",
        "Multicentricity",
        "BilateralDisease",
        "SkinInvolvement",
        "NippleInvolvement",
        "ChestWallInvasion",
        "LymphNodeInvolvement",
        "AxillaryNodes",
        "InternalMammaryNodes",
        "TumorSize",
        "TumorVolume",
        "Resectability",

        # Treatment monitoring
        "NeoadjuvantChemotherapy",
        "TreatmentResponse",
        "ResponseAssessment",
        "Responder",
        "NonResponder",
        "PartialResponse",
        "CompleteResponse",
        "ProgressiveDisease",
        "StableDisease",
        "TumorShrinkage",
        "Ki67",
        "Cellularity",

        # Implant assessment
        "BreastImplant",
        "ImplantType",
        "ImplantIntegrity",
        "ImplantRupture",
        "ImplantLocation",
        "ImplantAge",
        "ImplantComplications",
        "SiliconeImplant",
        "SalineImplant",

        # Screening and diagnostic
        "ScreeningMRI",
        "DiagnosticMRI",
        "HighRiskScreening",
        "GeneticPredisposition",
        "BRCA",
        "FamilyHistory",
        "PersonalHistory",
        "PriorSurgery",
        "RadiationTherapy",
        "HormoneTherapy",

        # Additional breast MRI parameters
        "BackgroundEnhancement",
        "BackgroundParenchymalEnhancement",
        "BPE",
        "MinimalBPE",
        "MildBPE",
        "ModerateBPE",
        "MarkedBPE",
        "Artifacts",
        "MotionArtifacts",
        "SusceptibilityArtifacts",
        "ImageQuality",
        "FatSuppression",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of breast MRI-specific DICOM field names"""
        return self.BREAST_MRI_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract breast MRI-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing breast MRI metadata extraction results
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

            # Detect if this is a breast MRI study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_breast_mri = (
                modality == "MR" and (
                    "breast" in series_desc or "breast" in study_desc or
                    "mri breast" in series_desc or "mri breast" in study_desc or
                    "bilateral" in series_desc and "breast" in study_desc or
                    "dce" in series_desc and "breast" in study_desc or
                    "bi-rads" in series_desc or "birads" in study_desc
                )
            )

            metadata["is_breast_mri_study"] = is_breast_mri
            metadata["modality"] = modality

            # Extract breast MRI-specific fields
            fields_extracted = 0

            for field in self.BREAST_MRI_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add anatomy analysis if available
            if "BreastSide" in metadata or "BreastDensity" in metadata:
                anatomy_params = self._extract_anatomy_parameters(dcm)
                metadata.update(anatomy_params)
                fields_extracted += len(anatomy_params)

            # Add contrast analysis if available
            if "ContrastAgent" in metadata or "DynamicContrastEnhanced" in metadata:
                contrast_params = self._extract_contrast_parameters(dcm)
                metadata.update(contrast_params)
                fields_extracted += len(contrast_params)

            # Add kinetic analysis if available
            if "KineticAnalysis" in metadata or "TimeIntensityCurve" in metadata:
                kinetic_params = self._extract_kinetic_parameters(dcm)
                metadata.update(kinetic_params)
                fields_extracted += len(kinetic_params)

            # Add lesion analysis if available
            if "LesionDetection" in metadata or "MassDetection" in metadata:
                lesion_params = self._extract_lesion_parameters(dcm)
                metadata.update(lesion_params)
                fields_extracted += len(lesion_params)

            # Add BI-RADS analysis if available
            if "BIRADS" in metadata or "BIRADSCategory" in metadata:
                birads_params = self._extract_birads_parameters(dcm)
                metadata.update(birads_params)
                fields_extracted += len(birads_params)

            # Add surgical planning if available
            if "SurgicalPlanning" in metadata or "TumorExtent" in metadata:
                surgical_params = self._extract_surgical_parameters(dcm)
                metadata.update(surgical_params)
                fields_extracted += len(surgical_params)

            # Add treatment monitoring if available
            if "NeoadjuvantChemotherapy" in metadata or "TreatmentResponse" in metadata:
                treatment_params = self._extract_treatment_parameters(dcm)
                metadata.update(treatment_params)
                fields_extracted += len(treatment_params)

            # Add warnings if this doesn't appear to be a breast MRI study
            if not is_breast_mri:
                warnings.append(
                    "This file may not be a breast MRI study. "
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
            logger.error(f"Breast MRI extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_anatomy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract breast anatomy parameters"""
        params = {}

        # Anatomy fields
        anatomy_fields = [
            "BreastSide",
            "BreastDensity",
            "BreastComposition",
            "BreastPosition",
            "BilateralImaging",
        ]

        for field in anatomy_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Anatomy_{field}"] = value

        return params

    def _extract_contrast_parameters(self, dcm) -> Dict[str, Any]:
        """Extract contrast administration parameters"""
        params = {}

        # Contrast fields
        contrast_fields = [
            "ContrastAgent",
            "ContrastVolume",
            "ContrastFlowRate",
            "DynamicContrastEnhanced",
            "ContrastPhases",
        ]

        for field in contrast_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Contrast_{field}"] = value

        return params

    def _extract_kinetic_parameters(self, dcm) -> Dict[str, Any]:
        """Extract kinetic analysis parameters"""
        params = {}

        # Kinetic fields
        kinetic_fields = [
            "KineticCurve",
            "InitialPhase",
            "DelayedPhase",
            "Washout",
            "TimeIntensityCurve",
            "PeakEnhancement",
        ]

        for field in kinetic_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Kinetic_{field}"] = value

        return params

    def _extract_lesion_parameters(self, dcm) -> Dict[str, Any]:
        """Extract lesion detection parameters"""
        params = {}

        # Lesion fields
        lesion_fields = [
            "LesionDetection",
            "LesionSize",
            "LesionLocation",
            "LesionMorphology",
            "MassShape",
            "MassMargins",
            "InternalEnhancement",
        ]

        for field in lesion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Lesion_{field}"] = value

        return params

    def _extract_birads_parameters(self, dcm) -> Dict[str, Any]:
        """Extract BI-RADS assessment parameters"""
        params = {}

        # BI-RADS fields
        birads_fields = [
            "BIRADS",
            "BIRADSCategory",
            "BIRADSAssessment",
            "MalignancyPotential",
            "ManagementRecommendation",
        ]

        for field in birads_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"BIRADS_{field}"] = value

        return params

    def _extract_surgical_parameters(self, dcm) -> Dict[str, Any]:
        """Extract surgical planning parameters"""
        params = {}

        # Surgical fields
        surgical_fields = [
            "TumorExtent",
            "Multifocality",
            "SkinInvolvement",
            "LymphNodeInvolvement",
            "TumorSize",
        ]

        for field in surgical_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Surgical_{field}"] = value

        return params

    def _extract_treatment_parameters(self, dcm) -> Dict[str, Any]:
        """Extract treatment monitoring parameters"""
        params = {}

        # Treatment fields
        treatment_fields = [
            "NeoadjuvantChemotherapy",
            "TreatmentResponse",
            "ResponseAssessment",
            "TumorShrinkage",
        ]

        for field in treatment_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Treatment_{field}"] = value

        return params

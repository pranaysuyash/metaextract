"""
CT Colonography DICOM Extension
Implements specialized metadata extraction for CT colonography and virtual colonoscopy studies
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


class CTColonographyExtension(DICOMExtensionBase):
    """
    CT Colonography metadata extraction.

    Extracts specialized CT colonography-related DICOM tags including:
    - Colon examination and preparation parameters
    - Insufflation and distension data
    - Patient positioning and scanning protocols
    - Polyp detection and measurement
    - Virtual colonoscopy navigation
    - CAD (Computer-Aided Detection) results
    - 2D and 3D rendering parameters
    - Colorectal screening findings
    """

    SPECIALTY = "ct_colonography"
    FIELD_COUNT = 65
    REFERENCE = "DICOM PS3.3 (CT Colonography)"
    DESCRIPTION = "CT Colonography specialized metadata extraction"
    VERSION = "1.0.0"

    # CT colonography field definitions
    CT_COLONOGRAPHY_FIELDS = [
        # Examination preparation
        "BowelPreparation",
        "BowelPreparationQuality",
        "BowelPreparationAgent",
        "FecalTagging",
        "FecalTaggingAgent",
        "FecalTaggingQuality",
        "ColonicCleansingMethod",
        "PreparationRegimen",
        "PreparationCompliance",
        "DietaryPreparation",
        "LaxativeAgent",
        "ContrastAgent",
        "ContrastAgentAmount",

        # Insufflation and distension
        "InsufflationAgent",
        "InsufflationMethod",
        "InsufflationVolume",
        "InsufflationPressure",
        "InsufflationQuality",
        "ColonicDistension",
        "ColonicDistensionQuality",
        "DistensionScore",
        "LuminalDistension",
        "ColonicCollapse",
        "GasDistension",
        "FluidLevel",

        # Patient positioning and scanning
        "PatientPosition",
        "ScanningPositions",
        "SupineScan",
        "ProneScan",
        "DecubitusScan",
        "ScanProtocol",
        "ScanningRange",
        "Coverage",
        "ScanningPhase",
        "ContrastPhase",
        "ColonCoverage",
        "SegmentalCoverage",

        # Colon segments and anatomy
        "ColonSegment",
        "ColonSegmentSequence",
        "Ceceum",
        "AscendingColon",
        "TransverseColon",
        "DescendingColon",
        "SigmoidColon",
        "Rectum",
        "AnatomyIdentification",
        "AnatomicRegion",
        "HaustralFolds",

        # Polyp detection and characterization
        "PolypDetection",
        "PolypSequence",
        "PolypCount",
        "PolypSize",
        "PolypLocation",
        "PolypMorphology",
        "PolypShape",
        "PolypSurface",
        "PolypTexture",
        "PolypDensity",
        "PolypEnhancement",
        "PolypType",
        "PolypHistology",
        "PolypRisk",
        "PolypMeasurementMethod",

        # Virtual colonoscopy navigation
        "VirtualColonoscopy",
        "NavigationMethod",
        "ViewingAngle",
        "FlyThroughPath",
        "EndoluminalView",
        "NavigationSpeed",
        "CameraPosition",
        "ViewDirection",
        "FieldOfView",
        "Perspective",

        # CAD results
        "CadPolypDetection",
        "CadPolypSequence",
        "CadPolypCount",
        "CadPolypConfidence",
        "CadAlgorithm",
        "CadAlgorithmVersion",
        "CadSensitivity",
        "CadFalsePositiveRate",
        "CadFindings",
        "CadDetectionMethod",
        "CadPerformance",

        # 2D and 3D rendering
        "RenderingMethod",
        "RenderingAlgorithm",
        "3DRendering",
        "2DDisplay",
        "VolumeRendering",
        "SurfaceRendering",
        "Shading",
        "Lighting",
        "Opacity",
        "TransferFunction",
        "WindowLevel",
        "WindowWidth",
        "ViewProjection",

        # Findings and measurements
        "ColonicFinding",
        "ColonicPathology",
        "MassDetection",
        "MassCharacterization",
        "WallThickness",
        "WallEnhancement",
        "LumenDiameter",
        "StrictureDetection",
        "Diverticulosis",
        "Diverticulitis",
        "Colitis",
        "TumorDetection",
        "TumorStaging",

        # Quality and technical parameters
        "ImageQuality",
        "MotionArtifact",
        "BeamHardening",
        "NoiseLevel",
        "SpatialResolution",
        "ContrastResolution",
        "ScanParameters",
        "ReconstructionAlgorithm",
        "SliceThickness",
        "ReconstructionInterval",

        # Screening and reporting
        "ScreeningIndication",
        "ScreeningGuidelines",
        "RiskFactors",
        "FamilyHistory",
        "PreviousFindings",
        "Recommendation",
        "FollowUpInterval",
        "ReportingStandard",
        "ExaminationCompleteness",
        "ExaminationQuality",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of CT colonography-specific DICOM field names"""
        return self.CT_COLONOGRAPHY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract CT colonography-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing CT colonography metadata extraction results
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

            # Detect if this is a CT colonography study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_ctc = (
                modality == "CT" and (
                    "colonography" in series_desc or "colonography" in study_desc or
                    "virtual colonoscopy" in series_desc or "virtual colonoscopy" in study_desc or
                    "ctc" in series_desc or "ctc" in study_desc or
                    "colon" in series_desc and "screening" in study_desc or
                    "polyp" in series_desc or "polyp" in study_desc
                )
            )

            metadata["is_ct_colonography_study"] = is_ctc
            metadata["modality"] = modality

            # Extract CT colonography-specific fields
            fields_extracted = 0

            for field in self.CT_COLONOGRAPHY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add preparation analysis if available
            if "BowelPreparation" in metadata or "FecalTagging" in metadata:
                preparation_params = self._extract_preparation_parameters(dcm)
                metadata.update(preparation_params)
                fields_extracted += len(preparation_params)

            # Add insufflation analysis if available
            if "InsufflationAgent" in metadata or "ColonicDistension" in metadata:
                insufflation_params = self._extract_insufflation_parameters(dcm)
                metadata.update(insufflation_params)
                fields_extracted += len(insufflation_params)

            # Add polyp analysis if available
            if "PolypDetection" in metadata or "PolypSequence" in metadata:
                polyp_params = self._extract_polyp_parameters(dcm)
                metadata.update(polyp_params)
                fields_extracted += len(polyp_params)

            # Add virtual colonoscopy analysis if available
            if "VirtualColonoscopy" in metadata or "NavigationMethod" in metadata:
                virtual_params = self._extract_virtual_colonoscopy_parameters(dcm)
                metadata.update(virtual_params)
                fields_extracted += len(virtual_params)

            # Add CAD analysis if available
            if "CadPolypDetection" in metadata or "CadPolypSequence" in metadata:
                cad_params = self._extract_cad_parameters(dcm)
                metadata.update(cad_params)
                fields_extracted += len(cad_params)

            # Add findings analysis if available
            if "ColonicFinding" in metadata or "ColonicPathology" in metadata:
                findings_params = self._extract_findings_parameters(dcm)
                metadata.update(findings_params)
                fields_extracted += len(findings_params)

            # Add warnings if this doesn't appear to be a CT colonography study
            if not is_ctc:
                warnings.append(
                    "This file may not be a CT colonography study. "
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
            logger.error(f"CT colonography extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_preparation_parameters(self, dcm) -> Dict[str, Any]:
        """Extract bowel preparation parameters"""
        params = {}

        # Preparation fields
        preparation_fields = [
            "BowelPreparation",
            "BowelPreparationQuality",
            "FecalTagging",
            "FecalTaggingAgent",
            "ColonicCleansingMethod",
            "PreparationRegimen",
            "LaxativeAgent",
        ]

        for field in preparation_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Preparation_{field}"] = value

        return params

    def _extract_insufflation_parameters(self, dcm) -> Dict[str, Any]:
        """Extract insufflation and distension parameters"""
        params = {}

        # Insufflation fields
        insufflation_fields = [
            "InsufflationAgent",
            "InsufflationMethod",
            "InsufflationVolume",
            "ColonicDistension",
            "ColonicDistensionQuality",
            "GasDistension",
        ]

        for field in insufflation_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Insufflation_{field}"] = value

        return params

    def _extract_polyp_parameters(self, dcm) -> Dict[str, Any]:
        """Extract polyp detection parameters"""
        params = {}

        # Polyp fields
        polyp_fields = [
            "PolypDetection",
            "PolypCount",
            "PolypSize",
            "PolypLocation",
            "PolypMorphology",
            "PolypShape",
            "PolypType",
            "PolypRisk",
        ]

        for field in polyp_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Polyp_{field}"] = value

        return params

    def _extract_virtual_colonoscopy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract virtual colonoscopy parameters"""
        params = {}

        # Virtual colonoscopy fields
        virtual_fields = [
            "VirtualColonoscopy",
            "NavigationMethod",
            "ViewingAngle",
            "FlyThroughPath",
            "EndoluminalView",
            "3DRendering",
        ]

        for field in virtual_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Virtual_{field}"] = value

        return params

    def _extract_cad_parameters(self, dcm) -> Dict[str, Any]:
        """Extract CAD detection parameters"""
        params = {}

        # CAD fields
        cad_fields = [
            "CadPolypDetection",
            "CadPolypCount",
            "CadPolypConfidence",
            "CadAlgorithm",
            "CadSensitivity",
            "CadFindings",
        ]

        for field in cad_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"CAD_{field}"] = value

        return params

    def _extract_findings_parameters(self, dcm) -> Dict[str, Any]:
        """Extract findings and pathology parameters"""
        params = {}

        # Findings fields
        findings_fields = [
            "ColonicFinding",
            "ColonicPathology",
            "MassDetection",
            "WallThickness",
            "StrictureDetection",
            "Diverticulosis",
            "Colitis",
            "TumorDetection",
        ]

        for field in findings_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Finding_{field}"] = value

        return params

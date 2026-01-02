"""
Dental DICOM Extension
Implements specialized metadata extraction for dental and maxillofacial imaging studies
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


class DentalExtension(DICOMExtensionBase):
    """
    Dental metadata extraction.

    Extracts specialized dental-related DICOM tags including:
    - Dental imaging parameters and modalities
    - Tooth identification and numbering systems
    - Oral and maxillofacial anatomy
    - Dental restoration and implant data
    - Orthodontic assessment parameters
    - Cephalometric analysis
    - TMJ (Temporomandibular Joint) imaging
    - Periodontal assessment
    """

    SPECIALTY = "dental"
    FIELD_COUNT = 58
    REFERENCE = "DICOM PS3.3 (Dental)"
    DESCRIPTION = "Dental specialized metadata extraction"
    VERSION = "1.0.0"

    # Dental field definitions
    DENTAL_FIELDS = [
        # Dental imaging parameters
        "DentalImagingType",
        "DentalAcquisitionDevice",
        "DentalRadiographyType",
        "IntraoralRadiography",
        "ExtraoralRadiography",
        "ConeBeamCT",
        "DigitalRadiography",
        "FilmRadiography",
        "PanoramicRadiography",
        "CephalometricRadiography",
        "BitewingRadiography",
        "PeriapicalRadiography",
        "OcclusalRadiography",

        # Tooth identification systems
        "ToothIdentificationSystem",
        "UniversalNumberingSystem",
        "FDINotation",
        "PalmerNotation",
        "ToothNumber",
        "ToothRegion",
        "ToothQuadrant",
        "ToothArch",
        "ToothSequence",
        "ToothLabel",
        "ToothDescription",

        # Dental anatomy and structures
        "ToothType",
        "Incisor",
        "Canine",
        "Premolar",
        "Molar",
        "PrimaryTooth",
        "PermanentTooth",
        "ToothSurface",
        "OcclusalSurface",
        "MesialSurface",
        "DistalSurface",
        "BuccalSurface",
        "LingualSurface",
        "LabialSurface",
        "PalatalSurface",

        # Dental pathology and findings
        "DentalCaries",
        "CariesDetection",
        "CariesDepth",
        "CariesActivity",
        "DentalRestoration",
        "RestorationType",
        "RestorationMaterial",
        "RestorationQuality",
        "DentalImplant",
        "ImplantType",
        "ImplantMaterial",
        "ImplantPosition",
        "ImplantLength",
        "ImplantDiameter",
        "AbutmentType",

        # Periodontal assessment
        "PeriodontalStatus",
        "PeriodontalPocket",
        "PocketDepth",
        "ClinicalAttachmentLevel",
        "GingivalRecession",
        "GingivalInflammation",
        "BoneLevel",
        "AlveolarBoneLoss",
        "PeriodontalMembrane",
        "LaminaDura",

        # Orthodontic assessment
        "OrthodonticAssessment",
        "Malocclusion",
        "MalocclusionClass",
        "Overjet",
        "Overbite",
        "Crowding",
        "Spacing",
        "ToothRotation",
        "ToothDisplacement",
        "MidlineDeviation",
        "ArchForm",
        "ArchLength",

        # Cephalometric analysis
        "CephalometricAnalysis",
        "CephalometricPoints",
        "SellaPoint",
        "NasionPoint",
        "PointA",
        "PointB",
        "GonionPoint",
        "MentonPoint",
        "ANS",
        "PNS",
        "CranialBaseAngle",
        "MaxillaryPosition",
        "MandibularPosition",
        "FacialPattern",
        "GrowthPattern",

        # TMJ imaging
        "TMJImaging",
        "TMJLeft",
        "TMJRight",
        "CondylePosition",
        "CondylarHead",
        "GlenoidFossa",
        "ArticularDisc",
        "JointSpace",
        "MandibularMovement",
        "MouthOpening",
        "MouthPosition",
        "OpenPosition",
        "ClosedPosition",

        # Maxillofacial anatomy
        "Maxilla",
        "Mandible",
        "MaxillarySinus",
        "SinusPathology",
        "NasalCavity",
        "Zygoma",
        "Orbit",
        "Nasopharynx",
        "Oropharynx",
        "SoftTissue",
        "HardPalate",
        "SoftPalate",

        # Image acquisition parameters
        "FieldOfView",
        "VoxelSize",
        "ReconstructionInterval",
        "ExposureParameters",
        "kV",
        "mA",
        "ExposureTime",
        "AcquisitionAngle",
        "RotationStep",
        "ScanningTime",
        "PatientPosition",

        # Quality and artifacts
        "ImageQuality",
        "MotionArtifact",
        "BeamHardening",
        "MetalArtifact",
        "Scatter",
        "NoiseLevel",
        "Contrast",

        # Treatment planning
        "TreatmentPlan",
        "OrthodonticTreatment",
        "ImplantPlanning",
        "OralSurgeryPlanning",
        "EndodonticTreatment",
        "PeriodontalTreatment",
        "RestorativePlanning",
        "ProsthodonticPlanning",
        "DigitalSmileDesign",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of dental-specific DICOM field names"""
        return self.DENTAL_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract dental-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing dental metadata extraction results
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

            # Detect if this is a dental study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_dental = (
                "dental" in series_desc or "dental" in study_desc or
                "tooth" in series_desc or "tooth" in study_desc or
                "orthodontic" in series_desc or "orthodontic" in study_desc or
                "cephalometric" in series_desc or "cephalometric" in study_desc or
                "panoramic" in series_desc or "panoramic" in study_desc or
                "cbct" in series_desc or "cbct" in study_desc or
                "maxillofacial" in series_desc or "maxillofacial" in study_desc or
                "tmj" in series_desc or "tmj" in study_desc or
                "implant" in series_desc and "dental" in study_desc
            )

            metadata["is_dental_study"] = is_dental
            metadata["modality"] = modality

            # Extract dental-specific fields
            fields_extracted = 0

            for field in self.DENTAL_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add imaging type analysis if available
            if "DentalImagingType" in metadata or "ConeBeamCT" in metadata:
                imaging_params = self._extract_imaging_parameters(dcm)
                metadata.update(imaging_params)
                fields_extracted += len(imaging_params)

            # Add tooth identification analysis if available
            if "ToothNumber" in metadata or "ToothSequence" in metadata:
                tooth_params = self._extract_tooth_parameters(dcm)
                metadata.update(tooth_params)
                fields_extracted += len(tooth_params)

            # Add pathology analysis if available
            if "DentalCaries" in metadata or "DentalRestoration" in metadata:
                pathology_params = self._extract_pathology_parameters(dcm)
                metadata.update(pathology_params)
                fields_extracted += len(pathology_params)

            # Add orthodontic analysis if available
            if "OrthodonticAssessment" in metadata or "Malocclusion" in metadata:
                orthodontic_params = self._extract_orthodontic_parameters(dcm)
                metadata.update(orthodontic_params)
                fields_extracted += len(orthodontic_params)

            # Add cephalometric analysis if available
            if "CephalometricAnalysis" in metadata or "SellaPoint" in metadata:
                cephalometric_params = self._extract_cephalometric_parameters(dcm)
                metadata.update(cephalometric_params)
                fields_extracted += len(cephalometric_params)

            # Add TMJ analysis if available
            if "TMJImaging" in metadata or "CondylePosition" in metadata:
                tmj_params = self._extract_tmj_parameters(dcm)
                metadata.update(tmj_params)
                fields_extracted += len(tmj_params)

            # Add warnings if this doesn't appear to be a dental study
            if not is_dental:
                warnings.append(
                    "This file may not be a dental study. "
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
            logger.error(f"Dental extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_imaging_parameters(self, dcm) -> Dict[str, Any]:
        """Extract dental imaging parameters"""
        params = {}

        # Imaging fields
        imaging_fields = [
            "DentalImagingType",
            "ConeBeamCT",
            "PanoramicRadiography",
            "CephalometricRadiography",
            "IntraoralRadiography",
            "FieldOfView",
            "VoxelSize",
        ]

        for field in imaging_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Imaging_{field}"] = value

        return params

    def _extract_tooth_parameters(self, dcm) -> Dict[str, Any]:
        """Extract tooth identification parameters"""
        params = {}

        # Tooth fields
        tooth_fields = [
            "ToothNumber",
            "ToothType",
            "ToothRegion",
            "ToothArch",
            "ToothQuadrant",
            "ToothSurface",
        ]

        for field in tooth_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Tooth_{field}"] = value

        return params

    def _extract_pathology_parameters(self, dcm) -> Dict[str, Any]:
        """Extract dental pathology parameters"""
        params = {}

        # Pathology fields
        pathology_fields = [
            "DentalCaries",
            "CariesDetection",
            "DentalRestoration",
            "RestorationType",
            "DentalImplant",
            "ImplantType",
            "PeriodontalStatus",
        ]

        for field in pathology_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Pathology_{field}"] = value

        return params

    def _extract_orthodontic_parameters(self, dcm) -> Dict[str, Any]:
        """Extract orthodontic assessment parameters"""
        params = {}

        # Orthodontic fields
        orthodontic_fields = [
            "OrthodonticAssessment",
            "Malocclusion",
            "MalocclusionClass",
            "Overjet",
            "Overbite",
            "Crowding",
            "Spacing",
            "ArchForm",
        ]

        for field in orthodontic_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Orthodontic_{field}"] = value

        return params

    def _extract_cephalometric_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cephalometric analysis parameters"""
        params = {}

        # Cephalometric fields
        cephalometric_fields = [
            "CephalometricAnalysis",
            "SellaPoint",
            "NasionPoint",
            "PointA",
            "PointB",
            "CranialBaseAngle",
            "MaxillaryPosition",
            "MandibularPosition",
        ]

        for field in cephalometric_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Cephalometric_{field}"] = value

        return params

    def _extract_tmj_parameters(self, dcm) -> Dict[str, Any]:
        """Extract TMJ imaging parameters"""
        params = {}

        # TMJ fields
        tmj_fields = [
            "TMJImaging",
            "TMJLeft",
            "TMJRight",
            "CondylePosition",
            "JointSpace",
            "MandibularMovement",
            "MouthOpening",
        ]

        for field in tmj_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"TMJ_{field}"] = value

        return params

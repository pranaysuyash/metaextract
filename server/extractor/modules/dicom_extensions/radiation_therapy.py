"""
Radiation Therapy DICOM Extension
Implements specialized metadata extraction for radiation therapy and oncology treatments
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


class RadiationTherapyExtension(DICOMExtensionBase):
    """
    Radiation Therapy metadata extraction.

    Extracts specialized radiation therapy-related DICOM tags including:
    - Treatment planning and dose calculation parameters
    - Beam configuration and delivery data
    - Radiation dose distribution and volume histograms
    - Treatment machine and accessory information
    - Patient setup and positioning data
    - Image registration and fusion
    - Treatment session and delivery records
    - Quality assurance and verification
    """

    SPECIALTY = "radiation_therapy"
    FIELD_COUNT = 85
    REFERENCE = "DICOM PS3.3 (Radiation Therapy)"
    DESCRIPTION = "Radiation Therapy specialized metadata extraction"
    VERSION = "1.0.0"

    # Radiation therapy field definitions
    RT_FIELDS = [
        # Treatment planning
        "TreatmentPlanName",
        "TreatmentPlanDate",
        "TreatmentPlanTime",
        "TreatmentPlanLabel",
        "TreatmentPlanDescription",
        "PlanIntent",
        "PlanStatus",
        "TreatmentProtocol",
        "PrescriptionDescription",
        "TreatmentTerminationCode",

        # Dose information
        "DoseUnits",
        "DoseType",
        "DoseComment",
        "DoseSummationType",
        "DoseReferenceSequence",
        "DoseReferenceNumber",
        "DoseReferenceUID",
        "DoseReferenceDescription",
        "DoseReferencePointCoordinates",
        "DoseReferencePointType",
        "NominalBeamDose",
        "BeamDose",
        "BeamDoseSpecificationPoint",

        # Beam configuration
        "BeamName",
        "BeamType",
        "BeamDescription",
        "BeamNumber",
        "BeamSequence",
        "PrimaryDosimeterUnit",
        "SourceAxisDistance",
        "VirtualSourceAxisDistance",

        # Beam energy and quality
        "RadiationType",
        "RadiationBeamType",
        "HighDoseTechnique",
        "BeamEnergy",
        "BeamEnergyMode",
        "RadiationBeamWidth",
        "RadiationBeamHeight",

        # Beam shaping and modifiers
        "BeamLimitingDeviceSequence",
        "BeamLimitingDeviceLabel",
        "BeamLimitingDeviceType",
        "BeamLimitingDevicePosition",
        "BeamLimitingDeviceAngle",
        "AccessoryCode",
        "WedgeType",
        "WedgeAngle",
        "WedgeFactor",
        "WedgeOrientation",
        "WedgeID",
        "WedgeNumber",
        "CompensatorID",
        "CompensatorNumber",
        "CompensatorThickness",
        "CompensatorTraversed",

        # Beam delivery parameters
        "NumberOfWedges",
        "NumberOfCompensators",
        "NumberOfBoli",
        "NumberOfBlocks",
        "FinalCumulativeTimeWeight",
        "BeamWeight",
        "BeamMeterset",
        "ControlPointSequence",
        "NumberOfControlPoints",
        "GantryAngle",
        "GantryPitchAngle",
        "GantryRotationDirection",
        "BeamLimitingDeviceAngle",
        "PatientSupportAngle",
        "TableTopPitchAngle",
        "TableTopRollAngle",
        "TableTopLongitudinalPosition",
        "TableTopLateralPosition",
        "TableTopVerticalPosition",

        # Patient setup and positioning
        "PatientSetupNumber",
        "PatientSetupLabel",
        "PatientSetupDescription",
        "PatientPosition",
        "PatientSetupSequence",
        "FixationDeviceSequence",
        "FixationLabel",
        "FixationDescription",
        "FixationType",

        # Dose volume and distribution
        "DoseVolumeSequence",
        "DoseVolumeUID",
        "DoseVolumeLabel",
        "DoseVolumeDescription",
        "DoseVolumeGeometry",
        "DoseVolumeData",
        "DVHSequence",
        "DVHType",
        "DVHDoseScaling",
        "DVHVolumeUnits",
        "DVHNumberOfBins",
        "DVHData",
        "DVHMaximumDose",
        "DVHMinimumDose",
        "DVHMeanDose",
        "DVH prescribedDose",

        # Structure set and contours
        "StructureSetLabel",
        "StructureSetDate",
        "StructureSetTime",
        "StructureSetDescription",
        "StructureSetSequence",
        "StructureLabel",
        "StructureDescription",
        "StructureNumber",
        "StructureContourSequence",
        "ContourSequence",
        "ContourNumber",
        "ContourImageSequence",
        "ContourGeometricType",
        "ContourData",
        "ROIDescription",
        "ROINumber",
        "ROIGenerationAlgorithm",
        "ROIType",
        "ROIVolume",

        # Image registration and fusion
        "RegistrationSequence",
        "MatrixRegistrationSequence",
        "RegistrationType",
        "RegistrationMatrix",
        "RegistrationMatrixCodeSequence",
        "FusionSequence",
        "FusionLabel",
        "FusionDescription",
        "FusionTransform",
        "FusionPixelData",

        # Treatment session and delivery
        "TreatmentSession",
        "TreatmentSessionLabel",
        "TreatmentSessionDescription",
        "TreatmentDate",
        "TreatmentTime",
        "TreatmentTerminationStatus",
        "TreatmentStatus",
        "TreatmentOutcome",
        "TreatmentComments",

        # Treatment machine information
        "Manufacturer",
        "ManufacturerModelName",
        "DeviceSerialNumber",
        "SoftwareVersions",
        "TreatmentMachineSequence",
        "TreatmentMachineName",
        "TreatmentMachineType",
        "TreatmentMachineDescription",

        # Quality assurance and verification
        "QAProcedure",
        "QAProcedureDescription",
        "QAProcedureCodeSequence",
        "QAIndicator",
        "QAIndicatorDescription",
        "QAIndicatorValue",
        "VerificationSequence",
        "VerificationFlag",
        "VerificationDateTime",
        "VerificationResult",

        # Additional radiation therapy parameters
        "ReferencedRTPlanSequence",
        "ReferencedRTStructureSetSequence",
        "ReferencedRTDoseSequence",
        "ReferencedTreatmentRecordSequence",
        "ApprovedPlanSequence",
        "ApprovalStatus",
        "ApprovalDate",
        "ApprovalTime",
        "ApprovedBy",
        "TreatmentSites",
        "CurrentFractionNumber",
        "TotalNumberOfFractions",
        "FractionPattern",
        "FractionGroupSequence",
        "NumberOfFractionsPlanned",
        "BeamDosePointDepth",
        "BeamDosePointEquivalentDepth",
        "BeamDosePointSSD",
        "BeamDosePointSourceAxisDistance",
        "ScanMode",
        "KVP",
        "FocalSpots",
        "FilterMaterial",
        "FilterThickness",
        "ExposureTime",
        "XRayTubeCurrent",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of radiation therapy-specific DICOM field names"""
        return self.RT_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract radiation therapy-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing radiation therapy metadata extraction results
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

            # Detect if this is a radiation therapy study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_rt = (
                "rt" in modality.lower() or
                "radiation" in series_desc or "radiation" in study_desc or
                "therapy" in series_desc or "therapy" in study_desc or
                "plan" in series_desc or "plan" in study_desc or
                "dose" in series_desc or "dose" in study_desc or
                modality in ["RTPLAN", "RTDOSE", "RTSTRUCT", "RTIMAGE", "RTRECORD"]
            )

            metadata["is_radiation_therapy_study"] = is_rt
            metadata["modality"] = modality

            # Extract radiation therapy-specific fields
            fields_extracted = 0

            for field in self.RT_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add treatment planning analysis if available
            if "TreatmentPlanName" in metadata or "PlanIntent" in metadata:
                planning_params = self._extract_treatment_planning_parameters(dcm)
                metadata.update(planning_params)
                fields_extracted += len(planning_params)

            # Add beam configuration if available
            if "BeamSequence" in metadata or "BeamName" in metadata:
                beam_params = self._extract_beam_configuration_parameters(dcm)
                metadata.update(beam_params)
                fields_extracted += len(beam_params)

            # Add dose information if available
            if "DoseUnits" in metadata or "DoseVolumeSequence" in metadata:
                dose_params = self._extract_dose_parameters(dcm)
                metadata.update(dose_params)
                fields_extracted += len(dose_params)

            # Add patient setup if available
            if "PatientSetupSequence" in metadata or "PatientPosition" in metadata:
                setup_params = self._extract_patient_setup_parameters(dcm)
                metadata.update(setup_params)
                fields_extracted += len(setup_params)

            # Add structure analysis if available
            if "StructureSetSequence" in metadata or "ROIType" in metadata:
                structure_params = self._extract_structure_parameters(dcm)
                metadata.update(structure_params)
                fields_extracted += len(structure_params)

            # Add treatment delivery if available
            if "TreatmentSession" in metadata or "TreatmentDate" in metadata:
                delivery_params = self._extract_treatment_delivery_parameters(dcm)
                metadata.update(delivery_params)
                fields_extracted += len(delivery_params)

            # Add quality assurance if available
            if "QAProcedure" in metadata or "VerificationSequence" in metadata:
                qa_params = self._extract_quality_assurance_parameters(dcm)
                metadata.update(qa_params)
                fields_extracted += len(qa_params)

            # Add warnings if this doesn't appear to be a radiation therapy study
            if not is_rt:
                warnings.append(
                    "This file may not be a radiation therapy study. "
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
            logger.error(f"Radiation therapy extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_treatment_planning_parameters(self, dcm) -> Dict[str, Any]:
        """Extract treatment planning parameters"""
        params = {}

        # Treatment planning fields
        planning_fields = [
            "TreatmentPlanName",
            "TreatmentPlanDate",
            "PlanIntent",
            "PlanStatus",
            "TreatmentProtocol",
            "PrescriptionDescription",
        ]

        for field in planning_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Planning_{field}"] = value

        return params

    def _extract_beam_configuration_parameters(self, dcm) -> Dict[str, Any]:
        """Extract beam configuration parameters"""
        params = {}

        # Beam configuration fields
        beam_fields = [
            "BeamName",
            "BeamType",
            "BeamNumber",
            "RadiationType",
            "BeamEnergy",
            "BeamWeight",
            "GantryAngle",
            "BeamLimitingDeviceAngle",
            "PatientSupportAngle",
        ]

        for field in beam_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Beam_{field}"] = value

        return params

    def _extract_dose_parameters(self, dcm) -> Dict[str, Any]:
        """Extract dose parameters"""
        params = {}

        # Dose fields
        dose_fields = [
            "DoseUnits",
            "DoseType",
            "DoseSummationType",
            "BeamDose",
            "NominalBeamDose",
            "DoseVolumeLabel",
            "DVHMaximumDose",
            "DVHMinimumDose",
            "DVHMeanDose",
        ]

        for field in dose_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Dose_{field}"] = value

        return params

    def _extract_patient_setup_parameters(self, dcm) -> Dict[str, Any]:
        """Extract patient setup parameters"""
        params = {}

        # Patient setup fields
        setup_fields = [
            "PatientSetupNumber",
            "PatientSetupLabel",
            "PatientPosition",
            "FixationDeviceSequence",
            "FixationLabel",
            "FixationType",
        ]

        for field in setup_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Setup_{field}"] = value

        return params

    def _extract_structure_parameters(self, dcm) -> Dict[str, Any]:
        """Extract structure set parameters"""
        params = {}

        # Structure fields
        structure_fields = [
            "StructureSetLabel",
            "StructureLabel",
            "StructureNumber",
            "StructureDescription",
            "ROIType",
            "ROIVolume",
            "ROIDescription",
        ]

        for field in structure_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Structure_{field}"] = value

        return params

    def _extract_treatment_delivery_parameters(self, dcm) -> Dict[str, Any]:
        """Extract treatment delivery parameters"""
        params = {}

        # Treatment delivery fields
        delivery_fields = [
            "TreatmentSession",
            "TreatmentDate",
            "TreatmentTime",
            "TreatmentStatus",
            "TreatmentTerminationStatus",
            "CurrentFractionNumber",
            "TotalNumberOfFractions",
        ]

        for field in delivery_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Delivery_{field}"] = value

        return params

    def _extract_quality_assurance_parameters(self, dcm) -> Dict[str, Any]:
        """Extract quality assurance parameters"""
        params = {}

        # QA fields
        qa_fields = [
            "QAProcedure",
            "QAProcedureDescription",
            "QAIndicator",
            "QAIndicatorValue",
            "VerificationFlag",
            "VerificationResult",
        ]

        for field in qa_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"QA_{field}"] = value

        return params

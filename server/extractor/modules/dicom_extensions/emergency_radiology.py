"""
Emergency Radiology DICOM Extension
Implements specialized metadata extraction for emergency and trauma imaging studies
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


class EmergencyRadiologyExtension(DICOMExtensionBase):
    """
    Emergency Radiology metadata extraction.

    Extracts specialized emergency radiology-related DICOM tags including:
    - Trauma assessment and injury severity
    - Emergency protocol and triage information
    - Time-critical imaging parameters
    - Acute pathology detection
    - Injury scoring and classification
    - Emergency treatment guidance
    - Critical findings communication
    - Rapid imaging protocols
    """

    SPECIALTY = "emergency_radiology"
    FIELD_COUNT = 78
    REFERENCE = "DICOM PS3.3 (Emergency Radiology)"
    DESCRIPTION = "Emergency Radiology specialized metadata extraction"
    VERSION = "1.0.0"

    # Emergency radiology field definitions
    EMERGENCY_FIELDS = [
        # Emergency protocol
        "EmergencyExamination",
        "TraumaProtocol",
        "CodeTrauma",
        "RapidResponse",
        "TriageCategory",
        "EmergencyLevel",
        "Urgency",
        "TimeCritical",
        "StatExam",
        "ImmediateAction",
        "EmergencyActivation",

        # Time parameters
        "ExamStartTime",
        "ExamEndTime",
        "ExamDuration",
        "TimeToAcquisition",
        "TimeToPrelim",
        "TimeToFinal",
        "TurnaroundTime",
        "CriticalValueTime",
        "NotificationTime",
        "TreatmentTime",
        "DoorToScanTime",
        "ScanToDecisionTime",

        # Trauma assessment
        "TraumaAssessment",
        "InjurySeverity",
        "InjuryPattern",
        "MechanismOfInjury",
        "TraumaScore",
        "ISS",
        "InjurySeverityScore",
        "GCS",
        "GlasgowComaScale",
        "TraumaLevel",
        "LevelITrauma",
        "LevelIITrauma",
        "MultiSystemTrauma",
        "Polytrauma",

        # Acute brain emergencies
        "AcuteBrainEmergency",
        "IntracranialHemorrhage",
        "SubarachnoidHemorrhage",
        "SubduralHematoma",
        "EpiduralHematoma",
        "IntracerebralHemorrhage",
        "BrainContusion",
        "DiffuseAxonalInjury",
        "CerebralEdema",
        "Herniation",
        "MidlineShift",
        "MassEffect",
        "Stroke",
        "IschemicStroke",
        "HemorrhagicStroke",
        "LargeVesselOcclusion",

        # Spinal trauma
        "SpinalTrauma",
        "SpinalFracture",
        "SpinalCordInjury",
        "VertebralFracture",
        "CompressionFracture",
        "BurstFracture",
        "FractureDislocation",
        "SpinalStenosis",
        "CervicalSpine",
        "ThoracicSpine",
        "LumbarSpine",

        # Chest trauma
        "ChestTrauma",
        "Pneumothorax",
        "Hemothorax",
        "RibFracture",
        "FlailChest",
        "PulmonaryContusion",
        "AorticInjury",
        "CardiacContusion",
        "SternalFracture",
        "ClavicleFracture",
        "ScapulaFracture",

        # Abdominal trauma
        "AbdominalTrauma",
        "SolidOrganInjury",
        "LiverLaceration",
        "SplenicInjury",
        "RenalInjury",
        "HollowViscusInjury",
        "BowelPerforation",
        "MesentericInjury",
        "VascularInjury",
        "AbdominalCompartment",
        "FreeAir",
        "FreeFluid",
        "Hemoperitoneum",

        # Musculoskeletal trauma
        "MusculoskeletalTrauma",
        "FractureDetection",
        "FractureClassification",
        "LongBoneFracture",
        "PelvicFracture",
        "AcetabularFracture",
        "JointDislocation",
        "SoftTissueInjury",
        "VascularInjury",
        "CompartmentSyndrome",

        # Acute cardiovascular
        "AcuteCardiovascular",
        "AorticDissection",
        "AorticRupture",
        "PulmonaryEmbolism",
        "AcuteCoronarySyndrome",
        "MyocardialInfarction",
        "CardiacTamponade",
        "AneurysmRupture",
        "VascularEmergency",
        "EndOrganIschemia",

        # Acute abdominal emergencies
        "AcuteAbdomen",
        "Appendicitis",
        "Cholecystitis",
        "Pancreatitis",
        "BowelObstruction",
        "BowelPerforation",
        "Diverticulitis",
        "MesentericIschemia",
        "RupturedAneurysm",
        "EctopicPregnancy",
        "OvarianTorsion",
        "TesticularTorsion",

        # Critical findings
        "CriticalFinding",
        "UrgentFinding",
        "EmergencyFinding",
        "LifeThreatening",
        "RequireImmediateAction",
        "StatResult",
        "CriticalValue",
        "PanicValue",
        "AlertCriteria",
        "EscalationRequired",

        # Communication and reporting
        "CriticalResultNotification",
        "VerbalReport",
        "PreliminaryReport",
        "UrgentCommunication",
        "TreatingPhysician",
        "ReferringPhysician",
        "EmergencyDepartment",
        "EDContact",
        "TraumaTeam",
        "RapidResponseTeam",
        "CriticalCareTeam",

        # Additional emergency parameters
        "PatientStability",
        "HemodynamicStatus",
        "AirwayStatus",
        "BreathingStatus",
        "CirculationStatus",
        "NeurologicalStatus",
        "VitalSigns",
        "BloodPressure",
        "HeartRate",
        "OxygenSaturation",
        "RespiratoryRate",
        "Temperature",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of emergency radiology-specific DICOM field names"""
        return self.EMERGENCY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract emergency radiology-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing emergency radiology metadata extraction results
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

            # Detect if this is an emergency radiology study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_emergency = (
                "trauma" in series_desc or "trauma" in study_desc or
                "emergency" in series_desc or "emergency" in study_desc or
                "stat" in series_desc or "stat" in study_desc or
                "acute" in series_desc or "critical" in study_desc or
                "code" in series_desc or "triage" in study_desc or
                "rapid" in series_desc or "urgent" in study_desc
            )

            metadata["is_emergency_study"] = is_emergency
            metadata["modality"] = modality

            # Extract emergency radiology-specific fields
            fields_extracted = 0

            for field in self.EMERGENCY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add emergency protocol analysis if available
            if "EmergencyExamination" in metadata or "TraumaProtocol" in metadata:
                protocol_params = self._extract_protocol_parameters(dcm)
                metadata.update(protocol_params)
                fields_extracted += len(protocol_params)

            # Add trauma analysis if available
            if "TraumaAssessment" in metadata or "InjurySeverity" in metadata:
                trauma_params = self._extract_trauma_parameters(dcm)
                metadata.update(trauma_params)
                fields_extracted += len(trauma_params)

            # Add brain emergency analysis if available
            if "AcuteBrainEmergency" in metadata or "IntracranialHemorrhage" in metadata:
                brain_params = self._extract_brain_emergency_parameters(dcm)
                metadata.update(brain_params)
                fields_extracted += len(brain_params)

            # Add cardiovascular analysis if available
            if "AcuteCardiovascular" in metadata or "AorticDissection" in metadata:
                cardiovascular_params = self._extract_cardiovascular_parameters(dcm)
                metadata.update(cardiovascular_params)
                fields_extracted += len(cardiovascular_params)

            # Add abdominal emergency analysis if available
            if "AcuteAbdomen" in metadata or "Appendicitis" in metadata:
                abdominal_params = self._extract_abdominal_emergency_parameters(dcm)
                metadata.update(abdominal_params)
                fields_extracted += len(abdominal_params)

            # Add critical findings analysis if available
            if "CriticalFinding" in metadata or "UrgentFinding" in metadata:
                critical_params = self._extract_critical_findings_parameters(dcm)
                metadata.update(critical_params)
                fields_extracted += len(critical_params)

            # Add communication analysis if available
            if "CriticalResultNotification" in metadata or "VerbalReport" in metadata:
                communication_params = self._extract_communication_parameters(dcm)
                metadata.update(communication_params)
                fields_extracted += len(communication_params)

            # Add warnings if this doesn't appear to be an emergency study
            if not is_emergency:
                warnings.append(
                    "This file may not be an emergency radiology study. "
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
            logger.error(f"Emergency radiology extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_protocol_parameters(self, dcm) -> Dict[str, Any]:
        """Extract emergency protocol parameters"""
        params = {}

        # Protocol fields
        protocol_fields = [
            "EmergencyExamination",
            "TraumaProtocol",
            "TriageCategory",
            "EmergencyLevel",
            "TimeCritical",
            "DoorToScanTime",
        ]

        for field in protocol_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Protocol_{field}"] = value

        return params

    def _extract_trauma_parameters(self, dcm) -> Dict[str, Any]:
        """Extract trauma assessment parameters"""
        params = {}

        # Trauma fields
        trauma_fields = [
            "TraumaAssessment",
            "InjurySeverity",
            "MechanismOfInjury",
            "TraumaScore",
            "GlasgowComaScale",
            "MultiSystemTrauma",
        ]

        for field in trauma_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Trauma_{field}"] = value

        return params

    def _extract_brain_emergency_parameters(self, dcm) -> Dict[str, Any]:
        """Extract acute brain emergency parameters"""
        params = {}

        # Brain emergency fields
        brain_fields = [
            "AcuteBrainEmergency",
            "IntracranialHemorrhage",
            "SubarachnoidHemorrhage",
            "IschemicStroke",
            "MidlineShift",
        ]

        for field in brain_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"BrainEmergency_{field}"] = value

        return params

    def _extract_cardiovascular_parameters(self, dcm) -> Dict[str, Any]:
        """Extract acute cardiovascular parameters"""
        params = {}

        # Cardiovascular fields
        cardiovascular_fields = [
            "AcuteCardiovascular",
            "AorticDissection",
            "PulmonaryEmbolism",
            "MyocardialInfarction",
            "CardiacTamponade",
        ]

        for field in cardiovascular_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Cardiovascular_{field}"] = value

        return params

    def _extract_abdominal_emergency_parameters(self, dcm) -> Dict[str, Any]:
        """Extract acute abdominal emergency parameters"""
        params = {}

        # Abdominal emergency fields
        abdominal_fields = [
            "AcuteAbdomen",
            "Appendicitis",
            "Cholecystitis",
            "BowelObstruction",
            "MesentericIschemia",
        ]

        for field in abdominal_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"AbdominalEmergency_{field}"] = value

        return params

    def _extract_critical_findings_parameters(self, dcm) -> Dict[str, Any]:
        """Extract critical findings parameters"""
        params = {}

        # Critical findings fields
        critical_fields = [
            "CriticalFinding",
            "UrgentFinding",
            "LifeThreatening",
            "RequireImmediateAction",
            "CriticalValue",
        ]

        for field in critical_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Critical_{field}"] = value

        return params

    def _extract_communication_parameters(self, dcm) -> Dict[str, Any]:
        """Extract communication parameters"""
        params = {}

        # Communication fields
        communication_fields = [
            "CriticalResultNotification",
            "VerbalReport",
            "TreatingPhysician",
            "EmergencyDepartment",
            "TraumaTeam",
        ]

        for field in communication_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Communication_{field}"] = value

        return params

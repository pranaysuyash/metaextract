"""
Nuclear Medicine DICOM Extension
Implements specialized metadata extraction for nuclear medicine imaging studies
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


class NuclearMedicineExtension(DICOMExtensionBase):
    """
    Nuclear Medicine metadata extraction.

    Extracts specialized nuclear medicine-related DICOM tags including:
    - Radiopharmaceutical administration and dosage
    - Radionuclide information and properties
    - Imaging acquisition parameters
    - Quantification and calibration data
    - Uptake measurements and physiological parameters
    - Time activity curves and kinetic modeling
    - Quality control and calibration
    - Multi-modality fusion and registration
    """

    SPECIALTY = "nuclear_medicine"
    FIELD_COUNT = 78
    REFERENCE = "DICOM PS3.3 (Nuclear Medicine)"
    DESCRIPTION = "Nuclear Medicine specialized metadata extraction"
    VERSION = "1.0.0"

    # Nuclear medicine field definitions
    NM_FIELDS = [
        # Radiopharmaceutical administration
        "Radiopharmaceutical",
        "RadiopharmaceuticalRoute",
        "RadiopharmaceuticalVolume",
        "RadiopharmaceuticalStartTime",
        "RadiopharmaceuticalStopTime",
        "RadiopharmaceuticalTotalDose",
        "RadiopharmaceuticalSpecificActivity",
        "RadiopharmaceuticalStartDateTime",
        "RadiopharmaceuticalStopDateTime",
        "RadionuclideTotalDose",
        "RadionuclideHalfLife",
        "RadionuclidePositronFraction",
        "Radionuclide",
        "RadiopharmaceuticalCodeSequence",
        "RadiopharmaceuticalAgent",

        # Radionuclide properties
        "RadionuclideName",
        "RadionuclideCodeSequence",
        "RadionuclideNuclearReaction",
        "RadionuclideRadiation",
        "RadionuclidePhotonEnergy",
        "RadionuclideBranchingRatio",
        "RadionuclidePositronFraction",
        "RadionuclideHalfLife",
        "RadionuclideSpecificActivity",
        "RadionuclideAdministrationRoute",

        # Acquisition parameters
        "DetectionProcess",
        "DetectorGeometry",
        "CollimatorType",
        "CollimatorConfiguration",
        "ScatterFraction",
        "AttenuationCorrectionMethod",
        "DecayCorrection",
        "ReconstructionMethod",
        "ReconstructionAlgorithm",
        "AcquisitionType",
        "AcquisitionDuration",
        "AcquisitionStartTime",
        "AcquisitionStopTime",
        "AcquisitionTerminationCondition",
        "NumberOfFrames",
        "FrameTime",
        "FrameTimeVector",

        # Energy and detector information
        "EnergyWindowVector",
        "EnergyWindowLowerLimit",
        "EnergyWindowUpperLimit",
        "EnergyWindowName",
        "DetectorVector",
        "NumberOfDetectors",
        "DetectorSize",
        "DetectorMaterial",
        "DetectorEfficiency",
        "DeadTimeCorrection",
        "DeadTimeFactor",
        "PhotonEnergy",

        # Quantification and calibration
        "Units",
        "CountsSource",
        "CountsAccumulated",
        "CountsRate",
        "CalibrationFactor",
        "CalibrationDate",
        "CalibrationTime",
        "CalibrationDescription",
        "SensitivityFactor",
        "SensitivityCorrection",
        "GeometricEfficiency",
        "IntrinsicEfficiency",
        "ExtrinsicEfficiency",

        # Uptake measurements
        "Uptake",
        "UptakeUnits",
        "UptakeMeasurement",
        "StandardizedUptakeValue",
        "StandardizedUptakeValueBodyWeight",
        "StandardizedUptakeValueLeanBodyMass",
        "StandardizedUptakeValueBasis",
        "SUV",
        "SUVType",
        "BodyWeight",
        "LeanBodyMass",
        "BodySurfaceArea",

        # Time activity and kinetics
        "TimeActivityCurve",
        "TimeSlotVector",
        "TimeSlot",
        "ActivityPerSlice",
        "ActivityPerVolume",
        "ActivityConcentration",
        "ActivityUnits",
        "PhantomType",
        "ReferenceRegion",
        "KineticModel",
        "KineticModelParameters",
        "RateConstants",
        "CompartmentModel",

        # Image quality and corrections
        "ScatterCorrectionMethod",
        "AttenuationCorrectionSource",
        "DecayFactor",
        "PartialVolumeCorrection",
        "SpillOverRatio",
        "ContrastRecovery",
        "ImageQualityMetric",
        "NoiseLevel",
        "SignalToNoiseRatio",
        "BackgroundLevel",

        # Multi-modality and fusion
        "RegistrationSequence",
        "FusionMethod",
        "FusionModality",
        "FusionImageSequence",
        "FusionQuality",
        "AnatomicReferenceSequence",
        "CoRegistrationMatrix",
        "RegistrationAccuracy",

        # Gating and motion
        "GatingInformation",
        "GatingType",
        "TriggerTime",
        "TriggerDelay",
        "RRInterval",
        "RespiratoryGating",
        "CardiacGating",
        "MotionCorrection",
        "MotionVector",

        # Additional nuclear medicine parameters
        "InjectRadioactivity",
        "InjectTime",
        "InjectDateTime",
        "InjectDepth",
        "InjectSite",
        "InjectComment",
        "InjectorType",
        "InjectorManufacturer",
        "InjectDoseCalibrationFactor",
        "RadionuclideSequence",
        "RadiopharmaceuticalSequence",
        "CalibrationSequence",
        "DetectedCountRate",
        "PromptCountRate",
        "RandomCountRate",
        "SingleCountRate",
        "MultipleCountRate",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of nuclear medicine-specific DICOM field names"""
        return self.NM_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract nuclear medicine-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing nuclear medicine metadata extraction results
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

            # Detect if this is a nuclear medicine study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_nm = (
                modality in ["NM", "PT"] or
                "nuclear" in series_desc or "nuclear" in study_desc or
                "spect" in series_desc or "spect" in study_desc or
                "pet" in series_desc or "pet" in study_desc or
                "radionuclide" in series_desc or "radionuclide" in study_desc or
                "radiopharmaceutical" in series_desc or "radiopharmaceutical" in study_desc or
                "uptake" in series_desc or "uptake" in study_desc
            )

            metadata["is_nuclear_medicine_study"] = is_nm
            metadata["modality"] = modality

            # Extract nuclear medicine-specific fields
            fields_extracted = 0

            for field in self.NM_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add radiopharmaceutical analysis if available
            if "Radiopharmaceutical" in metadata or "Radionuclide" in metadata:
                radiopharma_params = self._extract_radiopharmaceutical_parameters(dcm)
                metadata.update(radiopharma_params)
                fields_extracted += len(radiopharma_params)

            # Add acquisition analysis if available
            if "AcquisitionType" in metadata or "AcquisitionDuration" in metadata:
                acquisition_params = self._extract_acquisition_parameters(dcm)
                metadata.update(acquisition_params)
                fields_extracted += len(acquisition_params)

            # Add quantification analysis if available
            if "CalibrationFactor" in metadata or "StandardizedUptakeValue" in metadata:
                quantification_params = self._extract_quantification_parameters(dcm)
                metadata.update(quantification_params)
                fields_extracted += len(quantification_params)

            # Add uptake analysis if available
            if "Uptake" in metadata or "SUV" in metadata:
                uptake_params = self._extract_uptake_parameters(dcm)
                metadata.update(uptake_params)
                fields_extracted += len(uptake_params)

            # Add time activity analysis if available
            if "TimeActivityCurve" in metadata or "TimeSlot" in metadata:
                time_activity_params = self._extract_time_activity_parameters(dcm)
                metadata.update(time_activity_params)
                fields_extracted += len(time_activity_params)

            # Add quality analysis if available
            if "ScatterCorrectionMethod" in metadata or "ImageQualityMetric" in metadata:
                quality_params = self._extract_quality_parameters(dcm)
                metadata.update(quality_params)
                fields_extracted += len(quality_params)

            # Add warnings if this doesn't appear to be a nuclear medicine study
            if not is_nm:
                warnings.append(
                    "This file may not be a nuclear medicine study. "
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
            logger.error(f"Nuclear medicine extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_radiopharmaceutical_parameters(self, dcm) -> Dict[str, Any]:
        """Extract radiopharmaceutical parameters"""
        params = {}

        # Radiopharmaceutical fields
        radiopharma_fields = [
            "Radiopharmaceutical",
            "RadiopharmaceuticalRoute",
            "RadiopharmaceuticalTotalDose",
            "RadiopharmaceuticalStartTime",
            "Radionuclide",
            "RadionuclideHalfLife",
            "RadiopharmaceuticalSpecificActivity",
        ]

        for field in radiopharma_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Radiopharma_{field}"] = value

        return params

    def _extract_acquisition_parameters(self, dcm) -> Dict[str, Any]:
        """Extract acquisition parameters"""
        params = {}

        # Acquisition fields
        acquisition_fields = [
            "AcquisitionType",
            "AcquisitionDuration",
            "AcquisitionStartTime",
            "DetectionProcess",
            "CollimatorType",
            "NumberOfFrames",
            "FrameTime",
        ]

        for field in acquisition_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Acquisition_{field}"] = value

        return params

    def _extract_quantification_parameters(self, dcm) -> Dict[str, Any]:
        """Extract quantification and calibration parameters"""
        params = {}

        # Quantification fields
        quantification_fields = [
            "CalibrationFactor",
            "CalibrationDate",
            "SensitivityFactor",
            "Units",
            "CountsAccumulated",
            "CountsRate",
            "GeometricEfficiency",
        ]

        for field in quantification_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Quantification_{field}"] = value

        return params

    def _extract_uptake_parameters(self, dcm) -> Dict[str, Any]:
        """Extract uptake measurement parameters"""
        params = {}

        # Uptake fields
        uptake_fields = [
            "Uptake",
            "UptakeUnits",
            "StandardizedUptakeValue",
            "StandardizedUptakeValueBodyWeight",
            "StandardizedUptakeValueLeanBodyMass",
            "SUV",
            "SUVType",
            "BodyWeight",
        ]

        for field in uptake_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Uptake_{field}"] = value

        return params

    def _extract_time_activity_parameters(self, dcm) -> Dict[str, Any]:
        """Extract time activity curve parameters"""
        params = {}

        # Time activity fields
        time_activity_fields = [
            "TimeActivityCurve",
            "TimeSlot",
            "ActivityPerSlice",
            "ActivityConcentration",
            "ActivityUnits",
            "KineticModel",
            "RateConstants",
        ]

        for field in time_activity_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"TimeActivity_{field}"] = value

        return params

    def _extract_quality_parameters(self, dcm) -> Dict[str, Any]:
        """Extract quality control and correction parameters"""
        params = {}

        # Quality fields
        quality_fields = [
            "ScatterCorrectionMethod",
            "AttenuationCorrectionMethod",
            "DecayCorrection",
            "PartialVolumeCorrection",
            "ImageQualityMetric",
            "SignalToNoiseRatio",
        ]

        for field in quality_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Quality_{field}"] = value

        return params

"""
PET and Nuclear Medicine DICOM Extension
Implements specialized metadata extraction for PET and nuclear medicine studies
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


class PETNuclearMedicineExtension(DICOMExtensionBase):
    """
    PET and Nuclear Medicine metadata extraction.

    Extracts specialized PET/NM-related DICOM tags including:
    - Radiopharmaceutical information and tracking
    - Decay correction and calibration factors
    - PET reconstruction parameters
    - Uptake values and quantitative metrics
    - Dose administration and timing
    - Stress test parameters for cardiac PET
    """

    SPECIALTY = "pet_nuclear_medicine"
    FIELD_COUNT = 98
    REFERENCE = "DICOM PS3.3 (PET/NM)"
    DESCRIPTION = "PET and Nuclear Medicine specialized metadata extraction"
    VERSION = "1.0.0"

    # PET/Nuclear Medicine field definitions
    PET_NUCLEAR_FIELDS = [
        # Radiopharmaceutical information sequence
        "RadiopharmaceuticalInformationSequence",
        "RadiopharmaceuticalStartDateTime",
        "RadiopharmaceuticalStopDateTime",
        "RadionuclideSequence",
        "RadionuclideCodeSequence",
        "RadionuclideHalfLife",
        "RadionuclideTotalDose",
        "RadionuclideRoute",
        "RadiopharmaceuticalVolume",
        "RadiopharmaceuticalConcentration",
        "RadiopharmaceuticalSpecificActivity",
        "RadiopharmaceuticalStartTimeOffset",
        "RadiopharmaceuticalStopTimeOffset",

        # Calibration data
        "CalibrationDataSequence",
        "DecayCorrectionDateTime",
        "DecayFactor",
        "DoseCalibrationFactor",
        "DeadTimeFactor",
        "DeadTimeCorrectionCodeSequence",
        "CrossCorrectionFactor",
        "SensitivityFactor",
        "ScatterFractionFactor",
        "RandomsFractionFactor",

        # Acquisition flow
        "AcquisitionFlowIdentifierSequence",
        "ReconstructionSequence",
        "ReferencesSegment",
        "SeriesBasedSegment",
        "ReconstructedImageType",

        # PET-specific parameters
        "TimeOfFlightInformation",
        "ReconstructionType",
        "DecayMethod",
        "AttenuationCorrectionMethod",
        "DecayCorrectedUnits",
        "ReconstructionStatus",
        "RandomCorrectionMethod",
        "ScatterCorrectionMethod",
        "AxialComfortCorrection",
        "SlicePositionVector",

        # Isotope information
        "IsotopeName",
        "IsotopeNumber",
        "IsotopeHalfLife",
        "EnergyWindowNumber",
        "EnergyWindowLowerLimit",
        "EnergyWindowUpperLimit",

        # Radiopharmaceutical details
        "RadiopharmaceuticalName",
        "RadiopharmaceuticalCodeSequence",
        "AdministrationRouteCodeSequence",
        "AdministrationRouteName",
        "AdministrationRouteSequence",
        "AdministrationRouteStartDateTime",
        "AdministrationRouteStopDateTime",
        "AdministrationRouteTotalDose",
        "AdministrationRouteTotalDoseUnit",
        "AdministrationRouteTotalDoseDescription",

        # Pharmacological stress (cardiac PET)
        "PharmacologicallyInducedStress",
        "StressAgent",
        "StressAgentCodeSequence",
        "StressAgentName",
        "StressAgentConcentration",
        "StressAgentVolume",
        "StressAgentNumber",
        "PreInjectionTime",
        "PostInjectionTime",
        "InjectionDuration",

        # Vital signs during stress
        "StartMeanArterialPressure",
        "EndMeanArterialPressure",
        "StartCardiacBloodPressure",
        "EndCardiacBloodPressure",
        "StartHeartRate",
        "EndHeartRate",
        "StartRespiratoryRate",
        "EndRespiratoryRate",

        # Procedure tracking
        "ProcedureStepState",
        "PerformedSeriesSequence",
        "RadiopharmaceuticalAgent",
        "BolusAgent",
        "BolusAgentCodeSequence",
        "BolusAgentName",
        "BolusVolume",
        "BolusStartTimeRelativeToInjection",
        "BolusDuration",

        # Activity measurements
        "InjectedActivity",
        "InjectedActivityDateTime",
        "InjectedActivityUnit",
        "InjectedActivityConcentration",
        "InjectedVolume",
        "ActivityConcentrationUnit",
        "PharmacologicalStressAgent",

        # PET frame acquisition
        "PETFrameAcquisitionSequence",
        "PETFramePositionSequence",
        "PETReconstructionSequence",
        "PETFrameType",
        "DecayTime",
        "CountsAccumulated",
        "DoseCalibrationFactor",
        "PromptCountsAccumulated",
        "RandomCountsAccumulated",
        "ScatterFractionFactor",
        "DeadTimeFactor",
        "DeadTimeCorrectionFlag",

        # Image correction types
        "PromptGammaRaySensitivity",
        "RandomCorrectionFactor",
        "DecayCorrectedImageType",
        "AttenuationCorrectedImageType",

        # Quantitative PET parameters
        "StandardUptakeValue",
        "SUVNormalizedTo",
        "SUVReferenceBodyWeight",
        "SUVReferenceLeanBodyMass",
        "SUVReferenceBodySurfaceArea",
        "BodyMass",
        "LeanBodyMass",
        "BodySurfaceArea",

        # PET geometry and positioning
        "ApexPosition",
        "BasePosition",
        "TableOrientation",
        "DetectorGeometry",
        "DetectorElementSize",
        "CrystalPackingFraction",

        # Image quality metrics
        "SignalToNoiseRatio",
        "ContrastToNoiseRatio",
        "NoiseStandardDeviation",
        "NoiseMeanValue",
        "ImageUniformity",
        "SpatialResolution",

        # Additional nuclear medicine parameters
        "NumberOfEnergyWindows",
        "EnergyWindowInformationSequence",
        "NumberOfDetectors",
        "DetectorDimensions",
        "GantryTilt",
        "GantryRotation",
        "TableSpeed",
        "TableFeed",

        # Quality control
        "QualityControlDate",
        "QualityControlTime",
        "QualityControlDescription",
        "CalibrationDate",
        "CalibrationTime",
        "CalibrationDescription",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of PET/Nuclear Medicine field names"""
        return self.PET_NUCLEAR_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract PET/Nuclear Medicine-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing PET/NM metadata extraction results
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

            # Detect if this is a PET/Nuclear Medicine study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_pet_nm = (
                "pet" in series_desc or "pet" in study_desc or
                "nuclear" in series_desc or "nuclear" in study_desc or
                "spect" in series_desc or "spect" in study_desc or
                "nm" in series_desc or "nm" in study_desc or
                modality in ["PT", "NM", "ST", "NT"]
            )

            metadata["is_pet_nuclear_study"] = is_pet_nm
            metadata["modality"] = modality

            # Extract PET/Nuclear Medicine-specific fields
            fields_extracted = 0

            for field in self.PET_NUCLEAR_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add PET-specific quantitative parameters if available
            if modality == "PT" or "pet" in series_desc:
                pet_params = self._extract_pet_parameters(dcm)
                metadata.update(pet_params)
                fields_extracted += len(pet_params)

            # Add Nuclear Medicine specific parameters if available
            elif modality in ["NM", "ST", "NT"] or "nm" in series_desc:
                nm_params = self._extract_nuclear_medicine_parameters(dcm)
                metadata.update(nm_params)
                fields_extracted += len(nm_params)

            # Add radiopharmaceutical tracking if available
            if "RadiopharmaceuticalInformationSequence" in metadata:
                pharm_params = self._extract_radiopharmaceutical_parameters(dcm)
                metadata.update(pharm_params)
                fields_extracted += len(pharm_params)

            # Calculate SUV if possible
            if "InjectedActivity" in metadata or "RadiopharmaceuticalTotalDose" in metadata:
                suv_params = self._calculate_suv_parameters(dcm, metadata)
                metadata.update(suv_params)
                fields_extracted += len(suv_params)

            # Add warnings if this doesn't appear to be a PET/NM study
            if not is_pet_nm:
                warnings.append(
                    "This file may not be a PET/Nuclear Medicine study. "
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
            logger.error(f"PET/Nuclear Medicine extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_pet_parameters(self, dcm) -> Dict[str, Any]:
        """Extract PET-specific parameters"""
        params = {}

        # PET technical parameters
        pet_fields = [
            "PETFrameAcquisitionSequence",
            "PETReconstructionSequence",
            "TimeOfFlightInformation",
            "ScatterFractionFactor",
            "RandomsFractionFactor",
            "PromptCountsAccumulated",
            "RandomCountsAccumulated",
        ]

        for field in pet_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"PET_{field}"] = value

        return params

    def _extract_nuclear_medicine_parameters(self, dcm) -> Dict[str, Any]:
        """Extract Nuclear Medicine-specific parameters"""
        params = {}

        # NM technical parameters
        nm_fields = [
            "NumberOfEnergyWindows",
            "EnergyWindowInformationSequence",
            "DetectorDimensions",
            "GantryTilt",
            "TableSpeed",
            "TableFeed",
        ]

        for field in nm_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"NM_{field}"] = value

        return params

    def _extract_radiopharmaceutical_parameters(self, dcm) -> Dict[str, Any]:
        """Extract radiopharmaceutical tracking parameters"""
        params = {}

        # Radiopharmaceutical tracking
        pharm_fields = [
            "DecayCorrectionDateTime",
            "DecayFactor",
            "DoseCalibrationFactor",
            "DeadTimeFactor",
            "InjectedActivity",
            "InjectedActivityDateTime",
            "BolusVolume",
            "BolusStartTimeRelativeToInjection",
            "StartHeartRate",
            "EndHeartRate",
        ]

        for field in pharm_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Pharm_{field}"] = value

        return params

    def _calculate_suv_parameters(self, dcm, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate SUV (Standard Uptake Value) parameters if possible"""
        params = {}

        try:
            # Get relevant values for SUV calculation
            body_weight = safe_extract_dicom_field(dcm, "PatientWeight")
            injected_dose = metadata.get("InjectedActivity") or metadata.get("RadiopharmaceuticalTotalDose")
            patient_size = safe_extract_dicom_field(dcm, "PatientSize")
            patient_height = safe_extract_dicom_field(dcm, "PatientSize")

            # Store calculated parameters
            if body_weight:
                params["SUV_BodyWeight_kg"] = body_weight

            if injected_dose:
                params["SUV_InjectedDose_MBq"] = injected_dose

            # Flag that SUV calculation is possible
            if body_weight and injected_dose:
                params["SUV_CalculationPossible"] = True
            else:
                params["SUV_CalculationPossible"] = False
                params["SUV_MissingParameters"] = []
                if not body_weight:
                    params["SUV_MissingParameters"].append("PatientWeight")
                if not injected_dose:
                    params["SUV_MissingParameters"].append("InjectedActivity")

        except Exception as e:
            logger.debug(f"Error calculating SUV parameters: {e}")

        return params
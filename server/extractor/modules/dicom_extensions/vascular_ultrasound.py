"""
Vascular Ultrasound DICOM Extension
Implements specialized metadata extraction for vascular ultrasound studies
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


class VascularUltrasoundExtension(DICOMExtensionBase):
    """
    Vascular Ultrasound metadata extraction.

    Extracts specialized vascular ultrasound-related DICOM tags including:
    - Doppler ultrasound parameters and measurements
    - Blood flow velocity and waveform analysis
    - Vascular anatomy and vessel characterization
    - Carotid artery assessment
    - Venous thrombosis and DVT detection
    - Arterial stenosis and plaque characterization
    - Venous insufficiency assessment
    - Endovascular intervention guidance
    """

    SPECIALTY = "vascular_ultrasound"
    FIELD_COUNT = 75
    REFERENCE = "DICOM PS3.3 (Vascular Ultrasound)"
    DESCRIPTION = "Vascular Ultrasound specialized metadata extraction"
    VERSION = "1.0.0"

    # Vascular ultrasound field definitions
    VASCULAR_US_FIELDS = [
        # Vessel identification
        "VesselLabel",
        "VesselType",
        "VesselLocation",
        "VesselSide",
        "VesselSegment",
        "VascularAnatomy",
        "VascularTerritory",
        "CarotidArtery",
        "VertebralArtery",
        "RenalArtery",
        "MesentericArtery",
        "FemoralArtery",
        "PoplitealArtery",
        "TibialArtery",
        "VeinIdentification",
        "DeepVein",
        "SuperficialVein",

        # Doppler parameters
        "DopplerMode",
        "DopplerType",
        "PulseWaveDoppler",
        "ContinuousWaveDoppler",
        "ColorDoppler",
        "PowerDoppler",
        "DuplexMode",
        "TriplexMode",
        "DopplerFrequency",
        "DopplerAngle",
        "DopplerSampleVolume",
        "DopplerGate",
        "WallFilter",
        "PRF",
        "DopplerGain",

        # Blood flow measurements
        "PeakSystolicVelocity",
        "EndDiastolicVelocity",
        "MeanVelocity",
        "PeakVelocity",
        "VelocityTimeIntegral",
        "FlowRate",
        "FlowVolume",
        "ResistiveIndex",
        "PulsatilityIndex",
        "SystolicDiastolicRatio",
        "AccelerationTime",
        "AccelerationIndex",
        "TAMAX",
        "TAMEAN",

        # Waveform analysis
        "WaveformType",
        "WaveformPattern",
        "WaveformMorphology",
        "SystolicPeak",
        "DiastolicNotch",
        "ReversalFlow",
        "TurbulentFlow",
        "LaminarFlow",
        "FlowProfile",
        "FlowPattern",

        # Arterial assessment
        "ArterialStenosis",
        "StenosisPercentage",
        "StenosisVelocity",
        "StenosisRatio",
        "PlaqueIdentification",
        "PlaqueType",
        "PlaqueMorphology",
        "PlaqueSize",
        "PlaqueSurface",
        "PlaqueUlceration",
        "PlaqueCalcification",
        "IntimaMediaThickness",
        "IMT",
        "IMTMeasurement",
        "ArterialDiameter",
        "LumenDiameter",
        "OuterDiameter",

        # Carotid specific
        "CarotidBifurcation",
        "InternalCarotidArtery",
        "ExternalCarotidArtery",
        "CommonCarotidArtery",
        "CarotidIntimaMediaThickness",
        "CarotidPlaque",
        "CarotidStenosis",
        "CarotidFlowPattern",
        "CarotidHemodynamics",

        # Venous assessment
        "VenousThrombosis",
        "DeepVeinThrombosis",
        "DVT",
        "ThrombusLocation",
        "ThrombusSize",
        "ThrombusAge",
        "VenousCompression",
        "CompressionTest",
        "AugmentationTest",
        "VenousReflux",
        "RefluxDuration",
        "RefluxVelocity",
        "VenousInsufficiency",
        "VenousDiameter",
        "VenousCollaterals",
        "GreatSaphenousVein",
        "SmallSaphenousVein",

        # Physiological parameters
        "BloodPressure",
        "SystolicPressure",
        "DiastolicPressure",
        "MeanArterialPressure",
        "AnkleBrachialIndex",
        "ABI",
        "SegmentalPressures",
        "PulseVolumeRecordings",
        "ExerciseTest",
        "ReactiveHyperemia",
        "FlowMediatedDilation",
        "EndothelialFunction",

        # Additional vascular parameters
        "VascularAccess",
        "FistulaAssessment",
        "GraftEvaluation",
        "DialysisAccess",
        "VascularMalformation",
        "AneurysmDetection",
        "AneurysmSize",
        "AneurysmLocation",
        "DissectionDetection",
        "VascularTrauma",
        "VascularInjury",
        "EndovascularProcedure",
        "StentEvaluation",
        "StentPatency",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of vascular ultrasound-specific DICOM field names"""
        return self.VASCULAR_US_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract vascular ultrasound-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing vascular ultrasound metadata extraction results
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

            # Detect if this is a vascular ultrasound study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_vascular_us = (
                modality == "US" and (
                    "vascular" in series_desc or "vascular" in study_desc or
                    "doppler" in series_desc or "doppler" in study_desc or
                    "carotid" in series_desc or "carotid" in study_desc or
                    "venous" in series_desc or "venous" in study_desc or
                    "arterial" in series_desc or "arterial" in study_desc or
                    "dvt" in series_desc or "dvt" in study_desc or
                    "aneurysm" in series_desc or "aneurysm" in study_desc
                )
            )

            metadata["is_vascular_ultrasound_study"] = is_vascular_us
            metadata["modality"] = modality

            # Extract vascular ultrasound-specific fields
            fields_extracted = 0

            for field in self.VASCULAR_US_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add vessel analysis if available
            if "VesselLabel" in metadata or "CarotidArtery" in metadata:
                vessel_params = self._extract_vessel_parameters(dcm)
                metadata.update(vessel_params)
                fields_extracted += len(vessel_params)

            # Add Doppler analysis if available
            if "DopplerMode" in metadata or "PeakSystolicVelocity" in metadata:
                doppler_params = self._extract_doppler_parameters(dcm)
                metadata.update(doppler_params)
                fields_extracted += len(doppler_params)

            # Add arterial analysis if available
            if "ArterialStenosis" in metadata or "PlaqueIdentification" in metadata:
                arterial_params = self._extract_arterial_parameters(dcm)
                metadata.update(arterial_params)
                fields_extracted += len(arterial_params)

            # Add venous analysis if available
            if "VenousThrombosis" in metadata or "DeepVeinThrombosis" in metadata:
                venous_params = self._extract_venous_parameters(dcm)
                metadata.update(venous_params)
                fields_extracted += len(venous_params)

            # Add physiological analysis if available
            if "AnkleBrachialIndex" in metadata or "BloodPressure" in metadata:
                physiological_params = self._extract_physiological_parameters(dcm)
                metadata.update(physiological_params)
                fields_extracted += len(physiological_params)

            # Add warnings if this doesn't appear to be a vascular ultrasound study
            if not is_vascular_us:
                warnings.append(
                    "This file may not be a vascular ultrasound study. "
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
            logger.error(f"Vascular ultrasound extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_vessel_parameters(self, dcm) -> Dict[str, Any]:
        """Extract vessel identification parameters"""
        params = {}

        # Vessel fields
        vessel_fields = [
            "VesselLabel",
            "VesselType",
            "VesselLocation",
            "VesselSide",
            "CarotidArtery",
            "FemoralArtery",
            "DeepVein",
        ]

        for field in vessel_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Vessel_{field}"] = value

        return params

    def _extract_doppler_parameters(self, dcm) -> Dict[str, Any]:
        """Extract Doppler measurement parameters"""
        params = {}

        # Doppler fields
        doppler_fields = [
            "DopplerMode",
            "DopplerType",
            "DopplerFrequency",
            "DopplerAngle",
            "PeakSystolicVelocity",
            "EndDiastolicVelocity",
            "ResistiveIndex",
            "PulsatilityIndex",
        ]

        for field in doppler_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Doppler_{field}"] = value

        return params

    def _extract_arterial_parameters(self, dcm) -> Dict[str, Any]:
        """Extract arterial assessment parameters"""
        params = {}

        # Arterial fields
        arterial_fields = [
            "ArterialStenosis",
            "StenosisPercentage",
            "PlaqueIdentification",
            "PlaqueType",
            "IntimaMediaThickness",
            "ArterialDiameter",
            "LumenDiameter",
        ]

        for field in arterial_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Arterial_{field}"] = value

        return params

    def _extract_venous_parameters(self, dcm) -> Dict[str, Any]:
        """Extract venous assessment parameters"""
        params = {}

        # Venous fields
        venous_fields = [
            "VenousThrombosis",
            "DeepVeinThrombosis",
            "ThrombusLocation",
            "VenousCompression",
            "VenousReflux",
            "RefluxDuration",
        ]

        for field in venous_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Venous_{field}"] = value

        return params

    def _extract_physiological_parameters(self, dcm) -> Dict[str, Any]:
        """Extract physiological measurement parameters"""
        params = {}

        # Physiological fields
        physiological_fields = [
            "BloodPressure",
            "AnkleBrachialIndex",
            "SegmentalPressures",
            "FlowMediatedDilation",
            "EndothelialFunction",
        ]

        for field in physiological_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Physiological_{field}"] = value

        return params

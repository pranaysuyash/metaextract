"""
Cardiac MRI DICOM Extension
Implements specialized metadata extraction for cardiac MRI studies
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


class CardiacMRIExtension(DICOMExtensionBase):
    """
    Cardiac MRI metadata extraction.

    Extracts specialized cardiac MRI-related DICOM tags including:
    - Cardiac function and ventricular parameters
    - Myocardial perfusion and viability
    - Cardiac gating and synchronization
    - Flow quantification and phase contrast
    - Stress testing and ischemia detection
    - Valve assessment and function
    - Congenital heart disease evaluation
    - Cardiac morphology and structure
    """

    SPECIALTY = "cardiac_mri"
    FIELD_COUNT = 82
    REFERENCE = "DICOM PS3.3 (Cardiac MRI)"
    DESCRIPTION = "Cardiac MRI specialized metadata extraction"
    VERSION = "1.0.0"

    # Cardiac MRI field definitions
    CARDIAC_MRI_FIELDS = [
        # Cardiac anatomy and morphology
        "CardiacChamber",
        "LeftVentricle",
        "RightVentricle",
        "LeftAtrium",
        "RightAtrium",
        "VentricularVolume",
        "AtrialVolume",
        "WallThickness",
        "WallMotion",
        "WallMotionScore",
        "WallThickening",
        "MyocardialMass",
        "CardiacMass",
        "ChamberDimensions",
        "SeptalThickness",
        "PosteriorWallThickness",

        # Cardiac function
        "EjectionFraction",
        "StrokeVolume",
        "CardiacOutput",
        "CardiacIndex",
        "FractionalShortening",
        "VentricularFunction",
        "SystolicFunction",
        "DiastolicFunction",
        "GlobalFunction",
        "RegionalFunction",
        "StrainAnalysis",
        "StrainRate",
        "DeformationImaging",

        # Myocardial perfusion
        "MyocardialPerfusion",
        "PerfusionImaging",
        "StressPerfusion",
        "RestPerfusion",
        "PerfusionDefect",
        "IschemiaDetection",
        "MyocardialBloodFlow",
        "MyocardialBloodVolume",
        "CoronaryFlowReserve",
        "PerfusionTerritory",
        "StressAgent",
        "StressType",
        "PharmacologicalStress",

        # Myocardial viability and scar
        "LateGadoliniumEnhancement",
        "LGE",
        "ViabilityImaging",
        "ScarDetection",
        "ScarSize",
        "ScarLocation",
        "TransmuralExtent",
        "MyocardialFibrosis",
        "T1Mapping",
        "T2Mapping",
        "NativeT1",
        "PostContrastT1",
        "ExtracellularVolume",
        "ECV",

        # Cardiac gating and synchronization
        "CardiacGating",
        "ECGTriggering",
        "ECGLeads",
        "TriggerDelay",
        "TriggerWindow",
        "ArrhythmiaRejection",
        "HeartRate",
        "RRInterval",
        "CardiacPhase",
        "SystolicPhase",
        "DiastolicPhase",
        "TriggerType",
        "RetrospectiveGating",
        "ProspectiveGating",

        # Flow quantification
        "PhaseContrast",
        "FlowQuantification",
        "FlowVelocity",
        "FlowVolume",
        "FlowRate",
        "RegurgitantFraction",
        "ShuntQuantification",
        "QPCalculation",
        "ValveFlow",
        "AorticFlow",
        "PulmonaryFlow",
        "MitralFlow",
        "TricuspidFlow",

        # Valve assessment
        "ValveMorphology",
        "ValveFunction",
        "ValveArea",
        "ValveStenosis",
        "ValveRegurgitation",
        "MitralValve",
        "AorticValve",
        "TricuspidValve",
        "PulmonicValve",
        "ValveMotion",
        "ValveCalcification",
        "ProstheticValve",

        # Stress testing
        "StressTesting",
        "ExerciseStress",
        "DobutamineStress",
        "WallMotionAbnormality",
        "IschemicCascade",
        "StressInducedWMA",
        "StressWallMotionScore",
        "RestWallMotionScore",
        "IschemicBurden",

        # Congenital heart disease
        "CongenitalHeartDisease",
        "SeptalDefect",
        "ASD",
        "VSD",
        "PDA",
        "TetralogyOfFallot",
        "GreatVessels",
        "AorticArch",
        "PulmonaryArteries",
        "SystemicVeins",
        "PulmonaryVeins",
        "Situs",
        "SegmentalAnatomy",

        # Cardiac sequences and protocols
        "CineImaging",
        "SteadyStateFreePrecession",
        "GradientEcho",
        "SpinEcho",
        "TurboSpinEcho",
        "InversionRecovery",
        "GradientEcho",
        "EchoPlanarImaging",
        "CardiacAcquisition",
        "BreathHold",
        "Navigator",
        "ParallelImaging",
        "AccelerationFactor",

        # Additional cardiac MRI parameters
        "MyocardialStrain",
        "FeatureTracking",
        "Tagging",
        "SPAMM",
        "DOR",
        "MyocardialTagging",
        "StrainEncoding",
        "DisplacementEncoding",
        "PhaseEncoding",
        "VelocityEncoding",
        "DiffusionWeighting",
        "T2StarImaging",
        "IronOverload",
        "Hemochromatosis",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of cardiac MRI-specific DICOM field names"""
        return self.CARDIAC_MRI_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract cardiac MRI-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing cardiac MRI metadata extraction results
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

            # Detect if this is a cardiac MRI study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_cardiac_mri = (
                modality == "MR" and (
                    "cardiac" in series_desc or "cardiac" in study_desc or
                    "heart" in series_desc or "heart" in study_desc or
                    "ventricle" in series_desc or "ventricle" in study_desc or
                    "atrium" in series_desc or "atrium" in study_desc or
                    "perfusion" in series_desc and "cardiac" in study_desc or
                    "lge" in series_desc or "viability" in study_desc
                )
            )

            metadata["is_cardiac_mri_study"] = is_cardiac_mri
            metadata["modality"] = modality

            # Extract cardiac MRI-specific fields
            fields_extracted = 0

            for field in self.CARDIAC_MRI_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add cardiac function analysis if available
            if "EjectionFraction" in metadata or "CardiacOutput" in metadata:
                function_params = self._extract_function_parameters(dcm)
                metadata.update(function_params)
                fields_extracted += len(function_params)

            # Add perfusion analysis if available
            if "MyocardialPerfusion" in metadata or "PerfusionImaging" in metadata:
                perfusion_params = self._extract_perfusion_parameters(dcm)
                metadata.update(perfusion_params)
                fields_extracted += len(perfusion_params)

            # Add viability analysis if available
            if "LateGadoliniumEnhancement" in metadata or "LGE" in metadata:
                viability_params = self._extract_viability_parameters(dcm)
                metadata.update(viability_params)
                fields_extracted += len(viability_params)

            # Add gating analysis if available
            if "CardiacGating" in metadata or "ECGTriggering" in metadata:
                gating_params = self._extract_gating_parameters(dcm)
                metadata.update(gating_params)
                fields_extracted += len(gating_params)

            # Add flow analysis if available
            if "PhaseContrast" in metadata or "FlowQuantification" in metadata:
                flow_params = self._extract_flow_parameters(dcm)
                metadata.update(flow_params)
                fields_extracted += len(flow_params)

            # Add valve analysis if available
            if "ValveMorphology" in metadata or "ValveFunction" in metadata:
                valve_params = self._extract_valve_parameters(dcm)
                metadata.update(valve_params)
                fields_extracted += len(valve_params)

            # Add stress analysis if available
            if "StressTesting" in metadata or "WallMotionAbnormality" in metadata:
                stress_params = self._extract_stress_parameters(dcm)
                metadata.update(stress_params)
                fields_extracted += len(stress_params)

            # Add congenital analysis if available
            if "CongenitalHeartDisease" in metadata or "SeptalDefect" in metadata:
                congenital_params = self._extract_congenital_parameters(dcm)
                metadata.update(congenital_params)
                fields_extracted += len(congenital_params)

            # Add warnings if this doesn't appear to be a cardiac MRI study
            if not is_cardiac_mri:
                warnings.append(
                    "This file may not be a cardiac MRI study. "
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
            logger.error(f"Cardiac MRI extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_function_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cardiac function parameters"""
        params = {}

        # Function fields
        function_fields = [
            "EjectionFraction",
            "StrokeVolume",
            "CardiacOutput",
            "FractionalShortening",
            "VentricularVolume",
            "WallMotionScore",
            "StrainAnalysis",
        ]

        for field in function_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Function_{field}"] = value

        return params

    def _extract_perfusion_parameters(self, dcm) -> Dict[str, Any]:
        """Extract myocardial perfusion parameters"""
        params = {}

        # Perfusion fields
        perfusion_fields = [
            "MyocardialPerfusion",
            "PerfusionImaging",
            "StressPerfusion",
            "PerfusionDefect",
            "MyocardialBloodFlow",
            "CoronaryFlowReserve",
        ]

        for field in perfusion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Perfusion_{field}"] = value

        return params

    def _extract_viability_parameters(self, dcm) -> Dict[str, Any]:
        """Extract myocardial viability parameters"""
        params = {}

        # Viability fields
        viability_fields = [
            "LateGadoliniumEnhancement",
            "LGE",
            "ViabilityImaging",
            "ScarDetection",
            "ScarSize",
            "T1Mapping",
            "T2Mapping",
            "ExtracellularVolume",
        ]

        for field in viability_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Viability_{field}"] = value

        return params

    def _extract_gating_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cardiac gating parameters"""
        params = {}

        # Gating fields
        gating_fields = [
            "CardiacGating",
            "ECGTriggering",
            "TriggerDelay",
            "HeartRate",
            "RRInterval",
            "CardiacPhase",
        ]

        for field in gating_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Gating_{field}"] = value

        return params

    def _extract_flow_parameters(self, dcm) -> Dict[str, Any]:
        """Extract flow quantification parameters"""
        params = {}

        # Flow fields
        flow_fields = [
            "PhaseContrast",
            "FlowQuantification",
            "FlowVelocity",
            "FlowVolume",
            "RegurgitantFraction",
            "ValveFlow",
        ]

        for field in flow_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Flow_{field}"] = value

        return params

    def _extract_valve_parameters(self, dcm) -> Dict[str, Any]:
        """Extract valve assessment parameters"""
        params = {}

        # Valve fields
        valve_fields = [
            "ValveMorphology",
            "ValveFunction",
            "ValveArea",
            "ValveStenosis",
            "ValveRegurgitation",
            "MitralValve",
            "AorticValve",
        ]

        for field in valve_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Valve_{field}"] = value

        return params

    def _extract_stress_parameters(self, dcm) -> Dict[str, Any]:
        """Extract stress testing parameters"""
        params = {}

        # Stress fields
        stress_fields = [
            "StressTesting",
            "StressType",
            "WallMotionAbnormality",
            "IschemicCascade",
            "IschemicBurden",
        ]

        for field in stress_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Stress_{field}"] = value

        return params

    def _extract_congenital_parameters(self, dcm) -> Dict[str, Any]:
        """Extract congenital heart disease parameters"""
        params = {}

        # Congenital fields
        congenital_fields = [
            "CongenitalHeartDisease",
            "SeptalDefect",
            "ASD",
            "VSD",
            "TetralogyOfFallot",
            "GreatVessels",
        ]

        for field in congenital_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Congenital_{field}"] = value

        return params

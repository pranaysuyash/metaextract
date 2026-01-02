"""
MRI and MRS DICOM Extension
Implements specialized metadata extraction for MRI and Magnetic Resonance Spectroscopy studies
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


class MRIMRSExtension(DICOMExtensionBase):
    """
    MRI and MRS metadata extraction.

    Extracts specialized MRI/MRS-related DICOM tags including:
    - MRI acquisition parameters and sequences
    - Magnetic resonance angiography (MRA) data
    - Diffusion-weighted imaging (DTI) parameters
    - Functional MRI (fMRI) activation maps
    - Magnetic resonance spectroscopy (MRS) data
    - Cardiac MRI gating and synchronization
    - Contrast enhancement and perfusion
    - Image quality and artifact metrics
    """

    SPECIALTY = "mri_mrs"
    FIELD_COUNT = 88
    REFERENCE = "DICOM PS3.3 (MRI)"
    DESCRIPTION = "MRI and MRS specialized metadata extraction"
    VERSION = "1.0.0"

    # MRI/MRS field definitions
    MRI_MRS_FIELDS = [
        # MRI scanning parameters
        "ScanningSequence",
        "SequenceVariant",
        "ScanOptions",
        "MRAcquisitionType",
        "SequenceName",
        "AngioFlag",
        "RepetitionTime",
        "EchoTime",
        "InversionTime",
        "NumberOfAverages",
        "ImagingFrequency",
        "ImagedNucleus",
        "EchoNumber",
        "MagneticFieldStrength",
        "SpacingBetweenSlices",
        "NumberOfPhaseEncodingSteps",
        "EchoTrainLength",
        "PercentSampling",
        "PercentPhaseFieldOfView",
        "PixelBandwidth",

        # Gradient and coil information
        "GradientEchoTraining",
        "GradientOutput",
        "GradientAmplitude",
        "GradientDuration",
        "GradientOrientation",
        "CoilType",
        "CoilElements",
        "CoilConfiguration",
        "TransmitCoilName",
        "ReceiveCoilName",
        "Quadrature CoilFlag",

        # Image characteristics
        "ImagingFrequency",
        "ImagedNucleus",
        "ChemicalShift",
        "ChemicalShiftReference",
        "ProtonDensity",
        "T1RelaxationTime",
        "T2RelaxationTime",
        "T2StarRelaxationTime",
        "SpinDensity",
        "MagneticFieldStrength",
        "SAR",

        # Diffusion and DTI
        "DiffusionDirectionality",
        "DiffusionOrientation",
        "DiffusionBValue",
        "DiffusionGradientOrientation",
        "DiffusionBFactor",
        "NumberOfDiffusionDirections",
        "DiffusionDirectionSequence",
        "DiffusionAnisotropyType",
        "FractionalAnisotropy",
        "ApparentDiffusionCoefficient",
        "DiffusionTensor",
        "TraceValue",

        # fMRI and functional imaging
        "FunctionalMRIFlag",
        "BloodOxygenationLevel",
        "BloodOxygenationLevelDependent",
        "FMRIContrastType",
        "FMRIRepetitionTime",
        "FMRIRepetitionTimeFunctional",
        "FMRIActivationMap",
        "FMRIStatisticalParameters",
        "FMRIModelParameters",
        "RestingStateFMRI",
        "TaskBasedFMRI",
        "ParadigmType",

        # MRA and angiography
        "MRAcquisitionType",
        "AngioFlag",
        "VelocityEncoding",
        "VelocityEncodingDirection",
        "MaximumVelocity",
        "MinimumVelocity",
        "VesselLabel",
        "VesselType",
        "FlowQuantification",
        "FlowDirection",

        # Cardiac MRI
        "HeartRate",
        "CardiacNumberOfImages",
        "TriggerTime",
        "TriggerDelay",
        "CardiacSignalSequence",
        "CardiacGatingTechnique",
        "ArrhythmiaRejection",
        "RRInterval",
        "QRSComplex",
        "DiastoleTime",
        "SystoleTime",

        # Perfusion and contrast
        "PerfusionFlag",
        "ContrastBolusAgent",
        "ContrastBolusVolume",
        "ContrastBolusRoute",
        "ContrastBolusStartTime",
        "ContrastBolusStopTime",
        "ContrastFlowRate",
        "PerfusionCurve",
        "PerfusionMap",
        "TimeIntensityCurve",
        "CerebralBloodFlow",
        "CerebralBloodVolume",

        # MRS spectroscopy
        "SpectroscopyAcquisitionType",
        "SpectroscopyFrequency",
        "SpectroscopyNucleus",
        "SpectralWidth",
        "SpectralPoints",
        "NumberOfSpectralLines",
        "MetaboliteMap",
        "MetaboliteConcentration",
        "MetaboliteRatio",
        "ChemicalShiftImaging",
        "SpectralPeak",
        "PeakArea",
        "PeakWidth",
        "SignalToNoiseRatio",
        "ShimmingData",

        # Image quality and artifacts
        "ImageQuality",
        "ImageQualityMetric",
        "ArtifactMetricSequence",
        "MotionArtifactLevel",
        "GhostingLevel",
        "SNR",
        "CNR",
        "Uniformity",
        "GeometricDistortion",
        "IntensityNonUniformity",

        # Acquisition timing
        "AcquisitionDuration",
        "AcquisitionDateTime",
        "AcquisitionNumber",
        "FrameTime",
        "FrameDelay",
        "TemporalPosition",
        "TemporalResolution",
        "NumberOfTemporalPositions",

        # Spatial parameters
        "SliceThickness",
        "SliceLocation",
        "SpacingBetweenSlices",
        "ImagePositionPatient",
        "ImageOrientationPatient",
        "InPlanePhaseEncodingDirection",
        "FrequencyDirection",

        # Additional MRI parameters
        "VariableFlipAngleFlag",
        "SAR",
        "SpecificAbsorptionRate",
        "GradientMode",
        "FlowCompensation",
        "PartialFourierDirection",
        "PartialFourierFlag",
        "ParallelAcquisition",
        "ParallelAcquisitionTechnique",
        "AccelerationFactor",
        "kSpaceCoverage",
        "OversamplingPhase",
        "OversamplingSlice",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of MRI/MRS-specific DICOM field names"""
        return self.MRI_MRS_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract MRI/MRS-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing MRI/MRS metadata extraction results
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

            # Detect if this is an MRI/MRS study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_mri = (
                modality == "MR" or
                "mri" in series_desc or "mri" in study_desc or
                "magnetic resonance" in series_desc or "magnetic resonance" in study_desc or
                "spectroscopy" in series_desc or "spectroscopy" in study_desc or
                "fmri" in series_desc or "fmri" in study_desc or
                "diffusion" in series_desc or "diffusion" in study_desc or
                "angiography" in series_desc and "mr" in study_desc
            )

            metadata["is_mri_mrs_study"] = is_mri
            metadata["modality"] = modality

            # Extract MRI/MRS-specific fields
            fields_extracted = 0

            for field in self.MRI_MRS_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add scanning parameters analysis if available
            if "ScanningSequence" in metadata or "RepetitionTime" in metadata:
                scanning_params = self._extract_scanning_parameters(dcm)
                metadata.update(scanning_params)
                fields_extracted += len(scanning_params)

            # Add diffusion analysis if available
            if "DiffusionBValue" in metadata or "DiffusionDirectionality" in metadata:
                diffusion_params = self._extract_diffusion_parameters(dcm)
                metadata.update(diffusion_params)
                fields_extracted += len(diffusion_params)

            # Add fMRI analysis if available
            if "FunctionalMRIFlag" in metadata or "BloodOxygenationLevel" in metadata:
                fmri_params = self._extract_fmri_parameters(dcm)
                metadata.update(fmri_params)
                fields_extracted += len(fmri_params)

            # Add cardiac MRI analysis if available
            if "HeartRate" in metadata or "TriggerTime" in metadata:
                cardiac_params = self._extract_cardiac_mri_parameters(dcm)
                metadata.update(cardiac_params)
                fields_extracted += len(cardiac_params)

            # Add perfusion analysis if available
            if "PerfusionFlag" in metadata or "ContrastBolusAgent" in metadata:
                perfusion_params = self._extract_perfusion_parameters(dcm)
                metadata.update(perfusion_params)
                fields_extracted += len(perfusion_params)

            # Add MRS analysis if available
            if "SpectroscopyAcquisitionType" in metadata or "MetaboliteMap" in metadata:
                mrs_params = self._extract_mrs_parameters(dcm)
                metadata.update(mrs_params)
                fields_extracted += len(mrs_params)

            # Add image quality if available
            if "ImageQuality" in metadata or "SNR" in metadata:
                quality_params = self._extract_quality_parameters(dcm)
                metadata.update(quality_params)
                fields_extracted += len(quality_params)

            # Add warnings if this doesn't appear to be an MRI study
            if not is_mri:
                warnings.append(
                    "This file may not be an MRI/MRS study. "
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
            logger.error(f"MRI/MRS extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_scanning_parameters(self, dcm) -> Dict[str, Any]:
        """Extract MRI scanning parameters"""
        params = {}

        # Scanning parameter fields
        scanning_fields = [
            "ScanningSequence",
            "SequenceVariant",
            "RepetitionTime",
            "EchoTime",
            "InversionTime",
            "NumberOfAverages",
            "ImagingFrequency",
            "MagneticFieldStrength",
        ]

        for field in scanning_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Scanning_{field}"] = value

        return params

    def _extract_diffusion_parameters(self, dcm) -> Dict[str, Any]:
        """Extract diffusion and DTI parameters"""
        params = {}

        # Diffusion fields
        diffusion_fields = [
            "DiffusionBValue",
            "DiffusionDirectionality",
            "DiffusionGradientOrientation",
            "FractionalAnisotropy",
            "ApparentDiffusionCoefficient",
            "NumberOfDiffusionDirections",
        ]

        for field in diffusion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Diffusion_{field}"] = value

        return params

    def _extract_fmri_parameters(self, dcm) -> Dict[str, Any]:
        """Extract fMRI parameters"""
        params = {}

        # fMRI fields
        fmri_fields = [
            "FunctionalMRIFlag",
            "BloodOxygenationLevel",
            "FMRIContrastType",
            "FMRIRepetitionTime",
            "FMRIActivationMap",
            "RestingStateFMRI",
            "TaskBasedFMRI",
        ]

        for field in fmri_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"fMRI_{field}"] = value

        return params

    def _extract_cardiac_mri_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cardiac MRI parameters"""
        params = {}

        # Cardiac MRI fields
        cardiac_fields = [
            "HeartRate",
            "TriggerTime",
            "TriggerDelay",
            "CardiacGatingTechnique",
            "ArrhythmiaRejection",
            "RRInterval",
            "DiastoleTime",
        ]

        for field in cardiac_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"CardiacMRI_{field}"] = value

        return params

    def _extract_perfusion_parameters(self, dcm) -> Dict[str, Any]:
        """Extract perfusion parameters"""
        params = {}

        # Perfusion fields
        perfusion_fields = [
            "PerfusionFlag",
            "ContrastBolusAgent",
            "ContrastBolusVolume",
            "ContrastFlowRate",
            "PerfusionCurve",
            "CerebralBloodFlow",
            "CerebralBloodVolume",
        ]

        for field in perfusion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Perfusion_{field}"] = value

        return params

    def _extract_mrs_parameters(self, dcm) -> Dict[str, Any]:
        """Extract MRS spectroscopy parameters"""
        params = {}

        # MRS fields
        mrs_fields = [
            "SpectroscopyAcquisitionType",
            "SpectroscopyFrequency",
            "SpectralWidth",
            "MetaboliteMap",
            "MetaboliteConcentration",
            "ChemicalShiftImaging",
            "PeakArea",
            "SignalToNoiseRatio",
        ]

        for field in mrs_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"MRS_{field}"] = value

        return params

    def _extract_quality_parameters(self, dcm) -> Dict[str, Any]:
        """Extract image quality parameters"""
        params = {}

        # Quality fields
        quality_fields = [
            "ImageQuality",
            "ImageQualityMetric",
            "MotionArtifactLevel",
            "SNR",
            "CNR",
            "Uniformity",
            "GeometricDistortion",
        ]

        for field in quality_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Quality_{field}"] = value

        return params

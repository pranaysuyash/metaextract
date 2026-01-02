"""
Ultrasound DICOM Extension
Implements specialized metadata extraction for ultrasound imaging studies
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


class UltrasoundExtension(DICOMExtensionBase):
    """
    Ultrasound metadata extraction.

    Extracts specialized ultrasound-related DICOM tags including:
    - Transducer and acquisition parameters
    - Image orientation and scanning techniques
    - Doppler measurements and flow data
    - 3D/4D ultrasound volumetric data
    - Elastography and tissue characterization
    - Contrast-enhanced ultrasound data
    - Measurements and calculations
    - Biometric measurements for obstetrics/gynecology
    - Cardiac ultrasound (echocardiography) parameters
    """

    SPECIALTY = "ultrasound"
    FIELD_COUNT = 94
    REFERENCE = "DICOM PS3.3 (Ultrasound)"
    DESCRIPTION = "Ultrasound specialized metadata extraction"
    VERSION = "1.0.0"

    # Ultrasound field definitions
    US_FIELDS = [
        # Transducer information
        "TransducerType",
        "TransducerApplication",
        "TransducerFrequency",
        "TransducerBandwidth",
        "TransducerManufacturer",
        "TransducerModel",
        "TransducerSerialNumber",
        "TransducerElementCount",
        "TransducerElementPitch",
        "TransducerElementWidth",
        "TransducerApertureSize",
        "TransducerGeometry",
        "TransducerBeamProfile",

        # Image acquisition parameters
        "AcquisitionDateTime",
        "AcquisitionDuration",
        "FrameTime",
        "FrameRate",
        "LinesPerFrame",
        "SamplesPerLine",
        "PixelsPerLine",
        "PixelSpacing",
        "ZoomFactor",
        "ZoomCenter",
        "ScanDirection",
        "ScanMode",
        "TransducerScanType",
        "AcquisitionZone",
        "RegionOfInterest",

        # Image orientation and position
        "ImageOrientation",
        "ImageOrientationPatient",
        "ImagePositionPatient",
        "SliceThickness",
        "SliceLocation",
        "PatientOrientation",
        "PatientPosition",
        "ViewCodeSequence",
        "ViewModifierCodeSequence",

        # Doppler parameters
        "VelocityEncode",
        "VelocityScale",
        "VelocityMinimum",
        "VelocityMaximum",
        "AliasingThreshold",
        "DopplerSampleVolume",
        "DopplerAngle",
        "DopplerFrequency",
        "DopplerGain",
        "DopplerPRF",
        "WallFilterFrequency",
        "EnsembleSize",
        "AcquisitionTime",
        "TemporalResolution",
        "FlowDirection",
        "FlowType",

        # 3D/4D ultrasound
        "Volume3D",
        "Volume3DAxis",
        "Volume3DData",
        "Volume3DThickness",
        "Volume3DWidth",
        "Volume3DHeight",
        "Volume3DDepth",
        "Volume3DNumberOfFrames",
        "Volume3DFrameRate",
        "RenderMethod",
        "CameraParameters",
        "ViewingParameters",
        "RenderingParameters",

        # Tissue characterization
        "TissueHarmonics",
        "TissueFrequency",
        "MechanicalIndex",
        "ThermalIndex",
        "TissueCharacterization",
        "TissueType",
        "ScattererSize",
        "ScattererConcentration",

        # Elastography
        "Elastography",
        "ElastographyType",
        "StrainValue",
        "StrainRatio",
        "StiffnessValue",
        "ShearWaveVelocity",
        "Elastogram",
        "ElastographyParameters",

        # Contrast-enhanced ultrasound
        "ContrastAgent",
        "ContrastAgentVolume",
        "ContrastAgentRoute",
        "ContrastAgentInjectionTime",
        "ContrastBolusTracking",
        "ContrastDose",
        "ContrastDoseRate",
        "ContrastWashout",
        "ContrastEnhancement",

        # Measurements and calculations
        "MeasurementSequence",
        "MeasurementLabel",
        "MeasurementValue",
        "MeasurementUnits",
        "MeasurementMethod",
        "MeasurementAlgorithm",
        "MeasurementDateTime",
        "MeasurementComments",
        "RealWorldValueMappingSequence",

        # Obstetrics/Gynecology biometrics
        "GestationalAge",
        "FetalHeartRate",
        "FetalPresentation",
        "PlacentaLocation",
        "AmnioticFluidIndex",
        "CervicalLength",
        "FundalHeight",
        "FetalWeight",
        "FetalLength",
        "HeadCircumference",
        "AbdominalCircumference",
        "FemurLength",
        "BiparietalDiameter",
        "OccipitofrontalDiameter",

        # Cardiac ultrasound (echocardiography)
        "CardiacImageType",
        "CardiacView",
        "CardiacSequence",
        "LeftVentricularEndDiastolicDimension",
        "LeftVentricularEndSystolicDimension",
        "EjectionFraction",
        "FractionalShortening",
        "WallThickness",
        "WallMotionScore",
        "ValveArea",
        "ValveVelocity",
        "PressureGradient",
        "CardiacOutput",
        "StrokeVolume",

        # Image processing
        "Gain",
        "DynamicRange",
        "Power",
        "Contrast",
        "Brightness",
        "Gamma",
        "EdgeEnhancement",
        "Persistence",
        "Smoothness",
        "ImageProcessing",
        "ImageFilter",
        "ImageEnhancement",

        # Device information
        "Manufacturer",
        "ManufacturerModelName",
        "DeviceSerialNumber",
        "SoftwareVersions",
        "DeviceDescription",
        "StationName",
        "InstitutionName",
        "InstitutionalDepartmentName",

        # Additional ultrasound parameters
        "SoundVelocity",
        "Attenuation",
        "Scattering",
        "Reflection",
        "Refraction",
        "Diffraction",
        "Interference",
        "AcousticPower",
        "AcousticPressure",
        "AcousticIntensity",
        "BeamFormerType",
        "BeamFormerSettings",
        "ImageFormat",
        "ImageDepth",
        "FocusDepth",
        "NumberOfFocalZones",
        "FocalZonePositions",

        # Quality control
        "QualityControlImage",
        "ImageQualityIndicator",
        "ArtifactMetricSequence",
        "ImageArtifacts",
        "ImageQualityScore",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of ultrasound-specific DICOM field names"""
        return self.US_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract ultrasound-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing ultrasound metadata extraction results
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

            # Detect if this is an ultrasound study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_ultrasound = (
                modality == "US" or
                "ultrasound" in series_desc or "ultrasound" in study_desc or
                "sonography" in series_desc or "sonography" in study_desc or
                "echo" in series_desc or "echo" in study_desc or
                "doppler" in series_desc or "doppler" in study_desc or
                "transducer" in series_desc or "transducer" in study_desc
            )

            metadata["is_ultrasound_study"] = is_ultrasound
            metadata["modality"] = modality

            # Extract ultrasound-specific fields
            fields_extracted = 0

            for field in self.US_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add transducer analysis if available
            if "TransducerType" in metadata or "TransducerFrequency" in metadata:
                transducer_params = self._extract_transducer_parameters(dcm)
                metadata.update(transducer_params)
                fields_extracted += len(transducer_params)

            # Add Doppler analysis if available
            if "VelocityEncode" in metadata or "DopplerFrequency" in metadata:
                doppler_params = self._extract_doppler_parameters(dcm)
                metadata.update(doppler_params)
                fields_extracted += len(doppler_params)

            # Add 3D/4D analysis if available
            if "Volume3D" in metadata or "Volume3DData" in metadata:
                volume_params = self._extract_volume_parameters(dcm)
                metadata.update(volume_params)
                fields_extracted += len(volume_params)

            # Add measurements if available
            if "MeasurementSequence" in metadata or "MeasurementValue" in metadata:
                measurement_params = self._extract_measurement_parameters(dcm)
                metadata.update(measurement_params)
                fields_extracted += len(measurement_params)

            # Add obstetrics analysis if available
            if "GestationalAge" in metadata or "FetalHeartRate" in metadata:
                obstetrics_params = self._extract_obstetrics_parameters(dcm)
                metadata.update(obstetrics_params)
                fields_extracted += len(obstetrics_params)

            # Add cardiac analysis if available
            if "CardiacImageType" in metadata or "EjectionFraction" in metadata:
                cardiac_params = self._extract_cardiac_parameters(dcm)
                metadata.update(cardiac_params)
                fields_extracted += len(cardiac_params)

            # Add elastography if available
            if "Elastography" in metadata or "StrainValue" in metadata:
                elastography_params = self._extract_elastography_parameters(dcm)
                metadata.update(elastography_params)
                fields_extracted += len(elastography_params)

            # Add warnings if this doesn't appear to be an ultrasound study
            if not is_ultrasound:
                warnings.append(
                    "This file may not be an ultrasound study. "
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
            logger.error(f"Ultrasound extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_transducer_parameters(self, dcm) -> Dict[str, Any]:
        """Extract transducer parameters"""
        params = {}

        # Transducer fields
        transducer_fields = [
            "TransducerType",
            "TransducerFrequency",
            "TransducerBandwidth",
            "TransducerGeometry",
            "TransducerApplication",
        ]

        for field in transducer_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Transducer_{field}"] = value

        return params

    def _extract_doppler_parameters(self, dcm) -> Dict[str, Any]:
        """Extract Doppler parameters"""
        params = {}

        # Doppler fields
        doppler_fields = [
            "VelocityEncode",
            "VelocityScale",
            "DopplerAngle",
            "DopplerFrequency",
            "DopplerGain",
            "DopplerPRF",
            "FlowDirection",
            "FlowType",
        ]

        for field in doppler_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Doppler_{field}"] = value

        return params

    def _extract_volume_parameters(self, dcm) -> Dict[str, Any]:
        """Extract 3D/4D volume parameters"""
        params = {}

        # Volume fields
        volume_fields = [
            "Volume3D",
            "Volume3DThickness",
            "Volume3DWidth",
            "Volume3DHeight",
            "Volume3DDepth",
            "Volume3DNumberOfFrames",
            "RenderMethod",
        ]

        for field in volume_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Volume_{field}"] = value

        return params

    def _extract_measurement_parameters(self, dcm) -> Dict[str, Any]:
        """Extract measurement parameters"""
        params = {}

        # Measurement fields
        measurement_fields = [
            "MeasurementLabel",
            "MeasurementValue",
            "MeasurementUnits",
            "MeasurementMethod",
            "MeasurementDateTime",
        ]

        for field in measurement_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Measurement_{field}"] = value

        return params

    def _extract_obstetrics_parameters(self, dcm) -> Dict[str, Any]:
        """Extract obstetrics/gynecology parameters"""
        params = {}

        # Obstetrics fields
        obstetrics_fields = [
            "GestationalAge",
            "FetalHeartRate",
            "FetalPresentation",
            "PlacentaLocation",
            "AmnioticFluidIndex",
            "FetalWeight",
            "HeadCircumference",
            "AbdominalCircumference",
        ]

        for field in obstetrics_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Obstetrics_{field}"] = value

        return params

    def _extract_cardiac_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cardiac ultrasound parameters"""
        params = {}

        # Cardiac fields
        cardiac_fields = [
            "CardiacImageType",
            "CardiacView",
            "EjectionFraction",
            "FractionalShortening",
            "WallThickness",
            "ValveArea",
            "CardiacOutput",
        ]

        for field in cardiac_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Cardiac_{field}"] = value

        return params

    def _extract_elastography_parameters(self, dcm) -> Dict[str, Any]:
        """Extract elastography parameters"""
        params = {}

        # Elastography fields
        elastography_fields = [
            "ElastographyType",
            "StrainValue",
            "StrainRatio",
            "StiffnessValue",
            "ShearWaveVelocity",
        ]

        for field in elastography_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Elastography_{field}"] = value

        return params

"""
X-Ray Angiography DICOM Extension
Implements specialized metadata extraction for X-Ray angiography and interventional studies
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


class XRayAngiographyExtension(DICOMExtensionBase):
    """
    X-Ray Angiography metadata extraction.

    Extracts specialized X-ray angiography-related DICOM tags including:
    - X-ray acquisition and exposure parameters
    - Image intensifier and detector information
    - Angiographic injection and contrast data
    - Positioner and gantry information
    - Fluoroscopy and cine acquisition
    - Interventional device tracking
    - Dose monitoring and radiation safety
    - Vascular imaging parameters
    """

    SPECIALTY = "xray_angiography"
    FIELD_COUNT = 82
    REFERENCE = "DICOM PS3.3 (X-Ray Angiography)"
    DESCRIPTION = "X-Ray Angiography specialized metadata extraction"
    VERSION = "1.0.0"

    # X-ray angiography field definitions
    XRAY_ANGIO_FIELDS = [
        # X-ray generation parameters
        "KVP",
        "XRayTubeCurrent",
        "XRayTubeCurrentInmA",
        "Exposure",
        "ExposureInuAs",
        "ExposureTime",
        "ExposureTimeInms",
        "PulseSequence",
        "PulseRate",
        "NumberOfPulses",
        "AveragePulseWidth",
        "RadiationSetting",
        "RadiationMode",
        "BeamArea",
        "BeamAreaProduct",
        "BeamHardening",
        "BeamFiltering",

        # Image intensifier and detector
        "ImageIntensifierSize",
        "ImageIntensifierManufacturer",
        "ImageIntensifierModel",
        "ImageIntensifierSerialNumber",
        "DetectorSize",
        "DetectorManufacturer",
        "DetectorModel",
        "DetectorType",
        "DetectorConfiguration",
        "DetectorElementSize",
        "DetectorActiveArea",
        "DetectorActiveShape",
        "DetectorActiveDimensions",
        "DetectorElementPhysicalSize",
        "PositionerType",
        "PositionerManufacturer",
        "PositionerModel",
        "PositionerSerialNumber",

        # Positioner and gantry
        "PositionerPrimaryAngle",
        "PositionerSecondaryAngle",
        "PositionerPrimaryAngleIncrement",
        "PositionerSecondaryAngleIncrement",
        "GantryAngle",
        "GantryPitchAngle",
        "GantryRotationDirection",
        "GantryDetectorTilt",
        "TableHeight",
        "TableHorizontalRotation",
        "TableHeadTilt",
        "TableCraneTilt",
        "TableLongitude",
        "TableLaterality",
        "TableVerticalPosition",
        "TableLongitudinalPosition",
        "TableLateralPosition",

        # Angiographic injection
        "ContrastBolusAgent",
        "ContrastBolusVolume",
        "ContrastBolusRoute",
        "ContrastBolusStartTime",
        "ContrastBolusStopTime",
        "ContrastBolusTotalDose",
        "ContrastFlowRate",
        "ContrastInjectionProtocol",
        "ContrastTemperature",
        "ContrastViscosity",
        "InjectionSequence",
        "InjectionType",
        "InjectorManufacturer",
        "InjectorModel",
        "InjectorSerialNumber",

        # Fluoroscopy and cine
        "FluoroscopyFlag",
        "FluoroscopyMode",
        "FluoroscopyFrameRate",
        "FluoroscopyTime",
        "FluoroscopyTotalTime",
        "FluoroscopyAcquisitionDose",
        "FluoroscopyDoseAreaProduct",
        "CineFlag",
        "CineFrameRate",
        "CineTime",
        "CineDuration",
        "FrameTime",
        "FrameTimeVector",
        "CineMode",
        "AcquisitionRate",
        "AcquisitionTime",

        # Vascular and cardiac parameters
        "HeartRate",
        "TriggerType",
        "TriggerTime",
        "TriggerDelay",
        "CardiacSynchronization",
        "ECGTriggerType",
        "ECGTriggerSource",
        "ArrhythmiaRejection",
        "RRInterval",
        "CardiacPhase",
        "VesselLabel",
        "VesselType",
        "VesselDiameter",
        "StenosisPercentage",
        "LesionLength",
        "ReferenceDiameter",

        # Interventional devices
        "CatheterType",
        "CatheterManufacturer",
        "CatheterModel",
        "CatheterSize",
        "CatheterShape",
        "GuidewireType",
        "GuidewireSize",
        "StentType",
        "StentSize",
        "StentManufacturer",
        "BalloonType",
        "BalloonSize",
        "BalloonPressure",
        "EmbolicDevice",
        "CoilType",
        "CoilSize",

        # Dose and radiation
        "DoseAreaProduct",
        "DoseAreaProductSequence",
        "CumulativeDose",
        "CumulativeDoseSequence",
        "EntranceDose",
        "EntranceDoseInmGy",
        "ReferencedDoseSequence",
        "DoseSummary",
        "FluoroscopyDoseAreaProductTotal",
        "CineDoseAreaProductTotal",
        "TotalDoseAreaProduct",
        "SkinDose",
        "SkinDoseSequence",
        "PeakSkinDose",

        # Image processing
        "ImageProcessingSequence",
        "ImageProcessingType",
        "ImageProcessingParameters",
        "ImageFilter",
        "ImageEnhancement",
        "EdgeEnhancement",
        "NoiseReduction",
        "ContrastEnhancement",
        "GammaCorrection",
        "WindowCenter",
        "WindowWidth",
        "VOILUTFunction",

        # Distance and magnification
        "DistanceSourceToPatient",
        "DistanceSourceToDetector",
        "DistancePatientToDetector",
        "ImagerPixelSpacing",
        "EstimatedRadiographicMagnificationFactor",
        "FieldOfView",
        "FieldOfViewShape",
        "FieldOfViewDimensions",

        # Additional angiographic parameters
        "AngioFlag",
        "AngioDevice",
        "AcquisitionStatus",
        "AcquisitionComments",
        "AcquisitionProtocol",
        "AcquisitionTechnique",
        "ViewType",
        "ViewLabel",
        "AcquisitionPlane",
        "AnatomicRegion",
        "ProjectionEponymousName",
        "PatientOrientationCodeSequence",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of X-ray angiography-specific DICOM field names"""
        return self.XRAY_ANGIO_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract X-ray angiography-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing X-ray angiography metadata extraction results
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

            # Detect if this is an X-ray angiography study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_xray_angio = (
                modality in ["XA", "RF"] or
                "angiography" in series_desc or "angiography" in study_desc or
                "angio" in series_desc or "angio" in study_desc or
                "catheterization" in series_desc or "catheterization" in study_desc or
                "interventional" in series_desc or "interventional" in study_desc or
                "fluoroscopy" in series_desc or "fluoroscopy" in study_desc or
                "coronary" in series_desc or "coronary" in study_desc
            )

            metadata["is_xray_angiography_study"] = is_xray_angio
            metadata["modality"] = modality

            # Extract X-ray angiography-specific fields
            fields_extracted = 0

            for field in self.XRAY_ANGIO_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add X-ray parameters analysis if available
            if "KVP" in metadata or "XRayTubeCurrent" in metadata:
                xray_params = self._extract_xray_parameters(dcm)
                metadata.update(xray_params)
                fields_extracted += len(xray_params)

            # Add positioner analysis if available
            if "PositionerPrimaryAngle" in metadata or "GantryAngle" in metadata:
                positioner_params = self._extract_positioner_parameters(dcm)
                metadata.update(positioner_params)
                fields_extracted += len(positioner_params)

            # Add contrast analysis if available
            if "ContrastBolusAgent" in metadata or "ContrastFlowRate" in metadata:
                contrast_params = self._extract_contrast_parameters(dcm)
                metadata.update(contrast_params)
                fields_extracted += len(contrast_params)

            # Add fluoroscopy analysis if available
            if "FluoroscopyFlag" in metadata or "CineFlag" in metadata:
                fluoro_params = self._extract_fluoroscopy_parameters(dcm)
                metadata.update(fluoro_params)
                fields_extracted += len(fluoro_params)

            # Add vascular analysis if available
            if "HeartRate" in metadata or "VesselLabel" in metadata:
                vascular_params = self._extract_vascular_parameters(dcm)
                metadata.update(vascular_params)
                fields_extracted += len(vascular_params)

            # Add device analysis if available
            if "CatheterType" in metadata or "StentType" in metadata:
                device_params = self._extract_device_parameters(dcm)
                metadata.update(device_params)
                fields_extracted += len(device_params)

            # Add dose analysis if available
            if "DoseAreaProduct" in metadata or "SkinDose" in metadata:
                dose_params = self._extract_dose_parameters(dcm)
                metadata.update(dose_params)
                fields_extracted += len(dose_params)

            # Add warnings if this doesn't appear to be an X-ray angiography study
            if not is_xray_angio:
                warnings.append(
                    "This file may not be an X-ray angiography study. "
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
            logger.error(f"X-ray angiography extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_xray_parameters(self, dcm) -> Dict[str, Any]:
        """Extract X-ray generation parameters"""
        params = {}

        # X-ray fields
        xray_fields = [
            "KVP",
            "XRayTubeCurrent",
            "Exposure",
            "ExposureTime",
            "PulseSequence",
            "PulseRate",
            "NumberOfPulses",
            "RadiationMode",
        ]

        for field in xray_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"XRay_{field}"] = value

        return params

    def _extract_positioner_parameters(self, dcm) -> Dict[str, Any]:
        """Extract positioner and gantry parameters"""
        params = {}

        # Positioner fields
        positioner_fields = [
            "PositionerPrimaryAngle",
            "PositionerSecondaryAngle",
            "GantryAngle",
            "GantryPitchAngle",
            "TableHeight",
            "TableHorizontalRotation",
            "TableHeadTilt",
        ]

        for field in positioner_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Positioner_{field}"] = value

        return params

    def _extract_contrast_parameters(self, dcm) -> Dict[str, Any]:
        """Extract contrast injection parameters"""
        params = {}

        # Contrast fields
        contrast_fields = [
            "ContrastBolusAgent",
            "ContrastBolusVolume",
            "ContrastFlowRate",
            "ContrastInjectionProtocol",
            "InjectionType",
            "InjectorManufacturer",
        ]

        for field in contrast_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Contrast_{field}"] = value

        return params

    def _extract_fluoroscopy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract fluoroscopy and cine parameters"""
        params = {}

        # Fluoroscopy fields
        fluoro_fields = [
            "FluoroscopyMode",
            "FluoroscopyFrameRate",
            "FluoroscopyTotalTime",
            "CineFlag",
            "CineFrameRate",
            "CineDuration",
            "AcquisitionRate",
        ]

        for field in fluoro_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Fluoroscopy_{field}"] = value

        return params

    def _extract_vascular_parameters(self, dcm) -> Dict[str, Any]:
        """Extract vascular and cardiac parameters"""
        params = {}

        # Vascular fields
        vascular_fields = [
            "HeartRate",
            "TriggerType",
            "TriggerTime",
            "CardiacSynchronization",
            "VesselLabel",
            "VesselDiameter",
            "StenosisPercentage",
        ]

        for field in vascular_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Vascular_{field}"] = value

        return params

    def _extract_device_parameters(self, dcm) -> Dict[str, Any]:
        """Extract interventional device parameters"""
        params = {}

        # Device fields
        device_fields = [
            "CatheterType",
            "CatheterSize",
            "GuidewireType",
            "GuidewireSize",
            "StentType",
            "StentSize",
            "BalloonType",
            "BalloonSize",
        ]

        for field in device_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Device_{field}"] = value

        return params

    def _extract_dose_parameters(self, dcm) -> Dict[str, Any]:
        """Extract radiation dose parameters"""
        params = {}

        # Dose fields
        dose_fields = [
            "DoseAreaProduct",
            "CumulativeDose",
            "EntranceDose",
            "FluoroscopyDoseAreaProductTotal",
            "CineDoseAreaProductTotal",
            "SkinDose",
            "PeakSkinDose",
        ]

        for field in dose_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Dose_{field}"] = value

        return params

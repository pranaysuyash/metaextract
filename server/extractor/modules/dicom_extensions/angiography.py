"""
Angiography and Interventional Radiology DICOM Extension
Implements specialized metadata extraction for angiography and interventional studies
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


class AngiographyInterventionalExtension(DICOMExtensionBase):
    """
    Angiography and Interventional Radiology metadata extraction.

    Extracts specialized angiography-related DICOM tags including:
    - X-ray angiography acquisition sequences
    - IVUS (Intravascular Ultrasound) imaging data
    - Interventional device and positioner information
    - Dose tracking and radiation metrics
    - Hemodynamic measurements and physiological data
    - Cardiac catheterization parameters
    - Fluoroscopy and contrast injection data
    """

    SPECIALTY = "angiography_interventional"
    FIELD_COUNT = 96
    REFERENCE = "DICOM PS3.3 (Angiography)"
    DESCRIPTION = "Angiography and Interventional Radiology specialized metadata extraction"
    VERSION = "1.0.0"

    # Angiography field definitions
    ANGIOGRAPHY_FIELDS = [
        # X-ray angiography acquisition
        "XRayAngiographicAcquisitionSequence",
        "XRay3DAcquisitionSequence",
        "XRayAxialAcquisitionSequence",
        "XAngle",
        "YAngle",
        "ZAngle",
        "RotationAngle",
        "PositionerMotion",
        "PositionerType",
        "PositionerPrimaryAngle",
        "PositionerSecondaryAngle",
        "PositionerScanArc",

        # Table and patient support
        "TableHeight",
        "TableHorizontalRotation",
        "TableHeadTilt",
        "TableCraneTilt",
        "TableLaterality",
        "TableLongitudinalPosition",
        "TableVerticalPosition",
        "TableHeadVerticalPosition",
        "TableLegVerticalPosition",

        # X-ray parameters
        "KVP",
        "XRayTubeCurrent",
        "Exposure",
        "ExposureTime",
        "ExposureInuAs",
        "PulseSequence",
        "PulseRate",
        "PulseWidth",
        "AveragePulseWidth",
        "NumberOfPulses",
        "FrameTime",
        "FrameTimeVector",

        # Fluoroscopy data
        "FluoroscopyFlag",
        "FluoroscopyMode",
        "FluoroscopyFrameRate",
        "FluoroscopyTotalTime",
        "FluoroscopyAcquisitionDose",
        "FluoroscopyDoseAreaProduct",
        "FluoroscopyEntranceDose",

        # Contrast and injection
        "ContrastBolusAgent",
        "ContrastBolusVolume",
        "ContrastBolusRoute",
        "ContrastBolusStartTime",
        "ContrastBolusStopTime",
        "ContrastBolusTotalDose",
        "ContrastFlowRate",
        "ContrastInjectionProtocol",
        "ContrastStartTime",
        "ContrastStopTime",
        "ContrastVolume",
        "ContrastAgent",

        # Cardiac catheterization
        "CardiacHeartRate",
        "CardiacNumberOfImages",
        "CardiacCycleLength",
        "CardiacGatingTime",
        "CardiacTriggerTime",
        "CardiacImagePosition",
        "CardiacImageType",
        "CardiacViewName",
        "CardiacProjection",

        # Hemodynamic measurements
        "HemodynamicSynchronizationSequence",
        "HemodynamicMeasurementSequence",
        "CardiacOutput",
        "EjectionFraction",
        "LeftVentricularVolume",
        "RightVentricularVolume",
        "StrokeVolume",
        "SystemicVascularResistance",
        "PulmonaryArteryPressure",
        "PulmonaryCapillaryWedgePressure",

        # IVUS imaging
        "IVUSAcquisitionSequence",
        "IVUSFrameRate",
        "IVUSPullbackRate",
        "IVUSPullbackSpeed",
        "IVUSCatheterSize",
        "IVUSCatheterType",
        "IVUSImagingMode",
        "IVUSDepth",
        "IVUSFieldOfView",
        "IVUSNumberOfFrames",

        # Interventional devices
        "InterventionalDeviceSequence",
        "InterventionalDeviceType",
        "InterventionalDeviceName",
        "InterventionalDeviceManufacturer",
        "InterventionalDeviceSize",
        "InterventionalDevicePosition",
        "InterventionalDeviceStatus",
        "StentType",
        "StentSize",
        "StentDeploymentPressure",
        "BalloonType",
        "BalloonSize",
        "BalloonInflationPressure",
        "BalloonInflationDuration",

        # Dose measurements
        "DoseAreaProduct",
        "DoseAreaProductSequence",
        "CumulativeDose",
        "CumulativeDoseSequence",
        "EntranceDose",
        "EntranceDoseInmGy",
        "ExposedArea",
        "ReferenceDose",
        "RelativeXRayExposure",

        # Radiation dose reporting
        "RadiationDoseSequence",
        "CTDIPhantomType",
        "CTDIvol",
        "DLP",
        "OrganDose",
        "EffectiveDose",
        "SkinDose",
        "SkinDoseSequence",

        # Image quality indicators
        "ImageQualityEvaluation",
        "ImageQualityValue",
        "SignalToNoiseRatio",
        "ContrastToNoiseRatio",
        "SpatialResolution",
        "TemporalResolution",

        # Acquisition timing
        "AcquisitionDateTime",
        "AcquisitionDuration",
        "AcquisitionTerminationCondition",
        "AcquisitionTerminationConditionData",
        "StudyStatus",
        "StudyCompletionStatus",

        # View and projection
        "ViewCodeSequence",
        "ViewModifierCodeSequence",
        "ProjectionEponymousName",
        "PatientOrientationCodeSequence",
        "PatientGantryRelationshipCodeSequence",

        # Additional angiographic parameters
        "DistanceSourceToPatient",
        "DistanceSourceToDetector",
        "ImagerPixelSpacing",
        "Grid",
        "GridAbsorptionRatio",
        "GeneratingEquipment",
        "DateOfLastCalibration",
        "TimeOfLastCalibration",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of angiography-specific DICOM field names"""
        return self.ANGIOGRAPHY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract angiography-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing angiography metadata extraction results
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

            # Detect if this is an angiography study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_angiography = (
                "angio" in series_desc or "angio" in study_desc or
                "dsa" in series_desc or "dsa" in study_desc or
                "intervention" in series_desc or "intervention" in study_desc or
                "cardiac" in series_desc or "cardiac" in study_desc or
                "cath" in series_desc or "cath" in study_desc or
                "ivus" in series_desc or "ivus" in study_desc or
                "fluoro" in series_desc or "fluoro" in study_desc or
                modality in ["XA", "RF", "US", "IVUS"]
            )

            metadata["is_angiography_study"] = is_angiography
            metadata["modality"] = modality

            # Extract angiography-specific fields
            fields_extracted = 0

            for field in self.ANGIOGRAPHY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add X-ray acquisition parameters if available
            if "XRayAngiographicAcquisitionSequence" in metadata or "KVP" in metadata:
                xray_params = self._extract_xray_parameters(dcm)
                metadata.update(xray_params)
                fields_extracted += len(xray_params)

            # Add fluoroscopy data if available
            if "FluoroscopyFlag" in metadata or "FluoroscopyMode" in metadata:
                fluoro_params = self._extract_fluoroscopy_parameters(dcm)
                metadata.update(fluoro_params)
                fields_extracted += len(fluoro_params)

            # Add contrast injection data if available
            if "ContrastBolusAgent" in metadata or "ContrastVolume" in metadata:
                contrast_params = self._extract_contrast_parameters(dcm)
                metadata.update(contrast_params)
                fields_extracted += len(contrast_params)

            # Add hemodynamic data if available
            if "CardiacHeartRate" in metadata or "HemodynamicMeasurementSequence" in metadata:
                hemodynamic_params = self._extract_hemodynamic_parameters(dcm)
                metadata.update(hemodynamic_params)
                fields_extracted += len(hemodynamic_params)

            # Add IVUS data if available
            if "IVUSAcquisitionSequence" in metadata or "IVUSFrameRate" in metadata:
                ivus_params = self._extract_ivus_parameters(dcm)
                metadata.update(ivus_params)
                fields_extracted += len(ivus_params)

            # Add interventional device data if available
            if "InterventionalDeviceSequence" in metadata or "StentType" in metadata:
                device_params = self._extract_interventional_device_parameters(dcm)
                metadata.update(device_params)
                fields_extracted += len(device_params)

            # Add dose measurements if available
            if "DoseAreaProduct" in metadata or "RadiationDoseSequence" in metadata:
                dose_params = self._extract_dose_parameters(dcm)
                metadata.update(dose_params)
                fields_extracted += len(dose_params)

            # Add warnings if this doesn't appear to be an angiography study
            if not is_angiography:
                warnings.append(
                    "This file may not be an angiography/interventional study. "
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
            logger.error(f"Angiography extraction failed for {filepath}: {e}")
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
        """Extract X-ray acquisition parameters"""
        params = {}

        # X-ray acquisition fields
        xray_fields = [
            "KVP",
            "XRayTubeCurrent",
            "Exposure",
            "ExposureTime",
            "PulseSequence",
            "PulseRate",
            "NumberOfPulses",
            "DistanceSourceToPatient",
            "DistanceSourceToDetector",
            "ImagerPixelSpacing",
        ]

        for field in xray_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"XRay_{field}"] = value

        return params

    def _extract_fluoroscopy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract fluoroscopy parameters"""
        params = {}

        # Fluoroscopy fields
        fluoro_fields = [
            "FluoroscopyMode",
            "FluoroscopyFrameRate",
            "FluoroscopyTotalTime",
            "FluoroscopyAcquisitionDose",
            "FluoroscopyDoseAreaProduct",
            "FluoroscopyEntranceDose",
        ]

        for field in fluoro_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Fluoroscopy_{field}"] = value

        return params

    def _extract_contrast_parameters(self, dcm) -> Dict[str, Any]:
        """Extract contrast injection parameters"""
        params = {}

        # Contrast injection fields
        contrast_fields = [
            "ContrastBolusAgent",
            "ContrastBolusVolume",
            "ContrastBolusRoute",
            "ContrastFlowRate",
            "ContrastInjectionProtocol",
            "ContrastStartTime",
            "ContrastStopTime",
        ]

        for field in contrast_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Contrast_{field}"] = value

        return params

    def _extract_hemodynamic_parameters(self, dcm) -> Dict[str, Any]:
        """Extract hemodynamic measurement parameters"""
        params = {}

        # Hemodynamic measurement fields
        hemodynamic_fields = [
            "CardiacHeartRate",
            "CardiacOutput",
            "EjectionFraction",
            "LeftVentricularVolume",
            "RightVentricularVolume",
            "StrokeVolume",
            "SystemicVascularResistance",
        ]

        for field in hemodynamic_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Hemodynamic_{field}"] = value

        return params

    def _extract_ivus_parameters(self, dcm) -> Dict[str, Any]:
        """Extract IVUS imaging parameters"""
        params = {}

        # IVUS fields
        ivus_fields = [
            "IVUSFrameRate",
            "IVUSPullbackRate",
            "IVUSPullbackSpeed",
            "IVUSCatheterSize",
            "IVUSCatheterType",
            "IVUSImagingMode",
            "IVUSDepth",
        ]

        for field in ivus_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"IVUS_{field}"] = value

        return params

    def _extract_interventional_device_parameters(self, dcm) -> Dict[str, Any]:
        """Extract interventional device parameters"""
        params = {}

        # Interventional device fields
        device_fields = [
            "InterventionalDeviceType",
            "InterventionalDeviceName",
            "InterventionalDeviceSize",
            "StentType",
            "StentSize",
            "StentDeploymentPressure",
            "BalloonType",
            "BalloonSize",
            "BalloonInflationPressure",
        ]

        for field in device_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Device_{field}"] = value

        return params

    def _extract_dose_parameters(self, dcm) -> Dict[str, Any]:
        """Extract radiation dose parameters"""
        params = {}

        # Dose measurement fields
        dose_fields = [
            "DoseAreaProduct",
            "CumulativeDose",
            "EntranceDose",
            "ReferenceDose",
            "CTDIvol",
            "DLP",
            "EffectiveDose",
            "SkinDose",
        ]

        for field in dose_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Dose_{field}"] = value

        return params

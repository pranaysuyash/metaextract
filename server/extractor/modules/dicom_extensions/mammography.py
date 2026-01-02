"""
Mammography and Breast Imaging DICOM Extension
Implements specialized metadata extraction for mammography and breast imaging studies
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


class MammographyBreastImagingExtension(DICOMExtensionBase):
    """
    Mammography and Breast Imaging metadata extraction.

    Extracts specialized mammography-related DICOM tags including:
    - Breast density and composition analysis
    - Calcification detection and classification
    - CAD (Computer-Aided Detection) results
    - Compression parameters and quality metrics
    - MQSA compliance and accreditation data
    - View positioning and laterality
    """

    SPECIALTY = "mammography_breast_imaging"
    FIELD_COUNT = 76
    REFERENCE = "DICOM PS3.3 (Mammography)"
    DESCRIPTION = "Mammography and Breast Imaging specialized metadata extraction"
    VERSION = "1.0.0"

    # Mammography field definitions
    MAMMOGRAPHY_FIELDS = [
        # Breast characteristics
        "BreastImplantPresent",
        "BreastSide",
        "BreastProcedureCodeSequence",
        "ImageLaterality",
        "ViewPosition",
        "ViewCodeSequence",
        "ViewModifierCodeSequence",

        # Localization and positioning
        "LocalizationTechniqueCodeSequence",
        "PositionerType",
        "PositionerPrimaryAngle",
        "PositionerSecondaryAngle",

        # Calcification analysis
        "CalcificationCodeSequence",
        "CalcificationDistributionCodeSequence",
        "CalcificationTypeCodeSequence",
        "DensityCodeSequence",

        # Mass analysis
        "MassShapeCodeSequence",
        "MassMarginsCodeSequence",
        "MassTextureCodeSequence",
        "MassInternalStructureCodeSequence",

        # Quality metrics
        "MammographyQualityScore",
        "ImageQualityScore",
        "DetectorTemperature",
        "DetectorType",
        "DetectorMode",

        # Frame and view information
        "FrameOfReferenceUID",
        "IrradiationEventUID",
        "SourceOfReference",
        "ReferencedImageSequence",

        # Calibration and quality control
        "CalibrationImage",
        "CalibrationObjectType",
        "CalibrationDateTime",
        "DateOfLastCalibration",
        "TimeOfLastCalibration",

        # CAD results
        "CadStudyClassification",
        "CadSeriesNumber",
        "CadFrameNumber",
        "CadFrameOrigin",
        "CadZLocationOffset",
        "CadImageColumnPositions",
        "CadImageRowPositions",

        # CAD algorithm information
        "AlgorithmParameters",
        "AlgorithmVersion",
        "AlgorithmName",
        "AlgorithmFamilyCodeSequence",
        "AlgorithmNameCodeSequence",
        "AlgorithmParametersCodeSequence",
        "AlgorithmColorCodeSequence",
        "AlgorithmProbabilityEstimateCodeSequence",
        "AlgorithmProbabilityUnitCodeSequence",
        "AlgorithmClassCodeSequence",
        "AlgorithmSourceCodeSequence",
        "AlgorithmVersionName",
        "AlgorithmDescription",

        # Keyhole and positioning
        "KeyholeCodeSequence",
        "CollimatorShapeCodeSequence",
        "CollimatorLeftVerticalEdge",
        "CollimatorRightVerticalEdge",
        "CollimatorUpperHorizontalEdge",
        "CollimatorLowerHorizontalEdge",

        # Dose and exposure
        "CentralAxisDistance",
        "SourceDistance",
        "BodyPartThickness",
        "CompressionForce",
        "PixelSpacingCalibrationType",
        "PixelSpacingCalibrationDescription",
        "DoseCalibrationFactor",

        # X-ray parameters
        "MetersetExposure",
        "BeamAreaXLimit",
        "BeamAreaYLimit",
        "RadiationMode",
        "XRayTubeCurrentInmA",
        "ExposureInmAs",
        "AveragePulseWidth",
        "RadiationSetting",
        "RectificationType",
        "XRayOutput",
        "HalfValueLayer",

        # Beam characteristics
        "LuminosityCentralRayPath",
        "BeamPathOffset",
        "BeamPathTilt",

        # Device information
        "AcquisitionDeviceTypeCodeSequence",
        "AcquisitionMethodCodeSequence",
        "AcquisitionMethodVersionSequence",
        "AcquisitionMethodParametersSequence",

        # MQSA compliance
        "FacilityName",
        "AccreditationStatus",
        "AccreditationNumber",
        "AccreditingBody",
        "MQSAComplianceFlag",

        # Additional breast imaging parameters
        "BreastDensity",
        "BreastComposition",
        "FibroglandularDenseTissue",
        "BreastImplantDescription",
        "ImplantType",
        "ImplantMaterial",

        # Tomosynthesis parameters
        "TomosynthesisNumberOfFrames",
        "TomosynthesisAngle",
        "TomosynthesisSliceThickness",
        "TomosynthesisSliceSpacing",
        "TomosynthesisTotalScanTime",

        # Magnetic resonance (breast MRI)
        "MRImagingSequence",
        "SequenceName",
        "ContrastBolusAgent",
        "ContrastBolusVolume",
        "ContrastBolusRoute",
        "ContrastBolusStartTime",
        "ContrastBolusStopTime",

        # Ultrasound (breast ultrasound)
        "TransducerFrequency",
        "TransducerType",
        "DepthOfScanField",
        "Gain",
        "DynamicRange",

        # Nuclear medicine (breast-specific NM)
        "Radiopharmaceutical",
        "RadiopharmaceuticalRoute",
        "InjectedDose",
        "UptakeValue",

        # Image processing
        "ImageProcessingSequence",
        "ImageProcessingType",
        "ImageProcessingParameters",
        "WindowCenter",
        "WindowWidth",
        "VOILUTFunction",

        # Presentation and display
        "PresentationLUTShape",
        "RescaleIntercept",
        "RescaleSlope",
        "RescaleType",

        # Archive and storage
        "ArchiveStatus",
        "StorageMediaFileSetUID",
        "RetrieveURL",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of mammography-specific DICOM field names"""
        return self.MAMMOGRAPHY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract mammography-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing mammography metadata extraction results
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

            # Detect if this is a mammography study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_mammography = (
                "mammo" in series_desc or "mammo" in study_desc or
                "breast" in series_desc or "breast" in study_desc or
                "mgs" in series_desc or "mgs" in study_desc or
                modality in ["MG", "US", "MR"] and "breast" in study_desc
            )

            metadata["is_mammography_study"] = is_mammography
            metadata["modality"] = modality

            # Extract mammography-specific fields
            fields_extracted = 0

            for field in self.MAMMOGRAPHY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add breast-specific analysis if available
            if "BreastSide" in metadata or "ImageLaterality" in metadata:
                breast_params = self._extract_breast_parameters(dcm)
                metadata.update(breast_params)
                fields_extracted += len(breast_params)

            # Add CAD analysis if available
            if "CadStudyClassification" in metadata or "AlgorithmName" in metadata:
                cad_params = self._extract_cad_parameters(dcm)
                metadata.update(cad_params)
                fields_extracted += len(cad_params)

            # Add quality metrics if available
            if "MammographyQualityScore" in metadata or "DetectorTemperature" in metadata:
                quality_params = self._extract_quality_parameters(dcm)
                metadata.update(quality_params)
                fields_extracted += len(quality_params)

            # Add compression parameters if available
            if "CompressionForce" in metadata or "BodyPartThickness" in metadata:
                compression_params = self._extract_compression_parameters(dcm)
                metadata.update(compression_params)
                fields_extracted += len(compression_params)

            # Add tomosynthesis parameters if available
            if "tomosynthesis" in series_desc:
                tomo_params = self._extract_tomosynthesis_parameters(dcm)
                metadata.update(tomo_params)
                fields_extracted += len(tomo_params)

            # Add warnings if this doesn't appear to be a mammography study
            if not is_mammography:
                warnings.append(
                    "This file may not be a mammography/breast imaging study. "
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
            logger.error(f"Mammography extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_breast_parameters(self, dcm) -> Dict[str, Any]:
        """Extract breast-specific analysis parameters"""
        params = {}

        # Breast characteristics
        breast_fields = [
            "BreastDensity",
            "BreastComposition",
            "FibroglandularDenseTissue",
            "BreastImplantPresent",
            "BreastImplantDescription",
            "ImageLaterality",
            "ViewPosition",
        ]

        for field in breast_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Breast_{field}"] = value

        return params

    def _extract_cad_parameters(self, dcm) -> Dict[str, Any]:
        """Extract CAD (Computer-Aided Detection) parameters"""
        params = {}

        # CAD analysis results
        cad_fields = [
            "CadStudyClassification",
            "AlgorithmName",
            "AlgorithmVersion",
            "AlgorithmProbabilityEstimateCodeSequence",
            "CadFrameNumber",
            "CadImageColumnPositions",
            "CadImageRowPositions",
        ]

        for field in cad_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"CAD_{field}"] = value

        return params

    def _extract_quality_parameters(self, dcm) -> Dict[str, Any]:
        """Extract quality control parameters"""
        params = {}

        # Quality metrics
        quality_fields = [
            "MammographyQualityScore",
            "ImageQualityScore",
            "DetectorTemperature",
            "DetectorType",
            "CalibrationDateTime",
            "DateOfLastCalibration",
            "TimeOfLastCalibration",
        ]

        for field in quality_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Quality_{field}"] = value

        return params

    def _extract_compression_parameters(self, dcm) -> Dict[str, Any]:
        """Extract compression and positioning parameters"""
        params = {}

        # Compression and positioning
        compression_fields = [
            "CompressionForce",
            "BodyPartThickness",
            "PositionerPrimaryAngle",
            "PositionerSecondaryAngle",
            "CentralAxisDistance",
            "SourceDistance",
        ]

        for field in compression_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Compression_{field}"] = value

        return params

    def _extract_tomosynthesis_parameters(self, dcm) -> Dict[str, Any]:
        """Extract tomosynthesis (3D mammography) parameters"""
        params = {}

        # Tomosynthesis specific fields
        tomo_fields = [
            "TomosynthesisNumberOfFrames",
            "TomosynthesisAngle",
            "TomosynthesisSliceThickness",
            "TomosynthesisSliceSpacing",
            "TomosynthesisTotalScanTime",
        ]

        for field in tomo_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Tomosynthesis_{field}"] = value

        return params
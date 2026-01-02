"""
CT and MRI Perfusion Imaging DICOM Extension
Implements specialized metadata extraction for CT and MRI perfusion studies
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

from .base import (
    DICOMExtensionBase,
    DICOMExtractionResult,
    safe_extract_dicom_field,
    get_dicom_file_info
)

logger = logging.getLogger(__name__)


class CTPerfusionExtension(DICOMExtensionBase):
    """
    CT and MRI Perfusion Imaging metadata extraction.

    Extracts specialized perfusion-related DICOM tags including:
    - Perfusion parameters and sequences
    - CT acquisition details
    - MR perfusion protocols
    - Contrast administration
    - Quantitative perfusion metrics
    """

    SPECIALTY = "ct_mri_perfusion"
    FIELD_COUNT = 92
    REFERENCE = "DICOM PS3.3 (CT/MRI)"
    DESCRIPTION = "CT and MRI perfusion imaging specialized metadata extraction"
    VERSION = "1.0.0"

    # Perfusion-specific field definitions based on DICOM standards
    PERFUSION_FIELDS = [
        # Perfusion sequences
        "PerfusionSeriesSequence",
        "CTPIVersion",
        "CTEfficiencyFactor",
        "CTWaterEquivalentDiameter",
        "CTAdditionalPlanesSeriesSequence",
        "MultiphasicExaminationSequence",
        "PatientPositionModifierSequence",

        # CT acquisition specifics
        "CTAcquisitionTypeSequence",
        "AcquisitionType",
        "TubeAngle",
        "CollimationType",
        "ReconstructionAlgorithmSequence",
        "ReconstructionMethod",
        "ReconstructionKernel",
        "ReconstructionKernelDescription",
        "ReconstructionFOVSequence",
        "ReconstructionFieldOfView",
        "ReconstructionCenter",
        "ReconstructionPixelSpacing",
        "WeightingFunction",
        "ReconstructionDescription",
        "RapidRodIntegrationSequence",

        # Physical measurements
        "DiameterOfSignalArea",
        "PhysicalEntitySize",
        "PhysicalEntityDiameter",
        "PhysicalEntitySizeRangeCodeSequence",
        "AcquisitionDuration",

        # Contrast administration
        "ContrastAdministrationOrderSequence",
        "ContrastBolusComponentSequence",
        "ContrastBolusIngredientSequence",
        "WaterEquivalentDegree",

        # Flow encoding (MRI)
        "FlowCompensationDirection",
        "FlowEncodingDirectionValue",
        "FlowEncodingGradientStrength",
        "FlowEncodingGradientStrengthSequence",
        "FlowEncodingTag",
        "FlowEncodingValue",
        "GradientsInVolume",

        # Image quality factors
        "SliceSensitivityFactor",
        "ParallelSummationFactor",
        "EffectiveEchoTime",
        "RadiofrequencyEchoPulseType",
        "RadiofrequencyEchoTrainLength",
        "GradientEchoTrainLength",

        # Safety parameters
        "SpecificAbsorptionRateValue",
        "SpecificAbsorptionRateSequence",
        "SARValue",
        "dBdtValue",

        # MR transmit coil
        "MRTransmitCoilSequence",
        "TransmitCoilManufacturerName",
        "TransmitCoilType",
        "TransmitCoilDescription",
        "TransmitCoilNativeName",
        "TransmitCoilFrequency",
        "TransmitCoilFrequencyOffset",
        "CoilFitMethod",
        "CoilConfiguration",

        # Phase contrast (MRI)
        "PhaseContrastDirection",
        "VelocityEncodingDirectionValue",
        "VelocityEncodingMinimumValue",
        "VelocityEncodingMaximumValue",
        "PhaseEncodingDirection",
        "PhaseEncodingDirectionPositive",
        "VelocityEncodingStep",

        # T2 mapping (MRI)
        "NumberOfT2Encodings",
        "T2EncodingDirectionValue",
        "T2EncodingStep",
        "SpectrallySelectedExcitation",
        "SpectralSpatialExcitation",
        "SpatialPresaturation",

        # MR technical parameters
        "TransmitterFrequency",
        "ResonantNucleus",
        "FrequencyCorrection",
        "MRStatusSequence",
        "BodyPartExamined",
        "PatientPosition",
        "PartialFourier",
        "PartialFourierDirection",
        "ParallelReductionFactorInPlane",
        "ParallelReductionFactorOutOfPlane",
        "ParallelReductionEvaluationSequence",

        # Advanced MR parameters
        "B1rms",
        "BNRData",
        "MultibandAccelerationFactor",
        "MultibandSequenceLabel",
        "MultibandNavigatorTiming",
        "MultibandIntegrationTime",
        "MultibandNavigatorFlipAngle",
        "ParallelReductionFactorSlab",

        # Additional CT contrast parameters
        "ContrastBolusAgent",
        "ContrastBolusRoute",
        "ContrastBolusVolume",
        "ContrastBolusStartTime",
        "ContrastBolusStopTime",
        "ContrastBolusTotalDose",
        "ContrastFlowRate",
        "ContrastFlowDuration",

        # Perfusion analysis
        "PerfusionAnalysisSequence",
        "BloodVolume",
        "BloodFlow",
        "MeanTransitTime",
        "TimeToPeak",
        "MaxSlope",
        "PerfusionMapSequence",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of perfusion-specific DICOM field names"""
        return self.PERFUSION_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract perfusion-specific metadata from CT/MRI DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing perfusion metadata extraction results
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

            # Detect if this is actually a perfusion study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()

            is_perfusion = (
                "perfusion" in series_desc or
                "perfusion" in safe_extract_dicom_field(dcm, "StudyDescription", "").lower() or
                "perf" in series_desc or
                "ctpi" in series_desc or
                "cbv" in series_desc or
                "cbf" in series_desc
            )

            metadata["is_perfusion_study"] = is_perfusion
            metadata["modality"] = modality

            # Extract perfusion-specific fields
            fields_extracted = 0

            for field in self.PERFUSION_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add CT-specific technical parameters if available
            if modality == "CT":
                ct_params = self._extract_ct_parameters(dcm)
                metadata.update(ct_params)
                fields_extracted += len(ct_params)

            # Add MR-specific technical parameters if available
            elif modality == "MR":
                mr_params = self._extract_mr_parameters(dcm)
                metadata.update(mr_params)
                fields_extracted += len(mr_params)

            # Add perfusion quantitative metrics if available
            if is_perfusion:
                perfusion_metrics = self._extract_perfusion_metrics(dcm)
                metadata.update(perfusion_metrics)
                fields_extracted += len(perfusion_metrics)

            # Add warnings if this doesn't appear to be a perfusion study
            if not is_perfusion:
                warnings.append(
                    "This file may not be a perfusion study. "
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
            logger.error(f"Perfusion extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_ct_parameters(self, dcm) -> Dict[str, Any]:
        """Extract CT-specific perfusion parameters"""
        params = {}

        # CT acquisition parameters
        ct_fields = [
            "KVP",
            "XRayTubeCurrent",
            "ExposureTime",
            "Exposure",
            "FilterType",
            "ConvolutionKernel",
            "RevolutionTime",
            "SingleCollimationWidth",
            "TotalCollimationWidth",
            "TableSpeed",
            "TableFeedPerRotation",
            "SpiralPitchFactor",
            "CalciumScoringFactor",
        ]

        for field in ct_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"CT_{field}"] = value

        return params

    def _extract_mr_parameters(self, dcm) -> Dict[str, Any]:
        """Extract MR-specific perfusion parameters"""
        params = {}

        # MR acquisition parameters
        mr_fields = [
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
            "PixelBandwidth",
        ]

        for field in mr_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"MR_{field}"] = value

        return params

    def _extract_perfusion_metrics(self, dcm) -> Dict[str, Any]:
        """Extract quantitative perfusion metrics"""
        metrics = {}

        # Look for perfusion map sequences and derived values
        perfusion_fields = [
            "PerfusionMapSequence",
            "BloodVolume",
            "BloodFlow",
            "MeanTransitTime",
            "TimeToPeak",
            "MaxSlope",
            "CerebralBloodVolume",
            "CerebralBloodFlow",
            "TimeToMaximum",
            "Delay",
            "MeanTransitTime",
            "RelativeCBV",
            "RelativeCBF",
        ]

        for field in perfusion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                metrics[f"Perfusion_{field}"] = value

        return metrics
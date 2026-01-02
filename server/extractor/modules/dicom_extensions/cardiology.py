"""
Cardiology and ECG/VCG DICOM Extension
Implements specialized metadata extraction for cardiology and ECG/VCG studies
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


class CardiologyECGExtension(DICOMExtensionBase):
    """
    Cardiology and ECG/VCG metadata extraction.

    Extracts specialized cardiology-related DICOM tags including:
    - Waveform data (ECG leads, VCG)
    - Cardiac timing parameters
    - ECG acquisition settings
    - Cardiac catheterization data
    - Hemodynamic measurements
    """

    SPECIALTY = "cardiology_ecg"
    FIELD_COUNT = 96
    REFERENCE = "DICOM PS3.3 (Cardiology)"
    DESCRIPTION = "Cardiology and ECG/VCG specialized metadata extraction"
    VERSION = "1.0.0"

    # Cardiology-specific field definitions
    CARDIOLOGY_FIELDS = [
        # Waveform sequences
        "WaveformSequence",
        "ChannelSequence",
        "WaveformSampleBits",
        "WaveformSampleData",
        "WaveformPaddingValue",
        "WaveformDataObjectType",
        "Timebase",
        "WaveformNumberOfTimes",
        "WaveformLength",

        # Channel settings
        "ChannelMinimumValue",
        "ChannelMaximumValue",
        "WaveformFilterDescription",
        "LowFilterValue",
        "HighFilterValue",
        "NumberOfWaveformFilters",
        "FilterConfigurationSequence",
        "FilterLength",
        "FilterType",
        "FilterOrder",

        # Frequency response
        "FilterFrequencyResponseSequence",
        "FilterRippleFrequencyResponse",
        "FilterAttenuationResponse",
        "FilterPhaseResponse",
        "TimebaseCodeSequence",

        # Frame organization
        "GroupOfFramesIdentificationSequence",
        "FrameIdentificationSequence",
        "TriggerSamplePosition",
        "DataFrameAssignmentSequence",

        # Data path management
        "DataPathID",
        "DataTargetPathID",
        "SignalFilterSequence",
        "SignalPropertySequence",
        "WaveformDataDescriptionSequence",
        "ChannelPropertiesSequence",

        # Filter specifications
        "FilterPassband",
        "FilterTransitionBand",
        "NotchFilterFrequency",
        "NotchFilterBandwidth",

        # DAC (Digital-to-Analog Converter) settings
        "DacValue",
        "DacSequence",
        "DacType",

        # Security and signatures
        "DigitalSignatureSequence",
        "CertificateType",
        "DigitalSignatureDateTime",
        "DigitalSignature",
        "CertificateOfSigner",
        "Signature",
        "SignedContentDateTime",
        "SignedContentCreator",

        # Application metadata
        "ApplicationName",
        "ApplicationVersion",
        "ApplicationManufacturer",

        # Algorithm information
        "AlgorithmType",
        "AlgorithmName",
        "ArbitrarySeriesDescription",

        # Patient orientation
        "PatientOrientationSequence",

        # Counting parameters
        "UselessDataValue",
        "PrimaryPromptsPerSecond",
        "SecondaryCountsPerSecond",
        "FrameType",

        # Reference channels
        "ReferenceChannelZeroSequence",

        # Audio channels (for multimedia data)
        "MultiplexedAudioChannelsDescriptionCodeSequence",
        "MultiplexGroupLabel",

        # Matrix dimensions
        "TotalPixelMatrixColumns",
        "TotalPixelMatrixRows",

        # Image processing
        "AppliedMaskSubtractionSequence",
        "MaskFrameNumbers",
        "StartRow",
        "EndRow",
        "StartColumn",
        "EndColumn",

        # Frame analysis
        "FrameOfInterestDescription",
        "FrameOfInterestType",
        "MaskSubtractionDeliveryTechnique",
        "MaskSubtractionImageFrameSequence",

        # Algorithm details
        "AlgorithmFamilyCodeSequence",
        "AlgorithmNameCodeSequence",
        "AlgorithmParametersCodeSequence",

        # Geometric data
        "CharacteristicPoint",
        "Angle",
        "PointIndex",
        "ColumnPositionInTotalImageMatrix",
        "RowPositionInTotalImageMatrix",

        # Coding sequences
        "CCodeSequence",
        "MCodeSequence",
        "TargetPositionSequence",

        # Display environment
        "DisplayEnvironmentType",
        "DisplayShadingModel",

        # Cardiac-specific measurements
        "HeartRate",
        "RRInterval",
        "PRInterval",
        "QRSInterval",
        "QTInterval",
        "QTcInterval",
        "PAxis",
        "TAxis",
        "QRSAxis",

        # ECG lead data
        "NumberOfLeads",
        "LeadConfiguration",
        "LeadDataSequence",
        "LeadArray",

        # Cardiac timing
        "CardiacBeatRejectionTechnique",
        "BeatRejectionFlag",
        "LowRRValue",
        "HighRRValue",
        "IntervalsAcquired",
        "IntervalsRejected",
        "PVCRejection",
        "SkipBeats",

        # Triggering information
        "TriggerTime",
        "TriggerSourceOrType",
        "NominalInterval",
        "FrameTime",
        "CardiacFramingType",
        "FrameTimeVector",
        "FrameDelay",
        "ImageTriggerDelay",
        "MultiplexGroupTimeOffset",
        "TriggerTimeOffset",

        # Synchronization
        "SynchronizationTrigger",
        "SynchronizationChannel",
        "TriggerSamplePosition",

        # Radiopharmaceutical (for nuclear cardiology)
        "RadiopharmaceuticalRoute",
        "RadiopharmaceuticalVolume",
        "RadiopharmaceuticalStartTime",
        "RadiopharmaceuticalStopTime",
        "RadionuclideTotalDose",
        "RadionuclideHalfLife",
        "RadionuclidePositronFraction",
        "RadiopharmaceuticalSpecificActivity",
        "RadiopharmaceuticalStartDateTime",
        "RadiopharmaceuticalStopDateTime",

        # Stress test data
        "PharmacologicallyInducedStress",
        "StressAgent",
        "StressAgentCodeSequence",
        "StressAgentName",
        "StartMeanArterialPressure",
        "EndMeanArterialPressure",
        "StartCardiacBloodPressure",
        "EndCardiacBloodPressure",
        "StartHeartRate",
        "EndHeartRate",
        "StartRespiratoryRate",
        "EndRespiratoryRate",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of cardiology-specific DICOM field names"""
        return self.CARDIOLOGY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract cardiology-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing cardiology metadata extraction results
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

            # Detect if this is a cardiology study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_cardiology = (
                "ecg" in series_desc or "ecg" in study_desc or
                "cardiac" in series_desc or "cardiac" in study_desc or
                "echo" in series_desc or "echo" in study_desc or
                "cath" in series_desc or "cath" in study_desc or
                "hemodynamic" in series_desc or "hemodynamic" in study_desc or
                modality in ["ECG", "HD", "EPS"]
            )

            metadata["is_cardiology_study"] = is_cardiology
            metadata["modality"] = modality

            # Extract cardiology-specific fields
            fields_extracted = 0

            for field in self.CARDIOLOGY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add ECG-specific parameters if available
            if "HeartRate" in metadata or "RRInterval" in metadata:
                ecg_params = self._extract_ecg_parameters(dcm)
                metadata.update(ecg_params)
                fields_extracted += len(ecg_params)

            # Add cardiac catheterization parameters if available
            if "cath" in series_desc or "hemodynamic" in series_desc:
                cath_params = self._extract_catheterization_parameters(dcm)
                metadata.update(cath_params)
                fields_extracted += len(cath_params)

            # Add waveform data if available
            if "WaveformSequence" in metadata or "ChannelSequence" in metadata:
                waveform_params = self._extract_waveform_parameters(dcm)
                metadata.update(waveform_params)
                fields_extracted += len(waveform_params)

            # Add warnings if this doesn't appear to be a cardiology study
            if not is_cardiology:
                warnings.append(
                    "This file may not be a cardiology study. "
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
            logger.error(f"Cardiology extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_ecg_parameters(self, dcm) -> Dict[str, Any]:
        """Extract ECG-specific parameters"""
        params = {}

        # ECG intervals and measurements
        ecg_fields = [
            "NumberOfWaveformSamples",
            "MultiplexGroupLabel",
            "SynchronizationChannel",
            "TriggerSamplePosition",
        ]

        for field in ecg_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"ECG_{field}"] = value

        return params

    def _extract_catheterization_parameters(self, dcm) -> Dict[str, Any]:
        """Extract cardiac catheterization parameters"""
        params = {}

        # Hemodynamic measurements
        cath_fields = [
            "ProcedureCodeSequence",
            "ReasonForPerformedProcedureCodeSequence",
            "TargetParametricSite",
            "ParametricSite",
            "RadiopharmaceuticalAgent",
            "InterventionDrugInformationSequence",
        ]

        for field in cath_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Cath_{field}"] = value

        return params

    def _extract_waveform_parameters(self, dcm) -> Dict[str, Any]:
        """Extract waveform data parameters"""
        params = {}

        # Waveform technical parameters
        wave_fields = [
            "SamplingFrequency",
            "TriggerSamplePosition",
            "MultiplexGroupTimeOffset",
        ]

        for field in wave_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Waveform_{field}"] = value

        return params
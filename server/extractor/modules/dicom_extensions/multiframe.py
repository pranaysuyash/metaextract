"""
Multi-frame and Functional Groups DICOM Extension
Implements specialized metadata extraction for multi-frame images and functional groups
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


class MultiframeFunctionalGroupsExtension(DICOMExtensionBase):
    """
    Multi-frame and Functional Groups metadata extraction.

    Extracts specialized multi-frame-related DICOM tags including:
    - Multi-frame image organization and structure
    - Functional groups and shared functional groups
    - Per-frame and per-stack functional groups
    - Frame timing and temporal information
    - Frame anatomy and position
    - Dimension organization and vector parameters
    - Frame pixel data and transformation
    - Dynamic imaging and cine sequences
    """

    SPECIALTY = "multiframe_functional_groups"
    FIELD_COUNT = 79
    REFERENCE = "DICOM PS3.3 (Multi-frame)"
    DESCRIPTION = "Multi-frame and Functional Groups specialized metadata extraction"
    VERSION = "1.0.0"

    # Multi-frame field definitions
    MULTIFRAME_FIELDS = [
        # Multi-frame organization
        "NumberOfFrames",
        "ConcatenationUID",
        "InConcatenationNumber",
        "InConcatenationTotalNumber",
        "ConcatenationFrameOffsetNumber",
        "SharedFunctionalGroupsSequence",
        "PerFrameFunctionalGroupsSequence",

        # Dimension organization
        "DimensionOrganizationSequence",
        "DimensionIndexSequence",
        "DimensionOrganizationUID",
        "DimensionIndexPointer",
        "DimensionDescriptionLabel",

        # Frame identification
        "FrameIncrementPointer",
        "FrameVOILUTSequence",
        "FramePixelShiftSequence",
        "FrameDimensionOrganizationSequence",
        "StackID",
        "InStackPositionNumber",
        "TemporalPositionIndex",
        "StackPositionIndex",

        # Frame timing
        "FrameTime",
        "FrameTimeVector",
        "FrameDelay",
        "FrameAcquisitionDateTime",
        "FrameAcquisitionDuration",
        "FrameReferenceDateTime",
        "FrameDuration",
        "FrameAcquisitionNumber",
        "FrameComments",

        # Multi-frame pixel data
        "PixelData",
        "NumberOfFrames",
        "FramePixelDataSequence",
        "PixelDataProviderURL",
        "PixelRepresentation",
        "PlanarConfiguration",
        "PixelAspectRatio",
        "FramePixelShiftSequence",

        # Functional groups sequences
        "SharedFunctionalGroupsSequence",
        "PerFrameFunctionalGroupsSequence",
        "DerivedPixelData",
        "DerivedPixelDataSequence",

        # Frame content and identification
        "FrameContentSequence",
        "FrameLabel",
        "FrameLaterality",
        "FrameAnatomySequence",
        "FrameType",
        "FrameAcquisitionContext",
        "FrameAcquisitionDescription",
        "FrameComments",

        # Image frame type
        "ImageType",
        "AcquisitionType",
        "AcquisitionNumber",
        "AcquisitionDate",
        "AcquisitionTime",
        "ViewType",
        "ViewCodeSequence",

        # Position and orientation
        "ImagePositionPatient",
        "ImageOrientationPatient",
        "FrameOfReferenceUID",
        "TemporalPositionIndex",
        "TriggerTime",
        "TriggerDelayTime",
        "CardiacSynchronizationSequence",

        # Frame anatomy
        "FrameAnatomySequence",
        "RegionOfInterestSequence",
        "FrameAnatomicStructure",
        "Laterality",
        "PatientOrientationCodeSequence",

        # Pixel intensity transformations
        "PixelValueTransformationSequence",
        "PixelIntensityRelationship",
        "PixelIntensityRelationshipSign",
        "RescaleIntercept",
        "RescaleSlope",
        "RescaleType",

        # Frame VOI LUT
        "FrameVOILUTSequence",
        "WindowCenter",
        "WindowWidth",
        "WindowCenterWidthExplanation",
        "VOILUTSequence",
        "VOILUTFunction",

        # Frame pixel spacing
        "PixelSpacing",
        "PixelSpacingCalibrationType",
        "PixelSpacingCalibrationDescription",
        "ImagerPixelSpacing",
        "FramePixelSpacingSequence",

        # Frame display
        "RecommendedDisplayFrameRate",
        "FrameDisplaySequence",
        "CineDisplayRate",
        "PreferredPlaybackSequencing",

        # Temporal and dynamic imaging
        "TemporalResolution",
        "TemporalPositionIndex",
        "TemporalPositionTimeOffset",
        "TemporalPositionIdentifier",
        "NumberOfTemporalPositions",
        "TemporalPositionType",

        # Cardiac imaging
        "CardiacSynchronizationTechnique",
        "CardiacBeatRejectionTechnique",
        "HeartRate",
        "TriggerTime",
        "TriggerDelay",
        "CardiacCyclePosition",

        # Respiratory imaging
        "RespiratorySynchronizationTechnique",
        "RespiratoryCyclePosition",
        "RespiratoryTriggerType",
        "RespiratoryTriggerDelay",

        # Frame stacking
        "StackID",
        "InStackPositionNumber",
        "StackPositionIndex",
        "StackDescription",

        # Image plane and volume
        "ImagePlane",
        "ImageVolume",
        "ImagedVolumeWidth",
        "ImagedVolumeHeight",
        "ImagedVolumeDepth",

        # Derivation and source images
        "DerivationImageSequence",
        "SourceImageSequence",
        "DerivationCodeSequence",
        "DerivationDescription",

        # Frame annotations
        "FrameAnnotationSequence",
        "GraphicAnnotationSequence",
        "TextObjectSequence",
        "GraphicObjectSequence",

        # Additional multi-frame parameters
        "FrameDimensionOrganizationSequence",
        "DimensionOrganizationType",
        "DimensionOrganizationUID",
        "FrameDimensionPointer",
        "FrameLabel",

        # Reconstruction and processing
        "ReconstructionAlgorithm",
        "ReconstructionDiameter",
        "ReconstructionPixelSpacing",
        "ReconstructionAngle",
        "ReconstructionMethod",

        # Quality control
        "ImageQualityIndicator",
        "FrameQualityIndicator",
        "ArtifactMetricSequence",

        # Additional functional groups
        "UnassignedSharedConvertedAttributesSequence",
        "UnassignedPerFrameConvertedAttributesSequence",
        "PrivateSharedConvertedAttributesSequence",
        "PrivatePerFrameConvertedAttributesSequence",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of multi-frame-specific DICOM field names"""
        return self.MULTIFRAME_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract multi-frame-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing multi-frame metadata extraction results
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

            # Detect if this is a multi-frame study
            num_frames = safe_extract_dicom_field(dcm, "NumberOfFrames", 1)

            is_multiframe = (
                num_frames > 1 or
                "SharedFunctionalGroupsSequence" in dcm or
                "PerFrameFunctionalGroupsSequence" in dcm or
                "DimensionOrganizationSequence" in dcm
            )

            metadata["is_multiframe_study"] = is_multiframe
            metadata["number_of_frames"] = num_frames

            # Extract multi-frame-specific fields
            fields_extracted = 0

            for field in self.MULTIFRAME_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add frame organization analysis if available
            if "NumberOfFrames" in metadata or "SharedFunctionalGroupsSequence" in metadata:
                frame_org_params = self._extract_frame_organization_parameters(dcm)
                metadata.update(frame_org_params)
                fields_extracted += len(frame_org_params)

            # Add functional groups analysis if available
            if "SharedFunctionalGroupsSequence" in metadata or "PerFrameFunctionalGroupsSequence" in metadata:
                functional_params = self._extract_functional_groups_parameters(dcm)
                metadata.update(functional_params)
                fields_extracted += len(functional_params)

            # Add temporal analysis if available
            if "FrameTime" in metadata or "TemporalPositionIndex" in metadata:
                temporal_params = self._extract_temporal_parameters(dcm)
                metadata.update(temporal_params)
                fields_extracted += len(temporal_params)

            # Add dimension organization if available
            if "DimensionOrganizationSequence" in metadata or "DimensionIndexSequence" in metadata:
                dimension_params = self._extract_dimension_parameters(dcm)
                metadata.update(dimension_params)
                fields_extracted += len(dimension_params)

            # Add frame content analysis if available
            if "FrameContentSequence" in metadata or "FrameAnatomySequence" in metadata:
                content_params = self._extract_frame_content_parameters(dcm)
                metadata.update(content_params)
                fields_extracted += len(content_params)

            # Add warnings if this doesn't appear to be a multi-frame study
            if not is_multiframe:
                warnings.append(
                    "This file may not be a multi-frame study. "
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
            logger.error(f"Multi-frame extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_frame_organization_parameters(self, dcm) -> Dict[str, Any]:
        """Extract frame organization parameters"""
        params = {}

        # Frame organization fields
        org_fields = [
            "NumberOfFrames",
            "ConcatenationUID",
            "InConcatenationNumber",
            "InConcatenationTotalNumber",
            "StackID",
            "InStackPositionNumber",
        ]

        for field in org_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"FrameOrg_{field}"] = value

        return params

    def _extract_functional_groups_parameters(self, dcm) -> Dict[str, Any]:
        """Extract functional groups parameters"""
        params = {}

        # Functional groups fields
        functional_fields = [
            "SharedFunctionalGroupsSequence",
            "PerFrameFunctionalGroupsSequence",
            "DerivationImageSequence",
            "SourceImageSequence",
            "PixelValueTransformationSequence",
        ]

        for field in functional_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Functional_{field}"] = value

        return params

    def _extract_temporal_parameters(self, dcm) -> Dict[str, Any]:
        """Extract temporal parameters"""
        params = {}

        # Temporal fields
        temporal_fields = [
            "FrameTime",
            "FrameTimeVector",
            "FrameDelay",
            "TemporalPositionIndex",
            "TemporalPositionTimeOffset",
            "NumberOfTemporalPositions",
        ]

        for field in temporal_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Temporal_{field}"] = value

        return params

    def _extract_dimension_parameters(self, dcm) -> Dict[str, Any]:
        """Extract dimension organization parameters"""
        params = {}

        # Dimension organization fields
        dimension_fields = [
            "DimensionOrganizationSequence",
            "DimensionIndexSequence",
            "DimensionOrganizationUID",
            "DimensionIndexPointer",
            "DimensionDescriptionLabel",
        ]

        for field in dimension_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Dimension_{field}"] = value

        return params

    def _extract_frame_content_parameters(self, dcm) -> Dict[str, Any]:
        """Extract frame content parameters"""
        params = {}

        # Frame content fields
        content_fields = [
            "FrameContentSequence",
            "FrameLabel",
            "FrameLaterality",
            "FrameAnatomySequence",
            "FrameType",
            "FrameAcquisitionDescription",
        ]

        for field in content_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"FrameContent_{field}"] = value

        return params

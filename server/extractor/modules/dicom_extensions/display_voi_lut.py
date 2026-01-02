"""
Display and VOI LUT DICOM Extension
Implements specialized metadata extraction for display and Value of Interest (VOI) transformations
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


class DisplayVOIExtension(DICOMExtensionBase):
    """
    Display and VOI LUT metadata extraction.

    Extracts specialized display-related DICOM tags including:
    - VOI LUT (Value of Interest Lookup Table) transformations
    - Window center and width parameters
    - Presentation LUT and display settings
    - Color palette and color mapping
    - Pixel intensity transformations
    - Image display and rendering parameters
    - Spatial calibration and scaling
    - Annotation and overlay information
    """

    SPECIALTY = "display_voi_lut"
    FIELD_COUNT = 94
    REFERENCE = "DICOM PS3.3 (Display)"
    DESCRIPTION = "Display and VOI LUT specialized metadata extraction"
    VERSION = "1.0.0"

    # Display and VOI LUT field definitions
    DISPLAY_FIELDS = [
        # VOI LUT transformations
        "VOILUTSequence",
        "VOILUTDescriptor",
        "VOILUTExplanation",
        "VOILUTFunction",
        "WindowCenter",
        "WindowWidth",
        "WindowCenterWidthExplanation",
        "RecommendedViewingModeType",

        # Pixel intensity transformations
        "RescaleIntercept",
        "RescaleSlope",
        "RescaleType",
        "PixelIntensityRelationship",
        "PixelIntensityRelationshipSign",
        "PixelValueTransformationSequence",

        # Presentation LUT
        "PresentationLUTSequence",
        "PresentationLUTShape",
        "PresentationLUTDescriptor",
        "PresentationLUTExplanation",

        # Color palette and mapping
        "PaletteColorLookupTableUID",
        "PaletteColorLookupTableSequence",
        "SegmentedPaletteColorLookupTableUID",
        "SegmentedPaletteColorLookupTableSequence",
        "BreathingSuppressionHold",
        "BreathingSignalSequence",
        "BreathingSignal",
        "BreathingSignalSourceID",

        # Image display parameters
        "ImagePresentationComments",
        "PresentationDisplayCollectionUID",
        "PresentationDisplayCollectionSequence",
        "PresentationSequence",
        "DisplaySetLabel",
        "DisplaySetNumber",
        "PresentationDisplayNumber",

        # Spatial calibration
        "PixelSpacing",
        "PixelSpacingCalibrationType",
        "PixelSpacingCalibrationDescription",
        "ImagerPixelSpacing",
        "PixelAspectRatio",
        "NominalScannedPixelSpacing",

        # Scaling and transformations
        "PixelSpacingSequence",
        "PixelSpacingInSpatialCoordinates",
        "AspectRatio",
        "AspectRatioInformation",
        "SpatialResolution",
        "ImagePositionPatient",
        "ImageOrientationPatient",
        "SliceThickness",
        "SliceLocation",

        # Anatomical orientation
        "ImageOrientationLabel",
        "PatientOrientation",
        "PatientOrientationCodeSequence",
        "PatientGantryRelationshipCodeSequence",
        "ViewCodeSequence",
        "ViewModifierCodeSequence",

        # Display and rendering
        "BurnedInAnnotation",
        "RecognizableVisualFeatures",
        "QualityControlImage",
        "ImageQualityGrade",
        "ArtifactPresent",
        "ArtifactDescription",

        # Overlay data
        "OverlaySequence",
        "OverlayRows",
        "OverlayColumns",
        "OverlayDescription",
        "OverlayType",
        "OverlaySubtype",
        "OverlayOrigin",
        "OverlayBitsAllocated",
        "OverlayBitPosition",
        "OverlayData",
        "OverlayLabel",
        "OverlayDataDescription",

        # Curve data
        "CurveSequence",
        "CurveDescriptor",
        "CurveData",
        "CurveType",
        "CurveLabel",

        # Modality LUT
        "ModalityLUTSequence",
        "ModalityLUTDescriptor",
        "ModalityLUTType",
        "ModalityLUTData",
        "LUTDescriptor",
        "LUTExplanation",
        "LUTData",
        "LUTFunction",

        # Color and display
        "RedPaletteColorLookupTableDescriptor",
        "GreenPaletteColorLookupTableDescriptor",
        "BluePaletteColorLookupTableDescriptor",
        "RedPaletteColorLookupTableData",
        "GreenPaletteColorLookupTableData",
        "BluePaletteColorLookupTableData",
        "ICCProfile",
        "ColorSpace",

        # Image plane
        "ImagePlane",
        "ImagePosition",
        "ImageOrientation",
        "PixelSpacing",
        "FrameOfReferenceUID",

        # Display shutter
        "ShutterShape",
        "ShutterLeftVerticalEdge",
        "ShutterRightVerticalEdge",
        "ShutterUpperHorizontalEdge",
        "ShutterLowerHorizontalEdge",
        "ShutterPresentationValue",
        "ShutterOverlayGroup",

        # Display annotations
        "TextString",
        "TextBox",
        "TextBoxSequence",
        "TextJustification",
        "TextBoxAlignment",
        "AnnotationSequence",
        "GraphicAnnotationSequence",

        # Image transformation
        "TransformLabel",
        "TransformDescription",
        "TransformVersion",
        "TransformPersistence",
        "TransformOrder",

        # Real-time display
        "RealTimeDisplay",
        "DisplayFrameRate",
        "FrameDelay",
        "TriggerTime",

        # Stereoscopic display
        "StereoBaseline",
        "StereoBaseAngle",
        "StereoPresentationFlag",
        "MonoscopicDisplayOption",

        # Display environment
        "DisplayEnvironmentSpatialPosition",
        "AmbientLightIntensity",
        "ReflectedAmbientLight",
        "PerceivedLight",

        # Additional display parameters
        "SoftcopyPresentationLUTSequence",
        "SoftcopyVOILUTSequence",
        "ImageOrientationSlide",
        "TopLeftHandedness",
        "MatrixX",
        "MatrixY",
        "MatrixZ",

        # Color Doppler display
        "VelocityEncodeDirection",
        "VelocityEncodeMinimum",
        "VelocityEncodeMaximum",
        "AliasConditionDescription",

        # Image quality metrics
        "SignalToNoiseRatio",
        "ContrastToNoiseRatio",
        "ArtifactMetricSequence",
        "ImagePresentationTitle",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of display-specific DICOM field names"""
        return self.DISPLAY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract display-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing display metadata extraction results
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

            # Extract display-specific fields
            fields_extracted = 0

            for field in self.DISPLAY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add VOI LUT analysis if available
            if "WindowCenter" in metadata or "VOILUTSequence" in metadata:
                voi_params = self._extract_voi_parameters(dcm)
                metadata.update(voi_params)
                fields_extracted += len(voi_params)

            # Add pixel intensity transformations if available
            if "RescaleIntercept" in metadata or "PixelIntensityRelationship" in metadata:
                intensity_params = self._extract_intensity_parameters(dcm)
                metadata.update(intensity_params)
                fields_extracted += len(intensity_params)

            # Add presentation LUT analysis if available
            if "PresentationLUTSequence" in metadata or "PresentationLUTShape" in metadata:
                presentation_params = self._extract_presentation_parameters(dcm)
                metadata.update(presentation_params)
                fields_extracted += len(presentation_params)

            # Add color palette analysis if available
            if "PaletteColorLookupTableUID" in metadata or "RedPaletteColorLookupTableData" in metadata:
                color_params = self._extract_color_parameters(dcm)
                metadata.update(color_params)
                fields_extracted += len(color_params)

            # Add spatial calibration if available
            if "PixelSpacing" in metadata or "ImageOrientationPatient" in metadata:
                spatial_params = self._extract_spatial_parameters(dcm)
                metadata.update(spatial_params)
                fields_extracted += len(spatial_params)

            # Add overlay analysis if available
            if "OverlaySequence" in metadata or "OverlayData" in metadata:
                overlay_params = self._extract_overlay_parameters(dcm)
                metadata.update(overlay_params)
                fields_extracted += len(overlay_params)

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
            logger.error(f"Display extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_voi_parameters(self, dcm) -> Dict[str, Any]:
        """Extract VOI LUT parameters"""
        params = {}

        # VOI LUT fields
        voi_fields = [
            "WindowCenter",
            "WindowWidth",
            "WindowCenterWidthExplanation",
            "VOILUTSequence",
            "VOILUTFunction",
            "RecommendedViewingModeType",
        ]

        for field in voi_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"VOI_{field}"] = value

        return params

    def _extract_intensity_parameters(self, dcm) -> Dict[str, Any]:
        """Extract pixel intensity transformation parameters"""
        params = {}

        # Intensity transformation fields
        intensity_fields = [
            "RescaleIntercept",
            "RescaleSlope",
            "RescaleType",
            "PixelIntensityRelationship",
            "PixelIntensityRelationshipSign",
        ]

        for field in intensity_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Intensity_{field}"] = value

        return params

    def _extract_presentation_parameters(self, dcm) -> Dict[str, Any]:
        """Extract presentation LUT parameters"""
        params = {}

        # Presentation LUT fields
        presentation_fields = [
            "PresentationLUTSequence",
            "PresentationLUTShape",
            "PresentationLUTDescriptor",
            "PresentationLUTExplanation",
            "SoftcopyPresentationLUTSequence",
        ]

        for field in presentation_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Presentation_{field}"] = value

        return params

    def _extract_color_parameters(self, dcm) -> Dict[str, Any]:
        """Extract color palette parameters"""
        params = {}

        # Color palette fields
        color_fields = [
            "PaletteColorLookupTableUID",
            "RedPaletteColorLookupTableDescriptor",
            "GreenPaletteColorLookupTableDescriptor",
            "BluePaletteColorLookupTableDescriptor",
            "ICCProfile",
            "ColorSpace",
        ]

        for field in color_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Color_{field}"] = value

        return params

    def _extract_spatial_parameters(self, dcm) -> Dict[str, Any]:
        """Extract spatial calibration parameters"""
        params = {}

        # Spatial calibration fields
        spatial_fields = [
            "PixelSpacing",
            "PixelSpacingCalibrationType",
            "ImagePositionPatient",
            "ImageOrientationPatient",
            "SliceThickness",
            "SliceLocation",
            "ImageOrientationLabel",
        ]

        for field in spatial_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Spatial_{field}"] = value

        return params

    def _extract_overlay_parameters(self, dcm) -> Dict[str, Any]:
        """Extract overlay parameters"""
        params = {}

        # Overlay fields
        overlay_fields = [
            "OverlaySequence",
            "OverlayRows",
            "OverlayColumns",
            "OverlayDescription",
            "OverlayType",
            "OverlayLabel",
        ]

        for field in overlay_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Overlay_{field}"] = value

        return params

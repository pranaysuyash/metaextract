"""
Endoscopy DICOM Extension
Implements specialized metadata extraction for endoscopic imaging studies
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


class EndoscopyExtension(DICOMExtensionBase):
    """
    Endoscopy metadata extraction.

    Extracts specialized endoscopy-related DICOM tags including:
    - Endoscopic device and instrument information
    - Visualization and illumination parameters
    - Procedure and intervention details
    - Anatomical location and positioning
    - Image enhancement and processing
    - Measurement and analysis tools
    - Video and recording parameters
    - Gastrointestinal, bronchoscopy, and other specialty endoscopy
    """

    SPECIALTY = "endoscopy"
    FIELD_COUNT = 72
    REFERENCE = "DICOM PS3.3 (Endoscopy)"
    DESCRIPTION = "Endoscopy specialized metadata extraction"
    VERSION = "1.0.0"

    # Endoscopy field definitions
    ENDOSCOPY_FIELDS = [
        # Endoscopic device information
        "EndoscopeType",
        "EndoscopeModel",
        "EndoscopeManufacturer",
        "EndoscopeSerialNumber",
        "EndoscopeDiameter",
        "EndoscopeLength",
        "EndoscopeTipType",
        "EndoscopeNumberOfChannels",
        "AccessoryDevice",
        "AccessoryDeviceType",
        "AccessoryDeviceModel",
        "AccessoryDeviceManufacturer",

        # Visualization and illumination
        "IlluminationType",
        "IlluminationColor",
        "IlluminationIntensity",
        "LightSourceModel",
        "LightSourceManufacturer",
        "LightSourceType",
        "LightSourceWavelength",
        "VisualizationMode",
        "VisualizationTechnique",
        "NarrowBandImaging",
        "AutoFluorescenceImaging",
        "Chromoendoscopy",
        "VirtualChromoendoscopy",

        # Imaging parameters
        "MagnificationFactor",
        "FocusDistance",
        "DepthOfField",
        "FieldOfView",
        "AngleOfView",
        "ViewingDirection",
        "DistortionCorrection",
        "ImageOrientation",
        "ImageFlip",
        "ImageRotation",

        # Procedure information
        "ProcedureType",
        "ProcedureIndication",
        "ProcedureDescription",
        "ProcedureDate",
        "ProcedureTime",
        "ProcedureStatus",
        "ProcedureTermination",
        "ProcedureComplications",
        "ProcedureComments",

        # Anatomical location
        "AnatomicRegionSequence",
        "AnatomicStructure",
        "AnatomicLocation",
        "AnatomicLaterality",
        "AccessRoute",
        "InsertionLength",
        "AdvancementDistance",
        "DepthOfInsertion",
        "LesionLocation",
        "LesionSize",
        "LesionCharacteristics",

        # Gastrointestinal endoscopy
        "GIType",
        "GIProcedure",
        "GILocation",
        "GIFindings",
        "GITreatment",
        "GISeverity",
        "GIBiopsySample",
        "GIBiopsyLocation",
        "GIBiopsyNumber",

        # Bronchoscopy
        "BronchoscopyType",
        "BronchoscopyProcedure",
        "AirwayLocation",
        "AirwayDiameter",
        "AirwayObstruction",
        "BronchoscopyFindings",
        "BronchoscopyTreatment",
        "TransbronchialBiopsy",
        "NeedleAspiration",

        # Image enhancement
        "ImageEnhancement",
        "ContrastEnhancement",
        "EdgeEnhancement",
        "SurfaceEnhancement",
        "VascularPatternEnhancement",
        "PitPatternEnhancement",
        "DigitalSubtraction",
        "ImageFiltering",
        "NoiseReduction",

        # Measurement and analysis
        "MeasurementSequence",
        "MeasurementTool",
        "MeasurementType",
        "MeasurementValue",
        "MeasurementUnits",
        "MeasurementMethod",
        "MeasurementAccuracy",
        "LesionMeasurement",
        "DiameterMeasurement",
        "AreaMeasurement",
        "VolumeMeasurement",

        # Intervention and treatment
        "InterventionSequence",
        "InterventionType",
        "InterventionMethod",
        "InterventionDevice",
        "InterventionResult",
        "TreatmentSequence",
        "TreatmentType",
        "TreatmentMethod",
        "TreatmentDevice",
        "TreatmentOutcome",
        "TherapyType",
        "AblationParameters",
        "ResectionParameters",
        "DilationParameters",

        # Recording and video
        "RecordingMethod",
        "RecordingFormat",
        "RecordingQuality",
        "FrameRate",
        "VideoFormat",
        "VideoCompression",
        "VideoBitRate",
        "VideoResolution",
        "AudioRecording",
        "AudioFormat",

        # Documentation and annotation
        "AnnotationSequence",
        "AnnotationLabel",
        "AnnotationText",
        "AnnotationLocation",
        "ImageMarker",
        "ImageLabel",
        "DocumentTitle",
        "DocumentComments",
        "FindingsDescription",
        "ConclusionDescription",

        # Quality and safety
        "ImageQuality",
        "ImageQualityScore",
        "ArtifactPresent",
        "ArtifactDescription",
        "ImageAdequacy",
        "PatientComfort",
        "SafetyParameters",
        "ComplicationSequence",

        # Additional endoscopy parameters
        "ScopeIdentification",
        "ChannelDiameter",
        "WorkingLength",
        "BendingSection",
        "TipDeflection",
        "SuctionApplied",
        "IrrigationApplied",
        "CO2Insufflation",
        "AirInsufflation",
        "PressureMeasurement",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of endoscopy-specific DICOM field names"""
        return self.ENDOSCOPY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract endoscopy-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing endoscopy metadata extraction results
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

            # Detect if this is an endoscopy study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_endoscopy = (
                modality == "ES" or
                "endoscopy" in series_desc or "endoscopy" in study_desc or
                "gastroscopy" in series_desc or "gastroscopy" in study_desc or
                "colonoscopy" in series_desc or "colonoscopy" in study_desc or
                "bronchoscopy" in series_desc or "bronchoscopy" in study_desc or
                "cystoscopy" in series_desc or "cystoscopy" in study_desc or
                "laparoscopy" in series_desc or "laparoscopy" in study_desc or
                "endoscope" in series_desc or "endoscope" in study_desc
            )

            metadata["is_endoscopy_study"] = is_endoscopy
            metadata["modality"] = modality

            # Extract endoscopy-specific fields
            fields_extracted = 0

            for field in self.ENDOSCOPY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add device analysis if available
            if "EndoscopeType" in metadata or "EndoscopeModel" in metadata:
                device_params = self._extract_device_parameters(dcm)
                metadata.update(device_params)
                fields_extracted += len(device_params)

            # Add visualization analysis if available
            if "VisualizationMode" in metadata or "IlluminationType" in metadata:
                visualization_params = self._extract_visualization_parameters(dcm)
                metadata.update(visualization_params)
                fields_extracted += len(visualization_params)

            # Add procedure analysis if available
            if "ProcedureType" in metadata or "ProcedureDescription" in metadata:
                procedure_params = self._extract_procedure_parameters(dcm)
                metadata.update(procedure_params)
                fields_extracted += len(procedure_params)

            # Add anatomical analysis if available
            if "AnatomicRegionSequence" in metadata or "AnatomicLocation" in metadata:
                anatomic_params = self._extract_anatomic_parameters(dcm)
                metadata.update(anatomic_params)
                fields_extracted += len(anatomic_params)

            # Add specialty analysis if available
            if "GIType" in metadata or "BronchoscopyType" in metadata:
                specialty_params = self._extract_specialty_parameters(dcm)
                metadata.update(specialty_params)
                fields_extracted += len(specialty_params)

            # Add measurement analysis if available
            if "MeasurementSequence" in metadata or "MeasurementValue" in metadata:
                measurement_params = self._extract_measurement_parameters(dcm)
                metadata.update(measurement_params)
                fields_extracted += len(measurement_params)

            # Add intervention analysis if available
            if "InterventionSequence" in metadata or "TreatmentType" in metadata:
                intervention_params = self._extract_intervention_parameters(dcm)
                metadata.update(intervention_params)
                fields_extracted += len(intervention_params)

            # Add warnings if this doesn't appear to be an endoscopy study
            if not is_endoscopy:
                warnings.append(
                    "This file may not be an endoscopy study. "
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
            logger.error(f"Endoscopy extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_device_parameters(self, dcm) -> Dict[str, Any]:
        """Extract endoscopic device parameters"""
        params = {}

        # Device fields
        device_fields = [
            "EndoscopeType",
            "EndoscopeModel",
            "EndoscopeDiameter",
            "EndoscopeLength",
            "EndoscopeNumberOfChannels",
            "AccessoryDevice",
            "AccessoryDeviceType",
        ]

        for field in device_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Device_{field}"] = value

        return params

    def _extract_visualization_parameters(self, dcm) -> Dict[str, Any]:
        """Extract visualization parameters"""
        params = {}

        # Visualization fields
        visualization_fields = [
            "VisualizationMode",
            "IlluminationType",
            "IlluminationIntensity",
            "NarrowBandImaging",
            "AutoFluorescenceImaging",
            "Chromoendoscopy",
            "MagnificationFactor",
        ]

        for field in visualization_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Visualization_{field}"] = value

        return params

    def _extract_procedure_parameters(self, dcm) -> Dict[str, Any]:
        """Extract procedure parameters"""
        params = {}

        # Procedure fields
        procedure_fields = [
            "ProcedureType",
            "ProcedureIndication",
            "ProcedureDescription",
            "ProcedureDate",
            "ProcedureStatus",
            "ProcedureComplications",
        ]

        for field in procedure_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Procedure_{field}"] = value

        return params

    def _extract_anatomic_parameters(self, dcm) -> Dict[str, Any]:
        """Extract anatomic location parameters"""
        params = {}

        # Anatomic fields
        anatomic_fields = [
            "AnatomicStructure",
            "AnatomicLocation",
            "AnatomicLaterality",
            "InsertionLength",
            "DepthOfInsertion",
            "LesionLocation",
            "LesionSize",
        ]

        for field in anatomic_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Anatomic_{field}"] = value

        return params

    def _extract_specialty_parameters(self, dcm) -> Dict[str, Any]:
        """Extract specialty-specific parameters"""
        params = {}

        # Specialty fields for GI, bronchoscopy, etc.
        specialty_fields = [
            "GIType",
            "GIProcedure",
            "GIFindings",
            "BronchoscopyType",
            "BronchoscopyProcedure",
            "BronchoscopyFindings",
            "AirwayLocation",
        ]

        for field in specialty_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Specialty_{field}"] = value

        return params

    def _extract_measurement_parameters(self, dcm) -> Dict[str, Any]:
        """Extract measurement parameters"""
        params = {}

        # Measurement fields
        measurement_fields = [
            "MeasurementTool",
            "MeasurementType",
            "MeasurementValue",
            "MeasurementUnits",
            "LesionMeasurement",
            "DiameterMeasurement",
        ]

        for field in measurement_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Measurement_{field}"] = value

        return params

    def _extract_intervention_parameters(self, dcm) -> Dict[str, Any]:
        """Extract intervention and treatment parameters"""
        params = {}

        # Intervention fields
        intervention_fields = [
            "InterventionType",
            "InterventionMethod",
            "InterventionResult",
            "TreatmentType",
            "TreatmentOutcome",
            "TherapyType",
        ]

        for field in intervention_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Intervention_{field}"] = value

        return params

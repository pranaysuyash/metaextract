"""
Ophthalmology and Optometry DICOM Extension
Implements specialized metadata extraction for ophthalmology and optometry studies
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


class OphthalmologyExtension(DICOMExtensionBase):
    """
    Ophthalmology and Optometry metadata extraction.

    Extracts specialized ophthalmology-related DICOM tags including:
    - Visual acuity measurements and corrections
    - Ophthalmic imaging parameters (fundus, anterior segment)
    - Corneal topography and pachymetry data
    - Retinal imaging and analysis
    - Refraction and ocular biometrics
    - Surgical and laser treatment parameters
    """

    SPECIALTY = "ophthalmology"
    FIELD_COUNT = 85
    REFERENCE = "DICOM PS3.3 (Ophthalmology)"
    DESCRIPTION = "Ophthalmology and Optometry specialized metadata extraction"
    VERSION = "1.0.0"

    # Ophthalmology field definitions
    OPHTHALMOLOGY_FIELDS = [
        # Ophthalmic imaging sequences
        "ReferencedOphthalmicMeasurementSeries",
        "OphthalmicPhotographicAcquisitionSequence",
        "OphthalmicPhotographyParametersSequence",
        "AcquisitionMethod",
        "AcquisitionMethodVersion",

        # Refraction and correction
        "TargetRefraction",
        "RefractiveState",
        "SphericalEquivalent",
        "CylinderPower",
        "CylinderAxis",
        "PrismPower",
        "PrismBase",
        "NearAddition",

        # Visual acuity measurements
        "VisualAcuityMeasurementSequence",
        "DecimalVisualAcuity",
        "VisualAcuityModality",
        "VisualAcuityRightEyeSequence",
        "VisualAcuityLeftEyeSequence",
        "VisualAcuityBothEyesSequence",
        "ReferencedVisualAcuityMeasurement",

        # Optotype and testing
        "Optotype",
        "OptotypeDetail",
        "OptotypeSize",
        "TestingDistance",
        "Illumination",
        "BackgroundLuminance",
        "Contrast",

        # Mydriatic agents (eye drops)
        "MydriaticAgentCodeSequence",
        "MydriaticAgentConcentration",
        "MydriaticAgentVolume",
        "MydriaticAgentNumber",
        "PreInjectionTime",
        "PostInjectionTime",
        "InjectionDuration",

        # Ophthalmic axial measurements
        "OphthalmicAxialMeasurementsSequence",
        "AxialLength",
        "AnteriorChamberDepth",
        "LensThickness",
        "VitreousDepth",
        "CentralCornealThickness",
        "RetinalThickness",

        # Lens status
        "LensStatusCodeSequence",
        "LensStatus",
        "CataractType",
        "NuclearColor",
        "CorticalType",
        "PosteriorSubcapsularType",

        # Vitreous and retinal status
        "VitrectomyStatusCodeSequence",
        "IridotomyStatusCodeSequence",
        "VitreousStatus",
        "RetinaStatus",
        "MaculaStatus",
        "OpticDiscStatus",

        # Physician and procedure info
        "PhysicianOptionSequence",
        "OphthalmicProcedureCodeSequence",
        "ProcedureType",
        "ProcedureLaterality",
        "ProcedureIndication",

        # Waveform data
        "ReferencedWaveformData",
        "WaveformSequence",
        "WaveformDataDescriptionSequence",
        "WaveformNumberOfChannels",
        "WaveformSampleRate",
        "WaveformBitsAllocated",

        # Image dimensions and scaling
        "ImagedVolumeWidth",
        "ImagedVolumeHeight",
        "ImagedVolumeDepth",
        "MatrixX",
        "MatrixY",
        "MatrixZ",
        "PixelRepresentation",
        "TopLeftHandedness",

        # Pixel spacing and calibration
        "PixelSpacingSequence",
        "PixelSpacingCalibrated",
        "PixelSpacingCalibrationDescription",
        "PixelSpacingInSpatialCoordinates",
        "AspectRatio",
        "AspectRatioInformation",

        # Image orientation
        "OphthalmicImageOrientation",
        "ImageOrientationSlide",
        "ImageOrientationLabel",
        "RotationAngle",
        "Mirroring",

        # Pixel intensity and display
        "PixelIntensityRelationship",
        "PixelIntensityRelationshipSign",
        "WindowCenter",
        "WindowWidth",
        "WindowCenterWidthExplanation",
        "RescaleIntercept",
        "RescaleSlope",
        "RescaleType",

        # VOI LUT and presentation
        "PixelValueTransformationSequence",
        "SaturationRGB",
        "VOILUTFunction",
        "PresentationLUTSequence",
        "PresentationLUTShape",

        # Image acquisition timing
        "AcquisitionTime",
        "StudyTime",
        "SeriesTime",
        "InstanceNumber",
        "TemporalPositionIndex",

        # Stack and frame organization
        "StackID",
        "InStackPositionNumber",
        "ViewNumber",
        "NumberOfFrames",
        "FrameNumber",

        # Image quality indicators
        "QualityControlImage",
        "BurnedInAnnotation",
        "RecognizableVisualFeatures",
        "ImageQualityGrade",
        "ArtifactPresent",
        "ArtifactDescription",

        # Monoscopic and stereo imaging
        "MonoscopicDisplayOption",
        "StereoBaseAngle",
        "StereoBaseline",
        "StereoPresentationFlag",

        # Proposed study and acquisition
        "ProposedStudySequence",
        "StartAcquisitionDateTime",
        "EndAcquisitionDateTime",
        "AcquisitionDuration",
        "NumberOfAcquisitions",

        # Applicator and treatment devices
        "ApplicatorSequence",
        "ApplicatorID",
        "ApplicatorType",
        "ApplicatorDescription",
        "ApplicatorPosition",

        # Dose measurements
        "ReferencedReferenceAirKermaRate",
        "MeasuredDoseReferenceSequence",
        "MeasuredDoseType",
        "MeasuredDoseValue",
        "RadiationDoseInVivo",

        # Comments and notes
        "Comment",
        "StudyComments",
        "SeriesComments",
        "ImageComments",

        # Ophthalmic device settings
        "OphthalmicDeviceManufacturer",
        "OphthalmicDeviceModelName",
        "OphthalmicDeviceSoftwareVersion",
        "OphthalmicDeviceSerialNumber",

        # Imaging modality specifics
        "ImagingModality",
        "ScanningTechnique",
        "ViewPosition",
        "ProjectionEponymousName",
        "PatientOrientation",

        # Corneal topography
        "CornealTopographyMap",
        "CornealElevationMap",
        "CornealPachymetryMap",
        "CornealPowerMap",
        "CornealAstigmatismMap",

        # Retinal imaging specifics
        "RetinalImageType",
        "FundusImageType",
        "OpticDiscImageCenter",
        "MaculaImageCenter",
        "PosteriorPole",

        # Glaucoma diagnostics
        "IntraocularPressure",
        "IOPMeasurementMethod",
        "IOPMeasurementTime",
        "GlaucomaDiagnosis",

        # Surgical parameters
        "SurgicalProcedure",
        "SurgicalLaterality",
        "SurgicalApproach",
        "SurgicalInstruments",
        "SurgicalComplications",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of ophthalmology-specific DICOM field names"""
        return self.OPHTHALMOLOGY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract ophthalmology-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing ophthalmology metadata extraction results
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

            # Detect if this is an ophthalmology study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_ophthalmology = (
                "ophthal" in series_desc or "ophthal" in study_desc or
                "eye" in series_desc or "eye" in study_desc or
                "fundus" in series_desc or "fundus" in study_desc or
                "retina" in series_desc or "retina" in study_desc or
                "cornea" in series_desc or "cornea" in study_desc or
                "glaucoma" in series_desc or "glaucoma" in study_desc or
                modality in ["OP", "RF", "US"] and "eye" in study_desc
            )

            metadata["is_ophthalmology_study"] = is_ophthalmology
            metadata["modality"] = modality

            # Extract ophthalmology-specific fields
            fields_extracted = 0

            for field in self.OPHTHALMOLOGY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add visual acuity parameters if available
            if "VisualAcuityMeasurementSequence" in metadata or "DecimalVisualAcuity" in metadata:
                acuity_params = self._extract_visual_acuity_parameters(dcm)
                metadata.update(acuity_params)
                fields_extracted += len(acuity_params)

            # Add ocular biometrics if available
            if "AxialLength" in metadata or "CentralCornealThickness" in metadata:
                biometric_params = self._extract_ocular_biometrics(dcm)
                metadata.update(biometric_params)
                fields_extracted += len(biometric_params)

            # Add refraction parameters if available
            if "TargetRefraction" in metadata or "SphericalEquivalent" in metadata:
                refraction_params = self._extract_refraction_parameters(dcm)
                metadata.update(refraction_params)
                fields_extracted += len(refraction_params)

            # Add corneal topography if available
            if "CornealTopographyMap" in metadata or "CornealElevationMap" in metadata:
                topography_params = self._extract_corneal_topography_parameters(dcm)
                metadata.update(topography_params)
                fields_extracted += len(topography_params)

            # Add warnings if this doesn't appear to be an ophthalmology study
            if not is_ophthalmology:
                warnings.append(
                    "This file may not be an ophthalmology study. "
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
            logger.error(f"Ophthalmology extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_visual_acuity_parameters(self, dcm) -> Dict[str, Any]:
        """Extract visual acuity measurement parameters"""
        params = {}

        # Visual acuity measurements
        acuity_fields = [
            "DecimalVisualAcuity",
            "Optotype",
            "OptotypeSize",
            "TestingDistance",
            "Illumination",
            "BackgroundLuminance",
            "Contrast",
        ]

        for field in acuity_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Acuity_{field}"] = value

        return params

    def _extract_ocular_biometrics(self, dcm) -> Dict[str, Any]:
        """Extract ocular biometric measurements"""
        params = {}

        # Ocular biometrics
        biometric_fields = [
            "AxialLength",
            "AnteriorChamberDepth",
            "LensThickness",
            "VitreousDepth",
            "CentralCornealThickness",
            "RetinalThickness",
        ]

        for field in biometric_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Biometric_{field}"] = value

        return params

    def _extract_refraction_parameters(self, dcm) -> Dict[str, Any]:
        """Extract refraction and correction parameters"""
        params = {}

        # Refraction measurements
        refraction_fields = [
            "SphericalEquivalent",
            "CylinderPower",
            "CylinderAxis",
            "PrismPower",
            "PrismBase",
            "NearAddition",
        ]

        for field in refraction_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Refraction_{field}"] = value

        return params

    def _extract_corneal_topography_parameters(self, dcm) -> Dict[str, Any]:
        """Extract corneal topography parameters"""
        params = {}

        # Corneal topography
        topography_fields = [
            "CornealTopographyMap",
            "CornealElevationMap",
            "CornealPachymetryMap",
            "CornealPowerMap",
            "CornealAstigmatismMap",
        ]

        for field in topography_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Topography_{field}"] = value

        return params
"""
Neurology MRI DICOM Extension
Implements specialized metadata extraction for neurology and brain MRI studies
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


class NeurologyMRIExtension(DICOMExtensionBase):
    """
    Neurology MRI metadata extraction.

    Extracts specialized neurology-related DICOM tags including:
    - Brain anatomy and morphology
    - Neurovascular imaging and perfusion
    - Diffusion and white matter integrity
    - Functional brain mapping
    - Neurodegeneration assessment
    - Brain tumor characterization
    - Traumatic brain injury evaluation
    - Pediatric neuroimaging
    """

    SPECIALTY = "neurology_mri"
    FIELD_COUNT = 88
    REFERENCE = "DICOM PS3.3 (Neurology)"
    DESCRIPTION = "Neurology MRI specialized metadata extraction"
    VERSION = "1.0.0"

    # Neurology field definitions
    NEUROLOGY_FIELDS = [
        # Brain anatomy
        "BrainRegion",
        "CerebralHemisphere",
        "FrontalLobe",
        "ParietalLobe",
        "TemporalLobe",
        "OccipitalLobe",
        "Cerebellum",
        "Brainstem",
        "Thalamus",
        "BasalGanglia",
        "CorpusCallosum",
        "LimbicSystem",
        "Insula",
        "WhiteMatter",
        "GrayMatter",
        "CSF",

        # Neurovascular imaging
        "CerebralBloodFlow",
        "CerebralBloodVolume",
        "PerfusionImaging",
        "ArterialSpinLabeling",
        "ASL",
        "MRAngiography",
        "MRA",
        "Venography",
        "MRV",
        "CerebralArteries",
        "CerebralVeins",
        "DuralSinuses",
        "CircleOfWillis",
        "CarotidArteries",
        "VertebralArteries",
        "CerebrovascularResistance",

        # Diffusion imaging
        "DiffusionWeightedImaging",
        "DWI",
        "DiffusionTensorImaging",
        "DTI",
        "FractionalAnisotropy",
        "MeanDiffusivity",
        "WhiteMatterTracts",
        "Tractography",
        "DiffusionMetrics",
        "ApparentDiffusionCoefficient",
        "WhiteMatterIntegrity",
        "Connectivity",
        "StructuralConnectivity",

        # Functional imaging
        "FunctionalMRI",
        "fMRI",
        "BOLD",
        "BloodOxygenationLevelDependent",
        "BrainActivation",
        "TaskBasedfMRI",
        "RestingStatefMRI",
        "FunctionalConnectivity",
        "BrainNetworks",
        "DefaultModeNetwork",
        "SensorimotorNetwork",
        "LanguageNetwork",
        "VisualNetwork",

        # Neurodegeneration
        "BrainAtrophy",
        "CorticalThickness",
        "GrayMatterVolume",
        "WhiteMatterVolume",
        "HippocampalVolume",
        "VentricularEnlargement",
        "CorticalAtrophy",
        "RegionalAtrophy",
        "Neurodegeneration",
        "DementiaAssessment",
        "AlzheimersDisease",
        "ParkinsonsDisease",
        "MultipleSclerosis",
        "MSLesions",
        "WhiteMatterLesions",

        # Brain tumors
        "BrainTumor",
        "TumorLocation",
        "TumorSize",
        "TumorType",
        "TumorGrading",
        "Glioma",
        "Meningioma",
        "Metastasis",
        "TumorEnhancement",
        "PeritumoralEdema",
        "MassEffect",
        "MidlineShift",
        "TumorResection",
        "SurgicalPlanning",

        # Trauma and emergency
        "TraumaticBrainInjury",
        "TBI",
        "BrainContusion",
        "IntracranialHemorrhage",
        "SubduralHematoma",
        "EpiduralHematoma",
        "SubarachnoidHemorrhage",
        "IntraventricularHemorrhage",
        "DiffuseAxonalInjury",
        "CerebralEdema",
        "IncreasedICP",
        "SkullFracture",
        "EmergencyNeuroimaging",

        # Advanced techniques
        "MagneticResonanceSpectroscopy",
        "MRS",
        "Metabolites",
        "NAA",
        "Choline",
        "Creatine",
        "Lactate",
        "QuantitativeMRI",
        "SusceptibilityWeightedImaging",
        "SWI",
        "QuantitativeSusceptibilityMapping",
        "QSM",
        "MagnetizationTransfer",
        "MT",

        # Pediatric neuroimaging
        "BrainDevelopment",
        "Myelination",
        "BrainMaturation",
        "PediatricBrain",
        "NeonatalBrain",
        "PrematureBrain",
        "GestationalAge",
        "BrainAge",
        "DevelopmentalMilestones",

        # Additional neurology parameters
        "SeizureFocus",
        "EpilepsyImaging",
        "PresurgicalMapping",
        "EloquentCortex",
        "MotorCortex",
        "SpeechCortex",
        "VisualCortex",
        "BrainMapping",
        "NeurosurgicalPlanning",
        "StereotacticPlanning",
        "DeepBrainStimulation",
        "DBS",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of neurology-specific DICOM field names"""
        return self.NEUROLOGY_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract neurology-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing neurology metadata extraction results
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

            # Detect if this is a neurology study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_neurology = (
                modality == "MR" and (
                    "brain" in series_desc or "brain" in study_desc or
                    "neuro" in series_desc or "neuro" in study_desc or
                    "cerebral" in series_desc or "cerebral" in study_desc or
                    "dementia" in series_desc or "alzheimer" in study_desc or
                    "ms" in series_desc or "multiple sclerosis" in study_desc or
                    "tumor" in series_desc and "brain" in study_desc or
                    "tbi" in series_desc or "traumatic brain" in study_desc
                )
            )

            metadata["is_neurology_study"] = is_neurology
            metadata["modality"] = modality

            # Extract neurology-specific fields
            fields_extracted = 0

            for field in self.NEUROLOGY_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add brain anatomy analysis if available
            if "BrainRegion" in metadata or "CerebralHemisphere" in metadata:
                anatomy_params = self._extract_anatomy_parameters(dcm)
                metadata.update(anatomy_params)
                fields_extracted += len(anatomy_params)

            # Add vascular analysis if available
            if "CerebralBloodFlow" in metadata or "MRAngiography" in metadata:
                vascular_params = self._extract_vascular_parameters(dcm)
                metadata.update(vascular_params)
                fields_extracted += len(vascular_params)

            # Add diffusion analysis if available
            if "DiffusionWeightedImaging" in metadata or "FractionalAnisotropy" in metadata:
                diffusion_params = self._extract_diffusion_parameters(dcm)
                metadata.update(diffusion_params)
                fields_extracted += len(diffusion_params)

            # Add functional analysis if available
            if "FunctionalMRI" in metadata or "BOLD" in metadata:
                functional_params = self._extract_functional_parameters(dcm)
                metadata.update(functional_params)
                fields_extracted += len(functional_params)

            # Add degeneration analysis if available
            if "BrainAtrophy" in metadata or "CorticalThickness" in metadata:
                degeneration_params = self._extract_degeneration_parameters(dcm)
                metadata.update(degeneration_params)
                fields_extracted += len(degeneration_params)

            # Add tumor analysis if available
            if "BrainTumor" in metadata or "Glioma" in metadata:
                tumor_params = self._extract_tumor_parameters(dcm)
                metadata.update(tumor_params)
                fields_extracted += len(tumor_params)

            # Add trauma analysis if available
            if "TraumaticBrainInjury" in metadata or "IntracranialHemorrhage" in metadata:
                trauma_params = self._extract_trauma_parameters(dcm)
                metadata.update(trauma_params)
                fields_extracted += len(trauma_params)

            # Add warnings if this doesn't appear to be a neurology study
            if not is_neurology:
                warnings.append(
                    "This file may not be a neurology study. "
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
            logger.error(f"Neurology extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_anatomy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract brain anatomy parameters"""
        params = {}

        # Anatomy fields
        anatomy_fields = [
            "BrainRegion",
            "CerebralHemisphere",
            "FrontalLobe",
            "Cerebellum",
            "WhiteMatter",
            "GrayMatter",
        ]

        for field in anatomy_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Anatomy_{field}"] = value

        return params

    def _extract_vascular_parameters(self, dcm) -> Dict[str, Any]:
        """Extract neurovascular parameters"""
        params = {}

        # Vascular fields
        vascular_fields = [
            "CerebralBloodFlow",
            "PerfusionImaging",
            "MRAngiography",
            "CircleOfWillis",
            "CerebralArteries",
        ]

        for field in vascular_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Vascular_{field}"] = value

        return params

    def _extract_diffusion_parameters(self, dcm) -> Dict[str, Any]:
        """Extract diffusion imaging parameters"""
        params = {}

        # Diffusion fields
        diffusion_fields = [
            "DiffusionWeightedImaging",
            "DiffusionTensorImaging",
            "FractionalAnisotropy",
            "MeanDiffusivity",
            "WhiteMatterTracts",
        ]

        for field in diffusion_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Diffusion_{field}"] = value

        return params

    def _extract_functional_parameters(self, dcm) -> Dict[str, Any]:
        """Extract functional imaging parameters"""
        params = {}

        # Functional fields
        functional_fields = [
            "FunctionalMRI",
            "BOLD",
            "BrainActivation",
            "FunctionalConnectivity",
            "DefaultModeNetwork",
        ]

        for field in functional_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Functional_{field}"] = value

        return params

    def _extract_degeneration_parameters(self, dcm) -> Dict[str, Any]:
        """Extract neurodegeneration parameters"""
        params = {}

        # Degeneration fields
        degeneration_fields = [
            "BrainAtrophy",
            "CorticalThickness",
            "HippocampalVolume",
            "VentricularEnlargement",
            "Neurodegeneration",
        ]

        for field in degeneration_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Degeneration_{field}"] = value

        return params

    def _extract_tumor_parameters(self, dcm) -> Dict[str, Any]:
        """Extract brain tumor parameters"""
        params = {}

        # Tumor fields
        tumor_fields = [
            "BrainTumor",
            "TumorLocation",
            "TumorSize",
            "Glioma",
            "TumorEnhancement",
            "PeritumoralEdema",
        ]

        for field in tumor_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Tumor_{field}"] = value

        return params

    def _extract_trauma_parameters(self, dcm) -> Dict[str, Any]:
        """Extract traumatic brain injury parameters"""
        params = {}

        # Trauma fields
        trauma_fields = [
            "TraumaticBrainInjury",
            "IntracranialHemorrhage",
            "SubduralHematoma",
            "BrainContusion",
        ]

        for field in trauma_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Trauma_{field}"] = value

        return params

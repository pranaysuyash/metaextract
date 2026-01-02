"""
Pediatric Imaging DICOM Extension
Implements specialized metadata extraction for pediatric and neonatal imaging studies
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


class PediatricImagingExtension(DICOMExtensionBase):
    """
    Pediatric Imaging metadata extraction.

    Extracts specialized pediatric-related DICOM tags including:
    - Pediatric age and size parameters
    - Growth and development assessment
    - Congenital abnormalities
    - Pediatric-specific protocols
    - Radiation dose optimization
    - Sedation and anesthesia considerations
    - Age-appropriate imaging parameters
    - Pediatric emergencies
    """

    SPECIALTY = "pediatric_imaging"
    FIELD_COUNT = 71
    REFERENCE = "DICOM PS3.3 (Pediatric)"
    DESCRIPTION = "Pediatric Imaging specialized metadata extraction"
    VERSION = "1.0.0"

    # Pediatric imaging field definitions
    PEDIATRIC_FIELDS = [
        # Pediatric demographics
        "PediatricPatient",
        "Neonate",
        "Infant",
        "Child",
        "Adolescent",
        "PatientAge",
        "GestationalAge",
        "CorrectedGestationalAge",
        "PostMenstrualAge",
        "BirthWeight",
        "CurrentWeight",
        "WeightForAge",
        "HeightForAge",
        "HeadCircumference",
        "BodySurfaceArea",
        "BMI",
        "BodyMassIndex",
        "GrowthPercentile",
        "GrowthParameters",

        # Pediatric protocols
        "PediatricProtocol",
        "AgeAppropriateProtocol",
        "SizeBasedProtocol",
        "WeightBasedProtocol",
        "LowDoseProtocol",
        "RadiationProtection",
        "DoseOptimization",
        "ChildFriendly",
        "ParentalPresence",
        "SedationRequired",
        "AnesthesiaRequired",
        "Immobilization",

        # Congenital abnormalities
        "CongenitalAbnormality",
        "CongenitalHeartDisease",
        "CongenitalBrainMalformation",
        "CongenitalLungAbnormality",
        "CongenitalGIAnomaly",
        "CongenitalOrthopedic",
        "GeneticSyndrome",
        "ChromosomalAbnormality",
        "SyndromicFeatures",
        "DysmorphicFeatures",
        "DevelopmentalDelay",
        "NeurodevelopmentalDisorder",

        # Brain development
        "BrainDevelopment",
        "Myelination",
        "MyelinationPattern",
        "BrainMaturation",
        "CorticalDevelopment",
        "Synaptogenesis",
        "Pruning",
        "WhiteMatterDevelopment",
        "GrayMatterDevelopment",
        "CerebellarDevelopment",
        "BrainVolume",
        "VentricularSize",
        "ExtraAxialSpace",
        "AgeAppropriateMyelination",

        # Pediatric emergencies
        "PediatricEmergency",
        "NeonatalEmergency",
        "ChildAbuse",
        "NonAccidentalTrauma",
        "ShakenBabySyndrome",
        "BirthTrauma",
        "PediatricTrauma",
        "AccidentalInjury",
        "ForeignBody",
        "Aspiration",
        "SuddenInfantDeath",

        # Pediatric-specific conditions
        "PediatricCondition",
        "NeonatalCondition",
        "Prematurity",
        "Preterm",
        "LowBirthWeight",
        "IntrauterineGrowthRestriction",
        "SmallForGestationalAge",
        "LargeForGestationalAge",
        "BronchopulmonaryDysplasia",
        "NecrotizingEnterocolitis",
        "RetinopathyOfPrematurity",
        "Jaundice",
        "NeonatalSepsis",

        # Orthopedic assessment
        "PediatricOrthopedic",
        "GrowthPlate",
        "Physis",
        "Ossification",
        "BoneAge",
        "SkeletalAge",
        "GrowthAssessment",
        "LegLengthDiscrepancy",
        "ScoliosisScreening",
        "DevelopmentalDysplasia",
        "CongenitalHipDysplasia",

        # Dose considerations
        "RadiationDose",
        "PediatricDose",
        "SizeSpecificDoseEstimate",
        "SSDE",
        "DoseLengthProduct",
        "EffectiveDose",
        "OrganDose",
        "DoseOptimization",
        "ALARA",
        "AsLowAsReasonablyAchievable",
        "DoseReduction",
        "LowDoseTechnique",

        # Imaging parameters
        "PediatricImaging",
        "AgeSpecificTechnique",
        "SizeBasedTechnique",
        "ReducedResolution",
        "IncreasedNoise",
        "FasterAcquisition",
        "MotionReduction",
        "SedationLevel",
        "AnesthesiaDepth",
        "PatientCooperation",

        # Additional pediatric parameters
        "ParentalConsent",
        "Assent",
        "GuardianPresent",
        "ChildLifeSpecialist",
        "PediatricRadiologist",
        "Neonatologist",
        "Pediatrician",
        "PediatricSurgeon",
        "PediatricOncologist",
        "PediatricCardiologist",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of pediatric-specific DICOM field names"""
        return self.PEDIATRIC_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract pediatric-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing pediatric metadata extraction results
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

            # Detect if this is a pediatric study
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_pediatric = (
                "pediatric" in series_desc or "pediatric" in study_desc or
                "child" in series_desc or "children" in study_desc or
                "neonatal" in series_desc or "neonate" in study_desc or
                "infant" in series_desc or "infant" in study_desc or
                "congenital" in series_desc or "genetic" in study_desc or
                "premature" in series_desc or "preterm" in study_desc or
                "birth" in series_desc and "weight" in study_desc
            )

            metadata["is_pediatric_study"] = is_pediatric
            metadata["modality"] = modality

            # Extract pediatric-specific fields
            fields_extracted = 0

            for field in self.PEDIATRIC_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add demographic analysis if available
            if "PediatricPatient" in metadata or "PatientAge" in metadata:
                demographic_params = self._extract_demographic_parameters(dcm)
                metadata.update(demographic_params)
                fields_extracted += len(demographic_params)

            # Add protocol analysis if available
            if "PediatricProtocol" in metadata or "LowDoseProtocol" in metadata:
                protocol_params = self._extract_protocol_parameters(dcm)
                metadata.update(protocol_params)
                fields_extracted += len(protocol_params)

            # Add congenital analysis if available
            if "CongenitalAbnormality" in metadata or "GeneticSyndrome" in metadata:
                congenital_params = self._extract_congenital_parameters(dcm)
                metadata.update(congenital_params)
                fields_extracted += len(congenital_params)

            # Add development analysis if available
            if "BrainDevelopment" in metadata or "Myelination" in metadata:
                development_params = self._extract_development_parameters(dcm)
                metadata.update(development_params)
                fields_extracted += len(development_params)

            # Add emergency analysis if available
            if "PediatricEmergency" in metadata or "ChildAbuse" in metadata:
                emergency_params = self._extract_emergency_parameters(dcm)
                metadata.update(emergency_params)
                fields_extracted += len(emergency_params)

            # Add dose analysis if available
            if "RadiationDose" in metadata or "SizeSpecificDoseEstimate" in metadata:
                dose_params = self._extract_dose_parameters(dcm)
                metadata.update(dose_params)
                fields_extracted += len(dose_params)

            # Add warnings if this doesn't appear to be a pediatric study
            if not is_pediatric:
                warnings.append(
                    "This file may not be a pediatric study. "
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
            logger.error(f"Pediatric extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_demographic_parameters(self, dcm) -> Dict[str, Any]:
        """Extract pediatric demographic parameters"""
        params = {}

        # Demographic fields
        demographic_fields = [
            "PediatricPatient",
            "Neonate",
            "PatientAge",
            "GestationalAge",
            "BirthWeight",
            "CurrentWeight",
            "HeadCircumference",
            "BodySurfaceArea",
        ]

        for field in demographic_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Demographic_{field}"] = value

        return params

    def _extract_protocol_parameters(self, dcm) -> Dict[str, Any]:
        """Extract pediatric protocol parameters"""
        params = {}

        # Protocol fields
        protocol_fields = [
            "PediatricProtocol",
            "AgeAppropriateProtocol",
            "LowDoseProtocol",
            "RadiationProtection",
            "SedationRequired",
            "DoseOptimization",
        ]

        for field in protocol_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Protocol_{field}"] = value

        return params

    def _extract_congenital_parameters(self, dcm) -> Dict[str, Any]:
        """Extract congenital abnormality parameters"""
        params = {}

        # Congenital fields
        congenital_fields = [
            "CongenitalAbnormality",
            "CongenitalHeartDisease",
            "GeneticSyndrome",
            "ChromosomalAbnormality",
            "DevelopmentalDelay",
        ]

        for field in congenital_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Congenital_{field}"] = value

        return params

    def _extract_development_parameters(self, dcm) -> Dict[str, Any]:
        """Extract development parameters"""
        params = {}

        # Development fields
        development_fields = [
            "BrainDevelopment",
            "Myelination",
            "BrainMaturation",
            "CorticalDevelopment",
            "WhiteMatterDevelopment",
            "BoneAge",
        ]

        for field in development_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Development_{field}"] = value

        return params

    def _extract_emergency_parameters(self, dcm) -> Dict[str, Any]:
        """Extract pediatric emergency parameters"""
        params = {}

        # Emergency fields
        emergency_fields = [
            "PediatricEmergency",
            "NeonatalEmergency",
            "ChildAbuse",
            "NonAccidentalTrauma",
            "BirthTrauma",
        ]

        for field in emergency_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Emergency_{field}"] = value

        return params

    def _extract_dose_parameters(self, dcm) -> Dict[str, Any]:
        """Extract radiation dose parameters"""
        params = {}

        # Dose fields
        dose_fields = [
            "RadiationDose",
            "SizeSpecificDoseEstimate",
            "EffectiveDose",
            "DoseOptimization",
            "ALARA",
        ]

        for field in dose_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Dose_{field}"] = value

        return params

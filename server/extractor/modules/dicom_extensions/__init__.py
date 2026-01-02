"""
DICOM Extensions Package
Specialized DICOM metadata extraction modules for medical imaging specialties
"""

from .base import DICOMExtensionBase, DICOMExtensionError
from .registry import (
    DICOMExtensionRegistry,
    get_global_registry,
    get_all_extensions,
    get_extension_by_specialty
)
from .ct_perfusion import CTPerfusionExtension
from .cardiology import CardiologyECGExtension
from .pet_nuclear import PETNuclearMedicineExtension
from .mammography import MammographyBreastImagingExtension
from .ophthalmology import OphthalmologyExtension
from .angiography import AngiographyInterventionalExtension
from .storage_retrieval import StorageRetrievalExtension
from .display_voi_lut import DisplayVOIExtension
from .multiframe import MultiframeFunctionalGroupsExtension
from .structured_report import StructuredReportExtension
from .radiation_therapy import RadiationTherapyExtension
from .ultrasound import UltrasoundExtension
from .mri_mrs import MRIMRSExtension
from .endoscopy import EndoscopyExtension
from .nuclear_medicine import NuclearMedicineExtension
from .xray_angiography import XRayAngiographyExtension
from .ct_colonography import CTColonographyExtension
from .dental import DentalExtension
from .vascular_ultrasound import VascularUltrasoundExtension
from .cardiac_mri import CardiacMRIExtension
from .breast_mri import BreastMRIExtension
from .neurology_mri import NeurologyMRIExtension
from .oncology_imaging import OncologyImagingExtension
from .emergency_radiology import EmergencyRadiologyExtension
from .pediatric_imaging import PediatricImagingExtension

__all__ = [
    "DICOMExtensionBase",
    "DICOMExtensionError",
    "DICOMExtensionRegistry",
    "get_global_registry",
    "get_all_extensions",
    "get_extension_by_specialty",
    "CTPerfusionExtension",
    "CardiologyECGExtension",
    "PETNuclearMedicineExtension",
    "MammographyBreastImagingExtension",
    "OphthalmologyExtension",
    "AngiographyInterventionalExtension",
    "StorageRetrievalExtension",
    "DisplayVOIExtension",
    "MultiframeFunctionalGroupsExtension",
    "StructuredReportExtension",
    "RadiationTherapyExtension",
    "UltrasoundExtension",
    "MRIMRSExtension",
    "EndoscopyExtension",
    "NuclearMedicineExtension",
    "XRayAngiographyExtension",
    "CTColonographyExtension",
    "DentalExtension",
    "VascularUltrasoundExtension",
    "CardiacMRIExtension",
    "BreastMRIExtension",
    "NeurologyMRIExtension",
    "OncologyImagingExtension",
    "EmergencyRadiologyExtension",
    "PediatricImagingExtension",
]

# Version and compatibility
__version__ = "1.0.0"
DICOM_STANDARD_VERSION = "2024b"

# Register extensions automatically
def _register_extensions():
    """Auto-register all extension classes"""
    import logging

    registry = get_global_registry()
    logger = logging.getLogger(__name__)

    extensions = [
        CTPerfusionExtension,
        CardiologyECGExtension,
        PETNuclearMedicineExtension,
        MammographyBreastImagingExtension,
        OphthalmologyExtension,
        AngiographyInterventionalExtension,
        StorageRetrievalExtension,
        DisplayVOIExtension,
        MultiframeFunctionalGroupsExtension,
        StructuredReportExtension,
        RadiationTherapyExtension,
        UltrasoundExtension,
        MRIMRSExtension,
        EndoscopyExtension,
        NuclearMedicineExtension,
        XRayAngiographyExtension,
        CTColonographyExtension,
        DentalExtension,
        VascularUltrasoundExtension,
        CardiacMRIExtension,
        BreastMRIExtension,
        NeurologyMRIExtension,
        OncologyImagingExtension,
        EmergencyRadiologyExtension,
        PediatricImagingExtension,
    ]

    for ext_class in extensions:
        try:
            registry.register_extension(ext_class)
        except Exception as e:
            logger.warning(f"Failed to register {ext_class.__name__}: {e}")

# Auto-register on import
_register_extensions()
"""
Image Extensions Package
Specialized image metadata extraction modules with standardized interface
"""

from .base import (
    ImageExtensionBase,
    ImageExtensionError,
    ImageExtractionResult,
    safe_extract_image_field,
    get_image_file_info
)
from .registry import (
    ImageExtractionRegistry,
    get_global_registry,
    reset_global_registry
)
from .basic_image_extension import BasicImageExtension
from .advanced_image_extension import AdvancedImageExtension
from .universal_image_extension import UniversalImageExtension
from .complete_gps_extension import CompleteGPSImageExtension
from .specialized_modules_extension import SpecializedModulesExtension
from .enhanced_master_extension import EnhancedMasterExtension

__all__ = [
    "ImageExtensionBase",
    "ImageExtensionError",
    "ImageExtractionResult",
    "safe_extract_image_field",
    "get_image_file_info",
    "ImageExtractionRegistry",
    "get_global_registry",
    "reset_global_registry",
    "BasicImageExtension",
    "AdvancedImageExtension",
    "UniversalImageExtension",
    "CompleteGPSImageExtension",
    "SpecializedModulesExtension",
    "EnhancedMasterExtension",
]

# Version and compatibility
__version__ = "1.0.0"

# Auto-register extensions on import
def _register_extensions():
    """Auto-register all image extension classes"""
    import logging
    logger = logging.getLogger(__name__)

    registry = get_global_registry()

    extensions = [
        BasicImageExtension,
        AdvancedImageExtension,
        UniversalImageExtension,
        CompleteGPSImageExtension,
        SpecializedModulesExtension,
        EnhancedMasterExtension,
    ]

    for ext_class in extensions:
        try:
            registry.register_extension(ext_class)
        except Exception as e:
            logger.warning(f"Failed to register {ext_class.__name__}: {e}")

# Auto-register on import
_register_extensions()
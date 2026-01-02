"""
DICOM Extension Registry
Central registry for all DICOM specialty extensions
"""

import logging
from typing import Dict, List, Optional, Type
from pathlib import Path

from .base import DICOMExtensionBase, DICOMExtensionError

logger = logging.getLogger(__name__)


class DICOMExtensionRegistry:
    """
    Central registry for managing DICOM specialty extensions.
    """

    def __init__(self):
        self._extensions: Dict[str, Type[DICOMExtensionBase]] = {}
        self._instances: Dict[str, DICOMExtensionBase] = {}

    def register_extension(
        self,
        extension_class: Type[DICOMExtensionBase],
        override: bool = False
    ) -> None:
        """
        Register a DICOM extension class.

        Args:
            extension_class: Extension class to register
            override: Whether to override existing registration

        Raises:
            DICOMExtensionError: If specialty already registered and override=False
        """
        # Create temporary instance to get specialty info
        try:
            temp_instance = extension_class()
            specialty = temp_instance.SPECIALTY
        except Exception as e:
            raise DICOMExtensionError(
                f"Failed to instantiate extension class {extension_class.__name__}: {e}"
            )

        if specialty in self._extensions and not override:
            raise DICOMExtensionError(
                f"Specialty '{specialty}' already registered with {self._extensions[specialty].__name__}. "
                f"Use override=True to replace."
            )

        self._extensions[specialty] = extension_class
        logger.info(f"Registered DICOM extension: {specialty} ({extension_class.__name__})")

    def get_extension(self, specialty: str) -> Optional[DICOMExtensionBase]:
        """
        Get an instance of a registered extension.

        Args:
            specialty: Specialty name (e.g., 'cardiology_ecg')

        Returns:
            Extension instance or None if not found
        """
        if specialty not in self._extensions:
            logger.warning(f"Extension not found for specialty: {specialty}")
            return None

        # Create and cache instance if not exists
        if specialty not in self._instances:
            try:
                self._instances[specialty] = self._extensions[specialty]()
            except Exception as e:
                logger.error(f"Failed to instantiate extension {specialty}: {e}")
                return None

        return self._instances[specialty]

    def get_all_specialties(self) -> List[str]:
        """Get list of all registered specialty names"""
        return list(self._extensions.keys())

    def get_extension_info(self, specialty: str) -> Optional[Dict]:
        """
        Get information about a registered extension.

        Args:
            specialty: Specialty name

        Returns:
            Extension info dictionary or None if not found
        """
        extension = self.get_extension(specialty)
        if extension is None:
            return None

        return extension.get_specialty_info()

    def get_all_extensions_info(self) -> Dict[str, Dict]:
        """
        Get information about all registered extensions.

        Returns:
            Dictionary mapping specialty names to extension info
        """
        info = {}
        for specialty in self.get_all_specialties():
            extension_info = self.get_extension_info(specialty)
            if extension_info:
                info[specialty] = extension_info
        return info

    def extract_from_file(
        self,
        filepath: str,
        specialties: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Extract metadata from DICOM file using specified or all extensions.

        Args:
            filepath: Path to DICOM file
            specialties: List of specialties to use (None = all registered)

        Returns:
            Dictionary mapping specialty names to extraction results
        """
        if specialties is None:
            specialties = self.get_all_specialties()

        results = {}
        for specialty in specialties:
            extension = self.get_extension(specialty)
            if extension and extension.validate_dicom_file(filepath):
                try:
                    result = extension.extract_specialty_metadata(filepath)
                    results[specialty] = result
                except Exception as e:
                    logger.error(f"Extraction failed for {specialty}: {e}")
                    results[specialty] = {
                        "specialty": specialty,
                        "error": str(e),
                        "fields_extracted": 0
                    }

        return results

    def get_total_field_capacity(self) -> int:
        """
        Get total number of fields that can be extracted across all extensions.

        Returns:
            Total field count
        """
        total = 0
        for specialty in self.get_all_specialties():
            extension = self.get_extension(specialty)
            if extension:
                total += extension.get_field_count()
        return total

    def auto_discover_extensions(self, package_path: str) -> None:
        """
        Automatically discover and register extension classes from a package.

        Args:
            package_path: Python package path (e.g., 'server.extractor.modules.dicom_extensions')
        """
        import importlib
        import inspect

        try:
            package = importlib.import_module(package_path)
            package_dir = Path(package.__file__).parent

            # Find all Python modules in package
            for module_file in package_dir.glob("*.py"):
                if module_file.name.startswith("__"):
                    continue

                module_name = f"{package_path}.{module_file.stem}"

                try:
                    module = importlib.import_module(module_name)

                    # Find all classes that inherit from DICOMExtensionBase
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, DICOMExtensionBase) and
                            obj is not DICOMExtensionBase and
                            obj.__module__ == module_name):

                            self.register_extension(obj)

                except Exception as e:
                    logger.debug(f"Failed to import {module_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to auto-discover extensions in {package_path}: {e}")


# Global registry instance
_global_registry: Optional[DICOMExtensionRegistry] = None


def get_global_registry() -> DICOMExtensionRegistry:
    """Get the global extension registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = DICOMExtensionRegistry()
    return _global_registry


def register_extension(extension_class: Type[DICOMExtensionBase]) -> None:
    """Register an extension with the global registry"""
    get_global_registry().register_extension(extension_class)


def get_extension(specialty: str) -> Optional[DICOMExtensionBase]:
    """Get an extension instance from the global registry"""
    return get_global_registry().get_extension(specialty)


def get_all_extensions() -> Dict[str, DICOMExtensionBase]:
    """Get all extension instances from the global registry"""
    registry = get_global_registry()
    extensions = {}
    for specialty in registry.get_all_specialties():
        extension = registry.get_extension(specialty)
        if extension:
            extensions[specialty] = extension
    return extensions


def get_extension_by_specialty(specialty: str) -> Optional[DICOMExtensionBase]:
    """Get an extension by specialty name (alias for get_extension)"""
    return get_extension(specialty)


def initialize_extensions() -> None:
    """
    Initialize all extensions by auto-discovery and registration.
    Call this once at application startup.
    """
    registry = get_global_registry()

    # Auto-discover extensions from this package
    try:
        registry.auto_discover_extensions("server.extractor.modules.dicom_extensions")
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {e}")

    logger.info(
        f"DICOM Extensions initialized: {registry.get_total_field_capacity()} fields "
        f"across {len(registry.get_all_specialties())} specialties"
    )
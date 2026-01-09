"""
Field Builder for Unified Field Registry

This module provides a fluent builder class for creating FieldDefinition
instances with a clean, chainable API.
"""

from typing import Any, Optional, List, Dict, Union
from field_definitions import (
    FieldDefinition,
    FieldType,
    FieldTier,
    DisplayLevel,
    FieldSource,
    ValidationSeverity,
    ValidationRuleType,
    FieldValidationRule,
    FieldDeprecation,
    FieldMetadata,
)


class FieldBuilder:
    """
    Builder class for creating FieldDefinition instances.
    
    Provides a fluent interface for field creation, making it easy to
    construct complex field definitions with method chaining.
    
    Example:
        field = (FieldBuilder()
            .create("GPSLatitude", FieldType.GPS, FieldSource.EXIF, "Geographic latitude")
            .with_tier(FieldTier.FREE)
            .with_display(DisplayLevel.SIMPLE)
            .with_example({"latitude": 37.7749, "longitude": -122.4194})
            .with_keywords("location", "coordinates", "gps")
            .related_to("GPSLongitude", "GPSAltitude")
            .build())
    """
    
    def __init__(self):
        self._field: Optional[FieldDefinition] = None
        self._collection: Optional[str] = None
    
    # =========================================================================
    # Creation Methods
    # =========================================================================
    
    def create(
        self,
        name: str,
        field_type: FieldType,
        source: FieldSource,
        description: str
    ) -> 'FieldBuilder':
        """
        Start building a new field definition.
        
        Args:
            name: Unique name for the field
            field_type: Data type of the field
            source: Source standard (EXIF, IPTC, etc.)
            description: Brief description of the field
            
        Returns:
            Self for method chaining
        """
        self._field = FieldDefinition(
            name=name,
            field_type=field_type,
            source=source,
            description=description
        )
        return self
    
    def from_existing(self, field: FieldDefinition) -> 'FieldBuilder':
        """
        Start building from an existing field definition.
        Creates a copy that can be modified.
        
        Args:
            field: FieldDefinition to copy
            
        Returns:
            Self for method chaining
        """
        import copy
        self._field = copy.deepcopy(field)
        return self
    
    # =========================================================================
    # Identity Methods
    # =========================================================================
    
    def with_name(self, name: str) -> 'FieldBuilder':
        """Set the field name"""
        if self._field:
            self._field.name = name
        return self
    
    def with_standard_name(self, standard_name: str) -> 'FieldBuilder':
        """Set the standard name (e.g., 'GPSLatitude' for EXIF)"""
        if self._field:
            self._field.standard_name = standard_name
        return self
    
    def with_field_id(self, field_id: str) -> 'FieldBuilder':
        """Set the field UUID"""
        if self._field:
            self._field.field_id = field_id
        return self
    
    # =========================================================================
    # Classification Methods
    # =========================================================================
    
    def with_type(self, field_type: FieldType) -> 'FieldBuilder':
        """Set the field data type"""
        if self._field:
            self._field.field_type = field_type
        return self
    
    def with_source(self, source: FieldSource) -> 'FieldBuilder':
        """Set the field source"""
        if self._field:
            self._field.source = source
        return self
    
    def with_tier(self, tier: FieldTier) -> 'FieldBuilder':
        """Set the access tier"""
        if self._field:
            self._field.tier = tier
        return self
    
    def free(self) -> 'FieldBuilder':
        """Set tier to FREE"""
        return self.with_tier(FieldTier.FREE)
    
    def professional(self) -> 'FieldBuilder':
        """Set tier to PROFESSIONAL"""
        return self.with_tier(FieldTier.PROFESSIONAL)
    
    def forensic(self) -> 'FieldBuilder':
        """Set tier to FORENSIC"""
        return self.with_tier(FieldTier.FORENSIC)
    
    def enterprise(self) -> 'FieldBuilder':
        """Set tier to ENTERPRISE"""
        return self.with_tier(FieldTier.ENTERPRISE)
    
    def with_display(self, display: DisplayLevel) -> 'FieldBuilder':
        """Set the display level"""
        if self._field:
            self._field.display = display
        return self
    
    def simple_display(self) -> 'FieldBuilder':
        """Set display to SIMPLE (always visible)"""
        return self.with_display(DisplayLevel.SIMPLE)
    
    def advanced_display(self) -> 'FieldBuilder':
        """Set display to ADVANCED"""
        return self.with_display(DisplayLevel.ADVANCED)
    
    def raw_display(self) -> 'FieldBuilder':
        """Set display to RAW (expert view only)"""
        return self.with_display(DisplayLevel.RAW)
    
    # =========================================================================
    # Documentation Methods
    # =========================================================================
    
    def with_description(self, description: str) -> 'FieldBuilder':
        """Set the brief description"""
        if self._field:
            self._field.description = description
        return self
    
    def with_long_description(self, description: str) -> 'FieldBuilder':
        """Set the detailed description"""
        if self._field:
            self._field.long_description = description
        return self
    
    def with_significance(self, significance: str) -> 'FieldBuilder':
        """Set the significance/explanation text"""
        if self._field:
            self._field.significance = significance
        return self
    
    # =========================================================================
    # Value Methods
    # =========================================================================
    
    def with_example(self, example: Any) -> 'FieldBuilder':
        """Set an example value for documentation"""
        if self._field:
            self._field.example_value = example
        return self
    
    def with_default(self, default: Any) -> 'FieldBuilder':
        """Set a default value"""
        if self._field:
            self._field.default_value = default
        return self
    
    # =========================================================================
    # Constraint Methods
    # =========================================================================
    
    def required(self) -> 'FieldBuilder':
        """Mark field as required"""
        if self._field:
            self._field.is_required = True
        return self
    
    def optional(self) -> 'FieldBuilder':
        """Mark field as optional (default)"""
        if self._field:
            self._field.is_required = False
        return self
    
    def deprecated(
        self,
        deprecated_version: str,
        removal_version: str,
        reason: str,
        alternative: Optional[str] = None,
        migration_path: Optional[str] = None
    ) -> 'FieldBuilder':
        """
        Mark field as deprecated.
        
        Args:
            deprecated_version: Version when deprecated
            removal_version: Version when will be removed
            reason: Reason for deprecation
            alternative: Alternative field to use
            migration_path: Path to migration documentation
        """
        if self._field:
            self._field.is_deprecated = True
            self._field.deprecation = FieldDeprecation(
                deprecated_version=deprecated_version,
                removal_version=removal_version,
                reason=reason,
                alternative_field=alternative,
                migration_path=migration_path
            )
        return self
    
    # =========================================================================
    # Validation Methods
    # =========================================================================
    
    def with_validation(
        self,
        rule_type: Union[str, ValidationRuleType],
        value: Any,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> 'FieldBuilder':
        """
        Add a validation rule.
        
        Args:
            rule_type: Type of validation (regex, range, choice, etc.)
            value: Rule value (pattern, range bounds, choices, etc.)
            message: Error/warning message
            severity: Severity level
        """
        if self._field:
            self._field.validation_rules.append(FieldValidationRule(
                rule_type=rule_type,
                value=value,
                message=message,
                severity=severity
            ))
        return self
    
    def regex_validation(
        self,
        pattern: str,
        message: str = "Value does not match required pattern"
    ) -> 'FieldBuilder':
        """Add a regex validation rule"""
        return self.with_validation(
            ValidationRuleType.REGEX,
            pattern,
            message
        )
    
    def range_validation(
        self,
        min_val: float,
        max_val: float,
        message: str = "Value is out of allowed range"
    ) -> 'FieldBuilder':
        """Add a numeric range validation rule"""
        return self.with_validation(
            ValidationRuleType.RANGE,
            (min_val, max_val),
            message
        )
    
    def length_validation(
        self,
        min_len: int,
        max_len: int,
        message: str = "Value length is out of allowed range"
    ) -> 'FieldBuilder':
        """Add a string length validation rule"""
        return self.with_validation(
            ValidationRuleType.LENGTH,
            (min_len, max_len),
            message
        )
    
    def choice_validation(
        self,
        choices: List[Any],
        message: str = "Value is not an allowed choice"
    ) -> 'FieldBuilder':
        """Add a choice validation rule"""
        return self.with_validation(
            ValidationRuleType.CHOICE,
            choices,
            message
        )
    
    def email_validation(
        self,
        message: str = "Invalid email format"
    ) -> 'FieldBuilder':
        """Add email format validation"""
        return self.with_validation(
            ValidationRuleType.EMAIL,
            True,
            message
        )
    
    def url_validation(
        self,
        message: str = "Invalid URL format"
    ) -> 'FieldBuilder':
        """Add URL format validation"""
        return self.with_validation(
            ValidationRuleType.URL,
            True,
            message
        )
    
    def ip_address_validation(
        self,
        message: str = "Invalid IP address format"
    ) -> 'FieldBuilder':
        """Add IP address validation"""
        return self.with_validation(
            ValidationRuleType.IP_ADDRESS,
            True,
            message
        )
    
    def uuid_validation(
        self,
        message: str = "Invalid UUID format"
    ) -> 'FieldBuilder':
        """Add UUID format validation"""
        return self.with_validation(
            ValidationRuleType.UUID,
            True,
            message
        )
    
    # =========================================================================
    # Metadata Methods
    # =========================================================================
    
    def with_keywords(self, *keywords: str) -> 'FieldBuilder':
        """Add search keywords"""
        if self._field:
            self._field.metadata.search_keywords.extend(keywords)
        return self
    
    def with_categories(self, *categories: str) -> 'FieldBuilder':
        """Add category tags"""
        if self._field:
            self._field.metadata.category_tags.extend(categories)
        return self
    
    def with_examples(self, *examples: str) -> 'FieldBuilder':
        """Add usage examples"""
        if self._field:
            self._field.metadata.usage_examples.extend(examples)
        return self
    
    def related_to(self, *field_names: str) -> 'FieldBuilder':
        """Mark related fields"""
        if self._field:
            self._field.metadata.related_fields.extend(field_names)
        return self
    
    def with_aliases(self, *aliases: str) -> 'FieldBuilder':
        """Add alias names"""
        if self._field:
            self._field.metadata.alias_names.extend(aliases)
        return self
    
    def with_see_also(self, *references: str) -> 'FieldBuilder':
        """Add see also references"""
        if self._field:
            self._field.metadata.see_also_references.extend(references)
        return self
    
    def with_parent(self, parent_field: str) -> 'FieldBuilder':
        """Set parent field"""
        if self._field:
            self._field.metadata.parent_field = parent_field
        return self
    
    def with_children(self, *child_fields: str) -> 'FieldBuilder':
        """Add child fields"""
        if self._field:
            self._field.metadata.child_fields.extend(child_fields)
        return self
    
    def with_extraction_cost(self, cost: str) -> 'FieldBuilder':
        """Set extraction cost (low, medium, high)"""
        if self._field:
            self._field.metadata.extraction_cost = cost
        return self
    
    def computed(self, dependencies: Optional[List[str]] = None) -> 'FieldBuilder':
        """Mark field as computed with optional dependencies"""
        if self._field:
            self._field.metadata.is_computed = True
            if dependencies:
                self._field.metadata.computation_dependencies = dependencies
        return self
    
    def since_version(self, version: str) -> 'FieldBuilder':
        """Set version when field was introduced"""
        if self._field:
            self._field.metadata.since_version = version
        return self
    
    # =========================================================================
    # Extension Methods
    # =========================================================================
    
    def compatible_with(self, *extensions: str) -> 'FieldBuilder':
        """Mark compatible extensions"""
        if self._field:
            self._field.compatible_extensions.extend(extensions)
        return self
    
    def with_extension(self, extension: str) -> 'FieldBuilder':
        """Add a compatible extension"""
        return self.compatible_with(extension)
    
    def for_dicom(self) -> 'FieldBuilder':
        """Mark as compatible with DICOM extensions"""
        return self.compatible_with("dicom_base", "dicom_cardiology", 
                                     "dicom_neurology", "dicom_radiology")
    
    def for_image(self) -> 'FieldBuilder':
        """Mark as compatible with image extensions"""
        return self.compatible_with("image_basic", "image_advanced", 
                                     "image_enhanced")
    
    def for_audio(self) -> 'FieldBuilder':
        """Mark as compatible with audio extensions"""
        return self.compatible_with("audio_basic", "audio_advanced")
    
    def for_video(self) -> 'FieldBuilder':
        """Mark as compatible with video extensions"""
        return self.compatible_with("video_basic", "video_advanced")
    
    # =========================================================================
    # Collection Methods
    # =========================================================================
    
    def in_collection(self, collection_id: str) -> 'FieldBuilder':
        """Specify collection to add field to"""
        self._collection = collection_id
        return self
    
    # =========================================================================
    # Build Method
    # =========================================================================
    
    def build(self) -> FieldDefinition:
        """
        Build and return the field definition.
        
        Returns:
            The constructed FieldDefinition
            
        Raises:
            ValueError: If no field has been created
        """
        if not self._field:
            raise ValueError(
                "No field has been created. Call create() first."
            )
        
        field = self._field
        self._field = None
        self._collection = None
        
        return field
    
    def build_with_collection(self) -> tuple:
        """
        Build field and return with collection name.
        
        Returns:
            Tuple of (FieldDefinition, collection_name_or_None)
        """
        collection = self._collection
        field = self.build()
        return field, collection
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def copy(self) -> 'FieldBuilder':
        """Create a copy of this builder"""
        import copy
        builder = FieldBuilder()
        builder._field = copy.deepcopy(self._field)
        builder._collection = self._collection
        return builder
    
    def reset(self) -> 'FieldBuilder':
        """Reset the builder"""
        self._field = None
        self._collection = None
        return self
    
    @property
    def field(self) -> Optional[FieldDefinition]:
        """Get the current field being built (for inspection)"""
        return self._field
    
    def __repr__(self) -> str:
        if self._field:
            return f"FieldBuilder(field={self._field.name}, type={self._field.field_type.value})"
        return "FieldBuilder(empty)"


# ============================================================================
# Pre-built Field Creators
# ============================================================================

class EXIFFieldBuilder(FieldBuilder):
    """Specialized builder for EXIF fields"""
    
    def create(
        self,
        name: str,
        field_type: FieldType,
        description: str
    ) -> 'FieldBuilder':
        return super().create(
            name, field_type, FieldSource.EXIF, description
        )


class XMPFieldBuilder(FieldBuilder):
    """Specialized builder for XMP fields"""
    
    def create(
        self,
        name: str,
        field_type: FieldType,
        description: str
    ) -> 'FieldBuilder':
        return super().create(
            name, field_type, FieldSource.XMP, description
        )


class DICOMFieldBuilder(FieldBuilder):
    """Specialized builder for DICOM fields"""
    
    def create(
        self,
        name: str,
        field_type: FieldType,
        description: str
    ) -> 'FieldBuilder':
        return super().create(
            name, field_type, FieldSource.DICOM, description
        ).for_dicom()


# ============================================================================
# Quick Field Creation Helpers
# ============================================================================

def create_simple_field(
    name: str,
    field_type: FieldType,
    source: FieldSource,
    description: str,
    tier: FieldTier = FieldTier.FREE,
    example: Optional[Any] = None
) -> FieldDefinition:
    """
    Quick helper to create a simple field.
    
    Args:
        name: Field name
        field_type: Data type
        source: Field source
        description: Description
        tier: Access tier
        example: Example value
        
    Returns:
        FieldDefinition
    """
    return (FieldBuilder()
        .create(name, field_type, source, description)
        .with_tier(tier)
        .with_example(example)
        .build())


def create_gps_field(
    name: str,
    description: str,
    tier: FieldTier = FieldTier.FREE
) -> FieldDefinition:
    """Create a GPS-related field"""
    return (FieldBuilder()
        .create(name, FieldType.GPS, FieldSource.EXIF, description)
        .with_tier(tier)
        .simple_display()
        .with_keywords("gps", "location", "coordinates")
        .build())


def create_datetime_field(
    name: str,
    description: str,
    tier: FieldTier = FieldTier.FREE
) -> FieldDefinition:
    """Create a datetime field"""
    return (FieldBuilder()
        .create(name, FieldType.DATETIME, FieldSource.EXIF, description)
        .with_tier(tier)
        .with_display(DisplayLevel.ADVANCED)
        .build())


# Export all
__all__ = [
    "FieldBuilder",
    "EXIFFieldBuilder",
    "XMPFieldBuilder", 
    "DICOMFieldBuilder",
    "create_simple_field",
    "create_gps_field",
    "create_datetime_field",
]

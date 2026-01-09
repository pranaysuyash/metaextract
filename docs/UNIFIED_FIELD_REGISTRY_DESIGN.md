# Unified Field Registry System Design

## Executive Summary

This document outlines the design for a unified field registry system that will serve as the single source of truth for all image metadata fields in the MetaExtract project. The system addresses the fragmentation identified in the audit findings, where field definitions are currently spread across 7+ locations with significant gaps (1,000+ missing fields).

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [System Architecture](#system-architecture)
3. [Field Definition Dataclass Design](#field-definition-dataclass-design)
4. [Class Structure and Methods](#class-structure-and-methods)
5. [Integration with Existing Extension System](#integration-with-existing-extension-system)
6. [TypeScript Code Generation](#typescript-code-generation)
7. [Migration Strategy](#migration-strategy)
8. [Gap Analysis and Field Coverage](#gap-analysis-and-field-coverage)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Current State Analysis

### Problem Statement

The MetaExtract codebase currently has field definitions scattered across multiple locations:

| Location | Type | Fields | Status |
|----------|------|--------|--------|
| `server/extractor/modules/field_registry.py` | Central registry (partial) | ~150 | Basic definitions only |
| `server/extractor/modules/exif.py` | Extraction module | 784 | Inventory-based |
| `server/extractor/modules/iptc_xmp.py` | Extraction module | 4,367 | Inventory-based |
| `server/extractor/modules/makernotes_complete.py` | Extraction module | 4,760 | Inventory-based |
| `server/extractor/modules/dicom_complete_ultimate.py` | Extraction module | 2,285 | Inventory-based |
| `server/extractor/modules/audio_codec_details.py` | Extraction module | 930 | Inventory-based |
| `server/extractor/modules/image_extensions/registry.py` | Extension registry | ~20 | Basic structure |
| `server/extractor/modules/dicom_extensions/registry.py` | Extension registry | ~30 | Basic structure |
| **Total Unique** | **~15+ locations** | **53,287 inventory** | **5+ locations untracked** |

### Audit Findings

1. **Fragmentation**: No single source of truth exists
2. **Inconsistency**: Different naming conventions, type systems, and metadata across modules
3. **Gaps**: 1,000+ fields identified as missing from registry vs. inventory
4. **Maintenance Burden**: Adding new fields requires updates in multiple places
5. **Type Safety**: No runtime validation of field values
6. **TypeScript Disconnect**: Python field definitions not automatically synced to TypeScript

---

## System Architecture

### Core Components

```
+-----------------------------------------------------------------------------+
|                        Unified Field Registry System                        |
+-----------------------------------------------------------------------------+
|                                                                              |
|  +----------------------------------------------------------------------+    |
|  |                      FieldRegistryCore                                |    |
|  |  +--------------+  +--------------+  +--------------------------+   |    |
|  |  | FieldBuilder |  | FieldValidator|  | FieldQueryEngine         |   |    |
|  |  +--------------+  +--------------+  +--------------------------+   |    |
|  +----------------------------------------------------------------------+    |
|                                                                              |
|  +----------------------------------------------------------------------+    |
|  |                    Extension Integration Layer                         |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  |  | ExtensionMapper  |  | FieldExtractor   |  | CapabilityRouter |   |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  +----------------------------------------------------------------------+    |
|                                                                              |
|  +----------------------------------------------------------------------+    |
|  |                     Code Generation Layer                              |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  |  | TypeScriptGen    |  | PythonGen        |  | DocumentationGen |   |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  +----------------------------------------------------------------------+    |
|                                                                              |
|  +----------------------------------------------------------------------+    |
|  |                     Storage & Persistence                              |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  |  | RegistryStore    |  | VersionControl   |  | MigrationManager |   |    |
|  |  +------------------+  +------------------+  +------------------+   |    |
|  +----------------------------------------------------------------------+    |
|                                                                              |
+-----------------------------------------------------------------------------+
```

### Design Principles

1. **Single Source of Truth**: All field definitions live in one location
2. **Immutability**: Field definitions are versioned and immutable once committed
3. **Type Safety**: Runtime validation of field values against definitions
4. **Discoverability**: Easy querying and filtering of available fields
5. **Extensibility**: Clear patterns for adding new fields and extensions
6. **Bidirectional Sync**: Python definitions generate TypeScript interfaces

---

## Field Definition Dataclass Design

### Core Dataclasses

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid


class FieldType(Enum):
    """Supported field data types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    BINARY = "binary"
    ARRAY = "array"
    OBJECT = "object"
    GPS = "gps"
    RATIONAL = "rational"
    UUID = "uuid"
    ENUM = "enum"
    COLOR = "color"
    HASH = "hash"


class FieldTier(Enum):
    """Access tier for field"""
    FREE = "free"
    PROFESSIONAL = "professional"
    FORENSIC = "forensic"
    ENTERPRISE = "enterprise"


class DisplayLevel(Enum):
    """UI display level"""
    SIMPLE = "simple"
    ADVANCED = "advanced"
    RAW = "raw"


class FieldSource(Enum):
    """Origin of field definition"""
    EXIF = "EXIF"
    IPTC = "IPTC"
    XMP = "XMP"
    MAKERNOTE = "MakerNote"
    DICOM = "DICOM"
    QUICKTIME = "QuickTime"
    MATROSKA = "Matroska"
    RIFF = "RIFF"
    PDF = "PDF"
    FLAC = "FLAC"
    VORBIS = "Vorbis"
    ID3 = "ID3"
    CUSTOM = "custom"


class ValidationSeverity(Enum):
    """Severity of validation rules"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class FieldValidationRule:
    """Validation rule for field values"""
    rule_type: str  # regex, range, pattern, custom
    value: Any
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


@dataclass
class FieldDeprecation:
    """Deprecation information for fields"""
    deprecated_version: str
    removal_version: str
    reason: str
    migration_path: Optional[str] = None
    alternative_field: Optional[str] = None


@dataclass
class FieldMetadata:
    """Extended metadata for fields"""
    # Search and discovery
    search_keywords: List[str] = field(default_factory=list)
    category_tags: List[str] = field(default_factory=list)
    
    # Documentation
    usage_examples: List[str] = field(default_factory=list)
    related_fields: List[str] = field(default_factory=list)
    see_also_references: List[str] = field(default_factory=list)
    
    # Relationships
    parent_field: Optional[str] = None
    child_fields: List[str] = field(default_factory=list)
    alias_names: List[str] = field(default_factory=list)
    
    # Performance hints
    extraction_cost: str = "low"  # low, medium, high
    is_computed: bool = False
    computation_dependencies: List[str] = field(default_factory=list)


@dataclass
class FieldDefinition:
    """
    Complete definition of a metadata field.
    
    This is the core dataclass representing a single field in the registry.
    All field definitions must conform to this structure.
    """
    # Identity
    name: str
    field_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard_name: str  # e.g., "GPSLatitude" for EXIF, "PatientName" for DICOM
    
    # Classification
    field_type: FieldType
    source: FieldSource
    tier: FieldTier = FieldTier.FREE
    display: DisplayLevel = DisplayLevel.ADVANCED
    
    # Documentation
    description: str
    long_description: Optional[str] = None
    significance: Optional[str] = None
    
    # Examples and defaults
    example_value: Optional[Any] = None
    default_value: Optional[Any] = None
    
    # Validation
    validation_rules: List[FieldValidationRule] = field(default_factory=list)
    is_required: bool = False
    is_deprecated: bool = False
    deprecation: Optional[FieldDeprecation] = None
    
    # Metadata
    metadata: FieldMetadata = field(default_factory=FieldMetadata)
    
    # Version tracking
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    
    # Extension mapping
    compatible_extensions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = {
            "name": self.name,
            "field_id": self.field_id,
            "standard_name": self.standard_name,
            "field_type": self.field_type.value,
            "source": self.source.value,
            "tier": self.tier.value,
            "display": self.display.value,
            "description": self.description,
            "long_description": self.long_description,
            "significance": self.significance,
            "example_value": self.example_value,
            "default_value": self.default_value,
            "validation_rules": [
                {
                    "rule_type": r.rule_type,
                    "value": r.value,
                    "message": r.message,
                    "severity": r.severity.value
                }
                for r in self.validation_rules
            ],
            "is_required": self.is_required,
            "is_deprecated": self.is_deprecated,
            "deprecation": {
                "deprecated_version": self.deprecation.deprecated_version,
                "removal_version": self.deprecation.removal_version,
                "reason": self.deprecation.reason,
                "migration_path": self.deprecation.migration_path,
                "alternative_field": self.deprecation.alternative_field
            } if self.deprecation else None,
            "metadata": {
                "search_keywords": self.metadata.search_keywords,
                "category_tags": self.metadata.category_tags,
                "usage_examples": self.metadata.usage_examples,
                "related_fields": self.metadata.related_fields,
                "see_also_references": self.metadata.see_also_references,
                "parent_field": self.metadata.parent_field,
                "child_fields": self.metadata.child_fields,
                "alias_names": self.metadata.alias_names,
                "extraction_cost": self.metadata.extraction_cost,
                "is_computed": self.metadata.is_computed,
                "computation_dependencies": self.metadata.computation_dependencies
            },
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "compatible_extensions": self.compatible_extensions
        }
        return data
```

### Field Collection Class

```python
@dataclass
class FieldCollection:
    """
    A collection of related field definitions.
    Groups fields by domain, standard, or extension.
    """
    collection_id: str
    name: str
    description: str
    source: str  # e.g., "EXIF", "MakerNotes:Canon", "DICOM"
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    
    # Statistics
    total_fields: int = 0
    free_fields: int = 0
    professional_fields: int = 0
    forensic_fields: int = 0
    enterprise_fields: int = 0
    
    # Metadata
    version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_field(self, field: FieldDefinition) -> None:
        """Add a field to the collection"""
        self.fields[field.name] = field
        self._recalculate_stats()
    
    def remove_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Remove a field from the collection"""
        field = self.fields.pop(field_name, None)
        if field:
            self._recalculate_stats()
        return field
    
    def _recalculate_stats(self) -> None:
        """Recalculate field statistics"""
        self.total_fields = len(self.fields)
        self.free_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.FREE)
        self.professional_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.PROFESSIONAL)
        self.forensic_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.FORENSIC)
        self.enterprise_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.ENTERPRISE)
```

---

## Class Structure and Methods

### FieldRegistryCore

```python
class FieldRegistryCore:
    """
    Core registry class managing all field definitions.
    This is the main entry point for the unified field registry system.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the field registry.
        
        Args:
            storage_path: Optional path to persistence storage
        """
        self._fields: Dict[str, FieldDefinition] = {}
        self._collections: Dict[str, FieldCollection] = {}
        self._indexes: Dict[str, Dict[str, FieldDefinition]] = {}
        self._storage_path = storage_path
        self._version_history: List[Dict[str, Any]] = []
        
        # Initialize built-in indexes
        self._init_indexes()
    
    # =========================================================================
    # Field Management
    # =========================================================================
    
    def register_field(
        self,
        field: FieldDefinition,
        collection: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        Register a new field definition.
        
        Args:
            field: FieldDefinition to register
            collection: Optional collection name to add to
            validate: Whether to validate the field before registration
            
        Returns:
            True if registration successful
            
        Raises:
            FieldValidationError: If validation fails
            FieldAlreadyExistsError: If field with same name exists
        """
        if validate:
            self._validate_field(field)
        
        if field.name in self._fields:
            raise FieldAlreadyExistsError(
                f"Field '{field.name}' already exists in registry"
            )
        
        # Set standard name if not provided
        if not field.standard_name:
            field.standard_name = field.name
        
        # Add to registry
        self._fields[field.name] = field
        
        # Add to collection if specified
        if collection:
            self._add_to_collection(field, collection)
        
        # Update indexes
        self._update_indexes(field)
        
        # Persist if storage configured
        if self._storage_path:
            self._persist_field(field)
        
        return True
    
    def register_field_batch(
        self,
        fields: List[FieldDefinition],
        collection: Optional[str] = None,
        fail_on_error: bool = False
    ) -> Dict[str, bool]:
        """
        Register multiple fields at once.
        
        Args:
            fields: List of FieldDefinition objects
            collection: Optional collection name for all fields
            fail_on_error: Whether to stop on first error
            
        Returns:
            Dictionary mapping field names to success status
        """
        results = {}
        for field in fields:
            try:
                success = self.register_field(field, collection, validate=True)
                results[field.name] = success
            except Exception as e:
                results[field.name] = False
                if fail_on_error:
                    raise
                # Log warning for non-fatal errors
                logger.warning(f"Failed to register field '{field.name}': {e}")
        return results
    
    def unregister_field(self, field_name: str) -> bool:
        """
        Remove a field from the registry.
        
        Args:
            field_name: Name of field to remove
            
        Returns:
            True if field was removed
        """
        if field_name not in self._fields:
            return False
        
        field = self._fields.pop(field_name)
        
        # Remove from indexes
        self._remove_from_indexes(field)
        
        # Remove from collections
        for collection in self._collections.values():
            collection.remove_field(field_name)
        
        return True
    
    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Get a field definition by name"""
        return self._fields.get(field_name)
    
    def get_field_by_id(self, field_id: str) -> Optional[FieldDefinition]:
        """Get a field definition by UUID"""
        for field in self._fields.values():
            if field.field_id == field_id:
                return field
        return None
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_all_fields(self) -> Dict[str, FieldDefinition]:
        """Get all registered fields"""
        return self._fields.copy()
    
    def get_fields_by_source(self, source: FieldSource) -> Dict[str, FieldDefinition]:
        """Get all fields from a specific source"""
        return {
            name: field for name, field in self._fields.items()
            if field.source == source
        }
    
    def get_fields_by_type(self, field_type: FieldType) -> Dict[str, FieldDefinition]:
        """Get all fields of a specific type"""
        return {
            name: field for name, field in self._fields.items()
            if field.field_type == field_type
        }
    
    def get_fields_by_tier(self, tier: FieldTier) -> Dict[str, FieldDefinition]:
        """Get all fields accessible at a specific tier"""
        tier_order = [FieldTier.FREE, FieldTier.PROFESSIONAL, FieldTier.FORENSIC, FieldTier.ENTERPRISE]
        max_tier_index = tier_order.index(tier)
        
        return {
            name: field for name, field in self._fields.items()
            if tier_order.index(field.tier) <= max_tier_index
        }
    
    def get_fields_for_display(self, display: DisplayLevel) -> Dict[str, FieldDefinition]:
        """Get all fields visible at a specific display level"""
        display_order = [DisplayLevel.SIMPLE, DisplayLevel.ADVANCED, DisplayLevel.RAW]
        max_display_index = display_order.index(display)
        
        return {
            name: field for name, field in self._fields.items()
            if display_order.index(field.display) <= max_display_index
        }
    
    def search_fields(
        self,
        query: str,
        search_metadata: bool = True,
        max_results: int = 100
    ) -> List[FieldDefinition]:
        """
        Search fields by name or metadata.
        
        Args:
            query: Search query string
            search_metadata: Whether to search in field metadata
            max_results: Maximum number of results
            
        Returns:
            List of matching FieldDefinition objects
        """
        query = query.lower()
        results = []
        
        for field in self._fields.values():
            # Check name
            if query in field.name.lower():
                results.append(field)
                continue
            
            # Check description
            if query in field.description.lower():
                results.append(field)
                continue
            
            # Check metadata if enabled
            if search_metadata:
                if query in field.metadata.search_keywords:
                    results.append(field)
                    continue
                
                if query in field.metadata.category_tags:
                    results.append(field)
                    continue
        
        return results[:max_results]
    
    def find_related_fields(self, field_name: str) -> List[FieldDefinition]:
        """Find fields related to a given field"""
        field = self.get_field(field_name)
        if not field:
            return []
        
        related = []
        
        # Check explicit relationships
        for related_name in field.metadata.related_fields:
            related_field = self.get_field(related_name)
            if related_field:
                related.append(related_field)
        
        # Check parent/child relationships
        if field.metadata.parent_field:
            parent = self.get_field(field.metadata.parent_field)
            if parent:
                related.append(parent)
        
        for child_name in field.metadata.child_fields:
            child = self.get_field(child_name)
            if child:
                related.append(child)
        
        return related
    
    # =========================================================================
    # Collection Management
    # =========================================================================
    
    def create_collection(
        self,
        collection_id: str,
        name: str,
        description: str,
        source: str
    ) -> FieldCollection:
        """Create a new field collection"""
        if collection_id in self._collections:
            raise ValueError(f"Collection '{collection_id}' already exists")
        
        collection = FieldCollection(
            collection_id=collection_id,
            name=name,
            description=description,
            source=source
        )
        self._collections[collection_id] = collection
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[FieldCollection]:
        """Get a field collection by ID"""
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> Dict[str, FieldCollection]:
        """Get all field collections"""
        return self._collections.copy()
    
    def _add_to_collection(self, field: FieldDefinition, collection_id: str) -> None:
        """Add a field to a collection"""
        collection = self._collections.get(collection_id)
        if collection:
            collection.add_field(field)
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    def validate_field_value(
        self,
        field_name: str,
        value: Any
    ) -> ValidationResult:
        """
        Validate a value against field definition.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            
        Returns:
            ValidationResult with success status and messages
        """
        field = self.get_field(field_name)
        if not field:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown field: {field_name}"],
                warnings=[]
            )
        
        errors = []
        warnings = []
        
        # Check required
        if value is None and field.is_required:
            errors.append(f"Field '{field_name}' is required but value is None")
        
        # Apply validation rules
        for rule in field.validation_rules:
            rule_result = self._apply_validation_rule(value, rule)
            if rule_result.severity == ValidationSeverity.ERROR:
                errors.append(rule_result.message)
            elif rule_result.severity == ValidationSeverity.WARNING:
                warnings.append(rule_result.message)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_field(self, field: FieldDefinition) -> None:
        """Validate a field definition before registration"""
        if not field.name:
            raise FieldValidationError("Field name is required")
        
        if not field.description:
            raise FieldValidationError("Field description is required")
        
        if field.example_value is not None:
            # Validate example against rules
            result = self.validate_field_value(field.name, field.example_value)
            if not result.is_valid:
                raise FieldValidationError(
                    f"Invalid example value: {result.errors}"
                )
    
    def _apply_validation_rule(
        self,
        value: Any,
        rule: FieldValidationRule
    ) -> ValidationResult:
        """Apply a single validation rule"""
        import re
        
        try:
            if rule.rule_type == "regex":
                if not re.match(str(rule.value), str(value)):
                    return ValidationResult(
                        is_valid=False,
                        errors=[rule.message],
                        warnings=[]
                    )
            elif rule.rule_type == "range":
                min_val, max_val = rule.value
                if not (min_val <= value <= max_val):
                    return ValidationResult(
                        is_valid=False,
                        errors=[rule.message],
                        warnings=[]
                    )
            # Add more rule types as needed
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation rule error: {str(e)}"],
                warnings=[]
            )
        
        return ValidationResult(is_valid=True, errors=[], warnings=[])
    
    # =========================================================================
    # Index Management
    # =========================================================================
    
    def _init_indexes(self) -> None:
        """Initialize search indexes"""
        self._indexes = {
            "by_source": {},
            "by_type": {},
            "by_tier": {},
            "by_display": {},
            "by_extension": {}
        }
    
    def _update_indexes(self, field: FieldDefinition) -> None:
        """Update all indexes with a field"""
        # By source
        if field.source.value not in self._indexes["by_source"]:
            self._indexes["by_source"][field.source.value] = {}
        self._indexes["by_source"][field.source.value][field.name] = field
        
        # By type
        if field.field_type.value not in self._indexes["by_type"]:
            self._indexes["by_type"][field.field_type.value] = {}
        self._indexes["by_type"][field.field_type.value][field.name] = field
        
        # By tier
        if field.tier.value not in self._indexes["by_tier"]:
            self._indexes["by_tier"][field.tier.value] = {}
        self._indexes["by_tier"][field.tier.value][field.name] = field
        
        # By display
        if field.display.value not in self._indexes["by_display"]:
            self._indexes["by_display"][field.display.value] = {}
        self._indexes["by_display"][field.display.value][field.name] = field
        
        # By extension
        for ext in field.compatible_extensions:
            if ext not in self._indexes["by_extension"]:
                self._indexes["by_extension"][ext] = {}
            self._indexes["by_extension"][ext][field.name] = field
    
    def _remove_from_indexes(self, field: FieldDefinition) -> None:
        """Remove a field from all indexes"""
        for index_name in self._indexes:
            index = self._indexes[index_name]
            # Find and remove from nested dicts
            for key in list(index.keys()):
                if field.name in index[key]:
                    del index[key][field.name]
    
    # =========================================================================
    # Statistics and Reporting
    # =========================================================================
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        return {
            "total_fields": len(self._fields),
            "total_collections": len(self._collections),
            "by_source": {
                source: len(fields) 
                for source, fields in self._indexes["by_source"].items()
            },
            "by_tier": {
                tier: len(fields)
                for tier, fields in self._indexes["by_tier"].items()
            },
            "by_type": {
                ftype: len(fields)
                for ftype, fields in self._indexes["by_type"].items()
            },
            "indexes_maintained": list(self._indexes.keys())
        }
```

### FieldBuilder

```python
class FieldBuilder:
    """
    Builder class for creating FieldDefinition instances.
    Provides a fluent interface for field creation.
    """
    
    def __init__(self):
        self._field = None
    
    def create(
        self,
        name: str,
        field_type: FieldType,
        source: FieldSource,
        description: str
    ) -> 'FieldBuilder':
        """Start building a new field"""
        self._field = FieldDefinition(
            name=name,
            field_type=field_type,
            source=source,
            description=description
        )
        return self
    
    def with_standard_name(self, standard_name: str) -> 'FieldBuilder':
        """Set the standard name"""
        if self._field:
            self._field.standard_name = standard_name
        return self
    
    def with_tier(self, tier: FieldTier) -> 'FieldBuilder':
        """Set the access tier"""
        if self._field:
            self._field.tier = tier
        return self
    
    def with_display(self, display: DisplayLevel) -> 'FieldBuilder':
        """Set the display level"""
        if self._field:
            self._field.display = display
        return self
    
    def with_long_description(self, description: str) -> 'FieldBuilder':
        """Set the long description"""
        if self._field:
            self._field.long_description = description
        return self
    
    def with_significance(self, significance: str) -> 'FieldBuilder':
        """Set the significance text"""
        if self._field:
            self._field.significance = significance
        return self
    
    def with_example(self, example: Any) -> 'FieldBuilder':
        """Set an example value"""
        if self._field:
            self._field.example_value = example
        return self
    
    def with_default(self, default: Any) -> 'FieldBuilder':
        """Set a default value"""
        if self._field:
            self._field.default_value = default
        return self
    
    def required(self) -> 'FieldBuilder':
        """Mark field as required"""
        if self._field:
            self._field.is_required = True
        return self
    
    def deprecated(
        self,
        deprecated_version: str,
        removal_version: str,
        reason: str,
        alternative: Optional[str] = None
    ) -> 'FieldBuilder':
        """Mark field as deprecated"""
        if self._field:
            self._field.is_deprecated = True
            self._field.deprecation = FieldDeprecation(
                deprecated_version=deprecated_version,
                removal_version=removal_version,
                reason=reason,
                alternative_field=alternative
            )
        return self
    
    def with_validation(
        self,
        rule_type: str,
        value: Any,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> 'FieldBuilder':
        """Add a validation rule"""
        if self._field:
            self._field.validation_rules.append(FieldValidationRule(
                rule_type=rule_type,
                value=value,
                message=message,
                severity=severity
            ))
        return self
    
    def with_keywords(self, *keywords: str) -> 'FieldBuilder':
        """Add search keywords"""
        if self._field:
            self._field.metadata.search_keywords.extend(keywords)
        return self
    
    def with_category(self, *categories: str) -> 'FieldBuilder':
        """Add category tags"""
        if self._field:
            self._field.metadata.category_tags.extend(categories)
        return self
    
    def related_to(self, *field_names: str) -> 'FieldBuilder':
        """Mark related fields"""
        if self._field:
            self._field.metadata.related_fields.extend(field_names)
        return self
    
    def compatible_with(self, *extensions: str) -> 'FieldBuilder':
        """Mark compatible extensions"""
        if self._field:
            self._field.compatible_extensions.extend(extensions)
        return self
    
    def build(self) -> FieldDefinition:
        """Build and return the field definition"""
        if not self._field:
            raise ValueError("No field has been created")
        
        field = self._field
        self._field = None  # Reset for next build
        return field
```

---

## Integration with Existing Extension System

### Extension Integration Layer

```python
class ExtensionMapper:
    """
    Maps fields to their compatible extraction extensions.
    Integrates with the existing extension registry system.
    """
    
    def __init__(self, field_registry: FieldRegistryCore):
        self.registry = field_registry
        self._extension_field_map: Dict[str, List[str]] = {}
    
    def register_extension(
        self,
        extension_id: str,
        extension_name: str,
        supported_fields: List[str]
    ) -> None:
        """
        Register an extension and its supported fields.
        
        Args:
            extension_id: Unique identifier for extension
            extension_name: Human-readable name
            supported_fields: List of field names this extension supports
        """
        self._extension_field_map[extension_id] = supported_fields
        
        # Update field definitions with extension compatibility
        for field_name in supported_fields:
            field = self.registry.get_field(field_name)
            if field and extension_id not in field.compatible_extensions:
                field.compatible_extensions.append(extension_id)
    
    def get_extension_for_field(self, field_name: str) -> List[str]:
        """Get extensions that can extract a given field"""
        extensions = []
        for ext_id, fields in self._extension_field_map.items():
            if field_name in fields:
                extensions.append(ext_id)
        return extensions
    
    def get_fields_for_extension(self, extension_id: str) -> List[str]:
        """Get all fields supported by an extension"""
        return self._extension_field_map.get(extension_id, [])
    
    def get_extension_coverage_report(self) -> Dict[str, Any]:
        """Generate a report on extension field coverage"""
        report = {
            "extensions": {},
            "gaps": []
        }
        
        all_fields = set(self.registry.get_all_fields().keys())
        covered_fields = set()
        
        for ext_id, fields in self._extension_field_map.items():
            field_count = len(fields)
            report["extensions"][ext_id] = {
                "field_count": field_count,
                "fields": fields
            }
            covered_fields.update(fields)
        report["total_covered"] = len(covered_fields)
        report["total_fields"] = len(all_fields)
        report["coverage_percent"] = round(
            len(covered_fields) / len(all_fields) * 100, 2
        ) if all_fields else 0
        
        # Identify gaps
        uncovered = all_fields - covered_fields
        for field_name in uncovered:
            field = self.registry.get_field(field_name)
            if field and not field.is_deprecated:
                report["gaps"].append({
                    "field": field_name,
                    "source": field.source.value,
                    "type": field.field_type.value
                })
        
        return report
```

---

## TypeScript Code Generation

### TypeScript Generator

```python
class TypeScriptGenerator:
    """
    Generates TypeScript interfaces and types from field definitions.
    Ensures TypeScript/Python consistency.
    """
    
    def __init__(self, field_registry: FieldRegistryCore):
        self.registry = field_registry
    
    def generate_interfaces(self) -> str:
        """Generate all TypeScript interfaces"""
        lines = [
            "// Auto-generated from Unified Field Registry",
            "// DO NOT EDIT MANUALLY",
            "",
            "export type MetadataValue = string | number | boolean | null;",
            ""
        ]
        
        # Generate enum types for field types
        lines.extend(self._generate_field_type_enum())
        
        # Generate field definition interface
        lines.extend(self._generate_field_definition_interface())
        
        # Generate interfaces for each collection
        for collection in self.registry.get_all_collections().values():
            lines.extend(self._generate_collection_interface(collection))
        
        return "\n".join(lines)
    
    def _generate_field_type_enum(self) -> List[str]:
        """Generate TypeScript enum for field types"""
        return [
            "export enum FieldType {",
            '  STRING = "string",',
            '  INTEGER = "integer",',
            '  FLOAT = "float",',
            '  BOOLEAN = "boolean",',
            '  DATETIME = "datetime",',
            '  BINARY = "binary",',
            '  ARRAY = "array",',
            '  OBJECT = "object",',
            '  GPS = "gps",',
            '  RATIONAL = "rational",',
            "}",
            ""
        ]
    
    def _generate_field_definition_interface(self) -> List[str]:
        """Generate TypeScript interface for field definition"""
        return [
            "export interface FieldDefinition {",
            "  name: string;",
            "  fieldId: string;",
            "  standardName: string;",
            "  fieldType: FieldType;",
            "  source: string;",
            "  tier: 'free' | 'professional' | 'forensic' | 'enterprise';",
            "  display: 'simple' | 'advanced' | 'raw';",
            "  description: string;",
            "  exampleValue?: MetadataValue;",
            "  isRequired: boolean;",
            "  isDeprecated: boolean;",
            "  searchKeywords: string[];",
            "  categoryTags: string[];",
            "  relatedFields: string[];",
            "  compatibleExtensions: string[];",
            "}",
            ""
        ]
    
    def _generate_collection_interface(
        self,
        collection: FieldCollection
    ) -> List[str]:
        """Generate TypeScript interface for a field collection"""
        interface_name = "".join(
            word.capitalize() for word in collection.name.split("_")
        )
        
        fields = []
        for field_name, field in collection.fields.items():
            ts_type = self._python_type_to_ts(field.field_type)
            optional = "?" if not field.is_required else ""
            fields.append(f"  {field_name}{optional}: {ts_type};")
        
        return [
            f"export interface {interface_name} {{",
            *fields,
            "}",
            ""
        ]
    
    def _python_type_to_ts(self, field_type: FieldType) -> str:
        """Convert Python field type to TypeScript type"""
        type_mapping = {
            FieldType.STRING: "string",
            FieldType.INTEGER: "number",
            FieldType.FLOAT: "number",
            FieldType.BOOLEAN: "boolean",
            FieldType.DATETIME: "string",
            FieldType.BINARY: "string",
            FieldType.ARRAY: "unknown[]",
            FieldType.OBJECT: "Record<string, unknown>",
            FieldType.GPS: "{ latitude: number; longitude: number }",
            FieldType.RATIONAL: "number",
            FieldType.UUID: "string",
            FieldType.ENUM: "string",
            FieldType.COLOR: "string",
            FieldType.HASH: "string",
        }
        return type_mapping.get(field_type, "unknown")
    
    def generate_field_registry_ts(self, output_path: str) -> None:
        """Generate complete TypeScript field registry file"""
        content = self.generate_interfaces()
        
        with open(output_path, "w") as f:
            f.write(content)
        
        logger.info(f"Generated TypeScript registry at {output_path}")
```

---

## Migration Strategy

### Phase 1: Analysis and Planning (Week 1)

- Complete audit of all field definition locations
- Document field format variations
- Create detailed migration plan
- Set up migration test environment

### Phase 2: Core Registry Implementation (Week 2-3)

- Implement `FieldDefinition` dataclass
- Implement `FieldRegistryCore` class
- Implement `FieldBuilder` for fluent creation
- Set up storage and persistence
- Implement validation framework
- Build indexing system

### Phase 3: Data Migration (Week 4)

- Create migration scripts for each source
- Migrate existing field definitions
- Verify migration completeness
- Run validation checks
- Fix any migration issues

### Phase 4: Extension Integration (Week 5)

- Update DICOM extension registry
- Update Image extension registry
- Modify extraction modules to use registry
- Update field counting system
- Test integration points

### Phase 5: TypeScript Generation (Week 6)

- Implement `TypeScriptGenerator`
- Generate initial TypeScript interfaces
- Update `shared/schema.ts`
- Set up regeneration in CI/CD
- Test TypeScript/Python consistency

### Phase 6: Testing and Validation (Week 7)

- Comprehensive unit testing
- Integration testing
- Performance testing
- Migration validation
- Documentation updates

### Phase 7: Deployment (Week 8)

- Deploy to staging environment
- Monitor field extraction accuracy
- Gather performance metrics
- Address any issues
- Deploy to production

---

## Gap Analysis and Field Coverage

### Current Coverage Status

Based on the audit findings, here is the gap analysis:

| Source | Inventory Fields | Registry Fields | Gap | Priority |
|--------|-----------------|-----------------|-----|----------|
| EXIF Standard | 1,200 | 784 | 416 | High |
| MakerNotes | 7,000 | 4,760 | 2,240 | High |
| IPTC | 150 | 117 | 33 | Medium |
| XMP | 500 | 4,250 | 0 (over) | Low |
| Color Management | 200 | 197 | 3 | Low |
| QuickTime | 1,438 | 0 | 1,438 | High |
| Matroska | 274 | 0 | 274 | High |
| DICOM | 5,179 | 2,285 | 2,894 | High |
| ID3 | 109 | 0 | 109 | Medium |
| FLAC/Vorbis/APE | 81 | 0 | 81 | Medium |
| **Total** | **16,131** | **~12,393** | **~5,488** | |

### Priority Matrix

**Phase 1 (High Priority - Immediate)**
- EXIF Standard fields (416 missing)
- MakerNotes for all vendors (2,240 missing)
- QuickTime/Matroska container fields (1,712 missing)
- DICOM standard tags (2,894 missing)

**Phase 2 (Medium Priority - 1 month)**
- ID3 frame fields (109 missing)
- Audio format fields (81 missing)
- IPTC extensions (33 missing)
- Color management enhancements (3 missing)

**Phase 3 (Lower Priority - Ongoing)**
- Proprietary/vendor-specific fields
- Emerging format support
- Specialized domain extensions

---

## Implementation Checklist

### Files to Create

| File | Purpose |
|------|---------|
| `server/extractor/modules/unified_field_registry.py` | Core registry implementation |
| `server/extractor/modules/field_definitions.py` | Dataclass definitions |
| `server/extractor/modules/field_builder.py` | Builder for field creation |
| `server/extractor/modules/extension_mapper.py` | Extension integration |
| `server/extractor/modules/typescript_generator.py` | TypeScript code generation |
| `scripts/migrate_fields.py` | Field migration script |
| `scripts/validate_registry.py` | Registry validation script |
| `tests/test_unified_field_registry.py` | Unit tests |

---

## Conclusion

The unified field registry system provides a single source of truth for all metadata field definitions, addressing the fragmentation issues identified in the audit. Key benefits include:

1. **Centralized Management**: All field definitions in one location
2. **Type Safety**: Runtime validation of field values
3. **Consistency**: Automatic TypeScript/Python synchronization
4. **Maintainability**: Clear patterns for adding new fields
5. **Extensibility**: Easy integration with new extensions
6. **Gap Tracking**: Built-in tools for identifying missing fields

The implementation follows a phased approach, minimizing disruption while ensuring comprehensive coverage of all existing and future field definitions.

---

**Document Version**: 1.0  
**Created**: January 9, 2026  
**Status**: Design Complete - Ready for Implementation

"""
Field Definition Dataclasses for Unified Field Registry

This module provides the core dataclasses and enums for defining
metadata fields in the unified field registry system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
import re


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
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"


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
    AAC = "AAC"
    ASF = "ASF"
    MXF = "MXF"
    M2TS = "M2TS"
    FITS = "FITS"
    TIFF = "TIFF"
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    HEIC = "HEIC"
    AVIF = "AVIF"
    CUSTOM = "custom"
    COMPUTED = "computed"


class ValidationSeverity(Enum):
    """Severity of validation rules"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationRuleType(Enum):
    """Types of validation rules"""
    REGEX = "regex"
    RANGE = "range"
    LENGTH = "length"
    PATTERN = "pattern"
    CHOICE = "choice"
    CUSTOM = "custom"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"


@dataclass
class FieldValidationRule:
    """Validation rule for field values"""
    rule_type: Union[str, ValidationRuleType]
    value: Any
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    def __post_init__(self):
        if isinstance(self.rule_type, str):
            try:
                self.rule_type = ValidationRuleType(self.rule_type)
            except ValueError:
                pass
        if isinstance(self.severity, str):
            self.severity = ValidationSeverity(self.severity)
    
    def validate(self, value: Any) -> tuple:
        """
        Validate a value against this rule.
        
        Returns:
            tuple: (is_valid, message)
        """
        if value is None:
            return True, ""
        
        try:
            if self.rule_type == ValidationRuleType.REGEX:
                if not re.match(str(self.value), str(value)):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.RANGE:
                min_val, max_val = self.value
                if not (min_val <= float(value) <= max_val):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.LENGTH:
                min_len, max_len = self.value
                str_val = str(value)
                if not (min_len <= len(str_val) <= max_len):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.CHOICE:
                if value not in self.value:
                    return False, self.message
            elif self.rule_type == ValidationRuleType.EMAIL:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, str(value)):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.URL:
                url_pattern = r'^https?://[\w\-\.]+(:\d+)?(/[^\s]*)?$'
                if not re.match(url_pattern, str(value)):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.IP_ADDRESS:
                ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                if not re.match(ip_pattern, str(value)):
                    return False, self.message
                parts = str(value).split('.')
                if any(not (0 <= int(p) <= 255) for p in parts):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.UUID:
                uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                if not re.match(uuid_pattern, str(value).lower()):
                    return False, self.message
            elif self.rule_type == ValidationRuleType.CUSTOM:
                if callable(self.value):
                    if not self.value(value):
                        return False, self.message
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        
        return True, ""


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
    search_keywords: List[str] = field(default_factory=list)
    category_tags: List[str] = field(default_factory=list)
    usage_examples: List[str] = field(default_factory=list)
    related_fields: List[str] = field(default_factory=list)
    see_also_references: List[str] = field(default_factory=list)
    parent_field: Optional[str] = None
    child_fields: List[str] = field(default_factory=list)
    alias_names: List[str] = field(default_factory=list)
    extraction_cost: str = "low"
    is_computed: bool = False
    computation_dependencies: List[str] = field(default_factory=list)
    since_version: Optional[str] = None
    last_modified_version: Optional[str] = None


@dataclass
class FieldDefinition:
    """
    Complete definition of a metadata field.
    
    This is the core dataclass representing a single field in the registry.
    All field definitions must conform to this structure.
    """
    name: str
    field_type: FieldType
    source: FieldSource
    description: str
    field_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    standard_name: str = ""
    tier: FieldTier = FieldTier.FREE
    display: DisplayLevel = DisplayLevel.ADVANCED
    long_description: Optional[str] = None
    significance: Optional[str] = None
    example_value: Optional[Any] = None
    default_value: Optional[Any] = None
    validation_rules: List[FieldValidationRule] = field(default_factory=list)
    is_required: bool = False
    is_deprecated: bool = False
    deprecation: Optional[FieldDeprecation] = None
    metadata: FieldMetadata = field(default_factory=FieldMetadata)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    compatible_extensions: List[str] = field(default_factory=list)
    extraction_order: int = 0
    
    def __post_init__(self):
        if not self.standard_name:
            self.standard_name = self.name
        if isinstance(self.field_type, str):
            self.field_type = FieldType(self.field_type)
        if isinstance(self.source, str):
            self.source = FieldSource(self.source)
        if isinstance(self.tier, str):
            self.tier = FieldTier(self.tier)
        if isinstance(self.display, str):
            self.display = DisplayLevel(self.display)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "name": self.name,
            "field_id": self.field_id,
            "standard_name": self.standard_name,
            "field_type": self.field_type.value if isinstance(self.field_type, FieldType) else self.field_type,
            "source": self.source.value if isinstance(self.source, FieldSource) else self.source,
            "tier": self.tier.value if isinstance(self.tier, FieldTier) else self.tier,
            "display": self.display.value if isinstance(self.display, DisplayLevel) else self.display,
            "description": self.description,
            "long_description": self.long_description,
            "significance": self.significance,
            "example_value": self.example_value,
            "default_value": self.default_value,
            "validation_rules": [
                {
                    "rule_type": r.rule_type.value if isinstance(r.rule_type, ValidationRuleType) else r.rule_type,
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
                "computation_dependencies": self.metadata.computation_dependencies,
                "since_version": self.metadata.since_version,
                "last_modified_version": self.metadata.last_modified_version
            },
            "version": self.version,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "created_by": self.created_by,
            "compatible_extensions": self.compatible_extensions,
            "extraction_order": self.extraction_order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldDefinition':
        """Create from dictionary"""
        validation_rules = []
        for r in data.get("validation_rules", []):
            rule_type = r.get("rule_type", "regex")
            if isinstance(rule_type, str):
                try:
                    rule_type = ValidationRuleType(rule_type)
                except ValueError:
                    pass
            validation_rules.append(FieldValidationRule(
                rule_type=rule_type,
                value=r["value"],
                message=r["message"],
                severity=ValidationSeverity(r.get("severity", "error"))
            ))
        
        deprecation = None
        if data.get("deprecation"):
            deprecation = FieldDeprecation(
                deprecated_version=data["deprecation"]["deprecated_version"],
                removal_version=data["deprecation"]["removal_version"],
                reason=data["deprecation"]["reason"],
                migration_path=data["deprecation"].get("migration_path"),
                alternative_field=data["deprecation"].get("alternative_field")
            )
        
        metadata = FieldMetadata(
            search_keywords=data.get("metadata", {}).get("search_keywords", []),
            category_tags=data.get("metadata", {}).get("category_tags", []),
            usage_examples=data.get("metadata", {}).get("usage_examples", []),
            related_fields=data.get("metadata", {}).get("related_fields", []),
            see_also_references=data.get("metadata", {}).get("see_also_references", []),
            parent_field=data.get("metadata", {}).get("parent_field"),
            child_fields=data.get("metadata", {}).get("child_fields", []),
            alias_names=data.get("metadata", {}).get("alias_names", []),
            extraction_cost=data.get("metadata", {}).get("extraction_cost", "low"),
            is_computed=data.get("metadata", {}).get("is_computed", False),
            computation_dependencies=data.get("metadata", {}).get("computation_dependencies", []),
            since_version=data.get("metadata", {}).get("since_version"),
            last_modified_version=data.get("metadata", {}).get("last_modified_version")
        )
        
        field_type = data.get("field_type", "string")
        if isinstance(field_type, str):
            try:
                field_type = FieldType(field_type)
            except ValueError:
                field_type = FieldType.STRING
        
        source = data.get("source", "EXIF")
        if isinstance(source, str):
            try:
                source = FieldSource(source)
            except ValueError:
                source = FieldSource.EXIF
        
        tier = data.get("tier", "free")
        if isinstance(tier, str):
            try:
                tier = FieldTier(tier)
            except ValueError:
                tier = FieldTier.FREE
        
        display = data.get("display", "advanced")
        if isinstance(display, str):
            try:
                display = DisplayLevel(display)
            except ValueError:
                display = DisplayLevel.ADVANCED
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except ValueError:
                created_at = datetime.utcnow()
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except ValueError:
                updated_at = datetime.utcnow()
        
        return cls(
            name=data["name"],
            field_id=data.get("field_id", str(uuid.uuid4())),
            standard_name=data.get("standard_name", data["name"]),
            field_type=field_type,
            source=source,
            tier=tier,
            display=display,
            description=data["description"],
            long_description=data.get("long_description"),
            significance=data.get("significance"),
            example_value=data.get("example_value"),
            default_value=data.get("default_value"),
            validation_rules=validation_rules,
            is_required=data.get("is_required", False),
            is_deprecated=data.get("is_deprecated", False),
            deprecation=deprecation,
            metadata=metadata,
            version=data.get("version", "1.0.0"),
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            created_by=data.get("created_by", "system"),
            compatible_extensions=data.get("compatible_extensions", []),
            extraction_order=data.get("extraction_order", 0)
        )
    
    def validate_value(self, value: Any) -> tuple:
        """
        Validate a value against this field's definition.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if value is None:
            if self.is_required:
                return False, f"Field '{self.name}' is required but value is None"
            return True, ""
        
        for rule in self.validation_rules:
            is_valid, message = rule.validate(value)
            if not is_valid:
                return False, message
        
        return True, ""
    
    def to_typescript_type(self) -> str:
        """Get TypeScript type for this field"""
        type_mapping = {
            FieldType.STRING: "string",
            FieldType.INTEGER: "number",
            FieldType.FLOAT: "number",
            FieldType.BOOLEAN: "boolean",
            FieldType.DATETIME: "string",
            FieldType.BINARY: "string",
            FieldType.ARRAY: "unknown[]",
            FieldType.OBJECT: "Record<string, unknown>",
            FieldType.GPS: "{ latitude: number; longitude: number; altitude?: number }",
            FieldType.RATIONAL: "number",
            FieldType.UUID: "string",
            FieldType.ENUM: "string",
            FieldType.COLOR: "string",
            FieldType.HASH: "string",
            FieldType.EMAIL: "string",
            FieldType.URL: "string",
            FieldType.IP_ADDRESS: "string",
        }
        return type_mapping.get(self.field_type, "unknown")
    
    def to_python_type(self) -> str:
        """Get Python type hint for this field"""
        type_mapping = {
            FieldType.STRING: "str",
            FieldType.INTEGER: "int",
            FieldType.FLOAT: "float",
            FieldType.BOOLEAN: "bool",
            FieldType.DATETIME: "datetime",
            FieldType.BINARY: "bytes",
            FieldType.ARRAY: "List[Any]",
            FieldType.OBJECT: "Dict[str, Any]",
            FieldType.GPS: "Dict[str, float]",
            FieldType.RATIONAL: "float",
            FieldType.UUID: "str",
            FieldType.ENUM: "str",
            FieldType.COLOR: "str",
            FieldType.HASH: "str",
            FieldType.EMAIL: "str",
            FieldType.URL: "str",
            FieldType.IP_ADDRESS: "str",
        }
        return type_mapping.get(self.field_type, "Any")


@dataclass
class FieldCollection:
    """A collection of related field definitions"""
    collection_id: str
    name: str
    description: str
    source: str
    fields: Dict[str, FieldDefinition] = field(default_factory=dict)
    total_fields: int = 0
    free_fields: int = 0
    professional_fields: int = 0
    forensic_fields: int = 0
    enterprise_fields: int = 0
    version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_field(self, field: FieldDefinition) -> None:
        """Add a field to the collection"""
        self.fields[field.name] = field
        self._recalculate_stats()
        self.last_updated = datetime.utcnow()
    
    def remove_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Remove a field from the collection"""
        field = self.fields.pop(field_name, None)
        if field:
            self._recalculate_stats()
        return field
    
    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Get a field by name"""
        return self.fields.get(field_name)
    
    def _recalculate_stats(self) -> None:
        """Recalculate field statistics"""
        self.total_fields = len(self.fields)
        self.free_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.FREE)
        self.professional_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.PROFESSIONAL)
        self.forensic_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.FORENSIC)
        self.enterprise_fields = sum(1 for f in self.fields.values() if f.tier == FieldTier.ENTERPRISE)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "total_fields": self.total_fields,
            "free_fields": self.free_fields,
            "professional_fields": self.professional_fields,
            "forensic_fields": self.forensic_fields,
            "enterprise_fields": self.enterprise_fields,
            "version": self.version,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldCollection':
        """Create from dictionary"""
        collection = cls(
            collection_id=data["collection_id"],
            name=data["name"],
            description=data["description"],
            source=data["source"],
            version=data.get("version", "1.0.0"),
            last_updated=datetime.fromisoformat(data["last_updated"]) if isinstance(data.get("last_updated"), str) else datetime.utcnow()
        )
        for field_data in data.get("fields", {}).values():
            collection.add_field(FieldDefinition.from_dict(field_data))
        return collection


@dataclass
class ValidationResult:
    """Result of field validation"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge another validation result"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.is_valid = self.is_valid and other.is_valid
        return self


# Export all classes and enums
__all__ = [
    "FieldType",
    "FieldTier", 
    "DisplayLevel",
    "FieldSource",
    "ValidationSeverity",
    "ValidationRuleType",
    "FieldValidationRule",
    "FieldDeprecation",
    "FieldMetadata",
    "FieldDefinition",
    "FieldCollection",
    "ValidationResult",
]

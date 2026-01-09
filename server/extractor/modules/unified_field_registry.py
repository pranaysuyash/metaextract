"""
Unified Field Registry Core

This module provides the core registry class for managing all field definitions
in the MetaExtract project. It serves as the single source of truth for all
metadata field definitions.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Set, Type, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from field_definitions import (
    FieldDefinition,
    FieldCollection,
    FieldType,
    FieldTier,
    DisplayLevel,
    FieldSource,
    ValidationSeverity,
    ValidationResult,
    FieldValidationRule,
)

logger = logging.getLogger(__name__)


class FieldRegistryError(Exception):
    """Base exception for field registry errors"""
    pass


class FieldAlreadyExistsError(FieldRegistryError):
    """Raised when attempting to register a field that already exists"""
    pass


class FieldNotFoundError(FieldRegistryError):
    """Raised when a field is not found in the registry"""
    pass


class FieldValidationError(FieldRegistryError):
    """Raised when field validation fails"""
    pass


class CollectionAlreadyExistsError(FieldRegistryError):
    """Raised when attempting to create a collection that already exists"""
    pass


@dataclass
class RegistryStats:
    """Statistics about the registry"""
    total_fields: int = 0
    total_collections: int = 0
    by_source: Dict[str, int] = None
    by_tier: Dict[str, int] = None
    by_type: Dict[str, int] = None
    by_display: Dict[str, int] = None
    deprecated_count: int = 0
    required_count: int = 0
    
    def __post_init__(self):
        if self.by_source is None:
            self.by_source = {}
        if self.by_tier is None:
            self.by_tier = {}
        if self.by_type is None:
            self.by_type = {}
        if self.by_display is None:
            self.by_display = {}


class FieldRegistryCore:
    """
    Core registry class managing all field definitions.
    
    This is the main entry point for the unified field registry system.
    It provides comprehensive field management including registration,
    querying, validation, and statistics.
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
        self._event_callbacks: Dict[str, List[callable]] = {}
        
        self._init_indexes()
        logger.info("FieldRegistryCore initialized")
    
    # =========================================================================
    # Field Management
    # =========================================================================
    
    def register_field(
        self,
        field: FieldDefinition,
        collection: Optional[str] = None,
        validate: bool = True,
        overwrite: bool = False
    ) -> bool:
        """
        Register a new field definition.
        
        Args:
            field: FieldDefinition to register
            collection: Optional collection name to add to
            validate: Whether to validate the field before registration
            overwrite: Whether to overwrite existing field
            
        Returns:
            True if registration successful
            
        Raises:
            FieldValidationError: If validation fails
            FieldAlreadyExistsError: If field exists and overwrite=False
        """
        if validate:
            self._validate_field(field)
        
        if field.name in self._fields and not overwrite:
            raise FieldAlreadyExistsError(
                f"Field '{field.name}' already exists in registry. "
                f"Use overwrite=True to replace."
            )
        
        old_field = self._fields.get(field.name)
        
        if not field.standard_name:
            field.standard_name = field.name
        
        field.updated_at = datetime.utcnow()
        
        self._fields[field.name] = field
        
        if collection:
            self._add_to_collection(field, collection)
        
        self._update_indexes(field)
        
        if self._storage_path:
            self._persist_field(field)
        
        self._emit_event("field_registered", {
            "field_name": field.name,
            "overwrite": overwrite,
            "old_version": old_field.version if old_field else None,
            "new_version": field.version
        })
        
        logger.debug(f"Registered field: {field.name} from {field.source.value}")
        return True
    
    def register_field_batch(
        self,
        fields: List[FieldDefinition],
        collection: Optional[str] = None,
        fail_on_error: bool = False,
        overwrite: bool = False
    ) -> Dict[str, bool]:
        """
        Register multiple fields at once.
        
        Args:
            fields: List of FieldDefinition objects
            collection: Optional collection name for all fields
            fail_on_error: Whether to stop on first error
            overwrite: Whether to overwrite existing fields
            
        Returns:
            Dictionary mapping field names to success status
        """
        results = {}
        for field in fields:
            try:
                success = self.register_field(
                    field, collection, validate=True, overwrite=overwrite
                )
                results[field.name] = success
            except Exception as e:
                results[field.name] = False
                if fail_on_error:
                    raise
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
        
        self._remove_from_indexes(field)
        
        for collection in self._collections.values():
            collection.remove_field(field_name)
        
        if self._storage_path:
            self._remove_persisted_field(field_name)
        
        self._emit_event("field_unregistered", {
            "field_name": field_name,
            "source": field.source.value
        })
        
        logger.debug(f"Unregistered field: {field_name}")
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
    
    def get_field_by_standard_name(
        self,
        standard_name: str,
        source: Optional[FieldSource] = None
    ) -> Optional[FieldDefinition]:
        """Get a field by standard name, optionally filtering by source"""
        for field in self._fields.values():
            if field.standard_name == standard_name:
                if source is None or field.source == source:
                    return field
        return None
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_all_fields(self) -> Dict[str, FieldDefinition]:
        """Get all registered fields"""
        return self._fields.copy()
    
    def get_all_field_names(self) -> List[str]:
        """Get list of all field names"""
        return list(self._fields.keys())
    
    def get_fields_by_source(
        self,
        source: Union[FieldSource, str]
    ) -> Dict[str, FieldDefinition]:
        """Get all fields from a specific source"""
        if isinstance(source, str):
            source = FieldSource(source)
        return {
            name: field for name, field in self._fields.items()
            if field.source == source
        }
    
    def get_fields_by_type(
        self,
        field_type: Union[FieldType, str]
    ) -> Dict[str, FieldDefinition]:
        """Get all fields of a specific type"""
        if isinstance(field_type, str):
            field_type = FieldType(field_type)
        return {
            name: field for name, field in self._fields.items()
            if field.field_type == field_type
        }
    
    def get_fields_by_tier(
        self,
        tier: Union[FieldTier, str]
    ) -> Dict[str, FieldDefinition]:
        """Get all fields accessible at a specific tier"""
        if isinstance(tier, str):
            tier = FieldTier(tier)
        
        tier_order = [
            FieldTier.FREE,
            FieldTier.PROFESSIONAL,
            FieldTier.FORENSIC,
            FieldTier.ENTERPRISE
        ]
        max_tier_index = tier_order.index(tier)
        
        return {
            name: field for name, field in self._fields.items()
            if tier_order.index(field.tier) <= max_tier_index
        }
    
    def get_fields_for_display(
        self,
        display: Union[DisplayLevel, str]
    ) -> Dict[str, FieldDefinition]:
        """Get all fields visible at a specific display level"""
        if isinstance(display, str):
            display = DisplayLevel(display)
        
        display_order = [
            DisplayLevel.SIMPLE,
            DisplayLevel.ADVANCED,
            DisplayLevel.RAW
        ]
        max_display_index = display_order.index(display)
        
        return {
            name: field for name, field in self._fields.items()
            if display_order.index(field.display) <= max_display_index
        }
    
    def get_compatible_fields(
        self,
        extension_id: str
    ) -> Dict[str, FieldDefinition]:
        """Get all fields compatible with an extension"""
        return {
            name: field for name, field in self._fields.items()
            if extension_id in field.compatible_extensions
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
            match = False
            
            if query in field.name.lower():
                match = True
            elif query in field.description.lower():
                match = True
            elif query in field.standard_name.lower():
                match = True
            
            if not match and search_metadata:
                if query in field.metadata.search_keywords:
                    match = True
                elif query in field.metadata.category_tags:
                    match = True
                elif query in field.metadata.alias_names:
                    match = True
            
            if match:
                results.append(field)
        
        return results[:max_results]
    
    def find_related_fields(self, field_name: str) -> List[FieldDefinition]:
        """Find fields related to a given field"""
        field = self.get_field(field_name)
        if not field:
            return []
        
        related = []
        
        for related_name in field.metadata.related_fields:
            related_field = self.get_field(related_name)
            if related_field:
                related.append(related_field)
        
        if field.metadata.parent_field:
            parent = self.get_field(field.metadata.parent_field)
            if parent:
                related.append(parent)
        
        for child_name in field.metadata.child_fields:
            child = self.get_field(child_name)
            if child:
                related.append(child)
        
        return related
    
    def find_similar_fields(
        self,
        field_name: str,
        max_similar: int = 5
    ) -> List[tuple]:
        """
        Find similar fields using name similarity.
        
        Returns:
            List of (field, similarity_score) tuples
        """
        field = self.get_field(field_name)
        if not field:
            return []
        
        from difflib import SequenceMatcher
        
        target_name = field.name.lower()
        similarities = []
        
        for name, other_field in self._fields.items():
            if name == field_name:
                continue
            
            ratio = SequenceMatcher(
                None, target_name, name.lower()
            ).ratio()
            similarities.append((other_field, ratio))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_similar]
    
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
            raise CollectionAlreadyExistsError(
                f"Collection '{collection_id}' already exists"
            )
        
        collection = FieldCollection(
            collection_id=collection_id,
            name=name,
            description=description,
            source=source
        )
        self._collections[collection_id] = collection
        
        self._emit_event("collection_created", {
            "collection_id": collection_id,
            "name": name
        })
        
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[FieldCollection]:
        """Get a field collection by ID"""
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> Dict[str, FieldCollection]:
        """Get all field collections"""
        return self._collections.copy()
    
    def add_field_to_collection(
        self,
        field_name: str,
        collection_id: str
    ) -> bool:
        """Add a field to a collection"""
        field = self.get_field(field_name)
        if not field:
            raise FieldNotFoundError(f"Field '{field_name}' not found")
        
        collection = self.get_collection(collection_id)
        if not collection:
            raise FieldRegistryError(f"Collection '{collection_id}' not found")
        
        collection.add_field(field)
        return True
    
    def remove_field_from_collection(
        self,
        field_name: str,
        collection_id: str
    ) -> bool:
        """Remove a field from a collection"""
        collection = self.get_collection(collection_id)
        if not collection:
            raise FieldRegistryError(f"Collection '{collection_id}' not found")
        
        return collection.remove_field(field_name) is not None
    
    def _add_to_collection(
        self,
        field: FieldDefinition,
        collection_id: str
    ) -> None:
        """Internal method to add a field to a collection"""
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
        """Validate a value against field definition"""
        field = self.get_field(field_name)
        if not field:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown field: {field_name}"]
            )
        
        return field.validate_value(value)
    
    def validate_all_fields(self) -> Dict[str, ValidationResult]:
        """Validate all field definitions"""
        results = {}
        for field_name, field in self._fields.items():
            validation = ValidationResult()
            
            if not field.name:
                validation.add_error("Field name is required")
            
            if not field.description:
                validation.add_error("Field description is required")
            
            if field.example_value is not None:
                result = field.validate_value(field.example_value)
                if not result.is_valid:
                    validation.add_error(f"Invalid example value: {result}")
            
            results[field_name] = validation
        
        return results
    
    def _validate_field(self, field: FieldDefinition) -> None:
        """Validate a field definition before registration"""
        if not field.name or not field.name.strip():
            raise FieldValidationError("Field name is required and cannot be empty")
        
        if not field.description or not field.description.strip():
            raise FieldValidationError(
                f"Field '{field.name}': description is required"
            )
        
        if field.example_value is not None:
            result = field.validate_value(field.example_value)
            if not result.is_valid:
                raise FieldValidationError(
                    f"Field '{field.name}': invalid example value - {result}"
                )
    
    def _apply_validation_rule(
        self,
        value: Any,
        rule: FieldValidationRule
    ) -> ValidationResult:
        """Apply a single validation rule"""
        is_valid, message = rule.validate(value)
        if not is_valid:
            return ValidationResult(is_valid=False, errors=[message])
        return ValidationResult()
    
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
            "by_extension": {},
            "by_standard_name": {}
        }
    
    def _update_indexes(self, field: FieldDefinition) -> None:
        """Update all indexes with a field"""
        source_key = field.source.value if hasattr(field.source, 'value') else str(field.source)
        type_key = field.field_type.value if hasattr(field.field_type, 'value') else str(field.field_type)
        tier_key = field.tier.value if hasattr(field.tier, 'value') else str(field.tier)
        display_key = field.display.value if hasattr(field.display, 'value') else str(field.display)
        
        if source_key not in self._indexes["by_source"]:
            self._indexes["by_source"][source_key] = {}
        self._indexes["by_source"][source_key][field.name] = field
        
        if type_key not in self._indexes["by_type"]:
            self._indexes["by_type"][type_key] = {}
        self._indexes["by_type"][type_key][field.name] = field
        
        if tier_key not in self._indexes["by_tier"]:
            self._indexes["by_tier"][tier_key] = {}
        self._indexes["by_tier"][tier_key][field.name] = field
        
        if display_key not in self._indexes["by_display"]:
            self._indexes["by_display"][display_key] = {}
        self._indexes["by_display"][display_key][field.name] = field
        
        standard_key = field.standard_name
        if standard_key not in self._indexes["by_standard_name"]:
            self._indexes["by_standard_name"][standard_key] = {}
        self._indexes["by_standard_name"][standard_key][field.name] = field
        
        for ext in field.compatible_extensions:
            if ext not in self._indexes["by_extension"]:
                self._indexes["by_extension"][ext] = {}
            self._indexes["by_extension"][ext][field.name] = field
    
    def _remove_from_indexes(self, field: FieldDefinition) -> None:
        """Remove a field from all indexes"""
        for index_name in self._indexes:
            index = self._indexes[index_name]
            keys_to_remove = []
            for key in index:
                if field.name in index[key]:
                    del index[key][field.name]
                    if not index[key]:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del index[key]
    
    def rebuild_indexes(self) -> None:
        """Rebuild all indexes from scratch"""
        self._init_indexes()
        for field in self._fields.values():
            self._update_indexes(field)
        logger.info("Indexes rebuilt successfully")
    
    # =========================================================================
    # Persistence
    # =========================================================================
    
    def save_to_disk(self, path: Optional[str] = None) -> str:
        """
        Save registry to disk.
        
        Returns:
            Path to saved file
        """
        save_path = path or self._storage_path
        if not save_path:
            raise FieldRegistryError("No storage path configured")
        
        data = {
            "version": "1.0.0",
            "saved_at": datetime.utcnow().isoformat(),
            "fields": {k: v.to_dict() for k, v in self._fields.items()},
            "collections": {k: v.to_dict() for k, v in self._collections.items()}
        }
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Registry saved to {save_path}")
        return save_path
    
    def load_from_disk(self, path: Optional[str] = None) -> int:
        """
        Load registry from disk.
        
        Returns:
            Number of fields loaded
        """
        load_path = path or self._storage_path
        if not load_path or not os.path.exists(load_path):
            logger.warning(f"No registry file found at {load_path}")
            return 0
        
        with open(load_path, "r") as f:
            data = json.load(f)
        
        fields_data = data.get("fields", {})
        for field_data in fields_data.values():
            field = FieldDefinition.from_dict(field_data)
            self.register_field(field, validate=False)
        
        collections_data = data.get("collections", {})
        for collection_data in collections_data.values():
            collection = FieldCollection.from_dict(collection_data)
            self._collections[collection.collection_id] = collection
        
        count = len(fields_data)
        logger.info(f"Loaded {count} fields from {load_path}")
        return count
    
    def _persist_field(self, field: FieldDefinition) -> None:
        """Persist a single field (for incremental saves)"""
        if not self._storage_path:
            return
        
        field_file = os.path.join(
            os.path.dirname(self._storage_path),
            "fields",
            f"{field.name}.json"
        )
        os.makedirs(os.path.dirname(field_file), exist_ok=True)
        
        with open(field_file, "w") as f:
            json.dump(field.to_dict(), f, indent=2)
    
    def _remove_persisted_field(self, field_name: str) -> None:
        """Remove a persisted field"""
        if not self._storage_path:
            return
        
        field_file = os.path.join(
            os.path.dirname(self._storage_path),
            "fields",
            f"{field_name}.json"
        )
        
        if os.path.exists(field_file):
            os.remove(field_file)
    
    # =========================================================================
    # Statistics and Reporting
    # =========================================================================
    
    def get_stats(self) -> RegistryStats:
        """Get comprehensive registry statistics"""
        stats = RegistryStats()
        stats.total_fields = len(self._fields)
        stats.total_collections = len(self._collections)
        
        for field in self._fields.values():
            source_key = field.source.value if hasattr(field.source, 'value') else str(field.source)
            type_key = field.field_type.value if hasattr(field.field_type, 'value') else str(field.field_type)
            tier_key = field.tier.value if hasattr(field.tier, 'value') else str(field.tier)
            display_key = field.display.value if hasattr(field.display, 'value') else str(field.display)
            
            stats.by_source[source_key] = stats.by_source.get(source_key, 0) + 1
            stats.by_type[type_key] = stats.by_type.get(type_key, 0) + 1
            stats.by_tier[tier_key] = stats.by_tier.get(tier_key, 0) + 1
            stats.by_display[display_key] = stats.by_display.get(display_key, 0) + 1
            
            if field.is_deprecated:
                stats.deprecated_count += 1
            if field.is_required:
                stats.required_count += 1
        
        return stats
    
    def generate_report(self) -> str:
        """Generate a human-readable registry report"""
        stats = self.get_stats()
        
        lines = [
            "=" * 60,
            "UNIFIED FIELD REGISTRY REPORT",
            "=" * 60,
            "",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "-" * 40,
            "SUMMARY",
            "-" * 40,
            f"Total Fields:        {stats.total_fields}",
            f"Total Collections:   {stats.total_collections}",
            f"Deprecated Fields:   {stats.deprecated_count}",
            f"Required Fields:     {stats.required_count}",
            "",
            "-" * 40,
            "FIELDS BY SOURCE",
            "-" * 40,
        ]
        
        for source, count in sorted(stats.by_source.items(), key=lambda x: -x[1]):
            lines.append(f"  {source:25s} {count:5d}")
        
        lines.extend([
            "",
            "-" * 40,
            "FIELDS BY TIER",
            "-" * 40,
        ])
        
        for tier, count in sorted(stats.by_tier.items()):
            lines.append(f"  {tier:25s} {count:5d}")
        
        lines.extend([
            "",
            "-" * 40,
            "FIELDS BY DISPLAY LEVEL",
            "-" * 40,
        ])
        
        for display, count in sorted(stats.by_display.items()):
            lines.append(f"  {display:25s} {count:5d}")
        
        lines.extend([
            "",
            "-" * 40,
            "COLLECTIONS",
            "-" * 40,
        ])
        
        for collection_id, collection in self._collections.items():
            lines.append(f"  {collection_id}: {collection.name} ({collection.total_fields} fields)")
        
        lines.extend([
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def export_json(self) -> Dict[str, Any]:
        """Export registry as JSON-serializable dictionary"""
        return {
            "metadata": {
                "version": "1.0.0",
                "exported_at": datetime.utcnow().isoformat(),
                "total_fields": len(self._fields),
                "total_collections": len(self._collections)
            },
            "fields": {k: v.to_dict() for k, v in self._fields.items()},
            "collections": {k: v.to_dict() for k, v in self._collections.items()}
        }
    
    # =========================================================================
    # Event System
    # =========================================================================
    
    def on(self, event: str, callback: callable) -> None:
        """Register an event callback"""
        if event not in self._event_callbacks:
            self._event_callbacks[event] = []
        self._event_callbacks[event].append(callback)
    
    def off(self, event: str, callback: callable) -> None:
        """Unregister an event callback"""
        if event in self._event_callbacks:
            self._event_callbacks[event] = [
                cb for cb in self._event_callbacks[event]
                if cb != callback
            ]
    
    def _emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered callbacks"""
        if event in self._event_callbacks:
            for callback in self._event_callbacks[event]:
                try:
                    callback(event, data)
                except Exception as e:
                    logger.error(f"Error in event callback for {event}: {e}")
    
    # =========================================================================
    # Dunder Methods
    # =========================================================================
    
    def __len__(self) -> int:
        """Return number of fields"""
        return len(self._fields)
    
    def __contains__(self, field_name: str) -> bool:
        """Check if field exists"""
        return field_name in self._fields
    
    def __iter__(self):
        """Iterate over field names"""
        return iter(self._fields)
    
    def __repr__(self) -> str:
        return (
            f"FieldRegistryCore("
            f"fields={len(self._fields)}, "
            f"collections={len(self._collections)})"
        )


# Convenience function to create a configured registry
def create_registry(storage_path: Optional[str] = None) -> FieldRegistryCore:
    """Create a configured field registry instance"""
    return FieldRegistryCore(storage_path=storage_path)


# Export classes and functions
__all__ = [
    "FieldRegistryCore",
    "FieldRegistryError",
    "FieldAlreadyExistsError",
    "FieldNotFoundError",
    "FieldValidationError",
    "CollectionAlreadyExistsError",
    "RegistryStats",
    "create_registry",
]

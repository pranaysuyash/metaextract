#!/usr/bin/env python3
"""
Field Registry Migration Script

This script migrates field definitions from existing sources into
the unified field registry system.
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add server/extractor/modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_field_registry import FieldRegistryCore, FieldRegistryError
from field_definitions import (
    FieldDefinition,
    FieldType,
    FieldTier,
    DisplayLevel,
    FieldSource,
)
from field_builder import FieldBuilder


class FieldMigration:
    """Handles migration of field definitions from legacy sources"""
    
    def __init__(self, registry: FieldRegistryCore):
        self.registry = registry
        self.migration_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
    
    def migrate_from_file(self, source_path: str) -> Dict[str, Any]:
        """
        Migrate fields from a Python file containing field definitions.
        
        Args:
            source_path: Path to source file
            
        Returns:
            Migration result statistics
        """
        self.migration_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        if not os.path.exists(source_path):
            self.migration_stats["errors"].append(f"File not found: {source_path}")
            return self.migration_stats
        
        with open(source_path) as f:
            content = f.read()
        
        # Detect source format and migrate
        if "_FIELDS" in content or "_TAGS" in content:
            self._migrate_from_dict_format(content, source_path)
        elif "get_" in content and "_field_count" in content:
            self._migrate_from_function_format(content, source_path)
        else:
            self.migration_stats["errors"].append(
                f"Unknown format in {source_path}"
            )
        
        return self.migration_stats
    
    def _migrate_from_dict_format(
        self,
        content: str,
        source_path: str
    ) -> None:
        """Migrate fields from dictionary format"""
        # Extract field name pattern
        field_pattern = r'(\w+)\s*:\s*FieldDefinition\('
        matches = re.findall(field_pattern, content)
        
        source = self._detect_source(source_path)
        
        for field_name in matches:
            self.migration_stats["total_processed"] += 1
            
            try:
                # Extract field details using regex
                field_def = self._extract_field_from_dict(content, field_name)
                
                if field_def:
                    field = self._create_field_definition(field_name, field_def, source)
                    self.registry.register_field(field, validate=False)
                    self.migration_stats["successful"] += 1
                else:
                    self.migration_stats["skipped"] += 1
                    
            except Exception as e:
                self.migration_stats["failed"] += 1
                self.migration_stats["errors"].append(
                    f"{field_name}: {str(e)}"
                )
    
    def _extract_field_from_dict(
        self,
        content: str,
        field_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract field definition from dictionary content"""
        # Find the field definition block
        pattern = rf'{field_name}\s*:\s*FieldDefinition\((.*?)\)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return None
        
        block = match.group(1)
        
        result = {}
        
        # Extract name
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', block)
        if name_match:
            result["name"] = name_match.group(1)
        
        # Extract description
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', block)
        if desc_match:
            result["description"] = desc_match.group(1)
        
        # Extract standard
        std_match = re.search(r'standard\s*=\s*["\']([^"\']+)["\']', block)
        if std_match:
            result["standard"] = std_match.group(1)
        
        # Extract type
        type_match = re.search(r'field_type\s*=\s*FieldType\.(\w+)', block)
        if type_match:
            result["field_type"] = type_match.group(1)
        
        # Extract tier
        tier_match = re.search(r'tier\s*=\s*FieldTier\.(\w+)', block)
        if tier_match:
            result["tier"] = tier_match.group(1)
        
        # Extract example
        ex_match = re.search(r'example\s*=\s*["\']([^"\']+)["\']', block)
        if ex_match:
            result["example"] = ex_match.group(1)
        
        return result if result else None
    
    def _migrate_from_function_format(
        self,
        content: str,
        source_path: str
    ) -> None:
        """Migrate fields from function-based format"""
        source = self._detect_source(source_path)
        
        # Look for field count function
        count_pattern = r'def\s+get_\w+_field_count\(\)\s*->\s*int.*?return\s+(\d+)'
        count_match = re.search(count_pattern, content, re.DOTALL)
        
        if count_match:
            estimated_count = int(count_match.group(1))
            
            # Try to extract field names from get_*_fields functions
            fields_pattern = r'def\s+get_\w+_fields\(\)\s*->.*?return\s*\[(.*?)\]'
            fields_match = re.search(fields_pattern, content, re.DOTALL)
            
            if fields_match:
                fields_str = fields_match.group(1)
                field_names = re.findall(r'["\'](\w+)["\']', fields_str)
                
                for field_name in field_names:
                    self.migration_stats["total_processed"] += 1
                    
                    try:
                        field = self._create_field_from_name(
                            field_name, source
                        )
                        self.registry.register_field(field, validate=False)
                        self.migration_stats["successful"] += 1
                    except Exception as e:
                        self.migration_stats["failed"] += 1
                        self.migration_stats["errors"].append(
                            f"{field_name}: {str(e)}"
                        )
    
    def _create_field_definition(
        self,
        name: str,
        field_def: Dict[str, Any],
        source: FieldSource
    ) -> FieldDefinition:
        """Create a FieldDefinition from extracted data"""
        # Map string type to FieldType
        type_map = {
            "string": FieldType.STRING,
            "integer": FieldType.INTEGER,
            "float": FieldType.FLOAT,
            "boolean": FieldType.BOOLEAN,
            "datetime": FieldType.DATETIME,
            "rational": FieldType.RATIONAL,
            "gps": FieldType.GPS,
            "array": FieldType.ARRAY,
        }
        
        field_type = type_map.get(
            field_def.get("field_type", "string").lower(),
            FieldType.STRING
        )
        
        # Map tier
        tier_map = {
            "free": FieldTier.FREE,
            "professional": FieldTier.PROFESSIONAL,
            "forensic": FieldTier.FORENSIC,
            "enterprise": FieldTier.ENTERPRISE,
        }
        
        tier = tier_map.get(
            field_def.get("tier", "free").lower(),
            FieldTier.FREE
        )
        
        return FieldDefinition(
            name=name,
            field_type=field_type,
            source=source,
            description=field_def.get("description", f"{name} field"),
            standard_name=field_def.get("standard", name),
            tier=tier,
            example_value=field_def.get("example"),
        )
    
    def _create_field_from_name(
        self,
        name: str,
        source: FieldSource
    ) -> FieldDefinition:
        """Create a basic FieldDefinition from field name"""
        return FieldDefinition(
            name=name,
            field_type=FieldType.STRING,
            source=source,
            description=f"{name} extracted from {source.value}",
        )
    
    def _detect_source(self, source_path: str) -> FieldSource:
        """Detect the field source from file path"""
        path_lower = source_path.lower()
        
        if "exif" in path_lower:
            return FieldSource.EXIF
        elif "iptc" in path_lower or "xmp" in path_lower:
            return FieldSource.XMP
        elif "maker" in path_lower or "canon" in path_lower or "nikon" in path_lower:
            return FieldSource.MAKERNOTE
        elif "dicom" in path_lower:
            return FieldSource.DICOM
        elif "audio" in path_lower or "id3" in path_lower:
            return FieldSource.ID3
        elif "video" in path_lower or "quicktime" in path_lower:
            return FieldSource.QUICKTIME
        elif "pdf" in path_lower:
            return FieldSource.PDF
        else:
            return FieldSource.CUSTOM
    
    def migrate_from_inventory(self, inventory_path: str) -> Dict[str, Any]:
        """
        Migrate fields from field inventory JSON.
        
        Args:
            inventory_path: Path to inventory JSON file
            
        Returns:
            Migration statistics
        """
        self.migration_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        if not os.path.exists(inventory_path):
            self.migration_stats["errors"].append(f"File not found: {inventory_path}")
            return self.migration_stats
        
        with open(inventory_path) as f:
            inventory = json.load(f)
        
        # Process each category
        for category, data in inventory.get("fields", {}).items():
            source = self._category_to_source(category)
            
            for field_data in data:
                self.migration_stats["total_processed"] += 1
                
                try:
                    field = self._field_from_inventory_entry(field_data, source)
                    self.registry.register_field(field, validate=False)
                    self.migration_stats["successful"] += 1
                except Exception as e:
                    self.migration_stats["failed"] += 1
                    self.migration_stats["errors"].append(
                        f"{field_data.get('name', 'unknown')}: {str(e)}"
                    )
        
        return self.migration_stats
    
    def _field_from_inventory_entry(
        self,
        entry: Dict[str, Any],
        source: FieldSource
    ) -> FieldDefinition:
        """Create FieldDefinition from inventory entry"""
        name = entry.get("name", "Unknown")
        description = entry.get("desc", f"{name} field")
        
        # Guess type from name and description
        field_type = self._guess_field_type(name, description)
        
        return FieldDefinition(
            name=name,
            field_type=field_type,
            source=source,
            description=description,
            standard_name=name,
        )
    
    def _guess_field_type(
        self,
        name: str,
        description: str
    ) -> FieldType:
        """Guess field type from name and description"""
        text = f"{name} {description}".lower()
        
        if "date" in text or "time" in text:
            return FieldType.DATETIME
        elif "latitude" in text or "longitude" in text or "gps" in text:
            return FieldType.GPS
        elif "number" in text or "count" in text or "size" in text:
            return FieldType.INTEGER
        elif "ratio" in text or "rate" in text or "version" in text:
            return FieldType.FLOAT
        elif "flag" in text or "boolean" in text:
            return FieldType.BOOLEAN
        elif "list" in text or "array" in text:
            return FieldType.ARRAY
        else:
            return FieldType.STRING
    
    def _category_to_source(self, category: str) -> FieldSource:
        """Convert category name to FieldSource"""
        category_lower = category.lower()
        
        if "exif" in category_lower:
            return FieldSource.EXIF
        elif "iptc" in category_lower:
            return FieldSource.IPTC
        elif "xmp" in category_lower:
            return FieldSource.XMP
        elif "maker" in category_lower or "canon" in category_lower:
            return FieldSource.MAKERNOTE
        elif "dicom" in category_lower:
            return FieldSource.DICOM
        elif "quicktime" in category_lower:
            return FieldSource.QUICKTIME
        elif "matroska" in category_lower or "mkv" in category_lower:
            return FieldSource.MATROSKA
        elif "id3" in category_lower:
            return FieldSource.ID3
        elif "flac" in category_lower:
            return FieldSource.FLAC
        elif "pdf" in category_lower:
            return FieldSource.PDF
        else:
            return FieldSource.CUSTOM
    
    def generate_migration_report(self) -> str:
        """Generate a human-readable migration report"""
        lines = [
            "=" * 60,
            "FIELD REGISTRY MIGRATION REPORT",
            "=" * 60,
            "",
            f"Timestamp: {datetime.utcnow().isoformat()}",
            "",
            "-" * 40,
            "SUMMARY",
            "-" * 40,
            f"Total Processed: {self.migration_stats['total_processed']}",
            f"Successful:      {self.migration_stats['successful']}",
            f"Failed:          {self.migration_stats['failed']}",
            f"Skipped:         {self.migration_stats['skipped']}",
            "",
        ]
        
        if self.migration_stats["errors"]:
            lines.extend([
                "-" * 40,
                "ERRORS",
                "-" * 40,
            ])
            for error in self.migration_stats["errors"][:50]:
                lines.append(f"  - {error}")
            
            if len(self.migration_stats["errors"]) > 50:
                lines.append(f"  ... and {len(self.migration_stats['errors']) - 50} more")
        
        lines.extend([
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """Main entry point for migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate field definitions to unified registry"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source file or directory to migrate"
    )
    parser.add_argument(
        "--output",
        help="Output path for migrated registry"
    )
    parser.add_argument(
        "--format",
        choices=["auto", "dict", "inventory"],
        default="auto",
        help="Source format (default: auto)"
    )
    parser.add_argument(
        "--storage",
        help="Path for registry storage"
    )
    
    args = parser.parse_args()
    
    # Create registry
    registry = FieldRegistryCore(storage_path=args.storage)
    
    # Create migration handler
    migration = FieldMigration(registry)
    
    # Run migration
    if os.path.isdir(args.source):
        # Migrate all files in directory
        for filename in os.listdir(args.source):
            if filename.endswith(".py"):
                filepath = os.path.join(args.source, filename)
                print(f"Migrating: {filepath}")
                result = migration.migrate_from_file(filepath)
                print(f"  Processed: {result['total_processed']}, "
                      f"Success: {result['successful']}, "
                      f"Failed: {result['failed']}")
    else:
        # Migrate single file
        result = migration.migrate_from_file(args.source)
        print(f"Migration complete: {result}")
    
    # Print report
    print("\n" + migration.generate_migration_report())
    
    # Save registry if output specified
    if args.output:
        registry.save_to_disk(args.output)
        print(f"\nRegistry saved to: {args.output}")
    
    # Print final stats
    stats = registry.get_stats()
    print(f"\nFinal registry stats:")
    print(f"  Total fields: {stats.total_fields}")
    print(f"  Total collections: {stats.total_collections}")


if __name__ == "__main__":
    main()

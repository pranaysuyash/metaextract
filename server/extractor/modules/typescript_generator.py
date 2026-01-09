"""
TypeScript Code Generator for Unified Field Registry

This module generates TypeScript interfaces and types from field definitions,
ensuring consistency between Python and TypeScript codebases.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from unified_field_registry import FieldRegistryCore
from field_definitions import (
    FieldDefinition,
    FieldCollection,
    FieldType,
    FieldTier,
    DisplayLevel,
    FieldSource,
)

logger = logging.getLogger(__name__)


class TypeScriptGenerator:
    """
    Generates TypeScript interfaces and types from field definitions.
    
    Ensures TypeScript/Python consistency by automatically generating
    TypeScript code from the field registry.
    """
    
    def __init__(self, field_registry: Optional[FieldRegistryCore] = None):
        """
        Initialize the TypeScript generator.
        
        Args:
            field_registry: Optional field registry instance
        """
        self.registry = field_registry
        self._generated_types: Dict[str, str] = {}
    
    def attach_registry(self, registry: FieldRegistryCore) -> None:
        """Attach a field registry"""
        self.registry = registry
    
    def generate_all(self) -> str:
        """
        Generate all TypeScript code.
        
        Returns:
            Complete TypeScript code as string
        """
        if not self.registry:
            raise ValueError("No registry attached")
        
        lines = [
            self._generate_header(),
            self._generate_types(),
            self._generate_enums(),
            self._generate_field_definition_interface(),
            self._generate_source_interfaces(),
            self._generate_collection_interfaces(),
            self._generate_registry_interface(),
            self._generate_helper_functions(),
            ""
        ]
        
        return "\n".join(filter(None, lines))
    
    def _generate_header(self) -> str:
        """Generate file header"""
        from datetime import datetime
        return f"""/**
 * Auto-generated TypeScript interfaces from Unified Field Registry
 * 
 * This file is AUTO-GENERATED from the Python field registry.
 * DO NOT EDIT MANUALLY - changes will be overwritten.
 * 
 * Generated: {datetime.utcnow().isoformat()}
 * 
 * To regenerate: Run scripts/generate_typescript.py
 */

"""
    
    def _generate_types(self) -> str:
        """Generate base type definitions"""
        return """// Base type for metadata values
export type MetadataValue = 
  | string 
  | number 
  | boolean 
  | null 
  | string[]
  | number[]
  | MetadataObject
  | MetadataArray;

// Generic object type
export interface MetadataObject {
  [key: string]: MetadataValue;
}

// Generic array type
export type MetadataArray = MetadataValue[];

// GPS coordinate type
export interface GPSCoordinates {
  latitude: number;
  longitude: number;
  altitude?: number;
  precision?: number;
}

// Color type
export type Color = string;

// Hash type
export type Hash = string;

// UUID type
export type UUID = string;

"""
    
    def _generate_enums(self) -> str:
        """Generate TypeScript enums from Python enums"""
        lines = [
            "// Field Type Enum",
            self._generate_field_type_enum(),
            "",
            "// Field Tier Enum",
            self._generate_field_tier_enum(),
            "",
            "// Display Level Enum",
            self._generate_display_level_enum(),
            "",
            "// Field Source Enum",
            self._generate_field_source_enum(),
            "",
        ]
        return "\n".join(lines)
    
    def _generate_field_type_enum(self) -> str:
        """Generate FieldType enum"""
        lines = [
            "export enum FieldType {",
        ]
        
        for member in FieldType:
            ts_name = member.name.upper()
            ts_value = member.value
            lines.append(f'  {ts_name} = "{ts_value}",')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_field_tier_enum(self) -> str:
        """Generate FieldTier enum"""
        lines = [
            "export enum FieldTier {",
        ]
        
        for member in FieldTier:
            ts_name = member.name.upper()
            ts_value = member.value
            lines.append(f'  {ts_name} = "{ts_value}",')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_display_level_enum(self) -> str:
        """Generate DisplayLevel enum"""
        lines = [
            "export enum DisplayLevel {",
        ]
        
        for member in DisplayLevel:
            ts_name = member.name.upper()
            ts_value = member.value
            lines.append(f'  {ts_name} = "{ts_value}",')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_field_source_enum(self) -> str:
        """Generate FieldSource enum"""
        lines = [
            "export enum FieldSource {",
        ]
        
        for member in FieldSource:
            ts_name = member.name.upper()
            ts_value = member.value
            lines.append(f'  {ts_name} = "{ts_value}",')
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_field_definition_interface(self) -> str:
        """Generate FieldDefinition interface"""
        return """// Field Validation Rule
export interface ValidationRule {
  ruleType: string;
  value: any;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

// Field Deprecation Info
export interface FieldDeprecation {
  deprecatedVersion: string;
  removalVersion: string;
  reason: string;
  migrationPath?: string;
  alternativeField?: string;
}

// Field Metadata
export interface FieldMetadata {
  searchKeywords: string[];
  categoryTags: string[];
  usageExamples: string[];
  relatedFields: string[];
  seeAlsoReferences: string[];
  parentField?: string;
  childFields: string[];
  aliasNames: string[];
  extractionCost: 'low' | 'medium' | 'high';
  isComputed: boolean;
  computationDependencies: string[];
  sinceVersion?: string;
  lastModifiedVersion?: string;
}

// Field Definition Interface
export interface FieldDefinition {
  name: string;
  fieldId: string;
  standardName: string;
  fieldType: FieldType;
  source: FieldSource;
  tier: FieldTier;
  display: DisplayLevel;
  description: string;
  longDescription?: string;
  significance?: string;
  exampleValue?: MetadataValue;
  defaultValue?: MetadataValue;
  validationRules: ValidationRule[];
  isRequired: boolean;
  isDeprecated: boolean;
  deprecation?: FieldDeprecation;
  metadata: FieldMetadata;
  version: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  compatibleExtensions: string[];
  extractionOrder: number;
}

"""
    
    def _generate_source_interfaces(self) -> str:
        """Generate interfaces for each field source"""
        if not self.registry:
            return ""
        
        lines = ["// Source-specific interfaces", ""]
        
        for source in FieldSource:
            fields = self.registry.get_fields_by_source(source)
            if not fields:
                continue
            
            interface_name = self._source_to_interface_name(source)
            lines.append(f"// {source.value} fields")
            lines.append(f"export interface {interface_name} {{")
            
            for field_name, field in sorted(fields.items()):
                ts_type = self._field_type_to_ts(field.field_type)
                optional = "?" if not field.is_required else ""
                doc = f"  // {field.description[:50]}" if field.description else ""
                lines.append(f"  {doc}")
                lines.append(f"  {field_name}{optional}: {ts_type};")
            
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_collection_interfaces(self) -> str:
        """Generate interfaces for field collections"""
        if not self.registry:
            return ""
        
        lines = ["// Collection interfaces", ""]
        
        for collection_id, collection in self.registry.get_all_collections().items():
            interface_name = self._to_pascal_case(collection.name)
            lines.append(f"// {collection.name} collection")
            lines.append(f"export interface {interface_name} {{")
            
            for field_name, field in collection.fields.items():
                ts_type = self._field_type_to_ts(field.field_type)
                optional = "?" if not field.is_required else ""
                lines.append(f"  {field_name}{optional}: {ts_type};")
            
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_registry_interface(self) -> str:
        """Generate registry interface"""
        return """// Field Registry Interface
export interface FieldRegistry {
  getField(name: string): FieldDefinition | undefined;
  getFieldById(id: string): FieldDefinition | undefined;
  getAllFields(): Record<string, FieldDefinition>;
  getFieldsBySource(source: FieldSource): Record<string, FieldDefinition>;
  getFieldsByTier(tier: FieldTier): Record<string, FieldDefinition>;
  getFieldsForDisplay(display: DisplayLevel): Record<string, FieldDefinition>;
  searchFields(query: string): FieldDefinition[];
  getStats(): RegistryStats;
}

// Registry Statistics
export interface RegistryStats {
  totalFields: number;
  totalCollections: number;
  bySource: Record<string, number>;
  byTier: Record<string, number>;
  byType: Record<string, number>;
  byDisplay: Record<string, number>;
  deprecatedCount: number;
  requiredCount: number;
}

// Extension Info
export interface ExtensionInfo {
  extensionId: string;
  name: string;
  description: string;
  version: string;
  supportedFields: string[];
  fileTypes: string[];
  priority: number;
  isActive: boolean;
}

// Validation Result
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

"""
    
    def _generate_helper_functions(self) -> str:
        """Generate helper functions"""
        return """// Helper functions

export function isFieldType(value: string): value is FieldType {
  return Object.values(FieldType).includes(value as FieldType);
}

export function isFieldTier(value: string): value is FieldTier {
  return Object.values(FieldTier).includes(value as FieldTier);
}

export function isDisplayLevel(value: string): value is DisplayLevel {
  return Object.values(DisplayLevel).includes(value as DisplayLevel);
}

export function isFieldSource(value: string): value is FieldSource {
  return Object.values(FieldSource).includes(value as FieldSource);
}

export function validateFieldValue(
  field: FieldDefinition,
  value: any
): ValidationResult {
  const result: ValidationResult = {
    isValid: true,
    errors: [],
    warnings: []
  };

  if (value === undefined || value === null) {
    if (field.isRequired) {
      result.isValid = false;
      result.errors.push(`Field '${field.name}' is required`);
    }
    return result;
  }

  // Apply validation rules
  for (const rule of field.validationRules) {
    // Simple validation examples - extend as needed
    if (rule.ruleType === 'regex' && typeof value === 'string') {
      const regex = new RegExp(rule.value);
      if (!regex.test(value)) {
        if (rule.severity === 'error') {
          result.isValid = false;
          result.errors.push(rule.message);
        } else {
          result.warnings.push(rule.message);
        }
      }
    }
  }

  return result;
}

export function fieldTypeToTsType(fieldType: FieldType): string {
  const mapping: Record<FieldType, string> = {
    [FieldType.STRING]: 'string',
    [FieldType.INTEGER]: 'number',
    [FieldType.FLOAT]: 'number',
    [FieldType.BOOLEAN]: 'boolean',
    [FieldType.DATETIME]: 'string',
    [FieldType.BINARY]: 'string',
    [FieldType.ARRAY]: 'unknown[]',
    [FieldType.OBJECT]: 'Record<string, unknown>',
    [FieldType.GPS]: 'GPSCoordinates',
    [FieldType.RATIONAL]: 'number',
    [FieldType.UUID]: 'UUID',
    [FieldType.ENUM]: 'string',
    [FieldType.COLOR]: 'Color',
    [FieldType.HASH]: 'Hash',
    [FieldType.EMAIL]: 'string',
    [FieldType.URL]: 'string',
    [FieldType.IP_ADDRESS]: 'string',
  };
  return mapping[fieldType] || 'unknown';
}

"""
    
    def _field_type_to_ts(self, field_type: FieldType) -> str:
        """Convert Python FieldType to TypeScript type"""
        type_mapping = {
            FieldType.STRING: "string",
            FieldType.INTEGER: "number",
            FieldType.FLOAT: "number",
            FieldType.BOOLEAN: "boolean",
            FieldType.DATETIME: "string",
            FieldType.BINARY: "string",
            FieldType.ARRAY: "MetadataArray",
            FieldType.OBJECT: "MetadataObject",
            FieldType.GPS: "GPSCoordinates",
            FieldType.RATIONAL: "number",
            FieldType.UUID: "UUID",
            FieldType.ENUM: "string",
            FieldType.COLOR: "Color",
            FieldType.HASH: "Hash",
            FieldType.EMAIL: "string",
            FieldType.URL: "string",
            FieldType.IP_ADDRESS: "string",
        }
        return type_mapping.get(field_type, "unknown")
    
    def _source_to_interface_name(self, source: FieldSource) -> str:
        """Convert FieldSource to interface name"""
        name = source.value.replace("-", "_").replace(" ", "_")
        return f"{name}Fields"
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert snake_case to PascalCase"""
        return "".join(word.capitalize() for word in name.split("_"))
    
    def generate_to_file(self, output_path: str) -> None:
        """
        Generate TypeScript and write to file.
        
        Args:
            output_path: Path to write TypeScript file
        """
        content = self.generate_all()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(content)
        
        logger.info(f"Generated TypeScript registry to {output_path}")
    
    def generate_image_metadata_types(self) -> str:
        """Generate image-specific TypeScript types"""
        if not self.registry:
            return ""
        
        lines = [
            "/**",
            " * Image-specific metadata types",
            " * Auto-generated from Unified Field Registry",
            " */",
            "",
            "// Basic Image Properties",
            "export interface BasicImageMetadata {",
            "  width: number;",
            "  height: number;",
            "  format: string;",
            "  mode: string;",
            "  hasTransparency: boolean;",
            "  aspectRatio: number;",
            "  megapixels: number;",
            "}",
            "",
            "// EXIF Image Properties",
            "export interface EXIFMetadata {",
            "  make?: string;",
            "  model?: string;",
            "  software?: string;",
            "  dateTimeOriginal?: string;",
            "  exposureTime?: string;",
            "  fNumber?: number;",
            "  isoSpeedRatings?: number;",
            "  focalLength?: number;",
            "  flash?: boolean;",
            "  gpsLatitude?: number;",
            "  gpsLongitude?: number;",
            "  gpsAltitude?: number;",
            "  artist?: string;",
            "  copyright?: string;",
            "  imageDescription?: string;",
            "}",
            "",
            "// IPTC/XMP Properties",
            "export interface IPTCXMPMetadata {",
            "  title?: string;",
            "  description?: string;",
            "  keywords?: string[];",
            "  byLine?: string;",
            "  credit?: string;",
            "  copyright?: string;",
            "  headline?: string;",
            "  city?: string;",
            "  country?: string;",
            "  dateCreated?: string;",
            "}",
            "",
            "// Complete Image Metadata",
            "export interface CompleteImageMetadata {",
            "  basic: BasicImageMetadata;",
            "  exif?: EXIFMetadata;",
            "  iptcXmp?: IPTCXMPMetadata;",
            "  colorProfile?: {",
            "    colorSpace: string;",
            "    profileName: string;",
            "    profileSize: number;",
            "  };",
            "  perceptualHashes?: {",
            "    ahash?: string;",
            "    phash?: string;",
            "    dhash?: string;",
            "    whash?: string;",
            "  };",
            "  qualityMetrics?: {",
            "    sharpness: number;",
            "    brightness: number;",
            "    contrast: number;",
            "    overallScore: number;",
            "  };",
            "}",
        ]
        
        return "\n".join(lines)
    
    def generate_dicom_metadata_types(self) -> str:
        """Generate DICOM-specific TypeScript types"""
        if not self.registry:
            return ""
        
        lines = [
            "/**",
            " * DICOM-specific metadata types",
            " * Auto-generated from Unified Field Registry",
            " */",
            "",
            "// Base DICOM Properties",
            "export interface DICOMBaseMetadata {",
            "  patientName?: string;",
            "  patientID?: string;",
            "  studyDate?: string;",
            "  studyTime?: string;",
            "  modality?: string;",
            "  studyInstanceUID?: string;",
            "  seriesInstanceUID?: string;",
            "  sopInstanceUID?: string;",
            "  rows?: number;",
            "  columns?: number;",
            "  bitsAllocated?: number;",
            "}",
            "",
            "// DICOM Specialty Types",
            "export interface DICOMCardiologyMetadata {",
            "  heartRate?: number;",
            "  lvEF?: number;",
            "  cardiacCyclePosition?: string;",
            "  acquisitionDate?: string;",
            "  acquisitionTime?: string;",
            "}",
            "",
            "export interface DICOMNeurologyMetadata {",
            "  brainVolume?: number;",
            "  sliceThickness?: number;",
            "  sequenceName?: string;",
            "  scanOptions?: string;",
            "}",
            "",
            "export interface DICOMRadiologyMetadata {",
            "  bodyPartExamined?: string;",
            "  protocolName?: string;",
            "  studyID?: string;",
            "  seriesNumber?: number;",
            "  instanceNumber?: number;",
            "  performingPhysicianName?: string;",
            "}",
            "",
            "// Complete DICOM Metadata",
            "export interface CompleteDICOMMetadata {",
            "  base: DICOMBaseMetadata;",
            "  cardiology?: DICOMCardiologyMetadata;",
            "  neurology?: DICOMNeurologyMetadata;",
            "  radiology?: DICOMRadiologyMetadata;",
            "}",
        ]
        
        return "\n".join(lines)


def generate_typescript_registry(
    registry: FieldRegistryCore,
    output_path: Optional[str] = None
) -> str:
    """
    Convenience function to generate TypeScript from registry.
    
    Args:
        registry: Field registry to generate from
        output_path: Optional path to write file
        
    Returns:
        Generated TypeScript code
    """
    generator = TypeScriptGenerator(registry)
    code = generator.generate_all()
    
    if output_path:
        generator.generate_to_file(output_path)
    
    return code


# Export
__all__ = [
    "TypeScriptGenerator",
    "generate_typescript_registry",
]

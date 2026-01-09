"""
Tests for Unified Field Registry System

Comprehensive test suite for the field registry, builder, and related components.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime

# Add server/extractor/modules to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "server" / "extractor" / "modules"))


class TestFieldDefinitions:
    """Tests for field definition dataclasses"""
    
    def test_field_definition_creation(self):
        """Test basic field definition creation"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldTier,
            DisplayLevel,
            FieldSource,
        )
        
        field = FieldDefinition(
            name="GPSLatitude",
            field_type=FieldType.GPS,
            source=FieldSource.EXIF,
            description="Geographic latitude"
        )
        
        assert field.name == "GPSLatitude"
        assert field.field_type == FieldType.GPS
        assert field.source == FieldSource.EXIF
        assert field.description == "Geographic latitude"
        assert field.tier == FieldTier.FREE
        assert field.display == DisplayLevel.ADVANCED
        assert field.is_required == False
        assert field.is_deprecated == False
    
    def test_field_definition_with_all_options(self):
        """Test field definition with all options set"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldTier,
            DisplayLevel,
            FieldSource,
            FieldMetadata,
        )
        
        field = FieldDefinition(
            name="ExposureTime",
            field_type=FieldType.RATIONAL,
            source=FieldSource.EXIF,
            description="Shutter speed in seconds",
            tier=FieldTier.FREE,
            display=DisplayLevel.SIMPLE,
            example_value="1/250",
            significance="Affects motion blur",
            is_required=False,
            metadata=FieldMetadata(
                search_keywords=["shutter", "exposure", "photography"],
                category_tags=["camera", "exposure"],
                related_fields=["FNumber", "ISOSpeedRatings"]
            ),
            compatible_extensions=["image_advanced", "image_master"]
        )
        
        assert field.name == "ExposureTime"
        assert field.example_value == "1/250"
        assert field.significance == "Affects motion blur"
        assert "shutter" in field.metadata.search_keywords
        assert "FNumber" in field.metadata.related_fields
        assert "image_advanced" in field.compatible_extensions
    
    def test_field_to_dict(self):
        """Test field serialization to dictionary"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        field = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="A test field"
        )
        
        data = field.to_dict()
        
        assert data["name"] == "TestField"
        assert data["field_type"] == "string"
        assert data["source"] == "EXIF"
        assert data["description"] == "A test field"
    
    def test_field_from_dict(self):
        """Test field deserialization from dictionary"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        data = {
            "name": "TestField",
            "field_id": "test-uuid-123",
            "standard_name": "TestField",
            "field_type": "integer",
            "source": "EXIF",
            "tier": "professional",
            "display": "advanced",
            "description": "A test field",
            "version": "1.0.0"
        }
        
        field = FieldDefinition.from_dict(data)
        
        assert field.name == "TestField"
        assert field.field_type == FieldType.INTEGER
        assert field.tier.value == "professional"
    
    def test_field_validation(self):
        """Test field value validation"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
            ValidationRuleType,
            FieldValidationRule,
        )
        
        field = FieldDefinition(
            name="EmailField",
            field_type=FieldType.STRING,
            source=FieldSource.XMP,
            description="Email address",
            validation_rules=[
                FieldValidationRule(
                    rule_type=ValidationRuleType.EMAIL,
                    value=True,
                    message="Invalid email format"
                )
            ]
        )
        
        # Valid email
        is_valid, _ = field.validate_value("test@example.com")
        assert is_valid == True
        
        # Invalid email
        is_valid, msg = field.validate_value("not-an-email")
        assert is_valid == False
        assert "Invalid email" in msg
    
    def test_enum_values(self):
        """Test enum value conversions"""
        from field_definitions import FieldType, FieldTier, DisplayLevel, FieldSource
        
        # Test FieldType
        assert FieldType.STRING.value == "string"
        assert FieldType.GPS.value == "gps"
        
        # Test FieldTier
        assert FieldTier.FREE.value == "free"
        assert FieldTier.PROFESSIONAL.value == "professional"
        
        # Test DisplayLevel
        assert DisplayLevel.SIMPLE.value == "simple"
        assert DisplayLevel.ADVANCED.value == "advanced"
        
        # Test FieldSource
        assert FieldSource.EXIF.value == "EXIF"
        assert FieldSource.DICOM.value == "DICOM"


class TestFieldBuilder:
    """Tests for field builder"""
    
    def test_basic_field_creation(self):
        """Test basic field builder usage"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource, FieldTier
        
        field = (FieldBuilder()
            .create("GPSLatitude", FieldType.GPS, FieldSource.EXIF, "Geographic latitude")
            .with_tier(FieldTier.FREE)
            .simple_display()
            .with_example({"latitude": 37.7749, "longitude": -122.4194})
            .with_keywords("gps", "location", "coordinates")
            .build())
        
        assert field.name == "GPSLatitude"
        assert field.field_type.value == "gps"
        assert field.tier.value == "free"
        assert field.display.value == "simple"
        assert "gps" in field.metadata.search_keywords
    
    def test_validation_rules(self):
        """Test adding validation rules"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource, ValidationRuleType
        
        field = (FieldBuilder()
            .create("Age", FieldType.INTEGER, FieldSource.CUSTOM, "Person age")
            .range_validation(0, 150, "Age must be between 0 and 150")
            .build())
        
        assert len(field.validation_rules) == 1
        assert field.validation_rules[0].rule_type == ValidationRuleType.RANGE
    
    def test_email_validation(self):
        """Test email validation builder method"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource
        
        field = (FieldBuilder()
            .create("ContactEmail", FieldType.EMAIL, FieldSource.XMP, "Contact email")
            .email_validation()
            .build())
        
        assert len(field.validation_rules) == 1
        assert field.validation_rules[0].rule_type.value == "email"
    
    def test_deprecation(self):
        """Test deprecation marking"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource
        
        field = (FieldBuilder()
            .create("OldField", FieldType.STRING, FieldSource.EXIF, "Deprecated field")
            .deprecated(
                deprecated_version="1.0.0",
                removal_version="2.0.0",
                reason="Replaced by NewField",
                alternative="NewField"
            )
            .build())
        
        assert field.is_deprecated == True
        assert field.deprecation is not None
        assert field.deprecation.alternative_field == "NewField"
    
    def test_collection_association(self):
        """Test field collection association"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource
        
        field, collection = (FieldBuilder()
            .create("TestField", FieldType.STRING, FieldSource.EXIF, "Test")
            .in_collection("exif_standard")
            .build_with_collection())
        
        assert collection == "exif_standard"
    
    def test_copy_builder(self):
        """Test builder copy functionality"""
        from field_builder import FieldBuilder
        from field_definitions import FieldType, FieldSource
        
        original = (FieldBuilder()
            .create("Original", FieldType.STRING, FieldSource.EXIF, "Original field")
            .with_keywords("original"))
        
        copied = original.copy()
        copied._field.name = "Copied"
        
        assert original.field.name == "Original"
        assert copied.field.name == "Copied"


class TestFieldRegistryCore:
    """Tests for field registry core"""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test"""
        from unified_field_registry import FieldRegistryCore
        return FieldRegistryCore()
    
    def test_register_field(self, registry):
        """Test field registration"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        field = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="A test field"
        )
        
        result = registry.register_field(field)
        assert result == True
        assert "TestField" in registry
        assert registry.get_field("TestField") == field
    
    def test_register_duplicate_fails(self, registry):
        """Test that registering duplicate fields fails"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        field1 = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="First field"
        )
        
        field2 = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="Second field"
        )
        
        registry.register_field(field1)
        
        from unified_field_registry import FieldAlreadyExistsError
        with pytest.raises(FieldAlreadyExistsError):
            registry.register_field(field2)
    
    def test_register_with_overwrite(self, registry):
        """Test that overwrite=True allows duplicate registration"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        field1 = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="First field"
        )
        
        field2 = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="Second field"
        )
        
        registry.register_field(field1)
        result = registry.register_field(field2, overwrite=True)
        
        assert result == True
        assert registry.get_field("TestField").description == "Second field"
    
    def test_unregister_field(self, registry):
        """Test field unregistration"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        field = FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="A test field"
        )
        
        registry.register_field(field)
        assert "TestField" in registry
        
        result = registry.unregister_field("TestField")
        assert result == True
        assert "TestField" not in registry
    
    def test_get_fields_by_source(self, registry):
        """Test filtering fields by source"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        registry.register_field(FieldDefinition(
            name="ExifField1", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="EXIF field 1"
        ))
        registry.register_field(FieldDefinition(
            name="ExifField2", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="EXIF field 2"
        ))
        registry.register_field(FieldDefinition(
            name="XmpField", field_type=FieldType.STRING,
            source=FieldSource.XMP, description="XMP field"
        ))
        
        exif_fields = registry.get_fields_by_source(FieldSource.EXIF)
        assert len(exif_fields) == 2
        assert "ExifField1" in exif_fields
        assert "ExifField2" in exif_fields
        assert "XmpField" not in exif_fields
    
    def test_get_fields_by_tier(self, registry):
        """Test filtering fields by tier"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
            FieldTier,
        )
        
        registry.register_field(FieldDefinition(
            name="FreeField", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Free tier",
            tier=FieldTier.FREE
        ))
        registry.register_field(FieldDefinition(
            name="ProField", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Professional tier",
            tier=FieldTier.PROFESSIONAL
        ))
        
        free_fields = registry.get_fields_by_tier(FieldTier.FREE)
        assert len(free_fields) == 1
        assert "FreeField" in free_fields
        assert "ProField" not in free_fields
        
        pro_fields = registry.get_fields_by_tier(FieldTier.PROFESSIONAL)
        # Should include both free and professional (tier inheritance)
        assert "FreeField" in pro_fields
        assert "ProField" in pro_fields
    
    def test_search_fields(self, registry):
        """Test field search functionality"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
        )
        
        registry.register_field(FieldDefinition(
            name="GPSLatitude",
            field_type=FieldType.GPS,
            source=FieldSource.EXIF,
            description="Geographic latitude from GPS"
        ))
        registry.register_field(FieldDefinition(
            name="GPSLongitude",
            field_type=FieldType.GPS,
            source=FieldSource.EXIF,
            description="Geographic longitude from GPS"
        ))
        registry.register_field(FieldDefinition(
            name="CameraMake",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="Camera manufacturer"
        ))
        
        # Search by keyword
        results = registry.search_fields("GPS")
        assert len(results) == 2
        
        # Search in metadata
        registry.get_field("GPSLatitude").metadata.search_keywords.append("coordinates")
        results = registry.search_fields("coordinates", search_metadata=True)
        assert len(results) == 1
    
    def test_create_collection(self, registry):
        """Test field collection creation"""
        from field_definitions import FieldType, FieldSource
        from field_builder import FieldBuilder
        
        collection = registry.create_collection(
            collection_id="exif_standard",
            name="EXIF Standard",
            description="Standard EXIF fields",
            source="EXIF"
        )
        
        assert collection is not None
        assert registry.get_collection("exif_standard") == collection
        
        field = (FieldBuilder()
            .create("Make", FieldType.STRING, FieldSource.EXIF, "Camera make")
            .in_collection("exif_standard")
            .build())
        
        registry.register_field(field, collection="exif_standard")
        
        collection = registry.get_collection("exif_standard")
        assert "Make" in collection.fields
        assert collection.total_fields == 1
    
    def test_registry_stats(self, registry):
        """Test registry statistics"""
        from field_definitions import (
            FieldDefinition,
            FieldType,
            FieldSource,
            FieldTier,
        )
        
        registry.register_field(FieldDefinition(
            name="Free1", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Free field",
            tier=FieldTier.FREE
        ))
        registry.register_field(FieldDefinition(
            name="Pro1", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Pro field",
            tier=FieldTier.PROFESSIONAL
        ))
        registry.register_field(FieldDefinition(
            name="Forensic1", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Forensic field",
            tier=FieldTier.FORENSIC
        ))
        
        stats = registry.get_stats()
        
        assert stats.total_fields == 3
        assert stats.by_tier.get("free", 0) == 1
        assert stats.by_tier.get("professional", 0) == 1
        assert stats.by_tier.get("forensic", 0) == 1
    
    def test_serialization_roundtrip(self, registry):
        """Test registry save/load cycle"""
        from field_definitions import FieldDefinition, FieldType, FieldSource
        from unified_field_registry import FieldRegistryCore
        
        registry.register_field(FieldDefinition(
            name="TestField",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="Test field for serialization"
        ))
        
        # Export
        export = registry.export_json()
        
        # Create new registry and import
        registry2 = FieldRegistryCore()
        for field_data in export["fields"].values():
            field = FieldDefinition.from_dict(field_data)
            registry2.register_field(field)
        
        assert registry2.get_field("TestField") is not None
        assert registry2.get_field("TestField").description == "Test field for serialization"
    
    def test_len_and_iter(self, registry):
        """Test registry length and iteration"""
        from field_definitions import FieldDefinition, FieldType, FieldSource
        
        for i in range(5):
            registry.register_field(FieldDefinition(
                name=f"Field{i}",
                field_type=FieldType.STRING,
                source=FieldSource.EXIF,
                description=f"Field {i}"
            ))
        
        assert len(registry) == 5
        assert len(list(registry)) == 5


class TestExtensionMapper:
    """Tests for extension mapper"""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with some fields"""
        from unified_field_registry import FieldRegistryCore
        from field_definitions import FieldDefinition, FieldType, FieldSource
        
        reg = FieldRegistryCore()
        reg.register_field(FieldDefinition(
            name="Make", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Camera make"
        ))
        reg.register_field(FieldDefinition(
            name="Model", field_type=FieldType.STRING,
            source=FieldSource.EXIF, description="Camera model"
        ))
        reg.register_field(FieldDefinition(
            name="CustomField", field_type=FieldType.STRING,
            source=FieldSource.CUSTOM, description="Custom field"
        ))
        return reg
    
    def test_extension_registration(self, registry):
        """Test extension registration"""
        from extension_mapper import ExtensionMapper
        
        mapper = ExtensionMapper(registry)
        
        mapper.register_extension(
            extension_id="test_extension",
            name="Test Extension",
            description="A test extension",
            supported_fields=["Make", "Model"],
            file_types=[".jpg", ".png"]
        )
        
        ext_info = mapper.get_extension_info("test_extension")
        assert ext_info is not None
        assert ext_info.name == "Test Extension"
        assert "Make" in ext_info.supported_fields
    
    def test_get_extension_for_field(self, registry):
        """Test finding extensions for a field"""
        from extension_mapper import ExtensionMapper
        
        mapper = ExtensionMapper(registry)
        
        mapper.register_extension(
            extension_id="test_extension",
            name="Test Extension",
            description="A test extension",
            supported_fields=["Make", "Model"],
            file_types=[".jpg"]
        )
        
        extensions = mapper.get_extension_for_field("Make")
        assert "test_extension" in extensions
    
    def test_get_best_extension(self, registry):
        """Test getting the best extension for a field"""
        from extension_mapper import ExtensionMapper
        
        mapper = ExtensionMapper(registry)
        
        mapper.register_extension(
            extension_id="basic_ext",
            name="Basic Extension",
            description="Basic extension",
            supported_fields=["Make"],
            priority=10,
            file_types=[".jpg"]
        )
        mapper.register_extension(
            extension_id="advanced_ext",
            name="Advanced Extension",
            description="Advanced extension",
            supported_fields=["Make"],
            priority=25,  # Higher than built-in image_advanced (priority=20)
            file_types=[".jpg"]
        )
        
        best = mapper.get_best_extension("Make", ".jpg")
        assert best == "advanced_ext"
    
    def test_coverage_report(self, registry):
        """Test coverage report generation"""
        from extension_mapper import ExtensionMapper
        
        mapper = ExtensionMapper(registry)
        
        mapper.register_extension(
            extension_id="test_extension",
            name="Test Extension",
            description="A test extension",
            supported_fields=["Make"],
            file_types=[".jpg"]
        )
        
        report = mapper.get_coverage_report()
        
        assert "extensions" in report
        assert "field_coverage" in report
        assert "gaps" in report
        assert "CustomField" in report["field_coverage"]
        assert report["field_coverage"]["CustomField"]["has_coverage"] == False


class TestTypeScriptGenerator:
    """Tests for TypeScript generator"""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with some fields"""
        from unified_field_registry import FieldRegistryCore
        from field_definitions import FieldDefinition, FieldType, FieldSource
        
        reg = FieldRegistryCore()
        reg.register_field(FieldDefinition(
            name="GPSLatitude",
            field_type=FieldType.GPS,
            source=FieldSource.EXIF,
            description="Geographic latitude"
        ))
        reg.register_field(FieldDefinition(
            name="Make",
            field_type=FieldType.STRING,
            source=FieldSource.EXIF,
            description="Camera make"
        ))
        return reg
    
    def test_generate_all(self, registry):
        """Test complete TypeScript generation"""
        from typescript_generator import TypeScriptGenerator
        
        generator = TypeScriptGenerator(registry)
        generator.attach_registry(registry)
        
        ts_code = generator.generate_all()
        
        assert "FieldType" in ts_code
        assert "FieldTier" in ts_code
        assert "DisplayLevel" in ts_code
        assert "FieldSource" in ts_code
        assert "FieldDefinition" in ts_code
        assert "GPSLatitude" in ts_code
        assert "Make" in ts_code
    
    def test_generate_field_type_enum(self, registry):
        """Test field type enum generation"""
        from typescript_generator import TypeScriptGenerator
        
        generator = TypeScriptGenerator(registry)
        generator.attach_registry(registry)
        
        enum_code = generator._generate_field_type_enum()
        
        assert 'STRING = "string"' in enum_code
        assert 'GPS = "gps"' in enum_code
        assert 'INTEGER = "integer"' in enum_code


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

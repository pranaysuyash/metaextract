#!/usr/bin/env python3
"""
Field Registry Validation Script

This script validates the field registry for completeness, consistency,
and correctness.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_field_registry import FieldRegistryCore
from field_definitions import (
    FieldDefinition,
    FieldType,
    FieldTier,
    DisplayLevel,
    FieldSource,
)


class RegistryValidator:
    """Validates field registry for completeness and correctness"""
    
    def __init__(self, registry: FieldRegistryCore):
        self.registry = registry
        self.validation_results: List[Dict[str, Any]] = []
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all validation checks"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "checks": [],
            "summary": {}
        }
        
        checks = [
            self._check_required_fields,
            self._check_field_naming,
            self._check_type_consistency,
            self._check_source_validity,
            self._check_tier_distribution,
            self._check_display_distribution,
            self._check_validation_rules,
            self._check_extension_coverage,
            self._check_for_deprecated_fields,
            self._check_related_fields,
            self._check_metadata_completeness,
            self._check_duplicate_fields,
            self._check_index_consistency,
        ]
        
        for check in checks:
            check_name = check.__name__.replace("_check_", "")
            results["total_checks"] += 1
            
            result = check()
            results["checks"].append({
                "name": check_name,
                "passed": result["passed"],
                "message": result.get("message", ""),
                "details": result.get("details", [])
            })
            
            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["warnings"] += result.get("warnings", 0)
        
        results["summary"] = {
            "total_checks": results["total_checks"],
            "passed": results["passed"],
            "failed": results["failed"],
            "warnings": results["warnings"],
            "pass_rate": round(results["passed"] / results["total_checks"] * 100, 2) if results["total_checks"] else 0
        }
        
        self.validation_results = results["checks"]
        return results
    
    def _check_required_fields(self) -> Dict[str, Any]:
        """Check that all required fields exist"""
        passed = True
        message = "Required fields check"
        details = []
        warnings = 0
        
        required_fields = ["name", "description", "field_type", "source"]
        missing_required = []
        
        for field_name, field in self.registry.get_all_fields().items():
            for req_field in required_fields:
                if not hasattr(field, req_field) or getattr(field, req_field) is None:
                    missing_required.append(f"{field_name}: missing {req_field}")
        
        if missing_required:
            passed = False
            details = missing_required[:10]
            if len(missing_required) > 10:
                details.append(f"... and {len(missing_required) - 10} more")
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_field_naming(self) -> Dict[str, Any]:
        """Check field naming conventions"""
        passed = True
        message = "Field naming conventions"
        details = []
        warnings = 0
        
        naming_issues = []
        
        for field_name, field in self.registry.get_all_fields().items():
            # Check for spaces or special characters
            if not field_name.replace("_", "").replace("-", "").isalnum():
                naming_issues.append(f"{field_name}: contains invalid characters")
            
            # Check for uppercase in non-standard names
            if field_name != field_name.lower() and field_name.upper() != field_name:
                # Allow some common abbreviations
                allowed = ["GPS", "EXIF", "IPTC", "XMP", "DICOM", "UUID", "URL", "ID"]
                is_allowed = any(field_name.startswith(a) or field_name.endswith(a) for a in allowed)
                if not is_allowed:
                    naming_issues.append(f"{field_name}: contains mixed case")
        
        if naming_issues:
            passed = False
            details = naming_issues[:10]
            if len(naming_issues) > 10:
                details.append(f"... and {len(naming_issues) - 10} more")
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_type_consistency(self) -> Dict[str, Any]:
        """Check type consistency"""
        passed = True
        message = "Field type consistency"
        details = []
        warnings = 0
        
        type_issues = []
        
        for field_name, field in self.registry.get_all_fields().items():
            # Check example values match field type
            if field.example_value is not None:
                if not self._validate_type(field.field_type, field.example_value):
                    type_issues.append(
                        f"{field_name}: example value type doesn't match field type"
                    )
        
        if type_issues:
            passed = False
            details = type_issues[:10]
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _validate_type(self, field_type: FieldType, value: Any) -> bool:
        """Validate that a value matches the expected type"""
        if field_type == FieldType.STRING:
            return isinstance(value, str)
        elif field_type in [FieldType.INTEGER, FieldType.FLOAT, FieldType.RATIONAL]:
            return isinstance(value, (int, float))
        elif field_type == FieldType.BOOLEAN:
            return isinstance(value, bool)
        elif field_type == FieldType.DATETIME:
            return isinstance(value, str)  # Simplified check
        elif field_type == FieldType.ARRAY:
            return isinstance(value, list)
        elif field_type == FieldType.OBJECT:
            return isinstance(value, dict)
        return True
    
    def _check_source_validity(self) -> Dict[str, Any]:
        """Check all field sources are valid"""
        passed = True
        message = "Field source validity"
        details = []
        warnings = 0
        
        invalid_sources = []
        
        for field_name, field in self.registry.get_all_fields().items():
            if not isinstance(field.source, FieldSource):
                invalid_sources.append(f"{field_name}: invalid source {field.source}")
        
        if invalid_sources:
            passed = False
            details = invalid_sources
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_tier_distribution(self) -> Dict[str, Any]:
        """Check tier distribution is reasonable"""
        passed = True
        message = "Tier distribution"
        details = []
        warnings = 0
        
        stats = self.registry.get_stats()
        tier_dist = stats.by_tier
        
        # Check for reasonable distribution
        if tier_dist.get("free", 0) < 100:
            warnings += 1
            details.append("Warning: Less than 100 FREE tier fields")
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_display_distribution(self) -> Dict[str, Any]:
        """Check display level distribution"""
        passed = True
        message = "Display level distribution"
        details = []
        warnings = 0
        
        stats = self.registry.get_stats()
        display_dist = stats.by_display
        
        # Check for reasonable distribution
        if display_dist.get("simple", 0) < 20:
            warnings += 1
            details.append("Warning: Less than 20 SIMPLE display fields")
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_validation_rules(self) -> Dict[str, Any]:
        """Check validation rules are properly formatted"""
        passed = True
        message = "Validation rules"
        details = []
        warnings = 0
        
        rule_issues = []
        
        for field_name, field in self.registry.get_all_fields().items():
            for rule in field.validation_rules:
                if not rule.message:
                    rule_issues.append(f"{field_name}: validation rule without message")
                if not rule.value and rule.value != 0:
                    rule_issues.append(f"{field_name}: validation rule without value")
        
        if rule_issues:
            passed = False
            details = rule_issues[:10]
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_extension_coverage(self) -> Dict[str, Any]:
        """Check extension coverage"""
        passed = True
        message = "Extension coverage"
        details = []
        warnings = 0
        
        # Check fields have extension compatibility
        fields_without_extensions = []
        for field_name, field in self.registry.get_all_fields().items():
            if not field.compatible_extensions:
                fields_without_extensions.append(field_name)
        
        if fields_without_extensions:
            warnings += 1
            details.append(
                f"{len(fields_without_extensions)} fields without extension compatibility"
            )
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_for_deprecated_fields(self) -> Dict[str, Any]:
        """Check deprecated fields have proper info"""
        passed = True
        message = "Deprecated fields"
        details = []
        warnings = 0
        
        deprecation_issues = []
        
        for field_name, field in self.registry.get_all_fields().items():
            if field.is_deprecated:
                if not field.deprecation:
                    deprecation_issues.append(
                        f"{field_name}: marked deprecated but no deprecation info"
                    )
                elif not field.deprecation.alternative_field:
                    deprecation_issues.append(
                        f"{field_name}: deprecated without alternative field"
                    )
        
        if deprecation_issues:
            passed = False
            details = deprecation_issues
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_related_fields(self) -> Dict[str, Any]:
        """Check related fields exist"""
        passed = True
        message = "Related fields consistency"
        details = []
        warnings = 0
        
        missing_relations = []
        
        for field_name, field in self.registry.get_all_fields().items():
            for related in field.metadata.related_fields:
                if not self.registry.get_field(related):
                    missing_relations.append(
                        f"{field_name}: references non-existent field {related}"
                    )
        
        if missing_relations:
            passed = False
            details = missing_relations[:10]
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_metadata_completeness(self) -> Dict[str, Any]:
        """Check metadata completeness"""
        passed = True
        message = "Metadata completeness"
        details = []
        warnings = 0
        
        incomplete_count = 0
        
        for field_name, field in self.registry.get_all_fields().items():
            if not field.metadata.search_keywords:
                incomplete_count += 1
        
        if incomplete_count > len(self.registry) * 0.5:
            warnings += 1
            details.append(
                f"Warning: {incomplete_count} fields ({round(incomplete_count/len(self.registry)*100)}%) "
                "have no search keywords"
            )
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_duplicate_fields(self) -> Dict[str, Any]:
        """Check for duplicate field definitions"""
        passed = True
        message = "Duplicate field check"
        details = []
        warnings = 0
        
        # Check by name
        names = list(self.registry.get_all_fields().keys())
        if len(names) != len(set(names)):
            passed = False
            details.append("Duplicate field names detected")
        
        # Check by standard_name
        standard_names = {}
        for field_name, field in self.registry.get_all_fields().items():
            std_name = field.standard_name
            if std_name in standard_names:
                if standard_names[std_name] != field_name:
                    details.append(
                        f"Fields {standard_names[std_name]} and {field_name} "
                        f"have same standard_name: {std_name}"
                    )
            else:
                standard_names[std_name] = field_name
        
        if details:
            passed = False
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def _check_index_consistency(self) -> Dict[str, Any]:
        """Check index consistency"""
        passed = True
        message = "Index consistency"
        details = []
        warnings = 0
        
        index_issues = []
        
        all_fields = set(self.registry.get_all_field_names())
        
        # Check that indexes don't have fields not in registry
        for index_name in ["by_source", "by_type", "by_tier", "by_display"]:
            index = self.registry._indexes.get(index_name, {})
            for key, fields in index.items():
                indexed_fields = set(fields.keys())
                missing = indexed_fields - all_fields
                if missing:
                    index_issues.append(
                        f"Index '{index_name}[{key}]' contains unknown fields: {missing}"
                    )
        
        if index_issues:
            passed = False
            details = index_issues[:10]
        
        return {"passed": passed, "message": message, "details": details, "warnings": warnings}
    
    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        if not self.validation_results:
            results = self.run_all_checks()
        else:
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "checks": self.validation_results
            }
        
        lines = [
            "=" * 60,
            "FIELD REGISTRY VALIDATION REPORT",
            "=" * 60,
            "",
            f"Generated: {results.get('timestamp', 'N/A')}",
            "",
            "-" * 40,
            "SUMMARY",
            "-" * 40,
        ]
        
        summary = results.get("summary", {})
        lines.extend([
            f"Total Checks:    {summary.get('total_checks', 'N/A')}",
            f"Passed:          {summary.get('passed', 'N/A')}",
            f"Failed:          {summary.get('failed', 'N/A')}",
            f"Warnings:        {summary.get('warnings', 'N/A')}",
            f"Pass Rate:       {summary.get('pass_rate', 'N/A')}%",
            "",
            "-" * 40,
            "CHECK RESULTS",
            "-" * 40,
        ])
        
        for check in results.get("checks", []):
            status = "✓ PASS" if check["passed"] else "✗ FAIL"
            lines.append(f"{status}: {check['message']}")
            
            if check.get("details"):
                for detail in check["details"][:3]:
                    lines.append(f"  - {detail}")
                if len(check["details"]) > 3:
                    lines.append(f"  - ... and {len(check['details']) - 3} more")
        
        lines.extend([
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ])
        
        return "\n".join(lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate field registry"
    )
    parser.add_argument(
        "--registry",
        help="Path to existing registry file"
    )
    parser.add_argument(
        "--output",
        help="Output path for validation report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Create registry
    registry = FieldRegistryCore()
    
    if args.registry and os.path.exists(args.registry):
        registry.load_from_disk(args.registry)
        print(f"Loaded registry from: {args.registry}")
    
    # Run validation
    validator = RegistryValidator(registry)
    results = validator.run_all_checks()
    
    # Generate report
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(validator.generate_report())
    
    # Write to file if requested
    if args.output:
        with open(args.output, "w") as f:
            if args.json:
                json.dump(results, f, indent=2)
            else:
                f.write(validator.generate_report())
        print(f"\nReport saved to: {args.output}")
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

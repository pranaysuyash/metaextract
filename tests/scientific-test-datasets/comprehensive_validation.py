#!/usr/bin/env python3
"""
Comprehensive Scientific Format Validation Suite
Tests all scientific test datasets with MetaExtract extraction modules.
Generates detailed validation reports and performance metrics.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Add server path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

# Import MetaExtract modules
from extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validating a single dataset."""
    dataset_name: str
    dataset_type: str
    file_path: str
    success: bool
    extraction_time: float
    fields_extracted: int = 0
    error_message: Optional[str] = None
    metadata_keys: List[str] = field(default_factory=list)
    validation_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FormatValidationReport:
    """Comprehensive validation report for a format type."""
    format_type: str
    total_datasets: int
    successful_extractions: int
    failed_extractions: int
    total_extraction_time: float
    average_extraction_time: float
    total_fields_extracted: int
    average_fields_per_dataset: float
    results: List[ValidationResult] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class ScientificFormatValidator:
    """Comprehensive validator for scientific format extraction."""

    def __init__(self, datasets_base_path: str):
        self.datasets_base_path = Path(datasets_base_path)
        self.manifest_path = self.datasets_base_path / "dataset_manifest.json"
        self.reports: Dict[str, FormatValidationReport] = {}
        # Initialize the comprehensive metadata extractor
        self.engine = ComprehensiveMetadataExtractor()

    def load_manifest(self) -> Dict[str, Any]:
        """Load the dataset manifest."""
        with open(self.manifest_path, 'r') as f:
            return json.load(f)

    def validate_dicom_dataset(self, dataset_info: Dict[str, Any]) -> ValidationResult:
        """Validate a DICOM dataset."""
        file_path = dataset_info['files'][0]
        dataset_name = list(dataset_info.keys())[0] if isinstance(dataset_info, dict) else "unknown"

        start_time = time.time()
        try:
            result = self.engine.medical_engine.extract_dicom_metadata(file_path)
            extraction_time = time.time() - start_time

            success = result.get('available', False) if result else False
            fields_extracted = 0
            if result and success:
                # Count fields in all DICOM info sections
                info_sections = ['patient_info', 'study_info', 'series_info', 'equipment_info',
                               'image_info', 'acquisition_params', 'dose_info', 'private_tags', 'raw_tags']
                for section in info_sections:
                    if section in result and isinstance(result[section], dict):
                        fields_extracted += len(result[section])
            metadata_keys = list(result.keys()) if result else []

            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type="dicom",
                file_path=file_path,
                success=success,
                extraction_time=extraction_time,
                fields_extracted=fields_extracted,
                metadata_keys=metadata_keys,
                validation_details={
                    'modality': result.get('modality', 'unknown') if result else 'unknown',
                    'manufacturer': result.get('manufacturer', 'unknown') if result else 'unknown',
                    'has_valid_dicom': result.get('available', False) if result else False
                }
            )
        except Exception as e:
            extraction_time = time.time() - start_time
            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type="dicom",
                file_path=file_path,
                success=False,
                extraction_time=extraction_time,
                error_message=str(e)
            )

    def validate_fits_dataset(self, dataset_info: Dict[str, Any]) -> ValidationResult:
        """Validate a FITS dataset."""
        file_path = dataset_info['files'][0]
        dataset_name = list(dataset_info.keys())[0] if isinstance(dataset_info, dict) else "unknown"

        start_time = time.time()
        try:
            result = self.engine.astronomical_engine.extract_fits_metadata(file_path)
            extraction_time = time.time() - start_time

            success = result.get('available', False) if result else False
            # Count fields in various FITS metadata sections
            fields_extracted = 0
            if result:
                if result.get('primary_header'):
                    fields_extracted += len(result['primary_header'])
                if result.get('wcs_info'):
                    fields_extracted += len(result['wcs_info'])
                if result.get('observation_info'):
                    fields_extracted += len(result['observation_info'])
                if result.get('raw_headers'):
                    # Count all header keywords
                    for hdu_headers in result['raw_headers'].values():
                        if isinstance(hdu_headers, dict):
                            fields_extracted += len(hdu_headers)

            metadata_keys = list(result.keys()) if result else []

            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type="fits",
                file_path=file_path,
                success=success,
                extraction_time=extraction_time,
                fields_extracted=fields_extracted,
                metadata_keys=metadata_keys,
                validation_details={
                    'format_detected': result.get('available', False) if result else False,
                    'has_wcs': bool(result.get('wcs_info', {})) if result else False,
                    'telescope': result.get('primary_header', {}).get('telescope', 'unknown') if result else 'unknown',
                    'num_hdus': result.get('file_info', {}).get('num_hdus', 0) if result else 0
                }
            )
        except Exception as e:
            extraction_time = time.time() - start_time
            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type="fits",
                file_path=file_path,
                success=False,
                extraction_time=extraction_time,
                error_message=str(e)
            )

    def validate_hdf5_netcdf_dataset(self, dataset_info: Dict[str, Any]) -> ValidationResult:
        """Validate HDF5 or NetCDF dataset."""
        file_path = dataset_info['files'][0]
        dataset_name = list(dataset_info.keys())[0] if isinstance(dataset_info, dict) else "unknown"
        dataset_type = dataset_info.get('type', 'unknown')

        start_time = time.time()
        try:
            if dataset_type == 'hdf5':
                result = self.engine.scientific_engine.extract_hdf5_metadata(file_path)
            elif dataset_type == 'netcdf':
                result = self.engine.scientific_engine.extract_netcdf_metadata(file_path)
            else:
                raise ValueError(f"Unknown dataset type: {dataset_type}")

            extraction_time = time.time() - start_time

            success = result.get('available', False) if result else False
            fields_extracted = 0

            if success and result:
                # Count various metadata fields
                if 'datasets' in result:
                    fields_extracted += len(result['datasets'])
                if 'variables' in result:
                    fields_extracted += len(result['variables'])
                if 'dimensions' in result:
                    fields_extracted += len(result['dimensions'])
                if 'global_attributes' in result:
                    fields_extracted += len(result['global_attributes'])
                if 'attributes' in result:
                    fields_extracted += len(result['attributes'])

            metadata_keys = list(result.keys()) if result else []

            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type=dataset_type,
                file_path=file_path,
                success=success,
                extraction_time=extraction_time,
                fields_extracted=fields_extracted,
                metadata_keys=metadata_keys,
                validation_details={
                    'file_format': result.get('file_info', {}).get('format', 'unknown') if result else 'unknown',
                    'num_datasets': len(result.get('datasets', {})) if result else 0,
                    'num_variables': len(result.get('variables', {})) if result else 0,
                    'num_dimensions': len(result.get('dimensions', {})) if result else 0
                }
            )
        except Exception as e:
            extraction_time = time.time() - start_time
            return ValidationResult(
                dataset_name=dataset_name,
                dataset_type=dataset_type,
                file_path=file_path,
                success=False,
                extraction_time=extraction_time,
                error_message=str(e)
            )

    def validate_format(self, format_type: str, datasets: Dict[str, Any]) -> FormatValidationReport:
        """Validate all datasets of a specific format."""
        logger.info(f"Validating {format_type} format with {len(datasets)} datasets")

        results = []
        total_time = 0.0
        successful = 0
        total_fields = 0

        for dataset_name, dataset_info in datasets.items():
            logger.info(f"  Testing {dataset_name}...")

            if format_type == 'dicom':
                result = self.validate_dicom_dataset(dataset_info)
            elif format_type == 'fits':
                result = self.validate_fits_dataset(dataset_info)
            elif format_type == 'hdf5_netcdf':
                result = self.validate_hdf5_netcdf_dataset(dataset_info)
            else:
                logger.warning(f"Unknown format type: {format_type}")
                continue

            results.append(result)
            total_time += result.extraction_time
            total_fields += result.fields_extracted

            if result.success:
                successful += 1
                logger.info(f"    ✅ SUCCESS - {result.extraction_time:.3f}s, {result.fields_extracted} fields")
            else:
                logger.error(f"    ❌ FAILED - {result.error_message}")

        # Calculate metrics
        avg_time = total_time / len(results) if results else 0
        avg_fields = total_fields / len(results) if results else 0

        report = FormatValidationReport(
            format_type=format_type,
            total_datasets=len(datasets),
            successful_extractions=successful,
            failed_extractions=len(datasets) - successful,
            total_extraction_time=total_time,
            average_extraction_time=avg_time,
            total_fields_extracted=total_fields,
            average_fields_per_dataset=avg_fields,
            results=results,
            performance_metrics={
                'success_rate': successful / len(datasets) * 100 if datasets else 0,
                'fastest_extraction': min((r.extraction_time for r in results), default=0),
                'slowest_extraction': max((r.extraction_time for r in results), default=0),
                'median_extraction_time': sorted([r.extraction_time for r in results])[len(results)//2] if results else 0
            }
        )

        self.reports[format_type] = report
        return report

    def run_comprehensive_validation(self) -> Dict[str, FormatValidationReport]:
        """Run validation on all scientific formats."""
        logger.info("Starting comprehensive scientific format validation...")

        manifest = self.load_manifest()
        datasets = manifest.get('datasets', {})

        # Validate each format
        for format_type in ['dicom', 'fits', 'hdf5_netcdf']:
            if format_type in datasets:
                self.validate_format(format_type, datasets[format_type])

        return self.reports

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        total_datasets = sum(report.total_datasets for report in self.reports.values())
        total_successful = sum(report.successful_extractions for report in self.reports.values())
        total_time = sum(report.total_extraction_time for report in self.reports.values())
        total_fields = sum(report.total_fields_extracted for report in self.reports.values())

        return {
            'validation_timestamp': datetime.now().isoformat(),
            'total_datasets_tested': total_datasets,
            'overall_success_rate': total_successful / total_datasets * 100 if total_datasets > 0 else 0,
            'total_extraction_time': total_time,
            'average_extraction_time_per_dataset': total_time / total_datasets if total_datasets > 0 else 0,
            'total_fields_extracted': total_fields,
            'average_fields_per_dataset': total_fields / total_datasets if total_datasets > 0 else 0,
            'format_reports': {
                format_type: {
                    'success_rate': report.performance_metrics['success_rate'],
                    'average_time': report.average_extraction_time,
                    'total_fields': report.total_fields_extracted,
                    'datasets_tested': report.total_datasets
                }
                for format_type, report in self.reports.items()
            },
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        for format_type, report in self.reports.items():
            success_rate = report.performance_metrics['success_rate']

            if success_rate < 80:
                recommendations.append(f"CRITICAL: {format_type} format has low success rate ({success_rate:.1f}%). Requires immediate attention.")
            elif success_rate < 95:
                recommendations.append(f"WARNING: {format_type} format success rate ({success_rate:.1f}%) could be improved.")

            if report.average_extraction_time > 5.0:
                recommendations.append(f"PERFORMANCE: {format_type} extraction is slow ({report.average_extraction_time:.2f}s avg). Consider optimization.")

        if not recommendations:
            recommendations.append("EXCELLENT: All formats showing high success rates and good performance.")

        return recommendations

    def save_reports(self, output_dir: str = "validation_reports"):
        """Save detailed validation reports to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save individual format reports
        for format_type, report in self.reports.items():
            report_file = output_path / f"{format_type}_validation_report.json"
            with open(report_file, 'w') as f:
                json.dump({
                    'format_type': report.format_type,
                    'summary': {
                        'total_datasets': report.total_datasets,
                        'successful_extractions': report.successful_extractions,
                        'failed_extractions': report.failed_extractions,
                        'success_rate': report.performance_metrics['success_rate'],
                        'average_extraction_time': report.average_extraction_time,
                        'total_fields_extracted': report.total_fields_extracted
                    },
                    'performance_metrics': report.performance_metrics,
                    'results': [
                        {
                            'dataset_name': r.dataset_name,
                            'success': r.success,
                            'extraction_time': r.extraction_time,
                            'fields_extracted': r.fields_extracted,
                            'error_message': r.error_message,
                            'validation_details': r.validation_details
                        }
                        for r in report.results
                    ]
                }, f, indent=2)

        # Save summary report
        summary = self.generate_summary_report()
        summary_file = output_path / "comprehensive_validation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Validation reports saved to {output_path}")

def main():
    """Main validation function."""
    # Path to the scientific test datasets
    datasets_path = Path(__file__).parent / "scientific-test-datasets"

    if not datasets_path.exists():
        logger.error(f"Scientific test datasets not found at {datasets_path}")
        sys.exit(1)

    # Create validator and run comprehensive validation
    validator = ScientificFormatValidator(str(datasets_path))

    try:
        logger.info("🧪 Starting Comprehensive Scientific Format Validation")
        reports = validator.run_comprehensive_validation()

        # Generate and display summary
        summary = validator.generate_summary_report()

        print("\n" + "="*80)
        print("📊 COMPREHENSIVE SCIENTIFIC FORMAT VALIDATION RESULTS")
        print("="*80)
        print(f"Total Datasets Tested: {summary['total_datasets_tested']}")
        print(".1f")
        print(".3f")
        print(".1f")
        print(f"Total Fields Extracted: {summary['total_fields_extracted']}")

        print("\n📈 Format-by-Format Results:")
        for fmt, data in summary['format_reports'].items():
            print(f"  {fmt.upper()}: {data['success_rate']:.1f}% success, {data['average_time']:.3f}s avg, {data['total_fields']} fields")

        print("\n💡 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")

        # Save detailed reports
        validator.save_reports()

        print(f"\n✅ Validation complete! Detailed reports saved to validation_reports/")

        # Exit with appropriate code
        success_rate = summary['overall_success_rate']
        if success_rate >= 95:
            print("🎉 EXCELLENT: All scientific formats validated successfully!")
            sys.exit(0)
        elif success_rate >= 80:
            print("⚠️  GOOD: Most formats working well, minor issues to address")
            sys.exit(1)
        else:
            print("❌ CRITICAL: Major issues detected, requires immediate attention")
            sys.exit(2)

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
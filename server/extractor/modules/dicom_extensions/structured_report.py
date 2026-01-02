"""
Structured Report and Documentation DICOM Extension
Implements specialized metadata extraction for structured reports and documentation
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

from .base import (
    DICOMExtensionBase,
    safe_extract_dicom_field,
    get_dicom_file_info
)

logger = logging.getLogger(__name__)


class StructuredReportExtension(DICOMExtensionBase):
    """
    Structured Report and Documentation metadata extraction.

    Extracts specialized structured report-related DICOM tags including:
    - Structured report content and observations
    - Document titles and document information
    - Measurement and numerical values
    - Observation values and units
    - Report references and verification
    - Document series and management
    - Template and mapping information
    - Content sequences and containers
    """

    SPECIALTY = "structured_report"
    FIELD_COUNT = 65
    REFERENCE = "DICOM PS3.3 (Structured Report)"
    DESCRIPTION = "Structured Report and Documentation specialized metadata extraction"
    VERSION = "1.0.0"

    # Structured report field definitions
    REPORT_FIELDS = [
        # Report identification
        "ReportNumber",
        "ReportStatus",
        "ReportPriority",
        "ReportType",
        "ReportCategory",
        "ReportDescription",
        "ReportComments",

        # Document information
        "DocumentTitle",
        "DocumentName",
        "DocumentType",
        "DocumentSubtype",
        "DocumentClass",
        "DocumentAuthor",
        "DocumentAuthorObserver",
        "DocumentVerificationDateTime",
        "DocumentVerificationStatus",
        "DocumentLastModified",
        "DocumentVersion",

        # Observation and measurement
        "ObservationDate",
        "ObservationTime",
        "ObservationDateTime",
        "ObservationBasis",
        "ObservationCategory",
        "ObservationDescription",
        "ObservationComments",
        "ObservationUID",

        # Measurement values
        "MeasurementValue",
        "MeasurementUnits",
        "MeasurementPrecision",
        "MeasurementAccuracy",
        "MeasurementRange",
        "MeasurementMethod",
        "MeasurementAlgorithm",
        "MeasurementDevice",

        # Numeric and text values
        "NumericValue",
        "NumericValueQualifier",
        "TextValue",
        "CodeValue",
        "CodeMeaning",
        "CodingSchemeDesignator",
        "CodingSchemeVersion",

        # Content sequences
        "ContentSequence",
        "ContentLabel",
        "ContentDescription",
        "ContentCreatorName",
        "ContentType",
        "ContentTemplateSequence",
        "ContentTemplateIdentifier",
        "ContentTemplateType",
        "ContentTemplateDescription",
        "ContentTemplateModifier",

        # Observation context
        "ObservationContext",
        "ObservationSubjectClass",
        "ObservationSubjectType",
        "ObservationSubjectContext",
        "ObserverType",
        "ObserverContext",

        # Document references
        "ReferencedRequestSequence",
        "ReferencedStudySequence",
        "ReferencedSeriesSequence",
        "ReferencedInstanceSequence",
        "ReferencedSOPClassUID",
        "ReferencedSOPInstanceUID",
        "ReferencedFrameNumber",

        # Current and previous observations
        "CurrentObserver",
        "CurrentObservationValue",
        "PreviousObservationValue",
        "ObservationChange",
        "ObservationTrend",

        # Procedure and protocol
        "ProcedureCodeSequence",
        "ProtocolCodeSequence",
        "ReasonForPerformedProcedureCodeSequence",
        "RequestedProcedureCodeSequence",
        "ScheduledProcedureCodeSequence",

        # Findings and conclusions
        "FindingsSequence",
        "FindingsText",
        "FindingsCodeSequence",
        "ConclusionText",
        "ConclusionCodeSequence",
        "RecommendationText",
        "RecommendationCodeSequence",
        "Impressions",
        "DiagnosisDescription",

        # Imaging measurements
        "ImagingMeasurement",
        "ImagingMeasurementSequence",
        "RealWorldValueMappingSequence",
        "RealWorldValueFirstValueMapped",
        "RealWorldValueLastValueMapped",
        "RealWorldValueIntercept",
        "RealWorldValueSlope",

        # Verification and approval
        "VerificationDateTime",
        "VerificationStatus",
        "VerifierName",
        "VerifierOrganization",
        "PredecessorDocumentsSequence",
        "ParentDocument",

        # Language and encoding
        "Language",
        "CountryOfLanguage",
        "SpecificCharacterSet",
        "Encoding",

        # Report management
        "DocumentStatus",
        "DocumentConfidentiality",
        "DocumentAvailability",
        "DocumentStorageClass",
        "DocumentRetrievalPriority",

        # Additional report parameters
        "ReportProductionStatus",
        "ReportPublicationDate",
        "ReportDistributionStatus",
        "ReportTrackingIdentifier",
        "ReportVersion",
        "ReportUpdateReason",

        # Quality and completeness
        "ReportCompleteness",
        "ReportQuality",
        "ReportAccuracy",
        "ReportReliability",

        # Reference and related documents
        "ReferencedDocumentsSequence",
        "RelatedDocumentsSequence",
        "AttachedDocumentsSequence",

        # Report template and mapping
        "TemplateIdentifier",
        "TemplateVersion",
        "TemplateType",
        "TemplateDescription",
        "MappingResource",
        "MappingResourceName",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of structured report-specific DICOM field names"""
        return self.REPORT_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract structured report-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing structured report metadata extraction results
        """
        start_time = time.time()
        errors = []
        warnings = []
        metadata = {}

        try:
            import pydicom

            # Validate and read DICOM file
            if not self.validate_dicom_file(filepath):
                return {
                    "specialty": self.SPECIALTY,
                    "source_file": filepath,
                    "fields_extracted": 0,
                    "metadata": {},
                    "extraction_time": time.time() - start_time,
                    "errors": ["Invalid DICOM file"],
                    "warnings": warnings
                }

            dcm = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)

            # Extract basic file info
            file_info = get_dicom_file_info(filepath)
            if "error" not in file_info:
                metadata["file_info"] = file_info

            # Detect if this is a structured report
            modality = safe_extract_dicom_field(dcm, "Modality", "")
            series_desc = safe_extract_dicom_field(dcm, "SeriesDescription", "").lower()
            study_desc = safe_extract_dicom_field(dcm, "StudyDescription", "").lower()

            is_report = (
                "sr" in modality.lower() or
                "report" in series_desc or "report" in study_desc or
                "document" in series_desc or "document" in study_desc or
                "conclusion" in series_desc or "findings" in study_desc or
                "ContentSequence" in dcm or
                modality == "SR"
            )

            metadata["is_structured_report"] = is_report
            metadata["modality"] = modality

            # Extract structured report-specific fields
            fields_extracted = 0

            for field in self.REPORT_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add document information analysis if available
            if "DocumentTitle" in metadata or "DocumentType" in metadata:
                document_params = self._extract_document_parameters(dcm)
                metadata.update(document_params)
                fields_extracted += len(document_params)

            # Add observation analysis if available
            if "ObservationDateTime" in metadata or "ObservationDescription" in metadata:
                observation_params = self._extract_observation_parameters(dcm)
                metadata.update(observation_params)
                fields_extracted += len(observation_params)

            # Add measurement analysis if available
            if "MeasurementValue" in metadata or "NumericValue" in metadata:
                measurement_params = self._extract_measurement_parameters(dcm)
                metadata.update(measurement_params)
                fields_extracted += len(measurement_params)

            # Add content analysis if available
            if "ContentSequence" in metadata or "ContentLabel" in metadata:
                content_params = self._extract_content_parameters(dcm)
                metadata.update(content_params)
                fields_extracted += len(content_params)

            # Add findings and conclusions if available
            if "FindingsSequence" in metadata or "ConclusionText" in metadata:
                findings_params = self._extract_findings_parameters(dcm)
                metadata.update(findings_params)
                fields_extracted += len(findings_params)

            # Add warnings if this doesn't appear to be a structured report
            if not is_report:
                warnings.append(
                    "This file may not be a structured report/document. "
                    "Consider using a different DICOM extension."
                )

            result = {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": fields_extracted,
                "metadata": metadata,
                "extraction_time": time.time() - start_time,
                "errors": errors,
                "warnings": warnings
            }

            # Log extraction summary
            self.log_extraction_summary(result)

            return result

        except Exception as e:
            logger.error(f"Structured report extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_document_parameters(self, dcm) -> Dict[str, Any]:
        """Extract document information parameters"""
        params = {}

        # Document fields
        document_fields = [
            "DocumentTitle",
            "DocumentName",
            "DocumentType",
            "DocumentClass",
            "DocumentAuthor",
            "DocumentVerificationDateTime",
            "DocumentVersion",
        ]

        for field in document_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Document_{field}"] = value

        return params

    def _extract_observation_parameters(self, dcm) -> Dict[str, Any]:
        """Extract observation parameters"""
        params = {}

        # Observation fields
        observation_fields = [
            "ObservationDate",
            "ObservationDateTime",
            "ObservationCategory",
            "ObservationDescription",
            "ObservationBasis",
            "ObservationUID",
        ]

        for field in observation_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Observation_{field}"] = value

        return params

    def _extract_measurement_parameters(self, dcm) -> Dict[str, Any]:
        """Extract measurement parameters"""
        params = {}

        # Measurement fields
        measurement_fields = [
            "MeasurementValue",
            "MeasurementUnits",
            "MeasurementPrecision",
            "MeasurementMethod",
            "NumericValue",
            "NumericValueQualifier",
        ]

        for field in measurement_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Measurement_{field}"] = value

        return params

    def _extract_content_parameters(self, dcm) -> Dict[str, Any]:
        """Extract content sequence parameters"""
        params = {}

        # Content fields
        content_fields = [
            "ContentSequence",
            "ContentLabel",
            "ContentDescription",
            "ContentCreatorName",
            "ContentTemplateIdentifier",
            "ContentTemplateType",
        ]

        for field in content_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Content_{field}"] = value

        return params

    def _extract_findings_parameters(self, dcm) -> Dict[str, Any]:
        """Extract findings and conclusions parameters"""
        params = {}

        # Findings fields
        findings_fields = [
            "FindingsSequence",
            "FindingsText",
            "ConclusionText",
            "RecommendationText",
            "Impressions",
            "DiagnosisDescription",
        ]

        for field in findings_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Findings_{field}"] = value

        return params

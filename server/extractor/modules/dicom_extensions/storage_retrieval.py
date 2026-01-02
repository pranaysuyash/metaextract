"""
Storage and Retrieval DICOM Extension
Implements specialized metadata extraction for storage, retrieval and archival operations
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


class StorageRetrievalExtension(DICOMExtensionBase):
    """
    Storage and Retrieval metadata extraction.

    Extracts specialized storage-related DICOM tags including:
    - Storage and file format information
    - Compression and encoding parameters
    - Media storage and transfer specifications
    - Network and communication data
    - Archive and retrieval sequences
    - Privacy and security attributes
    - Quality control and integrity checks
    """

    SPECIALTY = "storage_retrieval"
    FIELD_COUNT = 96
    REFERENCE = "DICOM PS3.3 (Storage)"
    DESCRIPTION = "Storage and Retrieval specialized metadata extraction"
    VERSION = "1.0.0"

    # Storage and retrieval field definitions
    STORAGE_FIELDS = [
        # File format information
        "FileMetaInformationGroupLength",
        "FileMetaInformationVersion",
        "MediaStorageSOPClassUID",
        "MediaStorageSOPInstanceUID",
        "TransferSyntaxUID",
        "ImplementationClassUID",
        "ImplementationVersionName",
        "SourceApplicationEntityTitle",
        "SendingApplicationEntityTitle",
        "ReceivingApplicationEntityTitle",

        # File compression and encoding
        "LossyImageCompression",
        "LossyImageCompressionRatio",
        "LossyImageCompressionMethod",
        "DerivationDescription",
        "DerivationCodeSequence",
        "PixelRepresentation",
        "BitsAllocated",
        "BitsStored",
        "HighBit",
        "PixelAspectRatio",
        "PixelSpacing",

        # Image pixel data
        "PixelData",
        "NumberOfFrames",
        "FrameIncrementPointer",
        "PixelDataProviderURL",
        "WaveformData",

        # Transfer syntax specifications
        "TransferSyntaxUID",
        "TransferSyntaxName",
        "TransferSyntaxVersion",
        "CompressionAlgorithm",
        "CompressionFactor",
        "CompressedPixelData",

        # Media storage information
        "MediaStorageSOPClassUID",
        "MediaStorageSOPInstanceUID",
        "MediaStorageDeviceID",
        "MediaStorageLocation",
        "MediaStorageSequence",
        "MediaType",
        "MediaDensity",

        # Application entity information
        "StationName",
        "InstitutionName",
        "InstitutionAddress",
        "InstitutionalDepartmentName",
        "PerformingPhysicianName",
        "ReferringPhysicianName",
        "ReadingPhysicianName",
        "PhysiciansOfRecord",
        "NameOfPhysiciansReadingStudy",
        "OperatorName",

        # Network and communication
        "NetworkID",
        "StationAE",
        "HostSystem",
        "Manufacturer",
        "ManufacturerModelName",
        "DeviceSerialNumber",
        "SoftwareVersions",
        "DeviceDescription",
        "DeviceUID",

        # Study and series identification
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "SOPInstanceUID",
        "SOPClassUID",
        "InstanceNumber",
        "SeriesNumber",
        "SeriesDate",
        "SeriesTime",
        "StudyDate",
        "StudyTime",
        "AccessionNumber",
        "StudyID",
        "FrameOfReferenceUID",

        # Archive information
        "ArchiveStatus",
        "ArchiveDate",
        "ArchiveTime",
        "ArchiveBy",
        "RetrievalDate",
        "RetrievalTime",
        "RetrievalMethod",
        "StorageMediaFileSetUID",
        "StorageMediaFileSetID",
        "ReferencedSOPSequence",

        # Privacy and security
        "PatientID",
        "PatientName",
        "PatientBirthDate",
        "PatientSex",
        "PatientAddress",
        "PatientTelecomInformation",
        "PatientReligiousPreference",
        "PatientSpeciesDescription",
        "PatientBreedDescription",
        "ResponsiblePerson",
        "ResponsiblePersonRole",
        "PatientComments",
        "PatientState",
        "PatientInsurancePlanCodeSequence",

        # Quality control
        "QualityControlSubject",
        "QualityControlImage",
        "QualityControlReason",
        "ImagePresentationComments",
        "PresentationLUTSequence",
        "PresentationLUTShape",
        "PresentationStateSequence",

        # Data integrity and verification
        "DataElementTag",
        "DataElementLength",
        "DataElementValue",
        "DataSetTrailingPadding",
        "Checksum",
        "DigitalSignatureUID",
        "DigitalSignatureSequence",
        "MAC",
        "MACParametersSequence",
        "CertifiedTimestamp",
        "CertifiedTimestampType",

        # Storage commitment
        "StorageCommitmentUID",
        "StorageCommitmentSequence",
        "ReferencedSOPInstanceUID",
        "ReferencedSOPClassUID",
        "StorageCommitmentResult",
        "StorageCommitmentReason",

        # Application confidentiality
        "OriginalAttributesSequence",
        "CodingSchemeIdentificationSequence",
        "AnatomicRegionSequence",
        "PrimaryAnatomicStructureSequence",

        # De-identification and privacy
        "DeidentificationMethod",
        "DeidentificationMethodCodeSequence",
        "CertifiedDataType",
        "CertifiedDate",
        "TrialRegistryNumber",

        # Storage timestamps
        "ContentDate",
        "ContentTime",
        "AcquisitionDateTime",
        "CreationDate",
        "CreationTime",
        "LastModifiedDate",
        "LastModifiedTime",

        # File system and media
        "Filename",
        "Filepath",
        "FileSize",
        "FileFormat",
        "DirectoryRecordType",
        "OffsetOfTheNextDirectoryRecord",
        "OffsetOfReferencedLowerLevelDirectoryEntity",
        "DirectoryRecordType",

        # Performance metrics
        "StorageSpeed",
        "RetrievalSpeed",
        "CompressionTime",
        "DecompressionTime",
        "TransferRate",

        # Additional storage parameters
        "SequenceOfUltrasoundRegions",
        "RegionSpatialFormat",
        "RegionDataType",
        "RegionLocationMinX0",
        "RegionLocationMinY0",
        "RegionLocationMaxX1",
        "RegionLocationMaxY1",
        "ReferencePixelX0",
        "ReferencePixelY0",
        "PhysicalUnitsXDirection",
        "PhysicalUnitsYDirection",
        "PhysicalDeltaX",
        "PhysicalDeltaY",
    ]

    def get_field_definitions(self) -> List[str]:
        """Get list of storage-specific DICOM field names"""
        return self.STORAGE_FIELDS

    def extract_specialty_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract storage-specific metadata from DICOM file.

        Args:
            filepath: Path to DICOM file

        Returns:
            Dictionary containing storage metadata extraction results
        """
        start_time = time.time()
        errors = []
        warnings = []
        metadata = {}

        try:
            import pydicom
            import os

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

            # Add file system metadata
            try:
                metadata["filesystem_size"] = os.path.getsize(filepath)
                metadata["filesystem_path"] = filepath
                metadata["filesystem_filename"] = os.path.basename(filepath)
            except Exception as e:
                errors.append(f"Error getting filesystem info: {e}")

            # Extract storage-specific fields
            fields_extracted = 0

            for field in self.STORAGE_FIELDS:
                try:
                    value = safe_extract_dicom_field(dcm, field)
                    if value is not None:
                        metadata[field] = value
                        fields_extracted += 1
                except Exception as e:
                    errors.append(f"Error extracting {field}: {e}")

            # Add file format analysis if available
            if "TransferSyntaxUID" in metadata or "FileMetaInformationVersion" in metadata:
                format_params = self._extract_file_format_parameters(dcm)
                metadata.update(format_params)
                fields_extracted += len(format_params)

            # Add compression analysis if available
            if "LossyImageCompression" in metadata or "CompressionAlgorithm" in metadata:
                compression_params = self._extract_compression_parameters(dcm)
                metadata.update(compression_params)
                fields_extracted += len(compression_params)

            # Add privacy and security analysis if available
            if "PatientID" in metadata or "DeidentificationMethod" in metadata:
                privacy_params = self._extract_privacy_parameters(dcm)
                metadata.update(privacy_params)
                fields_extracted += len(privacy_params)

            # Add storage performance analysis if available
            if "StorageSpeed" in metadata or "TransferRate" in metadata:
                performance_params = self._extract_performance_parameters(dcm)
                metadata.update(performance_params)
                fields_extracted += len(performance_params)

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
            logger.error(f"Storage extraction failed for {filepath}: {e}")
            return {
                "specialty": self.SPECIALTY,
                "source_file": filepath,
                "fields_extracted": 0,
                "metadata": {},
                "extraction_time": time.time() - start_time,
                "errors": [f"Extraction failed: {e}"],
                "warnings": warnings
            }

    def _extract_file_format_parameters(self, dcm) -> Dict[str, Any]:
        """Extract file format parameters"""
        params = {}

        # File format fields
        format_fields = [
            "TransferSyntaxUID",
            "FileMetaInformationVersion",
            "MediaStorageSOPClassUID",
            "MediaStorageSOPInstanceUID",
            "ImplementationClassUID",
            "ImplementationVersionName",
        ]

        for field in format_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Format_{field}"] = value

        return params

    def _extract_compression_parameters(self, dcm) -> Dict[str, Any]:
        """Extract compression parameters"""
        params = {}

        # Compression fields
        compression_fields = [
            "LossyImageCompression",
            "LossyImageCompressionRatio",
            "LossyImageCompressionMethod",
            "CompressionAlgorithm",
            "CompressionFactor",
        ]

        for field in compression_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Compression_{field}"] = value

        return params

    def _extract_privacy_parameters(self, dcm) -> Dict[str, Any]:
        """Extract privacy and security parameters"""
        params = {}

        # Privacy fields
        privacy_fields = [
            "PatientID",
            "PatientName",
            "DeidentificationMethod",
            "DigitalSignatureUID",
            "MAC",
            "CertifiedTimestamp",
        ]

        for field in privacy_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Privacy_{field}"] = value

        return params

    def _extract_performance_parameters(self, dcm) -> Dict[str, Any]:
        """Extract storage performance parameters"""
        params = {}

        # Performance fields
        performance_fields = [
            "StorageSpeed",
            "RetrievalSpeed",
            "CompressionTime",
            "DecompressionTime",
            "TransferRate",
        ]

        for field in performance_fields:
            value = safe_extract_dicom_field(dcm, field)
            if value is not None:
                params[f"Performance_{field}"] = value

        return params

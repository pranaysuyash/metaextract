#!/usr/bin/env python3
"""
DICOM Medical Imaging Extractor for MetaExtract.
Extracts metadata from DICOM files used in medical imaging.
"""

import os
import sys
import json
import struct
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

DICOM_AVAILABLE = True
try:
    import pydicom
except ImportError:
    DICOM_AVAILABLE = False
    logger.warning("pydicom not available - DICOM extraction limited")


class DICOMExtractor:
    """Extract metadata from DICOM medical imaging files."""

    def __init__(self):
        self.transfer_syntaxes = {
            '1.2.840.10008.1.2': 'Implicit VR Little Endian',
            '1.2.840.10008.1.2.1': 'Explicit VR Little Endian',
            '1.2.840.10008.1.2.2': 'Explicit VR Big Endian',
            '1.2.840.10008.1.2.4.50': 'JPEG Baseline (Process 1)',
            '1.2.840.10008.1.2.4.51': 'JPEG Extended (Process 2&4)',
            '1.2.840.10008.1.2.4.57': 'JPEG Lossless (Process 14)',
            '1.2.840.10008.1.2.4.70': 'JPEG Lossless (Process 14, Selection 1)',
            '1.2.840.10008.1.2.4.80': 'JPEG-LS Lossless',
            '1.2.840.10008.1.2.4.81': 'JPEG-LS Lossy',
            '1.2.840.10008.1.2.5': 'RLE Lossless',
            '1.2.840.10008.1.2.6.1': 'RFC 2551',
            '1.2.840.10008.1.2.4.100': 'MPEG2 MP@HL',
            '1.2.840.10008.1.2.4.101': 'MPEG2 MP@ML',
            '1.2.840.10008.1.2.4.102': 'MPEG-4 Part 2 High Profile / Level 3b',
            '1.2.840.10008.1.2.4.103': 'MPEG-4 Part 2 High Profile / Level 3b',
        }

    def is_dicom_file(self, filepath: str) -> bool:
        """Check if file is a valid DICOM file."""
        try:
            with open(filepath, 'rb') as f:
                preamble = f.read(132)
                if preamble[128:132] == b'DICM':
                    return True
                f.seek(0)
                first_bytes = f.read(4)
                return first_bytes[:2] in [b'\x00\x01', b'\x01\x00']
        except:
            return False

    def parse_dicom_preamble(self, filepath: str) -> Dict[str, Any]:
        """Parse DICOM file without pydicom."""
        result = {
            "format": "dicom",
            "basic_info": {},
            "patient_info": {},
            "study_info": {},
            "series_info": {},
            "image_info": {},
        }

        try:
            with open(filepath, 'rb') as f:
                preamble = f.read(132)
                has_preamble = preamble[128:132] == b'DICM'
                if has_preamble:
                    f.seek(132)
                
                read_result = self._read_dicom_elements(f, has_preamble)
                result.update(read_result)

        except Exception as e:
            logger.error(f"Error parsing DICOM: {e}")
            return {"error": str(e)}

        return result

    def _read_dicom_elements(self, f, has_preamble: bool) -> Dict[str, Any]:
        """Read DICOM elements from file."""
        result = {
            "basic_info": {},
            "patient_info": {},
            "study_info": {},
            "series_info": {},
            "image_info": {},
            "private_tags": [],
        }

        patient_tags = {
            '0010,0010': 'patient_name',
            '0010,0020': 'patient_id',
            '0010,0030': 'patient_birth_date',
            '0010,0040': 'patient_sex',
            '0010,1010': 'patient_age',
            '0010,1030': 'patient_weight',
            '0010,1040': 'patient_address',
        }

        study_tags = {
            '0020,000d': 'study_instance_uid',
            '0008,0020': 'study_date',
            '0008,0030': 'study_time',
            '0008,1030': 'study_description',
            '0008,0060': 'modality',
            '0020,0010': 'study_id',
            '0008,0090': 'referring_physician',
            '0008,0080': 'institution_name',
        }

        series_tags = {
            '0020,000e': 'series_instance_uid',
            '0020,0011': 'series_number',
            '0008,103e': 'series_description',
            '0008,0060': 'modality',
            '0008,0021': 'series_date',
            '0008,0031': 'series_time',
            '0040,0253': 'performed_procedure_step_start_date',
            '0040,0241': 'performed_procedure_step_start_time',
        }

        image_tags = {
            '0028,0010': 'rows',
            '0028,0011': 'columns',
            '0028,0100': 'bits_allocated',
            '0028,0101': 'bits_stored',
            '0028,0102': 'high_bit',
            '0028,0103': 'pixel_representation',
            '0028,0002': 'samples_per_pixel',
            '0028,0004': 'photometric_interpretation',
            '0028,0030': 'pixel_spacing',
            '0018,0050': 'slice_thickness',
            '0018,0087': 'magnetic_field_strength',
            '0018,1020': 'software_versions',
            '0018,1030': 'protocol_name',
        }

        basic_tags = {
            '0008,0020': 'study_date',
            '0008,0030': 'study_time',
            '0008,0050': 'accession_number',
            '0008,0060': 'modality',
            '0008,0070': 'manufacturer',
            '0008,0080': 'institution_name',
            '0008,1090': 'manufacturer_model_name',
            '0008,1030': 'study_description',
            '0008,103e': 'series_description',
        }

        elements_read = 0
        max_elements = 100

        while elements_read < max_elements:
            try:
                tag_bytes = f.read(4)
                if len(tag_bytes) < 4:
                    break

                group = struct.unpack('>H', tag_bytes[:2])[0]
                element = struct.unpack('>H', tag_bytes[2:4])[0]
                tag = f'{group:04x},{element:04x}'

                if group == 0x0002:
                    vr = f.read(2).decode('ascii', errors='replace')
                    length = struct.unpack('>H', f.read(2))[0] if vr in ['OB', 'OW', 'UN', 'SQ'] else struct.unpack('>I', f.read(4))[0]
                else:
                    vr = 'UN'
                    length = struct.unpack('>I', f.read(4))[0]

                if length > 10000:
                    f.seek(length, 1)
                    continue

                value = f.read(length)

                if tag in basic_tags and not result["basic_info"].get(basic_tags[tag]):
                    result["basic_info"][basic_tags[tag]] = self._format_value(value, vr)
                if tag in patient_tags and not result["patient_info"].get(patient_tags[tag]):
                    result["patient_info"][patient_tags[tag]] = self._format_value(value, vr)
                if tag in study_tags and not result["study_info"].get(study_tags[tag]):
                    result["study_info"][study_tags[tag]] = self._format_value(value, vr)
                if tag in series_tags and not result["series_info"].get(series_tags[tag]):
                    result["series_info"][series_tags[tag]] = self._format_value(value, vr)
                if tag in image_tags and not result["image_info"].get(image_tags[tag]):
                    result["image_info"][image_tags[tag]] = self._format_value(value, vr)

                if group & 0xFF00 == 0x1000:
                    result["private_tags"].append(tag)

                elements_read += 1

            except Exception:
                break

        return result

    def _format_value(self, value: bytes, vr: str) -> Any:
        """Format DICOM value based on VR."""
        if vr in ['LO', 'SH', 'CS', 'PN', 'ST', 'LT', 'UT']:
            return value.rstrip(b'\x00').decode('ascii', errors='replace').strip()
        elif vr in ['US', 'SS']:
            return struct.unpack('>H', value[:2])[0] if len(value) >= 2 else None
        elif vr in ['UL', 'SL']:
            return struct.unpack('>I', value[:4])[0] if len(value) >= 4 else None
        elif vr in ['FD', 'FL']:
            return struct.unpack('>d', value[:8])[0] if len(value) >= 8 else None
        elif vr == 'DS':
            return float(value.decode('ascii', errors='replace').strip())
        elif vr == 'IS':
            return int(value.decode('ascii', errors='replace').strip())
        elif vr == 'DA':
            return value.decode('ascii', errors='replace').strip()
        elif vr == 'TM':
            return value.decode('ascii', errors='replace').strip()
        elif vr == 'DT':
            return value.decode('ascii', errors='replace').strip()
        else:
            return value.rstrip(b'\x00').decode('ascii', errors='replace').strip()

    def extract_with_pydicom(self, filepath: str) -> Dict[str, Any]:
        """Extract DICOM metadata using pydicom."""
        if not DICOM_AVAILABLE:
            return self.parse_dicom_preamble(filepath)

        try:
            ds = pydicom.dcmread(filepath)
            result = {
                "format": "dicom",
                "pydicom_available": True,
                "patient_info": {},
                "study_info": {},
                "series_info": {},
                "image_info": {},
                "device_info": {},
                "private_tags": [],
            }

            patient_fields = [
                'PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
                'PatientAge', 'PatientWeight', 'PatientAddress', 'PatientComments'
            ]
            for field in patient_fields:
                if hasattr(ds, field):
                    result["patient_info"][field] = str(getattr(ds, field))

            study_fields = [
                'StudyInstanceUID', 'StudyDate', 'StudyTime', 'StudyDescription',
                'StudyID', 'AccessionNumber', 'Modality', 'ReferringPhysicianName',
                'InstitutionName'
            ]
            for field in study_fields:
                if hasattr(ds, field):
                    result["study_info"][field] = str(getattr(ds, field))

            series_fields = [
                'SeriesInstanceUID', 'SeriesNumber', 'SeriesDescription',
                'SeriesDate', 'SeriesTime', 'Modality'
            ]
            for field in series_fields:
                if hasattr(ds, field):
                    result["series_info"][field] = str(getattr(ds, field))

            image_fields = [
                'Rows', 'Columns', 'BitsAllocated', 'BitsStored', 'HighBit',
                'PixelRepresentation', 'SamplesPerPixel', 'PhotometricInterpretation',
                'PixelSpacing', 'SliceThickness', 'PixelSpacing'
            ]
            for field in image_fields:
                if hasattr(ds, field):
                    result["image_info"][field] = str(getattr(ds, field))

            device_fields = [
                'Manufacturer', 'ManufacturerModelName', 'SoftwareVersions',
                'DeviceSerialNumber', 'StationName'
            ]
            for field in device_fields:
                if hasattr(ds, field):
                    result["device_info"][field] = str(getattr(ds, field))

            if hasattr(ds, 'file_meta'):
                result["file_meta"] = {
                    "transfer_syntax": str(ds.file_meta.get('TransferSyntaxUID', '')),
                    "media_storage_sop_class": str(ds.file_meta.get('MediaStorageSOPClassUID', '')),
                    "media_storage_sop_instance": str(ds.file_meta.get('MediaStorageSOPInstanceUID', '')),
                }

            return result

        except Exception as e:
            logger.error(f"Error extracting DICOM with pydicom: {e}")
            return self.parse_dicom_preamble(filepath)

    def extract(self, filepath: str) -> Dict[str, Any]:
        """Extract DICOM metadata from a file."""
        result = {
            "source": "metaextract_dicom_extractor",
            "filepath": filepath,
            "format_detected": None,
            "extraction_success": False,
            "dicom_metadata": {},
        }

        if not os.path.exists(filepath):
            result["error"] = "File not found"
            return result

        if not self.is_dicom_file(filepath):
            result["format_detected"] = "unknown"
            result["dicom_metadata"] = {"error": "Not a valid DICOM file"}
            return result

        result["format_detected"] = "dicom"

        if DICOM_AVAILABLE:
            result["dicom_metadata"] = self.extract_with_pydicom(filepath)
        else:
            result["dicom_metadata"] = self.parse_dicom_preamble(filepath)

        result["extraction_success"] = "error" not in result["dicom_metadata"]

        return result


def extract_dicom_metadata(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract DICOM metadata."""
    extractor = DICOMExtractor()
    return extractor.extract(filepath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dicom_extractor.py <file.dcm>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_dicom_metadata(filepath)
    print(json.dumps(result, indent=2, default=str))

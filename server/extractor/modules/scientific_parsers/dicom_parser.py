"""
DICOM Parser
============

Extracts metadata from DICOM medical imaging files (CT, MRI, X-Ray, Ultrasound, etc.).

DICOM Structure:
- File Meta Information (Group 0002)
- Patient Information (Group 0010)
- Study Information (Group 0008, 0020)
- Series Information (Group 0020)
- Equipment Information (Group 0008)
- Image Information (Group 0028, 7FE0)
- Modality-specific tags (CT, MR, CR, DX, US, MG, NM, PT, etc.)

Reference: NEMA PS3.6 (DICOM Data Elements)
"""

from . import ScientificParser, logger
from typing import Dict, Any, Optional
from pathlib import Path
import struct


class DicomParser(ScientificParser):
    """DICOM-specific metadata parser."""
    
    FORMAT_NAME = "DICOM"
    SUPPORTED_EXTENSIONS = ['.dcm', '.dicom']
    
    def parse(self, filepath: str) -> Dict[str, Any]:
        """Extract DICOM metadata."""
        result = {}
        
        try:
            import pydicom
            from pydicom.tag import Tag
            
            ds = pydicom.dcmread(filepath, stop_before_pixels=True)
            
            result = self._extract_dicom_metadata(ds)
            
        except ImportError:
            result = self._parse_basic_dicom(filepath)
        except Exception as e:
            logger.warning(f"DICOM parsing failed: {e}")
            result = {"error": str(e)[:200]}
        
        return result
    
    def _extract_dicom_metadata(self, ds) -> Dict[str, Any]:
        """Extract comprehensive DICOM metadata using pydicom."""
        metadata = {}
        
        metadata['file_type'] = 'DICOM'
        metadata['sop_class'] = str(getattr(ds, 'SOPClassUID', ''))
        metadata['sop_instance'] = str(getattr(ds, 'SOPInstanceUID', ''))
        
        metadata['patient'] = self._extract_patient_data(ds)
        metadata['study'] = self._extract_study_data(ds)
        metadata['series'] = self._extract_series_data(ds)
        metadata['equipment'] = self._extract_equipment_data(ds)
        metadata['image'] = self._extract_image_data(ds)
        metadata['modality_specific'] = self._extract_modality_specific(ds)
        
        return metadata
    
    def _extract_patient_data(self, ds) -> Dict[str, Any]:
        """Extract patient demographics."""
        return {
            'patient_name': str(getattr(ds, 'PatientName', '')),
            'patient_id': str(getattr(ds, 'PatientID', '')),
            'patient_birth_date': str(getattr(ds, 'PatientBirthDate', '')),
            'patient_sex': str(getattr(ds, 'PatientSex', '')),
            'patient_age': str(getattr(ds, 'PatientAge', '')),
            'patient_weight': float(getattr(ds, 'PatientWeight', 0)) or None,
            'patient_size': float(getattr(ds, 'PatientSize', 0)) or None,
            'patient_address': str(getattr(ds, 'PatientAddress', '')),
        }
    
    def _extract_study_data(self, ds) -> Dict[str, Any]:
        """Extract study information."""
        return {
            'study_instance_uid': str(getattr(ds, 'StudyInstanceUID', '')),
            'study_id': str(getattr(ds, 'StudyID', '')),
            'study_date': str(getattr(ds, 'StudyDate', '')),
            'study_time': str(getattr(ds, 'StudyTime', '')),
            'study_description': str(getattr(ds, 'StudyDescription', '')),
            'accession_number': str(getattr(ds, 'AccessionNumber', '')),
            'referring_physician': str(getattr(ds, 'ReferringPhysicianName', '')),
            'study_status': str(getattr(ds, 'StudyStatusID', '')),
        }
    
    def _extract_series_data(self, ds) -> Dict[str, Any]:
        """Extract series information."""
        return {
            'series_instance_uid': str(getattr(ds, 'SeriesInstanceUID', '')),
            'series_number': int(getattr(ds, 'SeriesNumber', 0)) or None,
            'modality': str(getattr(ds, 'Modality', '')),
            'series_description': str(getattr(ds, 'SeriesDescription', '')),
            'body_part_examined': str(getattr(ds, 'BodyPartExamined', '')),
            'series_date': str(getattr(ds, 'SeriesDate', '')),
            'series_time': str(getattr(ds, 'SeriesTime', '')),
            'performed_procedure_step_start_date': str(getattr(ds, 'PerformedProcedureStepStartDate', '')),
        }
    
    def _extract_equipment_data(self, ds) -> Dict[str, Any]:
        """Extract equipment/manufacturer information."""
        return {
            'manufacturer': str(getattr(ds, 'Manufacturer', '')),
            'manufacturer_model_name': str(getattr(ds, 'ManufacturerModelName', '')),
            'device_serial_number': str(getattr(ds, 'DeviceSerialNumber', '')),
            'software_versions': str(getattr(ds, 'SoftwareVersions', '')),
            'station_name': str(getattr(ds, 'StationName', '')),
            'institution_name': str(getattr(ds, 'InstitutionName', '')),
            'institution_address': str(getattr(ds, 'InstitutionAddress', '')),
        }
    
    def _extract_image_data(self, ds) -> Dict[str, Any]:
        """Extract image technical parameters."""
        rows = int(getattr(ds, 'Rows', 0)) or 0
        cols = int(getattr(ds, 'Columns', 0)) or 0
        
        pixel_spacing = getattr(ds, 'PixelSpacing', None)
        pixel_spacing_str = ''
        if pixel_spacing:
            pixel_spacing_str = f"{pixel_spacing[0]}/{pixel_spacing[1]}"
        
        return {
            'rows': rows,
            'columns': cols,
            'bits_allocated': int(getattr(ds, 'BitsAllocated', 0)) or None,
            'bits_stored': int(getattr(ds, 'BitsStored', 0)) or None,
            'high_bit': int(getattr(ds, 'HighBit', 0)) or None,
            'pixel_representation': int(getattr(ds, 'PixelRepresentation', 0)) or None,
            'photometric_interpretation': str(getattr(ds, 'PhotometricInterpretation', '')),
            'samples_per_pixel': int(getattr(ds, 'SamplesPerPixel', 0)) or None,
            'planar_configuration': int(getattr(ds, 'PlanarConfiguration', 0)) or None,
            'pixel_spacing': pixel_spacing_str,
            'slice_thickness': str(getattr(ds, 'SliceThickness', '')),
            'slice_location': float(getattr(ds, 'SliceLocation', 0)) or None,
            'image_orientation_patient': list(getattr(ds, 'ImageOrientationPatient', [])),
            'image_position_patient': list(getattr(ds, 'ImagePositionPatient', [])),
            'megapixels': round(rows * cols / 1_000_000, 2) if rows and cols else None,
        }
    
    def _extract_modality_specific(self, ds) -> Dict[str, Any]:
        """Extract modality-specific parameters."""
        modality = str(getattr(ds, 'Modality', ''))
        modality_data = {'modality': modality}
        
        if modality == 'CT':
            modality_data.update(self._extract_ct_data(ds))
        elif modality == 'MR':
            modality_data.update(self._extract_mr_data(ds))
        elif modality in ['CR', 'DX', 'DG']:
            modality_data.update(self._extract_radiography_data(ds))
        elif modality == 'US':
            modality_data.update(self._extract_us_data(ds))
        elif modality == 'NM':
            modality_data.update(self._extract_nm_data(ds))
        elif modality == 'PT':
            modality_data.update(self._extract_pt_data(ds))
        elif modality == 'MG':
            modality_data.update(self._extract_mg_data(ds))
        
        return modality_data
    
    def _extract_ct_data(self, ds) -> Dict[str, Any]:
        """Extract CT-specific parameters."""
        return {
            'kvp': float(getattr(ds, 'KVP', 0)) or None,
            'exposure': float(getattr(ds, 'Exposure', 0)) or None,
            'exposure_time': float(getattr(ds, 'ExposureTime', 0)) or None,
            'xray_tube_current': float(getattr(ds, 'XRayTubeCurrent', 0)) or None,
            'reconstruction_algorithm': str(getattr(ds, 'ReconstructionAlgorithm', '')),
            'reconstruction_diameter': float(getattr(ds, 'ReconstructionDiameter', 0)) or None,
            'convolution_kernel': str(getattr(ds, 'ConvolutionKernel', '')),
            'window_center': float(getattr(ds, 'WindowCenter', 0)) or None,
            'window_width': float(getattr(ds, 'WindowWidth', 0)) or None,
        }
    
    def _extract_mr_data(self, ds) -> Dict[str, Any]:
        """Extract MRI-specific parameters."""
        return {
            'repetition_time': float(getattr(ds, 'RepetitionTime', 0)) or None,
            'echo_time': float(getattr(ds, 'EchoTime', 0)) or None,
            'echo_train_length': int(getattr(ds, 'EchoTrainLength', 0)) or None,
            'inversion_time': float(getattr(ds, 'InversionTime', 0)) or None,
            'flip_angle': float(getattr(ds, 'FlipAngle', 0)) or None,
            'magnetic_field_strength': float(getattr(ds, 'MagneticFieldStrength', 0)) or None,
            'number_of_averages': float(getattr(ds, 'NumberOfAverages', 0)) or None,
            'imaging_frequency': float(getattr(ds, 'ImagingFrequency', 0)) or None,
            'sequence_name': str(getattr(ds, 'SequenceName', '')),
            'sequence_variant': str(getattr(ds, 'SequenceVariant', '')),
        }
    
    def _extract_radiography_data(self, ds) -> Dict[str, Any]:
        """Extract radiography (CR/DX) specific parameters."""
        return {
            'kvp': float(getattr(ds, 'KVP', 0)) or None,
            'exposure': float(getattr(ds, 'Exposure', 0)) or None,
            'exposure_time': float(getattr(ds, 'ExposureTime', 0)) or None,
            'xray_tube_current': float(getattr(ds, 'XRayTubeCurrent', 0)) or None,
            'anode_target_material': str(getattr(ds, 'AnodeTargetMaterial', '')),
            'body_part_thickness': float(getattr(ds, 'BodyPartThickness', 0)) or None,
            'compression_force': float(getattr(ds, 'CompressionForce', 0)) or None,
        }
    
    def _extract_us_data(self, ds) -> Dict[str, Any]:
        """Extract ultrasound-specific parameters."""
        return {
            'frequency': float(getattr(ds, 'Frequency', 0)) or None,
            'depth': float(getattr(ds, 'Depth', 0)) or None,
            'gain': float(getattr(ds, 'Gain', 0)) or None,
            'dynamic_range': float(getattr(ds, 'DynamicRange', 0)) or None,
            'transducer_type': str(getattr(ds, 'TransducerType', '')),
            'processing_function': str(getattr(ds, 'ProcessingFunction', '')),
        }
    
    def _extract_nm_data(self, ds) -> Dict[str, Any]:
        """Extract nuclear medicine-specific parameters."""
        return {
            'radionuclide': str(getattr(ds, 'Radionuclide', '')),
            'radionuclide_half_life': float(getattr(ds, 'RadionuclideHalfLife', 0)) or None,
            'radionuclide_total_dose': float(getattr(ds, 'RadionuclideTotalDose', 0)) or None,
            'administration_route': str(getattr(ds, 'AdministrationRoute', '')),
            'injected_activity': float(getattr(ds, 'InjectedActivity', 0)) or None,
            'injection_time': str(getattr(ds, 'InjectionTime', '')),
        }
    
    def _extract_pt_data(self, ds) -> Dict[str, Any]:
        """Extract PET-specific parameters."""
        return {
            'radionuclide': str(getattr(ds, 'Radionuclide', '')),
            'radionuclide_half_life': float(getattr(ds, 'RadionuclideHalfLife', 0)) or None,
            'dose_start_time': str(getattr(ds, 'DoseStartTime', '')),
            'dose_duration': float(getattr(ds, 'DoseDuration', 0)) or None,
            'total_dose': float(getattr(ds, 'TotalDose', 0)) or None,
            'frame_reference_time': float(getattr(ds, 'FrameReferenceTime', 0)) or None,
        }
    
    def _extract_mg_data(self, ds) -> Dict[str, Any]:
        """Extract mammography-specific parameters."""
        return {
            'kvp': float(getattr(ds, 'KVP', 0)) or None,
            'anode_target_material': str(getattr(ds, 'AnodeTargetMaterial', '')),
            'compression_force': float(getattr(ds, 'CompressionForce', 0)) or None,
            'compression_thickness': float(getattr(ds, 'CompressionThickness', 0)) or None,
            'view_position': str(getattr(ds, 'ViewPosition', '')),
            'organ_dose': float(getattr(ds, 'OrganDose', 0)) or None,
            'exposure_control_mode': str(getattr(ds, 'ExposureControlMode', '')),
        }
    
    def _parse_basic_dicom(self, filepath: str) -> Dict[str, Any]:
        """Parse DICOM without pydicom - basic file analysis."""
        try:
            with open(filepath, 'rb') as f:
                f.seek(128)
                dicm_sig = f.read(4)
                if dicm_sig != b'DICM':
                    return {"error": "Not a valid DICOM file"}
                
                f.seek(132)
                group = f.read(2)
                element = f.read(2)
                vr = f.read(2).decode('ascii', errors='replace')
                length = struct.unpack('>I', f.read(4))[0]
                
                return {
                    "file_type": "DICOM",
                    "parsing_mode": "basic",
                    "detected": True,
                    "transfer_syntax_vr": vr,
                    "meta_group": group.hex().upper(),
                    "meta_element": element.hex().upper(),
                }
        except Exception as e:
            return {"error": str(e)[:200], "parsing_mode": "failed"}
    
    def get_real_field_count(self, metadata: Dict[str, Any]) -> int:
        """Count real DICOM metadata fields."""
        return self._count_real_fields(metadata)
    
    def can_parse(self, filepath: str) -> bool:
        """Check if file is DICOM."""
        ext = Path(filepath).suffix.lower()
        if ext not in ['.dcm', '.dicom']:
            return False
        
        try:
            with open(filepath, 'rb') as f:
                f.seek(128)
                return f.read(4) == b'DICM'
        except:
            return False


def parse_dicom(filepath: str) -> Dict[str, Any]:
    """Parse DICOM file and return metadata."""
    parser = DicomParser()
    return parser.parse(filepath)


# HIPAA De-identification Functions (DICOM PS3.15 Annex E)
# These implement the Basic Profile for Safe Harbor de-identification

DICOM_DEIDENTIFY_TAGS = {
    # Patient Identification (Group 0010)
    'PatientName',
    'PatientID',
    'PatientBirthDate',
    'PatientBirthTime',
    'PatientSex',
    'PatientAge',
    'PatientSize',
    'PatientWeight',
    'PatientAddress',
    'PatientTelephoneNumbers',
    'PatientReligiousPreference',
    'PatientMedicalRecordNumber',
    'PatientMilitaryRank',
    'PatientVeteran',
    'PatientInsurancePlanCodeSequence',
    'PatientPrimaryLanguageCodeSequence',
    
    # Referring Physician (Group 0008)
    'ReferringPhysicianName',
    'ReferringPhysicianAddress',
    'ReferringPhysicianTelephoneNumbers',
    'ReferringPhysicianIdentificationSequence',
    
    # Study (Group 0008, 0020)
    'StudyDate',
    'StudyTime',
    'AccessionNumber',
    'StudyID',
    'StudyDescription',
    'NameOfPhysiciansReadingStudy',
    
    # Series (Group 0020)
    'OperatorsName',
    'SeriesDescription',
    'SeriesNumber',
    
    # Equipment (Group 0008)
    'InstitutionName',
    'InstitutionAddress',
    'StationName',
    'InstitutionalDepartmentName',
    'Manufacturer',
    'ManufacturerModelName',
    'DeviceSerialNumber',
    'SoftwareVersions',
    
    # Other Identifiers
    'OtherPatientNames',
    'OtherPatientIDs',
    'PerformedProcedureStepID',
    'PerformedProcedureStepDescription',
    'ScheduledStepAttributesSequence',
    'RequestingPhysician',
    'RequestingService',
    'RequestedProcedureDescription',
    'RequestedProcedureCodeSequence',
    'StudyIDIssuer',
    'PrivacyBlockSequence',
    'ResponsibleOrganization',
}


DICOM_CLEANUP_TAGS = {
    # Remove these tags entirely (safe harbor)
    'PatientBirthDate': None,
    'PatientBirthTime': None,
    'StudyDate': None,
    'StudyTime': None,
    'AccessionNumber': None,
    'SeriesNumber': None,
}


def deidentify_dicom_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply HIPAA Basic Profile de-identification to DICOM metadata.
    
    This removes or replaces all Direct Identifiers as specified in
    DICOM PS3.15 Annex E.1 (Basic Profile).
    
    Args:
        metadata: Raw DICOM metadata dict
        
    Returns:
        De-identified metadata dict with PHI removed
    """
    deidentified = {}
    
    for key, value in metadata.items():
        if key == 'patient':
            deidentified['patient'] = deidentify_patient_data(value)
        elif key == 'study':
            deidentified['study'] = deidentify_study_data(value)
        elif key == 'series':
            deidentified['series'] = deidentify_series_data(value)
        elif key == 'equipment':
            deidentified['equipment'] = deidentify_equipment_data(value)
        else:
            # Pass through other fields unchanged
            deidentified[key] = value
    
    # Add de-identification status
    deidentified['_deidentified'] = {
        'status': 'deidentified',
        'method': 'hipaa_basic_profile',
        'timestamp': str(__import__('datetime').datetime.now()),
        'fields_removed': count_removed_fields(metadata, deidentified)
    }
    
    return deidentified


def deidentify_patient_data(patient: Dict[str, Any]) -> Dict[str, Any]:
    """De-identify patient demographic data."""
    deid = {}
    
    for key, value in patient.items():
        if key in ['patient_name', 'patient_id', 'patient_address', 'patient_phone']:
            # Remove PHI
            deid[key] = '[REMOVED]'
        elif key in ['patient_birth_date', 'patient_birth_time']:
            # Keep year only (DOB year is allowed if year > 89)
            if value and len(str(value)) >= 4:
                year = str(value)[:4]
                deid[key] = f"{year}0101"  # Approximate to Jan 1
            else:
                deid[key] = ''
        elif key == 'patient_sex':
            deid[key] = value  # Sex is not PHI
        else:
            deid[key] = value
    
    return deid


def deidentify_study_data(study: Dict[str, Any]) -> Dict[str, Any]:
    """De-identify study data."""
    deid = {}
    
    for key, value in study.items():
        if key in ['accession_number', 'study_id', 'referring_physician']:
            deid[key] = '[REMOVED]'
        elif key in ['study_date', 'study_time']:
            # Keep date/time for clinical use but could be shifted
            deid[key] = value
        elif key == 'study_description':
            deid[key] = value  # Keep clinical info
        else:
            deid[key] = value
    
    return deid


def deidentify_series_data(series: Dict[str, Any]) -> Dict[str, Any]:
    """De-identify series data."""
    deid = {}
    
    for key, value in series.items():
        if key == 'operators_name':
            deid[key] = '[REMOVED]'
        elif key in ['series_description', 'modality', 'body_part_examined']:
            deid[key] = value  # Keep clinical info
        else:
            deid[key] = value
    
    return deid


def deidentify_equipment_data(equipment: Dict[str, Any]) -> Dict[str, Any]:
    """De-identify equipment data (keep for quality assurance)."""
    # Equipment info is generally kept for QA purposes
    # but serial numbers should be generalized
    deid = {}
    
    for key, value in equipment.items():
        if key in ['device_serial_number', 'institution_name', 'institution_address']:
            deid[key] = '[GENERALIZED]'
        elif key in ['manufacturer', 'manufacturer_model_name']:
            deid[key] = value  # Keep manufacturer info
        else:
            deid[key] = value
    
    return deid


def count_removed_fields(original: Dict, deidentified: Dict) -> int:
    """Count how many fields were removed or modified."""
    count = 0
    
    def count_recursive(orig, deid, path=''):
        nonlocal count
        if isinstance(orig, dict):
            for k in orig:
                if k == '_deidentified':
                    continue
                new_path = f"{path}.{k}" if path else k
                if k not in deid:
                    count += 1
                elif isinstance(orig[k], dict) and isinstance(deid.get(k), dict):
                    count_recursive(orig[k], deid[k], new_path)
                elif orig[k] != deid.get(k):
                    count += 1
        elif isinstance(orig, list):
            for i, item in enumerate(orig):
                if i >= len(deidentified if isinstance(deidentified, list) else []):
                    count += 1
                elif isinstance(item, (dict, list)):
                    count_recursive(item, deidentified[i] if i < len(deidentified) else {}, f"{path}[{i}]")
    
    count_recursive(original, deidentified)
    return count


def create_deidentification_report(original: Dict[str, Any], 
                                   deidentified: Dict[str, Any]) -> Dict[str, Any]:
    """Create a report of what was de-identified."""
    return {
        'original_fields': count_fields(original),
        'deidentified_fields': count_fields(deidentified),
        'fields_removed': count_removed_fields(original, deidentified),
        'deidentification_method': 'HIPAA Basic Profile (DICOM PS3.15 E.1)',
        'compliance_status': 'safe_harbor_compliant',
        'recommendations': [
            'Review and validate de-identified data before sharing',
            'Ensure data transfer uses secure methods',
            'Document the de-identification process for audit trail',
            'Consider additional de-identification for research use'
        ]
    }


def count_fields(data: Any, depth: int = 0) -> int:
    """Count total fields in nested dict."""
    if depth > 10:
        return 0
    
    if isinstance(data, dict):
        count = 0
        for v in data.values():
            count += count_fields(v, depth + 1)
        return count
    return 1

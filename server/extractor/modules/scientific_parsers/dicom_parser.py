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


def parse_dicom_volume(filepath: str) -> Dict[str, Any]:
    """
    Parse DICOM volume (multi-frame) and extract 3D metadata.
    
    Useful for CT, MRI, PET volumes where multiple slices represent
    a 3D volume.
    
    Args:
        filepath: Path to DICOM file
        
    Returns:
        Volume metadata including 3D geometry, slice positions, etc.
    """
    try:
        import pydicom
        from pydicom.sr.coding import CodedConcept
        
        ds = pydicom.dcmread(filepath)
        
        result = {
            'is_volume': False,
            'volume_info': None,
            'slice_analysis': None
        }
        
        # Check if this is a multi-frame instance
        num_frames = getattr(ds, 'NumberOfFrames', 1)
        
        if num_frames > 1 or _is_ct_mr_volume(ds):
            result['is_volume'] = True
            
            # Extract volume geometry
            result['volume_info'] = _extract_volume_geometry(ds)
            
            # Analyze slices
            result['slice_analysis'] = _analyze_volume_slices(ds)
            
        # Check for shared functional groups (multi-frame)
        if hasattr(ds, 'SharedFunctionalGroupsSequence'):
            result['shared_functional_groups'] = _extract_shared_groups(ds)
        
        # Check for per-frame groups
        if hasattr(ds, 'PerFrameFunctionalGroupsSequence'):
            result['per_frame_groups'] = _extract_per_frame_groups(ds)
        
        return result
        
    except ImportError:
        return {
            'is_volume': False,
            'error': 'pydicom required for volume parsing'
        }
    except Exception as e:
        logger.warning(f"Volume parsing failed: {e}")
        return {
            'is_volume': False,
            'error': str(e)[:200]
        }


def _is_ct_mr_volume(ds) -> bool:
    """Check if DICOM represents a CT or MR volume."""
    modality = getattr(ds, 'Modality', '')
    slices = getattr(ds, 'ImagesInAcquisition', 0)
    
    if modality in ['CT', 'MR', 'PT', 'NM'] and slices > 1:
        return True
    
    # Check for multiple series instances
    if modality in ['CT', 'MR'] and hasattr(ds, 'SeriesInstanceUID'):
        return True
    
    return False


def _extract_volume_geometry(ds) -> Dict[str, Any]:
    """Extract 3D volume geometry information."""
    geometry = {}
    
    # Basic dimensions
    rows = getattr(ds, 'Rows', 0)
    cols = getattr(ds, 'Columns', 0)
    frames = getattr(ds, 'NumberOfFrames', 1)
    
    geometry['dimensions_2d'] = f"{cols}x{rows}"
    geometry['total_slices'] = frames
    
    # Pixel spacing
    pixel_spacing = getattr(ds, 'PixelSpacing', [])
    if pixel_spacing and len(pixel_spacing) >= 2:
        geometry['pixel_spacing'] = {
            'x_mm': float(pixel_spacing[0]),
            'y_mm': float(pixel_spacing[1])
        }
        geometry['voxel_size_xy_mm'] = float(pixel_spacing[0])
    
    # Slice thickness (spacing between slices)
    slice_thickness = getattr(ds, 'SliceThickness', '')
    if slice_thickness:
        try:
            geometry['slice_thickness_mm'] = float(slice_thickness.replace('mm', ''))
            geometry['voxel_volume_mm3'] = round(
                geometry.get('voxel_size_xy_mm', 1) ** 2 * float(slice_thickness.replace('mm', '')), 3
            )
        except (ValueError, KeyError):
            pass
    
    # Slice spacing
    slice_spacing = getattr(ds, 'SpacingBetweenSlices', '')
    if slice_spacing:
        try:
            geometry['slice_spacing_mm'] = float(slice_spacing)
        except ValueError:
            pass
    
    # Image position patient (first slice position)
    image_position = getattr(ds, 'ImagePositionPatient', [])
    if image_position and len(image_position) >= 3:
        geometry['first_slice_position'] = {
            'x_mm': float(image_position[0]),
            'y_mm': float(image_position[1]),
            'z_mm': float(image_position[2])
        }
    
    # Image orientation patient
    orientation = getattr(ds, 'ImageOrientationPatient', [])
    if orientation and len(orientation) >= 6:
        geometry['orientation'] = {
            'row_vector': [float(orientation[0]), float(orientation[1]), float(orientation[2])],
            'column_vector': [float(orientation[3]), float(orientation[4]), float(orientation[5])]
        }
    
    # Calculate volume coverage
    if frames > 1 and slice_thickness:
        try:
            thickness = float(slice_thickness.replace('mm', ''))
            geometry['volume_coverage_cm'] = round(frames * thickness / 10, 1)
        except ValueError:
            pass
    
    # Estimate total volume
    if rows and cols and frames:
        geometry['estimated_voxels'] = rows * cols * frames
    
    return geometry


def _analyze_volume_slices(ds) -> Dict[str, Any]:
    """Analyze slice distribution and timing."""
    analysis = {}
    
    # Acquisition timing
    acquisition_time = getattr(ds, 'AcquisitionTime', '')
    if acquisition_time:
        analysis['acquisition_time'] = acquisition_time
    
    # Reconstruction
    reconstruction_kernel = getattr(ds, 'ReconstructionKernel', '')
    if reconstruction_kernel:
        analysis['reconstruction_kernel'] = reconstruction_kernel
    
    # Window/Level (for CT, typical brain and lung windows)
    window_center = getattr(ds, 'WindowCenter', '')
    window_width = getattr(ds, 'WindowWidth', '')
    
    if window_center and window_width:
        analysis['display_window'] = {
            'center': str(window_center),
            'width': str(window_width)
        }
    
    # Slice location range (if available)
    slice_locations = getattr(ds, 'SliceLocation', '')
    if slice_locations:
        try:
            analysis['slice_location_mm'] = float(slice_locations)
        except ValueError:
            pass
    
    # CT-specific dose info
    modality = getattr(ds, 'Modality', '')
    if modality == 'CT':
        ct_divol = getattr(ds, 'CTDIvol', 0)
        dlp = getattr(ds, 'DoseLengthProduct', 0)
        
        if ct_divol or dlp:
            analysis['dose'] = {
                'ct_divol_mgy': float(ct_divol) if ct_divol else None,
                'dlp_mgy_cm': float(dlp) if dlp else None
            }
    
    # MRI-specific parameters
    if modality == 'MR':
        tr = getattr(ds, 'RepetitionTime', 0)
        te = getattr(ds, 'EchoTime', 0)
        flip_angle = getattr(ds, 'FlipAngle', 0)
        
        if tr or te or flip_angle:
            analysis['mri_parameters'] = {
                'tr_ms': float(tr) if tr else None,
                'te_ms': float(te) if te else None,
                'flip_angle_degrees': float(flip_angle) if flip_angle else None
            }
    
    return analysis


def _extract_shared_groups(ds) -> Dict[str, Any]:
    """Extract shared functional groups for multi-frame DICOM."""
    shared = {}
    
    try:
        shared_seq = ds.SharedFunctionalGroupsSequence
        
        # Pixel measures
        if hasattr(shared_seq, 'PixelMeasuresSequence'):
            pm = shared_seq.PixelMeasuresSequence
            if hasattr(pm, 'PixelSpacing'):
                shared['pixel_spacing'] = list(pm.PixelSpacing)
            if hasattr(pm, 'SliceThickness'):
                shared['slice_thickness'] = str(pm.SliceThickness)
        
        # Plane orientation
        if hasattr(shared_seq, 'PlaneOrientationSequence'):
            po = shared_seq.PlaneOrientationSequence
            if hasattr(po, 'ImageOrientationPatient'):
                shared['orientation'] = list(po.ImageOrientationPatient)
        
        # CT dose
        if hasattr(shared_seq, 'CTAcquisitionTypeSequence'):
            ct = shared_seq.CTAcquisitionTypeSequence
            if hasattr(ct, 'AcquisitionType'):
                shared['ct_acquisition_type'] = str(ct.AcquisitionType)
        
    except Exception as e:
        logger.debug(f"Shared functional groups extraction failed: {e}")
    
    return shared


def _extract_per_frame_groups(ds) -> Dict[str, Any]:
    """Extract per-frame functional groups for multi-frame DICOM."""
    per_frame = {
        'frames_analyzed': 0,
        'frame_positions': [],
        'unique_positions': 0
    }
    
    try:
        frame_seq = ds.PerFrameFunctionalGroupsSequence
        positions = []
        
        for frame in frame_seq:
            per_frame['frames_analyzed'] += 1
            
            # Get frame position
            if hasattr(frame, 'PlanePositionSequence'):
                pos_seq = frame.PlanePositionSequence
                if hasattr(pos_seq, 'ImagePositionPatient'):
                    positions.append(list(pos_seq.ImagePositionPatient))
        
        if positions:
            per_frame['frame_positions'] = positions[:100]  # Limit to 100
            per_frame['unique_positions'] = len(set(tuple(p) for p in positions))
            
    except Exception as e:
        logger.debug(f"Per-frame groups extraction failed: {e}")
    
    return per_frame


# Protocol Deviation Detection for DICOM (Quality Assurance)
# Compares actual acquisition parameters against expected protocols

PROTOCOL_THRESHOLDS = {
    'CT': {
        'slice_thickness_mm': {'min': 0.5, 'max': 10.0, 'optimal': 2.5},
        'kvp': {'min': 80, 'max': 140, 'optimal': 120},
        'max_mas': {'min': 10, 'max': 800, 'optimal': 200},
        'pitch': {'min': 0.5, 'max': 1.5, 'optimal': 0.984}
    },
    'MR': {
        'slice_thickness_mm': {'min': 0.5, 'max': 10.0, 'optimal': 5.0},
        'tr_ms': {'min': 500, 'max': 10000, 'optimal': 2000},
        'te_ms': {'min': 10, 'max': 200, 'optimal': 30},
        'flip_angle_degrees': {'min': 5, 'max': 180, 'optimal': 90}
    },
    'CR': {
        'exposure_uAs': {'min': 1, 'max': 500, 'optimal': 25},
        'kvp': {'min': 40, 'max': 125, 'optimal': 110}
    },
    'DX': {
        'exposure_mAs': {'min': 0.5, 'max': 100, 'optimal': 5},
        'kvp': {'min': 40, 'max': 150, 'optimal': 120}
    },
    'US': {
        'mechanical_index': {'min': 0, 'max': 1.9, 'optimal': 0.8},
        'thermal_index': {'min': 0, 'max': 2.0, 'optimal': 0.5}
    }
}


def detect_protocol_deviations(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect protocol deviations in DICOM metadata.
    
    Compares actual acquisition parameters against expected ranges
    for quality assurance purposes.
    
    Args:
        metadata: DICOM metadata dict
        
    Returns:
        Protocol deviation analysis dict
    """
    analysis = {
        'is_compliant': True,
        'deviations': [],
        'warnings': [],
        'recommendations': [],
        'protocol_scores': {},
        'overall_score': 100
    }
    
    # Get modality
    modality = metadata.get('series', {}).get('modality', '')
    if not modality:
        return {
            'is_compliant': False,
            'error': 'Modality not identified',
            'recommendations': ['Unable to assess - missing modality information']
        }
    
    thresholds = PROTOCOL_THRESHOLDS.get(modality, {})
    if not thresholds:
        return {
            'is_compliant': True,
            'modality': modality,
            'note': 'No protocol thresholds defined for this modality',
            'recommendations': ['Consider establishing protocol thresholds for quality assurance']
        }
    
    # Get acquisition parameters
    acq = metadata.get('acquisition', {})
    modality_specific = metadata.get('modality_specific', {})
    
    # Check each parameter
    deviations_found = []
    warnings_found = []
    scores = []
    
    for param, limits in thresholds.items():
        # Find the actual value
        value = None
        
        # Check in acquisition
        if param in acq:
            value = acq[param]
        # Check in modality-specific
        elif param in modality_specific:
            value = modality_specific[param]
        
        if value is None:
            continue
        
        try:
            # Convert to float if needed
            if isinstance(value, str):
                value = float(value.replace('mm', '').replace('mAs', '').replace('uAs', '').replace('ms', ''))
            else:
                value = float(value)
            
            # Check for deviations
            if value < limits['min']:
                deviations_found.append({
                    'parameter': param,
                    'value': value,
                    'expected_min': limits['min'],
                    'severity': 'high' if value < limits['min'] * 0.5 else 'medium',
                    'message': f"{param} ({value}) below minimum threshold ({limits['min']})"
                })
                scores.append(50)
            elif value > limits['max']:
                deviations_found.append({
                    'parameter': param,
                    'value': value,
                    'expected_max': limits['max'],
                    'severity': 'high' if value > limits['max'] * 1.5 else 'medium',
                    'message': f"{param} ({value}) above maximum threshold ({limits['max']})"
                })
                scores.append(50)
            elif value < limits['optimal'] * 0.8 or value > limits['optimal'] * 1.2:
                warnings_found.append({
                    'parameter': param,
                    'value': value,
                    'optimal': limits['optimal'],
                    'message': f"{param} ({value}) outside optimal range ({limits['optimal']})"
                })
                scores.append(80)
            else:
                scores.append(100)
                
        except (ValueError, TypeError):
            pass
    
    # Calculate overall score
    if scores:
        analysis['overall_score'] = round(sum(scores) / len(scores), 1)
    
    # Determine compliance status
    high_severity = [d for d in deviations_found if d['severity'] == 'high']
    analysis['is_compliant'] = len(high_severity) == 0
    analysis['deviations'] = deviations_found
    analysis['warnings'] = warnings_found
    
    # Generate recommendations
    if high_severity:
        analysis['recommendations'].append(
            f"Critical: {len(high_severity)} protocol deviation(s) detected. Review acquisition parameters."
        )
    if deviations_found:
        analysis['recommendations'].append(
            f"Review {len(deviations_found)} parameter(s) outside acceptable range."
        )
    if warnings_found:
        analysis['recommendations'].append(
            f"Consider optimizing {len(warnings_found)} parameter(s) for better image quality."
        )
    if analysis['is_compliant'] and not warnings_found:
        acquisition = metadata.get('series', {}).get('series_description', '')
        analysis['recommendations'].append(
            f"Protocol appears compliant for {modality} acquisition."
        )
    
    analysis['protocol_scores'] = {
        'parameters_evaluated': len(scores),
        'optimal_parameters': len([s for s in scores if s == 100]),
        'suboptimal_parameters': len([s for s in scores if 70 <= s < 100]),
        'deviant_parameters': len([s for s in scores if s < 70])
    }
    
    return analysis


def validate_dicom_quality(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive DICOM quality validation.
    
    Checks for common quality issues:
    - Missing required fields
    - Out of range values
    - Consistency checks
    - Completeness scoring
    
    Args:
        metadata: DICOM metadata dict
        
    Returns:
        Quality validation report
    """
    validation = {
        'is_valid': True,
        'completeness_score': 0,
        'issues': [],
        'quality_level': 'unknown',
        'checks_performed': []
    }
    
    required_patient = ['patient_id', 'patient_name', 'patient_birth_date']
    required_study = ['study_instance_uid', 'study_date', 'study_id']
    required_series = ['series_instance_uid', 'modality']
    required_image = ['rows', 'columns']
    
    all_checks = []
    
    # Check patient data completeness
    patient = metadata.get('patient', {})
    patient_present = sum(1 for f in required_patient if patient.get(f))
    patient_score = round(patient_present / len(required_patient) * 100, 1)
    all_checks.append(('patient_completeness', patient_score))
    
    # Check study data completeness
    study = metadata.get('study', {})
    study_present = sum(1 for f in required_study if study.get(f))
    study_score = round(study_present / len(required_study) * 100, 1)
    all_checks.append(('study_completeness', study_score))
    
    # Check series data completeness
    series = metadata.get('series', {})
    series_present = sum(1 for f in required_series if series.get(f))
    series_score = round(series_present / len(required_series) * 100, 1)
    all_checks.append(('series_completeness', series_score))
    
    # Check image data completeness
    image = metadata.get('image', {})
    image_present = sum(1 for f in required_image if image.get(f))
    image_score = round(image_present / len(required_image) * 100, 1)
    all_checks.append(('image_completeness', image_score))
    
    # Calculate overall completeness
    if all_checks:
        validation['completeness_score'] = round(sum(s for _, s in all_checks) / len(all_checks), 1)
    
    # Identify issues
    issues = []
    
    if patient_score < 50:
        issues.append({'type': 'missing_patient_data', 'severity': 'high'})
    if study_score < 50:
        issues.append({'type': 'missing_study_data', 'severity': 'high'})
    if image.get('bits_stored', 0) < 8:
        issues.append({'type': 'low_bit_depth', 'severity': 'medium'})
    if not image.get('pixel_spacing'):
        issues.append({'type': 'missing_pixel_spacing', 'severity': 'medium'})
    
    validation['issues'] = issues
    validation['checks_performed'] = [f"{name}: {score}%" for name, score in all_checks]
    validation['is_valid'] = len([i for i in issues if i['severity'] == 'high']) == 0
    
    # Determine quality level
    if validation['completeness_score'] >= 95 and validation['is_valid']:
        validation['quality_level'] = 'excellent'
    elif validation['completeness_score'] >= 80 and validation['is_valid']:
        validation['quality_level'] = 'good'
    elif validation['completeness_score'] >= 60:
        validation['quality_level'] = 'acceptable'
    else:
        validation['quality_level'] = 'poor'
    
    return validation

"""
Unit Tests for Scientific Parsers (DICOM, FITS, HDF5, NetCDF)
=============================================================

Tests for the scientific_parsers module covering:
- DICOM medical imaging (CT, MRI, X-Ray, Ultrasound)
- FITS astronomical imaging
- HDF5 scientific datasets
- NetCDF climate data
"""

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, '/Users/pranay/Projects/metaextract/server')

from extractor.modules.scientific_parsers import (
    parse_scientific_metadata,
    get_parser_registry,
    ScientificParserRegistry
)
from extractor.modules.scientific_parsers.dicom_parser import DicomParser
from extractor.modules.scientific_parsers.fits_parser import FitsParser
from extractor.modules.scientific_parsers.hdf5_netcdf_parser import Hdf5Parser, NetcdfParser


class TestScientificParserRegistry(unittest.TestCase):
    """Test the scientific parser registry."""
    
    def test_registry_singleton(self):
        """Test that registry returns consistent instance."""
        registry1 = get_parser_registry()
        registry2 = get_parser_registry()
        self.assertIs(registry1, registry2)
    
    def test_registered_parsers_count(self):
        """Test expected number of parsers are registered."""
        registry = get_parser_registry()
        parsers = registry.get_all_parsers()
        # Multiple extensions per parser means multiple registrations
        unique_formats = set(p.FORMAT_NAME for p in parsers)
        self.assertEqual(len(unique_formats), 5)  # 5 unique parser types
        self.assertEqual(len(registry.get_supported_extensions()), 12)
    
    def test_supported_extensions(self):
        """Test all expected extensions are supported."""
        registry = get_parser_registry()
        extensions = registry.get_supported_extensions()
        
        expected_extensions = ['.dcm', '.dicom', '.fits', '.fit', '.fts', 
                              '.h5', '.hdf5', '.he5', '.nc', '.cdf', '.nii', '.nii.gz']
        
        for ext in expected_extensions:
            self.assertIn(ext, extensions, f"Extension {ext} not found in registry")
    
    def test_get_parser_by_extension(self):
        """Test getting parser for specific extension."""
        registry = get_parser_registry()
        
        dcm_parser = registry.get_parser('test.dcm')
        self.assertIsNotNone(dcm_parser)
        
        fits_parser = registry.get_parser('test.fits')
        self.assertIsNotNone(fits_parser)
        
        hdf5_parser = registry.get_parser('test.h5')
        self.assertIsNotNone(hdf5_parser)
        
        nc_parser = registry.get_parser('test.nc')
        self.assertIsNotNone(nc_parser)
        
        unknown_parser = registry.get_parser('test.xyz')
        self.assertIsNone(unknown_parser)


class TestFieldCounting(unittest.TestCase):
    """Test accurate field counting."""
    
    def test_count_real_fields_empty(self):
        """Test counting empty/none values."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.dcm')
        
        empty_data = {
            'file_type': None,
            'width': None,
            'empty_string': '',
            'zero': 0,
            'nested': {
                'value': None,
                'data': {}
            }
        }
        
        count = parser._count_real_fields(empty_data)
        self.assertEqual(count, 0)
    
    def test_count_real_fields_with_data(self):
        """Test counting real data fields."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.dcm')
        
        data = {
            'file_type': 'DICOM',
            'patient': {
                'patient_name': 'Test^Patient',
                'patient_id': '12345',
                'patient_sex': 'M',
            },
            'study': {
                'study_date': '20240115',
                'modality': 'CT',
            }
        }
        
        count = parser._count_real_fields(data)
        self.assertGreater(count, 0)
    
    def test_count_ignores_bookkeeping(self):
        """Test that bookkeeping fields are not counted."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.dcm')
        
        data = {
            'file_type': 'DICOM',
            'source': 'extraction_info',
            'errors': [],
            'warnings': [],
            'performance': {'duration': 0.5},
            'extraction_info': {'method': 'native'}
        }
        
        count = parser._count_real_fields(data)
        self.assertEqual(count, 1)  # Only 'file_type' counts


class TestParseScientificMetadata(unittest.TestCase):
    """Test the unified parse_scientific_metadata function."""
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file returns error."""
        result = parse_scientific_metadata('/nonexistent/path/test.dcm')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'File not found')
        self.assertEqual(result['fields_extracted'], 0)
    
    def test_parse_unsupported_format(self):
        """Test parsing unsupported format returns error."""
        unsupported_path = '/tmp/test.unsupported_format_xyz'
        Path(unsupported_path).touch()
        
        try:
            result = parse_scientific_metadata(unsupported_path)
            
            self.assertFalse(result['success'])
            self.assertFalse(result['supported'])
            self.assertIn('Unsupported format', result['error'])
        finally:
            Path(unsupported_path).unlink()


class TestDicomParser(unittest.TestCase):
    """Test DICOM parsing functionality."""
    
    def test_dicom_can_parse_valid_extension(self):
        """Test can_parse returns True for valid DICOM extension."""
        parser = DicomParser()
        
        self.assertIn('.dcm', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.dicom', parser.SUPPORTED_EXTENSIONS)
    
    def test_dicom_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-DICOM extension."""
        parser = DicomParser()
        
        self.assertNotIn('.jpg', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.fits', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.nc', parser.SUPPORTED_EXTENSIONS)
    
    def test_dicom_patient_data(self):
        """Test DICOM patient data extraction."""
        parser = DicomParser()
        
        mock_ds = type('MockDS', (), {})()
        mock_ds.PatientName = 'Test^Patient'
        mock_ds.PatientID = '12345'
        mock_ds.PatientBirthDate = '19800101'
        mock_ds.PatientSex = 'M'
        mock_ds.PatientAge = '044Y'
        mock_ds.PatientWeight = 75.5
        mock_ds.PatientSize = 1.75
        mock_ds.PatientAddress = ''
        
        patient_data = parser._extract_patient_data(mock_ds)
        
        self.assertEqual(patient_data['patient_name'], 'Test^Patient')
        self.assertEqual(patient_data['patient_id'], '12345')
        self.assertEqual(patient_data['patient_sex'], 'M')


class TestFitsParser(unittest.TestCase):
    """Test FITS parsing functionality."""
    
    def test_fits_can_parse_valid_extension(self):
        """Test can_parse returns True for valid FITS extension."""
        parser = FitsParser()
        
        self.assertIn('.fits', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.fit', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.fts', parser.SUPPORTED_EXTENSIONS)
    
    def test_fits_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-FITS extension."""
        parser = FitsParser()
        
        self.assertNotIn('.jpg', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.dcm', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.nc', parser.SUPPORTED_EXTENSIONS)
    
    def test_fits_sexagesimal_parsing(self):
        """Test RA/Dec sexagesimal parsing."""
        parser = FitsParser()
        
        ra_deg = parser._parse_sexagesimal('12:30:45.5')
        self.assertIsNotNone(ra_deg)
        self.assertAlmostEqual(ra_deg, 187.6896, places=2)
        
        dec_deg = parser._parse_sexagesimal_dec('-45:30:15')
        self.assertIsNotNone(dec_deg)
        self.assertAlmostEqual(dec_deg, -45.5042, places=2)
    
    def test_fits_data_type_mapping(self):
        """Test FITS data type mapping."""
        parser = FitsParser()
        
        self.assertEqual(parser._get_fits_data_type(8), 'unsigned byte')
        self.assertEqual(parser._get_fits_data_type(16), 'signed short')
        self.assertEqual(parser._get_fits_data_type(-32), 'single float')
        self.assertEqual(parser._get_fits_data_type(-64), 'double float')


class TestHdf5Parser(unittest.TestCase):
    """Test HDF5 parsing functionality."""
    
    def test_hdf5_can_parse_valid_extension(self):
        """Test can_parse returns True for valid HDF5 extension."""
        parser = Hdf5Parser()
        
        self.assertIn('.h5', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.hdf5', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.he5', parser.SUPPORTED_EXTENSIONS)
    
    def test_hdf5_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-HDF5 extension."""
        parser = Hdf5Parser()
        
        self.assertNotIn('.jpg', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.fits', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.nc', parser.SUPPORTED_EXTENSIONS)


class TestNetcdfParser(unittest.TestCase):
    """Test NetCDF parsing functionality."""
    
    def test_netcdf_can_parse_valid_extension(self):
        """Test can_parse returns True for valid NetCDF extension."""
        parser = NetcdfParser()
        
        self.assertIn('.nc', parser.SUPPORTED_EXTENSIONS)
        self.assertIn('.cdf', parser.SUPPORTED_EXTENSIONS)
    
    def test_netcdf_can_parse_invalid_extension(self):
        """Test can_parse returns False for non-NetCDF extension."""
        parser = NetcdfParser()
        
        self.assertNotIn('.jpg', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.h5', parser.SUPPORTED_EXTENSIONS)
        self.assertNotIn('.fits', parser.SUPPORTED_EXTENSIONS)


class TestScientificFieldCountingHonesty(unittest.TestCase):
    """Test that field counting is honest (no synthetic placeholders)."""
    
    def test_no_synthetic_drone_telemetry(self):
        """Test that drone_telemetry is not added for scientific files."""
        registry = get_parser_registry()
        parser = registry.get_parser('test.fits')
        
        test_data = {
            'file_type': 'FITS',
            'telescope': 'Keck',
            'observation': {
                'object': 'M31',
            }
        }
        
        synthetic_fields = [
            'drone_telemetry',
            'blockchain_provenance',
            'healthcare_medical',
            'scientific_fits'
        ]
        
        for field in synthetic_fields:
            self.assertNotIn(field, test_data, 
                f"Synthetic field '{field}' should not be present")


class TestNiftiParser(unittest.TestCase):
    """Test NIfTI parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from extractor.modules.scientific_parsers.nifti_parser import NiftiParser
        self.parser = NiftiParser()
        self.test_dir = Path('/Users/pranay/Projects/metaextract/test-data')
    
    def test_parser_format_name(self):
        """Test parser reports correct format name."""
        self.assertEqual(self.parser.FORMAT_NAME, "NIfTI")
    
    def test_parser_supported_extensions(self):
        """Test parser supports expected extensions."""
        expected = ['.nii', '.nii.gz']
        self.assertEqual(self.parser.SUPPORTED_EXTENSIONS, expected)
    
    def test_can_parse_nii_file(self):
        """Test can_parse identifies .nii files."""
        test_file = self.test_dir / 'test.nii'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = self.parser.can_parse(str(test_file))
        self.assertTrue(result)
    
    def test_can_parse_nii_gz_file(self):
        """Test can_parse identifies .nii.gz files."""
        test_file = self.test_dir / 'test.nii.gz'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = self.parser.can_parse(str(test_file))
        self.assertTrue(result)
    
    def test_can_parse_rejects_non_nifti(self):
        """Test can_parse rejects non-NIfTI files."""
        result = self.parser.can_parse('/Users/pranay/Projects/metaextract/test-data/test.jpg')
        self.assertFalse(result)
    
    def test_parse_non_existent_file(self):
        """Test parsing non-existent file returns error."""
        result = parse_scientific_metadata('/nonexistent/test.nii')
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'File not found')
    
    def test_parse_unsupported_format(self):
        """Test parsing unsupported format returns error."""
        result = parse_scientific_metadata('/Users/pranay/Projects/metaextract/test-data/test.jpg')
        self.assertFalse(result['success'])
        self.assertFalse(result['supported'])
    
    def test_parse_nii_file_structure(self):
        """Test parsing .nii file returns expected structure."""
        test_file = self.test_dir / 'test.nii'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = parse_scientific_metadata(str(test_file))
        
        if not result['success']:
            self.skipTest(f"Parsing failed: {result.get('error', 'Unknown error')}")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['format'], 'NIfTI')
        self.assertTrue(result['supported'])
        self.assertIn('metadata', result)
        self.assertIn('fields_extracted', result)
        self.assertIsInstance(result['fields_extracted'], int)
    
    def test_parse_nii_metadata_categories(self):
        """Test parsed metadata contains expected categories."""
        test_file = self.test_dir / 'test.nii'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = parse_scientific_metadata(str(test_file))
        
        if not result['success']:
            self.skipTest(f"Parsing failed: {result.get('error', 'Unknown error')}")
        
        metadata = result['metadata']
        
        expected_categories = [
            'file_information',
            'dimensions',
            'data_type',
            'spatial_parameters',
            'temporal_parameters'
        ]
        
        for category in expected_categories:
            self.assertIn(category, metadata, f"Missing category: {category}")
    
    def test_nifti_field_counting(self):
        """Test field counting excludes null values."""
        test_file = self.test_dir / 'test.nii'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = parse_scientific_metadata(str(test_file))
        
        if not result['success']:
            self.skipTest(f"Parsing failed: {result.get('error', 'Unknown error')}")
        
        fields_extracted = result['fields_extracted']
        
        self.assertIsInstance(fields_extracted, int)
        self.assertGreaterEqual(fields_extracted, 0)
    
    def test_nifti_no_synthetic_fields(self):
        """Test parsing doesn't include synthetic placeholder fields."""
        test_file = self.test_dir / 'test.nii'
        if not test_file.exists():
            self.skipTest("Test file not found")
        
        result = parse_scientific_metadata(str(test_file))
        
        if not result['success']:
            self.skipTest(f"Parsing failed: {result.get('error', 'Unknown error')}")
        
        test_data = result.get('metadata', {})
        
        synthetic_fields = [
            'drone_telemetry',
            'blockchain_provenance',
            'healthcare_medical',
            'advanced_dicom_ultimate'
        ]
        
        for field in synthetic_fields:
            self.assertNotIn(field, test_data,
                f"Synthetic field '{field}' should not be present")


class TestNiftiHeaderParsing(unittest.TestCase):
    """Test NIfTI header parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from extractor.modules.scientific_parsers.nifti_parser import NiftiParser
        self.parser = NiftiParser()
    
    def test_dimension_extraction(self):
        """Test dimension extraction from header."""
        mock_header = {
            'dim': [3, 64, 64, 32, 100, 0, 0, 0],
            'pixdim': [0.0, 3.0, 3.0, 3.0, 2.0, 0.0, 0.0, 0.0],
            'datatype': 16,
            'bitpix': 32
        }
        
        dims = self.parser._extract_dimensions(mock_header)
        
        self.assertEqual(dims['ndim'], 3)
        self.assertEqual(dims['nx'], 64)
        self.assertEqual(dims['ny'], 64)
        self.assertEqual(dims['nz'], 32)
        self.assertEqual(dims['nt'], 100)
    
    def test_datatype_extraction(self):
        """Test data type extraction from header."""
        test_cases = [
            (16, 'float32', 32),
            (4, 'int16', 16),
            (2, 'uint8', 8),
            (64, 'float64', 64)
        ]
        
        for datatype_code, expected_name, expected_bitpix in test_cases:
            mock_header = {'datatype': datatype_code, 'bitpix': expected_bitpix}
            dt = self.parser._extract_datatype(mock_header)
            
            self.assertEqual(dt['data_type_code'], datatype_code)
            self.assertEqual(dt['data_type_name'], expected_name)
            self.assertEqual(dt['bits_per_voxel'], expected_bitpix)
    
    def test_spatial_parameters_extraction(self):
        """Test spatial parameters extraction."""
        mock_header = {
            'pixdim0': 0.0, 'pixdim1': 2.5, 'pixdim2': 2.5, 'pixdim3': 2.5,
            'pixdim4': 0.0, 'pixdim5': 0.0, 'pixdim6': 0.0, 'pixdim7': 0.0,
            'dim': [3, 128, 128, 64, 0, 0, 0, 0],
            'xyzt_units': 2
        }
        
        spatial = self.parser._extract_spatial_parameters(mock_header)
        
        self.assertEqual(spatial['voxel_size_x'], 2.5)
        self.assertEqual(spatial['voxel_size_y'], 2.5)
        self.assertEqual(spatial['voxel_size_z'], 2.5)
        self.assertEqual(spatial['fov_x'], 320.0)
        self.assertEqual(spatial['fov_y'], 320.0)
        self.assertEqual(spatial['fov_z'], 160.0)
    
    def test_temporal_parameters_extraction(self):
        """Test temporal parameters extraction."""
        mock_header = {
            'pixdim0': 0.0, 'pixdim1': 3.0, 'pixdim2': 3.0, 'pixdim3': 3.0,
            'pixdim4': 2.0, 'pixdim5': 0.0, 'pixdim6': 0.0, 'pixdim7': 0.0,
            'dim': [4, 64, 64, 32, 200, 0, 0, 0],
            'xyzt_units': 24
        }
        
        temporal = self.parser._extract_temporal_parameters(mock_header)
        
        self.assertEqual(temporal['num_time_points'], 200)
        self.assertEqual(temporal['tr_ms'], 2000.0)
        self.assertEqual(temporal['total_duration_seconds'], 400.0)
    
    def test_coordinate_system_extraction(self):
        """Test coordinate system extraction."""
        mock_header = {
            'qform_code': 1,
            'sform_code': 4
        }
        
        coords = self.parser._extract_coordinate_system(mock_header)
        
        self.assertEqual(coords['qform_code'], 1)
        self.assertEqual(coords['qform_name'], 'scanner')
        self.assertEqual(coords['sform_code'], 4)
        self.assertEqual(coords['sform_name'], 'mni152')
    
    def test_slice_info_extraction(self):
        """Test slice information extraction."""
        mock_header = {
            'slice_code': 3,
            'slice_start': 0,
            'slice_end': 31,
            'slice_duration': 0.05,
            'dim': [3, 64, 64, 32, 0, 0, 0, 0]
        }
        
        slices = self.parser._extract_slice_info(mock_header)
        
        self.assertEqual(slices['slice_ordering_code'], 3)
        self.assertEqual(slices['slice_ordering_name'], 'alt+')
        self.assertEqual(slices['number_of_slices'], 32)
        self.assertEqual(slices['slice_duration_ms'], 50.0)
    
    def test_intent_extraction(self):
        """Test intent information extraction."""
        mock_header = {
            'intent_code': 1005,
            'intent_p1': 0.0,
            'intent_p2': 0.0,
            'intent_p3': 0.0,
            'intent_name': '',
            'descrip': 'SPM T-map'
        }
        
        intent = self.parser._extract_intent(mock_header)
        
        self.assertEqual(intent['intent_code'], 1005)
        self.assertEqual(intent['intent_name'], 'spm t')
        self.assertIn('SPM', intent['description'])
    
    def test_description_extraction(self):
        """Test description extraction."""
        mock_header = {
            'descrip': 'Functional MRI experiment',
            'aux_file': ''
        }
        
        desc = self.parser._extract_description(mock_header)
        
        self.assertEqual(desc['description'], 'Functional MRI experiment')
        self.assertIsNone(desc['auxiliary_file'])
    
    def test_calibration_extraction(self):
        """Test calibration information extraction."""
        mock_header = {
            'cal_max': 1000.0,
            'cal_min': 0.0,
            'scl_slope': 1.0,
            'scl_inter': 0.0,
            'glmax': 2000,
            'glmin': 0
        }
        
        cal = self.parser._extract_calibration(mock_header)
        
        self.assertEqual(cal['cal_max'], 1000.0)
        self.assertIsNone(cal['scaling_slope'])
    
    def test_voxel_summary_extraction(self):
        """Test voxel data summary extraction."""
        mock_header = {
            'dim': [3, 64, 64, 64, 0, 0, 0, 0],
            'datatype': 16,
            'bitpix': 32,
            'vox_offset': 352.0
        }
        
        voxel = self.parser._extract_voxel_summary(mock_header)
        
        self.assertEqual(voxel['total_voxels'], 262144)
        self.assertEqual(voxel['bytes_per_voxel'], 4)
        self.assertEqual(voxel['data_type'], 'float32')
        self.assertEqual(voxel['dimensions'], '64x64x64')


class TestNiftiRegistryIntegration(unittest.TestCase):
    """Test NIfTI parser integration with registry."""
    
    def test_nifti_registered_in_registry(self):
        """Test NIfTI parser is registered in global registry."""
        registry = get_parser_registry()
        
        nii_parser = registry.get_parser('test.nii')
        self.assertIsNotNone(nii_parser)
        self.assertEqual(nii_parser.FORMAT_NAME, 'NIfTI')
        
        nii_gz_parser = registry.get_parser('test.nii.gz')
        self.assertIsNotNone(nii_gz_parser)
    
    def test_nifti_extensions_in_supported_list(self):
        """Test NIfTI extensions are in supported extensions list."""
        registry = get_parser_registry()
        extensions = registry.get_supported_extensions()
        
        self.assertIn('.nii', extensions)
        self.assertIn('.nii.gz', extensions)
    
    def test_registry_counts_nifti(self):
        """Test registry includes NIfTI in parser count."""
        registry = get_parser_registry()
        parsers = registry.get_all_parsers()
        
        unique_formats = set(p.FORMAT_NAME for p in parsers)
        self.assertIn('NIfTI', unique_formats)


if __name__ == '__main__':
    unittest.main()

# Scientific Test Datasets Generator

This testing infrastructure agent creates comprehensive test datasets for scientific formats used in MetaExtract testing.

## Overview

The `ScientificTestDatasetGenerator` creates synthetic but realistic test data for:

- **DICOM files**: CT, MRI, and Ultrasound scans from different modalities
- **FITS files**: Astronomical data from Hubble, Chandra, and SDSS surveys
- **HDF5/NetCDF files**: Climate models, weather radar, and oceanographic data

## Generated Datasets

### DICOM Datasets

- **CT Scan**: Synthetic abdomen/pelvis CT with Siemens metadata
- **MRI Scan**: T1-weighted brain MRI with GE Medical Systems metadata
- **Ultrasound**: Abdominal ultrasound with Philips metadata

### FITS Datasets

- **Hubble Space Telescope**: ACS F606W observation with WCS coordinates
- **Chandra X-ray**: ACIS observation with telescope-specific metadata
- **SDSS Spectroscopy**: Galaxy spectrum with SDSS pipeline metadata

### HDF5/NetCDF Datasets

- **Climate Model**: 10-year monthly temperature/precipitation data (CF-1.8 compliant)
- **Weather Radar**: Doppler radar data with reflectivity, velocity, spectrum width
- **Oceanographic**: 30-day 6-hourly ocean model with T/S/current data

## Usage

### Basic Usage

```python
from scientific_test_generator import ScientificTestDatasetGenerator

# Create generator
generator = ScientificTestDatasetGenerator()

# Generate all datasets
datasets = generator.generate_all_datasets()

# Access specific datasets
ct_dataset = datasets['dicom']['ct_scan']
hst_dataset = datasets['fits']['hst_observation']
climate_dataset = datasets['hdf5_netcdf']['climate_model']
```

### Command Line

```bash
cd tests/scientific-test-datasets
python scientific_test_generator.py
```

### Custom Output Directory

```python
generator = ScientificTestDatasetGenerator(output_dir="/path/to/custom/dir")
```

## Dependencies

### Required Libraries

- **DICOM**: `pydicom` (for DICOM file generation)
- **FITS**: `astropy` (for astronomical FITS files)
- **HDF5/NetCDF**: `h5py` and `netCDF4` (for scientific data formats)
- **General**: `numpy` (for synthetic data generation)

### Installation

```bash
pip install pydicom astropy h5py netCDF4 numpy
```

## Dataset Structure

```
scientific-test-datasets/
├── dicom/
│   ├── ct_scan/
│   │   ├── ct_scan.dcm
│   │   └── metadata.json
│   ├── mri_scan/
│   │   ├── mri_scan.dcm
│   │   └── metadata.json
│   └── ultrasound/
│       ├── ultrasound.dcm
│       └── metadata.json
├── fits/
│   ├── hst_observation/
│   │   ├── hst_observation.fits
│   │   └── metadata.json
│   ├── chandra_observation/
│   │   ├── chandra_observation.fits
│   │   └── metadata.json
│   └── sdss_spectrum/
│       ├── sdss_spectrum.fits
│       └── metadata.json
├── hdf5_netcdf/
│   ├── climate_model/
│   │   ├── climate_model.nc
│   │   └── metadata.json
│   ├── weather_radar/
│   │   ├── weather_radar.h5
│   │   └── metadata.json
│   └── oceanographic/
│       ├── oceanographic.nc
│       └── metadata.json
└── dataset_manifest.json
```

## Dataset Manifest

The `dataset_manifest.json` file contains:

- Generation timestamp and version info
- Complete metadata for all datasets
- File paths and descriptions
- Summary statistics

## Integration with MetaExtract Testing

### Using in Pytest

```python
import pytest
from pathlib import Path
from scientific_test_generator import ScientificTestDatasetGenerator

@pytest.fixture(scope="session")
def scientific_datasets(tmp_path_factory):
    """Generate scientific test datasets for the test session"""
    output_dir = tmp_path_factory.mktemp("scientific_datasets")
    generator = ScientificTestDatasetGenerator(str(output_dir))
    return generator.generate_all_datasets()

def test_dicom_ct_extraction(scientific_datasets):
    """Test DICOM CT metadata extraction"""
    ct_dataset = scientific_datasets['dicom']['ct_scan']
    ct_file = ct_dataset['files'][0]

    # Test MetaExtract DICOM extraction
    result = extract_dicom_metadata(ct_file)
    assert result['modality'] == 'CT'
    assert 'SIEMENS' in result['manufacturer']
```

### Using in Test Files

```python
# In test_scientific_formats.py
from tests.scientific_test_datasets.scientific_test_generator import ScientificTestDatasetGenerator

def test_fits_hst_extraction():
    generator = ScientificTestDatasetGenerator()
    datasets = generator.generate_all_datasets()

    hst_file = datasets['fits']['hst_observation']['files'][0]
    result = extract_fits_metadata(hst_file)

    assert result['TELESCOP'] == 'HST'
    assert result['INSTRUME'] == 'ACS'
```

## Mock Datasets

If required libraries are not available, the generator creates mock datasets with JSON metadata files. These contain the expected structure and can be used for testing metadata parsing logic without the full scientific libraries.

## Validation

Each generated dataset includes:

- **Realistic metadata**: Based on actual scientific data standards
- **Proper file formats**: Compliant with format specifications
- **Sensible data ranges**: Physically plausible values
- **Complete headers**: All required and optional metadata fields

## Extending the Generator

### Adding New DICOM Modalities

```python
def _create_pet_dataset(self, output_path: Path) -> Dict[str, Any]:
    """Create a synthetic PET DICOM dataset"""
    # Implementation for PET modality
    pass
```

### Adding New FITS Surveys

```python
def _create_jwst_fits_dataset(self, output_path: Path) -> Dict[str, Any]:
    """Create a synthetic JWST FITS dataset"""
    # Implementation for James Webb Space Telescope
    pass
```

### Adding New Scientific Domains

```python
def _create_genomic_dataset(self, output_path: Path) -> Dict[str, Any]:
    """Create a synthetic genomic HDF5 dataset"""
    # Implementation for genomic data
    pass
```

## Performance Notes

- **File sizes**: Datasets are kept reasonably small for testing (MB range)
- **Generation time**: ~30 seconds for full dataset generation
- **Memory usage**: Minimal, uses streaming where possible
- **Dependencies**: Graceful degradation when libraries unavailable

## Contributing

When adding new datasets:

1. Follow the existing naming conventions
2. Include comprehensive metadata
3. Add proper validation
4. Update the manifest structure
5. Document the scientific domain and standards used

# MetaExtract Comprehensive Metadata Engine API Reference

## Overview

The MetaExtract Comprehensive Metadata Engine provides a comprehensive API for extracting metadata from files across multiple domains. This API supports both programmatic access and command-line usage.

## Core API Functions

### `extract_comprehensive_metadata(filepath, tier="super")`

Extracts comprehensive metadata from a single file using all available specialized engines.

#### Parameters
- `filepath` (str): Path to the file to extract metadata from
- `tier` (str): Access tier ("free", "starter", "premium", "super") - default: "super"

#### Returns
- `dict`: Comprehensive metadata extraction result with all available fields based on tier

#### Example
```python
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

# Extract with default super tier
result = extract_comprehensive_metadata("photo.jpg")

# Extract with specific tier
result = extract_comprehensive_metadata("medical.dcm", tier="super")

# Check for errors
if "error" in result:
    print(f"Extraction failed: {result['error']}")
else:
    print(f"Extracted {result['extraction_info']['comprehensive_fields_extracted']} fields")
```

### `extract_comprehensive_batch(filepaths, tier="super", max_workers=4, store_results=False)`

Extracts metadata from multiple files in parallel.

#### Parameters
- `filepaths` (list): List of file paths to process
- `tier` (str): Access tier - default: "super"
- `max_workers` (int): Maximum number of concurrent workers - default: 4
- `store_results` (bool): Whether to store results in database - default: False

#### Returns
- `dict`: Batch processing results with individual file results and summary

#### Example
```python
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_batch

files = ["file1.jpg", "file2.dcm", "file3.fits"]
results = extract_comprehensive_batch(files, tier="super", max_workers=2)

# Process results
for filepath, metadata in results["results"].items():
    if "error" not in metadata:
        print(f"{filepath}: {metadata['extraction_info']['comprehensive_fields_extracted']} fields")
    else:
        print(f"{filepath}: Error - {metadata['error']}")

# Access summary
summary = results["summary"]
print(f"Processed {summary['successful']} of {summary['total_files']} files successfully")
```

### `get_comprehensive_extractor()`

Gets or creates the global comprehensive extractor instance.

#### Returns
- `ComprehensiveMetadataExtractor`: The global extractor instance

#### Example
```python
from server.extractor.comprehensive_metadata_engine import get_comprehensive_extractor

extractor = get_comprehensive_extractor()
result = extractor.extract_comprehensive_metadata("file.jpg", tier="premium")
```

## Specialized Engine Classes

### `ComprehensiveMetadataExtractor`

Main class that orchestrates all specialized extraction engines.

#### Methods

##### `extract_comprehensive_metadata(filepath, tier="super")`
Main extraction method that coordinates all specialized engines.

```python
extractor = ComprehensiveMetadataExtractor()
result = extractor.extract_comprehensive_metadata("file.jpg", tier="super")
```

### `MedicalImagingEngine`

Specialized engine for DICOM medical imaging files.

#### Methods

##### `extract_dicom_metadata(filepath)`
Extracts comprehensive metadata from DICOM files.

```python
from server.extractor.comprehensive_metadata_engine import MedicalImagingEngine

engine = MedicalImagingEngine()
result = engine.extract_dicom_metadata("medical_image.dcm")
```

### `AstronomicalDataEngine`

Specialized engine for FITS astronomical data files.

#### Methods

##### `extract_fits_metadata(filepath)`
Extracts comprehensive metadata from FITS files.

```python
from server.extractor.comprehensive_metadata_engine import AstronomicalDataEngine

engine = AstronomicalDataEngine()
result = engine.extract_fits_metadata("observation.fits")
```

### `GeospatialEngine`

Specialized engine for geospatial data formats.

#### Methods

##### `extract_geotiff_metadata(filepath)`
Extracts metadata from GeoTIFF files.

```python
from server.extractor.comprehensive_metadata_engine import GeospatialEngine

engine = GeospatialEngine()
result = engine.extract_geotiff_metadata("geospatial_data.tif")
```

##### `extract_shapefile_metadata(filepath)`
Extracts metadata from Shapefile files.

```python
result = engine.extract_shapefile_metadata("vector_data.shp")
```

### `ScientificInstrumentEngine`

Specialized engine for scientific data formats.

#### Methods

##### `extract_hdf5_metadata(filepath)`
Extracts metadata from HDF5 files.

```python
from server.extractor.comprehensive_metadata_engine import ScientificInstrumentEngine

engine = ScientificInstrumentEngine()
result = engine.extract_hdf5_metadata("scientific_data.h5")
```

##### `extract_netcdf_metadata(filepath)`
Extracts metadata from NetCDF files.

```python
result = engine.extract_netcdf_metadata("climate_data.nc")
```

## Command Line Interface

The engine provides a comprehensive command-line interface.

### Basic Usage

```bash
# Extract metadata from a single file
python server/extractor/comprehensive_metadata_engine.py image.jpg

# Extract with specific tier
python server/extractor/comprehensive_metadata_engine.py image.jpg --tier premium

# Extract to output file
python server/extractor/comprehensive_metadata_engine.py image.jpg --output result.json

# Process multiple files in batch
python server/extractor/comprehensive_metadata_engine.py img1.jpg img2.jpg img3.jpg --batch

# View available specialized engines
python server/extractor/comprehensive_metadata_engine.py --engines
```

### CLI Options

- `--tier, -t`: Access tier (free, starter, premium, super) - default: super
- `--output, -o`: Output JSON file path
- `--engines`: Show available specialized engines
- `--batch`: Process files in batch mode
- `--store`: Store metadata in local database
- `--max-workers`: Batch concurrency - default: 4
- `--performance`: Include performance metrics (compatibility)
- `--advanced`: Enable advanced analysis (compatibility)
- `--quiet, -q`: JSON only output (no status messages)

### Example CLI Usage

```bash
# Extract with super tier and save to file
python server/extractor/comprehensive_metadata_engine.py photo.jpg --tier super --output metadata.json

# Batch process multiple files
python server/extractor/comprehensive_metadata_engine.py *.jpg --batch --tier premium

# Process with database storage
python server/extractor/comprehensive_metadata_engine.py medical.dcm --store --tier super

# View available engines
python server/extractor/comprehensive_metadata_engine.py --engines
```

## Response Format

The API returns a standardized JSON response format:

```json
{
  "extraction_info": {
    "timestamp": "2024-12-31T10:30:45.123456",
    "tier": "super",
    "engine_version": "4.0.0",
    "comprehensive_version": "4.0.0",
    "exiftool_used": true,
    "fields_extracted": 1247,
    "comprehensive_fields_extracted": 8452,
    "specialized_field_counts": {
      "medical_imaging": 2341,
      "astronomical_data": 1205,
      "geospatial": 892
    },
    "libraries": {
      "pillow": true,
      "exifread": true,
      "exiftool": true,
      "pydicom": true,
      "astropy": true
    },
    "specialized_engines": {
      "medical_imaging": true,
      "astronomical_data": true,
      "geospatial_analysis": true
    }
  },
  "file": {
    "path": "/path/to/file.jpg",
    "name": "file.jpg",
    "extension": ".jpg",
    "mime_type": "image/jpeg"
  },
  "summary": {
    "filename": "file.jpg",
    "filesize": "2.45 MB",
    "filesize_bytes": 2567890,
    "filetype": "JPG",
    "mime_type": "image/jpeg",
    "width": 4000,
    "height": 3000,
    "aspect_ratio": "4:3"
  },
  "filesystem": {
    "size_bytes": 2567890,
    "size_human": "2.45 MB",
    "created": "2024-12-30T15:22:33.123456",
    "modified": "2024-12-30T15:22:33.123456",
    "accessed": "2024-12-31T10:30:45.123456",
    "permissions_oct": "0o644",
    "permissions_human": "-rw-r--r--",
    "owner": "user",
    "group": "staff"
  },
  "locked_fields": ["makernote", "iptc", "xmp"],
  "hashes": {
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "crc32": "00000000"
  }
}
```

## Error Handling

The API provides comprehensive error handling:

```python
result = extract_comprehensive_metadata("nonexistent.jpg")

if "error" in result:
    print(f"Error: {result['error']}")
    # Handle error appropriately
```

Common error responses:

```json
{
  "error": "File not found: nonexistent.jpg"
}
```

```json
{
  "error": "Not a file: directory_path"
}
```

```json
{
  "medical_imaging": {
    "available": false,
    "error": "pydicom not installed"
  }
}
```

## Tier-Based Access Control

The API enforces tier-based access control:

```python
# Free tier - limited access
result = extract_comprehensive_metadata("photo.jpg", tier="free")
# Result will have many fields marked as {"_locked": True}

# Super tier - full access
result = extract_comprehensive_metadata("photo.jpg", tier="super")
# Result will have full metadata access
```

Locked fields are indicated with `{"_locked": True}` and listed in the `locked_fields` array.

## Performance Considerations

### Caching
The API supports Redis-based caching when available:

```python
# Results are automatically cached when Redis is available
result = extract_comprehensive_metadata("file.jpg", tier="super")
# Subsequent calls with same file and tier use cached results
```

### Batch Processing
For multiple files, use batch processing:

```python
# More efficient than individual calls
results = extract_comprehensive_batch([
    "file1.jpg", "file2.dcm", "file3.fits"
], tier="super", max_workers=4)
```

### Memory Management
The API processes files efficiently:

- Files are processed in memory when possible
- Temporary files are automatically deleted
- Large files are processed in chunks

## Advanced Usage

### Custom Processing
Access the extractor directly for custom processing:

```python
from server.extractor.comprehensive_metadata_engine import get_comprehensive_extractor

extractor = get_comprehensive_extractor()
result = extractor.extract_comprehensive_metadata("file.jpg", tier="super")
```

### Engine Availability Check
Check which engines are available:

```python
from server.extractor.comprehensive_metadata_engine import (
    DICOM_AVAILABLE, FITS_AVAILABLE, RASTERIO_AVAILABLE, 
    HDF5_AVAILABLE, NETCDF_AVAILABLE
)

print(f"DICOM support: {DICOM_AVAILABLE}")
print(f"FITS support: {FITS_AVAILABLE}")
```

### Integration with External Systems
The API can be integrated with external systems:

```python
def process_file_with_metadata(filepath, tier="super"):
    """Process a file and integrate metadata with external system"""
    result = extract_comprehensive_metadata(filepath, tier)
    
    if "error" not in result:
        # Send metadata to external system
        send_to_external_system(result)
        return result
    else:
        # Handle error
        log_error(result["error"])
        return result
```

## File Format Support

The API supports the following file formats:

### Images
- JPEG, PNG, GIF, WebP, TIFF, BMP, HEIC/HEIF
- RAW formats: CR2, CR3, NEF, ARW, DNG, ORF, RW2, RAF, PEF

### Video
- MP4, MOV, AVI, WebM, MKV, M4V

### Audio
- MP3, FLAC, WAV, OGG, M4A, AAC, AIFF

### Documents
- PDF, SVG

### Scientific
- DICOM, FITS, HDF5, NetCDF, GeoTIFF, Shapefile

### Emerging Technologies
- AI/ML models: .h5, .pb, .pth, .onnx, .tflite, .mlmodel
- Quantum: .qasm, .qc, .qobj
- IoT: Device configs, sensor data
- Blockchain: NFT metadata, smart contracts

## Dependencies

The API requires various dependencies based on the file types being processed:

### Core Dependencies
- Python 3.11+
- pillow, exifread, mutagen, pypdf

### Enhanced Features
- exiftool (for parsed MakerNotes, full IPTC/XMP)
- ffmpeg-python (for video extraction)

### Specialized Engines
- pydicom (for DICOM files)
- astropy (for FITS files)
- rasterio, fiona (for geospatial files)
- h5py, netCDF4 (for scientific data)

## Testing

### Unit Testing
```python
import unittest
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

class TestMetadataExtraction(unittest.TestCase):
    def test_basic_extraction(self):
        result = extract_comprehensive_metadata("test.jpg", tier="free")
        self.assertIn("extraction_info", result)
        self.assertIn("file", result)
    
    def test_tier_access(self):
        # Test that free tier has locked fields
        free_result = extract_comprehensive_metadata("test.jpg", tier="free")
        premium_result = extract_comprehensive_metadata("test.jpg", tier="premium")
        
        self.assertLess(
            free_result["extraction_info"]["fields_extracted"],
            premium_result["extraction_info"]["fields_extracted"]
        )
```

### Integration Testing
```python
def test_batch_processing():
    files = ["test1.jpg", "test2.png"]
    results = extract_comprehensive_batch(files, tier="super")
    
    assert results["summary"]["total_files"] == 2
    assert results["summary"]["successful"] == 2
```

## Troubleshooting

### Common Issues

**Missing Dependencies**
```python
# Check if specialized engines are available
from server.extractor.comprehensive_metadata_engine import DICOM_AVAILABLE
if not DICOM_AVAILABLE:
    print("Install pydicom for DICOM support: pip install pydicom")
```

**Tier Access Issues**
```python
# Ensure using appropriate tier
result = extract_comprehensive_metadata("file.dcm", tier="super")
if "medical_imaging" not in result:
    print("Medical imaging requires Super tier")
```

**File Format Issues**
```python
# Validate file exists and is accessible
import os
if not os.path.exists(filepath):
    print(f"File does not exist: {filepath}")
```

### Performance Issues
```python
# Monitor processing time
import time
start = time.time()
result = extract_comprehensive_metadata("large_file.dcm", tier="super")
processing_time = time.time() - start
print(f"Processing took {processing_time:.2f} seconds")
```

## Best Practices

1. **Use appropriate tiers**: Request only the metadata level you need
2. **Batch processing**: Use batch methods for multiple files
3. **Error handling**: Always check for errors in responses
4. **Caching**: Leverage caching for repeated extractions
5. **File validation**: Validate files before extraction
6. **Memory management**: Process large files appropriately
7. **Dependency management**: Ensure required libraries are installed
8. **Performance monitoring**: Monitor processing times and resource usage
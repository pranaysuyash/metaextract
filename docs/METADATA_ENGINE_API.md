# MetaExtract Comprehensive Metadata Engine API Documentation

## Overview

The MetaExtract Comprehensive Metadata Engine (v4.0) is the world's most comprehensive metadata extraction system, capable of extracting over 45,000 metadata fields across multiple domains including medical imaging, astronomical data, geospatial analysis, scientific instruments, and more.

## Key Features

- **Medical Imaging**: DICOM files with 4,600+ standardized fields
- **Astronomical Data**: FITS files with 3,000+ fields and WCS support
- **Geospatial Analysis**: GeoTIFF, Shapefile with full CRS and projection metadata
- **Scientific Data**: HDF5, NetCDF with unlimited metadata fields
- **Professional Video**: Broadcast standards, HDR, timecode analysis
- **AI Content Detection**: Detect AI-generated images, videos, and text
- **Blockchain Provenance**: NFT metadata, C2PA content credentials
- **Enhanced Forensics**: Advanced steganography and manipulation detection
- **Drone/UAV Telemetry**: Flight data, GPS tracks, sensor readings
- **And much more...**

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+ (for web interface)
- PostgreSQL (for metadata storage)
- Redis (for caching)

### Python Dependencies

```bash
pip install -r requirements.txt
```

### System Dependencies

```bash
# macOS
brew install exiftool ffmpeg libmagic

# Ubuntu/Debian
sudo apt install libimage-exiftool-perl ffmpeg libmagic1
```

## Quick Start

### Command Line Interface

```bash
# Extract metadata from a single file
python server/extractor/comprehensive_metadata_engine.py image.jpg

# Extract with premium tier access
python server/extractor/comprehensive_metadata_engine.py image.jpg --tier premium

# Extract with super tier (full access)
python server/extractor/comprehensive_metadata_engine.py image.jpg --tier super

# Batch processing
python server/extractor/comprehensive_metadata_engine.py image1.jpg image2.jpg image3.jpg --batch --tier super

# View available specialized engines
python server/extractor/comprehensive_metadata_engine.py --engines
```

### Python API

```python
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

# Extract metadata with default tier (super)
result = extract_comprehensive_metadata("path/to/file.jpg")

# Extract with specific tier
result = extract_comprehensive_metadata("path/to/file.jpg", tier="premium")

# Check for errors
if "error" in result:
    print(f"Extraction failed: {result['error']}")
else:
    print(f"Extracted {result['extraction_info']['comprehensive_fields_extracted']} fields")
```

### Batch Processing API

```python
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_batch

# Process multiple files
file_list = ["file1.jpg", "file2.dcm", "file3.fits"]
results = extract_comprehensive_batch(file_list, tier="super", max_workers=4)

# Access individual results
for filepath, metadata in results["results"].items():
    if "error" not in metadata:
        print(f"{filepath}: {metadata['extraction_info']['comprehensive_fields_extracted']} fields extracted")
```

## Tier Configuration

The engine supports four different access tiers with varying levels of metadata access:

### Free Tier
- Basic EXIF data (~50 fields)
- File system metadata
- Calculated fields
- Limited file types (JPG, PNG, GIF, WebP)

### Starter Tier
- All Free tier features
- Additional file types (RAW, PDF, Audio)
- ~200 metadata fields
- GPS data
- File hashes

### Premium Tier
- All Starter tier features
- 7,000+ metadata fields
- MakerNote parsing
- Full IPTC/XMP support
- Video extraction
- PDF details
- Batch processing
- Advanced audio analysis

### Super Tier
- All Premium tier features
- **Comprehensive extraction** (45,000+ fields)
- All specialized engines enabled
- Medical imaging (DICOM)
- Astronomical data (FITS)
- Geospatial analysis
- Scientific instruments (HDF5/NetCDF)
- Blockchain provenance
- AI content detection
- Emerging technologies

## Specialized Extraction Engines

### Medical Imaging Engine (DICOM)

Extracts comprehensive medical imaging metadata:

```python
# DICOM files automatically trigger the medical imaging engine
result = extract_comprehensive_metadata("medical_image.dcm", tier="super")

# Access medical imaging data
if "medical_imaging" in result:
    patient_info = result["medical_imaging"]["patient_info"]
    study_info = result["medical_imaging"]["study_info"]
    equipment_info = result["medical_imaging"]["equipment_info"]
    acquisition_params = result["medical_imaging"]["acquisition_params"]
```

**Features:**
- 4,600+ DICOM standard fields
- Patient information (anonymized)
- Study and series metadata
- Equipment information
- Acquisition parameters
- Modality-specific settings (CT, MR, X-Ray)
- Radiation dose information
- Private tags

### Astronomical Data Engine (FITS)

Extracts astronomical observation metadata:

```python
# FITS files automatically trigger the astronomical data engine
result = extract_comprehensive_metadata("observation.fits", tier="super")

# Access astronomical data
if "astronomical_data" in result:
    observation_info = result["astronomical_data"]["observation_info"]
    instrument_info = result["astronomical_data"]["instrument_info"]
    wcs_info = result["astronomical_data"]["wcs_info"]
```

**Features:**
- 3,000+ FITS standard keywords
- Observation metadata
- Instrument configuration
- World Coordinate System (WCS) analysis
- Field of view calculations
- Coordinate systems
- Processing history

### Geospatial Engine

Extracts geospatial metadata from GeoTIFF and Shapefile formats:

```python
# GeoTIFF and Shapefile automatically trigger the geospatial engine
result = extract_comprehensive_metadata("geospatial_data.tif", tier="super")

# Access geospatial data
if "geospatial" in result:
    raster_info = result["geospatial"]["raster_info"]
    coordinate_system = result["geospatial"]["coordinate_system"]
    geotransform = result["geospatial"]["geotransform"]
```

**Features:**
- Coordinate Reference System (CRS) information
- Geotransform matrix
- Raster dimensions and data types
- Spatial bounds
- Pixel resolution and area calculations
- Band statistics

### Scientific Instrument Engine

Extracts data from scientific formats (HDF5, NetCDF):

```python
# Scientific formats automatically trigger the scientific engine
result = extract_comprehensive_metadata("scientific_data.h5", tier="super")

# Access scientific data
if "scientific_data" in result:
    file_info = result["scientific_data"]["file_info"]
    groups = result["scientific_data"]["groups"]
    datasets = result["scientific_data"]["datasets"]
```

**Features:**
- Hierarchical data structure
- Dataset shapes and types
- Attributes and metadata
- Group relationships
- File format information

### Drone/UAV Telemetry Engine

Extracts flight and sensor data from drone-captured media:

```python
# Images/videos from drones automatically trigger the telemetry engine
result = extract_comprehensive_metadata("drone_photo.jpg", tier="super")

# Access drone telemetry
if "drone_telemetry" in result:
    flight_data = result["drone_telemetry"]["flight_data"]
    camera_data = result["drone_telemetry"]["camera_data"]
    gps_track = result["drone_telemetry"]["gps_track"]
```

**Features:**
- Flight path coordinates
- Camera gimbal settings
- Exposure parameters
- Manufacturer-specific data (DJI, GoPro, etc.)
- GPS tracking information

### Blockchain Provenance Engine

Extracts blockchain and content authenticity metadata:

```python
# Files with blockchain metadata trigger the provenance engine
result = extract_comprehensive_metadata("nft_image.jpg", tier="super")

# Access blockchain data
if "blockchain_provenance" in result:
    c2pa_manifest = result["blockchain_provenance"]["c2pa_manifest"]
    nft_metadata = result["blockchain_provenance"]["nft_metadata"]
```

**Features:**
- C2PA (Content Authenticity) manifests
- Digital signatures
- NFT metadata
- Content credentials
- Blockchain references

## API Response Format

The comprehensive metadata engine returns a structured JSON response:

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
    "permissions_octal": "0o644",
    "permissions_human": "-rw-r--r--",
    "owner": "user",
    "group": "staff"
  },
  "hashes": {
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "crc32": "00000000"
  },
  "image": {
    "width": 4000,
    "height": 3000,
    "format": "JPEG",
    "mode": "RGB",
    "dpi": [72, 72],
    "bits_per_pixel": 24,
    "color_palette": "no",
    "animation": false,
    "frames": 1,
    "icc_profile": "yes",
    "has_icc_profile": true,
    "has_transparency": false
  },
  "exif": {
    "Make": "Canon",
    "Model": "Canon EOS R5",
    "DateTime": "2024:12:30 15:22:33",
    "ExposureTime": "1/125",
    "FNumber": 5.6,
    "ISO": 100,
    "FocalLength": "85.0 mm",
    "LensInfo": "85.0 mm f/1.2"
  },
  "gps": {
    "GPSLatitude": "34 deg 0' 12.34\" N",
    "GPSLongitude": "118 deg 24' 56.78\" W",
    "latitude_decimal": 34.003428,
    "longitude_decimal": -118.415772,
    "coordinates": "34.0034, -118.4158",
    "google_maps_url": "https://www.google.com/maps?q=34.003428,-118.415772"
  },
  "makernote": {
    "canon": {
      "CameraTemperature": "23 C",
      "WBShiftAB": 0,
      "WBShiftGM": 0,
      "SerialNumber": "XXXXXXXXX"
    }
  },
  "medical_imaging": {
    "available": true,
    "patient_info": {
      "name": "[ANONYMIZED]",
      "id": "[ANONYMIZED]",
      "birth_date": "19800101",
      "sex": "M",
      "age": "043Y"
    },
    "study_info": {
      "uid": "1.2.840.113619.2.55.3.832347654.123456",
      "date": "20241230",
      "time": "152233.123456",
      "description": "CT ABDOMEN W WO CONTRAST"
    },
    "equipment_info": {
      "manufacturer": "SIEMENS",
      "model": "SOMATOM Definition AS+",
      "serial_number": "12345",
      "software_version": "syngo CT 2011A"
    }
  }
}
```

## Error Handling

The engine provides detailed error information:

```python
result = extract_comprehensive_metadata("invalid_file.xyz", tier="super")

if "error" in result:
    print(f"Extraction failed: {result['error']}")
    # Handle error appropriately
```

Common error scenarios:
- File not found
- Unsupported file format
- Insufficient permissions
- Missing dependencies
- Invalid tier access

## Performance Considerations

### Caching
The engine supports Redis-based caching for improved performance on repeated extractions:

```python
# Results are automatically cached when Redis is available
result = extract_comprehensive_metadata("file.jpg", tier="super")
# Subsequent calls with the same file and tier will use cached results
```

### Batch Processing
For processing multiple files, use the batch interface:

```python
# More efficient than individual calls
results = extract_comprehensive_batch([
    "file1.jpg", "file2.dcm", "file3.fits"
], tier="super", max_workers=4)
```

### Memory Management
The engine processes files efficiently with automatic cleanup:

- Files are processed in memory when possible
- Temporary files are automatically deleted
- Large files are processed in chunks

## Advanced Usage

### Custom Processing

You can access the comprehensive extractor directly:

```python
from server.extractor.comprehensive_metadata_engine import get_comprehensive_extractor

extractor = get_comprehensive_extractor()
result = extractor.extract_comprehensive_metadata("file.jpg", tier="super")
```

### Engine Availability Check

Check which specialized engines are available:

```python
from server.extractor.comprehensive_metadata_engine import (
    DICOM_AVAILABLE, FITS_AVAILABLE, RASTERIO_AVAILABLE, 
    HDF5_AVAILABLE, NETCDF_AVAILABLE
)

print(f"DICOM support: {DICOM_AVAILABLE}")
print(f"FITS support: {FITS_AVAILABLE}")
print(f"Geospatial support: {RASTERIO_AVAILABLE}")
print(f"Scientific data support: {HDF5_AVAILABLE or NETCDF_AVAILABLE}")
```

## Troubleshooting

### Missing Dependencies

If specialized engines are not available, install the required packages:

```bash
# Medical imaging (DICOM)
pip install pydicom

# Astronomical data (FITS)
pip install astropy

# Geospatial data
pip install rasterio fiona

# Scientific data
pip install h5py netCDF4
```

### File Format Support

The engine supports the following file formats:

**Images:** JPEG, PNG, GIF, WebP, TIFF, BMP, HEIC/HEIF, CR2, CR3, NEF, ARW, DNG, ORF, RW2, RAF, PEF

**Video:** MP4, MOV, AVI, WebM, MKV, M4V

**Audio:** MP3, FLAC, WAV, OGG, M4A, AAC, AIFF

**Documents:** PDF, SVG

**Scientific:** DICOM, FITS, HDF5, NetCDF, GeoTIFF, Shapefile

### Tier Access Issues

Ensure you're using the correct tier for the metadata you need:

```python
# Check if a specific engine is available for your tier
result = extract_comprehensive_metadata("file.dcm", tier="premium")
if "medical_imaging" not in result:
    # Medical imaging requires super tier
    result = extract_comprehensive_metadata("file.dcm", tier="super")
```

## Best Practices

1. **Use appropriate tiers**: Request only the metadata level you need to optimize performance
2. **Batch processing**: Use batch methods for multiple files
3. **Error handling**: Always check for errors in the response
4. **Caching**: Leverage caching for repeated extractions
5. **File validation**: Validate files before extraction to avoid errors
6. **Memory management**: Process large files in appropriate environments

## Support

For issues and feature requests, please check the GitHub repository or contact the development team.
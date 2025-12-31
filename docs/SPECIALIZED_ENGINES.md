# MetaExtract Specialized Extraction Engines Documentation

## Overview

The MetaExtract Comprehensive Metadata Engine includes multiple specialized extraction engines designed to handle specific file formats and domains. Each engine is optimized for extracting domain-specific metadata with high precision and accuracy.

## Engine Architecture

The specialized engines follow a consistent architecture pattern:

1. **Detection**: Identify if the file format matches the engine's domain
2. **Extraction**: Extract domain-specific metadata using appropriate libraries
3. **Normalization**: Structure the metadata in a consistent format
4. **Integration**: Merge results with the main extraction result

## Medical Imaging Engine (DICOM)

### Purpose
The Medical Imaging Engine extracts comprehensive metadata from DICOM (Digital Imaging and Communications in Medicine) files used in healthcare and medical imaging.

### Capabilities
- **4,600+ DICOM standard fields** including patient, study, series, and equipment information
- **Anonymized patient data** to protect privacy while preserving metadata
- **Modality-specific parameters** (CT, MR, X-Ray, Ultrasound, etc.)
- **Radiation dose information** for CT and X-Ray studies
- **Private tags** and custom manufacturer fields
- **Image dimensions and quality metrics**

### Implementation
```python
from server.extractor.comprehensive_metadata_engine import MedicalImagingEngine

engine = MedicalImagingEngine()
result = engine.extract_dicom_metadata("medical_image.dcm")
```

### Output Structure
```json
{
  "medical_imaging": {
    "available": true,
    "patient_info": {
      "name": "[ANONYMIZED]",
      "id": "[ANONYMIZED]",
      "birth_date": "19800101",
      "sex": "M",
      "age": "043Y",
      "weight": "75.0",
      "height": "175.0"
    },
    "study_info": {
      "uid": "1.2.840.113619.2.55.3.832347654.123456",
      "date": "20241230",
      "time": "152233.123456",
      "description": "CT ABDOMEN W WO CONTRAST",
      "id": "123456",
      "accession_number": "ACC123456"
    },
    "series_info": {
      "uid": "1.2.840.113619.2.55.3.832347654.123457",
      "number": "1",
      "date": "20241230",
      "time": "152233.123456",
      "description": "AXIAL",
      "modality": "CT",
      "body_part": "ABDOMEN",
      "patient_position": "FFS"
    },
    "equipment_info": {
      "manufacturer": "SIEMENS",
      "model": "SOMATOM Definition AS+",
      "serial_number": "12345",
      "software_version": "syngo CT 2011A",
      "station_name": "CT01",
      "institution_name": "Medical Center",
      "department": "Radiology"
    },
    "image_info": {
      "dimensions": [512, 512],
      "data_type": "int16",
      "height": 512,
      "width": 512,
      "bits_allocated": 16,
      "bits_stored": 16,
      "high_bit": 15,
      "pixel_representation": 1,
      "photometric_interpretation": "MONOCHROME2",
      "samples_per_pixel": 1,
      "pixel_spacing": [0.78125, 0.78125],
      "slice_thickness": 5.0
    },
    "acquisition_params": {
      "kvp": 120.0,
      "tube_current": 100,
      "exposure_time": 1000,
      "filter_type": "FILTER1",
      "kernel": "K50F",
      "slice_thickness": 5.0,
      "table_height": 120.0,
      "gantry_tilt": 0.0,
      "ctdi_vol": 15.2,
      "dlp": 650.0
    },
    "dose_info": {
      "ctdi_vol": 15.2,
      "dlp": 650.0,
      "total_dlp": 1300.0,
      "effective_dose": 6.5
    },
    "dicom_standard": {
      "file_meta_info_version": [0, 1],
      "media_storage_sop_class": "1.2.840.10008.5.1.4.1.1.2",
      "transfer_syntax": "1.2.840.10008.1.2.1",
      "total_tags": 2341,
      "private_tag_count": 42,
      "standard_tag_count": 2299
    }
  }
}
```

### Dependencies
- `pydicom`: Required for DICOM parsing

### Usage Notes
- Patient information is automatically anonymized
- Requires Super tier for full access
- Handles both standard and private DICOM tags

## Astronomical Data Engine (FITS)

### Purpose
The Astronomical Data Engine extracts comprehensive metadata from FITS (Flexible Image Transport System) files used in astronomy and astrophysics.

### Capabilities
- **3,000+ FITS standard keywords** covering observation and instrument metadata
- **World Coordinate System (WCS)** analysis for astronomical coordinates
- **Observation parameters** including telescope, instrument, and filter information
- **Processing history** and calibration metadata
- **Field of view calculations** and coordinate system analysis

### Implementation
```python
from server.extractor.comprehensive_metadata_engine import AstronomicalDataEngine

engine = AstronomicalDataEngine()
result = engine.extract_fits_metadata("observation.fits")
```

### Output Structure
```json
{
  "astronomical_data": {
    "available": true,
    "file_info": {
      "num_hdus": 2,
      "hdu_types": ["PrimaryHDU", "BinTableHDU"],
      "hdu_names": ["", "COMPANIONS"]
    },
    "primary_header": {
      "conforms_to_fits": true,
      "bits_per_pixel": -32,
      "num_axes": 2,
      "has_extensions": true,
      "object_name": "M51",
      "telescope": "HST",
      "instrument": "WFPC2",
      "observer": "Dr. Smith",
      "observation_date": "2024-01-15",
      "observation_time": "12:34:56.789",
      "exposure_time": 1200.0,
      "filter": "F555W",
      "airmass": 1.23,
      "seeing": 0.8
    },
    "observation_info": {
      "right_ascension": 202.469575,
      "declination": 47.195258,
      "equinox": 2000.0,
      "epoch": 2000.0,
      "coordinate_system": "FK5",
      "coord_type_1": "RA---TAN",
      "coord_type_2": "DEC--TAN",
      "reference_value_1": 202.469575,
      "reference_value_2": 47.195258,
      "reference_pixel_1": 512.0,
      "reference_pixel_2": 512.0,
      "pixel_scale_1": 0.0492,
      "pixel_scale_2": 0.0492
    },
    "instrument_info": {
      "detector": "WF2",
      "gain": 7.0,
      "read_noise": 4.7,
      "pixel_scale": 0.0492,
      "focal_length": 5791.0,
      "aperture_diameter": 2.4,
      "aperture_area": 4.52,
      "x_binning": 1,
      "y_binning": 1,
      "temperature": -78.0,
      "cooling_status": "ON"
    },
    "wcs_info": {
      "has_celestial_wcs": true,
      "coordinate_system": "FK5",
      "projection": "TAN",
      "reference_coordinates": {
        "ra": 202.469575,
        "dec": 47.195258
      },
      "pixel_scale": {
        "ra": 0.0492,
        "dec": 0.0492
      },
      "field_of_view": {
        "ra_arcsec": 50.3808,
        "dec_arcsec": 50.3808,
        "ra_arcmin": 0.8397,
        "dec_arcmin": 0.8397,
        "ra_degrees": 0.0140,
        "dec_degrees": 0.0140
      }
    },
    "extensions": [
      {
        "index": 1,
        "name": "COMPANIONS",
        "type": "BinTableHDU",
        "header_keywords": 15,
        "data_shape": [25, 12],
        "data_type": "float64",
        "key_headers": {
          "EXTNAME": "COMPANIONS",
          "EXTVER": 1,
          "TTYPE1": "ID",
          "TFORM1": "K",
          "TUNIT1": "count"
        }
      }
    ],
    "raw_headers": {
      "HDU_": {
        "SIMPLE": true,
        "BITPIX": -32,
        "NAXIS": 2,
        "NAXIS1": 1024,
        "NAXIS2": 1024,
        "BSCALE": 1.0,
        "BZERO": 0.0
      }
    },
    "file_info": {
      "total_keywords": 1247
    }
  }
}
```

### Dependencies
- `astropy`: Required for FITS parsing and WCS analysis

### Usage Notes
- Requires Super tier for full access
- Handles multi-extension FITS files
- Provides coordinate system analysis

## Geospatial Engine

### Purpose
The Geospatial Engine extracts comprehensive metadata from geospatial formats including GeoTIFF and Shapefile.

### Capabilities
- **Coordinate Reference System (CRS)** information and transformation parameters
- **Geotransform matrix** for spatial coordinate conversion
- **Raster dimensions** and data type information
- **Spatial bounds** and coverage area
- **Pixel resolution** and area calculations
- **Band statistics** and color interpretation

### Implementation
```python
from server.extractor.comprehensive_metadata_engine import GeospatialEngine

engine = GeospatialEngine()
result = engine.extract_geotiff_metadata("geospatial_data.tif")
result = engine.extract_shapefile_metadata("vector_data.shp")
```

### Output Structure (GeoTIFF)
```json
{
  "geospatial": {
    "available": true,
    "raster_info": {
      "width": 2000,
      "height": 1500,
      "count": 3,
      "dtype": "uint8",
      "driver": "GTiff",
      "nodata": null,
      "bounds": {
        "left": -122.4194,
        "bottom": 37.7749,
        "right": -122.2194,
        "top": 37.9749
      },
      "pixel_area": 0.0000000001,
      "total_area": 0.0003,
      "resolution": {
        "x": 0.0001,
        "y": 0.0001,
        "units": "degrees"
      }
    },
    "coordinate_system": {
      "crs_string": "+proj=longlat +datum=WGS84 +no_defs",
      "epsg_code": 4326,
      "proj4_string": "+proj=longlat +datum=WGS84 +no_defs",
      "wkt": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
      "is_geographic": true,
      "is_projected": false,
      "units": 1.0
    },
    "geotransform": {
      "pixel_size_x": 0.0001,
      "rotation_x": 0.0,
      "top_left_x": -122.4194,
      "rotation_y": 0.0,
      "pixel_size_y": -0.0001,
      "top_left_y": 37.9749,
      "matrix": [0.0001, 0.0, -122.4194, 0.0, -0.0001, 37.9749]
    },
    "bands": [
      {
        "band_number": 1,
        "dtype": "uint8",
        "nodata": null,
        "statistics": {
          "min": 0,
          "max": 255,
          "mean": 128.5,
          "std": 64.2
        },
        "color_interpretation": "Red"
      }
    ],
    "tags": {
      "TIFFTAG_SOFTWARE": "GDAL 3.4.0",
      "TIFFTAG_COPYRIGHT": "© 2024 Organization"
    }
  }
}
```

### Output Structure (Shapefile)
```json
{
  "geospatial": {
    "available": true,
    "vector_info": {
      "driver": "ESRI Shapefile",
      "feature_count": 1250,
      "geometry_type": "Polygon"
    },
    "coordinate_system": {
      "crs_string": "+proj=longlat +datum=WGS84 +no_defs",
      "crs_wkt": "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137,298.257223563]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295]]"
    },
    "schema": {
      "geometry": "Polygon",
      "properties": {
        "ID": "int:9",
        "NAME": "str:80",
        "AREA": "float:24.15",
        "POPULATION": "int:10"
      }
    },
    "bounds": {
      "left": -122.4194,
      "bottom": 37.7749,
      "right": -122.2194,
      "top": 37.9749
    },
    "features": {
      "sample_count": 5,
      "samples": [
        {
          "id": 1,
          "geometry_type": "Polygon",
          "properties": {
            "ID": 1,
            "NAME": "Downtown",
            "AREA": 2.5,
            "POPULATION": 25000
          }
        }
      ]
    }
  }
}
```

### Dependencies
- `rasterio`: Required for GeoTIFF processing
- `fiona`: Required for Shapefile processing

### Usage Notes
- Requires Super tier for full access
- Handles both projected and geographic coordinate systems
- Provides area and resolution calculations

## Scientific Instrument Engine

### Purpose
The Scientific Instrument Engine extracts metadata from scientific data formats including HDF5 and NetCDF.

### Capabilities
- **Hierarchical data structure** analysis for HDF5 files
- **Dataset shapes and types** with attributes
- **NetCDF dimensions and variables** with CF conventions
- **File format information** and version details
- **Attribute preservation** for scientific metadata

### Implementation
```python
from server.extractor.comprehensive_metadata_engine import ScientificInstrumentEngine

engine = ScientificInstrumentEngine()
result = engine.extract_hdf5_metadata("scientific_data.h5")
result = engine.extract_netcdf_metadata("climate_data.nc")
```

### Output Structure (HDF5)
```json
{
  "scientific_data": {
    "available": true,
    "file_info": {
      "hdf5_version": [1, 10, 4],
      "file_size": 1048576,
      "total_groups": 5,
      "total_datasets": 12,
      "total_attributes": 23
    },
    "groups": {
      "/": {
        "path": "/",
        "attributes": {
          "title": "Climate Data Collection",
          "institution": "Research Institute",
          "date_created": "2024-01-01"
        },
        "subgroups": ["temperature", "pressure", "humidity"],
        "datasets": ["metadata"]
      },
      "/temperature": {
        "path": "/temperature",
        "attributes": {
          "units": "celsius",
          "long_name": "Air Temperature"
        },
        "subgroups": [],
        "datasets": ["daily_avg", "monthly_avg"]
      }
    },
    "datasets": {
      "/metadata": {
        "path": "/metadata",
        "shape": [1],
        "dtype": "<U256",
        "size": 1,
        "attributes": {
          "description": "Dataset metadata"
        },
        "chunks": null,
        "compression": null,
        "compression_opts": null
      },
      "/temperature/daily_avg": {
        "path": "/temperature/daily_avg",
        "shape": [365, 100, 100],
        "dtype": "<f4",
        "size": 3650000,
        "attributes": {
          "units": "celsius",
          "long_name": "Daily Average Temperature",
          "valid_range": [-50, 50],
          "scale_factor": 0.1,
          "_FillValue": -999.0
        },
        "chunks": [1, 100, 100],
        "compression": "gzip",
        "compression_opts": 4
      }
    },
    "attributes": {
      "title": "Climate Data Collection",
      "institution": "Research Institute",
      "date_created": "2024-01-01"
    }
  }
}
```

### Output Structure (NetCDF)
```json
{
  "scientific_data": {
    "available": true,
    "file_info": {
      "format": "NETCDF4",
      "file_format": "NETCDF4",
      "disk_format": "netCDF-4",
      "num_dimensions": 3,
      "num_variables": 8,
      "num_global_attributes": 12
    },
    "dimensions": {
      "time": {
        "size": 365,
        "unlimited": false
      },
      "lat": {
        "size": 180,
        "unlimited": false
      },
      "lon": {
        "size": 360,
        "unlimited": false
      }
    },
    "variables": {
      "temperature": {
        "dimensions": ["time", "lat", "lon"],
        "shape": [365, 180, 360],
        "dtype": "<f4",
        "attributes": {
          "units": "celsius",
          "long_name": "Air Temperature",
          "standard_name": "air_temperature",
          "valid_range": [-50, 50],
          "scale_factor": 0.1,
          "add_offset": 0.0,
          "_FillValue": -999.0
        },
        "cf_attributes": {
          "units": "celsius",
          "long_name": "Air Temperature",
          "standard_name": "air_temperature",
          "valid_range": [-50, 50]
        }
      }
    },
    "global_attributes": {
      "title": "Climate Data Collection",
      "institution": "Research Institute",
      "source": "Weather Station Network",
      "history": "Created on 2024-01-01",
      "references": "Climate Research Paper 2024"
    }
  }
}
```

### Dependencies
- `h5py`: Required for HDF5 processing
- `netCDF4`: Required for NetCDF processing

### Usage Notes
- Requires Super tier for full access
- Handles complex hierarchical structures
- Preserves scientific metadata standards

## Drone/UAV Telemetry Engine

### Purpose
The Drone/UAV Telemetry Engine extracts flight and sensor data from media captured by drones and action cameras.

### Capabilities
- **Flight path coordinates** and GPS tracking
- **Camera gimbal settings** and exposure parameters
- **Manufacturer-specific data** (DJI, GoPro, etc.)
- **Sensor readings** and flight telemetry
- **Flight time and altitude** information

### Implementation
The engine is automatically invoked when processing drone-captured media with the Super tier.

### Output Structure
```json
{
  "drone_telemetry": {
    "available": true,
    "flight_data": {
      "altitude_msl": 120.5,
      "altitude_agl": 115.2,
      "relative_altitude": 115.2,
      "flight_speed": 15.3,
      "flight_yaw_degree": 45.2,
      "gimbal_pitch_degree": -12.5,
      "gimbal_yaw_degree": 0.0,
      "gimbal_roll_degree": 0.1
    },
    "camera_data": {
      "exposure_settings": {
        "iso": 100,
        "shutter_speed": "1/60",
        "aperture": 2.8,
        "focal_length": "24.0 mm"
      },
      "white_balance": "Auto",
      "color_space": "sRGB"
    },
    "gps_track": {
      "has_gps": true,
      "coordinates": {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "altitude": 120.5
      },
      "movement": {
        "speed": 15.3,
        "direction": 45.2,
        "image_direction": 45.0
      }
    },
    "sensor_data": {
      "accelerometer": {
        "x": 0.02,
        "y": -0.01,
        "z": 0.98
      },
      "gyroscope": {
        "x": 0.1,
        "y": -0.05,
        "z": 0.02
      }
    },
    "manufacturer_specific": {
      "dji": {
        "Aircraft-Location": "34.0522,-118.2437,120.5",
        "Aircraft-Altitude": 120.5,
        "Flight-Mode": "P-Mode",
        "Gimbal-Data": "-12.5,0.0,0.1",
        "Speed-X": 15.3,
        "Speed-Y": -2.1,
        "Speed-Z": 0.5
      }
    }
  }
}
```

### Dependencies
- ExifTool with DJI/GoPro support
- Available when processing image/video files

### Usage Notes
- Automatically processes drone-captured media
- Requires Super tier for full access
- Extracts manufacturer-specific telemetry

## Blockchain Provenance Engine

### Purpose
The Blockchain Provenance Engine extracts blockchain and content authenticity metadata including NFT information and C2PA (Content Authenticity Initiative) manifests.

### Capabilities
- **C2PA content authenticity** manifests
- **Digital signatures** and provenance chains
- **NFT metadata** and token information
- **Blockchain references** and transaction data
- **Content credentials** and origin verification

### Implementation
The engine is automatically invoked when processing files with blockchain metadata with the Super tier.

### Output Structure
```json
{
  "blockchain_provenance": {
    "available": true,
    "c2pa_manifest": {
      "c2pa:ingredient": "data:application/c2pa-manifest;...",
      "c2pa:manifest": "data:application/c2pa-manifest;...",
      "c2pa:signature": "signature_data_here"
    },
    "digital_signatures": {
      "signature_count": 1,
      "signature_valid": true,
      "certificate_chain": ["cert1", "cert2"]
    },
    "nft_metadata": {
      "token_id": "12345",
      "contract_address": "0x1234...",
      "blockchain": "ethereum",
      "collection_name": "Digital Art Collection",
      "attributes": {
        "rarity": "epic",
        "trait_count": 12
      }
    },
    "content_credentials": {
      "creator": "Artist Name",
      "creation_tool": "Adobe Photoshop",
      "modification_history": ["edited", "enhanced"],
      "authenticity_verified": true
    },
    "blockchain_references": {
      "ethereum_transaction": "0xabc123...",
      "ipfs_hash": "QmHash...",
      "arweave_id": "arId123"
    }
  }
}
```

### Dependencies
- ExifTool for XMP metadata extraction
- Available when processing files with blockchain metadata

### Usage Notes
- Automatically processes files with blockchain metadata
- Requires Super tier for full access
- Extracts content authenticity information

## Emerging Technology Engine

### Purpose
The Emerging Technology Engine provides metadata extraction for cutting-edge technologies including AI/ML models, quantum computing, IoT devices, and more.

### Capabilities
- **AI/ML model metadata** (formats: .h5, .pb, .pth, .onnx, etc.)
- **Quantum computing metadata** (formats: .qasm, .qc, .qobj, etc.)
- **IoT device metadata** (sensor configs, telemetry, etc.)
- **Neural network metadata** (architectures, training configs)
- **Robotics metadata** (URDF, SDF, ROS configs)
- **Biotechnology metadata** (genomics, proteomics, drug discovery)

### Implementation
The engine is automatically invoked when processing files from emerging technology domains with the Super tier.

### Output Structure
```json
{
  "emerging_technology": {
    "available": true,
    "ai_ml": {
      "model_format": "TensorFlow",
      "input_shape": [1, 224, 224, 3],
      "output_shape": [1, 1000],
      "parameters": 25600000,
      "framework": "TensorFlow 2.13",
      "training_data": "ImageNet",
      "accuracy": 0.76,
      "flops": 4100000000
    },
    "quantum": {
      "qasm_version": "2.0",
      "qubit_count": 5,
      "gate_count": 120,
      "circuit_depth": 25,
      "algorithm": "Variational Quantum Eigensolver"
    },
    "iot": {
      "device_type": "Temperature Sensor",
      "firmware_version": "1.2.3",
      "sensor_type": "DS18B20",
      "calibration_date": "2024-06-15",
      "last_telemetry": "2024-12-31T10:30:45Z",
      "telemetry_data": {
        "temperature": 23.5,
        "humidity": 45.2,
        "battery_level": 87
      }
    }
  }
}
```

### Dependencies
- Various domain-specific libraries loaded dynamically
- Available when processing emerging technology files

### Usage Notes
- Automatically processes files from emerging technology domains
- Requires Super tier for full access
- Extensible architecture for new technology domains

## Engine Integration

### Tier-Based Access Control
Each specialized engine is controlled by the tier configuration system:

```python
from server.extractor.comprehensive_metadata_engine import COMPREHENSIVE_TIER_CONFIGS, Tier

# Check if medical imaging is available for premium tier
config = COMPREHENSIVE_TIER_CONFIGS[Tier.PREMIUM]
if config.medical_imaging:
    # Medical imaging engine will be invoked
    pass
```

### File Type Detection
Engines are automatically selected based on file extension and MIME type:

```python
# DICOM files trigger medical imaging engine
if file_ext in ['.dcm', '.dicom']:
    # MedicalImagingEngine processes the file
    
# FITS files trigger astronomical data engine  
elif file_ext in ['.fits', '.fit', '.fts']:
    # AstronomicalDataEngine processes the file
```

### Performance Considerations
- Engines are loaded on-demand to minimize memory usage
- Processing is parallelized when possible
- Results are cached for repeated extractions
- Resource-intensive engines are skipped for lower tiers

## Error Handling

Each engine implements comprehensive error handling:

```python
try:
    result = engine.extract_fits_metadata(filepath)
    if result and result.get("available"):
        # Process successful result
        pass
    else:
        # Handle unavailable or failed extraction
        pass
except Exception as e:
    # Engine-specific error handling
    error_result = {"available": False, "error": str(e)}
```

## Extending the Engine System

New specialized engines can be added by following the established pattern:

1. Create a new engine class with appropriate methods
2. Add the engine to the ComprehensiveMetadataExtractor
3. Update the tier configuration
4. Register the engine in the extraction flow
5. Update documentation

This modular approach allows for continuous expansion of the extraction capabilities while maintaining a consistent interface.
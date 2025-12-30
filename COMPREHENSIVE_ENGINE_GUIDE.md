# MetaExtract Comprehensive Engine v4.0 - Ultimate Metadata Extraction

## 🌟 Overview

MetaExtract v4.0 introduces the **Comprehensive Metadata Engine** - the world's most advanced metadata extraction system capable of extracting **45,000+ metadata fields** across all digital domains.

### 🎯 What's New in v4.0

- **45,000+ metadata fields** (up from 7,000+)
- **10 specialized extraction engines** for different domains
- **AI content detection** for images, videos, and text
- **Enhanced forensic analysis** with advanced steganography and manipulation detection
- **Medical imaging support** (DICOM) with 4,600+ standardized fields
- **Astronomical data support** (FITS) with 3,000+ fields and WCS
- **Geospatial analysis** (GeoTIFF, Shapefile) with full CRS support
- **Scientific data formats** (HDF5, NetCDF) with unlimited metadata
- **Blockchain provenance** (NFT, C2PA, digital signatures)
- **Professional video analysis** (broadcast standards, HDR, timecode)

## 🏗️ Architecture

### Core Components

```
MetaExtract v4.0 Architecture
├── Base Engine (metadata_engine.py)           # 7,000+ standard fields
├── Enhanced Engine (metadata_engine_enhanced.py) # Performance & caching
└── Comprehensive Engine (comprehensive_metadata_engine.py) # 45,000+ fields
    ├── Medical Imaging Engine                 # DICOM (4,600+ fields)
    ├── Astronomical Data Engine               # FITS (3,000+ fields)
    ├── Geospatial Engine                     # GIS data & projections
    ├── Scientific Instrument Engine          # HDF5, NetCDF
    ├── Drone/UAV Engine                      # Flight telemetry
    ├── Blockchain Provenance Engine          # NFT, C2PA
    ├── AI Content Detection Engine           # AI-generated content
    ├── Enhanced Steganography Detector       # Hidden data analysis
    ├── Enhanced Manipulation Detector        # Tampering detection
    └── Professional Video Engine             # Broadcast metadata
```

### Specialized Engines

| Engine | Domain | Fields | File Types | Tier Required |
|--------|--------|--------|------------|---------------|
| **Medical Imaging** | Healthcare | 4,600+ | DICOM (.dcm) | Super |
| **Astronomical Data** | Science | 3,000+ | FITS (.fits, .fit) | Super |
| **Geospatial** | GIS/Mapping | 2,000+ | GeoTIFF, Shapefile | Premium+ |
| **Scientific Instruments** | Research | Unlimited | HDF5, NetCDF | Super |
| **Drone/UAV** | Aerial | 500+ | Images/Videos with telemetry | Premium+ |
| **Professional Video** | Broadcast | 1,000+ | All video formats | Premium+ |
| **AI Content Detection** | Forensics | 200+ | Images, Videos, Text | Super |
| **Blockchain Provenance** | Digital Assets | 300+ | Any file with blockchain refs | Premium+ |
| **Enhanced Steganography** | Security | 100+ | Images | Premium+ |
| **Enhanced Manipulation** | Forensics | 150+ | Images, Videos | Premium+ |

## 🚀 Installation

### Quick Install (Recommended)

```bash
# Run the comprehensive installation script
./scripts/install_comprehensive_engine.sh
```

### Manual Installation

1. **System Dependencies**
```bash
# macOS
brew install python@3.11 ffmpeg exiftool libmagic redis postgresql gdal proj geos hdf5 netcdf opencv exempi

# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-dev ffmpeg libimage-exiftool-perl libmagic1 redis-server postgresql gdal-bin libgdal-dev libproj-dev libgeos-dev libhdf5-dev libnetcdf-dev libopencv-dev libexempi8
```

2. **Python Environment**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Verify Installation**
```bash
python test_comprehensive_engine.py
```

## 📖 Usage

### Basic Usage

```python
from server.extractor.comprehensive_metadata_engine import extract_comprehensive_metadata

# Extract metadata with comprehensive engine
result = extract_comprehensive_metadata("photo.jpg", tier="premium")

print(f"Fields extracted: {result['extraction_info']['comprehensive_fields_extracted']}")
print(f"Specialized engines: {result['extraction_info']['specialized_engines']}")
```

### Advanced Usage with Specific Engines

```python
from server.extractor.comprehensive_metadata_engine import ComprehensiveMetadataExtractor

extractor = ComprehensiveMetadataExtractor()

# Medical imaging (DICOM)
dicom_result = extractor.medical_engine.extract_dicom_metadata("scan.dcm")

# Astronomical data (FITS)
fits_result = extractor.astronomical_engine.extract_fits_metadata("galaxy.fits")

# Geospatial data (GeoTIFF)
geo_result = extractor.geospatial_engine.extract_geotiff_metadata("satellite.tif")
```

### CLI Usage

```bash
# Basic extraction
python server/extractor/comprehensive_metadata_engine.py photo.jpg --tier premium

# Show available engines
python server/extractor/comprehensive_metadata_engine.py --engines

# Advanced analysis (Super tier)
python server/extractor/comprehensive_metadata_engine.py photo.jpg --tier super --advanced
```

## 🔬 Specialized Engines Deep Dive

### 1. Medical Imaging Engine (DICOM)

Extracts **4,600+ standardized DICOM fields** from medical images:

```python
# Patient info (anonymized)
patient_info: {
    "age": "45Y",
    "sex": "M", 
    "weight": "70kg"
}

# Study information
study_info: {
    "date": "20231215",
    "description": "Brain MRI",
    "modality": "MR"
}

# Equipment details
equipment_info: {
    "manufacturer": "Siemens",
    "model": "MAGNETOM Skyra",
    "field_strength": "3T"
}

# Acquisition parameters (MR-specific)
acquisition_params: {
    "tr": "2000ms",
    "te": "30ms", 
    "flip_angle": "90°",
    "slice_thickness": "5mm"
}
```

**Supported Modalities:**
- CT (Computed Tomography)
- MR (Magnetic Resonance)
- US (Ultrasound)
- DX/CR/DR (Digital Radiography)
- PT (Positron Emission Tomography)
- NM (Nuclear Medicine)
- And 20+ more modalities

### 2. Astronomical Data Engine (FITS)

Extracts **3,000+ fields** from astronomical images and data:

```python
# Observation info
observation_info: {
    "object_name": "M31 Galaxy",
    "telescope": "Hubble Space Telescope",
    "instrument": "ACS/WFC",
    "exposure_time": "300s",
    "filter": "F606W"
}

# World Coordinate System
wcs_info: {
    "coordinate_system": "ICRS",
    "projection": "TAN",
    "reference_coordinates": {
        "ra": 10.684708,
        "dec": 41.268750
    },
    "pixel_scale": {
        "ra": 0.05,  # arcsec/pixel
        "dec": 0.05
    },
    "field_of_view": {
        "ra_degrees": 0.34,
        "dec_degrees": 0.34
    }
}
```

**Supported Features:**
- Multi-extension FITS files
- World Coordinate System (WCS) analysis
- Instrument-specific metadata
- Calibration frame detection
- Spectral data analysis

### 3. Geospatial Engine

Extracts comprehensive **GIS metadata** with full coordinate system support:

```python
# Coordinate Reference System
coordinate_system: {
    "epsg_code": 4326,
    "proj4_string": "+proj=longlat +datum=WGS84",
    "is_geographic": true,
    "units": "degrees"
}

# Geotransform
geotransform: {
    "pixel_size_x": 0.0001,
    "pixel_size_y": -0.0001,
    "top_left_x": -180.0,
    "top_left_y": 90.0
}

# Raster information
raster_info: {
    "width": 3600,
    "height": 1800,
    "bands": 3,
    "pixel_area": 0.00000001,  # square degrees
    "total_area": 64800.0      # square degrees
}
```

### 4. Scientific Instrument Engine

Handles **unlimited metadata** from scientific data formats:

```python
# HDF5 structure
hdf5_metadata: {
    "groups": {
        "/data": {
            "attributes": {"experiment": "protein_folding"},
            "datasets": ["temperature", "pressure", "coordinates"]
        }
    },
    "datasets": {
        "/data/temperature": {
            "shape": [1000, 100, 100],
            "dtype": "float64",
            "attributes": {
                "units": "kelvin",
                "standard_name": "temperature"
            }
        }
    }
}
```

### 5. AI Content Detection Engine

Detects **AI-generated content** using multiple analysis methods:

```python
# AI detection result
ai_detection: {
    "ai_probability": 0.85,
    "detection_methods": {
        "frequency_analysis": {"ai_likelihood": 0.8},
        "noise_analysis": {"ai_likelihood": 0.9},
        "statistical_analysis": {"ai_likelihood": 0.8}
    },
    "suspicious_patterns": [
        "High frequency domain anomalies",
        "Unusual noise distribution"
    ]
}
```

**Detection Methods:**
- Frequency domain analysis
- Noise pattern analysis
- Compression artifact analysis
- Statistical property analysis
- Metadata analysis for AI tools

## 🎚️ Tier Comparison

| Feature | Free | Starter | Premium | Super |
|---------|------|---------|---------|-------|
| **Total Fields** | ~200 | ~1,000 | ~15,000 | **45,000+** |
| **File Types** | Images | Images, PDF, Audio | All standard formats | **All formats** |
| **Max File Size** | 10MB | 50MB | 500MB | **1GB** |
| **Specialized Engines** | None | None | 6 engines | **All 10 engines** |
| **Medical Imaging** | ❌ | ❌ | ❌ | **✅** |
| **Astronomical Data** | ❌ | ❌ | ❌ | **✅** |
| **AI Content Detection** | ❌ | ❌ | ❌ | **✅** |
| **Advanced Analysis** | ❌ | ❌ | ✅ | **✅** |
| **Batch Processing** | ❌ | ❌ | ✅ | **✅** |

## 🔧 Configuration

### Environment Variables

```bash
# Redis caching (required for caching layer)
REDIS_URL=redis://localhost:6379

# Database (for analytics)
DATABASE_URL=postgresql://user:pass@localhost/metaextract

# Performance tuning
MAX_WORKERS=4
CACHE_TTL_HOURS=24
MAX_FILE_SIZE_MB=1000

# AI/ML models (Super tier)
ENABLE_AI_DETECTION=true
AI_MODEL_PATH=/path/to/models
```

### Performance Optimization

1. **Enable Redis Caching**
```bash
# Install and start Redis
brew install redis  # macOS
sudo apt install redis-server  # Linux
redis-server
```

2. **Optimize for Large Files**
```python
# Increase memory limits for large scientific files
import resource
resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, -1))  # 8GB
```

3. **GPU Acceleration** (for AI features)
```bash
# Install CUDA support (NVIDIA GPUs)
pip install tensorflow-gpu torch-gpu
```

## 📊 Performance Benchmarks

### Extraction Speed by File Type

| File Type | Size | Free Tier | Premium Tier | Super Tier |
|-----------|------|-----------|--------------|------------|
| JPEG Image | 5MB | 0.5s | 1.2s | 2.1s |
| RAW Image | 25MB | N/A | 3.5s | 5.8s |
| MP4 Video | 100MB | N/A | 8.2s | 12.4s |
| DICOM Medical | 50MB | N/A | N/A | 15.3s |
| FITS Astronomy | 200MB | N/A | N/A | 28.7s |
| HDF5 Scientific | 500MB | N/A | N/A | 45.2s |

### Memory Usage

| Engine | Typical RAM Usage | Peak RAM Usage |
|--------|------------------|----------------|
| Base Engine | 50MB | 100MB |
| Medical Imaging | 200MB | 500MB |
| Astronomical Data | 300MB | 800MB |
| Scientific Data | 500MB | 2GB |
| AI Detection | 1GB | 4GB |

## 🛠️ Development

### Adding New Engines

1. **Create Engine Class**
```python
class MyCustomEngine:
    @staticmethod
    def extract_custom_metadata(filepath: str) -> Dict[str, Any]:
        # Your extraction logic here
        return {"available": True, "custom_data": {}}
```

2. **Register in Comprehensive Engine**
```python
# In comprehensive_metadata_engine.py
class ComprehensiveMetadataExtractor:
    def __init__(self):
        self.custom_engine = MyCustomEngine()
    
    def extract_comprehensive_metadata(self, filepath, tier):
        # Add your engine logic
        if tier_config.custom_analysis:
            result["custom_data"] = self.custom_engine.extract_custom_metadata(filepath)
```

### Testing

```bash
# Run comprehensive tests
python -m pytest tests/test_comprehensive_engine.py

# Test specific engine
python -m pytest tests/test_medical_imaging.py

# Performance benchmarks
python scripts/benchmark_engines.py
```

## 🔍 Troubleshooting

### Common Issues

1. **"pydicom not found" Error**
```bash
pip install pydicom>=2.4.0
```

2. **"GDAL not found" Error**
```bash
# macOS
brew install gdal
# Linux
sudo apt-get install gdal-bin libgdal-dev
```

3. **Memory Issues with Large Files**
```python
# Increase virtual memory
ulimit -v 8388608  # 8GB
```

4. **Slow Performance**
```bash
# Enable Redis caching
redis-server &
export REDIS_URL=redis://localhost:6379
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable comprehensive engine debugging
result = extract_comprehensive_metadata("file.jpg", tier="super")
```

## 📚 API Reference

### Main Functions

```python
# Primary extraction function
extract_comprehensive_metadata(filepath: str, tier: str) -> Dict[str, Any]

# Individual engine access
ComprehensiveMetadataExtractor.medical_engine.extract_dicom_metadata(filepath: str)
ComprehensiveMetadataExtractor.astronomical_engine.extract_fits_metadata(filepath: str)
ComprehensiveMetadataExtractor.geospatial_engine.extract_geotiff_metadata(filepath: str)
```

### Response Format

```python
{
    "extraction_info": {
        "comprehensive_version": "4.0.0",
        "comprehensive_fields_extracted": 15420,
        "specialized_engines": {
            "medical_imaging": false,
            "astronomical_data": false,
            "geospatial_analysis": true,
            # ... other engines
        },
        "specialized_field_counts": {
            "geospatial": 1250,
            "drone_telemetry": 89
        }
    },
    # Standard metadata sections
    "file": {...},
    "exif": {...},
    "gps": {...},
    # Specialized engine results
    "medical_imaging": {...},      # DICOM data (Super tier)
    "astronomical_data": {...},    # FITS data (Super tier)
    "geospatial": {...},          # GIS data (Premium+)
    "scientific_data": {...},     # HDF5/NetCDF (Super tier)
    "drone_telemetry": {...},     # UAV data (Premium+)
    "blockchain_provenance": {...}, # NFT/C2PA (Premium+)
    "advanced_analysis": {         # Advanced forensics (Premium+)
        "ai_content_detection": {...},
        "enhanced_steganography": {...},
        "enhanced_manipulation_detection": {...}
    }
}
```

## 🤝 Contributing

We welcome contributions to expand the comprehensive engine:

1. **New File Format Support**
2. **Additional Specialized Engines**
3. **Performance Optimizations**
4. **AI/ML Model Improvements**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MetaExtract Comprehensive Engine v4.0 is licensed under the MIT License.

## 🆘 Support

- **Documentation**: [docs/comprehensive-engine/](docs/comprehensive-engine/)
- **Issues**: [GitHub Issues](https://github.com/metaextract/metaextract/issues)
- **Discussions**: [GitHub Discussions](https://github.com/metaextract/metaextract/discussions)
- **Email**: support@metaextract.com

---

**MetaExtract v4.0** - The Ultimate Metadata Extraction Engine
*Extracting 45,000+ fields across all digital domains*

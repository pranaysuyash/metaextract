# MetaExtract Tier Configuration and Access Control Documentation

## Overview

The MetaExtract system implements a sophisticated tier-based access control system that determines which metadata fields and specialized engines are available to users based on their subscription level. This system ensures that users receive appropriate access to metadata extraction capabilities while maintaining a sustainable business model.

## Tier Structure

The system supports four distinct tiers, each with increasing levels of access:

### Free Tier
- **Target users**: Casual users, evaluation
- **Metadata fields**: ~50 basic fields
- **File types**: JPEG, PNG, GIF, WebP
- **Access level**: Limited to basic EXIF and file system metadata

### Starter Tier
- **Target users**: Individual users, small projects
- **Metadata fields**: ~200 fields
- **File types**: All Free tier types plus RAW, PDF, Audio
- **Access level**: Extended metadata including GPS, hashes, basic forensics

### Premium Tier
- **Target users**: Professional users, businesses
- **Metadata fields**: 7,000+ fields
- **File types**: All Starter tier types plus Video
- **Access level**: Full EXIF, MakerNotes, IPTC/XMP, video/audio details, batch processing

### Super Tier
- **Target users**: Enterprise, research institutions
- **Metadata fields**: 45,000+ fields
- **File types**: All Premium tier types plus specialized formats
- **Access level**: All specialized engines, comprehensive extraction, emerging technologies

## Tier Configuration System

### Base Tier Configuration

The base tier configuration is defined in the original metadata engine:

```python
from enum import Enum
from dataclasses import dataclass

class Tier(Enum):
    FREE = "free"
    STARTER = "starter"
    PREMIUM = "premium"
    SUPER = "super"

@dataclass
class TierConfig:
    file_hashes: bool = False
    filesystem_details: bool = False
    calculated_fields: bool = False
    gps_data: bool = False
    makernotes: bool = False
    iptc_xmp: bool = False
    perceptual_hashes: bool = False
    thumbnails: bool = False
    video_encoding: bool = False
    audio_details: bool = False
    pdf_details: bool = False
    extended_attributes: bool = False
    raw_exif: bool = False
    forensic_details: bool = False
    serial_numbers: bool = False
    exiftool_enhanced: bool = False
    burned_metadata: bool = False
    metadata_comparison: bool = False
    # Phase 2 toggles
    video_codec_details: bool = False
    container_details: bool = False
    audio_codec_details: bool = False
    scientific_details: bool = False
    # Phase 3 toggles
    pdf_complete: bool = False
    office_documents: bool = False
    web_social_metadata: bool = False
    email_metadata: bool = False
    # Phase 4 toggles
    ai_ml_metadata: bool = False
    blockchain_nft_metadata: bool = False
    ar_vr_metadata: bool = False
    iot_metadata: bool = False
    quantum_metadata: bool = False
    neural_network_metadata: bool = False
    robotics_metadata: bool = False
    autonomous_metadata: bool = False
    biotechnology_metadata: bool = False

TIER_CONFIGS = {
    Tier.FREE: TierConfig(),
    Tier.STARTER: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, audio_details=True, pdf_details=True, forensic_details=True,
        perceptual_hashes=True, thumbnails=True,
    ),
    Tier.PREMIUM: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True,
        raw_exif=True, forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        burned_metadata=True, metadata_comparison=True,
        # Phase 2 capabilities enabled for Premium
        video_codec_details=True, container_details=True, audio_codec_details=True,
        scientific_details=True,
        # Phase 3 capabilities
        pdf_complete=True,
        office_documents=True,
        web_social_metadata=True,
        email_metadata=True,
        # Phase 4 capabilities
        ai_ml_metadata=True,
        blockchain_nft_metadata=True,
        ar_vr_metadata=True,
        iot_metadata=True,
        quantum_metadata=True,
        neural_network_metadata=True,
        robotics_metadata=True,
        autonomous_metadata=True,
        biotechnology_metadata=True,
    ),
    Tier.SUPER: TierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True,
        raw_exif=True, forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        burned_metadata=True, metadata_comparison=True,
        video_codec_details=True, container_details=True, audio_codec_details=True,
        scientific_details=True,
    ),
}
```

### Comprehensive Tier Configuration

The comprehensive engine extends this with specialized engine access controls:

```python
@dataclass
class ComprehensiveTierConfig:
    # Base features (from original engine)
    file_hashes: bool = False
    filesystem_details: bool = False
    # ... (all base features)
    
    # Comprehensive features
    medical_imaging: bool = False          # DICOM extraction
    astronomical_data: bool = False        # FITS extraction
    geospatial_analysis: bool = False      # GIS/mapping data
    scientific_instruments: bool = False   # Lab equipment data
    drone_telemetry: bool = False         # UAV flight data
    professional_video: bool = False      # Broadcast/cinema metadata
    advanced_audio: bool = False          # Spectral analysis, broadcast audio
    blockchain_provenance: bool = False    # NFT, C2PA, digital signatures
    social_media_context: bool = False    # Platform-specific metadata
    mobile_sensors: bool = False          # Smartphone sensor data
    web_metadata: bool = False            # HTML, schema.org, Open Graph
    steganography_detection: bool = False # Hidden data analysis
    manipulation_detection: bool = False   # Image/video tampering
    timeline_reconstruction: bool = False  # Forensic timeline analysis
    batch_comparison: bool = False        # Multi-file analysis
    ai_content_detection: bool = False    # AI-generated content detection
    emerging_technology: bool = False     # AI/ML models, quantum, XR, IoT, etc.
    advanced_video_analysis: bool = False # Professional video analysis
    advanced_audio_analysis: bool = False # Professional audio analysis
    document_analysis: bool = False       # Office, PDF, web documents
    scientific_research: bool = False     # Research papers, lab data, microscopy, spectroscopy
    multimedia_entertainment: bool = False # Gaming, streaming, digital art, music production
    industrial_manufacturing: bool = False # CAD, CNC, quality control, IoT sensors
    financial_business: bool = False      # Financial reports, trading data, banking, compliance
    healthcare_medical: bool = False      # EHR, DICOM, clinical trials, medical devices
    transportation_logistics: bool = False # Vehicle telemetry, GPS tracking, supply chain
    education_academic: bool = False      # LMS, educational content, academic research
    legal_compliance: bool = False        # Legal documents, regulatory compliance, IP
    environmental_sustainability: bool = False # Environmental monitoring, climate data, ESG
    social_media_digital: bool = False    # Social media posts, digital marketing, messaging
    gaming_entertainment: bool = False    # Video games, esports, streaming, interactive media

COMPREHENSIVE_TIER_CONFIGS = {
    Tier.FREE: ComprehensiveTierConfig(),
    Tier.STARTER: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, audio_details=True, pdf_details=True, forensic_details=True,
        perceptual_hashes=True, thumbnails=True, web_metadata=True,
    ),
    Tier.PREMIUM: ComprehensiveTierConfig(
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True,
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        # Premium additions
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
    ),
    Tier.SUPER: ComprehensiveTierConfig(
        # All Premium features plus:
        file_hashes=True, filesystem_details=True, calculated_fields=True,
        gps_data=True, makernotes=True, iptc_xmp=True, video_encoding=True,
        audio_details=True, pdf_details=True, extended_attributes=True,
        perceptual_hashes=True, thumbnails=True, raw_exif=True,
        forensic_details=True, serial_numbers=True, exiftool_enhanced=True,
        geospatial_analysis=True, drone_telemetry=True, advanced_audio=True,
        web_metadata=True, mobile_sensors=True, steganography_detection=True,
        timeline_reconstruction=True, batch_comparison=True,
        # Super exclusive features
        medical_imaging=True, astronomical_data=True, scientific_instruments=True,
        professional_video=True, blockchain_provenance=True, social_media_context=True,
        manipulation_detection=True, ai_content_detection=True, emerging_technology=True,
        advanced_video_analysis=True, advanced_audio_analysis=True, document_analysis=True,
        scientific_research=True, multimedia_entertainment=True, industrial_manufacturing=True,
        financial_business=True, healthcare_medical=True, transportation_logistics=True,
        education_academic=True, legal_compliance=True, environmental_sustainability=True,
        social_media_digital=True, gaming_entertainment=True,
    ),
}
```

## Access Control Implementation

### Feature-Based Access Control

The system implements feature-based access control where each metadata field or engine is gated by the corresponding tier configuration:

```python
def extract_metadata(filepath: str, tier: str = "super") -> Dict[str, Any]:
    # Get tier configuration
    tier_enum = Tier(tier.lower())
    tier_config = TIER_CONFIGS[tier_enum]
    
    result = {"locked_fields": []}
    
    # Conditional extraction based on tier
    if tier_config.file_hashes:
        result["hashes"] = extract_file_hashes(filepath)
    else:
        result["hashes"] = {"_locked": True}
        result["locked_fields"].append("hashes")
    
    if tier_config.makernotes:
        result["makernote"] = extract_makernotes(filepath)
    else:
        result["makernote"] = {"_locked": True}
        result["locked_fields"].append("makernote")
    
    # Similar pattern for all features...
    
    return result
```

### Specialized Engine Access Control

For the comprehensive engine, specialized engines are controlled similarly:

```python
def extract_comprehensive_metadata(filepath: str, tier: str = "super"):
    # Get comprehensive tier configuration
    tier_enum = Tier(tier.lower())
    tier_config = COMPREHENSIVE_TIER_CONFIGS[tier_enum]
    
    # Medical imaging access control
    if tier_config.medical_imaging and file_ext in ['.dcm', '.dicom']:
        dicom_result = medical_engine.extract_dicom_metadata(filepath)
        if dicom_result and dicom_result.get("available"):
            base_result["medical_imaging"] = dicom_result
    
    # Astronomical data access control
    if tier_config.astronomical_data and file_ext in ['.fits', '.fit', '.fts']:
        fits_result = astronomical_engine.extract_fits_metadata(filepath)
        # ... process result
    
    # Similar pattern for all specialized engines...
```

## Tier-Specific Behavior

### Free Tier Limitations

The Free tier has significant limitations:

- **Limited file types**: Only basic image formats (JPEG, PNG, GIF, WebP)
- **Basic metadata only**: No MakerNotes, IPTC/XMP, video, or advanced features
- **No specialized engines**: Medical, astronomical, geospatial engines disabled
- **No exiftool**: Enhanced extraction features unavailable
- **Limited fields**: ~50 basic fields only

### Starter Tier Enhancements

The Starter tier adds:

- **Extended file support**: RAW, PDF, Audio formats
- **GPS data**: Location information extraction
- **File hashes**: MD5, SHA256, etc.
- **Calculated fields**: Aspect ratios, file age, etc.
- **Basic forensics**: File integrity checks
- **Web metadata**: HTML/schema.org extraction

### Premium Tier Capabilities

The Premium tier provides:

- **Full EXIF support**: Complete EXIF data extraction
- **MakerNote parsing**: Parsed manufacturer-specific data
- **IPTC/XMP**: Complete metadata standards support
- **Video extraction**: Complete video metadata
- **Audio details**: Complete audio metadata
- **PDF details**: Complete PDF metadata
- **Extended attributes**: File system extended attributes
- **Batch processing**: Multiple file processing
- **Advanced forensics**: Enhanced analysis features

### Super Tier Comprehensive Access

The Super tier includes everything plus:

- **All specialized engines**: Medical, astronomical, geospatial, etc.
- **45,000+ fields**: Comprehensive extraction
- **Emerging technologies**: AI/ML, quantum, IoT, etc.
- **Advanced analysis**: Steganography, manipulation detection
- **Blockchain provenance**: NFT and C2PA metadata
- **Research capabilities**: Scientific instrument data

## Implementation Details

### Tier Validation

The system validates tier access at multiple levels:

```python
def validate_tier_access(tier: str) -> Tier:
    """Validate and normalize tier input"""
    try:
        return Tier(tier.lower())
    except ValueError:
        # Default to Super tier for invalid inputs
        return Tier.SUPER

def check_feature_access(tier_config: TierConfig, feature_name: str) -> bool:
    """Check if a specific feature is available for the tier"""
    return getattr(tier_config, feature_name, False)
```

### Locked Field Indication

When features are not available for a tier, the system returns locked indicators:

```python
# Instead of returning actual data
result["makernote"] = {"_locked": True}
result["locked_fields"].append("makernotes")

# This allows the frontend to understand what's unavailable
```

### Performance Optimization

The tier system is designed for performance:

- **Early validation**: Tier checks happen early in the process
- **Conditional processing**: Features are only processed if available
- **Caching**: Results are cached by tier to avoid redundant processing
- **Resource management**: Lower-tier requests use fewer resources

## Business Logic Integration

### Pricing Tiers

The technical tier configuration aligns with business pricing:

| Tier        | Price  | File Types                   | Fields | Key Features                 |
| ----------- | ------ | ---------------------------- | ------ | ---------------------------- |
| **Free**    | $0     | Images (JPG, PNG, GIF, WebP) | ~50    | Basic EXIF, 10MB limit       |
| **Starter** | $5/mo  | + RAW, PDF, Audio            | ~200   | GPS, hashes, forensics       |
| **Pro**     | $27/mo | + Video, all formats         | 7000+  | MakerNotes, IPTC, XMP, batch |
| **Super**   | $99/mo | All + API                    | 45000+ | All specialized engines      |

### Usage Tracking

The system can track usage by tier:

```python
def track_usage(filepath: str, tier: str, result: Dict[str, Any]):
    """Track usage for billing and analytics"""
    extracted_fields = result.get("extraction_info", {}).get("fields_extracted", 0)
    processing_time = result.get("extraction_info", {}).get("processing_ms", 0)
    
    # Log usage for the specific tier
    log_usage(tier, extracted_fields, processing_time)
```

## API Integration

### Tier Parameter

All API endpoints accept a tier parameter:

```python
# API endpoint example
@app.post("/api/extract")
async def extract_metadata_api(
    file: UploadFile = File(...),
    tier: str = Query("super", enum=["free", "starter", "premium", "super"])
):
    result = extract_comprehensive_metadata(file_path, tier=tier)
    return result
```

### Tier-Based Response Filtering

The API automatically filters responses based on tier:

```python
def filter_response_by_tier(result: Dict, tier: str) -> Dict:
    """Filter response to only include tier-accessible data"""
    tier_config = COMPREHENSIVE_TIER_CONFIGS[Tier(tier.lower())]
    
    # Remove or lock inaccessible fields
    filtered = result.copy()
    
    # Process each field based on tier configuration
    for field_name, is_available in tier_config.__dict__.items():
        if not is_available and field_name in filtered:
            filtered[field_name] = {"_locked": True}
    
    return filtered
```

## Security Considerations

### Data Privacy

The tier system maintains data privacy:

- **Anonymization**: Medical data is automatically anonymized
- **Access control**: No unauthorized access to sensitive fields
- **Audit trails**: All access is logged by tier
- **Data minimization**: Only necessary data is processed

### Resource Protection

The system protects resources:

- **Rate limiting**: Different limits per tier
- **Concurrent processing**: Tier-based concurrency limits
- **Memory management**: Tier-appropriate resource allocation
- **Dependency management**: Only load required libraries per tier

## Extensibility

### Adding New Features

New features can be added to the tier configuration:

```python
# Add new field to TierConfig
@dataclass
class TierConfig:
    # ... existing fields ...
    new_feature: bool = False  # Default to False (Free tier restriction)

# Add to tier configurations
TIER_CONFIGS = {
    Tier.FREE: TierConfig(),
    Tier.STARTER: TierConfig(
        # ... existing config ...
    ),
    Tier.PREMIUM: TierConfig(
        # ... existing config ...
        new_feature=True,  # Enable for Premium+
    ),
    Tier.SUPER: TierConfig(
        # ... existing config ...
        new_feature=True,  # Enable for Super
    ),
}

# Implement conditional access in extraction logic
if tier_config.new_feature:
    result["new_feature_data"] = extract_new_feature(filepath)
else:
    result["new_feature_data"] = {"_locked": True}
    result["locked_fields"].append("new_feature")
```

### Custom Tier Logic

The system supports custom tier logic:

```python
def apply_custom_tier_logic(result: Dict, tier: str, filepath: str):
    """Apply custom business logic based on tier"""
    if tier == "free":
        # Apply free tier restrictions
        result = apply_free_tier_restrictions(result)
    elif tier == "starter":
        # Apply starter tier enhancements
        result = apply_starter_enhancements(result)
    
    return result
```

## Monitoring and Analytics

### Tier Usage Analytics

The system tracks tier usage:

```python
def get_tier_usage_stats():
    """Get analytics on tier usage"""
    return {
        "total_requests": {
            "free": 12500,
            "starter": 3400,
            "premium": 1200,
            "super": 800
        },
        "avg_fields_extracted": {
            "free": 45,
            "starter": 180,
            "premium": 6800,
            "super": 32000
        },
        "avg_processing_time_ms": {
            "free": 120,
            "starter": 280,
            "premium": 850,
            "super": 2400
        }
    }
```

### Tier Performance Metrics

Performance metrics are tracked by tier:

```python
def get_tier_performance():
    """Get performance metrics by tier"""
    return {
        "response_times": {
            "p50": {"free": 100, "starter": 250, "premium": 700, "super": 2000},
            "p95": {"free": 180, "starter": 450, "premium": 1200, "super": 3500}
        },
        "error_rates": {
            "free": 0.001,
            "starter": 0.002,
            "premium": 0.003,
            "super": 0.005
        }
    }
```

## Best Practices

### Tier Design Principles

1. **Progressive Enhancement**: Each tier builds on the previous one
2. **Clear Value Proposition**: Each tier offers clear additional value
3. **Performance Considerations**: Higher tiers may require more resources
4. **Business Alignment**: Technical tiers align with business pricing
5. **User Experience**: Locked fields are clearly indicated to users

### Implementation Guidelines

1. **Consistent Pattern**: Use the same access control pattern throughout
2. **Default Security**: Default to locked/False for new features
3. **Clear Documentation**: Document which features are available per tier
4. **Performance Monitoring**: Monitor performance by tier
5. **Analytics Tracking**: Track usage by tier for business insights

## Troubleshooting

### Common Issues

**Feature Not Available**: Check if the requested tier has access to the feature
```python
# Verify tier configuration
config = COMPREHENSIVE_TIER_CONFIGS[Tier("premium")]
if not config.medical_imaging:
    print("Medical imaging not available for Premium tier")
```

**Unexpected Locked Fields**: Verify the tier parameter is being passed correctly
```python
# Ensure tier is properly validated
tier_enum = validate_tier_access("premium")
print(f"Tier: {tier_enum.value}")
```

**Performance Issues**: Higher tiers may require more processing time
```python
# Monitor processing time by tier
import time
start = time.time()
result = extract_comprehensive_metadata(filepath, tier="super")
processing_time = time.time() - start
print(f"Processing time: {processing_time}s")
```

This tier configuration system provides a robust, scalable approach to access control that balances user needs with business requirements while maintaining system performance and security.
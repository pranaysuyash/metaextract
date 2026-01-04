# Persona Interpretation API Documentation

## Overview

The Persona Interpretation API transforms complex technical metadata into user-friendly, context-aware answers tailored to three different user personas:

- **Sarah (Phone Photo User)**: Casual smartphone photographers who want simple, plain English answers
- **Peter (Professional Photographer)**: Technical camera users who want detailed camera settings and professional recommendations
- **Mike (Forensic Investigator)**: Forensic analysts who want chain of custody and authenticity assessments

## API Endpoints

### Main Extraction Endpoint

```
POST /api/extract
```

The persona interpretation is automatically included in the metadata response when available.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tier` | string | No | Tier level (free, professional, enterprise) - affects which persona features are available |

## Response Structure

The persona interpretation is included in the main metadata response under the `persona_interpretation` field:

```json
{
  "persona_interpretation": {
    "persona": "phone_photo_sarah",
    "key_findings": [
      "📅 Taken on 2024-01-15T14:30:45Z",
      "📍 San Francisco, CA",
      "📱 iPhone 13 Pro"
    ],
    "plain_english_answers": {
      "when_taken": {
        "answer": "January 15, 2024 at 2:30 PM",
        "details": "Photo creation date from EXIF data",
        "confidence": "high",
        "source": "exif_datetime_original"
      },
      "location": {
        "has_location": true,
        "answer": "San Francisco, CA",
        "details": "GPS coordinates from photo metadata",
        "confidence": "high",
        "coordinates": {
          "latitude": 37.7749,
          "longitude": -122.4194,
          "formatted": "37.7749° N, 122.4194° W"
        },
        "address": {
          "city": "San Francisco",
          "state": "California",
          "country": "United States",
          "formatted": "San Francisco, CA, USA"
        }
      },
      "device": {
        "answer": "iPhone 13 Pro",
        "device_type": "smartphone",
        "confidence": "high",
        "details": {
          "make": "Apple",
          "model": "iPhone 13 Pro",
          "software": "iOS 17.2"
        },
        "enhanced_info": {
          "type": "flagship_smartphone",
          "capabilities": [
            "computational_photography",
            "advanced_hdr",
            "portrait_mode"
          ],
          "image_quality_indicators": {
            "megapixels": 12,
            "sensor_type": "CMOS",
            "image_stabilization": true
          }
        }
      },
      "authenticity": {
        "answer": "Photo appears authentic",
        "assessment": "appears_authentic",
        "score": 95,
        "confidence": "high",
        "reasons": [
          "Original EXIF date/time present",
          "No software modification signatures",
          "GPS data intact",
          "Thumbnail matches main image"
        ]
      }
    }
  }
}
```

## Persona Types

### 1. Phone Photo Sarah (phone_photo_sarah)

**Target Users**: Casual smartphone photographers

**Features**:
- Simple, plain English answers to common questions
- Color-coded confidence levels (green=high, yellow=medium, red=low)
- Emoji-enhanced visual presentation
- Four key questions answered:
  - When was this photo taken?
  - Where was I when I took this?
  - What phone took this?
  - Is this photo authentic?

**Response Fields**:
```json
{
  "persona": "phone_photo_sarah",
  "key_findings": ["emoji-prefixed summary points"],
  "plain_english_answers": {
    "when_taken": {...},
    "location": {...},
    "device": {...},
    "authenticity": {...}
  }
}
```

### 2. Photographer Peter (photographer_peter)

**Target Users**: Professional photographers, photography enthusiasts

**Features**:
- Technical camera settings analysis
- Lens information and specifications
- Shooting conditions assessment
- Professional recommendations
- Image quality metrics

**Additional Response Fields**:
```json
{
  "persona": "photographer_peter",
  "key_findings": ["technical summary points"],
  "plain_english_answers": {...},
  "camera_settings": {
    "exposure": {
      "shutter_speed": "1/250",
      "aperture": "f/2.8",
      "iso": 400,
      "exposure_mode": "Manual"
    }
  },
  "lens_information": {
    "basic": {
      "model": "EF 24-70mm f/2.8L II USM"
    },
    "focal_length": {
      "actual": "50mm",
      "equivalent_35mm": "50mm"
    },
    "stabilization": {
      "enabled": true,
      "type": "optical"
    }
  },
  "shooting_conditions": {
    "lighting": "natural_daylight",
    "environment": "outdoor",
    "subject_distance": "5 meters"
  },
  "image_quality": {
    "sharpness": "high",
    "noise_level": "low",
    "dynamic_range": "good"
  },
  "professional_recommendations": [
    "Excellent use of wide aperture for subject separation",
    "Consider faster shutter speed for moving subjects",
    "Good white balance handling for mixed lighting"
  ]
}
```

### 3. Investigator Mike (investigator_mike)

**Target Users**: Forensic analysts, investigators, researchers

**Features**:
- Forensic file analysis
- Authenticity assessment with risk factors
- Manipulation detection indicators
- Chain of custody information
- Investigative recommendations

**Additional Response Fields**:
```json
{
  "persona": "investigator_mike",
  "key_findings": ["forensic summary points"],
  "plain_english_answers": {...},
  "forensic_analysis": {
    "file_characteristics": {
      "size": "2.4 MB",
      "type": "JPEG",
      "compression": "standard"
    },
    "processing_history": {
      "software": "Adobe Photoshop 2024",
      "last_modified": "2024-01-15T15:45:30Z",
      "save_count": 2
    },
    "metadata_integrity": {
      "exif_intact": true,
      "thumbnails_match": true,
      "hash_consistent": true
    }
  },
  "authenticity_assessment": {
    "overall_authenticity": {
      "assessment": "appears_authentic",
      "confidence_level": "high",
      "risk_factors": []
    },
    "manipulation_indicators": {
      "detected": false,
      "signatures": [],
      "artifacts": []
    },
    "chain_of_custody": {
      "original_filename": "IMG_2024.jpg",
      "creation_date": "2024-01-15T14:30:45Z",
      "transfer_method": "direct"
    }
  },
  "investigative_recommendations": [
    "File appears authentic with no manipulation detected",
    "EXIF data intact and consistent",
    "Suitable for evidentiary purposes",
    "Recommend preserving original file format"
  ]
}
```

## Enhanced Features

### Reverse Geocoding

GPS coordinates are automatically converted to readable addresses using OpenStreetMap Nominatim API:

```json
{
  "location": {
    "coordinates": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "formatted": "37.7749° N, 122.4194° W"
    },
    "address": {
      "city": "San Francisco",
      "state": "California",
      "country": "United States",
      "formatted": "San Francisco, CA, USA",
      "postcode": "94102",
      "street": "Market Street",
      "house_number": "123"
    }
  }
}
```

**API Used**: OpenStreetMap Nominatim (free, no API key required)

### Enhanced Device Detection

Devices are identified using pattern matching against EXIF metadata:

```json
{
  "device": {
    "answer": "iPhone 13 Pro",
    "device_type": "smartphone",
    "confidence": "high",
    "enhanced_info": {
      "type": "flagship_smartphone",
      "capabilities": [
        "computational_photography",
        "advanced_hdr",
        "portrait_mode",
        "night_mode",
        "proRAW_support"
      ],
      "image_quality_indicators": {
        "megapixels": 12,
        "sensor_type": "CMOS",
        "image_stabilization": true
      }
    }
  }
}
```

**Device Categories**:
- Smartphones (flagship, mid-range, budget)
- DSLR cameras (professional, enthusiast)
- Mirrorless cameras (full-frame, APS-C, medium format)
- Action cameras (GoPro, DJI, etc.)
- Drones (consumer, professional)
- Webcams and other devices

### Authenticity Analysis

Photos are analyzed for signs of manipulation:

```json
{
  "authenticity": {
    "answer": "Photo appears authentic",
    "assessment": "appears_authentic",
    "score": 95,
    "confidence": "high",
    "checks_performed": {
      "has_original_datetime": true,
      "has_software_signatures": false,
      "has_gps": true,
      "exif_intact": true,
      "thumbnails_match": true,
      "suspicious_signs": []
    },
    "reasons": [
      "Original EXIF date/time present",
      "No software modification signatures",
      "GPS data intact",
      "Thumbnail matches main image"
    ]
  }
}
```

**Authenticity Levels**:
- `appears_authentic` (score: 85-100): No manipulation detected
- `possibly_edited` (score: 60-84): Minor editing detected
- `possibly_modified` (score: 40-59): Moderate modifications
- `likely_modified` (score: 20-39): Heavy editing suspected
- `likely_manipulated` (score: 0-19): High probability of manipulation

## Confidence Levels

All interpretation fields include confidence assessments:

- **high**: High confidence based on clear metadata
- **medium**: Moderate confidence with some ambiguity
- **low**: Low confidence with significant missing data
- **none**: No relevant metadata available

## Frontend Integration

### React Component

The system includes a pre-built React component for displaying persona interpretation:

```tsx
import { PersonaDisplay } from '@/components/persona-display';

<PersonaDisplay interpretation={metadata.persona_interpretation} />
```

### TypeScript Types

```typescript
interface PersonaInterpretation {
  persona: 'phone_photo_sarah' | 'photographer_peter' | 'investigator_mike';
  key_findings: string[];
  plain_english_answers: {
    when_taken: PlainEnglishAnswer;
    location: LocationAnswer;
    device: DeviceAnswer;
    authenticity: AuthenticityAnswer;
  };
  // Additional persona-specific fields
  camera_settings?: CameraSettings;
  lens_information?: LensInformation;
  forensic_analysis?: ForensicAnalysis;
  // ... other persona-specific fields
}
```

## Usage Examples

### Example 1: Smartphone Photo (Sarah)

**Request**:
```bash
curl -X POST http://localhost:5000/api/extract \
  -F "file=@iphone_photo.jpg" \
  -F "tier=professional"
```

**Response**: Returns `phone_photo_sarah` persona with simple answers about when/where/device/authenticity.

### Example 2: Professional DSLR Photo (Peter)

**Request**:
```bash
curl -X POST http://localhost:5000/api/extract \
  -F "file=@canon_raw.cr2" \
  -F "tier=professional"
```

**Response**: Returns `photographer_peter` persona with technical camera settings, lens info, and professional recommendations.

### Example 3: Forensic Analysis (Mike)

**Request**:
```bash
curl -X POST http://localhost:5000/api/extract \
  -F "file=@suspect_image.jpg" \
  -F "tier=enterprise"
```

**Response**: Returns `investigator_mike` persona with forensic analysis, chain of custody, and authenticity assessment.

## Performance Considerations

- **Reverse Geocoding**: Adds ~0.5-2 seconds per request (uses external API)
- **Device Detection**: Adds ~0.1 seconds (pattern matching)
- **Authenticity Analysis**: Adds ~0.2 seconds (metadata validation)
- **Total Overhead**: ~1-3 seconds for full persona interpretation

## Tier Availability

| Feature | Free | Professional | Enterprise |
|---------|------|--------------|------------|
| Sarah (basic answers) | ✅ | ✅ | ✅ |
| Peter (technical analysis) | ❌ | ✅ | ✅ |
| Mike (forensic analysis) | ❌ | ❌ | ✅ |
| Reverse geocoding | ❌ | ✅ | ✅ |
| Enhanced device detection | ❌ | ✅ | ✅ |
| Authenticity scoring | ❌ | ✅ | ✅ |

## Error Handling

```json
{
  "persona_interpretation": {
    "error": "Unable to generate persona interpretation",
    "details": "Missing required EXIF metadata",
    "fallback_available": true,
    "basic_data": {
      "filename": "image.jpg",
      "filesize": "1.2 MB",
      "filetype": "JPEG"
    }
  }
}
```

## Implementation Details

### Backend Processing

The persona interpretation is implemented in:
- `server/extractor/persona_interpretation.py`: Core interpretation engine
- `server/extractor/comprehensive_metadata_engine.py`: Integration layer

### Frontend Display

The persona display is implemented in:
- `client/src/components/persona-display.tsx`: Main display component
- `client/src/pages/results.tsx`: Results page integration

## Future Enhancements

Planned features for future releases:
1. **Additional Personas**: Security analyst, social media manager, genealogy researcher
2. **Multi-language Support**: Spanish, French, German, Japanese
3. **Batch Processing**: Process multiple images with persona comparison
4. **Custom Personas**: User-defined interpretation templates
5. **Export Formats**: PDF reports, CSV data, JSON schemas

## Support

For API support and questions:
- GitHub Issues: [MetaExtract Issues](https://github.com/your-repo/issues)
- Documentation: [Full API Docs](https://docs.metaextract.io)
- Email: support@metaextract.io
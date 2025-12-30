# Burned-in Metadata Handling Guide

## Overview

MetaExtract now handles **two types of metadata**:

1. **Embedded Metadata** (Traditional)

   - Stored in file headers/tags (EXIF, XMP, IPTC, ID3, etc.)
   - Extractable without viewing the image
   - Can be stripped/modified without affecting image pixels

2. **Burned-in Metadata** (NEW)
   - Visually overlaid ON the image pixels
   - Requires OCR (Optical Character Recognition) to extract
   - Cannot be removed without editing the image itself
   - Common in camera apps like "GPS Map Camera"

## Why This Matters

### Problem Scenarios

1. **GPS Map Camera Apps**: Apps like "GPS Map Camera" overlay location data, maps, timestamps, weather, etc. directly onto photos
2. **Social Media**: Instagram, Snapchat add timestamps, location tags visually
3. **Security Cameras**: Burn timestamps and camera IDs into footage
4. **Watermarks**: Professional cameras may add visible metadata overlays

### Forensic Implications

- **Authenticity Verification**: Compare embedded vs burned data to detect tampering
- **Metadata Stripping**: If EXIF stripped but overlay remains, you can still extract location
- **Time/Location Conflicts**: Discrepancies between burned and embedded data indicate manipulation

## Installation

### Required: Tesseract OCR

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Verify Installation

```bash
tesseract --version
```

## Usage

### With MetaExtract API

The burned metadata extraction is **automatically enabled** for Premium and Super tiers:

```python
from server.extractor.metadata_engine import extract_metadata

# Extract with burned metadata (Premium/Super tier)
result = extract_metadata('photo.jpg', tier='premium')

# Check results
print(result['burned_metadata'])  # OCR-extracted data
print(result['metadata_comparison'])  # Comparison analysis
```

### Standalone Usage

#### Extract Burned Metadata Only

```bash
python server/extractor/modules/ocr_burned_metadata.py photo.jpg
```

Output:

```json
{
  "has_burned_metadata": true,
  "ocr_available": true,
  "extracted_text": "GPS Map Camera\nBengaluru, Karnataka, India\n...",
  "parsed_data": {
    "gps": {
      "latitude": 12.923974,
      "longitude": 77.625419,
      "google_maps_url": "https://www.google.com/maps?q=12.923974,77.625419"
    },
    "location": {
      "city": "Bengaluru",
      "state": "Karnataka",
      "country": "India"
    },
    "timestamp": "Thursday, 25/12/2025 04:48 PM GMT +05:30",
    "weather": {
      "temperature": "25.54",
      "humidity": "34"
    },
    "camera_app": "GPS Map Camera"
  },
  "confidence": "high"
}
```

#### Compare Embedded vs Burned

```python
from server.extractor.modules.metadata_comparator import compare_metadata

# You already have both extracted
embedded_data = extract_metadata('photo.jpg', tier='premium')
burned_data = embedded_data['burned_metadata']

# Compare
comparison = compare_metadata(embedded_data, burned_data)
print(comparison)
```

Output:

```json
{
  "has_both": true,
  "matches": [
    {
      "field": "gps",
      "matches": true,
      "embedded": { "latitude": 12.923974, "longitude": 77.625419 },
      "burned": { "latitude": 12.923974, "longitude": 77.625419 },
      "difference": {
        "approx_meters": 0.0
      }
    }
  ],
  "discrepancies": [],
  "summary": {
    "overall_status": "verified"
  }
}
```

## Supported Burned Metadata Fields

The OCR extractor recognizes and parses:

### Location Data

- **GPS Coordinates** (multiple formats):
  - `Lat 12.923974° Long 77.625419°`
  - `12.923974, 77.625419`
  - `N 12°55'26.3" E 77°37'31.5"`
- **Plus Codes**: `7J4VWJFG+H6`
- **Addresses**: Full street addresses with postal codes
- **City/State/Country**: Structured location names

### Timestamps

- Various date/time formats
- Timezone information (GMT offsets)
- Day of week

### Weather Data

- Temperature (°C/°F)
- Humidity (%)
- Wind speed (km/h)
- Altitude (m)

### Device/App Info

- Camera app watermarks
- Compass direction (degrees + cardinal)

## Comparison Analysis

### Status Values

The comparison returns these statuses:

#### Overall Status

- `verified` - Both sources present, data matches
- `suspicious` - Both sources present, data conflicts
- `no_overlay` - Only embedded metadata present
- `stripped_exif` - Only burned metadata present (EXIF stripped)
- `no_metadata` - Neither source has relevant metadata

#### GPS Comparison

- `match` - Coordinates match within tolerance (±111m)
- `mismatch` - Coordinates differ significantly
- `embedded_only` - GPS only in EXIF
- `burned_only` - GPS only in overlay
- `no_gps` - No GPS in either source

#### Timestamp Comparison

- `match` - Timestamps match (same date)
- `mismatch` - Timestamps differ
- `embedded_only` - Timestamp only in EXIF
- `burned_only` - Timestamp only in overlay
- `no_timestamp` - No timestamp in either source

## API Integration

### Frontend Query

```typescript
// Fetch with burned metadata
const response = await fetch('/api/metadata/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fileId: 'abc123',
    tier: 'premium',
    includeBurnedMetadata: true,
  }),
});

const data = await response.json();

// Access burned metadata
if (data.burned_metadata.has_burned_metadata) {
  console.log('GPS from overlay:', data.burned_metadata.parsed_data.gps);
  console.log('Location:', data.burned_metadata.parsed_data.location);
}

// Check comparison
if (data.metadata_comparison.overall_status === 'suspicious') {
  alert('Warning: Embedded and burned metadata do not match!');
}
```

### TypeScript Types

```typescript
interface BurnedMetadata {
  has_burned_metadata: boolean;
  ocr_available: boolean;
  extracted_text: string | null;
  parsed_data: {
    gps?: {
      latitude: number;
      longitude: number;
      google_maps_url: string;
    };
    location?: {
      city: string;
      state: string;
      country: string;
    };
    address?: string;
    plus_code?: string;
    timestamp?: string;
    weather?: {
      temperature?: string;
      humidity?: string;
      speed?: string;
      altitude?: string;
    };
    compass?: {
      degrees: string;
      direction: string;
    };
    camera_app?: string;
  };
  confidence: 'none' | 'low' | 'medium' | 'high';
}

interface MetadataComparison {
  has_both: boolean;
  has_embedded_only: boolean;
  has_burned_only: boolean;
  matches: Array<{
    field: string;
    matches: boolean;
    embedded: any;
    burned: any;
    difference?: any;
  }>;
  discrepancies: Array<{
    field: string;
    matches: false;
    warning: string;
  }>;
  warnings: string[];
  summary: {
    embedded_metadata_present: boolean;
    burned_metadata_present: boolean;
    gps_comparison: string;
    timestamp_comparison: string;
    overall_status: string;
  };
}
```

## UI Display Examples

### Simple Badge

```tsx
{
  metadata.burned_metadata.has_burned_metadata && (
    <Badge variant='info'>
      <Camera className='w-3 h-3 mr-1' />
      Overlay Detected
    </Badge>
  );
}
```

### Detailed Card

```tsx
{
  metadata.burned_metadata.has_burned_metadata && (
    <Card>
      <CardHeader>
        <CardTitle>Burned-in Metadata</CardTitle>
        <CardDescription>
          Visually overlaid on image (extracted via OCR)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {metadata.burned_metadata.parsed_data.camera_app && (
          <div className='text-sm'>
            <strong>App:</strong>{' '}
            {metadata.burned_metadata.parsed_data.camera_app}
          </div>
        )}

        {metadata.burned_metadata.parsed_data.gps && (
          <div className='text-sm mt-2'>
            <strong>GPS:</strong>{' '}
            {metadata.burned_metadata.parsed_data.gps.latitude},
            {metadata.burned_metadata.parsed_data.gps.longitude}
            <a
              href={metadata.burned_metadata.parsed_data.gps.google_maps_url}
              target='_blank'
              className='ml-2 text-blue-500'
            >
              View on Map
            </a>
          </div>
        )}

        <Badge
          variant={
            metadata.burned_metadata.confidence === 'high'
              ? 'success'
              : 'warning'
          }
        >
          {metadata.burned_metadata.confidence} confidence
        </Badge>
      </CardContent>
    </Card>
  );
}
```

### Comparison Warning

```tsx
{
  metadata.metadata_comparison?.overall_status === 'suspicious' && (
    <Alert variant='destructive'>
      <AlertTriangle className='h-4 w-4' />
      <AlertTitle>Metadata Mismatch</AlertTitle>
      <AlertDescription>
        The embedded metadata and burned overlay data do not match. This may
        indicate tampering or editing.
        <ul className='mt-2 list-disc list-inside'>
          {metadata.metadata_comparison.discrepancies.map((d, i) => (
            <li key={i}>{d.warning}</li>
          ))}
        </ul>
      </AlertDescription>
    </Alert>
  );
}
```

## Performance Considerations

### Processing Time

OCR adds processing time:

- Small images (< 2MB): +1-3 seconds
- Large images (> 5MB): +3-10 seconds
- Very large (> 20MB): +10-30 seconds

### Optimization Tips

1. **Conditional Extraction**: Only run OCR when needed

   ```python
   # Check if image likely has overlay (file from known camera app)
   if 'gps_camera' in filename.lower():
       result = extract_metadata(file, tier='premium')
   ```

2. **Async Processing**: Run OCR in background

   ```python
   import asyncio

   async def extract_with_ocr(filepath):
       return extract_burned_metadata(filepath)
   ```

3. **Region of Interest**: OCR only bottom corner where overlays typically appear
   (Future enhancement)

## Troubleshooting

### OCR Not Working

**Problem**: `ocr_available: false`

**Solution**:

```bash
# Check if Tesseract installed
tesseract --version

# If not, install it
brew install tesseract  # macOS
sudo apt install tesseract-ocr  # Linux
```

### Poor OCR Accuracy

**Problem**: `confidence: low` or incorrect data

**Causes**:

- Low image quality
- Complex backgrounds
- Small text
- Non-English text (Tesseract defaults to English)

**Solutions**:

- Use higher resolution images
- Improve image contrast
- Specify language: `tesseract image.jpg stdout -l eng+hin` (for Hindi)

### No Burned Metadata Detected

**Problem**: `has_burned_metadata: false` but overlay is visible

**Causes**:

- Text too stylized/decorative
- Overlay in unexpected format
- OCR pattern matching needs update

**Solution**: Enhance regex patterns in `ocr_burned_metadata.py`

## Tier Availability

| Feature               | Free | Starter | Premium | Super |
| --------------------- | ---- | ------- | ------- | ----- |
| Embedded metadata     | ✓    | ✓       | ✓       | ✓     |
| Burned metadata (OCR) | ✗    | ✗       | ✓       | ✓     |
| Metadata comparison   | ✗    | ✗       | ✓       | ✓     |

## Example Use Cases

### 1. Real Estate Photography

```python
# Real estate photos often have address/date overlays
result = extract_metadata('property_photo.jpg', tier='premium')

if result['burned_metadata']['parsed_data'].get('address'):
    address = result['burned_metadata']['parsed_data']['address']
    print(f"Property address: {address}")
```

### 2. Security/Surveillance

```python
# CCTV footage with timestamp burns
result = extract_metadata('security_cam.jpg', tier='premium')

timestamp = result['burned_metadata']['parsed_data'].get('timestamp')
camera_id = result['burned_metadata']['extracted_text']
```

### 3. Forensic Analysis

```python
# Verify authenticity by comparing sources
result = extract_metadata('evidence.jpg', tier='premium')

if result['metadata_comparison']['overall_status'] == 'suspicious':
    print("⚠️ ALERT: Metadata tampering suspected")
    print(result['metadata_comparison']['discrepancies'])
```

### 4. Social Media Archiving

```python
# Extract location even if EXIF stripped
result = extract_metadata('instagram_photo.jpg', tier='premium')

# Instagram strips EXIF but visual overlays remain
if result['burned_metadata']['has_burned_metadata']:
    location = result['burned_metadata']['parsed_data'].get('location')
    print(f"Original location: {location}")
```

## Future Enhancements

- [ ] Video frame OCR (extract burned metadata from video)
- [ ] Multi-language OCR support
- [ ] Machine learning for better pattern recognition
- [ ] Region-specific OCR (only scan bottom 20% of image)
- [ ] Batch processing optimization
- [ ] Custom pattern templates for specific camera apps

## Related Documentation

- [METADATA_COMPLETE_EXHAUSTIVE.md](../docs/METADATA_COMPLETE_EXHAUSTIVE.md) - All extractable fields
- [metadata_engine.py](metadata_engine.py) - Main extraction engine
- [ocr_burned_metadata.py](modules/ocr_burned_metadata.py) - OCR implementation
- [metadata_comparator.py](modules/metadata_comparator.py) - Comparison logic

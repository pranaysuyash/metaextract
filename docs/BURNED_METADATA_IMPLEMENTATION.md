# Burned Metadata Implementation Summary

## What We Built

### 🎯 Problem Solved

Your images have metadata **visually burned/overlaid** onto the pixels (like GPS maps, timestamps, location text) that traditional EXIF extraction can't read. We now extract this data using OCR.

### 📦 New Components

1. **`ocr_burned_metadata.py`** - OCR extraction module

   - Runs Tesseract OCR on images
   - Extracts text from visual overlays
   - Parses structured data (GPS, timestamps, weather, etc.)
   - Pattern matching for various formats

2. **`metadata_comparator.py`** - Comparison engine

   - Compares embedded (EXIF) vs burned (OCR) metadata
   - Detects discrepancies (potential tampering)
   - Provides security assessment
   - Returns detailed match/mismatch report

3. **Integration into `metadata_engine.py`**

   - Automatic OCR extraction for Premium/Super tiers
   - Side-by-side comparison of both metadata types
   - New fields in extraction results

4. **`test_burned_metadata.py`** - Test/demo script

   - Test OCR extraction on your images
   - See comparison results
   - Export full JSON

5. **`BURNED_METADATA_GUIDE.md`** - Complete documentation
   - Installation instructions
   - Usage examples
   - API integration
   - UI patterns
   - Troubleshooting

## What It Extracts

From your GPS Map Camera images, it will extract:

### ✅ Location Data

- GPS coordinates (multiple formats)
- City, State, Country
- Full addresses
- Plus Codes

### ✅ Timestamps

- Date and time
- Timezone info
- Day of week

### ✅ Environmental Data

- Temperature
- Humidity
- Wind speed
- Altitude
- Compass direction

### ✅ Device Info

- Camera app name/watermark

## How It Works

```
Image with overlay → Tesseract OCR → Raw text → Regex parsing → Structured data
```

```python
# Your images from GPS Map Camera
result = extract_metadata('photo.jpg', tier='premium')

# New fields in result:
{
  "burned_metadata": {
    "has_burned_metadata": true,
    "parsed_data": {
      "gps": {
        "latitude": 12.923974,
        "longitude": 77.625419,
        "google_maps_url": "..."
      },
      "location": {
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India"
      },
      "timestamp": "Thursday, 25/12/2025 04:48 PM",
      "weather": {
        "temperature": "25.54",
        "humidity": "34"
      },
      "camera_app": "GPS Map Camera"
    },
    "confidence": "high"
  },

  "metadata_comparison": {
    "overall_status": "verified",  // or "suspicious", "stripped_exif", etc.
    "matches": [...],
    "discrepancies": [...]
  }
}
```

## Key Features

### 1. Dual Extraction

- **WITH overlay**: Extracts both EXIF + OCR data
- **WITHOUT overlay**: Just EXIF data (standard extraction)

### 2. Smart Comparison

- Compares GPS coordinates (with tolerance)
- Compares timestamps
- Detects tampering/editing
- Provides security assessment

### 3. Forensic Analysis

- `verified` - Data matches across sources ✓
- `suspicious` - Data conflicts ⚠️
- `stripped_exif` - EXIF removed but overlay remains ⚠️
- `no_overlay` - Standard photo ℹ️

### 4. Flexible Patterns

Handles various GPS formats:

```
Lat 12.923974° Long 77.625419°
12.923974, 77.625419
N 12°55'26.3" E 77°37'31.5"
```

## Installation

```bash
# Install Tesseract OCR (required)
brew install tesseract  # macOS
sudo apt install tesseract-ocr  # Linux

# Verify
tesseract --version
```

## Testing

```bash
# Test on your GPS Map Camera images
cd /Users/pranay/Projects/metaextract/server
python test_burned_metadata.py /path/to/photo.jpg

# Save full JSON
python test_burned_metadata.py /path/to/photo.jpg --save
```

## Performance

- Small images: +1-3 seconds
- Large images: +3-10 seconds
- Very large: +10-30 seconds

## Tier Availability

| Feature             | Free | Starter | Premium | Super |
| ------------------- | ---- | ------- | ------- | ----- |
| Burned metadata OCR | ✗    | ✗       | ✓       | ✓     |
| Metadata comparison | ✗    | ✗       | ✓       | ✓     |

## Use Cases

### ✓ Your Scenario (GPS Map Camera)

Extract location even if EXIF stripped, verify authenticity

### ✓ Real Estate

Extract property addresses from watermarked photos

### ✓ Security/CCTV

Extract timestamps from surveillance footage

### ✓ Social Media

Extract location from Instagram/Snapchat overlays

### ✓ Forensics

Detect photo manipulation by comparing sources

## Files Modified

```
server/extractor/
├── metadata_engine.py  (MODIFIED - added OCR integration)
├── modules/
│   ├── ocr_burned_metadata.py  (NEW)
│   └── metadata_comparator.py  (NEW)
└── test_burned_metadata.py  (NEW)

docs/
└── BURNED_METADATA_GUIDE.md  (NEW)
```

## Next Steps

1. **Install Tesseract** (if not installed)

   ```bash
   brew install tesseract
   ```

2. **Test on your images**

   ```bash
   cd server
   python test_burned_metadata.py /path/to/gps_map_photo.jpg
   ```

3. **Review results**

   - Check `burned_metadata` section
   - Review `metadata_comparison` for discrepancies
   - Look at confidence levels

4. **Integrate in UI**
   - Add burned metadata display
   - Show comparison warnings
   - Badge for "Overlay Detected"

## Example Output

```
================================================================================
BURNED METADATA EXTRACTION TEST
================================================================================

File: photo.jpg

1. Extracting burned-in metadata (OCR)...
--------------------------------------------------------------------------------
✓ Burned metadata detected!
  Confidence: high

  Raw OCR Text:
  GPS Map Camera
  Bengaluru, Karnataka, India
  A27, Santhosapuram, Kudremukh Colony...

  Parsed Data:
    📍 GPS: 12.923974, 77.625419
       Maps: https://www.google.com/maps?q=12.923974,77.625419
    🏙️  Location: Bengaluru, Karnataka, India
    🕐 Timestamp: Thursday, 25/12/2025 04:48 PM GMT +05:30
    🌡️  Weather:
       Temperature: 25.54°C
       Humidity: 34%
    📷 Camera App: GPS Map Camera

2. Extracting full metadata (embedded + burned)...
--------------------------------------------------------------------------------
  Embedded EXIF GPS: ✓
  Burned OCR GPS:    ✓

3. Comparing embedded vs burned metadata...
--------------------------------------------------------------------------------
  Overall Status: VERIFIED

  ✓ MATCHES (2 fields):
    - gps: Data verified across both sources
      (GPS difference: ~0.0 meters)
    - timestamp: Data verified across both sources

4. Security Assessment
--------------------------------------------------------------------------------
  ✓ VERIFIED: Embedded and burned metadata match
  → Image metadata appears authentic

================================================================================
TEST COMPLETE
================================================================================
```

## Troubleshooting

### OCR not working?

```bash
# Check if Tesseract installed
tesseract --version

# Install if missing
brew install tesseract  # macOS
```

### Poor accuracy?

- Use higher resolution images
- Improve image contrast
- Check image quality

### Not detecting overlay?

- Verify overlay has readable text
- Check if text is too stylized
- Update regex patterns in `ocr_burned_metadata.py`

## Questions?

See full documentation in:

- `docs/BURNED_METADATA_GUIDE.md`
- `server/extractor/modules/ocr_burned_metadata.py` (source code)
- `server/extractor/modules/metadata_comparator.py` (comparison logic)

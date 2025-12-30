# 🔍 Burned-in Metadata Feature

## Quick Start

Your images have metadata **visually overlaid** on the pixels (GPS maps, timestamps, location text). This feature extracts that data using OCR.

### 1️⃣ Install Requirements

```bash
# Run the setup script
cd server
./setup_burned_metadata.sh
```

Or manually:

```bash
# macOS
brew install tesseract

# Linux
sudo apt install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2️⃣ Test It

```bash
cd server
python test_burned_metadata.py /path/to/your/gps_map_photo.jpg
```

This will show:

- ✓ GPS coordinates extracted from overlay
- ✓ Location (city, state, country)
- ✓ Timestamp from visible text
- ✓ Weather data (temperature, humidity)
- ✓ Comparison with embedded EXIF data
- ✓ Security assessment (verified/suspicious)

### 3️⃣ Use in Your App

The feature is **automatically enabled** for Premium and Super tiers:

```python
from server.extractor.metadata_engine import extract_metadata

result = extract_metadata('photo.jpg', tier='premium')

# New fields available:
print(result['burned_metadata'])  # OCR-extracted data
print(result['metadata_comparison'])  # Embedded vs burned comparison
```

## What Gets Extracted

From images like yours (GPS Map Camera):

| Data          | Example                                    |
| ------------- | ------------------------------------------ |
| **GPS**       | `12.923974, 77.625419` + Google Maps link  |
| **Location**  | `Bengaluru, Karnataka, India`              |
| **Address**   | `A27, Santhosapuram, Kudremukh Colony...`  |
| **Timestamp** | `Thursday, 25/12/2025 04:48 PM GMT +05:30` |
| **Weather**   | `Temperature: 25.54°C, Humidity: 34%`      |
| **Compass**   | `231° SW`                                  |
| **Altitude**  | `903 m`                                    |
| **Speed**     | `7.42 km/h`                                |
| **App**       | `GPS Map Camera`                           |

## Key Scenarios

### ✅ With Overlay (Your Case)

Image has GPS map overlay → **Extracts both EXIF + OCR data** → Compares for verification

### ✅ Without Overlay

Standard photo → **Extracts EXIF only** → Normal metadata extraction

### ⚠️ EXIF Stripped

Someone removed EXIF but overlay remains → **OCR still extracts location** → Flags as suspicious

### ⚠️ Data Mismatch

EXIF GPS ≠ Overlay GPS → **Detects discrepancy** → Warns of potential tampering

## Output Example

```json
{
  "burned_metadata": {
    "has_burned_metadata": true,
    "confidence": "high",
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
    }
  },

  "metadata_comparison": {
    "overall_status": "verified",
    "matches": [
      {
        "field": "gps",
        "matches": true,
        "difference": {
          "approx_meters": 0.0
        }
      }
    ],
    "summary": {
      "embedded_metadata_present": true,
      "burned_metadata_present": true,
      "gps_comparison": "match"
    }
  }
}
```

## Files Created

```
server/
├── extractor/
│   ├── metadata_engine.py  ← Modified (integrated OCR)
│   └── modules/
│       ├── ocr_burned_metadata.py  ← NEW (OCR extraction)
│       └── metadata_comparator.py  ← NEW (comparison logic)
├── test_burned_metadata.py  ← NEW (test script)
└── setup_burned_metadata.sh  ← NEW (setup script)

docs/
├── BURNED_METADATA_GUIDE.md  ← NEW (full documentation)
└── BURNED_METADATA_IMPLEMENTATION.md  ← NEW (summary)
```

## Performance

- Small images (< 2MB): +1-3 seconds
- Medium images (2-5MB): +3-5 seconds
- Large images (> 5MB): +5-10 seconds

OCR only runs when:

1. File is an image
2. User has Premium/Super tier
3. Tesseract is installed

## Tier Availability

| Tier    | Embedded Metadata | Burned Metadata (OCR) | Comparison |
| ------- | ----------------- | --------------------- | ---------- |
| Free    | Basic             | ✗                     | ✗          |
| Starter | ✓                 | ✗                     | ✗          |
| Premium | ✓                 | ✓                     | ✓          |
| Super   | ✓                 | ✓                     | ✓          |

## Troubleshooting

**OCR not working?**

```bash
tesseract --version  # Check if installed
./setup_burned_metadata.sh  # Run setup
```

**Poor accuracy?**

- Use higher resolution images
- Check image quality
- Ensure text is readable

**Not detecting overlay?**

- Verify overlay has text
- Check if text is too stylized
- Try different image

## Documentation

- **Quick Start**: This file
- **Complete Guide**: [docs/BURNED_METADATA_GUIDE.md](../docs/BURNED_METADATA_GUIDE.md)
- **Implementation Details**: [docs/BURNED_METADATA_IMPLEMENTATION.md](../docs/BURNED_METADATA_IMPLEMENTATION.md)
- **Source Code**:
  - [ocr_burned_metadata.py](extractor/modules/ocr_burned_metadata.py)
  - [metadata_comparator.py](extractor/modules/metadata_comparator.py)

## Use Cases

1. **Your Scenario**: Extract GPS from GPS Map Camera overlays
2. **Real Estate**: Extract addresses from watermarked property photos
3. **Security**: Extract timestamps from CCTV footage
4. **Social Media**: Get location from Instagram/Snapchat overlays
5. **Forensics**: Detect photo tampering by comparing sources

## Next Steps

1. ✓ You've created the feature
2. → Run setup: `./setup_burned_metadata.sh`
3. → Test with your images: `python test_burned_metadata.py photo.jpg`
4. → Review results
5. → Integrate in UI

---

**Questions?** See [BURNED_METADATA_GUIDE.md](../docs/BURNED_METADATA_GUIDE.md) for complete documentation.

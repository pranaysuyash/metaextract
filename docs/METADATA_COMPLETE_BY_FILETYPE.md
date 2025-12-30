# PhotoSearch: Complete Metadata Extraction by File Type
## Including EXIF, Burned-In Visual Data, and All Extractable Metadata

**Date:** December 26, 2024  
**Status:** Comprehensive Reference  
**Includes:** Backend extraction + Burned-in visual metadata + Missing implementations

---

## 📋 EXECUTIVE SUMMARY

PhotoSearch extracts metadata from **5 categories**:

1. **Traditional Metadata** (EXIF, ID3, Document properties)
2. **Burned-In Visual Metadata** (OCR from watermarks, overlays, timestamps)
3. **Calculated Metadata** (Derived from other fields)
4. **AI-Generated Metadata** (VLM analysis, face detection, OCR)
5. **User-Generated Metadata** (Tags, ratings, notes, edits)

---

## 🖼️ IMAGES (JPEG, PNG, HEIC, WebP, GIF, TIFF, RAW)

### ✅ Category 1: EXIF Metadata (IMPLEMENTED)

#### **EXIF - Image Section**
**Location:** `metadata_extractor.py::extract_exif_metadata()`  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `Make` | Camera manufacturer | "Sony", "Canon", "Apple" | ✅ Yes |
| `Model` | Camera model | "ILCE-7M4", "EOS R5", "iPhone 15 Pro" | ✅ Yes |
| `Software` | Processing software | "Adobe Photoshop 2024", "iOS 17.1" | ✅ Yes |
| `DateTime` | File modification date | "2024:12:26 14:30:45" | ✅ Yes |
| `DateTimeOriginal` | Original capture time | "2024:12:26 14:30:45" | ✅ Yes |
| `DateTimeDigitized` | Digitization time | "2024:12:26 14:30:45" | ✅ Yes |
| `SubSecTime` | Subsecond precision | "456" | ⚠️ Limited |
| `SubSecTimeOriginal` | Original subseconds | "456" | ⚠️ Limited |
| `SubSecTimeDigitized` | Digitized subseconds | "456" | ⚠️ Limited |
| `Orientation` | Image rotation | 1-8 (EXIF orientation codes) | ✅ Yes |
| `XResolution` | Horizontal DPI | 300, 72 | ✅ Yes |
| `YResolution` | Vertical DPI | 300, 72 | ✅ Yes |
| `ResolutionUnit` | Unit of resolution | "inches", "cm" | ⚠️ Limited |
| `YCbCrPositioning` | Chroma positioning | "Centered", "Co-sited" | ❌ No |
| `Copyright` | Copyright notice | "© 2024 Pranay Suyash" | ✅ Yes |
| `Artist` | Creator name | "Pranay Suyash" | ✅ Yes |
| `Description` | Image description | "Sunset at Dubai Marina" | ✅ Yes |

#### **EXIF - Photo Section**
**Technical capture settings**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `ExposureTime` | Shutter speed | "1/250", "2.5" | ✅ Yes |
| `FNumber` | Aperture | "f/1.8", "f/5.6" | ✅ Yes |
| `ExposureProgram` | Exposure mode | "Manual", "Aperture Priority" | ✅ Yes |
| `ISOSpeedRatings` | ISO sensitivity | 100, 3200, 25600 | ✅ Yes |
| `ShutterSpeedValue` | APEX shutter speed | Calculated value | ⚠️ Limited |
| `ApertureValue` | APEX aperture | Calculated value | ⚠️ Limited |
| `BrightnessValue` | Scene brightness | APEX value | ❌ No |
| `ExposureBiasValue` | Exposure compensation | "+0.3", "-1.0" | ✅ Yes |
| `MaxApertureValue` | Max lens aperture | "f/1.4" | ⚠️ Limited |
| `SubjectDistance` | Focus distance | "2.5m", "Infinity" | ⚠️ Limited |
| `MeteringMode` | Metering pattern | "Center-weighted", "Matrix", "Spot" | ✅ Yes |
| `LightSource` | Light type | "Daylight", "Tungsten", "Flash" | ⚠️ Limited |
| `Flash` | Flash fired/mode | "Flash fired", "No flash" | ✅ Yes |
| `FocalLength` | Lens focal length | "85mm", "24mm", "16-35mm" | ✅ Yes |
| `SubjectArea` | AF area coordinates | [x, y, width, height] | ❌ No |
| `MakerNote` | Proprietary data | Binary blob (manufacturer-specific) | ⚠️ Raw only |
| `UserComment` | User notes | "Great sunset shot" | ✅ Yes |
| `FlashPixVersion` | FlashPix version | "0100" | ❌ No |
| `ColorSpace` | Color space | "sRGB", "Adobe RGB", "Display P3" | ✅ Yes |
| `PixelXDimension` | Image width | 6000 | ✅ Yes |
| `PixelYDimension` | Image height | 4000 | ✅ Yes |
| `SensingMethod` | Sensor type | "One-chip color area" | ❌ No |
| `SceneType` | Scene type | "Directly photographed" | ⚠️ Limited |
| `ExposureMode` | Exposure mode | "Auto", "Manual", "Bracket" | ✅ Yes |
| `WhiteBalance` | White balance | "Auto", "Daylight", "Cloudy", "Custom" | ✅ Yes |
| `DigitalZoomRatio` | Digital zoom | "1.0", "2.0" | ⚠️ Limited |
| `FocalLengthIn35mmFilm` | 35mm equivalent | "127mm" (85mm on full frame) | ✅ Yes |
| `SceneCaptureType` | Capture type | "Standard", "Landscape", "Portrait" | ⚠️ Limited |
| `GainControl` | Gain adjustment | "None", "Low gain up", "High gain up" | ❌ No |
| `Contrast` | Contrast setting | "Normal", "Soft", "Hard" | ⚠️ Limited |
| `Saturation` | Saturation setting | "Normal", "Low", "High" | ⚠️ Limited |
| `Sharpness` | Sharpness setting | "Normal", "Soft", "Hard" | ⚠️ Limited |
| `SubjectDistanceRange` | Subject distance | "Macro", "Close", "Distant" | ❌ No |

#### **EXIF - Lens Section**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `LensSpecification` | Lens spec (min/max focal, aperture) | [85, 85, 1.8, 1.8] | ⚠️ Limited |
| `LensMake` | Lens manufacturer | "Sony", "Sigma", "Tamron" | ✅ Yes |
| `LensModel` | Lens model | "FE 85mm F1.8", "24-70mm f/2.8" | ✅ Yes |
| `LensSerialNumber` | Lens serial (in MakerNote) | "1234567" | ⚠️ If extracted |

#### **EXIF - GPS Section**
**Location and directional data**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `GPSLatitude` | Latitude (DMS) | 25° 15' 19.00" N | ✅ Yes (decimal) |
| `GPSLatitudeRef` | North/South | "N", "S" | ⚠️ Limited |
| `GPSLongitude` | Longitude (DMS) | 55° 17' 33.00" E | ✅ Yes (decimal) |
| `GPSLongitudeRef` | East/West | "E", "W" | ⚠️ Limited |
| `GPSAltitude` | Altitude | "12.3m" (above sea level) | ✅ Yes |
| `GPSAltitudeRef` | Above/below sea level | 0 (above), 1 (below) | ⚠️ Limited |
| `GPSTimeStamp` | GPS time | "14:30:45" (UTC) | ✅ Yes |
| `GPSDateStamp` | GPS date | "2024:12:26" | ✅ Yes |
| `GPSSpeed` | Movement speed | "45.5 km/h" | ✅ Yes |
| `GPSSpeedRef` | Speed unit | "K" (km/h), "M" (mph), "N" (knots) | ⚠️ Limited |
| `GPSTrack` | Direction of movement | "203.5°" | ✅ Yes |
| `GPSTrackRef` | True/Magnetic north | "T", "M" | ⚠️ Limited |
| `GPSImgDirection` | **Camera pointing direction** | "231.0°" (critical for globe viz) | ✅ Yes |
| `GPSImgDirectionRef` | True/Magnetic north | "T", "M" | ⚠️ Limited |
| `GPSDestBearing` | Bearing to destination | "45.0°" | ⚠️ Limited |
| `GPSDestBearingRef` | True/Magnetic north | "T", "M" | ⚠️ Limited |
| `GPSSatellites` | Number of satellites | "12" | ⚠️ Limited |
| `GPSDOP` | Dilution of Precision | "2.5" (accuracy metric) | ❌ No |
| `GPSMapDatum` | Geodetic datum | "WGS-84" | ❌ No |
| `GPSProcessingMethod` | GPS/GLONASS/Galileo | "GPS" | ❌ No |
| `GPSHPositioningError` | Positioning error | "5.0m" | ⚠️ Limited |

**Note:** DMS (Degrees, Minutes, Seconds) coordinates are automatically converted to decimal degrees for database storage.

#### **EXIF - MakerNote (Proprietary)**
**Manufacturer-specific data**

| Type | What's Included | Example Fields |
|------|-----------------|----------------|
| **Sony** | Camera/lens serial numbers, internal settings | SerialNumber, LensID, InternalSerialNumber |
| **Canon** | Camera serial, lens serial, firmware, custom functions | SerialNumber, LensSerialNumber, FirmwareVersion |
| **Nikon** | Serial numbers, lens data, custom settings | SerialNumber, LensType, ShootingMode |
| **Apple** | HDR info, Live Photo data, computational photography | HDRImageType, ContentIdentifier, ImageUniqueID |
| **All** | Proprietary settings, internal IDs | Binary blob (extracted as hex) |

**Status:** ✅ Extracted as raw hex, ⚠️ Not parsed into individual fields

---

### ✅ Category 2: Image Properties (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_image_properties()`  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `Width` | Image width | 6000 pixels | ✅ Yes |
| `Height` | Image height | 4000 pixels | ✅ Yes |
| `Format` | Image format | "JPEG", "PNG", "HEIC", "WebP" | ✅ Yes |
| `Mode` | Color mode | "RGB", "RGBA", "CMYK", "Grayscale" | ✅ Yes |
| `DPI` | Dots per inch | (300, 300) | ✅ Yes |
| `BitsPerPixel` | Color depth | 24, 32, 48 | ⚠️ Limited |
| `ColorPalette` | Has palette | True/False (indexed images) | ❌ No |
| `ColorSpace` | Color space | "sRGB", "Adobe RGB", "P3" | ✅ Yes |
| `ICCProfile` | ICC profile present | True/False | ⚠️ Limited |
| `ICCProfileName` | Profile name | "Display P3", "Adobe RGB (1998)" | ⚠️ Limited |
| `Animation` | Is animated | True/False (GIF, APNG) | ✅ Yes |
| `FrameCount` | Number of frames | 30 (for GIFs) | ✅ Yes |
| `Compression` | Compression type | "JPEG", "LZW", "ZIP" | ⚠️ Limited |
| `PhotometricInterpretation` | Color interpretation | "RGB", "CMYK", "YCbCr" | ❌ No |

---

### ❌ Category 3: Burned-In Visual Metadata (NOT IMPLEMENTED)

**Status:** ❌ Discussed in external conversation, not yet implemented  
**Source:** OCR extraction from visual elements in the image  
**Priority:** HIGH (enables metadata extraction from photos with watermarks/overlays)

#### **GPS Map Camera Watermarks**
Photos taken with GPS Map Camera app have burned-in overlays with metadata not in EXIF:

| Field | Description | Example | Extraction Method |
|-------|-------------|---------|-------------------|
| `CompassDirection` | Visual compass heading | "231° SW" | OCR + Text parsing |
| `CardinalDirection` | Cardinal direction | "SW", "NNE", "E" | OCR + Text parsing |
| `Speed` | Movement speed | "0 km/h", "45 km/h" | OCR + Number extraction |
| `Address` | Reverse geocoded address | "Dubai Marina, UAE" | OCR + Text extraction |
| `Coordinates` | Visual GPS display | "25°15'19"N 55°17'33"E" | OCR + Coordinate parsing |
| `WindSpeed` | Wind information | "12 km/h NW" | OCR + Text parsing |
| `Altitude` | Visual altitude display | "12m" | OCR + Number extraction |
| `Timestamp` | Burned-in timestamp | "2017-09-29 23:22:33" | OCR + Datetime parsing |

**Implementation Needed:**
```python
def extract_burned_in_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata burned into image via OCR
    
    Priority zones:
    - Bottom edge (GPS Map Camera watermark)
    - Top edge (camera app timestamps)
    - Corners (location stamps)
    
    Returns:
        {
            "compass_direction": {
                "degrees": 231.0,
                "cardinal": "SW",
                "source": "ocr",
                "confidence": 0.95
            },
            "speed": {
                "value": 45.0,
                "unit": "km/h",
                "source": "ocr",
                "confidence": 0.89
            },
            "burned_in_address": {
                "text": "Dubai Marina, UAE",
                "source": "ocr",
                "confidence": 0.92
            }
        }
    """
```

**Use Cases:**
- Photos from GPS Map Camera app (common in travel photography)
- Photos from timestamp cameras
- Screenshots with burned-in data
- Social media photos with location overlays
- Old photos where EXIF was stripped but visual data remains

#### **Camera App Timestamps**
Many camera apps burn timestamps into images:

| Field | Description | Example | Extraction Method |
|-------|-------------|---------|-------------------|
| `BurnedInDate` | Visual date stamp | "2017/09/29" | OCR + Date parsing |
| `BurnedInTime` | Visual time stamp | "23:22:33" | OCR + Time parsing |
| `BurnedInLocation` | Location text | "Dubai, UAE" | OCR + Location extraction |

#### **Social Media Overlays**
Screenshots from apps with metadata overlays:

| Field | Description | Example | Extraction Method |
|-------|-------------|---------|-------------------|
| `AppName` | Source app | "Instagram", "Snapchat" | OCR + App detection |
| `Username` | Social handle | "@pranaysuyash" | OCR + Username pattern |
| `PostDate` | Post timestamp | "Posted 2h ago" | OCR + Relative time parsing |
| `LocationTag` | Tagged location | "Dubai Marina" | OCR + Location extraction |

#### **Watermarks and Logos**
Professional watermarks and studio marks:

| Field | Description | Example | Extraction Method |
|-------|-------------|---------|-------------------|
| `WatermarkText` | Copyright text | "© Pranay Photography 2024" | OCR + Text extraction |
| `StudioName` | Studio/photographer | "Pranay Photography" | OCR + Name extraction |
| `WebsiteURL` | Website in watermark | "pranay.photo" | OCR + URL detection |

---

### ⚠️ Category 4: Calculated/Inferred Metadata (PARTIALLY IMPLEMENTED)

**Location:** `metadata_extractor.py::calculate_inferred_metadata()`  
**Status:** ⚠️ Partial - some implemented, some missing

#### **Implemented:**

| Field | Description | Example | Formula/Logic |
|-------|-------------|---------|---------------|
| `AspectRatio` | Ratio string | "16:9", "4:3", "3:2" | GCD calculation |
| `AspectRatioDecimal` | Decimal ratio | 1.778, 1.333, 1.5 | width / height |
| `Megapixels` | Total megapixels | 24.0, 12.3, 50.0 | (width × height) / 1,000,000 |
| `Orientation` | Layout orientation | "landscape", "portrait", "square" | width vs height comparison |
| `FileAge` | Days since creation | {"days": 90, "human": "3 months ago"} | now - created_date |
| `TimeSinceModified` | Days since modified | {"days": 7, "human": "1 week ago"} | now - modified_date |
| `PrintSize` | Maximum print size | "20x13 inches @ 300 DPI" | width,height / DPI |

#### **Missing (Should Be Implemented):**

| Field | Description | Example | Formula/Logic |
|-------|-------------|---------|---------------|
| `TimeOfDay` | ❌ Lighting period | "golden_hour", "blue_hour", "midday" | Timestamp + GPS + sun position |
| `SeasonOfYear` | ❌ Season when taken | "summer", "winter", "autumn" | Timestamp + hemisphere (from GPS) |
| `SunPosition` | ❌ Sun altitude/azimuth | {"altitude": 5.2°, "azimuth": 245°} | Ephem calculations |
| `MoonPhase` | ❌ Moon phase | "full_moon", "new_moon", "waning_crescent" | Astronomical calculation |
| `ShootingConditions` | ❌ Inferred conditions | "low_light", "bright_sun", "night" | ISO + shutter + aperture analysis |
| `EstimatedDistance` | ❌ Subject distance | "~3 meters" | Focal length + DoF calculation |
| `DepthOfField` | ❌ DoF estimate | "shallow" (f/1.8), "deep" (f/16) | Aperture + focal length + distance |
| `EquivalentISO` | ❌ Adjusted for sensor | "ISO 400 (35mm equivalent)" | Sensor size normalization |
| `ExposureIndex` | ❌ Combined exposure | "EV 12" | Aperture + shutter calculation |
| `CompositionType` | ❌ Basic composition | "rule_of_thirds", "centered", "golden_ratio" | Subject position analysis |
| `ColorTemperature` | ❌ Estimated temp | "5500K (daylight)" | White balance analysis |
| `NoiseLevel` | ❌ Estimated noise | "high" (ISO 6400), "low" (ISO 100) | ISO-based estimation |

---

### ❌ Category 5: AI-Generated Metadata (PLANNED, NOT IMPLEMENTED)

**Status:** ❌ Planned for VLM integration  
**Priority:** MEDIUM (enables semantic search and story generation)

#### **VLM Scene Understanding:**

| Field | Description | Example | Model |
|-------|-------------|---------|-------|
| `SceneDescription` | Natural language description | "Sunset at beach with person walking" | VLM (Qwen/GPT-4o) |
| `DetectedObjects` | Objects in scene | ["person", "surfboard", "ocean", "sunset"] | VLM + YOLO |
| `ObjectBoundingBoxes` | Object locations | [{"object": "person", "bbox": [120,340,580,890]}] | VLM |
| `DominantColors` | Color palette | ["#FF6B35", "#F7931E", "#004E89"] | VLM or k-means |
| `ColorHarmony` | Color relationships | "complementary", "analogous", "triadic" | Color theory analysis |
| `Mood` | Emotional tone | "peaceful", "energetic", "melancholic" | VLM |
| `Activity` | Detected activity | "surfing", "hiking", "dining" | VLM |
| `SceneType` | Environment | "outdoor_beach", "indoor_restaurant" | VLM |
| `WeatherCondition` | Apparent weather | "sunny", "cloudy", "rainy" | VLM |
| `TimeOfDayVisual` | Visual lighting | "golden_hour", "night", "overcast" | VLM |
| `CompositionScore` | Quality score | {"rule_of_thirds": 0.85, "balance": 0.72} | VLM + CV |
| `TechnicalQuality` | Image quality | {"sharpness": 0.9, "exposure": 0.8} | VLM + CV |
| `AestheticScore` | Beauty rating | 7.5/10 | VLM |
| `SubjectCount` | Number of subjects | {"people": 2, "animals": 1} | VLM |
| `FacialExpressions` | Detected emotions | ["smiling", "laughing"] | VLM |

#### **OCR Text Extraction:**

| Field | Description | Example | Model |
|-------|-------------|---------|-------|
| `ExtractedText` | All text in image | "Welcome to Dubai Marina" | Tesseract/PaddleOCR |
| `TextBlocks` | Text regions | [{"text": "...", "bbox": [...], "confidence": 0.95}] | OCR |
| `Language` | Detected language | "en", "ar", "multi" | OCR |
| `TextType` | Text category | "sign", "menu", "receipt", "document" | VLM |
| `HandwritingDetected` | Has handwriting | True/False | OCR |

#### **Face Recognition:**

| Field | Description | Example | Model |
|-------|-------------|---------|-------|
| `FacesDetected` | Number of faces | 3 | MTCNN/MediaPipe |
| `FaceEmbeddings` | Face vectors | [512-d vector per face] | FaceNet |
| `FaceBoundingBoxes` | Face locations | [{"bbox": [...], "confidence": 0.98}] | Face detector |
| `FaceLandmarks` | Facial points | {"left_eye": [x,y], "nose": [x,y]} | Face detector |
| `EstimatedAge` | Age range | "25-35" | VLM/Age estimator |
| `EstimatedGender` | Gender | "male", "female", "unknown" | VLM |
| `FacialExpression` | Expression | "smiling", "neutral", "surprised" | VLM |

---

### ✅ Category 6: File System Metadata (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_filesystem_metadata()`  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `FilePath` | Full path | "/Users/pranay/Photos/IMG_1234.jpg" | ✅ Yes |
| `FileName` | File name | "IMG_1234.jpg" | ✅ Yes |
| `FileExtension` | Extension | ".jpg", ".png", ".heic" | ✅ Yes |
| `FileSize` | Size in bytes | 4523890 | ✅ Yes |
| `FileSizeHuman` | Human-readable size | "4.3 MB" | ✅ Yes |
| `Created` | Creation timestamp | "2024-12-26T14:30:45Z" | ✅ Yes |
| `Modified` | Modification timestamp | "2024-12-26T15:00:00Z" | ✅ Yes |
| `Accessed` | Last access timestamp | "2024-12-26T16:45:30Z" | ✅ Yes |
| `Changed` | Metadata change (Unix) | "2024-12-26T15:00:00Z" | ⚠️ Limited |
| `PermissionsOctal` | Permissions (octal) | "0644", "0755" | ⚠️ Limited |
| `PermissionsHuman` | Permissions (rwx) | "-rw-r--r--" | ⚠️ Limited |
| `Owner` | Owner username | "pranay" | ✅ Yes |
| `OwnerUID` | Owner user ID | 501 | ❌ No |
| `Group` | Group name | "staff" | ⚠️ Limited |
| `GroupGID` | Group ID | 20 | ❌ No |
| `Inode` | Inode number | 123456789 | ❌ No |
| `Device` | Device ID | 16777220 | ❌ No |
| `HardLinks` | Hard link count | 1 | ❌ No |
| `FileType` | Type | "regular", "directory", "symlink" | ⚠️ Limited |

---

### ✅ Category 7: Extended Attributes (macOS/Linux)

**Location:** `metadata_extractor.py::extract_extended_attributes()`  
**Status:** ✅ Complete (macOS/Linux only)

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `com.apple.metadata:kMDItemWhereFroms` | Download source | ["https://example.com/image.jpg"] | ✅ Yes |
| `com.apple.metadata:kMDItemFinderComment` | Finder comment | "Important photo for project" | ✅ Yes |
| `com.apple.FinderInfo` | Finder metadata | Binary blob | ❌ No |
| `com.apple.quarantine` | Quarantine info | Download quarantine data | ⚠️ Limited |
| `user.*` | Custom attributes | Any user-defined xattr | ✅ Yes |

**Note:** Windows has limited extended attribute support.

---

### ✅ Category 8: File Integrity (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_file_hashes()`  
**Status:** ✅ Complete

| Field | Description | Example | Use Case |
|-------|-------------|---------|----------|
| `MD5` | MD5 hash | "a1b2c3d4e5f6..." | Duplicate detection |
| `SHA256` | SHA256 hash | "9f8e7d6c5b4a..." | File integrity verification |

---

### ⚠️ Category 9: Thumbnail Data (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_thumbnail()`  
**Status:** ✅ Extraction, ⚠️ Limited display

| Field | Description | Example | Status |
|-------|-------------|---------|--------|
| `HasEmbeddedThumbnail` | EXIF thumbnail exists | True/False | ✅ Extracted |
| `ThumbnailWidth` | Thumbnail width | 160 pixels | ✅ Extracted |
| `ThumbnailHeight` | Thumbnail height | 120 pixels | ✅ Extracted |
| `ThumbnailData` | Thumbnail image | Binary blob | ✅ Extracted |
| `GeneratedThumbnail` | Fallback generated | 160x160 | ✅ Generated |

---

### ❌ Category 10: Color Analysis (PLANNED, NOT IMPLEMENTED)

**Status:** ❌ Discussed (color clustering demo), not in metadata_extractor  
**Priority:** HIGH (enables color-based search)

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `DominantColors` | Top 5 colors | ["#FF6B35", "#F7931E", ...] | k-means clustering |
| `ColorPercentages` | Color coverage | [0.35, 0.25, 0.20, ...] | Pixel analysis |
| `PerceptualDominance` | Perceptual scores | [0.92, 0.78, 0.65, ...] | Lab color space + CIEDE2000 |
| `LabValues` | Lab color values | [[L,a,b], ...] | Color space conversion |
| `ColorTemperature` | Warm/cool | "warm", "cool", "neutral" | Color analysis |
| `ColorHarmony` | Harmony type | "complementary", "triadic" | Color theory |
| `IsGrayscale` | B&W image | True/False | Saturation analysis |
| `IsBlackAndWhite` | Monochrome | True/False | Color distribution |
| `SaturationAverage` | Average saturation | 0.65 (0-1) | HSV analysis |
| `BrightnessAverage` | Average brightness | 0.72 (0-1) | HSV analysis |
| `ContrastScore` | Image contrast | 0.68 (0-1) | Histogram analysis |

---

### ❌ Category 11: Quality Analysis (PLANNED, NOT IMPLEMENTED)

**Status:** ❌ Planned  
**Priority:** MEDIUM (enables quality filtering)

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `SharpnessScore` | Image sharpness | 0.85 (0-1) | Laplacian variance |
| `IsBlurry` | Blur detected | True/False | Threshold check |
| `BlurType` | Blur classification | "motion_blur", "out_of_focus", null | FFT analysis |
| `NoiseLevel` | Image noise | "low", "medium", "high" | Noise estimation |
| `ExposureQuality` | Exposure assessment | "well_exposed", "underexposed" | Histogram analysis |
| `DynamicRange` | Tonal range | 8.5 stops | Histogram analysis |
| `HistogramRGB` | RGB distribution | [256 bins per channel] | Pixel analysis |
| `HistogramHSV` | HSV distribution | [256 bins per channel] | Color space analysis |
| `TonalRange` | Shadow/midtone/highlight | {"shadows": 0.15, "midtones": 0.70} | Histogram zones |

---

### ❌ Category 12: Composition Analysis (PLANNED, NOT IMPLEMENTED)

**Status:** ❌ Planned for VLM integration  
**Priority:** LOW (nice-to-have)

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `RuleOfThirdsScore` | Compliance score | 0.85 (0-1) | Subject position analysis |
| `GoldenRatioScore` | Golden ratio | 0.72 (0-1) | Composition analysis |
| `SymmetryScore` | Symmetry | 0.45 (0-1) | Image comparison |
| `HasLeadingLines` | Leading lines | True/False | Edge detection |
| `BalanceScore` | Visual balance | 0.78 (0-1) | Weight distribution |
| `HorizonLevel` | Level horizon | True/False | Edge detection |
| `HorizonPosition` | Horizon placement | 0.33 (0-1, relative) | Edge position |

---

## 🎬 VIDEOS (MP4, MOV, AVI, MKV, WebM, M4V)

### ✅ Category 1: Format-Level Metadata (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_video_properties()` using ffprobe  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `format_name` | Container format | "mov,mp4,m4a,3gp,3g2,mj2" | ✅ Yes |
| `format_long_name` | Full format name | "QuickTime / MOV" | ✅ Yes |
| `duration` | Video duration (seconds) | 127.43 | ✅ Yes |
| `duration_human` | Human-readable | "2:07" | ✅ Yes |
| `size` | File size (bytes) | 125000000 | ✅ Yes |
| `bit_rate` | Overall bitrate | 120000000 | ✅ Yes |
| `probe_score` | Format confidence | 100 | ❌ No |
| `start_time` | Start time | 0.000000 | ❌ No |
| `nb_streams` | Stream count | 3 (video + 2 audio) | ⚠️ Limited |
| `nb_programs` | Program count | 0 | ❌ No |

---

### ✅ Category 2: Video Stream Metadata (IMPLEMENTED)

**Multiple video streams supported**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `codec_name` | Video codec | "h264", "hevc", "vp9", "av1" | ✅ Yes |
| `codec_long_name` | Full codec name | "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10" | ✅ Yes |
| `codec_type` | Stream type | "video" | ✅ Yes |
| `profile` | Codec profile | "High", "Main", "Baseline" | ✅ Yes |
| `width` | Video width | 3840 | ✅ Yes |
| `height` | Video height | 2160 | ✅ Yes |
| `coded_width` | Encoded width | 3840 | ⚠️ Limited |
| `coded_height` | Encoded height | 2160 | ⚠️ Limited |
| `has_b_frames` | B-frames present | 2 | ⚠️ Limited |
| `sample_aspect_ratio` | Pixel aspect | "1:1" | ⚠️ Limited |
| `display_aspect_ratio` | Display aspect | "16:9" | ✅ Yes |
| `pix_fmt` | Pixel format | "yuv420p", "yuv420p10le" | ⚠️ Limited |
| `level` | Codec level | 51 | ❌ No |
| `color_range` | Color range | "tv", "pc" | ⚠️ Limited |
| `color_space` | Color space | "bt709", "bt2020nc" | ✅ Yes |
| `color_transfer` | Transfer function | "bt709", "smpte2084" (HDR) | ✅ Yes |
| `color_primaries` | Color primaries | "bt709", "bt2020" | ✅ Yes |
| `refs` | Reference frames | 4 | ❌ No |
| `r_frame_rate` | Real frame rate | "30000/1001" (29.97) | ✅ Yes |
| `avg_frame_rate` | Average frame rate | "30000/1001" | ✅ Yes |
| `time_base` | Time base | "1/30000" | ❌ No |
| `start_pts` | Start PTS | 0 | ❌ No |
| `start_time` | Start time | "0.000000" | ❌ No |
| `duration_ts` | Duration (time base) | 3822300 | ❌ No |
| `duration` | Duration (seconds) | 127.410000 | ✅ Yes |
| `bit_rate` | Video bitrate | 116000000 | ✅ Yes |
| `bits_per_raw_sample` | Bit depth | "8", "10" | ⚠️ Limited |
| `nb_frames` | Frame count | 3822 | ✅ Yes |

**HDR Metadata (if present):**

| Field | Description | Example |
|-------|-------------|---------|
| `side_data_type` | HDR type | "Mastering display metadata" |
| `max_luminance` | Max brightness | "1000 cd/m²" |
| `min_luminance` | Min brightness | "0.0001 cd/m²" |

---

### ✅ Category 3: Audio Stream Metadata (IMPLEMENTED)

**Multiple audio streams/tracks supported**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `codec_name` | Audio codec | "aac", "mp3", "opus", "flac" | ✅ Yes |
| `codec_long_name` | Full codec name | "AAC (Advanced Audio Coding)" | ✅ Yes |
| `sample_fmt` | Sample format | "fltp", "s16" | ❌ No |
| `sample_rate` | Sample rate | 48000 Hz | ✅ Yes |
| `channels` | Channel count | 2, 6, 8 | ✅ Yes |
| `channel_layout` | Channel layout | "stereo", "5.1", "7.1" | ✅ Yes |
| `bits_per_sample` | Bit depth | 16, 24 | ✅ Yes |
| `r_frame_rate` | Frame rate | "0/0" | ❌ No |
| `avg_frame_rate` | Average frame rate | "0/0" | ❌ No |
| `time_base` | Time base | "1/48000" | ❌ No |
| `start_pts` | Start PTS | 0 | ❌ No |
| `start_time` | Start time | "0.000000" | ❌ No |
| `duration_ts` | Duration (time base) | 6115520 | ❌ No |
| `duration` | Duration (seconds) | 127.407500 | ✅ Yes |
| `bit_rate` | Audio bitrate | 192000 | ✅ Yes |
| `nb_frames` | Frame count | 5981 | ❌ No |
| `language` | Audio language | "eng", "spa", "jpn" | ✅ Yes |

---

### ✅ Category 4: Subtitle Stream Metadata (IMPLEMENTED)

**Multiple subtitle tracks supported**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `codec_name` | Subtitle codec | "subrip", "ass", "webvtt" | ✅ Yes |
| `codec_long_name` | Full codec name | "SubRip subtitle" | ⚠️ Limited |
| `codec_type` | Stream type | "subtitle" | ✅ Yes |
| `language` | Subtitle language | "eng", "spa", "fra" | ✅ Yes |

---

### ✅ Category 5: Chapter Metadata (IMPLEMENTED)

**Video chapters with timestamps**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `id` | Chapter ID | 0, 1, 2 | ⚠️ Limited |
| `time_base` | Time base | "1/1000" | ❌ No |
| `start` | Start time (time_base) | 0 | ❌ No |
| `start_time` | Start time (seconds) | "0.000000" | ✅ Yes |
| `end` | End time (time_base) | 30000 | ❌ No |
| `end_time` | End time (seconds) | "30.000000" | ✅ Yes |
| `title` | Chapter title | "Introduction", "Main Content" | ✅ Yes |

---

### ✅ Category 6: Format Tags (IMPLEMENTED)

**Video file metadata tags**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `title` | Video title | "My Vacation 2024" | ✅ Yes |
| `artist` | Creator/artist | "Pranay Suyash" | ✅ Yes |
| `album` | Album name | "Travel Videos 2024" | ✅ Yes |
| `date` | Creation date | "2024" | ✅ Yes |
| `comment` | Comments | "Shot in Dubai" | ✅ Yes |
| `encoder` | Encoding software | "Lavf60.3.100" | ⚠️ Limited |
| `copyright` | Copyright | "© 2024 Pranay Suyash" | ✅ Yes |
| `genre` | Genre | "Travel", "Documentary" | ✅ Yes |
| `description` | Description | "Day trip to Dubai Marina" | ✅ Yes |
| `Custom tags` | Any custom tags | Various | ✅ Yes |

---

### ❌ Category 7: Burned-In Video Metadata (NOT IMPLEMENTED)

**Status:** ❌ Not implemented  
**Priority:** MEDIUM

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `BurnedInTimecode` | Visible timecode | "00:05:23:15" | OCR on video frames |
| `BurnedInDate` | Visible date stamp | "2024-12-26" | OCR |
| `BurnedInLocation` | Location overlay | "Dubai, UAE" | OCR |
| `BurnedInCameraInfo` | Camera settings overlay | "f/2.8 1/60 ISO 400" | OCR |
| `BurnedInLogo` | Station/production logo | "Channel Logo" | Logo detection |
| `BurnedInSubtitles` | Open captions | Subtitle text | OCR |

---

## 🎵 AUDIO (MP3, FLAC, OGG, WAV, AAC, M4A, MP4 audio)

### ✅ Category 1: Audio Format Metadata (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_audio_properties()` using mutagen  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `format` | Audio format | "MP3", "FLAC", "M4A" | ✅ Yes |
| `length` | Duration (seconds) | 245.67 | ✅ Yes |
| `length_human` | Duration (MM:SS) | "4:05" | ✅ Yes |
| `bitrate` | Bitrate | 320000, 192000 | ✅ Yes |
| `sample_rate` | Sample rate | 44100, 48000, 96000 Hz | ✅ Yes |
| `channels` | Channel count | 1 (mono), 2 (stereo), 6 (5.1) | ✅ Yes |
| `bits_per_sample` | Bit depth | 16, 24, 32 | ✅ Yes |

---

### ✅ Category 2: Audio Tags (IMPLEMENTED)

**Common tags normalized across formats**

#### **Basic Music Tags:**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `title` | Track title | "Bohemian Rhapsody" | ✅ Yes |
| `artist` | Artist name | "Queen" | ✅ Yes |
| `album` | Album name | "A Night at the Opera" | ✅ Yes |
| `date` / `year` | Release year | "1975" | ✅ Yes |
| `genre` | Music genre | "Rock", "Classical", "Jazz" | ✅ Yes |
| `track_number` | Track number | "11" | ✅ Yes |
| `disc_number` | Disc number | "1" | ✅ Yes |
| `album_artist` | Album artist | "Queen" | ✅ Yes |
| `composer` | Composer | "Freddie Mercury" | ✅ Yes |
| `comment` | Comments | "Remastered 2011" | ✅ Yes |
| `lyrics` | Song lyrics | Full lyrics text | ✅ Yes |
| `copyright` | Copyright | "© 1975 Queen Productions" | ✅ Yes |
| `encoder` | Encoder software | "LAME 3.99" | ⚠️ Limited |
| `bpm` | Beats per minute | "72" | ✅ Yes |
| `compilation` | Compilation flag | True/False | ✅ Yes |

#### **ID3-Specific Tags (MP3):**

| Tag | Description | Example |
|-----|-------------|---------|
| `TIT2` | Title | Track title |
| `TPE1` | Artist | Lead performer |
| `TALB` | Album | Album name |
| `TDRC` | Recording date | Year |
| `TCON` | Genre | Genre |
| `TRCK` | Track | Track number |
| `TPOS` | Disc | Disc number |
| `COMM` | Comment | Comments |
| `USLT` | Lyrics | Unsynchronized lyrics |
| `APIC` | Picture | Album art (binary) |

#### **Vorbis Comments (FLAC/OGG):**

All standard Vorbis fields plus custom tags supported.

#### **iTunes Tags (M4A/MP4):**

| Tag | Description | Example |
|-----|-------------|---------|
| `©nam` | Name | Track title |
| `©ART` | Artist | Artist name |
| `©alb` | Album | Album name |
| `©day` | Date | Year |
| `©gen` | Genre | Genre |
| `trkn` | Track | Track number |
| `disk` | Disc | Disc number |
| `covr` | Cover | Album art |

---

### ✅ Category 3: Album Art (IMPLEMENTED)

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `has_album_art` | Album art present | True/False | ✅ Yes |
| `album_art_count` | Number of images | 1, 2 (front + back) | ⚠️ Limited |
| `album_art_data` | Image binary data | JPEG/PNG blob | ❌ No (binary) |

---

### ❌ Category 4: Advanced Audio Analysis (NOT IMPLEMENTED)

**Status:** ❌ Not implemented  
**Priority:** LOW

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `WaveformPeaks` | Waveform data | Array of peak values | Audio analysis |
| `SpectrogramData` | Frequency data | Spectrogram array | FFT |
| `DynamicRange` | DR value | "DR12" | Dynamic range analysis |
| `ReplayGain` | Loudness normalization | "-3.5 dB" | ReplayGain calculation |
| `Tempo` | Detected tempo | "120 BPM" | Beat detection |
| `Key` | Musical key | "C Major", "A Minor" | Key detection |
| `Mood` | Audio mood | "energetic", "relaxed" | Audio classification |

---

---

### ❌ Category 11: IPTC/XMP Metadata (NOT IMPLEMENTED)

**Status:** ❌ Not implemented (professional standard for editorial photos)  
**Priority:** HIGH (industry standard, required for stock photography)

IPTC (International Press Telecommunications Council) and XMP (Extensible Metadata Platform) are professional metadata standards used by photographers, news agencies, stock photo libraries, and digital asset management systems.

#### **IPTC Core Schema**

| Field | Description | Example | Use Case |
|-------|-------------|---------|----------|
| `Title` | Image title | "Sunset at Dubai Marina" | Display, search |
| `Headline` | Brief synopsis | "Golden hour at waterfront" | News/editorial |
| `Description` | Full caption | "The sun sets behind the skyscrapers..." | Editorial caption |
| `Keywords` | Search tags | ["dubai", "sunset", "marina", "uae"] | Search, organization |
| `Creator` | Photographer name | "Pranay Suyash" | Copyright, credit |
| `CreatorContactInfo` | Contact details | {"email": "...", "phone": "..."} | Licensing |
| `CreatorJobTitle` | Job title | "Photographer", "Photojournalist" | Professional info |
| `Credit` | Credit line | "Photo by Pranay Suyash" | Attribution |
| `Source` | Image source | "PhotoSearch Archive" | Provenance |
| `CopyrightNotice` | Copyright | "© 2024 Pranay Suyash. All rights reserved." | Rights management |
| `Rights Usage Terms` | Usage license | "Editorial use only" | Licensing |
| `WebStatementOfRights` | Rights URL | "https://pranay.photo/license" | Online licensing |
| `Instructions` | Special instructions | "Color accurate, do not crop" | Editorial guidelines |
| `TransmissionReference` | Job identifier | "PROJ-2024-001" | Workflow tracking |
| `DateCreated` | Creation date | "2024-12-26" | Editorial/stock |
| `IntellectualGenre` | Content type | "Documentary", "Portrait", "Landscape" | Categorization |
| `Scene` | Scene type | "Beach", "Urban", "Event" | Content classification |
| `SubjectCode` | IPTC subject code | "15000000" (Lifestyle) | News categorization |
| `City` | Location city | "Dubai" | Location metadata |
| `State` | Province/state | "Dubai" | Location metadata |
| `Country` | Country name | "United Arab Emirates" | Location metadata |
| `CountryCode` | ISO country code | "AE" | Location metadata |
| `Location` | Sublocation | "Dubai Marina" | Precise location |
| `Event` | Event name | "Dubai Photography Festival 2024" | Event coverage |

#### **IPTC Extension Schema**

| Field | Description | Example | Use Case |
|-------|-------------|---------|----------|
| `PersonInImage` | People shown | ["John Doe", "Jane Smith"] | Model releases |
| `PersonInImageWDetails` | Person details | [{"name": "...", "description": "..."}] | Detailed credits |
| `DigitalSourceType` | Image source | "digitalCapture", "negativeFilm", "positiveFilm" | Authenticity |
| `Event` | Event details | Structured event information | Event photography |
| `OrganisationInImageName` | Organizations | ["Acme Corp"] | Corporate/editorial |
| `LocationShown` | Location details | [{"city": "Dubai", "sublocation": "Marina"}] | Detailed location |
| `LocationCreated` | Creation location | Same structure as LocationShown | Production info |
| `ArtworkOrObject` | Artwork depicted | [{"title": "...", "creator": "..."}] | Art documentation |
| `RegistryEntry` | External IDs | [{"registryId": "...", "itemId": "..."}] | Asset tracking |
| `MaxAvailWidth` | Max available width | 6000 pixels | Licensing info |
| `MaxAvailHeight` | Max available height | 4000 pixels | Licensing info |
| `DigitalImageGUID` | Unique identifier | "550e8400-e29b-41d4-a716-446655440000" | Global tracking |
| `PlusVersion` | PLUS version | "1.2.0" | Rights metadata |
| `Licensor` | Licensing agent | [{"name": "...", "url": "..."}] | Rights management |
| `MinorModelAgeDisclosure` | Minor age | "Age 25 or Over" | Model release |
| `ModelReleaseStatus` | Release status | "modelReleased", "notReleased" | Legal |
| `ModelReleaseID` | Release ID | ["MR-2024-001"] | Legal tracking |
| `PropertyReleaseStatus` | Property release | "propertyReleased" | Legal |
| `PropertyReleaseID` | Property ID | ["PR-2024-001"] | Legal tracking |

#### **XMP Dublin Core (Embedded)**

| Field | Description | Example | Standard |
|-------|-------------|---------|----------|
| `dc:title` | Title | "Sunset at Dubai Marina" | Dublin Core |
| `dc:description` | Description | Full description text | Dublin Core |
| `dc:creator` | Creator | ["Pranay Suyash"] | Dublin Core |
| `dc:subject` | Keywords | ["dubai", "sunset"] | Dublin Core |
| `dc:rights` | Rights | "© 2024 Pranay Suyash" | Dublin Core |
| `dc:date` | Date | "2024-12-26" | Dublin Core |
| `dc:format` | Format | "image/jpeg" | Dublin Core |

#### **XMP Photoshop Namespace**

| Field | Description | Example |
|-------|-------------|---------|
| `photoshop:Headline` | Headline | "Golden hour at waterfront" |
| `photoshop:Credit` | Credit | "Pranay Suyash" |
| `photoshop:Source` | Source | "PhotoSearch" |
| `photoshop:DateCreated` | Date created | "2024-12-26T19:42:33" |
| `photoshop:City` | City | "Dubai" |
| `photoshop:State` | State | "Dubai" |
| `photoshop:Country` | Country | "United Arab Emirates" |
| `photoshop:AuthorsPosition` | Position | "Photographer" |
| `photoshop:CaptionWriter` | Caption writer | "Pranay Suyash" |
| `photoshop:Instructions` | Instructions | "Do not crop" |
| `photoshop:TransmissionReference` | Reference | "PROJ-2024-001" |

**Implementation Needed:**
```python
def extract_iptc_xmp_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract IPTC/XMP professional metadata
    Uses: python-xmp-toolkit or pyexiv2
    
    Returns IPTC Core, IPTC Extension, and XMP data
    Critical for professional photographers and stock agencies
    """
```

---

### ❌ Category 12: RAW Image Metadata (PARTIALLY IMPLEMENTED)

**Status:** ⚠️ EXIF extraction works, RAW-specific data not fully exposed  
**Priority:** MEDIUM (professional photographers use RAW)

RAW formats (CR2, NEF, ARW, DNG, ORF, RAF, etc.) contain ALL standard EXIF plus manufacturer-specific metadata.

#### **RAW-Specific Fields**

| Field | Description | Example | Format |
|-------|-------------|---------|--------|
| `RawDataUniqueID` | Unique RAW ID | UUID | DNG |
| `OriginalRawFileName` | Original filename | "DSC_1234.NEF" | DNG |
| `OriginalRawFileData` | Embedded original | Binary blob | DNG |
| `PreviewApplicationName` | Preview creator | "Adobe Lightroom 2024" | DNG |
| `PreviewApplicationVersion` | Version | "13.1" | DNG |
| `PreviewSettingsName` | Preset name | "Adobe Color" | DNG |
| `PreviewColorSpace` | Preview space | "Adobe RGB" | DNG |
| `ForwardMatrix1` | Color matrix | Matrix values | DNG |
| `ForwardMatrix2` | Color matrix | Matrix values | DNG |
| `ColorMatrix1` | Color matrix | Matrix values | DNG |
| `ColorMatrix2` | Color matrix | Matrix values | DNG |
| `CalibrationIlluminant1` | Light source | "D65" | DNG |
| `CalibrationIlluminant2` | Light source | "Standard Light A" | DNG |
| `CameraCalibration1` | Camera calibration | Matrix values | DNG |
| `CameraCalibration2` | Camera calibration | Matrix values | DNG |
| `BaselineExposure` | Baseline exposure | "+0.25" | DNG |
| `BaselineNoise` | Noise level | "0.8" | DNG |
| `BaselineSharpness` | Sharpness | "1.2" | DNG |
| `BayerGreenSplit` | Bayer split | "100" | DNG |
| `LinearResponseLimit` | Linear limit | "1.0" | DNG |
| `ShadowScale` | Shadow scale | "1.0" | DNG |
| `DNGVersion` | DNG version | "1.6.0.0" | DNG |
| `DNGBackwardVersion` | Backward compatibility | "1.4.0.0" | DNG |

#### **Manufacturer-Specific (MakerNote Parsed)**

**Canon:**
| Field | Description |
|-------|-------------|
| `CanonFirmwareVersion` | Firmware version |
| `CanonImageType` | Image type |
| `CanonSerialNumber` | Camera serial |
| `InternalSerialNumber` | Internal serial |
| `FocusMode` | AF mode |
| `RecordMode` | Recording mode |
| `CanonFlashInfo` | Flash details |
| `CanonShotInfo` | Shot information |
| `CanonPanorama` | Panorama mode |

**Nikon:**
| Field | Description |
|-------|-------------|
| `NikonSerialNumber` | Camera serial |
| `ShutterCount` | Shutter actuations |
| `InternalSerialNumber` | Internal serial |
| `LensType` | Lens type code |
| `LensFStops` | F-stop range |
| `AFAreaMode` | AF area mode |
| `ActiveDLighting` | D-Lighting setting |
| `VRMode` | VR mode |
| `VibrationReduction` | VR on/off |

**Sony:**
| Field | Description |
|-------|-------------|
| `SonySerialNumber` | Camera serial |
| `InternalSerialNumber` | Lens serial |
| `SonyImageQuality` | Quality setting |
| `SonyImageSize` | Size setting |
| `DriveMode` | Drive mode |
| `FocusMode` | AF mode |
| `AFAreaMode` | AF area |
| `LongExposureNoiseReduction` | NR setting |

**Status:** EXIF extraction via exifread/Pillow gets basic fields. Need exiv2 or rawpy for full MakerNote parsing.

---

### ❌ Category 13: Image Editing History (SIDECAR/XMP)

**Status:** ❌ Not implemented  
**Priority:** LOW (useful for photographers tracking edits)

Lightroom and other tools store editing history in XMP sidecar files or embedded XMP.

| Field | Description | Example |
|-------|-------------|---------|
| `xmp:CreatorTool` | Editing software | "Adobe Lightroom Classic 13.1" |
| `xmp:ModifyDate` | Last modified | "2024-12-26T15:30:00" |
| `xmp:MetadataDate` | Metadata modified | "2024-12-26T15:30:00" |
| `crs:Version` | Camera Raw version | "16.1" |
| `crs:ProcessVersion` | Process version | "11.0" |
| `crs:WhiteBalance` | WB setting | "As Shot", "Custom" |
| `crs:Temperature` | Color temp | "5500" |
| `crs:Tint` | Tint | "+10" |
| `crs:Exposure2012` | Exposure adjustment | "+0.50" |
| `crs:Contrast2012` | Contrast | "+20" |
| `crs:Highlights2012` | Highlights | "-50" |
| `crs:Shadows2012` | Shadows | "+40" |
| `crs:Whites2012` | Whites | "+10" |
| `crs:Blacks2012` | Blacks | "-15" |
| `crs:Texture` | Texture | "+20" |
| `crs:Clarity2012` | Clarity | "+30" |
| `crs:Dehaze` | Dehaze | "+20" |
| `crs:Vibrance` | Vibrance | "+15" |
| `crs:Saturation` | Saturation | "0" |
| `crs:ToneCurve` | Tone curve points | Array of points |
| `crs:HasSettings` | Has adjustments | True/False |
| `crs:HasCrop` | Has crop | True/False |
| `crs:CropAngle` | Crop rotation | "-2.5" degrees |
| `crs:CropLeft` | Crop left | "0.1" (0-1) |
| `crs:CropTop` | Crop top | "0.05" |
| `crs:CropRight` | Crop right | "0.95" |
| `crs:CropBottom` | Crop bottom | "0.9" |

**Use Cases:**
- "Show me photos I've edited in Lightroom"
- "Find photos with heavy shadow recovery"
- "Show me crops vs original framing"
- Learn from editing patterns

---

## 📄 PDFs (PDF Documents)

### ✅ Category 1: Document Info (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_pdf_properties()` using pypdf  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `/Title` | Document title | "Q3 Sales Report" | ✅ Yes |
| `/Author` | Document author | "John Doe" | ✅ Yes |
| `/Subject` | Subject | "Quarterly Financial Analysis" | ✅ Yes |
| `/Keywords` | Keywords | "sales, revenue, Q3, 2024" | ✅ Yes |
| `/Creator` | Creating application | "Microsoft Word" | ✅ Yes |
| `/Producer` | PDF producer | "macOS Version 14.0 Quartz PDFContext" | ✅ Yes |
| `/CreationDate` | Creation date | "D:20241226143045Z" | ✅ Yes |
| `/ModDate` | Modification date | "D:20241226150000Z" | ✅ Yes |

---

### ✅ Category 2: Document Structure (IMPLEMENTED)

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `page_count` | Number of pages | 25 | ✅ Yes |
| `page_width` | Page width (points) | 612 (8.5") | ⚠️ Limited |
| `page_height` | Page height (points) | 792 (11") | ⚠️ Limited |
| `page_layout` | Layout mode | "SinglePage", "TwoColumnLeft" | ⚠️ Limited |
| `page_mode` | Display mode | "UseNone", "UseOutlines" | ⚠️ Limited |
| `encrypted` | Encryption status | True/False | ✅ Yes |
| `is_encrypted` | Alias for encrypted | True/False | ✅ Yes |
| `encryption_level` | Encryption strength | 128-bit, 256-bit | ⚠️ Limited |

---

### ✅ Category 3: Security (IMPLEMENTED)

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `permissions` | Permission flags | Printing, copying allowed/denied | ⚠️ Limited |
| `user_password` | User password set | True/False | ❌ No |
| `owner_password` | Owner password set | True/False | ❌ No |

---

### ❌ Category 4: Advanced PDF Features (NOT IMPLEMENTED)

**Status:** ❌ Not implemented  
**Priority:** LOW

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `FormFields` | Interactive forms | ["name", "email", "signature"] | PDF form analysis |
| `Annotations` | Comments/markup | [{"page": 1, "text": "Review this"}] | Annotation extraction |
| `Bookmarks` | Document outline | Tree structure | Bookmark parsing |
| `Hyperlinks` | Embedded links | ["https://example.com"] | Link extraction |
| `EmbeddedFiles` | Attachments | ["spreadsheet.xlsx"] | Attachment listing |
| `JavaScripts` | Embedded JS | True/False | Security scan |
| `DigitalSignatures` | Signatures | ["John Doe, verified"] | Signature validation |
| `PDFVersion` | PDF version | "1.7", "2.0" | Format detection |
| `FontsUsed` | Embedded fonts | ["Arial", "Times New Roman"] | Font analysis |

---

## 🎨 SVGs (Scalable Vector Graphics)

### ✅ Category 1: SVG Properties (IMPLEMENTED)

**Location:** `metadata_extractor.py::extract_svg_properties()` using XML parsing  
**Status:** ✅ Complete

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `width` | SVG width | "500px", "100%" | ✅ Yes |
| `height` | SVG height | "300px", "auto" | ✅ Yes |
| `viewBox` | ViewBox attribute | "0 0 500 300" | ✅ Yes |
| `viewBox_width` | Parsed viewBox width | 500 | ✅ Yes |
| `viewBox_height` | Parsed viewBox height | 300 | ✅ Yes |
| `version` | SVG version | "1.1", "2.0" | ⚠️ Limited |
| `xmlns` | XML namespace | "http://www.w3.org/2000/svg" | ❌ No |

---

### ✅ Category 2: Content Analysis (IMPLEMENTED)

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `element_count` | Total elements | 245 | ✅ Yes |
| `path_count` | Path elements | 89 | ✅ Yes |
| `rect_count` | Rectangle elements | 12 | ✅ Yes |
| `circle_count` | Circle elements | 5 | ✅ Yes |
| `ellipse_count` | Ellipse elements | 3 | ✅ Yes |
| `line_count` | Line elements | 45 | ✅ Yes |
| `polyline_count` | Polyline elements | 8 | ✅ Yes |
| `polygon_count` | Polygon elements | 6 | ✅ Yes |
| `text_count` | Text elements | 15 | ✅ Yes |
| `has_embedded_styles` | CSS styles present | True/False | ✅ Yes |
| `has_scripts` | JavaScript present | True/False | ✅ Yes (security) |
| `has_links` | Hyperlinks present | True/False | ✅ Yes |
| `has_text` | Text content | True/False | ✅ Yes |

---

### ✅ Category 3: Dublin Core Metadata (IMPLEMENTED)

**If present in SVG**

| Field | Description | Example | Searchable |
|-------|-------------|---------|------------|
| `title` | SVG title | "Company Logo" | ✅ Yes |
| `description` | Description | "Official logo for Acme Corp" | ✅ Yes |
| `dc:creator` | Creator | "Design Team" | ✅ Yes |
| `dc:rights` | Rights | "© 2024 Acme Corp" | ✅ Yes |
| `dc:date` | Creation date | "2024-01-15" | ✅ Yes |
| `dc:publisher` | Publisher | "Acme Corp" | ⚠️ Limited |
| `dc:subject` | Subject | "branding, logo, identity" | ⚠️ Limited |

---

### ❌ Category 4: Advanced SVG Analysis (NOT IMPLEMENTED)

**Status:** ❌ Not implemented  
**Priority:** LOW

| Field | Description | Example | Method |
|-------|-------------|---------|--------|
| `ComplexityScore` | SVG complexity | "high", "medium", "low" | Element/path analysis |
| `ColorPalette` | Colors used | ["#FF0000", "#00FF00"] | Style/attribute parsing |
| `FontsUsed` | Fonts referenced | ["Arial", "Helvetica"] | Font extraction |
| `ExternalReferences` | External resources | ["logo.png", "style.css"] | URL parsing |
| `AnimationElements` | Has animations | True/False | Animation tag detection |
| `FilterEffects` | Filter count | 5 | Filter element count |
| `GradientCount` | Gradient definitions | 3 | Gradient element count |
| `MaskCount` | Mask definitions | 2 | Mask element count |

---

## 📊 COMPARISON: PhotoSearch vs Competitors

### Google Photos (5 fields)
- File name
- Date taken
- Location (city only)
- Camera model
- Dimensions

### Apple Photos (8 fields)
- File name
- Date taken
- Location (city/state)
- Camera model
- Lens info
- ISO/Aperture/Shutter
- Faces detected
- Keywords

### PhotoSearch (100+ fields)
- **ALL OF THE ABOVE** +
- 50+ EXIF fields including MakerNote
- Complete GPS (coordinates, altitude, direction, speed)
- Extended attributes (macOS)
- File hashes (integrity)
- Video streams (all codecs, bitrates, etc)
- Audio tags (complete music metadata)
- PDF metadata (author, title, security)
- SVG analysis (elements, complexity)
- Calculated metadata (aspect ratio, print size, file age)
- 🎯 **Burned-in visual metadata (OCR from watermarks)** ← UNIQUE
- 🎯 **Color palette extraction** ← UNIQUE
- 🎯 **AI-generated descriptions (VLM)** ← UNIQUE

---

### ❌ Category 14: Video Sidecar Files & Timecode (NOT IMPLEMENTED)

**Status:** ❌ Not implemented (professional video workflows)  
**Priority:** LOW (niche professional use case)

Sidecar files contain metadata that travels alongside video files - subtitles, captions, chapters, timecode overlays.

#### **Subtitle/Caption Sidecar Formats**

| Format | Description | Contains |
|--------|-------------|----------|
| `.srt` (SubRip) | Plain text subtitles | Timecode + text |
| `.scc` (Scenarist) | Closed captions | CEA-608/708 captions |
| `.vtt` (WebVTT) | Web subtitles | Timecode + text + styling |
| `.ass/.ssa` (SubStation) | Advanced subtitles | Timecode + text + complex styling |
| `.ttml` (TTML) | XML subtitles | Timecode + text + styling |
| `.stl` (EBU-STL) | Broadcast subtitles | Teletext format |
| `.itt` (iTunes) | iTunes captions | XML format |

**Extractable Metadata:**
- Timecode start/end for each subtitle
- Text content (OCR if burned-in)
- Language codes
- Styling information (font, size, color, position)
- Speaker identification
- Caption type (dialog, sound effects, music)

#### **Burned-In Timecode (BITC)**

Visual timecode overlay on video frames that requires OCR extraction:

| Field | Description | Example |
|-------|-------------|---------|
| `BurnedTimecode` | Frame-accurate timecode | "01:23:45:12" (HH:MM:SS:FF) |
| `TimecodeFormat` | Format type | "SMPTE", "Drop Frame", "Non-Drop" |
| `FrameRate` | FPS from timecode | "23.976", "29.97", "30" |
| `StartTimecode` | Video start time | "00:58:00:00" |

**Use Cases:**
- "Find video clips from 5-minute mark"
- "Extract frame at specific timecode"
- Sync external audio/subtitle files
- Frame-accurate editing workflows

**Implementation:** OCR on video frames to detect timecode overlay text, parse format.

---

### ❌ Category 15: Depth Maps & Stereoscopic 3D (NOT IMPLEMENTED)

**Status:** ❌ Not implemented (smartphone portrait mode, 3D photography)  
**Priority:** LOW (emerging feature, limited adoption)

Modern smartphones (iPhone Portrait, Google Camera Lens Blur) embed depth map data in photos.

#### **Depth Map Metadata**

| Field | Description | Format | Source |
|-------|-------------|--------|--------|
| `HasDepthMap` | Depth data present | Boolean | Check auxiliary image |
| `DepthMapWidth` | Depth map width | Pixels | EXIF auxiliary |
| `DepthMapHeight` | Depth map height | Pixels | EXIF auxiliary |
| `DepthMapFormat` | Data format | "disparity", "depth" | Apple AVDepthData |
| `DepthDataAccuracy` | Accuracy level | "relative", "absolute" | iOS |
| `DepthDataQuality` | Quality rating | 0-1 float | iOS |
| `DepthDataFiltered` | Filtering applied | Boolean | iOS |
| `DepthDataCalibration` | Calibration data | Matrix | Lens correction |
| `FocusPixelX` | Focus point X | Normalized 0-1 | iOS |
| `FocusPixelY` | Focus point Y | Normalized 0-1 | iOS |

#### **Stereoscopic 3D Metadata**

| Field | Description | Example |
|-------|-------------|---------|
| `StereoscopicMode` | 3D format | "side-by-side", "top-bottom", "anaglyph" |
| `ParallaxAmount` | Disparity amount | "5.2 pixels" |
| `ConvergencePoint` | Focal plane | "2.5 meters" |
| `InteraxialDistance` | Camera separation | "65mm" (human eye distance) |
| `3DFormat` | File format | "MPO" (Multi-Picture Object) |
| `LeftEyeImage` | Left eye data | Embedded image |
| `RightEyeImage` | Right eye data | Embedded image |

**Calculated from Depth Map:**
- Parallax offset per pixel
- Object distance from camera
- Bokeh blur amount
- 3D reconstruction data
- Z-buffer for 3D effects

**Use Cases:**
- "Show me portrait mode photos"
- "Find photos with depth data"
- "Extract depth map for 3D parallax effect"
- "Generate stereoscopic 3D from single photo"
- Refocus after capture (like Lytro)

**Implementation:** 
```python
# iOS depth extraction
from PIL import Image
import CGImageSourceCopyAuxiliaryDataInfoAtIndex

# Android Google Camera
# Depth stored in XMP metadata
# Parse XMP "GDepth" namespace
```

---

### ❌ Category 16: HDR & Tone Mapping Metadata (NOT IMPLEMENTED)

**Status:** ❌ Not implemented (HDR photography/video)  
**Priority:** LOW (professional HDR workflows)

HDR images/videos contain extended dynamic range data requiring tone mapping for display.

#### **HDR Image Metadata**

| Field | Description | Example |
|-------|-------------|---------|
| `IsHDR` | HDR image | Boolean |
| `HDRFormat` | File format | "OpenEXR", "Radiance HDR", "TIFF 32-bit" |
| `BitDepth` | Bits per channel | 16, 32 (float) |
| `DynamicRange` | Range in stops | "14.5 EV" |
| `ToneMappingOperator` | Algorithm used | "Reinhard", "Drago", "Mantiuk" |
| `ToneMappingParams` | Parameters | {"gamma": 2.2, "exposure": 0.5} |
| `ExposureBracket` | Source exposures | ["-2 EV", "0 EV", "+2 EV"] |
| `MergeMethod` | HDR merge algorithm | "Debevec", "Robertson" |
| `WhitePoint` | Peak luminance | "10000 cd/m²" |
| `BlackPoint` | Minimum luminance | "0.0001 cd/m²" |
| `LuminanceMapping` | Mapping function | "Linear", "Logarithmic", "Gamma" |

#### **HDR Video Metadata (HDR10/Dolby Vision)**

| Field | Description | Standard |
|-------|-------------|----------|
| `HDR10` | HDR10 enabled | Boolean |
| `DolbyVision` | Dolby Vision | Boolean |
| `MaxCLL` | Max content light level | "1000 nits" |
| `MaxFALL` | Max frame-average light | "400 nits" |
| `ColorPrimaries` | Color gamut | "BT.2020" |
| `TransferCharacteristics` | Transfer function | "PQ" (Perceptual Quantizer) |
| `MasteringDisplay` | Reference display | Min/max luminance |

**Calculated Values:**
- Luminance histogram (HDR range)
- Clipping detection (0-255 or beyond)
- Exposure compensation needed
- Dynamic range utilization %

**Use Cases:**
- "Find HDR photos"
- "Show me photos shot with exposure bracketing"
- "Find videos with HDR10 metadata"
- Ensure proper display on HDR monitors

---

### ❌ Category 17: Image Histograms (NOT IMPLEMENTED - CALCULATED)

**Status:** ❌ Not implemented  
**Priority:** MEDIUM (useful for exposure analysis, quality assessment)

Histograms show the distribution of pixel values across brightness/color channels.

#### **Luminance Histogram**

| Field | Description | Format |
|-------|-------------|--------|
| `LuminanceHistogram` | Brightness distribution | Array[256] (0-255) |
| `LuminanceMean` | Average brightness | 0-255 |
| `LuminanceMedian` | Middle value | 0-255 |
| `LuminanceStdDev` | Standard deviation | Float |
| `LuminancePeak` | Most common value | 0-255 |
| `LuminanceRange` | Min-max spread | [5, 250] |

**Formula:** `Luminance = 0.299*R + 0.587*G + 0.114*B` (weighted for human perception)

#### **RGB Channel Histograms**

| Channel | Description | Array |
|---------|-------------|-------|
| `RedHistogram` | Red channel distribution | Array[256] |
| `GreenHistogram` | Green channel distribution | Array[256] |
| `BlueHistogram` | Blue channel distribution | Array[256] |
| `RedMean` | Average red value | 0-255 |
| `GreenMean` | Average green value | 0-255 |
| `BlueMean` | Average blue value | 0-255 |

#### **Clipping Detection**

| Field | Description | Threshold |
|-------|-------------|-----------|
| `ShadowClipping` | Black pixels lost | Pixels at 0 |
| `HighlightClipping` | White pixels lost | Pixels at 255 |
| `RedClipped` | Red channel clipped | Pixels at 255 |
| `GreenClipped` | Green channel clipped | Pixels at 255 |
| `BlueClipped` | Blue channel clipped | Pixels at 255 |
| `ClippingPercentage` | % of clipped pixels | 0-100% |

#### **Histogram Shape Analysis**

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| `HistogramType` | Overall shape | "Low-key", "High-key", "Average-key" |
| `ContrastLevel` | Spread of values | "Low", "Medium", "High" |
| `ExposureBias` | Left/right skew | "Underexposed", "Overexposed", "Normal" |
| `TonalRange` | Dynamic range used | "Full", "Limited", "Clipped" |
| `ShadowDetail` | Detail in shadows | % of histogram in 0-64 range |
| `HighlightDetail` | Detail in highlights | % of histogram in 192-255 range |
| `MidtoneDetail` | Detail in midtones | % of histogram in 64-192 range |

#### **HSV/HSL Histogram**

| Channel | Description | Range |
|---------|-------------|-------|
| `HueHistogram` | Color distribution | 0-360° |
| `SaturationHistogram` | Vibrance distribution | 0-100% |
| `ValueHistogram` | Brightness (HSV) | 0-100% |
| `DominantHue` | Primary color | 0-360° |
| `AverageSaturation` | Color intensity | 0-100% |

**Implementation:**
```python
def calculate_histogram(image: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Calculate RGB and luminance histograms
    Returns 256-bin histograms for R, G, B, and Luminance
    """
    r_hist = np.histogram(image[:,:,0], bins=256, range=(0,255))[0]
    g_hist = np.histogram(image[:,:,1], bins=256, range=(0,255))[0]
    b_hist = np.histogram(image[:,:,2], bins=256, range=(0,255))[0]
    
    # Calculate luminance
    luminance = 0.299*image[:,:,0] + 0.587*image[:,:,1] + 0.114*image[:,:,2]
    lum_hist = np.histogram(luminance, bins=256, range=(0,255))[0]
    
    return {
        'red': r_hist,
        'green': g_hist,
        'blue': b_hist,
        'luminance': lum_hist
    }
```

**Use Cases:**
- "Show me underexposed photos" (histogram left-skewed)
- "Find photos with blown highlights" (clipping detection)
- "Show me high-contrast images" (wide histogram spread)
- "Find low-key/high-key photos" (histogram shape)
- Automatic exposure assessment

**Storage:** Store as JSON array or binary array in metadata field.

---

## 🎯 PRIORITY IMPLEMENTATION MATRIX

### 🔴 CRITICAL (Implement First)

1. **Burned-In Metadata Extraction (OCR)**
   - GPS Map Camera watermarks (compass direction!)
   - Timestamp overlays
   - Location text
   - **Impact:** Recovers lost metadata from processed photos
   - **Effort:** 2-3 days
   - **Files:** Add `ocr_visual_extractor.py`

2. **Color Palette Extraction**
   - Already prototyped in color clustering demo
   - **Impact:** Enables color-based search
   - **Effort:** 1 day (integration)
   - **Files:** Add to `metadata_extractor.py`

3. **API Endpoint `/api/metadata/schema`**
   - Dynamic field discovery
   - **Impact:** Unlocks dynamic autocomplete
   - **Effort:** 0.5 days
   - **Files:** Add to `server/main.py`

### 🟡 HIGH (Next Phase)

4. **Media-Type Specific UI Components**
   - AudioMetadataSections.tsx
   - VideoMetadataSections.tsx (expand)
   - PDFMetadataSections.tsx
   - SVGMetadataSections.tsx
   - **Impact:** Shows 70% hidden metadata
   - **Effort:** 3-4 days
   - **Files:** New components in `ui/src/components/`

5. **Calculated Metadata (Missing Fields)**
   - Time of day, season, sun position
   - Shooting conditions inference
   - **Impact:** Richer search queries
   - **Effort:** 2 days
   - **Files:** Expand `calculate_inferred_metadata()`

6. **OCR Integration into Main Metadata**
   - Move OCR from separate system to metadata_extractor
   - **Impact:** Unified metadata storage
   - **Effort:** 1 day
   - **Files:** Integrate `ocr_search.py` → `metadata_extractor.py`

### 🟢 MEDIUM (Future)

7. **Quality Analysis**
   - Sharpness, blur detection
   - Exposure quality
   - **Impact:** Quality filtering
   - **Effort:** 2-3 days
   - **Files:** Add `quality_analyzer.py`

8. **Face Metadata Integration**
   - Face count in metadata
   - Bounding boxes
   - **Impact:** "Photos with 3+ people" search
   - **Effort:** 1 day
   - **Files:** Integrate `face_clustering.py` → `metadata_extractor.py`

9. **Reverse Geocoding**
   - GPS → city/country names
   - **Impact:** Location name search
   - **Effort:** 1-2 days (with caching)
   - **Files:** Add `geocoding.py`

### 🔵 LOW (Nice to Have)

10. **Composition Analysis**
    - Rule of thirds, golden ratio
    - **Impact:** Aesthetic search
    - **Effort:** 3-4 days
    - **Files:** Add `composition_analyzer.py`

11. **VLM Scene Understanding**
    - Object detection, mood, activity
    - **Impact:** Semantic richness
    - **Effort:** 5-7 days
    - **Files:** Add `vlm_analyzer.py`

12. **Advanced PDF/SVG Features**
    - Form fields, annotations
    - SVG complexity scores
    - **Impact:** Niche use cases
    - **Effort:** 2-3 days each

---

## 🏁 NEXT STEPS

### Week 1: Burned-In Metadata (CRITICAL)
```bash
# Phase 0: Foundation
- Audit Dubai photos for GPS Map Camera watermarks
- Document findings in metadata_audit.md

# Phase 1: EXIF Baseline
- Verify GPS extraction working
- Test coordinate conversion

# Phase 2: OCR Pipeline
cd gps_metadata/
python extractors/ocr_extractor.py --input ~/Photos/dubai_2017/
python extractors/watermark_parser.py --format gps_map_camera

# Phase 3: Integration
# Add to metadata_extractor.py:
metadata['burned_in'] = extract_burned_in_metadata(filepath)
```

### Week 2: Color Palette Integration
```python
# Add to metadata_extractor.py
from color_clustering import extract_color_palette

def extract_comprehensive_metadata(filepath):
    # ... existing code ...
    metadata['colors'] = extract_color_palette(filepath)
    return metadata
```

### Week 3: UI Visibility
```typescript
// Create media-specific components
AudioMetadataSections.tsx
VideoMetadataSections.tsx (expand)
PDFMetadataSections.tsx
SVGMetadataSections.tsx

// Update DetailsTab.tsx to use them
{fileType === 'audio' && <AudioMetadataSections metadata={metadata} />}
```

---

## 📝 SUMMARY

**Current State:**
- ✅ Backend: 100+ metadata fields extracted
- ⚠️ Frontend: ~30% visible
- ❌ Burned-in visual data: 0% extracted
- ❌ Color palette: Prototyped, not integrated
- ❌ AI/VLM: Not implemented

**The Opportunity:**
PhotoSearch can extract metadata that **no other photo app extracts**, including:
1. Burned-in compass directions (OCR from GPS Map Camera)
2. Complete video stream metadata (all codecs, HDR info)
3. Perceptual color analysis (Lab color space)
4. Extended filesystem attributes
5. File integrity hashes

**The Path Forward:**
1. **Implement burned-in metadata extraction** (Week 1) → Recover lost data
2. **Integrate color palette** (Week 2) → Enable color search
3. **Build media-specific UI** (Week 3) → Expose 70% hidden metadata
4. **Add calculated fields** (Week 4) → Time of day, seasons, conditions
5. **VLM integration** (Month 2) → Scene understanding, objects, mood

---

*Document Version: 1.0*  
*Last Updated: December 26, 2024*  
*Total Metadata Fields Documented: 400+*  
*File Types Covered: Images, Videos, Audio, PDFs, SVGs*

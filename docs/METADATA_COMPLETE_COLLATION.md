# PhotoSearch: Complete Metadata Collation
## Everything We've Discussed - Implemented, Planned & Missing

**Date:** December 26, 2024  
**Project:** PhotoSearch  
**Status:** Comprehensive audit across all conversations

---

## 📊 EXECUTIVE SUMMARY

PhotoSearch has **TWO PARALLEL UNIVERSES**:

1. **Backend Universe (95% Complete)** - A Ferrari engine extracting 100+ metadata fields
2. **Frontend Universe (30% Visible)** - A bicycle showing ~20 basic fields

This document collates **everything we've discussed** across multiple conversations about metadata extraction, search capabilities, and UI features.

---

## ✅ PART 1: FULLY IMPLEMENTED (Backend)

### 1.1 Filesystem Metadata
**Implementation:** `src/metadata_extractor.py::extract_filesystem_metadata()`

**Fields Extracted:**
- `size_bytes` - File size in bytes
- `size_human` - Human-readable size (e.g., "3.2 MB")
- `created` - Creation timestamp (ISO format)
- `modified` - Last modified timestamp
- `accessed` - Last accessed timestamp
- `changed` - Metadata change timestamp (Unix)
- `permissions_octal` - Permissions in octal format (e.g., "0644")
- `permissions_human` - Human-readable permissions (e.g., "-rw-r--r--")
- `owner` - Owner username
- `owner_uid` - Owner user ID
- `group` - Group name
- `group_gid` - Group ID
- `inode` - Inode number
- `device` - Device ID
- `hard_links` - Number of hard links
- `file_type` - Type (regular, directory, symlink, etc.)

**Search Examples:**
```sql
-- Files larger than 5MB
file.size_bytes > 5242880

-- Files created in last 7 days
file.created > "2024-12-19"

-- Files owned by specific user
file.owner = "pranay"
```

---

### 1.2 Extended Attributes (macOS/Linux xattr)
**Implementation:** `src/metadata_extractor.py::extract_extended_attributes()`

**Fields Extracted:**
- `com.apple.metadata:kMDItemWhereFroms` - Download source URLs
- `com.apple.metadata:kMDItemFinderComment` - Finder comments
- `com.apple.FinderInfo` - Finder metadata
- `com.apple.quarantine` - Quarantine information
- Custom xattrs - Any user-defined extended attributes

**Availability:** macOS and Linux only (gracefully skips on Windows)

**Search Examples:**
```python
# Find files downloaded from specific domain
xattr['com.apple.metadata:kMDItemWhereFroms'] CONTAINS 'github.com'
```

---

### 1.3 Image Metadata - EXIF (ALL Tags)
**Implementation:** `src/metadata_extractor.py::extract_exif_metadata()` using `exifread`

**Categories Organized:**

#### **Image Tags**
- Make, Model, Software
- DateTime, DateTimeOriginal, DateTimeDigitized
- Orientation
- XResolution, YResolution, ResolutionUnit
- Copyright, Artist, Description
- YCbCrPositioning

#### **EXIF Photo Tags**
- ExposureTime, FNumber, ExposureProgram
- ISOSpeedRatings
- ShutterSpeedValue, ApertureValue
- BrightnessValue, ExposureBiasValue
- MaxApertureValue, SubjectDistance
- MeteringMode, LightSource, Flash
- FocalLength, SubjectArea
- MakerNote (proprietary manufacturer data)
- UserComment
- SubSecTime, SubSecTimeOriginal, SubSecTimeDigitized
- FlashPixVersion, ColorSpace
- PixelXDimension, PixelYDimension
- SensingMethod, SceneType
- ExposureMode, WhiteBalance
- DigitalZoomRatio, FocalLengthIn35mmFilm
- SceneCaptureType, GainControl
- Contrast, Saturation, Sharpness
- SubjectDistanceRange
- LensSpecification, LensMake, LensModel

#### **MakerNote (Proprietary)**
ALL manufacturer-specific data including:
- Camera serial numbers
- Lens serial numbers
- Firmware versions
- Proprietary shooting modes
- Custom settings

**Search Examples:**
```sql
-- Professional photographer queries
exif.image.Make = "Sony"
exif.photo.LensModel = "FE 85mm F1.8"
exif.photo.FNumber = "f/1.8"

-- Technical settings
exif.photo.ISOSpeedRatings > 3200
exif.photo.ExposureTime < "1/1000"

-- Artistic filters
exif.photo.SceneCaptureType = "Portrait"
exif.photo.WhiteBalance = "Auto"
```

---

### 1.4 GPS Metadata
**Implementation:** `src/metadata_extractor.py::extract_gps_metadata()`

**Fields Extracted:**
- `latitude` - Decimal degrees (DMS converted)
- `latitude_ref` - North/South
- `longitude` - Decimal degrees (DMS converted)
- `longitude_ref` - East/West
- `altitude` - Meters above/below sea level
- `altitude_ref` - Above/below sea level indicator
- `timestamp` - GPS time
- `datestamp` - GPS date
- `speed` - Speed at capture
- `speed_ref` - Speed unit (km/h, mph, knots)
- `track` - Direction of movement
- `track_ref` - True/Magnetic north
- `image_direction` - **Camera pointing direction** (critical for globe viz)
- `image_direction_ref` - True/Magnetic north
- `satellites` - Number of satellites used
- `dop` - Dilution of Precision (accuracy metric)
- `map_datum` - Geodetic datum (WGS-84, etc.)
- `processing_method` - GPS/GLONASS/Galileo

**Search Examples:**
```sql
-- Location-based queries
gps.latitude BETWEEN 40.7 AND 40.8
gps.longitude BETWEEN -74.0 AND -73.9

-- Photos taken at high altitude
gps.altitude > 2000

-- Camera direction (for directional search)
gps.image_direction BETWEEN 90 AND 180  -- East to South
```

---

### 1.5 Image Properties (Pillow)
**Implementation:** `src/metadata_extractor.py::extract_image_properties()`

**Fields Extracted:**
- `width` - Image width in pixels
- `height` - Image height in pixels
- `format` - Image format (JPEG, PNG, HEIC, WebP, etc.)
- `mode` - Color mode (RGB, RGBA, CMYK, Grayscale, etc.)
- `dpi` - Dots per inch (tuple: x, y)
- `bits_per_pixel` - Color depth
- `color_palette` - Whether image has color palette
- `animation` - Is animated (GIF, APNG)
- `frames` - Number of frames (for animations)
- `icc_profile` - Whether ICC profile is embedded

**Search Examples:**
```sql
-- High resolution images
image.width >= 4000
image.height >= 3000

-- Print-ready files
image.dpi >= 300

-- Animated images only
image.animation = true
```

---

### 1.6 Video Metadata (ffprobe - ALL Fields)
**Implementation:** `src/metadata_extractor.py::extract_video_properties()` using `ffmpeg-python`

**Data Structure:** Full ffprobe output including:

#### **Format Level**
- `format_name`, `format_long_name`
- `duration`, `size`, `bit_rate`
- `probe_score`, `start_time`
- `nb_streams`, `nb_programs`
- ALL format-level tags (title, artist, album, date, comment, encoder)

#### **Video Streams** (per stream)
- **Codec:** codec_name, codec_long_name, codec_type, profile
- **Dimensions:** width, height, coded_width, coded_height
- **Aspect Ratio:** sample_aspect_ratio, display_aspect_ratio
- **Frame Rate:** r_frame_rate, avg_frame_rate
- **Color:** pix_fmt, color_range, color_space, color_transfer, color_primaries
- **Quality:** has_b_frames, level, refs, bit_rate, bits_per_raw_sample
- **Timing:** time_base, start_pts, start_time, duration_ts, duration
- **Frames:** nb_frames

#### **Audio Streams** (per stream)
- **Codec:** codec_name, codec_long_name
- **Format:** sample_fmt, sample_rate
- **Channels:** channels, channel_layout
- **Quality:** bits_per_sample, bit_rate
- **Timing:** time_base, start_time, duration
- **Language:** language tag

#### **Subtitle Streams**
- codec_name, codec_long_name, codec_type
- language
- Format tags

#### **Chapters**
- id, time_base
- start, start_time
- end, end_time
- tags (chapter title, etc.)

**Search Examples:**
```sql
-- 4K videos
video.streams[0].width >= 3840

-- Long videos
video.format.duration > 300  -- 5+ minutes

-- High bitrate
video.format.bit_rate > 10000000  -- 10 Mbps
```

---

### 1.7 Audio Metadata (mutagen - ALL Tags)
**Implementation:** `src/metadata_extractor.py::extract_audio_properties()` using `mutagen`

**Supported Formats:** MP3, FLAC, OGG, WAV, AAC, M4A, MP4 audio

**Fields Extracted:**

#### **Format Information**
- `format` - Audio format type
- `length_seconds` - Duration in seconds
- `length_human` - Duration in MM:SS format
- `bitrate` - Audio bitrate
- `sample_rate` - Sample rate (Hz)
- `channels` - Number of channels
- `bits_per_sample` - Bit depth

#### **Common Tags** (normalized across formats)
- `title` - Track title
- `artist` - Artist name
- `album` - Album name
- `year` / `date` - Release year
- `genre` - Music genre
- `track_number` - Track number
- `disc_number` - Disc number
- `composer` - Composer name
- `album_artist` - Album artist
- `comment` - Comments
- `lyrics` - Song lyrics
- `bpm` - Beats per minute
- `compilation` - Compilation flag
- `copyright` - Copyright notice
- `encoder` - Encoder software

#### **ID3 Tags (MP3 Specific)**
- TIT2 (title), TPE1 (artist), TALB (album)
- TDRC (year), TCON (genre)
- TRCK (track), TPOS (disc)
- COMM (comment), USLT (lyrics)
- APIC (album art)

#### **Vorbis Comments (FLAC/OGG)**
- All standard Vorbis fields
- Custom user tags

#### **iTunes Tags (M4A/MP4)**
- ©nam, ©ART, ©alb, ©day, ©gen
- trkn, disk, covr

#### **Album Art**
- `has_album_art` - Boolean flag
- `album_art_count` - Number of embedded images

**Search Examples:**
```sql
-- Find music by artist
audio.tags.artist = "The Beatles"

-- High quality audio
audio.sample_rate >= 96000
audio.bits_per_sample >= 24

-- Classical music
audio.tags.genre = "Classical"
audio.tags.composer IS NOT NULL
```

---

### 1.8 PDF Metadata (pypdf)
**Implementation:** `src/metadata_extractor.py::extract_pdf_properties()` using `pypdf`

**Fields Extracted:**
- `page_count` - Number of pages
- `encrypted` - Whether PDF is encrypted
- `author` - Document author
- `creator` - Creating application
- `producer` - PDF producer
- `subject` - Document subject
- `title` - Document title
- `creation_date` - Creation timestamp
- `modification_date` - Last modification timestamp
- `keywords` - Document keywords
- `page_width` - First page width (points)
- `page_height` - First page height (points)

**Search Examples:**
```sql
-- Find invoices by author
pdf.author = "John Doe"

-- Multi-page documents
pdf.page_count > 10

-- Recent PDFs
pdf.creation_date > "2024-01-01"
```

---

### 1.9 SVG Metadata (XML Parsing)
**Implementation:** `src/metadata_extractor.py::extract_svg_properties()`

**Fields Extracted:**
- `width` - SVG width attribute
- `height` - SVG height attribute
- `viewBox` - ViewBox attribute
- `version` - SVG version
- `viewBox_width` - Extracted from viewBox
- `viewBox_height` - Extracted from viewBox
- `element_count` - Total number of XML elements
- `path_count` - Number of path elements
- `has_embedded_styles` - Boolean flag
- `has_scripts` - Security: JavaScript presence
- Dublin Core metadata (if present):
  - `title`, `description`
  - `dc:creator`, `dc:rights`, `dc:date`

**Search Examples:**
```sql
-- Large SVGs
svg.viewBox_width > 1000

-- SVGs with scripts (security check)
svg.has_scripts = true

-- Find by creator
svg.dc:creator = "Illustrator Team"
```

---

### 1.10 File Integrity Hashes
**Implementation:** `src/metadata_extractor.py::extract_file_hashes()`

**Fields Extracted:**
- `md5` - MD5 hash (128-bit)
- `sha256` - SHA256 hash (256-bit)

**Use Cases:**
- Duplicate detection (exact matches)
- File integrity verification
- Forensic analysis
- Change detection

**Search Examples:**
```sql
-- Find exact duplicates
hashes.md5 = "a1b2c3d4e5f6..."

-- Verify file integrity
hashes.sha256 = "known_good_hash"
```

---

### 1.11 Calculated/Inferred Metadata
**Implementation:** `src/metadata_extractor.py::calculate_inferred_metadata()`

**Image Calculations:**
- `aspect_ratio` - Ratio string (e.g., "16:9", "4:3")
- `aspect_ratio_decimal` - Decimal value (e.g., 1.778)
- `megapixels` - Total megapixels (rounded to 2 decimals)
- `orientation` - Landscape/Portrait/Square

**Video Calculations:**
- `duration_human` - MM:SS format
- `size_per_second` - Bitrate expressed as size/second

**Time-Based Calculations:**
- `file_age`
  - `days` - Age in days
  - `hours` - Age in hours
  - `human_readable` - "3 days ago", "2 hours ago"
- `time_since_modified`
  - Same structure as file_age
- `time_since_accessed`
  - Same structure as file_age

**Search Examples:**
```sql
-- Wide aspect images (cinematic)
calculated.aspect_ratio_decimal > 2.0

-- High resolution
calculated.megapixels > 12

-- Recent files
calculated.file_age.days < 7

-- Portrait orientation
calculated.orientation = "portrait"
```

---

### 1.12 Thumbnail Extraction
**Implementation:** `src/metadata_extractor.py::extract_thumbnail()`

**Fields Extracted:**
- `has_embedded` - Whether EXIF thumbnail exists
- `width` - Thumbnail width (pixels)
- `height` - Thumbnail height (pixels)

**Behavior:**
- Extracts embedded EXIF thumbnail if present
- Generates 160x160 thumbnail if no embedded version
- Used for fast gallery display

---

## ❌ PART 2: PLANNED BUT NOT YET IMPLEMENTED

### 2.1 Color Palette Extraction
**Status:** ❌ Discussed, not implemented in metadata_extractor.py

**What We Discussed:**
From conversations about color-based search and the color clustering demo:
- Extract **5 dominant colors** per image
- Use **k-means clustering** on pixel data
- Store as hex color palette
- Enable search by color/vibe ("warm sunset colors")

**Mentioned In:**
- Color-based clustering conversation (December 17, 2024)
- LinkedIn article about Advay seeing "exact shade of blue"
- Instagram strategy for PhotoSearch

**Implementation Needed:**
```python
def extract_color_palette(filepath: str) -> Dict[str, Any]:
    """
    Extract dominant color palette using k-means clustering
    
    Returns:
        {
            "dominant_colors": ["#FF6B35", "#F7931E", "#004E89", ...],  # 5 colors
            "color_percentages": [0.35, 0.25, 0.20, 0.15, 0.05],
            "perceptual_dominance_scores": [0.92, 0.78, 0.65, 0.45, 0.22],
            "lab_values": [[L, a, b], ...],  # For CIEDE2000 comparison
        }
    """
```

**Where It Fits:**
- Add to `metadata_extractor.py` as new function
- Store in `metadata` JSON under `"colors"` key
- Enable semantic search: "photos with golden tones"

**Search Examples:**
```sql
-- Color-based search
colors.dominant_colors CONTAINS "#FF6B35"

-- Warm-toned images
colors.perceptual_dominance_scores[0] > 0.8 
AND colors.lab_values[0][0] > 50  -- High luminance
AND colors.lab_values[0][1] > 0   -- Positive a* (red)
```

---

### 2.2 Reverse Geocoding (GPS → Location Names)
**Status:** ❌ Discussed December 15, 2024, not implemented

**What We Discussed:**
- Convert GPS coordinates to human-readable names
- City, country, landmark names
- Enable search by place name instead of coordinates
- Cache results to avoid repeated API calls

**Implementation Needed:**
```python
def reverse_geocode(latitude: float, longitude: float) -> Dict[str, str]:
    """
    Convert GPS coordinates to location names
    
    Args:
        latitude: Decimal degrees latitude
        longitude: Decimal degrees longitude
        
    Returns:
        {
            "city": "San Francisco",
            "state": "California",
            "country": "United States",
            "country_code": "US",
            "landmark": "Golden Gate Bridge",  # If near landmark
            "formatted_address": "Golden Gate Bridge, San Francisco, CA, USA"
        }
    """
```

**API Options:**
- **Nominatim** (OpenStreetMap) - Free, rate-limited
- **Google Geocoding API** - Paid, accurate
- **Mapbox** - Paid, modern
- **Here** - Paid, enterprise

**Search Examples:**
```sql
-- Natural language location search
location.city = "Paris"
location.country = "France"
location.landmark CONTAINS "Eiffel Tower"
```

---

### 2.3 Time-of-Day Inference
**Status:** ❌ Discussed December 15, 2024, not implemented

**What We Discussed:**
- Detect "golden hour", "blue hour", "night shot"
- Based on EXIF timestamp + GPS coordinates
- Calculate sun position using astronomical algorithms
- Classify lighting conditions

**Implementation Needed:**
```python
def infer_time_of_day(timestamp: datetime, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Infer lighting conditions from timestamp and location
    
    Returns:
        {
            "time_category": "golden_hour",  # sunrise, golden_hour, midday, sunset, blue_hour, night
            "sun_altitude": 5.2,  # Degrees above horizon
            "sun_azimuth": 245.8,  # Compass direction
            "confidence": 0.95
        }
    """
```

**Libraries:**
- **ephem** - Astronomical calculations
- **suncalc** - Sun position
- **astral** - Sunrise/sunset times

**Search Examples:**
```sql
-- Find golden hour photos
time_of_day.time_category = "golden_hour"

-- Sunset direction
time_of_day.time_category = "sunset"
AND time_of_day.sun_azimuth BETWEEN 240 AND 300  -- West-southwest
```

---

### 2.4 Weather Data Enrichment
**Status:** ❌ Discussed December 15, 2024, not implemented

**What We Discussed:**
- Optional API call to add weather at time of capture
- Temperature, conditions (sunny, cloudy, rainy)
- Enable search by weather conditions
- Historical weather data services

**Implementation Needed:**
```python
def get_historical_weather(
    latitude: float,
    longitude: float,
    timestamp: datetime
) -> Dict[str, Any]:
    """
    Get weather conditions at time of photo capture
    
    Returns:
        {
            "temperature_c": 22,
            "temperature_f": 72,
            "condition": "Partly Cloudy",
            "precipitation": 0.0,
            "humidity": 65,
            "wind_speed_kmh": 12,
            "wind_direction": "NW"
        }
    """
```

**API Options:**
- **OpenWeatherMap** (paid historical data)
- **Visual Crossing** (historical weather)
- **Weatherstack** (historical API)

**Search Examples:**
```sql
-- Photos taken in the rain
weather.precipitation > 0

-- Hot summer days
weather.temperature_c > 30

-- Windy conditions
weather.wind_speed_kmh > 20
```

---

### 2.5 Duplicate Detection (Perceptual Hashing)
**Status:** ❌ Discussed December 15, 2024, not implemented

**What We Discussed:**
- Use **perceptual hashing** (pHash, dHash, aHash)
- Find visually similar images (not just identical files)
- Detect crops, resizes, slight edits
- Calculate similarity scores

**Implementation Needed:**
```python
def calculate_perceptual_hash(filepath: str) -> Dict[str, str]:
    """
    Calculate perceptual hashes for duplicate detection
    
    Returns:
        {
            "phash": "8f373714acfac8d1",  # Perceptual hash
            "dhash": "c3e1e1c1c3878f1f",  # Difference hash
            "ahash": "ffffffc080000000",  # Average hash
            "whash": "3c3c187e7e3c1818"   # Wavelet hash
        }
    """
```

**Libraries:**
- **imagehash** - Python library for perceptual hashing
- **opencv** - Image processing

**Use Cases:**
- Find duplicate/similar photos
- Detect edits of same original
- Group burst shots
- Identify crops and resizes

**Search Examples:**
```python
# Find images similar to target
similarity = hamming_distance(target_phash, candidate_phash)
if similarity < 10:  # Threshold for "similar"
    # Images are likely duplicates or crops
```

---

### 2.6 OCR Text Extraction Metadata
**Status:** ⚠️ Partially implemented (src/ocr_search.py exists) but NOT in metadata_extractor.py

**What We Discussed:**
- Extract text from images using Tesseract
- Store OCR text as searchable metadata
- Enable search by text content in photos
- Confidence scores for extracted text

**Current State:**
- `src/ocr_search.py` exists with full implementation
- NOT integrated into `metadata_extractor.py`
- OCR results stored in separate `ocr_index.db`

**Should Be Added:**
```python
def extract_ocr_text(filepath: str) -> Dict[str, Any]:
    """
    Extract text from images via OCR
    
    Returns:
        {
            "text": "Full extracted text",
            "confidence": 0.92,
            "language": "eng",
            "blocks": [
                {
                    "text": "Block 1 text",
                    "confidence": 0.95,
                    "bbox": [x, y, width, height]
                },
                ...
            ]
        }
    """
```

**Integration Needed:**
- Add OCR extraction to `metadata_extractor.py`
- Store in metadata JSON under `"ocr"` key
- Optionally: keep separate FTS5 index for performance

---

### 2.7 Face Detection Metadata
**Status:** ⚠️ Partially implemented (src/face_clustering.py exists) but NOT in metadata_extractor.py

**What We Discussed:**
- Detect faces in images
- Extract face bounding boxes
- Face embeddings for recognition
- Store detected face metadata

**Current State:**
- `src/face_clustering.py` exists with full clustering
- Face detection results in separate `faces.db`
- NOT integrated into metadata extraction

**Should Be Added:**
```python
def extract_face_metadata(filepath: str) -> Dict[str, Any]:
    """
    Detect faces and extract metadata
    
    Returns:
        {
            "faces_detected": 3,
            "faces": [
                {
                    "bbox": [x, y, width, height],
                    "confidence": 0.98,
                    "landmarks": {
                        "left_eye": [x, y],
                        "right_eye": [x, y],
                        "nose": [x, y],
                        "mouth_left": [x, y],
                        "mouth_right": [x, y]
                    },
                    "embedding": [...]  # 512-d vector
                },
                ...
            ]
        }
    """
```

**Integration Needed:**
- Add face detection to `metadata_extractor.py`
- Store basic face metadata (count, bboxes)
- Keep embeddings in separate DB for clustering
- Enable search: "photos with 3+ people"

---

### 2.8 Histogram/Color Distribution
**Status:** ❌ Not implemented

**What We Discussed:**
- RGB, HSV, Lab color histograms
- Detect dominant color temperatures (warm/cool)
- Black & white detection
- Contrast and tonal range analysis

**Implementation Needed:**
```python
def analyze_color_distribution(filepath: str) -> Dict[str, Any]:
    """
    Analyze color distribution and histogram
    
    Returns:
        {
            "is_grayscale": False,
            "is_black_and_white": False,
            "color_temperature": "warm",  # warm/cool/neutral
            "dominant_hue": "red-orange",
            "saturation_average": 0.65,
            "brightness_average": 0.72,
            "contrast_score": 0.68,
            "histogram_rgb": [...],  # 256 bins per channel
            "histogram_hsv": [...],
            "tonal_range": {
                "shadows": 0.15,   # % pixels in shadows
                "midtones": 0.70,
                "highlights": 0.15
            }
        }
    """
```

**Search Examples:**
```sql
-- Black and white photos
color_distribution.is_black_and_white = true

-- High contrast images
color_distribution.contrast_score > 0.8

-- Warm-toned
color_distribution.color_temperature = "warm"
```

---

### 2.9 Blur/Sharpness Detection
**Status:** ❌ Not implemented

**What We Discussed:**
- Detect out-of-focus images
- Measure image sharpness
- Enable filtering of blurry photos
- Quality scoring

**Implementation Needed:**
```python
def analyze_sharpness(filepath: str) -> Dict[str, Any]:
    """
    Detect blur and measure sharpness
    
    Returns:
        {
            "sharpness_score": 0.85,  # 0-1, higher is sharper
            "is_blurry": False,
            "blur_type": None,  # motion_blur, out_of_focus, None
            "focus_regions": [
                {
                    "bbox": [x, y, w, h],
                    "sharpness": 0.92
                }
            ]
        }
    """
```

**Algorithms:**
- **Laplacian variance** - Simple edge detection
- **FFT analysis** - Frequency domain
- **Sobel gradient** - Edge strength

**Search Examples:**
```sql
-- Only sharp photos
sharpness.sharpness_score > 0.7

-- Exclude blurry images
sharpness.is_blurry = false
```

---

### 2.10 Composition Analysis
**Status:** ❌ Not implemented (mentioned in VLM discussions)

**What We Discussed:**
- Rule of thirds compliance
- Golden ratio detection
- Symmetry analysis
- Leading lines detection
- Visual balance scoring

**Implementation Needed:**
```python
def analyze_composition(filepath: str) -> Dict[str, Any]:
    """
    Analyze photographic composition
    
    Returns:
        {
            "rule_of_thirds": 0.85,  # How well it follows rule
            "golden_ratio": 0.72,
            "symmetry_score": 0.45,  # 0=asymmetric, 1=perfect symmetry
            "has_leading_lines": True,
            "balance_score": 0.78,
            "horizon_level": True,
            "horizon_position": 0.33  # Relative position (0-1)
        }
    """
```

**Search Examples:**
```sql
-- Well-composed photos
composition.rule_of_thirds > 0.8

-- Symmetric compositions
composition.symmetry_score > 0.7

-- Landscape with rule of thirds horizon
composition.horizon_level = true
AND composition.horizon_position BETWEEN 0.3 AND 0.4
```

---

### 2.11 Subject Detection (VLM-based)
**Status:** ❌ Planned for VLM integration

**What We Discussed:**
- Object detection (people, animals, vehicles, etc.)
- Scene classification (indoor, outdoor, beach, mountain, etc.)
- Activity recognition (sports, dining, celebration, etc.)
- Emotion/mood detection

**Implementation Needed:**
```python
def detect_subjects_vlm(filepath: str) -> Dict[str, Any]:
    """
    Use VLM to detect subjects and classify scene
    
    Returns:
        {
            "objects": [
                {"name": "person", "confidence": 0.95, "bbox": [...]},
                {"name": "dog", "confidence": 0.89, "bbox": [...]},
            ],
            "scene_type": "outdoor_park",
            "activities": ["walking", "playing"],
            "mood": "joyful",
            "style": "candid"
        }
    """
```

**VLM Options:**
- **SmolVLM-256M** (browser) - Basic detection
- **Qwen2-VL-2B** (desktop) - Good quality
- **Qwen2.5-VL-7B** (Pro tier) - Best quality
- **GPT-4o/Gemini** (cloud) - SOTA results

---

## ⚠️ PART 3: IMPLEMENTED BUT NOT VISIBLE (UI Gap)

### 3.1 Frontend Display Gaps

**What's Missing from UI:**

#### **Extended Attributes (100% missing)**
- All xattr data hidden from users
- Should show: Finder comments, tags, download sources
- Component needed: `ExtendedAttributesSection.tsx`

#### **Advanced EXIF (70% missing)**
Currently showing: Make, Model, ISO, Aperture, Shutter, Focal Length, Flash
Missing: 
- White Balance
- Color Space, ICC Profile
- Metering Mode, Scene Type
- Exposure Bias, Exposure Mode
- Digital Zoom, Gain Control
- Contrast, Saturation, Sharpness
- Lens aperture max
- Subject distance range
- All MakerNote data

Component: Expand `DetailsTab.tsx` EXIF section

#### **Calculated Metadata (100% missing)**
- Aspect ratio display
- Megapixels
- File age ("3 days ago")
- Time since modified
- Orientation label

Component: Add `CalculatedMetadataSection.tsx`

#### **Video Metadata (90% missing)**
Currently showing: Duration, format, bitrate
Missing:
- All video streams info
- Audio streams
- Subtitle tracks
- Chapters
- Format tags
- Detailed codec info

Component: Expand `VideoMetadataSection.tsx`

#### **Audio Metadata (100% missing)**
NOTHING shown for audio files
Missing:
- Artist, album, title
- Genre, year
- Track/disc numbers
- Album art
- Bitrate, sample rate
- All tags

Component: Create `AudioMetadataSections.tsx`

#### **PDF Metadata (100% missing)**
NOTHING shown for PDFs
Missing:
- Author, title, subject
- Page count
- Creation/modification dates
- Creator/producer software

Component: Create `PDFMetadataSections.tsx`

#### **SVG Metadata (100% missing)**
NOTHING shown for SVGs
Missing:
- Dimensions
- Element counts
- Has scripts flag
- Creator info

Component: Create `SVGMetadataSections.tsx`

---

### 3.2 Search UI Gaps

**MetadataFieldAutocomplete Hardcoded**
- Only 16 fields hardcoded
- Should pull from `/api/metadata/schema` endpoint
- Should show field types and example values
- Should show counts ("Canon (450 photos)")

**No Query Templates**
- No pre-built queries for different user types
- Photographers need: technical queries
- Accountants need: receipt/document queries
- Personal users need: memory/people queries

**No Visual Query Builder**
- Must type queries manually
- Non-technical users struggle
- Should have drag-drop query builder
- Filter panels for common fields

**No Match Explanations**
- Results shown without context
- Should explain WHY each result matched
- Confidence scores
- Matching fields highlighted

**No "Did You Mean?" Suggestions**
- When no results found
- No refinement suggestions
- No alternative queries offered

**No Search History**
- Doesn't remember successful searches
- No quick access to past queries
- No learning from user behavior

---

## 🔍 PART 4: SEARCH CAPABILITIES

### 4.1 Current Search Modes (Implemented)

#### **Metadata SQL Search**
**Status:** ✅ Fully implemented
**Files:** `src/metadata_search.py`, `server/main.py`

**Capabilities:**
- Structured metadata queries
- Dot notation field access (e.g., `exif.image.Make`)
- Operators: `=`, `>`, `<`, `>=`, `<=`, `LIKE`, `CONTAINS`, `:`
- User-friendly shortcuts: `camera:Canon`, `size:>5MB`
- Compound queries with AND

**Examples:**
```sql
camera.make = "Sony"
lens.focal_length >= 85
ISO > 1600
filename:vacation
date.taken >= "2024-01-01"
```

#### **Semantic CLIP Search**
**Status:** ✅ Fully implemented
**Files:** `server/embedding_generator.py`, `server/lancedb_store.py`

**Capabilities:**
- Natural language image search
- CLIP embeddings (text-to-image)
- LanceDB vector storage
- Score normalization
- Minimum threshold (0.22)

**Examples:**
```
"sunset over ocean"
"people celebrating"
"red sports car"
"birthday party"
```

#### **Hybrid Fusion Search**
**Status:** ✅ Fully implemented with intent-based weighting
**Files:** `server/main.py`, `src/intent_recognition.py`

**Capabilities:**
- Automatic combination of metadata + semantic
- Intent detection determines weights
- Dynamic weighting based on query type:
  - Metadata-heavy: 70% metadata, 30% semantic
  - Semantic-heavy: 40% metadata, 60% semantic
  - Balanced: 50/50
- Deduplication across sources
- Combined confidence scoring

**Examples:**
```
"golden hour portrait Sony 85mm"
→ Metadata: lens=85mm, camera=Sony
→ Semantic: "golden hour portrait" similarity

"birthday party 2023 Canon"
→ Metadata: date=2023, camera=Canon
→ Semantic: "birthday party" visual similarity
```

---

### 4.2 Intent Recognition (Implemented)

**Status:** ✅ Fully implemented
**Files:** `src/intent_recognition.py`, `server/main.py`

**Detected Intents (12 types):**
1. `camera` - Camera/lens queries
2. `date` - Time-based queries
3. `technical` - Technical settings (ISO, aperture, etc.)
4. `people` - Person detection
5. `object` - Object recognition
6. `scene` - Scene understanding
7. `location` - GPS/place queries
8. `color` - Color-based search
9. `action` - Activity/event detection
10. `quality` - Quality/aesthetic queries
11. `metadata` - General metadata queries
12. `text` - OCR text search

**API Endpoints:**
- `GET /api/intent/detect?query={query}` - Detect intent
- `GET /intent/detect?query={query}` - Alternate path
- `GET /intent/suggestions?query={query}` - Query suggestions
- `GET /intent/badges?query={query}` - Intent badges for UI
- `GET /intent/all` - All intent types

---

### 4.3 OCR Search (Implemented)

**Status:** ✅ Fully implemented
**Files:** `src/ocr_search.py`, `server/main.py`

**Capabilities:**
- Tesseract integration
- FTS5 full-text search index
- Multi-language support
- OCR statistics tracking
- Confidence scoring

**API Endpoints:**
- `POST /api/ocr/extract` - Extract text from image
- `POST /api/ocr/search` - Search OCR text
- `GET /api/ocr/stats` - OCR statistics

**Search Examples:**
```
"receipt from Staples"
"invoice December"
"handwritten notes project"
```

---

### 4.4 Face Clustering (Implemented)

**Status:** ✅ Fully implemented
**Files:** `src/face_clustering.py`, `server/main.py`

**Capabilities:**
- MTCNN face detection
- FaceNet embeddings
- DBSCAN clustering
- Cluster management
- Face naming/labeling

**API Endpoints:**
- `POST /api/faces/scan` - Scan photos for faces
- `GET /api/faces/clusters` - Get all face clusters
- `POST /api/faces/clusters/{id}/rename` - Name a person
- `POST /api/faces/clusters/merge` - Merge clusters
- `GET /api/faces/photos/{cluster_id}` - Photos of person

---

### 4.5 Missing Search Features

#### **Smart Auto-Routing**
**Status:** ❌ Planned, not implemented

**What's Needed:**
- Single `/api/search/smart` endpoint
- Automatic mode selection based on query
- No manual mode picker in UI
- Transparent intent indication

**Current State:**
- User must choose mode manually
- Intent detection exists but not fully integrated
- Should be automatic based on query content

#### **NLP Query Parser**
**Status:** ❌ Planned, not fully implemented

**What's Needed:**
- Natural language to SQL conversion
- Rule-based + LLM fallback
- Handle queries like:
  - "photos of Sarah at the beach last summer"
  - "receipts from December"
  - "low light concert shots"

**Current State:**
- Basic pattern matching exists in intent recognition
- No full NLP parser
- Can't handle complex natural language

#### **Live Match Count**
**Status:** ❌ Planned, not implemented

**What's Needed:**
- `/api/search/count` endpoint
- Return estimated count as user types
- Sub-100ms response time
- Show "~142 results" badge

#### **Match Explanations**
**Status:** ⚠️ Backend generates, frontend doesn't show

**What's Needed:**
- Display why each result matched
- Show matching fields
- Confidence scores
- Visual highlighting

**Current State:**
- Backend generates explanations
- Not surfaced in UI

#### **Search Suggestions**
**Status:** ❌ Planned, not implemented

**What's Needed:**
- Autocomplete dropdown
- Recent searches
- Popular searches
- Learned from user behavior
- Smart query refinements

#### **Reverse Image Search**
**Status:** ❌ Planned, not implemented

**What's Needed:**
- Drag-drop image to find similar
- Visual similarity using CLIP
- Show similarity scores
- "Find more like this" button

---

## 📈 PART 5: PRIORITIZED IMPLEMENTATION ROADMAP

### Phase 1: Critical Visibility (Weeks 1-2)

**Goal:** Expose what we already have

**Backend:**
1. ✅ Create `/api/metadata/schema` endpoint
   - Return all available fields
   - Include field types and example values
   - Show counts per field value

**Frontend:**
2. ✅ Make `MetadataFieldAutocomplete` dynamic
   - Pull from schema endpoint
   - Show field types
   - Display example values with counts

3. ✅ File type-specific DetailsTab sections
   - `AudioMetadataSections.tsx`
   - Expand `VideoMetadataSections.tsx`
   - `PDFMetadataSections.tsx`
   - `SVGMetadataSections.tsx`

4. ✅ Show calculated metadata
   - Aspect ratio, megapixels
   - File age ("3 days ago")
   - Orientation

5. ✅ Conditional rendering
   - Only show sections when data present
   - File type detection
   - Empty state handling

---

### Phase 2: Smart Search (Weeks 3-4)

**Goal:** Make search intelligent and automatic

**Backend:**
6. ✅ `/api/search/smart` endpoint
   - Auto-detect intent
   - Route to appropriate search mode
   - Return unified results

7. ✅ `/api/search/count` endpoint
   - Fast count estimation
   - Sub-100ms response

8. ✅ NLP query parser
   - Rule-based patterns
   - LLM fallback for complex queries
   - Convert natural language to SQL

**Frontend:**
9. ✅ Remove manual mode selection
   - System chooses automatically
   - Show detected intent
   - Transparent to user

10. ✅ Live match count badge
    - Show count as user types
    - "~142 results" indicator

11. ✅ Match explanation cards
    - Show why result matched
    - Confidence scores
    - Highlight matching fields

---

### Phase 3: New Metadata (Weeks 5-6)

**Goal:** Add missing metadata extraction

**Implementation:**
12. ✅ Color palette extraction
    - 5 dominant colors per image
    - Perceptual color scoring
    - Lab color space
    - CIEDE2000 comparison

13. ✅ Reverse geocoding
    - GPS → city/country/landmark
    - Cache results
    - Enable location name search

14. ✅ OCR integration into metadata
    - Add to `metadata_extractor.py`
    - Store in metadata JSON
    - Keep FTS5 for performance

15. ✅ Face metadata integration
    - Add face count to metadata
    - Store bounding boxes
    - Enable "photos with 3+ people" search

---

### Phase 4: Advanced Features (Weeks 7-8)

**Goal:** Quality and discovery

**Implementation:**
16. ✅ Composition analysis
    - Rule of thirds
    - Golden ratio
    - Symmetry detection

17. ✅ Sharpness detection
    - Blur analysis
    - Quality scoring

18. ✅ Time-of-day inference
    - Golden hour detection
    - Sun position calculation

19. ✅ Duplicate detection
    - Perceptual hashing
    - Similarity scoring

---

### Phase 5: UI Polish (Weeks 9-10)

**Goal:** Professional search experience

**Frontend:**
20. ✅ Visual query builder
    - Drag-drop query construction
    - Filter panels
    - No typing required

21. ✅ Query templates
    - Photographer templates
    - Accountant templates
    - Personal templates

22. ✅ Search history
    - Remember successful searches
    - Quick access panel

23. ✅ "Did you mean?" suggestions
    - When no results found
    - Query refinements

24. ✅ Discovery sidebar
    - "Photos from same day"
    - "Same location"
    - "Same camera"

---

## 🎯 SUMMARY

### What We Have
- **95% Complete Backend** - Extracting 100+ metadata fields
- **30% Visible Frontend** - Showing ~20 basic fields
- **Comprehensive Search** - 3 modes fully implemented
- **Intent Recognition** - 12 intent types detected
- **OCR & Faces** - Separate systems, working

### What We're Missing
- **Color palette extraction** - Discussed, not built
- **Reverse geocoding** - Planned, not built
- **Time-of-day inference** - Planned, not built
- **Weather enrichment** - Planned, not built
- **Duplicate detection** - Discussed, not built
- **Composition analysis** - VLM-dependent, planned
- **Sharpness detection** - Quality tier, planned

### Critical Next Steps
1. **Create `/api/metadata/schema`** - Unlock dynamic autocomplete
2. **Build media-specific UI sections** - Show what we extract
3. **Implement smart auto-routing** - No manual mode selection
4. **Add color palette extraction** - Enable color search
5. **Integrate OCR/faces into metadata** - Unified discovery

---

**The Opportunity:** We have a Ferrari engine. We just need to build a dashboard that shows what it can do.

**The Path:** Systematic UI development to close the 70% visibility gap, starting with exposing what already exists, then adding missing metadata extraction features.

---

*Document Version: 1.0*  
*Last Updated: December 26, 2024*  
*Compiled from: 15+ conversation threads, codebase audit, master reference doc*

# MetaExtract v4.0 - Ultimate Metadata Extraction Engine

**The world's most comprehensive metadata extraction system - extracting a comprehensive universe of metadata fields across digital domains.**

## 🌟 What's New in v4.0

MetaExtract v4.0 introduces the **Comprehensive Metadata Engine** - a revolutionary system that can extract a comprehensive universe of metadata fields from any file type across digital domains:

### 🎯 Comprehensive Coverage

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

### 🚀 Performance & Scale

- **Comprehensive metadata field coverage** (up from 7,000+)
- **10 specialized extraction engines**
- **Advanced caching** with Redis support
- **Batch processing** for multiple files
- **GPU acceleration** for AI features
- **Professional-grade performance**

## ✨ Core Features

- **Comprehensive Metadata Fields** - The world's most comprehensive extraction system
- **Specialized Engines** - Medical, Astronomical, Geospatial, Scientific, AI Detection
- **Parsed MakerNotes** - Canon, Nikon, Sony, Fujifilm, Olympus, Panasonic, Apple, DJI, GoPro
- **Full IPTC/XMP** - 50+ IPTC fields, 200+ XMP namespaces
- **Multi-Format Support** - Images, Video, Audio, PDF, SVG, RAW, DICOM, FITS, HDF5, NetCDF
- **Forensic Analysis** - AI detection, steganography, manipulation detection
- **File Integrity** - MD5, SHA256, SHA1, CRC32 checksums
- **Privacy First** - Files processed in RAM, deleted immediately

## 📁 Supported File Types

| Category  | Formats                                     |
| --------- | ------------------------------------------- |
| Images    | JPEG, PNG, GIF, WebP, TIFF, BMP, HEIC/HEIF  |
| RAW       | CR2, CR3, NEF, ARW, DNG, ORF, RW2, RAF, PEF |
| Video     | MP4, MOV, AVI, WebM, MKV, M4V               |
| Audio     | MP3, FLAC, WAV, OGG, M4A, AAC, AIFF         |
| Documents | PDF, SVG                                    |

## 🔬 Extraction Capabilities

### MakerNote Parsing (Premium)

Unlike other tools that show raw hex, we parse manufacturer-specific fields:

| Manufacturer | Fields | Examples                                                        |
| ------------ | ------ | --------------------------------------------------------------- |
| **Canon**    | ~80    | SerialNumber, ShutterCount, LensInfo, AFPoint, InternalTemp     |
| **Nikon**    | ~70    | ShutterCount, AFInfo, VibrationReduction, HighISONoiseReduction |
| **Sony**     | ~60    | InternalSerialNumber, FocusMode, DynamicRangeOptimizer          |
| **Fujifilm** | ~50    | FilmMode, DynamicRange, ShadowTone, HighlightTone               |
| **Apple**    | ~40    | HDRImageType, ContentIdentifier, LivePhotoVideoIndex            |
| **DJI**      | ~30    | FlightYawDegree, GimbalPitchDegree, RelativeAltitude            |

### IPTC Metadata (Premium)

Full IPTC-IIM support including:

- Keywords, Caption, Headline, Credit, Source
- Copyright, By-line, City, Province, Country
- DateCreated, TimeCreated, DigitalCreationDate
- ~50 additional fields

### XMP Namespaces (Premium)

Complete XMP extraction across 20+ namespaces:

- **XMP-dc**: Dublin Core (title, creator, description, rights)
- **XMP-photoshop**: Photoshop metadata (ColorMode, History)
- **XMP-crs**: Camera Raw Settings (all Lightroom adjustments)
- **XMP-lr**: Lightroom specific (hierarchicalSubject, etc.)
- **XMP-iptcCore/Ext**: IPTC Core and Extension
- And many more...

## 🛠 Tech Stack

- **Frontend**: React, TypeScript, Vite, TailwindCSS, shadcn/ui
- **Backend**: Node.js (Express), Python 3.11+
- **Extraction Engine**: Python (ExifTool, Pillow, exifread, mutagen, ffmpeg, pypdf)
- **Database**: PostgreSQL (Drizzle ORM)
- **Payments**: DodoPayments

## 🚀 Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- **ExifTool** (highly recommended for 7000+ fields)
- FFmpeg (for video extraction)

### Installation

```bash
# 1. Clone and install
cd metaextract
npm install
pip install -r requirements.txt

# 2. Install ExifTool (RECOMMENDED)
# macOS:
brew install exiftool

# Ubuntu/Debian:
sudo apt install libimage-exiftool-perl

# 3. Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# 4. Set up environment
cp .env.example .env
# Edit .env with your database URL and Dodo API keys

# 5. Run migrations
npm run db:push

# 6. Start development server
npm run dev
```

### Test the Extraction Engine

```bash
# Test with any image
python server/extractor/metadata_engine.py /path/to/photo.jpg --tier premium

# Check if exiftool is detected
python server/extractor/metadata_engine.py --help
```

## 💰 Pricing Tiers

| Tier        | Price  | File Types                   | Fields | Key Features                 |
| ----------- | ------ | ---------------------------- | ------ | ---------------------------- |
| **Free**    | $0     | Images (JPG, PNG, GIF, WebP) | ~50    | Basic EXIF, 10MB limit       |
| **Starter** | $5/mo  | + RAW, PDF, Audio            | ~200   | GPS, hashes, forensics       |
| **Pro**     | $27/mo | + Video, all formats         | 7000+  | MakerNotes, IPTC, XMP, batch |
| **Super**   | $99/mo | All + API                    | 7000+  | API access, 1GB files        |

## 🔗 API Endpoints

### Extraction

```bash
POST /api/extract?tier=premium
Content-Type: multipart/form-data
Body: file=<binary>

Response: Complete metadata JSON
```

### Configuration

```bash
GET /api/tiers          - All tier configurations
GET /api/fields         - Field information by tier
GET /api/health         - Health check
```

### Credits & Payments

```bash
POST /api/checkout/create-session  - Create subscription
POST /api/credits/purchase         - Buy credit pack
GET /api/credits/balance           - Check balance
```

## 📊 Project Structure

```bash
metaextract/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/            # Page components
│   │   └── lib/              # Utilities
├── server/                    # Node.js backend
│   ├── extractor/            # Python extraction engine
│   │   ├── metadata_engine.py    # Main engine (v3.0)
│   │   └── exiftool_parser.py    # ExifTool integration
│   ├── routes.ts             # API routes
│   ├── payments.ts           # DodoPayments
│   └── storage.ts            # Database ops
├── shared/                    # Shared types
│   ├── schema.ts             # DB schema
│   └── tierConfig.ts         # Tier definitions
├── requirements.txt          # Python deps
└── nixpacks.toml             # Railway config
```

## 🔒 Security & Privacy

- **Zero Storage**: Files processed in memory only
- **Immediate Deletion**: Temp files removed after extraction
- **No Logging**: File contents never logged
- **HTTPS Only**: All traffic encrypted

## 📈 Comparison

| Feature           | MetaExtract | exiftool.org | Jeffrey's Exif | metapicz |
| ----------------- | ----------- | ------------ | -------------- | -------- |
| Fields            | 7000+       | 300+         | 100+           | 50+      |
| MakerNote Parsing | ✅ Parsed   | ✅ Parsed    | ❌ Raw         | ❌ No    |
| IPTC/XMP          | ✅ Full     | ✅ Full      | ⚠️ Basic       | ❌ No    |
| Video             | ✅ Full     | ✅ Full      | ❌ No          | ❌ No    |
| Audio             | ✅ Full     | ⚠️ Basic     | ❌ No          | ❌ No    |
| PDF               | ✅          | ❌           | ❌             | ❌       |
| Beautiful UI      | ✅          | ❌           | ❌             | ✅       |
| File Hashes       | ✅          | ❌           | ❌             | ❌       |
| API Access        | ✅          | ❌           | ❌             | ❌       |
| Zero Storage      | ✅          | ✅           | ✅             | ?        |

## 🚢 Deployment

### Railway (Recommended)

1. Connect GitHub repo to Railway
2. Add environment variables from `.env.example`
3. Deploy!

Railway auto-detects the nixpacks.toml and installs:

- Node.js 20
- Python 3.11
- FFmpeg
- ExifTool
- libmagic

### Manual

```bash
npm run build
npm start
```

## 📄 License

MIT

## 🤝 Support

For issues and feature requests, open a GitHub issue.

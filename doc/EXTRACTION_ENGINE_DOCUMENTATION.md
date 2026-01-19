# MetaExtract Extraction Engine Documentation

**Version:** 4.0.0  
**Date:** January 18, 2026  
**Total Modules:** 585 Python extraction modules  
**Total Fields:** 45,000+ metadata fields across all domains

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [ractor Classes](#mainMain Ext-extractor-classes)
3. [Supported File Formats](#supported-file-formats)
4. [Module Catalog by Domain](#module-catalog-by-domain)
5. [Metadata Fields by Category](#metadata-fields-by-category)
6. [Use Cases](#use-cases)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MetaExtract Engine v4.0                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Unified Extraction Interface                │   │
│  │            (comprehensive_metadata_engine.py)            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│            ┌───────────────┼───────────────┐                   │
│            ▼               ▼               ▼                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │  Image Extractor│ │ Audio Extractor │ │ Video Extractor │  │
│  │ (9,000+ fields) │ │ (3,500+ fields) │ │ (8,000+ fields) │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│            │               │               │                   │
│            ▼               ▼               ▼                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │ Document Extract│ │Scientific Extract│ │ Forensic Extract│  │
│  │ (4,000+ fields) │ │(15,000+ fields) │ │ (2,500+ fields) │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│                            │                                    │
│            ┌───────────────┼───────────────┐                   │
│            ▼               ▼               ▼                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Module Discovery & Dynamic Loading             │   │
│  │              (module_discovery.py - 585 modules)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│            ┌───────────────┼───────────────┐                   │
│            ▼               ▼               ▼                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │  Core Modules   │ │  Format Parsers │ │  Specialized    │  │
│  │   (exif, iptc,  │ │  (jpeg, png,    │ │  (medical,      │  │
│  │   xmp, colors)  │ │   tiff, etc.)   │ │   scientific)   │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component                          | Purpose                                        |
| ---------------------------------- | ---------------------------------------------- |
| `comprehensive_metadata_engine.py` | Main entry point, orchestrates all extraction  |
| `module_discovery.py`              | Dynamic module loading and registration        |
| `core/base_engine.py`              | Base extractor class with common functionality |
| `extractors/`                      | Specialized extractors by file type            |
| `modules/`                         | Individual extraction modules (585 files)      |
| `formats/`                         | Low-level format parsers and header readers    |

---

## Main Extractor Classes

### 1. Image Extractors

| Extractor                | File                          | Fields | Purpose                                 |
| ------------------------ | ----------------------------- | ------ | --------------------------------------- |
| `EnhancedImageExtractor` | `enhanced_image_extractor.py` | 9,000+ | Full image metadata with AI enhancement |
| `RegistryImageExtractor` | `registry_image_extractor.py` | 8,500+ | Registry-based extraction               |
| `UnifiedImageExtractor`  | `unified_image_extractor.py`  | 8,000+ | Unified interface for all image formats |
| `RegistryAwareExtractor` | `registry_aware_extractor.py` | 7,500+ | Aware of image registry system          |
| `BasicImageExtractor`    | `image_extractor.py`          | 5,000+ | Core image extraction                   |

### 2. Document Extractor

| Extractor           | File                    | Fields | Purpose                        |
| ------------------- | ----------------------- | ------ | ------------------------------ |
| `DocumentExtractor` | `document_extractor.py` | 4,000+ | PDF, Office, e-books, web docs |

### 3. Audio Extractor

| Extractor        | File                 | Fields | Purpose                        |
| ---------------- | -------------------- | ------ | ------------------------------ |
| `AudioExtractor` | `audio_extractor.py` | 3,500+ | MP3, WAV, FLAC, AAC, OGG, etc. |

### 4. Video Extractor

| Extractor        | File                 | Fields | Purpose                  |
| ---------------- | -------------------- | ------ | ------------------------ |
| `VideoExtractor` | `video_extractor.py` | 8,000+ | MP4, AVI, MOV, MKV, etc. |

### 5. Scientific Extractor

| Extractor             | File                      | Fields  | Purpose                            |
| --------------------- | ------------------------- | ------- | ---------------------------------- |
| `ScientificExtractor` | `scientific_extractor.py` | 15,000+ | DICOM, FITS, HDF5, NetCDF, GeoTIFF |

---

## Supported File Formats

### Image Formats (100+ formats)

| Category         | Formats                                                     | Extensions                                                                             |
| ---------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Standard**     | JPEG, PNG, GIF, BMP, TIFF, WebP                             | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`                      |
| **RAW Formats**  | Canon CR2/CR3, Nikon NEF, Sony ARW, Fujifilm RAF, Adobe DNG | `.cr2`, `.cr3`, `.nef`, `.arw`, `.raf`, `.dng`, `.orf`, `.rw2`, `.pef`, `.x3f`, `.sr2` |
| **Modern**       | HEIC/HEIF, AVIF, JPEG XL                                    | `.heic`, `.heif`, `.avif`, `.jxl`                                                      |
| **Professional** | PSD, TIFF (large), ProPhoto RGB                             | `.psd`, `.tiff`                                                                        |
| **Scientific**   | DICOM, FITS, HDF5                                           | `.dcm`, `.dicom`, `.fits`, `.fts`, `.h5`                                               |
| **3D/Graphics**  | SVG, OpenEXR, HDR                                           | `.svg`, `.exr`, `.hdr`                                                                 |
| **Camera RAW**   | Phase One, Leaf, Hasselblad                                 | `.iiq`, `.mrw`, `.3fr`                                                                 |

### Audio Formats (50+ formats)

| Category         | Formats                       | Extensions                                      |
| ---------------- | ----------------------------- | ----------------------------------------------- |
| **Common**       | MP3, WAV, FLAC, AAC, M4A, OGG | `.mp3`, `.wav`, `.flac`, `.aac`, `.m4a`, `.ogg` |
| **Lossless**     | AIFF, ALAC, APE, WavPack      | `.aiff`, `.aif`, `.alac`, `.ape`, `.wv`         |
| **Professional** | DSD, DXD, Broadcast WAV       | `.dsf`, `.dff`, `.bwf`                          |
| **Streaming**    | Opus, WMA, RA                 | `.opus`, `.wma`, `.ra`                          |
| **MIDI**         | MIDI, Standard MIDI           | `.mid`, `.midi`                                 |

### Video Formats (60+ formats)

| Category         | Formats                  | Extensions                              |
| ---------------- | ------------------------ | --------------------------------------- |
| **Common**       | MP4, AVI, MOV, MKV, WebM | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` |
| **Professional** | ProRes, DNxHD, CineForm  | `.mov`, `.mxf`, `.r3d`                  |
| **Broadcast**    | MPEG-TS, MPEG-PS, VOB    | `.ts`, `.mpeg`, `.vob`, `.m2ts`         |
| **Legacy**       | WMV, FLV, RM, DivX       | `.wmv`, `.flv`, `.rm`, `.divx`          |
| **360/VR**       | 360° video, VR180        | `.mp4` (360)                            |

### Document Formats (80+ formats)

| Category             | Formats                 | Extensions                                           |
| -------------------- | ----------------------- | ---------------------------------------------------- |
| **PDF**              | PDF, PDF/A, PDF/X       | `.pdf`, `.pdfa`, `.pdfx`                             |
| **Microsoft Office** | Word, Excel, PowerPoint | `.docx`, `.docm`, `.xlsx`, `.xlsm`, `.pptx`, `.pptm` |
| **OpenDocument**     | ODT, ODS, ODP           | `.odt`, `.ods`, `.odp`                               |
| **E-books**          | EPUB, MOBI, AZW, FB2    | `.epub`, `.mobi`, `.azw`, `.fb2`                     |
| **Web**              | HTML, HTM               | `.html`, `.htm`                                      |

### Scientific Formats (40+ formats)

| Category            | Formats                 | Extensions                              |
| ------------------- | ----------------------- | --------------------------------------- |
| **Medical Imaging** | DICOM, NIfTI, Analyze   | `.dcm`, `.dicom`, `.nii`, `.img`        |
| **Astronomy**       | FITS, IRAF              | `.fits`, `.fit`, `.fts`                 |
| **Scientific Data** | HDF5, NetCDF, GRIB      | `.h5`, `.hdf5`, `.nc`, `.nc4`, `.grib`  |
| **Geospatial**      | GeoTIFF, Shapefile, KML | `.tif`, `.tiff`, `.shp`, `.kml`, `.kmz` |
| **Microscopy**      | OME-TIFF, Bio-Formats   | `.ome.tiff`                             |

### Forensic/Blockchain Formats (20+ formats)

| Category               | Formats                        | Extensions             |
| ---------------------- | ------------------------------ | ---------------------- |
| **Blockchain**         | NFT metadata, Ethereum, Solana | `.json` (metadata)     |
| **Digital Signatures** | PGP, S/MIME                    | `.sig`, `.p7s`         |
| **Evidence**           | Raw disk images, E01, AFF      | `.img`, `.e01`, `.aff` |

---

## Module Catalog by Domain

### Core Metadata Modules (50 modules)

| Module                        | Fields | Description                     |
| ----------------------------- | ------ | ------------------------------- |
| `exif.py`                     | 450+   | EXIF/EXIF2 metadata extraction  |
| `iptc_xmp.py`                 | 380+   | IPTC and XMP metadata           |
| `xmp_extended.py`             | 200+   | Extended XMP namespaces         |
| `images.py`                   | 150+   | Image properties and dimensions |
| `colors.py`                   | 180+   | Color profiles and palettes     |
| `icc_profile.py`              | 120+   | ICC color profile extraction    |
| `icc_profile_parser.py`       | 100+   | Deep ICC profile parsing        |
| `geocoding.py`                | 250+   | GPS and geocoding data          |
| `geocoding_cached.py`         | 200+   | Cached reverse geocoding        |
| `quality.py`                  | 150+   | Image quality metrics           |
| `quality_metrics.py`          | 180+   | Advanced quality analysis       |
| `time_based.py`               | 200+   | Temporal metadata               |
| `temporal_astronomical.py`    | 150+   | Astronomical time calculations  |
| `hashes.py`                   | 80+    | File hashes (MD5, SHA, phash)   |
| `perceptual_hashes.py`        | 60+    | Perceptual hashing for matching |
| `perceptual_hashes_cached.py` | 50+    | Cached phash calculations       |
| `filesystem.py`               | 100+   | Filesystem metadata             |

### Camera/Makernotes Modules (30 modules)

| Module                          | Fields | Description                                                            |
| ------------------------------- | ------ | ---------------------------------------------------------------------- |
| `camera_makernotes_basic.py`    | 200+   | Basic maker notes                                                      |
| `camera_makernotes_advanced.py` | 350+   | Advanced maker notes                                                   |
| `camera_makernotes_ext_*.py`    | 150+   | Extended maker notes (10 files)                                        |
| `camera_makernotes_pro.py`      | 400+   | Professional camera maker notes                                        |
| `camera_makernotes_raw.py`      | 300+   | RAW format maker notes                                                 |
| `camera_makernotes_ultra.py`    | 500+   | Ultra-detailed maker notes                                             |
| `makernotes_*.py`               | 200+   | Vendor-specific (Canon, Nikon, Sony, Fuji, Olympus, Panasonic, Pentax) |
| `makernotes_dji.py`             | 180+   | DJI drone maker notes                                                  |
| `makernotes_hasselblad.py`      | 150+   | Hasselblad maker notes                                                 |
| `makernotes_leica.py`           | 150+   | Leica maker notes                                                      |
| `makernotes_phase_one.py`       | 150+   | Phase One maker notes                                                  |
| `vendor_makernotes.py`          | 100+   | Generic vendor data                                                    |

### Audio Modules (25 modules)

| Module                           | Fields | Description               |
| -------------------------------- | ------ | ------------------------- |
| `audio.py`                       | 200+   | Basic audio metadata      |
| `audio_basic.py`                 | 150+   | Basic audio properties    |
| `audio_advanced.py`              | 250+   | Advanced audio metadata   |
| `audio_metadata_advanced.py`     | 200+   | Advanced ID3/metadata     |
| `audio_id3_advanced.py`          | 180+   | Advanced ID3 tags         |
| `audio_id3_complete_registry.py` | 300+   | Complete ID3 registry     |
| `audio_id3_extended.py`          | 150+   | Extended ID3 frames       |
| `audio_codec_details.py`         | 120+   | Audio codec details       |
| `audio_pro.py`                   | 200+   | Professional audio        |
| `audio_master.py`                | 250+   | Master audio files        |
| `audio_hi_res.py`                | 180+   | High-resolution audio     |
| `audio_ultimate_advanced.py`     | 300+   | Ultimate audio extraction |
| `audio_advanced_id3.py`          | 200+   | Advanced ID3 v2.4         |
| `audio_advanced_id3.py`          | 200+   | Advanced ID3 v2.4         |
| `audio_bwf_registry.py`          | 150+   | Broadcast WAV registry    |
| `audio_bitstream_parser.py`      | 100+   | Bitstream analysis        |
| `wav_riff_extractor.py`          | 120+   | WAV/RIFF extraction       |
| `aiff_extractor.py`              | 100+   | AIFF extraction           |
| `apev2_extractor.py`             | 80+    | APEv2 extraction          |
| `opus_extractor.py`              | 80+    | Opus extraction           |

### Video Modules (35 modules)

| Module                                    | Fields | Description                |
| ----------------------------------------- | ------ | -------------------------- |
| `video.py`                                | 200+   | Basic video metadata       |
| `video_basic.py`                          | 150+   | Basic video properties     |
| `video_advanced.py`                       | 250+   | Advanced video metadata    |
| `video_pro.py`                            | 300+   | Professional video         |
| `video_professional.py`                   | 350+   | Professional video formats |
| `video_professional_advanced.py`          | 400+   | Advanced pro video         |
| `video_professional_ultimate_advanced.py` | 500+   | Ultimate pro video         |
| `video_codec_advanced.py`                 | 200+   | Video codec details        |
| `video_codec_analysis.py`                 | 250+   | Codec analysis             |
| `video_codec_details.py`                  | 180+   | Detailed codec info        |
| `video_broadcast.py`                      | 200+   | Broadcast standards        |
| `video_cinema.py`                         | 150+   | Cinema formats             |
| `video_360.py`                            | 120+   | 360° video                 |
| `video_vr.py`                             | 100+   | VR video                   |
| `video_telemetry.py`                      | 150+   | Video telemetry            |
| `video_keyframes.py`                      | 100+   | Keyframe extraction        |
| `container_metadata.py`                   | 180+   | Container format metadata  |
| `container_deep_parser.py`                | 250+   | Deep container parsing     |
| `mp4_atoms_extractor.py`                  | 150+   | MP4 atom extraction        |

### Scientific/Medical Modules (60 modules)

| Module                           | Fields | Description                |
| -------------------------------- | ------ | -------------------------- |
| `dicom_extractor.py`             | 4,600+ | DICOM medical imaging      |
| `dicom_medical.py`               | 3,500+ | Medical DICOM              |
| `dicom_advanced.py`              | 4,000+ | Advanced DICOM             |
| `dicom_complete_registry.py`     | 4,500+ | Complete DICOM registry    |
| `dicom_complete_ultimate.py`     | 4,600+ | Ultimate DICOM             |
| `dicom_private_tags_complete.py` | 500+   | Private DICOM tags         |
| `dicom_vendor_tags.py`           | 300+   | Vendor-specific DICOM      |
| `fits_extractor.py`              | 3,000+ | FITS astronomy             |
| `fits_astronomical_imaging.py`   | 2,500+ | Astronomical FITS          |
| `fits_astronomy_registry.py`     | 2,800+ | FITS astronomy registry    |
| `fits_complete.py`               | 3,000+ | Complete FITS              |
| `hdf5_scientific_data.py`        | 2,000+ | HDF5 scientific data       |
| `geospatial_extractor.py`        | 1,500+ | Geospatial data            |
| `geospatial_gis.py`              | 1,800+ | GIS metadata               |
| `microscopy_imaging.py`          | 1,200+ | Microscopy data            |
| `microscopy_ome_registry.py`     | 1,000+ | OME-TIFF registry          |
| `genomic_extractor.py`           | 1,500+ | Genomic data               |
| `scientific_*.py`                | 500+   | Various scientific formats |

### Forensic/Security Modules (40 modules)

| Module                            | Fields | Description                |
| --------------------------------- | ------ | -------------------------- |
| `forensic_basic.py`               | 200+   | Basic forensic metadata    |
| `forensic_advanced.py`            | 350+   | Advanced forensics         |
| `forensic_complete.py`            | 500+   | Complete forensics         |
| `forensic_master.py`              | 600+   | Master forensic            |
| `forensic_pro.py`                 | 700+   | Professional forensics     |
| `forensic_extractor.py`           | 400+   | Forensic extraction        |
| `forensic_metadata.py`            | 300+   | Forensic metadata          |
| `forensic_analysis_integrator.py` | 400+   | Analysis integration       |
| `forensic_digital_advanced.py`    | 450+   | Advanced digital forensics |
| `forensic_enterprise.py`          | 600+   | Enterprise forensics       |
| `image_forensics.py`              | 300+   | Image forensics            |
| `manipulation_detection.py`       | 200+   | Manipulation detection     |
| `error_level_analysis.py`         | 150+   | ELA analysis               |
| `steganography.py`                | 100+   | Steganography detection    |
| `security_audit.py`               | 150+   | Security auditing          |
| `security_compliance.py`          | 200+   | Compliance checking        |
| `security_investigation.py`       | 250+   | Investigation tools        |
| `security_monitoring.py`          | 180+   | Security monitoring        |

### Document Modules (25 modules)

| Module                          | Fields | Description               |
| ------------------------------- | ------ | ------------------------- |
| `document_extractor.py`         | 500+   | Basic document extraction |
| `document_master.py`            | 600+   | Master document           |
| `document_metadata_ultimate.py` | 800+   | Ultimate document         |
| `pdf_metadata_complete.py`      | 400+   | Complete PDF              |
| `pdf_forensics.py`              | 300+   | PDF forensics             |
| `pdf_office_*.py`               | 300+   | PDF/Office integration    |
| `office_documents.py`           | 350+   | Office documents          |
| `office_documents_complete.py`  | 400+   | Complete Office           |
| `web_metadata.py`               | 200+   | Web document metadata     |
| `email_metadata.py`             | 150+   | Email metadata            |

### AI/ML Modules (15 modules)

| Module                       | Fields | Description                    |
| ---------------------------- | ------ | ------------------------------ |
| `ai_generation_detector.py`  | 50+    | AI-generated content detection |
| `ai_culling_engine.py`       | 100+   | AI-powered culling             |
| `ai_ml_metadata.py`          | 80+    | ML model metadata              |
| `ai_ml_metadata_registry.py` | 100+   | ML metadata registry           |
| `ai_vision_extractor.py`     | 150+   | Computer vision metadata       |
| `neural_network_metadata.py` | 100+   | Neural network metadata        |
| `ml_extractor.py`            | 80+    | ML model extraction            |

### Blockchain/Crypto Modules (10 modules)

| Module                               | Fields | Description               |
| ------------------------------------ | ------ | ------------------------- |
| `blockchain_nft_metadata.py`         | 80+    | NFT metadata              |
| `blockchain_asset_registry.py`       | 100+   | Blockchain asset registry |
| `blockchain_extended_registry.py`    | 120+   | Extended blockchain       |
| `blockchain_provenance_extractor.py` | 100+   | Provenance extraction     |

### Social/Mobile/Web Modules (20 modules)

| Module                     | Fields | Description            |
| -------------------------- | ------ | ---------------------- |
| `social_media_metadata.py` | 150+   | Social media metadata  |
| `web_metadata.py`          | 200+   | Web document metadata  |
| `mobile_metadata.py`       | 180+   | Mobile device metadata |
| `wearables.py`             | 100+   | Wearable device data   |
| `iot_metadata.py`          | 120+   | IoT device metadata    |

---

## Metadata Fields by Category

### Image Metadata Fields (15,000+ total)

| Category             | Fields | Examples                                                   |
| -------------------- | ------ | ---------------------------------------------------------- |
| **EXIF Standard**    | 450+   | Make, Model, DateTime, Exposure, FNumber, ISO, FocalLength |
| **EXIF GPS**         | 50+    | GPSLatitude, GPSLongitude, GPSAltitude, GPSSpeed           |
| **MakerNotes**       | 2,000+ | Camera-specific settings, lens info, focus points          |
| **IPTC**             | 300+   | Caption, Creator, Copyright, Keywords, Scene               |
| **XMP**              | 500+   | Dublin Core, Photoshop, Camera RAW, AI tags                |
| **ICC Profile**      | 120+   | Color space, primaries, tone curve                         |
| **Image Properties** | 150+   | Dimensions, bit depth, color type, compression             |
| **Color Analysis**   | 180+   | Histogram, dominant colors, palette                        |
| **Quality Metrics**  | 150+   | Sharpness, noise, blur detection                           |
| **Perceptual Hash**  | 60+    | pHash, dHash, wHash values                                 |
| **Geocoding**        | 250+   | Address, city, country from GPS                            |
| **Temporal**         | 200+   | Sunrise, sunset, golden hour, moon phase                   |

### Video Metadata Fields (8,000+ total)

| Category                | Fields | Examples                               |
| ----------------------- | ------ | -------------------------------------- |
| **Container Format**    | 150+   | Format, duration, bitrate, streams     |
| **Video Stream**        | 500+   | Codec, resolution, frame rate, bitrate |
| **Audio Stream**        | 300+   | Codec, sample rate, channels, bitrate  |
| **Codec Details**       | 400+   | H.264 profile/level, HEVC tier         |
| **HDR Metadata**        | 100+   | HDR10, Dolby Vision, color primaries   |
| **Chapters**            | 100+   | Chapter markers, timestamps            |
| **Timecode**            | 50+    | SMTPE timecode, drop frame             |
| **Broadcast Standards** | 200+   | ATSC, DVB, ISDB compliance             |
| **Drone Telemetry**     | 150+   | GPS, altitude, speed, gimbal angle     |
| **360/VR**              | 120+   | Projection type, stereo format         |

### Audio Metadata Fields (3,500+ total)

| Category               | Fields | Examples                           |
| ---------------------- | ------ | ---------------------------------- |
| **ID3v1**              | 10+    | Title, Artist, Album, Year, Genre  |
| **ID3v2.3/2.4**        | 300+   | All ID3v2 frames, APIC, TXXX       |
| **Vorbis Comment**     | 150+   | Album, track, genre, replay gain   |
| **Codec Info**         | 200+   | Encoder, bitrate, sample rate      |
| **Broadcast WAV**      | 100+   | BWF metadata, timecode             |
| **Professional Audio** | 300+   | Cue markers, MIDI data, mixer info |
| **Master Audio**       | 250+   | DSD metadata, DXD format           |

### Document Metadata Fields (4,000+ total)

| Category              | Fields | Examples                                       |
| --------------------- | ------ | ---------------------------------------------- |
| **PDF Properties**    | 200+   | Title, Author, Creator, Producer, CreationDate |
| **PDF Pages**         | 100+   | Page count, page dimensions, rotation          |
| **PDF Security**      | 50+    | Encryption, permissions, passwords             |
| **Office Core**       | 200+   | Application, Company, Created, Modified        |
| **Office Statistics** | 150+   | Word/character count, revision number          |
| **XMP in Docs**       | 300+   | Dublin Core, XMP rights, custom tags           |

### Scientific/Medical Fields (15,000+ total)

| Category          | Fields | Examples                                          |
| ----------------- | ------ | ------------------------------------------------- |
| **DICOM Patient** | 100+   | PatientName, PatientID, BirthDate, Sex            |
| **DICOM Study**   | 150+   | StudyInstanceUID, StudyDate, ReferringPhysician   |
| **DICOM Series**  | 200+   | SeriesInstanceUID, Modality, BodyPartExamined     |
| **DICOM Image**   | 500+   | Rows, Columns, BitsAllocated, PixelRepresentation |
| **DICOM Private** | 1,000+ | Vendor-specific tags                              |
| **FITS Header**   | 300+   | SIMPLE, BITPIX, NAXIS, BSCALE, BZERO              |
| **FITS WCS**      | 200+   | CRPIX, CDELT, CRVAL, CTYPE (world coords)         |
| **HDF5**          | 1,500+ | Dataset structure, attributes, types              |
| **NetCDF**        | 500+   | Dimensions, variables, attributes                 |
| **GeoTIFF**       | 300+   | ModelTiepoint, ModelPixelScale, RPC               |

### Forensic Fields (2,500+ total)

| Category                   | Fields | Examples                              |
| -------------------------- | ------ | ------------------------------------- |
| **File System**            | 100+   | Permissions, timestamps, ACLs         |
| **Hash Values**            | 80+    | MD5, SHA-1, SHA-256, SSDEEP           |
| **Image Analysis**         | 200+   | Error Level Analysis, clone detection |
| **Manipulation Detection** | 150+   | JPEG artifacts, histogram anomalies   |
| **Steganography**          | 100+   | LSB indicators, hidden data detection |
| **Digital Signatures**     | 150+   | Signature validity, certificate info  |
| **Chain of Custody**       | 200+   | Audit trail, hash verification        |

---

## Use Cases

### 1. Digital Forensics & E-Discovery

**Relevant Modules:**

- `forensic_complete.py`, `forensic_master.py`, `image_forensics.py`
- `error_level_analysis.py`, `steganography.py`
- `security_investigation.py`, `pdf_forensics.py`

**Extracted Data:**

- File origin and manipulation history
- Embedded metadata for timeline reconstruction
- Hidden/steganographic content detection
- Digital signature verification
- Hash verification for evidence integrity

**Use Case Example:**

```
Law enforcement receives suspect's camera memory card. Use MetaExtract to:
1. Extract all camera settings, GPS coordinates, timestamps
2. Detect any image manipulation or editing
3. Find hidden/steganographic content
4. Build a timeline of photo capture
5. Verify file integrity with cryptographic hashes
```

### 2. Medical Imaging & Healthcare

**Relevant Modules:**

- `dicom_complete_ultimate.py`, `dicom_medical.py`
- `microscopy_imaging.py`, `genomic_extractor.py`
- `medical_*.py` (60+ modules)

**Extracted Data:**

- Patient demographics (de-identified for HIPAA)
- Imaging modality and parameters
- Anatomical region and study type
- DICOM tags for PACS integration
- Laboratory and pathology data

**Use Case Example:**

```
Hospital radiology department receives CT scan. Use MetaExtract to:
1. Extract patient info (properly de-identified)
2. Get imaging parameters for quality control
3. Verify DICOM conformance
4. Extract measurement data
5. Export metadata for research database
```

### 3. Stock Photography & Digital Asset Management

**Relevant Modules:**

- `exif.py`, `iptc_xmp.py`, `camera_makernotes_*.py`
- `geocoding.py`, `social_media_metadata.py`
- `workflow_dam.py`, `image_format_registry.py`

**Extracted Data:**

- Complete technical camera settings
- Photographer credits and copyright
- GPS location for map display
- Keyword/tags for searchability
- Usage rights and licensing info

**Use Case Example:**

```
Stock photo agency processes 10,000 images. Use MetaExtract to:
1. Extract all EXIF/IPTC/XMP metadata
2. Flag images missing required fields
3. Auto-generate keyword suggestions
4. Extract GPS for geotagging
5. Build searchable metadata database
```

### 4. AI/ML Content Detection

**Relevant Modules:**

- `ai_generation_detector.py`
- `image_forensics.py`, `manipulation_detection.py`
- `neural_network_metadata.py`

**Extracted Data:**

- AI generation probability scores
- GAN/fingerprint signatures
- Manipulation detection results
- Model metadata from AI-generated content

**Use Case Example:**

```
Social media platform needs to identify AI-generated images. Use MetaExtract to:
1. Run AI generation detection
2. Check for manipulation artifacts
3. Extract C2PA manifest if present
4. Flag synthetic content for labeling
5. Track AI content trends
```

### 5. Drone/UAV Photography

**Relevant Modules:**

- `drone_metadata.py`, `makernotes_dji.py`
- `video_telemetry.py`, `gps_coordinates.py`
- `temporal_astronomical.py`

**Extracted Data:**

- Flight telemetry (altitude, speed, heading)
- Gimbal and camera settings
- GPS track and waypoints
- Environmental conditions
- No-fly zone detection

**Use Case Example:**

```
Drone operator processes aerial survey. Use MetaExtract to:
1. Extract flight path from telemetry
2. Verify GPS accuracy
3. Extract camera settings per image
4. Calculate golden hour timing
5. Verify no-fly zone compliance
```

### 6. Astronomy & Scientific Research

**Relevant Modules:**

- `fits_extractor.py`, `fits_astronomical_imaging.py`
- `scientific_dicom_fits_*.py`, `geospatial_gis.py`
- `hdf5_scientific_data.py`, `netcdf_metadata.py`

**Extracted Data:**

- FITS headers and WCS coordinates
- Telescope and observation details
- Instrument calibration data
- Climate/environmental measurements
- Dataset structure and variables

**Use Case Example:**

```
Astronomer processes telescope data. Use MetaExtract to:
1. Extract FITS headers with world coordinates
2. Get observation parameters
3. Convert WCS to sky coordinates
4. Extract calibration metadata
5. Export for research database
```

### 7. Legal Compliance & Privacy

**Relevant Modules:**

- `accessibility_metadata.py`, `medical_privacy.py`
- `security_compliance.py`, `legal_compliance_*.py`
- `redaction_detection.py`, `pii_detection.py`

**Extracted Data:**

- PII locations and redaction status
- Accessibility compliance status
- Document retention metadata
- Privacy regulation compliance

**Use Case Example:**

```
Legal team reviews documents for PII. Use MetaExtract to:
1. Scan all documents for PII
2. Flag documents needing redaction
3. Verify accessibility compliance
4. Check retention policy adherence
5. Generate compliance report
```

### 8. Blockchain/NFT Provenance

**Relevant Modules:**

- `blockchain_nft_metadata.py`
- `blockchain_provenance_extractor.py`
- `blockchain_asset_registry.py`
- `c2pa_adobe_cc.py`, `c2pa_manifest_registry.py`

**Extracted Data:**

- NFT contract and token metadata
- Ownership history and provenance
- C2PA content authenticity manifest
- Blockchain transaction data

**Use Case Example:**

```
NFT marketplace verifies asset authenticity. Use MetaExtract to:
1. Extract on-chain metadata
2. Verify content matches hash
3. Extract C2PA authenticity chain
4. Trace provenance history
5. Flag counterfeit assets
```

---

## Field Count Summary

| Domain                 | Modules | Approximate Fields |
| ---------------------- | ------- | ------------------ |
| **Images**             | 120+    | 15,000+            |
| **Video**              | 45+     | 8,000+             |
| **Audio**              | 30+     | 3,500+             |
| **Documents**          | 30+     | 4,000+             |
| **Scientific/Medical** | 70+     | 15,000+            |
| **Forensic/Security**  | 50+     | 2,500+             |
| **AI/ML**              | 15+     | 500+               |
| **Blockchain**         | 10+     | 400+               |
| **Social/Mobile**      | 25+     | 1,000+             |
| **Other**              | 50+     | 1,500+             |
| **TOTAL**              | **585** | **45,000+**        |

---

## Adding New Modules

The extraction engine uses dynamic module discovery. To add a new extraction module:

1. Create a Python file in `/server/extractor/modules/`
2. Implement extraction functions starting with `extract_`, `detect_`, or `analyze_`
3. Functions should accept `filepath` as first parameter
4. Return a dictionary of extracted metadata
5. Optionally define `MODULE_DEPENDENCIES` list
6. Module is automatically discovered and registered

Example:

```python
# server/extractor/modules/example_module.py

def extract_example_metadata(filepath: str) -> dict:
    """Extract example-specific metadata."""
    # Your extraction logic here
    return {
        "example_field": value,
        "another_field": value2
    }

def get_example_field_count() -> int:
    """Return the number of fields this module extracts."""
    return 2
```

---

## Performance Notes

- **Dynamic Loading:** 585 modules are loaded on-demand
- **Caching:** Results cached for identical files
- **Parallel Processing:** Extraction can run in parallel for batches
- **Memory Management:** Streaming available for large files
- **Registry System:** Reduces redundant extraction for similar files

---

_Generated: January 18, 2026_  
_MetaExtract v4.0.0_

# Sample Files for MetaExtract Demo

This directory contains sample files for demonstrating MetaExtract capabilities.

## Files Included

### Images
- `sample_photo.jpg` - Standard JPEG with EXIF data
- `sample_raw.cr2` - Canon RAW file with MakerNotes
- `sample_gps.jpg` - Photo with GPS coordinates
- `sample_edited.jpg` - Photo with editing history

### Video
- `sample_video.mp4` - Video with metadata
- `sample_hdr.mov` - HDR video sample

### Audio
- `sample_audio.mp3` - MP3 with ID3 tags
- `sample_lossless.flac` - FLAC with metadata

### Documents
- `sample_document.pdf` - PDF with metadata
- `sample_vector.svg` - SVG with embedded data

## Usage

These files are automatically served by the `/api/samples` endpoint and can be used for:

1. User onboarding and tutorials
2. Feature demonstrations
3. Testing different metadata extraction capabilities
4. Showcasing tier differences

## Metadata Highlights

Each file is carefully selected to demonstrate specific metadata extraction capabilities:

- **EXIF Data**: Camera settings, timestamps, software info
- **GPS Coordinates**: Location data with mapping links
- **MakerNotes**: Vendor-specific camera data
- **File Integrity**: Hash verification
- **Editing History**: Modification detection
- **Format-Specific**: Video codecs, audio tags, PDF properties
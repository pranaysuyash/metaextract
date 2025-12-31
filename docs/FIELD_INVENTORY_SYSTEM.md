# MetaExtract Field Inventory System

## Overview

This system generates _actual_ metadata field inventories from multiple sources, mapped to the 45K+ "Ultimate Metadata Universe" taxonomy.

**Current Status (2025-12-30):**

- **Total fields:** 26,466 tags across 44 categories
- **Unique field names:** 25,527
- **45K+ Taxonomy coverage:** 94.1% (22,169/23,550 mapped)

## Tools

### 1. `generate_field_inventory.py` - Main Inventory Generator

Generates field inventories from multiple sources:

**Sources:**

- **ExifTool** (groups: EXIF, IPTC, XMP, MakerNotes, QuickTime, Matroska, RIFF, PDF, ICC_Profile, FLAC, Vorbis, APE, AAC, ASF, MXF, M2TS)
- **ffprobe** (format/stream fields)
- **pydicom** (DICOM dictionary, 5179 tags)
- **ID3** (static frame registry, 109 fields)

**Features:**

- ExifTool group discovery (`exiftool -listg`)
- ExifTool XML streaming parser (`-listx` to avoid memory issues)
- Multi-source inventory in single run
- Supports specific group selection (`--include-groups`)
- Supports all MakerNotes vendors (`--makernotes`)

**Usage:**

```bash
# Full comprehensive inventory (recommended)
python3 scripts/generate_field_inventory.py \
    --out-dir dist/field_inventory_comprehensive \
    --exif --iptc --xmp --makernotes \
    --ffprobe --pydicom --id3 \
    --include-groups QuickTime Matroska RIFF ASF MXF \
    --timeout-s 900

# Discover and inventory ALL ExifTool groups (slow!)
python3 scripts/generate_field_inventory.py \
    --out-dir dist/exiftool_all \
    --discover-all-groups \
    --timeout-s 1800

# Specific groups only
python3 scripts/generate_field_inventory.py \
    --out-dir dist/quicktime_only \
    --include-groups QuickTime
```

**Outputs:**

- `field_inventory_<source>.json` - Full inventory with tables + tags
- `field_inventory_summary.json` - Counts + rollups by category

### 2. `map_taxonomy.py` - Taxonomy Mapper

Maps generated inventory to the legacy 45K 'Ultimate Metadata Universe' taxonomy (for compatibility).

**Features:**

- Categorizes inventory into 7 major domains
- Calculates coverage percentages per domain
- Identifies gaps for future work
- Generates human-readable report

**Usage:**

```bash
python3 scripts/map_taxonomy.py
```

**Outputs:**

- `taxonomy_mapping.json` - Structured mapping
- `TAXONOMY_REPORT.md` - Human-readable summary

### 3. `inventory_status.py` - Status & Summary

Shows comprehensive inventory status, coverage by domain, and next steps.

**Usage:**

```bash
python3 scripts/inventory_status.py
```

### 4. `query_inventory.py` - Query Tool

Search and query the comprehensive inventory.

**Commands:**

```bash
# Search for fields (case-sensitive)
python3 scripts/query_inventory.py search "GPSLatitude"

# Case-insensitive search
python3 scripts/query_inventory.py search "gps" -i

# List all categories
python3 scripts/query_inventory.py categories

# List categories with counts
python3 scripts/query_inventory.py categories -c

# Count total fields
python3 scripts/query_inventory.py count

# List tables for specific category
python3 scripts/query_inventory.py tables "MakerNotes:Canon"

# Limit results
python3 scripts/query_inventory.py tables "MakerNotes:Canon" -n 10
```

## Coverage Breakdown

### Image Metadata (Target: 12,550 | Mapped: 12,798 | 102.0%)

| Subdomain        | Target | Mapped | Coverage |
| ---------------- | ------ | ------ | -------- |
| EXIF Standard    | 1,200  | 784    | 65.3%    |
| MakerNotes       | 7,000  | 7,430  | 106.1%   |
| IPTC Standards   | 150    | 117    | 78.0%    |
| XMP Standards    | 500    | 4,250  | 850.0%   |
| Color Management | 200    | 197    | 98.5%    |

**Top MakerNotes Vendors:**

1. Canon - 1,788 tags (98 tables)
2. Nikon - 1,416 tags (120 tables)
3. Sony - 1,251 tags (65 tables)
4. Pentax - 570 tags (47 tables)
5. Olympus - 447 tags (26 tables)
   ... and 19 more

### Video Metadata (Target: 2,000 | Mapped: 3,755 | 187.8%)

| Container | Tags  | Tables |
| --------- | ----- | ------ |
| MXF       | 1,584 | 2      |
| QuickTime | 1,438 | 99     |
| Matroska  | 274   | 3      |
| ASF       | 219   | 10     |
| RIFF      | 198   | 23     |
| M2TS      | 7     | 2      |

### Audio Metadata (Target: 3,500 | Mapped: 457 | 13.1%)

| Format       | Tags | Tables |
| ------------ | ---- | ------ |
| ID3 (static) | 109  | 3      |
| FLAC         | 22   | 3      |
| Vorbis       | 37   | 2      |
| APE          | 22   | 3      |
| AAC          | 4    | 1      |

### Scientific/Medical (Target: 11,000 | Mapped: 5,179 | 47.1%)

| Source                                          | Tags  | Tables |
| ----------------------------------------------- | ----- | ------ |
| pydicom (DicomDictionary + RepeatersDictionary) | 5,179 | 2      |

### Gaps (Unmapped Domains)

**Priority gaps (next 3 steps):**

1. FITS astronomical keywords (requires `pip install astropy`)
2. GeoTIFF fields
3. File System & OS metadata

**Other gaps:**

- Digital signatures & authentication
- Network/communication headers
- Device & hardware fingerprints
- Social media metadata (requires API integration)
- Mobile device metadata
- Web standards (Open Graph, Twitter Cards, Schema.org)

## Architecture

### Data Model

Field records in the inventory follow this structure:

```json
{
  "name": "TagName",
  "id": "0x0010",
  "desc": "Optional description (from ExifTool)"
}
```

Categories contain tables, each containing tag lists:

```json
{
  "EXIF": {
    "selectors": ["-EXIF:All"],
    "tags_seen": 784,
    "tables": {
      "Exif::Main": {
        "table": {"name": "Exif::Main", "g0": "EXIF", "g1": "Main"},
        "tags": [...]
      }
    }
  }
}
```

### Taxonomy Mapping

Inventory categories map to 45K+ domains:

- **IMAGE_METADATA** → EXIF, MakerNotes, IPTC, XMP, Color Management
- **VIDEO_METADATA** → Container Formats (QuickTime, Matroska, MXF, etc.)
- **AUDIO_METADATA** → ID3, Other Formats (FLAC, Vorbis, APE, AAC)
- **SCIENTIFIC_MEDICAL** → DICOM
- **FORENSIC_SECURITY** → File System & OS (future)
- **SOCIAL_MOBILE_WEB** → Web Standards (future)

## Integration with MetaExtract

The inventory system provides _ground truth_ field names for building extraction modules:

1. **Generator runs** → JSON outputs in `dist/field_inventory_comprehensive/`
2. **Extraction modules** → Reference inventory to add missing fields
3. **Field count tracking** → `field_count.py` compares inventory totals to implementation

### Example: Adding a new EXIF field

1. Query inventory:

   ```bash
   python3 scripts/query_inventory.py search "GPSDateStamp"
   ```

2. Add to extraction module (`server/extractor/modules/exif.py`):

   ```python
   EXIF_TAGS = {
       "GPSDateStamp": "gps_date_stamp",  # Found in inventory
       # ... existing tags
   }
   ```

3. Update field count:
   ```python
   def get_exif_field_count() -> int:
       # Query inventory to get current count
       return 785  # Incremented
   ```

## File Sizes

| File                                 | Size   |
| ------------------------------------ | ------ |
| `field_inventory_comprehensive.json` | 3.7 MB |
| `field_inventory_summary.json`       | 32 KB  |
| `taxonomy_mapping.json`              | 5.2 KB |
| `TAXONOMY_REPORT.md`                 | 2.4 KB |

## Next Steps

1. **Fill priority gaps:**

   - Install `astropy` and run FITS inventory
   - Add GeoTIFF group to inventory
   - Implement file system metadata extraction

2. **UI Development:**

   - Build three-pane explorer interface
   - Use inventory for progressive disclosure (show only relevant fields)
   - Add global search over extracted fields

3. **API Development:**
   - Expose inventory via REST API
   - Allow clients to query available fields per file type
   - Provide drill-down endpoints

## References

- **ExifTool:** https://exiftool.org/
- **ExifTool Tag Names:** https://exiftool.org/TagNames/index.html
- **DICOM Standard:** https://www.dicomstandard.org/
- **ID3v2.4 Frame Identifier:** https://id3.org/
- **FFmpeg:** https://ffmpeg.org/documentation.html

You reduce fear by doing two things: (1) control cognitive load, (2) control interpretation. Right now you’re dumping a forensic toolbox onto everyone. That reads as “I’m about to accuse your file of crimes” or “I’m leaking your secrets”.

A good mental model: Progressive disclosure + guided narrative. Show a small, accurate story first. Let power users dig.

What causes “fear” in this UI 1. Volume without prioritization: hundreds of fields implies “there’s something bad here”. 2. Jargon: MakerNotes, IPTC, XMP looks like hacking. 3. Ambiguous flags: “Not Found”, “Integrity”, “Forensic” triggers paranoia. 4. Locked blocks: feels like “we found something juicy but won’t tell you”. 5. No “what this means” layer: users can’t distinguish harmless metadata from risky metadata.

The presentation strategy

1. Start with a calm “Highlights” summary

Top of results should be a single card with:
• 3–7 bullet findings, plain language.
• Each item labeled with Impact: Privacy, Authenticity, Workflow, None.
• Each item labeled with Confidence: High/Med/Low.
• Always include one “limitations” line: “Metadata can be missing/stripped. Absence isn’t proof.”

Examples:
• “Location data: not present.” (Impact: Privacy, Confidence: High)
• “Edited by: Adobe Lightroom.” (Impact: Authenticity, Confidence: High)
• “Capture date: 2023-11-02 14:12.” (Impact: Provenance, Confidence: Medium)

This makes the first screen feel like a report, not a hex dump.

2. Replace scary tab names with intent names

Stop making users choose “FORENSIC / TECHNICAL / RAW”.
Use:
• Privacy
• Authenticity
• Photography
• Evidence
• Research
• Raw (advanced)

Even if the underlying data is the same, labels matter. “Raw” is for nerds who opt-in.

3. Add “Normal / Advanced” density control

A simple toggle:
• Normal: highlights + grouped sections + only fields with human meaning.
• Advanced: everything, tree view, raw JSON.

Default to Normal. Remember preference.

4. Group by user meaning, not standards

Users don’t think in EXIF/IPTC/XMP. They think:
• When and where
• Device and software
• Edit history
• Ownership/author
• Security/integrity
• File structure

So map standards under those headings, and only show the standard names as secondary metadata.

5. Make “risk” non-alarming and actionable

If you want to help privacy users, do it like:
• “This file contains location data. If you’re sharing publicly, consider removing it.”
Not:
• “GPSLatitude: 12.9716”

Always pair a finding with an action link:
• “How to remove metadata on iPhone / Android / Windows / macOS”
• “Export cleaned copy” (future)

6. Fix “missingness” language

“Not Found” reads like “we looked for something bad”. Use:
• “Not present in this file”
• “Not supported for this format”
• “Available on Pro for this file” (only if it exists)

This reduces paranoia and reduces “is this broken?” confusion.

7. Make the paywall feel honest, not ominous

Instead of a wall of “LOCKED” sections, show a small panel:
• “Unlock +128 additional fields for this file”
• Show 3–5 example locked fields that actually exist
• Tie to the user’s current intent:
• Photography: “lens calibration, focus points”
• Authenticity: “software history, XMP edit tags”
• Privacy: “embedded author fields”

No “we know secrets you don’t”.

A concrete results page layout that won’t scare people 1. Header: filename + detected type + one-line disclaimer
• “JPEG photo. Metadata may be incomplete if the file was shared via apps.” 2. Highlights card (default, always visible) 3. Intent tabs (Privacy / Authenticity / Photography / Evidence / Raw)
• Each tab shows 2–4 sections max, with “show more” inside. 4. “Details” accordion per section
• Shows key fields first
• “View all fields in this section” expands into table/tree 5. Export button always visible
• “Download JSON”
• Optional “Copy summary” 6. Diagnostics tucked away
• Small link: “How was this extracted?”
• Shows format detected, extractors used, warnings.

What I would implement first (highest leverage, least work) 1. Highlights card with Impact + Confidence + Limitations line. 2. Rename tabs to intent names and add Normal/Advanced toggle. 3. Replace “Not Found” with the three missingness states. 4. Paywall preview panel that shows real locked examples.

That alone will make the UI feel like a calm report rather than a forensic console.

Guardrail: don’t remove the power

Power users want the firehose. Keep it, but behind “Advanced/Raw”. Fear reduction is not dumbing down. It’s staging.

If you paste your current results page structure (tabs/sections) or share a screenshot, I can propose an exact mapping from your existing components to this “calm report first” layout without rewriting everything.
for you:# MetaExtract UI Analysis - Input for ChatGPT

## Test File Information

- **Filename**: `20251225_44810PMByGPSMapCamera_A27, Santhosapuram, Kudremukh Colony, Koramangala_Bengaluru_Karnataka_India_12_923974_77_6254197J4VWJFG+H5GMT_+05_30.jpg`
- **Size**: 9.12 MB (9,562,433 bytes)
- **Type**: JPEG image from Xiaomi phone with GPS Map Camera app
- **Resolution**: 3072 x 4096 (12.58 MP, portrait orientation)

## Burned-In Metadata (OCR Extracted from Image Overlay)

The image has visual text overlay containing:

```
Bengaluru, Karnataka, India
A27 Santhosapuram, Kudremukh Colony, Koramangala
Bengaluru, Karnataka 560034, India
Lat 12.923974° Long 77.625419°
Plus Code: 7J4VWJFG+H5
Thursday, 25/12/2025 04:48 PM GMT +05:30
231° SW (compass direction)
25.54° C (temperature)
297.42 km/h (speed - likely erroneous)
34% (humidity)
903 m (altitude)
```

## Current API Response Structure (Enterprise Tier)

```json
{
  "filename": "gps_test_image.jpg",
  "filesize": "9.12 MB",
  "filetype": "JPG",
  "mime_type": "image/jpeg",
  "tier": "enterprise",
  "fields_extracted": 232,
  "fields_available": 45000,
  "processing_ms": 8963,

  "file_integrity": {
    "md5": "dd32a8f4770a8ce5cb018679885284a0",
    "sha256": "8774745d7a887daa96ed3e96552a9cc5fcb4683552dbaeb0db29415258367412",
    "sha1": "e00bae45e607d74f05c87c31e790d20b0a0735f0",
    "crc32": "a12c2dc9"
  },

  "filesystem": {
    "size_bytes": 9562433,
    "size_human": "9.12 MB",
    "created": "2026-01-01T00:43:21.220987",
    "modified": "2026-01-01T00:43:21.241103",
    "accessed": "2026-01-01T00:43:27.347190",
    "permissions_octal": "0o644",
    "permissions_human": "-rw-r--r--",
    "owner": "pranay",
    "inode": 192777236,
    "hard_links": 1
  },

  "calculated": {
    "aspect_ratio": "3:4",
    "megapixels": 12.58,
    "orientation": "portrait",
    "file_age_human": "just now"
  },

  "gps": {}, // Empty - GPS data is burned into image, not in EXIF

  "summary": {
    "filename": "gps_test_image.jpg",
    "filesize": "9.12 MB",
    "filetype": "JPG",
    "width": 3072,
    "height": 4096
  },

  "forensic": {
    "forensic": {
      "digital_signatures": {},
      "blockchain_nft": {},
      "watermarking": {},
      "c2pa": {},
      "adobe_credentials": {},
      "filesystem": {
        "file_created": "...",
        "file_modified": "...",
        "file_extended_attributes": ["com.apple.provenance"]
      }
    },
    "authentication": {
      "is_authenticated": false,
      "confidence_score": 0,
      "issues": ["No authentication metadata found"],
      "security_flags": ["unauthenticated_content"]
    },
    "integrity": {
      "file_hash_md5": "...",
      "file_hash_sha256": "..."
    }
  },

  "exif": {
    "ImageWidth": 3072,
    "Model": "24053PY09I :: Captured by - GPS Map Camera",
    "ImageHeight": 4096,
    "Make": "Xiaomi",
    "ApertureValue": 1.62,
    "DateTimeOriginal": "2025:12:25 16:48:10",
    "WhiteBalance": 0,
    "ExposureTime": 0.01,
    "Flash": 16,
    "FNumber": 1.63,
    "ISO": 1011,
    "FocalLengthIn35mmFormat": 25,
    "FocalLength": 5.84,
    "MeteringMode": 1,
    "Orientation": 0,
    "ModifyDate": "2025:12:25 16:48:10"
  },

  "image": {
    "width": 3072,
    "height": 4096,
    "format": "JPEG",
    "mode": "RGB",
    "dpi": [72, 72],
    "bits_per_pixel": 24,
    "has_icc_profile": true
  },

  "normalized": {
    "camera_make": "Xiaomi",
    "camera_model": "24053PY09I :: Captured by - GPS Map Camera",
    "iso": 1011,
    "aperture": 1.63,
    "shutter_speed": "1/100",
    "focal_length": 5.84,
    "flash_used": false,
    "color_space": "sRGB",
    "exposure_triangle": "ISO 1011, f/1.63, 1/100"
  },

  "thumbnail": {
    "has_embedded": true,
    "width": 120,
    "height": 160
  },

  "perceptual_hashes": {
    "available": true,
    "phash": "f9d8c0e443c3e1d3",
    "dhash": "3133337b3f07c3d1",
    "ahash": "fcdd990080c3f101",
    "whash": "fcdf990881c3f311"
  },

  "burned_metadata": {
    "has_burned_metadata": false, // OCR didn't detect it automatically
    "ocr_available": true,
    "extracted_text": null,
    "confidence": "none"
  },

  "metadata_comparison": {
    "has_both": false,
    "has_embedded_only": false,
    "has_burned_only": false,
    "summary": {
      "embedded_metadata_present": false,
      "burned_metadata_present": false,
      "gps_comparison": "no_gps",
      "overall_status": "no_metadata"
    }
  },

  "locked_fields": [], // Enterprise tier has no locked fields

  "extraction_info": {
    "tier": "super",
    "exiftool_used": true,
    "fields_extracted": 232,
    "specialized_engines": {
      "medical_imaging": true,
      "astronomical_data": true,
      "geospatial_analysis": true,
      "drone_telemetry": true,
      "blockchain_provenance": true,
      "emerging_technology": true
      // ... 21 specialized engines total
    }
  }
}
```

---

## Current Results Page Structure

### Main Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: filename | SIZE: 9.12 MB | TYPE: JPG | SHA256: 8774745d...  │
│ [Context Indicator] [DOWNLOAD_REPORT / UNLOCK_FULL_DATA button]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌─────────────────────────────────────────────┐  │
│  │ LEFT SIDEBAR │  │              MAIN CONTENT AREA              │  │
│  │              │  │                                             │  │
│  │ Analysis     │  │  TABS: ALL | EXPLORER | ADVANCED |          │  │
│  │ Summary      │  │        FORENSIC | TECHNICAL | RAW           │  │
│  │ ─────────    │  │                                             │  │
│  │ Total Fields │  │  [Search/Filter input]                      │  │
│  │ 232          │  │                                             │  │
│  │              │  │  ┌─────────────────────────────────────┐    │  │
│  │ File         │  │  │ SECTION: File Integrity             │    │  │
│  │ Integrity    │  │  │ MD5: dd32a8f4770a8ce5cb018679...    │    │  │
│  │ VERIFIED     │  │  │ SHA256: 8774745d7a887daa96ed...     │    │  │
│  │              │  │  └─────────────────────────────────────┘    │  │
│  │ Location     │  │                                             │  │
│  │ Data         │  │  ┌─────────────────────────────────────┐    │  │
│  │ Not Found    │  │  │ SECTION: Forensic Evidence          │    │  │
│  │              │  │  │ authentication.is_authenticated:    │    │  │
│  │ Dimensions   │  │  │   false                             │    │  │
│  │ 12.58 MP     │  │  │ authentication.confidence_score: 0  │    │  │
│  │              │  │  │ ...                                 │    │  │
│  │ Advanced     │  │  └─────────────────────────────────────┘    │  │
│  │ Analysis     │  │                                             │  │
│  │ Not Run      │  │  ┌─────────────────────────────────────┐    │  │
│  ├──────────────┤  │  │ SECTION: File Summary               │    │  │
│  │ GPS Location │  │  │ filename: gps_test_image.jpg        │    │  │
│  │ (if present) │  │  │ filesize: 9.12 MB                   │    │  │
│  │ LAT: ...     │  │  │ width: 3072                         │    │  │
│  │ LON: ...     │  │  │ height: 4096                        │    │  │
│  │ [View Maps]  │  │  └─────────────────────────────────────┘    │  │
│  ├──────────────┤  │                                             │  │
│  │ File Preview │  │  ┌─────────────────────────────────────┐    │  │
│  │ [placeholder]│  │  │ SECTION: Calculated Fields          │    │  │
│  │              │  │  │ aspect_ratio: 3:4                   │    │  │
│  │ ZERO_DATA_   │  │  │ megapixels: 12.58                   │    │  │
│  │ RETENTION    │  │  │ orientation: portrait               │    │  │
│  └──────────────┘  │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  ┌─────────────────────────────────────┐    │  │
│                    │  │ SECTION: Camera & EXIF              │    │  │
│                    │  │ ImageWidth: 3072                    │    │  │
│                    │  │ Model: 24053PY09I :: Captured by... │    │  │
│                    │  │ Make: Xiaomi                        │    │  │
│                    │  │ DateTimeOriginal: 2025:12:25...     │    │  │
│                    │  │ ISO: 1011                           │    │  │
│                    │  │ FNumber: 1.63                       │    │  │
│                    │  │ ... (30+ fields)                    │    │  │
│                    │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  ┌─────────────────────────────────────┐    │  │
│                    │  │ SECTION: GPS Location               │    │  │
│                    │  │ (empty - no EXIF GPS data)          │    │  │
│                    │  └─────────────────────────────────────┘    │  │
│                    │                                             │  │
│                    │  [LOCKED FIELDS NOTICE - if not unlocked]   │  │
│                    │  "X ADDITIONAL FIELDS AVAILABLE"            │  │
│                    │  [UNLOCK_ALL_FIELDS button]                 │  │
│                    └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Tab Structure

### Tab 1: ALL (Default)

Shows all metadata in sections:

- File Integrity (MD5, SHA256)
- Metadata Comparison (if burned metadata detected)
- Burned Metadata Display (if detected)
- Forensic Evidence
- File Summary
- Calculated Fields
- Camera & EXIF
- GPS Location (if present)
- [Locked fields notice for free tier]

### Tab 2: EXPLORER

- Interactive metadata tree explorer
- View modes: simple | advanced | raw
- Expandable/collapsible sections

### Tab 3: ADVANCED

- Advanced forensic analysis results
- Steganography detection
- Manipulation detection
- AI content detection
- Comparison results
- Timeline analysis
- Forensic report generation

### Tab 4: FORENSIC

- Metadata Comparison Display
- Burned Metadata Display
- File Integrity Hashes
- Chain of Custody
- Filesystem Metadata

### Tab 5: TECHNICAL

- Camera Settings (EXIF)
- Interoperability (IFD)
- MakerNote (Vendor-Specific) - LOCKED for free tier
- IPTC Metadata - LOCKED for free tier
- XMP Metadata - LOCKED for free tier
- XMP Namespaces - LOCKED for free tier
- ICC Profile
- Thumbnail Metadata
- Embedded Thumbnails - LOCKED for free tier
- Image Container
- Scientific Metadata - LOCKED for free tier
- Scientific Data (HDF5/NetCDF) - LOCKED for free tier
- Video Telemetry
- 360° / Panorama

### Tab 6: RAW

- Extended metadata fields (200+ fields)
- Full JSON export capability
- LOCKED for free tier with purchase prompt

---

## Current Section Headers (with icons)

| Section             | Icon        | Color       | Description                |
| ------------------- | ----------- | ----------- | -------------------------- |
| File Integrity      | Hash        | amber-500   | MD5, SHA256 hashes         |
| Forensic Evidence   | ShieldCheck | emerald-500 | Authentication, provenance |
| File Summary        | FileText    | primary     | Basic file info            |
| Calculated Fields   | Calculator  | cyan-500    | Derived values             |
| Camera & EXIF       | Camera      | purple-400  | Camera settings            |
| GPS Location        | MapPin      | rose-500    | Coordinates                |
| MakerNote           | Tag         | orange-400  | Vendor-specific            |
| IPTC Metadata       | Tag         | indigo-400  | Press/publishing           |
| XMP Metadata        | Tag         | pink-400    | Adobe extensible           |
| XMP Namespaces      | Tag         | fuchsia-400 | XMP namespace details      |
| ICC Profile         | Tag         | emerald-400 | Color profile              |
| Thumbnail Metadata  | Tag         | amber-400   | Embedded thumbnail info    |
| Embedded Thumbnails | Image       | yellow-400  | Thumbnail images           |
| Image Container     | Tag         | blue-400    | Container format           |
| Scientific Metadata | Database    | sky-400     | Scientific data            |
| Scientific Data     | FileText    | emerald-400 | HDF5/NetCDF                |
| Video Telemetry     | Zap         | rose-400    | Video sensor data          |
| 360° / Panorama     | Camera      | teal-400    | Spherical images           |

---

## Current "Locked" UI Patterns

### Pattern 1: Individual Field Lock

```tsx
<button onClick={() => setShowPayment(true)}>
  <span>Upgrade to view</span>
  <Lock className="w-3 h-3" />
</button>
```

### Pattern 2: Section Lock Block

```tsx
<div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
  <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
  <p className="text-xs text-slate-400 font-mono mb-2">
    {count} VENDOR-SPECIFIC FIELDS LOCKED
  </p>
  <Button variant="link" onClick={() => setShowPayment(true)}>
    UNLOCK_MAKERNOTES
  </Button>
</div>
```

### Pattern 3: Full Tab Lock (RAW tab)

```tsx
<div className="flex flex-col items-center justify-center h-[400px] text-center">
  <Database className="w-16 h-16 text-white/5 mb-4" />
  <h3 className="text-lg font-bold text-white font-mono mb-2">
    RAW_DATA_LOCKED
  </h3>
  <p className="text-slate-500 max-w-sm mb-6 text-sm">
    Access to {count} extended metadata fields including MakerNotes, IPTC, XMP,
    and proprietary tags requires a license.
  </p>
  <Button onClick={() => setShowPayment(true)}>PURCHASE_LICENSE ($5.00)</Button>
</div>
```

---

## Current Issues Identified (from ChatGPT's analysis)

1. **Volume without prioritization**: 232 fields displayed without hierarchy
2. **Jargon**: MakerNotes, IPTC, XMP, IFD visible to all users
3. **Ambiguous flags**: "Not Found", "Integrity", "Forensic" terminology
4. **Locked blocks**: Multiple "LOCKED" sections feel ominous
5. **No "what this means" layer**: No plain-language explanations
6. **Tab names**: FORENSIC / TECHNICAL / RAW are intimidating
7. **Missing highlights**: No summary of key findings at top
8. **No impact/confidence labels**: Users can't assess importance

---

## Requested Mapping

Please provide an exact mapping from the current components to a "calm report first" layout that:

1. Adds a **Highlights card** at the top with:
   - 3-7 bullet findings in plain language
   - Impact labels (Privacy, Authenticity, Workflow, None)
   - Confidence labels (High/Med/Low)
   - Limitations disclaimer

2. Renames tabs to **intent-based names**:
   - Current: ALL | EXPLORER | ADVANCED | FORENSIC | TECHNICAL | RAW
   - Proposed: Privacy | Authenticity | Photography | Evidence | Research | Raw (advanced)

3. Adds **Normal/Advanced toggle** for density control

4. Groups by **user meaning** instead of standards:
   - When and where
   - Device and software
   - Edit history
   - Ownership/author
   - Security/integrity
   - File structure

5. Makes **risk non-alarming** with actionable language

6. Fixes **missingness language**:
   - "Not Found" → "Not present in this file"
   - "LOCKED" → "Available on Pro" with example fields

7. Makes **paywall feel honest**:
   - Show real locked field examples
   - Tie to user's current intent

CHATGPT_UI_ANALYSIS_INPUT.md contains:

Test File Info: The GPS Map Camera image from Bengaluru with burned-in metadata (coordinates, address, weather, compass, altitude)

OCR-Extracted Burned Metadata:

Location: A27 Santhosapuram, Kudremukh Colony, Koramangala, Bengaluru
GPS: Lat 12.923974° Long 77.625419°
Plus Code: 7J4VWJFG+H5
Date: Thursday, 25/12/2025 04:48 PM GMT +05:30
Weather: 25.54°C, 34% humidity, 903m altitude
Compass: 231° SW
Full API Response Structure (232 fields from enterprise tier)

Current Results Page Layout (ASCII diagram showing sidebar + tabs + sections)

Current Tab Structure:

ALL | EXPLORER | ADVANCED | FORENSIC | TECHNICAL | RAW
Each tab's sections listed
Section Headers with icons and colors

Current "Locked" UI Patterns (3 different lock styles)

Issues Identified from ChatGPT's analysis

Requested Mapping for the "calm report first" redesign

also:You’re right — I should have responded, not pasted. Here’s the tailored answer, mapped to this repo:

Start with a calm “Highlights” card on the results page. Use the existing summary area in results.tsx to show 3–7 plain‑language findings with impact/confidence, plus a short limits note (“metadata can be missing or stripped”). Replace “VERIFIED [MD5+SHA256]” with “Hashes computed (MD5/SHA256)” and “Not Found” with “Not present in this file.”
Rename tabs to intent‑based labels. In results.tsx, switch ALL/FORENSIC/TECHNICAL to something like Summary / Privacy / Authenticity / Photography / Evidence / Raw, keeping Raw opt‑in.
The explorer already has density control; make it feel safe by default. In metadata-explorer.tsx, rename “Simple” to “Normal,” keep Advanced/Raw behind explicit choice, and persist the preference.
Group by meaning instead of standards. Lean on metadataCategories.ts to surface “When/Where,” “Device/Software,” “Edit history,” “Ownership,” “Security,” and show EXIF/IPTC/XMP as secondary labels only.
Reframe the paywall. Replace the “ADDITIONAL FIELDS AVAILABLE” block in results.tsx with “Unlock X more fields for this file” and show 3–5 real examples from locked sections.
You already have the right raw data. The problem is presentation. Right now the UI is shaped like a forensic console: it leads with hashes, “forensic”, “not found”, “locked”. For most users that reads as danger, not insight.

Below is an exact component-to-component mapping from what you have to a “calm report first” layout. I’ll anchor this to your GPS Map Camera JPEG example because it’s the perfect stress test: embedded GPS is empty, but the user-visible truth is in the pixels.

⸻

The core rule that reduces fear

On first render, show only: 1. What matters for the likely intent 2. What is true for this file 3. What the user can do next

Everything else goes behind an explicit “Advanced” choice.

⸻

0. Fix the scariest number first: “fields_available: 45000”

Do not show “45,000 available” on the results page. It implies:
• you found 45k things about their file
• or you are withholding 45k secrets

Replace it with:
• “Fields found in this file: 232”
Optional secondary copy:
• “More metadata types exist for other formats and devices.”

Keep 45k for marketing or internal coverage dashboards, not per-file UX.

⸻

1. Header mapping

Current header

filename | SIZE | TYPE | SHA256

New header (calm)
• Line 1: Filename (truncate)
• Line 2 (small): Detected: JPEG photo, 12.58 MP, Portrait
• Right side actions: Download JSON (always), Copy summary (optional), Run OCR for overlay (only if applicable)

Move SHA256 out of the header. Hashes are important, but not “first 1 second” important for most users.

Where to show SHA256:
• Evidence tab (default collapsed section)
• A small “Integrity available” badge in header that expands on click

⸻

2. Left sidebar mapping

Current sidebar items
• Total Fields 232
• File Integrity VERIFIED
• Location Data Not Found
• Dimensions 12.58 MP
• Advanced Analysis Not Run
• GPS Location section
• Preview placeholder
• ZERO_DATA_RETENTION badge

New sidebar content (same space, less fear)

Replace the forensic-style bullets with a neutral “Report overview”:

Report overview
• Capture time: 25 Dec 2025, 4:48 PM (from EXIF)
• Location: Not embedded (EXIF). Overlay text may contain location.
• Device: Xiaomi 24053PY09I (GPS Map Camera)
• Edits: No edit metadata detected (not proof of no edits)
• Integrity: Hashes computed

Keep “Zero retention” but put it as a quiet trust chip near the bottom, not shouting.

Remove “Not Found” language. Use “Not embedded in this file”.

⸻

3. Main content mapping

A) Add a Highlights card at the very top (new component)

This is the single highest leverage change.

For your GPS Map Camera JPEG, the Highlights card should render like this:

Highlights
• Capture time found: 2025-12-25 16:48:10 (EXIF)
Impact: Workflow, Confidence: High
• Location not embedded: No EXIF GPS tags in this file
Impact: Privacy, Confidence: High
• Device info present: Xiaomi 24053PY09I, tagged “Captured by GPS Map Camera”
Impact: Privacy, Confidence: High
• Overlay text likely contains address/GPS: Run OCR to extract
Impact: Privacy, Confidence: Medium
• Hashes computed: MD5, SHA1, SHA256
Impact: Evidence, Confidence: High

Limits (one line)
Metadata can be missing or stripped. Overlay text is part of the pixels, not embedded EXIF.

This makes the first screen feel like a calm report, not an investigation.

Where it comes from in your data:
• EXIF DateTimeOriginal, ModifyDate
• EXIF Make/Model
• gps object empty
• file_integrity present
• burned_metadata.ocr_available true but extracted_text null

B) Replace current tabs with intent-based tabs (exact mapping)

Current tabs:
• ALL | EXPLORER | ADVANCED | FORENSIC | TECHNICAL | RAW

New tabs:
• Privacy | Authenticity | Photography | Evidence | Research | Raw

Now map each old tab to the new ones:

OLD: ALL → NEW: Privacy (default for this file) + small “Overview”
“ALL” should stop being a tab. It becomes:
• Highlights card (always visible)
• Then the currently selected intent tab content

If you still want an “Overview”, make it a section inside each intent tab, not a tab.

OLD: FORENSIC → NEW: Evidence + Authenticity
Split it:
• Evidence gets: hashes, chain of custody, filesystem metadata, report/export framing
• Authenticity gets: authentication status, re-encoding signals, manipulation/AI detection outcomes (when run)

OLD: TECHNICAL → NEW: Photography + Raw
Split it:
• Photography gets: camera settings, exposure triangle, lens, ISO, shutter
• Raw gets: standards-specific dumps (IFD/IPTC/XMP/ICC) and the Explorer tree

OLD: ADVANCED → NEW: Research
Research tab becomes the place for:
• steganography, manipulation detection, AI detection
• timeline analysis
• comparisons
This is opt-in. Default collapsed/empty state is fine with a “Run analysis” button.

OLD: EXPLORER → NEW: Raw (sub-view)
Explorer becomes a mode inside Raw:
• Normal: curated key groups
• Advanced: tree view
• Raw: JSON

OLD: RAW → NEW: Raw
Keep it, but move it to the far right and label clearly as advanced.

⸻

4. Normal/Advanced density toggle mapping

You already have view modes in EXPLORER. Make that global and safe by default.

Current

Explorer: simple | advanced | raw (unclear naming)

New

Global toggle (top right of results):
• Normal (default)
• Advanced

Behavior:
• Normal: shows Highlights + curated sections only, no jargon labels
• Advanced: reveals standards names (EXIF/IPTC/XMP), shows the Explorer tree affordance, shows more sections expanded by default
• Raw JSON export stays available in both, but Raw tab remains opt-in

Persist preference per user.

⸻

5. Group by user meaning, using your existing sections

You don’t need to delete sections. You need a mapping layer that decides what to show where.

Here’s the exact mapping from your current sections to the new meaning groups:

Meaning group: When and where
• EXIF: DateTimeOriginal, ModifyDate
• GPS Location section (but only if non-empty)
• Burned Metadata Display (if OCR extracted)
• Filesystem created/modified/accessed (label as “On this computer”, not capture time)

Critical wording:
• “Capture time (from EXIF)”
• “File created time (this computer)”
These are not the same thing.

Meaning group: Device and software
• Camera & EXIF: Make, Model, exposure, ISO, flash
• Normalized: exposure_triangle, color_space
• Any “software” tags if present (often in EXIF/XMP)

Meaning group: Edit history
• XMP metadata (if present)
• IPTC metadata (if present)
• ModifyDate is not edit history. Label it as “EXIF modify timestamp” and avoid implying editing.

Meaning group: Ownership and author
• IPTC creator/credit fields (if present)
• XMP author fields (if present)
• Filesystem owner (label “Local file owner”, do not imply original author)

Meaning group: Security and integrity
• File Integrity hashes
• Forensic authentication block (but rename it)

Rename:
• “Forensic Evidence” → “Authenticity signals”
• “Unauthenticated content” → “No authenticity proof found” (neutral)

Meaning group: File structure
• File Summary
• Image Container
• ICC Profile
• Thumbnail Metadata / embedded thumbnail
• Perceptual hashes
• Calculated fields

⸻

6. Make risk non-alarming and actionable

Where you currently show:
• “Location Data Not Found”
Use:
• “Location not embedded in this file.”

Where you currently show:
• “UNAUTHENTICATED_CONTENT”
Use:
• “No authenticity proof found. This is common.”

Every risk-ish item gets a “What can I do?” link:
• Remove location metadata guidance
• If overlay text has location: “You need a clean copy without overlay if you want to share safely.”

⸻

7. Fix the “burned metadata” story (your test file exposes it)

Your API says:
• burned_metadata.has_burned_metadata = false
• ocr_available = true
• extracted_text = null

But you already know the overlay contains rich location data.

UI behavior that feels calm and correct:
• In Highlights: “Overlay text detected: Run OCR to extract” only if you have any signal
If you have no automated signal yet, don’t claim detection. Instead:
• “This image may contain overlay text (common in GPS camera apps). Run OCR to check.”

Then the Privacy tab includes a dedicated card:
Overlay text (in pixels)
• Status: Not extracted
• Button: Run OCR
• After OCR: show parsed fields in a neat, human list

This turns a scary gap into an obvious next step.

⸻

8. Unify “Locked” patterns into one non-ominous pattern

You currently have 3 lock UIs. Replace all of them with one pattern that is file-specific and intent-specific.

New copy rules:
• Never shout “LOCKED”.
• Never show “locked fields” for fields that do not exist for the file.

Use:
Available on Pro
Unlock +N fields for this file.
Examples: <field1>, <field2>, <field3>.

For enterprise tier, hide paywall entirely.

Implementation implication:
Your API should provide, for non-enterprise tiers:
• locked_count_by_group
• locked_examples_by_group (real fields present for that file)

Do not fabricate examples.

⸻

9. What each new tab shows for this file

Privacy (default)
• Highlights (already shows location not embedded, overlay OCR prompt)
• “Location and sharing risks”
• EXIF GPS: not embedded
• Overlay text: run OCR
• Device identifiers: Make/Model
• “What to do next”
• Remove metadata guidance
• Export summary

Authenticity
• “Authenticity signals”
• No authenticity proof found (common)
• Perceptual hashes
• Any re-encode/manipulation results if available
• Keep language conservative: signals, not verdicts

Photography
• Camera settings and exposure triangle
• Thumbnail presence, ICC profile, basic imaging properties

Evidence
• Hashes
• Filesystem timestamps and provenance (labeled correctly)
• “Download evidence report” later, but JSON export now

Research
• Buttons to run advanced analysis modules
• Show results only after run, keep defaults collapsed

Raw
• Explorer tree
• Full JSON
• Standards names visible here, not in Normal mode

⸻

The one change that will make everything feel safer immediately

Make the default landing on results:
• Highlights card
• Privacy tab
• Normal density

Even photographers will tolerate that because Photography tab is one click away. Non-technical users stop seeing “forensic”, “raw”, “locked”, “hashes” as the opening move.

⸻

If you want this to be executable for your agents, the next step is to convert the above mapping into a task list with acceptance criteria tied to the specific file behavior (especially the “EXIF GPS empty but overlay present” case). That prevents the redesign from becoming just renaming and rearranging.
Below is a repo-ready task plan doc that agents can execute. It is grounded in your current components and the GPS Map Camera test file, with concrete acceptance criteria and QA steps.

:::writing{id=“90562” variant=“standard”}

Calm Report First Redesign: Task Plan and Acceptance Criteria

Path suggestion: docs/ux/tasks/calm-report-first.md

This doc converts the “calm report first” UX mapping into shippable tasks with acceptance criteria, using real repo components and a concrete test fixture.

Related docs:
• docs/ux/ux-audit.md
• docs/ux/personas.md
• docs/ux/agent-playbook.md

⸻

0. Goal

Reduce user fear and cognitive overload by changing the results page from:
• forensic-console-first
to:
• calm-report-first with progressive disclosure

Success means:
• most users understand what was found in <10 seconds
• scary jargon and forensic framing are opt-in, not default
• missingness and locking feel honest and file-specific
• advanced users still have full power via Raw/Explorer

⸻

1. Non-negotiables (hard rules)
   1. Do not show per-file “fields_available: 45000” anywhere in the results UI.
   2. “Not Found” is banned. Use explicit missingness states:
      • Not present in this file
      • Not supported for this format
      • Available on Pro for this file (only if it actually exists)
   3. “LOCKED” is banned in user-facing copy. Use “Available on Pro”.
   4. Default tab must be intent-based and calm (Privacy for this test file).
   5. Hashes and forensic signals must not dominate the first screen.
   6. Paywall previews must only show locked fields that exist for this file.
   7. For the GPS Map Camera use case, EXIF GPS empty must be explained without implying the user is unsafe by default.

⸻

2. Test fixture (must be used in QA)

File

20251225*44810PMByGPSMapCamera_A27, Santhosapuram, Kudremukh Colony, Koramangala_Bengaluru_Karnataka_India_12_923974_77_6254197J4VWJFG+H5GMT*+05_30.jpg

Properties
• JPEG, 9.12 MB, 3072x4096, Xiaomi, GPS Map Camera overlay
• EXIF contains DateTimeOriginal and camera details
• EXIF GPS is empty
• Overlay contains address, lat/long, plus code, timestamp, compass, temperature, humidity, altitude, speed

Current API fields relevant
• exif.Make, exif.Model, exif.DateTimeOriginal, exif.ISO, etc.
• gps is empty
• file_integrity present
• burned_metadata.ocr_available = true but extracted_text = null

This fixture must validate that the UI:
• does not claim embedded GPS exists
• prompts OCR for overlay text in a calm way

⸻

3. Workstreams and tasks

WS-A: Top-of-page Highlights Card (calm summary first)

Task A1: Add Highlights card at top of results page
• Persona: P4, P10, P2, P5 (see docs/ux/personas.md)
• Step: Results
• Problem: user sees 232 raw fields and forensic sections, feels overwhelmed
• UX change:
• Insert a Highlights card above tabs in results (likely results.tsx)
• 3 to 7 bullets, each with:
• plain-language statement
• Impact label: Privacy | Authenticity | Workflow | None
• Confidence label: High | Med | Low
• Add one-line limits note: “Metadata can be missing or stripped. Overlay text is part of pixels, not embedded tags.”
• Data/logic:
• Derive highlights deterministically from existing response:
• Capture time from exif.DateTimeOriginal (High)
• Location embedded status from gps presence (High)
• Device info from exif.Make/exif.Model (High)
• Overlay OCR prompt if burned_metadata.ocr_available and extracted_text null (Med)
• Hashes present from file_integrity (High)
• Acceptance criteria (GPS Map Camera file): 1. Highlights renders within first screen without scrolling. 2. Shows capture time from EXIF. 3. Shows “Location not embedded” (not “not found”). 4. Shows “Overlay text may contain location. Run OCR to extract.” 5. Shows “Hashes computed: MD5, SHA1, SHA256”. 6. Does not show “45,000 available” anywhere.
• QA steps:
• Upload fixture file, confirm 3 to 7 bullets and limit line.
• Confirm no “Not Found” text on page.

Task A2: Add “Copy summary” action
• Persona: P10, P4, P2
• Step: Results
• UX change:
• Add button near Highlights: Copy summary text (bullets only) to clipboard
• Acceptance:
• Copies plain text summary without IDs/jargon
• Works in Normal and Advanced mode

⸻

WS-B: Intent tabs (rename and restructure)

Task B1: Rename tabs to intent-based names
• Current tabs: ALL | EXPLORER | ADVANCED | FORENSIC | TECHNICAL | RAW
• New tabs: Privacy | Authenticity | Photography | Evidence | Research | Raw
• UX change:
• Replace the tab labels and routing while preserving underlying sections
• Keep Raw as far-right and visually “advanced”
• Mapping:
• Privacy: location/sharing, overlay OCR, device identifiers, what-to-do
• Authenticity: authenticity signals, perceptual hashes, manipulation results if run
• Photography: camera settings, exposure triangle, ICC profile basics
• Evidence: hashes, filesystem times labeled properly, chain-of-custody framing
• Research: advanced analysis modules and results, gated behind “Run analysis”
• Raw: explorer tree + full JSON
• Acceptance criteria: 1. Old labels no longer appear anywhere in UI. 2. Default tab for fixture file is Privacy. 3. Raw tab exists and contains Explorer + JSON. 4. Evidence tab contains hashes but hashes are not shown as the first main section in Privacy.
• QA:
• Navigate through all tabs, confirm content appears and no broken routes.

⸻

WS-C: Density control (Normal vs Advanced)

Task C1: Add global Normal/Advanced toggle
• Current: Explorer has simple | advanced | raw
• UX change:
• Add global toggle near tabs: Normal | Advanced
• Normal hides standards jargon by default and collapses noisy sections
• Advanced reveals more fields, shows standards labels as secondary text
• Persist user selection (local storage or profile)
• Acceptance: 1. Default is Normal on first visit. 2. Switching to Advanced increases detail density without changing facts. 3. Preference persists after refresh. 4. Normal mode does not show “MakerNote”, “IPTC”, “XMP” as first-class headers outside Raw.
• QA:
• Toggle on/off, refresh page, confirm persistence and content changes.

⸻

WS-D: Group by user meaning, not standards

Task D1: Create meaning-group mapping layer for sections
• UX change:
• Present sections under these meaning groups: 1. When and where 2. Device and software 3. Edit history 4. Ownership and author 5. Security and integrity 6. File structure
• Implementation notes:
• Use existing section data but change display grouping order.
• Standards names are secondary labels only (Advanced/Raw).
• Proposed mapping (from current sections):
• When and where:
• EXIF DateTimeOriginal, ModifyDate
• GPS section (only if non-empty)
• Burned metadata (after OCR)
• Filesystem times labeled as “on this computer”
• Device and software:
• Camera & EXIF (Make/Model, exposure, ISO)
• Normalized exposure triangle
• Edit history:
• XMP/IPTC only if present
• Ownership and author:
• IPTC/XMP author fields if present
• Filesystem owner labeled “local file owner”
• Security and integrity:
• File Integrity hashes
• Authenticity signals (renamed from forensic evidence)
• File structure:
• Summary, Calculated, Image container, ICC profile, thumbnail metadata, perceptual hashes
• Acceptance: 1. In Normal mode, user sees meaning groups, not standards groups. 2. GPS Map Camera fixture shows “When and where” with capture time and “Location not embedded”. 3. “Device and software” shows Xiaomi model string. 4. “Security and integrity” contains hashes but is collapsed by default in Privacy.
• QA:
• Verify ordering and correct labeling of filesystem times vs capture time.

⸻

WS-E: Language and interpretation guardrails

Task E1: Replace “Not Found” and similar phrases
• UX change:
• Replace all “Not Found” with “Not present in this file”
• Replace “Unauthenticated content” with “No authenticity proof found (common)”
• Replace “VERIFIED” hash language with “Hashes computed”
• Acceptance: 1. No “Not Found” appears anywhere. 2. “No authenticity proof found” appears in Authenticity tab for fixture file. 3. Hash section uses neutral language and is not colored like an alarm.
• QA:
• Search UI text for “Not Found”, “LOCKED”, “UNAUTHENTICATED”, ensure none leak.

Task E2: Add “What this means” tooltips in Normal mode
• UX change:
• Add short tooltips for 6 meaning groups
• Add one tooltip for “Capture time vs file created time”
• Acceptance:
• Tooltips are short, neutral, and do not overclaim.

⸻

WS-F: Paywall honesty and UI unification

Task F1: Replace 3 lock patterns with 1 “Available on Pro” panel
• Current patterns:
• field lock button
• section lock block
• full tab lock
• UX change:
• Single component: AvailableOnProPanel
• Shows:
• “Unlock +N fields for this file”
• 3 to 5 example locked fields that exist for this file
• One sentence tying value to current intent tab
• Data/logic:
• Requires backend or response adapter to provide:
• locked_count_by_group
• locked_examples_by_group (real fields for that file)
• Acceptance: 1. No “LOCKED” text appears. 2. Free tier shows file-specific examples, not generic “MakerNotes, IPTC, XMP” copy. 3. Enterprise tier shows no paywall blocks.
• QA:
• Test with a free-tier response fixture (or mock) and ensure examples are real.

⸻

WS-G: Overlay OCR flow (burned metadata)

Task G1: Add “Run OCR for overlay” action and card
• Persona: P4, P16, P10
• Step: Results, Privacy
• Problem: EXIF GPS empty but overlay contains sensitive location info, currently missed
• UX change:
• Privacy tab includes “Overlay text (in pixels)” card:
• Status: Not extracted
• Button: Run OCR
• After OCR: show parsed fields in a human list (address, lat/long, date/time, compass, weather)
• Acceptance (fixture file): 1. Privacy tab shows overlay card with Run OCR button. 2. If OCR not run, UI does not claim overlay was detected as a fact. It says “may contain”. 3. After OCR completes, highlights update to include extracted address and lat/long with Confidence: Medium or High depending on OCR confidence. 4. GPS section remains “not embedded” even if overlay contains coordinates.
• QA:
• Verify the separation between embedded GPS and overlay-extracted GPS.

⸻

WS-H: Instrumentation (minimum viable)

Task H1: Add events for the redesign
Event list:
• results_viewed (include: filetype, size_bucket, default_intent)
• intent_tab_changed (from, to)
• density_toggled (normal, advanced)
• highlights_copied
• ocr_overlay_started, ocr_overlay_completed (success/failure)
• export_json_clicked
• paywall_viewed (intent, filetype)
• paywall_purchase_clicked (intent, plan)

Acceptance:
• Events fire once per action and include required properties.

⸻

4. Default behavior for the GPS Map Camera fixture (definition of done)

When the fixture file is uploaded and results open: 1. First screen shows Highlights card with 3 to 7 bullets and limits line. 2. Default tab is Privacy, Normal mode. 3. “Location not embedded in this file” is shown, not “Not Found”. 4. Overlay OCR prompt appears as “may contain” with Run OCR button. 5. Hashes are available but not visually alarming and not the main content of Privacy. 6. No forensic jargon is visible by default outside Evidence/Raw. 7. Raw tab exists for power users and includes Explorer tree + JSON export. 8. No “45,000 available” appears anywhere.

⸻

5. Risks and edge cases (must be handled)
   1. Social-app stripped images: no EXIF at all.
      • Highlights must say “No embedded capture metadata present (common after sharing apps).”
   2. Images with embedded GPS:
      • Privacy tab should show “Location embedded” plus guidance.
   3. Incorrect filesystem timestamps:
      • Must label as “On this computer” and never imply capture time.
   4. OCR false positives:
      • Overlay extraction should show confidence and avoid hard claims.
   5. Locked fields mismatch:
      • Do not show examples unless they exist for the file.

⸻

6. Implementation notes (repo touchpoints)

Likely files:
• Results page: results.tsx (tabs, header, sidebar, sections)
• Explorer: metadata-explorer.tsx (modes and tree)
• Category mapping: metadataCategories.ts (or equivalent)
• Paywall components: the three lock UI patterns noted in the input
• Response adapter: where API response is transformed for UI
• Analytics: wherever events are emitted

⸻

7. Phase order (do in this order)

Phase 0 (highest leverage):
• A1 Highlights card
• B1 Intent tab rename
• C1 Global Normal/Advanced toggle
• E1 Language fixes (“Not Found”, “LOCKED”, “VERIFIED”)

Phase 1 (honesty and trust):
• D1 Meaning-group mapping
• F1 Unified “Available on Pro” panel

Phase 2 (this fixture’s missing truth):
• G1 Overlay OCR flow

Phase 3:
• H1 Instrumentation polish and metrics dashboard wiring
:::
Below is the continuation that “finishes” the task plan. It adds the missing parts agents need to execute cleanly: component specs, copy specs, data contracts, tests/fixtures, PR slicing, and agent assignment. Paste it as an appendix to docs/ux/tasks/calm-report-first.md.

:::writing{id=“31874” variant=“standard”}

8. Component specs (what to build, not just what to change)

These specs are deliberately tight so agents do not bikeshed UI.

8.1 HighlightsCard

Inputs
• highlights: Array<{ text: string; impact: "Privacy"|"Authenticity"|"Workflow"|"None"; confidence: "High"|"Med"|"Low"; }>
• limits_note: string
• optional actions:
• onCopySummary()
• onRunOcr() (only if applicable)

UI rules
• Max 7 bullets. If more, collapse to 7 and add “View more” (Advanced only).
• Bullets must be plain language. No raw tag names (no “DateTimeOriginal”).
• Show Impact and Confidence as small chips, not loud badges.
• Limits note is always shown, single line, calm tone.

GPS Map Camera expected bullets
• Capture time found (EXIF)
• Location not embedded (EXIF GPS missing)
• Device info present (Make/Model)
• Overlay text may contain location. Run OCR to extract
• Hashes computed

⸻

8.2 IntentTabs

Tabs
• Privacy | Authenticity | Photography | Evidence | Research | Raw

Rules
• Default tab determined by intent inference (Section 10).
• Raw is rightmost and visually marked as advanced (subtle).

⸻

8.3 DensityToggle

Values
• Normal (default)
• Advanced

Rules
• Normal hides standards-first headers outside Raw.
• Advanced can show secondary labels like “Source: EXIF / XMP”.
• Persist preference.

⸻

8.4 MeaningGroupSection

A reusable group container for:
• When and where
• Device and software
• Edit history
• Ownership and author
• Security and integrity
• File structure

Rules
• Normal mode: each group shows 3–8 “key rows” and a “Show all” expander.
• Advanced mode: expanded by default (except Raw).

⸻

8.5 OverlayTextCard

States
• Not extracted: shows explanation + “Run OCR”
• Running OCR: progress indicator
• Extracted: shows parsed fields in a clean list

Rules
• Must clearly label this data as “text in pixels”, not embedded metadata.
• Parsed output must include confidence per field group (single score is fine).

⸻

8.6 AvailableOnProPanel (unified paywall UI)

Inputs
• unlock_count: number (for this file)
• examples: Array<{ label: string; value_preview: string }> (real fields)
• intent: current tab
• CTA: upgrade flow trigger

Rules
• Must never appear on enterprise tier.
• Must never show generic examples if file-specific examples are unavailable. If no examples, show only “Unlock +N fields for this file.”

⸻

9. Copy spec (fear-reduction language rules)

9.1 Banned phrases
• Not Found
• LOCKED
• VERIFIED
• UNAUTHENTICATED_CONTENT
• FORENSIC (as a default-facing label)

9.2 Required replacements
• “Not Found” → “Not present in this file”
• “Verified” → “Hashes computed”
• “Unauthenticated content” → “No authenticity proof found (common)”
• “Forensic Evidence” → “Authenticity signals”
• “GPS Location (empty)” → “Location not embedded (EXIF)”

9.3 Interpretation guardrails (must appear somewhere in Normal mode)
• “Metadata can be missing or stripped. Absence is not proof.”
• “File timestamps on this computer are not the same as capture time.”

9.4 Risk messaging pattern

Always use this structure: 1. Neutral finding 2. Why it matters (one clause) 3. What to do next (actionable link/button)

Example:
• “Location not embedded (EXIF). If you are sharing publicly, you may still have location in overlay text. Run OCR to check.”

⸻

10. Intent inference (deterministic defaults)

Goal: choose the default tab without guessing wildly.

Rules (priority order) 1. If overlay OCR is available and GPS is empty and Model string contains “GPS Map Camera”:
• default intent = Privacy 2. If EXIF/MakerNotes coverage is high (RAW/Pro) and camera tags present:
• default intent = Photography 3. If authenticity flags exist or advanced analyses were run:
• default intent = Authenticity 4. If user came from evidence-focused context (plan, route, or explicit action):
• default intent = Evidence 5. Otherwise:
• default intent = Privacy

If uncertain, show a one-time 3-option prompt:
• “Privacy” | “Authenticity” | “Photography”
Store choice.

⸻

11. Data contract changes (UI adapter requirements)

These are minimal additions to make UI honest and prevent fake previews.

11.1 Missingness state model (UI-level)

For any group/field, the adapter must classify:
• state: "present" | "not_present" | "not_supported" | "available_on_pro"

Do not overload empty objects with “not present” unless you are certain.

11.2 Locked fields preview support (non-enterprise tiers)

Add to response (or adapter computed):
• locked_summary: { total_locked_for_file: number; by_group: Record<string, number> }
• locked_examples: Record<string, Array<{ label: string; preview: string }>>

Rules:
• examples must be derived from real extraction output that is gated, not guessed.

11.3 Overlay OCR support

For overlay text:
• overlay_ocr: { status: "not_run"|"running"|"done"|"failed"; extracted_text?: string; parsed?: {...}; confidence?: number }

UI must treat “ocr_available” as capability, not evidence.

⸻

12. Testing and fixtures (non-optional)

12.1 Add UI fixtures

Create fixtures for: 1. GPS Map Camera file (this doc’s fixture) 2. EXIF-stripped social share image (no EXIF) 3. Image with real EXIF GPS 4. File with XMP edit history 5. Free-tier response with locked fields + real examples

Fixtures must include:
• response JSON
• expected default intent tab
• expected highlights bullets

12.2 Unit tests (logic)

Test:
• highlight generation function
• missingness classifier
• intent inference
• paywall preview selection (real fields only)

12.3 Integration tests (UI)

At minimum:
• renders Highlights card
• no banned phrases appear
• toggling Normal/Advanced changes density
• Raw tab exists and contains Explorer + JSON export
• overlay OCR flow renders correct states

12.4 Snapshot/regression checks (optional but recommended)
• snapshot the first screen of results for each fixture in Normal mode

⸻

13. PR slicing (how to ship without chaos)

PR 1: Language and headline structure
• Replace banned phrases
• Move hashes out of header into Evidence section
• Remove “fields_available: 45000” display

PR 2: Highlights + intent tabs
• Implement HighlightsCard
• Rename tabs and route sections accordingly
• Default to Privacy for the fixture

PR 3: Normal/Advanced density toggle + meaning groups
• Implement DensityToggle
• Implement meaning-group layout (Normal mode curated)

PR 4: Unified paywall component
• Implement AvailableOnProPanel
• Remove 3 old lock patterns
• Wire to locked preview data contract

PR 5: Overlay OCR flow
• Implement OverlayTextCard
• Add “Run OCR” action and results display
• Update highlights after OCR

PR 6: Tests + instrumentation
• Add fixtures
• Add unit/integration tests
• Add analytics events

⸻

14. Agent assignment (who does what)

Agent: UX-Layout

Owns PR 2 and PR 3.
Deliverables:
• HighlightsCard
• IntentTabs rename/mapping
• Meaning-group layout in Normal mode

Agent: Copy-Guardrails

Owns PR 1.
Deliverables:
• banned phrase sweep
• neutral replacements
• tooltips and limits note

Agent: Data-Adapter

Owns PR 4 data requirements.
Deliverables:
• missingness classifier
• locked preview extraction (real examples)
• intent inference logic if in adapter layer

Agent: OCR-Flow

Owns PR 5.
Deliverables:
• OverlayTextCard states
• OCR triggers and parsed presentation
• ensures embedded GPS vs overlay GPS separation is correct

Agent: QA/Tests

Owns PR 6.
Deliverables:
• fixtures
• unit tests for highlight/missingness/intent
• integration tests for first screen behavior

⸻

15. Final acceptance checklist (one page)

For the GPS Map Camera fixture:
• First screen shows Highlights card + limits note
• Default tab: Privacy, Normal mode
• “Location not embedded (EXIF)” shown, never “Not Found”
• Overlay OCR prompt shown as “may contain”, not a claim
• Hashes exist but not dominant in Privacy
• No “LOCKED”, “FORENSIC”, “VERIFIED”, “45,000 available” visible by default
• Raw tab contains Explorer tree + JSON export
• If OCR is run, parsed overlay location appears and is labeled “from overlay text”
• Embedded GPS remains “not embedded” even after overlay OCR

This is “done”.
:::
:::writing{id=“60483” variant=“standard”}

Phase 3: Instrumentation, fixtures, and regression safety
• H1 Instrumentation (events)
• results_viewed, intent_tab_changed, density_toggled, export_json_clicked, highlights_copied, ocr_overlay_started/completed, paywall_viewed, paywall_purchase_clicked
• 12.x Fixtures + tests
• Add fixtures for: GPS Map Camera, EXIF-stripped, EXIF GPS present, XMP edit history, free-tier locked preview
• Unit tests: highlights generation, intent inference, missingness classifier, paywall preview selection
• UI integration tests: first-screen render, banned-phrase sweep, toggle persistence, raw tab access, OCR state transitions
• Copy guardrail sweep
• Ensure banned phrases never appear via a simple “string scan” test across rendered UI in CI.

Phase 4: UX polish and speed
• Processing state clarity
• Replace vague “Processing…” with truthful steps: Uploading → Extracting → Normalizing → Ready
• Show elapsed time, not ETA, unless you can compute ETA reliably
• Section ergonomics
• Collapsed-by-default rules tuned per intent
• “Show all” expansion UX consistent across meaning groups
• Export ergonomics
• “Download JSON” always visible
• Optional “Download CSV” for Normal mode top-level groups (if already supported)
• Evidence tab: “Download evidence report” placeholder CTA (disabled if not implemented) with clear “coming soon” only if you commit to it

Phase 5: Persona-targeted defaults and landing routing
• Intent routing from entry points
• If user comes from privacy-oriented landing: default Privacy tab
• If from photographer landing: default Photography tab
• If from evidence landing: default Evidence tab
• Remember user preference
• Persist last used intent tab per user
• Persist Normal/Advanced per user
• Optional: onboarding prompt
• One-time, 3-choice intent picker only when inference is uncertain

This completes Phase 3 and adds the remaining phases that should follow once Phase 2 ships.
:::
Yes. Launching “images-only” is the right move if your goal is PMF signal, not completeness. Image metadata is where you can deliver a fast “aha” in under 10 seconds, and your current UX problems are most fixable there.

But do it deliberately, or you’ll learn the wrong thing.

First-principles: what are you actually testing?

PMF test is not “can I sell metadata extraction”. It’s: 1. Do users have a recurring, urgent job-to-be-done for image metadata? 2. Do they trust you with files and believe the output is useful? 3. Do they pay with low friction when the value is obvious?

If you launch with everything (45000 fields, medical, forensic, etc.), you test confusion and trust failure. If you launch with images-only + calm report first, you test the right thing.

What I would ship as “ui_images”

Scope:
• Input: JPG/JPEG/PNG only.
• Output: the “calm report” results with:
• Highlights
• Intent tabs (Privacy, Authenticity, Photography, Evidence, Raw)
• Overlay OCR flow (because it catches the GPS Map Camera class)
• Export JSON

Non-goals for launch:
• Video/audio/docs/medical claims
• “specialized engines: true” list in the UI
• Anything that implies you extract things you don’t

Positioning:
• Don’t call it “ui_images”. Call it “Photo Metadata Check” or “Image Metadata”.

Pricing: your “$1 for 10 files” idea

Good instinct: credits are the lowest-commitment price discovery tool. But the exact number matters less than payment friction and perceived fairness.

Option A (best for PMF signal, low friction)
• Free: 3 files/day (or 5 total as a trial)
• Paid: $1 for 20 files (or $2 for 50)
• Why: lets users hit the “wow” moment before paying, and credits feel cheap enough to impulse buy.

Option B (pure paid, higher signal but higher drop-off)
• No free tier
• $1 for 10 files
• Why I don’t love it: you’ll conflate “payment friction” with “no value”. You’ll undercount demand.

Strong opinion: start with some free, but keep it tight. You want conversion data after a real aha, not “free forever” behavior.

What “PMF” looks like for images-only

You need at least one of these to be true: 1. Privacy use case: People repeatedly check photos before sharing (location/device leaks). 2. Authenticity/OSINT: People use it for verification work and export reports. 3. Photography nerds: People check camera/lens settings and MakerNotes, batch use.

If you see none of these, don’t widen formats. Fix value or audience.

What to remove or hide for launch (to avoid fear and mistrust)
• Remove “fields_available: 45000” from any user-facing surface.
• Hide or rename “Forensic” language unless user explicitly chooses Evidence/Authenticity.
• Stop showing empty GPS blocks as a big “Not Found”. Show “Not embedded”.
• Don’t mention medical/scientific engines on an images-only launch page.

What to instrument so you learn fast

Minimum events:
• upload_started, upload_completed
• results_viewed (default intent)
• ocr_overlay_clicked (this is huge for your GPS Map Camera example)
• export_json_clicked
• paywall_viewed, credit_purchase_completed
• repeat_user_7d (retention proxy)

Your PMF signal is not just conversion. It’s: do they come back with more files.

Launch plan (simple) 1. New route/landing: /images 2. Copy built for one primary persona first (I’d pick Privacy-conscious consumer + creator). 3. Upload to results in one flow. 4. Tight free trial + credits. 5. Watch: completion rate, OCR usage, paid conversion, repeat usage.

Biggest risk

You’ll be tempted to market “works for medical/scientific” again. Don’t. It poisons trust and wrecks learnings.

If you want one crisp bet: ship images-only with the calm report UX, add overlay OCR, and run free small trial + cheap credits. That will tell you in a week whether people care enough to return and pay.
MetaExtract Images-Only Launch UI Spec

Scope: JPG / JPEG / PNG only. Goal: fast “aha” with low fear, honest outputs, lightweight monetization.

⸻

1. Product surfaces

1.1 Landing page: /images

Purpose: intent-setting + trust + start upload.

Above the fold
• Title: Check what’s hidden in your photos
• Subtitle (one line): Privacy, authenticity, and camera details. Clear summary first.
• Primary CTA: Upload images
• Secondary CTA: See example report (opens a static demo)

Trust strip (small, non-technical)
• “No account needed for trial”
• “Files processed securely”
• “Export JSON report”
• If you truly do local-only: say it. If not, do not imply it.

What it does (3 cards max) 1. Privacy check: location, device identifiers, overlay text (GPS camera apps) 2. Authenticity signals: edit traces, stripped metadata, hashes 3. Photography details: camera settings, exposure triangle

Limits and pricing teaser
• “Trial: 3 files free”
• “Credits: $1 for 20 files”
• Show on landing, but do not lead with it.

⸻

1.2 Upload page: same route or modal on /images

Keep it one flow: landing -> upload -> results.

Upload zone
• Copy: Drop JPG, JPEG, PNG here
• Secondary line: “Up to 10 files at a time”
• File size note: pick a number you can support (ex: 15 MB each). Be explicit.

File list

Each selected file shows:
• Thumbnail
• Filename (truncate)
• Size
• Type badge (JPG/PNG)
• Status: queued, uploading, extracting, done, failed
• Remove button

Actions
• Primary: Analyze
• Secondary: Clear

Validation
• If unsupported format: “Only JPG, JPEG, PNG are supported in this version.”
• If too many: “Max 10 files per batch.”
• If too large: “Max 15 MB per file.”

⸻

1.3 Results page: /images/results/:id (or same view)

Design principle: calm report first, progressive disclosure.

Header
• Left: file name + “Image metadata report”
• Right actions:
• Download JSON
• Copy summary
• Optional: Analyze next file (if batch)

Do not show hashes in the header.

Global controls
• Intent tabs: Privacy | Authenticity | Photography | Evidence | Raw
• Density toggle: Normal | Advanced (default Normal)

Left sidebar (optional but useful)
• Preview thumbnail
• Quick facts (non-scary):
• Capture time (if present)
• Location: embedded or not embedded
• Device: make/model
• Overlay text: not checked / extracted
• Trust chip: “Data retention: …” only if truthful

⸻

2. Results content spec

2.1 Highlights card (always top)

Goal: 3 to 7 bullets, plain language, minimal fear.

Each bullet has:
• Text
• Impact chip: Privacy | Authenticity | Workflow | None
• Confidence: High | Med | Low

Include one “Limits” line:
• “Metadata can be missing or stripped. Overlay text is part of pixels, not embedded tags.”

Highlights generation rules (images-only)
• Capture time:
• If EXIF DateTimeOriginal exists -> show it (High)
• Else -> “No embedded capture time found (common after sharing apps).” (High)
• Location:
• If EXIF GPS exists -> “Location embedded in this file.” (High)
• Else -> “Location not embedded (EXIF).” (High)
• Device info:
• If Make/Model exists -> show (High)
• Else -> “No device info found.” (High)
• Overlay OCR:
• If OCR available and not run -> “This image may contain overlay text (GPS camera apps). Run OCR to check.” (Med)
• If OCR extracted -> show parsed location/time as “from overlay text” (Med/High based on confidence)
• Hashes:
• If computed -> “Hashes computed (SHA256 available).” (High)

⸻

2.2 Intent tabs: what each shows

Privacy tab (default for most users)

Sections, in this order: 1. Sharing risks

    •	Location:
    •	Embedded GPS: present or not embedded
    •	If present: “If sharing publicly, consider removing location metadata.”
    •	Device identifiers:
    •	Make/Model present
    •	Serial numbers only if actually present and label carefully
    •	Overlay text (pixels):
    •	OverlayTextCard (see below)

    2.	What to do next

    •	“How to remove metadata” (link or inline instructions)
    •	“Download JSON” button repeated here
    •	Optional: “Create a cleaned copy” only if you can do it

Default state: calm, no jargon, limited rows.

Authenticity tab

Purpose: signals, not verdicts.

Sections: 1. Authenticity signals

    •	“No authenticity proof found (common)” if nothing present
    •	If XMP edit software present: “Editing software metadata present: …”
    •	If metadata stripped signals: “Metadata appears stripped (common on social platforms).”

    2.	Fingerprints

    •	Perceptual hashes (pHash etc) if available
    •	Basic file properties

Copy guardrail:
• Never say “fake” or “tampered” without strong evidence.
• Say “signals” and “inconclusive” when needed.

Photography tab

Show camera-centric details with friendly labels:
• Camera: make/model
• Exposure triangle: ISO, f-number, shutter speed
• Lens info if present
• White balance, flash
• ICC profile presence
• Thumbnail present

Evidence tab

For legal/forensic minded users, but still calm.
• Hashes (MD5/SHA1/SHA256)
• File system timestamps labeled “on this computer”
• “Report details”: tool version, extraction time, processing ms

Raw tab (advanced, opt-in)
• Explorer tree view
• Full JSON viewer
• Search within keys
• “Copy JSON” and “Download JSON”

Raw is where EXIF/IPTC/XMP names can exist. Not in Normal mode elsewhere.

⸻

3. Overlay OCR spec (critical for GPS Map Camera)

3.1 OverlayTextCard states
• Not checked:
• Text: “Some apps burn location and time into the image itself. This is not embedded metadata.”
• Button: Run OCR
• Running:
• Spinner + “Extracting overlay text…”
• Done:
• Show extracted text and parsed fields:
• Address
• Lat/Long
• Plus code
• Date/time
• Direction
• Weather fields (temp, humidity, altitude, speed)
• Each group shows confidence (Low/Med/High)
• Failed:
• “Could not extract overlay text.”
• Retry button
• Optional reason: “low contrast” etc

3.2 Rules
• Overlay-derived fields must be labeled “from overlay text”.
• Embedded GPS remains “not embedded” even after OCR finds coordinates.
• If OCR confidence is low, show “may be inaccurate”.

⸻

4. Paywall and pricing UI

You want PMF signal with minimal friction.

4.1 Trial model
• Trial: 3 files total (or 3/day). Pick one and be consistent.
• No account required for trial.

4.2 Credits model
• Suggestion: $1 for 20 files (simple impulse buy)
• Show remaining credits in header on upload and results:
• “Credits: 12 files left”
• If out of credits:
• show a single purchase modal

4.3 Purchase modal
• Title: “Buy credits”
• Options:
• $1 for 20 files
• Optional: $3 for 100 files (value tier)
• Show what they get:
• “Analyze up to N images”
• “Export JSON”
• “Overlay OCR”
• No fake scarcity. No “locked secrets”.

4.4 Locking behavior

For images-only launch, keep locking minimal:
• Trial users can see Highlights and Privacy basics.
• If you must gate:
• Gate Raw tab
• Gate bulk export
• Gate full field tables
But always keep enough visible to create an aha.

Use one pattern only:
• “Available on credits” with:
• “Unlock +N additional fields for this file”
• 3 real examples that would unlock

⸻

5. States and error handling

5.1 Processing states (truthful)

Per file:
• Uploading
• Extracting metadata
• Normalizing
• Ready

Do not show “Advanced analysis not run” in a scary way. Put it under Research only.

5.2 Failure states
• Unsupported file: explain allowed formats
• Too big: show limit
• OCR failed: retry
• Extraction failed: “Could not read metadata from this image.” Provide download of basic file summary anyway.

⸻

6. Information architecture rules

6.1 Normal mode rules
• Show meaning groups
• Show at most 6 sections visible without scrolling
• No standards names as section headers
• No long tables by default

6.2 Advanced mode rules
• Standards labels become visible as secondary tags
• “Show all fields” expands to tables
• Raw tab still exists and is most detailed

⸻

7. Analytics instrumentation for PMF

Minimum events:
• images_landing_viewed
• upload_files_selected (count, total_size_bucket)
• analysis_started (count)
• analysis_completed (success_count, fail_count)
• results_viewed (default_intent, mode)
• intent_changed
• mode_toggled
• ocr_started, ocr_completed (success/fail, confidence_bucket)
• export_json_clicked
• credits_modal_viewed
• credits_purchase_completed
• repeat_user_7d (if you can track)

PMF proxy metrics:
• % reaching results
• time-to-first-value (highlights rendered)
• OCR usage rate on GPS overlay-like images
• credit purchase conversion
• repeat usage

⸻

8. Acceptance criteria for launch

For a GPS Map Camera JPEG with overlay and no EXIF GPS:
• Highlights show capture time, “location not embedded”, OCR prompt
• Privacy tab defaults, Normal mode
• OCR results label “from overlay text”
• No “Not Found”, “LOCKED”, “FORENSIC”, “VERIFIED”
• Download JSON always works
• Purchase flow is one modal and returns to results

⸻

If you share your actual current routes and component filenames (even just the top-level results component name), I can turn this into a repo task list with file-level implementation notes and PR slicing, aligned with your agents setup.

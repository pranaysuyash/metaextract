# Interactive Metadata Visualization Components

## Overview

This document describes the new visualization components that transform metadata from simple key-value lists into interactive, visual experiences.

## Components

### 1. DateTimeTimeline (`client/src/components/viz/DateTimeTimeline.tsx`)

**Purpose:** Visualize all date/time metadata on a single timeline

**Features:**

- **Multi-source dates:** Shows capture date, create date, modify date from EXIF and filesystem
- **Anomaly detection:** Highlights date inconsistencies (e.g., >24h gap between capture and file creation)
- **Visual timeline:** Vertical timeline with color-coded icons
- **Human-readable:** Shows "time since" (e.g., "3 days ago")
- **Source indicators:** Shows where each date came from (EXIF, filesystem, email)

**Data Types Handled:**

- EXIF: `DateTimeOriginal`, `CreateDate`, `ModifyDate`
- Filesystem: `FileCreateDate`, `FileModifyDate`, `FileAccessDate`
- Email: `email_datetime_parsed`, `email_timestamp`

**Usage Example:**

```tsx
import { DateTimeTimeline } from '@/components/viz';

<DateTimeTimeline metadata={metadata} fileType="image" />;
```

---

### 2. CameraSettingsRadar (`client/src/components/viz/CameraSettingsRadar.tsx`)

**Purpose:** Radar/spider chart showing camera settings at a glance

**Features:**

- **6-axis radar chart:** ISO, Aperture, Shutter, Focal Length, White Balance, Flash
- **Normalized values:** All settings scaled 0-100% for comparison
- **Tooltips:** Hover for actual values
- **Summary cards:** Numeric display below chart
- **Exif parsing:** Handles rational numbers (e.g., "1/120" exposure)

**Data Types Handled:**

- ISO (logarithmic scale)
- Aperture (f-number, inverse scale)
- Exposure time (fractional seconds)
- Focal length (mm)
- White balance (color temperature in K)
- Flash fired (boolean)

**Usage Example:**

```tsx
import { CameraSettingsRadar } from '@/components/viz';

<CameraSettingsRadar exif={exifData} image={imageData} />;
```

---

### 3. EmailThreadViz (`client/src/components/viz/EmailThreadViz.tsx`)

**Purpose:** Interactive visualization of email metadata

**Features:**

- **Thread structure:** Shows reply/forward relationships with visual indentation
- **Participant cards:** Avatar-style display for From/To/CC
- **Security dashboard:** DKIM, SPF, spam status with visual indicators
- **Attachment list:** File names with sizes
- **Priority badge:** High/Normal/Low priority display
- **Date display:** Formatted email date

**Data Types Handled:**

- Headers: From, To, CC, BCC, Subject, Message-ID
- Threading: In-Reply-To, References, Thread-Level
- Security: DKIM, SPF, Authentication-Results
- Content: Attachments, Content-Type

**Usage Example:**

```tsx
import { EmailThreadViz } from '@/components/viz';

<EmailThreadViz email={emailMetadata} />;
```

---

## File Type Specialization

### Images

| Visualization       | Key Data                                        |
| ------------------- | ----------------------------------------------- |
| DateTimeTimeline    | `DateTimeOriginal`, `CreateDate`, `ModifyDate`  |
| CameraSettingsRadar | `ISO`, `FNumber`, `ExposureTime`, `FocalLength` |

### Videos

| Visualization        | Key Data                         |
| -------------------- | -------------------------------- |
| DateTimeTimeline     | `DateTimeOriginal`, `CreateDate` |
| (Future) WaveformViz | Audio track visualization        |

### Emails

| Visualization    | Key Data                                 |
| ---------------- | ---------------------------------------- |
| EmailThreadViz   | All email headers, attachments, security |
| DateTimeTimeline | `email_timestamp`, `email_date`          |

### Documents

| Visualization    | Key Data                                      |
| ---------------- | --------------------------------------------- |
| DateTimeTimeline | `creation_date`, `mod_date`, `FileModifyDate` |

---

## Design Principles

1. **Progressive Disclosure:** Show key info upfront, details on hover
2. **Visual Hierarchy:** Use color, size, position to indicate importance
3. **Contextual Labels:** Explain what each field means (e.g., "ISO = Light sensitivity")
4. **Anomaly Detection:** Highlight suspicious or notable patterns
5. **Cross-Reference:** Link related fields across categories
6. **Human-Readable:** Convert technical values to understandable terms

---

## Future Enhancements

1. **LocationMapViz:** Embedded map with photo markers using Leaflet/Mapbox
2. **AudioWaveformViz:** Waveform display for audio files
3. **MetadataComparison:** Side-by-side comparison of multiple files
4. **ColorHistogramViz:** RGB histogram for images
5. **Medical3DViz:** 3D volume rendering for DICOM
6. **TimelineCluster:** Calendar heatmap for photo collections
7. **GPSPathViz:** Track visualization for GPS data
8. **ForensicTimeline:** Chain of custody timeline

---

## Integration

Import all visualizations:

```tsx
import {
  DateTimeTimeline,
  CameraSettingsRadar,
  EmailThreadViz,
} from '@/components/viz';
```

The `viz` directory also exports an index for easy importing.

import { useMemo } from 'react';
import { MvpMetadata, GpsCoordinates, FormatHint, Highlight } from '../lib/types';
import {
  getGpsCoords,
  parseOverlayGps,
  parseWhatsappFilenameDate,
  parseExifDate,
  hasValue,
} from '../utils/imageMetadataTransformers';

interface UseImageMetadataProcessingResult {
  gpsCoords: GpsCoordinates | null;
  overlayGps: GpsCoordinates | null;
  hasGps: boolean;
  embeddedGpsState: 'embedded' | 'overlay' | 'none';
  captureDateFromExif: Date | null;
  filenameDate: Date | null;
  captureDateLabel: string;
  captureDateValue: string | null;
  localModifiedValue: string | null;
  burnedTimestamp: string | null;
  hashSha256: string | null;
  hashMd5: string | null;
  fieldsExtracted: number | null;
  processingMs: number | null;
  software: string | null;
  formatHint: FormatHint | null;
  highlights: Highlight[];
  orderedHighlights: Highlight[];
  gpsMapUrl: string;
  dimensionsValue: string | null;
  megapixelsValue: string | null;
  colorSpaceValue: string | null;
  exifEntries: [string, unknown][];
  lockedGroups: Array<{ key: string; label: string; count: number }>;
  lockedTotal: number;
}

export const useImageMetadataProcessing = (
  metadata: MvpMetadata,
  purpose: string | null
): UseImageMetadataProcessingResult => {
  return useMemo(() => {
    const gpsCoords = getGpsCoords(metadata.gps);
    const overlayGps = parseOverlayGps(metadata.burned_metadata);
    const hasGps = !!gpsCoords;
    const embeddedGpsState = hasGps ? 'embedded' : overlayGps ? 'overlay' : 'none';
    
    const filenameDate = parseWhatsappFilenameDate(metadata.filename);
    const captureDateFromExif = parseExifDate(
      (metadata.exif?.DateTimeOriginal as string | null | undefined) ||
        (metadata.exif?.CreateDate as string | null | undefined)
    );
    const captureDateLabel = captureDateFromExif
      ? 'CAPTURE DATE'
      : filenameDate
      ? 'FILENAME DATE'
      : 'CAPTURE DATE';
    const captureDateValue = captureDateFromExif
      ? captureDateFromExif.toISOString()
      : filenameDate
      ? filenameDate.toISOString()
      : null;
    const localModifiedValue = metadata.client_last_modified_iso || null;

    const burnedTimestamp = metadata.burned_metadata?.parsed_data?.timestamp || null;
    const hashSha256 = metadata.hashes?.sha256 || metadata.file_integrity?.sha256 || null;
    const hashMd5 = metadata.hashes?.md5 || metadata.file_integrity?.md5 || null;
    const fieldsExtracted = metadata.fields_extracted ?? null;
    const processingMs = metadata.processing_ms ?? null;
    const software = (metadata.exif?.Software as string | undefined) || null;

    const formatHint = getFormatHint(metadata.mime_type, metadata.filename);

    const highlights: Highlight[] = [];
    if (captureDateValue) {
      highlights.push({
        text: `Capture time found (${captureDateLabel === 'FILENAME DATE' ? 'from filename' : 'from EXIF'}).`,
        intent: 'Photography',
        impact: 'Workflow',
        confidence: captureDateLabel === 'FILENAME DATE' ? 'Medium' : 'High',
        target: { tab: 'privacy', anchorId: 'section-timestamps' },
      });
    } else {
      highlights.push({
        text: 'Capture time not present in this file (common after sharing apps).',
        intent: 'Photography',
        impact: 'Workflow',
        confidence: 'Medium',
        target: { tab: 'privacy', anchorId: 'section-timestamps' },
      });
    }
    if (embeddedGpsState === 'embedded') {
      highlights.push({
        text: 'Location is embedded in EXIF.',
        intent: 'Privacy',
        impact: 'Privacy',
        confidence: 'High',
        target: { tab: 'privacy', anchorId: 'section-location' },
      });
    } else if (embeddedGpsState === 'overlay') {
      highlights.push({
        text: 'Location not embedded in EXIF, but found in overlay text (pixels).',
        intent: 'Privacy',
        impact: 'Privacy',
        confidence: 'Medium',
        target: { tab: 'privacy', anchorId: 'section-location' },
      });
    } else {
      highlights.push({
        text: 'Location not present in this file.',
        intent: 'Privacy',
        impact: 'Privacy',
        confidence: 'High',
        target: { tab: 'privacy', anchorId: 'section-location' },
      });
    }
    if (hasValue(metadata.exif?.Make) || hasValue(metadata.exif?.Model)) {
      highlights.push({
        text: `Device detected: ${[metadata.exif?.Make, metadata.exif?.Model].filter(Boolean).join(' ')}`,
        intent: 'Photography',
        impact: 'Privacy',
        confidence: 'High',
        target: { tab: 'privacy', anchorId: 'section-device' },
      });
    }
    if (hasValue(software)) {
      highlights.push({
        text: `Software tag present: ${software}`,
        intent: 'Authenticity',
        impact: 'Authenticity',
        confidence: 'High',
      });
    } else {
      highlights.push({
        text: 'No editing software tag present (inconclusive).',
        intent: 'Authenticity',
        impact: 'Authenticity',
        confidence: 'Low',
      });
    }
    if (hasValue(hashSha256)) {
      highlights.push({
        text: 'SHA-256 hash computed for integrity.',
        intent: 'Authenticity',
        impact: 'Authenticity',
        confidence: 'High',
      });
    }

    const preferredIntent =
      purpose === 'authenticity'
        ? 'Authenticity'
        : purpose === 'photography'
        ? 'Photography'
        : 'Privacy';

    const orderedHighlights = [...highlights].sort((a, b) => {
      const aScore = a.intent === preferredIntent ? 1 : 0;
      const bScore = b.intent === preferredIntent ? 1 : 0;
      return bScore - aScore;
    });

    const gpsMapUrl = gpsCoords
      ? ((metadata.gps as Record<string, unknown> | null)?.google_maps_url as string | undefined) ||
        `https://maps.google.com/?q=${gpsCoords.latitude},${gpsCoords.longitude}`
      : overlayGps
      ? overlayGps.google_maps_url ||
        `https://maps.google.com/?q=${overlayGps.latitude},${overlayGps.longitude}`
      : '';

    const imageWidth = metadata.exif?.ImageWidth;
    const imageHeight = metadata.exif?.ImageHeight ?? metadata.exif?.ImageLength;
    const dimensionsValue =
      hasValue(imageWidth) && hasValue(imageHeight)
        ? `${String(imageWidth)} × ${String(imageHeight)}`
        : null;
    const megapixelsValue = hasValue(metadata.calculated?.megapixels)
      ? String(metadata.calculated?.megapixels)
      : null;
    const colorSpaceNumeric = Number(metadata.exif?.ColorSpace);
    const colorSpaceValue =
      Number.isFinite(colorSpaceNumeric) && colorSpaceNumeric === 1
        ? 'sRGB'
        : hasValue(metadata.exif?.ColorSpace)
        ? String(metadata.exif?.ColorSpace)
        : null;

    const exifEntries = Object.entries(metadata.exif || {}).filter(([, v]) =>
      hasValue(v)
    );

    const registrySummary = metadata.registry_summary?.image as
      | {
          exif?: number;
          iptc?: number;
          xmp?: number;
          mobile?: number;
          perceptual_hashes?: number;
        }
      | undefined;
    const lockedGroups = [
      {
        key: 'exif',
        label: 'Full EXIF fields',
        count: registrySummary?.exif ?? 0,
      },
      {
        key: 'iptc',
        label: 'IPTC (author/rights)',
        count: registrySummary?.iptc ?? 0,
      },
      {
        key: 'xmp',
        label: 'XMP (edit history)',
        count: registrySummary?.xmp ?? 0,
      },
    ].filter(group => group.count > 0);
    const lockedTotal = lockedGroups.reduce((sum, group) => sum + group.count, 0);

    return {
      gpsCoords,
      overlayGps,
      hasGps,
      embeddedGpsState,
      captureDateFromExif,
      filenameDate,
      captureDateLabel,
      captureDateValue,
      localModifiedValue,
      burnedTimestamp,
      hashSha256,
      hashMd5,
      fieldsExtracted,
      processingMs,
      software,
      formatHint,
      highlights,
      orderedHighlights,
      gpsMapUrl,
      dimensionsValue,
      megapixelsValue,
      colorSpaceValue,
      exifEntries,
      lockedGroups,
      lockedTotal,
    };
  }, [metadata, purpose]);
};

const getFormatHint = (mimeType: string, filename: string): FormatHint | null => {
  const normalizedMime = (mimeType || '').toLowerCase();
  const filenameLower = (filename || '').toLowerCase();
  if (normalizedMime.includes('heic') || normalizedMime.includes('heif')) {
    return {
      title: 'HEIC photo detected',
      body: 'HEIC photos (common on iPhones) usually include rich metadata such as capture settings and device details.',
      tone: 'emerald',
    };
  }
  if (normalizedMime.includes('webp')) {
    return {
      title: 'WebP image detected',
      body: 'WebP metadata support varies by source. Some uploads may only include basic file details.',
      tone: 'amber',
    };
  }
  if (normalizedMime.includes('png')) {
    const screenshotHint =
      filenameLower.includes('screenshot') ||
      filenameLower.includes('screen shot');
    return {
      title: screenshotHint ? 'Screenshot detected' : 'PNG image detected',
      body: screenshotHint
        ? 'Screenshots often contain minimal metadata. For richer data, try the original photo.'
        : 'PNG files (especially graphics) often contain minimal metadata compared to camera photos.',
      tone: 'amber',
    };
  }
  if (normalizedMime.includes('jpeg') || normalizedMime.includes('jpg')) {
    return {
      title: 'JPEG photo detected',
      body: 'JPEG photos usually include camera metadata such as device, timestamps, and settings.',
      tone: 'emerald',
    };
  }
  return null;
};
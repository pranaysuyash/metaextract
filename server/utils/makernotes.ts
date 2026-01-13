/**
 * MakerNotes Enrichment Module
 *
 * Extracts high-value MakerNotes tags from popular camera manufacturers.
 * This is the 20% of MakerNotes that creates 80% perceived depth:
 * - Apple HEIC: Focus, Portrait, HDR modes
 * - Canon: Lens info, shooting mode, AF points
 * - Nikon: Lens serial, focus mode, flash settings
 * - Sony: Lens info, creative style, focus area
 */

import type { FrontendMetadataResponse } from './extraction-helpers';

export interface MakernoteDisplayField {
  label: string;
  value: string;
  description?: string;
}

export interface MakerNotesHighlight {
  text: string;
  category: string;
}

export interface MakerNotesEnrichment {
  manufacturer: string;
  model: string;
  deviceSpecific: Record<string, unknown>;
  enrichmentLevel: 'full' | 'partial' | 'none';
}

/**
 * Common MakerNotes tags by manufacturer
 */
const MAKER_NOTES_TAGS = {
  apple: [
    'FocusDistance',
    'LensModel',
    'LensMake',
    'FocalLength',
    'DigitalZoomRatio',
    'SceneCaptureType',
    'PortraitEnhancementMode',
    'HDRMode',
    'BurstMode',
    'LivePhoto',
    'ProcessingSoftware',
    'HostDeviceInfo',
  ],
  canon: [
    'LensModel',
    'LensSerialNumber',
    'LensType',
    'FocalLength',
    'FocalLengthIn35mmFilm',
    'AFPointsUsed',
    'AFPointsUsedArea',
    'MeteringMode',
    'ExposureProgram',
    'ShutterSpeedValue',
    'ApertureValue',
    'ISO',
    'WhiteBalance',
    'Flash',
    'DriveMode',
    'FocusMode',
    'Quality',
    'CanonImageType',
    'OwnerName',
    'CameraSerialNumber',
  ],
  nikon: [
    'LensModel',
    'LensSerialNumber',
    'LensFStops',
    'FocalLength',
    'FocalLengthIn35mmFilm',
    'FocusMode',
    'AFMode',
    'AFAreaMode',
    'AFPoints',
    'FlashMode',
    'FlashExposureComp',
    'ExposureMode',
    'ExposureProgram',
    'WhiteBalance',
    'ISO',
    'ShutterSpeed',
    'Aperture',
    'MeteringMode',
    'FocusPoint',
    'ActiveDLighting',
    'HueAdjustment',
    'PictureControl',
    'VignetteControl',
    'AutoDistortionControl',
  ],
  sony: [
    'LensModel',
    'LensSerialNumber',
    'LensID',
    'LensSpec',
    'FocalLength',
    'FocalLengthIn35mmFilm',
    'FocusMode',
    'FocusArea',
    'AFPointsSelected',
    'MeteringMode',
    'ExposureMode',
    'ExposureProgram',
    'WhiteBalance',
    'ISO',
    'ShutterSpeed',
    'Aperture',
    'CreativeStyle',
    'ColorTemperature',
    'PictureEffect',
    'ColorMode',
    'Quality',
    'LensMount',
    'BodySerialNumber',
    'ImageStabilization',
  ],
};

/**
 * Detect manufacturer from Make/Model fields
 */
function detectManufacturer(metadata: FrontendMetadataResponse): string | null {
  const make = ((metadata.exif?.Make as string) || '').toLowerCase();
  const model = ((metadata.exif?.Model as string) || '').toLowerCase();

  if (
    make.includes('apple') ||
    model.includes('iphone') ||
    model.includes('ipad')
  ) {
    return 'apple';
  }
  if (make.includes('canon')) {
    return 'canon';
  }
  if (make.includes('nikon')) {
    return 'nikon';
  }
  if (make.includes('sony')) {
    return 'sony';
  }
  if (make.includes('fuji') || model.includes('x-')) {
    return 'fuji';
  }
  if (make.includes('olympus') || make.includes('om system')) {
    return 'olympus';
  }
  if (make.includes('panasonic') || model.includes('lumix')) {
    return 'panasonic';
  }
  if (make.includes('samsung')) {
    return 'samsung';
  }

  return null;
}

/**
 * Check if MakerNotes is present and extractable
 */
export function hasMakerNotes(metadata: FrontendMetadataResponse): boolean {
  return !!(
    metadata.exif &&
    typeof metadata.exif === 'object' &&
    Object.keys(metadata.exif).length > 0
  );
}

/**
 * Enrich metadata with MakerNotes-specific fields
 */
export function enrichMakerNotes(
  metadata: FrontendMetadataResponse
): MakerNotesEnrichment {
  const manufacturer = detectManufacturer(metadata);
  const model =
    (metadata.exif?.Model as string) ||
    (metadata.exif?.Make as string) ||
    'Unknown';

  if (!manufacturer) {
    return {
      manufacturer: 'Unknown',
      model,
      deviceSpecific: {},
      enrichmentLevel: 'none',
    };
  }

  const deviceSpecific: Record<string, unknown> = {};
  const exif = metadata.exif as Record<string, unknown>;

  const tags =
    MAKER_NOTES_TAGS[manufacturer as keyof typeof MAKER_NOTES_TAGS] || [];

  for (const tag of tags) {
    if (exif[tag] !== undefined && exif[tag] !== null) {
      deviceSpecific[tag] = exif[tag];
    }
  }

  const enrichmentLevel: 'full' | 'partial' | 'none' =
    tags.length > 0 && Object.keys(deviceSpecific).length > 0
      ? Object.keys(deviceSpecific).length >= tags.length * 0.5
        ? 'full'
        : 'partial'
      : 'none';

  return {
    manufacturer: manufacturer.charAt(0).toUpperCase() + manufacturer.slice(1),
    model,
    deviceSpecific,
    enrichmentLevel,
  };
}

/**
 * Get human-readable description for common MakerNotes tags
 */
export function getMakerNotesDescription(
  manufacturer: string,
  tag: string,
  value: unknown
): string | null {
  const descriptions: Record<string, Record<string, string>> = {
    apple: {
      PortraitEnhancementMode: 'Portrait mode enhancement settings',
      HDRMode: 'High Dynamic Range capture mode',
      BurstMode: 'Continuous shooting mode',
      LivePhoto: 'Live Photo capture status',
      FocusDistance: 'Distance to subject at capture time',
    },
    canon: {
      AFPointsUsed: 'Autofocus points used in capture',
      LensSerialNumber: 'Unique lens identifier',
      LensType: 'Lens type and characteristics',
      Quality: 'Image quality settings (RAW, JPEG, etc.)',
      DriveMode: 'Drive mode (single, continuous, self-timer)',
    },
    nikon: {
      PictureControl: 'Picture control profile used',
      ActiveDLighting: 'Active D-Lighting (dynamic range enhancement)',
      AutoDistortionControl: 'Automatic distortion correction',
      FocusPoint: 'Selected focus point position',
      LensFStops: 'Lens aperture stops',
    },
    sony: {
      CreativeStyle: 'Creative style applied',
      PictureEffect: 'Picture effect filter used',
      ImageStabilization: 'SteadyShot/image stabilization',
      ColorTemperature: 'Color temperature setting (Kelvin)',
      ColorMode: 'Color mode/saturation setting',
    },
  };

  return descriptions[manufacturer]?.[tag] || null;
}

/**
 * Format MakerNotes for display
 */
export function formatMakerNotesForDisplay(
  enrichment: MakerNotesEnrichment
): Array<{ label: string; value: string; description?: string }> {
  if (enrichment.enrichmentLevel === 'none') {
    return [];
  }

  const items: Array<{ label: string; value: string; description?: string }> =
    [];

  for (const [key, value] of Object.entries(enrichment.deviceSpecific)) {
    if (value === null || value === undefined || value === '') {
      continue;
    }

    const description = getMakerNotesDescription(
      enrichment.manufacturer.toLowerCase(),
      key,
      value
    );

    items.push({
      label: formatLabel(key),
      value: formatValue(value),
      description: description ?? undefined,
    });
  }

  return items;
}

/**
 * Format camelCase to Title Case
 */
function formatLabel(str: string): string {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, s => s.toUpperCase())
    .trim();
}

/**
 * Format value for display
 */
function formatValue(value: unknown): string {
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number') {
    return String(value);
  }
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  return String(value);
}

/**
 * Get suggested highlights based on MakerNotes
 */
export function getMakerNotesHighlights(
  enrichment: MakerNotesEnrichment
): Array<{ text: string; category: string }> {
  const highlights: Array<{ text: string; category: string }> = [];
  const deviceSpecific = enrichment.deviceSpecific;

  if (enrichment.manufacturer === 'Apple') {
    if (deviceSpecific.PortraitEnhancementMode) {
      highlights.push({
        text: 'Portrait mode detected',
        category: 'capture',
      });
    }
    if (deviceSpecific.HDRMode) {
      highlights.push({
        text: 'HDR capture enabled',
        category: 'capture',
      });
    }
    if (deviceSpecific.LivePhoto) {
      highlights.push({
        text: 'Live Photo captured',
        category: 'capture',
      });
    }
  }

  if (enrichment.manufacturer === 'Canon') {
    if (deviceSpecific.Quality) {
      highlights.push({
        text: `Quality: ${deviceSpecific.Quality}`,
        category: 'settings',
      });
    }
    if (deviceSpecific.AFPointsUsed) {
      highlights.push({
        text: `${deviceSpecific.AFPointsUsed} AF points used`,
        category: 'focus',
      });
    }
    if (deviceSpecific.LensSerialNumber) {
      highlights.push({
        text: 'Lens serial recorded',
        category: 'device',
      });
    }
  }

  if (enrichment.manufacturer === 'Nikon') {
    if (deviceSpecific.PictureControl) {
      highlights.push({
        text: `Picture Control: ${deviceSpecific.PictureControl}`,
        category: 'settings',
      });
    }
    if (deviceSpecific.ActiveDLighting) {
      highlights.push({
        text: `Active D-Lighting: ${deviceSpecific.ActiveDLighting}`,
        category: 'capture',
      });
    }
    if (deviceSpecific.LensSerialNumber) {
      highlights.push({
        text: 'Lens serial recorded',
        category: 'device',
      });
    }
  }

  if (enrichment.manufacturer === 'Sony') {
    if (deviceSpecific.CreativeStyle) {
      highlights.push({
        text: `Creative Style: ${deviceSpecific.CreativeStyle}`,
        category: 'settings',
      });
    }
    if (deviceSpecific.PictureEffect) {
      highlights.push({
        text: `Effect: ${deviceSpecific.PictureEffect}`,
        category: 'capture',
      });
    }
    if (deviceSpecific.ImageStabilization) {
      highlights.push({
        text: 'SteadyShot active',
        category: 'capture',
      });
    }
  }

  return highlights;
}

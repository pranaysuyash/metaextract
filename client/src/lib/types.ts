// Shared client-side types for Images MVP

export type TabValue = 'privacy' | 'authenticity' | 'photography' | 'raw';
export type PurposeValue =
  | 'privacy'
  | 'authenticity'
  | 'photography'
  | 'explore';
export type DensityMode = 'normal' | 'advanced';

export interface GpsCoordinates {
  latitude: number;
  longitude: number;
  formatted?: string;
  google_maps_url?: string;
}

export interface HighlightTarget {
  tab: TabValue;
  anchorId: string;
}

export interface Highlight {
  text: string;
  intent: 'Privacy' | 'Authenticity' | 'Photography';
  impact: string;
  confidence: 'Low' | 'Medium' | 'High';
  target?: HighlightTarget;
}

export interface FormatHint {
  title: string;
  body: string;
  tone: 'emerald' | 'amber';
}

export interface DetailEntry {
  path: string;
  valuePreview: string;
  value: unknown;
}

export interface MvpMetadata {
  filename: string;
  filesize?: string | number | null;
  filetype?: string | null;
  mime_type: string;
  exif?: Record<string, unknown> | null;
  gps?: Record<string, unknown> | null;
  burned_metadata?: {
    parsed_data?: {
      gps?: { latitude: number; longitude: number; google_maps_url?: string };
      timestamp?: string;
      plus_code?: string;
      address?: string;
    };
    extracted_text?: string;
  } | null;
  hashes?: { sha256?: string | null; md5?: string | null } | null;
  file_integrity?: { sha256?: string | null; md5?: string | null } | null;
  calculated?: { megapixels?: number | null } | null;
  client_last_modified_iso?: string | null;
  fields_extracted?: number | null;
  processing_ms?: number | null;
  registry_summary?: {
    image?: {
      exif?: number;
      iptc?: number;
      xmp?: number;
      mobile?: number;
      perceptual_hashes?: number;
    };
    makerNotes?: { present?: boolean } | null;
  } | null;
  makernote?: { enriched?: { manufacturer?: string; deviceSpecific?: Record<string, unknown> } } | null;
  quality_metrics?: { confidence_score?: number; extraction_completeness?: number; format_support_level?: string } | null;
  processing_insights?: { total_fields_extracted?: number; processing_ms?: number } | null;
  access?: {
    mode?: 'device_free' | 'trial_limited' | 'paid';
    free_used?: number;
    granted?: boolean;
    trial_granted?: boolean;
  } | null;
  _limited?: boolean;
  _trial_limited?: boolean;
}

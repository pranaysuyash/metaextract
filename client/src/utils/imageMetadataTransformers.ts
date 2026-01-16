import { MvpMetadata, DetailEntry, GpsCoordinates } from '../lib/types';

export const formatDate = (
  dateStr?: string,
  emptyMessage = 'Not present in this file'
): string => {
  if (!dateStr) return emptyMessage;
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return dateStr;
  }
};

export const hasValue = (value: unknown): boolean => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return Number.isFinite(value);
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return (
      trimmed.length > 0 &&
      trimmed.toLowerCase() !== 'n/a' &&
      trimmed.toLowerCase() !== 'unknown'
    );
  }
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
};

export const previewValue = (value: unknown): string => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string')
    return value.length > 180 ? `${value.slice(0, 180)}…` : value;
  if (typeof value === 'number' || typeof value === 'boolean')
    return String(value);
  try {
    const text = JSON.stringify(value);
    return text.length > 180 ? `${text.slice(0, 180)}…` : text;
  } catch {
    return String(value);
  }
};

export const getGpsCoords = (gps: Record<string, unknown> | null | undefined): GpsCoordinates | null => {
  if (!gps || typeof gps !== 'object') return null;
  const record = gps as Record<string, unknown>;
  const latRaw =
    record.latitude ??
    record.lat ??
    record.GPSLatitude ??
    record.gps_latitude ??
    record.Latitude;
  const lonRaw =
    record.longitude ??
    record.lon ??
    record.lng ??
    record.GPSLongitude ??
    record.gps_longitude ??
    record.Longitude;
  const lat =
    typeof latRaw === 'number' ? latRaw : parseFloat(String(latRaw));
  const lon =
    typeof lonRaw === 'number' ? lonRaw : parseFloat(String(lonRaw));
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  return { latitude: lat, longitude: lon };
};

export const parseOverlayGps = (burned?: MvpMetadata['burned_metadata']): GpsCoordinates | null => {
  const raw = burned?.parsed_data?.gps;
  if (!raw) return null;
  const lat =
    typeof raw.latitude === 'number'
      ? raw.latitude
      : parseFloat(String(raw.latitude));
  const lon =
    typeof raw.longitude === 'number'
      ? raw.longitude
      : parseFloat(String(raw.longitude));
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
  return {
    latitude: lat,
    longitude: lon,
    google_maps_url: raw.google_maps_url,
  };
};

export const parseWhatsappFilenameDate = (name?: string): Date | null => {
  if (!name) return null;
  const match = name.match(
    /WhatsApp Image (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})\.(\d{2})/i
  );
  if (!match) return null;
  const [, year, month, day, hour, minute, second] = match;
  return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
};

export const parseExifDate = (value?: string | null): Date | null => {
  if (!value) return null;
  // Handle EXIF format: YYYY:MM:DD HH:MM:SS
  const match = value.match(
    /(\d{4}):(\d{2}):(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/
  );
  if (match) {
    const [, y, m, d, hh, mm, ss] = match;
    return new Date(`${y}-${m}-${d}T${hh}:${mm}:${ss}`);
  }
  const dt = new Date(value);
  return Number.isNaN(dt.getTime()) ? null : dt;
};

export const collectDetailEntries = (
  obj: unknown,
  prefix = '',
  depth = 0,
  maxDepth = 4,
  out: DetailEntry[] = [],
  maxEntries = 200
): DetailEntry[] => {
  if (out.length >= maxEntries) return out;
  if (depth > maxDepth) return out;
  if (obj === null || obj === undefined) return out;
  if (typeof obj !== 'object') {
    if (!hasValue(obj)) return out;
    out.push({
      path: prefix || '(root)',
      valuePreview: previewValue(obj),
      value: obj,
    });
    return out;
  }
  if (Array.isArray(obj)) {
    if (!hasValue(obj)) return out;
    out.push({
      path: prefix || '(root)',
      valuePreview: previewValue(obj),
      value: obj,
    });
    return out;
  }
  const record = obj as Record<string, unknown>;
  for (const key of Object.keys(record)) {
    if (key.startsWith('_')) continue;
    if (key === 'access') continue;
    if (key === 'extracted_text') continue;
    const next = prefix ? `${prefix}.${key}` : key;
    const value = record[key];
    if (
      value !== null &&
      typeof value === 'object' &&
      !Array.isArray(value)
    ) {
      collectDetailEntries(value, next, depth + 1, maxDepth, out, maxEntries);
    } else {
      if (!hasValue(value)) continue;
      out.push({
        path: next,
        valuePreview: previewValue(value),
        value,
      });
    }
    if (out.length >= maxEntries) break;
  }
  return out;
};

export const collectPaths = (
  obj: unknown,
  prefix = '',
  depth = 0,
  out: DetailEntry[] = []
): DetailEntry[] => {
  if (out.length >= 500) return out;
  if (depth > 5) return out;
  if (obj === null || obj === undefined) return out;
  if (typeof obj !== 'object') {
    out.push({
      path: prefix || '(root)',
      valuePreview: previewValue(obj).slice(0, 140),
      value: obj,
    });
    return out;
  }
  if (Array.isArray(obj)) {
    const preview = previewValue(obj.slice(0, 5));
    out.push({
      path: prefix || '(root)',
      valuePreview: preview.slice(0, 140),
      value: obj,
    });
    return out;
  }
  const record = obj as Record<string, unknown>;
  for (const key of Object.keys(record)) {
    const next = prefix ? `${prefix}.${key}` : key;
    const value = record[key];
    if (
      value !== null &&
      typeof value === 'object' &&
      !Array.isArray(value)
    ) {
      collectPaths(value, next, depth + 1, out);
    } else if (Array.isArray(value)) {
      const preview = previewValue(value.slice(0, 5));
      out.push({
        path: next,
        valuePreview: preview.slice(0, 140),
        value,
      });
    } else {
      if (!hasValue(value)) continue;
      out.push({
        path: next,
        valuePreview: previewValue(value).slice(0, 140),
        value,
      });
    }
    if (out.length >= 500) break;
  }
  return out;
};
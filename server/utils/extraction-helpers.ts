import path from 'path';
import fs from 'fs/promises';
import { spawn } from 'child_process';
import * as fsSync from 'fs';
import { normalizeTier } from '@shared/tierConfig';
import type { AuthRequest } from '../auth';
import { isPathSafe } from '../security-utils';

// Get the server directory - resolve from project root
// During tests, use process.cwd() which is the project root
// During runtime, the app will be at the project root
const projectRoot = process.cwd();
const currentDirPath = path.join(projectRoot, 'server');

// Python executable: prefer project venv, fall back to system python3
const venvCandidates = [
  path.join(currentDirPath, '..', '..', '.venv', 'bin', 'python3'),
  path.join(currentDirPath, '..', '..', 'venv', 'bin', 'python3'),
  path.join(currentDirPath, '..', '..', '.venv', 'bin', 'python'),
  path.join(currentDirPath, '..', '..', 'venv', 'bin', 'python'),
];

export function findPythonExecutable(): string {
  if (process.env.PYTHON_EXECUTABLE && process.env.PYTHON_EXECUTABLE.length)
    return process.env.PYTHON_EXECUTABLE;

  for (const candidate of venvCandidates) {
    try {
      if (fsSync.existsSync(candidate)) return candidate;
    } catch {
      // ignore
    }
  }

  // Last resort: rely on system python3 in PATH
  return 'python3';
}

export const pythonExecutable = findPythonExecutable();

export const PYTHON_SCRIPT_PATH = path.join(
  currentDirPath,
  'extractor',
  'comprehensive_metadata_engine.py'
);

// ============================================================================
// Types
// ============================================================================

export interface PythonMetadataResponse {
  extraction_info: {
    timestamp: string;
    tier: string;
    engine_version: string;
    libraries: Record<string, boolean>;
    fields_extracted: number;
    locked_categories: number;
    processing_ms?: number;
  };
  file: {
    path: string;
    name: string;
    stem: string;
    extension: string;
    mime_type: string;
  };
  summary: Record<string, any>;
  filesystem: Record<string, any>;
  hashes: Record<string, any>;
  image: Record<string, any> | null;
  exif: Record<string, any> | null;
  gps: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  extended_attributes: Record<string, any> | null;
  calculated: Record<string, any>;
  forensic: Record<string, any>;
  makernote: Record<string, any> | null;
  iptc: Record<string, any> | null;
  xmp: Record<string, any> | null;
  normalized?: Record<string, any> | null;
  web_metadata?: Record<string, any> | null;
  social_media?: Record<string, any> | null;
  mobile_metadata?: Record<string, any> | null;
  forensic_security?: Record<string, any> | null;
  action_camera?: Record<string, any> | null;
  print_publishing?: Record<string, any> | null;
  workflow_dam?: Record<string, any> | null;
  audio_advanced?: Record<string, any> | null;
  video_advanced?: Record<string, any> | null;
  steganography_analysis?: Record<string, any> | null;
  manipulation_detection?: Record<string, any> | null;
  ai_detection?: Record<string, any> | null;
  timeline_analysis?: Record<string, any> | null;
  iptc_raw?: Record<string, any> | null;
  xmp_raw?: Record<string, any> | null;
  thumbnail?: Record<string, any> | null;
  perceptual_hashes?: Record<string, any> | null;
  locked_fields: string[];
  burned_metadata?: Record<string, any> | null;
  metadata_comparison?: Record<string, any> | null;
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  } | null;
  // Specialized Modules
  medical_imaging?: Record<string, any> | null;
  astronomical_data?: Record<string, any> | null;
  geospatial_analysis?: Record<string, any> | null;
  scientific_instruments?: Record<string, any> | null;
  drone_telemetry?: Record<string, any> | null;
  blockchain_provenance?: Record<string, any> | null;
  emerging_technology?: Record<string, any> | null;
  document_analysis?: Record<string, any> | null;
  scientific_research?: Record<string, any> | null;
  multimedia_entertainment?: Record<string, any> | null;
  industrial_manufacturing?: Record<string, any> | null;
  financial_business?: Record<string, any> | null;
  healthcare_medical?: Record<string, any> | null;
  transportation_logistics?: Record<string, any> | null;
  education_academic?: Record<string, any> | null;
  legal_compliance?: Record<string, any> | null;
  environmental_sustainability?: Record<string, any> | null;
  social_media_digital?: Record<string, any> | null;
  gaming_entertainment?: Record<string, any> | null;
  forensic_analysis_integration?: Record<string, any> | null;
  // Email and Communication metadata
  email?: EmailMetadata | null;
  error?: string;
}

export interface PersonaInterpretation {
  persona: string;
  key_findings: string[];
  plain_english_answers: {
    when_taken: {
      answer: string;
      details: string;
      source: string;
      confidence: string;
    };
    location: {
      has_location: boolean;
      answer: string;
      details: string;
      confidence: string;
      coordinates?: {
        latitude: number;
        longitude: number;
        formatted: string;
      };
      readable_location?: string;
      possible_reasons?: string[];
    };
    device: {
      answer: string;
      device_type: string;
      details: {
        make: string | null;
        model: string | null;
        software: string | null;
      };
      confidence: string;
    };
    authenticity: {
      assessment: string;
      confidence: string;
      score: number;
      answer: string;
      checks_performed: Record<string, any>;
      reasons: string[];
    };
  };
  confidence_scores: Record<string, any>;
  warnings: string[];
  recommendations: string[];
}

export interface EmailMetadata {
  available: boolean;
  registry?: {
    available: boolean;
    fields_extracted: number;
    tags: Record<string, any>;
    unknown_tags: Record<string, any>;
    field_catalog: string[];
  };
  email_from?: string;
  email_from_name?: string;
  email_from_address?: string;
  email_to?: string;
  email_to_count?: number;
  email_to_addresses?: string[];
  email_cc?: string;
  email_cc_count?: number;
  email_cc_addresses?: string[];
  email_bcc?: string;
  email_bcc_count?: number;
  email_bcc_addresses?: string[];
  email_subject?: string;
  email_date?: string;
  email_message_id?: string;
  email_in_reply_to?: string;
  email_references?: string;
  email_reply_to?: string;
  email_sender?: string;
  email_return_path?: string;
  email_delivered_to?: string;
  email_received_headers?: string[];
  email_content_type?: string;
  email_content_transfer_encoding?: string;
  email_content_disposition?: string;
  email_user_agent?: string;
  email_x_mailer?: string;
  email_originating_ip?: string;
  email_x_sender?: string;
  email_x_receiver?: string;
  email_dkim_present?: boolean;
  email_spf_result?: string;
  email_authentication_results?: string;
  email_spam_status?: string;
  email_spam_score?: string;
  email_virus_scanned?: string;
  email_dkim?: Record<string, any>;
  email_is_multipart?: boolean;
  email_part_count?: number;
  email_text_parts?: number;
  email_html_parts?: number;
  email_attachment_parts?: number;
  email_content_main_type?: string;
  email_content_charset?: string;
  email_content_boundary?: string;
  email_received_count?: number;
  email_first_ip?: string;
  email_first_hostname?: string;
  email_first_protocol?: string;
  email_last_ip?: string;
  email_last_hostname?: string;
  email_last_protocol?: string;
  email_return_path_parsed?: string;
  email_datetime_parsed?: string;
  email_timestamp?: number;
  email_day_of_week?: string;
  email_hour_of_day?: number;
  email_is_weekend?: boolean;
  email_timezone?: string;
  email_timezone_offset?: number;
  email_is_reply?: boolean;
  email_is_direct_reply?: boolean;
  email_is_forward?: boolean;
  email_thread_level?: number;
  email_subject_length?: number;
  email_raw_size?: number;
  email_header_size?: number;
  email_content_language?: string;
  email_priority?: string;
  email_encrypted?: boolean;
  email_attachment_count?: number;
  email_attachments?: Array<{
    filename: string;
    content_type: string;
    size: number;
    disposition?: string;
  }>;
  email_attachments_total_size?: number;
  email_attachment_types?: string[];
  email_contains_calendar?: boolean;
  email_contains_vcard?: boolean;
  calendar?: Record<string, any>;
  vcard?: Record<string, any>;
  spf_result?: string;
  dkim_domain?: string;
  dkim_selector?: string;
  dkim_algorithm?: string;
  [key: string]: any;
}

export interface FrontendMetadataResponse {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  processing_ms: number;
  file_integrity: Record<string, string>;
  filesystem: Record<string, any>;
  calculated: Record<string, any>;
  gps: Record<string, any> | null;
  summary: Record<string, any>;
  forensic: Record<string, any>;
  exif: Record<string, any>;
  image: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  makernote: Record<string, any> | null;
  iptc: Record<string, any> | null;
  xmp: Record<string, any> | null;
  normalized?: Record<string, any> | null;
  locked_fields: string[];
  extraction_info: Record<string, any>;
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  };
  forensic_analysis_integration?: Record<string, any> | null;
  persona_interpretation?: PersonaInterpretation;
  // Email and Communication metadata
  email: EmailMetadata | null;
  [key: string]: any;
}

// ============================================================================
// Helper Functions
// ============================================================================

export function normalizeEmail(
  email: string | null | undefined
): string | null {
  if (!email || typeof email !== 'string') return null;
  const trimmed = email.trim().toLowerCase();
  return trimmed.length > 3 && trimmed.includes('@') ? trimmed : null;
}

export function getSessionId(req: AuthRequest): string | null {
  const bodySession =
    typeof req.body?.session_id === 'string' ? req.body.session_id : null;
  const querySession =
    typeof req.query?.session_id === 'string' ? req.query.session_id : null;
  const headerSession =
    typeof req.headers['x-session-id'] === 'string'
      ? req.headers['x-session-id']
      : null;
  return bodySession || querySession || headerSession || null;
}

export function transformMetadataForFrontend(
  raw: PythonMetadataResponse,
  originalFilename: string,
  tier: string
): FrontendMetadataResponse {
  const normalizeGps = (
    gps: Record<string, any> | null
  ): Record<string, any> | null => {
    if (!gps || typeof gps !== 'object') return null;
    const latRaw =
      gps.latitude ??
      gps.lat ??
      gps.latitude_decimal ??
      gps.GPSLatitude ??
      gps.gps_latitude ??
      gps.Latitude;
    const lonRaw =
      gps.longitude ??
      gps.lon ??
      gps.longitude_decimal ??
      gps.GPSLongitude ??
      gps.gps_longitude ??
      gps.Longitude;

    const lat =
      typeof latRaw === 'number' ? latRaw : parseFloat(String(latRaw));
    const lon =
      typeof lonRaw === 'number' ? lonRaw : parseFloat(String(lonRaw));

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return null;
    }

    const googleMapsUrl =
      gps.google_maps_url || `https://maps.google.com/?q=${lat},${lon}`;

    return {
      latitude: lat,
      longitude: lon,
      google_maps_url: googleMapsUrl,
    };
  };

  const flattenObject = (
    obj: Record<string, any> | null
  ): Record<string, any> => {
    if (!obj || typeof obj !== 'object') return {};
    const flat: Record<string, any> = {};

    // Flatten nested objects
    Object.entries(obj).forEach(([key, value]) => {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.entries(value).forEach(([subKey, subValue]) => {
          flat[`${key}_${subKey}`] = subValue;
        });
      } else {
        flat[key] = value;
      }
    });

    return flat;
  };

  const cleanedGps = normalizeGps(raw.gps);
  const exifData = raw.exif && Object.keys(raw.exif).length > 0 ? raw.exif : {};
  const iptcData =
    raw.iptc && Object.keys(raw.iptc).length > 0 ? raw.iptc : null;
  const xmpData = raw.xmp && Object.keys(raw.xmp).length > 0 ? raw.xmp : null;
  const mobileData =
    raw.mobile_metadata && Object.keys(raw.mobile_metadata).length > 0
      ? raw.mobile_metadata
      : null;

  const parseWhatsappFilenameDate = (name?: string) => {
    if (!name) return null;
    const match = name.match(
      /WhatsApp Image (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})\.(\d{2})/i
    );
    if (!match) return null;
    const [, year, month, day, hour, minute, second] = match;
    return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
  };

  const captureDateExif =
    (exifData as any)?.DateTimeOriginal ||
    (exifData as any)?.CreateDate ||
    null;
  const filenameDate = parseWhatsappFilenameDate(originalFilename);
  const captureDate =
    captureDateExif || (filenameDate ? filenameDate.toISOString() : null);
  const captureSource = captureDateExif
    ? 'exif'
    : filenameDate
      ? 'filename'
      : null;

  const calculated = {
    ...flattenObject(raw.calculated),
    capture_date: captureDate,
    capture_date_source: captureSource,
    location_embedded: !!cleanedGps,
  };

  const registrySummary = {
    image: {
      exif: exifData ? Object.keys(exifData).length : 0,
      iptc: iptcData ? Object.keys(iptcData).length : 0,
      xmp: xmpData ? Object.keys(xmpData).length : 0,
      mobile: mobileData ? Object.keys(mobileData).length : 0,
      perceptual_hashes: raw.perceptual_hashes
        ? Object.keys(raw.perceptual_hashes).length
        : 0,
    },
    email: raw.email ? Object.keys(raw.email).length - 1 : 0,
  };

  return {
    filename: originalFilename,
    filesize: raw.filesystem?.size_human || raw.summary?.filesize || 'Unknown',
    filetype:
      raw.file?.extension?.toUpperCase().replace('.', '') ||
      raw.summary?.filetype ||
      'Unknown',
    mime_type:
      raw.file?.mime_type ||
      raw.summary?.mime_type ||
      'application/octet-stream',
    tier: normalizeTier(tier),
    fields_extracted: raw.extraction_info?.fields_extracted || 0,
    processing_ms: raw.extraction_info?.processing_ms || 0,
    file_integrity: raw.hashes?._locked ? { _locked: true } : raw.hashes || {},
    filesystem: raw.filesystem || {},
    filesystem_source: raw.filesystem
      ? (raw.filesystem as any).source || 'server_temp_upload'
      : null,
    calculated,
    gps: cleanedGps,
    summary: { ...raw.summary, filename: originalFilename },
    forensic: flattenObject(raw.forensic),
    exif: exifData,
    image: raw.image,
    video: raw.video,
    audio: raw.audio,
    pdf: raw.pdf,
    svg: raw.svg,
    makernote: raw.makernote,
    iptc: iptcData,
    xmp: xmpData,
    normalized: raw.normalized,
    web_metadata: raw.web_metadata ?? null,
    social_media: raw.social_media ?? null,
    mobile_metadata: mobileData,
    forensic_security: raw.forensic_security ?? null,
    action_camera: raw.action_camera ?? null,
    print_publishing: raw.print_publishing ?? null,
    workflow_dam: raw.workflow_dam ?? null,
    audio_advanced: raw.audio_advanced ?? null,
    video_advanced: raw.video_advanced ?? null,
    steganography_analysis: raw.steganography_analysis ?? null,
    manipulation_detection: raw.manipulation_detection ?? null,
    ai_detection: raw.ai_detection ?? null,
    timeline_analysis: raw.timeline_analysis ?? null,
    iptc_raw: raw.iptc_raw,
    xmp_raw: raw.xmp_raw,
    thumbnail: raw.thumbnail,
    perceptual_hashes: raw.perceptual_hashes,
    extended_attributes: raw.extended_attributes,
    extended: raw.extended_attributes,
    burned_metadata: raw.burned_metadata ?? null,
    metadata_comparison: raw.metadata_comparison ?? null,
    registry_summary: registrySummary,
    locked_fields: raw.locked_fields || [],
    extraction_info: raw.extraction_info || {},

    // Specialized Modules
    medical_imaging: raw.medical_imaging ?? null,
    astronomical_data: raw.astronomical_data ?? null,
    geospatial_analysis: raw.geospatial_analysis ?? null,
    scientific_instruments: raw.scientific_instruments ?? null,
    drone_telemetry: raw.drone_telemetry ?? null,
    blockchain_provenance: raw.blockchain_provenance ?? null,
    emerging_technology: raw.emerging_technology ?? null,
    document_analysis: raw.document_analysis ?? null,
    scientific_research: raw.scientific_research ?? null,
    multimedia_entertainment: raw.multimedia_entertainment ?? null,
    industrial_manufacturing: raw.industrial_manufacturing ?? null,
    financial_business: raw.financial_business ?? null,
    healthcare_medical: raw.healthcare_medical ?? null,
    transportation_logistics: raw.transportation_logistics ?? null,
    education_academic: raw.education_academic ?? null,
    legal_compliance: raw.legal_compliance ?? null,
    environmental_sustainability: raw.environmental_sustainability ?? null,
    social_media_digital: raw.social_media_digital ?? null,
    gaming_entertainment: raw.gaming_entertainment ?? null,

    // Email and Communication metadata
    email: raw.email?._locked
      ? { _locked: true, available: false }
      : (raw.email ?? null),

    // Persona interpretation (if available from Python backend)
    persona_interpretation: (raw as any).persona_interpretation ?? undefined,

    // Forensic Analysis Integration (NEW: Phase 3.1)
    forensic_analysis_integration:
      raw.forensic_analysis_integration ?? undefined,
  };
}

// Apply access-mode redactions in a single place so all routes behave consistently
export function applyAccessModeRedaction(
  metadata: FrontendMetadataResponse,
  mode: 'device_free' | 'trial_limited' | 'paid'
) {
  if (mode === 'trial_limited') {
    // Current trial behavior: heavy redaction (same as before)
    metadata.iptc = null;
    metadata.xmp = null;
    metadata.exif = {}; // EXIF cannot be null in FrontendMetadataResponse, so use empty object
    metadata.iptc_raw = null;
    metadata.xmp_raw = null;
    metadata._trial_limited = true;
    // Mark locked_fields conservatively
    metadata.locked_fields = Array.from(
      new Set([
        ...(metadata.locked_fields || []),
        'filesystem_details',
        'hashes',
        'extended_attributes',
        'thumbnail',
        'embedded_thumbnails',
        'perceptual_hashes',
        'makernote',
        'gps',
        'iptc',
        'xmp',
        'calculated',
        'forensic',
        'burned_metadata',
        'metadata_comparison',
      ])
    );
  } else if (mode === 'device_free') {
    // Hybrid mode: keep high-value fields, redact only sensitive identifiers

    // GPS: round coordinates to 2 decimals OR replace with presence flag
    if (metadata.gps && typeof metadata.gps === 'object') {
      const lat = Number((metadata.gps as any).latitude ?? NaN);
      const lon = Number((metadata.gps as any).longitude ?? NaN);
      if (Number.isFinite(lat) && Number.isFinite(lon)) {
        (metadata.gps as any).latitude = Math.round(lat * 100) / 100;
        (metadata.gps as any).longitude = Math.round(lon * 100) / 100;
        // Remove precise map link to avoid exposing exact location
        if ((metadata.gps as any).google_maps_url)
          delete (metadata.gps as any).google_maps_url;
      } else {
        // No coordinates - keep gps null
        metadata.gps = null;
      }
    }

    // Burned metadata: keep presence and confidence, redact text and parsed precise location
    if (metadata.burned_metadata) {
      const bm = metadata.burned_metadata as any;
      bm.extracted_text = null;
      if (bm.parsed_data) {
        if (bm.parsed_data.gps) delete bm.parsed_data.gps;
        if (bm.parsed_data.plus_code) delete bm.parsed_data.plus_code;
        // Coarsen address by removing street-level info if present
        if (bm.parsed_data.location) {
          // Keep only city/state/country if available
          const loc = bm.parsed_data.location as any;
          const coarse: any = {};
          if (loc.city) coarse.city = loc.city;
          if (loc.state) coarse.state = loc.state;
          if (loc.country) coarse.country = loc.country;
          bm.parsed_data.location = Object.keys(coarse).length ? coarse : null;
        }
      }
    }

    // Extended attributes: keep available/count, redact attribute values
    if (
      metadata.extended_attributes &&
      (metadata.extended_attributes as any).attributes
    ) {
      const attrs = (metadata.extended_attributes as any).attributes;
      const redacted: Record<string, any> = {};
      Object.keys(attrs).forEach(k => (redacted[k] = null));
      (metadata.extended_attributes as any).attributes = redacted;
    }

    // Filesystem: remove owner and sensitive internals
    if (metadata.filesystem && typeof metadata.filesystem === 'object') {
      [
        'owner',
        'owner_uid',
        'group',
        'group_gid',
        'inode',
        'device',
        'permissions_octal',
        'permissions_human',
        'hard_links',
      ].forEach(k => delete (metadata.filesystem as any)[k]);
    }

    // Thumbnail: keep presence + basic attrs only
    if (metadata.thumbnail && typeof metadata.thumbnail === 'object') {
      const t = metadata.thumbnail as any;
      metadata.thumbnail = {
        has_embedded: !!t.has_embedded,
        width: t.width || null,
        height: t.height || null,
      } as any;
    }

    // Perceptual hashes: keep only basic hashes
    if (
      metadata.perceptual_hashes &&
      typeof metadata.perceptual_hashes === 'object'
    ) {
      const p = metadata.perceptual_hashes as any;
      metadata.perceptual_hashes = {
        phash: p.phash || null,
        dhash: p.dhash || null,
        ahash: p.ahash || null,
        whash: p.whash || null,
      } as any;
    }

    // Enterprise-only bulky buckets: hide to avoid leaking heavy internals
    [
      'drone_telemetry',
      'emerging_technology',
      'synthetic_media_analysis',
      'blockchain_provenance',
    ].forEach(k => {
      if ((metadata as any)[k]) (metadata as any)[k] = null;
    });

    // Update locked fields to reflect minimal redactions
    metadata.locked_fields = Array.from(
      new Set([...(metadata.locked_fields || []), 'gps', 'extended_attributes'])
    );
  }
}

type ExtractOptions = {
  ocr?: boolean;
  maxDim?: number;
};

export async function extractMetadataWithPython(
  filePath: string,
  tier: string,
  includePerformanceMetrics: boolean = false,
  enableAdvancedAnalysis: boolean = false,
  storeMetadata: boolean = false,
  opts: ExtractOptions = {}
): Promise<PythonMetadataResponse> {
  // Validate and sanitize the file path
  const resolvedPath = path.resolve(filePath);
  const tempDir = '/tmp/metaextract';
  const allowedDirs = [tempDir, process.cwd()];

  if (!isPathSafe(resolvedPath, allowedDirs)) {
    throw new Error(`Invalid file path: path is outside allowed directories`);
  }

  // Ensure the file exists (use async access so it's mockable in tests)
  try {
    await fs.access(resolvedPath);
  } catch {
    throw new Error(`File not found: ${filePath}`);
  }

  return new Promise((resolve, reject) => {
    const args = [PYTHON_SCRIPT_PATH, filePath, '--tier', tier];

    if (includePerformanceMetrics) {
      args.push('--performance');
    }

    if (enableAdvancedAnalysis) {
      args.push('--advanced');
    }

    if (storeMetadata) {
      args.push('--store');
    }

    if (opts?.ocr) {
      args.push('--ocr');
    }

    const maxDim = typeof opts?.maxDim === 'number' ? opts.maxDim : 2048;
    if (maxDim && Number.isFinite(maxDim)) {
      args.push('--max-dim', String(maxDim));
    }

    // Log the Python process startup (opt-in, to support manual smoke)
    if (process.env.METAEXTRACT_LOG_PY_ARGS === '1') {
      console.log(
        `[DEBUG] extractMetadataWithPython: tier=${tier}, file=${path.basename(filePath)}`
      );
      console.log(`Command: ${pythonExecutable} ${args.join(' ')}`);
    }

    const python = spawn(pythonExecutable, args);

    let stdout = '';
    let stderr = '';

    const enablePyLogging =
      process.env.NODE_ENV !== 'test' ||
      process.env.METAEXTRACT_LOG_PY_ARGS === '1';

    python.stdout.on('data', data => {
      const dataStr = data.toString();
      stdout += dataStr;
      // Log large outputs in chunks to avoid overwhelming the console
      if (enablePyLogging && dataStr.length > 1000) {
        console.log(
          `Python stdout (partial): ${dataStr.substring(0, 1000)}...`
        );
      }
    });

    python.stderr.on('data', data => {
      const dataStr = data.toString();
      stderr += dataStr;
      // Log errors immediately when not running unit tests
      if (enablePyLogging) {
        console.error(`Python stderr: ${dataStr}`);
      }
    });

    python.on('close', code => {
      if (enablePyLogging) {
        console.log(`Python extraction process exited with code: ${code}`);
      }

      if (code !== 0) {
        const errorDetails = {
          message: `Python extractor failed with code ${code}`,
          stderr: stderr || 'No stderr output',
          stdout: stdout || 'No stdout output',
          command: `${pythonExecutable} ${args.join(' ')}`,
          filePath,
          tier,
        };

        if (enablePyLogging) {
          console.error('Python extraction error details:', errorDetails);
        }
        reject(
          new Error(`Python extractor failed: ${stderr || 'Unknown error'}`)
        );
        return;
      }

      if (!stdout) {
        const error = 'Python extractor returned empty output';
        if (enablePyLogging) {
          console.error(error, {
            stderr,
            command: `${pythonExecutable} ${args.join(' ')}`,
          });
        }
        reject(new Error(error));
        return;
      }

      try {
        const result = JSON.parse(stdout);
        if (enablePyLogging) {
          console.log(
            `Successfully parsed Python extraction result for ${path.basename(
              filePath
            )}, ${result.extraction_info?.fields_extracted || 0} fields extracted`
          );
        }
        resolve(result);
      } catch (parseError) {
        if (enablePyLogging) {
          console.error(
            'Failed to parse Python extraction output:',
            parseError
          );
          console.error(
            'Raw stdout (first 1000 chars):',
            stdout.substring(0, 1000)
          );
          console.error('Raw stderr:', stderr.substring(0, 500));
        }
        reject(
          new Error(
            `Failed to parse metadata extraction result: ${
              parseError instanceof Error
                ? parseError.message
                : 'Unknown parsing error'
            }`
          )
        );
      }
    });

    python.on('error', err => {
      console.error('Failed to spawn Python extraction process:', err);
      reject(new Error(`Failed to start Python extractor: ${err.message}`));
    });

    // Set timeout with detailed logging
    const timeoutMs = 180000; // 3 minutes
    const timeoutId = setTimeout(() => {
      console.warn(
        `Python extraction timeout after ${timeoutMs}ms for file: ${filePath}`
      );
      if (!python.killed) {
        python.kill();
        console.log(`Killed Python process for file: ${filePath}`);
      }
      reject(new Error(`Metadata extraction timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    // Allow timer to not keep the Node process alive (so tests can exit)
    if (typeof timeoutId.unref === 'function') {
      timeoutId.unref();
    }

    // Clear timeout on completion
    python.on('close', () => {
      clearTimeout(timeoutId);
    });
  });
}

export async function cleanupTempFile(tempPath: string | null): Promise<void> {
  if (tempPath) {
    try {
      await fs.unlink(tempPath);
    } catch (error) {
      console.error('Failed to delete temp file:', error);
    }
  }
}

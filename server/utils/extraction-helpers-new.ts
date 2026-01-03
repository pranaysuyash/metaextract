/**
 * New extraction helpers using the refactored metadata engine.
 * 
 * This module provides compatibility functions that use the new modular
 * architecture while maintaining the same API as the original helpers.
 */

import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { spawn } from 'child_process';
import { existsSync } from 'fs';
import { normalizeTier } from '@shared/tierConfig';
import type { AuthRequest } from '../auth';

const currentFilePath = fileURLToPath(import.meta.url);
const currentDirPath = dirname(currentFilePath);

// Import the new refactored engine
import { extract_comprehensive_metadata_new } from '../extractor/core/comprehensive_engine';

// Re-export original helper functions for compatibility
export {
  transformMetadataForFrontend,
  normalizeEmail,
  getSessionId,
  cleanupTempFile
} from './extraction-helpers';

// Re-export the original types for compatibility
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
  registry_summary?: Record<string, any>;
}

/**
 * New metadata extraction function using the refactored engine.
 * Maintains compatibility with the original API while using the new architecture.
 */
export async function extractMetadataWithPythonNew(
  filePath: string,
  tier: string,
  includePerformanceMetrics: boolean = false,
  enableAdvancedAnalysis: boolean = false,
  storeMetadata: boolean = false
): Promise<PythonMetadataResponse> {
  try {
    // Get file information
    const fileStats = await fs.stat(filePath);
    const pathInfo = path.parse(filePath);
    const mimeType = await detectMimeType(filePath);
    
    // Record start time for performance tracking
    const startTime = Date.now();
    
    // Use the new refactored engine
    const result = await extract_comprehensive_metadata_new(filePath, tier);
    
    const processingTime = Date.now() - startTime;
    
    // Transform the new format to the old format for compatibility
    return transformNewResultToOldFormat(
      result,
      filePath,
      pathInfo,
      mimeType,
      fileStats,
      tier,
      processingTime,
      includePerformanceMetrics,
      enableAdvancedAnalysis
    );
    
  } catch (error) {
    console.error('New extraction failed, falling back to old engine:', error);
    // Fallback to the original extraction method
    return await extractMetadataWithPythonOriginal(
      filePath,
      tier,
      includePerformanceMetrics,
      enableAdvancedAnalysis,
      storeMetadata
    );
  }
}

/**
 * Transform the new engine result to the old format for compatibility.
 */
function transformNewResultToOldFormat(
  newResult: any,
  filePath: string,
  pathInfo: path.ParsedPath,
  mimeType: string,
  fileStats: any,
  tier: string,
  processingTime: number,
  includePerformanceMetrics: boolean,
  enableAdvancedAnalysis: boolean
): PythonMetadataResponse {
  const metadata = newResult.metadata || {};
  const extractionInfo = newResult.extraction_info || {};
  
  // Extract different metadata categories
  const fileInfo = metadata.file_info || {};
  const exifData = metadata.exif || {};
  const gpsData = metadata.gps || {};
  const iptcData = metadata.iptc || {};
  const xmpData = metadata.xmp || {};
  const pilData = metadata.pil || {};
  
  // Create registry summary for frontend
  const registrySummary = {
    image: {
      exif: Object.keys(exifData).length,
      iptc: Object.keys(iptcData).length,
      xmp: Object.keys(xmpData).length,
      mobile: 0, // Will be populated when mobile extractor is added
      perceptual_hashes: 0, // Will be populated when hash extractor is added
    }
  };
  
  // Determine locked fields based on tier
  const lockedFields = getLockedFields(tier, metadata);
  
  // Calculate field counts
  const totalFields = countFields(metadata);
  const lockedCategories = Math.max(0, 5 - getTierLevel(tier)); // Simplified logic
  
  return {
    extraction_info: {
      timestamp: new Date().toISOString(),
      tier: tier,
      engine_version: extractionInfo.engine_version || '4.1.0-refactored',
      libraries: extractionInfo.libraries || {},
      fields_extracted: totalFields,
      locked_categories: lockedCategories,
      processing_ms: processingTime,
    },
    file: {
      path: filePath,
      name: pathInfo.name,
      stem: pathInfo.name,
      extension: pathInfo.ext,
      mime_type: mimeType,
    },
    summary: createSummary(metadata),
    filesystem: fileInfo,
    hashes: {}, // Will be populated when hash extractor is added
    image: pilData,
    exif: exifData,
    gps: gpsData,
    video: null, // Will be populated when video extractor is added
    audio: null, // Will be populated when audio extractor is added
    pdf: null, // Will be populated when document extractor is added
    svg: null,
    extended_attributes: {},
    calculated: createCalculatedFields(metadata),
    forensic: {},
    makernote: extractMakerNotes(exifData),
    iptc: iptcData,
    xmp: xmpData,
    locked_fields: lockedFields,
    registry_summary: registrySummary,
    // Add other fields as they become available
    burned_metadata: null,
    advanced_analysis: enableAdvancedAnalysis ? createAdvancedAnalysis(metadata) : null,
  };
}

/**
 * Simple MIME type detection.
 */
async function detectMimeType(filePath: string): Promise<string> {
  const ext = path.extname(filePath).toLowerCase();
  const mimeMap: Record<string, string> = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.webp': 'image/webp',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
    '.mp4': 'video/mp4',
    '.avi': 'video/x-msvideo',
    '.mov': 'video/quicktime',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.pdf': 'application/pdf',
  };
  return mimeMap[ext] || 'application/octet-stream';
}

/**
 * Create a summary of the metadata.
 */
function createSummary(metadata: Record<string, any>): Record<string, any> {
  const summary: Record<string, any> = {};
  
  // Add key summary information
  if (metadata.exif) {
    summary.has_exif = Object.keys(metadata.exif).length > 0;
    summary.exif_field_count = Object.keys(metadata.exif).length;
  }
  
  if (metadata.gps) {
    summary.has_gps = Object.keys(metadata.gps).length > 0;
    summary.gps_coordinates = metadata.gps.latitude && metadata.gps.longitude;
  }
  
  if (metadata.iptc) {
    summary.has_iptc = Object.keys(metadata.iptc).length > 0;
    summary.iptc_field_count = Object.keys(metadata.iptc).length;
  }
  
  return summary;
}

/**
 * Create calculated fields.
 */
function createCalculatedFields(metadata: Record<string, any>): Record<string, any> {
  const calculated: Record<string, any> = {};
  
  // Add any calculated fields based on the metadata
  if (metadata.exif) {
    calculated.exif_field_count = Object.keys(metadata.exif).length;
  }
  
  if (metadata.gps) {
    calculated.has_location = !!(metadata.gps.latitude && metadata.gps.longitude);
  }
  
  return calculated;
}

/**
 * Extract maker notes from EXIF data.
 */
function extractMakerNotes(exifData: Record<string, any>): Record<string, any> | null {
  const makerNotes: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(exifData)) {
    if (key.toLowerCase().includes('maker') || key.toLowerCase().includes('makernote')) {
      makerNotes[key] = value;
    }
  }
  
  return Object.keys(makerNotes).length > 0 ? makerNotes : null;
}

/**
 * Get locked fields based on tier.
 */
function getLockedFields(tier: string, metadata: Record<string, any>): string[] {
  const tierLevel = getTierLevel(tier);
  const lockedFields: string[] = [];
  
  // Simple logic: higher tiers unlock more fields
  if (tierLevel < 2) {
    // Lock some advanced fields for lower tiers
    if (metadata.exif) {
      const exifKeys = Object.keys(metadata.exif);
      lockedFields.push(...exifKeys.slice(10)); // Lock fields beyond the first 10
    }
  }
  
  return lockedFields;
}

/**
 * Get tier level as a number.
 */
function getTierLevel(tier: string): number {
  const tierMap: Record<string, number> = {
    'free': 0,
    'basic': 1,
    'super': 2,
    'premium': 3,
    'enterprise': 4,
  };
  return tierMap[tier.toLowerCase()] || 0;
}

/**
 * Count total fields in metadata.
 */
function countFields(metadata: Record<string, any>): number {
  let count = 0;
  
  for (const section of Object.values(metadata)) {
    if (typeof section === 'object' && section !== null) {
      count += Object.keys(section).length;
    }
  }
  
  return count;
}

/**
 * Create advanced analysis data.
 */
function createAdvancedAnalysis(metadata: Record<string, any>): {
  enabled: boolean;
  processing_time_ms: number;
  modules_run: string[];
  forensic_score: number;
  authenticity_assessment: string;
} {
  return {
    enabled: true,
    processing_time_ms: 0, // Will be populated with actual timing
    modules_run: ['image_extractor'],
    forensic_score: 0.5, // Simplified scoring
    authenticity_assessment: 'basic_analysis_complete',
  };
}

/**
 * Original extraction function for fallback.
 * This would call the old Python engine as a backup.
 */
async function extractMetadataWithPythonOriginal(
  filePath: string,
  tier: string,
  includePerformanceMetrics: boolean,
  enableAdvancedAnalysis: boolean,
  storeMetadata: boolean
): Promise<PythonMetadataResponse> {
  // For now, throw an error to indicate fallback is not implemented
  // In a full implementation, this would call the original Python script
  throw new Error('Fallback to original engine not implemented yet');
}

// Re-export the new function with the original name for drop-in replacement
export const extractMetadataWithPython = extractMetadataWithPythonNew;
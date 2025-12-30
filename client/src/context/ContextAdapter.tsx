/**
 * Context Adapter - Dynamic UI Adaptation Controller
 *
 * Provides React context for managing file context detection and
 * dynamic UI template switching based on file type and content.
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  ReactNode,
} from 'react';

// ============================================================================
// Types
// ============================================================================

export interface ContextProfile {
  display_name: string;
  description: string;
  ui_template: string;
  icon: string;
  color: string;
  priority_fields: string[];
  special_components: string[];
  field_groups: Record<string, string[]>;
}

export interface AlternativeContext {
  context_type: string;
  confidence: number;
}

export interface FileContext {
  context_type: string;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low' | 'uncertain';
  is_fallback: boolean;
  detection_time_ms: number;
  profile: ContextProfile;
  alternative_contexts: AlternativeContext[];
  evidence: Record<string, any>;
}

export interface ContextAdapterState {
  currentContext: FileContext | null;
  isLoading: boolean;
  error: string | null;
  viewMode: 'simple' | 'advanced' | 'raw';
}

export interface ContextAdapterActions {
  detectContext: (metadata: Record<string, any>, filename: string) => void;
  setViewMode: (mode: 'simple' | 'advanced' | 'raw') => void;
  resetContext: () => void;
  overrideContext: (contextType: string) => void;
}

// ============================================================================
// Default Context Profiles (Fallback when API unavailable)
// ============================================================================

const DEFAULT_PROFILES: Record<string, ContextProfile> = {
  smartphone_photo: {
    display_name: 'Smartphone Photo',
    description: 'Photo taken with a smartphone camera',
    ui_template: 'computational_photography',
    icon: 'smartphone',
    color: 'blue',
    priority_fields: [
      'Make', 'Model', 'DateTimeOriginal', 'GPSLatitude', 'GPSLongitude',
      'LensModel', 'ExposureTime', 'FNumber', 'ISO'
    ],
    special_components: ['gps_map_mini', 'golden_hour_indicator'],
    field_groups: {
      'Camera': ['Make', 'Model', 'LensModel', 'Software'],
      'Exposure': ['ExposureTime', 'FNumber', 'ISO'],
      'Location': ['GPSLatitude', 'GPSLongitude', 'GPSAltitude'],
    },
  },
  dslr_photo: {
    display_name: 'DSLR/Mirrorless Photo',
    description: 'Photo taken with a professional camera',
    ui_template: 'exposure_triangle',
    icon: 'camera',
    color: 'purple',
    priority_fields: [
      'Make', 'Model', 'LensModel', 'ShutterCount', 'SerialNumber',
      'ExposureTime', 'FNumber', 'ISO', 'FocalLength'
    ],
    special_components: ['exposure_triangle_diagram', 'lens_profile_viewer', 'shutter_count_analysis'],
    field_groups: {
      'Camera Body': ['Make', 'Model', 'SerialNumber', 'ShutterCount'],
      'Lens': ['LensModel', 'FocalLength', 'MaxApertureValue'],
      'Exposure': ['ExposureTime', 'FNumber', 'ISO'],
    },
  },
  drone_photo: {
    display_name: 'Drone/Aerial Photo',
    description: 'Aerial photograph from a drone',
    ui_template: 'map_centered',
    icon: 'plane',
    color: 'cyan',
    priority_fields: [
      'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'RelativeAltitude',
      'GimbalRoll', 'GimbalPitch', 'Make', 'Model'
    ],
    special_components: ['aerial_map_overlay', 'altitude_chart', 'gimbal_orientation_3d'],
    field_groups: {
      'Flight Data': ['GPSAltitude', 'RelativeAltitude', 'FlightSpeed'],
      'Gimbal': ['GimbalRoll', 'GimbalPitch', 'GimbalYaw'],
      'Location': ['GPSLatitude', 'GPSLongitude'],
    },
  },
  dicom_medical: {
    display_name: 'Medical Image (DICOM)',
    description: 'Medical imaging file',
    ui_template: 'medical_context',
    icon: 'heart-pulse',
    color: 'red',
    priority_fields: [
      'PatientID', 'StudyDate', 'Modality', 'BodyPartExamined',
      'Manufacturer', 'InstitutionName'
    ],
    special_components: ['body_part_diagram', 'dose_meter', 'anonymization_warning'],
    field_groups: {
      'Study': ['StudyDate', 'StudyDescription'],
      'Patient': ['PatientID', 'BodyPartExamined'],
      'Equipment': ['Manufacturer', 'InstitutionName'],
    },
  },
  astronomy_fits: {
    display_name: 'Astronomical Data (FITS)',
    description: 'Astronomical observation',
    ui_template: 'astronomy_context',
    icon: 'star',
    color: 'indigo',
    priority_fields: [
      'OBJECT', 'RA', 'DEC', 'EXPTIME', 'FILTER', 'TELESCOP', 'DATE-OBS'
    ],
    special_components: ['celestial_coordinate_overlay', 'star_chart_viewer'],
    field_groups: {
      'Target': ['OBJECT', 'RA', 'DEC'],
      'Observation': ['DATE-OBS', 'EXPTIME', 'FILTER'],
      'Equipment': ['TELESCOP', 'INSTRUME'],
    },
  },
  ai_generated: {
    display_name: 'AI-Generated Image',
    description: 'Image created by AI',
    ui_template: 'ai_generated',
    icon: 'sparkles',
    color: 'pink',
    priority_fields: [
      'Software', 'Creator', 'Prompt', 'Model', 'Seed', 'Steps'
    ],
    special_components: ['ai_model_badge', 'prompt_viewer', 'authenticity_warning'],
    field_groups: {
      'Generation': ['Software', 'Model', 'Prompt'],
      'Parameters': ['Seed', 'Steps', 'CFGScale'],
    },
  },
  edited_image: {
    display_name: 'Edited Image',
    description: 'Image edited in software',
    ui_template: 'editing_history',
    icon: 'wand',
    color: 'amber',
    priority_fields: [
      'Software', 'HistoryAction', 'OriginalDocumentID', 'Make', 'Model'
    ],
    special_components: ['edit_history_timeline', 'software_chain_viewer'],
    field_groups: {
      'Edit History': ['Software', 'HistoryAction', 'EditingTime'],
      'Original': ['OriginalDocumentID', 'DateTimeOriginal'],
    },
  },
  generic_photo: {
    display_name: 'Photo',
    description: 'Standard photograph',
    ui_template: 'default_photo',
    icon: 'image',
    color: 'slate',
    priority_fields: [
      'Make', 'Model', 'DateTimeOriginal', 'ImageWidth', 'ImageHeight',
      'ExposureTime', 'FNumber', 'ISO'
    ],
    special_components: ['basic_exif_view'],
    field_groups: {
      'Camera': ['Make', 'Model'],
      'Exposure': ['ExposureTime', 'FNumber', 'ISO'],
      'Image': ['ImageWidth', 'ImageHeight'],
    },
  },
  generic_file: {
    display_name: 'File',
    description: 'Generic file',
    ui_template: 'default',
    icon: 'file',
    color: 'slate',
    priority_fields: ['FileName', 'FileSize', 'FileType', 'MIMEType'],
    special_components: [],
    field_groups: {
      'File': ['FileName', 'FileSize', 'FileType'],
    },
  },
};

// ============================================================================
// Context Detection Logic (Client-side fallback)
// ============================================================================

function detectContextFromMetadata(metadata: Record<string, any>): FileContext {
  const scores: Record<string, number> = {};
  const evidence: Record<string, any> = {};

  // Flatten metadata for easier searching
  const flatMetadata: Record<string, string> = {};
  const flatten = (obj: Record<string, any>, prefix = '') => {
    for (const [key, value] of Object.entries(obj)) {
      if (key.startsWith('_')) continue;
      const fullKey = prefix ? `${prefix}.${key}` : key;
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        flatten(value, fullKey);
      } else {
        flatMetadata[fullKey] = String(value);
      }
    }
  };
  flatten(metadata);

  const make = (metadata.Make || metadata.exif?.Make || '').toLowerCase();
  const model = (metadata.Model || metadata.exif?.Model || '').toLowerCase();
  const software = (metadata.Software || '').toLowerCase();

  // Smartphone detection
  const smartphoneMakers = ['apple', 'iphone', 'samsung', 'google', 'pixel', 'huawei', 'xiaomi', 'oneplus'];
  for (const maker of smartphoneMakers) {
    if (make.includes(maker) || model.includes(maker)) {
      scores['smartphone_photo'] = 0.85;
      evidence['smartphone'] = { maker_match: maker };
      break;
    }
  }

  // Check for computational photography
  const hasDepth = Object.keys(flatMetadata).some(k => k.toLowerCase().includes('depth'));
  const hasLivePhoto = Object.keys(flatMetadata).some(k =>
    k.toLowerCase().includes('livephoto') || k.toLowerCase().includes('motionphoto')
  );
  if (hasDepth || hasLivePhoto) {
    scores['smartphone_photo'] = Math.max(scores['smartphone_photo'] || 0, 0.9);
  }

  // DSLR detection
  const dslrMakers = ['canon eos', 'nikon', 'sony alpha', 'fujifilm', 'olympus', 'panasonic lumix'];
  const combined = `${make} ${model}`;
  for (const maker of dslrMakers) {
    if (combined.includes(maker)) {
      scores['dslr_photo'] = 0.85;
      evidence['dslr'] = { maker_match: maker };
      break;
    }
  }

  // Shutter count indicates DSLR
  if (metadata.ShutterCount || metadata.ImageCount || metadata.makernote?.ShutterCount) {
    scores['dslr_photo'] = Math.max(scores['dslr_photo'] || 0, 0.9);
    evidence['dslr'] = { ...evidence['dslr'], shutter_count: true };
  }

  // Drone detection
  const droneMakers = ['dji', 'mavic', 'phantom', 'parrot', 'autel'];
  for (const maker of droneMakers) {
    if (combined.includes(maker)) {
      scores['drone_photo'] = 0.95;
      evidence['drone'] = { maker_match: maker };
      break;
    }
  }

  // Gimbal data indicates drone
  const hasGimbal = Object.keys(flatMetadata).some(k => k.toLowerCase().includes('gimbal'));
  const hasFlightData = Object.keys(flatMetadata).some(k =>
    k.toLowerCase().includes('flightaltitude') || k.toLowerCase().includes('relativealtitude')
  );
  if (hasGimbal || hasFlightData) {
    scores['drone_photo'] = Math.max(scores['drone_photo'] || 0, 0.9);
  }

  // AI-generated detection
  const aiPatterns = ['midjourney', 'dall-e', 'stable diffusion', 'automatic1111', 'comfyui'];
  const allValues = Object.values(flatMetadata).join(' ').toLowerCase();
  for (const pattern of aiPatterns) {
    if (allValues.includes(pattern)) {
      scores['ai_generated'] = 0.95;
      evidence['ai'] = { software_match: pattern };
      break;
    }
  }

  // Edited image detection
  const editingSoftware = ['photoshop', 'lightroom', 'capture one', 'gimp', 'affinity'];
  for (const sw of editingSoftware) {
    if (software.includes(sw)) {
      scores['edited_image'] = 0.85;
      evidence['edited'] = { software_match: sw };
      break;
    }
  }

  // DICOM detection
  if (metadata.PatientID || metadata.StudyDate || metadata.Modality) {
    scores['dicom_medical'] = 0.95;
  }

  // FITS detection
  if (metadata.SIMPLE || metadata.BITPIX || metadata.TELESCOP) {
    scores['astronomy_fits'] = 0.95;
  }

  // Determine winner
  let bestContext = 'generic_photo';
  let bestScore = 0.3;

  for (const [context, score] of Object.entries(scores)) {
    if (score > bestScore) {
      bestContext = context;
      bestScore = score;
    }
  }

  // Build alternatives
  const alternatives: AlternativeContext[] = Object.entries(scores)
    .filter(([ctx]) => ctx !== bestContext)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([ctx, conf]) => ({ context_type: ctx, confidence: conf }));

  const profile = DEFAULT_PROFILES[bestContext] || DEFAULT_PROFILES['generic_file'];

  return {
    context_type: bestContext,
    confidence: bestScore,
    confidence_level: bestScore >= 0.75 ? 'high' : bestScore >= 0.5 ? 'medium' : 'low',
    is_fallback: bestScore < 0.3,
    detection_time_ms: 0,
    profile,
    alternative_contexts: alternatives,
    evidence,
  };
}

// ============================================================================
// Context Provider
// ============================================================================

const ContextAdapterContext = createContext<
  (ContextAdapterState & ContextAdapterActions) | null
>(null);

export function ContextAdapterProvider({ children }: { children: ReactNode }) {
  const [currentContext, setCurrentContext] = useState<FileContext | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'simple' | 'advanced' | 'raw'>('simple');

  const detectContext = useCallback((metadata: Record<string, any>, filename: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // First try API call
      // For now, use client-side detection as fallback
      const startTime = performance.now();
      const result = detectContextFromMetadata(metadata);
      result.detection_time_ms = performance.now() - startTime;

      setCurrentContext(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Context detection failed');
      // Fallback to generic
      setCurrentContext({
        context_type: 'generic_file',
        confidence: 0.1,
        confidence_level: 'uncertain',
        is_fallback: true,
        detection_time_ms: 0,
        profile: DEFAULT_PROFILES['generic_file'],
        alternative_contexts: [],
        evidence: {},
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetContext = useCallback(() => {
    setCurrentContext(null);
    setError(null);
  }, []);

  const overrideContext = useCallback((contextType: string) => {
    if (currentContext) {
      const profile = DEFAULT_PROFILES[contextType] || DEFAULT_PROFILES['generic_file'];
      setCurrentContext({
        ...currentContext,
        context_type: contextType,
        profile,
        confidence: 1.0, // Manual override = full confidence
        confidence_level: 'high',
        is_fallback: false,
      });
    }
  }, [currentContext]);

  const value = useMemo(
    () => ({
      currentContext,
      isLoading,
      error,
      viewMode,
      detectContext,
      setViewMode,
      resetContext,
      overrideContext,
    }),
    [currentContext, isLoading, error, viewMode, detectContext, resetContext, overrideContext]
  );

  return (
    <ContextAdapterContext.Provider value={value}>
      {children}
    </ContextAdapterContext.Provider>
  );
}

export function useContextAdapter() {
  const context = useContext(ContextAdapterContext);
  if (!context) {
    throw new Error('useContextAdapter must be used within a ContextAdapterProvider');
  }
  return context;
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Get priority fields for the current context
 */
export function usePriorityFields(metadata: Record<string, any>) {
  const { currentContext } = useContextAdapter();

  return useMemo(() => {
    if (!currentContext) return [];

    const priorityFields = currentContext.profile.priority_fields;
    return priorityFields.filter(field => {
      // Check if field exists in metadata (including nested)
      const keys = field.split('.');
      let value: any = metadata;
      for (const key of keys) {
        value = value?.[key];
        if (value === undefined) break;
      }
      return value !== undefined && value !== null && value !== '';
    });
  }, [currentContext, metadata]);
}

/**
 * Get field groups organized by the current context
 */
export function useFieldGroups(metadata: Record<string, any>) {
  const { currentContext } = useContextAdapter();

  return useMemo(() => {
    if (!currentContext) return {};

    const groups = currentContext.profile.field_groups;
    const result: Record<string, Array<{ key: string; value: any }>> = {};

    for (const [groupName, fields] of Object.entries(groups)) {
      result[groupName] = fields
        .map(field => {
          let value = metadata[field];
          // Check nested paths
          if (value === undefined) {
            const parts = field.split('.');
            value = metadata;
            for (const part of parts) {
              value = value?.[part];
            }
          }
          return { key: field, value };
        })
        .filter(item => item.value !== undefined && item.value !== null);
    }

    return result;
  }, [currentContext, metadata]);
}

/**
 * Check if a special component should be shown
 */
export function useSpecialComponents() {
  const { currentContext } = useContextAdapter();

  return useMemo(() => {
    if (!currentContext) return [];
    return currentContext.profile.special_components;
  }, [currentContext]);
}

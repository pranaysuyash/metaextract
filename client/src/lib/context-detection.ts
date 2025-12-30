/**
 * Context Detection Engine
 * 
 * Analyzes file metadata to determine the most appropriate UI context
 * and provides intelligent suggestions for metadata exploration.
 */

export interface FileContext {
  type: 'photography' | 'forensic' | 'scientific' | 'web' | 'mobile' | 'professional' | 'generic';
  confidence: number;
  indicators: string[];
  suggestedViews: string[];
  priorityFields: string[];
  warnings?: string[];
}

export interface ContextProfile {
  name: string;
  displayName: string;
  description: string;
  indicators: {
    required?: string[];
    preferred?: string[];
    negative?: string[];
  };
  priorityCategories: string[];
  suggestedActions: string[];
  uiTemplate: 'standard' | 'forensic' | 'scientific' | 'mobile' | 'professional';
}

// Context profiles registry
export const CONTEXT_PROFILES: Record<string, ContextProfile> = {
  photography: {
    name: 'photography',
    displayName: 'Photography',
    description: 'Professional photography workflow',
    indicators: {
      required: ['exif'],
      preferred: ['Make', 'Model', 'LensModel', 'FocalLength', 'FNumber', 'ExposureTime', 'ISO'],
      negative: ['forensic_security', 'scientific_data']
    },
    priorityCategories: ['exif', 'image', 'gps', 'makernote', 'iptc'],
    suggestedActions: ['view_camera_settings', 'check_location', 'analyze_exposure'],
    uiTemplate: 'standard'
  },
  
  forensic: {
    name: 'forensic',
    displayName: 'Forensic Analysis',
    description: 'Digital forensics and evidence analysis',
    indicators: {
      preferred: ['forensic', 'file_integrity', 'burned_metadata', 'manipulation_detection'],
      negative: []
    },
    priorityCategories: ['forensic', 'file_integrity', 'filesystem', 'burned_metadata', 'steganography_analysis'],
    suggestedActions: ['verify_integrity', 'check_manipulation', 'analyze_timeline', 'generate_report'],
    uiTemplate: 'forensic'
  },
  
  scientific: {
    name: 'scientific',
    displayName: 'Scientific Data',
    description: 'Scientific instruments and research data',
    indicators: {
      required: ['scientific_data'],
      preferred: ['scientific', 'HDF5', 'NetCDF', 'FITS'],
      negative: []
    },
    priorityCategories: ['scientific_data', 'scientific', 'calculated', 'extended'],
    suggestedActions: ['explore_datasets', 'view_parameters', 'export_data'],
    uiTemplate: 'scientific'
  },
  
  web: {
    name: 'web',
    displayName: 'Web Content',
    description: 'Web-optimized images and social media',
    indicators: {
      preferred: ['web_metadata', 'social_media', 'normalized'],
      negative: ['scientific_data']
    },
    priorityCategories: ['web_metadata', 'social_media', 'normalized', 'image'],
    suggestedActions: ['check_optimization', 'view_social_tags', 'analyze_compression'],
    uiTemplate: 'standard'
  },
  
  mobile: {
    name: 'mobile',
    displayName: 'Mobile Photography',
    description: 'Smartphone and mobile device photos',
    indicators: {
      preferred: ['mobile_metadata', 'action_camera', 'computational_photography'],
      negative: ['scientific_data']
    },
    priorityCategories: ['mobile_metadata', 'exif', 'gps', 'image'],
    suggestedActions: ['view_device_info', 'check_processing', 'analyze_location'],
    uiTemplate: 'mobile'
  },
  
  professional: {
    name: 'professional',
    displayName: 'Professional Workflow',
    description: 'Professional photography and publishing',
    indicators: {
      preferred: ['workflow_dam', 'print_publishing', 'iptc', 'xmp'],
      negative: []
    },
    priorityCategories: ['workflow_dam', 'print_publishing', 'iptc', 'xmp', 'makernote'],
    suggestedActions: ['manage_workflow', 'check_metadata', 'prepare_publishing'],
    uiTemplate: 'professional'
  }
};

/**
 * Analyzes metadata to detect the most appropriate context
 */
export function detectFileContext(metadata: Record<string, any>): FileContext {
  const contexts: Array<{ profile: ContextProfile; score: number; indicators: string[] }> = [];
  
  // Analyze each context profile
  Object.values(CONTEXT_PROFILES).forEach(profile => {
    let score = 0;
    const foundIndicators: string[] = [];
    
    // Check required indicators
    if (profile.indicators.required) {
      const requiredFound = profile.indicators.required.every(indicator => {
        const found = hasIndicator(metadata, indicator);
        if (found) foundIndicators.push(indicator);
        return found;
      });
      if (!requiredFound) return; // Skip if required indicators not found
      score += 30;
    }
    
    // Check preferred indicators
    if (profile.indicators.preferred) {
      profile.indicators.preferred.forEach(indicator => {
        if (hasIndicator(metadata, indicator)) {
          foundIndicators.push(indicator);
          score += 10;
        }
      });
    }
    
    // Check negative indicators (reduce score)
    if (profile.indicators.negative) {
      profile.indicators.negative.forEach(indicator => {
        if (hasIndicator(metadata, indicator)) {
          score -= 15;
        }
      });
    }
    
    // Bonus for category richness
    const categoryCount = profile.priorityCategories.filter(cat => 
      metadata[cat] && typeof metadata[cat] === 'object' && Object.keys(metadata[cat]).length > 0
    ).length;
    score += categoryCount * 5;
    
    if (score > 0) {
      contexts.push({ profile, score, indicators: foundIndicators });
    }
  });
  
  // Sort by score and select best match
  contexts.sort((a, b) => b.score - a.score);
  
  if (contexts.length === 0) {
    // Default to generic context
    return {
      type: 'generic',
      confidence: 0.5,
      indicators: [],
      suggestedViews: ['all', 'technical'],
      priorityFields: ['summary', 'exif', 'image', 'filesystem']
    };
  }
  
  const bestMatch = contexts[0];
  const confidence = Math.min(bestMatch.score / 100, 1.0);
  
  // Generate warnings
  const warnings: string[] = [];
  if (confidence < 0.3) {
    warnings.push('Low confidence in context detection');
  }
  if (hasIndicator(metadata, 'manipulation_detection') && metadata.manipulation_detection?.suspicious) {
    warnings.push('Potential image manipulation detected');
  }
  if (hasIndicator(metadata, 'burned_metadata') && metadata.burned_metadata?.has_burned_metadata) {
    warnings.push('Burned-in metadata found - verify authenticity');
  }
  
  return {
    type: bestMatch.profile.name as any,
    confidence,
    indicators: bestMatch.indicators,
    suggestedViews: getSuggestedViews(bestMatch.profile),
    priorityFields: getPriorityFields(metadata, bestMatch.profile),
    warnings: warnings.length > 0 ? warnings : undefined
  };
}

/**
 * Checks if metadata contains a specific indicator
 */
function hasIndicator(metadata: Record<string, any>, indicator: string): boolean {
  // Direct category check
  if (metadata[indicator] && typeof metadata[indicator] === 'object') {
    return Object.keys(metadata[indicator]).length > 0;
  }
  
  // Field name search across all categories
  for (const [category, data] of Object.entries(metadata)) {
    if (typeof data === 'object' && data !== null) {
      if (Object.keys(data).some(key => 
        key.toLowerCase().includes(indicator.toLowerCase()) ||
        indicator.toLowerCase().includes(key.toLowerCase())
      )) {
        return true;
      }
    }
  }
  
  return false;
}

/**
 * Gets suggested views based on context
 */
function getSuggestedViews(profile: ContextProfile): string[] {
  const baseViews = ['all'];
  
  switch (profile.uiTemplate) {
    case 'forensic':
      return [...baseViews, 'forensic', 'advanced', 'technical'];
    case 'scientific':
      return [...baseViews, 'technical', 'raw'];
    case 'mobile':
      return [...baseViews, 'advanced'];
    case 'professional':
      return [...baseViews, 'technical', 'advanced'];
    default:
      return [...baseViews, 'technical'];
  }
}

/**
 * Gets priority fields based on context and available data
 */
function getPriorityFields(metadata: Record<string, any>, profile: ContextProfile): string[] {
  const priorityFields: string[] = [];
  
  // Add fields from priority categories that have data
  profile.priorityCategories.forEach(category => {
    if (metadata[category] && typeof metadata[category] === 'object') {
      const fields = Object.keys(metadata[category]);
      priorityFields.push(...fields.slice(0, 5)); // Top 5 fields per category
    }
  });
  
  // Add context-specific important fields
  const contextFields = getContextSpecificFields(profile.name, metadata);
  priorityFields.push(...contextFields);
  
  // Remove duplicates and return top 20
  return [...new Set(priorityFields)].slice(0, 20);
}

/**
 * Gets context-specific important fields
 */
function getContextSpecificFields(contextType: string, metadata: Record<string, any>): string[] {
  switch (contextType) {
    case 'photography':
      return ['Make', 'Model', 'LensModel', 'FocalLength', 'FNumber', 'ExposureTime', 'ISO', 'DateTimeOriginal'];
    case 'forensic':
      return ['MD5', 'SHA256', 'creation_timestamp', 'modification_timestamp', 'SerialNumber'];
    case 'scientific':
      return ['instrument', 'observation_date', 'processing_level', 'data_format'];
    case 'web':
      return ['optimization_level', 'compression_quality', 'color_profile'];
    case 'mobile':
      return ['device_model', 'software_version', 'computational_photography'];
    case 'professional':
      return ['workflow_id', 'color_space', 'print_profile', 'copyright'];
    default:
      return [];
  }
}

/**
 * Gets UI adaptation suggestions based on context
 */
export function getUIAdaptations(context: FileContext): {
  layout: 'standard' | 'forensic' | 'scientific' | 'compact';
  emphasizedSections: string[];
  hiddenSections: string[];
  suggestedActions: Array<{
    label: string;
    action: string;
    priority: 'high' | 'medium' | 'low';
  }>;
} {
  const profile = CONTEXT_PROFILES[context.type] || CONTEXT_PROFILES.photography;
  
  return {
    layout: profile.uiTemplate as any,
    emphasizedSections: profile.priorityCategories,
    hiddenSections: getHiddenSections(context.type),
    suggestedActions: profile.suggestedActions.map(action => ({
      label: formatActionLabel(action),
      action,
      priority: getActionPriority(action, context)
    }))
  };
}

function getHiddenSections(contextType: string): string[] {
  switch (contextType) {
    case 'photography':
      return ['scientific_data', 'forensic_security'];
    case 'forensic':
      return ['workflow_dam', 'print_publishing'];
    case 'scientific':
      return ['social_media', 'web_metadata'];
    case 'web':
      return ['scientific_data', 'makernote'];
    case 'mobile':
      return ['scientific_data', 'print_publishing'];
    default:
      return [];
  }
}

function formatActionLabel(action: string): string {
  return action.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}

function getActionPriority(action: string, context: FileContext): 'high' | 'medium' | 'low' {
  if (context.warnings && context.warnings.length > 0) {
    if (action.includes('verify') || action.includes('check')) return 'high';
  }
  if (context.confidence > 0.8) return 'high';
  if (context.confidence > 0.5) return 'medium';
  return 'low';
}
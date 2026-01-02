/**
 * Results Organization System
 * 
 * Provides organized results visualization with:
 * - Results categorization and sectioning
 * - Search and filtering functionality
 * - Export to multiple formats (JSON, CSV, PDF)
 * 
 * Validates: Requirements 2.5, 5.6
 */

// Section categories for organizing metadata results
export type SectionCategory = 
  | 'file_info'
  | 'integrity'
  | 'forensic'
  | 'camera'
  | 'location'
  | 'technical'
  | 'timestamps'
  | 'advanced'
  | 'other';

export interface MetadataSection {
  id: string;
  category: SectionCategory;
  title: string;
  description: string;
  icon: string;
  priority: number; // Lower = higher priority (shown first)
  fields: MetadataField[];
  isCollapsible: boolean;
  defaultExpanded: boolean;
}

export interface MetadataField {
  key: string;
  label: string;
  value: any;
  formattedValue: string;
  category: SectionCategory;
  isLocked: boolean;
  isCopyable: boolean;
  description?: string;
  searchableText: string;
}

export interface SearchFilter {
  query: string;
  categories: SectionCategory[];
  showLocked: boolean;
  showEmpty: boolean;
}

export interface OrganizedResults {
  sections: MetadataSection[];
  totalFields: number;
  visibleFields: number;
  lockedFields: number;
  searchMatches: number;
}

export type ExportFormat = 'json' | 'csv' | 'pdf';

export interface ExportOptions {
  format: ExportFormat;
  includeLockedFields: boolean;
  includeSectionHeaders: boolean;
  filename?: string;
}

export interface ExportResult {
  success: boolean;
  format: ExportFormat;
  filename: string;
  data: string | Blob;
  mimeType: string;
  size: number;
}

// Section configuration with metadata
const SECTION_CONFIG: Record<SectionCategory, { title: string; description: string; icon: string; priority: number }> = {
  file_info: {
    title: 'File Information',
    description: 'Basic file properties and identification',
    icon: 'FileText',
    priority: 1,
  },
  integrity: {
    title: 'File Integrity',
    description: 'Cryptographic hashes and verification data',
    icon: 'Hash',
    priority: 2,
  },
  forensic: {
    title: 'Forensic Evidence',
    description: 'Chain of custody and authenticity indicators',
    icon: 'ShieldCheck',
    priority: 3,
  },
  camera: {
    title: 'Camera & EXIF',
    description: 'Camera settings and capture information',
    icon: 'Camera',
    priority: 4,
  },
  location: {
    title: 'GPS Location',
    description: 'Geographic coordinates and location data',
    icon: 'MapPin',
    priority: 5,
  },
  timestamps: {
    title: 'Timestamps',
    description: 'Creation, modification, and access times',
    icon: 'Calendar',
    priority: 6,
  },
  technical: {
    title: 'Technical Metadata',
    description: 'IPTC, XMP, ICC profiles, and vendor data',
    icon: 'Tag',
    priority: 7,
  },
  advanced: {
    title: 'Advanced Analysis',
    description: 'AI detection, steganography, and manipulation analysis',
    icon: 'Eye',
    priority: 8,
  },
  other: {
    title: 'Other Metadata',
    description: 'Additional extracted metadata fields',
    icon: 'Database',
    priority: 9,
  },
};

// Field categorization rules
const FIELD_CATEGORY_RULES: Array<{ pattern: RegExp; category: SectionCategory }> = [
  { pattern: /^(filename|filesize|filetype|mime_type|file_size|file_name)$/i, category: 'file_info' },
  { pattern: /^(md5|sha256|sha1|hash|checksum|integrity)/i, category: 'integrity' },
  { pattern: /(forensic|authenticity|manipulation|chain_of_custody)/i, category: 'forensic' },
  { pattern: /(camera|make|model|lens|aperture|shutter|iso|focal|exposure|flash|white_balance)/i, category: 'camera' },
  { pattern: /(gps|latitude|longitude|altitude|location|coordinates|map)/i, category: 'location' },
  { pattern: /(date|time|created|modified|accessed|timestamp)/i, category: 'timestamps' },
  { pattern: /(iptc|xmp|icc|makernote|interop|thumbnail|namespace)/i, category: 'technical' },
  { pattern: /(ai_|steganography|manipulation_detection|hidden_data)/i, category: 'advanced' },
];

/**
 * Categorize a field based on its key
 */
export function categorizeField(key: string): SectionCategory {
  const lowerKey = key.toLowerCase();
  
  for (const rule of FIELD_CATEGORY_RULES) {
    if (rule.pattern.test(lowerKey)) {
      return rule.category;
    }
  }
  
  return 'other';
}

/**
 * Format a field label for display
 */
export function formatFieldLabel(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, c => c.toUpperCase())
    .trim();
}

/**
 * Format a field value for display
 */
export function formatFieldValue(value: any): string {
  if (value === null || value === undefined) return 'N/A';
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') {
    if (value instanceof Date) return value.toISOString();
    if (value.rawValue !== undefined) return String(value.rawValue);
    try {
      return JSON.stringify(value);
    } catch {
      return '[Complex Object]';
    }
  }
  return String(value);
}

/**
 * Check if a field value indicates it's locked
 */
export function isFieldLocked(value: any): boolean {
  if (typeof value === 'string') {
    return value === 'LOCKED' || 
           value === 'LOCKED_UPGRADE_TO_VIEW' || 
           value.startsWith('LOCKED');
  }
  return false;
}

/**
 * Create searchable text from a field
 */
export function createSearchableText(key: string, value: any): string {
  const formattedValue = formatFieldValue(value);
  return `${key} ${formatFieldLabel(key)} ${formattedValue}`.toLowerCase();
}

/**
 * Convert raw metadata to organized MetadataField array
 */
export function extractFields(
  data: Record<string, any>,
  prefix: string = ''
): MetadataField[] {
  const fields: MetadataField[] = [];
  
  if (!data || typeof data !== 'object') return fields;
  
  for (const [key, value] of Object.entries(data)) {
    // Skip internal/private fields
    if (key.startsWith('_') || key === 'data_base64') continue;
    
    const fullKey = prefix ? `${prefix}.${key}` : key;
    
    // Recursively handle nested objects (but not arrays)
    if (value && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      fields.push(...extractFields(value, fullKey));
    } else {
      const category = categorizeField(fullKey);
      const locked = isFieldLocked(value);
      
      fields.push({
        key: fullKey,
        label: formatFieldLabel(key),
        value,
        formattedValue: formatFieldValue(value),
        category,
        isLocked: locked,
        isCopyable: !locked && typeof value !== 'object',
        searchableText: createSearchableText(fullKey, value),
      });
    }
  }
  
  return fields;
}

/**
 * Organize metadata into sections
 */
export function organizeMetadata(
  metadata: Record<string, any>,
  filter?: SearchFilter
): OrganizedResults {
  // Extract all fields from metadata
  const allFields = extractFields(metadata);
  
  // Apply search filter
  let filteredFields = allFields;
  let searchMatches = allFields.length;
  
  if (filter) {
    filteredFields = allFields.filter(field => {
      // Category filter
      if (filter.categories.length > 0 && !filter.categories.includes(field.category)) {
        return false;
      }
      
      // Locked filter
      if (!filter.showLocked && field.isLocked) {
        return false;
      }
      
      // Empty filter
      if (!filter.showEmpty && (field.value === null || field.value === undefined || field.value === '')) {
        return false;
      }
      
      // Search query
      if (filter.query) {
        const queryLower = filter.query.toLowerCase();
        if (!field.searchableText.includes(queryLower)) {
          return false;
        }
      }
      
      return true;
    });
    
    searchMatches = filteredFields.length;
  }
  
  // Group fields by category
  const fieldsByCategory = new Map<SectionCategory, MetadataField[]>();
  
  for (const field of filteredFields) {
    const existing = fieldsByCategory.get(field.category) || [];
    existing.push(field);
    fieldsByCategory.set(field.category, existing);
  }
  
  // Create sections
  const sections: MetadataSection[] = [];
  
  for (const [category, fields] of fieldsByCategory) {
    const config = SECTION_CONFIG[category];
    
    sections.push({
      id: category,
      category,
      title: config.title,
      description: config.description,
      icon: config.icon,
      priority: config.priority,
      fields,
      isCollapsible: true,
      defaultExpanded: config.priority <= 5, // Expand high-priority sections by default
    });
  }
  
  // Sort sections by priority
  sections.sort((a, b) => a.priority - b.priority);
  
  // Calculate totals
  const totalFields = allFields.length;
  const visibleFields = filteredFields.length;
  const lockedFields = allFields.filter(f => f.isLocked).length;
  
  return {
    sections,
    totalFields,
    visibleFields,
    lockedFields,
    searchMatches,
  };
}

/**
 * Search within organized results
 */
export function searchResults(
  results: OrganizedResults,
  query: string
): OrganizedResults {
  if (!query.trim()) return results;
  
  const queryLower = query.toLowerCase();
  
  const filteredSections = results.sections
    .map(section => ({
      ...section,
      fields: section.fields.filter(field => 
        field.searchableText.includes(queryLower)
      ),
    }))
    .filter(section => section.fields.length > 0);
  
  const searchMatches = filteredSections.reduce(
    (sum, section) => sum + section.fields.length,
    0
  );
  
  return {
    ...results,
    sections: filteredSections,
    visibleFields: searchMatches,
    searchMatches,
  };
}

/**
 * Export results to JSON format
 */
export function exportToJSON(
  results: OrganizedResults,
  options: ExportOptions
): ExportResult {
  const exportData: Record<string, any> = {};
  
  for (const section of results.sections) {
    const sectionData: Record<string, any> = {};
    
    for (const field of section.fields) {
      if (!options.includeLockedFields && field.isLocked) continue;
      sectionData[field.key] = field.value;
    }
    
    if (Object.keys(sectionData).length > 0) {
      if (options.includeSectionHeaders) {
        exportData[section.title] = sectionData;
      } else {
        Object.assign(exportData, sectionData);
      }
    }
  }
  
  const jsonString = JSON.stringify(exportData, null, 2);
  const filename = options.filename || `metadata_export_${Date.now()}.json`;
  
  return {
    success: true,
    format: 'json',
    filename,
    data: jsonString,
    mimeType: 'application/json',
    size: new Blob([jsonString]).size,
  };
}

/**
 * Export results to CSV format
 */
export function exportToCSV(
  results: OrganizedResults,
  options: ExportOptions
): ExportResult {
  const rows: string[][] = [];
  
  // Header row
  if (options.includeSectionHeaders) {
    rows.push(['Section', 'Field', 'Value']);
  } else {
    rows.push(['Field', 'Value']);
  }
  
  // Data rows
  for (const section of results.sections) {
    for (const field of section.fields) {
      if (!options.includeLockedFields && field.isLocked) continue;
      
      // Escape CSV values
      const escapedValue = field.formattedValue
        .replace(/"/g, '""')
        .replace(/\n/g, ' ');
      
      if (options.includeSectionHeaders) {
        rows.push([section.title, field.label, `"${escapedValue}"`]);
      } else {
        rows.push([field.label, `"${escapedValue}"`]);
      }
    }
  }
  
  const csvString = rows.map(row => row.join(',')).join('\n');
  const filename = options.filename || `metadata_export_${Date.now()}.csv`;
  
  return {
    success: true,
    format: 'csv',
    filename,
    data: csvString,
    mimeType: 'text/csv',
    size: new Blob([csvString]).size,
  };
}

/**
 * Export results to PDF format (generates HTML for PDF conversion)
 */
export function exportToPDF(
  results: OrganizedResults,
  options: ExportOptions
): ExportResult {
  // Generate HTML content for PDF
  let html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Metadata Export Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
    h1 { color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
    h2 { color: #1e40af; margin-top: 30px; }
    .section { margin-bottom: 30px; }
    .field { display: flex; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
    .field-label { font-weight: 600; width: 40%; color: #4b5563; }
    .field-value { width: 60%; word-break: break-word; }
    .locked { color: #9ca3af; font-style: italic; }
    .summary { background: #f3f4f6; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
    .summary-item { display: inline-block; margin-right: 30px; }
    .summary-label { font-size: 12px; color: #6b7280; }
    .summary-value { font-size: 24px; font-weight: bold; color: #2563eb; }
    @media print { body { margin: 20px; } }
  </style>
</head>
<body>
  <h1>Metadata Export Report</h1>
  <div class="summary">
    <div class="summary-item">
      <div class="summary-label">Total Fields</div>
      <div class="summary-value">${results.totalFields}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">Visible Fields</div>
      <div class="summary-value">${results.visibleFields}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">Sections</div>
      <div class="summary-value">${results.sections.length}</div>
    </div>
  </div>
`;

  for (const section of results.sections) {
    const visibleFields = options.includeLockedFields 
      ? section.fields 
      : section.fields.filter(f => !f.isLocked);
    
    if (visibleFields.length === 0) continue;
    
    html += `
  <div class="section">
    <h2>${section.title}</h2>
    <p style="color: #6b7280; font-size: 14px;">${section.description}</p>
`;
    
    for (const field of visibleFields) {
      const valueClass = field.isLocked ? 'field-value locked' : 'field-value';
      html += `
    <div class="field">
      <div class="field-label">${field.label}</div>
      <div class="${valueClass}">${field.isLocked ? '[Locked]' : escapeHtml(field.formattedValue)}</div>
    </div>
`;
    }
    
    html += `  </div>\n`;
  }
  
  html += `
  <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 12px;">
    Generated on ${new Date().toISOString()}
  </footer>
</body>
</html>
`;

  const filename = options.filename || `metadata_export_${Date.now()}.html`;
  
  return {
    success: true,
    format: 'pdf',
    filename,
    data: html,
    mimeType: 'text/html',
    size: new Blob([html]).size,
  };
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Export results in the specified format
 */
export function exportResults(
  results: OrganizedResults,
  options: ExportOptions
): ExportResult {
  switch (options.format) {
    case 'json':
      return exportToJSON(results, options);
    case 'csv':
      return exportToCSV(results, options);
    case 'pdf':
      return exportToPDF(results, options);
    default:
      return {
        success: false,
        format: options.format,
        filename: '',
        data: '',
        mimeType: '',
        size: 0,
      };
  }
}

/**
 * Download export result as a file
 */
export function downloadExport(result: ExportResult): void {
  if (!result.success) return;
  
  const blob = typeof result.data === 'string' 
    ? new Blob([result.data], { type: result.mimeType })
    : result.data;
  
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = result.filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Get available export formats
 */
export function getAvailableExportFormats(): ExportFormat[] {
  return ['json', 'csv', 'pdf'];
}

/**
 * Check if an export format is available
 */
export function isExportFormatAvailable(format: ExportFormat): boolean {
  return getAvailableExportFormats().includes(format);
}

/**
 * Get export format metadata
 */
export function getExportFormatInfo(format: ExportFormat): { 
  name: string; 
  description: string; 
  mimeType: string; 
  extension: string;
} {
  const formats: Record<ExportFormat, { name: string; description: string; mimeType: string; extension: string }> = {
    json: {
      name: 'JSON',
      description: 'JavaScript Object Notation - machine-readable format',
      mimeType: 'application/json',
      extension: '.json',
    },
    csv: {
      name: 'CSV',
      description: 'Comma-Separated Values - spreadsheet compatible',
      mimeType: 'text/csv',
      extension: '.csv',
    },
    pdf: {
      name: 'PDF',
      description: 'Portable Document Format - printable report',
      mimeType: 'application/pdf',
      extension: '.pdf',
    },
  };
  
  return formats[format];
}

/**
 * Get all section categories
 */
export function getAllCategories(): SectionCategory[] {
  return Object.keys(SECTION_CONFIG) as SectionCategory[];
}

/**
 * Get section configuration
 */
export function getSectionConfig(category: SectionCategory) {
  return SECTION_CONFIG[category];
}

/**
 * Create default search filter
 */
export function createDefaultFilter(): SearchFilter {
  return {
    query: '',
    categories: [],
    showLocked: true,
    showEmpty: false,
  };
}

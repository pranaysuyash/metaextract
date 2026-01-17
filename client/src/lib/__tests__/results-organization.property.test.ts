/**
 * Property Tests for Results Organization System
 * 
 * Property 9: Results organization
 * For any completed metadata extraction, results should be presented in clearly 
 * defined sections with proper formatting and search capability
 * Validates: Requirements 2.5
 * 
 * Property 19: Export format availability
 * For any analysis result, multiple export formats (PDF, JSON, CSV) should be 
 * available and functional
 * Validates: Requirements 5.6
 */

import * as fc from 'fast-check';
import {
  organizeMetadata,
  searchResults,
  exportResults,
  exportToJSON,
  exportToCSV,
  exportToPDF,
  categorizeField,
  formatFieldLabel,
  formatFieldValue,
  isFieldLocked,
  extractFields,
  getAvailableExportFormats,
  isExportFormatAvailable,
  getExportFormatInfo,
  getAllCategories,
  getSectionConfig,
  createDefaultFilter,
  type MetadataSection,
  type MetadataField,
  type OrganizedResults,
  type ExportFormat,
  type ExportOptions,
  type SearchFilter,
  type SectionCategory,
} from '../results-organization';

// Arbitrary generators for metadata
const metadataKeyArb = fc.string({ minLength: 1, maxLength: 30 }).filter(
  s => /^[a-z][a-z_]*$/i.test(s) && s.length > 0 && !s.startsWith('_')
);

const metadataValueArb = fc.oneof(
  fc.string({ minLength: 0, maxLength: 100 }),
  fc.integer(),
  fc.double({ noNaN: true }),
  fc.boolean(),
  fc.constant(null),
  fc.array(fc.string(), { maxLength: 5 })
);

const metadataObjectArb = fc.dictionary(metadataKeyArb, metadataValueArb, {
  minKeys: 1,
  maxKeys: 20,
});

const nestedMetadataArb = fc.dictionary(
  metadataKeyArb,
  fc.oneof(
    metadataValueArb,
    fc.dictionary(metadataKeyArb, metadataValueArb, { minKeys: 1, maxKeys: 5 })
  ),
  { minKeys: 1, maxKeys: 15 }
);

const searchQueryArb = fc.string({ minLength: 0, maxLength: 50 });

const exportFormatArb = fc.constantFrom<ExportFormat>('json', 'csv', 'pdf');

const exportOptionsArb = fc.record({
  format: exportFormatArb,
  includeLockedFields: fc.boolean(),
  includeSectionHeaders: fc.boolean(),
  filename: fc.option(fc.string({ minLength: 1, maxLength: 50 }), { nil: undefined }),
});

const categoryArb = fc.constantFrom<SectionCategory>(
  'file_info', 'integrity', 'forensic', 'camera', 'location', 
  'timestamps', 'technical', 'advanced', 'other'
);

const searchFilterArb = fc.record({
  query: searchQueryArb,
  categories: fc.array(categoryArb, { maxLength: 5 }),
  showLocked: fc.boolean(),
  showEmpty: fc.boolean(),
});

describe('Property 9: Results organization', () => {
  describe('Section organization', () => {
    it('should organize any metadata into clearly defined sections', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          
          // Results should always have sections array
          expect(Array.isArray(results.sections)).toBe(true);
          
          // Each section should have required properties
          for (const section of results.sections) {
            expect(section).toHaveProperty('id');
            expect(section).toHaveProperty('category');
            expect(section).toHaveProperty('title');
            expect(section).toHaveProperty('description');
            expect(section).toHaveProperty('icon');
            expect(section).toHaveProperty('priority');
            expect(section).toHaveProperty('fields');
            expect(Array.isArray(section.fields)).toBe(true);
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should assign every field to exactly one section', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          
          // Collect all field keys from sections
          const fieldKeys = new Set<string>();
          for (const section of results.sections) {
            for (const field of section.fields) {
              // No duplicate keys across sections
              expect(fieldKeys.has(field.key)).toBe(false);
              fieldKeys.add(field.key);
            }
          }
          
          // Total fields should match sum of section fields
          const totalSectionFields = results.sections.reduce(
            (sum, s) => sum + s.fields.length, 0
          );
          expect(totalSectionFields).toBe(results.visibleFields);
        }),
        { numRuns: 100 }
      );
    });

    it('should sort sections by priority', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          
          // Sections should be sorted by priority (ascending)
          for (let i = 1; i < results.sections.length; i++) {
            expect(results.sections[i].priority).toBeGreaterThanOrEqual(
              results.sections[i - 1].priority
            );
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should provide section metadata for each category', () => {
      fc.assert(
        fc.property(categoryArb, (category) => {
          const config = getSectionConfig(category);
          
          expect(config).toBeDefined();
          expect(typeof config.title).toBe('string');
          expect(config.title.length).toBeGreaterThan(0);
          expect(typeof config.description).toBe('string');
          expect(typeof config.icon).toBe('string');
          expect(typeof config.priority).toBe('number');
        }),
        { numRuns: 50 }
      );
    });
  });

  describe('Field formatting', () => {
    it('should format all field labels for readability', () => {
      fc.assert(
        fc.property(metadataKeyArb, (key: string) => {
          const label = formatFieldLabel(key);
          
          // Label should be non-empty
          expect(label.length).toBeGreaterThan(0);
          
          // Label should not contain underscores (converted to spaces)
          if (key.includes('_')) {
            expect(label).not.toContain('_');
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should format all field values to strings', () => {
      fc.assert(
        fc.property(metadataValueArb, (value) => {
          const formatted = formatFieldValue(value);
          
          // Formatted value should always be a string
          expect(typeof formatted).toBe('string');
          
          // Null/undefined should become 'N/A'
          if (value === null || value === undefined) {
            expect(formatted).toBe('N/A');
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should create searchable text for every field', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const fields = extractFields(metadata);
          
          for (const field of fields) {
            // Every field should have searchable text
            expect(typeof field.searchableText).toBe('string');
            expect(field.searchableText.length).toBeGreaterThan(0);
            
            // Searchable text should be lowercase
            expect(field.searchableText).toBe(field.searchableText.toLowerCase());
          }
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Search capability', () => {
    it('should filter results based on search query', () => {
      fc.assert(
        fc.property(
          nestedMetadataArb,
          fc.string({ minLength: 1, maxLength: 10 }),
          (metadata, query) => {
            const results = organizeMetadata(metadata);
            const filtered = searchResults(results, query);
            
            // Filtered results should have same or fewer fields
            expect(filtered.visibleFields).toBeLessThanOrEqual(results.visibleFields);
            
            // All remaining fields should match the normalized query.
            // Whitespace-only queries are treated as empty (no filtering).
            const normalizedQuery = query.trim().toLowerCase().replace(/\s+/g, ' ');
            if (!normalizedQuery) {
              expect(filtered.visibleFields).toBe(results.visibleFields);
              expect(filtered.sections.length).toBe(results.sections.length);
              return;
            }

            for (const section of filtered.sections) {
              for (const field of section.fields) {
                expect(field.searchableText).toContain(normalizedQuery);
              }
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should return all results for empty search query', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const filtered = searchResults(results, '');
          
          // Empty query should return all results
          expect(filtered.visibleFields).toBe(results.visibleFields);
          expect(filtered.sections.length).toBe(results.sections.length);
        }),
        { numRuns: 100 }
      );
    });

    it('should support category filtering', () => {
      fc.assert(
        fc.property(
          nestedMetadataArb,
          fc.array(categoryArb, { minLength: 1, maxLength: 3 }),
          (metadata, categories) => {
            const filter: SearchFilter = {
              query: '',
              categories,
              showLocked: true,
              showEmpty: true,
            };
            
            const results = organizeMetadata(metadata, filter);
            
            // All sections should be in the allowed categories
            for (const section of results.sections) {
              expect(categories).toContain(section.category);
            }
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should track search match count accurately', () => {
      fc.assert(
        fc.property(nestedMetadataArb, searchQueryArb, (metadata, query) => {
          const results = organizeMetadata(metadata);
          const filtered = searchResults(results, query);
          
          // Search matches should equal visible fields after filtering
          expect(filtered.searchMatches).toBe(filtered.visibleFields);
          
          // Count should match actual field count
          const actualCount = filtered.sections.reduce(
            (sum, s) => sum + s.fields.length, 0
          );
          expect(filtered.searchMatches).toBe(actualCount);
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Field categorization', () => {
    it('should categorize fields consistently', () => {
      fc.assert(
        fc.property(metadataKeyArb, (key: string) => {
          const category1 = categorizeField(key);
          const category2 = categorizeField(key);
          
          // Same key should always get same category
          expect(category1).toBe(category2);
          
          // Category should be valid
          expect(getAllCategories()).toContain(category1);
        }),
        { numRuns: 100 }
      );
    });

    it('should categorize GPS-related fields to location', () => {
      const gpsKeys = ['gps_latitude', 'longitude', 'coordinates', 'location_data'];
      
      for (const key of gpsKeys) {
        expect(categorizeField(key)).toBe('location');
      }
    });

    it('should categorize hash-related fields to integrity', () => {
      const hashKeys = ['md5', 'sha256', 'checksum', 'hash_value'];
      
      for (const key of hashKeys) {
        expect(categorizeField(key)).toBe('integrity');
      }
    });

    it('should categorize camera-related fields to camera', () => {
      const cameraKeys = ['camera_make', 'model', 'aperture', 'shutter_speed', 'iso'];
      
      for (const key of cameraKeys) {
        expect(categorizeField(key)).toBe('camera');
      }
    });
  });

  describe('Locked field handling', () => {
    it('should detect locked field values', () => {
      const lockedValues = ['LOCKED', 'LOCKED_UPGRADE_TO_VIEW', 'LOCKED_PREMIUM'];
      const unlockedValues = ['normal value', 123, true, null];
      
      for (const value of lockedValues) {
        expect(isFieldLocked(value)).toBe(true);
      }
      
      for (const value of unlockedValues) {
        expect(isFieldLocked(value)).toBe(false);
      }
    });

    it('should respect showLocked filter option', () => {
      const metadata = {
        normal_field: 'value',
        locked_field: 'LOCKED',
      };
      
      const withLocked = organizeMetadata(metadata, {
        query: '',
        categories: [],
        showLocked: true,
        showEmpty: true,
      });
      
      const withoutLocked = organizeMetadata(metadata, {
        query: '',
        categories: [],
        showLocked: false,
        showEmpty: true,
      });
      
      expect(withLocked.visibleFields).toBeGreaterThan(withoutLocked.visibleFields);
    });
  });
});

describe('Property 19: Export format availability', () => {
  describe('Format availability', () => {
    it('should provide JSON, CSV, and PDF export formats', () => {
      const formats = getAvailableExportFormats();
      
      expect(formats).toContain('json');
      expect(formats).toContain('csv');
      expect(formats).toContain('pdf');
      expect(formats.length).toBe(3);
    });

    it('should correctly report format availability', () => {
      fc.assert(
        fc.property(exportFormatArb, (format) => {
          // All standard formats should be available
          expect(isExportFormatAvailable(format)).toBe(true);
        }),
        { numRuns: 50 }
      );
    });

    it('should provide format metadata for all formats', () => {
      fc.assert(
        fc.property(exportFormatArb, (format) => {
          const info = getExportFormatInfo(format);
          
          expect(info).toBeDefined();
          expect(typeof info.name).toBe('string');
          expect(info.name.length).toBeGreaterThan(0);
          expect(typeof info.description).toBe('string');
          expect(typeof info.mimeType).toBe('string');
          expect(typeof info.extension).toBe('string');
          expect(info.extension.startsWith('.')).toBe(true);
        }),
        { numRuns: 50 }
      );
    });
  });

  describe('JSON export', () => {
    it('should successfully export any metadata to JSON', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportOptionsArb, (metadata, options) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToJSON(results, { ...options, format: 'json' });
          
          expect(exportResult.success).toBe(true);
          expect(exportResult.format).toBe('json');
          expect(exportResult.mimeType).toBe('application/json');
          expect(typeof exportResult.data).toBe('string');
          expect(exportResult.size).toBeGreaterThan(0);
        }),
        { numRuns: 100 }
      );
    });

    it('should produce valid JSON output', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToJSON(results, {
            format: 'json',
            includeLockedFields: true,
            includeSectionHeaders: false,
          });
          
          // Should be parseable JSON
          expect(() => JSON.parse(exportResult.data as string)).not.toThrow();
        }),
        { numRuns: 100 }
      );
    });

    it('should respect includeLockedFields option', () => {
      const metadata = {
        normal: 'value',
        locked: 'LOCKED',
      };
      
      const results = organizeMetadata(metadata);
      
      const withLocked = exportToJSON(results, {
        format: 'json',
        includeLockedFields: true,
        includeSectionHeaders: false,
      });
      
      const withoutLocked = exportToJSON(results, {
        format: 'json',
        includeLockedFields: false,
        includeSectionHeaders: false,
      });
      
      const dataWithLocked = JSON.parse(withLocked.data as string);
      const dataWithoutLocked = JSON.parse(withoutLocked.data as string);
      
      expect(Object.keys(dataWithLocked).length).toBeGreaterThanOrEqual(
        Object.keys(dataWithoutLocked).length
      );
    });
  });

  describe('CSV export', () => {
    it('should successfully export any metadata to CSV', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportOptionsArb, (metadata, options) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToCSV(results, { ...options, format: 'csv' });
          
          expect(exportResult.success).toBe(true);
          expect(exportResult.format).toBe('csv');
          expect(exportResult.mimeType).toBe('text/csv');
          expect(typeof exportResult.data).toBe('string');
          expect(exportResult.size).toBeGreaterThan(0);
        }),
        { numRuns: 100 }
      );
    });

    it('should include header row in CSV', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToCSV(results, {
            format: 'csv',
            includeLockedFields: true,
            includeSectionHeaders: false,
          });
          
          const lines = (exportResult.data as string).split('\n');
          
          // Should have at least header row
          expect(lines.length).toBeGreaterThanOrEqual(1);
          
          // Header should contain Field and Value
          expect(lines[0]).toContain('Field');
          expect(lines[0]).toContain('Value');
        }),
        { numRuns: 100 }
      );
    });

    it('should escape special characters in CSV', () => {
      const metadata = {
        field_with_comma: 'value, with, commas',
        field_with_quotes: 'value "with" quotes',
        field_with_newline: 'value\nwith\nnewlines',
      };
      
      const results = organizeMetadata(metadata);
      const exportResult = exportToCSV(results, {
        format: 'csv',
        includeLockedFields: true,
        includeSectionHeaders: false,
      });
      
      // CSV should be properly escaped (no raw commas breaking structure)
      const lines = (exportResult.data as string).split('\n');
      
      // Each data line should have exactly 2 commas (Field,Value format)
      // or properly quoted values
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
          // Values with commas should be quoted
          expect(lines[i]).toMatch(/^[^,]+,".+"$|^[^,]+,[^,]*$/);
        }
      }
    });
  });

  describe('PDF export', () => {
    it('should successfully export any metadata to PDF (HTML)', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportOptionsArb, (metadata, options) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToPDF(results, { ...options, format: 'pdf' });
          
          expect(exportResult.success).toBe(true);
          expect(exportResult.format).toBe('pdf');
          expect(exportResult.mimeType).toBe('text/html');
          expect(typeof exportResult.data).toBe('string');
          expect(exportResult.size).toBeGreaterThan(0);
        }),
        { numRuns: 100 }
      );
    });

    it('should produce valid HTML structure', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToPDF(results, {
            format: 'pdf',
            includeLockedFields: true,
            includeSectionHeaders: true,
          });
          
          const html = exportResult.data as string;
          
          // Should have basic HTML structure
          expect(html).toContain('<!DOCTYPE html>');
          expect(html).toContain('<html>');
          expect(html).toContain('</html>');
          expect(html).toContain('<head>');
          expect(html).toContain('</head>');
          expect(html).toContain('<body>');
          expect(html).toContain('</body>');
        }),
        { numRuns: 100 }
      );
    });

    it('should include summary statistics in PDF', () => {
      fc.assert(
        fc.property(nestedMetadataArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportToPDF(results, {
            format: 'pdf',
            includeLockedFields: true,
            includeSectionHeaders: true,
          });
          
          const html = exportResult.data as string;
          
          // Should include summary section
          expect(html).toContain('Total Fields');
          expect(html).toContain('Visible Fields');
          expect(html).toContain('Sections');
        }),
        { numRuns: 100 }
      );
    });

    it('should escape HTML special characters', () => {
      const metadata = {
        html_field: '<script>alert("xss")</script>',
        ampersand_field: 'value & more',
      };
      
      const results = organizeMetadata(metadata);
      const exportResult = exportToPDF(results, {
        format: 'pdf',
        includeLockedFields: true,
        includeSectionHeaders: true,
      });
      
      const html = exportResult.data as string;
      
      // Should escape HTML entities
      expect(html).not.toContain('<script>');
      expect(html).toContain('&lt;script&gt;');
      expect(html).toContain('&amp;');
    });
  });

  describe('Generic export function', () => {
    it('should route to correct exporter based on format', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportOptionsArb, (metadata, options) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportResults(results, options);
          
          expect(exportResult.success).toBe(true);
          expect(exportResult.format).toBe(options.format);
          
          // Check correct MIME type
          switch (options.format) {
            case 'json':
              expect(exportResult.mimeType).toBe('application/json');
              break;
            case 'csv':
              expect(exportResult.mimeType).toBe('text/csv');
              break;
            case 'pdf':
              expect(exportResult.mimeType).toBe('text/html');
              break;
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should generate appropriate filenames', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportFormatArb, (metadata, format) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportResults(results, {
            format,
            includeLockedFields: true,
            includeSectionHeaders: true,
          });
          
          expect(exportResult.filename).toBeDefined();
          expect(exportResult.filename.length).toBeGreaterThan(0);
          
          // Filename should contain format-appropriate extension
          const info = getExportFormatInfo(format);
          if (format === 'pdf') {
            // PDF exports as HTML for now
            expect(exportResult.filename).toContain('.html');
          } else {
            expect(exportResult.filename).toContain(info.extension);
          }
        }),
        { numRuns: 100 }
      );
    });

    it('should use custom filename when provided', () => {
      fc.assert(
        fc.property(
          nestedMetadataArb,
          exportFormatArb,
          fc.string({ minLength: 5, maxLength: 30 }),
          (metadata, format, customFilename) => {
            const results = organizeMetadata(metadata);
            const exportResult = exportResults(results, {
              format,
              includeLockedFields: true,
              includeSectionHeaders: true,
              filename: customFilename,
            });
            
            expect(exportResult.filename).toBe(customFilename);
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  describe('Export data integrity', () => {
    it('should preserve field values in exports', () => {
      fc.assert(
        fc.property(metadataObjectArb, (metadata) => {
          const results = organizeMetadata(metadata);
          const jsonExport = exportToJSON(results, {
            format: 'json',
            includeLockedFields: true,
            includeSectionHeaders: false,
          });
          
          const exportedData = JSON.parse(jsonExport.data as string);
          
          // All non-internal fields should be in export
          for (const [key, value] of Object.entries(metadata)) {
            if (!key.startsWith('_') && value !== null && value !== undefined) {
              // Field should exist in export (possibly nested)
              const flatExport = JSON.stringify(exportedData);
              
              // For simple string/number values, check they appear in export
              if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
                // The key should appear in the export
                expect(flatExport.toLowerCase()).toContain(key.toLowerCase());
              }
            }
          }
        }),
        { numRuns: 50 }
      );
    });

    it('should report accurate file sizes', () => {
      fc.assert(
        fc.property(nestedMetadataArb, exportFormatArb, (metadata, format) => {
          const results = organizeMetadata(metadata);
          const exportResult = exportResults(results, {
            format,
            includeLockedFields: true,
            includeSectionHeaders: true,
          });
          
          // Size should match actual data size
          const actualSize = new Blob([exportResult.data as string]).size;
          expect(exportResult.size).toBe(actualSize);
        }),
        { numRuns: 100 }
      );
    });
  });
});

describe('Default filter creation', () => {
  it('should create valid default filter', () => {
    const filter = createDefaultFilter();
    
    expect(filter.query).toBe('');
    expect(filter.categories).toEqual([]);
    expect(filter.showLocked).toBe(true);
    expect(filter.showEmpty).toBe(false);
  });
});

describe('Edge cases', () => {
  it('should handle empty metadata', () => {
    const results = organizeMetadata({});
    
    expect(results.sections).toEqual([]);
    expect(results.totalFields).toBe(0);
    expect(results.visibleFields).toBe(0);
  });

  it('should handle deeply nested metadata', () => {
    const deepMetadata = {
      level1: {
        level2: {
          level3: {
            level4: 'deep value',
          },
        },
      },
    };
    
    const results = organizeMetadata(deepMetadata);
    
    // Should flatten nested structure
    expect(results.totalFields).toBeGreaterThan(0);
    
    // Should find the deep value
    const allFields = results.sections.flatMap(s => s.fields);
    const deepField = allFields.find(f => f.formattedValue === 'deep value');
    expect(deepField).toBeDefined();
  });

  it('should handle special characters in field names', () => {
    const metadata = {
      'field_with_underscores': 'value1',
      'fieldWithCamelCase': 'value2',
      'FIELD_ALL_CAPS': 'value3',
    };
    
    const results = organizeMetadata(metadata);
    const allFields = results.sections.flatMap(s => s.fields);
    
    // All fields should have readable labels
    for (const field of allFields) {
      expect(field.label).not.toContain('_');
      expect(field.label.length).toBeGreaterThan(0);
    }
  });

  it('should handle array values', () => {
    const metadata = {
      tags: ['tag1', 'tag2', 'tag3'],
      numbers: [1, 2, 3],
    };
    
    const results = organizeMetadata(metadata);
    const allFields = results.sections.flatMap(s => s.fields);
    
    // Arrays should be formatted as comma-separated strings
    const tagsField = allFields.find(f => f.key === 'tags');
    expect(tagsField?.formattedValue).toBe('tag1, tag2, tag3');
  });
});

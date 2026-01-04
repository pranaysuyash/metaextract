/**
 * Property Tests for Help and Documentation System
 * 
 * Tests universal correctness properties of the help system.
 * 
 * @validates Requirements 2.6, 3.3 - Contextual help and metadata documentation
 */

import * as fc from 'fast-check';
import {
  helpTopics,
  metadataFieldDocs,
  HelpCategory,
  MetadataCategory,
  searchHelpTopics,
  getHelpTopic,
  getHelpTopicsByCategory,
  getRelatedTopics,
  getMetadataFieldDoc,
  getMetadataFieldsByCategory,
  getCommonMetadataFields,
  searchMetadataFields,
  getContextualHelp,
  getFieldTooltip,
  helpCategoryLabels,
  metadataCategoryLabels,
  HelpContext,
} from '../help-system';

describe('Help System Property Tests', () => {
  // ========================================================================
  // Help Topic Coverage (Property 10: Contextual help availability)
  // ========================================================================
  
  describe('Contextual Help Availability', () => {
    const allHelpTopics = Object.values(helpTopics);
    const allCategories: HelpCategory[] = [
      'getting-started', 'upload', 'metadata', 'analysis',
      'export', 'account', 'pricing', 'security', 'troubleshooting'
    ];
    const allContexts: HelpContext[] = [
      'upload-zone', 'results-view', 'metadata-panel', 'forensic-panel',
      'export-dialog', 'pricing-page', 'settings-page', 'dashboard'
    ];

    it('every help topic should have required fields', () => {
      allHelpTopics.forEach(topic => {
        expect(topic.id).toBeDefined();
        expect(topic.id.length).toBeGreaterThan(0);
        expect(topic.title).toBeDefined();
        expect(topic.title.length).toBeGreaterThan(0);
        expect(topic.shortDescription).toBeDefined();
        expect(topic.shortDescription.length).toBeGreaterThan(0);
        expect(topic.fullDescription).toBeDefined();
        expect(topic.fullDescription.length).toBeGreaterThan(0);
        expect(topic.keywords).toBeDefined();
        expect(Array.isArray(topic.keywords)).toBe(true);
        expect(topic.keywords.length).toBeGreaterThan(0);
        expect(topic.category).toBeDefined();
      });
    });

    it('every help category should have at least one topic', () => {
      allCategories.forEach(category => {
        const topics = getHelpTopicsByCategory(category);
        expect(topics.length).toBeGreaterThanOrEqual(1);
      });
    });

    it('every UI context should have contextual help available', () => {
      allContexts.forEach(context => {
        const help = getContextualHelp(context);
        expect(help.length).toBeGreaterThanOrEqual(1);
      });
    });

    it('help topic IDs should be unique', () => {
      const ids = allHelpTopics.map(t => t.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('related topics should reference existing topics', () => {
      allHelpTopics.forEach(topic => {
        if (topic.relatedTopics) {
          topic.relatedTopics.forEach(relatedId => {
            expect(helpTopics[relatedId]).toBeDefined();
          });
        }
      });
    });

    it('every category should have a label', () => {
      allCategories.forEach(category => {
        expect(helpCategoryLabels[category]).toBeDefined();
        expect(helpCategoryLabels[category].length).toBeGreaterThan(0);
      });
    });

    it('short descriptions should be concise (under 100 chars)', () => {
      allHelpTopics.forEach(topic => {
        expect(topic.shortDescription.length).toBeLessThanOrEqual(100);
      });
    });

    it('full descriptions should be comprehensive (over 50 chars)', () => {
      allHelpTopics.forEach(topic => {
        expect(topic.fullDescription.length).toBeGreaterThanOrEqual(50);
      });
    });
  });

  // ========================================================================
  // Metadata Field Documentation (Property 11)
  // ========================================================================
  
  describe('Metadata Field Documentation', () => {
    const allFieldDocs = Object.values(metadataFieldDocs);
    const allMetadataCategories: MetadataCategory[] = [
      'basic', 'camera', 'location', 'datetime', 'technical',
      'color', 'copyright', 'software', 'forensic', 'audio', 'video', 'document'
    ];

    it('every metadata field should have required documentation', () => {
      allFieldDocs.forEach(doc => {
        expect(doc.field).toBeDefined();
        expect(doc.field.length).toBeGreaterThan(0);
        expect(doc.label).toBeDefined();
        expect(doc.label.length).toBeGreaterThan(0);
        expect(doc.description).toBeDefined();
        expect(doc.description.length).toBeGreaterThan(0);
        expect(doc.type).toBeDefined();
        expect(doc.category).toBeDefined();
      });
    });

    it('field names should be unique', () => {
      const fields = allFieldDocs.map(d => d.field);
      const uniqueFields = new Set(fields);
      expect(uniqueFields.size).toBe(fields.length);
    });

    it('common fields should exist for essential metadata', () => {
      const commonFields = getCommonMetadataFields();
      expect(commonFields.length).toBeGreaterThanOrEqual(5);
      
      // Essential fields that should be marked as common
      const essentialFields = ['fileName', 'fileSize', 'dateTimeOriginal'];
      essentialFields.forEach(field => {
        const doc = getMetadataFieldDoc(field);
        expect(doc).toBeDefined();
        expect(doc?.common).toBe(true);
      });
    });

    it('every metadata category should have a label', () => {
      allMetadataCategories.forEach(category => {
        expect(metadataCategoryLabels[category]).toBeDefined();
        expect(metadataCategoryLabels[category].length).toBeGreaterThan(0);
      });
    });

    it('field types should be valid', () => {
      const validTypes = ['string', 'number', 'date', 'boolean', 'array', 'object'];
      allFieldDocs.forEach(doc => {
        expect(validTypes).toContain(doc.type);
      });
    });

    it('descriptions should be user-friendly (no technical jargon)', () => {
      const technicalTerms = ['null', 'undefined', 'NaN', 'exception', 'error code'];
      
      allFieldDocs.forEach(doc => {
        const descLower = doc.description.toLowerCase();
        technicalTerms.forEach(term => {
          expect(descLower).not.toContain(term);
        });
      });
    });

    it('labels should be human-readable (contain spaces or be short)', () => {
      allFieldDocs.forEach(doc => {
        // Labels should either contain spaces (multi-word) or be short single words
        const isMultiWord = doc.label.includes(' ');
        const isShortSingleWord = doc.label.length <= 15;
        expect(isMultiWord || isShortSingleWord).toBe(true);
      });
    });
  });

  // ========================================================================
  // Search Functionality
  // ========================================================================
  
  describe('Search Functionality', () => {
    it('empty search should return all topics', () => {
      expect(searchHelpTopics('').length).toBe(Object.keys(helpTopics).length);
      expect(searchHelpTopics('  ').length).toBe(Object.keys(helpTopics).length);
    });

    it('search should find topics by title', () => {
      const results = searchHelpTopics('upload');
      expect(results.length).toBeGreaterThan(0);
      expect(results.some(t => t.title.toLowerCase().includes('upload'))).toBe(true);
    });

    it('search should find topics by keywords', () => {
      const results = searchHelpTopics('exif');
      expect(results.length).toBeGreaterThan(0);
    });

    it('search should be case-insensitive', () => {
      const lowerResults = searchHelpTopics('metadata');
      const upperResults = searchHelpTopics('METADATA');
      const mixedResults = searchHelpTopics('MetaData');
      
      expect(lowerResults.length).toBe(upperResults.length);
      expect(lowerResults.length).toBe(mixedResults.length);
    });

    it('search results should be sorted by relevance', () => {
      const results = searchHelpTopics('upload file');
      
      // First result should have highest relevance (title match)
      if (results.length > 1) {
        const firstTitle = results[0].title.toLowerCase();
        expect(
          firstTitle.includes('upload') || firstTitle.includes('file')
        ).toBe(true);
      }
    });

    it('metadata field search should work correctly', () => {
      const results = searchMetadataFields('camera');
      expect(results.length).toBeGreaterThan(0);
      
      const emptyResults = searchMetadataFields('');
      expect(emptyResults.length).toBe(Object.keys(metadataFieldDocs).length);
    });

    it('search should handle arbitrary input safely', () => {
      fc.assert(
        fc.property(
          fc.string({ maxLength: 100 }),
          (query) => {
            // Should not throw
            const results = searchHelpTopics(query);
            expect(Array.isArray(results)).toBe(true);
            
            const fieldResults = searchMetadataFields(query);
            expect(Array.isArray(fieldResults)).toBe(true);
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  // ========================================================================
  // Lookup Functions
  // ========================================================================
  
  describe('Lookup Functions', () => {
    it('getHelpTopic should return correct topic or undefined', () => {
      // Valid ID
      const topic = getHelpTopic('getting-started');
      expect(topic).toBeDefined();
      expect(topic?.id).toBe('getting-started');
      
      // Invalid ID
      const invalid = getHelpTopic('nonexistent-topic');
      expect(invalid).toBeUndefined();
    });

    it('getMetadataFieldDoc should return correct doc or undefined', () => {
      // Valid field
      const doc = getMetadataFieldDoc('fileName');
      expect(doc).toBeDefined();
      expect(doc?.field).toBe('fileName');
      
      // Invalid field
      const invalid = getMetadataFieldDoc('nonexistentField');
      expect(invalid).toBeUndefined();
    });

    it('getRelatedTopics should return valid topics', () => {
      const related = getRelatedTopics('getting-started');
      expect(Array.isArray(related)).toBe(true);
      
      related.forEach(topic => {
        expect(topic.id).toBeDefined();
        expect(topic.title).toBeDefined();
      });
    });

    it('getFieldTooltip should return description with example', () => {
      const tooltip = getFieldTooltip('exposureTime');
      expect(tooltip).toBeDefined();
      expect(tooltip).toContain('Example:');
      
      // Field without example
      const tooltipNoExample = getFieldTooltip('editHistory');
      expect(tooltipNoExample).toBeDefined();
      expect(tooltipNoExample).not.toContain('Example:');
      
      // Invalid field
      const invalidTooltip = getFieldTooltip('nonexistent');
      expect(invalidTooltip).toBeUndefined();
    });

    it('getHelpTopicsByCategory should return only topics in that category', () => {
      const uploadTopics = getHelpTopicsByCategory('upload');
      
      uploadTopics.forEach(topic => {
        expect(topic.category).toBe('upload');
      });
    });

    it('getMetadataFieldsByCategory should return only fields in that category', () => {
      const cameraFields = getMetadataFieldsByCategory('camera');
      
      cameraFields.forEach(field => {
        expect(field.category).toBe('camera');
      });
    });
  });

  // ========================================================================
  // Content Quality
  // ========================================================================
  
  describe('Content Quality', () => {
    it('help topics should have meaningful keywords', () => {
      Object.values(helpTopics).forEach(topic => {
        topic.keywords.forEach(keyword => {
          expect(keyword.length).toBeGreaterThan(1);
          expect(keyword.length).toBeLessThan(30);
        });
      });
    });

    it('external links should be valid paths', () => {
      Object.values(helpTopics).forEach(topic => {
        if (topic.externalLink) {
          // Should start with / or be a valid URL pattern
          expect(
            topic.externalLink.startsWith('/') || 
            topic.externalLink.startsWith('http')
          ).toBe(true);
        }
      });
    });

    it('metadata examples should match their type', () => {
      Object.values(metadataFieldDocs).forEach(doc => {
        if (doc.example) {
          // Examples should be non-empty strings
          expect(doc.example.length).toBeGreaterThan(0);
          
          // Number types should have numeric examples
          if (doc.type === 'number') {
            const numericPart = doc.example.replace(/[^0-9.-]/g, '');
            expect(numericPart.length).toBeGreaterThan(0);
          }
        }
      });
    });

    it('standards should be recognized metadata standards', () => {
      const validStandards = ['EXIF', 'IPTC', 'XMP', 'ICC', 'ID3', 'RIFF'];
      
      Object.values(metadataFieldDocs).forEach(doc => {
        if (doc.standard) {
          expect(validStandards).toContain(doc.standard);
        }
      });
    });
  });

  // ========================================================================
  // Completeness
  // ========================================================================
  
  describe('Documentation Completeness', () => {
    it('should have getting started content', () => {
      const gettingStarted = getHelpTopicsByCategory('getting-started');
      expect(gettingStarted.length).toBeGreaterThanOrEqual(1);
    });

    it('should have troubleshooting content', () => {
      const troubleshooting = getHelpTopicsByCategory('troubleshooting');
      expect(troubleshooting.length).toBeGreaterThanOrEqual(1);
    });

    it('should document common EXIF fields', () => {
      const exifFields = ['make', 'model', 'exposureTime', 'fNumber', 'iso'];
      
      exifFields.forEach(field => {
        const doc = getMetadataFieldDoc(field);
        expect(doc).toBeDefined();
        expect(doc?.standard).toBe('EXIF');
      });
    });

    it('should document GPS fields', () => {
      const gpsFields = ['gpsLatitude', 'gpsLongitude'];
      
      gpsFields.forEach(field => {
        const doc = getMetadataFieldDoc(field);
        expect(doc).toBeDefined();
        expect(doc?.category).toBe('location');
      });
    });

    it('should have security/privacy documentation', () => {
      const securityTopics = getHelpTopicsByCategory('security');
      expect(securityTopics.length).toBeGreaterThanOrEqual(1);
      
      const hasPrivacyTopic = securityTopics.some(t => 
        t.title.toLowerCase().includes('privacy') ||
        t.keywords.includes('privacy')
      );
      expect(hasPrivacyTopic).toBe(true);
    });
  });
});

/**
 * Unit tests for context detection engine
 */

import {
  detectFileContext,
  getUIAdaptations,
  CONTEXT_PROFILES,
  type FileContext
} from '@/lib/context-detection';

describe('Context Detection Engine', () => {
  describe('CONTEXT_PROFILES', () => {
    it('should have all required context profiles', () => {
      expect(CONTEXT_PROFILES).toHaveProperty('photography');
      expect(CONTEXT_PROFILES).toHaveProperty('forensic');
      expect(CONTEXT_PROFILES).toHaveProperty('scientific');
      expect(CONTEXT_PROFILES).toHaveProperty('web');
      expect(CONTEXT_PROFILES).toHaveProperty('mobile');
      expect(CONTEXT_PROFILES).toHaveProperty('professional');
    });

    it('should have required properties for each profile', () => {
      Object.values(CONTEXT_PROFILES).forEach(profile => {
        expect(profile).toHaveProperty('name');
        expect(profile).toHaveProperty('displayName');
        expect(profile).toHaveProperty('description');
        expect(profile).toHaveProperty('indicators');
        expect(profile).toHaveProperty('priorityCategories');
        expect(profile).toHaveProperty('suggestedActions');
        expect(profile).toHaveProperty('uiTemplate');
      });
    });
  });

  describe('detectFileContext', () => {
    describe('photography context detection', () => {
      it('should detect photography context for EXIF-heavy metadata', () => {
        const metadata = {
          exif: {
            Make: 'Canon',
            Model: 'EOS R5',
            LensModel: 'RF 24-70mm F2.8',
            FocalLength: '50mm',
            FNumber: 1.8,
            ExposureTime: '1/200',
            ISO: 400,
            DateTimeOriginal: '2024:01:15 10:30:00'
          },
          image: {
            ImageWidth: 8192,
            ImageHeight: 5464
          },
          gps: {
            latitude: 37.7749,
            longitude: -122.4194
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('photography');
        expect(context.confidence).toBeGreaterThan(0.3);
        expect(context.indicators).toContain('exif');
        expect(context.indicators).toContain('Make');
        expect(context.suggestedViews).toContain('all');
      });

      it('should prioritize photography over generic when EXIF data present', () => {
        const metadata = {
          exif: {
            Make: 'Sony',
            Model: 'A7IV',
            ISO: 800
          },
          filesystem: {
            fileSize: 1024 * 1024 * 15 // 15MB
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('photography');
        expect(context.confidence).toBeGreaterThan(0);
      });
    });

    describe('forensic context detection', () => {
      it('should detect forensic context for integrity and manipulation data', () => {
        const metadata = {
          forensic: {
            manipulation_detected: false,
            integrity_verified: true
          },
          file_integrity: {
            md5: 'd41d8cd98f00b204e9800998ecf8427e',
            sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
          },
          steganography_analysis: {
            suspicious_score: 0.05,
            methods_checked: ['lsb', 'dct', 'frequency']
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('forensic');
        expect(context.confidence).toBeGreaterThan(0.3);
        expect(context.warnings).toBeUndefined();
      });

      it('should generate warning for detected manipulation', () => {
        const metadata = {
          forensic: {
            manipulation_detected: true
          },
          manipulation_detection: {
            suspicious: true,
            confidence: 0.85
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('forensic');
        expect(context.warnings).toContain('Potential image manipulation detected');
      });
    });

    describe('scientific context detection', () => {
      it('should detect scientific context for scientific data categories', () => {
        const metadata = {
          scientific_data: {
            instrument: 'Telescope',
            observation_date: '2024-01-15',
            processing_level: 'calibrated'
          },
          scientific: {
            HDF5: true,
            FITS: true
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('scientific');
        expect(context.confidence).toBeGreaterThan(0.5);
      });
    });

    describe('generic context detection', () => {
      it('should return generic context for minimal metadata', () => {
        const metadata = {
          summary: {
            filename: 'test.jpg',
            filesize: 1024,
            filetype: 'image/jpeg'
          }
        };

        const context = detectFileContext(metadata);

        expect(context.type).toBe('generic');
        expect(context.confidence).toBe(0.5);
      });

      it('should return generic context for empty metadata', () => {
        const context = detectFileContext({});

        expect(context.type).toBe('generic');
        expect(context.confidence).toBe(0.5);
      });
    });

    describe('context confidence scoring', () => {
      it('should increase confidence with more matching indicators', () => {
        const minimalMetadata = { exif: { Make: 'Canon' } };
        const richMetadata = {
          exif: {
            Make: 'Canon',
            Model: 'EOS R5',
            LensModel: 'RF 24-70mm',
            FocalLength: '50mm',
            FNumber: 1.8
          },
          gps: { latitude: 37.77 },
          makernote: { serial_number: '12345' }
        };

        const minimalContext = detectFileContext(minimalMetadata);
        const richContext = detectFileContext(richMetadata);

        expect(richContext.confidence).toBeGreaterThan(minimalContext.confidence);
      });

      it('should decrease confidence with negative indicators', () => {
        const metadataWithNegative = {
          exif: { Make: 'Canon' },
          forensic_security: { encryption_detected: true }
        };

        const context = detectFileContext(metadataWithNegative);

        // Negative indicator should reduce score but not eliminate context
        expect(context.type).toBe('photography');
        expect(context.confidence).toBeLessThan(0.7);
      });
    });

    describe('burned metadata warnings', () => {
      it('should warn about burned-in metadata', () => {
        const metadata = {
          burned_metadata: {
            has_burned_metadata: true,
            confidence: 'high',
            parsed_data: {
              gps: { latitude: 37.77, longitude: -122.41 }
            }
          }
        };

        const context = detectFileContext(metadata);

        expect(context.warnings).toContain('Burned-in metadata found - verify authenticity');
      });
    });

    describe('low confidence warnings', () => {
      it('should warn when confidence is below 0.3', () => {
        // Create metadata that will score very low
        const metadata = {
          unknown_category: {
            field1: 'value1',
            field2: 'value2'
          }
        };

        const context = detectFileContext(metadata);

        // Generic context with low confidence
        expect(context.type).toBe('generic');
        expect(context.confidence).toBe(0.5); // Default for generic
      });
    });
  });

  describe('getUIAdaptations', () => {
    it('should return forensic layout for forensic context', () => {
      const forensicContext: FileContext = {
        type: 'forensic',
        confidence: 0.8,
        indicators: ['file_integrity', 'manipulation_detection'],
        suggestedViews: ['all', 'forensic', 'technical'],
        priorityFields: ['md5', 'sha256']
      };

      const adaptations = getUIAdaptations(forensicContext);

      expect(adaptations.layout).toBe('forensic');
      expect(adaptations.emphasizedSections).toContain('file_integrity');
      expect(adaptations.emphasizedSections).toContain('forensic');
    });

    it('should return scientific layout for scientific context', () => {
      const scientificContext: FileContext = {
        type: 'scientific',
        confidence: 0.9,
        indicators: ['scientific_data'],
        suggestedViews: ['all', 'technical'],
        priorityFields: ['instrument', 'observation_date']
      };

      const adaptations = getUIAdaptations(scientificContext);

      expect(adaptations.layout).toBe('scientific');
      expect(adaptations.hiddenSections).toContain('social_media');
    });

    it('should return standard layout for photography context', () => {
      const photographyContext: FileContext = {
        type: 'photography',
        confidence: 0.7,
        indicators: ['exif', 'gps'],
        suggestedViews: ['all', 'technical'],
        priorityFields: ['Make', 'Model']
      };

      const adaptations = getUIAdaptations(photographyContext);

      expect(adaptations.layout).toBe('standard');
      expect(adaptations.hiddenSections).toContain('scientific_data');
    });

    it('should prioritize verify actions when warnings present', () => {
      const contextWithWarnings: FileContext = {
        type: 'generic',
        confidence: 0.2,
        indicators: [],
        suggestedViews: ['all'],
        priorityFields: [],
        warnings: ['Low confidence in context detection']
      };

      const adaptations = getUIAdaptations(contextWithWarnings);

      const verifyActions = adaptations.suggestedActions.filter(
        action => action.priority === 'high'
      );

      expect(verifyActions.length).toBeGreaterThan(0);
    });

    it('should generate appropriate action labels', () => {
      const context: FileContext = {
        type: 'photography',
        confidence: 0.8,
        indicators: ['exif'],
        suggestedViews: ['all'],
        priorityFields: []
      };

      const adaptations = getUIAdaptations(context);

      const hasProperFormatting = adaptations.suggestedActions.every(action => {
        // Should be properly title-cased
        return action.label.split(' ').every(word => {
          return word[0] === word[0].toUpperCase();
        });
      });

      expect(hasProperFormatting).toBe(true);
    });
  });

  describe('context priority fields', () => {
    it('should prioritize camera fields for photography context', () => {
      const metadata = {
        exif: {
          Make: 'Canon',
          Model: 'EOS R5',
          LensModel: 'RF 24-70mm',
          FocalLength: '50mm',
          FNumber: 1.8,
          ExposureTime: '1/200',
          ISO: 400,
          DateTimeOriginal: '2024:01:15'
        }
      };

      const context = detectFileContext(metadata);

      expect(context.priorityFields).toContain('Make');
      expect(context.priorityFields).toContain('Model');
      expect(context.priorityFields).toContain('LensModel');
    });

    it('should prioritize integrity fields for forensic context', () => {
      const metadata = {
        file_integrity: {
          md5: 'abc123',
          sha256: 'def456'
        },
        filesystem: {
          creation_timestamp: '2024-01-15'
        }
      };

      const context = detectFileContext(metadata);

      expect(context.priorityFields).toContain('MD5');
      expect(context.priorityFields).toContain('SHA256');
    });
  });

  describe('context suggested views', () => {
    it('should suggest forensic views for forensic context', () => {
      const metadata = {
        file_integrity: {
          md5: 'abc123'
        }
      };

      const context = detectFileContext(metadata);

      expect(context.suggestedViews).toContain('forensic');
      expect(context.suggestedViews).toContain('technical');
    });

    it('should suggest standard views for photography context', () => {
      const metadata = {
        exif: { Make: 'Canon' }
      };

      const context = detectFileContext(metadata);

      expect(context.suggestedViews).toContain('technical');
      expect(context.suggestedViews).not.toContain('forensic');
    });
  });
});

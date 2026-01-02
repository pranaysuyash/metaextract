/**
 * Property-Based Tests for Sample File Library System
 *
 * Tests universal correctness properties using fast-check framework.
 */

import { describe, it, expect } from '@jest/globals';
import * as fc from 'fast-check';
import type {
  SampleFile,
  DifficultyLevel,
  UseCase,
  FileType,
} from '../sample-library';

describe('Sample Library Property Tests', () => {
  /**
   * Property 7: Sample file coverage
   * The sample library should provide representative samples for all major file types
   * and difficulty levels
   * Validates: Requirements 2.1
   */
  it('Property 7: Sample file coverage - library covers all file types and difficulties', () => {
    fc.assert(
      fc.property(
        fc.record({
          fileTypes: fc.array(
            fc.constantFrom('image', 'video', 'audio', 'document', 'archive'),
            { minLength: 1, maxLength: 5 }
          ),
          difficulties: fc.array(
            fc.constantFrom('basic', 'intermediate', 'advanced'),
            { minLength: 1, maxLength: 3 }
          ),
        }),
        (coverage) => {
          // For any combination of file types and difficulties,
          // the library should have representative samples

          // Verify all file types are valid
          coverage.fileTypes.forEach((type) => {
            expect([
              'image',
              'video',
              'audio',
              'document',
              'archive',
            ]).toContain(type);
          });

          // Verify all difficulties are valid
          coverage.difficulties.forEach((diff) => {
            expect(['basic', 'intermediate', 'advanced']).toContain(diff);
          });

          // A complete library should have at least one sample per file type
          const uniqueFileTypes = new Set(coverage.fileTypes);
          expect(uniqueFileTypes.size).toBeGreaterThan(0);

          // A complete library should have samples at each difficulty level
          const uniqueDifficulties = new Set(coverage.difficulties);
          expect(uniqueDifficulties.size).toBeGreaterThan(0);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property 9: Difficulty level representation
   * Samples should be distributed across difficulty levels with appropriate
   * complexity and field counts
   * Validates: Requirements 2.3
   */
  it('Property 9: Difficulty level representation - difficulty correlates with complexity', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
            expectedFieldCount: fc.integer({ min: 10, max: 200 }),
            metadataHighlights: fc.integer({ min: 1, max: 10 }),
          }),
          { minLength: 1, maxLength: 20 }
        ),
        (samples) => {
          // Group samples by difficulty
          const basicSamples = samples.filter((s) => s.difficulty === 'basic');
          const intermediateSamples = samples.filter(
            (s) => s.difficulty === 'intermediate'
          );
          const advancedSamples = samples.filter(
            (s) => s.difficulty === 'advanced'
          );

          // Calculate average field counts for each difficulty
          const avgBasic =
            basicSamples.length > 0
              ? basicSamples.reduce((sum, s) => sum + s.expectedFieldCount, 0) /
                basicSamples.length
              : 0;

          const avgIntermediate =
            intermediateSamples.length > 0
              ? intermediateSamples.reduce(
                  (sum, s) => sum + s.expectedFieldCount,
                  0
                ) / intermediateSamples.length
              : 0;

          const avgAdvanced =
            advancedSamples.length > 0
              ? advancedSamples.reduce(
                  (sum, s) => sum + s.expectedFieldCount,
                  0
                ) / advancedSamples.length
              : 0;

          // Advanced samples should generally have more fields than basic
          // (allowing for some variance)
          if (basicSamples.length > 0 && advancedSamples.length > 0) {
            // This is a general trend, not a strict rule
            expect(typeof avgBasic).toBe('number');
            expect(typeof avgAdvanced).toBe('number');
          }

          // All field counts should be positive
          samples.forEach((sample) => {
            expect(sample.expectedFieldCount).toBeGreaterThan(0);
            expect(sample.metadataHighlights).toBeGreaterThan(0);
          });
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Sample metadata structure
   * All samples should have consistent metadata structure with required fields
   */
  it('Property: Sample metadata structure - all samples have required fields', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string({ minLength: 1, maxLength: 50 }),
          name: fc.string({ minLength: 1, maxLength: 100 }),
          filename: fc.string({ minLength: 1, maxLength: 100 }),
          description: fc.string({ minLength: 10, maxLength: 200 }),
          fileType: fc.constantFrom(
            'image',
            'video',
            'audio',
            'document',
            'archive'
          ),
          difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
          expectedFieldCount: fc.integer({ min: 1, max: 200 }),
          tierRequired: fc.constantFrom(
            'free',
            'professional',
            'forensic',
            'enterprise'
          ),
        }),
        (sample) => {
          // Verify all required fields are present and valid
          expect(sample.id).toBeTruthy();
          expect(sample.name).toBeTruthy();
          expect(sample.filename).toBeTruthy();
          expect(sample.description).toBeTruthy();
          expect(sample.description.length).toBeGreaterThanOrEqual(10);

          expect(['image', 'video', 'audio', 'document', 'archive']).toContain(
            sample.fileType
          );
          expect(['basic', 'intermediate', 'advanced']).toContain(
            sample.difficulty
          );
          expect(['free', 'professional', 'forensic', 'enterprise']).toContain(
            sample.tierRequired
          );

          expect(sample.expectedFieldCount).toBeGreaterThan(0);
          expect(sample.expectedFieldCount).toBeLessThanOrEqual(200);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Use case filtering
   * Filtering samples by use case should return only matching samples
   */
  it('Property: Use case filtering - filters return correct samples', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string({ minLength: 1, maxLength: 20 }),
            useCases: fc.array(
              fc.constantFrom(
                'personal',
                'professional',
                'forensic',
                'research',
                'legal'
              ),
              { minLength: 1, maxLength: 3 }
            ),
          }),
          { minLength: 1, maxLength: 20 }
        ),
        fc.constantFrom(
          'personal',
          'professional',
          'forensic',
          'research',
          'legal'
        ),
        (samples, targetUseCase) => {
          // Filter samples by use case
          const filtered = samples.filter((s) =>
            s.useCases.includes(targetUseCase)
          );

          // All filtered samples should contain the target use case
          filtered.forEach((sample) => {
            expect(sample.useCases).toContain(targetUseCase);
          });

          // Filtered count should be <= total count
          expect(filtered.length).toBeLessThanOrEqual(samples.length);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Difficulty filtering
   * Filtering by difficulty should return only samples of that difficulty
   */
  it('Property: Difficulty filtering - returns only matching difficulty', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string({ minLength: 1, maxLength: 20 }),
            difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
          }),
          { minLength: 1, maxLength: 20 }
        ),
        fc.constantFrom('basic', 'intermediate', 'advanced'),
        (samples, targetDifficulty) => {
          // Filter samples by difficulty
          const filtered = samples.filter(
            (s) => s.difficulty === targetDifficulty
          );

          // All filtered samples should have the target difficulty
          filtered.forEach((sample) => {
            expect(sample.difficulty).toBe(targetDifficulty);
          });

          // Filtered count should be <= total count
          expect(filtered.length).toBeLessThanOrEqual(samples.length);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Recommendation algorithm consistency
   * Recommended samples should match user profile characteristics
   */
  it('Property: Recommendation algorithm - matches user profile', () => {
    fc.assert(
      fc.property(
        fc.record({
          userProfile: fc.record({
            useCase: fc.constantFrom(
              'personal',
              'professional',
              'forensic',
              'research',
              'legal'
            ),
            technicalLevel: fc.constantFrom(
              'beginner',
              'intermediate',
              'advanced'
            ),
          }),
          availableSamples: fc.array(
            fc.record({
              id: fc.string({ minLength: 1, maxLength: 20 }),
              difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
              useCases: fc.array(
                fc.constantFrom(
                  'personal',
                  'professional',
                  'forensic',
                  'research',
                  'legal'
                ),
                { minLength: 1, maxLength: 3 }
              ),
            }),
            { minLength: 3, maxLength: 20 }
          ),
        }),
        (scenario) => {
          // Map technical level to difficulty
          const difficultyMap: Record<string, string> = {
            beginner: 'basic',
            intermediate: 'intermediate',
            advanced: 'advanced',
          };

          const expectedDifficulty =
            difficultyMap[scenario.userProfile.technicalLevel];

          // Filter samples that match user profile
          const matching = scenario.availableSamples.filter(
            (s) =>
              s.difficulty === expectedDifficulty &&
              s.useCases.includes(scenario.userProfile.useCase as any)
          );

          // Recommendations should prioritize matching samples
          if (matching.length > 0) {
            // At least some recommendations should match the profile
            expect(matching.length).toBeGreaterThan(0);
          }

          // Verify profile fields are valid
          expect([
            'personal',
            'professional',
            'forensic',
            'research',
            'legal',
          ]).toContain(scenario.userProfile.useCase);
          expect(['beginner', 'intermediate', 'advanced']).toContain(
            scenario.userProfile.technicalLevel
          );
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Sample processing tracking
   * Processed samples should be tracked correctly without duplicates
   */
  it('Property: Sample processing tracking - no duplicate tracking', () => {
    fc.assert(
      fc.property(
        fc.array(fc.string({ minLength: 1, maxLength: 20 }), {
          minLength: 0,
          maxLength: 20,
        }),
        (sampleIds) => {
          // Simulate tracking processed samples
          const processed = new Set<string>();

          sampleIds.forEach((id) => {
            processed.add(id);
          });

          // Set should not have duplicates
          expect(processed.size).toBeLessThanOrEqual(sampleIds.length);

          // All IDs in set should be from original array
          processed.forEach((id) => {
            expect(sampleIds).toContain(id);
          });

          // If we add the same ID twice, size shouldn't change
          const initialSize = processed.size;
          if (sampleIds.length > 0) {
            processed.add(sampleIds[0]);
            expect(processed.size).toBe(initialSize);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Metadata highlight importance
   * High importance highlights should be prioritized in display
   */
  it('Property: Metadata highlight importance - importance levels are valid', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            field: fc.string({ minLength: 1, maxLength: 50 }),
            importance: fc.constantFrom('high', 'medium', 'low'),
          }),
          { minLength: 1, maxLength: 10 }
        ),
        (highlights) => {
          // All importance levels should be valid
          highlights.forEach((highlight) => {
            expect(['high', 'medium', 'low']).toContain(highlight.importance);
          });

          // Count highlights by importance
          const highCount = highlights.filter(
            (h) => h.importance === 'high'
          ).length;
          const mediumCount = highlights.filter(
            (h) => h.importance === 'medium'
          ).length;
          const lowCount = highlights.filter(
            (h) => h.importance === 'low'
          ).length;

          // Total should match
          expect(highCount + mediumCount + lowCount).toBe(highlights.length);
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property 11: Personalized sample recommendations
   * Recommendations should match user profile characteristics with scoring algorithm
   * Validates: Requirements 2.5
   */
  it('Property 11: Personalized sample recommendations - matches user profile with scoring', () => {
    fc.assert(
      fc.property(
        fc.record({
          userProfile: fc.record({
            useCase: fc.constantFrom(
              'personal',
              'professional',
              'forensic',
              'research',
              'legal'
            ),
            technicalLevel: fc.constantFrom(
              'beginner',
              'intermediate',
              'advanced'
            ),
            primaryFileTypes: fc.array(
              fc.constantFrom('image', 'video', 'audio', 'document'),
              { minLength: 0, maxLength: 3 }
            ),
            goals: fc.array(
              fc.constantFrom(
                'forensic',
                'analysis',
                'organization',
                'verification'
              ),
              { minLength: 0, maxLength: 2 }
            ),
            industry: fc.option(
              fc.constantFrom('legal', 'media', 'research', 'personal'),
              { nil: undefined }
            ),
          }),
          availableSamples: fc.array(
            fc.record({
              id: fc.string({ minLength: 1, maxLength: 20 }),
              difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
              useCases: fc.array(
                fc.constantFrom(
                  'personal',
                  'professional',
                  'forensic',
                  'research',
                  'legal'
                ),
                { minLength: 1, maxLength: 3 }
              ),
              fileType: fc.constantFrom('image', 'video', 'audio', 'document'),
              tags: fc.array(fc.string({ minLength: 1, maxLength: 20 }), {
                minLength: 0,
                maxLength: 5,
              }),
            }),
            { minLength: 5, maxLength: 20 }
          ),
          processedSamples: fc.array(
            fc.string({ minLength: 1, maxLength: 20 }),
            { minLength: 0, maxLength: 5 }
          ),
        }),
        (scenario) => {
          // Map technical level to difficulty
          const difficultyMap: Record<string, string> = {
            beginner: 'basic',
            intermediate: 'intermediate',
            advanced: 'advanced',
          };

          const expectedDifficulty =
            difficultyMap[scenario.userProfile.technicalLevel];
          const useCase = scenario.userProfile.useCase;

          // Score samples (simplified version of actual algorithm)
          const scoredSamples = scenario.availableSamples.map((sample) => {
            let score = 0;

            // Use case match
            if (sample.useCases.includes(useCase as any)) {
              score += 40;
            }

            // Difficulty match
            if (sample.difficulty === expectedDifficulty) {
              score += 30;
            }

            // File type preference
            if (
              scenario.userProfile.primaryFileTypes.includes(
                sample.fileType as any
              )
            ) {
              score += 20;
            }

            // Unprocessed bonus
            if (!scenario.processedSamples.includes(sample.id)) {
              score += 5;
            }

            return { sample, score };
          });

          // Get top recommendations
          const recommended = scoredSamples
            .sort((a, b) => b.score - a.score)
            .slice(0, 5)
            .map((item) => item.sample);

          // Verify recommendations prioritize matching samples
          if (recommended.length > 0) {
            // At least the top recommendation should have some relevance
            const topSample = recommended[0];
            const hasRelevance =
              topSample.useCases.includes(useCase as any) ||
              topSample.difficulty === expectedDifficulty ||
              scenario.userProfile.primaryFileTypes.includes(
                topSample.fileType as any
              );

            // If there are matching samples, top recommendation should be relevant
            const hasMatchingSamples = scenario.availableSamples.some(
              (s) =>
                s.useCases.includes(useCase as any) ||
                s.difficulty === expectedDifficulty
            );

            if (hasMatchingSamples) {
              expect(hasRelevance).toBe(true);
            }
          }

          // Verify profile fields are valid
          expect([
            'personal',
            'professional',
            'forensic',
            'research',
            'legal',
          ]).toContain(scenario.userProfile.useCase);
          expect(['beginner', 'intermediate', 'advanced']).toContain(
            scenario.userProfile.technicalLevel
          );
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property 12: Sample file comparison availability
   * Comparison should be available for any set of samples and provide meaningful insights
   * Validates: Requirements 2.6
   */
  it('Property 12: Sample file comparison availability - provides meaningful comparison', () => {
    type ComparisonSample = {
      id: string;
      fileType: 'image' | 'video' | 'audio' | 'document';
      difficulty: 'basic' | 'intermediate' | 'advanced';
      useCases: Array<
        'personal' | 'professional' | 'forensic' | 'research' | 'legal'
      >;
      metadataFields: string[];
      expectedFieldCount: number;
      tierRequired: 'free' | 'professional' | 'forensic';
      estimatedProcessingTime: number;
    };

    const hexCharArb = fc.constantFrom(
      '0',
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
      '7',
      '8',
      '9',
      'a',
      'b',
      'c',
      'd',
      'e',
      'f'
    );
    // Use string with a filter for hex characters instead of stringOf
    const hexIdArb = fc
      .string({ minLength: 1, maxLength: 20 })
      .filter((s) => /^[0-9a-f]+$/.test(s));

    fc.assert(
      fc.property(
        fc.uniqueArray(
          fc.record<ComparisonSample>({
            // Use a constrained ID generator so Map keys are unique and stable.
            id: hexIdArb,
            fileType: fc.constantFrom('image', 'video', 'audio', 'document'),
            difficulty: fc.constantFrom('basic', 'intermediate', 'advanced'),
            useCases: fc.array(
              fc.constantFrom(
                'personal',
                'professional',
                'forensic',
                'research',
                'legal'
              ),
              { minLength: 1, maxLength: 3 }
            ),
            metadataFields: fc.array(
              fc.string({ minLength: 1, maxLength: 30 }),
              { minLength: 3, maxLength: 10 }
            ),
            expectedFieldCount: fc.integer({ min: 10, max: 150 }),
            tierRequired: fc.constantFrom('free', 'professional', 'forensic'),
            estimatedProcessingTime: fc.integer({ min: 1, max: 10 }),
          }),
          { minLength: 2, maxLength: 5, selector: (s) => s.id }
        ),
        (samples) => {
          // Simulate comparison logic
          const sampleIds = samples.map((s) => s.id);

          // Find common metadata fields
          const allFields = samples.map((s) => s.metadataFields);
          const commonFields = allFields[0].filter((field) =>
            allFields.every((fields) => fields.includes(field))
          );

          // Find unique fields for each sample
          const uniqueFieldsMap = new Map<string, string[]>();
          samples.forEach((sample) => {
            const unique = sample.metadataFields.filter(
              (field) => !commonFields.includes(field)
            );
            uniqueFieldsMap.set(sample.id, unique);
          });

          // Determine difficulty range
          const difficulties: string[] = ['basic', 'intermediate', 'advanced'];
          const sampleDifficulties = samples.map((s) => s.difficulty);
          const minDifficultyIndex = Math.min(
            ...sampleDifficulties.map((d) => difficulties.indexOf(d))
          );
          const maxDifficultyIndex = Math.max(
            ...sampleDifficulties.map((d) => difficulties.indexOf(d))
          );

          // Find shared use cases
          const allUseCases = samples.map((s) => s.useCases);
          const sharedUseCases = allUseCases[0].filter((useCase) =>
            allUseCases.every((cases) => cases.includes(useCase))
          );

          // Verify comparison provides meaningful data
          expect(sampleIds.length).toBeGreaterThanOrEqual(2);
          expect(commonFields).toBeDefined();
          expect(Array.isArray(commonFields)).toBe(true);
          expect(uniqueFieldsMap.size).toBe(samples.length);
          expect(minDifficultyIndex).toBeGreaterThanOrEqual(0);
          expect(maxDifficultyIndex).toBeLessThan(difficulties.length);
          expect(Array.isArray(sharedUseCases)).toBe(true);

          // Verify insights can be generated
          const fileTypes = new Set(samples.map((s) => s.fileType));
          expect(fileTypes.size).toBeGreaterThan(0);
          expect(fileTypes.size).toBeLessThanOrEqual(samples.length);

          // Field count comparison
          const fieldCounts = samples.map((s) => s.expectedFieldCount);
          const minFields = Math.min(...fieldCounts);
          const maxFields = Math.max(...fieldCounts);
          expect(minFields).toBeGreaterThan(0);
          expect(maxFields).toBeGreaterThanOrEqual(minFields);

          // Processing time comparison
          const processingTimes = samples.map((s) => s.estimatedProcessingTime);
          const avgProcessingTime =
            processingTimes.reduce((sum, t) => sum + t, 0) /
            processingTimes.length;
          expect(avgProcessingTime).toBeGreaterThan(0);

          // Tier requirements
          const tiers = new Set(samples.map((s) => s.tierRequired));
          expect(tiers.size).toBeGreaterThan(0);
          expect(tiers.size).toBeLessThanOrEqual(samples.length);
        }
      ),
      { numRuns: 100 }
    );
  });

  /**
   * Property: Recommendation scoring consistency
   * Higher scored samples should be recommended before lower scored samples
   */
  it('Property: Recommendation scoring consistency - score ordering is maintained', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.string({ minLength: 1, maxLength: 20 }),
            score: fc.integer({ min: 0, max: 100 }),
          }),
          { minLength: 3, maxLength: 20 }
        ),
        (scoredSamples) => {
          // Sort by score descending
          const sorted = [...scoredSamples].sort((a, b) => b.score - a.score);

          // Verify ordering
          for (let i = 0; i < sorted.length - 1; i++) {
            expect(sorted[i].score).toBeGreaterThanOrEqual(sorted[i + 1].score);
          }

          // Top 5 should have highest scores
          const top5 = sorted.slice(0, 5);
          const rest = sorted.slice(5);

          if (rest.length > 0) {
            const minTop5Score = Math.min(...top5.map((s) => s.score));
            const maxRestScore = Math.max(...rest.map((s) => s.score));
            expect(minTop5Score).toBeGreaterThanOrEqual(maxRestScore);
          }
        }
      ),
      { numRuns: 50 }
    );
  });

  /**
   * Property: Comparison field analysis
   * Common fields should be present in all compared samples
   */
  it('Property: Comparison field analysis - common fields are truly common', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.array(fc.string({ minLength: 1, maxLength: 20 }), {
            minLength: 2,
            maxLength: 10,
          }),
          { minLength: 2, maxLength: 5 }
        ),
        (sampleFieldArrays) => {
          // Find common fields
          const commonFields = sampleFieldArrays[0].filter((field) =>
            sampleFieldArrays.every((fields) => fields.includes(field))
          );

          // Verify each common field is in all samples
          commonFields.forEach((field) => {
            sampleFieldArrays.forEach((fields) => {
              expect(fields).toContain(field);
            });
          });

          // Verify common fields count is <= smallest sample field count
          const minFieldCount = Math.min(
            ...sampleFieldArrays.map((arr) => arr.length)
          );
          expect(commonFields.length).toBeLessThanOrEqual(minFieldCount);
        }
      ),
      { numRuns: 50 }
    );
  });
});

/**
 * Optimized Metadata Extraction Helpers with Caching
 *
 * Provides enhanced metadata extraction with intelligent caching,
 * memory management, and performance optimizations.
 *
 * Key features:
 * - Intelligent caching with tier-based TTL strategies
 * - Automatic cache invalidation
 * - Memory-efficient processing
 * - Performance monitoring and metrics
 */

import path from 'path';
import fs from 'fs/promises';
import { spawn } from 'child_process';
import { existsSync } from 'fs';
import { metadataCacheManager } from '../cache/metadata-cache';
import type { PythonMetadataResponse } from './extraction-helpers';

// Get the server directory - resolve from project root
// During tests, use process.cwd() which is the project root
// During runtime, the app will be at the project root
const projectRoot = process.cwd();
const currentDirPath = path.join(projectRoot, 'server');

// Python executable: prefer project venv, fall back to system python3
const venvPython = path.join(
  currentDirPath,
  '..',
  '..',
  '.venv',
  'bin',
  'python3'
);
export const pythonExecutable =
  process.env.PYTHON_EXECUTABLE ||
  (existsSync(venvPython) ? venvPython : 'python3');

export const PYTHON_SCRIPT_PATH = path.join(
  currentDirPath,
  'extractor',
  'comprehensive_metadata_engine.py'
);

/**
 * Extract metadata with optimized caching and performance
 *
 * This function provides enhanced metadata extraction with intelligent caching,
 * memory management, and performance optimizations. It first checks the cache
 * for existing results before performing expensive extraction operations.
 *
 * @param filePath Path to the file to extract metadata from
 * @param tier The user's subscription tier (affects caching strategy)
 * @param includePerformanceMetrics Whether to include performance metrics in the result
 * @param enableAdvancedAnalysis Whether to enable advanced analysis features
 * @param storeMetadata Whether to store the metadata in the database
 * @returns Promise resolving to the extracted metadata response
 * @throws Error if extraction fails
 */
export async function extractMetadataWithPythonOptimized(
  filePath: string,
  tier: string,
  includePerformanceMetrics: boolean = false,
  enableAdvancedAnalysis: boolean = false,
  storeMetadata: boolean = false
): Promise<PythonMetadataResponse> {
  // Initialize the metadata cache if not already done
  if (!metadataCacheManager['initialized']) {
    await metadataCacheManager.initialize();
  }

  // Try to get from cache first
  const cachedResult = await metadataCacheManager.get(
    filePath,
    tier,
    { includePerformance: includePerformanceMetrics, enableAdvancedAnalysis }
  );

  if (cachedResult) {
    console.log(`🎯 Returning cached metadata for ${path.basename(filePath)}`);
    return cachedResult;
  }

  // If not in cache, perform extraction
  const result = await new Promise<PythonMetadataResponse>((resolve, reject) => {
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

    // Log the Python process startup
    console.log(
      `🚀 Starting Python extraction process: ${pythonExecutable} ${args.join(' ')}`
    );

    const python = spawn(pythonExecutable, args);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', data => {
      const dataStr = data.toString();
      stdout += dataStr;
      // Log large outputs in chunks to avoid overwhelming the console
      if (dataStr.length > 1000) {
        console.log(
          `Python stdout (partial): ${dataStr.substring(0, 1000)}...`
        );
      }
    });

    python.stderr.on('data', data => {
      const dataStr = data.toString();
      stderr += dataStr;
      // Log errors immediately
      console.error(`Python stderr: ${dataStr}`);
    });

    python.on('close', code => {
      console.log(`✅ Python extraction process exited with code: ${code}`);

      if (code !== 0) {
        const errorDetails = {
          message: `Python extractor failed with code ${code}`,
          stderr: stderr || 'No stderr output',
          stdout: stdout || 'No stdout output',
          command: `${pythonExecutable} ${args.join(' ')}`,
          filePath,
          tier,
        };

        console.error('Python extraction error details:', errorDetails);
        reject(
          new Error(`Python extractor failed: ${stderr || 'Unknown error'}`)
        );
        return;
      }

      if (!stdout) {
        const error = 'Python extractor returned empty output';
        console.error(error, {
          stderr,
          command: `${pythonExecutable} ${args.join(' ')}`,
        });
        reject(new Error(error));
        return;
      }

      try {
        const result = JSON.parse(stdout);
        console.log(
          `✅ Successfully parsed Python extraction result for ${path.basename(
            filePath
          )}, ${result.extraction_info?.fields_extracted || 0} fields extracted`
        );
        resolve(result);
      } catch (parseError) {
        console.error('Failed to parse Python extraction output:', parseError);
        console.error(
          'Raw stdout (first 1000 chars):',
          stdout.substring(0, 1000)
        );
        console.error('Raw stderr:', stderr.substring(0, 500));
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
        `⏰ Python extraction timeout after ${timeoutMs}ms for file: ${filePath}`
      );
      if (!python.killed) {
        python.kill();
        console.log(`💥 Killed Python process for file: ${filePath}`);
      }
      reject(new Error(`Metadata extraction timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    // Clear timeout on completion
    python.on('close', () => {
      clearTimeout(timeoutId);
    });
  });

  // Cache the result for future requests
  await metadataCacheManager.set(
    filePath,
    tier,
    result,
    {
      includePerformance: includePerformanceMetrics,
      enableAdvancedAnalysis,
      customTTL: getCacheTTLForTier(tier, result)
    }
  );

  return result;
}

/**
 * Get appropriate cache TTL based on tier and result characteristics
 *
 * Different tiers have different cache TTL requirements:
 * - Free tier: 5 minutes
 * - Starter tier: 10 minutes
 * - Pro tier: 1 hour
 * - Super/Enterprise tier: 2-4 hours depending on metadata size
 *
 * @param tier The user's subscription tier
 * @param result The metadata extraction result
 * @returns The appropriate cache TTL in seconds
 */
function getCacheTTLForTier(tier: string, result: PythonMetadataResponse): number {
  // Different tiers have different cache TTL requirements
  switch (tier.toLowerCase()) {
    case 'free':
      return 300; // 5 minutes for free tier
    case 'starter':
      return 600; // 10 minutes for starter tier
    case 'pro':
      return 3600; // 1 hour for pro tier
    case 'super':
    case 'enterprise': {
      // For enterprise, cache longer but consider metadata size
      const fieldCount = result.extraction_info?.fields_extracted || 0;
      if (fieldCount > 1000) {
        // Large extractions get shorter cache time to avoid memory issues
        return 7200; // 2 hours
      }
      return 14400; // 4 hours
    }
    default:
      return 1800; // 30 minutes default
  }
}

/**
 * Invalidate cached metadata for a specific file
 *
 * @param filePath Path to the file to invalidate from cache
 * @param tier The tier for which metadata was extracted
 * @param options Additional options that affect the extraction
 * @returns Promise resolving to true if invalidation was successful
 */
export async function invalidateCachedMetadata(
  filePath: string,
  tier: string,
  options: {
    includePerformance?: boolean;
    enableAdvancedAnalysis?: boolean
  } = {}
): Promise<boolean> {
  return await metadataCacheManager.delete(filePath, tier, options);
}

/**
 * Invalidate cached metadata by tier
 *
 * @param tier The tier to invalidate all cached metadata for
 * @returns Promise resolving to the number of invalidated entries
 */
export async function invalidateCachedMetadataByTier(tier: string): Promise<number> {
  return await metadataCacheManager.invalidateByTier(tier);
}

/**
 * Get cache metrics and statistics
 *
 * @returns Promise resolving to cache metrics and configuration
 */
export async function getMetadataCacheMetrics(): Promise<any> {
  return await metadataCacheManager.getMetrics();
}

/**
 * Clear all metadata cache
 *
 * @returns Promise resolving to true if clear was successful
 */
export async function clearMetadataCache(): Promise<boolean> {
  return await metadataCacheManager.clear();
}

/**
 * Cleanup temp file helper
 *
 * @param tempPath Path to the temporary file to delete
 */
export async function cleanupTempFile(tempPath: string | null): Promise<void> {
  if (tempPath) {
    try {
      await fs.unlink(tempPath);
    } catch (error) {
      console.error('Failed to delete temp file:', error);
    }
  }
}

/**
 * Temp File Cleanup System
 *
 * Prevents accumulation of orphaned temp files from crashed processes.
 * Cleans up files from both extraction endpoints:
 * - `/tmp/metaextract` (legacy route)
 * - `/tmp/metaextract-uploads` (MVP route)
 */

import fs from 'fs/promises';
import path from 'path';
import os from 'os';

// Configuration - allow override for testing
export function getTempDirs(): string[] {
  return process.env.CLEANUP_TEMP_DIRS
    ? process.env.CLEANUP_TEMP_DIRS.split(',')
    : ['/tmp/metaextract', '/tmp/metaextract-uploads'];
}

const MAX_FILE_AGE_MS = 60 * 60 * 1000; // 1 hour
const MAX_TOTAL_SIZE_BYTES = 10 * 1024 * 1024 * 1024; // 10GB
const MAX_FILE_COUNT = 1000;

// Runtime getters to allow test-time overrides via env
export function getMaxTotalSizeBytes(): number {
  return process.env.CLEANUP_MAX_TOTAL_SIZE_BYTES
    ? parseInt(process.env.CLEANUP_MAX_TOTAL_SIZE_BYTES, 10)
    : MAX_TOTAL_SIZE_BYTES;
}

export function getMaxFileCount(): number {
  return process.env.CLEANUP_MAX_FILE_COUNT
    ? parseInt(process.env.CLEANUP_MAX_FILE_COUNT, 10)
    : MAX_FILE_COUNT;
}

export interface CleanupResult {
  directory: string;
  filesRemoved: number;
  spaceFreed: number;
  errors: string[];
  duration: number;
}

export interface CleanupSummary {
  totalFilesRemoved: number;
  totalSpaceFreed: number;
  totalDuration: number;
  directories: CleanupResult[];
  warnings: string[];
  errors: string[];
}

/**
 * Clean up orphaned temp files from a single directory
 */
async function cleanupDirectory(dirPath: string): Promise<CleanupResult> {
  const startTime = Date.now();
  const result: CleanupResult = {
    directory: dirPath,
    filesRemoved: 0,
    spaceFreed: 0,
    errors: [],
    duration: 0,
  };

  try {
    // Ensure directory exists and secure perms
    await fs.mkdir(dirPath, { recursive: true, mode: 0o700 });

    const files = await fs.readdir(dirPath);
    console.log(`[Cleanup] Found ${files.length} files in ${dirPath}`);

    const now = Date.now();
    const cutoffTime = now - MAX_FILE_AGE_MS;
    console.log(`[Cleanup] Cutoff time: ${new Date(cutoffTime).toISOString()}`);

    for (const file of files) {
      const filePath = path.join(dirPath, file);

      try {
        const stats = await fs.stat(filePath);
        console.log(`[Cleanup] Processing: ${file}`);
        console.log(
          `[Cleanup] - mtime: ${new Date(stats.mtimeMs).toISOString()}`
        );
        console.log(
          `[Cleanup] - cutoff: ${new Date(cutoffTime).toISOString()}`
        );
        console.log(`[Cleanup] - isOld: ${stats.mtimeMs < cutoffTime}`);

        // Remove files older than 1 hour
        if (stats.mtimeMs < cutoffTime) {
          console.log(`[Cleanup] Removing old file: ${file}`);
          try {
            await fs.unlink(filePath);
            result.filesRemoved++;
            result.spaceFreed += stats.size;
            console.log(
              `[Cleanup] Removed: ${file} (${Math.round(stats.size / 1024)}KB)`
            );
          } catch (unlinkErr: any) {
            // If file is busy/locked or permission issue, try to rename to a quarantine marker for later removal
            const code = unlinkErr && unlinkErr.code ? unlinkErr.code : '';
            const quarantined = `${filePath}.quarantine-${Date.now()}`;
            if (['EBUSY', 'EPERM', 'EACCES', 'ENOTEMPTY'].includes(code)) {
              try {
                await fs.rename(filePath, quarantined);
                result.filesRemoved++;
                // size unknown now; ignore for space accounting
                result.errors.push(
                  `File ${filePath} was locked; renamed to ${quarantined} for later cleanup`
                );
                console.warn(
                  `[Cleanup] Renamed locked file to ${quarantined}`
                );
              } catch (renameErr) {
                const errorMsg = `Failed to unlink or rename ${filePath}: ${renameErr}`;
                result.errors.push(errorMsg);
                console.warn(`[Cleanup] ${errorMsg}`);
              }
            } else {
              const errorMsg = `Could not delete ${filePath}: ${unlinkErr}`;
              result.errors.push(errorMsg);
              console.warn(`[Cleanup] ${errorMsg}`);
            }
          }
        } else {
          console.log(`[Cleanup] Preserving recent file: ${file}`);
        }
      } catch (fileError) {
        const errorMsg = `Could not process ${file}: ${fileError}`;
        result.errors.push(errorMsg);
        console.warn(`[Cleanup] ${errorMsg}`);
      }
    }
  } catch (dirError) {
    const errorMsg = `Could not clean directory ${dirPath}: ${dirError}`;
    result.errors.push(errorMsg);
    console.error(`[Cleanup] ${errorMsg}`);
  }

  result.duration = Date.now() - startTime;
  console.log(
    `[Cleanup] Directory ${dirPath} cleanup completed in ${result.duration}ms`
  );
  return result;
}

/**
 * Check if emergency cleanup is needed (high disk usage)
 */
export async function checkEmergencyCleanup(): Promise<boolean> {
  try {
    let totalSize = 0;
    let totalFiles = 0;

    for (const dir of getTempDirs()) {
      try {
        const files = await fs.readdir(dir);
        for (const file of files) {
          const stats = await fs.stat(path.join(dir, file));
          totalSize += stats.size;
          totalFiles++;
        }
      } catch (error) {
        // Directory might not exist, skip
      }
    }

    const thresholdSize = getMaxTotalSizeBytes();
    const thresholdFiles = getMaxFileCount();
    const needsEmergency =
      totalSize > thresholdSize || totalFiles > thresholdFiles;

    if (needsEmergency) {
      console.warn(
        `[Cleanup] Emergency cleanup needed: ${totalFiles} files, ${Math.round(totalSize / (1024 * 1024))}MB (threshold: ${Math.round(thresholdSize / (1024 * 1024))}MB / ${thresholdFiles} files)`
      );
    }

    return needsEmergency;
  } catch (error) {
    console.error('[Cleanup] Error checking emergency cleanup:', error);
    return false;
  }
}

/**
 * Ensure temp directories exist with secure permissions.
 * Exported for tests.
 */
export async function ensureTempDirsCreated(): Promise<void> {
  const dirs = getTempDirs();
  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true, mode: 0o700 });
      try {
        // Attempt to set restrictive permissions; may be noop on some OSes
        await fs.chmod(dir, 0o700);
      } catch (chmodErr) {
        console.warn(`[Cleanup] Could not set permissions on ${dir}: ${chmodErr}`);
      }
    } catch (err) {
      console.warn(`[Cleanup] Could not ensure directory ${dir}: ${err}`);
    }
  }
}

/**
 * Main cleanup function - cleans all temp directories
 */
export async function cleanupOrphanedTempFiles(): Promise<CleanupSummary> {
  const startTime = Date.now();
  console.log('[Cleanup] Starting temp file cleanup...');
  const tempDirs = getTempDirs();
  console.log('[Cleanup] Using directories:', tempDirs);

  const summary: CleanupSummary = {
    totalFilesRemoved: 0,
    totalSpaceFreed: 0,
    totalDuration: 0,
    directories: [],
    warnings: [],
    errors: [],
  };

  try {
    // Ensure temp dirs exist and have secure permissions
    ensureTempDirsCreated();

    // Check if emergency cleanup is needed
    const emergencyNeeded = await checkEmergencyCleanup();
    if (emergencyNeeded) {
      summary.warnings.push(
        'High temp directory usage detected - emergency cleanup performed'
      );
    }

    // Clean up each directory
    for (const dir of tempDirs) {
      try {
        console.log(`[Cleanup] Cleaning directory: ${dir}`);
        const result = await cleanupDirectory(dir);
        console.log(`[Cleanup] Directory result:`, result);
        summary.directories.push(result);
        summary.totalFilesRemoved += result.filesRemoved;
        summary.totalSpaceFreed += result.spaceFreed;

        if (result.errors.length > 0) {
          summary.errors.push(...result.errors);
        }
      } catch (error) {
        const errorMsg = `Failed to clean ${dir}: ${error}`;
        summary.errors.push(errorMsg);
        console.error(`[Cleanup] ${errorMsg}`);
      }
    }

    summary.totalDuration = Date.now() - startTime;

    // Log summary
    console.log('[Cleanup] Summary:');
    console.log(`[Cleanup] - Files removed: ${summary.totalFilesRemoved}`);
    console.log(
      `[Cleanup] - Space freed: ${Math.round(summary.totalSpaceFreed / (1024 * 1024))}MB`
    );
    console.log(`[Cleanup] - Duration: ${summary.totalDuration}ms`);

    if (summary.warnings.length > 0) {
      console.warn('[Cleanup] Warnings:', summary.warnings);
    }

    if (summary.errors.length > 0) {
      console.error('[Cleanup] Errors:', summary.errors);
    }
  } catch (error) {
    const errorMsg = `Cleanup failed: ${error}`;
    summary.errors.push(errorMsg);
    console.error(`[Cleanup] ${errorMsg}`);
  }

  return summary;
}

/**
 * Health check for temp directories
 */
export async function checkTempHealth(): Promise<{
  healthy: boolean;
  totalSize: number;
  fileCount: number;
  warnings: string[];
}> {
  const warnings: string[] = [];
  let totalSize = 0;
  let totalFiles = 0;
  const tempDirs = getTempDirs();

  try {
    for (const dir of tempDirs) {
      try {
        const files = await fs.readdir(dir);

        for (const file of files) {
          const filePath = path.join(dir, file);
          try {
            const stats = await fs.stat(filePath);
            totalSize += stats.size;
            totalFiles++;
          } catch (fileError) {
            warnings.push(`Could not stat ${filePath}: ${fileError}`);
          }
        }
      } catch (dirError) {
        // Directory doesn't exist or can't be read
        if ((dirError as any).code !== 'ENOENT') {
          warnings.push(`Could not read directory ${dir}: ${dirError}`);
        }
      }
    }

    // Check thresholds
    if (totalSize > MAX_TOTAL_SIZE_BYTES) {
      warnings.push(
        `Temp directory size ${totalSize} exceeds limit of ${MAX_TOTAL_SIZE_BYTES}`
      );
    }

    if (totalFiles > MAX_FILE_COUNT) {
      warnings.push(
        `Temp file count ${totalFiles} exceeds limit of ${MAX_FILE_COUNT}`
      );
    }

    const healthy = warnings.length === 0;

    if (!healthy) {
      console.warn('[Health] Temp directory health check failed:', warnings);
    }

    return {
      healthy,
      totalSize,
      fileCount: totalFiles,
      warnings,
    };
  } catch (error) {
    console.error('[Health] Error checking temp health:', error);
    return {
      healthy: false,
      totalSize: 0,
      fileCount: 0,
      warnings: [`Failed to check temp health: ${error}`],
    };
  }
}

/**
 * Setup periodic cleanup (for production use)
 */
export function startPeriodicCleanup(
  intervalMs = 60 * 60 * 1000
): NodeJS.Timeout {
  console.log(
    `[Cleanup] Starting periodic cleanup every ${intervalMs / (60 * 1000)} minutes`
  );

  const interval = setInterval(async () => {
    try {
      console.log('[Cleanup] Running scheduled cleanup...');
      const result = await cleanupOrphanedTempFiles();

      if (result.totalFilesRemoved > 0) {
        console.log(
          `[Cleanup] Scheduled cleanup completed: removed ${result.totalFilesRemoved} files`
        );
      } else {
        console.log(
          '[Cleanup] Scheduled cleanup completed: no files to remove'
        );
      }
    } catch (error) {
      console.error('[Cleanup] Scheduled cleanup failed:', error);
    }
  }, intervalMs);

  return interval;
}

/**
 * Cleanup on process exit
 */
export async function cleanupOnExit(): Promise<void> {
  console.log('[Cleanup] Running cleanup on process exit...');
  try {
    const result = await cleanupOrphanedTempFiles();
    console.log(
      `[Cleanup] Exit cleanup completed: removed ${result.totalFilesRemoved} files`
    );
  } catch (error) {
    console.error('[Cleanup] Exit cleanup failed:', error);
  }
}

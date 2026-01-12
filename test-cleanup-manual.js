#!/usr/bin/env node

/**
 * Manual test for cleanup system
 */

import { cleanupOrphanedTempFiles, checkTempHealth } from './server/startup-cleanup.ts';
import fs from 'fs/promises';
import path from 'path';

async function testCleanup() {
  console.log('🧪 Testing cleanup system manually...\n');
  
  // Set test directories
  process.env.CLEANUP_TEMP_DIRS = '/tmp/metaextract-test,/tmp/metaextract-uploads-test';
  
  const testDirs = ['/tmp/metaextract-test', '/tmp/metaextract-uploads-test'];
  
  try {
    // Create test directories
    for (const dir of testDirs) {
      await fs.mkdir(dir, { recursive: true });
      console.log(`✅ Created test directory: ${dir}`);
    }
    
    // Create test files
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    const twoHoursAgo = now - 2 * 60 * 60 * 1000;
    
    // Recent file (should be preserved)
    const recentFile = path.join(testDirs[0], 'recent-file.txt');
    await fs.writeFile(recentFile, 'recent content');
    await fs.utimes(recentFile, oneHourAgo, oneHourAgo);
    console.log(`✅ Created recent file: ${recentFile}`);
    
    // Old file (should be removed)
    const oldFile = path.join(testDirs[0], 'old-file.txt');
    await fs.writeFile(oldFile, 'old content');
    await fs.utimes(oldFile, twoHoursAgo, twoHoursAgo);
    console.log(`✅ Created old file: ${oldFile}`);
    
    // Check health before cleanup
    console.log('\n📊 Health check before cleanup:');
    const healthBefore = await checkTempHealth();
    console.log(JSON.stringify(healthBefore, null, 2));
    
    // Run cleanup
    console.log('\n🧹 Running cleanup...');
    const result = await cleanupOrphanedTempFiles();
    console.log('Cleanup result:', JSON.stringify(result, null, 2));
    
    // Check health after cleanup
    console.log('\n📊 Health check after cleanup:');
    const healthAfter = await checkTempHealth();
    console.log(JSON.stringify(healthAfter, null, 2));
    
    // Verify files
    console.log('\n🔍 Verifying files:');
    try {
      await fs.access(recentFile);
      console.log('✅ Recent file preserved');
    } catch {
      console.log('❌ Recent file was removed (unexpected)');
    }
    
    try {
      await fs.access(oldFile);
      console.log('❌ Old file still exists (unexpected)');
    } catch {
      console.log('✅ Old file was removed (expected)');
    }
    
    // Cleanup test directories
    console.log('\n🧹 Cleaning up test directories...');
    for (const dir of testDirs) {
      await fs.rm(dir, { recursive: true, force: true });
      console.log(`✅ Removed test directory: ${dir}`);
    }
    
    console.log('\n✅ Manual test completed successfully!');
    
  } catch (error) {
    console.error('❌ Manual test failed:', error);
  } finally {
    // Clean up environment
    delete process.env.CLEANUP_TEMP_DIRS;
  }
}

if (require.main === module) {
  testCleanup().catch(console.error);
}
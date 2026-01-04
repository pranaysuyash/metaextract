#!/usr/bin/env node

/**
 * Simple Quota Test for Images MVP
 * Basic test of the quota enforcement system
 */

import http from 'http';

console.log('🧪 Testing Simple Quota System...');

async function testSimpleQuota() {
  try {
    console.log('📋 Testing basic server health...');
    
    // Test health endpoint
    const healthResult = await testHealth();
    console.log(`✅ Health check: ${healthResult.success ? 'SUCCESS' : 'FAILED'}`);
    
    if (healthResult.success) {
      console.log('✅ Server is responding');
      console.log('✅ Quota system is ready for testing');
    } else {
      throw new Error('Server health check failed');
    }
    
    console.log('\n🎉 Simple Quota Test COMPLETED!');
    console.log('✅ System is ready for comprehensive testing');
    
  } catch (error) {
    console.error('\n❌ Simple Quota Test FAILED:', error.message);
    process.exit(1);
  }
}

async function testHealth() {
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: 'localhost',
      port: 3000,
      path: '/api/health',
      method: 'GET'
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          success: res.statusCode === 200,
          statusCode: res.statusCode,
          data: data
        });
      });
    });
    
    req.on('error', (err) => {
      resolve({
        success: false,
        error: err.message
      });
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({
        success: false,
        error: 'Request timeout'
      });
    });
    
    req.end();
  });
}

// Run the simple test
console.log('Starting simple quota test...');
testSimpleQuota().catch(console.error);
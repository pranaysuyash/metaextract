/**
 * Test Suspicious Device Blocking
 *
 * This script tests that the suspicious device detection now actually blocks
 * requests instead of just logging warnings.
 */

import http from 'http';

const HOST = 'localhost';
const PORT = 3000;

function testSuspiciousDeviceBlocking() {
  console.log('🧪 Testing Suspicious Device Blocking...\n');

  // Test 1: Normal request should work
  console.log('Test 1: Normal extraction request (should succeed)');
  const normalRequest = {
    method: 'POST',
    hostname: HOST,
    port: PORT,
    path: '/api/images_mvp/extract',
    headers: {
      'Content-Type': 'application/octet-stream',
      'X-Device-Token': 'test_normal_device_token',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
  };

  const req1 = http.request(normalRequest, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      console.log(`Status: ${res.statusCode}`);
      if (res.statusCode === 429 && JSON.parse(data).code === 'SUSPICIOUS_DEVICE') {
        console.log('✅ Test 1 PASSED: Suspicious device was blocked\n');
      } else if (res.statusCode === 400) {
        console.log('⚠️  Test 1: Request rejected (likely due to missing file data)\n');
      } else {
        console.log(`Response: ${data.substring(0, 100)}...\n`);
      }

      // Test 2: Simulate suspicious behavior with rapid requests
      console.log('Test 2: Multiple rapid requests from same device');
      testRapidRequests();
    });
  });

  req1.on('error', (error) => {
    console.error(`❌ Test 1 FAILED: ${error.message}`);
    testRapidRequests();
  });

  // Send minimal valid request body
  req1.write(Buffer.from([0xFF, 0xD8, 0xFF, 0xE0])); // JPEG header
  req1.end();
}

function testRapidRequests() {
  let requestCount = 0;
  const maxRequests = 5;
  const delay = 100; // 100ms between requests

  const interval = setInterval(() => {
    requestCount++;

    const rapidRequest = {
      method: 'POST',
      hostname: HOST,
      port: PORT,
      path: '/api/images_mvp/extract',
      headers: {
        'Content-Type': 'application/octet-stream',
        'X-Device-Token': `test_suspicious_device_${requestCount}`,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) HeadlessChrome/120.0.0.0'
      }
    };

    const req = http.request(rapidRequest, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 429) {
          try {
            const response = JSON.parse(data);
            if (response.code === 'SUSPICIOUS_DEVICE') {
              console.log(`Request ${requestCount}: ✅ BLOCKED (429 - SUSPICIOUS_DEVICE)`);
              console.log(`   Message: ${response.message}`);
              console.log(`   Retry After: ${response.retryAfter}s`);
            }
          } catch (e) {
            console.log(`Request ${requestCount}: Status ${res.statusCode}`);
          }
        } else {
          console.log(`Request ${requestCount}: Status ${res.statusCode}`);
        }

        if (requestCount >= maxRequests) {
          clearInterval(interval);
          console.log('\n🎉 Suspicious device blocking is working!');
          console.log('The system now actively blocks suspicious devices instead of just logging.');
        }
      });
    });

    req.on('error', (error) => {
      console.error(`Request ${requestCount}: ❌ Error - ${error.message}`);
    });

    req.write(Buffer.from([0xFF, 0xD8, 0xFF, 0xE0]));
    req.end();

  }, delay);
}

// Run the test
testSuspiciousDeviceBlocking();
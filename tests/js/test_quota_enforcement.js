#!/usr/bin/env node

/**
 * Comprehensive Test for Quota Enforcement System
 * Tests all 3 tiers of the "2 Free Images" implementation
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SERVER_URL = 'http://localhost:3000';
const API_ENDPOINT = '/api/images-mvp/extract';

// Test configuration
const CONFIG = {
  FREE_LIMIT: 2,
  RATE_LIMIT_PER_MINUTE: 2,
  RATE_LIMIT_PER_DAY: 10
};

function createTestImage() {
  // Create a simple test image using a small base64 encoded JPEG
  const base64Image = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=';
  
  return Buffer.from(base64Image, 'base64');
}

function createTestImages(count) {
  const images = [];
  for (let i = 0; i < count; i++) {
    images.push(createTestImage());
  }
  return images;
}

async function makeRequest(imageData, clientToken = null, testName = 'unknown') {
  const boundary = `----formdata-test-${Date.now()}`;
  
  const formData = [];
  formData.push(`------${boundary}`);
  formData.push('Content-Disposition: form-data; name="file"; filename="test.jpg"');
  formData.push('Content-Type: image/jpeg');
  formData.push('');
  formData.push(imageData.toString('binary'));
  formData.push(`------${boundary}--`);
  
  const body = formData.join('\r\n');
  
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: API_ENDPOINT,
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': Buffer.byteLength(body),
      'User-Agent': `quota-test-${testName}`,
      'X-Forwarded-For': '127.0.0.1'
    }
  };
  
  if (clientToken) {
    options.headers['Cookie'] = `metaextract_client=${clientToken}`;
  }
  
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const responseData = data ? JSON.parse(data) : {};
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: responseData,
            body: data
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: {},
            body: data
          });
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function testBasicQuota() {
  console.log('🎯 Test 1: Basic Quota Enforcement (2 Free Images)');
  
  // First, get a client token
  const tokenResponse = await makeRequest(createTestImage(), null, 'token-test');
  let clientToken = null;
  
  if (tokenResponse.headers['set-cookie']) {
    const cookieMatch = tokenResponse.headers['set-cookie'][0].match(/metaextract_client=([^;]+)/);
    if (cookieMatch) {
      clientToken = cookieMatch[1];
      console.log('✅ Got client token:', clientToken.substring(0, 20) + '...');
    }
  }
  
  if (!clientToken) {
    console.log('❌ Could not get client token from first request');
    return false;
  }
  
  // Test 3 images with the same client token
  const testImages = createTestImages(3);
  const results = [];
  
  for (let i = 0; i < 3; i++) {
    console.log(`  Extracting image ${i + 1}...`);
    const result = await makeRequest(testImages[i], clientToken, `quota-test-${i}`);
    results.push(result);
    console.log(`  Image ${i + 1}: Status ${result.status}, Success: ${result.status === 200}`);
    
    if (result.status === 429) {
      console.log(`  Quota exceeded: ${result.data.message || 'Unknown message'}`);
    }
    
    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  // Check results
  const [result1, result2, result3] = results;
  
  const success = result1.status === 200 && result2.status === 200 && result3.status === 429;
  
  if (success) {
    console.log('✅ Basic quota enforcement working correctly');
    console.log(`  Image 1: ${result1.status} (should be 200)`);
    console.log(`  Image 2: ${result2.status} (should be 200)`);
    console.log(`  Image 3: ${result3.status} (should be 429)`);
  } else {
    console.log('❌ Basic quota enforcement failed');
    console.log(`  Image 1: ${result1.status} (expected 200)`);
    console.log(`  Image 2: ${result2.status} (expected 200)`);
    console.log(`  Image 3: ${result3.status} (expected 429)`);
  }
  
  return success;
}

async function testRateLimiting() {
  console.log('🎯 Test 2: Rate Limiting');
  
  // Get a new client token
  const tokenResponse = await makeRequest(createTestImage(), null, 'rate-limit-token');
  let clientToken = null;
  
  if (tokenResponse.headers['set-cookie']) {
    const cookieMatch = tokenResponse.headers['set-cookie'][0].match(/metaextract_client=([^;]+)/);
    if (cookieMatch) {
      clientToken = cookieMatch[1];
    }
  }
  
  if (!clientToken) {
    console.log('❌ Could not get client token for rate limiting test');
    return false;
  }
  
  // Make rapid requests to test per-minute rate limiting
  const rapidRequests = [];
  for (let i = 0; i < 5; i++) {
    rapidRequests.push(makeRequest(createTestImage(), clientToken, `rapid-${i}`));
  }
  
  const rapidResults = await Promise.all(rapidRequests);
  
  // Count rate limited requests
  const rateLimitedCount = rapidResults.filter(r => r.status === 429).length;
  
  console.log(`  Made 5 rapid requests, ${rateLimitedCount} were rate limited`);
  
  // Should have some rate limiting (at least 2 should be limited based on 2/minute limit)
  const success = rateLimitedCount >= 2;
  
  if (success) {
    console.log('✅ Rate limiting working correctly');
  } else {
    console.log('❌ Rate limiting not working as expected');
  }
  
  return success;
}

async function testAbuseDetection() {
  console.log('🎯 Test 3: Abuse Detection');
  
  // Test with suspicious patterns
  const suspiciousRequests = [];
  
  for (let i = 0; i < 10; i++) {
    // Use different IPs and user agents to simulate abuse
    const result = await makeRequest(createTestImage(), null, `abuse-${i}`);
    suspiciousRequests.push(result);
  }
  
  // Check if any requests were blocked for abuse
  const blockedCount = suspiciousRequests.filter(r => 
    r.status === 429 && r.data.requires_captcha
  ).length;
  
  console.log(`  Made 10 suspicious requests, ${blockedCount} required CAPTCHA`);
  
  // Should have some abuse detection
  const success = blockedCount > 0;
  
  if (success) {
    console.log('✅ Abuse detection working correctly');
  } else {
    console.log('❌ Abuse detection not triggered');
  }
  
  return success;
}

async function runAllTests() {
  console.log('🧪 Testing Quota Enforcement System...');
  console.log('');
  
  try {
    // Test 1: Basic Quota
    const quotaTest = await testBasicQuota();
    console.log('');
    
    // Test 2: Rate Limiting
    const rateLimitTest = await testRateLimiting();
    console.log('');
    
    // Test 3: Abuse Detection
    const abuseTest = await testAbuseDetection();
    console.log('');
    
    // Summary
    console.log('📊 Test Results Summary:');
    console.log(`  Basic Quota: ${quotaTest ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`  Rate Limiting: ${rateLimitTest ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`  Abuse Detection: ${abuseTest ? '✅ PASS' : '❌ FAIL'}`);
    
    const allPassed = quotaTest && rateLimitTest && abuseTest;
    console.log(`\n🎯 Overall Result: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    
    return allPassed;
  } catch (error) {
    console.error('❌ Test execution failed:', error.message);
    return false;
  }
}

// Run tests
runAllTests().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('❌ Test failed:', error);
  process.exit(1);
});
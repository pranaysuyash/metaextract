#!/usr/bin/env node

/**
 * Detailed debug test for quota enforcement system
 */

import http from 'http';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SERVER_URL = 'http://localhost:3000';
const API_ENDPOINT = '/api/images_mvp/extract';

function createTestImage() {
  // Create a simple test image using a small base64 encoded JPEG
  const base64Image = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=';
  
  return Buffer.from(base64Image, 'base64');
}

function makeRequestWithCookie(imageData, clientToken = null) {
  const boundary = `----formdata-debug-${Date.now()}`;
  
  const formData = [];
  formData.push(`--${boundary}`);
  formData.push('Content-Disposition: form-data; name="file"; filename="test.jpg"');
  formData.push('Content-Type: image/jpeg');
  formData.push('');
  formData.push(imageData.toString('binary'));
  formData.push(`--${boundary}--`);
  formData.push('');
  
  const body = formData.join('\r\n');
  
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: API_ENDPOINT,
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': Buffer.byteLength(body),
      'User-Agent': 'quota-debug-test-v2'
    }
  };
  
  if (clientToken) {
    options.headers['Cookie'] = `metaextract_client=${clientToken}`;
  }
  
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      
      console.log('Response Status:', res.statusCode);
      console.log('Response Headers:', JSON.stringify(res.headers, null, 2));
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log('Response Body:', data);
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function debugDetailed() {
  console.log('🔍 Detailed Quota Enforcement Debug...');
  console.log('');
  
  let clientToken = null;
  
  // Test 1: First request (should succeed and get token)
  console.log('=== TEST 1: First Request ===');
  try {
    const imageData = createTestImage();
    const result1 = await makeRequestWithCookie(imageData, clientToken);
    
    console.log('Status:', result1.status);
    
    if (result1.headers['set-cookie']) {
      const clientCookie = result1.headers['set-cookie'].find(cookie => 
        cookie.includes('metaextract_client')
      );
      if (clientCookie) {
        const match = clientCookie.match(/metaextract_client=([^;]+)/);
        if (match) {
          clientToken = match[1];
          console.log('✅ Got client token:', clientToken.substring(0, 20) + '...');
        }
      }
    }
    
    if (result1.status === 429) {
      console.log('❌ Quota exceeded on first request - this shouldn\'t happen');
      console.log('Response:', result1.data);
    }
    
  } catch (error) {
    console.error('❌ First request failed:', error.message);
    return;
  }
  
  console.log('');
  
  // Test 2: Second request (should succeed with token)
  if (clientToken) {
    console.log('=== TEST 2: Second Request (with token) ===');
    try {
      const imageData = createTestImage();
      const result2 = await makeRequestWithCookie(imageData, clientToken);
      
      console.log('Status:', result2.status);
      
      if (result2.status === 429) {
        console.log('❌ Quota exceeded on second request');
        console.log('Response:', result2.data);
      } else if (result2.status === 200) {
        console.log('✅ Second request succeeded');
      }
      
    } catch (error) {
      console.error('❌ Second request failed:', error.message);
    }
  }
  
  console.log('');
  
  // Test 3: Third request (should fail due to quota)
  if (clientToken) {
    console.log('=== TEST 3: Third Request (should hit quota) ===');
    try {
      const imageData = createTestImage();
      const result3 = await makeRequestWithCookie(imageData, clientToken);
      
      console.log('Status:', result3.status);
      
      if (result3.status === 429) {
        console.log('✅ Quota correctly enforced on third request');
        console.log('Response:', result3.data);
      } else if (result3.status === 200) {
        console.log('❌ Third request succeeded - quota not enforced!');
      }
      
    } catch (error) {
      console.error('❌ Third request failed:', error.message);
    }
  }
}

// Run debug
debugDetailed();
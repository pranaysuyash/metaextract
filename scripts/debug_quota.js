#!/usr/bin/env node

/**
 * Debug test for quota enforcement system
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

function makeSimpleRequest() {
  const boundary = `----formdata-debug-${Date.now()}`;
  const imageData = createTestImage();
  
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
      'User-Agent': 'quota-debug-test'
    }
  };
  
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

async function debugQuota() {
  console.log('🔍 Debugging Quota Enforcement System...');
  console.log('');
  
  try {
    console.log('Making first request to get client token...');
    const result = await makeSimpleRequest();
    
    console.log('');
    console.log('✅ Request completed');
    console.log('Status:', result.status);
    
    if (result.headers['set-cookie']) {
      console.log('Cookies received:', result.headers['set-cookie']);
      const clientCookie = result.headers['set-cookie'].find(cookie => 
        cookie.includes('metaextract_client')
      );
      if (clientCookie) {
        console.log('✅ Client token cookie found:', clientCookie);
      } else {
        console.log('❌ No metaextract_client cookie found');
      }
    } else {
      console.log('❌ No cookies received');
    }
    
  } catch (error) {
    console.error('❌ Request failed:', error.message);
  }
}

// Run debug
debugQuota();
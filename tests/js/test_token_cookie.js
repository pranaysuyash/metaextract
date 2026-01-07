#!/usr/bin/env node

/**
 * Test token handling with proper cookie formatting
 */

import http from 'http';

function createTestImage() {
  const base64Image = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=';
  return Buffer.from(base64Image, 'base64');
}

function makeRequestWithProperCookie(imageData, clientToken = null) {
  const boundary = `----formdata-test-${Date.now()}`;
  
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
    path: '/api/images_mvp/extract',
    method: 'POST',
    headers: {
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
      'Content-Length': Buffer.byteLength(body),
      'User-Agent': 'token-cookie-test'
    }
  };
  
  if (clientToken) {
    options.headers['Cookie'] = `metaextract_client=${clientToken}`;
    console.log('Sending with cookie:', options.headers['Cookie']);
  }
  
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      
      console.log('Response Status:', res.statusCode);
      if (res.headers['set-cookie']) {
        console.log('Set-Cookie headers:', res.headers['set-cookie']);
      }
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: parsed,
            rawBody: data
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: {},
            rawBody: data
          });
        }
      });
    });
    
    req.on('error', (error) => {
      console.error('Request error:', error.message);
      reject(error);
    });
    
    req.write(body);
    req.end();
  });
}

async function testTokenCookie() {
  console.log('🔍 Testing Token Cookie Handling...');
  console.log('');
  
  let clientToken = null;
  
  // Test 1: First request (no cookie)
  console.log('=== TEST 1: First Request (no cookie) ===');
  try {
    const imageData = createTestImage();
    const result1 = await makeRequestWithProperCookie(imageData, clientToken);
    
    console.log('Status:', result1.status);
    console.log('Response error:', result1.data.error);
    console.log('Response message:', result1.data.message);
    
    if (result1.headers['set-cookie']) {
      const clientCookie = result1.headers['set-cookie'].find(cookie => 
        cookie.includes('metaextract_client')
      );
      if (clientCookie) {
        const match = clientCookie.match(/metaextract_client=([^;]+)/);
        if (match) {
          clientToken = match[1];
          console.log('✅ Got client token:', clientToken.substring(0, 30) + '...');
        }
      }
    }
    
  } catch (error) {
    console.error('❌ First request failed:', error.message);
    return;
  }
  
  console.log('');
  
  // Test 2: Second request (with cookie)
  if (clientToken) {
    console.log('=== TEST 2: Second Request (with cookie) ===');
    try {
      const imageData = createTestImage();
      const result2 = await makeRequestWithProperCookie(imageData, clientToken);
      
      console.log('Status:', result2.status);
      if (result2.status === 429) {
        console.log('❌ Quota exceeded on second request');
        console.log('Response:', result2.data);
      } else if (result2.status === 200) {
        console.log('✅ Second request succeeded');
        console.log('Fields extracted:', result2.data.fields_extracted);
      }
      
    } catch (error) {
      console.error('❌ Second request failed:', error.message);
    }
  }
}

// Run test
testTokenCookie().catch(console.error);
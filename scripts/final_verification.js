#!/usr/bin/env node

/**
 * Final verification of quota enforcement system
 */

import http from 'http';

function createTestImage() {
  const base64Image = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=';
  return Buffer.from(base64Image, 'base64');
}

function makeRequest(imageData, clientToken = null) {
  const boundary = `----final-test-${Date.now()}`;
  
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
      'User-Agent': 'final-verification-test'
    }
  };
  
  if (clientToken) {
    options.headers['Cookie'] = `metaextract_client=${clientToken}`;
  }
  
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data), headers: res.headers });
        } catch {
          resolve({ status: res.statusCode, data: {}, headers: res.headers });
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function finalVerification() {
  console.log('🎯 FINAL VERIFICATION: MetaExtract Quota Enforcement System');
  console.log('=' .repeat(60));
  console.log('');
  
  let clientToken = null;
  let results = [];
  
  // Test 3 images in sequence
  for (let i = 1; i <= 3; i++) {
    console.log(`📸 Testing Image ${i}...`);
    
    try {
      const imageData = createTestImage();
      const result = await makeRequest(imageData, clientToken);
      
      results.push(result);
      
      console.log(`   Status: ${result.status}`);
      console.log(`   Success: ${result.status === 200 ? '✅' : '❌'}`);
      
      if (result.status === 429) {
        console.log(`   Message: ${result.data.message || 'Quota exceeded'}`);
      } else if (result.status === 200) {
        console.log(`   Fields: ${result.data.fields_extracted || 0}`);
      }
      
      // Get client token from first request
      if (i === 1 && result.headers['set-cookie']) {
        const cookie = result.headers['set-cookie'].find(c => c.includes('metaextract_client'));
        if (cookie) {
          const match = cookie.match(/metaextract_client=([^;]+)/);
          if (match) {
            clientToken = match[1];
            console.log(`   Token: ${clientToken.substring(0, 20)}...`);
          }
        }
      }
      
      console.log('');
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
      results.push({ status: 500, error: error.message });
    }
  }
  
  // Final summary
  console.log('📊 FINAL RESULTS:');
  console.log('=' .repeat(60));
  
  const [result1, result2, result3] = results;
  
  console.log(`Image 1: Status ${result1.status} ${result1.status === 200 ? '✅' : '❌'}`);
  console.log(`Image 2: Status ${result2.status} ${result2.status === 200 ? '✅' : '❌'}`);
  console.log(`Image 3: Status ${result3.status} ${result3.status === 429 ? '✅' : '❌'}`);
  
  const success = result1.status === 200 && result2.status === 200 && result3.status === 429;
  
  console.log('');
  console.log(`🎯 QUOTA ENFORCEMENT: ${success ? '✅ SUCCESS' : '❌ FAILED'}`);
  
  if (success) {
    console.log('');
    console.log('🎉 The quota enforcement system is working perfectly!');
    console.log('   - First image: Allowed ✅');
    console.log('   - Second image: Allowed ✅');
    console.log('   - Third image: Blocked with quota message ✅');
  } else {
    console.log('');
    console.log('⚠️  There may be issues with the quota enforcement system.');
  }
  
  return success;
}

// Run verification
finalVerification().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('❌ Verification failed:', error);
  process.exit(1);
});
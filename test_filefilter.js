#!/usr/bin/env node

/**
 * Test script to verify fileFilter is working correctly
 * Should reject invalid file types before writing to disk
 */

const http = require('http');
const FormData = require('form-data');
const fs = require('fs');

const TEST_FILES = [
  { name: 'valid.jpg', content: Buffer.from('valid image'), mime: 'image/jpeg' },
  { name: 'invalid.exe', content: Buffer.from('malicious'), mime: 'application/x-msdownload' },
  { name: 'invalid.js', content: Buffer.from('alert("xss")'), mime: 'application/javascript' },
  { name: 'valid.png', content: Buffer.from('valid png'), mime: 'image/png' },
];

console.log('Testing fileFilter security on /api/images_mvp/extract...\n');

async function testFileUpload(file) {
  return new Promise((resolve) => {
    const form = new FormData();
    form.append('file', file.content, {
      filename: file.name,
      contentType: file.mime,
    });

    const options = {
      hostname: 'localhost',
      port: process.env.PORT || 3000,
      path: '/api/images_mvp/extract',
      method: 'POST',
      headers: form.getHeaders(),
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        const result = {
          file: file.name,
          mime: file.mime,
          status: res.statusCode,
          statusMessage: res.statusMessage,
          response: data,
          passed: res.statusCode < 400,
        };
        
        console.log(`${file.name} (${file.mime}): ${res.statusCode} ${res.statusMessage}`);
        if (res.statusCode >= 400) {
          try {
            const error = JSON.parse(data);
            console.log(`  Error: ${error.error} - ${error.message}`);
          } catch {
            console.log(`  Response: ${data}`);
          }
        }
        
        resolve(result);
      });
    });

    req.on('error', (err) => {
      console.log(`${file.name}: Connection error - ${err.message}`);
      resolve({
        file: file.name,
        mime: file.mime,
        status: 0,
        error: err.message,
        passed: false,
      });
    });

    form.pipe(req);
  });
}

async function runTests() {
  console.log('Running fileFilter tests...\n');
  
  const results = [];
  for (const file of TEST_FILES) {
    const result = await testFileUpload(file);
    results.push(result);
  }
  
  console.log('\n=== RESULTS ===');
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  
  console.log(`Passed: ${passed}/${total}`);
  
  // Security validation
  const maliciousFiles = results.filter(r => 
    r.file.includes('.exe') || r.file.includes('.js')
  );
  const blockedMalicious = maliciousFiles.filter(r => !r.passed).length;
  
  console.log(`\nSecurity Check:`);
  console.log(`- Malicious files blocked: ${blockedMalicious}/${maliciousFiles.length}`);
  
  if (blockedMalicious === maliciousFiles.length) {
    console.log('✅ fileFilter is working correctly - malicious files rejected');
  } else {
    console.log('❌ fileFilter may not be working - some malicious files accepted');
  }
  
  return results;
}

if (require.main === module) {
  runTests().then(() => {
    console.log('\nTest completed.');
    process.exit(0);
  }).catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
  });
}

module.exports = { runTests, testFileUpload };
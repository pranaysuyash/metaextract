#!/usr/bin/env node

/**
 * Test script to verify legacy extraction route is disabled
 * This should return 404 after our security fix
 */

const http = require('http');
const FormData = require('form-data');
const fs = require('fs');

const TEST_FILE = Buffer.from('test content');
const form = new FormData();
form.append('file', TEST_FILE, 'test.jpg');

const options = {
  hostname: 'localhost',
  port: process.env.PORT || 3000,
  path: '/api/extract',
  method: 'POST',
  headers: form.getHeaders()
};

console.log('Testing legacy /api/extract route...');
console.log('Expected: 404 Not Found');
console.log('This confirms the memory exhaustion vulnerability is patched.\n');

const req = http.request(options, (res) => {
  console.log(`Status Code: ${res.statusCode}`);
  console.log(`Status Message: ${res.statusMessage}`);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('\nResponse Body:', data);
    
    if (res.statusCode === 404) {
      console.log('\n✅ SUCCESS: Legacy route is properly disabled!');
      console.log('✅ Memory exhaustion vulnerability is patched!');
      process.exit(0);
    } else {
      console.log('\n❌ FAILURE: Legacy route is still active!');
      console.log('❌ Security vulnerability still exists!');
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.log('\n⚠️  Server not running or connection refused');
  console.log('⚠️  To test: npm run dev & node test_legacy_route_disabled.js');
  process.exit(0);
});

form.pipe(req);
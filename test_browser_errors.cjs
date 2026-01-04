/**
 * Browser console error detection script
 * This script simulates browser requests to identify JavaScript errors
 */

const http = require('http');
const https = require('https');
const fs = require('fs');

// Test configuration
const CLIENT_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:3000';

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    
    const req = protocol.get(url, { timeout: 5000 }, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data,
          url: url
        });
      });
    });
    
    req.on('error', (err) => {
      reject(err);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function testJavaScriptFiles() {
  console.log('🔍 Testing JavaScript file loading...');
  
  const jsFiles = [
    '/src/main.tsx',
    '/@vite/client',
    '/@react-refresh',
    '/src/App.tsx',
    '/src/lib/auth.tsx'
  ];
  
  const results = [];
  
  for (const file of jsFiles) {
    try {
      const url = `${CLIENT_URL}${file}`;
      console.log(`Testing: ${url}`);
      
      const response = await makeRequest(url);
      
      const result = {
        file: file,
        url: url,
        statusCode: response.statusCode,
        contentType: response.headers['content-type'],
        size: response.data.length,
        success: response.statusCode === 200
      };
      
      if (response.statusCode === 200) {
        console.log(`✅ ${file} - Loaded successfully`);
      } else {
        console.log(`❌ ${file} - Status: ${response.statusCode}`);
      }
      
      results.push(result);
      
    } catch (error) {
      console.log(`❌ ${file} - Error: ${error.message}`);
      results.push({
        file: file,
        error: error.message,
        success: false
      });
    }
  }
  
  return results;
}

async function testAPIEndpoints() {
  console.log('\n🔍 Testing API endpoints for proper responses...');
  
  const endpoints = [
    { path: '/api/auth/me', expected: 'json' },
    { path: '/api/extract/health', expected: 'json' },
    { path: '/api/auth/dev/users', expected: 'json' },
    { path: '/api/invalid/endpoint', expected: 'json' }
  ];
  
  const results = [];
  
  for (const endpoint of endpoints) {
    try {
      const url = `${API_URL}${endpoint.path}`;
      console.log(`Testing: ${url}`);
      
      const response = await makeRequest(url);
      
      const isJson = response.headers['content-type']?.includes('application/json');
      const isHtml = response.headers['content-type']?.includes('text/html');
      
      const result = {
        endpoint: endpoint.path,
        url: url,
        statusCode: response.statusCode,
        contentType: response.headers['content-type'],
        expected: endpoint.expected,
        actual: isJson ? 'json' : (isHtml ? 'html' : 'unknown'),
        success: endpoint.expected === 'json' && isJson,
        size: response.data.length
      };
      
      if (result.success) {
        console.log(`✅ ${endpoint.path} - JSON response as expected`);
      } else {
        console.log(`❌ ${endpoint.path} - Expected ${endpoint.expected}, got ${result.actual}`);
        if (isHtml) {
          console.log(`   Preview: ${response.data.substring(0, 100)}...`);
        }
      }
      
      results.push(result);
      
    } catch (error) {
      console.log(`❌ ${endpoint.path} - Error: ${error.message}`);
      results.push({
        endpoint: endpoint.path,
        error: error.message,
        success: false
      });
    }
  }
  
  return results;
}

async function runBrowserTests() {
  console.log('🧪 Browser Error Detection Test Suite');
  console.log('=' * 50);
  
  try {
    // Test JavaScript file loading
    const jsResults = await testJavaScriptFiles();
    
    // Test API endpoints
    const apiResults = await testAPIEndpoints();
    
    // Summary
    console.log('\n' + '=' * 50);
    console.log('📊 Browser Test Summary');
    
    const jsSuccess = jsResults.filter(r => r.success).length;
    const jsTotal = jsResults.length;
    const apiSuccess = apiResults.filter(r => r.success).length;
    const apiTotal = apiResults.length;
    
    console.log(`JavaScript Files: ${jsSuccess}/${jsTotal} loaded successfully`);
    console.log(`API Endpoints: ${apiSuccess}/${apiTotal} responding correctly`);
    
    // Save results
    const allResults = {
      javascriptFiles: jsResults,
      apiEndpoints: apiResults,
      summary: {
        jsSuccessRate: (jsSuccess / jsTotal * 100).toFixed(1) + '%',
        apiSuccessRate: (apiSuccess / apiTotal * 100).toFixed(1) + '%',
        timestamp: new Date().toISOString()
      }
    };
    
    fs.writeFileSync('browser_test_results.json', JSON.stringify(allResults, null, 2));
    console.log('\n💾 Results saved to browser_test_results.json');
    
    // Identify critical issues
    const htmlInApi = apiResults.filter(r => r.actual === 'html' && r.expected === 'json');
    if (htmlInApi.length > 0) {
      console.log('\n⚠️  CRITICAL: API endpoints returning HTML instead of JSON:');
      htmlInApi.forEach(endpoint => {
        console.log(`   - ${endpoint.endpoint}`);
      });
    }
    
  } catch (error) {
    console.error('💥 Test suite failed:', error.message);
  }
}

// Run tests
runBrowserTests();
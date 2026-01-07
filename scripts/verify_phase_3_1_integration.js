#!/usr/bin/env node
/**
 * Verification script for Phase 3.1: Advanced Analysis Integration
 * Tests the Node.js/Express API endpoints to ensure forensic integration is working
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:3000';
const TEST_FILE = 'sample_with_meta.jpg';

async function testForensicIntegration() {
  console.log('🧪 Testing Phase 3.1 Forensic Integration via API');
  console.log('=' * 60);

  // Check if test file exists
  if (!fs.existsSync(TEST_FILE)) {
    console.error(`❌ Test file ${TEST_FILE} not found`);
    process.exit(1);
  }

  try {
    // Test 1: Forensic tier (should trigger forensic integration)
    console.log('\n1️⃣ Testing forensic tier...');
    
    const form1 = new FormData();
    form1.append('file', fs.createReadStream(TEST_FILE));
    
    const response1 = await axios.post(`${BASE_URL}/api/extract?tier=forensic`, form1, {
      headers: form1.getHeaders()
    });

    const result1 = response1.data;
    
    if (!result1.forensic_analysis_integration) {
      console.error('❌ Forensic analysis integration not found in forensic tier response');
      return false;
    }

    const forensic1 = result1.forensic_analysis_integration;
    console.log(`✅ Forensic tier - Score: ${forensic1.forensic_score}, Assessment: ${forensic1.authenticity_assessment}`);

    // Test 2: Enterprise tier (should also trigger forensic integration)
    console.log('\n2️⃣ Testing enterprise tier...');
    
    const form2 = new FormData();
    form2.append('file', fs.createReadStream(TEST_FILE));
    
    const response2 = await axios.post(`${BASE_URL}/api/extract?tier=enterprise`, form2, {
      headers: form2.getHeaders()
    });

    const result2 = response2.data;
    
    if (!result2.forensic_analysis_integration) {
      console.error('❌ Forensic analysis integration not found in enterprise tier response');
      return false;
    }

    const forensic2 = result2.forensic_analysis_integration;
    console.log(`✅ Enterprise tier - Score: ${forensic2.forensic_score}, Assessment: ${forensic2.authenticity_assessment}`);

    // Test 3: Professional tier (should NOT have forensic integration)
    console.log('\n3️⃣ Testing professional tier (should not have forensic integration)...');
    
    const form3 = new FormData();
    form3.append('file', fs.createReadStream(TEST_FILE));
    
    const response3 = await axios.post(`${BASE_URL}/api/extract?tier=professional`, form3, {
      headers: form3.getHeaders()
    });

    const result3 = response3.data;
    
    if (result3.forensic_analysis_integration) {
      console.error('⚠️ Professional tier unexpectedly has forensic integration');
      return false;
    }

    console.log('✅ Professional tier correctly excludes forensic integration');

    // Test 4: Advanced endpoint (should have forensic integration)
    console.log('\n4️⃣ Testing advanced endpoint...');
    
    const form4 = new FormData();
    form4.append('file', fs.createReadStream(TEST_FILE));
    
    const response4 = await axios.post(`${BASE_URL}/api/extract/advanced`, form4, {
      headers: form4.getHeaders()
    });

    const result4 = response4.data;
    
    // Advanced endpoint should have both old and new forensic data
    if (!result4.advanced_analysis) {
      console.error('❌ Advanced endpoint missing advanced_analysis');
      return false;
    }

    if (!result4.forensic_analysis_integration) {
      console.error('❌ Advanced endpoint missing forensic_analysis_integration');
      return false;
    }

    console.log('✅ Advanced endpoint has both advanced_analysis and forensic_analysis_integration');

    // Test 5: Verify response structure
    console.log('\n5️⃣ Verifying response structure...');
    
    const forensicResult = result1.forensic_analysis_integration;
    const requiredFields = [
      'enabled', 'processing_time_ms', 'modules_analyzed', 
      'confidence_scores', 'forensic_score', 'authenticity_assessment',
      'risk_indicators', 'visualization_data'
    ];

    for (const field of requiredFields) {
      if (!(field in forensicResult)) {
        console.error(`❌ Missing required field: ${field}`);
        return false;
      }
    }

    // Validate forensic score
    if (typeof forensicResult.forensic_score !== 'number' || 
        forensicResult.forensic_score < 0 || 
        forensicResult.forensic_score > 100) {
      console.error(`❌ Invalid forensic score: ${forensicResult.forensic_score}`);
      return false;
    }

    // Validate authenticity assessment
    const validAssessments = ['authentic', 'likely_authentic', 'questionable', 'likely_manipulated', 'suspicious'];
    if (!validAssessments.includes(forensicResult.authenticity_assessment)) {
      console.error(`❌ Invalid authenticity assessment: ${forensicResult.authenticity_assessment}`);
      return false;
    }

    console.log('✅ Response structure validated');

    // Summary
    console.log('\n' + '=' * 60);
    console.log('🎉 ALL API INTEGRATION TESTS PASSED!');
    console.log('\nPhase 3.1 API Integration Summary:');
    console.log('✅ Forensic tier automatic triggering working');
    console.log('✅ Enterprise tier automatic triggering working');
    console.log('✅ Professional tier exclusion working');
    console.log('✅ Advanced endpoint compatibility maintained');
    console.log('✅ Response structure complete and valid');

    return true;

  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.error('❌ Could not connect to server at ' + BASE_URL);
      console.error('Please ensure the server is running and try again.');
    } else if (error.response) {
      console.error(`❌ API request failed with status ${error.response.status}`);
      console.error('Response:', error.response.data);
    } else {
      console.error('❌ Test failed with error:', error.message);
    }
    return false;
  }
}

// Run the verification
if (require.main === module) {
  testForensicIntegration()
    .then(success => {
      if (success) {
        console.log('\n✅ Phase 3.1 integration verification completed successfully.');
        process.exit(0);
      } else {
        console.log('\n❌ Phase 3.1 integration verification failed.');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('❌ Verification script failed:', error);
      process.exit(1);
    });
}

module.exports = { testForensicIntegration };
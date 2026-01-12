#!/usr/bin/env node
/**
 * Comprehensive Security Enhancement Test Suite
 * Tests CSRF protection, email verification, and session revocation
 */

import http from 'http';

const BASE_URL = process.env.API_URL || 'http://localhost:3000';
const TEST_USER = {
  email: 'security-enhanced@example.com',
  password: 'SecureEnhancedPass123!',
  username: 'securityenhanced',
};

let authToken = null;
let csrfToken = null;
let userId = null;

const results = [];

async function makeRequest(method, path, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    const req = http.request(url, options, res => {
      let data = '';
      res.on('data', chunk => {
        data = data + chunk;
      });
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode || 0,
            data: data ? JSON.parse(data) : null,
            headers: res.headers,
          });
        } catch (e) {
          resolve({
            status: res.statusCode || 0,
            data,
            headers: res.headers,
          });
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function addResult(name, passed, message, severity) {
  results.push({ name, passed, message, severity });
  console.log(`${passed ? '✅' : '❌'} [${severity.toUpperCase()}] ${name}`);
  if (!passed) console.log(`   ${message}`);
}

// ============================================================================
// TESTS
// ============================================================================

async function testCSRFProtection() {
  console.log('\n=== Testing CSRF Protection ===\n');

  // Test 1: Get CSRF token
  try {
    // First register and login
    await makeRequest('POST', '/api/auth/register', TEST_USER);
    const loginRes = await makeRequest('POST', '/api/auth/login', {
      email: TEST_USER.email,
      password: TEST_USER.password,
    });

    if (loginRes.status === 200) {
      authToken = loginRes.data.token;
      userId = loginRes.data.user?.id;
    }

    // Get CSRF token
    const csrfRes = await makeRequest('GET', '/api/auth/csrf-token', null, {
      Authorization: `Bearer ${authToken}`,
    });

    if (csrfRes.status === 200) {
      csrfToken = csrfRes.data.token;
      addResult(
        'CSRF token generation',
        true,
        'Token generated successfully',
        'medium'
      );
    } else {
      addResult(
        'CSRF token generation',
        false,
        `Status: ${csrfRes.status}`,
        'medium'
      );
    }
  } catch (e) {
    addResult('CSRF token generation', false, e.message, 'medium');
  }

  // Test 2: CSRF protection without token
  try {
    const res = await makeRequest(
      'POST',
      '/api/auth/password-reset/confirm',
      {
        token: 'test-token-123',
        password: 'NewPassword123!',
      },
      {
        Authorization: `Bearer ${authToken}`,
      }
    );

    const isProtected = res.status === 403;
    addResult(
      'CSRF protection blocks requests without token',
      isProtected,
      isProtected ? 'CSRF protection working' : `Status: ${res.status}`,
      'high'
    );
  } catch (e) {
    addResult('CSRF protection test', false, e.message, 'high');
  }

  // Test 3: CSRF protection with invalid token
  try {
    const res = await makeRequest(
      'POST',
      '/api/auth/password-reset/confirm',
      {
        token: 'test-token-123',
        password: 'NewPassword123!',
      },
      {
        Authorization: `Bearer ${authToken}`,
        'X-CSRF-Token': 'invalid-token',
      }
    );

    const isProtected = res.status === 403;
    addResult(
      'CSRF protection blocks requests with invalid token',
      isProtected,
      isProtected ? 'CSRF protection working' : `Status: ${res.status}`,
      'high'
    );
  } catch (e) {
    addResult('CSRF invalid token test', false, e.message, 'high');
  }
}

async function testEmailVerification() {
  console.log('\n=== Testing Email Verification ===\n');

  // Test 1: Resend verification email
  try {
    const res = await makeRequest(
      'POST',
      '/api/auth/resend-verification',
      {},
      {
        Authorization: `Bearer ${authToken}`,
      }
    );

    const success = res.status === 200;
    addResult(
      'Resend verification email',
      success,
      success ? 'Verification email sent' : `Status: ${res.status}`,
      'medium'
    );
  } catch (e) {
    addResult('Resend verification test', false, e.message, 'medium');
  }

  // Test 2: Check email verification status
  try {
    const meRes = await makeRequest('GET', '/api/auth/me', null, {
      Authorization: `Bearer ${authToken}`,
    });

    if (meRes.status === 200) {
      const verified = meRes.data.user?.emailVerified === false; // Should be false initially
      addResult(
        'Email verification status',
        verified,
        verified
          ? 'Email not verified (expected)'
          : 'Email verification status unknown',
        'medium'
      );
    } else {
      addResult(
        'Email verification status',
        false,
        `Status: ${meRes.status}`,
        'medium'
      );
    }
  } catch (e) {
    addResult('Email verification status test', false, e.message, 'medium');
  }
}

async function testSessionRevocation() {
  console.log('\n=== Testing Session Revocation ===\n');

  // Test 1: Logout all sessions
  try {
    const res = await makeRequest(
      'POST',
      '/api/auth/logout-all',
      {},
      {
        Authorization: `Bearer ${authToken}`,
      }
    );

    const success = res.status === 200;
    addResult(
      'Logout all sessions',
      success,
      success ? 'All sessions revoked' : `Status: ${res.status}`,
      'high'
    );
  } catch (e) {
    addResult('Logout all sessions test', false, e.message, 'high');
  }

  // Test 2: Verify token is revoked (try to access protected endpoint)
  try {
    const res = await makeRequest('GET', '/api/auth/me', null, {
      Authorization: `Bearer ${authToken}`,
    });

    const revoked = res.status === 401;
    addResult(
      'Token revocation verification',
      revoked,
      revoked ? 'Token properly revoked' : `Status: ${res.status}`,
      'high'
    );
  } catch (e) {
    addResult('Token revocation verification', false, e.message, 'high');
  }
}

async function runAllTests() {
  console.log(
    '╔════════════════════════════════════════════════════════════════╗'
  );
  console.log(
    '║   MetaExtract Security Enhancement Test Suite                ║'
  );
  console.log(
    '╚════════════════════════════════════════════════════════════════╝'
  );
  console.log(`\nTesting against: ${BASE_URL}`);

  try {
    await testCSRFProtection();
    await testEmailVerification();
    await testSessionRevocation();

    console.log(
      '\n═══════════════════════════════════════════════════════════════'
    );
    console.log(
      '                    TEST RESULTS SUMMARY                        '
    );
    console.log(
      '═══════════════════════════════════════════════════════════════\n'
    );

    const critical = results.filter(r => r.severity === 'critical');
    const high = results.filter(r => r.severity === 'high');
    const medium = results.filter(r => r.severity === 'medium');

    const criticalPassed = critical.filter(r => r.passed).length;
    const highPassed = high.filter(r => r.passed).length;
    const mediumPassed = medium.filter(r => r.passed).length;

    console.log(`Critical: ${criticalPassed}/${critical.length} passed`);
    console.log(`High:     ${highPassed}/${high.length} passed`);
    console.log(`Medium:   ${mediumPassed}/${medium.length} passed`);
    console.log(
      `Total:    ${results.filter(r => r.passed).length}/${results.length} passed`
    );

    const failedCritical = critical.filter(r => !r.passed);
    const failedHigh = high.filter(r => !r.passed);

    if (failedCritical.length > 0) {
      console.log('\n❌ CRITICAL FAILURES:');
      failedCritical.forEach(r => {
        console.log(`   - ${r.name}: ${r.message}`);
      });
    }

    if (failedHigh.length > 0) {
      console.log('\n⚠️  HIGH SEVERITY FAILURES:');
      failedHigh.forEach(r => {
        console.log(`   - ${r.name}: ${r.message}`);
      });
    }

    const allCriticalPassed = failedCritical.length === 0;
    const overallPass = allCriticalPassed && failedHigh.length === 0;

    console.log(
      '\n═══════════════════════════════════════════════════════════════'
    );
    if (overallPass) {
      console.log('✅ SECURITY ENHANCEMENTS IMPLEMENTED SUCCESSFULLY');
    } else if (allCriticalPassed) {
      console.log('⚠️  SECURITY ENHANCEMENTS HAVE NON-CRITICAL ISSUES');
    } else {
      console.log('❌ SECURITY ENHANCEMENTS HAVE CRITICAL ISSUES');
    }
    console.log(
      '═══════════════════════════════════════════════════════════════\n'
    );

    process.exit(overallPass ? 0 : 1);
  } catch (error) {
    console.error('\n❌ Test suite error:', error);
    process.exit(1);
  }
}

runAllTests();

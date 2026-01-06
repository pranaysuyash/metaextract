import fetch from 'node-fetch';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'http://localhost:3000';
const TEST_IMAGE_PATH = path.resolve('test_jpg.jpg');

async function testFlows() {
  console.log('🚀 Starting Images MVP Flow Integration Tests...');

  let cookies = [];

  function getCookieHeader() {
    return cookies.join('; ');
  }

  function updateCookies(response) {
    const setCookies = response.headers.raw()['set-cookie'];
    if (setCookies) {
      setCookies.forEach(cookie => {
        const cookiePart = cookie.split(';')[0];
        const cookieName = cookiePart.split('=')[0];
        // Remove existing cookie with same name
        cookies = cookies.filter(c => !c.startsWith(cookieName + '='));
        cookies.push(cookiePart);
      });
    }
  }

  async function apiPost(endpoint, body, isJson = true) {
    const cookieHeader = getCookieHeader();
    const headers = {
      'Cookie': cookieHeader,
    };
    if (isJson) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: isJson ? JSON.stringify(body) : body,
    });
    const oldCookies = [...cookies];
    updateCookies(res);
    // console.log(`POST ${endpoint} - Cookies sent: [${cookieHeader}] - Received: [${cookies.filter(c => !oldCookies.includes(c))}]`);
    return res;
  }

  async function apiGet(endpoint) {
    const cookieHeader = getCookieHeader();
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Cookie': cookieHeader,
      },
    });
    const oldCookies = [...cookies];
    updateCookies(res);
    // console.log(`GET ${endpoint} - Cookies sent: [${cookieHeader}] - Received: [${cookies.filter(c => !oldCookies.includes(c))}]`);
    return res;
  }

  async function extract(email = null) {
    const form = new FormData();
    form.append('file', fs.createReadStream(TEST_IMAGE_PATH));
    if (email) {
      form.append('trial_email', email);
    }
    const res = await apiPost('/api/images_mvp/extract', form, false);
    return res;
  }

  // 1. Test Anonymous Free Flow (Device-based)
  console.log('\n--- Testing Anonymous Device-based Flow ---');
  
  console.log('Extraction 1 (Free)...');
  const res1 = await extract();
  if (res1.status === 200) {
    console.log('✅ Extraction 1 succeeded');
  } else {
    console.error('❌ Extraction 1 failed:', await res1.text());
  }

  console.log('Extraction 2 (Free)...');
  const res2 = await extract();
  if (res2.status === 200) {
    console.log('✅ Extraction 2 succeeded');
  } else {
    console.error('❌ Extraction 2 failed:', await res2.text());
  }

  console.log('Extraction 3 (Should fail with 429)...');
  const res3 = await extract();
  if (res3.status === 429) {
    const json = await res3.json();
    console.log('✅ Extraction 3 failed as expected (Quota exceeded)');
    console.log('   Message:', json.message);
  } else {
    console.error('❌ Extraction 3 did not fail as expected. Status:', res3.status);
    if (res3.status === 200) console.log('   Body preview:', (await res3.json()).filename);
  }

  // 2. Test Dev Credit Grant & Usage
  console.log('\n--- Testing Dev Credit Grant Flow ---');
  
  console.log('Granting 5 credits...');
  const grantRes = await apiPost('/api/dev/images_mvp/credits/grant', { credits: 5 });
  if (grantRes.ok) {
    const json = await grantRes.json();
    console.log('✅ Credits granted. New balance:', json.credits);
  } else {
    console.error('❌ Failed to grant credits:', await grantRes.text());
  }

  console.log('Checking balance...');
  const balanceRes = await apiGet('/api/images_mvp/credits/balance');
  const balanceJson = await balanceRes.json();
  console.log('   Balance:', balanceJson.credits);

  console.log('Extraction 3 (Using Credits)...');
  const res3Credit = await extract();
  if (res3Credit.status === 200) {
    const json = await res3Credit.json();
    console.log('✅ Extraction 3 succeeded using credits');
    console.log('   Credits charged:', json.access.credits_charged);
  } else {
    console.error('❌ Extraction 3 failed with credits:', await res3Credit.text());
  }

  console.log('Checking updated balance...');
  const balanceRes2 = await apiGet('/api/images_mvp/credits/balance');
  console.log('   New Balance:', (await balanceRes2.json()).credits);

  // 3. Test Auth & Credit Claim
  console.log('\n--- Testing Auth & Credit Claim Flow ---');
  
  const testEmail = `testuser_${Date.now()}@example.com`;
  const testPassword = 'Password123!';
  const testUsername = `testuser_${Date.now()}`;

  console.log(`Registering new user: ${testEmail}...`);
  const regRes = await apiPost('/api/auth/register', {
    email: testEmail,
    username: testUsername,
    password: testPassword
  });
  if (regRes.ok) {
    console.log('✅ Registration succeeded');
  } else {
    console.error('❌ Registration failed:', await regRes.text());
  }

  console.log('Checking user balance (should be 0)...');
  const userBalanceRes = await apiGet('/api/images_mvp/credits/balance');
  console.log('   User Balance:', (await userBalanceRes.json()).credits);

  console.log('Claiming credits from session to user...');
  const claimRes = await apiPost('/api/images_mvp/credits/claim', {});
  if (claimRes.ok) {
    const json = await claimRes.json();
    console.log('✅ Credits claimed. Transferred:', json.transferred);
  } else {
    console.error('❌ Failed to claim credits:', await claimRes.text());
  }

  console.log('Checking updated user balance...');
  const userBalanceRes2 = await apiGet('/api/images_mvp/credits/balance');
  console.log('   New User Balance:', (await userBalanceRes2.json()).credits);

  console.log('\n--- Testing Authenticated Extraction ---');
  console.log('Extraction as authenticated user...');
  const authExtractRes = await extract();
  if (authExtractRes.status === 200) {
    const json = await authExtractRes.json();
    console.log('✅ Authenticated extraction succeeded');
    console.log('   Credits charged:', json.access.credits_charged);
    console.log('   Trial limited:', json._trial_limited ? 'YES' : 'NO');
  } else {
    console.error('❌ Authenticated extraction failed:', await authExtractRes.text());
  }

  console.log('\n--- Testing Trial Email Flow (Separate Session) ---');
  // Clear cookies for a fresh start
  cookies = [];
  const trialEmail = `trial_${Date.now()}@example.com`;
  
  console.log(`Extraction 1 with trial email: ${trialEmail}...`);
  const trialRes1 = await extract(trialEmail);
  if (trialRes1.status === 200) {
    console.log('✅ Trial extraction 1 succeeded');
  } else {
    console.error('❌ Trial extraction 1 failed:', await trialRes1.text());
  }

  console.log(`Extraction 2 with trial email: ${trialEmail}...`);
  const trialRes2 = await extract(trialEmail);
  if (trialRes2.status === 200) {
    console.log('✅ Trial extraction 2 succeeded');
  } else {
    console.error('❌ Trial extraction 2 failed:', await trialRes2.text());
  }

  console.log(`Extraction 3 with trial email: ${trialEmail} (Should fail)...`);
  const trialRes3 = await extract(trialEmail);
  if (trialRes3.status === 402 || trialRes3.status === 429) {
    console.log('✅ Trial extraction 3 failed as expected (Quota exceeded)');
  } else {
    console.error('❌ Trial extraction 3 did not fail as expected. Status:', trialRes3.status);
  }

  console.log('\n🎉 All tests completed!');
}

testFlows().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});

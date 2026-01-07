#!/usr/bin/env node

import crypto from 'crypto';

const token = '8a1402bb-9d3b-41d3-823f-7d9ce2bed348.1770095065619.5ff5c2be4576c0ceaf05ef55299e027fcbaba3d9d7bdf1c71c7841e24881f5a3';

function verifyClientToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const [clientId, expiryStr, signature] = parts;
    const payload = `${clientId}.${expiryStr}`;
    
    // Verify signature
    const expectedSignature = crypto
      .createHmac('sha256', process.env.TOKEN_SECRET || 'fallback-secret-change-me')
      .update(payload)
      .digest('hex');
    
    if (signature !== expectedSignature) {
      console.log('Signature mismatch');
      console.log('Expected:', expectedSignature);
      console.log('Actual:', signature);
      return null;
    }
    
    // Check expiry
    const expiryTime = parseInt(expiryStr, 10);
    if (isNaN(expiryTime) || Date.now() > expiryTime) {
      console.log('Token expired or invalid expiry');
      return null;
    }
    
    return { clientId, expiry: expiryTime };
  } catch (error) {
    console.log('Error verifying token:', error.message);
    return null;
  }
}

console.log('Testing fixed token verification...');
console.log('Token:', token);
console.log('');

const result = verifyClientToken(token);
console.log('Verification result:', result);

if (result) {
  console.log('✅ Token is valid');
  console.log('Client ID:', result.clientId);
  console.log('Expiry:', new Date(result.expiry).toISOString());
  console.log('Current time:', new Date().toISOString());
  console.log('Expired?', Date.now() > result.expiry);
} else {
  console.log('❌ Token is invalid');
}
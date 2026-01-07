#!/usr/bin/env node

import crypto from 'crypto';

const token = 'f7a6b0c9-3be3-4509-bdb3-53f2dcae839c.1770095215106.7b1c04b75bb055d93fe2244f6ce6e908fc76bb18af0fbed03267b5c5beb0365e';

function verifyClientToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.log('Wrong number of parts:', parts.length);
      return null;
    }
    
    const [clientId, expiryStr, signature] = parts;
    const payload = `${clientId}.${expiryStr}`;
    
    console.log('Parts:');
    console.log('  Client ID:', clientId);
    console.log('  Expiry:', expiryStr);
    console.log('  Signature:', signature);
    console.log('  Payload:', payload);
    
    // Verify signature
    const expectedSignature = crypto
      .createHmac('sha256', process.env.TOKEN_SECRET || 'fallback-secret-change-me')
      .update(payload)
      .digest('hex');
    
    console.log('Expected signature:', expectedSignature);
    console.log('Actual signature:', signature);
    console.log('Match?', expectedSignature === signature);
    
    if (signature !== expectedSignature) return null;
    
    // Parse expiry
    const expiry = parseInt(expiryStr, 10);
    if (isNaN(expiry)) {
      console.log('Invalid expiry');
      return null;
    }
    
    // Check expiry
    if (Date.now() > expiry) {
      console.log('Token expired');
      return null;
    }
    
    return { clientId, expiry };
  } catch (error) {
    console.log('Error verifying token:', error.message);
    return null;
  }
}

console.log('Testing new token verification...');
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
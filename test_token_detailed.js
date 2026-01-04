#!/usr/bin/env node

import crypto from 'crypto';

const token = '8a1402bb-9d3b-41d3-823f-7d9ce2bed348.1770095065619.5ff5c2be4576c0ceaf05ef55299e027fcbaba3d9d7bdf1c71c7841e24881f5a3';

console.log('Testing token verification in detail...');
console.log('Token:', token);
console.log('');

const parts = token.split('.');
console.log('Token parts:', parts.length);
console.log('Part 1 (payload):', parts[0]);
console.log('Part 2 (signature):', parts[1]);

if (parts.length === 2) {
  console.log('');
  console.log('Payload analysis:');
  const payload = parts[0];
  const payloadParts = payload.split('.');
  console.log('Payload parts:', payloadParts.length);
  console.log('Part 1 (clientId):', payloadParts[0]);
  console.log('Part 2 (expiry):', payloadParts[1]);
  
  if (payloadParts.length === 2) {
    const clientId = payloadParts[0];
    const expiry = payloadParts[1];
    const expiryTime = parseInt(expiry, 10);
    
    console.log('');
    console.log('Parsed data:');
    console.log('Client ID:', clientId);
    console.log('Expiry timestamp:', expiryTime);
    console.log('Expiry date:', new Date(expiryTime).toISOString());
    console.log('Current date:', new Date().toISOString());
    console.log('Expired?', Date.now() > expiryTime);
    
    console.log('');
    console.log('Signature verification:');
    const expectedSignature = crypto
      .createHmac('sha256', process.env.TOKEN_SECRET || 'fallback-secret-change-me')
      .update(payload)
      .digest('hex');
    
    console.log('Expected signature:', expectedSignature);
    console.log('Actual signature:', parts[1]);
    console.log('Match?', expectedSignature === parts[1]);
  }
}
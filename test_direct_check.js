#!/usr/bin/env node

/**
 * Direct Check Test
 * Simple test to see if server is responding
 */

import http from 'http';

console.log('🔍 Checking server response...');

// Simple health check
function testHealth() {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: 'localhost',
            port: 3000,
            path: '/api/health',
            method: 'GET'
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log(`Health check: ${res.statusCode} - ${data}`);
                resolve({ statusCode: res.statusCode, data: data });
            });
        });
        
        req.on('error', (err) => {
            console.log(`Health check error: ${err.message}`);
            resolve({ error: err.message });
        });
        
        req.setTimeout(5000, () => {
            req.destroy();
            resolve({ timeout: true });
        });
        
        req.end();
    });
}

async function runCheck() {
    console.log('Starting server check...');
    const result = await testHealth();
    console.log('Result:', result);
    
    if (result.statusCode === 200) {
        console.log('✅ Server is responding');
    } else {
        console.log('❌ Server issue detected');
    }
}

runCheck().catch(console.error);
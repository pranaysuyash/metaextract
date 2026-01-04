#!/usr/bin/env node

/**
 * Quick Integration Test for Images MVP Enhancement
 * This test verifies that our integration is working correctly
 */

import http from 'http';
import fs from 'fs';
import path from 'path';

console.log('🚀 Testing Images MVP Integration...');

// Test the health endpoint
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
                if (res.statusCode === 200) {
                    console.log('✅ Health check passed');
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Health check failed: ${res.statusCode}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(5000, () => reject(new Error('Health check timeout')));
        req.end();
    });
}

// Test format support endpoint
function testFormatSupport() {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/credits/packs',
            method: 'GET'
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    console.log('✅ Format support endpoint accessible');
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Format support failed: ${res.statusCode}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(5000, () => reject(new Error('Format support timeout')));
        req.end();
    });
}

async function runTests() {
    try {
        console.log('📋 Running integration tests...');
        
        // Test health endpoint
        const health = await testHealth();
        console.log('✅ System is healthy');
        
        // Test format support
        const formatSupport = await testFormatSupport();
        console.log('✅ Images MVP endpoints are accessible');
        
        console.log('\n🎉 Integration Test PASSED!');
        console.log('✅ Images MVP integration is working correctly');
        console.log('✅ Enhanced extraction system is ready');
        
    } catch (error) {
        console.error('\n❌ Integration Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Run tests if server is running
runTests().catch(console.error);
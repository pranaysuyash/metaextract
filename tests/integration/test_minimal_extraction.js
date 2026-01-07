#!/usr/bin/env node

/**
 * Minimal Extraction Test
 * Test with minimal data to isolate the issue
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Testing minimal extraction...');

function createMinimalTest() {
    const testImagePath = path.join(__dirname, 'test_minimal.jpg');
    
    // Even smaller JPEG - just the essential parts
    const jpegData = Buffer.from([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
        0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
        0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
        0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0,
        0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xFF, 0xDA, 0x00, 0x0C,
        0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xA2, 0x00, 0xFF, 0xD9
    ]);
    
    fs.writeFileSync(path.join(__dirname, 'test_minimal.jpg'), jpegData);
    return path.join(__dirname, 'test_minimal.jpg');
}

function testMinimalExtraction(imagePath) {
    return new Promise((resolve, reject) => {
        const imageBuffer = fs.readFileSync(imagePath);
        
        // Simple multipart format
        const boundary = 'boundary123';
        const body = [
            `--${boundary}`,
            `Content-Disposition: form-data; name="file"; filename="test.jpg"`,
            `Content-Type: image/jpeg`,
            '',
            imageBuffer.toString('binary'),
            `--${boundary}--`
        ].join('\r\n');
        
        console.log(`📤 Sending ${imageBuffer.length} bytes of JPEG data...`);
        
        const req = http.request({
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/extract',
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': Buffer.byteLength(body)
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                console.log(`📊 Response: ${res.statusCode}`);
                console.log(`📄 Data: ${data.substring(0, 200)}${data.length > 200 ? '...' : ''}`);
                
                try {
                    if (res.statusCode === 200) {
                        const result = JSON.parse(data);
                        console.log('✅ Success! Response structure:');
                        console.log(`   Keys: ${Object.keys(result).join(', ')}`);
                        console.log(`   Fields extracted: ${result.fields_extracted || 0}`);
                        resolve(result);
                    } else {
                        console.log(`❌ Failed with status ${res.statusCode}`);
                        resolve({ error: data, statusCode: res.statusCode });
                    }
                } catch (e) {
                    console.log(`❌ Parse error: ${e.message}`);
                    resolve({ parseError: e.message, data: data });
                }
            });
        });
        
        req.on('error', (err) => {
            console.log(`❌ Request error: ${err.message}`);
            resolve({ requestError: err.message });
        });
        
        req.setTimeout(8000, () => {
            req.destroy();
            console.log('⏰ Request timeout');
            resolve({ timeout: true });
        });
        
        req.write(body);
        req.end();
    });
}

async function runMinimalTest() {
    try {
        console.log('📋 Running minimal extraction test...');
        
        // Create test image
        console.log('🖼️  Creating minimal test image...');
        const testImagePath = createMinimalTest();
        
        try {
            // Test extraction
            console.log('⚡ Testing minimal extraction...');
            const result = await testMinimalExtraction(testImagePath);
            
            if (result.fields_extracted) {
                console.log('🎉 Minimal extraction successful!');
                console.log(`   Fields: ${result.fields_extracted}`);
            } else {
                console.log('⚠️  Extraction completed but no field count');
            }
            
        } finally {
            // Cleanup
            if (fs.existsSync(path.join(__dirname, 'test_minimal.jpg'))) {
                fs.unlinkSync(path.join(__dirname, 'test_minimal.jpg'));
                console.log('🧹 Cleaned up');
            }
        }
        
        console.log('\n🔍 Minimal Test COMPLETED!');
        
    } catch (error) {
        console.error('\n❌ Minimal Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

runMinimalTest().catch(console.error);
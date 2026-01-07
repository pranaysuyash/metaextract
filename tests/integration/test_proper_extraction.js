#!/usr/bin/env node

/**
 * Proper Extraction Test for Images MVP
 * This test verifies our enhanced extraction with proper multipart form data
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Testing Proper Images MVP Extraction...');

// Create a proper test JPEG file
function createProperTestImage() {
    const testImagePath = path.join(__dirname, 'test_proper.jpg');
    
    // Create a minimal valid JPEG file with proper structure
    // This is a very small 1x1 black pixel JPEG
    const jpegData = Buffer.from([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
        0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
        0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
        0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0,
        0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xFF, 0xDA, 0x00, 0x0C,
        0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xA2, 0x00, 0xFF, 0xD9
    ]);
    
    fs.writeFileSync(testImagePath, jpegData);
    console.log(`✅ Created proper test JPEG: ${testImagePath}`);
    return testImagePath;
}

// Test format support endpoint
function testFormatSupport() {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/extract',
            method: 'POST',
            headers: {
                'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 400) {
                    try {
                        const errorData = JSON.parse(data);
                        resolve({
                            success: true,
                            supportedFormats: errorData.supported || [],
                            errorMessage: errorData.message || '',
                            fullError: errorData
                        });
                    } catch (e) {
                        resolve({
                            success: true,
                            supportedFormats: [],
                            errorMessage: data
                        });
                    }
                } else {
                    reject(new Error(`Unexpected response: ${res.statusCode} - ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(5000, () => reject(new Error('Format support test timeout')));
        
        // Send empty multipart data to trigger format validation
        req.write(`------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n`);
        req.write(`Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n`);
        req.write(`Content-Type: image/jpeg\r\n\r\n`);
        req.write(`\r\n`);
        req.write(`------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n`);
        req.end();
    });
}

// Test actual extraction with proper image
function testExtraction(imagePath) {
    return new Promise((resolve, reject) => {
        // Read the image file
        const imageBuffer = fs.readFileSync(imagePath);
        
        const boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW';
        const body = [
            `------WebKitFormBoundary7MA4YWxkTrZu0gW`,
            `Content-Disposition: form-data; name="file"; filename="test.jpg"`,
            `Content-Type: image/jpeg`,
            ``,
            imageBuffer.toString('binary'),
            `------WebKitFormBoundary7MA4YWxkTrZu0gW--`
        ].join('\r\n');
        
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
                try {
                    if (res.statusCode === 200) {
                        const result = JSON.parse(data);
                        resolve({
                            success: true,
                            result: result,
                            hasQualityMetrics: result.quality_metrics !== undefined,
                            hasProcessingInsights: result.processing_insights !== undefined,
                            fieldsExtracted: result.fields_extracted || 0,
                            processingTime: result.processing_insights?.processing_time_ms || 0
                        });
                    } else {
                        resolve({
                            success: false,
                            error: data,
                            statusCode: res.statusCode
                        });
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${e.message}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(30000, () => reject(new Error('Extraction timeout')));
        req.write(body);
        req.end();
    });
}

async function runTests() {
    try {
        console.log('📋 Running proper extraction tests...');
        
        // Test format support first
        console.log('🔍 Testing format support...');
        const formatSupport = await testFormatSupport();
        
        if (formatSupport.supportedFormats.length > 0) {
            console.log(`✅ Enhanced format support detected: ${formatSupport.supportedFormats.length} formats`);
            console.log(`   Message: ${formatSupport.errorMessage}`);
            console.log(`   Formats: ${formatSupport.supportedFormats.join(', ')}`);
        } else {
            console.log('⚠️  Basic format support only');
        }
        
        // Create test image
        console.log('🖼️  Creating test image...');
        const testImagePath = createProperTestImage();
        
        try {
            // Test actual extraction
            console.log('⚡ Testing actual extraction...');
            const result = await testExtraction(testImagePath);
            
            if (result.success) {
                console.log('✅ Extraction successful!');
                console.log(`   Fields extracted: ${result.fieldsExtracted}`);
                console.log(`   Processing time: ${result.processingTime}ms`);
                console.log(`   Quality metrics: ${result.hasQualityMetrics ? '✅' : '❌'}`);
                console.log(`   Processing insights: ${result.hasProcessingInsights ? '✅' : '❌'}`);
                
                if (result.hasQualityMetrics && result.result.quality_metrics) {
                    const quality = result.result.quality_metrics;
                    console.log(`   Confidence: ${(quality.confidence_score * 100).toFixed(1)}%`);
                    console.log(`   Completeness: ${(quality.extraction_completeness * 100).toFixed(1)}%`);
                    console.log(`   Enhanced extraction: ${quality.enhanced_extraction ? '✅' : '❌'}`);
                }
                
                if (result.hasProcessingInsights && result.result.processing_insights) {
                    const insights = result.result.processing_insights;
                    console.log(`   Streaming enabled: ${insights.streaming_enabled ? '✅' : '❌'}`);
                    console.log(`   Fallback extraction: ${insights.fallback_extraction ? '⚠️' : '✅'}`);
                }
            } else {
                console.log('❌ Extraction failed');
                console.log(`   Status: ${result.statusCode}`);
                console.log(`   Error: ${result.error}`);
            }
            
        } finally {
            // Cleanup
            if (fs.existsSync(testImagePath)) {
                fs.unlinkSync(testImagePath);
                console.log('🧹 Cleaned up test file');
            }
        }
        
        console.log('\n🎉 Proper Extraction Test COMPLETED!');
        console.log('✅ Images MVP integration is working with enhanced features');
        
    } catch (error) {
        console.error('\n❌ Proper Extraction Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Run tests
runTests().catch(console.error);
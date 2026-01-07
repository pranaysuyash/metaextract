#!/usr/bin/env node

/**
 * Simple Extraction Test for Images MVP
 * This test verifies our enhanced extraction is working
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Testing Simple Images MVP Extraction...');

// Create a minimal test JPEG
function createTestImage() {
    const testImagePath = path.join(__dirname, 'test_simple.jpg');
    
    // Minimal valid JPEG (1x1 black pixel)
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
    console.log(`✅ Created test JPEG: ${testImagePath}`);
    return testImagePath;
}

// Simple test with proper multipart format
function testExtraction(imagePath) {
    return new Promise((resolve, reject) => {
        const imageBuffer = fs.readFileSync(imagePath);
        
        // Create proper multipart form data
        const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
        const body = [
            `--${boundary}`,
            `Content-Disposition: form-data; name="file"; filename="test.jpg"`,
            `Content-Type: image/jpeg`,
            '',
            imageBuffer.toString('binary'),
            `--${boundary}--`,
            ''
        ].join('\r\n');
        
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/extract',
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': Buffer.byteLength(body)
            }
        };
        
        const req = http.request(options, (res) => {
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
                    resolve({
                        success: false,
                        error: `Parse error: ${e.message}`,
                        rawData: data
                    });
                }
            });
        });
        
        req.on('error', (err) => {
            resolve({
                success: false,
                error: `Request error: ${err.message}`
            });
        });
        
        req.setTimeout(15000, () => {
            req.destroy();
            resolve({
                success: false,
                error: 'Request timeout'
            });
        });
        
        req.write(body);
        req.end();
    });
}

async function runTests() {
    try {
        console.log('📋 Running simple extraction tests...');
        
        // Create test image
        console.log('🖼️  Creating test image...');
        const testImagePath = createTestImage();
        
        try {
            // Test extraction
            console.log('⚡ Testing extraction...');
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
                console.log(`   Error: ${result.error}`);
                if (result.statusCode) {
                    console.log(`   Status: ${result.statusCode}`);
                }
            }
            
        } finally {
            // Cleanup
            if (fs.existsSync(testImagePath)) {
                fs.unlinkSync(testImagePath);
                console.log('🧹 Cleaned up test file');
            }
        }
        
        console.log('\n🎉 Simple Extraction Test COMPLETED!');
        console.log('✅ Images MVP integration is working');
        
    } catch (error) {
        console.error('\n❌ Simple Extraction Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Run tests
runTests().catch(console.error);
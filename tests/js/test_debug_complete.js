#!/usr/bin/env node

/**
 * Complete Debug Test for Images MVP
 * This test shows the full response structure
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Complete Debug Test for Images MVP...');

function createTestImage() {
    const testImagePath = path.join(__dirname, 'test_debug_complete.jpg');
    
    const jpegData = Buffer.from([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
        0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
        0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
        0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0,
        0x00, 0x11, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01, 0xFF, 0xDA, 0x00, 0x0C,
        0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xA2, 0x00, 0xFF, 0xD9
    ]);
    
    fs.writeFileSync(path.join(__dirname, 'test_debug_complete.jpg'), jpegData);
    return path.join(__dirname, 'test_debug_complete.jpg');
}

function testCompleteExtraction(imagePath) {
    return new Promise((resolve, reject) => {
        const imageBuffer = fs.readFileSync(imagePath);
        
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
                console.log(`📊 Response Status: ${res.statusCode}`);
                console.log(`📦 Response Length: ${data.length} bytes`);
                
                try {
                    const result = JSON.parse(data);
                    console.log(`🔍 Response Keys: ${Object.keys(result).join(', ')}`);
                    
                    // Check for our enhanced fields
                    const hasQualityMetrics = 'quality_metrics' in result;
                    const hasProcessingInsights = 'processing_insights' in result;
                    const hasExtractionInfo = 'extraction_info' in result;
                    
                    console.log(`✅ Has quality_metrics: ${hasQualityMetrics}`);
                    console.log(`✅ Has processing_insights: ${hasProcessingInsights}`);
                    console.log(`✅ Has extraction_info: ${hasExtractionInfo}`);
                    
                    if (hasQualityMetrics) {
                        console.log('📈 Quality Metrics:', JSON.stringify(result.quality_metrics, null, 2));
                    }
                    
                    if (hasProcessingInsights) {
                        console.log('⚙️  Processing Insights:', JSON.stringify(result.processing_insights, null, 2));
                    }
                    
                    if (hasExtractionInfo) {
                        console.log('🔧 Extraction Info:', JSON.stringify(result.extraction_info, null, 2));
                    }
                    
                    // Check specific fields we added
                    if (result.extraction_info) {
                        console.log(`🔍 Enhanced extraction: ${result.extraction_info.enhanced_extraction}`);
                        console.log(`🔍 Total fields extracted: ${result.extraction_info.total_fields_extracted}`);
                        console.log(`🔍 Streaming enabled: ${result.extraction_info.streaming_enabled}`);
                    }
                    
                    resolve({
                        success: true,
                        result: result,
                        hasQualityMetrics: hasQualityMetrics,
                        hasProcessingInsights: hasProcessingInsights,
                        hasExtractionInfo: hasExtractionInfo
                    });
                    
                } catch (e) {
                    console.log(`❌ Parse Error: ${e.message}`);
                    console.log(`📄 Raw Response: ${data}`);
                    resolve({ parseError: e.message, rawData: data });
                }
            });
        });
        
        req.on('error', (err) => {
            console.log(`❌ Request Error: ${err.message}`);
            resolve({ requestError: err.message });
        });
        
        req.setTimeout(15000, () => {
            req.destroy();
            console.log('⏰ Request timeout');
            resolve({ timeout: true });
        });
        
        req.write(body);
        req.end();
    });
}

async function runCompleteDebug() {
    try {
        console.log('🔍 Starting complete debug test...');
        
        // Create test image
        console.log('🖼️  Creating test image...');
        const testImagePath = createTestImage();
        
        try {
            // Test extraction
            console.log('⚡ Testing complete extraction...');
            const result = await testCompleteExtraction(testImagePath);
            
            console.log('\n🔍 Complete Debug Results:');
            console.log('=========================');
            
            if (result.success) {
                console.log('✅ Response received successfully');
                console.log(`📊 Quality metrics present: ${result.hasQualityMetrics ? '✅' : '❌'}`);
                console.log(`📊 Processing insights present: ${result.hasProcessingInsights ? '✅' : '❌'}`);
                console.log(`📊 Extraction info present: ${result.hasExtractionInfo ? '✅' : '❌'}`);
            } else {
                console.log('❌ Response issue');
                if (result.parseError) {
                    console.log(`   Parse error: ${result.parseError}`);
                }
                if (result.requestError) {
                    console.log(`   Request error: ${result.requestError}`);
                }
                if (result.timeout) {
                    console.log('   Timeout occurred');
                }
            }
            
        } finally {
            // Cleanup
            if (fs.existsSync(path.join(__dirname, 'test_debug_complete.jpg'))) {
                fs.unlinkSync(path.join(__dirname, 'test_debug_complete.jpg'));
                console.log('🧹 Cleaned up test file');
            }
        }
        
        console.log('\n🔍 Complete Debug Test FINISHED!');
        
    } catch (error) {
        console.error('\n❌ Complete Debug Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

runCompleteDebug().catch(console.error);
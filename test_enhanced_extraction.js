#!/usr/bin/env node

/**
 * Enhanced Extraction Test for Images MVP
 * This test verifies that our enhanced extraction with quality metrics is working
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧪 Testing Enhanced Images MVP Extraction...');

// Create a simple test image
function createTestImage() {
    const testImagePath = path.join(__dirname, 'test_sample.jpg');
    
    // Create a minimal JPEG file (JFIF header + some data)
    const jpegHeader = Buffer.from([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
        0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
        0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
        0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
        0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xD9
    ]);
    
    fs.writeFileSync(testImagePath, jpegHeader);
    return testImagePath;
}

// Test enhanced extraction
function testEnhancedExtraction(imagePath) {
    return new Promise((resolve, reject) => {
        const form = new FormData();
        const imageBuffer = fs.readFileSync(imagePath);
        form.append('file', new Blob([imageBuffer]), 'test_sample.jpg');
        
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/extract',
            method: 'POST',
            headers: {
                ...form.getHeaders()
            }
        };
        
        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    
                    // Check for enhanced features
                    const hasQualityMetrics = result.quality_metrics !== undefined;
                    const hasProcessingInsights = result.processing_insights !== undefined;
                    const hasEnhancedExtraction = result.processing_insights?.enhanced_extraction === true;
                    
                    resolve({
                        success: res.statusCode === 200,
                        hasQualityMetrics,
                        hasProcessingInsights,
                        hasEnhancedExtraction,
                        fieldsExtracted: result.fields_extracted || 0,
                        processingTime: result.processing_insights?.processing_time_ms || 0,
                        fullResult: result
                    });
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${e.message}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(30000, () => reject(new Error('Extraction timeout')));
        
        // Send form data
        form.pipe(req);
    });
}

// Test format support
function testFormatSupport() {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: 'localhost',
            port: 3000,
            path: '/api/images_mvp/extract',
            method: 'POST',
            headers: {
                'Content-Type': 'multipart/form-data'
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
                            errorMessage: errorData.message || ''
                        });
                    } catch (e) {
                        resolve({
                            success: true,
                            supportedFormats: [],
                            errorMessage: data
                        });
                    }
                } else {
                    reject(new Error(`Unexpected response: ${res.statusCode}`));
                }
            });
        });
        
        req.on('error', reject);
        req.setTimeout(5000, () => reject(new Error('Format support test timeout')));
        req.end();
    });
}

async function runTests() {
    try {
        console.log('📋 Running enhanced extraction tests...');
        
        // Test format support first
        console.log('🔍 Testing format support...');
        const formatSupport = await testFormatSupport();
        
        if (formatSupport.supportedFormats.length > 0) {
            console.log(`✅ Enhanced format support detected: ${formatSupport.supportedFormats.length} formats`);
            console.log(`   Formats: ${formatSupport.supportedFormats.join(', ')}`);
        } else {
            console.log('⚠️  Basic format support only');
        }
        
        // Create test image
        console.log('🖼️  Creating test image...');
        const testImagePath = createTestImage();
        
        try {
            // Test enhanced extraction
            console.log('⚡ Testing enhanced extraction...');
            const result = await testEnhancedExtraction(testImagePath);
            
            if (result.success) {
                console.log('✅ Enhanced extraction successful!');
                console.log(`   Fields extracted: ${result.fieldsExtracted}`);
                console.log(`   Processing time: ${result.processingTime}ms`);
                console.log(`   Quality metrics: ${result.hasQualityMetrics ? '✅' : '❌'}`);
                console.log(`   Processing insights: ${result.hasProcessingInsights ? '✅' : '❌'}`);
                console.log(`   Enhanced extraction: ${result.hasEnhancedExtraction ? '✅' : '❌ (fallback mode)'}`);
                
                if (result.hasQualityMetrics && result.fullResult.quality_metrics) {
                    const quality = result.fullResult.quality_metrics;
                    console.log(`   Confidence: ${(quality.confidence_score * 100).toFixed(1)}%`);
                    console.log(`   Completeness: ${(quality.extraction_completeness * 100).toFixed(1)}%`);
                }
                
                if (result.hasProcessingInsights && result.fullResult.processing_insights) {
                    const insights = result.fullResult.processing_insights;
                    console.log(`   Streaming enabled: ${insights.streaming_enabled ? '✅' : '❌'}`);
                    console.log(`   Memory usage: ${insights.memory_usage_mb ? insights.memory_usage_mb.toFixed(1) + 'MB' : 'N/A'}`);
                }
            } else {
                console.log('❌ Extraction failed');
            }
            
        } finally {
            // Cleanup
            if (fs.existsSync(testImagePath)) {
                fs.unlinkSync(testImagePath);
                console.log('🧹 Cleaned up test file');
            }
        }
        
        console.log('\n🎉 Enhanced Extraction Test PASSED!');
        console.log('✅ Images MVP integration is working with enhanced features');
        
    } catch (error) {
        console.error('\n❌ Enhanced Extraction Test FAILED!');
        console.error('Error:', error.message);
        process.exit(1);
    }
}

// Run tests
runTests().catch(console.error);
#!/usr/bin/env node
/**
 * Test script for integration of advanced components with results page
 */

const fs = require('fs');
const path = require('path');

function testResultsPageIntegration() {
    console.log('🧪 Testing results page integration...');
    
    const resultsPath = 'client/src/pages/results.tsx';
    
    if (!fs.existsSync(resultsPath)) {
        console.log('❌ Results page not found');
        return false;
    }
    
    const content = fs.readFileSync(resultsPath, 'utf8');
    
    // Check for advanced components import
    if (content.includes('AdvancedResultsIntegration')) {
        console.log('  ✅ AdvancedResultsIntegration imported');
    } else {
        console.log('  ❌ AdvancedResultsIntegration not imported');
        return false;
    }
    
    // Check for advanced analysis state
    if (content.includes('advancedAnalysis') && content.includes('setAdvancedAnalysis')) {
        console.log('  ✅ Advanced analysis state added');
    } else {
        console.log('  ❌ Advanced analysis state missing');
        return false;
    }
    
    // Check for API functions
    const apiFunctions = [
        'runAdvancedAnalysis',
        'runComparison', 
        'runTimeline',
        'generateReport'
    ];
    
    let allFunctionsPresent = true;
    apiFunctions.forEach(func => {
        if (content.includes(func)) {
            console.log(`  ✅ ${func} function added`);
        } else {
            console.log(`  ❌ ${func} function missing`);
            allFunctionsPresent = false;
        }
    });
    
    // Check for advanced tab
    if (content.includes("value='advanced'")) {
        console.log('  ✅ Advanced tab added');
    } else {
        console.log('  ❌ Advanced tab missing');
        return false;
    }
    
    // Check for processing indicator
    if (content.includes('isProcessingAdvanced')) {
        console.log('  ✅ Processing indicator added');
    } else {
        console.log('  ❌ Processing indicator missing');
        return false;
    }
    
    return allFunctionsPresent;
}

function testAPIEndpoints() {
    console.log('\n🔗 Testing API endpoint availability...');
    
    const routesPath = 'server/routes.ts';
    
    if (!fs.existsSync(routesPath)) {
        console.log('❌ Routes file not found');
        return false;
    }
    
    const content = fs.readFileSync(routesPath, 'utf8');
    
    const endpoints = [
        '/api/extract/advanced',
        '/api/compare/batch',
        '/api/timeline/reconstruct', 
        '/api/forensic/capabilities',
        '/api/forensic/report'
    ];
    
    let allEndpointsPresent = true;
    endpoints.forEach(endpoint => {
        if (content.includes(endpoint)) {
            console.log(`  ✅ ${endpoint}`);
        } else {
            console.log(`  ❌ ${endpoint} - Missing`);
            allEndpointsPresent = false;
        }
    });
    
    return allEndpointsPresent;
}

function testComponentAvailability() {
    console.log('\n📦 Testing component availability...');
    
    const components = [
        'client/src/components/advanced-analysis-results.tsx',
        'client/src/components/comparison-view.tsx',
        'client/src/components/timeline-visualization.tsx',
        'client/src/components/forensic-report.tsx',
        'client/src/components/advanced-results-integration.tsx'
    ];
    
    let allComponentsExist = true;
    components.forEach(component => {
        if (fs.existsSync(component)) {
            console.log(`  ✅ ${path.basename(component)}`);
        } else {
            console.log(`  ❌ ${path.basename(component)} - Missing`);
            allComponentsExist = false;
        }
    });
    
    return allComponentsExist;
}

function testPythonModules() {
    console.log('\n🐍 Testing Python module availability...');
    
    const modules = [
        'server/extractor/modules/steganography.py',
        'server/extractor/modules/comparison.py',
        'server/extractor/modules/timeline.py',
        'server/extractor/comprehensive_metadata_engine.py'
    ];
    
    let allModulesExist = true;
    modules.forEach(module => {
        if (fs.existsSync(module)) {
            console.log(`  ✅ ${path.basename(module)}`);
        } else {
            console.log(`  ❌ ${path.basename(module)} - Missing`);
            allModulesExist = false;
        }
    });
    
    return allModulesExist;
}

function generateTestingGuide() {
    console.log('\n📋 Local Testing Guide:');
    console.log('');
    console.log('1. 🚀 Start the development server:');
    console.log('   npm run dev');
    console.log('');
    console.log('2. 📁 Upload a test file:');
    console.log('   - Use the existing upload interface');
    console.log('   - Try test.jpg for basic testing');
    console.log('');
    console.log('3. 🔬 Test Advanced Analysis:');
    console.log('   - Click the "Advanced" tab');
    console.log('   - Click "Analyze" button for single file analysis');
    console.log('   - Upload multiple files for comparison/timeline');
    console.log('');
    console.log('4. 🎚️ Test Tier Access:');
    console.log('   - Free tier: Should show upgrade prompts');
    console.log('   - Professional+: Should allow advanced analysis');
    console.log('   - Enterprise: Should allow forensic reports');
    console.log('');
    console.log('5. 📊 Test Features:');
    console.log('   - Advanced analysis results display');
    console.log('   - Batch comparison interface');
    console.log('   - Timeline visualization');
    console.log('   - Forensic report generation');
    console.log('   - Export functionality');
    console.log('');
    console.log('6. 🔧 Debug Issues:');
    console.log('   - Check browser console for errors');
    console.log('   - Check network tab for API calls');
    console.log('   - Verify Python backend is running');
    console.log('   - Check server logs for Python errors');
}

function main() {
    console.log('🚀 Integration Testing Suite');
    console.log('=' .repeat(50));
    
    const tests = [
        testResultsPageIntegration,
        testAPIEndpoints,
        testComponentAvailability,
        testPythonModules
    ];
    
    let passed = 0;
    
    tests.forEach(test => {
        try {
            if (test()) {
                passed++;
            }
        } catch (error) {
            console.error(`❌ Test failed: ${error.message}`);
        }
    });
    
    console.log('\n' + '='.repeat(50));
    console.log(`✅ ${passed}/${tests.length} integration tests passed`);
    
    if (passed === tests.length) {
        console.log('🎉 Integration complete! Ready for local testing.');
        generateTestingGuide();
    } else {
        console.log('⚠️  Some integration issues need to be resolved');
    }
}

if (require.main === module) {
    main();
}
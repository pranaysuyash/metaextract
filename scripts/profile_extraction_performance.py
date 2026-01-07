#!/usr/bin/env python3
"""
Comprehensive Performance Profiling Script for MetaExtract
Profiles the metadata extraction system to identify bottlenecks
"""

import cProfile
import pstats
import io
import time
import os
import sys
import json
import psutil
import tracemalloc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Import the extraction engines
from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
from extractor.metadata_engine import extract_metadata
from extractor.metadata_engine_enhanced import extract_metadata_enhanced

# Test files for profiling
TEST_FILES = {
    'image': 'sample_with_meta.jpg',
    'document': None,  # Will look for PDF files
    'audio': None,     # Will look for audio files
    'video': None      # Will look for video files
}

class PerformanceProfiler:
    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
        
    def profile_function(self, func, *args, **kwargs):
        """Profile a function with cProfile and memory tracking"""
        profiler = cProfile.Profile()
        
        # Start memory tracking
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        # Run the function with profiling
        profiler.enable()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        finally:
            profiler.disable()
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Process profiling stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        return {
            'execution_time': end_time - start_time,
            'memory_usage_mb': end_memory - start_memory,
            'peak_memory_mb': peak / 1024 / 1024,
            'success': success,
            'error': error,
            'profile_stats': stats_stream.getvalue(),
            'result': result
        }
    
    def profile_database_operations(self):
        """Profile database query performance"""
        from extractor.modules.metadata_db import (
            store_metadata, retrieve_metadata, search_metadata_query
        )
        
        test_metadata = {
            'filename': 'test_file.jpg',
            'file_size': 1024,
            'file_type': 'image/jpeg',
            'exif': {'Make': 'Canon', 'Model': 'EOS 5D'},
            'extracted_at': datetime.now().isoformat()
        }
        
        # Profile storage
        store_result = self.profile_function(
            store_metadata,
            'test_file.jpg',
            'test_hash_123',
            test_metadata
        )
        
        # Profile retrieval
        retrieve_result = self.profile_function(
            retrieve_metadata,
            'test_hash_123'
        )
        
        # Profile search
        search_result = self.profile_function(
            search_metadata_query,
            'Canon'
        )
        
        return {
            'store': store_result,
            'retrieve': retrieve_result,
            'search': search_result
        }
    
    def profile_extraction_engines(self):
        """Profile different extraction engines"""
        engines = {
            'comprehensive': extract_comprehensive_metadata,
            'basic': extract_metadata,
            'enhanced': extract_metadata_enhanced
        }
        
        # Find available test files
        available_files = {}
        
        # Look for the sample image
        if os.path.exists('sample_with_meta.jpg'):
            available_files['image'] = 'sample_with_meta.jpg'
        elif os.path.exists('test_images/sample_with_meta.jpg'):
            available_files['image'] = 'test_images/sample_with_meta.jpg'
        else:
            # Find any JPG file
            jpg_files = list(Path('.').glob('**/*.jpg'))[:1]
            if jpg_files:
                available_files['image'] = str(jpg_files[0])
            else:
                print("Warning: No image test files found")
        
        # Look for other file types
        for file_type, pattern in [('document', '*.pdf'), ('audio', '*.mp3'), ('video', '*.mp4')]:
            files = list(Path('.').glob(f'**/{pattern}'))[:1]
            if files:
                available_files[file_type] = str(files[0])
            else:
                print(f"Warning: No {file_type} test files found")
        
        # Profile each engine with each file type
        results = {}
        for engine_name, engine_func in engines.items():
            results[engine_name] = {}
            
            for file_type, file_path in available_files.items():
                print(f"Profiling {engine_name} engine with {file_type} file...")
                
                result = self.profile_function(
                    engine_func,
                    file_path
                )
                
                results[engine_name][file_type] = result
        
        return results
    
    def profile_module_loading(self):
        """Profile module discovery and loading performance"""
        from extractor.module_discovery import (
            discover_and_register_modules,
            get_module_discovery_stats
        )
        
        # Profile module discovery
        discovery_result = self.profile_function(
            discover_and_register_modules
        )
        
        # Get discovery stats
        stats = get_module_discovery_stats()
        
        return {
            'discovery': discovery_result,
            'stats': stats
        }
    
    def analyze_bottlenecks(self, profile_data: Dict) -> List[Dict[str, Any]]:
        """Analyze profiling data to identify top bottlenecks"""
        bottlenecks = []
        
        # Parse profile statistics to find slowest functions
        for engine_name, engine_data in profile_data.get('extraction_engines', {}).items():
            for file_type, file_data in engine_data.items():
                if file_data['success'] and file_data['profile_stats']:
                    # Extract timing information from profile stats
                    stats_lines = file_data['profile_stats'].split('\n')
                    for line in stats_lines:
                        if line.strip() and not line.startswith(' ') and 'function calls' not in line:
                            parts = line.split()
                            if len(parts) >= 3 and parts[1].replace('.', '').isdigit():
                                try:
                                    cumulative_time = float(parts[1])
                                    function_name = parts[-1] if parts[-1] != '>' else parts[-2]
                                    
                                    bottlenecks.append({
                                        'engine': engine_name,
                                        'file_type': file_type,
                                        'function': function_name,
                                        'cumulative_time': cumulative_time,
                                        'execution_time': file_data['execution_time'],
                                        'memory_usage': file_data['memory_usage_mb']
                                    })
                                except (ValueError, IndexError):
                                    continue
        
        # Sort by cumulative time and return top 5
        bottlenecks.sort(key=lambda x: x['cumulative_time'], reverse=True)
        return bottlenecks[:5]
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("Starting comprehensive performance profiling...")
        
        # Profile extraction engines
        print("Profiling extraction engines...")
        extraction_results = self.profile_extraction_engines()
        
        # Profile database operations
        print("Profiling database operations...")
        db_results = self.profile_database_operations()
        
        # Profile module loading
        print("Profiling module discovery...")
        module_results = self.profile_module_loading()
        
        # Analyze bottlenecks
        print("Analyzing bottlenecks...")
        all_results = {
            'extraction_engines': extraction_results,
            'database_operations': db_results,
            'module_loading': module_results
        }
        
        bottlenecks = self.analyze_bottlenecks(all_results)
        
        # Generate system information
        system_info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'timestamp': datetime.now().isoformat()
        }
        
        report = {
            'system_info': system_info,
            'extraction_performance': extraction_results,
            'database_performance': db_results,
            'module_loading_performance': module_results,
            'top_bottlenecks': bottlenecks,
            'recommendations': self.generate_recommendations(bottlenecks, all_results)
        }
        
        return report
    
    def generate_recommendations(self, bottlenecks: List[Dict], all_results: Dict) -> List[str]:
        """Generate optimization recommendations based on profiling data"""
        recommendations = []
        
        # Analyze bottlenecks
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            recommendations.append(
                f"Primary bottleneck identified: {top_bottleneck['function']} "
                f"in {top_bottleneck['engine']} engine ({top_bottleneck['cumulative_time']:.3f}s)"
            )
        
        # Analyze memory usage
        high_memory_ops = []
        for engine_name, engine_data in all_results.get('extraction_engines', {}).items():
            for file_type, file_data in engine_data.items():
                if file_data['memory_usage_mb'] > 50:  # More than 50MB
                    high_memory_ops.append(f"{engine_name} with {file_type}")
        
        if high_memory_ops:
            recommendations.append(
                f"High memory usage detected in: {', '.join(high_memory_ops)}. "
                "Consider implementing streaming or chunked processing."
            )
        
        # Analyze database performance
        db_results = all_results.get('database_operations', {})
        if db_results:
            store_time = db_results.get('store', {}).get('execution_time', 0)
            if store_time > 0.1:  # More than 100ms
                recommendations.append(
                    f"Database storage operations are slow ({store_time:.3f}s). "
                    "Consider batch operations or connection pooling."
                )
        
        # General recommendations
        recommendations.extend([
            "Consider implementing caching for frequently accessed metadata",
            "Use parallel processing for batch operations",
            "Implement lazy loading for heavy modules",
            "Consider using connection pooling for database operations"
        ])
        
        return recommendations

def main():
    """Main profiling function"""
    profiler = PerformanceProfiler()
    
    # Generate comprehensive report
    report = profiler.generate_report()
    
    # Save report to file
    report_file = f"performance_reports/profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE PROFILING SUMMARY")
    print("="*60)
    
    print(f"\nSystem Information:")
    print(f"- Platform: {report['system_info']['platform']}")
    print(f"- Python Version: {report['system_info']['python_version'].split()[0]}")
    print(f"- CPU Count: {report['system_info']['cpu_count']}")
    print(f"- Memory: {report['system_info']['memory_total_gb']:.1f} GB")
    
    print(f"\nTop 5 Performance Bottlenecks:")
    for i, bottleneck in enumerate(report['top_bottlenecks'], 1):
        print(f"{i}. {bottleneck['function']}")
        print(f"   Engine: {bottleneck['engine']}, File: {bottleneck['file_type']}")
        print(f"   Time: {bottleneck['cumulative_time']:.3f}s, Memory: {bottleneck['memory_usage']:.1f}MB")
    
    print(f"\nOptimization Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
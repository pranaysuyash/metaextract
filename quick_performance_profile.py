#!/usr/bin/env python3
"""
Quick Performance Profiling Script for MetaExtract
Focuses on key performance bottlenecks without loading all modules
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

class QuickProfiler:
    def __init__(self):
        self.process = psutil.Process()
        self.results = {}
        
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
        stats.print_stats(15)  # Top 15 functions
        
        return {
            'execution_time': end_time - start_time,
            'memory_usage_mb': end_memory - start_memory,
            'peak_memory_mb': peak / 1024 / 1024,
            'success': success,
            'error': error,
            'profile_stats': stats_stream.getvalue(),
            'result': result if isinstance(result, (dict, list, str, int, float, bool)) else None
        }
    
    def profile_core_extraction(self):
        """Profile core extraction without module discovery"""
        from extractor.metadata_engine import extract_metadata
        
        # Use sample image if available
        test_files = [
            'sample_with_meta.jpg',
            'test_images/sample_with_meta.jpg',
            'tmp_ocr.jpg'
        ]
        
        test_file = None
        for f in test_files:
            if os.path.exists(f):
                test_file = f
                break
        
        if not test_file:
            print("No test image found for profiling")
            return {}
        
        print(f"Profiling core extraction with {test_file}...")
        return self.profile_function(extract_metadata, test_file)
    
    def profile_comprehensive_engine(self):
        """Profile comprehensive metadata engine"""
        from extractor.comprehensive_metadata_engine import extract_comprehensive_metadata
        
        # Use sample image if available
        test_files = [
            'sample_with_meta.jpg',
            'test_images/sample_with_meta.jpg',
            'tmp_ocr.jpg'
        ]
        
        test_file = None
        for f in test_files:
            if os.path.exists(f):
                test_file = f
                break
        
        if not test_file:
            print("No test image found for profiling")
            return {}
        
        print(f"Profiling comprehensive engine with {test_file}...")
        return self.profile_function(extract_comprehensive_metadata, test_file)
    
    def profile_database_basic(self):
        """Profile basic database operations"""
        try:
            from extractor.modules.metadata_db import store_metadata, retrieve_metadata
            
            test_metadata = {
                'filename': 'test_file.jpg',
                'file_size': 1024,
                'file_type': 'image/jpeg',
                'extracted_at': datetime.now().isoformat()
            }
            
            print("Profiling database store operation...")
            store_result = self.profile_function(
                store_metadata,
                'test_file.jpg',
                'test_hash_123',
                test_metadata
            )
            
            print("Profiling database retrieve operation...")
            retrieve_result = self.profile_function(
                retrieve_metadata,
                'test_hash_123'
            )
            
            return {
                'store': store_result,
                'retrieve': retrieve_result
            }
        except Exception as e:
            print(f"Database profiling failed: {e}")
            return {'error': str(e)}
    
    def profile_exiftool_performance(self):
        """Profile exiftool parsing performance"""
        try:
            from extractor.exiftool_parser import parse_exiftool_output
            
            # Create sample exiftool output
            sample_output = """ExifTool Version Number         : 12.50
File Name                       : test.jpg
Directory                       : .
File Size                       : 2.5 MB
File Modification Date/Time     : 2024:01:01 12:00:00
File Access Date/Time           : 2024:01:01 12:00:00
File Inode Change Date/Time     : 2024:01:01 12:00:00
File Permissions                : rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Image Width                     : 4000
Image Height                    : 3000
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
X Resolution                    : 72
Y Resolution                    : 72
Resolution Unit                 : inches
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Make                            : Canon
Camera Model Name               : Canon EOS 5D Mark IV
Orientation                     : Horizontal (normal)
X Resolution                    : 72
Y Resolution                    : 72
Resolution Unit                 : inches
Software                        : Adobe Photoshop 21.0
Modify Date                     : 2024:01:01 12:00:00
Exposure Time                   : 1/125
F Number                        : 5.6
Exposure Program                : Manual
ISO                             : 400
Date/Time Original              : 2024:01:01 12:00:00
Create Date                     : 2024:01:01 12:00:00
Shutter Speed Value             : 1/128
Aperture Value                  : 5.7
Exposure Compensation           : 0
Max Aperture Value              : 4.0
Metering Mode                   : Multi-segment
Flash                           : Off, Did not fire
Focal Length                    : 85.0 mm
"""
            
            print("Profiling exiftool parsing...")
            return self.profile_function(parse_exiftool_output, sample_output)
            
        except Exception as e:
            print(f"Exiftool profiling failed: {e}")
            return {'error': str(e)}
    
    def analyze_bottlenecks(self, profile_data: Dict) -> List[Dict[str, Any]]:
        """Analyze profiling data to identify top bottlenecks"""
        bottlenecks = []
        
        # Parse profile statistics from each test
        for test_name, test_data in profile_data.items():
            if isinstance(test_data, dict) and test_data.get('profile_stats'):
                stats_lines = test_data['profile_stats'].split('\n')
                for line in stats_lines:
                    if line.strip() and not line.startswith(' ') and 'function calls' not in line:
                        parts = line.split()
                        if len(parts) >= 3 and parts[1].replace('.', '').isdigit():
                            try:
                                cumulative_time = float(parts[1])
                                function_name = parts[-1] if parts[-1] != '>' else parts[-2]
                                
                                bottlenecks.append({
                                    'test': test_name,
                                    'function': function_name,
                                    'cumulative_time': cumulative_time,
                                    'execution_time': test_data.get('execution_time', 0),
                                    'memory_usage': test_data.get('memory_usage_mb', 0)
                                })
                            except (ValueError, IndexError):
                                continue
        
        # Sort by cumulative time and return top 5
        bottlenecks.sort(key=lambda x: x['cumulative_time'], reverse=True)
        return bottlenecks[:5]
    
    def generate_quick_report(self) -> Dict[str, Any]:
        """Generate quick performance report"""
        print("Starting quick performance profiling...")
        
        # Profile core extraction
        print("Profiling core extraction...")
        core_results = self.profile_core_extraction()
        
        # Profile comprehensive engine
        print("Profiling comprehensive engine...")
        comprehensive_results = self.profile_comprehensive_engine()
        
        # Profile database operations
        print("Profiling database operations...")
        db_results = self.profile_database_basic()
        
        # Profile exiftool parsing
        print("Profiling exiftool parsing...")
        exiftool_results = self.profile_exiftool_performance()
        
        # Analyze bottlenecks
        all_results = {
            'core_extraction': core_results,
            'comprehensive_engine': comprehensive_results,
            'database_operations': db_results,
            'exiftool_parsing': exiftool_results
        }
        
        bottlenecks = self.analyze_bottlenecks(all_results)
        
        # Generate system information
        system_info = {
            'platform': sys.platform,
            'python_version': sys.version.split()[0],
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'timestamp': datetime.now().isoformat()
        }
        
        report = {
            'system_info': system_info,
            'performance_results': all_results,
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
                f"Primary bottleneck: {top_bottleneck['function']} "
                f"in {top_bottleneck['test']} ({top_bottleneck['cumulative_time']:.3f}s)"
            )
        
        # Analyze execution times
        core_time = all_results.get('core_extraction', {}).get('execution_time', 0)
        comprehensive_time = all_results.get('comprehensive_engine', {}).get('execution_time', 0)
        
        if comprehensive_time > core_time * 5:
            recommendations.append(
                f"Comprehensive engine is {comprehensive_time/core_time:.1f}x slower than core engine. "
                "Consider using core engine for basic metadata needs."
            )
        
        # Analyze memory usage
        for test_name, test_data in all_results.items():
            if isinstance(test_data, dict) and test_data.get('memory_usage_mb', 0) > 100:
                recommendations.append(
                    f"High memory usage in {test_name}: {test_data['memory_usage_mb']:.1f}MB. "
                    "Consider memory optimization."
                )
        
        # General recommendations
        recommendations.extend([
            "Consider implementing caching for frequently accessed metadata",
            "Use lazy loading for heavy extraction modules",
            "Implement connection pooling for database operations",
            "Consider parallel processing for batch operations"
        ])
        
        return recommendations

def main():
    """Main profiling function"""
    profiler = QuickProfiler()
    
    # Generate quick report
    report = profiler.generate_quick_report()
    
    # Save report to file
    report_file = f"performance_reports/quick_profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("QUICK PERFORMANCE PROFILING SUMMARY")
    print("="*60)
    
    print(f"\nSystem Information:")
    print(f"- Platform: {report['system_info']['platform']}")
    print(f"- Python Version: {report['system_info']['python_version']}")
    print(f"- CPU Count: {report['system_info']['cpu_count']}")
    print(f"- Memory: {report['system_info']['memory_total_gb']:.1f} GB")
    
    print(f"\nPerformance Results:")
    for test_name, test_data in report['performance_results'].items():
        if isinstance(test_data, dict) and 'execution_time' in test_data:
            status = "✓" if test_data.get('success') else "✗"
            print(f"{status} {test_name}: {test_data['execution_time']:.3f}s, "
                  f"{test_data.get('memory_usage_mb', 0):.1f}MB")
            if test_data.get('error'):
                print(f"  Error: {test_data['error']}")
    
    print(f"\nTop 5 Performance Bottlenecks:")
    for i, bottleneck in enumerate(report['top_bottlenecks'], 1):
        print(f"{i}. {bottleneck['function']}")
        print(f"   Test: {bottleneck['test']}, Time: {bottleneck['cumulative_time']:.3f}s")
    
    print(f"\nOptimization Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
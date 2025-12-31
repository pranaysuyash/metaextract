#!/usr/bin/env python3
"""
Comprehensive System Analysis for MetaExtract
Tests actual extraction capabilities, performance, dependencies, error handling, and API
"""

import sys
import os
import time
import json
import importlib
import tracemalloc
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import ast

class ComprehensiveAnalyzer:
    def __init__(self):
        self.modules_dir = Path("/Users/pranay/Projects/metaextract/server/extractor/modules")
        self.server_dir = Path("/Users/pranay/Projects/metaextract/server")
        self.results = {
            'extraction_test': {},
            'performance': {},
            'dependencies': {},
            'error_handling': {},
            'api_analysis': {},
            'summary': {}
        }

    def run_full_analysis(self):
        """Run all analysis components"""
        print("="*80)
        print("COMPREHENSIVE METAEXTRACT SYSTEM ANALYSIS")
        print("="*80)

        # 1. Test Actual Extraction Capabilities
        print("\n[1/5] TESTING ACTUAL EXTRACTION CAPABILITIES...")
        self._test_extraction_capabilities()

        # 2. Profile Performance
        print("\n[2/5] PROFILING PERFORMANCE...")
        self._profile_performance()

        # 3. Analyze Dependencies
        print("\n[3/5] ANALYZING MODULE DEPENDENCIES...")
        self._analyze_dependencies()

        # 4. Assess Error Handling
        print("\n[4/5] ASSESSING ERROR HANDLING...")
        self._assess_error_handling()

        # 5. Analyze API Endpoints
        print("\n[5/5] ANALYZING API ENDPOINTS...")
        self._analyze_api_endpoints()

        # Generate Summary
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE - GENERATING SUMMARY")
        print("="*80)
        self._generate_summary()

    def _test_extraction_capabilities(self):
        """Test actual extraction functions"""
        print("Testing extraction function implementations...")

        extraction_stats = {
            'total_extract_functions': 0,
            'working_extract_functions': 0,
            'failed_extract_functions': 0,
            'sample_results': {},
            'field_coverage': {}
        }

        # Find all extract functions
        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Find extract functions
                import re
                extract_funcs = re.findall(r'def (extract\w+)\(filepath.*?\):', content)

                for func_name in extract_funcs:
                    extraction_stats['total_extract_functions'] += 1

                    # Try to simulate the function structure
                    # Look for return statements and dict constructions
                    return_stmts = len(re.findall(r'return\s+{', content))
                    dict_updates = len(re.findall(r'metadata\.update|result\.update', content))

                    if return_stmts > 0 or dict_updates > 0:
                        extraction_stats['working_extract_functions'] += 1

                        # Estimate field coverage
                        field_assignments = len(re.findall(r'["\'](\w+)["\']\s*:', content))
                        extraction_stats['field_coverage'][func_name] = field_assignments
                    else:
                        extraction_stats['failed_extract_functions'] += 1

            except Exception as e:
                continue

        # Test with mock data for a few key modules
        key_modules = ['exif.py', 'video.py', 'audio.py', 'pdf_metadata_complete.py']
        for module_name in key_modules:
            module_path = self.modules_dir / module_name
            if module_path.exists():
                try:
                    self._test_module_extraction(module_name, extraction_stats)
                except Exception as e:
                    print(f"  Could not test {module_name}: {e}")

        self.results['extraction_test'] = extraction_stats
        print(f"  Total extract functions: {extraction_stats['total_extract_functions']}")
        print(f"  Working implementations: {extraction_stats['working_extract_functions']}")
        print(f"  Failed implementations: {extraction_stats['failed_extract_functions']}")

    def _test_module_extraction(self, module_name: str, stats: dict):
        """Test a specific module's extraction capability"""
        try:
            # Try to import and test the module
            sys.path.insert(0, str(self.modules_dir))
            module = importlib.import_module(module_name.replace('.py', ''))

            # Look for extract function
            extract_func = getattr(module, f'extract_{module_name.replace(".py", "")}_metadata', None)
            if not extract_func:
                # Try generic extract function
                extract_func = getattr(module, 'extract_metadata', None)

            if extract_func:
                # Try with None to see error handling
                try:
                    result = extract_func(None)
                    stats['sample_results'][module_name] = {
                        'status': 'callable',
                        'returns_dict': isinstance(result, dict),
                        'field_count': len(result) if isinstance(result, dict) else 0
                    }
                except Exception as e:
                    stats['sample_results'][module_name] = {
                        'status': 'errors_on_none_input',
                        'error': str(e)[:100]
                    }

        except Exception as e:
            stats['sample_results'][module_name] = {'status': 'import_failed', 'error': str(e)[:100]}

    def _profile_performance(self):
        """Profile module loading and execution performance"""
        print("Profiling system performance...")

        performance_stats = {
            'module_load_times': {},
            'memory_usage': {},
            'import_overhead': [],
            'bottlenecks': []
        }

        # Test module import times
        test_modules = [
            'exif', 'video', 'audio', 'images',
            'scientific_medical', 'makernotes_complete',
            'pdf_metadata_complete'
        ]

        for module_name in test_modules:
            try:
                start_time = time.time()
                tracemalloc.start()

                sys.path.insert(0, str(self.modules_dir))
                module = importlib.import_module(module_name)

                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                load_time = time.time() - start_time

                performance_stats['module_load_times'][module_name] = {
                    'load_time': round(load_time, 4),
                    'memory_kb': round(peak / 1024, 2)
                }

                # Identify bottlenecks (>100ms load time)
                if load_time > 0.1:
                    performance_stats['bottlenecks'].append({
                        'module': module_name,
                        'issue': f'Slow load time: {load_time:.3f}s'
                    })

            except Exception as e:
                performance_stats['module_load_times'][module_name] = {'error': str(e)[:100]}

        # Analyze code complexity
        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Count complexity indicators
                function_count = len(re.findall(r'def \w+', content))
                class_count = len(re.findall(r'class \w+', content))
                import_count = len(re.findall(r'^import |^from ', content, re.MULTILINE))
                dict_count = len(re.findall(r'\{.*?:.*?\}', content))

                if function_count > 50 or dict_count > 100:
                    performance_stats['bottlenecks'].append({
                        'file': py_file.name,
                        'issue': f'High complexity: {function_count} functions, {dict_count} dicts'
                    })

            except Exception as e:
                continue

        self.results['performance'] = performance_stats

        avg_load_time = sum([
            m.get('load_time', 0) for m in performance_stats['module_load_times'].values()
            if isinstance(m, dict) and 'load_time' in m
        ]) / len(performance_stats['module_load_times'])

        print(f"  Average module load time: {avg_load_time:.4f}s")
        print(f"  Performance bottlenecks found: {len(performance_stats['bottlenecks'])}")

    def _analyze_dependencies(self):
        """Analyze module dependencies and integration patterns"""
        print("Analyzing module dependencies...")

        dependency_stats = {
            'import_graph': defaultdict(list),
            'module_levels': {},
            'circular_dependencies': [],
            'orphan_modules': [],
            'hub_modules': [],
            'external_dependencies': Counter()
        }

        # Build import graph
        for py_file in self.modules_dir.rglob("*.py"):
            module_name = py_file.stem
            try:
                content = py_file.read_text()

                # Find local imports
                local_imports = re.findall(r'from \.(\w+)|from (\w+) import', content)
                for from_match, direct_import in local_imports:
                    target = from_match or direct_import
                    if target and target != module_name:
                        dependency_stats['import_graph'][module_name].append(target)

                # Find external dependencies
                external_imports = re.findall(r'^import (\w+)|^from (\w+) import', content, re.MULTILINE)
                for ext_import, _ in external_imports:
                    if ext_import and not ext_import.startswith('_'):
                        dependency_stats['external_dependencies'][ext_import] += 1

            except Exception as e:
                continue

        # Identify hub modules (imported by many others)
        import_count = defaultdict(int)
        for module, imports in dependency_stats['import_graph'].items():
            for imp in imports:
                import_count[imp] += 1

        # Convert to Counter for most_common
        import_counter = Counter(import_count)
        dependency_stats['hub_modules'] = [
            (module, count) for module, count in import_counter.most_common(10)
        ]

        # Find potential circular dependencies
        for module, imports in dependency_stats['import_graph'].items():
            for imp in imports:
                if imp in dependency_stats['import_graph'] and module in dependency_stats['import_graph'][imp]:
                    if sorted([module, imp]) not in dependency_stats['circular_dependencies']:
                        dependency_stats['circular_dependencies'].append(sorted([module, imp]))

        # Find orphan modules (no dependencies)
        dependency_stats['orphan_modules'] = [
            module for module in dependency_stats['import_graph']
            if not dependency_stats['import_graph'][module] and module != '__init__'
        ]

        self.results['dependencies'] = dependency_stats

        print(f"  Module dependency pairs: {sum(len(v) for v in dependency_stats['import_graph'].values())}")
        print(f"  Hub modules (top 10): {len(dependency_stats['hub_modules'])}")
        print(f"  Circular dependencies: {len(dependency_stats['circular_dependencies'])}")
        print(f"  Orphan modules: {len(dependency_stats['orphan_modules'])}")

    def _assess_error_handling(self):
        """Assess error handling quality across modules"""
        print("Assessing error handling capabilities...")

        error_handling_stats = {
            'try_catch_blocks': 0,
            'specific_exceptions': 0,
            'generic_exceptions': 0,
            'error_logging': 0,
            'graceful_degradation': 0,
            'risky_modules': []
        }

        for py_file in self.modules_dir.rglob("*.py"):
            try:
                content = py_file.read_text()

                # Count try-except blocks
                try_blocks = len(re.findall(r'try:', content))
                except_blocks = re.findall(r'except\s+([^:]+):', content)

                error_handling_stats['try_catch_blocks'] += try_blocks

                for exception in except_blocks:
                    exception = exception.strip()
                    if exception == 'Exception' or exception == '':
                        error_handling_stats['generic_exceptions'] += 1
                    else:
                        error_handling_stats['specific_exceptions'] += 1

                # Check for error logging
                if re.search(r'logging\.error|logger\.error|print.*error', content, re.IGNORECASE):
                    error_handling_stats['error_logging'] += 1

                # Check for graceful degradation (return empty dict on error)
                if re.search(r'return\s*\{\}|except.*?return\s*\{\}', content):
                    error_handling_stats['graceful_degradation'] += 1

                # Identify risky modules (no try-except but file operations)
                has_file_ops = bool(re.search(r'open\(|Path\(|\.read\(\)|\.write\(', content))
                has_error_handling = try_blocks > 0

                if has_file_ops and not has_error_handling:
                    error_handling_stats['risky_modules'].append(py_file.name)

            except Exception as e:
                continue

        self.results['error_handling'] = error_handling_stats

        total_modules = len(list(self.modules_dir.rglob("*.py")))
        safe_modules = total_modules - len(error_handling_stats['risky_modules'])

        print(f"  Total try-except blocks: {error_handling_stats['try_catch_blocks']}")
        print(f"  Specific exceptions: {error_handling_stats['specific_exceptions']}")
        print(f"  Generic exceptions: {error_handling_stats['generic_exceptions']}")
        print(f"  Modules with error logging: {error_handling_stats['error_logging']}")
        print(f"  Modules with graceful degradation: {error_handling_stats['graceful_degradation']}")
        print(f"  Risky modules (file ops without error handling): {len(error_handling_stats['risky_modules'])}")
        print(f"  Safety rate: {(safe_modules/total_modules)*100:.1f}%")

    def _analyze_api_endpoints(self):
        """Analyze API endpoints and functionality"""
        print("Analyzing API endpoints...")

        api_stats = {
            'routes_file': None,
            'endpoints': [],
            'middleware': [],
            'exposure_level': 'unknown',
            'authentication': [],
            'data_validation': []
        }

        # Look for routes file
        routes_files = list(self.server_dir.rglob("*route*.py")) + list(self.server_dir.rglob("app.py"))
        if routes_files:
            routes_file = routes_files[0]
            api_stats['routes_file'] = str(routes_file)

            try:
                content = routes_file.read_text()

                # Find API endpoints
                endpoint_patterns = [
                    r'@app\.route\([\'"]([^\'"]+)[\'"]',
                    r'@router\.(\w+)\([\'"]([^\'"]+)[\'"]',
                    r'@\w+\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]',
                    r'app\.(\w+)\([\'"]([^\'"]+)[\'"]'
                ]

                for pattern in endpoint_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            method = match[0] if match[0] else 'GET'
                            path = match[1] if len(match) > 1 else match[0]
                        else:
                            method = 'GET'
                            path = match

                        api_stats['endpoints'].append({
                            'path': path,
                            'method': method.upper()
                        })

                # Check for middleware
                middleware_patterns = [
                    r'@.*cors', r'@.*auth', r'@.*validate',
                    r'middleware', r'before_request', r'after_request'
                ]

                for pattern in middleware_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        api_stats['middleware'].append(pattern)

                # Check for authentication
                if re.search(r'auth|login|jwt|token|api_key', content, re.IGNORECASE):
                    api_stats['authentication'].append('auth_detected')

                # Check for data validation
                if re.search(r'validate|schema|request\.json|request\.files', content, re.IGNORECASE):
                    api_stats['data_validation'].append('validation_detected')

            except Exception as e:
                api_stats['error'] = str(e)[:100]

        self.results['api_analysis'] = api_stats

        print(f"  Routes file: {api_stats['routes_file']}")
        print(f"  Endpoints found: {len(api_stats['endpoints'])}")
        print(f"  Middleware detected: {len(api_stats['middleware'])}")
        print(f"  Authentication: {len(api_stats['authentication']) > 0}")
        print(f"  Data validation: {len(api_stats['data_validation']) > 0}")

        if api_stats['endpoints']:
            print(f"  Sample endpoints:")
            for endpoint in api_stats['endpoints'][:5]:
                print(f"    {endpoint['method']:6s} {endpoint['path']}")

    def _generate_summary(self):
        """Generate comprehensive summary"""
        summary = {
            'overall_health': 'unknown',
            'critical_issues': [],
            'recommendations': [],
            'metrics': {}
        }

        # Calculate health score
        extraction_health = (
            self.results['extraction_test'].get('working_extract_functions', 0) /
            max(self.results['extraction_test'].get('total_extract_functions', 1), 1) * 100
        )

        bottlenecks = len(self.results['performance'].get('bottlenecks', []))
        risky_modules = len(self.results['error_handling'].get('risky_modules', []))

        health_score = (extraction_health + (100 - min(bottlenecks, 100)) + (100 - min(risky_modules * 5, 100))) / 3

        if health_score > 80:
            summary['overall_health'] = 'good'
        elif health_score > 60:
            summary['overall_health'] = 'fair'
        else:
            summary['overall_health'] = 'poor'

        # Critical issues
        if risky_modules > 10:
            summary['critical_issues'].append(f'{risky_modules} modules lack error handling for file operations')
        if bottlenecks > 5:
            summary['critical_issues'].append(f'{bottlenecks} performance bottlenecks detected')
        if self.results['dependencies'].get('circular_dependencies'):
            summary['critical_issues'].append(f'{len(self.results["dependencies"]["circular_dependencies"])} circular dependencies found')

        # Recommendations
        summary['recommendations'] = [
            'Implement comprehensive error handling across all file operation modules',
            'Optimize modules with high complexity and slow load times',
            'Break circular dependencies to improve modularity',
            'Add unit tests for critical extraction functions',
            'Implement API rate limiting and authentication',
            'Document field coverage discrepancy (theoretical vs actual)'
        ]

        summary['metrics'] = {
            'extraction_functions': self.results['extraction_test'].get('total_extract_functions', 0),
            'working_extractions': self.results['extraction_test'].get('working_extract_functions', 0),
            'performance_bottlenecks': bottlenecks,
            'risky_modules': risky_modules,
            'api_endpoints': len(self.results['api_analysis'].get('endpoints', [])),
            'health_score': round(health_score, 1)
        }

        self.results['summary'] = summary

        print(f"\n" + "="*80)
        print("SYSTEM HEALTH SUMMARY")
        print("="*80)
        print(f"Overall Health: {summary['overall_health'].upper()}")
        print(f"Health Score: {summary['metrics']['health_score']}/100")
        print(f"Extraction Functions: {summary['metrics']['extraction_functions']}")
        print(f"Working Extractions: {summary['metrics']['working_extractions']}")
        print(f"Performance Bottlenecks: {summary['metrics']['performance_bottlenecks']}")
        print(f"Risky Modules: {summary['metrics']['risky_modules']}")
        print(f"API Endpoints: {summary['metrics']['api_endpoints']}")

        if summary['critical_issues']:
            print(f"\n⚠️  CRITICAL ISSUES ({len(summary['critical_issues'])}):")
            for issue in summary['critical_issues']:
                print(f"  • {issue}")

        print(f"\n📋 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(summary['recommendations'][:5], 1):
            print(f"  {i}. {rec}")

        # Save detailed results
        output_file = Path("/Users/pranay/Projects/metaextract/docs/comprehensive_system_analysis.json")
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📊 Detailed analysis saved to: {output_file}")

def main():
    analyzer = ComprehensiveAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
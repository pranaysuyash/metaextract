#!/usr/bin/env python3
"""
Test script to verify database performance index improvements
"""

import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def test_query_performance():
    """Test query performance before and after index creation"""
    from extractor.modules.metadata_db import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    test_results = {}
    
    print("Testing database query performance...")
    print("=" * 60)
    
    # Test 1: File type queries (should use idx_files_type)
    print("1. Testing file type queries...")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(*) as count, file_type
        FROM files 
        WHERE file_type IN ('.jpg', '.png', '.mp4')
        GROUP BY file_type
        ORDER BY count DESC
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    test_results['file_type_query'] = {
        'execution_time': query_time,
        'results': len(results),
        'description': 'File type grouping query'
    }
    print(f"   ✓ Found {len(results)} file types in {query_time:.4f}s")
    
    # Test 2: Metadata search (should use idx_metadata_category_key_value)
    print("2. Testing metadata search...")
    start_time = time.time()
    cursor.execute("""
        SELECT f.file_path, f.file_type, m.value
        FROM files f
        JOIN metadata m ON f.id = m.file_id
        WHERE m.category = 'exif' AND m.key = 'Make' AND m.value LIKE '%Canon%'
        LIMIT 10
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    test_results['metadata_search'] = {
        'execution_time': query_time,
        'results': len(results),
        'description': 'Metadata search with JOIN'
    }
    print(f"   ✓ Found {len(results)} files with Canon metadata in {query_time:.4f}s")
    
    # Test 3: Recent files query (should use idx_files_recent)
    print("3. Testing recent files query...")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(*) as recent_count
        FROM files
        WHERE extracted_at > datetime('now', '-30 days')
    """)
    result = cursor.fetchone()
    query_time = time.time() - start_time
    test_results['recent_files'] = {
        'execution_time': query_time,
        'results': result[0] if result else 0,
        'description': 'Recent files count (last 30 days)'
    }
    print(f"   ✓ Found {result[0] if result else 0} recent files in {query_time:.4f}s")
    
    # Test 4: File size range query (should use idx_files_size_range)
    print("4. Testing file size range query...")
    start_time = time.time()
    cursor.execute("""
        SELECT COUNT(*) as count, 
               CASE 
                   WHEN file_size < 1024*1024 THEN 'Small (<1MB)'
                   WHEN file_size < 10*1024*1024 THEN 'Medium (1-10MB)'
                   ELSE 'Large (>10MB)'
               END as size_category
        FROM files
        WHERE file_size > 0
        GROUP BY size_category
        ORDER BY count DESC
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    test_results['size_range'] = {
        'execution_time': query_time,
        'results': len(results),
        'description': 'File size distribution'
    }
    print(f"   ✓ Analyzed file size distribution in {query_time:.4f}s")
    
    # Test 5: Complex JOIN query (should use multiple indexes)
    print("5. Testing complex JOIN query...")
    start_time = time.time()
    cursor.execute("""
        SELECT f.file_path, f.file_type, f.extracted_at,
               COUNT(m.file_id) as metadata_count
        FROM files f
        LEFT JOIN metadata m ON f.id = m.file_id
        WHERE f.extracted_at > datetime('now', '-7 days')
        GROUP BY f.id, f.file_path, f.file_type, f.extracted_at
        HAVING metadata_count > 5
        ORDER BY f.extracted_at DESC
        LIMIT 20
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    test_results['complex_join'] = {
        'execution_time': query_time,
        'results': len(results),
        'description': 'Complex JOIN with GROUP BY and HAVING'
    }
    print(f"   ✓ Found {len(results)} files with rich metadata in {query_time:.4f}s")
    
    # Test 6: Favorites query (should use idx_favorites_files_join)
    print("6. Testing favorites query...")
    start_time = time.time()
    cursor.execute("""
        SELECT f.file_path, f.file_type, fav.added_at
        FROM favorites fav
        JOIN files f ON fav.file_id = f.id
        ORDER BY fav.added_at DESC
        LIMIT 10
    """)
    results = cursor.fetchall()
    query_time = time.time() - start_time
    test_results['favorites'] = {
        'execution_time': query_time,
        'results': len(results),
        'description': 'Favorites with file JOIN'
    }
    print(f"   ✓ Found {len(results)} favorite files in {query_time:.4f}s")
    
    conn.close()
    
    return test_results

def test_index_usage():
    """Test if indexes are being used by examining query plans"""
    from extractor.modules.metadata_db import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\nTesting index usage with EXPLAIN QUERY PLAN...")
    print("=" * 60)
    
    # Test query plans for common queries
    test_queries = [
        {
            'name': 'File type search',
            'query': "EXPLAIN QUERY PLAN SELECT * FROM files WHERE file_type = '.jpg' LIMIT 10",
            'expected_index': 'idx_files_type'
        },
        {
            'name': 'Metadata category search',
            'query': "EXPLAIN QUERY PLAN SELECT * FROM metadata WHERE category = 'exif' LIMIT 10",
            'expected_index': 'idx_metadata_category'
        },
        {
            'name': 'Recent files',
            'query': "EXPLAIN QUERY PLAN SELECT * FROM files WHERE extracted_at > datetime('now', '-7 days') ORDER BY extracted_at DESC LIMIT 10",
            'expected_index': 'idx_files_extracted_at'
        },
        {
            'name': 'File hash lookup',
            'query': "EXPLAIN QUERY PLAN SELECT * FROM files WHERE file_hash = 'test123' LIMIT 1",
            'expected_index': 'idx_files_hash'
        }
    ]
    
    index_usage_results = {}
    
    for test in test_queries:
        print(f"\n{test['name']}:")
        try:
            cursor.execute(test['query'])
            plan = cursor.fetchall()
            
            # Check if expected index is mentioned in the plan
            plan_text = ' '.join([str(row) for row in plan])
            index_used = test['expected_index'] in plan_text
            
            print(f"   Query plan: {plan_text}")
            print(f"   Index usage: {'✓ USING INDEX' if index_used else '✗ NO INDEX'}")
            
            index_usage_results[test['name']] = {
                'index_used': index_used,
                'expected_index': test['expected_index'],
                'plan': plan_text
            }
        except Exception as e:
            print(f"   Error: {e}")
            index_usage_results[test['name']] = {
                'error': str(e)
            }
    
    conn.close()
    
    return index_usage_results

def generate_performance_report():
    """Generate a comprehensive performance report"""
    print("\n" + "=" * 60)
    print("DATABASE PERFORMANCE INDEX TEST REPORT")
    print("=" * 60)
    
    # Run performance tests
    performance_results = test_query_performance()
    
    # Run index usage tests
    index_results = test_index_usage()
    
    # Generate summary
    report = {
        'timestamp': datetime.now().isoformat(),
        'performance_tests': performance_results,
        'index_usage': index_results,
        'summary': {
            'total_tests': len(performance_results),
            'successful_queries': sum(1 for r in performance_results.values() if 'error' not in r),
            'average_query_time': sum(r.get('execution_time', 0) for r in performance_results.values()) / len(performance_results),
            'indexes_used': sum(1 for r in index_results.values() if r.get('index_used', False))
        }
    }
    
    # Print summary
    print(f"\nSUMMARY:")
    print(f"Total queries tested: {report['summary']['total_tests']}")
    print(f"Successful queries: {report['summary']['successful_queries']}")
    print(f"Average query time: {report['summary']['average_query_time']:.4f}s")
    print(f"Indexes being used: {report['summary']['indexes_used']}/{len(index_results)}")
    
    # Performance recommendations
    print(f"\nPERFORMANCE RECOMMENDATIONS:")
    
    slow_queries = [name for name, result in performance_results.items() 
                   if result.get('execution_time', 0) > 0.1]  # Queries taking >100ms
    
    if slow_queries:
        print(f"⚠️  Slow queries detected (>100ms): {', '.join(slow_queries)}")
        print(f"   Consider analyzing these queries for additional optimization")
    else:
        print("✓ All queries completed in under 100ms")
    
    unused_indexes = [name for name, result in index_results.items() 
                     if not result.get('index_used', False)]
    
    if unused_indexes:
        print(f"⚠️  Queries not using expected indexes: {', '.join(unused_indexes)}")
        print(f"   Consider reviewing index definitions or query patterns")
    else:
        print("✓ All queries are using expected indexes")
    
    # Save report
    report_file = f"performance_reports/index_performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    generate_performance_report()
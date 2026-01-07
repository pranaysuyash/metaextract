#!/usr/bin/env python3
"""
Database Performance Profiling Script for MetaExtract
"""

import time
import json
import sqlite3
import psutil
from datetime import datetime
from pathlib import Path

# Add the server directory to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def profile_database_operations():
    """Profile database operations directly"""
    from extractor.modules.metadata_db import (
        store_file_metadata, get_file_metadata, search_metadata_query, get_db_connection
    )
    
    results = {}
    process = psutil.Process()
    
    # Test file path
    test_file_path = "test_image.jpg"
    test_file_hash = "abc123def456"
    
    # Sample metadata
    test_metadata = {
        "filename": "test_image.jpg",
        "file_size": 2048576,
        "file_type": "image/jpeg",
        "width": 1920,
        "height": 1080,
        "camera_make": "Canon",
        "camera_model": "EOS 5D",
        "created_at": "2024-01-01T12:00:00Z",
        "exif": {
            "ISO": 400,
            "Aperture": "f/5.6",
            "ShutterSpeed": "1/125s",
            "FocalLength": "85mm"
        }
    }
    
    print("Profiling database operations...")
    
    # Profile store operation
    print("1. Testing metadata storage...")
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        store_file_metadata(test_file_path, test_file_hash, test_metadata)
        store_success = True
        store_error = None
    except Exception as e:
        store_success = False
        store_error = str(e)
    
    store_time = time.time() - start_time
    store_memory = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    results['store'] = {
        'execution_time': store_time,
        'memory_usage_mb': store_memory,
        'success': store_success,
        'error': store_error
    }
    
    # Profile retrieve operation
    print("2. Testing metadata retrieval...")
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        retrieved_metadata = get_file_metadata(test_file_hash)
        retrieve_success = True
        retrieve_error = None
    except Exception as e:
        retrieved_metadata = None
        retrieve_success = False
        retrieve_error = str(e)
    
    retrieve_time = time.time() - start_time
    retrieve_memory = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    results['retrieve'] = {
        'execution_time': retrieve_time,
        'memory_usage_mb': retrieve_memory,
        'success': retrieve_success,
        'error': retrieve_error,
        'result_count': len(retrieved_metadata) if retrieved_metadata else 0
    }
    
    # Profile search operation
    print("3. Testing metadata search...")
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        search_results = search_metadata_query("Canon")
        search_success = True
        search_error = None
    except Exception as e:
        search_results = []
        search_success = False
        search_error = str(e)
    
    search_time = time.time() - start_time
    search_memory = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    results['search'] = {
        'execution_time': search_time,
        'memory_usage_mb': search_memory,
        'success': search_success,
        'error': search_error,
        'result_count': len(search_results)
    }
    
    # Test bulk operations
    print("4. Testing bulk operations...")
    bulk_results = profile_bulk_operations()
    results['bulk'] = bulk_results
    
    # Test database statistics
    print("5. Testing database statistics...")
    try:
        from extractor.modules.metadata_db import get_statistics
        stats = get_statistics()
        results['statistics'] = {
            'success': True,
            'data': stats
        }
    except Exception as e:
        results['statistics'] = {
            'success': False,
            'error': str(e)
        }
    
    return results

def profile_bulk_operations():
    """Profile bulk database operations"""
    from extractor.modules.metadata_db import store_file_metadata, get_db_connection
    
    results = {}
    process = psutil.Process()
    
    # Create sample data for bulk operations
    bulk_data = []
    for i in range(10):
        bulk_data.append({
            "file_path": f"bulk_test_{i}.jpg",
            "file_hash": f"hash_{i}_abc123",
            "metadata": {
                "filename": f"bulk_test_{i}.jpg",
                "file_size": 1024000 + i * 100000,
                "file_type": "image/jpeg",
                "width": 1920,
                "height": 1080,
                "camera_make": "TestCamera",
                "camera_model": f"Model {i}",
                "created_at": f"2024-01-{i+1:02d}T12:00:00Z"
            }
        })
    
    # Profile bulk store
    print("  4a. Testing bulk storage...")
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        for item in bulk_data:
            store_file_metadata(item['file_path'], item['file_hash'], item['metadata'])
        bulk_store_success = True
        bulk_store_error = None
    except Exception as e:
        bulk_store_success = False
        bulk_store_error = str(e)
    
    bulk_store_time = time.time() - start_time
    bulk_store_memory = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    results['bulk_store'] = {
        'execution_time': bulk_store_time,
        'memory_usage_mb': bulk_store_memory,
        'success': bulk_store_success,
        'error': bulk_store_error,
        'items_processed': len(bulk_data) if bulk_store_success else 0,
        'avg_time_per_item': bulk_store_time / len(bulk_data) if bulk_store_success else 0
    }
    
    # Profile bulk retrieve
    print("  4b. Testing bulk retrieval...")
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    try:
        from extractor.modules.metadata_db import get_file_metadata
        retrieved_items = []
        for item in bulk_data:
            metadata = get_file_metadata(item['file_hash'])
            if metadata:
                retrieved_items.append(metadata)
        bulk_retrieve_success = True
        bulk_retrieve_error = None
    except Exception as e:
        retrieved_items = []
        bulk_retrieve_success = False
        bulk_retrieve_error = str(e)
    
    bulk_retrieve_time = time.time() - start_time
    bulk_retrieve_memory = (process.memory_info().rss / 1024 / 1024) - start_memory
    
    results['bulk_retrieve'] = {
        'execution_time': bulk_retrieve_time,
        'memory_usage_mb': bulk_retrieve_memory,
        'success': bulk_retrieve_success,
        'error': bulk_retrieve_error,
        'items_retrieved': len(retrieved_items),
        'avg_time_per_item': bulk_retrieve_time / len(bulk_data) if bulk_retrieve_success else 0
    }
    
    return results

def analyze_database_file():
    """Analyze the database file itself"""
    db_path = Path("data/metadata.db")
    
    if not db_path.exists():
        return {"error": "Database file not found"}
    
    stats = {
        "file_size_bytes": db_path.stat().st_size,
        "file_size_mb": round(db_path.stat().st_size / 1024 / 1024, 2),
        "created": datetime.fromtimestamp(db_path.stat().st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
    }
    
    # Get table information
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        stats["tables"] = [table[0] for table in tables]
        
        # Get row counts for each table
        table_counts = {}
        for table in stats["tables"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_counts[table] = count
        stats["table_row_counts"] = table_counts
        
        # Get database schema
        schema = {}
        for table in stats["tables"]:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema[table] = [(col[1], col[2]) for col in columns]  # name, type
        stats["schema"] = schema
        
        conn.close()
    except Exception as e:
        stats["database_error"] = str(e)
    
    return stats

def main():
    """Main profiling function"""
    print("Database Performance Profiling")
    print("=" * 50)
    
    # Profile database operations
    db_results = profile_database_operations()
    
    # Analyze database file
    file_stats = analyze_database_file()
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 1)
        },
        "database_operations": db_results,
        "database_file_stats": file_stats
    }
    
    # Save report
    report_file = f"performance_reports/database_profiling_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("DATABASE PERFORMANCE SUMMARY")
    print("=" * 50)
    
    print(f"\nDatabase Operations:")
    for op_name, op_data in db_results.items():
        if isinstance(op_data, dict) and 'execution_time' in op_data:
            status = "✓" if op_data.get('success') else "✗"
            print(f"{status} {op_name}: {op_data['execution_time']:.4f}s")
            if op_data.get('error'):
                print(f"  Error: {op_data['error']}")
    
    print(f"\nDatabase File Stats:")
    if "error" not in file_stats:
        print(f"- File Size: {file_stats['file_size_mb']} MB")
        print(f"- Tables: {len(file_stats.get('tables', []))}")
        print(f"- Total Rows: {sum(file_stats.get('table_row_counts', {}).values())}")
    else:
        print(f"- {file_stats['error']}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
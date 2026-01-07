#!/usr/bin/env python3
"""
Apply performance indexes and measure improvements
"""

import os
import sys
import psycopg2
import time
import json
from datetime import datetime
from pathlib import Path

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'metaextract'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        return None

def apply_migration(migration_file):
    """Apply a single migration file"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Split by DO $$ blocks and execute each separately
            blocks = sql_content.split('DO $$')
            
            for i, block in enumerate(blocks):
                if i == 0 and not block.strip():
                    continue
                    
                # Reconstruct the DO $$ block
                if i > 0:
                    block = 'DO $$' + block
                
                # Find the matching END $$ for this block
                if 'END$$' in block:
                    # Execute the anonymous code block
                    cursor.execute(block)
                elif block.strip() and not block.startswith('--'):
                    # Execute regular SQL statements
                    statements = [stmt.strip() for stmt in block.split(';') if stmt.strip()]
                    for statement in statements:
                        if statement and not statement.startswith('--'):
                            cursor.execute(statement + ';')
            
            conn.commit()
            print(f"✓ Applied migration: {migration_file}")
            return True
            
    except Exception as e:
        conn.rollback()
        print(f"✗ Failed to apply migration {migration_file}: {e}")
        return False
    finally:
        conn.close()

def benchmark_query_performance():
    """Benchmark key query performance with and without indexes"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    results = {}
    
    try:
        with conn.cursor() as cursor:
            # Test queries that should benefit from our new indexes
            test_queries = [
                {
                    'name': 'metadata_store_by_type_tier',
                    'query': """
                        SELECT COUNT(*) as count, file_type, tier_used
                        FROM metadata_store
                        WHERE file_type IN ('image', 'video', 'audio')
                        GROUP BY file_type, tier_used
                        ORDER BY count DESC
                    """,
                    'expected_index': 'idx_metadata_store_type_tier'
                },
                {
                    'name': 'field_analytics_by_count',
                    'query': """
                        SELECT field_name, extraction_count, last_extracted_at
                        FROM field_analytics
                        WHERE extraction_count > 100
                        ORDER BY extraction_count DESC
                        LIMIT 20
                    """,
                    'expected_index': 'idx_field_analytics_count_date'
                },
                {
                    'name': 'metadata_store_by_user_time',
                    'query': """
                        SELECT file_path, file_type, extracted_at, total_fields_extracted
                        FROM metadata_store
                        WHERE user_id IS NOT NULL
                        ORDER BY extracted_at DESC
                        LIMIT 50
                    """,
                    'expected_index': 'idx_metadata_store_user_created'
                },
                {
                    'name': 'ui_events_by_product_time',
                    'query': """
                        SELECT product, event_name, COUNT(*) as event_count
                        FROM ui_events
                        WHERE created_at > NOW() - INTERVAL '7 days'
                        GROUP BY product, event_name
                        ORDER BY event_count DESC
                    """,
                    'expected_index': 'idx_ui_events_time_product'
                }
            ]
            
            for test in test_queries:
                print(f"\nBenchmarking: {test['name']}")
                
                # Execute query multiple times and measure average time
                times = []
                for i in range(5):
                    start_time = time.time()
                    cursor.execute(test['query'])
                    results_data = cursor.fetchall()
                    query_time = time.time() - start_time
                    times.append(query_time)
                
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                results[test['name']] = {
                    'average_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'results_count': len(results_data),
                    'expected_index': test['expected_index']
                }
                
                print(f"  Average: {avg_time:.4f}s (min: {min_time:.4f}s, max: {max_time:.4f}s)")
                print(f"  Results: {len(results_data)} rows")
                
    except Exception as e:
        print(f"Error during benchmarking: {e}")
        results['error'] = str(e)
    finally:
        conn.close()
    
    return results

def check_index_usage():
    """Check if indexes are being used effectively"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    results = {}
    
    try:
        with conn.cursor() as cursor:
            # Check index usage statistics
            cursor.execute("""
                SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE schemaname = 'public'
                ORDER BY idx_tup_read DESC
            """)
            
            index_stats = cursor.fetchall()
            results['index_usage'] = [
                {
                    'schema': row[0],
                    'table': row[1],
                    'index': row[2],
                    'tuple_reads': row[3],
                    'tuple_fetches': row[4]
                }
                for row in index_stats
            ]
            
            # Check table sizes
            cursor.execute("""
                SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY n_live_tup DESC
            """)
            
            table_stats = cursor.fetchall()
            results['table_sizes'] = [
                {
                    'schema': row[0],
                    'table': row[1],
                    'inserts': row[2],
                    'updates': row[3],
                    'deletes': row[4],
                    'live_tuples': row[5]
                }
                for row in table_stats
            ]
            
    except Exception as e:
        print(f"Error checking index usage: {e}")
        results['error'] = str(e)
    finally:
        conn.close()
    
    return results

def main():
    """Main function to apply migrations and test performance"""
    print("Database Performance Index Application")
    print("=" * 60)
    
    # Ensure performance_reports directory exists
    os.makedirs('performance_reports', exist_ok=True)
    
    # Apply migrations
    migrations = [
        'server/migrations/009_performance_indexes_metadata.sql',
        'server/migrations/010_performance_indexes_joins.sql'
    ]
    
    applied_migrations = []
    
    for migration_file in migrations:
        if os.path.exists(migration_file):
            print(f"\nApplying migration: {migration_file}")
            if apply_migration(migration_file):
                applied_migrations.append(migration_file)
            else:
                print("Migration failed, stopping...")
                return
        else:
            print(f"⚠️  Migration file not found: {migration_file}")
    
    print(f"\n✓ Successfully applied {len(applied_migrations)} migrations")
    
    # Benchmark performance
    print("\n" + "=" * 60)
    print("BENCHMARKING QUERY PERFORMANCE")
    print("=" * 60)
    
    benchmark_results = benchmark_query_performance()
    
    # Check index usage
    print("\n" + "=" * 60)
    print("CHECKING INDEX USAGE")
    print("=" * 60)
    
    usage_results = check_index_usage()
    
    # Generate comprehensive report
    report = {
        'timestamp': datetime.now().isoformat(),
        'applied_migrations': applied_migrations,
        'benchmark_results': benchmark_results,
        'index_usage': usage_results,
        'summary': {
            'migrations_applied': len(applied_migrations),
            'queries_benchmarked': len(benchmark_results),
            'total_indexes': len(usage_results.get('index_usage', [])),
            'active_tables': len(usage_results.get('table_sizes', []))
        }
    }
    
    # Save report
    report_file = f"performance_reports/index_application_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Migrations applied: {report['summary']['migrations_applied']}")
    print(f"Queries benchmarked: {report['summary']['queries_benchmarked']}")
    print(f"Total indexes in database: {report['summary']['total_indexes']}")
    print(f"Active tables: {report['summary']['active_tables']}")
    
    if benchmark_results:
        avg_time = sum(r.get('average_time', 0) for r in benchmark_results.values() if isinstance(r, dict)) / len(benchmark_results)
        print(f"Average query time: {avg_time:.4f}s")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Performance recommendations
    print(f"\nRECOMMENDATIONS:")
    
    if usage_results.get('index_usage'):
        unused_indexes = [idx for idx in usage_results['index_usage'] 
                         if idx.get('tuple_reads', 0) == 0 and idx.get('tuple_fetches', 0) == 0]
        if unused_indexes:
            print(f"⚠️  Found {len(unused_indexes)} potentially unused indexes")
            print(f"   Consider reviewing: {', '.join(idx['index'] for idx in unused_indexes[:5])}")
    
    if benchmark_results:
        slow_queries = [name for name, result in benchmark_results.items() 
                       if isinstance(result, dict) and result.get('average_time', 0) > 0.1]
        if slow_queries:
            print(f"⚠️  Slow queries detected (>100ms): {', '.join(slow_queries)}")
            print(f"   Consider additional optimization for these patterns")
    
    print("\n✓ Index application and testing completed successfully!")

if __name__ == "__main__":
    main()
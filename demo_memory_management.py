#!/usr/bin/env python3
"""
Memory Management Agent - Demo Script

Showcases all 4 memory management components:
1. Memory usage analysis
2. Streaming for large files
3. Memory-efficient processing
4. Garbage collection optimization
"""

import sys
import os
import time
import tempfile
import json

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from extractor.memory_management_agent import (
    get_memory_agent,
    MemoryMonitor,
    GarbageCollectionOptimizer,
    MemoryResourcePool,
    ExtractionStrategy,
    cleanup_memory_agent
)
from extractor.streaming_large_files import (
    StreamingConfig,
    BinaryStreamReader,
    AdaptiveChunkSizer
)


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_memory_monitoring():
    """Task 1: Analyze memory usage patterns."""
    print_header("Task 1: Memory Usage Analysis")
    
    monitor = MemoryMonitor()
    
    # Get current snapshot
    snapshot = monitor.get_current_snapshot()
    print(f"\n📊 Current Memory Status:")
    print(f"   Resident Memory:  {snapshot.resident_mb:.1f} MB")
    print(f"   Virtual Memory:   {snapshot.virtual_mb:.1f} MB")
    print(f"   Percent Used:     {snapshot.percent_used:.1f}%")
    print(f"   Available:        {snapshot.available_mb:.1f} MB")
    print(f"   Memory Level:     {snapshot.memory_level.value}")
    
    # Start monitoring
    print(f"\n⏱️  Monitoring memory for 2 seconds...")
    monitor.start_monitoring()
    
    # Allocate some memory
    data = [i for i in range(500000)]
    
    time.sleep(2)
    
    monitor.stop_monitoring()
    
    # Get stats
    stats = monitor.get_memory_summary()
    print(f"\n📈 Memory Statistics:")
    print(f"   Peak Memory:      {stats['peak_mb']:.1f} MB")
    print(f"   Average Memory:   {stats['average_mb']:.1f} MB")
    print(f"   Snapshots:        {stats['snapshots_collected']}")
    
    del data


def demo_streaming():
    """Task 2: Streaming for large files."""
    print_header("Task 2: Streaming Large Files")
    
    # Create test file
    print(f"\n📝 Creating test file...")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
        test_file = f.name
        # Write 5MB of test data
        f.write(b'x' * (5 * 1024 * 1024))
    
    try:
        # Demo streaming
        print(f"\n📖 Streaming file in chunks:")
        
        config = StreamingConfig(
            chunk_size=512 * 1024,  # 512KB chunks
            adaptive_sizing=False
        )
        
        reader = BinaryStreamReader(config)
        
        total_size = 0
        chunk_count = 0
        
        for chunk in reader.read_chunks(test_file):
            chunk_count += 1
            total_size += len(chunk)
            
            if chunk_count <= 3 or chunk_count % 5 == 0:
                print(f"   Chunk {chunk_count}: {len(chunk) / (1024):.0f} KB "
                      f"(Total: {total_size / (1024 * 1024):.1f} MB)")
        
        print(f"\n✅ Completed: {chunk_count} chunks, {total_size / (1024 * 1024):.1f} MB total")
        
    finally:
        os.unlink(test_file)


def demo_memory_efficiency():
    """Task 3: Memory-efficient processing."""
    print_header("Task 3: Memory-Efficient Processing")
    
    sizer = AdaptiveChunkSizer()
    
    print(f"\n🧠 Adaptive Chunk Sizing:")
    optimal = sizer.get_optimal_chunk_size()
    print(f"   Min Size:         {sizer.min_chunk / (1024 * 1024):.1f} MB")
    print(f"   Max Size:         {sizer.max_chunk / (1024 * 1024):.1f} MB")
    print(f"   Optimal Size:     {optimal / (1024 * 1024):.1f} MB")
    
    print(f"\n🔄 Buffer Pooling Demo:")
    pool = MemoryResourcePool(buffer_size=1 * 1024 * 1024)
    
    # Allocate buffers
    buffers = []
    for i in range(3):
        buf = pool.allocate_buffer()
        buffers.append(buf)
    
    stats = pool.get_stats()
    print(f"   Allocations:      {stats['allocations']}")
    print(f"   Available:        {stats['currently_available']}")
    print(f"   In Use:           {stats['currently_in_use']}")
    
    # Return buffers
    print(f"\n   Releasing buffers to pool...")
    for buf in buffers:
        pool.release_buffer(buf)
    
    stats = pool.get_stats()
    print(f"   Allocations:      {stats['allocations']}")
    print(f"   Reuses:           {stats['reuses']}")
    print(f"   Available:        {stats['currently_available']}")
    print(f"   In Use:           {stats['currently_in_use']}")
    
    # Reuse
    print(f"\n   Reallocating (will reuse from pool)...")
    new_buf = pool.allocate_buffer()
    stats = pool.get_stats()
    print(f"   Reuses after realloc: {stats['reuses']}")


def demo_gc_optimization():
    """Task 4: Garbage collection optimization."""
    print_header("Task 4: Garbage Collection Optimization")
    
    optimizer = GarbageCollectionOptimizer()
    
    print(f"\n🔄 GC Configuration Demo:")
    print(f"   Original Thresholds: {optimizer.original_thresholds}")
    
    # Test different strategies
    strategies = [
        (ExtractionStrategy.AGGRESSIVE, "Fast extraction, plenty of memory"),
        (ExtractionStrategy.BALANCED, "Balanced approach (default)"),
        (ExtractionStrategy.CONSERVATIVE, "Limited memory scenario"),
    ]
    
    for strategy, description in strategies:
        optimizer.optimize_for_extraction(strategy)
        config = optimizer.get_current_config()
        print(f"\n   {strategy.value.upper()}:")
        print(f"   {description}")
        print(f"   Thresholds: {config['thresholds']}")
    
    # Reset
    optimizer.reset_to_default()
    print(f"\n✅ Reset to default: {optimizer.original_thresholds}")


def demo_memory_agent():
    """Full Memory Management Agent demo."""
    print_header("Complete Memory Management Agent")
    
    agent = get_memory_agent()
    
    print(f"\n🎯 Agent Status:")
    status = agent.get_memory_status()
    print(f"   Memory Level:     {status['memory_level']}")
    print(f"   Available:        {status['available_mb']:.1f} MB")
    print(f"   Used:             {status['used_percent']:.1f}%")
    
    print(f"\n📊 Running optimizations...")
    agent.optimize_all()
    
    print(f"\n✅ Optimization complete!")
    
    # Generate report
    report = agent.get_analysis_report()
    print(f"\n📈 Analysis Report:")
    print(f"   Timestamp:        {report['timestamp']}")
    print(f"   Memory Level:     {report['memory_status']['memory_level']}")
    print(f"   Available:        {report['memory_status']['available_mb']:.1f} MB")
    
    cleanup_memory_agent()


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  Memory Management Agent - Complete Demonstration")
    print("="*60)
    
    try:
        # Run all demos
        demo_memory_monitoring()
        demo_streaming()
        demo_memory_efficiency()
        demo_gc_optimization()
        demo_memory_agent()
        
        # Summary
        print_header("Summary")
        print(f"""
✅ Task 1: Memory Usage Analysis
   - Real-time monitoring with snapshots
   - Peak/average tracking
   - Memory level classification

✅ Task 2: Streaming for Large Files
   - Chunked processing (configurable size)
   - Memory-efficient generators
   - Format-specific readers

✅ Task 3: Memory-Efficient Processing
   - Adaptive chunk sizing
   - Strategy selection
   - Buffer pooling for reuse

✅ Task 4: Garbage Collection Optimization
   - Strategy-based thresholds
   - Incremental collection support
   - Force collection and leak detection

All 4 memory management components working perfectly!
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

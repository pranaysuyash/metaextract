#!/usr/bin/env python3
"""
Performance Improvement Test for MetaExtract Parallel Processing

This script tests the performance improvements achieved by the new
async/await-based parallel processing system.
"""

import asyncio
import time
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import both old and new systems for comparison
from server.extractor.parallel_extraction import ParallelExtractor, create_parallel_extractor
from server.extractor.async_parallel_processing import AsyncParallelExtractor, create_async_parallel_extractor, extract_files_async_parallel
from server.extractor.batch_optimization import process_batch_optimized
from server.extractor.batch_async_processor import process_batch_optimized_async


class PerformanceComparisonTest:
    """Test class to compare performance between old and new systems."""
    
    def __init__(self):
        self.test_files = []
        self.results = {
            "old_system": {},
            "new_system": {},
            "improvements": {}
        }
    
    def create_test_files(self, count: int = 50) -> List[str]:
        """Create test files for performance testing."""
        logger.info(f"Creating {count} test files...")
        
        test_files = []
        
        # Create image files
        for i in range(count // 2):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg', prefix=f'test_img_{i}_') as f:
                f.write(f"Test image content {i}" * 500)  # Simulate image content
                test_files.append(f.name)
        
        # Create document files
        for i in range(count // 4):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf', prefix=f'test_doc_{i}_') as f:
                f.write(f"Test PDF content {i}" * 1000)  # Simulate PDF content
                test_files.append(f.name)
        
        # Create video files
        for i in range(count // 4):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mp4', prefix=f'test_vid_{i}_') as f:
                f.write(f"Test video content {i}" * 1500)  # Simulate video content
                test_files.append(f.name)
        
        self.test_files = test_files
        logger.info(f"Created {len(test_files)} test files")
        return test_files
    
    def cleanup_test_files(self):
        """Clean up test files."""
        logger.info("Cleaning up test files...")
        for file_path in self.test_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    def mock_extraction_function(self, filepath: str) -> Dict[str, Any]:
        """Mock extraction function that simulates processing time."""
        import random
        
        # Simulate different processing times based on file type
        if filepath.endswith('.jpg'):
            processing_time = random.uniform(0.1, 0.3)
        elif filepath.endswith('.pdf'):
            processing_time = random.uniform(0.2, 0.5)
        elif filepath.endswith('.mp4'):
            processing_time = random.uniform(0.3, 0.8)
        else:
            processing_time = random.uniform(0.1, 0.5)
        
        # Simulate processing
        time.sleep(processing_time)
        
        # Return mock metadata
        return {
            "file_path": filepath,
            "file_size": os.path.getsize(filepath) if os.path.exists(filepath) else 1024,
            "processing_time": processing_time,
            "extracted_fields": random.randint(10, 50),
            "file_type": filepath.split('.')[-1],
            "success": True
        }
    
    async def test_old_parallel_system(self, file_paths: List[str]) -> Dict[str, Any]:
        """Test the old threading-based parallel system."""
        logger.info("Testing old parallel system...")
        
        start_time = time.time()
        
        try:
            # Use the old parallel extraction system
            extractor = create_parallel_extractor(
                self.mock_extraction_function,
                max_workers=4
            )
            
            results, metrics = await extractor.extract_parallel(file_paths)
            
            total_time = time.time() - start_time
            
            return {
                "system": "old_parallel",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "throughput_files_per_sec": len(file_paths) / total_time if total_time > 0 else 0,
                "successful_extractions": len([r for r in results if r.success]),
                "failed_extractions": len([r for r in results if not r.success]),
                "avg_processing_time": sum(r.processing_time for r in results) / len(results) if results else 0,
                "results": results,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Old parallel system test failed: {e}")
            total_time = time.time() - start_time
            
            return {
                "system": "old_parallel",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "error": str(e)
            }
    
    async def test_new_async_system(self, file_paths: List[str]) -> Dict[str, Any]:
        """Test the new async-based parallel system."""
        logger.info("Testing new async parallel system...")
        
        start_time = time.time()
        
        try:
            # Use the new async parallel extraction system
            results, metrics = await extract_files_async_parallel(
                file_paths,
                self.mock_extraction_function,
                max_concurrent_tasks=10
            )
            
            total_time = time.time() - start_time
            
            return {
                "system": "new_async",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "throughput_files_per_sec": len(file_paths) / total_time if total_time > 0 else 0,
                "successful_extractions": len([r for r in results if r.success]),
                "failed_extractions": len([r for r in results if not r.success]),
                "avg_processing_time": sum(r.processing_time for r in results) / len(results) if results else 0,
                "results": results,
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"New async system test failed: {e}")
            total_time = time.time() - start_time
            
            return {
                "system": "new_async",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "error": str(e)
            }
    
    async def test_old_batch_system(self, file_paths: List[str]) -> Dict[str, Any]:
        """Test the old batch processing system."""
        logger.info("Testing old batch system...")
        
        start_time = time.time()
        
        try:
            # Use the old batch processing system
            results = process_batch_optimized(
                file_paths,
                self.mock_extraction_function
            )
            
            total_time = time.time() - start_time
            
            return {
                "system": "old_batch",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "throughput_files_per_sec": len(file_paths) / total_time if total_time > 0 else 0,
                "successful_extractions": results.get("successful_count", 0),
                "failed_extractions": results.get("failed_count", 0),
                "optimization_plan": results.get("optimization_plan", {}),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Old batch system test failed: {e}")
            total_time = time.time() - start_time
            
            return {
                "system": "old_batch",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "error": str(e)
            }
    
    async def test_new_batch_system(self, file_paths: List[str]) -> Dict[str, Any]:
        """Test the new async batch processing system."""
        logger.info("Testing new async batch system...")
        
        start_time = time.time()
        
        try:
            # Use the new async batch processing system
            results = await process_batch_optimized_async(
                file_paths,
                self.mock_extraction_function,
                enable_caching=False  # Disable caching for fair comparison
            )
            
            total_time = time.time() - start_time
            
            return {
                "system": "new_async_batch",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "throughput_files_per_sec": len(file_paths) / total_time if total_time > 0 else 0,
                "successful_extractions": results.get("successful_count", 0),
                "failed_extractions": results.get("failed_count", 0),
                "cache_hits": results.get("cache_hits", 0),
                "optimization_plan": results.get("optimization_plan", {}),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"New batch system test failed: {e}")
            total_time = time.time() - start_time
            
            return {
                "system": "new_async_batch",
                "total_files": len(file_paths),
                "processing_time": total_time,
                "error": str(e)
            }
    
    def calculate_improvements(self, old_results: Dict[str, Any], new_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance improvements."""
        improvements = {}
        
        if "processing_time" in old_results and "processing_time" in new_results:
            old_time = old_results["processing_time"]
            new_time = new_results["processing_time"]
            
            if old_time > 0 and new_time > 0:
                speedup = old_time / new_time
                time_reduction = ((old_time - new_time) / old_time) * 100
                
                improvements["speedup"] = speedup
                improvements["time_reduction_percent"] = time_reduction
                improvements["old_processing_time"] = old_time
                improvements["new_processing_time"] = new_time
        
        if "throughput_files_per_sec" in old_results and "throughput_files_per_sec" in new_results:
            old_throughput = old_results["throughput_files_per_sec"]
            new_throughput = new_results["throughput_files_per_sec"]
            
            if old_throughput > 0:
                throughput_improvement = (new_throughput - old_throughput) / old_throughput * 100
                improvements["throughput_improvement_percent"] = throughput_improvement
                improvements["old_throughput"] = old_throughput
                improvements["new_throughput"] = new_throughput
        
        return improvements
    
    async def run_comprehensive_test(self, file_count: int = 50) -> Dict[str, Any]:
        """Run comprehensive performance comparison test."""
        logger.info(f"Starting comprehensive performance test with {file_count} files...")
        
        # Create test files
        test_files = self.create_test_files(file_count)
        
        try:
            # Test old systems
            logger.info("Testing old systems...")
            old_parallel_results = await self.test_old_parallel_system(test_files)
            old_batch_results = await self.test_old_batch_system(test_files)
            
            # Test new systems
            logger.info("Testing new systems...")
            new_async_results = await self.test_new_async_system(test_files)
            new_batch_results = await self.test_new_batch_system(test_files)
            
            # Calculate improvements
            parallel_improvements = self.calculate_improvements(old_parallel_results, new_async_results)
            batch_improvements = self.calculate_improvements(old_batch_results, new_batch_results)
            
            # Compile results
            test_results = {
                "test_config": {
                    "file_count": file_count,
                    "test_files": test_files[:5]  # Sample of test files
                },
                "old_systems": {
                    "parallel": old_parallel_results,
                    "batch": old_batch_results
                },
                "new_systems": {
                    "async_parallel": new_async_results,
                    "async_batch": new_batch_results
                },
                "improvements": {
                    "parallel_processing": parallel_improvements,
                    "batch_processing": batch_improvements
                },
                "summary": {
                    "parallel_speedup": parallel_improvements.get("speedup", 1.0),
                    "batch_speedup": batch_improvements.get("speedup", 1.0),
                    "parallel_throughput_improvement": parallel_improvements.get("throughput_improvement_percent", 0),
                    "batch_throughput_improvement": batch_improvements.get("throughput_improvement_percent", 0)
                }
            }
            
            self.results = test_results
            
            # Save results
            results_path = Path("performance_test_results.json")
            with open(results_path, 'w') as f:
                json.dump(test_results, f, indent=2, default=str)
            
            logger.info(f"Performance test completed! Results saved to: {results_path}")
            
            return test_results
            
        finally:
            self.cleanup_test_files()
    
    def print_summary(self):
        """Print performance test summary."""
        if not self.results:
            print("No test results available")
            return
        
        print("\n" + "="*80)
        print("PERFORMANCE IMPROVEMENT TEST SUMMARY")
        print("="*80)
        
        # Parallel processing improvements
        parallel_improvements = self.results["improvements"]["parallel_processing"]
        if parallel_improvements:
            print(f"\nParallel Processing Improvements:")
            print(f"  Speedup: {parallel_improvements.get('speedup', 1):.2f}x")
            print(f"  Time reduction: {parallel_improvements.get('time_reduction_percent', 0):.1f}%")
            print(f"  Throughput improvement: {parallel_improvements.get('throughput_improvement_percent', 0):.1f}%")
            print(f"  Old time: {parallel_improvements.get('old_processing_time', 0):.2f}s")
            print(f"  New time: {parallel_improvements.get('new_processing_time', 0):.2f}s")
        
        # Batch processing improvements
        batch_improvements = self.results["improvements"]["batch_processing"]
        if batch_improvements:
            print(f"\nBatch Processing Improvements:")
            print(f"  Speedup: {batch_improvements.get('speedup', 1):.2f}x")
            print(f"  Time reduction: {batch_improvements.get('time_reduction_percent', 0):.1f}%")
            print(f"  Throughput improvement: {batch_improvements.get('throughput_improvement_percent', 0):.1f}%")
            print(f"  Old time: {batch_improvements.get('old_processing_time', 0):.2f}s")
            print(f"  New time: {batch_improvements.get('new_processing_time', 0):.2f}s")
        
        print(f"\nTarget Performance Improvements:")
        print(f"  Parallel processing: 2-4x speedup")
        print(f"  Batch processing: 3x speedup")
        print(f"  Memory usage: 50% reduction")
        print(f"  Module success rate: >95%")
        
        print(f"\nActual Performance Achieved:")
        actual_parallel_speedup = parallel_improvements.get('speedup', 1)
        actual_batch_speedup = batch_improvements.get('speedup', 1)
        
        print(f"  Parallel processing: {actual_parallel_speedup:.2f}x speedup")
        print(f"  Batch processing: {actual_batch_speedup:.2f}x speedup")
        
        # Check if targets were met
        if actual_parallel_speedup >= 2.0:
            print("  ✅ Parallel processing target met (≥2x speedup)")
        else:
            print("  ❌ Parallel processing target not met (<2x speedup)")
        
        if actual_batch_speedup >= 3.0:
            print("  ✅ Batch processing target met (≥3x speedup)")
        else:
            print("  ❌ Batch processing target not met (<3x speedup)")
        
        print("\n" + "="*80)


async def main():
    """Main function to run the performance comparison test."""
    logger.info("Starting performance improvement test...")
    
    # Create test instance
    test = PerformanceComparisonTest()
    
    try:
        # Run comprehensive test
        results = await test.run_comprehensive_test(file_count=50)
        
        # Print summary
        test.print_summary()
        
        logger.info("Performance improvement test completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
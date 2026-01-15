#!/usr/bin/env python3
"""
Tests for tools/benchmark_suite.py fixes

Verifies:
- F1: Empty success list handling (already handled by existing code)
- F2: Throughput calculation edge cases
- F3: Memory efficiency calculation with NaN for zero file sizes
- F5: Output path validation for path traversal prevention
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from tools.benchmark_suite import (
    MetaExtractBenchmark,
    BenchmarkResults,
    ExtractionBenchmark,
    MemoryProfiler,
    BenchmarkSuite,
)


class TestEmptySuccessListHandling:
    """Tests for F1: Empty success list handling"""

    def test_aggregate_with_all_failures_returns_none(self):
        """Verify that _aggregate_results returns None when all extractions fail"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = []

        result = benchmarker._aggregate_results('test', 1.0)

        assert result is None

    def test_aggregate_with_mixed_results_handles_correctly(self):
        """Verify aggregation works when some extractions succeed"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = [
            ExtractionBenchmark(
                filepath='/test/file1.jpg',
                filename='file1.jpg',
                file_size_mb=1.0,
                file_type='.jpg',
                extraction_time_ms=100.0,
                initial_memory_mb=50.0,
                peak_memory_mb=75.0,
                final_memory_mb=60.0,
                memory_delta_mb=10.0,
                success=True,
                extracted_fields=100
            ),
            ExtractionBenchmark(
                filepath='/test/file2.jpg',
                filename='file2.jpg',
                file_size_mb=1.0,
                file_type='.jpg',
                extraction_time_ms=0,
                initial_memory_mb=0,
                peak_memory_mb=0,
                final_memory_mb=0,
                memory_delta_mb=0,
                success=False,
                error_message="File not found"
            ),
        ]

        result = benchmarker._aggregate_results('test', 1.0)

        assert result is not None
        assert result.files_processed == 2
        assert result.files_successful == 1
        assert result.files_failed == 1
        assert result.success_rate == 0.5


class TestThroughputCalculation:
    """Tests for F2: Throughput calculation edge cases"""

    def test_throughput_with_zero_time_returns_inf(self):
        """Verify throughput returns infinity for zero elapsed time"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = [
            ExtractionBenchmark(
                filepath='/test/file.jpg',
                filename='file.jpg',
                file_size_mb=1.0,
                file_type='.jpg',
                extraction_time_ms=100.0,
                initial_memory_mb=50.0,
                peak_memory_mb=75.0,
                final_memory_mb=60.0,
                memory_delta_mb=10.0,
                success=True,
                extracted_fields=100
            ),
        ]

        result = benchmarker._aggregate_results('test', 0.0)

        assert result is not None
        import math
        assert math.isinf(result.throughput_files_per_minute)
        assert result.throughput_files_per_minute > 0

    def test_throughput_with_negative_time_handled(self):
        """Verify throughput handles negative time gracefully"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = [
            ExtractionBenchmark(
                filepath='/test/file.jpg',
                filename='file.jpg',
                file_size_mb=1.0,
                file_type='.jpg',
                extraction_time_ms=100.0,
                initial_memory_mb=50.0,
                peak_memory_mb=75.0,
                final_memory_mb=60.0,
                memory_delta_mb=10.0,
                success=True,
                extracted_fields=100
            ),
        ]

        result = benchmarker._aggregate_results('test', -1.0)

        assert result is not None
        import math
        assert math.isinf(result.throughput_files_per_minute)


class TestMemoryEfficiencyCalculation:
    """Tests for F3: Memory efficiency calculation with NaN for zero file sizes"""

    def test_memory_efficiency_with_zero_file_size_returns_nan(self):
        """Verify memory efficiency returns NaN when average file size is zero"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = [
            ExtractionBenchmark(
                filepath='/test/file.jpg',
                filename='file.jpg',
                file_size_mb=0.0,  # Zero-size file
                file_type='.jpg',
                extraction_time_ms=100.0,
                initial_memory_mb=50.0,
                peak_memory_mb=75.0,
                final_memory_mb=60.0,
                memory_delta_mb=10.0,
                success=True,
                extracted_fields=100
            ),
        ]

        result = benchmarker._aggregate_results('test', 1.0)

        assert result is not None
        import math
        assert math.isnan(result.memory_efficiency)

    def test_memory_efficiency_with_normal_files_returns_number(self):
        """Verify memory efficiency returns valid number for normal files"""
        benchmarker = MetaExtractBenchmark()
        benchmarker.results = [
            ExtractionBenchmark(
                filepath='/test/file.jpg',
                filename='file.jpg',
                file_size_mb=100.0,
                file_type='.jpg',
                extraction_time_ms=100.0,
                initial_memory_mb=50.0,
                peak_memory_mb=75.0,
                final_memory_mb=60.0,
                memory_delta_mb=10.0,
                success=True,
                extracted_fields=100
            ),
        ]

        result = benchmarker._aggregate_results('test', 1.0)

        assert result is not None
        import math
        assert not math.isnan(result.memory_efficiency)
        assert result.memory_efficiency == 75.0  # 75MB peak / 100MB file * 100 = 75%


class TestOutputPathValidation:
    """Tests for F5: Output path validation for path traversal prevention"""

    def test_path_traversal_attempt_raises_error(self):
        """Verify path traversal attempts are rejected"""
        benchmarker = MetaExtractBenchmark()
        mock_results = Mock(spec=BenchmarkResults)
        mock_results.suite_name = 'test'
        mock_results.timestamp = '2024-01-01T00:00:00'
        mock_results.files_processed = 1
        mock_results.files_successful = 1
        mock_results.files_failed = 0
        mock_results.total_time_seconds = 1.0
        mock_results.avg_extraction_time_ms = 100.0
        mock_results.min_extraction_time_ms = 100.0
        mock_results.max_extraction_time_ms = 100.0
        mock_results.throughput_files_per_minute = 60.0
        mock_results.avg_peak_memory_mb = 75.0
        mock_results.max_peak_memory_mb = 75.0
        mock_results.memory_efficiency = 75.0
        mock_results.success_rate = 1.0
        mock_results.failure_breakdown = {}
        mock_results.individual_results = []

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Attempt path traversal
                malicious_path = '../../../tmp/malicious.json'

                with pytest.raises(ValueError, match="Invalid output path"):
                    benchmarker.save_results(mock_results, malicious_path)
            finally:
                os.chdir(original_cwd)

    def test_valid_relative_path_allowed(self):
        """Verify valid relative paths are allowed"""
        benchmarker = MetaExtractBenchmark()
        mock_results = Mock(spec=BenchmarkResults)
        mock_results.suite_name = 'test'
        mock_results.timestamp = '2024-01-01T00:00:00'
        mock_results.files_processed = 1
        mock_results.files_successful = 1
        mock_results.files_failed = 0
        mock_results.total_time_seconds = 1.0
        mock_results.avg_extraction_time_ms = 100.0
        mock_results.min_extraction_time_ms = 100.0
        mock_results.max_extraction_time_ms = 100.0
        mock_results.throughput_files_per_minute = 60.0
        mock_results.avg_peak_memory_mb = 75.0
        mock_results.max_peak_memory_mb = 75.0
        mock_results.memory_efficiency = 75.0
        mock_results.success_rate = 1.0
        mock_results.failure_breakdown = {}
        mock_results.individual_results = []

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Create the results subdirectory
                os.makedirs('results', exist_ok=True)

                # Valid relative path should work
                result = benchmarker.save_results(mock_results, 'results/output.json')

                assert result is not None
                assert (Path(tmpdir) / 'results/output.json').exists()
            finally:
                os.chdir(original_cwd)


class TestMemoryProfiler:
    """Tests for MemoryProfiler class"""

    def test_memory_profiler_start_stop(self):
        """Verify MemoryProfiler can start and stop without errors"""
        profiler = MemoryProfiler()

        # Should not raise
        profiler.start()
        profiler.take_snapshot()  # Take at least one snapshot
        stats = profiler.stop()

        assert 'initial_memory_mb' in stats
        assert 'final_memory_mb' in stats
        assert 'peak_memory_mb' in stats

    def test_memory_snapshot_capture(self):
        """Verify memory snapshots can be captured"""
        profiler = MemoryProfiler()
        profiler.start()

        # Take a snapshot
        profiler.take_snapshot()

        assert len(profiler.snapshots) == 1
        assert profiler.snapshots[0].rss_mb >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

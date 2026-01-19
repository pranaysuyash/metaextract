#!/usr/bin/env python3
"""
MetaExtract Comprehensive Benchmark Suite
==========================================

This script benchmarks extraction using REAL files from the codebase:
- Real phone photos with GPS/EXIF
- Real DICOM medical images  
- Real FITS scientific data
- Synthetic files with embedded metadata

Usage:
    python benchmarks/run_comprehensive_benchmark.py --iterations 3
"""

import json
import time
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXIFTOOL_PATH = "/opt/homebrew/bin/exiftool"

OUTPUT_DIR = Path("benchmarks/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CREDIT_SCHEDULE = {
    'base': 1,
    'embedding': 3,
    'ocr': 5,
    'forensics': 4,
}

MP_BUCKETS = [
    {'label': 'standard', 'maxMp': 12, 'credits': 0},
    {'label': 'large', 'maxMp': 24, 'credits': 1},
    {'label': 'xl', 'maxMp': 48, 'credits': 3},
    {'label': 'xxl', 'maxMp': 96, 'credits': 7},
]

BENCHMARK_FILES = {
    'real_phone_with_gps': [
        'tests/fixtures/test_image.jpg',  # 100 tags, GPS, ICC
        'tests/persona-files/sarah-phone-photos/IMG_20251225_164634.jpg',  # 84 tags, ExifIFD
        'tests/persona-files/sarah-phone-photos/gps-map-photo.jpg',  # GPS data
    ],
    'real_dicom_medical': [
        'test-data/CT_small.dcm',  # 267 tags, medical imaging
        'test-data/MR_small.dcm',  # MRI scan
    ],
    'real_fits_scientific': [
        'test-data/wcs_astronomy.fits',  # 28 tags, astronomy
        'test-data/primary_3d.fits',  # 25MB, large dataset
    ],
    'large_images': [
        'test-data/png_standard.png',  # 3 MP
        'test-data/png_xl.png',  # 12 MP
        'test-data/large_xl.jpg',  # 48 MP
        'test-data/large_xxl.jpg',  # 96 MP
    ],
    'raw_simulation': [
        'test-data/raw_simulation.jpg',  # 110 tags, extensive metadata
    ],
    'standard_synthetic': [
        'test-data/test_jpg.jpg',
        'test-data/test_png.png',
        'test-data/test_webp.webp',
    ],
    'professional_synthetic': [
        'test-data/test_tiff.tiff',
        'test-data/test_dng.dng',
        'test-data/test_minimal.psd',
    ],
}


def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(filepath) if os.path.exists(filepath) else 0


def extract_with_exiftool(filepath: str) -> Dict[str, Any]:
    """Extract metadata using ExifTool."""
    if not os.path.exists(EXIFTOOL_PATH):
        return {'error': 'ExifTool not available'}
    
    cmd = [EXIFTOOL_PATH, '-j', '-a', '-G1', '-s', filepath]
    
    start = time.perf_counter()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        elapsed = time.perf_counter() - start
        
        if result.returncode != 0:
            return {'error': result.stderr, 'elapsed_ms': round(elapsed * 1000, 2)}
        
        output = result.stdout.strip()
        if output:
            data = json.loads(output)
            raw_data = data[0] if data else {}
            
            categories = {}
            for k in raw_data.keys():
                if ':' in k:
                    g = k.split(':')[0]
                elif not k.startswith('ExifTool') and not k.startswith('SourceFile'):
                    g = 'File'
                else:
                    g = 'System'
                categories[g] = categories.get(g, 0) + 1
            
            return {
                'data': raw_data,
                'elapsed_ms': round(elapsed * 1000, 2),
                'total_tags': len(raw_data),
                'categories': categories,
            }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {'error': str(e), 'elapsed_ms': round(elapsed * 1000, 2)}
    
    return {'error': 'No output', 'elapsed_ms': 0}


def calculate_mp_credits(filepath: str) -> Dict[str, Any]:
    """Calculate MP bucket and credits for a file."""
    size = get_file_size(filepath)
    mb = size / (1024 * 1024)
    
    if mb <= 10:
        bucket = 'standard'
        credits = 0
    elif mb <= 25:
        bucket = 'large'
        credits = 1
    elif mb <= 50:
        bucket = 'xl'
        credits = 3
    else:
        bucket = 'xxl'
        credits = 7
    
    return {
        'size_mb': round(mb, 3),
        'bucket': bucket,
        'credits': credits,
    }


def benchmark_file(filepath: str, iterations: int = 3) -> Dict[str, Any]:
    """Run benchmark on a single file."""
    if not os.path.exists(filepath):
        return {'error': f'File not found: {filepath}'}
    
    file_ext = Path(filepath).suffix.lower()
    file_size = get_file_size(filepath)
    
    times = []
    tag_counts = []
    
    for _ in range(iterations):
        result = extract_with_exiftool(filepath)
        if 'elapsed_ms' in result:
            times.append(result['elapsed_ms'])
        if 'total_tags' in result:
            tag_counts.append(result['total_tags'])
    
    avg_time = sum(times) / len(times) if times else 0
    avg_tags = sum(tag_counts) / len(tag_counts) if tag_counts else 0
    
    full_result = extract_with_exiftool(filepath)
    mp_info = calculate_mp_credits(filepath)
    
    credits_total = 1 + mp_info['credits']  # base + MP bucket
    
    return {
        'filepath': filepath,
        'file_ext': file_ext,
        'file_size_bytes': file_size,
        'file_size_mb': mp_info['size_mb'],
        'mp_bucket': mp_info['bucket'],
        'iterations': iterations,
        'avg_time_ms': round(avg_time, 2),
        'min_time_ms': round(min(times), 2) if times else 0,
        'max_time_ms': round(max(times), 2) if times else 0,
        'avg_tags': round(avg_tags, 1),
        'total_tags': tag_counts[0] if tag_counts else 0,
        'categories': full_result.get('categories', {}),
        'credits_base': 1,
        'credits_mp': mp_info['credits'],
        'credits_total': credits_total,
    }


def run_benchmarks(iterations: int = 3) -> Dict[str, Any]:
    """Run comprehensive benchmarks."""
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'exiftool_available': os.path.exists(EXIFTOOL_PATH),
        'iterations': iterations,
        'files': [],
        'by_category': {},
        'summary': {},
    }
    
    for category, files in BENCHMARK_FILES.items():
        logger.info(f"Benchmarking category: {category}")
        category_results = []
        
        for filepath in files:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                continue
                
            logger.info(f"  {filepath}")
            result = benchmark_file(filepath, iterations)
            result['category'] = category
            results['files'].append(result)
            category_results.append(result)
        
        if category_results:
            cat_times = [f['avg_time_ms'] for f in category_results if 'avg_time_ms' in f]
            cat_tags = [f['avg_tags'] for f in category_results if 'avg_tags' in f]
            results['by_category'][category] = {
                'count': len(category_results),
                'avg_time_ms': round(sum(cat_times) / len(cat_times), 2) if cat_times else 0,
                'avg_tags': round(sum(cat_tags) / len(cat_tags), 1) if cat_tags else 0,
                'files': [f['filepath'] for f in category_results],
            }
    
    if results['files']:
        times = [f['avg_time_ms'] for f in results['files'] if 'avg_time_ms' in f]
        tags = [f['avg_tags'] for f in results['files'] if 'avg_tags' in f]
        credits = [f['credits_total'] for f in results['files']]
        sizes = [f['file_size_bytes'] for f in results['files']]
        
        results['summary'] = {
            'total_files': len(results['files']),
            'categories_tested': len(results['by_category']),
            'avg_time_ms': round(sum(times) / len(times), 2) if times else 0,
            'min_time_ms': min(times) if times else 0,
            'max_time_ms': max(times) if times else 0,
            'avg_tags': round(sum(tags) / len(tags), 1) if tags else 0,
            'total_tags': round(sum(tags), 1),
            'total_credits': sum(credits),
            'avg_credits': round(sum(credits) / len(credits), 2),
            'total_size_bytes': sum(sizes),
            'total_size_mb': round(sum(sizes) / (1024 * 1024), 2),
        }
    
    return results


def generate_report(results: Dict) -> str:
    """Generate comprehensive markdown report."""
    md = []
    md.append("# MetaExtract Comprehensive Benchmark Report\n")
    md.append(f"**Generated:** {results['timestamp']}\n")
    md.append(f"**ExifTool Available:** {results['exiftool_available']}\n")
    md.append(f"**Iterations per file:** {results['iterations']}\n")
    
    md.append("\n## Executive Summary\n")
    md.append(f"- **Total Files Tested:** {results['summary'].get('total_files', 0)}\n")
    md.append(f"- **Categories Covered:** {results['summary'].get('categories_tested', 0)}\n")
    md.append(f"- **Average Time:** {results['summary'].get('avg_time_ms', 0)}ms\n")
    md.append(f"- **Average Tags per File:** {results['summary'].get('avg_tags', 0)}\n")
    md.append(f"- **Total Tags Extracted:** {results['summary'].get('total_tags', 0)}\n")
    md.append(f"- **Total Size:** {results['summary'].get('total_size_mb', 0)}MB\n")
    
    md.append("\n## By Category\n")
    md.append("| Category | Files | Avg Time | Avg Tags | Sample Files |\n")
    md.append("|----------|-------|----------|----------|--------------|\n")
    for category, data in results.get('by_category', {}).items():
        md.append(f"| {category} | {data['count']} | {data['avg_time_ms']}ms | {data['avg_tags']} | {len(data['files'])} files |\n")
    
    md.append("\n## File Details\n")
    md.append("| File | Ext | Size | MP Bucket | Time | Tags | Credits |\n")
    md.append("|------|-----|------|-----------|------|------|---------|\n")
    
    for f in sorted(results['files'], key=lambda x: x.get('avg_tags', 0), reverse=True):
        name = Path(f['filepath']).name[:40]
        md.append(f"| {name} | {f['file_ext']} | {f['file_size_mb']}MB | {f['mp_bucket']} | "
                 f"{f['avg_time_ms']}ms | {f['avg_tags']} | {f['credits_total']} |\n")
    
    md.append("\n## Tag Categories (All Files Combined)\n")
    all_categories = {}
    for f in results['files']:
        for cat, count in f.get('categories', {}).items():
            all_categories[cat] = all_categories.get(cat, 0) + count
    
    md.append("| Category | Total Tags |\n")
    md.append("|----------|------------|\n")
    for cat, count in sorted(all_categories.items(), key=lambda x: -x[1]):
        md.append(f"| {cat} | {count} |\n")
    
    md.append("\n## Credit Breakdown\n")
    md.append("| Feature | Credit Cost |\n")
    md.append("|---------|-------------|\n")
    for feature, cost in CREDIT_SCHEDULE.items():
        md.append(f"| {feature} | {cost} |\n")
    
    md.append("\n## MP Bucket Pricing\n")
    md.append("| Bucket | Size Limit | Credits |\n")
    md.append("|--------|------------|---------|\n")
    for bucket in MP_BUCKETS:
        md.append(f"| {bucket['label']} | {bucket['maxMp']} MP | {bucket['credits']} |\n")
    
    md.append("\n## Files Used\n")
    for category, files in BENCHMARK_FILES.items():
        md.append(f"\n### {category}\n")
        for f in files:
            exists = "✓" if os.path.exists(f) else "✗"
            md.append(f"- {f} {exists}\n")
    
    return '\n'.join(md)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='MetaExtract Comprehensive Benchmark')
    parser.add_argument('--iterations', type=int, default=3, help='Iterations per file')
    parser.add_argument('--json-only', action='store_true', help='JSON output only')
    args = parser.parse_args()
    
    logger.info(f"Starting comprehensive benchmarks (iterations={args.iterations})...")
    
    results = run_benchmarks(args.iterations)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    json_path = OUTPUT_DIR / f'comprehensive_benchmark_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"JSON report: {json_path}")
    
    if not args.json_only:
        md_path = OUTPUT_DIR / f'comprehensive_benchmark_{timestamp}.md'
        with open(md_path, 'w') as f:
            f.write(generate_report(results))
        logger.info(f"Markdown report: {md_path}")
    
    print("\n" + "="*70)
    print("COMPREHENSIVE BENCHMARK RESULTS")
    print("="*70)
    print(f"Files tested: {results['summary'].get('total_files', 0)}")
    print(f"Categories: {results['summary'].get('categories_tested', 0)}")
    print(f"Avg time: {results['summary'].get('avg_time_ms', 0)}ms")
    print(f"Avg tags: {results['summary'].get('avg_tags', 0)}")
    print(f"Total tags: {results['summary'].get('total_tags', 0)}")
    print(f"Total size: {results['summary'].get('total_size_mb', 0)}MB")
    print("="*70)
    
    return results


if __name__ == '__main__':
    main()

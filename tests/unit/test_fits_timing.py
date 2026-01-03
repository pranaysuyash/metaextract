#!/usr/bin/env python3
import sys
sys.path.insert(0, 'server')
sys.path.insert(0, 'server/extractor')
sys.path.insert(0, 'server/extractor/modules')

from fits_extractor import FITSExtractor
import time

extractor = FITSExtractor()
test_files = [
    'tests/scientific-test-datasets/scientific-test-datasets/fits/hst_observation/hst_observation.fits',
    'tests/scientific-test-datasets/scientific-test-datasets/fits/chandra_observation/chandra_observation.fits',
    'tests/scientific-test-datasets/scientific-test-datasets/fits/sdss_spectrum/sdss_spectrum.fits'
]

print("Testing direct FITS extractor times (10 runs each):")
for f in test_files:
    times = []
    for i in range(10):
        start = time.time()
        result = extractor.extract(f)
        times.append(time.time() - start)
    avg = sum(times) / len(times)
    variation = (max(times) - min(times)) / min(times) * 100 if min(times) > 0 else 0
    print(f'{f.split("/")[-1]:30s}: avg={avg:.4f}s, min={min(times):.4f}s, max={max(times):.4f}s, var={variation:.1f}%')


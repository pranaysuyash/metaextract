# AI-Assisted Photo Culling System Integration Guide

## Overview

The AI-Assisted Photo Culling System automatically selects the best shots based on focus scores, exposure evaluation, and technical quality analysis. This guide shows how to integrate the system into your photography workflow.

## Features

### 🎯 AI-Powered Scoring

- **Focus Analysis**: AF points, sharpness, eye detection
- **Exposure Analysis**: Histogram balance, dynamic range, clipping detection
- **Composition Analysis**: Aspect ratio, face detection, scene recognition
- **Technical Quality**: Resolution, lens quality, camera capabilities
- **Aesthetic Scoring**: Subject distance, focal length, flash usage

### 📊 Smart Grouping

- **Time Sequences**: Groups burst shots and similar-timestamp photos
- **Similar Composition**: Finds visually similar photos
- **Duplicate Detection**: Identifies near-duplicate shots for culling

### ⚡ Performance Optimization

- **Batch Processing**: Handles 1000+ photos efficiently
- **Parallel Analysis**: Multi-core CPU utilization
- **Memory Management**: Streaming for very large sets
- **Caching**: Fast re-analysis of previous batches

## Quick Start

### 1. Server Integration

```python
# Add to your FastAPI app
from server.routes.ai_culling import router

app.include_router(router)
```

### 2. Client Integration

```tsx
import PhotoCullingInterface from '@/components/photo-culling-interface';

function PhotoWorkflow() {
  const [photos, setPhotos] = useState([]);
  const [results, setResults] = useState(null);

  return (
    <PhotoCullingInterface
      photos={photos}
      onCullingComplete={results => setResults(results)}
      onSelectionChange={selected => console.log('Selected:', selected)}
    />
  );
}
```

## API Usage

### Analyze Photos

```javascript
const response = await fetch('/api/ai-culling/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    photos: [
      {
        filename: 'photo1.jpg',
        filepath: '/path/to/photo1.jpg',
        width: 6000,
        height: 4000,
        exif: {
          isospeedratings: 200,
          fnumber: 2.8,
          exposuretime: 0.004,
          focusmode: 'AF-S',
          pointsinfocus: 1,
          facedetected: true,
        },
      },
    ],
    user_preferences: {
      focus_weight: 0.3,
      exposure_weight: 0.25,
      composition_weight: 0.2,
      technical_weight: 0.15,
      aesthetic_weight: 0.1,
    },
  }),
});

const results = await response.json();
```

### Score Single Photo

```javascript
const scoreResponse = await fetch('/api/ai-culling/score-single', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filename: 'photo1.jpg',
    filepath: '/path/to/photo1.jpg',
    width: 6000,
    height: 4000,
    exif: {
      /* EXIF data */
    },
  }),
});

const score = await scoreResponse.json();
console.log(`Overall score: ${score.overall_score}`);
```

## Real-World Examples

### Wedding Photography Workflow

```python
# Wedding photographer preferences
wedding_prefs = {
    'focus_weight': 0.35,      # Emphasize sharp focus
    'exposure_weight': 0.25,
    'composition_weight': 0.20,
    'technical_weight': 0.15,
    'aesthetic_weight': 0.05,
    'prefer_face_detection': True,   # Prioritize people shots
    'prefer_eye_focus': True,        # Eyes must be sharp
    'min_overall_score': 70.0        # High quality threshold
}

# Analyze wedding photos
from modules.ai_culling_engine import analyze_photos_for_culling

results = analyze_photos_for_culling(wedding_photos, wedding_prefs)

# Get recommended keepers
keepers = [
    rec for rec in results['recommendations']
    if rec['action'] == 'keep'
]

print(f"Recommended {len(keepers)} photos from {len(wedding_photos)} total")
```

### Sports Photography Workflow

```python
# Sports photographer preferences
sports_prefs = {
    'focus_weight': 0.40,      # Focus is critical
    'exposure_weight': 0.20,
    'composition_weight': 0.15,
    'technical_weight': 0.20,    # Technical quality important
    'aesthetic_weight': 0.05,
    'prefer_face_detection': False,  # Less important for sports
    'prefer_eye_focus': False,
    'min_overall_score': 65.0       # Action photos can be lower quality
}

# Fast action sequence analysis
from modules.culling_performance import optimize_culling_performance

results = await optimize_culling_performance(
    sports_photos,
    sports_prefs,
    BatchConfig(batch_size=25, use_multiprocessing=True)
)
```

### Landscape Photography Workflow

```python
# Landscape photographer preferences
landscape_prefs = {
    'focus_weight': 0.25,
    'exposure_weight': 0.30,    # Exposure critical for landscapes
    'composition_weight': 0.25,   # Composition is key
    'technical_weight': 0.15,
    'aesthetic_weight': 0.05,
    'prefer_face_detection': False,
    'prefer_eye_focus': False,
    'min_overall_score': 75.0       # High quality standards
}
```

## Performance Optimization

### Large Batch Processing

```python
from modules.culling_performance import (
    BatchConfig,
    CullingOptimizedEngine,
    optimize_culling_performance
)

# Configure for large batch
config = BatchConfig(
    batch_size=100,           # Process 100 photos at once
    max_workers=8,            # Use 8 CPU cores
    use_multiprocessing=True,  # Enable parallel processing
    memory_limit_mb=2048,     # Use up to 2GB RAM
    enable_gpu=False          # GPU not available yet
)

# Process 1000 photos efficiently
results = await optimize_culling_performance(
    large_photo_set,
    user_preferences,
    config
)

print(f"Processed {results['total_photos']} photos in {results['processing_time']:.2f}s")
print(f"Throughput: {results['performance_metrics']['throughput_photos_per_second']:.1f} photos/sec")
```

### Memory-Efficient Processing

```python
# For memory-constrained environments
memory_config = BatchConfig(
    batch_size=20,            # Small batches
    max_workers=2,             # Fewer workers
    memory_limit_mb=512,      # Limit memory usage
    cache_intermediate=True     # Cache intermediate results
)

results = await optimize_culling_performance(
    massive_photo_set,
    user_preferences,
    memory_config
)
```

## User Interface Components

### Score Visualization

```tsx
import PhotoScoreVisualization from '@/components/photo-score-visualization';

<PhotoScoreVisualization
  scores={photoScores}
  recommendations={recommendations}
  compact={false}
  showDetails={true}
  onScoreClick={category => console.log('Category clicked:', category)}
/>;
```

### Culling Interface

```tsx
import PhotoCullingInterface from '@/components/photo-culling-interface';

<PhotoCullingInterface
  photos={photos}
  onCullingComplete={results => {
    console.log('Culling complete:', results);
    // Handle results - show recommendations, enable export
  }}
  onSelectionChange={selectedPhotos => {
    console.log('Selection changed:', selectedPhotos);
    // Update UI for selected photos
  }}
/>;
```

### Score Comparison

```tsx
import { ScoreComparison } from '@/components/photo-score-visualization';

<ScoreComparison
  before={originalScores}
  after={optimizedScores}
  improvements={[
    'Focus improved by 15 points',
    'Exposure balance optimized',
    'Better composition detected',
  ]}
/>;
```

## Configuration

### Scoring Weights

```javascript
const userPreferences = {
  focus_weight: 0.3, // How important focus is
  exposure_weight: 0.25, // How important exposure is
  composition_weight: 0.2, // How important composition is
  technical_weight: 0.15, // How important technical quality is
  aesthetic_weight: 0.1, // How important aesthetics are

  // All weights must sum to 1.0
};
```

### Performance Settings

```javascript
const performanceConfig = {
  batch_size: 50, // Photos per batch
  max_workers: 4, // Parallel workers
  use_multiprocessing: true, // Use multiple processes
  memory_limit_mb: 1024, // Memory limit in MB
  enable_gpu: false, // GPU acceleration (future)
  cache_intermediate: true, // Cache results
};
```

## Testing

### Run Tests

```bash
# Run all culling tests
python -m pytest server/tests/test_ai_culling_system.py -v

# Run performance benchmarks
python -m pytest server/tests/test_ai_culling_system.py::TestPerformanceBenchmarks -v
```

### Test Data

```python
# Create test photo set
def create_test_photos(count=50):
    photos = []
    for i in range(count):
        photos.append({
            'filename': f'test_photo_{i:03d}.jpg',
            'filepath': f'/test/test_photo_{i:03d}.jpg',
            'width': 6000,
            'height': 4000,
            'exif': {
                'isospeedratings': 200 + (i % 8) * 100,
                'fnumber': 2.8 + (i % 5) * 1.2,
                'exposuretime': 0.001 * (i % 10 + 1),
                'focusmode': ['AF-S', 'AF-C', 'Manual'][i % 3],
                'pointsinfocus': (i % 5) + 1,
                'facedetected': i % 3 == 0
            }
        })
    return photos

# Test the system
test_photos = create_test_photos(100)
results = analyze_photos_for_culling(test_photos)
print(f"Test passed: {results['success']}")
```

## Best Practices

### For Wedding Photographers

1. **Prioritize focus and faces**: Set higher focus weight
2. **Enable eye detection**: Critical for portrait quality
3. **Group by time sequences**: Natural burst grouping
4. **Higher quality threshold**: 70+ for professional work

### For Sports Photographers

1. **Focus is paramount**: 40%+ focus weight
2. **Fast processing**: Use multiprocessing for large sets
3. **Lower aesthetic weight**: Action over composition
4. **Include motion blur factors**: Fast shutter preference

### For Landscape Photographers

1. **Emphasize exposure**: 30% exposure weight
2. **Composition matters**: 25% composition weight
3. **Technical quality**: High resolution preference
4. **Manual focus handling**: Landscape often uses manual focus

### Performance Tips

1. **Batch size optimization**: 50-100 photos per batch
2. **Memory management**: Monitor RAM usage
3. **Caching**: Enable for repeated analysis
4. **Background processing**: Use async for large sets

## Troubleshooting

### Common Issues

#### Low Confidence Scores

```python
# Check metadata completeness
if score.confidence < 0.5:
    print("Low confidence - check EXIF data:")
    print(f"Has focus data: {'focusmode' in photo.exif}")
    print(f"Has exposure data: {'fnumber' in photo.exif}")
    print(f"Has face data: {'facedetected' in photo.exif}")
```

#### Slow Processing

```python
# Optimize configuration
config = BatchConfig(
    batch_size=25,        # Reduce batch size
    max_workers=2,        # Fewer workers
    use_multiprocessing=False  # Use threading instead
)
```

#### Memory Issues

```python
# Use streaming processing
from modules.culling_performance import optimize_culling_performance

results = await optimize_culling_performance(
    photos,
    preferences,
    BatchConfig(memory_limit_mb=512)  # Limit memory
)
```

### Performance Monitoring

```python
# Monitor system resources
import psutil

def monitor_resources():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent()

    return {
        'memory_mb': memory_mb,
        'cpu_percent': cpu_percent,
        'threads': process.num_threads()
    }

# Check during processing
before = monitor_resources()
results = analyze_photos_for_culling(photos)
after = monitor_resources()

print(f"Memory used: {after['memory_mb']:.1f}MB")
print(f"CPU usage: {after['cpu_percent']:.1f}%")
```

## Future Enhancements

### Planned Features

1. **GPU Acceleration**: CUDA/OpenCL support
2. **Machine Learning**: Train on user preferences
3. **Advanced Face Detection**: Age/gender/emotion recognition
4. **Style Analysis**: Artistic style classification
5. **Cloud Processing**: API for remote analysis

### Integration Opportunities

1. **Editing Software**: Plugin for Lightroom/Capture One
2. **Camera Apps**: Mobile integration
3. **Cloud Storage**: Direct Dropbox/Google Drive analysis
4. **Social Media**: Auto-culling for uploads
5. **Print Services**: Quality validation for printing

## Support

For support and questions:

- Check the test files for usage examples
- Review the API documentation
- Monitor performance metrics
- Report issues with detailed logs

The AI Culling System is designed to significantly improve photographer workflow by automating the tedious culling process while maintaining professional quality standards.

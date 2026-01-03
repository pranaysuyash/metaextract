# Phase 2 Refactoring Plan - Remaining Extractors

## Summary

**Status**: 🚀 **STARTING** - Phase 2 Remaining Extractors
**Branch**: `phase1-refactoring-critical-issues` (continuing)
**Goal**: Add remaining specialized extractors for complete coverage

## Current Status After Integration

✅ **Phase 1 Completed Successfully:**
- Modular architecture implemented
- Image extractor working (20+ formats, 54 fields detected)
- Registry summary for frontend tier management
- Exception hierarchy standardized
- Frontend enhancements integrated (purpose, density, registry summary)

## Phase 2 Objectives

### 1. **Video Extractor** 🎥
**Target**: Support MP4, AVI, MOV, MKV, WebM, etc.
**Metadata**: Codec info, duration, resolution, frame rate, bitrate, telemetry

### 2. **Audio Extractor** 🎵
**Target**: MP3, WAV, FLAC, AAC, OGG, M4A, etc.
**Metadata**: ID3 tags, codec info, duration, bitrate, album art

### 3. **Document Extractor** 📄
**Target**: PDF, DOCX, XLSX, PPTX, ODT, etc.
**Metadata**: Author, creation date, pages, properties, embedded files

### 4. **Scientific Extractor** 🔬
**Target**: DICOM, FITS, HDF5, NetCDF, GeoTIFF
**Metadata**: Medical imaging, astronomical data, scientific measurements

## Implementation Plan

### Week 1: Video Extractor

#### Day 1-2: Research & Design
- [ ] Analyze current video extraction in `metadata_engine.py`
- [ ] Research ffmpeg-python capabilities
- [ ] Design video extractor class structure
- [ ] Plan supported formats and metadata categories

#### Day 3-4: Implementation
- [ ] Create `VideoExtractor` class in `extractors/video_extractor.py`
- [ ] Implement basic video metadata extraction
- [ ] Add codec-specific metadata parsing
- [ ] Implement video telemetry extraction

#### Day 5: Testing & Integration
- [ ] Add video extractor to orchestrator
- [ ] Test with sample video files
- [ ] Update registry summary for video fields
- [ ] Document video extraction capabilities

### Week 2: Audio Extractor

#### Day 1-2: Research & Design
- [ ] Analyze current audio extraction in `metadata_engine.py`
- [ ] Research mutagen library capabilities
- [ ] Design audio extractor class structure
- [ ] Plan supported formats and metadata categories

#### Day 3-4: Implementation
- [ ] Create `AudioExtractor` class in `extractors/audio_extractor.py`
- [ ] Implement ID3 tag extraction
- [ ] Add codec-specific metadata parsing
- [ ] Implement album art and advanced audio metadata

#### Day 5: Testing & Integration
- [ ] Add audio extractor to orchestrator
- [ ] Test with sample audio files
- [ ] Update registry summary for audio fields
- [ ] Document audio extraction capabilities

### Week 3: Document Extractor

#### Day 1-2: Research & Design
- [ ] Analyze current document extraction in `metadata_engine.py`
- [ ] Research PyPDF2, python-docx capabilities
- [ ] Design document extractor class structure
- [ ] Plan supported formats and metadata categories

#### Day 3-4: Implementation
- [ ] Create `DocumentExtractor` class in `extractors/document_extractor.py`
- [ ] Implement PDF metadata extraction
- [ ] Add Office document metadata extraction
- [ ] Implement document properties and embedded files

#### Day 5: Testing & Integration
- [ ] Add document extractor to orchestrator
- [ ] Test with sample documents
- [ ] Update registry summary for document fields
- [ ] Document document extraction capabilities

### Week 4: Scientific Extractor

#### Day 1-2: Research & Design
- [ ] Analyze current scientific extraction in `metadata_engine.py`
- [ ] Research specialized libraries (pydicom, astropy, h5py)
- [ ] Design scientific extractor class structure
- [ ] Plan supported formats and metadata categories

#### Day 3-4: Implementation
- [ ] Create `ScientificExtractor` class in `extractors/scientific_extractor.py`
- [ ] Implement DICOM medical imaging metadata
- [ ] Add FITS astronomical data extraction
- [ ] Implement HDF5/NetCDF scientific data extraction

#### Day 5: Testing & Integration
- [ ] Add scientific extractor to orchestrator
- [ ] Test with sample scientific files
- [ ] Update registry summary for scientific fields
- [ ] Document scientific extraction capabilities

## Detailed Extractor Specifications

### Video Extractor Specifications

```python
class VideoExtractor(BaseExtractor):
    supported_formats = [
        '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv',
        '.m4v', '.3gp', '.mts', '.m2ts', '.ogv', '.mpg', '.mpeg'
    ]
    
    metadata_categories = {
        'format': 'Container format information',
        'codec': 'Video and audio codec details',
        'stream': 'Individual stream properties',
        'telemetry': 'Drone/action camera telemetry',
        'quality': 'Resolution, frame rate, bitrate',
        'chapter': 'Video chapters and timestamps'
    }
```

### Audio Extractor Specifications

```python
class AudioExtractor(BaseExtractor):
    supported_formats = [
        '.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma',
        '.opus', '.aiff', '.au', '.ra', '.mid', '.midi'
    ]
    
    metadata_categories = {
        'id3': 'ID3v1/v2 tags for MP3',
        'vorbis': 'Vorbis comments for OGG/FLAC',
        'codec': 'Audio codec specifications',
        'album': 'Album and track information',
        'broadcast': 'Broadcast audio metadata',
        'technical': 'Technical audio properties'
    }
```

### Document Extractor Specifications

```python
class DocumentExtractor(BaseExtractor):
    supported_formats = [
        '.pdf', '.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp',
        '.doc', '.xls', '.ppt', '.rtf', '.txt', '.csv'
    ]
    
    metadata_categories = {
        'properties': 'Document properties',
        'author': 'Author and creation info',
        'security': 'Security and permissions',
        'structure': 'Document structure',
        'embedded': 'Embedded files and objects',
        'version': 'Version and compatibility'
    }
```

### Scientific Extractor Specifications

```python
class ScientificExtractor(SpecializedExtractor):
    supported_formats = [
        '.dcm', '.dicom', '.fits', '.fit', '.hdf', '.h5', '.nc',
        '.tif', '.tiff', '.geojson', '.shp', '.kml'
    ]
    
    metadata_categories = {
        'medical': 'DICOM medical imaging',
        'astronomical': 'FITS astronomical data',
        'geospatial': 'GIS and mapping data',
        'scientific': 'Generic scientific data',
        'instrument': 'Instrument-specific data',
        'measurement': 'Measurement and calibration'
    }
```

## Integration Requirements

### 1. Orchestrator Updates
- [ ] Add new extractors to the orchestrator
- [ ] Update extractor selection logic
- [ ] Enhance result aggregation for multiple extractors
- [ ] Update registry summary for all extractor types

### 2. Registry Summary Enhancement
```javascript
registry_summary: {
  image: { exif: 45, iptc: 12, xmp: 8, mobile: 15, perceptual_hashes: 3 },
  video: { format: 8, codec: 15, stream: 25, telemetry: 12 },
  audio: { id3: 32, codec: 18, broadcast: 9 },
  document: { properties: 20, author: 8, security: 12, embedded: 5 },
  scientific: { medical: 125, astronomical: 89, geospatial: 67 }
}
```

### 3. Frontend Compatibility
- [ ] Ensure all metadata formats are properly displayed
- [ ] Update field counting for tier limitations
- [ ] Add new metadata categories to UI
- [ ] Enhance purpose-based filtering for new file types

### 4. Performance Optimization
- [ ] Implement parallel extraction across file types
- [ ] Add caching for frequently extracted files
- [ ] Optimize memory usage for large files
- [ ] Add streaming extraction for huge files

## Testing Strategy

### Unit Tests
- [ ] Test each extractor independently
- [ ] Test extractor selection logic
- [ ] Test registry summary generation
- [ ] Test error handling scenarios

### Integration Tests
- [ ] Test orchestrator with multiple extractors
- [ ] Test frontend compatibility
- [ ] Test tier-based field filtering
- [ ] Test performance under load

### Sample Files Needed
- [ ] Video: MP4, AVI, MOV, MKV with different codecs
- [ ] Audio: MP3, WAV, FLAC, AAC with different tags
- [ ] Documents: PDF, DOCX, XLSX, PPTX with different properties
- [ ] Scientific: DICOM, FITS, HDF5, NetCDF, GeoTIFF

## Success Criteria

### Quantitative Metrics
- [ ] Support for 50+ file formats across all extractors
- [ ] Extract 10,000+ metadata fields total
- [ ] Processing time < 100ms for typical files
- [ ] Memory usage < 100MB for large files
- [ ] 95%+ test coverage for new code

### Qualitative Metrics
- [ ] Seamless integration with existing architecture
- [ ] Consistent API across all extractors
- [ ] Graceful degradation when libraries unavailable
- [ ] Comprehensive error handling and logging
- [ ] Clear documentation and examples

## Risk Mitigation

### Technical Risks
- **Library Dependencies**: Some extractors require specialized libraries
- **Performance**: Large files might cause memory issues
- **Compatibility**: Different file format versions

### Mitigation Strategies
- [ ] Graceful fallback when libraries unavailable
- [ ] Streaming processing for large files
- [ ] Comprehensive format validation
- [ ] Extensive testing with real-world files

## Deliverables

### Code Deliverables
- [ ] 4 new specialized extractors
- [ ] Updated orchestrator
- [ ] Enhanced registry summary
- [ ] Comprehensive test suite
- [ ] Updated documentation

### Documentation Deliverables
- [ ] Extractor development guide
- [ ] API documentation
- [ ] Performance benchmarks
- [ ] Integration examples
- [ ] Troubleshooting guide

## Timeline

- **Week 1**: Video Extractor
- **Week 2**: Audio Extractor  
- **Week 3**: Document Extractor
- **Week 4**: Scientific Extractor + Integration + Testing

**Target Completion**: February 3, 2026

---

**Next Steps**: Begin Video Extractor implementation
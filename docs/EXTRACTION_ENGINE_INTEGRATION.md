# MetaExtract - Python-Node.js Extraction Engine Integration

## Overview

The MetaExtract system uses a hybrid architecture where the frontend and API are built with Node.js/Express, but the core metadata extraction is performed by Python engines. This document details the integration between these components.

## Architecture

```
┌─────────────────┐    HTTP Request     ┌──────────────────┐
│   Frontend      │ ────────────────→   │   Node.js API    │
│   (React)       │                     │   (Express)      │
└─────────────────┘                     └──────────────────┘
                                               │
                                               │ File Upload
                                               ▼
                                      ┌──────────────────┐
                                      │ Python Process   │
                                      │ (metadata_engine)│
                                      └──────────────────┘
                                               │
                                               │ JSON Response
                                               ▼
                                      ┌──────────────────┐
                                      │ Response to      │
                                      │ Frontend         │
                                      └──────────────────┘
```

## Integration Details

### 1. File Upload Flow

1. Frontend uploads file via `POST /api/extract`
2. Express receives file via Multer middleware
3. File is temporarily stored in memory/temp directory
4. Python extraction engine is spawned as subprocess
5. Results are processed and returned as JSON

### 2. Python Engine Communication

The Node.js server communicates with the Python extraction engine using:

- **Subprocess spawning**: Using Node.js `child_process.spawn()`
- **Standard I/O**: Communication via stdout/stderr
- **JSON protocol**: Results formatted as JSON

### 3. Key Components

#### Server Route: `/api/extract`
- Handles file uploads
- Manages temporary files
- Spawns Python extraction process
- Processes and transforms results
- Handles billing/credits

#### Python Engine: `comprehensive_metadata_engine.py`
- Performs actual metadata extraction
- Supports multiple file types
- Implements tier-based feature access
- Returns structured JSON results

## Error Handling

### Current Error Handling Strategy

1. **Process spawning errors**: Caught and returned as HTTP 500
2. **Python execution errors**: Captured from stderr and logged
3. **JSON parsing errors**: Caught and returned as HTTP 500
4. **Timeout errors**: Process killed after 180 seconds
5. **File validation errors**: Returned as HTTP 400/403

### Health Check Endpoint

The system includes a health check endpoint at `GET /api/extract/health` that:
- Tests Python engine availability
- Verifies basic functionality
- Returns status information
- Times out after 10 seconds

## Configuration

### Environment Variables
- `PYTHON_PATH`: Path to Python executable (defaults to `python3`)
- File size limits based on user tier
- Timeout configurations

### Tier-Based Access
- Different metadata fields available based on user subscription tier
- Implemented in both Node.js and Python layers
- Validation occurs in both layers

## Performance Considerations

### File Handling
- Files are temporarily stored in `/tmp/metaextract/`
- Files are automatically cleaned up after processing
- Memory usage is monitored to prevent abuse

### Process Management
- Python processes are spawned per request
- Timeout prevents hanging processes
- Process resources are cleaned up automatically

### Caching (Future Enhancement)
- Currently no caching implemented
- Consider Redis for result caching
- Cache based on file hash to avoid duplicate processing

## Security Considerations

### File Upload Security
- File type validation using MIME types
- File size limits enforced
- Temporary files are securely handled
- No permanent file storage

### Process Security
- Python processes run with minimal privileges
- Input validation on file paths
- Output sanitization for JSON responses

## Logging

### Log Categories
- Process spawn events
- Extraction results
- Error conditions
- Performance metrics
- Security events

### Log Format
- Timestamp
- Process ID
- Request ID (when available)
- Event type
- Relevant metadata

## Troubleshooting

### Common Issues

1. **Python not found**
   - Check if `python3` is in system PATH
   - Verify Python dependencies are installed
   - Check `requirements.txt` for missing packages

2. **Timeout errors**
   - Large files may take longer to process
   - Check system resources (CPU, memory)
   - Consider increasing timeout for large files

3. **Permission errors**
   - Verify write access to `/tmp/metaextract/`
   - Check file permissions for Python scripts
   - Ensure proper user privileges

### Debugging Steps

1. Check Node.js server logs
2. Check Python process stderr output
3. Verify Python dependencies
4. Test Python engine directly from command line
5. Check system resources

## API Endpoints

### Main Extraction
- **Endpoint**: `POST /api/extract`
- **Parameters**: 
  - `file`: Uploaded file (multipart/form-data)
  - `tier`: User tier (optional, defaults to 'enterprise')
- **Response**: JSON with metadata fields
- **Auth**: Required (via session/cookie)

### Batch Extraction
- **Endpoint**: `POST /api/extract/batch`
- **Parameters**:
  - `files`: Multiple uploaded files
  - `tier`: User tier
- **Response**: JSON with results for each file

### Advanced Analysis
- **Endpoint**: `POST /api/extract/advanced`
- **Parameters**:
  - `file`: Uploaded file
  - `tier`: User tier (requires 'forensic' or 'enterprise')
- **Response**: JSON with advanced analysis results

### Health Check
- **Endpoint**: `GET /api/extract/health`
- **Response**: System health status
- **Auth**: Not required

## Future Enhancements

### Planned Improvements
1. **Process pooling**: Reuse Python processes to reduce spawn overhead
2. **Asynchronous processing**: Queue system for large files
3. **Enhanced caching**: Store results to avoid duplicate processing
4. **Better monitoring**: Real-time performance metrics
5. **Resource limits**: CPU/memory usage controls

### Scaling Considerations
- Horizontal scaling with load balancer
- Distributed processing for large workloads
- Database-backed job queue for processing
- CDN for static assets
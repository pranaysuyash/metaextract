# 🛠️ MetaExtract Development Guide

## 🚀 **Quick Start**

### **Automated Setup**
```bash
# Run the deployment script for full setup
./scripts/deploy.sh

# Or manually install dependencies
npm install
pip install -r requirements.txt
```

### **Development Server**
```bash
# Start development server (frontend + backend)
npm run dev

# Or start components separately
npm run dev:client  # Frontend only (port 5000)
npm run dev         # Backend only (API server)
```

### **Production Build**
```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## 📁 **Project Structure**

```
metaextract/
├── client/                     # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── enhanced-upload-zone.tsx
│   │   │   ├── sample-files.tsx
│   │   │   └── onboarding-tutorial.tsx
│   │   ├── pages/             # Page components
│   │   ├── lib/               # Utilities and helpers
│   │   └── hooks/             # Custom React hooks
│   └── public/                # Static assets
├── server/                     # Node.js backend
│   ├── extractor/             # Python metadata engine
│   │   ├── metadata_engine.py           # Original engine
│   │   ├── metadata_engine_enhanced.py  # Enhanced with caching
│   │   └── utils/             # Performance utilities
│   │       ├── cache.py       # Redis caching system
│   │       └── performance.py # Performance monitoring
│   ├── routes.ts              # API routes
│   ├── storage.ts             # Database operations
│   └── payments.ts            # Payment integration
├── shared/                     # Shared TypeScript types
│   ├── schema.ts              # Database schema
│   └── tierConfig.ts          # Pricing tier configuration
├── docs/                       # Documentation
├── scripts/                    # Deployment and utility scripts
└── requirements.txt            # Python dependencies
```

---

## 🔧 **Development Environment Setup**

### **Prerequisites**
- **Node.js 20+** (LTS recommended)
- **Python 3.11+** 
- **PostgreSQL** (or SQLite for development)
- **Redis** (required for caching layer)

### **System Dependencies**
```bash
# macOS
brew install ffmpeg exiftool redis libmagic

# Ubuntu/Debian
sudo apt install ffmpeg libimage-exiftool-perl redis-server libmagic1

# Windows
# Install FFmpeg from https://ffmpeg.org/
# Install ExifTool from https://exiftool.org/
```

### **Environment Variables**
```env
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/metaextract
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
NODE_ENV=development
PORT=5000

# Performance settings
MAX_CONCURRENT_EXTRACTIONS=10
CACHE_TTL_HOURS=24
MAX_FILE_SIZE_MB=1000

# Payment integration (for production)
DODO_PAYMENTS_API_KEY=your_api_key
DODO_WEBHOOK_SECRET=your_webhook_secret
DODO_ENV=test
```

---

## 🏗️ **Architecture Overview**

### **Backend Architecture**
```
API Layer (Express.js)
├── Routes (routes.ts)
├── Middleware (auth, validation, rate limiting)
├── Database Layer (Drizzle ORM + PostgreSQL)
└── Python Metadata Engine
    ├── Core Engine (metadata_engine.py)
    ├── Enhanced Engine (metadata_engine_enhanced.py)
    ├── Caching Layer (utils/cache.py)
    └── Performance Monitoring (utils/performance.py)
```

### **Frontend Architecture**
```
React Application
├── Pages (home, results, checkout)
├── Components
│   ├── UI Components (shadcn/ui)
│   ├── Enhanced Upload Zone
│   ├── Sample Files Gallery
│   └── Onboarding Tutorial
├── State Management (React Query)
└── Styling (TailwindCSS)
```

### **Data Flow**
```
1. File Upload → Frontend validation
2. API Request → Backend tier validation
3. Temp Storage → Memory-only processing
4. Python Engine → Metadata extraction
5. Cache Storage → Redis
6. Response → Filtered by tier
7. Cleanup → Temp files deleted
```

---

## 🧪 **Testing Strategy**

### **Backend Testing**
```bash
# Test Python metadata engine
python3 server/extractor/metadata_engine_enhanced.py sample.jpg --tier premium

# Test API endpoints
curl -X POST http://localhost:5000/api/extract \
  -F "file=@sample.jpg" \
  -F "tier=premium"

# Test batch processing
curl -X POST http://localhost:5000/api/extract/batch \
  -F "files=@sample1.jpg" \
  -F "files=@sample2.jpg" \
  -F "tier=premium"
```

### **Frontend Testing**
```bash
# Run development server
npm run dev

# Test upload functionality
# 1. Navigate to http://localhost:5000
# 2. Upload a sample file
# 3. Verify metadata extraction
# 4. Test tier-based field filtering
```

### **Performance Testing**
```bash
# Test caching performance
python3 -c "
from server.extractor.utils.cache import get_cache_stats
print(get_cache_stats())
"

# Test system resources
python3 -c "
from server.extractor.utils.performance import check_system_resources
print(check_system_resources())
"
```

---

## 📊 **Performance Optimization**

### **Caching Strategy**
```python
# Cache configuration
CACHE_SETTINGS = {
    "ttl_hours": 24,           # Cache expiration
    "max_file_size_mb": 100,   # Don't cache files larger than 100MB
    "redis_timeout": 5,        # Redis connection timeout
    "enable_compression": True  # Compress cached data
}
```

### **Processing Optimization**
```python
# File size-based optimization
def optimize_for_file_size(file_size_bytes):
    if file_size_bytes < 1_000_000:      # < 1MB
        return {"parallel": False, "chunk_size": 64*1024}
    elif file_size_bytes < 50_000_000:   # < 50MB  
        return {"parallel": True, "chunk_size": 1*1024*1024}
    else:                                # >= 50MB
        return {"parallel": True, "chunk_size": 4*1024*1024}
```

### **Memory Management**
```python
# Automatic cleanup
with tempfile.NamedTemporaryFile(delete=True) as tmp:
    # Process file
    metadata = extract_metadata(tmp.name)
    # File automatically deleted when context exits
```

---

## 🔌 **API Reference**

### **Core Endpoints**

#### **Single File Extraction**
```http
POST /api/extract?tier=premium
Content-Type: multipart/form-data

file: <binary data>
```

**Response:**
```json
{
  "filename": "sample.jpg",
  "tier": "premium", 
  "fields_extracted": 1247,
  "processing_ms": 2341,
  "file_integrity": {
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb924..."
  },
  "exif": { /* EXIF data */ },
  "gps": { /* GPS data */ },
  "performance_metrics": { /* Performance data */ }
}
```

#### **Batch Processing**
```http
POST /api/extract/batch?tier=premium
Content-Type: multipart/form-data

files: <binary data>
files: <binary data>
```

**Response:**
```json
{
  "success": true,
  "total_files": 2,
  "successful_files": 2,
  "processing_time_ms": 4523,
  "results": {
    "file1.jpg": { /* metadata */ },
    "file2.jpg": { /* metadata */ }
  }
}
```

#### **Sample Files**
```http
GET /api/samples
```

**Response:**
```json
{
  "samples": [
    {
      "id": "sample_photo",
      "name": "Standard Photo",
      "description": "JPEG with basic EXIF data",
      "tier_required": "free"
    }
  ]
}
```

#### **Performance Monitoring**
```http
GET /api/performance/stats
```

**Response:**
```json
{
  "cache": {
    "available": true,
    "hit_rate": 0.85,
    "used_memory_human": "45.2MB"
  },
  "server": {
    "uptime_seconds": 86400,
    "memory_usage": { /* Node.js memory stats */ }
  }
}
```

---

## 🎨 **Frontend Development**

### **Component Development**
```typescript
// Enhanced Upload Zone usage
import { EnhancedUploadZone } from "@/components/enhanced-upload-zone";

<EnhancedUploadZone
  onResults={(results) => console.log(results)}
  tier="premium"
  maxFiles={10}
/>
```

### **Sample Files Integration**
```typescript
// Sample files component
import { SampleFiles } from "@/components/sample-files";

<SampleFiles
  onSampleSelect={(sampleId) => processSample(sampleId)}
  currentTier="premium"
/>
```

### **Onboarding Tutorial**
```typescript
// Tutorial integration
import { OnboardingTutorial } from "@/components/onboarding-tutorial";

<OnboardingTutorial
  isOpen={showTutorial}
  onClose={() => setShowTutorial(false)}
  onComplete={() => markTutorialComplete()}
  userTier="free"
/>
```

### **Styling Guidelines**
```css
/* Use TailwindCSS classes */
.upload-zone {
  @apply border-2 border-dashed border-muted-foreground/25;
  @apply hover:border-muted-foreground/50 transition-colors;
  @apply rounded-lg p-8 text-center cursor-pointer;
}

/* Dark theme support */
.dark .upload-zone {
  @apply border-white/10 hover:border-white/20;
}
```

---

## 🚀 **Deployment**

### **Development Deployment**
```bash
# Start all services
npm run dev

# Or start individually
npm run dev:client  # Frontend (port 5000)
npm run dev         # Backend API
```

### **Production Deployment**
```bash
# Build application
npm run build

# Start production server
npm start

# Or use PM2 for process management
pm2 start dist/index.cjs --name metaextract
```

### **Docker Deployment**
```dockerfile
# Dockerfile example
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 5000
CMD ["npm", "start"]
```

### **Environment-Specific Configuration**
```bash
# Development
NODE_ENV=development
DATABASE_URL=sqlite:./dev.db
REDIS_HOST=localhost

# Production  
NODE_ENV=production
DATABASE_URL=postgresql://...
REDIS_HOST=redis.production.com
```

---

## 🔍 **Debugging & Troubleshooting**

### **Common Issues**

#### **Python Dependencies**
```bash
# Issue: Python packages not found
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

#### **FFmpeg Not Found**
```bash
# Issue: Video processing fails
# Solution: Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

#### **Redis Connection Failed**
```bash
# Issue: Caching disabled
# Solution: Start Redis server
# macOS: brew services start redis
# Ubuntu: sudo systemctl start redis-server
```

#### **ExifTool Missing**
```bash
# Issue: Limited metadata extraction
# Solution: Install ExifTool
# macOS: brew install exiftool
# Ubuntu: sudo apt install libimage-exiftool-perl
```

### **Debug Logging**
```python
# Enable debug logging in Python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check extraction process
python3 server/extractor/metadata_engine_enhanced.py sample.jpg --tier premium --performance
```

### **Performance Debugging**
```bash
# Check system resources
python3 -c "
from server.extractor.utils.performance import check_system_resources
import json
print(json.dumps(check_system_resources(), indent=2))
"

# Monitor cache performance
curl http://localhost:5000/api/performance/stats | jq
```

---

## 📚 **Additional Resources**

### **Documentation**
- [Implementation Progress](IMPLEMENTATION_PROGRESS.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](README.md)

### **External Dependencies**
- [ExifTool Documentation](https://exiftool.org/TagNames/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Redis Documentation](https://redis.io/documentation)
- [Drizzle ORM](https://orm.drizzle.team/)

### **Development Tools**
- [React Developer Tools](https://react.dev/learn/react-developer-tools)
- [Postman Collection](docs/MetaExtract.postman_collection.json)
- [VS Code Extensions](docs/recommended-extensions.md)

---

## 🤝 **Contributing**

### **Development Workflow**
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request
5. Code review and merge

### **Code Standards**
- **TypeScript**: Strict mode enabled
- **Python**: PEP 8 compliance
- **Testing**: Unit tests for new features
- **Documentation**: Update docs for API changes

### **Commit Guidelines**
```bash
# Format: type(scope): description
feat(api): add batch processing endpoint
fix(cache): resolve Redis connection timeout
docs(readme): update installation instructions
perf(engine): optimize large file processing
```

---

**Happy coding! 🚀**

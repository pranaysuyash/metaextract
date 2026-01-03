# MetaExtract Deployment Guide

This guide provides instructions for deploying MetaExtract in various environments.

## Prerequisites

Before deploying MetaExtract, ensure your system meets the following requirements:

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+), macOS 10.15+, or Windows 10/11 WSL2
- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ RAM (8GB+ recommended for heavy usage)
- **Storage**: 10GB+ available space

### Software Dependencies
- **Node.js**: Version 20.x or higher
- **Python**: Version 3.11 or higher
- **FFmpeg**: For video/audio processing
- **ExifTool**: For comprehensive metadata extraction
- **PostgreSQL**: Version 12+ (for production)
- **Redis**: For caching and session storage

## Quick Setup

### Automated Setup (Recommended)
Run the automated setup script:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

The script will:
- Verify system requirements
- Install missing dependencies
- Install Node.js and Python packages
- Create necessary directories
- Run database migrations
- Build the application

## Production Deployment

### Environment Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET`: Secret for JWT tokens
- `DOOD_API_KEY`: API key for DodoPayments
- `MAX_FILE_SIZE`: Maximum upload size in bytes

### Using Docker (Recommended)

Build and run with Docker Compose:

```bash
# Build the images
docker-compose build

# Start the services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

1. Install dependencies:
```bash
npm install
pip install -r requirements.txt
```

2. Set up the database:
```bash
npm run db:push
```

3. Build the application:
```bash
npm run build
```

4. Start the application:
```bash
npm start
```

## Configuration Options

### Security Levels
MetaExtract supports different security levels:
- `basic`: Minimal security checks
- `standard`: Standard security checks (default)
- `strict`: Enhanced security checks
- `paranoid`: Maximum security checks

Configure using the `SECURITY_LEVEL` environment variable.

### Performance Tuning
Adjust these parameters based on your workload:

- `MAX_WORKERS`: Number of worker threads for processing
- `BATCH_CHUNK_SIZE`: Number of files to process in each batch
- `CACHE_MAX_SIZE`: Maximum number of items in cache
- `CACHE_TTL`: Cache time-to-live in seconds

### Monitoring and Alerting
Configure monitoring parameters:

- `MONITORING_INTERVAL`: Interval for collecting metrics (seconds)
- `ALERT_HIGH_ERROR_THRESHOLD`: Error rate threshold for alerts
- `ALERT_SLOW_PROCESSING_THRESHOLD`: Processing time threshold (ms)
- `ALERT_LOW_THROUGHPUT_THRESHOLD`: Throughput threshold (requests/minute)

## Scaling

### Horizontal Scaling
For high-traffic deployments, consider:
- Load balancing multiple application instances
- Using a managed PostgreSQL instance
- Using a managed Redis instance
- CDN for static assets

### Vertical Scaling
Increase resources for:
- Processing large files
- High-volume batch processing
- Real-time analytics

## Security Best Practices

1. **Environment Variables**: Store sensitive information in environment variables
2. **File Uploads**: Limit file sizes and validate file types
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **SSL/TLS**: Use HTTPS in production
5. **Regular Updates**: Keep dependencies updated

## Monitoring

### Health Checks
The application provides a health check endpoint:
```
GET /api/health
```

### Metrics
Access metrics at:
```
GET /api/monitoring/status
GET /api/monitoring/performance
GET /api/monitoring/errors
```

### Logging
Logs are written to the `logs/` directory. Configure log retention based on your needs.

## Troubleshooting

### Common Issues

#### Dependency Installation
If you encounter issues with Python dependencies:
```bash
# On macOS
brew install libmagic

# On Ubuntu/Debian
sudo apt install libmagic1
```

#### File Permissions
Ensure the application has write permissions to:
- `uploads/` directory
- `temp/` directory
- `logs/` directory

#### Database Connection
Verify database connectivity:
```bash
# Test PostgreSQL connection
pg_isready -h hostname -p port -U username
```

### Performance Issues
- Monitor memory usage during large file processing
- Adjust `MAX_FILE_SIZE` based on available memory
- Consider increasing worker threads for CPU-intensive tasks

## Backup and Recovery

### Database Backup
Regularly backup your PostgreSQL database:
```bash
pg_dump -h hostname -U username database_name > backup.sql
```

### Configuration Backup
Keep copies of:
- Environment configuration files
- SSL certificates
- Custom configuration files

## Updating

To update to a new version:

1. Pull the latest code
2. Run setup script: `./setup.sh`
3. Run database migrations: `npm run db:push`
4. Restart the application

## Support

For deployment issues or questions:
- Check the logs in the `logs/` directory
- Review the application health endpoint
- Consult the monitoring endpoints for performance metrics
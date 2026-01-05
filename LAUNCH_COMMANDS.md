# Images MVP Launch - Command Reference

Quick reference for deployment commands.

---

## Pre-Launch Verification (Do This First)

```bash
# Navigate to project root
cd /Users/pranay/Projects/metaextract

# 1. Format code
npm run format:check

# 2. Run linter
npm run lint

# 3. Run type check
npm run type-check

# 4. Run tests
npm run test:ci

# 5. Verify database migrations exist
ls -la server/migrations/

# 6. Verify init.sql was created
ls -la init.sql

# 7. Check database connection works locally
npm run check:db
```

---

## Build for Production

```bash
# Build client
npm run build:client

# Build server (TypeScript compilation)
npm run build:server

# Or build everything at once
npm run build

# Create Docker image
docker build -t metaextract:latest .
```

---

## Local Development (Testing Before Deploy)

```bash
# Start dev environment (client + server)
npm run dev

# Or run separately:
npm run dev:client      # Terminal 1: http://localhost:5173
npm run dev:server      # Terminal 2: http://localhost:3000

# Run migrations if needed
npm run db:migrate

# Check database status
npm run check:db
```

---

## Docker Deployment (Recommended for Production)

### Start Services

```bash
# Navigate to project
cd /Users/pranay/Projects/metaextract

# Start all services (app, database, redis, nginx, backup)
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f nginx

# Access the app
# http://localhost or http://localhost:3000
```

### Database Setup

```bash
# Wait for DB to be ready (check health)
docker-compose exec db pg_isready -U metaextract -d metaextract

# View database logs
docker-compose logs db

# Run migrations (if not automatic)
docker-compose exec app npm run db:migrate

# Check database schema
docker-compose exec db psql -U metaextract -d metaextract -c "\dt"
```

### Stop Services

```bash
# Stop all services gracefully
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop and remove everything including images
docker-compose down -v --rmi all
```

---

## Backup & Restore

### View Backups

```bash
# List all backups
ls -lah ./backups/

# View backup schedule
docker-compose logs backup
```

### Manual Backup

```bash
# Create manual backup
docker-compose exec db pg_dump -U metaextract metaextract > ./backups/manual-backup-$(date +%Y%m%d-%H%M%S).sql

# Compress backup
gzip ./backups/*.sql
```

### Restore from Backup

```bash
# Restore latest backup
docker-compose exec -T db psql -U metaextract metaextract < ./backups/latest.sql

# Or restore specific backup
docker-compose exec -T db psql -U metaextract metaextract < ./backups/manual-backup-20260106.sql

# Verify restore
docker-compose exec db psql -U metaextract -d metaextract -c "SELECT count(*) FROM users;"
```

---

## Monitoring Setup

### Start Monitoring Stack (Optional)

```bash
# Add to docker-compose.yml first, then:
docker-compose up -d prometheus grafana

# Access Grafana
# http://localhost:3001
# Username: admin
# Password: admin

# Access Prometheus
# http://localhost:9090

# Check targets in Prometheus
curl http://localhost:9090/api/v1/targets
```

---

## Scaling & Load Testing

### Scale Services

```bash
# Increase replicas (if using Kubernetes or Docker Swarm)
docker-compose up -d --scale app=2

# Or rebuild with new env vars
POSTGRES_CONNECTIONS=50 docker-compose up -d db
```

### Load Testing

```bash
# Install Apache Bench
brew install httpd      # macOS
sudo apt install apache2-utils  # Linux

# Run 100 concurrent requests
ab -n 1000 -c 100 http://localhost:3000/api/images_mvp/credits/packs

# Test WebSocket stability
# Use a tool like Artillery or Locust
npm install -g artillery
artillery quick --count 100 --num 10 http://localhost:3000
```

---

## Monitoring & Debugging

### Check API Health

```bash
# Health check endpoint
curl http://localhost:3000/api/health

# Database connection test
curl http://localhost:3000/api/db-status

# WebSocket test
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:3000/api/images_mvp/progress/test-session-id
```

### View Logs

```bash
# Docker logs
docker-compose logs -f app       # App logs
docker-compose logs -f db        # Database logs
docker-compose logs -f redis     # Redis logs
docker-compose logs -f nginx     # Nginx logs
docker-compose logs -f backup    # Backup logs

# View app metrics
curl http://localhost:3000/metrics

# View database queries (if slow query log enabled)
docker-compose exec db psql -U metaextract -d metaextract \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Performance Profiling

```bash
# Check connection pool usage
docker-compose exec app npm run check:db

# View database statistics
docker-compose exec db psql -U metaextract -d metaextract -c "\d+"

# Check index usage
docker-compose exec db psql -U metaextract -d metaextract \
  -c "SELECT * FROM pg_stat_user_indexes;"

# Monitor real-time connections
docker-compose exec db psql -U metaextract -d metaextract \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'metaextract';"
```

---

## Environment Variables

### Required (set in .env)

```bash
# Database
DATABASE_URL=postgresql://metaextract:password@db:5432/metaextract
STORAGE_REQUIRE_DATABASE=true

# Authentication
JWT_SECRET=your-super-secure-random-jwt-secret-here-at-least-32-characters

# Payment
DODO_PAYMENTS_API_KEY=your-dodo-api-key

# Optional
REDIS_URL=redis://redis:6379
NODE_ENV=production
```

### Docker-Specific (in docker-compose.yml)

```yaml
environment:
  - NODE_ENV=production
  - DATABASE_URL=postgresql://metaextract:password@db:5432/metaextract
  - STORAGE_REQUIRE_DATABASE=true
  - JWT_SECRET=${JWT_SECRET}
  - DODO_PAYMENTS_API_KEY=${DODO_PAYMENTS_API_KEY}
```

---

## Troubleshooting

### Database Won't Start

```bash
# Check PostgreSQL logs
docker-compose logs db

# Verify database volume
docker volume ls | grep metaextract

# Remove corrupted volume and restart
docker-compose down -v
docker-compose up -d db
```

### App Won't Connect to Database

```bash
# Test database connection
docker-compose exec app npm run check:db

# Check DATABASE_URL in logs
docker-compose logs app | grep DATABASE_URL

# Verify database is ready
docker-compose exec db pg_isready -U metaextract -d metaextract
```

### WebSocket Errors

```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:3000/api/images_mvp/progress/test

# View app logs for WebSocket errors
docker-compose logs app | grep websocket

# Verify express-ws middleware
grep -r "express-ws" server/
```

### High Memory Usage

```bash
# Check Node.js memory
docker-compose exec app node -e "console.log(require('os').freemem())"

# Check database memory
docker-compose exec db free -h

# Check Redis memory
docker-compose exec redis redis-cli INFO memory
```

---

## Zero-Downtime Deployment

```bash
# 1. Build new image
docker build -t metaextract:new .

# 2. Stop old app container only
docker-compose stop app

# 3. Update image tag in docker-compose.yml
# Change: image: metaextract:latest
# To: image: metaextract:new

# 4. Start new app
docker-compose up -d app

# 5. Verify new version is running
curl http://localhost:3000/api/health

# 6. View logs
docker-compose logs -f app

# 7. If successful, tag new as latest
docker tag metaextract:new metaextract:latest

# 8. If rollback needed, run:
docker-compose stop app
# Change image tag back in docker-compose.yml
docker-compose up -d app
```

---

## Rollback Procedure

```bash
# If something goes wrong, quick rollback:

# Option 1: Revert code
git revert HEAD
npm run build
docker build -t metaextract:latest .

# Option 2: Restore database from backup
docker-compose down
docker-compose up -d db
docker-compose exec -T db psql -U metaextract metaextract < ./backups/latest.sql
docker-compose up -d

# Option 3: Use previous Docker image
docker-compose down
docker tag metaextract:previous metaextract:latest
docker-compose up -d

# Verify system is healthy
curl http://localhost:3000/api/health
npm run check:db
```

---

## Post-Launch Monitoring

### First 24 Hours

```bash
# Check every 15 minutes
docker-compose logs app | tail -50
curl http://localhost:3000/api/health
npm run check:db

# Monitor metrics
curl http://localhost:3000/metrics
```

### Daily Check

```bash
# Database
docker-compose exec db psql -U metaextract -d metaextract \
  -c "SELECT count(*) FROM ui_events WHERE created_at > NOW() - INTERVAL '1 day';"

# Backups
ls -lah ./backups/ | head -5

# Error logs
docker-compose logs app | grep ERROR | wc -l

# Connection pool
docker-compose logs app | grep "Database connection"
```

---

## Quick Reference (TL;DR)

```bash
# Pre-launch
npm run format:check && npm run lint && npm run test:ci && npm run build

# Deploy
docker-compose up -d

# Verify
curl http://localhost:3000/api/health

# Monitor
docker-compose logs -f app

# Backup
docker-compose exec db pg_dump -U metaextract metaextract > ./backups/backup.sql

# Restore
docker-compose exec -T db psql -U metaextract metaextract < ./backups/backup.sql
```

---

## Emergency Contacts

If things go wrong:
- Check Docker logs: `docker-compose logs -f`
- Check database: `npm run check:db`
- Check metrics: `curl http://localhost:3000/metrics`
- Rollback: See "Rollback Procedure" above
- Contact: See documentation in LAUNCH_READINESS_FINAL.md

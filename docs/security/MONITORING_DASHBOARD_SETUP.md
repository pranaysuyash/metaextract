# Monitoring Dashboard Setup Guide

## Quick Start

### Option 1: Local Development Monitoring (Node.js Built-in)
No additional setup required. Use built-in metrics.

### Option 2: Docker Compose with Prometheus + Grafana (Recommended)
Add these services to your `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - app-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./monitoring/grafana-dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml
    ports:
      - "3001:3000"
    networks:
      - app-network
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

---

## Metrics to Monitor

### Application Metrics
```
- HTTP Request Count (by endpoint, status code)
- HTTP Request Duration (p50, p95, p99)
- Active WebSocket Connections
- Upload Success Rate
- Average File Processing Time
- Trial Conversions
- Credit Purchase Rate
```

### Database Metrics
```
- Connection Pool Usage
- Query Duration (p50, p95, p99)
- Slow Queries (>1s)
- Transaction Count
- Insert/Update/Delete Rates
- Index Hit Ratio
```

### Infrastructure Metrics
```
- CPU Usage
- Memory Usage
- Disk Usage (for uploads)
- Network I/O
- Redis Memory Usage
- Backup Job Status
```

### Business Metrics
```
- Daily Active Users
- Trial to Paid Conversion
- Revenue
- Customer Churn
- Support Tickets
- Error Rate by Feature
```

---

## Key Dashboards to Create

### 1. Overview Dashboard
Real-time status of all critical systems:
- Database connection pool usage
- WebSocket active connections
- Upload success/failure rate
- API latency (p95)
- Revenue (last 24h)

### 2. Database Performance
Query and connection analysis:
- Connection pool usage trend
- Slow query count
- Query duration distribution
- Transaction rate
- Index hit ratio

### 3. User Experience
Upload and conversion funnel:
- Upload completion rate
- Average processing time
- Trial usage breakdown
- Conversion rate
- Mobile vs Desktop success rate

### 4. Infrastructure Health
System resource utilization:
- CPU, Memory, Disk usage
- Network I/O
- Redis memory
- Backup status
- Service restarts

---

## Quick Implementation (DIY Monitoring)

### Create Prometheus Configuration
**monitoring/prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'metaextract'
    static_configs:
      - targets: ['localhost:3000/metrics']

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Create Grafana Datasource Configuration
**monitoring/grafana-datasources.yml**:
```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

---

## Instrumentation Code Required

### Add Metrics Middleware to Express
```typescript
import prometheus from 'prom-client';

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status']
});

// Middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);
    httpRequestTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .inc();
  });
  next();
});

// Expose metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(await prometheus.register.metrics());
});
```

---

## Alternative: Use DataDog/New Relic

### DataDog Implementation
```typescript
import dd from 'dd-trace';

dd.init({ service: 'metaextract-api' });

// Automatically tracks Express, PostgreSQL, Redis
```

### New Relic Implementation
```typescript
import newrelic from 'newrelic';

// Tracks metrics automatically
// Configure via newrelic.js
```

---

## Alert Rules

### Critical Alerts (PagerDuty/OpsGenie)
```yaml
- name: Database Down
  condition: up{job="postgres"} == 0
  duration: 5m
  severity: critical

- name: High Error Rate
  condition: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  duration: 5m
  severity: critical

- name: WebSocket Failing
  condition: websocket_connection_errors > 10
  duration: 5m
  severity: critical
```

### Warning Alerts (Slack)
```yaml
- name: Slow Database Queries
  condition: rate(mysql_slow_queries[5m]) > 1
  duration: 10m
  severity: warning

- name: High CPU Usage
  condition: node_cpu_usage > 80
  duration: 10m
  severity: warning

- name: Low Disk Space
  condition: node_disk_available_bytes < 1GB
  duration: 10m
  severity: warning
```

---

## Quick Setup Commands

```bash
# Create monitoring directory
mkdir -p monitoring

# Add services to docker-compose
# (Use the YAML above)

# Start monitoring stack
docker-compose up -d prometheus grafana

# Access Grafana
# URL: http://localhost:3001
# Username: admin
# Password: admin

# Access Prometheus
# URL: http://localhost:9090
```

---

## Verification

1. **Check Prometheus Targets**
   - Visit http://localhost:9090/targets
   - Should see app, database, redis status

2. **Check Grafana Datasource**
   - Settings → Data Sources
   - Should see Prometheus connected

3. **Verify Metrics Endpoint**
   - Visit http://localhost:3000/metrics
   - Should see Prometheus metrics

---

## Recommended Paid Services (If Budget Allows)

| Service | Cost | Benefits |
|---------|------|----------|
| DataDog | $30+/month | Full observability, automatic instrumentation |
| New Relic | $100+/month | Detailed APM, transaction tracing |
| Grafana Cloud | $50+/month | Managed Prometheus + Grafana |
| PagerDuty | $30+/month | Incident management and alerting |

---

## Next Steps

1. **Week 1**: Set up basic Prometheus/Grafana locally
2. **Week 2**: Add application instrumentation
3. **Week 3**: Set up alerting rules
4. **Month 2**: Migrate to managed service (optional)

---

## References

- [Prometheus Documentation](https://prometheus.io/docs)
- [Grafana Documentation](https://grafana.com/docs)
- [DataDog Guide](https://docs.datadoghq.com)
- [Node.js Metrics Libraries](https://nodejs.org/en/docs/guides/nodejs-performance-monitoring/)

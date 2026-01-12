#!/bin/bash

# MetaExtract Security Monitoring Setup Script

echo "🚀 Setting up MetaExtract Security Monitoring..."

# Create directories
mkdir -p monitoring/{grafana/{dashboards,provisioning/{dashboards,datasources}},prometheus,filebeat,elasticsearch,kibana,clamav}

# Setup Grafana provisioning
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Setup Prometheus config
cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'metaextract-app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/api/monitoring/metrics'
EOF

# Setup Filebeat
cat > monitoring/filebeat/filebeat.yml << 'EOF'
filebeat.inputs:
- type: log
  paths:
    - /logs/*.log
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
EOF

echo "✅ Monitoring setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy monitoring/docker-compose.monitoring.yml to docker-compose.yml"
echo "2. Run: docker-compose up -d"
echo "3. Access Grafana at http://localhost:3000 (admin/admin123)"
echo "4. Access Prometheus at http://localhost:9090"
echo "5. Access Kibana at http://localhost:5601"
echo ""
echo "Security metrics will be available at:"
echo "- Dashboard: http://localhost:3000/d/security"
echo "- Metrics: http://localhost:9090/metrics"
echo "- Health: http://localhost:3000/api/health"
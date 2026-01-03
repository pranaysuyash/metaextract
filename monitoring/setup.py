#!/usr/bin/env python3
"""
Production Monitoring Setup for MetaExtract Platform

This script sets up comprehensive monitoring and alerting for the production environment.
"""

import psutil
import json
import time
import redis
import psycopg2
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/metaextract/logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionMonitor:
    """Comprehensive production monitoring system"""
    
    def __init__(self, config_file: str = "/opt/metaextract/config/monitor.json"):
        self.config = self._load_config(config_file)
        self.log_file = Path(self.config.get('log_file', '/opt/metaextract/logs/monitor.log'))
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.metrics_collector = MetricsCollector(max_history=10000)
        self.alert_manager = AlertManager(self.config.get('webhook_url'))
        self.health_checker = HealthChecker(self.config)
        
        logger.info("Production Monitor initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        config_path = Path(config_file)
        
        # Default configuration
        default_config = {
            'log_file': '/opt/metaextract/logs/monitor.log',
            'webhook_url': os.getenv('MONITORING_WEBHOOK_URL', ''),
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database': os.getenv('DB_NAME', 'metaextract_production'),
                'user': os.getenv('DB_USER', 'metaextract'),
                'password': os.getenv('DB_PASSWORD', '')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379'))
            },
            'alerting': {
                'enabled': True,
                'webhook_url': os.getenv('ALERT_WEBHOOK_URL', ''),
                'thresholds': {
                    'cpu_percent': 80,
                    'memory_percent': 85,
                    'disk_percent': 90,
                    'error_rate': 5
                }
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        return default_config
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("Starting production monitoring...")
        
        while True:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                
                # Check health
                health_status = self.health_checker.check_health()
                
                # Combine all metrics
                combined_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system': system_metrics,
                    'application': app_metrics,
                    'health': health_status
                }
                
                # Store metrics
                self._store_metrics(combined_metrics)
                
                # Check for alerts
                alerts = self.alert_manager.check_metrics_and_alert(combined_metrics)
                
                # Log status
                if health_status['status'] == 'healthy':
                    logger.info(f"System healthy - CPU: {system_metrics['cpu_percent']}%, Memory: {system_metrics['memory_percent']}%")
                else:
                    logger.warning(f"System degraded - {len(alerts)} alerts triggered")
                
                # Wait before next check
                time.sleep(self.config.get('check_interval', 30))
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'load_average': load_avg,
                'process_count': len(psutil.pids()),
                'uptime_seconds': time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level metrics"""
        try:
            # Check Node.js processes
            node_processes = [p for p in psutil.process_iter(['pid', 'name', 'memory_percent']) 
                            if 'node' in p.info['name'].lower()]
            
            # Check database connection
            db_healthy = self._check_database_health()
            
            # Check Redis connection
            redis_healthy = self._check_redis_health()
            
            # Check application endpoints
            app_healthy = self._check_application_endpoints()
            
            return {
                'node_processes': len(node_processes),
                'node_memory_percent': sum(p.info['memory_percent'] for p in node_processes),
                'database_healthy': db_healthy,
                'redis_healthy': redis_healthy,
                'application_healthy': app_healthy,
                'uptime_seconds': int(time.time() - psutil.Process().create_time())
            }
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {'error': str(e)}
    
    def _check_database_health(self) -> bool:
        """Check database health"""
        try:
            conn = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['database'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                connect_timeout=5
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _check_redis_health(self) -> bool:
        """Check Redis health"""
        try:
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                decode_responses=True
            )
            return r.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    def _check_application_endpoints(self) -> bool:
        """Check application endpoints"""
        try:
            # Check main API endpoint
            response = requests.get('http://localhost:3000/api/health', timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Application endpoint check failed: {e}")
            return False
    
    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store metrics to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")


class MetricsCollector:
    """Metrics collection and analysis"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics_history = {
            'extraction_times': deque(maxlen=max_history),
            'error_rates': deque(maxlen=max_history),
            'throughput': deque(maxlen=max_history),
            'user_engagement': deque(maxlen=max_history)
        }
    
    def record_extraction_metric(self, processing_time: float, success: bool, file_size: int) -> None:
        """Record extraction performance metric"""
        self.metrics_history['extraction_times'].append({
            'timestamp': datetime.now().isoformat(),
            'processing_time': processing_time,
            'success': success,
            'file_size': file_size
        })
    
    def record_error_metric(self, error_type: str, file_path: str) -> None:
        """Record error metric"""
        self.metrics_history['error_rates'].append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'file_path': file_path
        })
    
    def calculate_performance_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Calculate performance metrics for specified time range"""
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # Filter metrics by time range
        recent_metrics = {
            'extraction_times': [
                m for m in self.metrics_history['extraction_times']
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ],
            'error_rates': [
                m for m in self.metrics_history['error_rates']
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
        }
        
        # Calculate metrics
        extraction_metrics = self._calculate_extraction_metrics(recent_metrics['extraction_times'])
        error_metrics = self._calculate_error_metrics(recent_metrics['error_rates'])
        
        return {
            'time_range': f"{time_range_hours}h",
            'extraction_metrics': extraction_metrics,
            'error_metrics': error_metrics,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_extraction_metrics(self, extraction_times: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate extraction performance metrics"""
        if not extraction_times:
            return {'status': 'no_data'}
        
        processing_times = [m['processing_time'] for m in extraction_times]
        success_count = sum(1 for m in extraction_times if m['success'])
        total_count = len(extraction_times)
        
        return {
            'total_extractions': total_count,
            'successful_extractions': success_count,
            'success_rate': (success_count / total_count) * 100,
            'avg_processing_time': sum(processing_times) / len(processing_times),
            'min_processing_time': min(processing_times),
            'max_processing_time': max(processing_times),
            'median_processing_time': sorted(processing_times)[len(processing_times) // 2]
        }
    
    def _calculate_error_metrics(self, error_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate error rate metrics"""
        if not error_records:
            return {'status': 'no_errors'}
        
        error_types = defaultdict(int)
        for error in error_records:
            error_types[error['error_type']] += 1
        
        return {
            'total_errors': len(error_records),
            'error_types': dict(error_types),
            'most_common_error': max(error_types.items(), key=lambda x: x[1])[0] if error_types else 'none'
        }


class AlertManager:
    """Alert management and notification system"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.alert_rules = self._load_alert_rules()
        self.alert_history = deque(maxlen=1000)
    
    def _load_alert_rules(self) -> List[Dict[str, Any]]:
        """Load alert rules from configuration"""
        return [
            {
                'name': 'high_cpu_usage',
                'condition': lambda metrics: metrics['system']['cpu_percent'] > 80,
                'severity': 'warning',
                'message': 'CPU usage is above 80%'
            },
            {
                'name': 'high_memory_usage',
                'condition': lambda metrics: metrics['system']['memory_percent'] > 85,
                'severity': 'critical',
                'message': 'Memory usage is above 85%'
            },
            {
                'name': 'database_connection_lost',
                'condition': lambda metrics: not metrics['application']['database_healthy'],
                'severity': 'critical',
                'message': 'Database connection lost'
            },
            {
                'name': 'redis_connection_lost',
                'condition': lambda metrics: not metrics['application']['redis_healthy'],
                'severity': 'critical',
                'message': 'Redis connection lost'
            },
            {
                'name': 'application_unhealthy',
                'condition': lambda metrics: not metrics['application']['application_healthy'],
                'severity': 'warning',
                'message': 'Application health check failed'
            },
            {
                'name': 'disk_space_critical',
                'condition': lambda metrics: metrics['system']['disk_percent'] > 90,
                'severity': 'critical',
                'message': 'Disk usage is above 90%'
            }
        ]
    
    def check_metrics_and_alert(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics and trigger alerts if necessary"""
        alerts_triggered = []
        
        for rule in self.alert_rules:
            try:
                if rule['condition'](metrics):
                    alert = {
                        'rule_name': rule['name'],
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'timestamp': datetime.now().isoformat(),
                        'metrics': metrics
                    }
                    alerts_triggered.append(alert)
                    self.alert_history.append(alert)
                    self._send_alert(alert)
            except Exception as e:
                logger.error(f"Alert rule error: {e}")
        
        return alerts_triggered
    
    def _send_alert(self, alert: Dict[str, Any]) -> bool:
        """Send alert to configured webhook"""
        if not self.webhook_url:
            logger.info(f"Alert triggered (no webhook configured): {alert['message']}")
            return False
        
        try:
            payload = {
                'text': f"🚨 MetaExtract Alert: {alert['message']}",
                'attachments': [
                    {
                        'color': self._get_alert_color(alert['severity']),
                        'fields': [
                            {'title': 'Rule', 'value': alert['rule_name'], 'short': True},
                            {'title': 'Severity', 'value': alert['severity'], 'short': True},
                            {'title': 'Timestamp', 'value': alert['timestamp'], 'short': True},
                            {'title': 'Status', 'value': alert['metrics']['health']['status'], 'short': True}
                        ]
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            success = response.status_code == 200
            
            if success:
                logger.info(f"Alert sent successfully: {alert['rule_name']}")
            else:
                logger.error(f"Failed to send alert: {response.status_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def _get_alert_color(self, severity: str) -> str:
        """Get color for alert severity"""
        colors = {
            'info': '#36a64f',
            'warning': '#ff9800',
            'critical': '#f44336'
        }
        return colors.get(severity, '#9e9e9e')


class HealthChecker:
    """Health checking utilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            system_health = self._check_system_health()
            app_health = self._check_application_health()
            
            overall_status = 'healthy' if all([
                system_health.get('cpu_percent', 0) < 80,
                system_health.get('memory_percent', 0) < 80,
                system_health.get('disk_percent', 0) < 90,
                app_health.get('database_healthy', False),
                app_health.get('redis_healthy', False)
            ]) else 'degraded'
            
            return {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'system': system_health,
                'application': app_health
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"System health check error: {e}")
            return {'error': str(e)}
    
    def _check_application_health(self) -> Dict[str, Any]:
        """Check application health metrics"""
        try:
            # Check Node.js processes
            node_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                            if 'node' in p.info['name'].lower()]
            
            # Check database connection
            db_healthy = self._check_database_connection()
            
            # Check Redis connection
            redis_healthy = self._check_redis_connection()
            
            return {
                'node_processes': len(node_processes),
                'database_healthy': db_healthy,
                'redis_healthy': redis_healthy
            }
        except Exception as e:
            logger.error(f"Application health check error: {e}")
            return {'error': str(e)}
    
    def _check_database_connection(self) -> bool:
        """Check database connection"""
        try:
            conn = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['database'],
                user=self.config['database']['user'],
                password=self.config['database']['password'],
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def _check_redis_connection(self) -> bool:
        """Check Redis connection"""
        try:
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                decode_responses=True
            )
            return r.ping()
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False


def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MetaExtract Production Monitor')
    parser.add_argument('--config', default='/opt/metaextract/config/monitor.json',
                       help='Configuration file path')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon in background')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds')
    
    args = parser.parse_args()
    
    if args.daemon:
        # Run as daemon
        import daemon
        with daemon.DaemonContext():
            monitor = ProductionMonitor(args.config)
            monitor.start_monitoring()
    else:
        # Run in foreground
        monitor = ProductionMonitor(args.config)
        monitor.start_monitoring()


if __name__ == "__main__":
    main()
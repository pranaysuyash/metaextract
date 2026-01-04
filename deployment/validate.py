#!/usr/bin/env python3
"""
MetaExtract Production Deployment Validation Script

This script performs comprehensive validation before and after deployment.
"""

import subprocess
import json
import requests
import psycopg2
import redis
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import argparse
import logging
import os
import socket
import ssl
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/metaextract/logs/validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeploymentValidator:
    """Comprehensive deployment validation system"""
    
    def __init__(self, config_file: str = "/opt/metaextract/config/validation.json"):
        self.config = self._load_config(config_file)
        self.validation_results = {
            'system_checks': [],
            'application_checks': [],
            'integration_checks': [],
            'security_checks': [],
            'performance_checks': []
        }
        
        logger.info("Deployment Validator initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load validation configuration"""
        config_path = Path(config_file)
        
        # Default configuration
        default_config = {
            'domain': os.getenv('DOMAIN', 'your-domain.com'),
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
            'application': {
                'host': os.getenv('APP_HOST', 'localhost'),
                'port': int(os.getenv('APP_PORT', '3000'))
            },
            'thresholds': {
                'disk_space_min_gb': 5,
                'memory_max_percent': 90,
                'cpu_max_percent': 85,
                'response_time_max_ms': 5000
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
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        logger.info("Starting comprehensive deployment validation...")
        
        # System validation
        self._validate_system_requirements()
        
        # Application validation
        self._validate_application_health()
        
        # Integration validation
        self._validate_integrations()
        
        # Security validation
        self._validate_security()
        
        # Performance validation
        self._validate_performance()
        
        # Generate report
        return self._generate_validation_report()
    
    def _validate_system_requirements(self):
        """Validate system requirements"""
        logger.info("Validating system requirements...")
        
        # Check disk space
        try:
            disk_usage = psutil.disk_usage('/')
            disk_free_gb = disk_usage.free / (1024**3)
            disk_ok = disk_free_gb >= self.config['thresholds']['disk_space_min_gb']
            
            self.validation_results['system_checks'].append({
                'check': 'disk_space',
                'status': 'pass' if disk_ok else 'fail',
                'details': f"Free disk space: {disk_free_gb:.1f}GB (required: {self.config['thresholds']['disk_space_min_gb']}GB)",
                'value': disk_free_gb
            })
        except Exception as e:
            self.validation_results['system_checks'].append({
                'check': 'disk_space',
                'status': 'error',
                'details': str(e)
            })
        
        # Check memory
        try:
            memory = psutil.virtual_memory()
            memory_ok = memory.percent <= self.config['thresholds']['memory_max_percent']
            
            self.validation_results['system_checks'].append({
                'check': 'memory_usage',
                'status': 'pass' if memory_ok else 'fail',
                'details': f"Memory usage: {memory.percent}% (max: {self.config['thresholds']['memory_max_percent']}%)",
                'value': memory.percent
            })
        except Exception as e:
            self.validation_results['system_checks'].append({
                'check': 'memory_usage',
                'status': 'error',
                'details': str(e)
            })
        
        # Check CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_ok = cpu_percent <= self.config['thresholds']['cpu_max_percent']
            
            self.validation_results['system_checks'].append({
                'check': 'cpu_usage',
                'status': 'pass' if cpu_ok else 'fail',
                'details': f"CPU usage: {cpu_percent}% (max: {self.config['thresholds']['cpu_max_percent']}%)",
                'value': cpu_percent
            })
        except Exception as e:
            self.validation_results['system_checks'].append({
                'check': 'cpu_usage',
                'status': 'error',
                'details': str(e)
            })
        
        # Check system uptime
        try:
            uptime = time.time() - psutil.boot_time()
            uptime_ok = uptime > 60  # System should be up for at least 1 minute
            
            self.validation_results['system_checks'].append({
                'check': 'system_uptime',
                'status': 'pass' if uptime_ok else 'fail',
                'details': f"System uptime: {uptime:.0f} seconds",
                'value': uptime
            })
        except Exception as e:
            self.validation_results['system_checks'].append({
                'check': 'system_uptime',
                'status': 'error',
                'details': str(e)
            })
    
    def _validate_application_health(self):
        """Validate application health"""
        logger.info("Validating application health...")
        
        # Check Node.js processes
        try:
            result = subprocess.run(['pgrep', '-f', 'node'], capture_output=True, text=True)
            node_processes = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            node_ok = node_processes > 0
            
            self.validation_results['application_checks'].append({
                'check': 'node_processes',
                'status': 'pass' if node_ok else 'fail',
                'details': f"Node.js processes: {node_processes}",
                'value': node_processes
            })
        except Exception as e:
            self.validation_results['application_checks'].append({
                'check': 'node_processes',
                'status': 'error',
                'details': str(e)
            })
        
        # Check application port
        try:
            port_ok = self._check_port_open(self.config['application']['host'], 
                                          self.config['application']['port'])
            
            self.validation_results['application_checks'].append({
                'check': 'application_port',
                'status': 'pass' if port_ok else 'fail',
                'details': f"Port {self.config['application']['port']} is {'open' if port_ok else 'closed'}",
                'value': port_ok
            })
        except Exception as e:
            self.validation_results['application_checks'].append({
                'check': 'application_port',
                'status': 'error',
                'details': str(e)
            })
        
        # Check health endpoint
        try:
            health_url = f"http://{self.config['application']['host']}:{self.config['application']['port']}/api/health"
            response = requests.get(health_url, timeout=10)
            health_ok = response.status_code == 200
            
            self.validation_results['application_checks'].append({
                'check': 'health_endpoint',
                'status': 'pass' if health_ok else 'fail',
                'details': f"Health endpoint status: {response.status_code}",
                'value': response.status_code
            })
        except Exception as e:
            self.validation_results['application_checks'].append({
                'check': 'health_endpoint',
                'status': 'error',
                'details': str(e)
            })
    
    def _validate_integrations(self):
        """Validate external integrations"""
        logger.info("Validating external integrations...")
        
        # Check database connection
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
            
            db_ok = result is not None
            
            self.validation_results['integration_checks'].append({
                'check': 'database_connection',
                'status': 'pass' if db_ok else 'fail',
                'details': 'Database connection successful' if db_ok else 'Database connection failed',
                'value': db_ok
            })
        except Exception as e:
            self.validation_results['integration_checks'].append({
                'check': 'database_connection',
                'status': 'error',
                'details': str(e)
            })
        
        # Check Redis connection
        try:
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                decode_responses=True
            )
            redis_ok = r.ping()
            
            self.validation_results['integration_checks'].append({
                'check': 'redis_connection',
                'status': 'pass' if redis_ok else 'fail',
                'details': 'Redis connection successful' if redis_ok else 'Redis connection failed',
                'value': redis_ok
            })
        except Exception as e:
            self.validation_results['integration_checks'].append({
                'check': 'redis_connection',
                'status': 'error',
                'details': str(e)
            })
    
    def _validate_security(self):
        """Validate security configurations"""
        logger.info("Validating security configurations...")
        
        # Check SSL certificate
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.config['domain'], 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.config['domain']) as ssock:
                    cert = ssock.getpeercert()
                    ssl_ok = cert is not None
                    
                    cert_info = {
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert['version'],
                        'serialNumber': cert['serialNumber'],
                        'notBefore': cert['notBefore'],
                        'notAfter': cert['notAfter']
                    }
            
            self.validation_results['security_checks'].append({
                'check': 'ssl_certificate',
                'status': 'pass' if ssl_ok else 'fail',
                'details': f"SSL certificate valid for {self.config['domain']}",
                'value': ssl_ok
            })
        except Exception as e:
            self.validation_results['security_checks'].append({
                'check': 'ssl_certificate',
                'status': 'error',
                'details': str(e)
            })
        
        # Check security headers
        try:
            response = requests.get(f"https://{self.config['domain']}", timeout=10)
            
            # Check for important security headers
            security_headers = {
                'Strict-Transport-Security': 'HSTS',
                'X-Content-Type-Options': 'XCTO',
                'X-Frame-Options': 'XFO',
                'X-XSS-Protection': 'XXSS',
                'Content-Security-Policy': 'CSP'
            }
            
            headers_found = []
            for header, name in security_headers.items():
                if header in response.headers:
                    headers_found.append(name)
            
            headers_ok = len(headers_found) >= 3  # At least 3 security headers
            
            self.validation_results['security_checks'].append({
                'check': 'security_headers',
                'status': 'pass' if headers_ok else 'warning',
                'details': f"Security headers found: {', '.join(headers_found)}",
                'value': len(headers_found)
            })
        except Exception as e:
            self.validation_results['security_checks'].append({
                'check': 'security_headers',
                'status': 'error',
                'details': str(e)
            })
    
    def _validate_performance(self):
        """Validate performance metrics"""
        logger.info("Validating performance metrics...")
        
        # Check API response time
        try:
            start_time = time.time()
            response = requests.get(f"http://{self.config['application']['host']}:{self.config['application']['port']}/api/health", 
                                  timeout=30)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            response_ok = response_time <= self.config['thresholds']['response_time_max_ms']
            
            self.validation_results['performance_checks'].append({
                'check': 'api_response_time',
                'status': 'pass' if response_ok else 'fail',
                'details': f"API response time: {response_time:.0f}ms (max: {self.config['thresholds']['response_time_max_ms']}ms)",
                'value': response_time
            })
        except Exception as e:
            self.validation_results['performance_checks'].append({
                'check': 'api_response_time',
                'status': 'error',
                'details': str(e)
            })
    
    def _check_port_open(self, host: str, port: int) -> bool:
        """Check if a port is open"""
        try:
            with socket.create_connection((host, port), timeout=5):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        # Calculate summary statistics
        total_checks = sum(len(checks) for checks in self.validation_results.values())
        passed_checks = sum(sum(1 for check in checks if check['status'] == 'pass') 
                           for checks in self.validation_results.values())
        failed_checks = sum(sum(1 for check in checks if check['status'] == 'fail') 
                           for checks in self.validation_results.values())
        error_checks = sum(sum(1 for check in checks if check['status'] == 'error') 
                          for checks in self.validation_results.values())
        
        # Determine overall status
        overall_status = 'ready' if failed_checks == 0 and error_checks == 0 else 'needs_attention'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'errors': error_checks,
                'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
            },
            'details': self.validation_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        for category, checks in self.validation_results.items():
            for check in checks:
                if check['status'] != 'pass':
                    if check['check'] == 'disk_space':
                        recommendations.append("🔧 Free up disk space - minimum 5GB required")
                    elif check['check'] == 'memory_usage':
                        recommendations.append("🔧 Reduce memory usage - consider scaling or optimization")
                    elif check['check'] == 'cpu_usage':
                        recommendations.append("🔧 Reduce CPU usage - check for resource-intensive processes")
                    elif check['check'] == 'node_processes':
                        recommendations.append("🔧 Start Node.js application processes")
                    elif check['check'] == 'database_connection':
                        recommendations.append("🔧 Check database configuration and connection settings")
                    elif check['check'] == 'redis_connection':
                        recommendations.append("🔧 Check Redis configuration and connection settings")
                    elif check['check'] == 'ssl_certificate':
                        recommendations.append("🔧 Install or renew SSL certificate")
                    elif check['check'] == 'api_response_time':
                        recommendations.append("🔧 Optimize API performance for better response times")
        
        return recommendations

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description='MetaExtract Deployment Validator')
    parser.add_argument('--config', default='/opt/metaextract/config/validation.json',
                       help='Configuration file path')
    parser.add_argument('--output', default='validation_report.json',
                       help='Output file for validation report')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create validator
    validator = DeploymentValidator(args.config)
    
    # Run validation
    report = validator.validate_all()
    
    # Display results
    print("\n" + "="*60)
    print("📊 DEPLOYMENT VALIDATION REPORT")
    print("="*60)
    
    print(f"\n🎯 Overall Status: {report['overall_status'].upper()}")
    print(f"📅 Timestamp: {report['timestamp']}")
    
    print(f"\n📈 Summary:")
    print(f"   Total Checks: {report['summary']['total_checks']}")
    print(f"   ✅ Passed: {report['summary']['passed']}")
    print(f"   ❌ Failed: {report['summary']['failed']}")
    print(f"   ⚠️  Errors: {report['summary']['errors']}")
    print(f"   📊 Success Rate: {report['summary']['success_rate']:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for category, checks in report['details'].items():
        print(f"\n   {category.replace('_', ' ').title()}:")
        for check in checks:
            status_icon = {
                'pass': '✅',
                'fail': '❌',
                'error': '⚠️',
                'warning': '⚠️'
            }.get(check['status'], '❓')
            
            print(f"     {status_icon} {check['check']}: {check['details']}")
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   {rec}")
    
    # Save report to file
    try:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    except Exception as e:
        print(f"\n❌ Failed to save report: {e}")
    
    # Exit with appropriate code
    exit_code = 0 if report['overall_status'] == 'ready' else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
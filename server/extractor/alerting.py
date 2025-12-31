"""
MetaExtract Alerting System

This module provides alerting capabilities based on monitoring metrics.
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging

from .monitoring import get_monitor, SystemMonitor

logger = logging.getLogger(__name__)


class AlertRule:
    """Definition of an alert rule."""
    
    def __init__(self, name: str, condition_func: Callable, message: str, severity: str = "medium"):
        self.name = name
        self.condition_func = condition_func  # Function that takes metrics dict and returns bool
        self.message = message
        self.severity = severity  # "low", "medium", "high", "critical"
        self.last_triggered = None
        self.trigger_count = 0


class AlertManager:
    """Manages alert rules and notifications."""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Dict] = []
        self.notification_callbacks: List[Callable] = []
        self.check_interval = 60  # seconds
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        with self._lock:
            self.rules.append(rule)
    
    def add_notification_callback(self, callback: Callable):
        """Add a notification callback function."""
        self.notification_callbacks.append(callback)
    
    def check_rules(self):
        """Check all rules against current metrics."""
        monitor = get_monitor()
        metrics_data = monitor.get_monitoring_data()
        current_metrics = metrics_data.get("metrics", {})
        
        triggered_alerts = []
        
        with self._lock:
            for rule in self.rules:
                try:
                    if rule.condition_func(current_metrics):
                        # Check if this alert was already triggered recently
                        time_since_last = None
                        if rule.last_triggered:
                            time_since_last = time.time() - rule.last_triggered
                        
                        # Only trigger if it hasn't been triggered recently (to avoid spam)
                        if not rule.last_triggered or time_since_last > 300:  # 5 minutes
                            alert = {
                                "name": rule.name,
                                "message": rule.message,
                                "severity": rule.severity,
                                "timestamp": datetime.now().isoformat(),
                                "metrics": current_metrics.copy()
                            }
                            
                            rule.last_triggered = time.time()
                            rule.trigger_count += 1
                            triggered_alerts.append(alert)
                            self.alert_history.append(alert)
                            
                            # Keep only recent alerts (last 100)
                            if len(self.alert_history) > 100:
                                self.alert_history = self.alert_history[-100:]
                                
                except Exception as e:
                    logger.error(f"Error checking rule {rule.name}: {e}")
        
        # Send notifications for triggered alerts
        for alert in triggered_alerts:
            self._send_notifications(alert)
    
    def _send_notifications(self, alert: Dict):
        """Send notifications for an alert."""
        for callback in self.notification_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        if self._running:
            return
            
        self._running = True
        
        def monitoring_loop():
            while self._running:
                try:
                    self.check_rules()
                    time.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"Error in alert monitoring loop: {e}")
                    time.sleep(self.check_interval)  # Continue even if there's an error
        
        self._thread = threading.Thread(target=monitoring_loop, daemon=True)
        self._thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self._running = False
        if self._thread:
            self._thread.join()
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts."""
        with self._lock:
            return self.alert_history[-limit:]
    
    def get_active_rules(self) -> List[str]:
        """Get names of active rules."""
        with self._lock:
            return [rule.name for rule in self.rules]


# Global alert manager instance
_alert_manager = None
_alert_manager_lock = threading.Lock()


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        with _alert_manager_lock:
            if _alert_manager is None:
                _alert_manager = AlertManager()
    return _alert_manager


def setup_default_alerts():
    """Set up default alert rules."""
    manager = get_alert_manager()
    
    # High error rate alert
    def high_error_rate_condition(metrics):
        success_rate = metrics.get("success_rate", 1.0)
        return success_rate < 0.8  # Less than 80% success rate
    
    manager.add_rule(AlertRule(
        name="High Error Rate",
        condition_func=high_error_rate_condition,
        message="Success rate has dropped below 80%",
        severity="high"
    ))
    
    # Slow processing alert
    def slow_processing_condition(metrics):
        avg_time = metrics.get("avg_processing_time_ms", 0)
        return avg_time > 5000  # More than 5 seconds average
    
    manager.add_rule(AlertRule(
        name="Slow Processing",
        condition_func=slow_processing_condition,
        message="Average processing time has exceeded 5 seconds",
        severity="medium"
    ))
    
    # High error count alert
    def high_error_count_condition(metrics):
        failed_count = metrics.get("failed_extractions", 0)
        total_count = metrics.get("total_extractions", 1)
        error_rate = failed_count / total_count if total_count > 0 else 0
        return error_rate > 0.3 and total_count > 10  # More than 30% errors with at least 10 extractions
    
    manager.add_rule(AlertRule(
        name="High Error Count",
        condition_func=high_error_count_condition,
        message="Error rate has exceeded 30%",
        severity="high"
    ))
    
    # Low throughput alert
    def low_throughput_condition(metrics):
        throughput = metrics.get("extractions_per_minute", float('inf'))
        return throughput < 1  # Less than 1 extraction per minute
    
    manager.add_rule(AlertRule(
        name="Low Throughput",
        condition_func=low_throughput_condition,
        message="System throughput has dropped below 1 extraction per minute",
        severity="medium"
    ))
    
    # High memory usage alert (if we had memory metrics)
    # This is just an example - in a real system you'd have actual memory metrics
    def high_resource_usage_condition(metrics):
        # This would check actual resource usage if available
        return False
    
    manager.add_rule(AlertRule(
        name="High Resource Usage",
        condition_func=high_resource_usage_condition,
        message="System resource usage is high",
        severity="medium"
    ))


def email_notification_callback(alert: Dict):
    """Example notification callback that sends email alerts."""
    # This is a placeholder - in a real system you'd configure actual email settings
    print(f"ALERT: {alert['name']} - {alert['message']} (Severity: {alert['severity']})")
    print(f"Timestamp: {alert['timestamp']}")
    print(f"Metrics: {json.dumps(alert['metrics'], indent=2)[:200]}...")  # Truncate long metrics


def console_notification_callback(alert: Dict):
    """Simple console notification callback."""
    print(f"🚨 [{alert['severity'].upper()}] {alert['name']}: {alert['message']}")


def get_alert_status() -> Dict:
    """Get current alert status."""
    manager = get_alert_manager()
    recent_alerts = manager.get_alert_history(10)
    
    # Count alerts by severity
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for alert in recent_alerts:
        severity = alert.get("severity", "medium")
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    return {
        "active_rules": manager.get_active_rules(),
        "recent_alerts": recent_alerts,
        "severity_counts": severity_counts,
        "total_alerts": len(recent_alerts)
    }


# Initialize default alerts when module is loaded
setup_default_alerts()


if __name__ == "__main__":
    # Example usage
    manager = get_alert_manager()
    
    # Add a console notification callback
    manager.add_notification_callback(console_notification_callback)
    
    # Start monitoring
    manager.start_monitoring()
    
    print("Alert manager started. Monitoring for alerts...")
    print("Active rules:", manager.get_active_rules())
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(10)
            status = get_alert_status()
            print(f"Current status: {status['total_alerts']} recent alerts")
    except KeyboardInterrupt:
        print("Stopping alert manager...")
        manager.stop_monitoring()
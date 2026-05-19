"""
⚽ NEXUS FOOTBALL — Structured Logging & Monitoring
Comprehensive logging with structured output and monitoring
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import sys
from pythonjsonlogger import jsonlogger
from functools import wraps
import time

# ━━━━━ STRUCTURED LOGGER ━━━━━

class StructuredLogger:
    """Structured logging with JSON output"""
    
    def __init__(self, name: str = "nexus-football"):
        self.logger = logging.getLogger(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup JSON and console handlers"""
        # JSON handler (file)
        json_handler = logging.FileHandler("logs/nexus-football.json")
        json_formatter = jsonlogger.JsonFormatter()
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **context):
        """Log info with context"""
        self.logger.info(message, extra=context)
    
    def error(self, message: str, exception: Optional[Exception] = None, **context):
        """Log error with context"""
        if exception:
            context['exception'] = str(exception)
            context['exception_type'] = type(exception).__name__
        
        self.logger.error(message, extra=context)
    
    def warning(self, message: str, **context):
        """Log warning with context"""
        self.logger.warning(message, extra=context)
    
    def debug(self, message: str, **context):
        """Log debug with context"""
        self.logger.debug(message, extra=context)

# ━━━━━ REQUEST/RESPONSE LOGGING ━━━━━

class RequestLogger:
    """Log HTTP requests and responses"""
    
    def __init__(self):
        self.logger = StructuredLogger("nexus-http")
        self.request_count = 0
        self.error_count = 0
    
    def log_request(self, request, method: str, path: str, user_id: Optional[str] = None):
        """Log incoming request"""
        self.request_count += 1
        
        self.logger.info(
            f"{method} {path}",
            method=method,
            path=path,
            user_id=user_id,
            request_count=self.request_count,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_response(self, status_code: int, response_time_ms: float, path: str):
        """Log outgoing response"""
        if status_code >= 400:
            self.error_count += 1
        
        level = "error" if status_code >= 500 else "warning" if status_code >= 400 else "info"
        
        self.logger.info(
            f"Response {status_code}",
            status_code=status_code,
            response_time_ms=response_time_ms,
            path=path,
            level=level
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get request metrics"""
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        }

# ━━━━━ PERFORMANCE MONITORING ━━━━━

class PerformanceMonitor:
    """Monitor system performance"""
    
    def __init__(self):
        self.logger = StructuredLogger("nexus-performance")
        self.metrics = {}
    
    def record_operation(self, operation_name: str, duration_ms: float, success: bool = True):
        """Record operation performance"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                "count": 0,
                "total_duration": 0,
                "min_duration": float('inf'),
                "max_duration": 0,
                "errors": 0
            }
        
        metric = self.metrics[operation_name]
        metric['count'] += 1
        metric['total_duration'] += duration_ms
        metric['min_duration'] = min(metric['min_duration'], duration_ms)
        metric['max_duration'] = max(metric['max_duration'], duration_ms)
        
        if not success:
            metric['errors'] += 1
        
        self.logger.info(
            f"Operation: {operation_name}",
            operation=operation_name,
            duration_ms=duration_ms,
            success=success,
            avg_duration_ms=metric['total_duration'] / metric['count']
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        result = {}
        
        for op_name, metric in self.metrics.items():
            result[op_name] = {
                "count": metric['count'],
                "avg_duration_ms": metric['total_duration'] / metric['count'],
                "min_duration_ms": metric['min_duration'],
                "max_duration_ms": metric['max_duration'],
                "error_count": metric['errors'],
                "error_rate": (metric['errors'] / metric['count']) * 100 if metric['count'] > 0 else 0
            }
        
        return result

# ━━━━━ DECORATORS ━━━━━

def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            op_name = operation_name or func.__name__
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                monitor.record_operation(op_name, duration_ms, success=True)
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitor.record_operation(op_name, duration_ms, success=False)
                raise
        
        return async_wrapper
    
    return decorator

# ━━━━━ DATA QUALITY MONITOR ━━━━━

class DataQualityMonitor:
    """Monitor data quality"""
    
    def __init__(self):
        self.logger = StructuredLogger("nexus-data-quality")
        self.checks = {}
    
    def check_missing_values(self, data: Dict[str, Any], required_fields: list) -> bool:
        """Check for missing required fields"""
        missing = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing:
            self.logger.warning(
                f"Missing required fields: {missing}",
                missing_fields=missing,
                data_key=str(data.get('id', 'unknown'))
            )
            return False
        
        return True
    
    def check_data_types(self, data: Dict[str, Any], schema: Dict[str, type]) -> bool:
        """Check data types match schema"""
        errors = []
        
        for field, expected_type in schema.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    errors.append(f"{field}: expected {expected_type}, got {type(data[field])}")
        
        if errors:
            self.logger.warning(
                f"Data type mismatches: {errors}",
                errors=errors
            )
            return False
        
        return True
    
    def check_outliers(self, values: list, field_name: str, threshold: float = 3.0):
        """Detect statistical outliers"""
        if not values or len(values) < 3:
            return True
        
        import statistics
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        outliers = [v for v in values if abs(v - mean) > threshold * stdev]
        
        if outliers:
            self.logger.warning(
                f"Outliers detected in {field_name}",
                field=field_name,
                outlier_count=len(outliers),
                mean=mean,
                stdev=stdev
            )
            return False
        
        return True

# ━━━━━ ALERT SYSTEM ━━━━━

class AlertManager:
    """Manage system alerts"""
    
    def __init__(self):
        self.logger = StructuredLogger("nexus-alerts")
        self.alerts = []
    
    def create_alert(self, severity: str, message: str, context: Dict = None):
        """Create alert"""
        alert = {
            "severity": severity,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        self.alerts.append(alert)
        
        self.logger.info(
            f"Alert [{severity.upper()}]: {message}",
            severity=severity,
            alert_id=len(self.alerts),
            context=context
        )
        
        # Send notification if critical
        if severity == "critical":
            self._send_critical_alert(alert)
    
    def _send_critical_alert(self, alert: Dict):
        """Send critical alert notification"""
        # TODO: Implement email/SMS/Slack notification
        self.logger.error(
            "CRITICAL ALERT TRIGGERED",
            alert=alert
        )
    
    def get_recent_alerts(self, limit: int = 10) -> list:
        """Get recent alerts"""
        return self.alerts[-limit:]

# ━━━━━ GLOBAL INSTANCES ━━━━━

logger = StructuredLogger()
request_logger = RequestLogger()
performance_monitor = PerformanceMonitor()
data_quality_monitor = DataQualityMonitor()
alert_manager = AlertManager()

"""
MetaExtract Security Middleware

This module implements additional security hardening measures for the application.
"""

import os
import re
import time
import hashlib
import hmac
import secrets
from typing import Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import logging
from pathlib import Path

from flask import request, jsonify, g, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
import html


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Return recommended security headers."""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Feature-Policy': "geolocation 'none'; microphone 'none'; camera 'none'",
        }


class InputValidation:
    """Input validation utilities."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal and other attacks."""
        # Remove path separators to prevent directory traversal
        filename = re.sub(r'[\/\\]+', '', filename)
        
        # Remove potentially dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Limit length to prevent buffer overflow
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    @staticmethod
    def validate_file_path(filepath: str, allowed_directories: List[str]) -> bool:
        """Validate that file path is within allowed directories."""
        try:
            abs_path = os.path.abspath(filepath)
            for allowed_dir in allowed_directories:
                if abs_path.startswith(os.path.abspath(allowed_dir)):
                    return True
            return False
        except:
            return False
    
    @staticmethod
    def sanitize_input(text: str, allowed_tags: Optional[List[str]] = None) -> str:
        """Sanitize user input to prevent XSS attacks."""
        if allowed_tags is None:
            allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
        
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title'],
        }
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_content_type(content_type: str, allowed_types: List[str]) -> bool:
        """Validate content type against allowed list."""
        return content_type in allowed_types


class RateLimiter:
    """Enhanced rate limiting with multiple strategies."""
    
    def __init__(self):
        self.limits = {}
        self.request_counts = {}
        self.blocked_ips = set()
        self.blocked_until = {}
    
    def add_limit(self, key: str, max_requests: int, window_seconds: int):
        """Add a rate limit rule."""
        self.limits[key] = {
            'max_requests': max_requests,
            'window_seconds': window_seconds
        }
    
    def is_allowed(self, ip: str, key: str = 'default') -> bool:
        """Check if request is allowed based on rate limits."""
        if ip in self.blocked_ips:
            if ip in self.blocked_until and time.time() < self.blocked_until[ip]:
                return False
            else:
                # Unblock if timeout has passed
                self.blocked_ips.discard(ip)
                if ip in self.blocked_until:
                    del self.blocked_until[ip]
        
        current_time = time.time()
        request_key = f"{ip}:{key}"
        
        if request_key not in self.request_counts:
            self.request_counts[request_key] = []
        
        # Clean old requests
        self.request_counts[request_key] = [
            req_time for req_time in self.request_counts[request_key]
            if current_time - req_time < self.limits.get(key, {}).get('window_seconds', 3600)
        ]
        
        # Check if limit exceeded
        limit_info = self.limits.get(key, {})
        if len(self.request_counts[request_key]) >= limit_info.get('max_requests', 100):
            # Block IP temporarily
            self.blocked_ips.add(ip)
            self.blocked_until[ip] = current_time + 3600  # Block for 1 hour
            return False
        
        # Add current request
        self.request_counts[request_key].append(current_time)
        return True


class SecurityMiddleware:
    """Main security middleware class."""
    
    def __init__(self, app=None):
        self.app = app
        self.input_validation = InputValidation()
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)
        
        # Initialize rate limits
        self._setup_default_limits()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        # Register before request handler
        app.before_request(self.before_request)
        
        # Register after request handler for security headers
        app.after_request(self.after_request)
    
    def _setup_default_limits(self):
        """Setup default rate limiting rules."""
        # Default limits
        self.rate_limiter.add_limit('default', 100, 3600)  # 100 requests per hour
        self.rate_limiter.add_limit('api', 1000, 3600)    # 1000 API requests per hour
        self.rate_limiter.add_limit('upload', 10, 3600)   # 10 uploads per hour per IP
        self.rate_limiter.add_limit('login', 5, 300)      # 5 login attempts per 5 minutes
    
    def before_request(self):
        """Process request before it reaches the view."""
        # Add request start time for timing attacks prevention
        g.request_start_time = time.time()
        
        # Validate request method
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            self.logger.warning(f"Invalid HTTP method: {request.method} from {request.remote_addr}")
            return jsonify({'error': 'Invalid request method'}), 405
        
        # Check rate limits
        if not self._check_rate_limits():
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        # Validate content type for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_length and request.content_length > 100 * 1024 * 1024:  # 100MB
                self.logger.warning(f"Request too large from {request.remote_addr}")
                return jsonify({'error': 'Request too large'}), 413
        
        # Sanitize inputs
        self._sanitize_inputs()
        
        # Log security-relevant information
        self._log_security_event('request_received', {
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.content_type
        })
    
    def after_request(self, response):
        """Add security headers to response."""
        headers = SecurityHeaders.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        
        # Add custom security header
        response.headers['X-MetaExtract-Version'] = '4.0.0'
        
        return response
    
    def _check_rate_limits(self) -> bool:
        """Check if request exceeds rate limits."""
        ip = request.remote_addr
        
        # Determine rate limit key based on endpoint
        if request.path.startswith('/api/upload'):
            key = 'upload'
        elif request.path.startswith('/api/auth'):
            key = 'login'
        elif request.path.startswith('/api/'):
            key = 'api'
        else:
            key = 'default'
        
        is_allowed = self.rate_limiter.is_allowed(ip, key)
        
        if not is_allowed:
            self._log_security_event('rate_limit_exceeded', {
                'ip': ip,
                'path': request.path,
                'limit_key': key
            })
        
        return is_allowed
    
    def _sanitize_inputs(self):
        """Sanitize request inputs."""
        # Sanitize form data
        if request.form:
            sanitized_form = {}
            for key, value in request.form.items():
                if isinstance(value, str):
                    sanitized_form[key] = self.input_validation.sanitize_input(value)
                else:
                    sanitized_form[key] = value
            # Note: In a real implementation, we'd need to replace request.form
            # This is simplified for demonstration
        
        # Sanitize query parameters
        if request.args:
            for key, value in request.args.items():
                if isinstance(value, str):
                    # In a real implementation, we'd sanitize these
                    pass
    
    def _log_security_event(self, event_type: str, details: Dict):
        """Log security-related events."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.logger.info(f"SECURITY_EVENT: {log_entry}")


class AuthenticationSecurity:
    """Additional authentication security measures."""
    
    def __init__(self):
        self.failed_attempts = {}
        self.lockout_duration = 900  # 15 minutes
        self.max_attempts = 5
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed authentication attempt."""
        current_time = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Clean old attempts
        self.failed_attempts[identifier] = [
            attempt_time for attempt_time in self.failed_attempts[identifier]
            if current_time - attempt_time < self.lockout_duration
        ]
        
        # Add current attempt
        self.failed_attempts[identifier].append(current_time)
    
    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is locked out."""
        if identifier not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[identifier]
        return len(attempts) >= self.max_attempts
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """Get remaining attempts before lockout."""
        if identifier not in self.failed_attempts:
            return self.max_attempts
        
        attempts = self.failed_attempts[identifier]
        return max(0, self.max_attempts - len(attempts))


class CSRFProtection:
    """CSRF protection mechanism."""
    
    def __init__(self):
        self.tokens = {}
        self.token_timeout = 3600  # 1 hour
    
    def generate_token(self, user_id: str) -> str:
        """Generate a CSRF token for a user."""
        token = secrets.token_urlsafe(32)
        current_time = time.time()
        
        if user_id not in self.tokens:
            self.tokens[user_id] = {}
        
        # Clean old tokens
        self.tokens[user_id] = {
            tok: timestamp for tok, timestamp in self.tokens[user_id].items()
            if current_time - timestamp < self.token_timeout
        }
        
        self.tokens[user_id][token] = current_time
        return token
    
    def validate_token(self, user_id: str, token: str) -> bool:
        """Validate a CSRF token."""
        if user_id not in self.tokens or token not in self.tokens[user_id]:
            return False
        
        timestamp = self.tokens[user_id][token]
        current_time = time.time()
        
        # Check if token is expired
        if current_time - timestamp > self.token_timeout:
            del self.tokens[user_id][token]
            return False
        
        # Valid token, remove it to prevent replay attacks
        del self.tokens[user_id][token]
        return True


# Global security instances
security_middleware = SecurityMiddleware()
auth_security = AuthenticationSecurity()
csrf_protection = CSRFProtection()


def require_csrf_token(f):
    """Decorator to require CSRF token for protected endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(g, 'user_id', 'anonymous')
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token or not csrf_protection.validate_token(user_id, token):
            return jsonify({'error': 'Invalid or missing CSRF token'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def security_audit_log(event_type: str, details: Dict):
    """Helper function to log security events."""
    logger = logging.getLogger(__name__)
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details
    }
    logger.info(f"SECURITY_AUDIT: {log_entry}")


# Example usage in an endpoint
def example_secure_endpoint():
    """Example of how to use security measures in an endpoint."""
    # This would be used in a Flask route
    pass


if __name__ == "__main__":
    # Example of how to use the security features
    print("MetaExtract Security Framework")
    print("==============================")
    
    # Example input sanitization
    print("\nInput Sanitization Examples:")
    malicious_filename = "../../../etc/passwd"
    clean_filename = InputValidation.sanitize_filename(malicious_filename)
    print(f"Original: {malicious_filename}")
    print(f"Sanitized: {clean_filename}")
    
    # Example rate limiting
    print("\nRate Limiting Example:")
    limiter = RateLimiter()
    limiter.add_limit('test', 3, 60)  # 3 requests per minute
    
    for i in range(5):
        allowed = limiter.is_allowed('127.0.0.1', 'test')
        print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'}")
    
    # Example authentication security
    print("\nAuthentication Security Example:")
    auth_sec = AuthenticationSecurity()
    
    # Simulate failed attempts
    for i in range(6):
        auth_sec.record_failed_attempt('user123')
        remaining = auth_sec.get_remaining_attempts('user123')
        print(f"After attempt {i+1}: {remaining} attempts remaining")
    
    is_locked = auth_sec.is_locked_out('user123')
    print(f"Account locked: {is_locked}")
"""
MetaExtract API Rate Limiting System

This module provides sophisticated rate limiting based on monitoring data
to prevent abuse and ensure system stability.
"""

import time
import threading
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import hashlib
import json
from enum import Enum
from dataclasses import dataclass


class RateLimitTier(Enum):
    """Rate limit tiers."""
    FREE = "free"
    STARTER = "starter"
    PREMIUM = "premium"
    SUPER = "super"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int  # Max requests in a short burst


@dataclass
class RateLimitState:
    """Current state of rate limiting for a client."""
    minute_requests: deque
    hour_requests: deque
    day_requests: deque
    burst_requests: deque
    last_reset: float
    tier: RateLimitTier


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts limits based on system monitoring data."""
    
    def __init__(self):
        self.clients: Dict[str, RateLimitState] = {}
        self.configs: Dict[RateLimitTier, RateLimitConfig] = self._get_default_configs()
        self.lock = threading.RLock()
        
        # System health metrics that affect rate limiting
        self.system_health = {
            'error_rate': 0.0,
            'avg_response_time': 0.0,
            'active_connections': 0,
            'cpu_usage': 0.0,
            'memory_usage': 0.0
        }
        self.health_lock = threading.Lock()
        
        # Default multipliers based on system health
        self.health_multipliers = {
            'error_rate': 0.1,  # Higher error rate = lower limits
            'response_time': 0.05,  # Higher response time = lower limits
            'cpu_usage': 0.02,  # Higher CPU usage = lower limits
            'memory_usage': 0.01  # Higher memory usage = lower limits
        }
    
    def _get_default_configs(self) -> Dict[RateLimitTier, RateLimitConfig]:
        """Get default rate limit configurations."""
        return {
            RateLimitTier.FREE: RateLimitConfig(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=500,
                burst_limit=5
            ),
            RateLimitTier.STARTER: RateLimitConfig(
                requests_per_minute=30,
                requests_per_hour=300,
                requests_per_day=1000,
                burst_limit=10
            ),
            RateLimitTier.PREMIUM: RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=1000,
                requests_per_day=5000,
                burst_limit=25
            ),
            RateLimitTier.SUPER: RateLimitConfig(
                requests_per_minute=300,
                requests_per_hour=3000,
                requests_per_day=10000,
                burst_limit=50
            )
        }
    
    def _get_client_key(self, client_id: str, endpoint: str = "*") -> str:
        """Get a unique key for a client and endpoint."""
        return f"{client_id}:{endpoint}"
    
    def _get_adjusted_config(self, tier: RateLimitTier) -> RateLimitConfig:
        """Get rate limit config adjusted based on system health."""
        base_config = self.configs[tier]
        
        # Calculate health-based multiplier (0.5 to 1.5, where 1.0 is normal)
        with self.health_lock:
            health_factor = 1.0
            health_factor -= self.system_health['error_rate'] * self.health_multipliers['error_rate']
            health_factor -= (self.system_health['avg_response_time'] / 1000) * self.health_multipliers['response_time']  # Convert ms to s
            health_factor -= self.system_health['cpu_usage'] * self.health_multipliers['cpu_usage']
            health_factor -= self.system_health['memory_usage'] * self.health_multipliers['memory_usage']
        
        # Ensure health factor is between 0.5 and 1.5
        health_factor = max(0.5, min(1.5, health_factor))
        
        return RateLimitConfig(
            requests_per_minute=int(base_config.requests_per_minute * health_factor),
            requests_per_hour=int(base_config.requests_per_hour * health_factor),
            requests_per_day=int(base_config.requests_per_day * health_factor),
            burst_limit=int(base_config.burst_limit * health_factor)
        )
    
    def _cleanup_old_requests(self, request_times: deque, window_seconds: int):
        """Remove requests older than the time window."""
        cutoff_time = time.time() - window_seconds
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
    
    def update_system_health(self, error_rate: float, avg_response_time: float, 
                           active_connections: int, cpu_usage: float, memory_usage: float):
        """Update system health metrics that affect rate limiting."""
        with self.health_lock:
            self.system_health.update({
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'active_connections': active_connections,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage
            })
    
    def is_allowed(self, client_id: str, tier: RateLimitTier = RateLimitTier.FREE, 
                   endpoint: str = "*", current_time: Optional[float] = None) -> Tuple[bool, Dict[str, int]]:
        """Check if a request is allowed based on rate limits."""
        if current_time is None:
            current_time = time.time()
        
        with self.lock:
            client_key = self._get_client_key(client_id, endpoint)
            
            # Get or create client state
            if client_key not in self.clients:
                self.clients[client_key] = RateLimitState(
                    minute_requests=deque(),
                    hour_requests=deque(),
                    day_requests=deque(),
                    burst_requests=deque(),
                    last_reset=current_time,
                    tier=tier
                )
            
            client_state = self.clients[client_key]
            
            # Update tier if it changed
            if client_state.tier != tier:
                client_state.tier = tier
            
            # Get adjusted config based on system health
            config = self._get_adjusted_config(tier)
            
            # Cleanup old requests
            self._cleanup_old_requests(client_state.minute_requests, 60)  # 1 minute
            self._cleanup_old_requests(client_state.hour_requests, 3600)  # 1 hour
            self._cleanup_old_requests(client_state.day_requests, 86400)  # 1 day
            self._cleanup_old_requests(client_state.burst_requests, 1)  # 1 second
            
            # Check current counts against limits
            current_minute_count = len(client_state.minute_requests)
            current_hour_count = len(client_state.hour_requests)
            current_day_count = len(client_state.day_requests)
            current_burst_count = len(client_state.burst_requests)
            
            # Check all limits
            limits_exceeded = {}
            
            if current_minute_count >= config.requests_per_minute:
                limits_exceeded['minute'] = config.requests_per_minute - current_minute_count
            
            if current_hour_count >= config.requests_per_hour:
                limits_exceeded['hour'] = config.requests_per_hour - current_hour_count
            
            if current_day_count >= config.requests_per_day:
                limits_exceeded['day'] = config.requests_per_day - current_day_count
            
            if current_burst_count >= config.burst_limit:
                limits_exceeded['burst'] = config.burst_limit - current_burst_count
            
            # Determine if request is allowed
            is_allowed = len(limits_exceeded) == 0
            
            # Add the current request if allowed
            if is_allowed:
                client_state.minute_requests.append(current_time)
                client_state.hour_requests.append(current_time)
                client_state.day_requests.append(current_time)
                client_state.burst_requests.append(current_time)
            
            return is_allowed, {
                'minute_remaining': max(0, config.requests_per_minute - current_minute_count),
                'hour_remaining': max(0, config.requests_per_hour - current_hour_count),
                'day_remaining': max(0, config.requests_per_day - current_day_count),
                'burst_remaining': max(0, config.burst_limit - current_burst_count),
                'limits_exceeded': limits_exceeded
            }
    
    def get_reset_times(self, client_id: str, endpoint: str = "*") -> Dict[str, float]:
        """Get time until rate limits reset."""
        with self.lock:
            client_key = self._get_client_key(client_id, endpoint)
            
            if client_key not in self.clients:
                return {
                    'minute': 0,
                    'hour': 0,
                    'day': 0,
                    'burst': 0
                }
            
            current_time = time.time()
            client_state = self.clients[client_key]
            
            # Find next reset times
            minute_reset = 60 if client_state.minute_requests else 0
            hour_reset = 3600 if client_state.hour_requests else 0
            day_reset = 86400 if client_state.day_requests else 0
            burst_reset = 1 if client_state.burst_requests else 0
            
            # Calculate actual reset times
            return {
                'minute': minute_reset,
                'hour': hour_reset,
                'day': day_reset,
                'burst': burst_reset
            }
    
    def get_usage_stats(self, client_id: str, endpoint: str = "*") -> Dict[str, int]:
        """Get current usage statistics for a client."""
        with self.lock:
            client_key = self._get_client_key(client_id, endpoint)
            
            if client_key not in self.clients:
                return {
                    'minute_requests': 0,
                    'hour_requests': 0,
                    'day_requests': 0,
                    'burst_requests': 0
                }
            
            client_state = self.clients[client_key]
            
            # Cleanup old requests first
            self._cleanup_old_requests(client_state.minute_requests, 60)
            self._cleanup_old_requests(client_state.hour_requests, 3600)
            self._cleanup_old_requests(client_state.day_requests, 86400)
            self._cleanup_old_requests(client_state.burst_requests, 1)
            
            return {
                'minute_requests': len(client_state.minute_requests),
                'hour_requests': len(client_state.hour_requests),
                'day_requests': len(client_state.day_requests),
                'burst_requests': len(client_state.burst_requests)
            }


class MonitoringBasedRateLimiter:
    """Rate limiter that adapts based on monitoring data."""
    
    def __init__(self):
        self.rate_limiter = AdaptiveRateLimiter()
        self.monitoring_data = {}
        self.last_update = time.time()
        self.update_interval = 60  # Update system health every minute
    
    def update_from_monitoring(self, monitoring_data: Dict):
        """Update rate limiter with current monitoring data."""
        self.monitoring_data = monitoring_data
        
        # Extract relevant metrics
        metrics = monitoring_data.get('metrics', {})
        
        error_rate = 1 - metrics.get('success_rate', 1.0)
        avg_response_time = metrics.get('avg_processing_time_ms', 0)
        # active_connections would come from server metrics
        active_connections = 0  # This would be passed from server connection tracking
        cpu_usage = 0.0  # This would come from system monitoring
        memory_usage = 0.0  # This would come from system monitoring
        
        # Update system health in the rate limiter
        self.rate_limiter.update_system_health(
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            active_connections=active_connections,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage
        )
    
    def is_allowed(self, client_id: str, tier: str = "free", endpoint: str = "*") -> Tuple[bool, Dict]:
        """Check if a request is allowed based on adaptive rate limits."""
        # Convert tier string to enum
        try:
            tier_enum = RateLimitTier(tier.upper())
        except ValueError:
            tier_enum = RateLimitTier.FREE  # Default to free tier
        
        return self.rate_limiter.is_allowed(client_id, tier_enum, endpoint)
    
    def get_usage_stats(self, client_id: str, endpoint: str = "*") -> Dict:
        """Get usage statistics for a client."""
        return self.rate_limiter.get_usage_stats(client_id, endpoint)
    
    def get_reset_times(self, client_id: str, endpoint: str = "*") -> Dict:
        """Get reset times for rate limits."""
        return self.rate_limiter.get_reset_times(client_id, endpoint)


# Global rate limiter instance
_rate_limiter = None
_rate_limiter_lock = threading.Lock()


def get_rate_limiter() -> MonitoringBasedRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        with _rate_limiter_lock:
            if _rate_limiter is None:
                _rate_limiter = MonitoringBasedRateLimiter()
    return _rate_limiter


def is_request_allowed(client_id: str, tier: str = "free", endpoint: str = "*") -> Tuple[bool, Dict]:
    """Convenience function to check if a request is allowed."""
    limiter = get_rate_limiter()
    return limiter.is_allowed(client_id, tier, endpoint)


def update_rate_limiter_from_monitoring(monitoring_data: Dict):
    """Convenience function to update rate limiter with monitoring data."""
    limiter = get_rate_limiter()
    limiter.update_from_monitoring(monitoring_data)


def get_client_usage_stats(client_id: str, endpoint: str = "*") -> Dict:
    """Convenience function to get client usage stats."""
    limiter = get_rate_limiter()
    return limiter.get_usage_stats(client_id, endpoint)


# Example usage and testing
if __name__ == "__main__":
    import time
    
    print("Testing adaptive rate limiting...")
    
    # Create a rate limiter
    limiter = get_rate_limiter()
    
    # Simulate some monitoring data
    mock_monitoring_data = {
        'metrics': {
            'success_rate': 0.95,
            'avg_processing_time_ms': 200
        }
    }
    
    # Update with monitoring data
    limiter.update_from_monitoring(mock_monitoring_data)
    
    # Test rate limiting for different clients and tiers
    test_cases = [
        ("client1", "free"),
        ("client2", "premium"),
        ("client3", "super")
    ]
    
    print("\n--- Testing Rate Limiting ---")
    for client_id, tier in test_cases:
        print(f"\nTesting {client_id} (tier: {tier}):")
        
        # Make several requests quickly to test burst limiting
        for i in range(5):
            allowed, info = limiter.is_allowed(client_id, tier)
            print(f"  Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'} - Remaining: {info['burst_remaining']}")
            
            # Small delay to simulate burst
            time.sleep(0.1)
    
    # Check usage stats
    print(f"\n--- Usage Stats for client1 ---")
    stats = limiter.get_usage_stats("client1")
    print(f"Current usage: {stats}")
    
    reset_times = limiter.get_reset_times("client1")
    print(f"Reset times: {reset_times}")
    
    # Simulate system stress (higher error rate)
    print(f"\n--- Simulating System Stress ---")
    stress_monitoring_data = {
        'metrics': {
            'success_rate': 0.70,  # Higher error rate
            'avg_processing_time_ms': 1500  # Higher response time
        }
    }
    
    limiter.update_from_monitoring(stress_monitoring_data)
    
    print("After system stress simulation:")
    allowed, info = limiter.is_allowed("client1", "free")
    print(f"Request now: {'ALLOWED' if allowed else 'BLOCKED'} - Remaining: {info['burst_remaining']}")
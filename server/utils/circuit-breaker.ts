/**
 * Circuit Breaker for Emergency Load Shedding
 * 
 * Protects the system during high load or attack conditions:
 * - Free tier gets delayed (not denied) during high load
 * - Paid tier stays fast
 * - Prevents cost runaway from attacks
 * 
 * States:
 * - CLOSED: Normal operation, all requests processed normally
 * - OPEN: High load, free tier delayed, paid tier normal
 * - HALF_OPEN: Testing if load has normalized
 */

export type CircuitState = 'closed' | 'open' | 'half_open';

export interface CircuitBreakerConfig {
  /** Queue depth threshold to trip the breaker */
  queueDepthThreshold: number;
  /** CPU percentage threshold */
  cpuThreshold: number;
  /** Memory percentage threshold */
  memoryThreshold: number;
  /** How long to stay open before testing (ms) */
  resetTimeout: number;
  /** Number of successful requests to close from half-open */
  successThreshold: number;
}

export interface LoadCheckResult {
  allowed: boolean;
  delayed: boolean;
  estimatedWaitSeconds: number;
  message: string;
  circuitState: CircuitState;
}

const DEFAULT_CONFIG: CircuitBreakerConfig = {
  queueDepthThreshold: 500,
  cpuThreshold: 80,
  memoryThreshold: 85,
  resetTimeout: 60000, // 1 minute
  successThreshold: 5,
};

export class CircuitBreaker {
  private state: CircuitState = 'closed';
  private config: CircuitBreakerConfig;
  private lastTrippedAt: number = 0;
  private successCount: number = 0;
  private currentQueueDepth: number = 0;
  private currentCpuUsage: number = 0;
  private currentMemoryUsage: number = 0;
  
  constructor(config: Partial<CircuitBreakerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  
  /**
   * Update system metrics (called periodically or before checks)
   */
  updateMetrics(metrics: {
    queueDepth?: number;
    cpuUsage?: number;
    memoryUsage?: number;
  }): void {
    if (typeof metrics.queueDepth === 'number') {
      this.currentQueueDepth = metrics.queueDepth;
    }
    if (typeof metrics.cpuUsage === 'number') {
      this.currentCpuUsage = metrics.cpuUsage;
    }
    if (typeof metrics.memoryUsage === 'number') {
      this.currentMemoryUsage = metrics.memoryUsage;
    }
    
    // Check if we need to trip or reset
    this.evaluateState();
  }
  
  /**
   * Evaluate and potentially change circuit state
   */
  private evaluateState(): void {
    const shouldTrip = 
      this.currentQueueDepth > this.config.queueDepthThreshold ||
      this.currentCpuUsage > this.config.cpuThreshold ||
      this.currentMemoryUsage > this.config.memoryThreshold;
    
    if (this.state === 'closed' && shouldTrip) {
      this.trip();
    } else if (this.state === 'open') {
      // Check if we should try to recover
      const elapsed = Date.now() - this.lastTrippedAt;
      if (elapsed > this.config.resetTimeout) {
        this.state = 'half_open';
        this.successCount = 0;
        console.log('🔄 Circuit breaker entering half-open state');
      }
    } else if (this.state === 'half_open') {
      if (shouldTrip) {
        // Still under load, trip again
        this.trip();
      } else if (this.successCount >= this.config.successThreshold) {
        // Load has normalized, close the circuit
        this.reset();
      }
    }
  }
  
  /**
   * Trip the circuit breaker (enter open state)
   */
  trip(): void {
    this.state = 'open';
    this.lastTrippedAt = Date.now();
    this.successCount = 0;
    console.warn('⚡ Circuit breaker TRIPPED - Free tier requests will be delayed');
  }
  
  /**
   * Reset the circuit breaker (return to closed state)
   */
  reset(): void {
    this.state = 'closed';
    this.successCount = 0;
    console.log('✅ Circuit breaker RESET - Normal operation resumed');
  }
  
  /**
   * Record a successful request (for half-open state)
   */
  recordSuccess(): void {
    if (this.state === 'half_open') {
      this.successCount++;
      this.evaluateState();
    }
  }
  
  /**
   * Check if a free tier request should be delayed
   */
  checkFreeTier(): LoadCheckResult {
    this.evaluateState();
    
    if (this.state === 'closed') {
      return {
        allowed: true,
        delayed: false,
        estimatedWaitSeconds: 0,
        message: '',
        circuitState: this.state,
      };
    }
    
    // Open or half-open: delay free tier
    const estimatedWait = Math.min(300, Math.ceil(this.currentQueueDepth / 10));
    
    return {
      allowed: true, // Still allowed, just delayed
      delayed: true,
      estimatedWaitSeconds: estimatedWait,
      message: `High demand: Your file is queued. Estimated wait: ${estimatedWait} seconds. Paid tier bypasses queue.`,
      circuitState: this.state,
    };
  }
  
  /**
   * Check if a paid tier request should be delayed (rarely)
   */
  checkPaidTier(): LoadCheckResult {
    // Paid tier is almost never delayed
    // Only in extreme circumstances
    if (this.currentQueueDepth > this.config.queueDepthThreshold * 3) {
      return {
        allowed: true,
        delayed: true,
        estimatedWaitSeconds: 10,
        message: 'System under extreme load. Brief delay expected.',
        circuitState: this.state,
      };
    }
    
    return {
      allowed: true,
      delayed: false,
      estimatedWaitSeconds: 0,
      message: '',
      circuitState: this.state,
    };
  }
  
  /**
   * Get current state for monitoring
   */
  getStatus(): {
    state: CircuitState;
    queueDepth: number;
    cpuUsage: number;
    memoryUsage: number;
    lastTrippedAt: number | null;
  } {
    return {
      state: this.state,
      queueDepth: this.currentQueueDepth,
      cpuUsage: this.currentCpuUsage,
      memoryUsage: this.currentMemoryUsage,
      lastTrippedAt: this.lastTrippedAt || null,
    };
  }
}

// Export singleton instance
export const circuitBreaker = new CircuitBreaker();

/**
 * Middleware factory for circuit breaker
 */
export function createCircuitBreakerMiddleware(isPaidTier: (req: any) => boolean) {
  return async (req: any, res: any, next: any) => {
    const isPaid = isPaidTier(req);
    const check = isPaid ? circuitBreaker.checkPaidTier() : circuitBreaker.checkFreeTier();
    
    if (check.delayed) {
      // Add delay headers for client awareness
      res.setHeader('X-Queue-Delayed', 'true');
      res.setHeader('X-Estimated-Wait', check.estimatedWaitSeconds.toString());
      
      // For free tier, we might want to return early with queue info
      // For now, just add headers and proceed
    }
    
    // Store check result on request for downstream handlers
    req.circuitBreaker = check;
    
    next();
  };
}

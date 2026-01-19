/**
 * Security Event Logger
 * Logs security-critical events for audit trail
 */

import { v4 as uuidv4 } from 'uuid';

export interface AuditEvent {
  id: string;
  timestamp: string;
  event: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  userId?: string;
  sessionId?: string;
  requestId?: string;
  ip?: string;
  details: Record<string, unknown>;
}

class SecurityEventLogger {
  private events: AuditEvent[] = [];
  private maxEvents = 10000;

  /**
   * Log a security event
   */
  logEvent(event: Omit<AuditEvent, 'id' | 'timestamp'>): AuditEvent {
    const auditEvent: AuditEvent = {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      ...event,
    };

    // Log to console for visibility
    const level =
      auditEvent.severity === 'critical' || auditEvent.severity === 'error'
        ? 'error'
        : auditEvent.severity === 'warning'
          ? 'warn'
          : 'info';

    console[level](`[AUDIT] ${auditEvent.event}:`, {
      id: auditEvent.id,
      userId: auditEvent.userId,
      severity: auditEvent.severity,
      ...auditEvent.details,
    });

    // Store in memory (in production, this would go to database)
    this.events.push(auditEvent);

    // Trim old events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents);
    }

    return auditEvent;
  }

  /**
   * Log credit transaction
   */
  logCreditTransaction(params: {
    userId: string;
    type: 'reserve' | 'commit' | 'release' | 'purchase' | 'transfer';
    amount: number;
    balanceId: string;
    quoteId?: string;
    requestId?: string;
    description?: string;
  }): AuditEvent {
    return this.logEvent({
      event: `credit_${params.type}`,
      severity:
        params.type === 'purchase' || params.type === 'transfer'
          ? 'info'
          : 'info',
      userId: params.userId,
      details: {
        amount: params.amount,
        balanceId: params.balanceId,
        quoteId: params.quoteId,
        requestId: params.requestId,
        description: params.description,
      },
    });
  }

  /**
   * Log authentication event
   */
  logAuth(params: {
    userId?: string;
    type: 'login' | 'logout' | 'register' | 'token_refresh' | 'token_revoke';
    success: boolean;
    ip?: string;
    reason?: string;
  }): AuditEvent {
    return this.logEvent({
      event: `auth_${params.type}`,
      severity: params.success ? 'info' : 'warning',
      userId: params.userId,
      ip: params.ip,
      details: {
        success: params.success,
        reason: params.reason,
      },
    });
  }

  /**
   * Log extraction event
   */
  logExtraction(params: {
    userId: string;
    sessionId: string;
    fileType: string;
    fileSize: number;
    creditsUsed: number;
    success: boolean;
    error?: string;
  }): AuditEvent {
    return this.logEvent({
      event: 'extraction',
      severity: params.success ? 'info' : 'warning',
      userId: params.userId,
      sessionId: params.sessionId,
      details: {
        fileType: params.fileType,
        fileSize: params.fileSize,
        creditsUsed: params.creditsUsed,
        success: params.success,
        error: params.error,
      },
    });
  }

  /**
   * Log payment event
   */
  logPayment(params: {
    userId: string;
    paymentId: string;
    amount: number;
    credits: number;
    success: boolean;
    error?: string;
  }): AuditEvent {
    return this.logEvent({
      event: 'payment',
      severity: params.success ? 'info' : 'critical',
      userId: params.userId,
      details: {
        paymentId: params.paymentId,
        amount: params.amount,
        credits: params.credits,
        success: params.success,
        error: params.error,
      },
    });
  }

  /**
   * Get recent events (for debugging/admin)
   */
  getRecentEvents(limit = 100): AuditEvent[] {
    return this.events.slice(-limit);
  }

  /**
   * Get events for a specific user
   */
  getEventsForUser(userId: string): AuditEvent[] {
    return this.events.filter(e => e.userId === userId);
  }

  /**
   * Clear all events (for testing)
   */
  clear(): void {
    this.events = [];
  }
}

// Singleton instance
export const securityEventLogger = new SecurityEventLogger();

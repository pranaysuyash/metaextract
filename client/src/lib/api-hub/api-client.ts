/**
 * API Hub - Centralized API management and integration system
 */

import { v4 as uuidv4 } from 'uuid';

export interface ApiKey {
  id: string;
  userId: string;
  key: string;
  name: string;
  permissions: string[];
  createdAt: Date;
  lastUsedAt?: Date;
  expiresAt?: Date;
  isActive: boolean;
}

export interface ApiUsageRecord {
  id: string;
  apiKeyId: string;
  userId: string;
  endpoint: string;
  method: string;
  statusCode: number;
  responseTime: number; // in ms
  requestSize: number; // in bytes
  responseSize: number; // in bytes
  timestamp: Date;
  ip: string;
  userAgent?: string;
}

export interface Webhook {
  id: string;
  userId: string;
  url: string;
  events: string[]; // ['extraction.completed', 'file.uploaded', etc.]
  secret: string;
  isActive: boolean;
  createdAt: Date;
  lastTriggeredAt?: Date;
  failureCount: number;
}

export interface WebhookEvent {
  id: string;
  webhookId: string;
  event: string;
  payload: any;
  status: 'pending' | 'sent' | 'failed';
  attempts: number;
  createdAt: Date;
  sentAt?: Date;
  error?: string;
}

export interface RateLimitConfig {
  windowMs: number; // Time window in milliseconds
  maxRequests: number; // Max requests per window
  tier: 'free' | 'professional' | 'forensic' | 'enterprise';
  endpoint?: string; // Specific endpoint, or global if undefined
}

export interface ApiHubConfig {
  defaultRateLimit: RateLimitConfig;
  webhookTimeout: number; // in ms
  maxPayloadSize: number; // in bytes
  corsOrigins: string[];
}

export class ApiHub {
  private apiKeys: Map<string, ApiKey> = new Map();
  private usageRecords: ApiUsageRecord[] = [];
  private webhooks: Map<string, Webhook> = new Map();
  private webhookEvents: Map<string, WebhookEvent[]> = new Map();
  private rateLimits: Map<string, RateLimitConfig[]> = new Map(); // userId -> limits
  private config: ApiHubConfig;

  constructor(config?: Partial<ApiHubConfig>) {
    this.config = {
      defaultRateLimit: {
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 100,
        tier: 'free'
      },
      webhookTimeout: 10000, // 10 seconds
      maxPayloadSize: 10 * 1024 * 1024, // 10MB
      corsOrigins: ['*'],
      ...config
    };
  }

  /**
   * Generate a new API key for a user
   */
  async generateApiKey(userId: string, name: string, permissions: string[] = []): Promise<ApiKey> {
    const apiKey: ApiKey = {
      id: uuidv4(),
      userId,
      key: this.generateSecureApiKey(),
      name,
      permissions,
      createdAt: new Date(),
      isActive: true
    };

    this.apiKeys.set(apiKey.id, apiKey);
    return apiKey;
  }

  /**
   * Generate a secure API key
   */
  private generateSecureApiKey(): string {
    // Generate a secure random API key
    return `meta_${uuidv4().replace(/-/g, '')}`;
  }

  /**
   * Validate an API key
   */
  async validateApiKey(key: string): Promise<ApiKey | null> {
    for (const apiKey of this.apiKeys.values()) {
      if (apiKey.key === key && apiKey.isActive) {
        // Update last used timestamp
        apiKey.lastUsedAt = new Date();
        return apiKey;
      }
    }
    return null;
  }

  /**
   * Revoke an API key
   */
  async revokeApiKey(keyId: string, userId: string): Promise<boolean> {
    const key = this.apiKeys.get(keyId);
    if (!key || key.userId !== userId) {
      return false;
    }

    key.isActive = false;
    return true;
  }

  /**
   * Record API usage
   */
  async recordUsage(
    apiKeyId: string,
    userId: string,
    endpoint: string,
    method: string,
    statusCode: number,
    responseTime: number,
    requestSize: number,
    responseSize: number,
    ip: string,
    userAgent?: string
  ): Promise<void> {
    const usage: ApiUsageRecord = {
      id: uuidv4(),
      apiKeyId,
      userId,
      endpoint,
      method,
      statusCode,
      responseTime,
      requestSize,
      responseSize,
      timestamp: new Date(),
      ip,
      userAgent
    };

    this.usageRecords.push(usage);

    // Keep only last 10000 records to prevent memory issues
    if (this.usageRecords.length > 10000) {
      this.usageRecords = this.usageRecords.slice(-10000);
    }
  }

  /**
   * Get API usage for a user
   */
  async getUsage(
    userId: string,
    startDate?: Date,
    endDate?: Date,
    limit: number = 100
  ): Promise<ApiUsageRecord[]> {
    let records = this.usageRecords.filter(record => record.userId === userId);

    if (startDate) {
      records = records.filter(record => record.timestamp >= startDate);
    }

    if (endDate) {
      records = records.filter(record => record.timestamp <= endDate);
    }

    // Sort by timestamp descending and limit
    return records
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  /**
   * Get API usage summary for a user
   */
  async getUsageSummary(userId: string, days = 30): Promise<{
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    avgResponseTime: number;
    totalDataTransferred: number;
    requestsByEndpoint: Record<string, number>;
    requestsByMethod: Record<string, number>;
  }> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const userRecords = this.usageRecords.filter(
      record => record.userId === userId && record.timestamp >= cutoffDate
    );

    const totalRequests = userRecords.length;
    const successfulRequests = userRecords.filter(r => r.statusCode >= 200 && r.statusCode < 300).length;
    const failedRequests = userRecords.filter(r => r.statusCode >= 400).length;
    const avgResponseTime = userRecords.length > 0
      ? userRecords.reduce((sum, r) => sum + r.responseTime, 0) / userRecords.length
      : 0;
    const totalDataTransferred = userRecords.reduce((sum, r) => sum + r.responseSize, 0);

    const requestsByEndpoint: Record<string, number> = {};
    const requestsByMethod: Record<string, number> = {};

    for (const record of userRecords) {
      requestsByEndpoint[record.endpoint] = (requestsByEndpoint[record.endpoint] || 0) + 1;
      requestsByMethod[record.method] = (requestsByMethod[record.method] || 0) + 1;
    }

    return {
      totalRequests,
      successfulRequests,
      failedRequests,
      avgResponseTime,
      totalDataTransferred,
      requestsByEndpoint,
      requestsByMethod
    };
  }

  /**
   * Create a new webhook
   */
  async createWebhook(
    userId: string,
    url: string,
    events: string[],
    name?: string
  ): Promise<Webhook> {
    const webhook: Webhook = {
      id: uuidv4(),
      userId,
      url,
      events,
      secret: this.generateWebhookSecret(),
      isActive: true,
      createdAt: new Date(),
      failureCount: 0
    };

    this.webhooks.set(webhook.id, webhook);
    this.webhookEvents.set(webhook.id, []);
    return webhook;
  }

  /**
   * Generate a secure webhook secret
   */
  private generateWebhookSecret(): string {
    return `whsec_${uuidv4().replace(/-/g, '')}`;
  }

  /**
   * Update a webhook
   */
  async updateWebhook(
    webhookId: string,
    userId: string,
    updates: Partial<Webhook>
  ): Promise<boolean> {
    const webhook = this.webhooks.get(webhookId);
    if (!webhook || webhook.userId !== userId) {
      return false;
    }

    Object.assign(webhook, updates);
    return true;
  }

  /**
   * Delete a webhook
   */
  async deleteWebhook(webhookId: string, userId: string): Promise<boolean> {
    const webhook = this.webhooks.get(webhookId);
    if (!webhook || webhook.userId !== userId) {
      return false;
    }

    this.webhooks.delete(webhookId);
    this.webhookEvents.delete(webhookId);
    return true;
  }

  /**
   * Trigger a webhook event
   */
  async triggerWebhookEvent(
    userId: string,
    event: string,
    payload: any
  ): Promise<void> {
    // Find all active webhooks for this user that listen to this event
    const userWebhooks = Array.from(this.webhooks.values()).filter(
      wh => wh.userId === userId && wh.isActive && wh.events.includes(event)
    );

    for (const webhook of userWebhooks) {
      const webhookEvent: WebhookEvent = {
        id: uuidv4(),
        webhookId: webhook.id,
        event,
        payload,
        status: 'pending',
        attempts: 0,
        createdAt: new Date()
      };

      // Add to webhook's event queue
      if (!this.webhookEvents.has(webhook.id)) {
        this.webhookEvents.set(webhook.id, []);
      }
      this.webhookEvents.get(webhook.id)!.push(webhookEvent);

      // Attempt to send the webhook (in a real implementation, this would be done asynchronously)
      await this.sendWebhook(webhook, webhookEvent);
    }
  }

  /**
   * Send a webhook event
   */
  private async sendWebhook(webhook: Webhook, event: WebhookEvent): Promise<void> {
    try {
      // In a real implementation, we would make an HTTP request to the webhook URL
      // For now, we'll just simulate the process
      console.log(`Simulating webhook to ${webhook.url} for event ${event.event}`);

      // Update event status
      event.status = 'sent';
      event.sentAt = new Date();
      event.attempts += 1;

      // Update webhook last triggered time
      webhook.lastTriggeredAt = new Date();
    } catch (error) {
      event.status = 'failed';
      event.error = (error as Error).message;
      event.attempts += 1;
      webhook.failureCount += 1;
    }
  }

  /**
   * Get webhooks for a user
   */
  async getUserWebhooks(userId: string): Promise<Webhook[]> {
    return Array.from(this.webhooks.values()).filter(wh => wh.userId === userId);
  }

  /**
   * Get webhook events
   */
  async getWebhookEvents(
    webhookId: string,
    userId: string,
    limit: number = 50
  ): Promise<WebhookEvent[]> {
    const webhook = this.webhooks.get(webhookId);
    if (!webhook || webhook.userId !== userId) {
      return [];
    }

    const events = this.webhookEvents.get(webhookId) || [];
    return events
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  /**
   * Set rate limit for a user
   */
  async setRateLimit(
    userId: string,
    config: RateLimitConfig
  ): Promise<void> {
    if (!this.rateLimits.has(userId)) {
      this.rateLimits.set(userId, []);
    }

    const limits = this.rateLimits.get(userId)!;
    
    // Check if there's already a limit for this endpoint/tier combination
    const existingIndex = limits.findIndex(l => 
      l.tier === config.tier && l.endpoint === config.endpoint
    );

    if (existingIndex !== -1) {
      limits[existingIndex] = config;
    } else {
      limits.push(config);
    }
  }

  /**
   * Get rate limits for a user
   */
  async getRateLimits(userId: string): Promise<RateLimitConfig[]> {
    return this.rateLimits.get(userId) || [this.config.defaultRateLimit];
  }

  /**
   * Check if a request is rate limited
   */
  async isRateLimited(
    userId: string,
    apiKeyId: string,
    endpoint: string,
    method: string
  ): Promise<{ isLimited: boolean; resetTime?: Date; limit?: number; remaining?: number }> {
    const limits = await this.getRateLimits(userId);
    
    // Find the most specific rate limit (endpoint-specific first, then tier-specific)
    const applicableLimit = limits.find(l => l.endpoint === endpoint) ||
      limits.find(l => !l.endpoint) ||
      this.config.defaultRateLimit;

    // In a real implementation, we would check the actual request count
    // against the time window to determine if the user is rate limited
    // For now, we'll return a mock response indicating not limited
    return {
      isLimited: false,
      resetTime: new Date(Date.now() + applicableLimit.windowMs),
      limit: applicableLimit.maxRequests,
      remaining: applicableLimit.maxRequests
    };
  }

  /**
   * Get API documentation
   */
  getApiDocumentation(): any {
    return {
      version: '1.0.0',
      title: 'MetaExtract API',
      description: 'Comprehensive metadata extraction API',
      endpoints: [
        {
          path: '/api/extract',
          method: 'POST',
          description: 'Extract metadata from a file',
          parameters: [
            { name: 'file', type: 'binary', required: true, description: 'File to extract metadata from' },
            { name: 'tier', type: 'string', required: false, description: 'Extraction tier (free, professional, forensic, enterprise)' }
          ],
          responses: [
            { code: 200, description: 'Successful extraction' },
            { code: 400, description: 'Bad request' },
            { code: 401, description: 'Unauthorized' },
            { code: 402, description: 'Payment required' },
            { code: 429, description: 'Rate limited' }
          ]
        },
        {
          path: '/api/extract/batch',
          method: 'POST',
          description: 'Extract metadata from multiple files',
          parameters: [
            { name: 'files', type: 'array', required: true, description: 'Array of files to extract metadata from' },
            { name: 'tier', type: 'string', required: false, description: 'Extraction tier' }
          ],
          responses: [
            { code: 200, description: 'Successful batch extraction' },
            { code: 400, description: 'Bad request' },
            { code: 401, description: 'Unauthorized' },
            { code: 402, description: 'Payment required' },
            { code: 429, description: 'Rate limited' }
          ]
        },
        {
          path: '/api/webhooks',
          method: 'POST',
          description: 'Create a new webhook',
          parameters: [
            { name: 'url', type: 'string', required: true, description: 'Webhook URL' },
            { name: 'events', type: 'array', required: true, description: 'Events to listen for' }
          ],
          responses: [
            { code: 201, description: 'Webhook created' },
            { code: 400, description: 'Bad request' },
            { code: 401, description: 'Unauthorized' }
          ]
        }
      ],
      rateLimits: {
        free: { requestsPerMinute: 10 },
        professional: { requestsPerMinute: 100 },
        forensic: { requestsPerMinute: 500 },
        enterprise: { requestsPerMinute: 1000 }
      },
      authentication: {
        method: 'API Key',
        header: 'Authorization: Bearer YOUR_API_KEY'
      }
    };
  }
}

// Singleton instance
export const apiHub = new ApiHub();

export default apiHub;

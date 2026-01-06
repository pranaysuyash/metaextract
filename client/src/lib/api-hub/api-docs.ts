/**
 * API Documentation - Auto-generated API docs and SDK
 */

export interface ApiEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters: ApiParameter[];
  requestBody?: ApiRequestBody;
  responses: ApiResponse[];
  authRequired: boolean;
  rateLimitTier: 'free' | 'professional' | 'forensic' | 'enterprise';
}

export interface ApiParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description: string;
  example?: any;
}

export interface ApiRequestBody {
  description: string;
  required: boolean;
  schema: any;
  example?: any;
}

export interface ApiResponse {
  code: number;
  description: string;
  schema?: any;
  example?: any;
}

export interface ApiDocumentation {
  version: string;
  title: string;
  description: string;
  endpoints: ApiEndpoint[];
  rateLimits: {
    free: { requestsPerMinute: number };
    professional: { requestsPerMinute: number };
    forensic: { requestsPerMinute: number };
    enterprise: { requestsPerMinute: number };
  };
  authentication: {
    method: string;
    header: string;
  };
}

export interface WebhookEventDefinition {
  name: string;
  description: string;
  payloadSchema: any;
  examplePayload: any;
}

export interface WebhookDefinition {
  id: string;
  name: string;
  description: string;
  events: WebhookEventDefinition[];
  url: string;
  secretRequired: boolean;
}

export class ApiDocs {
  /**
   * Generate API documentation
   */
  static generateDocumentation(): ApiDocumentation {
    return {
      version: '1.0.0',
      title: 'MetaExtract API',
      description: 'Comprehensive metadata extraction API with advanced forensic capabilities',
      endpoints: [
        {
          path: '/api/extract',
          method: 'POST',
          description: 'Extract metadata from a file with comprehensive analysis',
          parameters: [
            {
              name: 'tier',
              type: 'string',
              required: false,
              description: 'Extraction tier (free, professional, forensic, enterprise)',
              example: 'professional'
            },
            {
              name: 'includeAdvanced',
              type: 'boolean',
              required: false,
              description: 'Include advanced forensic analysis',
              example: true
            }
          ],
          requestBody: {
            description: 'File to extract metadata from',
            required: true,
            schema: {
              type: 'object',
              properties: {
                file: {
                  type: 'string',
                  format: 'binary',
                  description: 'File to extract metadata from'
                },
                options: {
                  type: 'object',
                  properties: {
                    tier: { type: 'string', enum: ['free', 'professional', 'forensic', 'enterprise'] },
                    includeAdvanced: { type: 'boolean' }
                  }
                }
              }
            }
          },
          responses: [
            {
              code: 200,
              description: 'Successful metadata extraction',
              schema: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  metadata: { type: 'object' },
                  analysis: { type: 'object' },
                  confidence: { type: 'number' }
                }
              },
              example: {
                id: 'abc123',
                metadata: { make: 'Canon', model: 'EOS R5', datetime: '2025-01-05T10:30:00Z' },
                analysis: { authenticity: 'high', gps: { lat: 37.7749, lng: -122.4194 } },
                confidence: 95
              }
            },
            {
              code: 400,
              description: 'Bad request - invalid file or parameters',
              example: { error: 'Invalid file format' }
            },
            {
              code: 401,
              description: 'Unauthorized - invalid API key',
              example: { error: 'Invalid API key' }
            },
            {
              code: 402,
              description: 'Payment required - insufficient credits',
              example: { error: 'Insufficient credits' }
            },
            {
              code: 429,
              description: 'Rate limited - too many requests',
              example: { error: 'Rate limit exceeded' }
            }
          ],
          authRequired: true,
          rateLimitTier: 'free'
        },
        {
          path: '/api/extract/batch',
          method: 'POST',
          description: 'Extract metadata from multiple files in a batch operation',
          parameters: [
            {
              name: 'tier',
              type: 'string',
              required: false,
              description: 'Extraction tier for all files',
              example: 'forensic'
            }
          ],
          requestBody: {
            description: 'Multiple files to extract metadata from',
            required: true,
            schema: {
              type: 'object',
              properties: {
                files: {
                  type: 'array',
                  items: {
                    type: 'string',
                    format: 'binary'
                  }
                },
                options: {
                  type: 'object',
                  properties: {
                    tier: { type: 'string', enum: ['free', 'professional', 'forensic', 'enterprise'] },
                    includeAdvanced: { type: 'boolean' }
                  }
                }
              }
            }
          },
          responses: [
            {
              code: 200,
              description: 'Successful batch extraction',
              schema: {
                type: 'object',
                properties: {
                  results: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        id: { type: 'string' },
                        filename: { type: 'string' },
                        metadata: { type: 'object' },
                        analysis: { type: 'object' },
                        confidence: { type: 'number' }
                      }
                    }
                  }
                }
              },
              example: {
                results: [
                  {
                    id: 'def456',
                    filename: 'image1.jpg',
                    metadata: { make: 'Nikon', model: 'D850' },
                    analysis: { authenticity: 'medium' },
                    confidence: 85
                  }
                ]
              }
            }
          ],
          authRequired: true,
          rateLimitTier: 'professional'
        },
        {
          path: '/api/webhooks',
          method: 'POST',
          description: 'Create a new webhook to receive event notifications',
          parameters: [],
          requestBody: {
            description: 'Webhook configuration',
            required: true,
            schema: {
              type: 'object',
              properties: {
                url: { type: 'string', description: 'URL to send webhook events to' },
                events: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'List of events to subscribe to'
                }
              }
            }
          },
          responses: [
            {
              code: 201,
              description: 'Webhook created successfully',
              schema: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  url: { type: 'string' },
                  events: { type: 'array', items: { type: 'string' } },
                  secret: { type: 'string', description: 'Webhook secret for verification' }
                }
              }
            }
          ],
          authRequired: true,
          rateLimitTier: 'professional'
        },
        {
          path: '/api/analytics',
          method: 'GET',
          description: 'Get analytics and usage statistics',
          parameters: [
            {
              name: 'startDate',
              type: 'string',
              required: false,
              description: 'Start date for analytics (ISO format)',
              example: '2025-01-01T00:00:00Z'
            },
            {
              name: 'endDate',
              type: 'string',
              required: false,
              description: 'End date for analytics (ISO format)',
              example: '2025-01-31T23:59:59Z'
            }
          ],
          requestBody: undefined,
          responses: [
            {
              code: 200,
              description: 'Analytics data retrieved successfully',
              schema: {
                type: 'object',
                properties: {
                  extractions: { type: 'number' },
                  successRate: { type: 'number' },
                  avgProcessingTime: { type: 'number' },
                  topFormats: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        format: { type: 'string' },
                        count: { type: 'number' }
                      }
                    }
                  }
                }
              }
            }
          ],
          authRequired: true,
          rateLimitTier: 'professional'
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

  /**
   * Generate webhook documentation
   */
  static generateWebhookDocumentation(): WebhookDefinition[] {
    return [
      {
        id: 'extraction.completed',
        name: 'Extraction Completed',
        description: 'Triggered when a metadata extraction is completed',
        events: [
          {
            name: 'extraction.completed',
            description: 'Sent when metadata extraction is completed',
            payloadSchema: {
              type: 'object',
              properties: {
                extractionId: { type: 'string' },
                filename: { type: 'string' },
                metadata: { type: 'object' },
                analysis: { type: 'object' },
                completedAt: { type: 'string', format: 'date-time' }
              }
            },
            examplePayload: {
              extractionId: 'abc123',
              filename: 'photo.jpg',
              metadata: { make: 'Canon', model: 'EOS R5' },
              analysis: { authenticity: 'high' },
              completedAt: '2025-01-05T10:30:00Z'
            }
          }
        ],
        url: 'https://your-domain.com/webhook',
        secretRequired: true
      },
      {
        id: 'file.uploaded',
        name: 'File Uploaded',
        description: 'Triggered when a file is successfully uploaded',
        events: [
          {
            name: 'file.uploaded',
            description: 'Sent when a file is uploaded successfully',
            payloadSchema: {
              type: 'object',
              properties: {
                fileId: { type: 'string' },
                filename: { type: 'string' },
                size: { type: 'number' },
                mimeType: { type: 'string' },
                uploadedAt: { type: 'string', format: 'date-time' }
              }
            },
            examplePayload: {
              fileId: 'def456',
              filename: 'document.pdf',
              size: 1024000,
              mimeType: 'application/pdf',
              uploadedAt: '2025-01-05T10:29:00Z'
            }
          }
        ],
        url: 'https://your-domain.com/webhook',
        secretRequired: true
      }
    ];
  }

  /**
   * Generate SDK documentation
   */
  static generateSdkDocumentation(): string {
    return `
# MetaExtract JavaScript SDK

## Installation

\`\`\`bash
npm install @metaextract/sdk
\`\`\`

## Usage

\`\`\`javascript
import { MetaExtractClient } from '@metaextract/sdk';

const client = new MetaExtractClient({
  apiKey: 'YOUR_API_KEY'
});

// Extract metadata from a file
const result = await client.extract(file, {
  tier: 'professional',
  includeAdvanced: true
});

console.log(result.metadata);
console.log(result.analysis);
\`\`\`

## Webhook Verification

\`\`\`javascript
import { verifyWebhookSignature } from '@metaextract/sdk';

const isValid = verifyWebhookSignature(
  payload,
  signature,
  secret
);

if (isValid) {
  // Process webhook
}
\`\`\`

## Rate Limiting

The API enforces rate limits based on your subscription tier:
- Free: 10 requests per minute
- Professional: 100 requests per minute
- Forensic: 500 requests per minute
- Enterprise: 1000 requests per minute

Exceeding the rate limit will result in a 429 response code.
    `;
  }

  /**
   * Get rate limit information for a tier
   */
  static getRateLimitInfo(tier: 'free' | 'professional' | 'forensic' | 'enterprise'): { requestsPerMinute: number; description: string } {
    const limits = {
      free: { requestsPerMinute: 10, description: 'Basic usage tier' },
      professional: { requestsPerMinute: 100, description: 'Professional usage tier' },
      forensic: { requestsPerMinute: 500, description: 'Forensic analysis tier' },
      enterprise: { requestsPerMinute: 1000, description: 'Enterprise usage tier' }
    };

    return limits[tier];
  }
}

// Export the documentation
export const apiDocumentation = ApiDocs.generateDocumentation();
export const webhookDocumentation = ApiDocs.generateWebhookDocumentation();
export const sdkDocumentation = ApiDocs.generateSdkDocumentation();

export default ApiDocs;
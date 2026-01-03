/**
 * LLM-powered Findings Extraction
 *
 * Uses AI to generate plain English answers from metadata
 * Supports multiple providers: Claude (primary), OpenAI (fallback), Gemini (fallback)
 * 
 * Features:
 * - Input size validation (max 500KB)
 * - Request timeout handling (15s)
 * - Proper HTTP error codes (502, 503, 504)
 * - Environment-driven configuration
 * - Robust JSON parsing
 * - Graceful fallback to rule-based extraction
 * - Stricter rate limiting (10 req/min, 100/day) for expensive LLM calls
 * - Multi-provider support with automatic fallback
 */

import type { Express } from 'express';
import { rateLimitExtraction } from '../rateLimitMiddleware';

// Configuration constants
const MAX_METADATA_SIZE = 500 * 1024; // 500 KB
const LLM_TIMEOUT_MS = 15000; // 15 seconds

// Provider configurations
const PROVIDERS = {
  CLAUDE: {
    baseUrl: process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com/v1',
    model: process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022',
    apiKey: process.env.ANTHROPIC_API_KEY,
  },
  OPENAI: {
    baseUrl: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
    model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
    apiKey: process.env.OPENAI_API_KEY,
  },
  GEMINI: {
    baseUrl: process.env.GEMINI_BASE_URL || 'https://generativelanguage.googleapis.com/v1beta',
    model: process.env.GEMINI_MODEL || 'gemini-1.5-flash',
    apiKey: process.env.GEMINI_API_KEY,
  },
} as const;

const NODE_ENV = process.env.NODE_ENV || 'development';

// Safe logging with metadata redaction
function safeLog(label: string, data?: unknown) {
  if (NODE_ENV === 'development') {
    // In development, log with minimal redaction
    const message = data ? `${label} ${JSON.stringify(data)}` : label;
    console.log(`[${new Date().toISOString()}] ${message}`);
  } else {
    // In production, redact sensitive fields
    const sanitized = data ? sanitizeForLogging(data) : undefined;
    const message = sanitized ? `${label} ${JSON.stringify(sanitized)}` : label;
    console.log(`[${new Date().toISOString()}] ${message}`);
  }
}

function sanitizeForLogging(obj: unknown): unknown {
  if (!obj || typeof obj !== 'object') return obj;
  
  const keys = ['password', 'apiKey', 'api_key', 'token', 'secret', 'metadata'];
  const result = Array.isArray(obj) ? [...obj] : { ...(obj as Record<string, unknown>) };
  
  for (const key in result) {
    if (keys.some(k => key.toLowerCase().includes(k.toLowerCase()))) {
      (result as Record<string, unknown>)[key] = '[REDACTED]';
    } else if (typeof (result as Record<string, unknown>)[key] === 'object') {
      (result as Record<string, unknown>)[key] = sanitizeForLogging((result as Record<string, unknown>)[key]);
    }
  }
  return result;
}

export function registerLLMFindingsRoutes(app: Express): void {
  // Apply stricter rate limiting for expensive LLM operations
  app.post('/api/metadata/findings',
    rateLimitExtraction({
      enabled: true,
      // Even stricter limits for LLM calls (expensive external API)
      endpoints: {
        requestsPerMinute: 10, // Much lower than default extraction limits
        requestsPerDay: 100,   // Conservative daily limit
        burstLimit: 2,         // Very low burst to prevent API abuse
      },
    }),
    async (req, res) => {
    try {
      const { metadata } = req.body;

      // Validate metadata presence
      if (!metadata) {
        safeLog('[LLM Findings] Missing metadata in request');
        return res.status(400).json({ error: 'Metadata required' });
      }

      // Validate metadata size
      const metadataSize = Buffer.byteLength(JSON.stringify(metadata));
      if (metadataSize > MAX_METADATA_SIZE) {
        safeLog('[LLM Findings] Metadata size exceeds limit', {
          size: metadataSize,
          limit: MAX_METADATA_SIZE,
        });
        return res.status(413).json({
          error: 'Metadata too large',
          details: `Maximum ${MAX_METADATA_SIZE / 1024}KB allowed`,
        });
      }

      // Validate basic metadata structure
      if (typeof metadata !== 'object') {
        safeLog('[LLM Findings] Invalid metadata type:', typeof metadata);
        return res.status(400).json({ error: 'Metadata must be an object' });
      }

      // Check if any LLM provider is configured
      const availableProviders = Object.entries(PROVIDERS)
        .filter(([_, config]) => config.apiKey)
        .map(([name]) => name);

      if (availableProviders.length === 0) {
        safeLog('[LLM Findings] No LLM API keys configured, falling back to rule-based extraction');
        // Return null to trigger fallback to rule-based extraction
        return res.json({ findings: null });
      }

      safeLog('[LLM Findings] Available providers:', availableProviders);

      // Call LLM providers in order: Claude → OpenAI → Gemini
      const findings = await extractFindingsWithLLM(metadata);

      res.json({ findings });
    } catch (error) {
      // Distinguish between timeout, API errors, and other errors
      if (error instanceof Error) {
        if (error.message.includes('timeout') || error.message.includes('AbortError')) {
          safeLog('[LLM Findings] Request timeout after 15 seconds');
          return res.status(504).json({
            error: 'LLM request timeout',
            findings: null,
          });
        }

        if (error.message.includes('Claude API error')) {
          safeLog('[LLM Findings] Claude API error:', error.message);
          return res.status(502).json({
            error: 'LLM service unavailable',
            findings: null,
          });
        }

        safeLog('[LLM Findings] Extraction error:', error.message);
      } else {
        safeLog('[LLM Findings] Unexpected error:', String(error));
      }

      // Generic error response
      return res.status(500).json({
        error: 'LLM extraction failed',
        findings: null,
      });
    }
  });
}

interface Finding {
  icon: string;
  label: string;
  value: string;
  confidence?: 'high' | 'medium' | 'low';
  status?: 'success' | 'warning' | 'error';
}

async function extractFindingsWithLLM(metadata: Record<string, unknown>): Promise<Finding[]> {
  const prompt = `You are a metadata analyst. Analyze this file metadata and answer these questions in plain English:

1. WHEN was this file created? (Look for photo taken date, file creation date, etc.)
2. WHERE was it taken? (GPS coordinates if available)
3. DEVICE that created it? (Camera make/model, phone model, etc.)
4. AUTHENTICITY assessment? (Check for manipulation indicators, date mismatches, etc.)

Metadata:
\`\`\`json
${JSON.stringify(metadata, null, 2)}
\`\`\`

Respond with a JSON array of findings. Each finding should have:
- icon: one of ["Calendar", "MapPin", "Smartphone", "Shield"]
- label: one of ["WHEN", "WHERE", "DEVICE", "AUTHENTICITY"]
- value: Plain English answer (e.g., "June 15, 2023 at 2:30 PM" not "2023:06:15 14:30:22")
- confidence: "high", "medium", or "low"
- status: "success", "warning", or "error" (warning for missing data, error for manipulation)

If data is missing, be honest: "Date not available in metadata" with status: "warning".
For GPS, show coordinates AND try to describe general area if recognizable.
For device, use friendly names: "iPhone 13 Pro" not "iPhone14,2".

Return ONLY the JSON array, no explanation.`;

  // Try providers in order: Claude → OpenAI → Gemini
  const providers = [
    { name: 'Claude', config: PROVIDERS.CLAUDE, func: extractFindingsWithClaude },
    { name: 'OpenAI', config: PROVIDERS.OPENAI, func: extractFindingsWithOpenAI },
    { name: 'Gemini', config: PROVIDERS.GEMINI, func: extractFindingsWithGemini },
  ];

  for (const { name, config, func } of providers) {
    if (config.apiKey) {
      try {
        safeLog(`[LLM Findings] Trying provider: ${name}`);
        const findings = await func(metadata, config.apiKey, prompt);
        safeLog(`[LLM Findings] Success with provider: ${name}`);
        return findings;
      } catch (error) {
        safeLog(`[LLM Findings] Provider ${name} failed:`, error instanceof Error ? error.message : String(error));
        // Continue to next provider
      }
    } else {
      safeLog(`[LLM Findings] Provider ${name} not configured (no API key)`);
    }
  }

  // All providers failed
  throw new Error('All LLM providers failed');
}

async function extractFindingsWithClaude(
  metadata: Record<string, unknown>,
  apiKey: string,
  prompt: string
): Promise<Finding[]> {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), LLM_TIMEOUT_MS);

  try {
    const response = await fetch(`${PROVIDERS.CLAUDE.baseUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: PROVIDERS.CLAUDE.model,
        max_tokens: 1024,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.content?.[0]?.text;

    if (!content) {
      throw new Error('No response from Claude');
    }

    return parseFindingsResponse(content);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('timeout: Claude request exceeded ' + LLM_TIMEOUT_MS + 'ms');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function extractFindingsWithOpenAI(
  metadata: Record<string, unknown>,
  apiKey: string,
  prompt: string
): Promise<Finding[]> {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), LLM_TIMEOUT_MS);

  try {
    const response = await fetch(`${PROVIDERS.OPENAI.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: PROVIDERS.OPENAI.model,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
        max_tokens: 1024,
        temperature: 0.1,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content;

    if (!content) {
      throw new Error('No response from OpenAI');
    }

    return parseFindingsResponse(content);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('timeout: OpenAI request exceeded ' + LLM_TIMEOUT_MS + 'ms');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function extractFindingsWithGemini(
  metadata: Record<string, unknown>,
  apiKey: string,
  prompt: string
): Promise<Finding[]> {
  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), LLM_TIMEOUT_MS);

  try {
    const response = await fetch(`${PROVIDERS.GEMINI.baseUrl}/models/${PROVIDERS.GEMINI.model}:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: prompt,
              },
            ],
          },
        ],
        generationConfig: {
          maxOutputTokens: 1024,
          temperature: 0.1,
        },
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!content) {
      throw new Error('No response from Gemini');
    }

    return parseFindingsResponse(content);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('timeout: Gemini request exceeded ' + LLM_TIMEOUT_MS + 'ms');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

function parseFindingsResponse(content: string): Finding[] {
  // Improved JSON parsing: extract code block or direct JSON
  let findings: Finding[] = [];

  // Try to parse direct JSON first
  try {
    const trimmed = content.trim();
    if (trimmed.startsWith('[')) {
      findings = JSON.parse(trimmed);
    } else {
      // Try to find JSON array in markdown code block
      const codeBlockMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (codeBlockMatch) {
        findings = JSON.parse(codeBlockMatch[1].trim());
      } else {
        // Fallback: look for any valid JSON array
        const jsonMatch = content.match(/\[[\s\S]*?\]/);
        if (jsonMatch) {
          findings = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('No valid JSON array found in response');
        }
      }
    }
  } catch (parseError) {
    safeLog('[LLM Findings] JSON parse error:', parseError instanceof Error ? parseError.message : String(parseError));
    throw new Error('Failed to parse LLM response');
  }

  // Validate findings structure
  if (!Array.isArray(findings)) {
    throw new Error('Response is not an array');
  }

  // Map and validate findings
  const validatedFindings: Finding[] = [];
  for (const f of findings) {
    if (f && typeof f === 'object') {
      const found = f as unknown as Record<string, unknown>;
      validatedFindings.push({
        icon: String(found.icon || '').replace(/"/g, ''),
        label: String(found.label || ''),
        value: String(found.value || ''),
        confidence: ['high', 'medium', 'low'].includes(String(found.confidence))
          ? (String(found.confidence) as 'high' | 'medium' | 'low')
          : 'medium',
        status: ['success', 'warning', 'error'].includes(String(found.status))
          ? (String(found.status) as 'success' | 'warning' | 'error')
          : 'warning',
      });
    }
  }

  return validatedFindings;
}

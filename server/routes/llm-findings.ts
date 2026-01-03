/**
 * LLM-powered Findings Extraction
 *
 * Uses AI to generate plain English answers from metadata
 */

import type { Express } from 'express';

export function registerLLMFindingsRoutes(app: Express): void {
  app.post('/api/metadata/findings', async (req, res) => {
    try {
      const { metadata } = req.body;

      if (!metadata) {
        return res.status(400).json({ error: 'Metadata required' });
      }

      // Check if Anthropic API key is configured
      const apiKey = process.env.ANTHROPIC_API_KEY;
      if (!apiKey) {
        // Return null to trigger fallback to rule-based extraction
        return res.json({ findings: null });
      }

      // Call Claude API to extract findings
      const findings = await extractFindingsWithClaude(metadata, apiKey);

      res.json({ findings });
    } catch (error) {
      console.error('[LLM Findings] Error:', error);
      // Return null instead of error to trigger graceful fallback
      res.json({ findings: null });
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

async function extractFindingsWithClaude(
  metadata: any,
  apiKey: string
): Promise<Finding[]> {
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

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
    }),
  });

  if (!response.ok) {
    throw new Error(`Claude API error: ${response.status}`);
  }

  const data = await response.json();
  const content = data.content?.[0]?.text;

  if (!content) {
    throw new Error('No response from Claude');
  }

  // Parse JSON response
  const jsonMatch = content.match(/\[[\s\S]*\]/);
  if (!jsonMatch) {
    throw new Error('Invalid JSON response from Claude');
  }

  const findings = JSON.parse(jsonMatch[0]);

  // Map icon strings to match frontend expectations
  return findings.map((f: any) => ({
    ...f,
    icon: f.icon.replace(/"/g, ''), // Remove quotes if present
  }));
}

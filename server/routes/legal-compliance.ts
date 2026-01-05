/**
 * Legal Compliance Routes for MetaExtract
 * 
 * Handles legal compliance endpoints including:
 * - Privacy policy
 * - Terms of service
 * - GDPR compliance
 * - Data processing agreements
 */

import type { Express, Request, Response } from 'express';
import { z } from 'zod';
import { storage } from '../storage';
import { authenticateToken } from '../auth';
import { rateLimitAPI } from '../rateLimitMiddleware';

// ============================================================================
// Validation Schemas
// ============================================================================

const gdprRequestSchema = z.object({
  requestType: z.enum(['access', 'rectification', 'erasure', 'portability']),
  reason: z.string().min(10).max(500),
  verification: z.object({
    email: z.string().email(),
    confirmationCode: z.string().length(6),
  }),
});

// ============================================================================
// Privacy Policy
// ============================================================================

const PRIVACY_POLICY_VERSION = '1.0.0';
const PRIVACY_POLICY_LAST_UPDATED = '2025-01-04';

const privacyPolicyContent = `
<h1>Privacy Policy for MetaExtract</h1>

<p><strong>Last Updated:</strong> ${new Date().toISOString().split('T')[0]}</p>

<h2>Information We Collect</h2>
<p>We collect the following types of information when you use our service:</p>

<h3>File Data</h3>
<ul>
  <li>Metadata from uploaded files (EXIF, IPTC, XMP, etc.)</li>
  <li>File hashes for integrity verification</li>
  <li>File type, size, and basic properties</li>
  <li>Processing results and analysis</li>
</ul>

<h3>Technical Information</h3>
<ul>
  <li>IP address and browser information</li>
  <li>Device type and operating system</li>
  <li>Timestamps of file uploads and downloads</li>
  <li>Usage patterns and feature preferences</li>
</ul>

<h3>Account Information</h3>
<ul>
  <li>Email address and username</li>
  <li>Subscription tier and payment information</li>
  <li>Credit usage and transaction history</li>
  <li>Communication preferences</li>
</ul>

<h2>How We Use Your Information</h2>
<ul>
  <li>Provide and improve the service</li>
  <li>Process and analyze uploaded files</li>
  <li>Manage accounts, subscriptions, and billing</li>
  <li>Protect against fraud and abuse and comply with legal obligations</li>
</ul>

<h2>Data Retention and Deletion</h2>
<ul>
  <li>Uploaded files are deleted after processing.</li>
  <li>Metadata results may be retained to provide the service and improve reliability.</li>
  <li>Account information is retained while your account remains active; deletion requests are processed subject to legal obligations.</li>
</ul>

<h2>Your Rights</h2>
<p>Depending on your jurisdiction (including GDPR), you may have rights to access, correct, delete, or export your personal data.</p>

<h2>Security Measures</h2>
<p>We use reasonable technical and organizational safeguards to protect your data, including encryption in transit and access controls.</p>

<h2>Data Sharing and Disclosure</h2>
<p>We do not sell your personal information. We may share information with service providers (e.g., infrastructure, payment processing) and to comply with legal obligations.</p>

<h2>International Transfers</h2>
<p>If you are located outside the country where our servers are located, your information may be transferred and processed there with appropriate safeguards.</p>

<h2>Children's Privacy</h2>
<p>Our service does not address anyone under the age of 13. We do not knowingly collect personal information from children under 13.</p>

<h2>Changes to This Privacy Policy</h2>
<p>We may update this policy periodically by posting an updated version and changing the “Last Updated” date.</p>

<h2>Contact Us</h2>
<p>If you have questions about this privacy policy, contact <a href="mailto:privacy@metaextract.com">privacy@metaextract.com</a>.</p>
`;

// ============================================================================
// Terms of Service
// ============================================================================

const TERMS_OF_SERVICE_VERSION = '1.0.0';
const TERMS_OF_SERVICE_LAST_UPDATED = '2025-01-04';

const termsOfServiceContent = `
<h1>Terms of Service for MetaExtract</h1>

<p><strong>Last Updated:</strong> ${new Date().toISOString().split('T')[0]}</p>

<h2>Acceptance of Terms</h2>
<p>By accessing and using MetaExtract, you accept and agree to be bound by these Terms.</p>

<h2>Description of Service</h2>
<p>MetaExtract provides metadata extraction services for uploaded files. Results depend on what metadata is embedded in the file; some files may have metadata removed or missing.</p>

<h2>Credits and Usage</h2>
<p>Some features require credits. Credits are consumed per analysis and are non-transferable.</p>

<h2>Refund Policy (Credit Packs)</h2>
<p><strong>Refunds are available within 7 days of purchase for unused credit packs only.</strong> If any credits are used, the purchase is non-refundable.</p>

<h2>User Responsibilities</h2>
<h3>Acceptable Use</h3>
<ul>
  <li>Use the service in compliance with applicable laws</li>
  <li>Respect intellectual property rights</li>
  <li>Do not upload illegal content</li>
  <li>Do not attempt to circumvent security measures</li>
</ul>

<h3>Prohibited Activities</h3>
<ul>
  <li>Uploading copyrighted material without permission</li>
  <li>Using the service for illegal activities</li>
  <li>Attempting to disrupt service operations</li>
  <li>Scraping or reverse engineering the service</li>
</ul>

<h2>Intellectual Property</h2>
<p>The service and its original content, features, and functionality are owned by MetaExtract and are protected by applicable intellectual property laws.</p>

<h2>Limitation of Liability</h2>
<p>To the maximum extent permitted by law, MetaExtract will not be liable for indirect, incidental, special, consequential, or punitive damages.</p>

<h2>Termination</h2>
<p>We may terminate or suspend access to the service if you breach these Terms.</p>

<h2>Contact Information</h2>
<p>For questions about these Terms, contact <a href="mailto:legal@metaextract.com">legal@metaextract.com</a>.</p>
`;

// ============================================================================
// GDPR Compliance
// ============================================================================

async function handleGDPRAccessRequest(userId: string): Promise<any> {
  // Retrieve all personal data associated with the user
  const userData = await storage.getUserById(userId);
  const creditBalance = await storage.getCreditBalance(userId);
  const extractionHistory = await storage.getExtractionHistory(userId, { limit: 100 });
  
  return {
    userData: {
      id: userData.id,
      email: userData.email,
      username: userData.username,
      createdAt: userData.createdAt,
      updatedAt: userData.updatedAt,
    },
    creditData: creditBalance,
    extractionHistory,
    timestamp: new Date().toISOString(),
  };
}

async function handleGDPRErasureRequest(userId: string): Promise<void> {
  // Anonymize or delete user data according to retention policies
  await storage.anonymizeUserData(userId);
}

async function handleGDPRRectificationRequest(userId: string, updates: any): Promise<void> {
  // Update user data as requested
  await storage.updateUserProfile(userId, updates);
}

// ============================================================================
// Registration Function
// ============================================================================

export function registerLegalComplianceRoutes(app: Express): void {
  // Rate limit for legal endpoints
  const legalRateLimiter = rateLimitAPI({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests for legal pages, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
  });

  // Privacy Policy
  app.get('/api/legal/privacy', legalRateLimiter, (_req: Request, res: Response) => {
    res.json({
      version: PRIVACY_POLICY_VERSION,
      lastUpdated: PRIVACY_POLICY_LAST_UPDATED,
      content: privacyPolicyContent,
    });
  });

  // Terms of Service
  app.get('/api/legal/terms', legalRateLimiter, (_req: Request, res: Response) => {
    res.json({
      version: TERMS_OF_SERVICE_VERSION,
      lastUpdated: TERMS_OF_SERVICE_LAST_UPDATED,
      content: termsOfServiceContent,
    });
  });

  // GDPR Compliance Requests (authenticated users only)
  app.post('/api/legal/gdpr', authenticateToken, legalRateLimiter, async (req: Request, res: Response) => {
    try {
      const validationResult = gdprRequestSchema.safeParse(req.body);
      if (!validationResult.success) {
        return res.status(400).json({
          error: 'Validation failed',
          details: validationResult.error.flatten().fieldErrors,
        });
      }

      const { requestType, reason } = validationResult.data;
      const userId = (req as any).user.id;

      let result;
      switch (requestType) {
        case 'access':
          result = await handleGDPRAccessRequest(userId);
          break;
        case 'rectification':
          // For rectification, we need the updates in the request
          if (!req.body.updates) {
            return res.status(400).json({ error: 'Updates required for rectification request' });
          }
          await handleGDPRRectificationRequest(userId, req.body.updates);
          result = { success: true, message: 'Data rectification completed' };
          break;
        case 'erasure':
          await handleGDPRErasureRequest(userId);
          result = { success: true, message: 'Data erasure completed' };
          break;
        case 'portability':
          result = await handleGDPRAccessRequest(userId);
          break;
        default:
          return res.status(400).json({ error: 'Invalid request type' });
      }

      res.json({
        success: true,
        requestType,
        result,
      });
    } catch (error) {
      console.error('GDPR request error:', error);
      res.status(500).json({ error: 'GDPR request failed' });
    }
  });

  // Data Processing Agreement (DPA)
  app.get('/api/legal/dpa', legalRateLimiter, (_req: Request, res: Response) => {
    const dpaContent = `
# Data Processing Agreement (DPA)

**Effective Date:** ${new Date().toISOString().split('T')[0]}

This Data Processing Agreement ("DPA") supplements the Terms of Service between MetaExtract ("Processor") and the Customer ("Controller").

## Purpose
This DPA governs the processing of personal data by Processor on behalf of Controller in connection with the provision of the MetaExtract service.

## Scope of Processing
- **Personal Data:** Metadata extracted from customer files that may contain personal identifiers
- **Processing Activities:** Extraction, analysis, and reporting of metadata
- **Categories of Data Subjects:** End users whose files contain personal metadata
- **Types of Personal Data:** Location data, device identifiers, timestamps, and other personal identifiers contained in file metadata

## Instructions for Processing
Processor shall process personal data only on documented instructions from Controller, as set forth in the main service agreement and this DPA, unless required to do otherwise by EU or Member State law.

## Obligations of Processor
Processor agrees to:
- Implement appropriate technical and organizational measures to ensure security
- Assist with data subject requests for access, rectification, erasure, and portability
- Notify Controller of any personal data breaches within 24 hours
- Delete or return personal data at the end of the service

## Sub-processors
Processor may engage sub-processors for the provision of services, provided that it maintains responsibility for compliance with this DPA.

## Data Security
Processor implements appropriate technical and organizational measures including:
- Encryption in transit and at rest
- Access controls and authentication
- Regular security assessments
- Staff training on data protection

## International Transfers
If personal data is transferred internationally, Processor ensures appropriate safeguards are in place.

## Audit Rights
Controller has the right to audit Processor's compliance with this DPA annually.

## Term and Termination
This DPA remains in effect as long as personal data is processed on behalf of Controller.
    `;

    res.json({
      version: '1.0.0',
      lastUpdated: new Date().toISOString().split('T')[0],
      content: dpaContent,
    });
  });

  // Cookie Policy
  app.get('/api/legal/cookies', legalRateLimiter, (_req: Request, res: Response) => {
    const cookiePolicyContent = `
# Cookie Policy for MetaExtract

**Last Updated:** ${new Date().toISOString().split('T')[0]}

## What Are Cookies?

Cookies are small text files placed on your device when you visit our website. They help us provide our services and improve your experience.

## Types of Cookies We Use

### Essential Cookies
- Authenticate users
- Enable core functionality
- Remember session information

### Performance Cookies
- Analyze site usage
- Improve site performance
- Identify popular features

### Functional Cookies
- Remember user preferences
- Provide personalized features
- Enable social media functions

## Managing Cookies

You can control and manage cookies in several ways:
- Adjust your browser settings
- Use our cookie preference manager
- Delete existing cookies

## Updates to This Policy

We may update this cookie policy periodically. Continued use of our service constitutes acceptance of any changes.
    `;

    res.json({
      version: '1.0.0',
      lastUpdated: new Date().toISOString().split('T')[0],
      content: cookiePolicyContent,
    });
  });

  // Acceptable Use Policy
  app.get('/api/legal/aup', legalRateLimiter, (_req: Request, res: Response) => {
    const aupContent = `
# Acceptable Use Policy for MetaExtract

**Last Updated:** ${new Date().toISOString().split('T')[0]}

## Prohibited Uses

You agree not to use our service to:
- Upload illegal or copyrighted content without permission
- Engage in unlawful activities
- Violate intellectual property rights
- Circumvent security measures
- Disrupt service operations
- Harvest or scrape user data

## Enforcement

Violations of this policy may result in:
- Account suspension or termination
- Reporting to appropriate authorities
- Legal action when necessary

## Reporting Violations

If you discover a violation of this policy, please report it to: abuse@metaextract.com
    `;

    res.json({
      version: '1.0.0',
      lastUpdated: new Date().toISOString().split('T')[0],
      content: aupContent,
    });
  });

  console.log('✅ Legal compliance routes registered');
}

export default registerLegalComplianceRoutes;

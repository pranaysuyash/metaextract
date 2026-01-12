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
# Privacy Policy for MetaExtract

**Last Updated:** ${new Date().toISOString().split('T')[0]}

## Information We Collect

We collect the following types of information when you use our service:

### File Data
- Metadata from uploaded files (EXIF, IPTC, XMP, etc.)
- File hashes for integrity verification
- File type, size, and basic properties
- Processing results and analysis

### Technical Information
- IP address and browser information
- Device type and operating system
- Timestamps of file uploads and downloads
- Usage patterns and feature preferences

### Account Information
- Email address and username
- Subscription tier and payment information
- Credit usage and transaction history
- Communication preferences

## How We Use Your Information

We use your information for the following purposes:

### Service Provision
- To provide metadata extraction services
- To process and analyze your uploaded files
- To generate reports and results
- To maintain service functionality

### Account Management
- To authenticate and identify users
- To manage subscriptions and billing
- To track credit usage
- To provide customer support

### Security and Compliance
- To protect against unauthorized access
- To detect and prevent fraudulent activities
- To comply with legal obligations
- To maintain service integrity

## Data Retention and Deletion

### File Data
- Uploaded files are deleted immediately after processing
- Metadata results are retained for 30 days unless you have an active subscription
- For subscribed users, data retention follows your selected plan

### Account Data
- Account information is retained as long as your account remains active
- Upon account deletion, personal information is removed within 30 days
- Aggregated, anonymized data may be retained for service improvement

## Your Rights

Under GDPR and other privacy laws, you have the following rights:

### Right of Access
- Request a copy of your personal data
- Know how your data is being used
- Receive information about data processing

### Right to Rectification
- Correct inaccurate personal data
- Complete incomplete personal data
- Update outdated information

### Right to Erasure
- Request deletion of your personal data
- Remove consent for data processing
- Close your account with data deletion

### Right to Data Portability
- Receive your personal data in a structured format
- Transfer your data to another service
- Obtain copies of your processed metadata

## Security Measures

We implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including:

### Technical Safeguards
- Encryption in transit (TLS 1.3)
- Secure file processing (temporary storage only)
- Regular security assessments
- Access controls and authentication

### Organizational Safeguards
- Employee confidentiality agreements
- Regular security training
- Incident response procedures
- Third-party security reviews

## Data Sharing and Disclosure

We do not sell, trade, or rent your personal identification information to others. We may share your information in the following situations:

### Service Providers
- Cloud infrastructure providers
- Payment processors
- Analytics services
- Customer support platforms

### Legal Requirements
- Compliance with legal obligations
- Protection of our rights
- Response to legal requests
- Prevention of fraud

## International Transfers

If you are located outside the country where our servers are located, your information may be transferred to and processed in that country. We ensure appropriate safeguards are in place for international transfers.

## Children's Privacy

Our service does not address anyone under the age of 13. We do not knowingly collect personal information from children under 13.

## Changes to This Privacy Policy

We may update this privacy policy periodically. We will notify you of any changes by posting the new privacy policy on this page and updating the "Last Updated" date.

## Contact Us

If you have questions about this privacy policy, please contact us at:

Email: privacy@metaextract.com
Address: [Company Address]
`;

// ============================================================================
// Terms of Service
// ============================================================================

const TERMS_OF_SERVICE_VERSION = '1.0.0';
const TERMS_OF_SERVICE_LAST_UPDATED = '2025-01-04';

const termsOfServiceContent = `
# Terms of Service for MetaExtract

**Last Updated:** ${new Date().toISOString().split('T')[0]}

## Acceptance of Terms

By accessing and using MetaExtract, you accept and agree to be bound by the terms and provisions of this agreement.

## Description of Service

MetaExtract provides comprehensive metadata extraction services for various file types including images, videos, documents, and more.

## User Responsibilities

### Acceptable Use
- Use the service in compliance with applicable laws
- Respect intellectual property rights
- Do not upload illegal content
- Do not attempt to circumvent security measures

### Prohibited Activities
- Uploading copyrighted material without permission
- Using the service for illegal activities
- Attempting to disrupt service operations
- Scraping or reverse engineering the service

## Intellectual Property

The service and its original content, features, and functionality are owned by MetaExtract and are protected by international copyright, trademark, and other intellectual property laws.

## Limitation of Liability

In no event shall MetaExtract, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential, or punitive damages.

## Termination

We may terminate or suspend your account immediately, without prior notice, for any reason whatsoever, including without limitation if you breach the Terms.

## Governing Law

These Terms shall be governed and construed in accordance with the laws of [Jurisdiction], without regard to its conflict of law provisions.

## Contact Information

If you have any questions about these Terms, please contact us at:

Email: legal@metaextract.com
Address: [Company Address]
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
/**
 * Request Validation Schemas
 *
 * Zod schemas for validating incoming API requests.
 * Provides type-safe request parsing and error handling.
 *
 * Usage:
 *   const result = extractionRequestSchema.safeParse(req.body);
 *   if (!result.success) {
 *     return sendValidationErrorResponseFromZod(res, result.error);
 *   }
 */

import { z } from 'zod';

/**
 * Extract endpoint request schema
 */
export const extractionRequestSchema = z.object({
  file: z.unknown().optional().describe('File (multipart)'),
  tier: z
    .enum(['free', 'professional', 'forensic', 'enterprise'])
    .optional()
    .describe('User tier'),
  store: z
    .enum(['true', 'false'])
    .optional()
    .describe('Whether to store metadata'),
  advanced: z
    .enum(['true', 'false'])
    .optional()
    .describe('Enable advanced analysis'),
});

export type ExtractionRequest = z.infer<typeof extractionRequestSchema>;

/**
 * Batch extraction request schema
 */
export const batchExtractionRequestSchema = z.object({
  files: z
    .array(z.unknown())
    .min(1, 'At least one file is required')
    .max(100, 'Maximum 100 files per batch')
    .describe('Array of files'),
  tier: z
    .enum(['free', 'professional', 'forensic', 'enterprise'])
    .optional()
    .describe('User tier'),
  parallel: z
    .enum(['true', 'false'])
    .optional()
    .describe('Process files in parallel'),
});

export type BatchExtractionRequest = z.infer<
  typeof batchExtractionRequestSchema
>;

/**
 * Login request schema
 */
export const loginRequestSchema = z.object({
  email: z
    .string()
    .email('Invalid email address')
    .describe('User email'),
  password: z
    .string()
    .min(1, 'Password is required')
    .describe('User password'),
  session_id: z
    .string()
    .optional()
    .describe('Session ID (optional)'),
});

export type LoginRequest = z.infer<typeof loginRequestSchema>;

/**
 * Register request schema
 */
export const registerRequestSchema = z
  .object({
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(50, 'Username must be at most 50 characters')
      .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens')
      .describe('Username'),
    email: z
      .string()
      .email('Invalid email address')
      .describe('Email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .max(128, 'Password must be at most 128 characters')
      .describe('Password'),
    confirmPassword: z
      .string()
      .describe('Password confirmation'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type RegisterRequest = z.infer<typeof registerRequestSchema>;

/**
 * File upload request validation
 * (file is validated separately via multer)
 */
export const uploadFileRequestSchema = z.object({
  filename: z
    .string()
    .min(1, 'Filename is required')
    .max(255, 'Filename is too long')
    .describe('Original filename'),
  mimeType: z
    .string()
    .optional()
    .describe('MIME type'),
  size: z
    .number()
    .positive('File size must be positive')
    .optional()
    .describe('File size in bytes'),
});

export type UploadFileRequest = z.infer<typeof uploadFileRequestSchema>;

/**
 * Metadata query parameters schema
 */
export const metadataQuerySchema = z.object({
  fields: z
    .string()
    .optional()
    .describe('Comma-separated field names to include'),
  exclude: z
    .string()
    .optional()
    .describe('Comma-separated field names to exclude'),
  format: z
    .enum(['json', 'csv', 'xml'])
    .optional()
    .describe('Response format'),
  minify: z
    .enum(['true', 'false'])
    .optional()
    .describe('Minify response'),
});

export type MetadataQuery = z.infer<typeof metadataQuerySchema>;

/**
 * Tier upgrade request schema
 */
export const tierUpgradeRequestSchema = z.object({
  tier: z
    .enum(['professional', 'forensic', 'enterprise'])
    .describe('Target tier'),
  billingPeriod: z
    .enum(['monthly', 'yearly'])
    .optional()
    .describe('Billing period'),
});

export type TierUpgradeRequest = z.infer<typeof tierUpgradeRequestSchema>;

/**
 * Validate request and return typed result or error response
 *
 * Usage:
 *   const result = await validateRequest(req.body, loginRequestSchema);
 *   if (!result.success) {
 *     return res.status(400).json(result.error);
 *   }
 *   const loginData = result.data;
 */
export async function validateRequest<T>(
  data: unknown,
  schema: z.ZodSchema<T>
): Promise<
  | { success: true; data: T }
  | { success: false; errors: z.ZodError }
> {
  const result = schema.safeParse(data);
  if (!result.success) {
    return { success: false, errors: result.error };
  }
  return { success: true, data: result.data };
}

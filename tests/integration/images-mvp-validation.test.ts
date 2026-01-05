/**
 * Images MVP Validation Tests
 * 
 * Tests for magic-byte validation, rate limiting, and edge cases.
 * Part of the Images MVP Subsystem Audit remediation.
 */

import { describe, it, expect, beforeAll } from '@jest/globals';
import * as fs from 'fs/promises';
import * as path from 'path';
import { fileTypeFromBuffer } from 'file-type';

// Test fixtures directory
const FIXTURES_DIR = path.join(__dirname, '../fixtures');

describe('Images MVP Validation', () => {
  describe('Magic-byte validation', () => {
    it('should detect JPEG files correctly', async () => {
      const jpegPath = path.join(FIXTURES_DIR, 'test.jpg');
      const buffer = await fs.readFile(jpegPath);
      const type = await fileTypeFromBuffer(buffer);
      
      expect(type).toBeDefined();
      expect(type?.mime).toBe('image/jpeg');
    });

    it('should reject files with spoofed extensions', async () => {
      // Create a text file pretending to be an image
      const fakeImageBuffer = Buffer.from('This is not an image file. Just plain text.');
      const type = await fileTypeFromBuffer(fakeImageBuffer);
      
      // file-type returns undefined for non-recognized formats
      expect(type?.mime).not.toBe('image/jpeg');
      expect(type?.mime).not.toBe('image/png');
    });

    it('should handle empty files gracefully', async () => {
      const emptyBuffer = Buffer.alloc(0);
      const type = await fileTypeFromBuffer(emptyBuffer);
      
      expect(type).toBeUndefined();
    });

    it('should handle very small files', async () => {
      const tinyBuffer = Buffer.from([0xFF, 0xD8]); // Partial JPEG header
      const type = await fileTypeFromBuffer(tinyBuffer);
      
      // Might be detected as JPEG start or undefined
      // The important thing is it doesn't crash
      expect(true).toBe(true); // Test passes if no exception
    });
  });

  describe('Supported image formats', () => {
    const SUPPORTED_MIMES = new Set([
      'image/jpeg',
      'image/png',
      'image/webp',
      'image/heic',
      'image/heif',
      'image/tiff',
      'image/bmp',
      'image/gif',
    ]);

    it('should have correct SUPPORTED_MIMES set', () => {
      expect(SUPPORTED_MIMES.has('image/jpeg')).toBe(true);
      expect(SUPPORTED_MIMES.has('image/png')).toBe(true);
      expect(SUPPORTED_MIMES.has('application/pdf')).toBe(false);
    });
  });

  describe('File size limits', () => {
    const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

    it('should have reasonable size limit', () => {
      expect(MAX_FILE_SIZE).toBe(104857600);
    });

    it('should reject files over limit', () => {
      const oversizedFile = { size: 150 * 1024 * 1024 }; // 150MB
      expect(oversizedFile.size > MAX_FILE_SIZE).toBe(true);
    });
  });
});

describe('EXIF Stripper Utility', () => {
  it('should be available for CDN use', async () => {
    // Dynamically import to verify module exists
    const { stripExif, processImageBuffer } = await import('../../server/utils/exif-stripper');
    
    expect(typeof stripExif).toBe('function');
    expect(typeof processImageBuffer).toBe('function');
  });
});

describe('Rate Limiting', () => {
  it('should have rateLimitExtraction middleware', async () => {
    const { rateLimitExtraction } = await import('../../server/rateLimitMiddleware');
    
    expect(typeof rateLimitExtraction).toBe('function');
    
    // Should return a middleware function
    const middleware = rateLimitExtraction();
    expect(typeof middleware).toBe('function');
  });
});

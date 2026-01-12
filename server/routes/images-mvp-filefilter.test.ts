/**
 * Tests for fileFilter security in Images MVP route
 * 
 * Verifies that:
 * 1. Valid image files are accepted
 * 2. Invalid/malicious files are rejected BEFORE disk write
 * 3. Proper error messages are returned
 * 4. No temp files are created for rejected uploads
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerImagesMvpRoutes } from './images-mvp';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

describe('Images MVP FileFilter Security', () => {
  let app: Express;
  const uploadDir = path.join(os.tmpdir(), 'metaextract-uploads');

  beforeAll(async () => {
    app = express();
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));
    
    // Register only the Images MVP routes for isolated testing
    registerImagesMvpRoutes(app);

    // Monkey-patch heavy extraction to a fast stub for file-filter focused tests
    try {
      const helpers = require('../utils/extraction-helpers');
      if (helpers && typeof helpers.extractMetadataWithPython === 'function') {
        helpers.extractMetadataWithPython = async () => ({ extraction_info: { fields_extracted: 0 } });
      }
    } catch (err) {
      // If patching fails, continue; tests will surface issues
      console.debug('Could not stub extractMetadataWithPython for filefilter tests:', err);
    }
    
    // Ensure upload directory exists and is empty
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      const files = await fs.readdir(uploadDir);
      // Clean up any existing files
      for (const file of files) {
        await fs.unlink(path.join(uploadDir, file));
      }
    } catch (error) {
      console.warn('Could not clean upload directory:', error);
    }
  });

  afterEach(async () => {
    // Clean up any files that were created during tests
    try {
      const files = await fs.readdir(uploadDir);
      for (const file of files) {
        await fs.unlink(path.join(uploadDir, file));
      }
    } catch (error) {
      // Directory might not exist, that's okay
    }
  });

  describe('Valid Image Files', () => {
    test('should accept JPEG files', async () => {
      const response = await request(app)
        .post('/api/images_mvp/extract')
        .attach('file', Buffer.from('fake jpeg content'), 'test.jpg')
        .set('Content-Type', 'image/jpeg');
      
      // Should not be rejected by fileFilter (may fail later in processing)
      expect(response.status).not.toBe(403);
      expect(response.status).not.toBe(400);
      console.log(`✅ JPEG file accepted: ${response.status}`);
    });

    test('should accept PNG files', async () => {
      const response = await request(app)
        .post('/api/images_mvp/extract')
        .attach('file', Buffer.from('fake png content'), 'test.png')
        .set('Content-Type', 'image/png');
      
      expect(response.status).not.toBe(403);
      expect(response.status).not.toBe(400);
      console.log(`✅ PNG file accepted: ${response.status}`);
    });

    test('should accept supported RAW formats', async () => {
      const rawFormats = ['.cr2', '.nef', '.arw', '.dng'];
      
      for (const ext of rawFormats) {
        const response = await request(app)
          .post('/api/images_mvp/extract')
          .attach('file', Buffer.from('fake raw content'), `test${ext}`)
          .set('Content-Type', 'image/x-raw');
        
        expect(response.status).not.toBe(403);
        expect(response.status).not.toBe(400);
        console.log(`✅ ${ext} file accepted: ${response.status}`);
      }
    });
  });

  describe('Invalid/Malicious Files', () => {
    test('should reject executable files', async () => {
      const maliciousFiles = [
        { name: 'malware.exe', mime: 'application/x-msdownload' },
        { name: 'virus.dll', mime: 'application/x-msdownload' },
        { name: 'trojan.com', mime: 'application/x-msdownload' },
      ];

      for (const file of maliciousFiles) {
        const response = await request(app)
          .post('/api/images_mvp/extract')
          .attach('file', Buffer.from('malicious content'), file.name)
          .set('Content-Type', file.mime);
        
        expect(response.status).toBe(403);
        expect(response.body).toMatchObject({
          error: 'Unsupported file type',
          code: 'UNSUPPORTED_FILE_TYPE'
        });
        console.log(`✅ ${file.name} rejected: ${response.status}`);
      }
    });

    test('should reject script files', async () => {
      const scriptFiles = [
        { name: 'hack.js', mime: 'application/javascript' },
        { name: 'exploit.py', mime: 'text/x-python' },
        { name: 'malicious.php', mime: 'application/x-php' },
        { name: 'virus.sh', mime: 'text/x-shellscript' },
      ];

      for (const file of scriptFiles) {
        const response = await request(app)
          .post('/api/images_mvp/extract')
          .attach('file', Buffer.from('malicious script'), file.name)
          .set('Content-Type', file.mime);
        
        expect(response.status).toBe(403);
        console.log(`✅ ${file.name} rejected: ${response.status}`);
      }
    });

    test('should reject document files', async () => {
      const docFiles = [
        { name: 'malware.pdf', mime: 'application/pdf' },
        { name: 'virus.docx', mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
        { name: 'exploit.xls', mime: 'application/vnd.ms-excel' },
      ];

      for (const file of docFiles) {
        const response = await request(app)
          .post('/api/images_mvp/extract')
          .attach('file', Buffer.from('fake document'), file.name)
          .set('Content-Type', file.mime);
        
        expect(response.status).toBe(403);
        console.log(`✅ ${file.name} rejected: ${response.status}`);
      }
    });

    test('should reject files with fake image extensions', async () => {
      const fakeImageFiles = [
        { name: 'malware.jpg.exe', mime: 'application/x-msdownload' },
        { name: 'virus.png.js', mime: 'application/javascript' },
        { name: 'exploit.gif.php', mime: 'application/x-php' },
      ];

      for (const file of fakeImageFiles) {
        const response = await request(app)
          .post('/api/images_mvp/extract')
          .attach('file', Buffer.from('fake content'), file.name)
          .set('Content-Type', file.mime);
        
        expect(response.status).toBe(403);
        console.log(`✅ ${file.name} rejected: ${response.status}`);
      }
    });
  });

  describe('File Size Limits', () => {
    test('should reject files exceeding size limit', async () => {
      // Create a buffer larger than the 100MB limit
      const largeBuffer = Buffer.alloc(101 * 1024 * 1024); // 101MB
      
      const response = await request(app)
        .post('/api/images_mvp/extract')
        .attach('file', largeBuffer, 'huge.jpg')
        .set('Content-Type', 'image/jpeg');
      
      expect(response.status).toBe(413);
      expect(response.body).toMatchObject({
        error: 'File too large',
        code: 'FILE_TOO_LARGE'
      });
      console.log(`✅ Large file rejected: ${response.status}`);
    });
  });

  describe('Disk Write Prevention', () => {
    test('should not create temp files for rejected uploads', async () => {
      // Count files before test
      const filesBefore = await fs.readdir(uploadDir).catch(() => []);
      
      // Attempt to upload malicious file
      const response = await request(app)
        .post('/api/images_mvp/extract')
        .attach('file', Buffer.from('malware content'), 'virus.exe')
        .set('Content-Type', 'application/x-msdownload');
      
      expect(response.status).toBe(403);
      
      // Count files after test
      const filesAfter = await fs.readdir(uploadDir).catch(() => []);
      
      // No new files should have been created
      expect(filesAfter.length).toBe(filesBefore.length);
      console.log(`✅ No disk write for rejected file: ${filesBefore.length} -> ${filesAfter.length} files`);
    });
  });

  describe('Error Messages', () => {
    test('should provide clear error messages for rejected files', async () => {
      const response = await request(app)
        .post('/api/images_mvp/extract')
        .attach('file', Buffer.from('malware'), 'virus.exe')
        .set('Content-Type', 'application/x-msdownload');
      
      expect(response.status).toBe(403);
      expect(response.body).toMatchObject({
        error: 'Unsupported file type',
        message: expect.stringContaining('File type not permitted'),
        code: 'UNSUPPORTED_FILE_TYPE'
      });
      
      console.log(`✅ Clear error message provided: ${response.body.message}`);
    });
  });
});
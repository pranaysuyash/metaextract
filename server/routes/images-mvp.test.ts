
/** @jest-environment node */
import request from 'supertest';
import express, { type Express } from 'express';
import { registerImagesMvpRoutes } from './images-mvp';
import { storage } from '../storage/index';
import { db } from '../db';
import { extractMetadataWithPython, transformMetadataForFrontend } from '../utils/extraction-helpers';

// Mock dependencies
jest.mock('../storage/index', () => ({
  storage: {
    getOrCreateCreditBalance: jest.fn(),
    logExtractionUsage: jest.fn().mockResolvedValue(undefined),
    useCredits: jest.fn().mockResolvedValue(undefined),
    recordTrialUsage: jest.fn().mockResolvedValue(undefined),
  },
}));

jest.mock('../db', () => ({
  db: {
    select: jest.fn().mockReturnThis(),
    from: jest.fn().mockReturnThis(),
    where: jest.fn().mockReturnThis(),
    limit: jest.fn().mockReturnThis(),
  },
}));

jest.mock('fs/promises', () => ({
  mkdir: jest.fn().mockResolvedValue(undefined),
  writeFile: jest.fn().mockResolvedValue(undefined),
  unlink: jest.fn().mockResolvedValue(undefined),
}));

// Mock helpers to avoid ESM module issues and isolate logic
jest.mock('../utils/extraction-helpers', () => ({
  extractMetadataWithPython: jest.fn().mockResolvedValue({
        extraction_info: { fields_extracted: 10, processing_ms: 100 },
        file: { extension: '.jpg', mime_type: 'image/jpeg' },
        summary: { filesize: '1MB', filetype: 'JPEG' },
        filesystem: {},
        hashes: {},
        exif: {},
        gps: null,
        video: null,
        audio: null,
        pdf: null,
        svg: null,
        image: null,
        makernote: null,
        iptc: null,
        xmp: null,
        forensic: {},
        calculated: {},
        extended_attributes: null,
        locked_fields: [],
  }),
  transformMetadataForFrontend: jest.fn().mockReturnValue({
    filename: 'test.jpg',
    access: {},
    fields_extracted: 10,
    tier: 'professional' // default return
  }),
  normalizeEmail: jest.fn((email) => (email ? email.trim().toLowerCase() : null)),
  getSessionId: jest.fn((req) => req.query.session_id || req.body.session_id || req.headers['x-session-id']),
  cleanupTempFile: jest.fn(),
  pythonExecutable: 'python3',
  PYTHON_SCRIPT_PATH: '/path/to/script.py',
}));

// Mock DodoPayments
jest.mock('dodopayments', () => {
  return jest.fn().mockImplementation(() => ({
    checkoutSessions: {
      create: jest.fn().mockResolvedValue({
        checkout_url: 'http://test-checkout',
        session_id: 'sess_123',
      }),
    },
  }));
});

describe('Images MVP API Tests', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerImagesMvpRoutes(app);
    jest.clearAllMocks();
    process.env.DODO_PAYMENTS_API_KEY = 'test_key'; 
  });

  afterEach(() => {
      delete process.env.DODO_PAYMENTS_API_KEY;
  });

  describe('GET /api/images_mvp/credits/packs', () => {
    it('should return credit packs', async () => {
      const response = await request(app)
        .get('/api/images_mvp/credits/packs')
        .expect(200);

      expect(response.body).toHaveProperty('packs');
      expect(response.body.packs).toHaveProperty('starter');
      expect(response.body.packs.starter).toHaveProperty('credits', 25);
    });
  });

  describe('GET /api/images_mvp/credits/balance', () => {
    it('should return zero balance for new session', async () => {
      (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({
        id: 'bal_123',
        credits: 0,
        sessionId: 'images_mvp:sess_abc',
      });

      const response = await request(app)
        .get('/api/images_mvp/credits/balance?sessionId=sess_abc')
        .expect(200);

      expect(response.body).toEqual({ credits: 0, balanceId: 'bal_123' });
      expect(storage.getOrCreateCreditBalance).toHaveBeenCalledWith('images_mvp:sess_abc');
    });
  });

  describe('POST /api/images_mvp/extract', () => {
    it('should reject non-image files', async () => {
        const response = await request(app)
            .post('/api/images_mvp/extract')
            .attach('file', Buffer.from('fake pdf'), { filename: 'test.pdf', contentType: 'application/pdf' })
            .expect(400);
        
        expect(response.body.error).toBe('Invalid file type');
    });

    it('should use trial if available (uses < 2)', async () => {
        // Mock DB uses to return 0 (trial available)
        (db.select().from().where as jest.Mock).mockResolvedValue([{ uses: 0 }]);
        (storage.recordTrialUsage as jest.Mock).mockResolvedValue({});

        const response = await request(app)
            .post('/api/images_mvp/extract')
            .attach('file', Buffer.from('fake jpg'), 'test.jpg')
            .field('trial_email', 'newuser@example.com')
            .expect(200);

        expect(response.body.access.trial_granted).toBe(true);
        expect(storage.recordTrialUsage).toHaveBeenCalled();
        expect(storage.useCredits).not.toHaveBeenCalled();
        expect(extractMetadataWithPython).toHaveBeenCalled();
    });

    it('should reject trial if uses >= 2 and no credits', async () => {
        // Mock DB uses to return 2 (trial used up)
        (db.select().from().where as jest.Mock).mockResolvedValue([{ uses: 2 }]);
        
        // Mock balance 0
        (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({ credits: 0, id: 'bal_1' });

        const response = await request(app)
            .post('/api/images_mvp/extract?session_id=sess_1')
            .attach('file', Buffer.from('fake jpg'), 'test.jpg')
            .field('trial_email', 'useduser@example.com')
            .expect(402); // Quota exceeded

        expect(response.body.error.message).toMatch(/Insufficient credits/);
    });

    it('should use credits if trial exhausted', async () => {
        // Mock DB uses to return 2
        (db.select().from().where as jest.Mock).mockResolvedValue([{ uses: 2 }]);
        // Mock balance 5
        (storage.getOrCreateCreditBalance as jest.Mock).mockResolvedValue({ id: 'bal_1', credits: 5 });

        // Setup mock return for transform that indicates trial_granted false
        (transformMetadataForFrontend as jest.Mock).mockReturnValue({
            filename: 'test.jpg',
            access: { trial_granted: false }, // logic sets this in route actually
            fields_extracted: 10
        });

        const response = await request(app)
            .post('/api/images_mvp/extract?session_id=sess_1')
            .attach('file', Buffer.from('fake jpg'), 'test.jpg')
            .field('trial_email', 'useduser@example.com')
            .expect(200);

        expect(response.body.access.trial_granted).toBe(false);
        expect(storage.useCredits).toHaveBeenCalledWith('bal_1', 1, expect.stringContaining('Extraction'), expect.any(String));
        expect(extractMetadataWithPython).toHaveBeenCalled();
    });
  });
});

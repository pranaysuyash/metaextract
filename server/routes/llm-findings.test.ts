/**
 * Tests for LLM Findings Route
 *
 * Tests LLM-powered findings extraction endpoints
 */

import request from 'supertest';
import express, { type Express } from 'express';
import { registerLLMFindingsRoutes } from './llm-findings';

describe('LLM Findings Routes', () => {
  let app: Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    registerLLMFindingsRoutes(app);
  });

  describe('POST /api/metadata/findings', () => {
    it('should return findings for valid metadata', async () => {
      const metadata = {
        exif: {
          DateTimeOriginal: '2024:01:15 10:30:00',
          Make: 'Canon',
          Model: 'EOS R5',
        },
        gps: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
      };

      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata })
        .expect('Content-Type', /json/);

      expect(response.body).toHaveProperty('findings');
    });

    it('should return 400 when metadata is missing', async () => {
      const response = await request(app)
        .post('/api/metadata/findings')
        .send({})
        .expect(400);

      expect(response.body.error).toBe('Metadata required');
    });

    it('should return 400 when metadata is not an object', async () => {
      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata: 'not an object' })
        .expect(400);

      expect(response.body.error).toBe('Metadata must be an object');
    });

    it('should handle empty metadata object', async () => {
      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata: {} })
        .expect(200);

      expect(response.body).toHaveProperty('findings');
    });

    it('should handle metadata with various field types', async () => {
      const metadata = {
        exif: {
          DateTimeOriginal: '2024:01:15 10:30:00',
          Make: 'Canon',
          Model: 'EOS R5',
          ExposureTime: '1/250',
          FNumber: 2.8,
          ISOSpeedRatings: 400,
        },
        gps: {
          latitude: 37.7749,
          longitude: -122.4194,
          Altitude: 100,
        },
        iptc: {
          Caption: 'Test image caption',
          Copyright: '2024 Test',
        },
        xmp: {
          Rating: 5,
        },
      };

      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata })
        .expect(200);

      expect(response.body).toHaveProperty('findings');
    });

    it('should handle null values in metadata', async () => {
      const metadata = {
        exif: {
          DateTimeOriginal: null,
          Make: undefined,
          Model: 'Test',
        },
      };

      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata })
        .expect(200);

      expect(response.body).toHaveProperty('findings');
    });

    it('should handle nested metadata objects', async () => {
      const metadata = {
        file: {
          name: 'test.jpg',
          size: 1024000,
        },
        exif: {
          DateTimeOriginal: '2024:01:15 10:30:00',
        },
        gps: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
        nested: {
          deep: {
            value: 'test',
          },
        },
      };

      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata })
        .expect(200);

      expect(response.body).toHaveProperty('findings');
    });

    it('should handle arrays in metadata', async () => {
      const metadata = {
        exif: {
          DateTimeOriginal: '2024:01:15 10:30:00',
          LensModel: ['EF 24-70mm f/2.8L II USM'],
        },
      };

      const response = await request(app)
        .post('/api/metadata/findings')
        .send({ metadata })
        .expect(200);

      expect(response.body).toHaveProperty('findings');
    });
  });
});

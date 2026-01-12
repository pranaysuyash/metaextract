/** @jest-environment node */
import request from 'supertest';
import express from 'express';

// Ensure we load the real helpers (not the mock used elsewhere)
beforeEach(() => {
  jest.resetModules();
});

describe('Images MVP integration - applyAccessModeRedaction used', () => {
  it('device_free response shows hybrid redaction using real helper', async () => {
    // Load helpers and route after ensuring we have the real implementation
    const helpers = await import('../utils/extraction-helpers');
    // Spy on python extract to return a usable raw metadata
    jest.spyOn(helpers, 'extractMetadataWithPython').mockResolvedValue({
      extraction_info: { fields_extracted: 100, processing_ms: 10 },
      file: { extension: '.jpg', mime_type: 'image/jpeg' },
      summary: { filesize: '1MB' },
      filesystem: { size_bytes: 123, owner: 'me', owner_uid: 501, group: 'wheel' },
      hashes: { md5: 'a' },
      exif: { Model: 'X' },
      gps: { latitude: 12.345678, longitude: 98.765432, google_maps_url: 'https://maps' },
      burned_metadata: {
        has_burned_metadata: true,
        extracted_text: 'secret',
        confidence: 0.9,
        parsed_data: {
          gps: { latitude: 12.345678, longitude: 98.765432 },
          plus_code: 'ABC',
          location: { street: '1 st', city: 'Town', state: 'ST', country: 'CT' },
        },
      },
      extended_attributes: { attributes: { secret: 'val' } },
      thumbnail: { has_embedded: true, width: 120, height: 160, extra: 'remove' },
      perceptual_hashes: { phash: 'p', dhash: 'd', ahash: 'a', whash: 'w' },
      drone_telemetry: { foo: 'bar' },
    } as any);

    // Use real transform but we can reuse the helper's transformMetadataForFrontend for shape
    jest.spyOn(helpers, 'transformMetadataForFrontend').mockImplementation((raw: any) => {
      return {
        filename: 'test.jpg',
        access: {},
        fields_extracted: raw.extraction_info.fields_extracted,
        tier: 'super',
        exif: raw.exif,
        calculated: { aspect_ratio: '3:4' },
        metadata_comparison: { summary: {} },
        file_integrity: raw.hashes || {},
        thumbnail: raw.thumbnail,
        perceptual_hashes: raw.perceptual_hashes,
        burned_metadata: raw.burned_metadata,
        gps: raw.gps,
        filesystem: raw.filesystem,
        // Include enterprise buckets so redaction can remove them
        drone_telemetry: raw.drone_telemetry,
        locked_fields: [],
      } as any;
    });

    // Mock free quota enforcement to return usage below limit
    const freeQuota = await import('../utils/free-quota-enforcement');
    jest.spyOn(freeQuota, 'getClientUsage').mockResolvedValue({ freeUsed: 0 });
    jest.spyOn(freeQuota, 'incrementUsage').mockResolvedValue(undefined);

    // Now import the route and start app
    const { registerImagesMvpRoutes } = await import('./images-mvp');
    const app = express();
    app.use(express.json());
    registerImagesMvpRoutes(app);

    const response = await request(app)
      .post('/api/images_mvp/extract')
      .attach('file', Buffer.from('fake'), 'test.jpg')
      .expect(200);

    expect(response.body.access.mode).toBe('device_free');
    // burned text redacted
    expect(response.body.burned_metadata.extracted_text).toBeNull();
    // gps rounded and google_maps_url removed
    expect(Math.abs(response.body.gps.latitude - 12.35)).toBeLessThan(0.01);
    expect(response.body.gps.google_maps_url).toBeUndefined();
    // filesystem owner removed
    expect(response.body.filesystem.owner).toBeUndefined();
    // enterprise bucket removed
    expect(response.body.drone_telemetry).toBeNull();
    // not marked trial limited
    expect(response.body._trial_limited).toBeUndefined();
  });
});

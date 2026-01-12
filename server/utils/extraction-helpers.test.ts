import { applyAccessModeRedaction } from './extraction-helpers';

describe('applyAccessModeRedaction', () => {
  it('applies hybrid device_free redactions correctly', () => {
    const input: any = {
      gps: { latitude: 12.345678, longitude: 98.765432, google_maps_url: 'https://maps' },
      burned_metadata: {
        has_burned_metadata: true,
        extracted_text: 'secret text',
        confidence: 0.9,
        parsed_data: {
          gps: { latitude: 12.345678, longitude: 98.765432 },
          plus_code: 'ABC',
          location: { street: '1 st', city: 'Town', state: 'ST', country: 'CT' },
        },
      },
      extended_attributes: { attributes: { secret: 'val', other: 'x' } },
      filesystem: { size_bytes: 123, owner: 'me', owner_uid: 501, group: 'wheel', group_gid: 20, inode: 1234 },
      thumbnail: { has_embedded: true, width: 120, height: 160, extra: 'remove' },
      perceptual_hashes: { phash: 'p', dhash: 'd', ahash: 'a', whash: 'w', extra: 'x' },
      drone_telemetry: { foo: 'bar' },
      locked_fields: ['initial'],
    };

    applyAccessModeRedaction(input, 'device_free');

    // GPS rounding and map link removed
    expect(input.gps).toHaveProperty('latitude');
    expect(Math.abs(input.gps.latitude - 12.35)).toBeLessThan(0.001);
    expect(input.gps).not.toHaveProperty('google_maps_url');

    // Burned metadata: text redacted, gps and plus_code removed, location coarsened
    expect(input.burned_metadata.extracted_text).toBeNull();
    expect(input.burned_metadata.parsed_data).not.toHaveProperty('gps');
    expect(input.burned_metadata.parsed_data).not.toHaveProperty('plus_code');
    expect(input.burned_metadata.parsed_data.location).toEqual({ city: 'Town', state: 'ST', country: 'CT' });

    // Extended attributes values redacted
    expect(input.extended_attributes.attributes.secret).toBeNull();
    expect(input.extended_attributes.attributes.other).toBeNull();

    // Filesystem owner fields removed
    expect(input.filesystem.owner).toBeUndefined();
    expect(input.filesystem.owner_uid).toBeUndefined();
    expect(input.filesystem.group).toBeUndefined();
    expect(input.filesystem.group_gid).toBeUndefined();

    // Thumbnail: only presence and basic attrs kept
    expect(input.thumbnail).toEqual({ has_embedded: true, width: 120, height: 160 });

    // Perceptual hashes: extra removed
    expect(input.perceptual_hashes).toEqual({ phash: 'p', dhash: 'd', ahash: 'a', whash: 'w' });

    // Enterprise-only bulky bucket removed
    expect(input.drone_telemetry).toBeNull();

    // Locked fields updated
    expect(input.locked_fields).toContain('gps');
    expect(input.locked_fields).toContain('extended_attributes');

    // Should NOT be marked as trial limited
    expect(input._trial_limited).toBeUndefined();
  });

  it('applies trial_limited heavy redaction correctly', () => {
    const input: any = {
      iptc: { a: 1 },
      xmp: { b: 2 },
      exif: { Model: 'X' },
      iptc_raw: { raw: true },
      xmp_raw: { raw: true },
      locked_fields: [],
    };

    applyAccessModeRedaction(input, 'trial_limited');

    expect(input.iptc).toBeNull();
    expect(input.xmp).toBeNull();
    expect(input.exif).toEqual({});
    expect(input.iptc_raw).toBeNull();
    expect(input.xmp_raw).toBeNull();
    expect(input._trial_limited).toBe(true);
    expect(input.locked_fields).toEqual(expect.arrayContaining([
      'filesystem_details',
      'hashes',
      'extended_attributes',
      'thumbnail',
      'embedded_thumbnails',
      'perceptual_hashes',
      'makernote',
      'gps',
      'iptc',
      'xmp',
      'calculated',
      'forensic',
      'burned_metadata',
      'metadata_comparison'
    ]));
  });
});

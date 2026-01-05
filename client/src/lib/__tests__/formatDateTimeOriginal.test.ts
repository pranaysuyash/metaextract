import { formatDateTimeOriginal } from '@/utils/metadataTransformers';

describe('formatDateTimeOriginal', () => {
  it('returns formatted date when parse succeeds', () => {
    const meta = { exif: { DateTimeOriginal: '2025:12:25 16:48:00' } };
    const out = formatDateTimeOriginal(meta);
    expect(out).toMatch(/December 25, 2025/);
  });

  it('returns original string when parse fails', () => {
    const meta = { exif: { DateTimeOriginal: 'Some odd human text date 25th' } };
    const out = formatDateTimeOriginal(meta);
    expect(out).toBe('Some odd human text date 25th');
  });

  it('falls back to file modified time when no exif', () => {
    const meta = { file: { modified: '2025-12-25T16:48:00Z' } };
    const out = formatDateTimeOriginal(meta);
    expect(out).toMatch(/December 25, 2025/);
  });
});

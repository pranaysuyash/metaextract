import { parseExifDate } from '@/utils/metadataTransformers';

describe('parseExifDate', () => {
  it('parses standard EXIF format', () => {
    const d = parseExifDate('2025:12:25 16:48:00');
    expect(d.getFullYear()).toBe(2025);
    expect(d.getMonth()).toBe(11); // December -> 11
    expect(d.getDate()).toBe(25);
    expect(d.getHours()).toBe(16);
    expect(d.getMinutes()).toBe(48);
  });

  it('parses ISO format', () => {
    const d = parseExifDate('2025-12-25T16:48:00');
    expect(d.getFullYear()).toBe(2025);
  });

  it('parses human-friendly format with AM/PM', () => {
    const d = parseExifDate('December 25, 2025 at 4:48 PM');
    expect(d.getFullYear()).toBe(2025);
    expect(d.getMonth()).toBe(11);
    expect(d.getDate()).toBe(25);
    expect(d.getHours()).toBe(16);
    expect(d.getMinutes()).toBe(48);
  });

  it('returns invalid date when unknown format', () => {
    const d = parseExifDate('Some weird format');
    expect(isNaN(d.getTime())).toBe(true);
  });
});

import { MvpMetadata, Highlight } from '@/lib/types';

export const buildSummaryLines = (
  metadata: MvpMetadata,
  purpose: string | null,
  orderedHighlights: Highlight[]
): string => {
  const intentLabel = purpose
    ? `${purpose.charAt(0).toUpperCase()}${purpose.slice(1)}`
    : 'Unspecified';
  const lines = [
    `File: ${metadata.filename}`,
    `Type: ${metadata.filetype} (${metadata.mime_type})`,
    `Size: ${metadata.filesize}`,
    `Intent: ${intentLabel}`,
    '',
    'Highlights:',
  ];
  orderedHighlights.slice(0, 6).forEach(h => {
    lines.push(
      `- ${h.text} (Impact: ${h.impact}, Confidence: ${h.confidence})`
    );
  });
  lines.push('');
  lines.push(
    'Limitations: Metadata can be missing or stripped. Absence is not proof.'
  );
  return lines.join('\n');
};
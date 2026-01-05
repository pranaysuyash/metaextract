import { createHash, randomUUID } from 'node:crypto';
import { promisify } from 'node:util';
import { gzip, gunzip } from 'node:zlib';

const gzipAsync = promisify(gzip);
const gunzipAsync = promisify(gunzip);

const DEFAULT_SUMMARY_MAX_BYTES = Number(
  process.env.METADATA_SUMMARY_MAX_BYTES || 20000
);

export interface MetadataSummaryResult {
  summary: Record<string, unknown>;
  truncated: boolean;
}

export interface PreparedMetadataObject {
  body: Buffer;
  encoding: 'gzip' | 'identity';
  sha256: string;
  sizeBytes: number;
  contentType: string;
}

export function buildMetadataSummary(
  metadata: any,
  maxBytes: number = DEFAULT_SUMMARY_MAX_BYTES
): MetadataSummaryResult {
  const baseSummary: Record<string, unknown> = {
    filename: metadata?.filename || metadata?.file_name || null,
    mime_type: metadata?.mime_type || null,
    filesize: metadata?.filesize || null,
    fields_extracted: metadata?.fields_extracted,
    extraction_info: metadata?.extraction_info
      ? {
          processing_ms: metadata.extraction_info.processing_ms,
          engine: metadata.extraction_info.engine,
          tier: metadata.extraction_info.tier,
        }
      : undefined,
    top_level_keys: metadata ? Object.keys(metadata) : [],
    tags: metadata?.tags,
    errors: metadata?.errors,
    warnings: metadata?.warnings,
  };

  let serialized = JSON.stringify(baseSummary);
  if (Buffer.byteLength(serialized, 'utf8') <= maxBytes) {
    return { summary: baseSummary, truncated: false };
  }

  const minimalSummary = {
    filename: baseSummary.filename,
    mime_type: baseSummary.mime_type,
    filesize: baseSummary.filesize,
    fields_extracted: baseSummary.fields_extracted,
    extraction_info: baseSummary.extraction_info,
    top_level_keys: baseSummary.top_level_keys,
    summary_truncated: true,
  };

  serialized = JSON.stringify(minimalSummary);
  if (Buffer.byteLength(serialized, 'utf8') <= maxBytes) {
    return { summary: minimalSummary, truncated: true };
  }

  return {
    summary: {
      filename: minimalSummary.filename,
      mime_type: minimalSummary.mime_type,
      summary_truncated: true,
    },
    truncated: true,
  };
}

export async function prepareMetadataObject(
  metadata: any
): Promise<PreparedMetadataObject> {
  const rawBuffer = Buffer.from(JSON.stringify(metadata), 'utf8');
  const gzipped = await gzipAsync(rawBuffer);
  const useGzip = gzipped.byteLength < rawBuffer.byteLength;
  const body = useGzip ? gzipped : rawBuffer;
  const encoding: 'gzip' | 'identity' = useGzip ? 'gzip' : 'identity';
  const sha256 = createHash('sha256').update(body).digest('hex');
  return {
    body,
    encoding,
    sha256,
    sizeBytes: body.byteLength,
    contentType: 'application/json',
  };
}

export async function decompressMetadata(
  body: Buffer,
  encoding?: string
): Promise<any> {
  const normalized = (encoding || 'identity').toLowerCase();
  if (normalized === 'gzip') {
    const decompressed = await gunzipAsync(body);
    return JSON.parse(decompressed.toString('utf8'));
  }
  return JSON.parse(body.toString('utf8'));
}

export function buildObjectKey(recordId: string, fileName?: string): string {
  const safeName = (fileName || 'metadata')
    .replace(/[^a-zA-Z0-9._-]/g, '_')
    .slice(0, 120);
  return `metadata/${recordId}/${safeName || 'metadata'}.json`;
}

export function generateRecordId(): string {
  return randomUUID();
}

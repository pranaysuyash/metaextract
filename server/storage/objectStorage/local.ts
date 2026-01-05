import { promises as fs } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import {
  IObjectStorage,
  ObjectGetResult,
  ObjectInfo,
  ObjectLocation,
  ObjectPutRequest,
} from './types';

const DEFAULT_ROOT = path.resolve(process.cwd(), 'storage', 'objects');

function sanitizeKey(key: string): string {
  const normalized = key.replace(/^[\\/]+/, '');
  if (normalized.includes('..')) {
    throw new Error('Invalid object key: path traversal detected');
  }
  return normalized;
}

async function ensureDir(dirPath: string): Promise<void> {
  await fs.mkdir(dirPath, { recursive: true });
}

export class LocalObjectStorage implements IObjectStorage {
  readonly provider = 'local';
  private root: string;

  constructor(rootDirectory: string = DEFAULT_ROOT) {
    this.root = rootDirectory;
  }

  private buildPath(bucket: string, key: string): string {
    const safeKey = sanitizeKey(key);
    return path.join(this.root, bucket, safeKey);
  }

  async putObject(request: ObjectPutRequest): Promise<ObjectInfo> {
    const { bucket, key, body, contentType, encoding } = request;
    const filePath = this.buildPath(bucket, key);
    await ensureDir(path.dirname(filePath));
    await fs.writeFile(filePath, body);

    const sha256 = createHash('sha256').update(body).digest('hex');

    return {
      provider: this.provider,
      bucket,
      key,
      sizeBytes: body.byteLength,
      sha256,
      contentType,
      encoding,
      createdAt: new Date().toISOString(),
    };
  }

  async getObject(location: ObjectLocation): Promise<ObjectGetResult | null> {
    const filePath = this.buildPath(location.bucket, location.key);
    try {
      const body = await fs.readFile(filePath);
      return {
        body,
        sizeBytes: body.byteLength,
      };
    } catch (error: any) {
      if (error && error.code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }

  async deleteObject(location: ObjectLocation): Promise<void> {
    const filePath = this.buildPath(location.bucket, location.key);
    try {
      await fs.unlink(filePath);
    } catch (error: any) {
      if (error && error.code === 'ENOENT') {
        return;
      }
      throw error;
    }
  }
}

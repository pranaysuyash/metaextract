import path from 'node:path';
import { LocalObjectStorage } from './local';
import { R2ObjectStorage, type R2Config } from './r2';
import { IObjectStorage, ObjectStorageProvider } from './types';

function getEnv(name: string): string | undefined {
  const value = process.env[name];
  return value && value.trim().length > 0 ? value.trim() : undefined;
}

function resolveProvider(): ObjectStorageProvider | string {
  return (getEnv('OBJECT_STORAGE_PROVIDER') as ObjectStorageProvider) || 'local';
}

function buildR2Config(): R2Config {
  const accessKeyId = getEnv('OBJECT_STORAGE_ACCESS_KEY_ID');
  const secretAccessKey = getEnv('OBJECT_STORAGE_SECRET_ACCESS_KEY');
  const endpoint = getEnv('OBJECT_STORAGE_ENDPOINT');
  const bucket = getEnv('OBJECT_STORAGE_BUCKET');
  const region = getEnv('OBJECT_STORAGE_REGION') || 'auto';

  if (!accessKeyId || !secretAccessKey || !endpoint || !bucket) {
    throw new Error(
      'R2 object storage is enabled but required environment variables are missing (OBJECT_STORAGE_ACCESS_KEY_ID, OBJECT_STORAGE_SECRET_ACCESS_KEY, OBJECT_STORAGE_ENDPOINT, OBJECT_STORAGE_BUCKET).'
    );
  }

  return {
    accessKeyId,
    secretAccessKey,
    endpoint,
    bucket,
    region,
  };
}

export function createObjectStorage(): IObjectStorage {
  const provider = resolveProvider();

  if (provider === 'r2') {
    return new R2ObjectStorage(buildR2Config());
  }

  if (provider === 's3') {
    // Reuse the R2 client for S3-compatible providers; endpoint/region must be provided
    return new R2ObjectStorage(buildR2Config());
  }

  // Default to local filesystem-backed storage to keep development simple
  const root = getEnv('OBJECT_STORAGE_LOCAL_ROOT');
  const baseDir =
    root ||
    path.resolve(
      process.cwd(),
      'storage',
      'objects'
    );
  return new LocalObjectStorage(baseDir);
}

export * from './types';
export { LocalObjectStorage } from './local';
export { R2ObjectStorage } from './r2';

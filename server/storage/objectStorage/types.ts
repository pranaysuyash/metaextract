import { Buffer } from 'node:buffer';

export type ObjectStorageProvider = 'local' | 'r2' | 's3' | 'memory';

export interface ObjectLocation {
  provider: ObjectStorageProvider | string;
  bucket: string;
  key: string;
}

export interface ObjectPutRequest {
  bucket: string;
  key: string;
  body: Buffer;
  contentType?: string;
  encoding?: string;
}

export interface ObjectInfo extends ObjectLocation {
  sizeBytes: number;
  sha256: string;
  contentType?: string;
  encoding?: string;
  createdAt: string;
}

export interface ObjectGetResult {
  body: Buffer;
  sizeBytes: number;
  contentType?: string;
  encoding?: string;
  sha256?: string;
}

export interface IObjectStorage {
  readonly provider: ObjectStorageProvider | string;
  putObject(request: ObjectPutRequest): Promise<ObjectInfo>;
  getObject(location: ObjectLocation): Promise<ObjectGetResult | null>;
  deleteObject(location: ObjectLocation): Promise<void>;
}

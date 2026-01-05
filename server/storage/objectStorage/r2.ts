import { createHash } from 'node:crypto';
import {
  IObjectStorage,
  ObjectGetResult,
  ObjectInfo,
  ObjectLocation,
  ObjectPutRequest,
} from './types';

type S3ClientType = any;
type PutObjectCommandType = any;
type GetObjectCommandType = any;
type DeleteObjectCommandType = any;

async function loadS3Module(): Promise<{
  S3Client: S3ClientType;
  PutObjectCommand: PutObjectCommandType;
  GetObjectCommand: GetObjectCommandType;
  DeleteObjectCommand: DeleteObjectCommandType;
}> {
  try {
    // Dynamic import keeps the dependency optional until provider is enabled
    const mod = await import('@aws-sdk/client-s3');
    return {
      S3Client: (mod as any).S3Client,
      PutObjectCommand: (mod as any).PutObjectCommand,
      GetObjectCommand: (mod as any).GetObjectCommand,
      DeleteObjectCommand: (mod as any).DeleteObjectCommand,
    };
  } catch (error) {
    throw new Error(
      'Object storage provider "r2" requires @aws-sdk/client-s3. Install it and provide credentials.'
    );
  }
}

async function streamToBuffer(stream: any): Promise<Buffer> {
  const chunks: Buffer[] = [];
  for await (const chunk of stream) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks);
}

export interface R2Config {
  accessKeyId: string;
  secretAccessKey: string;
  bucket: string;
  endpoint: string;
  region?: string;
}

export class R2ObjectStorage implements IObjectStorage {
  readonly provider = 'r2';
  private clientPromise: Promise<S3ClientType>;
  private bucket: string;

  constructor(config: R2Config) {
    this.bucket = config.bucket;
    this.clientPromise = this.createClient(config);
  }

  private async createClient(config: R2Config): Promise<S3ClientType> {
    const { S3Client } = await loadS3Module();
    return new S3Client({
      region: config.region || 'auto',
      endpoint: config.endpoint,
      forcePathStyle: true,
      credentials: {
        accessKeyId: config.accessKeyId,
        secretAccessKey: config.secretAccessKey,
      },
    });
  }

  private async getCommands(): Promise<{
    client: S3ClientType;
    PutObjectCommand: PutObjectCommandType;
    GetObjectCommand: GetObjectCommandType;
    DeleteObjectCommand: DeleteObjectCommandType;
  }> {
    const client = await this.clientPromise;
    const { PutObjectCommand, GetObjectCommand, DeleteObjectCommand } =
      await loadS3Module();
    return { client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand };
  }

  async putObject(request: ObjectPutRequest): Promise<ObjectInfo> {
    const { key, body, contentType, encoding } = request;
    const { client, PutObjectCommand } = await this.getCommands();

    await client.send(
      new PutObjectCommand({
        Bucket: this.bucket,
        Key: key,
        Body: body,
        ContentType: contentType,
        ContentEncoding: encoding,
      })
    );

    const sha256 = createHash('sha256').update(body).digest('hex');

    return {
      provider: this.provider,
      bucket: this.bucket,
      key,
      sizeBytes: body.byteLength,
      sha256,
      contentType,
      encoding,
      createdAt: new Date().toISOString(),
    };
  }

  async getObject(location: ObjectLocation): Promise<ObjectGetResult | null> {
    const { client, GetObjectCommand } = await this.getCommands();
    try {
      const response = await client.send(
        new GetObjectCommand({
          Bucket: location.bucket,
          Key: location.key,
        })
      );

      if (!response || !response.Body) return null;

      const body = await streamToBuffer(response.Body);
      return {
        body,
        sizeBytes: body.byteLength,
        contentType: response.ContentType,
        encoding: response.ContentEncoding,
      };
    } catch (error: any) {
      if (error?.$metadata?.httpStatusCode === 404) {
        return null;
      }
      throw error;
    }
  }

  async deleteObject(location: ObjectLocation): Promise<void> {
    const { client, DeleteObjectCommand } = await this.getCommands();
    try {
      await client.send(
        new DeleteObjectCommand({
          Bucket: location.bucket,
          Key: location.key,
        })
      );
    } catch (error: any) {
      if (error?.$metadata?.httpStatusCode === 404) {
        return;
      }
      throw error;
    }
  }
}

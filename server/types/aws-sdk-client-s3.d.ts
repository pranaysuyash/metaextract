declare module '@aws-sdk/client-s3' {
  export class S3Client {
    constructor(options: any);
    send(command: any): Promise<any>;
  }

  export class PutObjectCommand {
    constructor(params: any);
  }

  export class GetObjectCommand {
    constructor(params: any);
  }

  export class DeleteObjectCommand {
    constructor(params: any);
  }
}

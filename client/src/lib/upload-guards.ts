export interface UploadGuardConfig {
  maxBytes: number;
  allowedMimes: string[];
  allowedExtensions: string[];
}

export interface UploadGuardResult {
  ok: boolean;
  reason?: 'file_too_large' | 'unsupported_mime' | 'unsupported_extension';
  message?: string;
}

const formatBytes = (bytes: number): string => {
  const mb = bytes / (1024 * 1024);
  return `${Math.round(mb)} MB`;
};

const getExtension = (name: string): string | null => {
  const index = name.lastIndexOf('.');
  if (index <= 0) return null;
  return name.slice(index).toLowerCase();
};

export const validateUploadFile = (
  file: File,
  config: UploadGuardConfig
): UploadGuardResult => {
  const ext = getExtension(file.name);
  const mime = (file.type || '').toLowerCase();

  if (file.size > config.maxBytes) {
    return {
      ok: false,
      reason: 'file_too_large',
      message: `Max ${formatBytes(config.maxBytes)}. Allowed: ${config.allowedExtensions.join(', ')}`,
    };
  }

  if (mime && !config.allowedMimes.includes(mime)) {
    return {
      ok: false,
      reason: 'unsupported_mime',
      message: `Unsupported file type. Allowed: ${config.allowedExtensions.join(', ')}`,
    };
  }

  if (!ext || !config.allowedExtensions.includes(ext)) {
    return {
      ok: false,
      reason: 'unsupported_extension',
      message: `Unsupported file extension. Allowed: ${config.allowedExtensions.join(', ')}`,
    };
  }

  return { ok: true };
};

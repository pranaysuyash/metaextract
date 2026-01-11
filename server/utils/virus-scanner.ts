/**
 * Virus Scanner Adapter
 * 
 * Abstraction layer for virus scanning.
 * Currently uses a mock/pass-through implementation.
 * Ready for ClamAV or Cloud-based scanning integration.
 */


export interface ScanResult {
  isClean: boolean;
  virusName?: string;
  error?: string;
}

/**
 * Scan a file buffer for viruses.
 * For MVP without ClamAV installed:
 * - Checks for EICAR test signature fallback
 * - Returns clean by default otherwise
 * 
 * @param buffer - File content to scan
 * @returns ScanResult
 */
export async function scanBuffer(buffer: Buffer): Promise<ScanResult> {
  // 1. Basic signature check for EICAR test file (Standard Anti-Virus Test File)
  const eicarSignature = 'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*';
  if (buffer.toString().includes(eicarSignature)) {
    return {
      isClean: false,
      virusName: 'EICAR-Test-Signature',
    };
  }

  // 2. Production ClamAV Check (Placeholder)
  // In production with ClamAV installed:
  // try {
  //   const { stdout } = await execAsync(`clamdscan --stream ...`);
  //   ...
  // }

  // Default to clean/safe for MVP if no scanner configured
  return { isClean: true };
}

/**
 * Scan a file path for viruses.
 * 
 * @param filePath - Path to file
 * @returns ScanResult
 */
export async function scanFile(_filePath: string): Promise<ScanResult> {
  // Placeholder for `clamdscan <filePath>`
  // MVP: fail-open until a scanner is configured.
  return { isClean: true };
}

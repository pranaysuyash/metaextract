/**
 * File Type Analysis Utility
 * 
 * Detects actual file types vs extensions and provides contextual warnings/suggestions
 * for better UX when uploading files for metadata extraction.
 */

export interface FileAnalysis {
  /** Detected file type category */
  category: 'image' | 'video' | 'audio' | 'document' | 'medical' | 'scientific' | 'unknown';
  
  /** Specific format detected */
  format?: string;
  
  /** Warnings about the file */
  warnings: string[];
  
  /** Helpful suggestions for the user */
  suggestions: string[];
  
  /** Expected metadata fields by category */
  expectedFields: { category: string; count: number }[];
  
  /** Whether this is a native format or derivative */
  isNativeFormat: boolean;
}

/**
 * Check if file is a DICOM medical imaging file by magic bytes
 */
export function isDICOMFile(file: File): Promise<boolean> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const buffer = e.target?.result as ArrayBuffer;
      if (!buffer) {
        resolve(false);
        return;
      }
      
      const view = new DataView(buffer);
      
      // DICOM files have "DICM" at byte 128-131
      if (buffer.byteLength >= 132) {
        const dicmBytes = new Uint8Array(buffer.slice(128, 132));
        const dicmString = String.fromCharCode(...dicmBytes);
        if (dicmString === 'DICM') {
          resolve(true);
          return;
        }
      }
      
      // Some DICOM files don't have preamble, check for tag patterns
      if (buffer.byteLength >= 4) {
        const firstBytes = view.getUint16(0, true); // Little endian
        // Common DICOM group tags: 0x0002, 0x0008, 0x0010
        if (firstBytes === 0x0002 || firstBytes === 0x0008 || firstBytes === 0x0010) {
          resolve(true);
          return;
        }
      }
      
      resolve(false);
    };
    
    reader.onerror = () => resolve(false);
    
    // Read first 256 bytes to check for DICOM magic
    reader.readAsArrayBuffer(file.slice(0, 256));
  });
}

/**
 * Analyze file and provide contextual information
 */
export async function analyzeFile(file: File): Promise<FileAnalysis> {
  const analysis: FileAnalysis = {
    category: 'unknown',
    warnings: [],
    suggestions: [],
    expectedFields: [],
    isNativeFormat: true
  };
  
  const ext = file.name.toLowerCase().split('.').pop() || '';
  const mimeType = file.type || '';
  
  // ============================================================================
  // Medical Files
  // ============================================================================
  
  if (ext === 'dcm' || ext === 'dicom' || mimeType === 'application/dicom') {
    const isDICOM = await isDICOMFile(file);
    
    if (isDICOM) {
      analysis.category = 'medical';
      analysis.format = 'DICOM';
      analysis.expectedFields = [
        { category: 'Patient Information', count: 8 },
        { category: 'Study Information', count: 8 },
        { category: 'Series Information', count: 6 },
        { category: 'Image Information', count: 12 },
        { category: 'Device Information', count: 5 }
      ];
      analysis.suggestions.push('✅ Native DICOM file detected - full medical metadata will be extracted');
    } else {
      analysis.category = 'image';
      analysis.warnings.push('⚠️ File has .dcm extension but is not a valid DICOM file');
      analysis.suggestions.push('This may be a renamed file. Upload the original DICOM file for medical metadata.');
    }
  }
  
  // JPEG/PNG that might be photographed medical scans
  else if ((ext === 'jpg' || ext === 'jpeg' || ext === 'png') && file.size > 5 * 1024 * 1024) {
    analysis.category = 'image';
    analysis.isNativeFormat = true;
    
    // Check if filename suggests it's a medical scan photo
    const medicalKeywords = ['xray', 'x-ray', 'scan', 'mri', 'ct', 'ultrasound', 'dicom', 'medical'];
    const hasMedicalKeyword = medicalKeywords.some(keyword => 
      file.name.toLowerCase().includes(keyword)
    );
    
    if (hasMedicalKeyword || file.size > 10 * 1024 * 1024) {
      analysis.warnings.push('⚠️ This appears to be a photo of a medical scan, not a native DICOM file');
      analysis.suggestions.push('For full medical metadata, upload the original .dcm file from the imaging equipment');
      analysis.suggestions.push('This JPEG will only contain camera/photo metadata, not medical scan parameters');
    }
    
    analysis.expectedFields = [
      { category: 'Camera Settings', count: 15 },
      { category: 'Image Properties', count: 8 },
      { category: 'GPS/Location', count: 5 }
    ];
  }
  
  // ============================================================================
  // RAW Image Files
  // ============================================================================
  
  else if (['cr2', 'cr3', 'nef', 'arw', 'dng', 'orf', 'rw2', 'raf', 'pef'].includes(ext)) {
    analysis.category = 'image';
    analysis.format = `RAW (${ext.toUpperCase()})`;
    analysis.isNativeFormat = true;
    analysis.expectedFields = [
      { category: 'Camera Settings', count: 50 },
      { category: 'MakerNotes', count: 80 },
      { category: 'Image Properties', count: 20 },
      { category: 'GPS/Location', count: 5 }
    ];
    analysis.suggestions.push('✅ Native RAW file - full camera metadata including MakerNotes will be extracted');
  }
  
  // ============================================================================
  // Standard Images
  // ============================================================================
  
  else if (mimeType.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff'].includes(ext)) {
    analysis.category = 'image';
    analysis.isNativeFormat = true;
    
    // Check if this might be a screenshot
    if (file.name.toLowerCase().includes('screenshot') || 
        file.name.toLowerCase().includes('screen shot')) {
      analysis.warnings.push('⚠️ This appears to be a screenshot');
      analysis.suggestions.push('Screenshots typically lose original photo metadata. Upload the original file for complete metadata.');
      analysis.isNativeFormat = false;
    }
    
    analysis.expectedFields = [
      { category: 'Basic EXIF', count: 15 },
      { category: 'Image Properties', count: 8 },
      { category: 'GPS/Location', count: 5 }
    ];
  }
  
  // ============================================================================
  // Video Files
  // ============================================================================
  
  else if (mimeType.startsWith('video/') || ['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext)) {
    analysis.category = 'video';
    analysis.isNativeFormat = true;
    analysis.expectedFields = [
      { category: 'Video Properties', count: 20 },
      { category: 'Audio Tracks', count: 10 },
      { category: 'Container Metadata', count: 15 }
    ];
    
    if (file.size > 500 * 1024 * 1024) {
      analysis.warnings.push('⚠️ Large video file - extraction may take 30-60 seconds');
    }
  }
  
  // ============================================================================
  // Audio Files
  // ============================================================================
  
  else if (mimeType.startsWith('audio/') || ['mp3', 'flac', 'wav', 'ogg', 'm4a'].includes(ext)) {
    analysis.category = 'audio';
    analysis.isNativeFormat = true;
    analysis.expectedFields = [
      { category: 'Audio Properties', count: 15 },
      { category: 'ID3 Tags', count: 20 },
      { category: 'Album Art', count: 3 }
    ];
  }
  
  // ============================================================================
  // Documents
  // ============================================================================
  
  else if (mimeType === 'application/pdf' || ext === 'pdf') {
    analysis.category = 'document';
    analysis.format = 'PDF';
    analysis.isNativeFormat = true;
    analysis.expectedFields = [
      { category: 'Document Properties', count: 10 },
      { category: 'PDF Metadata', count: 8 },
      { category: 'Creation Info', count: 5 }
    ];
  }
  
  // ============================================================================
  // Scientific Files
  // ============================================================================
  
  else if (['fits', 'fit', 'fts'].includes(ext)) {
    analysis.category = 'scientific';
    analysis.format = 'FITS (Astronomy)';
    analysis.isNativeFormat = true;
    analysis.expectedFields = [
      { category: 'Header Keywords', count: 100 },
      { category: 'WCS', count: 20 },
      { category: 'Observation Data', count: 30 }
    ];
    analysis.suggestions.push('✅ FITS astronomy file - extensive header metadata will be extracted');
  }
  
  // ============================================================================
  // Unknown/Other
  // ============================================================================
  
  else {
    analysis.category = 'unknown';
    analysis.warnings.push('⚠️ Unknown file type - basic file properties will be extracted');
    analysis.suggestions.push('For best results, upload common formats: JPG, PNG, RAW, MP4, PDF, DICOM');
  }
  
  return analysis;
}

/**
 * Format file analysis for display
 */
export function formatAnalysis(analysis: FileAnalysis): string {
  const parts: string[] = [];
  
  if (analysis.format) {
    parts.push(`Format: ${analysis.format}`);
  }
  
  if (analysis.warnings.length > 0) {
    parts.push(...analysis.warnings);
  }
  
  if (analysis.suggestions.length > 0) {
    parts.push(...analysis.suggestions);
  }
  
  if (analysis.expectedFields.length > 0) {
    const fieldSummary = analysis.expectedFields
      .map(f => `${f.category}: ~${f.count} fields`)
      .join(', ');
    parts.push(`Expected metadata: ${fieldSummary}`);
  }
  
  return parts.join('\n');
}

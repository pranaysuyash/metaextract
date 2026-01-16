import { useState, useCallback } from 'react';

/**
 * Patterns that suggest a file might be a map/GPS screenshot
 * These patterns trigger automatic OCR detection
 */
const OCR_MAP_PATTERNS = /gps|map|location|coords|coordinate|geotag/i;

interface UseOcrDetectionResult {
  ocrAutoApplied: boolean;
  ocrUserOverride: boolean;
  shouldAutoApplyOcr: (filename: string) => boolean;
  applyOcrOverride: () => void;
  clearOcrOverride: () => void;
  setAutoApplied: () => void;
  resetOcrState: () => void;
}

/**
 * Hook to manage OCR detection and auto-application logic
 * Automatically detects map/GPS screenshots and suggests OCR
 */
export const useOcrDetection = (): UseOcrDetectionResult => {
  const [ocrAutoApplied, setOcrAutoApplied] = useState(false);
  const [ocrUserOverride, setOcrUserOverride] = useState(false);

  /**
   * Check if filename suggests map/GPS content that would benefit from OCR
   */
  const shouldAutoApplyOcr = useCallback((filename: string): boolean => {
    return OCR_MAP_PATTERNS.test(filename.toLowerCase());
  }, []);

  /**
   * User manually toggled OCR - this overrides auto-detection
   */
  const applyOcrOverride = useCallback(() => {
    setOcrUserOverride(true);
    setOcrAutoApplied(false);
  }, []);

  /**
   * Clear user override (e.g., when file changes)
   */
  const clearOcrOverride = useCallback(() => {
    setOcrUserOverride(false);
    setOcrAutoApplied(false);
  }, []);

  /**
   * Set OCR as auto-applied (system detected map/GPS pattern)
   */
  const setAutoApplied = useCallback(() => {
    setOcrAutoApplied(true);
    setOcrUserOverride(false);
  }, []);

  /**
   * Reset all OCR state (useful when changing files)
   */
  const resetOcrState = useCallback(() => {
    setOcrAutoApplied(false);
    setOcrUserOverride(false);
  }, []);

  return {
    ocrAutoApplied,
    ocrUserOverride,
    shouldAutoApplyOcr,
    applyOcrOverride,
    clearOcrOverride,
    setAutoApplied,
    resetOcrState,
  };
};
/**
 * useKeyFindings Hook
 *
 * Custom React hook to extract and manage key findings from metadata.
 * Handles loading states and error cases gracefully.
 */

import { useMemo } from 'react';
import { extractKeyFindings, KeyFindings } from '@/utils/metadataTransformers';

interface UseKeyFindingsOptions {
  skipWhen?: boolean;
  skipWhere?: boolean;
  skipDevice?: boolean;
  skipAuthenticity?: boolean;
}

interface UseKeyFindingsResult {
  findings: KeyFindings | null;
  isLoading: boolean;
  error: Error | null;
}

/**
 * Hook to extract key findings from metadata
 *
 * @param metadata - Raw metadata object from extraction
 * @param options - Options to control which findings to include
 * @returns Object containing findings, loading state, and any errors
 *
 * @example
 * ```tsx
 * const { findings, error } = useKeyFindings(metadata);
 *
 * if (error) return <div>Error: {error.message}</div>;
 * if (!findings) return <div>No findings</div>;
 *
 * return <KeyFindings findings={findings} />;
 * ```
 */
export function useKeyFindings(
  metadata: any | null | undefined,
  options: UseKeyFindingsOptions = {}
): UseKeyFindingsResult {
  const { 
    skipWhen = false,
    skipWhere = false,
    skipDevice = false,
    skipAuthenticity = false
  } = options;

  const result = useMemo<UseKeyFindingsResult>(() => {
    try {
      if (!metadata) {
        return {
          findings: null,
          isLoading: false,
          error: null
        };
      }

      // Extract findings
      const findings = extractKeyFindings(metadata);

      // Apply skip options
      const filtered: KeyFindings = {
        ...findings,
        when: skipWhen ? null : findings.when,
        where: skipWhere ? null : findings.where,
        device: skipDevice ? null : findings.device,
        authenticity: skipAuthenticity ? findings.authenticity : findings.authenticity
      };

      return {
        findings: filtered,
        isLoading: false,
        error: null
      };
    } catch (error) {
      return {
        findings: null,
        isLoading: false,
        error: error instanceof Error ? error : new Error(String(error))
      };
    }
  }, [metadata, skipWhen, skipWhere, skipDevice, skipAuthenticity]);

  return result;
}

/**
 * Hook to check if any findings are available
 *
 * @param findings - Key findings object
 * @returns True if at least one finding is available
 */
export function useHasFindings(findings: KeyFindings | null): boolean {
  return useMemo(() => {
    if (!findings) return false;
    return !!(findings.when || findings.where || findings.device);
  }, [findings]);
}

/**
 * Hook to get a summary string of findings
 *
 * @param findings - Key findings object
 * @returns Human-readable summary of findings
 *
 * @example
 * ```
 * "Captured on January 3, 2025 in San Francisco with iPhone 15 Pro"
 * ```
 */
export function useKeyFindingsSummary(findings: KeyFindings | null): string {
  return useMemo(() => {
    if (!findings) return '';

    const parts = [];

    if (findings.when) {
      parts.push(`Captured on ${findings.when}`);
    }

    if (findings.where) {
      parts.push(`in ${findings.where}`);
    }

    if (findings.device) {
      parts.push(`with ${findings.device}`);
    }

    return parts.join(' ');
  }, [findings]);
}

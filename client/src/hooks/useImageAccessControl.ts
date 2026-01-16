import { useCallback } from 'react';
import { MvpMetadata } from '../lib/types';
import { trackImagesMvpEvent } from '../lib/images-mvp-analytics';

interface UseImageAccessControlResult {
  isLimited: boolean;
  canExport: boolean;
  handleDownloadJson: () => void;
  handleDownloadFullTxt: () => void;
  handleDownloadSummary: (buildSummaryLines: () => string) => void;
}

export const useImageAccessControl = (
  metadata: MvpMetadata,
  purpose: string | null
): UseImageAccessControlResult => {
  const isLimited = Boolean(
    (metadata._limited ?? metadata._trial_limited) ||
    (metadata.access?.granted ?? metadata.access?.trial_granted)
  );
  const canExport = !isLimited;

  const trackEvent = useCallback(
    (event: string, properties: Record<string, unknown> = {}) => {
      trackImagesMvpEvent(event, properties);
    },
    []
  );

  const handleDownloadJson = useCallback(() => {
    if (!canExport) {
      return;
    }
    trackEvent('export_json_downloaded', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
      purpose: purpose || 'unset',
    });
    const payload = JSON.stringify(metadata, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
    link.href = url;
    link.download = `${baseName}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [canExport, metadata, purpose, trackEvent]);

  const handleDownloadFullTxt = useCallback(() => {
    if (!canExport) {
      return;
    }
    trackEvent('export_full_txt_downloaded', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
      purpose: purpose || 'unset',
    });
    const payload = JSON.stringify(metadata, null, 2);
    const blob = new Blob([payload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
    link.href = url;
    link.download = `${baseName}-full.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }, [canExport, metadata, purpose, trackEvent]);

  const handleDownloadSummary = useCallback(
    (buildSummaryLines: () => string) => {
      const payload = buildSummaryLines();
      const blob = new Blob([payload], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
      link.href = url;
      link.download = `${baseName}-summary.txt`;
      link.click();
      URL.revokeObjectURL(url);
      trackEvent('export_summary_downloaded', {
        filetype: metadata.filetype,
        mime_type: metadata.mime_type,
        purpose: purpose || 'unset',
      });
    },
    [metadata, purpose, trackEvent]
  );

  return {
    isLimited,
    canExport,
    handleDownloadJson,
    handleDownloadFullTxt,
    handleDownloadSummary,
  };
};
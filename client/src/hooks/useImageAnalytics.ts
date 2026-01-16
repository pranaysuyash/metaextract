import { useCallback, useRef, useEffect } from 'react';
import { trackImagesMvpEvent } from '../lib/images-mvp-analytics';
import { MvpMetadata, TabValue, PurposeValue, DensityMode } from '../lib/types';

interface UseImageAnalyticsProps {
  metadata: MvpMetadata | null;
  activeTab: TabValue;
  densityMode: DensityMode;
  purpose: PurposeValue | null;
  showPurposeModal: boolean;
  showPricingModal: boolean;
}

interface UseImageAnalyticsResult {
  trackEvent: (event: string, properties?: Record<string, unknown>) => void;
  trackPurposeSelect: (value: PurposeValue) => void;
  trackDensityChange: (value: DensityMode) => void;
  trackPaywallCta: (lockedTotal: number) => void;
}

export const useImageAnalytics = ({
  metadata,
  activeTab,
  densityMode,
  purpose,
  showPurposeModal,
  showPricingModal,
}: UseImageAnalyticsProps): UseImageAnalyticsResult => {
  const purposePromptLogged = useRef(false);
  const formatHintLogged = useRef(false);
  const paywallLogged = useRef(false);
  const resultsLogged = useRef(false);

  const trackEvent = useCallback(
    (event: string, properties: Record<string, unknown> = {}) => {
      trackImagesMvpEvent(event, properties);
    },
    []
  );

  useEffect(() => {
    if (!showPurposeModal || purposePromptLogged.current) return;
    trackEvent('purpose_prompt_shown', { location: 'results' });
    purposePromptLogged.current = true;
  }, [showPurposeModal, trackEvent]);

  useEffect(() => {
    if (!metadata) return;
    trackEvent('tab_changed', {
      tab: activeTab,
      density: densityMode,
      purpose: purpose || 'unset',
    });
  }, [activeTab, densityMode, metadata, purpose, trackEvent]);

  useEffect(() => {
    if (!metadata || formatHintLogged.current) return;
    const hint = getFormatHint(metadata.mime_type, metadata.filename);
    if (!hint) return;
    trackEvent('format_hint_shown', {
      mime_type: metadata.mime_type,
      hint: hint.title,
    });
    formatHintLogged.current = true;
  }, [metadata, trackEvent]);

  useEffect(() => {
    if (!metadata || resultsLogged.current) return;
    trackEvent('results_viewed', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
    });
    resultsLogged.current = true;
  }, [metadata, trackEvent]);

  useEffect(() => {
    if (!metadata || paywallLogged.current) return;
    const isLimited =
      (metadata._limited ?? metadata._trial_limited) ||
      (metadata.access?.granted ?? metadata.access?.trial_granted);
    const summary = metadata.registry_summary?.image as
      | { exif?: number; iptc?: number; xmp?: number }
      | undefined;
    const lockedTotal =
      (summary?.exif ?? 0) + (summary?.iptc ?? 0) + (summary?.xmp ?? 0);
    if (isLimited && lockedTotal > 0) {
      trackEvent('paywall_preview_shown', {
        locked_total: lockedTotal,
      });
      paywallLogged.current = true;
    }
  }, [metadata, trackEvent]);

  const trackPurposeSelect = useCallback(
    (value: PurposeValue) => {
      trackEvent('purpose_selected', { purpose: value });
      if (value === 'explore') {
        trackEvent('density_changed', {
          mode: 'advanced',
          source: 'purpose_select',
        });
      }
    },
    [trackEvent]
  );

  const trackDensityChange = useCallback(
    (value: DensityMode) => {
      trackEvent('density_changed', { mode: value });
    },
    [trackEvent]
  );

  const trackPaywallCta = useCallback(
    (lockedTotal: number) => {
      trackEvent('paywall_cta_clicked', {
        locked_total: lockedTotal,
      });
    },
    [trackEvent]
  );

  return {
    trackEvent,
    trackPurposeSelect,
    trackDensityChange,
    trackPaywallCta,
  };
};

const getFormatHint = (mimeType: string, filename: string) => {
  const normalizedMime = (mimeType || '').toLowerCase();
  const filenameLower = (filename || '').toLowerCase();
  if (normalizedMime.includes('heic') || normalizedMime.includes('heif')) {
    return {
      title: 'HEIC photo detected',
      body: 'HEIC photos (common on iPhones) usually include rich metadata such as capture settings and device details.',
      tone: 'emerald' as const,
    };
  }
  if (normalizedMime.includes('webp')) {
    return {
      title: 'WebP image detected',
      body: 'WebP metadata support varies by source. Some uploads may only include basic file details.',
      tone: 'amber' as const,
    };
  }
  if (normalizedMime.includes('png')) {
    const screenshotHint =
      filenameLower.includes('screenshot') ||
      filenameLower.includes('screen shot');
    return {
      title: screenshotHint ? 'Screenshot detected' : 'PNG image detected',
      body: screenshotHint
        ? 'Screenshots often contain minimal metadata. For richer data, try the original photo.'
        : 'PNG files (especially graphics) often contain minimal metadata compared to camera photos.',
      tone: 'amber' as const,
    };
  }
  if (normalizedMime.includes('jpeg') || normalizedMime.includes('jpg')) {
    return {
      title: 'JPEG photo detected',
      body: 'JPEG photos usually include camera metadata such as device, timestamps, and settings.',
      tone: 'emerald' as const,
    };
  }
  return null;
};
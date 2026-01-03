const SESSION_STORAGE_KEY = 'metaextract_session_id';

const SIZE_BUCKETS = [
  { label: '<1MB', max: 1 * 1024 * 1024 },
  { label: '1-5MB', max: 5 * 1024 * 1024 },
  { label: '5-20MB', max: 20 * 1024 * 1024 },
  { label: '20-100MB', max: 100 * 1024 * 1024 },
];

export function getImagesMvpSessionId(): string | null {
  if (typeof window === 'undefined') return null;
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  }
  return sessionId;
}

export function getFileSizeBucket(bytes?: number | null): string {
  if (!bytes || bytes <= 0) return 'unknown';
  for (const bucket of SIZE_BUCKETS) {
    if (bytes <= bucket.max) return bucket.label;
  }
  return '>100MB';
}

export function trackImagesMvpEvent(
  event: string,
  properties: Record<string, unknown> = {}
): void {
  if (typeof window === 'undefined' || !event) return;

  const payload = JSON.stringify({
    event,
    properties,
    sessionId: getImagesMvpSessionId(),
  });

  if (navigator.sendBeacon) {
    const blob = new Blob([payload], { type: 'application/json' });
    navigator.sendBeacon('/api/images_mvp/analytics/track', blob);
    return;
  }

  fetch('/api/images_mvp/analytics/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
    keepalive: true,
  }).catch(() => {
    // Best-effort analytics.
  });
}

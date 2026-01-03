# Images MVP Analytics Report

This document captures the analytics events tracked by the Images MVP UI and the report endpoint that aggregates them. Use this to validate product decisions, personas, and paywall conversion.

## Events tracked

All events are recorded under `product: "images_mvp"` via `POST /api/images_mvp/analytics/track`.

### Core funnel

- `results_viewed` — fired once when a results page renders.
  - properties: `filetype`, `mime_type`
- `paywall_preview_shown` — fired when a trial report shows locked field counts.
  - properties: `locked_total`
- `paywall_cta_clicked` — fired when user clicks the paywall CTA to buy credits.
  - properties: `locked_total`

### Intent + disclosure

- `purpose_prompt_shown` — purpose selector modal shown.
  - properties: `location`
- `purpose_prompt_opened` — purpose selector opened via CTA.
  - properties: `location`
- `purpose_selected` — user picks a purpose.
  - properties: `purpose`, `location`
- `purpose_skipped` — user skips purpose selection.
  - properties: `location`
- `density_changed` — toggles Normal / Advanced.
  - properties: `mode`, `source`
- `tab_changed` — intent tabs selected.
  - properties: `tab`, `density`, `purpose`

### Education + format framing

- `format_hint_shown` — format-specific note shown.
  - properties: `mime_type`, `hint`

### Exports

- `export_summary_downloaded` — summary text file downloaded.
  - properties: `filetype`, `mime_type`, `purpose`
- `summary_copied` — summary copied to clipboard.
  - properties: `purpose`
- `export_json_downloaded` — JSON export downloaded (paid users only).
  - properties: `filetype`, `mime_type`, `purpose`

## Report endpoint

`GET /api/images_mvp/analytics/report`

Query params:
- `period`: `24h` | `7d` | `30d` | `all` (default: `7d`)
- `limit`: max events to consider (default: 5000)

Response summary fields:
- `period`: range, since/until timestamps, limit
- `totals`: events, sessions, users, first/last event timestamp
- `events`: count by event name
- `purposes`: selected counts by purpose + prompt shown/opened/skipped
- `tabs`: counts by tab
- `density`: counts by mode
- `formats`: counts by `mime_type` for hints and results views
- `exports`: counts for JSON, summary download, summary copied
- `paywall`: previewed and CTA clicked counts

### Example response

```json
{
  "period": {
    "range": "7d",
    "since": "2026-01-01T00:00:00.000Z",
    "until": "2026-01-08T00:00:00.000Z",
    "limit": 5000
  },
  "totals": {
    "events": 128,
    "sessions": 42,
    "users": 5,
    "firstEventAt": "2026-01-01T00:00:00.000Z",
    "lastEventAt": "2026-01-08T00:00:00.000Z"
  },
  "events": {
    "results_viewed": 30,
    "paywall_preview_shown": 18
  },
  "purposes": {
    "selected": { "privacy": 12, "authenticity": 6 },
    "prompt_shown": 20,
    "prompt_opened": 8,
    "skipped": 2
  },
  "tabs": { "privacy": 18, "authenticity": 7 },
  "density": { "normal": 22, "advanced": 4 },
  "formats": {
    "hints": { "image/png": 3 },
    "results": { "image/jpeg": 19 }
  },
  "exports": {
    "json": 4,
    "summary": 11,
    "summary_copied": 9
  },
  "paywall": {
    "previewed": 18,
    "cta_clicked": 5
  }
}
```

## Download behavior

Downloads are intentionally staged:
- Summary text export is always available (trial or paid) so users can keep a lightweight report.
- JSON export is only available after trial (paid credits), reinforcing the value of the full report.

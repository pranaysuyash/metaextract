# UX Audit Spine (MetaExtract)

Path suggestion: `docs/ux/ux-audit.md`

This document is the UX audit spine for MetaExtract. It summarizes the first-principles audit and cross-persona findings, and points to canonical references to avoid duplication.

Canonical references:

* Persona library: `docs/ux/personas.md`
* Agent execution playbook: `docs/ux/agent-playbook.md`

Status:

* This is a living doc. Updates should preserve truth boundaries and format-specific realities.

---

## 1) Purpose

MetaExtract’s extraction depth is strong, but UX is currently optimized for a forensic-native user. This creates three recurring problems:

1. Non-forensic users misread relevance and bounce.
2. Locked content feels like fake scarcity if previews are not tied to real fields in the uploaded file.
3. “Medical” is the sharp edge where over-claims can destroy trust.

This audit defines what should change, what must never be implied, and how agents should convert these insights into shippable tasks.

---

## 2) Scope

In scope:

* Discovery to upload to results to paywall to export.
* Result presentation defaults based on user intent.
* Trust, privacy, compliance clarity at the UX level.
* Missingness semantics: Not Present vs Not Supported vs Locked.
* Persona-specific expectations and success criteria.

Out of scope for this doc:

* Backend extraction roadmap (covered elsewhere).
* Model-based inference of “intent” beyond deterministic rules.
* Large-scale enterprise features (SSO, admin dashboards) beyond UX framing.

---

## 3) Non-negotiables

1. Truth boundaries must be explicit.
2. “Missing” must never be ambiguous.
3. Locked content must only reference fields that exist for the user’s file.
4. Medical claims must be format-gated (DICOM vs photographed scans).
5. Every persona expects an export artifact.

Implementation guidance is in `docs/ux/agent-playbook.md`.

---

## 4) First-principles audit walkthrough (medical scan photo upload)

This is the single most important first-principles flow because it exposes expectation mismatch and trust failure fastest.

### Step 1: Discovery (first 10 seconds)

Observed:

* Homepage reads like digital forensics for courts/journalists/security.
* “7,000+ hidden fields” and MakerNotes-heavy copy feels camera-centric.

User expectation (medical professional):

* Wants DICOM/PACS relevance, privacy assurances, and clinical value.

Primary failure:

* Audience mismatch. A doctor may bounce immediately.

What must change:

* Segmented landing variant or intent routing that makes medical truth explicit.
* If medical container formats are not supported yet, the landing must not imply otherwise.

### Step 2: Upload

Observed:

* “Medical” badge appears in supported formats, but it is not explained.
* User uploads `chest_xray.jpg` (photographed scan) and expects scan parameters.

Primary failure:

* The UI does not warn that JPEG of a scan will mostly contain camera metadata, not scan metadata.

What must change:

* Detect and label photographed scans as such.
* Provide “get the original DICOM” guidance if user expects clinical metadata.

### Step 3: Processing feedback

Observed:

* Progress feels opaque, creates anxiety (is it stuck, is it uploading, is it analyzing).
* No clear “what is happening” explanation (especially for sensitive content users).

What must change:

* Minimal but truthful processing states:

  * Uploading
  * Extracting metadata (list extractors used)
  * Normalizing fields
  * Ready

### Step 4: Results

Observed:

* User sees generic fields (file size, dimensions, GPS not found) that feel irrelevant to medical use.
* Tabs and categories (forensic, technical) are not contextualized.

Primary failure:

* Results are not intent-centered. Clinically irrelevant data appears first.

What must change:

* Default view must align to intent.
* Medical view should only appear for actual medical container formats.
* For photographed scans, default to a “Photographed Scan” summary:

  * What is possible from this file
  * What is not possible
  * Why

### Step 5: Locked content and paywall

Observed:

* Locked sections appear early but do not explain what they contain for this file.
* Creates “false scarcity” perception.

What must change:

* Paywall preview panel must show:

  * “Unlock +N additional fields for this file”
  * Top locked fields that actually exist for this file
  * Why they matter for this intent

### Step 6: Pricing comprehension

Observed:

* Tier names by persona (“Forensic”) confuse users in other domains.
* Credits vs subscription decision is unclear.

What must change:

* Reframe tiers by capability and output:

  * Basic: highlights + core fields
  * Pro: full extractors + export
  * Evidence: chain-of-custody report features
  * Research/Enterprise: API/bulk workflows
* Keep persona marketing, but the product tiers must explain capabilities.

---

## 5) Persona summary (what to prioritize)

This audit covers many personas. The canonical list is in `docs/ux/personas.md`. Use that file as source of truth.

Priority personas to address first (because they expose trust and conversion failures fastest):

1. Medical professional (P1): highest risk of misleading expectations.
2. Investigative journalist / OSINT (P2/P13): strong fit, needs workflow and export.
3. Privacy-conscious consumer (P4): trust, clarity, remediation.
4. Photographer (P5): unlock value is real, needs batch/export.
5. Law enforcement / legal (P3/P15): defensibility, reports, audit trail framing.

---

## 6) Cross-persona problems (root causes)

### Problem A: Value proposition mismatch

Cause:

* One forensic-forward landing and results UI for everyone.

Fix:

* Intent-first defaults and segmented landing variants.

### Problem B: Missingness ambiguity

Cause:

* “Not found” and “locked” are used without differentiating:

  * not present in file
  * not supported by extractor
  * gated

Fix:

* Formal missingness states in UI and exports.

### Problem C: Paywall distrust

Cause:

* Locked blocks appear without evidence they exist for this file.

Fix:

* Real-field paywall previews and count-based unlock messaging.

### Problem D: No export artifact

Cause:

* UI assumes interactive exploration is enough.

Fix:

* Always provide at least JSON export. Add report export for evidence personas.

### Problem E: Format reality not surfaced

Cause:

* UI does not show what format was detected and what extractors applied.

Fix:

* Add a lightweight diagnostics summary (even for non-technical users, phrased simply).

---

## 7) Product-wide UX principles

1. Intent-first, not feature-first.
2. Highlights first, raw data second.
3. Always show confidence and limitations for interpretation-heavy conclusions.
4. Make extraction pipeline legible (format detected, extractors used).
5. Paywall must be provably honest (file-specific preview).
6. Exports are not optional. They are the deliverable.

---

## 8) Execution plan (phased)

Phase 0: Fix trust and comprehension (high leverage)

* Missingness states everywhere.
* Highlights card on results.
* Intent selector + deterministic defaults.
* Paywall preview panel (real locked fields only).
* Always-available JSON export.

Phase 1: Format-specific truth (especially medical)

* DICOM vs non-DICOM detection.
* Photographed scan warning and guidance.
* Medical view gating based on container format.

Phase 2: Workflow acceleration for strong-fit personas

* Case mode: group files, compare key fields, export case report.
* Evidence report export: hashes, tool versions, extraction steps summary.
* Photography mode grouping: camera, lens, maker notes, edit history.

Phase 3: Enterprise and research readiness (doc-level UX scaffolding)

* Trust page and compliance posture narrative.
* API/CLI documentation placeholders even if features are staged.

Agents should generate tasks using `docs/ux/agent-playbook.md`.

---

## 9) Metrics and instrumentation (minimum viable)

Track:

* Landing to first upload conversion.
* Upload to results completion rate.
* Time-to-first-value (first render of Highlights card).
* Paywall click-through rate and conversion.
* Export usage rate (JSON download).
* Bounce rate from results page (especially for medical-flagged flows).
* “Photographed scan warning shown” count and subsequent user actions.

---

## 10) How to use this doc

* Use this as the summary for product decisions and internal alignment.
* Use `personas.md` for detailed persona expectations and default views.
* Use `agent-playbook.md` to convert findings into tasks with acceptance criteria.

Change control rule:

* Any change that affects claims or medical messaging must update this doc and `personas.md` in the same PR.

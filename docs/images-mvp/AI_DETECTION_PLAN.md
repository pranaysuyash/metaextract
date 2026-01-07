# AI-Generated Image Detection Integration Plan

**Date:** January 7, 2026
**Priority:** Critical (2026 Competitive Moat)
**Status:** Draft

---

## 1. Overview
As of 2026, distinguishing between genuine photographs and high-fidelity AI-generated images is the primary challenge for digital forensics. MetaExtract will integrate specialized AI detection APIs to provide an "AI Confidence Score" alongside traditional metadata analysis.

## 2. Integration Target: Hive AI
Hive AI is the current industry leader for diffusion-model detection.
- **API**: `https://api.thehive.ai/api/v2/predict/image`
- **Output**: Multi-class probability scores (e.g., `midjourney: 0.98`, `stable_diffusion: 0.02`, `not_ai: 0.00`).

## 3. Implementation Plan

### Step 1: Backend Integration (`server/extractor/ai_detection.py`)
- Create a new extraction module that calls the Hive AI API.
- Cache results by file hash to minimize API costs.
- Integrate into the `Mike (Investigator)` persona flow.

### Step 2: UI Implementation
- Add an "AI Authenticity" gauge to the top of the Results page.
- Show specific model detection (e.g., "Detected artifacts consistent with DALL-E 3").
- Contrast AI scores with EXIF findings (e.g., "AI detected despite 'iPhone 15' EXIF headers").

### Step 3: Combined Risk Scoring
- Create a unified "Trust Score" that combines:
    1. AI Detection (High weight)
    2. C2PA Verification (High weight)
    3. Metadata Consistency (Medium weight)
    4. Geolocation Verification (Low weight)

## 4. Why this matters
Metadata heuristics (EXIF) are easily faked. In 2026, an authenticity tool without an AI detection score is incomplete. This feature converts MetaExtract from a "technical tool" into a "truth engine."

---
*End of Plan*

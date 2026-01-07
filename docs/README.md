# Documentation Index

**Last Updated:** January 7, 2026

This directory contains comprehensive documentation for MetaExtract images_mvp abuse resistance, dependency updates, and implementation planning.

---

## Quick Start

### For Abuse/Misuse Prevention

1. Start with [**ABUSE_ANALYSIS_REPORT.md**](./abuse-resistance/ABUSE_ANALYSIS_REPORT.md) - Full vulnerability analysis
2. Then read [**FREE_TIER_IMPLEMENTATION.md**](./abuse-resistance/FREE_TIER_IMPLEMENTATION.md) - Detailed implementation plan
3. Track progress with [**IMPLEMENTATION_STATUS.md**](./implementation/IMPLEMENTATION_STATUS.md)

### For Dependency Updates

1. Start with [**DEPRECATION_UPDATE_PLAN.md**](./maintenance/DEPRECATION_UPDATE_PLAN.md) - All deprecations and update plans
2. Track progress with [**IMPLEMENTATION_STATUS.md**](./implementation/IMPLEMENTATION_STATUS.md)

---

## Abuse Resistance Documentation

### `/docs/abuse-resistance/`

| Document                                                                      | Description                                                                                                                    | Status      |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------- |
| [ABUSE_ANALYSIS_REPORT.md](./abuse-resistance/ABUSE_ANALYSIS_REPORT.md)       | Complete abuse/misuse analysis from attacker perspective. Identifies all vulnerability vectors and attack patterns.            | ✅ Complete |
| [FREE_TIER_IMPLEMENTATION.md](./abuse-resistance/FREE_TIER_IMPLEMENTATION.md) | Detailed implementation plan for abuse-resistant free tier. Includes all code examples, architecture, and deployment sequence. | ✅ Complete |

**Key Findings:**

**Critical Vulnerability:** Cookie-based device tracking is the primary weakness. Attackers can easily bypass by clearing cookies.

**Recommended Solution:** Server-issued device tokens (httpOnly, signed) + identity ladder with progressive friction.

**Attack Vectors Identified:**

1. Rate-limit evasion (HIGH RISK)
2. Session reset abuse (HIGH RISK)
3. IP hopping (MEDIUM RISK)
4. Headless browser abuse (MEDIUM RISK)
5. File spam uploads (MEDIUM-HIGH RISK)
6. Cost-extraction attacks (CRITICAL)

**What System Does Well:**

- ✅ File type validation (MIME + extension + magic byte)
- ✅ File size limits
- ✅ Multi-tier rate limiting
- ✅ WebSocket progress tracking
- ✅ Credit-based system

---

## Maintenance Documentation

### `/docs/maintenance/`

| Document                                                               | Description                                                                                                                                 | Status      |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| [DEPRECATION_UPDATE_PLAN.md](./maintenance/DEPRECATION_UPDATE_PLAN.md) | Complete analysis of Python deprecations, Node.js dependency updates, and TypeScript errors. Includes update commands and migration guides. | ✅ Complete |

**Key Findings:**

**Python Deprecations:**

- ✅ `audioop` deprecation FIXED - Suppressed with `warnings.filterwarnings()`
- Root cause: `pydub` and `audioread` use deprecated module internally
- Long-term solution: Monitor upstream for Python 3.13 compatibility

**Node.js Dependencies:**

- 🔶 27 packages outdated
- 6 major version updates requiring careful testing:
  - **Express 5** (breaking: `req.param()`, `res.json()`, query parser)
  - **jsPDF 4** (breaking: API changes)
  - **Recharts 3** (breaking: prop changes)
  - **React Resizable Panels 4** (breaking: API restructure)
  - **@types/express 5** (type changes)
  - **@types/node 25** (type changes)

**TypeScript Errors Found:**

- 6 existing errors unrelated to deprecations
- Locations:
  - `server/rateLimitMiddleware.ts:85` - Implicit any type
  - `server/security-utils.ts:92,107` - Control characters in regex
  - `server/routes/images-mvp.ts:110,111` - Redis type incompatibility
  - `server/routes/extraction.ts:276,1403` - React hooks called conditionally
  - `client/src/pages/images-mvp/index.tsx:25,43` - React accessibility

---

## Implementation Documentation

### `/docs/implementation/`

| Document                                                              | Description                                                                                 | Status      |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------- |
| [IMPLEMENTATION_STATUS.md](./implementation/IMPLEMENTATION_STATUS.md) | Tracks progress on all implementations. Includes checklist, timeline, and success criteria. | ✅ Complete |

**Implementation Progress:**

**Free Tier Abuse Resistance:**

- 📋 Design Complete
- ❌ Implementation Pending
- Estimated completion: 3 weeks

**Dependency Updates:**

- ✅ Analysis Complete
- ❌ Implementation Pending
- Estimated completion: 4 weeks (phased approach)

---

## File Structure

```
docs/
├── README.md (this file)
├── abuse-resistance/
│   ├── ABUSE_ANALYSIS_REPORT.md
│   └── FREE_TIER_IMPLEMENTATION.md
├── maintenance/
│   └── DEPRECATION_UPDATE_PLAN.md
└── implementation/
    └── IMPLEMENTATION_STATUS.md
```

---

## Quick Reference: Common Commands

### To Update Safe Packages (Phase 1)

```bash
npm update @types/jest @typescript-eslint/eslint-plugin @typescript-eslint/parser \
  axe-core concurrently dodopayments drizzle-zod esbuild \
  exiftool-vendored framer-motion jspdf-autotable \
  lucide-react react-hook-form typescript vite ws date-fns
```

### To Apply Updated package.json

```bash
cp package.json package.json.backup
cp package.json.updated package.json
npm install
```

### To Generate Device Token Secret

```bash
openssl rand -hex 32
# Add to .env as: DEVICE_TOKEN_SECRET=<output>
```

---

## Timeline Summary

### Week 1: Core Infrastructure

- Create utility files (device-token, cost-calculator, identity-ladder)
- Create queue and challenge systems
- Phase 1 dependency updates (safe packages)

### Week 2: Integration

- Database migrations
- Server route integration
- Client-side integration

### Week 3: Testing & Deployment

- Unit and integration testing
- Load testing and circuit breaker verification
- Staging and production deployment

### Week 4: Remaining Updates

- Phase 2 dependency updates (medium risk)
- Phase 3 major updates (one at a time)
- TypeScript error fixes

---

## Philosophy Notes

### Global Caps Are Wrong

**Problem:** Global cap (e.g., "500 total extractions/day") fails arbitrarily for legit users at scale.

**Attacker Bypass:** Attackers just wait until tomorrow.

**Better Approach:** Queue with priority - paid stays fast, free slows down gracefully under load.

### Attacker Economics

**Goal:** Make "sign up for Google" (30 seconds) easier than "write abuse script" (10 minutes).

**Mechanism:** Progressive friction identity ladder:

- Anonymous (2 credits) → Challenge (+3) → Email (+10) → OAuth (+20) → Paid

### Server-Issued Tokens Are Critical

**Problem:** Client-controlled cookies allow trivial bypass (just clear cookies).

**Solution:** Server-issued httpOnly cookies that client cannot modify or read.

### Cost-Based Budgeting Protects Resources

**Problem:** Request count doesn't reflect actual compute cost.

**Solution:** Cost units based on file type and size. HEIC/RAW cost more than JPG/PNG.

---

## Success Metrics

### Free Tier Abuse Resistance

- [ ] No global caps that break for legit users
- [ ] Server-controlled identity (not client cookies)
- [ ] Cost-based budgeting (bound compute exposure)
- [ ] Progressive friction (identity ladder)
- [ ] Load shedding via queue priorities
- [ ] Revenue-protecting (paid always faster)

### Dependencies

- [ ] No deprecation warnings in console
- [ ] All packages up-to-date
- [ ] All TypeScript errors resolved
- [ ] Express 5 tested and deployed
- [ ] jsPDF 4 tested and deployed
- [ ] Recharts 3 tested and deployed

---

## Related Files

### Production Files Referenced in Documentation

**Server-side:**

- `server/utils/device-token.ts` (TO BE CREATED)
- `server/utils/cost-calculator.ts` (TO BE CREATED)
- `server/utils/identity-ladder.ts` (TO BE CREATED)
- `server/utils/extraction-queue.ts` (TO BE CREATED)
- `server/middleware/challenge.ts` (TO BE CREATED)
- `server/routes/images-mvp.ts` (TO BE UPDATED)
- `server/utils/free-quota-enforcement.ts` (TO BE UPDATED)
- `server/extractor/modules/audio_metadata_extended.py` (✅ UPDATED)

**Client-side:**

- `client/src/components/images-mvp/simple-upload.tsx` (TO BE UPDATED)
- `client/src/components/images-mvp/challenge-modal.tsx` (TO BE CREATED)
- `client/src/pages/images-mvp/index.tsx` (TO BE UPDATED)

**Configuration:**

- `.env` (TO BE UPDATED - add DEVICE_TOKEN_SECRET)
- `package.json` (UPDATED VERSION CREATED)

---

## Questions?

For questions or clarifications:

1. **Abuse/Misuse:** See [ABUSE_ANALYSIS_REPORT.md](./abuse-resistance/ABUSE_ANALYSIS_REPORT.md) for attack vectors and recommendations

2. **Implementation Details:** See [FREE_TIER_IMPLEMENTATION.md](./abuse-resistance/FREE_TIER_IMPLEMENTATION.md) for complete code examples

3. **Dependency Updates:** See [DEPRECATION_UPDATE_PLAN.md](./maintenance/DEPRECATION_UPDATE_PLAN.md) for update commands and migration guides

4. **Progress Tracking:** See [IMPLEMENTATION_STATUS.md](./implementation/IMPLEMENTATION_STATUS.md) for current status

---

## Document Preservation

**Note:** These documents preserve the complete analysis and design work. Historical documentation has value for:

- Understanding decision rationale
- Learning from implementation approaches
- Reference for debugging issues
- Onboarding new team members

**Never delete old documentation.** Create backup versions when updating instead.

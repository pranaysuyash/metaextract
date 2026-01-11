# Source Of Truth

These are the authoritative references for how MetaExtract is supposed to work.
When these disagree with other docs or code comments, treat this list as the
source of truth and update other references.

## Product and Architecture
- `docs/metaextract_design.md` — product design doc and roadmap
- `shared/tierConfig.ts` — tier definitions, limits, feature flags

## Core Runtime Contracts
- `server/routes/images-mvp.ts` — Images MVP extraction route and request flow
- `server/utils/extraction-helpers.ts` — Python response contract interface

## How To Update
If you change product behavior, update the relevant source-of-truth file and
then update secondary docs to match.

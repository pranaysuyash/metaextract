# UX Agent Playbook

This file captures execution-ready UX tasks and the definition of done. It is the canonical companion to the persona library.

## Example Tasks Agents Can Execute Immediately

1) Add missingness states everywhere
- Persona: P4, P20
- Goal: stop the "missing looks like a bug" problem
- Acceptance: every field group shows Not Present vs Not Supported vs Locked with correct counts

2) Add highlights card and default views
- Persona: P10, P4, P2
- Goal: time-to-first-value under 10 seconds
- Acceptance: first screen shows a summary that is correct and non-misleading

3) Paywall preview uses real locked fields
- Persona: P5, P2
- Goal: paywall feels honest
- Acceptance: locked list only includes fields that exist for the file, shows +N, and explains value

4) Medical format warning
- Persona: P1
- Goal: stop medical disappointment and legal risk
- Acceptance: photographed scans show warning and guidance, DICOM shows medical tags

5) Export JSON button for every result
- Persona: P7, P11, P2
- Goal: unblock research and evidence workflows
- Acceptance: download JSON always works and includes schema version and extractor versions

## Definition of Done

A UX task is done only if:
- It is persona-specific.
- It ships a user-visible improvement.
- It includes truth boundaries and missingness semantics.
- It has acceptance criteria and a QA checklist.
- It does not introduce misleading claims.

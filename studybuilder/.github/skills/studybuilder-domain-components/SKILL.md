---
name: studybuilder-domain-components
description: Domain-specific guardrails when modernizing StudyBuilder study/library components.
---

# StudyBuilder domain guardrails

## Study components (`src/components/studies/`)
- Preserve study design matrix behavior (epochs/arms/visits/schedule)
- Keep CDISC/ODM/SDTM-related logic intact
- Keep validation strict; do not loosen rules
- Preserve export structures (XML/JSON)

## Library components (`src/components/library/`)
- Be careful with nested data structures (activity instances, item classes)
- Preserve reusability contracts (these are often shared across views)

## Output contract
- No domain behavior drift (especially exports and validation)



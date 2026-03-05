---
name: vue-modernization-verification
description: Verification checklist and recommended commands after a component modernization.
---

# Verification

## Must verify
- No `this` remains in `<script setup>`
- Props/emits/slots unchanged
- No new console errors/warnings

## Recommended repo checks
- Lint: `yarn lint`
- Format: `yarn format`

## If tests exist for the component
- Update selectors/expectations only as needed
- Avoid snapshot churn unless unavoidable



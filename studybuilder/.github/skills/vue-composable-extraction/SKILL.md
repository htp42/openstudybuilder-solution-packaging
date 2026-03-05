---
name: vue-composable-extraction
description: Extract reusable logic into composables during modernization when it reduces duplication without changing behavior.
---

# Composable extraction

## When to extract
- Same logic appears in multiple components
- A mixin is reused broadly
- A large block of imperative logic clutters the component and is self-contained

## Rules
- Keep composables small and single-purpose (`useXxx`)
- Place in `src/composables/`
- Preserve behavior and return shapes
- Use the composable immediately in the component you modernize

## Output contract
- Minimal new API surface
- No speculative “framework” code



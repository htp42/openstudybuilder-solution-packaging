---
name: vuetify-3-compat
description: Ensure component modernization keeps Vuetify 3 usage compatible and consistent with StudyBuilder UI conventions.
---

# Vuetify 3 compatibility

## Rules
- Do not redesign UI during modernization.
- Preserve existing props/events usage unless it’s deprecated/broken.
- Keep accessibility attrs intact (labels, aria-*, etc.).

## Common areas to verify
- Dialogs: v-model binding and close behavior
- Data tables: headers/items/slot syntax
- Form inputs: `rules`, `density`, `variant`, `rounded`, `hide-details`

## Output contract
- No new Vuetify warnings in console
- Visual and interaction behavior unchanged



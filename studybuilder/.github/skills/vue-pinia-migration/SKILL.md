---
name: vue-pinia-migration
description: Replace Vuex patterns with Pinia usage in StudyBuilder components, preserving state and action semantics.
---

# Vuex -> Pinia (StudyBuilder)

## Use when
- Component uses `mapState`, `mapGetters`, `mapActions`, `this.$store`, or Vuex module helpers.

## Rules
- Prefer store composables: `const store = useXStore()`
- Use `storeToRefs(store)` for reactive state/getters
- Call actions directly: `await store.someAction()`
- Do not wrap actions in extra methods unless it adds real value

## Quick patterns
- State/getters:
  - ❌ `const { currentStudy } = useStudiesStore()`
  - ✅ `const store = useStudiesStore(); const { currentStudy } = storeToRefs(store)`

## Output contract
- Keep external behavior the same (loading flags, errors, returned values)
- Avoid rewriting store internals unless required by the migration



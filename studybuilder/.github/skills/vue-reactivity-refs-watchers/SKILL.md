---
name: vue-reactivity-refs-watchers
description: Correctly migrate refs, watchers, and reactive state to Composition API without losing reactivity.
---

# Reactivity, refs, watchers

## Template refs
- Replace `this.$refs.x` with `const x = ref(null)` + `<... ref="x" />`
- Only access template refs after mount (`onMounted`) or defensively (`x.value?.focus()`)

## Watchers
- Watch refs, not `.value`:
  - ❌ `watch(name.value, ...)`
  - ✅ `watch(name, ...)`
- For props:
  - ✅ `watch(() => props.someProp, ...)`
- Use `{ immediate: true }` only when the Options API watcher was immediate / relied on mount-time behavior

## Reactivity pitfalls
- Don’t destructure reactive objects unless using `toRefs` / `storeToRefs`

## Output contract
- No reactivity regressions (computed/watches update as before)



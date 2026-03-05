---
name: vue-options-to-script-setup
description: Convert Vue Options API components to Vue 3 Composition API using <script setup> while preserving props/emits/slots and runtime behavior.
---

# Vue Options API -> `<script setup>`

## Goal
Produce a complete `<script setup>` conversion with **no behavior changes** and **no remaining `this.` usage**.

## Required preservation
- Prop names/defaults/requiredness
- Emitted event names and payload shapes
- Slots and their names
- Any parent expectations around refs/exposed methods

## Conversion mapping (mechanical)
- `props` -> `defineProps()`
- `emits` / `this.$emit` -> `defineEmits()`
- `data()` -> `ref()` / `reactive()` state
- `computed` -> `computed(() => ...)`
- `methods` -> plain functions
- `watch` -> `watch()` (correct watch sources)
- lifecycle:
  - `created`/`mounted` -> `onMounted` (and friends)
  - `beforeUnmount` -> `onBeforeUnmount`

## Common tricky areas
- `this.$attrs` / `inheritAttrs`: use `useAttrs()` or keep template behavior
- `this.$slots`: use `useSlots()` only if needed
- mixins:
  - If local-only: inline into setup
  - If reused: extract composable and import it
- `name:` option when needed for tests/devtools: `defineOptions({ name: 'ComponentName' })`

## Output contract
- Return a fully updated component file
- Call out any intentional contract change (should be rare)



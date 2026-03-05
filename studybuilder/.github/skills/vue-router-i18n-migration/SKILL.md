---
name: vue-router-i18n-migration
description: Replace this.$router/this.$route and this.$t usage with Vue Router 4 and Vue I18n composables.
---

# Router + i18n migration

## Router
- `this.$route` -> `const route = useRoute()`
- `this.$router` -> `const router = useRouter()`
- Access params/query via `route.params` / `route.query`

## i18n
- `this.$t('key')` -> `const { t } = useI18n(); t('key')`
- Keep translation keys unchanged

## Output contract
- Navigation behavior identical (same route names/params)
- No translation key changes



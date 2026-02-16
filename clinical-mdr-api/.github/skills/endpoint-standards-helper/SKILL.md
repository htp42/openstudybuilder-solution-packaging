---
name: ensure-endpoint-name-adherence-to-restful
description: Ensures API endpoint names follow RESTful conventions. Use when reviewing or renaming endpoints to be resource-oriented (nouns), consistently pluralized, hierarchical, and aligned with standard HTTP methods.
---

# Ensure endpoint names follow RESTful conventions

## Use this when reviewing or renaming endpoints
1. Run `git diff --staged` to list changed routes.
2. For each changed/renamed endpoint, verify naming rules below and update code or docs accordingly.
3. Produce a commit message that follows the recommended format (see "Commit message format").

## RESTful naming rules (quick checklist)
- Resource-oriented nouns, not verbs: use /users, not /getUsers or /createUser.
- Prefer plural resource names: /orders, /users/{user_id}/orders.
- Hierarchical, relationship-driven paths: /projects/{id}/tasks.
- Map actions to HTTP methods:
   - GET — read
   - POST — create
   - PUT/PATCH — update
   - DELETE — remove
- Path parameters for identities: /items/{item_id}, not /items?id=...
- Use query parameters for filtering, sorting, pagination: ?page_number=2&page_size=50
- Consistent casing (prefer kebab-case across the API).
- Avoid RPC-style paths and action verbs in path segments.
- Keep URLs stable; avoid breaking changes when possible.

## Commit message format for endpoint renames/changes
- Summary (≤50 chars): concise change (e.g., "Rename user endpoints to RESTful nouns")
- Body: Explain what changed and why (one paragraph). List all renamed or added endpoints and affected components (routes, controllers, docs).
- Footer: Include migration notes or client impacts if breaking.
- End the message with the single word:
   Done

## Examples
- Before: POST /create-user -> After: POST /users
- Before: GET /user/{id}/orders -> After: GET /users/{user_id}/orders

Follow these rules when updating code, tests, and documentation so endpoint names remain consistent and predictable.


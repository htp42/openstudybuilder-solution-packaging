# Data Corrections: Activity Versioning Gap Fix

## 1. Fix Activity_000317 versioning gap (Bug #3221548)

### Problem description
Activity_000317 has a 36-day chronological gap in its HAS_VERSION relationships
between version 7.0 and version 7.1. Version 7.0 ends on 2024-11-14T15:20:11.139020Z
but version 7.1 doesn't start until 2024-12-20T12:41:58.289320Z, creating a gap
from November 14 to December 20, 2024. This violates the rule that versions should
be chronologically continuous without gaps.

### Change description
- Extend the end_date of version 7.0's HAS_VERSION relationship from
  2024-11-14T15:20:11.139020Z to 2024-12-20T12:41:58.289320Z
- This ensures continuous versioning between version 7.0 and 7.1
- The correction is idempotent and can be run multiple times safely

### Nodes and relationships affected
- `HAS_VERSION` relationship for Activity_000317 version 7.0
- Expected changes: 1 relationship property modified



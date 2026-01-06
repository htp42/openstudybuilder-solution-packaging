## Data corrections: overview of data_corrections.correction_016

PRD Data Corrections: Before Release 2.2



## 1. Correction: add_missing_retired_relationships

### Insert a Final HAS_VERSION relationship for Retired library items where the only HAS_VERSION relationship is Retired

#### Problem description
In an earlier version of the StdyBuilder API, retiring an item would create a new value node
linked by a HAS_VERSION relationship with status "Retired".
It should only have added a new HAS_VERSION relationship with status "Retired" to an the existing latest value node.
As a result, some value nodes are linked to their root nodes only by a HAS_VERSION relationship with status "Retired",
without a corresponding "Final" or "Draft" HAS_VERSION relationship.
This correction inserts a short lived "Final" HAS_VERSION relationship to such value nodes.

#### Change description
- Insert a short lived "Final" HAS_VERSION relationship to value nodes that only have a "Retired" HAS_VERSION relationship

#### Nodes and relationships affected
- `ActivityRoot`, `ActivityValue`, `ActivityInstanceRoot`, `ActivityInstanceValue` nodes
- `HAS_VERSION`, `LATEST_FINAL` relationships
- Expected changes: 18 new relationships created, 9 relationships deleted, 9 relationship properties modified


## 2. Correction: fix_activity_000317_versioning_gap

### Fix Activity_000317 versioning gap (Bug #3221548)

#### Problem description
Activity_000317 has a 36-day chronological gap in its HAS_VERSION relationships
between version 7.0 and version 7.1. Version 7.0 ends on 2024-11-14T15:20:11.139020Z
but version 7.1 doesn't start until 2024-12-20T12:41:58.289320Z, creating a gap
from November 14 to December 20, 2024. This violates the rule that versions should
be chronologically continuous without gaps.

#### Change description
- Extend the end_date of version 7.0's HAS_VERSION relationship from
  2024-11-14T15:20:11.139020Z to 2024-12-20T12:41:58.289320Z
- This ensures continuous versioning between version 7.0 and 7.1
- The correction is idempotent and can be run multiple times safely

#### Nodes and relationships affected
- `HAS_VERSION` relationship for Activity_000317 version 7.0
- Expected changes: 1 relationship property modified


## 3. Correction: remove_cat_submission_value_suffix

### Remove the "nnnn_CAT" and "nnnn_SUB_CAT" suffixes from submission values in category codelists

#### Problem description
In StudyBuilder before 2.0, submision values had to be globaly unique.
To achieve this, a suffix, "nnnn_CAT" or "nnnn_SUB_CAT", was appended to submission values in category codelists.
With StudyBuilder 2.0, submission values only need to be unique within their codelist,
so this suffix is no longer necessary and should be removed.
This corretion needs to be applied in the
EVNTCAT, EVNTSCAT, FINDCAT, FINDSCAT, INTVCAT and INTVSCAT codelists.

#### Change description
- Remove the "nnnn_CAT" and "nnnn_SUB_CAT" suffixes from the `submission_value` property of `CTCodelistTerm` nodes

#### Nodes and relationships affected
- `CTCodelistTerm` nodes in the EVNTCAT, EVNTSCAT, FINDCAT, FINDSCAT, INTVCAT and INTVSCAT codelists
- Expected changes: 872 node properties modified



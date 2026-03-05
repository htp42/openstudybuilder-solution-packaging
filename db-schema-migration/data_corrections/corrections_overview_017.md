## Data corrections: overview of data_corrections.correction_017

PRD Data Corrections: Before Release 2.5



## 1. Correction: fix_duplicated_unique_visit_numbers_and_incorrect_visit_number_visit_name_and_short_name

#### Problem description
There exists an issue that some different StudyVisits share the same unique visit number.
It should not be the case as unique visit number should be a unique value across all StudyVisits within a Study.
The issue existed only for groups of subvisits when the anchor visit timing was edited and it was not properly updated.
#### Change description
- Update unique visit number and other properties (visit_name, short_visit_label, visit_number) for StudyVisits having wrong values
- Correct values are taken from API that calculates them based on the StudyVisit full schedule.
#### Nodes and relationships affected
- `StudyVisit` node
#### Expected changes: 2 StudyVisits (StudyVisit_004596, StudyVisit_009676) updated by correcting (visit_number, unique_visit_number, short_visit_label) properties and relationship to dependent visit_name node


## 2. Correction: remove_duplicated_non_visit_and_unscheduled_visits

#### Problem description
There should only exist one Non-visit and Unscheduled-visit in a given Study.
There was an API issue that when both Non-visit and Unscheduled-visit existed in given Study and we were editing
Non-visit to be Unscheduled-visit or vice versa, the API allowed to created duplicated Non or Unscheduled visit by edition.
#### Change description
- Delete duplicated Non-visit or Unscheduled-visit in the Study.
#### Nodes and relationships affected
- `StudyVisit` node
#### Expected changes: 1 call for DELETE /study-visits/{StudyVisit_000196} to delete duplicated non-visit.


## 3. Correction: rebuild_missing_protocol_soa_snapshots

### Problem description
Some (RELEASED) Study versions do not have a Protocol SoA snapshot created due to a (fixed) bug.
### Change description
- Rebuild missing/failing Protocol SoA snapshots for RELEASED Study versions, using contemporary StudySelections but latest ordering.
### Relationships affected
- (StudyValue)-[:HAS_PROTOCOL_SOA_CELL]->(StudySelection)
- (StudyValue)-[:HAS_PROTOCOL_SOA_FOOTNOTE]->(StudySelection)
### Expected changes
- Old relationships removed
- New relationships created



## 4. Correction: remove_study_action_with_broken_after

#### Problem description
Some StudyAction nodes exist without AFTER relationships. These are leftover from migrated study selections
where the StudySelection nodes were deleted but the StudyAction nodes remained. Every StudyAction (except
UpdateSoASnapshot) must have an AFTER relationship.
#### Change description
- Delete StudyAction nodes that don't have AFTER relationships (excluding UpdateSoASnapshot nodes).
#### Nodes and relationships affected
- `StudyAction` nodes


## 5. Correction: fix_not_coherent_in_time_library_selection

#### Problem description
Some StudyActivity nodes reference ActivityValue nodes that don't have valid HAS_VERSION
relationships at the time when the Create action was performed. This happens when the
ActivityValue version's start_date or end_date doesn't cover the Create action date.
Specifically, Activity_000317 version 7.0's HAS_VERSION relationship doesn't cover
the dates when some Create actions were performed.
#### Change description
- Fix version 7.0 of Activity_000317 by adjusting its HAS_VERSION start_date to cover
  the earliest Create action date that references it
#### Nodes and relationships affected
- `HAS_VERSION` relationship for Activity_000317 version 7.0


## 6. Correction: fix_studies_different_versions_with_the_same_start_date

#### Problem description
Some StudyRoot nodes have different versions with the same start_date, which violates
the constraint that no version should have a start_date greater than or equal to the
latest version's start_date. This happens when a previous version has the same start_date
as the latest version.
#### Change description
- For each StudyRoot, find versions with start_date >= the latest version's start_date
- Subtract 1 millisecond from those previous versions' start_date to make them earlier
- This ensures proper chronological ordering of versions
#### Nodes and relationships affected
- `HAS_VERSION` relationships for StudyRoot nodes


## 7. Correction: remove_soa_cell_relationships_without_released_study

#### Problem description
Some StudyValue nodes have HAS_PROTOCOL_SOA_CELL or HAS_PROTOCOL_SOA_FOOTNOTE relationships
when the StudyRoot doesn't have a RELEASED or LOCKED version. These relationships were created
as a result of bad cloning and should not exist without a released or locked version.
#### Change description
- Delete HAS_PROTOCOL_SOA_CELL and HAS_PROTOCOL_SOA_FOOTNOTE relationships from StudyValue nodes
  where the StudyRoot doesn't have a RELEASED or LOCKED version
#### Nodes and relationships affected
- `HAS_PROTOCOL_SOA_CELL` relationships
- `HAS_PROTOCOL_SOA_FOOTNOTE` relationships



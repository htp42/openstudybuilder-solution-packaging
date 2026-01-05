"""PRD Data Corrections: Before Release 2.2"""

import os

from data_corrections.utils.utils import (
    capture_changes,
    get_db_driver,
    run_cypher_query,
    save_md_title,
)
from migrations.utils.utils import get_logger, print_counters_table
from verifications import correction_verification_016

LOGGER = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()
CORRECTION_DESC = "data-correction-batch-016"


def main(run_label="correction"):
    desc = f"Running data corrections on DB '{os.environ['DATABASE_NAME']}'"
    LOGGER.info(desc)
    save_md_title(run_label, __doc__, desc)

    fix_activity_000317_versioning_gap(DB_DRIVER, LOGGER, run_label)
    remove_cat_submission_value_suffix(DB_DRIVER, LOGGER, run_label)
    add_missing_retired_relationships(DB_DRIVER, LOGGER, run_label)


@capture_changes(
    verify_func=correction_verification_016.test_activity_000317_versioning_gap
)
def fix_activity_000317_versioning_gap(db_driver, log, run_label):
    """
    ## Fix Activity_000317 versioning gap (Bug #3221548)

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
    """

    desc = "Fix Activity_000317 versioning gap between version 7.0 and 7.1"
    log.info(f"Run: {run_label}, {desc}")

    # Query to fix the versioning gap by extending version 7.0 end_date to version 7.1 start_date
    query = """
        MATCH (ar:ActivityRoot {uid: "Activity_000317"})
        MATCH (ar)-[hv1:HAS_VERSION {version: "7.0"}]->(av1:ActivityValue)
        MATCH (ar)-[hv2:HAS_VERSION {version: "7.1"}]->(av2:ActivityValue)
        WHERE hv1.end_date IS NOT NULL
            AND hv2.start_date IS NOT NULL
            AND hv1.end_date < hv2.start_date  // Only update if there's a gap
        SET hv1.end_date = hv2.start_date
        RETURN
            ar.uid AS activity_uid,
            hv1.version AS updated_version,
            hv1.end_date AS new_end_date,
            hv2.start_date AS v7_1_start_date
    """

    _, summary = run_cypher_query(db_driver, query)
    counters = summary.counters
    print_counters_table(counters)
    return counters.contains_updates


@capture_changes(
    verify_func=correction_verification_016.test_remove_cat_submission_value_suffix
)
def remove_cat_submission_value_suffix(db_driver, log, run_label):
    """
    ## Remove the "nnnn_CAT" and "nnnn_SUB_CAT" suffixes from submission values in category codelists

    ### Problem description
    In StudyBuilder before 2.0, submision values had to be globaly unique.
    To achieve this, a suffix, "nnnn_CAT" or "nnnn_SUB_CAT", was appended to submission values in category codelists.
    With StudyBuilder 2.0, submission values only need to be unique within their codelist,
    so this suffix is no longer necessary and should be removed.
    This corretion needs to be applied in the
    EVNTCAT, EVNTSCAT, FINDCAT, FINDSCAT, INTVCAT and INTVSCAT codelists.

    ### Change description
    - Remove the "nnnn_CAT" and "nnnn_SUB_CAT" suffixes from the `submission_value` property of `CTCodelistTerm` nodes

    ### Nodes and relationships affected
    - `CTCodelistTerm` nodes in the EVNTCAT, EVNTSCAT, FINDCAT, FINDSCAT, INTVCAT and INTVSCAT codelists
    - Expected changes: 872 node properties modified
    """

    desc = "Remove the nnnn_CAT and nnnn_SUB_CAT suffixes from submission values in category codelists"
    log.info(f"Run: {run_label}, {desc}")

    query = """
        MATCH (clr:CTCodelistRoot)-[har:HAS_ATTRIBUTES_ROOT]-(clar:CTCodelistAttributesRoot)-[clalat:LATEST]-(clav:CTCodelistAttributesValue)
        WHERE clav.submission_value IN ["EVNTCAT", "EVNTSCAT", "FINDCAT", "FINDSCAT", "INTVCAT", "INTVSCAT"]
        CALL {
            WITH clr
            MATCH (clr)-[:HAS_TERM]->(clt:CTCodelistTerm)
            WHERE clt.submission_value ENDS WITH "_CAT"
            WITH clt, clt.submission_value AS submval
            WITH clt, replace(submval, " FIND_SUB_CAT", "") AS submval
            WITH clt, replace(submval, " FIND_CAT", "") AS submval
            WITH clt, replace(submval, " INTRV_SUB_CAT", "") AS submval
            WITH clt, replace(submval, " INTRV_CAT", "") AS submval
            WITH clt, replace(submval, " EVNT_SUB_CAT", "") AS submval
            WITH clt, replace(submval, " EVNT_CAT", "") AS submval
            SET clt.submission_value = trim(submval)
        }
        RETURN *
    """

    _, summary = run_cypher_query(db_driver, query)
    counters = summary.counters
    print_counters_table(counters)
    return counters.contains_updates


@capture_changes(
    verify_func=correction_verification_016.test_missing_retired_relationships
)
def add_missing_retired_relationships(db_driver, log, run_label):
    """
    ## Insert a Final HAS_VERSION relationship for Retired library items where the only HAS_VERSION relationship is Retired

    ### Problem description
    In an earlier version of the StdyBuilder API, retiring an item would create a new value node
    linked by a HAS_VERSION relationship with status "Retired".
    It should only have added a new HAS_VERSION relationship with status "Retired" to an the existing latest value node.
    As a result, some value nodes are linked to their root nodes only by a HAS_VERSION relationship with status "Retired",
    without a corresponding "Final" or "Draft" HAS_VERSION relationship.
    This correction inserts a short lived "Final" HAS_VERSION relationship to such value nodes.

    ### Change description
    - Insert a short lived "Final" HAS_VERSION relationship to value nodes that only have a "Retired" HAS_VERSION relationship

    ### Nodes and relationships affected
    - `ActivityRoot`, `ActivityValue`, `ActivityInstanceRoot`, `ActivityInstanceValue` nodes
    - `HAS_VERSION`, `LATEST_FINAL` relationships
    - Expected changes: 18 new relationships created, 9 relationships deleted, 9 relationship properties modified

    """

    desc = "Add missing Final HAS_VERSION relationships for Retired library items"
    log.info(f"Run: {run_label}, {desc}")

    query = """
        MATCH (root)-[ret:HAS_VERSION {status: "Retired"}]->(value)
        WHERE NOT (root)-[:HAS_VERSION {status: "Final"}]->(value) AND NOT (root)-[:HAS_VERSION {status: "Draft"}]->(value)
        WITH root, value, ret, ret.start_date + duration({seconds: 1}) AS adjusted_date
        CREATE (root)-[final:HAS_VERSION {
            version: ret.version,
            status: "Final",
            start_date: ret.start_date,
            end_date: adjusted_date,
            author_id: ret.author_id,
            change_description: ret.change_description
        }]->(value)
        SET ret.start_date = adjusted_date
        WITH root, value
        CALL {
            WITH root, value
            MATCH (root)-[latest_ret:HAS_VERSION {status: "Retired"}]->(value)
            WHERE latest_ret.end_date IS NULL
            MATCH (root)-[lf:LATEST_FINAL]->()
            CREATE (root)-[new_lf:LATEST_FINAL]->(value)
            DELETE lf
        }
    """

    _, summary = run_cypher_query(db_driver, query)
    counters = summary.counters
    print_counters_table(counters)
    return counters.contains_updates


if __name__ == "__main__":
    main()

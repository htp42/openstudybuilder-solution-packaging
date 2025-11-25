"""PRD Data Corrections: Activity Versioning Gap Fix"""

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


if __name__ == "__main__":
    main()

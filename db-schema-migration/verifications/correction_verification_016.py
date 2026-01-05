"""
This modules verifies that database nodes/relations and API endpoints look and behave as expected.

It utilizes tests written for verifying a specific migration,
without inserting any test data and without running any migration script on the target database.
"""

import os

from data_corrections.utils.utils import get_db_driver, run_cypher_query
from migrations.utils.utils import get_logger

LOGGER = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()


def test_activity_000317_versioning_gap():
    """
    Bug #3221548: Check for Activity_000317 versioning gap issue.
    Verify that there is no chronological gap between version 7.0 and version 7.1
    of Activity_000317 in the HAS_VERSION relationships.
    """
    # Query to check for versioning gap in Activity_000317
    query = """
        MATCH (ar:ActivityRoot {uid: "Activity_000317"})
        MATCH (ar)-[hv1:HAS_VERSION {version: "7.0"}]->(av1:ActivityValue)
        MATCH (ar)-[hv2:HAS_VERSION {version: "7.1"}]->(av2:ActivityValue)
        // Check if there's a gap between version 7.0 end and version 7.1 start
        WITH hv1.end_date AS v7_0_end_date, hv2.start_date AS v7_1_start_date,
             duration.between(hv1.end_date, hv2.start_date).days AS gap_days
        WHERE hv1.end_date IS NOT NULL AND hv2.start_date IS NOT NULL
        RETURN
            v7_0_end_date,
            v7_1_start_date,
            gap_days,
            CASE
                WHEN gap_days > 0 THEN true
                ELSE false
            END AS has_gap
    """
    res, _ = run_cypher_query(DB_DRIVER, query)

    if len(res) > 0 and res[0][3]:  # has_gap is true
        assert False, (
            f"Activity_000317 has a {res[0][2]}-day versioning gap between "
            f"version 7.0 (end: {res[0][0]}) and version 7.1 (start: {res[0][1]}). "
            f"Expected continuous versioning with no gaps."
        )


def test_remove_cat_submission_value_suffix():
    """
    Verify that no CTCodelistTerm nodes in the EVNTCAT, EVNTSCAT, FINDCAT,
    FINDSCAT, INTVCAT and INTVSCAT codelists have submission_value suffixes
    "nnnn_CAT" or "nnnn_SUB_CAT".
    """
    query = """
        MATCH (clr:CTCodelistRoot)-[har:HAS_ATTRIBUTES_ROOT]-(clar:CTCodelistAttributesRoot)-[clalat:LATEST]-(clav:CTCodelistAttributesValue)
        WHERE clav.submission_value IN ['EVNTCAT', 'EVNTSCAT', 'FINDCAT', 'FINDSCAT', 'INTVCAT', 'INTVSCAT']
        WITH clr
        MATCH (clr)-[ht:HAS_TERM]->(clt:CTCodelistTerm)
        WHERE clt.submission_value ENDS WITH "_CAT" OR clt.submission_value ENDS WITH " "
        RETURN clt
    """
    res, _ = run_cypher_query(DB_DRIVER, query)

    assert (
        len(res) == 0
    ), f"Found {len(res)} CTCodelistTerm nodes with unwanted submission value suffixes"


def test_missing_retired_relationships():
    """
    Verify that all HAS_VERSION relationships with status Retired
    have a corresoinsding HAS_VERSION relationship with status Final or Draft.
    """
    query = """
        MATCH (root)-[ret:HAS_VERSION {status: "Retired"}]->(value)
        WHERE NOT (root)-[:HAS_VERSION {status: "Final"}]->(value) AND NOT (root)-[:HAS_VERSION {status: "Draft"}]->(value)
        RETURN root
    """
    res, _ = run_cypher_query(DB_DRIVER, query)

    assert (
        len(res) == 0
    ), f"Found {len(res)} retired HAS_VERSION relationships without corresponding Final or Draft relationships"

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
import csv
import time
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.services.studies.study import StudyService
from clinical_mdr_api.services.studies.study_flowchart import StudyFlowchartService
from clinical_mdr_api.tests.integration.utils.api import inject_base_data
from clinical_mdr_api.tests.integration.utils.factory_visit import (
    create_study_visit_codelists,
    generate_default_input_data_for_visit,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_study_epoch,
    input_metadata_in_study,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from consumer_api.consumer_api import app
from consumer_api.tests.utils import assert_response_status_code, set_db
from consumer_api.v1 import models

BASE_URL = "/v1"


# Global variables shared between fixtures and tests
rand: str
studies: list[models.Study]
total_studies: int = 25
study_visits: list[models.StudyVisit]
study_activities: list[models.StudyActivity]
study_activity_instances: list[models.StudyActivityInstance]

total_study_visits_version_1: int = 25
total_study_visits_version_latest: int = 26
total_study_activities_version_1: int = 25
total_study_activities_version_latest: int = 26
total_study_detailed_soa_version_1: int = 25
total_study_detailed_soa_version_latest: int = 26
total_study_operational_soa_version_1: int = 25
total_study_operational_soa_version_latest: int = 26

study_detailed_soas_version_1: list[dict[Any, Any]]
study_detailed_soas_version_latest: list[dict[Any, Any]]
study_operational_soas_version_1: list[dict[Any, Any]]
study_operational_soas_version_latest: list[dict[Any, Any]]


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data(api_client):
    """Initialize test data"""
    db_name = "consumer-api-v1-studies-audit-trail"
    set_db(db_name)
    study, _test_data_dict = inject_base_data()
    create_study_visit_codelists(create_unit_definitions=False, use_test_utils=True)
    global rand
    global studies
    global study_visits
    global study_activities
    global study_detailed_soas_version_1
    global study_operational_soas_version_1
    global study_detailed_soas_version_latest
    global study_operational_soas_version_latest

    activity_instance_class = TestUtils.create_activity_instance_class(
        name="Randomized activity instance class"
    )

    studies = [study]  # type: ignore[list-item]
    for _idx in range(1, total_studies):
        rand = TestUtils.random_str(4)
        studies.append(TestUtils.create_study(acronym=f"ACR-{rand}"))  # type: ignore[arg-type]

    study_epoch = create_study_epoch("EpochSubType_0001", study_uid=studies[0].uid)

    visit_to_create = generate_default_input_data_for_visit().copy()
    study_visits = []
    for _idx in range(0, total_study_visits_version_1):
        visit_to_create.update({"time_value": _idx})
        study_visits.append(
            TestUtils.create_study_visit(  # type: ignore[arg-type]
                study_uid=studies[0].uid,
                study_epoch_uid=study_epoch.uid,
                **visit_to_create,
            )
        )

    codelist = TestUtils.create_ct_codelist(
        name="Flowchart Group",
        submission_value="FLWCRTGRP",
        sponsor_preferred_name="Flowchart Group",
        nci_preferred_name="Flowchart Group",
        extensible=True,
        approve=True,
    )
    soa_group_term = TestUtils.create_ct_term(
        sponsor_preferred_name="EFFICACY",
        submission_value="EFFICACY",
        codelist_uid=codelist.codelist_uid,
    )

    yesno_codelist = TestUtils.create_ct_codelist(
        codelist_uid="C66742",
        name="No Yes Response",
        submission_value="NY",
        sponsor_preferred_name="No Yes Response",
        nci_preferred_name="No Yes Response",
        extensible=True,
        approve=True,
    )
    _yes_term = TestUtils.create_ct_term(
        sponsor_preferred_name="Yes",
        submission_value="Y",
        codelist_uid=yesno_codelist.codelist_uid,
        term_uid="C49488",
    )
    _no_term = TestUtils.create_ct_term(
        sponsor_preferred_name="No",
        submission_value="N",
        codelist_uid=yesno_codelist.codelist_uid,
        term_uid="C49487",
    )

    activity_group_uid = TestUtils.create_activity_group("Activity Group").uid
    activity_subgroup_uid = TestUtils.create_activity_subgroup(
        "Activity Sub Group", activity_groups=[activity_group_uid]
    ).uid

    study_activities = []

    for idx in range(0, total_study_activities_version_1):
        _add_study_activity(
            study_uid=studies[0].uid,
            idx=idx,
            activity_group_uid=activity_group_uid,
            activity_subgroup_uid=activity_subgroup_uid,
            soa_group_term_uid=soa_group_term.term_uid,
            activity_instance_class_uid=activity_instance_class.uid,
        )

    for idx in range(0, total_study_operational_soa_version_1):
        TestUtils.create_study_activity_schedule(
            study_uid=studies[0].uid,
            study_visit_uid=study_visits[idx].uid,
            study_activity_uid=study_activities[idx].study_activity_uid,
        )

    study_flowchart_service = StudyFlowchartService()
    study_detailed_soas_version_1 = (
        study_flowchart_service.download_detailed_soa_content(studies[0].uid)
    )

    study_operational_soas_version_1 = (
        study_flowchart_service.download_operational_soa_content(studies[0].uid)
    )

    TestUtils.create_library(name="UCUM", is_editable=True)
    codelist = TestUtils.create_ct_codelist()
    TestUtils.create_study_ct_data_map(codelist_uid=codelist.codelist_uid)
    # Inject study metadata
    input_metadata_in_study(studies[0].uid)
    # lock study
    study_service = StudyService()
    study_service.lock(uid=studies[0].uid, change_description="locking it")
    study_service.unlock(uid=studies[0].uid)

    # Add one more visit and activity to the latest draft version of the study
    visit_to_create.update({"time_value": total_study_visits_version_1})
    study_visits.append(
        TestUtils.create_study_visit(  # type: ignore[arg-type]
            study_uid=studies[0].uid,
            study_epoch_uid=study_epoch.uid,
            **visit_to_create,
        )
    )

    _add_study_activity(
        study_uid=studies[0].uid,
        idx=total_study_activities_version_1,
        activity_group_uid=activity_group_uid,
        activity_subgroup_uid=activity_subgroup_uid,
        soa_group_term_uid=soa_group_term.term_uid,
        activity_instance_class_uid=activity_instance_class.uid,
    )

    TestUtils.create_study_activity_schedule(
        study_uid=studies[0].uid,
        study_visit_uid=study_visits[len(study_visits) - 1].uid,
        study_activity_uid=study_activities[
            len(study_activities) - 1
        ].study_activity_uid,
    )

    study_detailed_soas_version_latest = (
        study_flowchart_service.download_detailed_soa_content(studies[0].uid)
    )
    study_operational_soas_version_latest = (
        study_flowchart_service.download_operational_soa_content(studies[0].uid)
    )


STUDY_AUDIT_TRAIL_FIELDS = [
    "ts",
    "study_uid",
    "study_id",
    "action",
    "entity_uid",
    "entity_type",
    "changed_properties",
    "author",
]

STUDY_AUDIT_TRAIL_FIELDS_NOT_NULL = [
    "ts",
    "study_uid",
    "study_id",
    "action",
    "entity_type",
    "changed_properties",
]


def test_get_study_audit_trail(api_client):
    from_ts = datetime.fromtimestamp(time.time() - 86400).isoformat()  # 24 hours ago
    to_ts = datetime.fromtimestamp(time.time() + 86400).isoformat()  # 24 hours from now

    response = api_client.get(
        f"{BASE_URL}/studies/audit-trail", params={"from_ts": from_ts, "to_ts": to_ts}
    )
    assert_response_status_code(response, 200)

    csv_content = response.content.decode("utf-8")
    csv_reader = csv.DictReader(csv_content.splitlines())
    rows = list(csv_reader)
    assert len(rows) > 0

    for row in rows:
        TestUtils.assert_response_shape_ok(
            row,
            STUDY_AUDIT_TRAIL_FIELDS,
            STUDY_AUDIT_TRAIL_FIELDS_NOT_NULL,
        )

        assert from_ts <= row["ts"] < to_ts
        assert row["action"] in ["Create", "Edit", "Delete"]

        # Verify that author field is present and is a valid MD5 hash (32 hex characters)
        assert "author" in row
        if row["author"]:
            assert (
                len(row["author"]) == 32
            ), f"Author hash should be 32 characters (MD5), got {len(row['author'])}"
            assert all(
                char in "0123456789abcdef" for char in row["author"]
            ), "Author hash should be valid hexadecimal"


def _add_study_activity(
    study_uid: str,
    idx: int,
    activity_group_uid: str,
    activity_subgroup_uid: str,
    soa_group_term_uid: str,
    activity_instance_class_uid: str | None,
) -> models.StudyActivity:
    activity = TestUtils.create_activity(
        f"Activity {str(idx + 1).zfill(2)}",
        activity_groups=[activity_group_uid],
        activity_subgroups=[activity_subgroup_uid],
    )

    activity_instance = TestUtils.create_activity_instance(
        name=f"Activity instance {idx}",
        activity_instance_class_uid=activity_instance_class_uid,  # type: ignore[arg-type]
        name_sentence_case=f"activity instance {idx}",
        topic_code=f"randomized activity instance topic code {idx}",
        adam_param_code=f"randomized adam_param_code {idx}",
        is_required_for_activity=True,
        activities=[activity.uid],
        activity_subgroups=[activity_subgroup_uid],
        activity_groups=[activity_group_uid],
        activity_items=[],
    )

    study_activity = TestUtils.create_study_activity(
        study_uid=study_uid,
        soa_group_term_uid=soa_group_term_uid,
        activity_uid=activity.uid,
        activity_group_uid=activity_group_uid,
        activity_subgroup_uid=activity_subgroup_uid,
        activity_instance_uid=activity_instance.uid,
    )

    study_activities.append(study_activity)  # type: ignore[arg-type]

    return study_activity

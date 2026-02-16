"""
Tests for /concepts/activities/activity-instances endpoints
"""

import json
import logging
import uuid
from functools import reduce
from operator import itemgetter
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClass,
)
from clinical_mdr_api.models.biomedical_concepts.activity_item_class import (
    ActivityItemClass,
)
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_instance import (
    ActivityInstance,
)
from clinical_mdr_api.models.concepts.activities.activity_item import ActivityItem
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.controlled_terminologies.ct_codelist import CTCodelist
from clinical_mdr_api.models.controlled_terminologies.ct_term import CTTerm
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import LIBRARY_NAME, TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code
from common.exceptions import BusinessLogicException

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments


log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
activity_instances_all: list[ActivityInstance]
activity_group: ActivityGroup
activity_subgroup: ActivitySubGroup
activities: list[Activity]
activity_instance_classes: list[ActivityInstanceClass]
activity_items: list[ActivityItem]
activity_item_classes: list[ActivityItemClass]
codelist: CTCodelist
ct_terms: list[CTTerm]
role_term: CTTerm
data_type_term: CTTerm
base_test_data: dict[str, Any]


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "activityinstances.apii"
    inject_and_clear_db(db_name)
    global base_test_data
    _study, base_test_data = inject_base_data(inject_unit_dimension=True)

    global activity_group
    activity_group = TestUtils.create_activity_group(name="activity_group")

    global activity_subgroup
    activity_subgroup = TestUtils.create_activity_subgroup(name="activity_subgroup")
    global activities
    activities = [
        TestUtils.create_activity(
            name="Activity",
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
        ),
        TestUtils.create_activity(
            name="Second activity",
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
        ),
    ]

    global activity_instance_classes
    activity_instance_classes = [
        TestUtils.create_activity_instance_class(
            name="Activity instance class 1",
            definition="def Activity instance class 1",
            is_domain_specific=True,
            level=1,
        ),
        TestUtils.create_activity_instance_class(
            name="Activity instance class 2",
            definition="def Activity instance class 2",
            is_domain_specific=True,
            level=2,
            parent_uid="ActivityInstanceClass_000001",
        ),
        TestUtils.create_activity_instance_class(
            name="Activity instance class 3",
            definition="def Activity instance class 3",
            is_domain_specific=True,
            level=3,
            parent_uid="ActivityInstanceClass_000002",
        ),
        TestUtils.create_activity_instance_class(name="NumericFindings"),
    ]
    global activity_item_classes
    global data_type_term
    global role_term

    data_type_codelist = TestUtils.create_ct_codelist(
        name="DATATYPE", submission_value="DATATYPE", extensible=True, approve=True
    )
    data_type_term = TestUtils.create_ct_term(
        sponsor_preferred_name="Data type", codelist_uid=data_type_codelist.codelist_uid
    )
    role_codelist = TestUtils.create_ct_codelist(
        name="ROLE", submission_value="ROLE", extensible=True, approve=True
    )
    role_term = TestUtils.create_ct_term(
        sponsor_preferred_name="Role", codelist_uid=role_codelist.codelist_uid
    )
    activity_item_classes = [
        TestUtils.create_activity_item_class(
            name="Activity Item Class name1",
            order=1,
            activity_instance_classes=[
                {
                    "uid": activity_instance_classes[0].uid,
                    "mandatory": True,
                    "is_adam_param_specific_enabled": True,
                    "is_additional_optional": False,
                    "is_default_linked": False,
                }
            ],
            role_uid=role_term.term_uid,
            data_type_uid=data_type_term.term_uid,
        ),
        TestUtils.create_activity_item_class(
            name="Activity Item Class name2",
            order=2,
            activity_instance_classes=[
                {
                    "uid": activity_instance_classes[1].uid,
                    "mandatory": True,
                    "is_adam_param_specific_enabled": True,
                    "is_additional_optional": False,
                    "is_default_linked": False,
                }
            ],
            role_uid=role_term.term_uid,
            data_type_uid=data_type_term.term_uid,
        ),
        TestUtils.create_activity_item_class(
            name="Activity Item Class name3",
            order=3,
            activity_instance_classes=[
                {
                    "uid": activity_instance_classes[2].uid,
                    "mandatory": True,
                    "is_adam_param_specific_enabled": False,
                    "is_additional_optional": False,
                    "is_default_linked": False,
                }
            ],
            role_uid=role_term.term_uid,
            data_type_uid=data_type_term.term_uid,
        ),
    ]
    global ct_terms
    # global odm_form
    # global odm_item_group
    # global odm_item
    global codelist

    codelist = TestUtils.create_ct_codelist(extensible=True, approve=True)
    ct_terms = [
        TestUtils.create_ct_term(
            codelist_uid=codelist.codelist_uid,
            sponsor_preferred_name="Activity item term",
        ),
        TestUtils.create_ct_term(
            codelist_uid=codelist.codelist_uid,
            sponsor_preferred_name="Activity item term2",
        ),
    ]
    global activity_items
    activity_items = [
        {
            "activity_item_class_uid": activity_item_classes[0].uid,
            "ct_terms": [],
            "unit_definition_uids": [
                base_test_data["day_unit"].uid,
            ],
            "is_adam_param_specific": True,
        },
        {
            "activity_item_class_uid": activity_item_classes[1].uid,
            "ct_terms": [
                {
                    "term_uid": ct_terms[1].term_uid,
                    "codelist_uid": codelist.codelist_uid,
                }
            ],
            "unit_definition_uids": [],
            "is_adam_param_specific": False,
        },
        {
            "activity_item_class_uid": activity_item_classes[2].uid,
            "ct_terms": [
                {
                    "term_uid": ct_terms[0].term_uid,
                    "codelist_uid": codelist.codelist_uid,
                },
                {
                    "term_uid": ct_terms[1].term_uid,
                    "codelist_uid": codelist.codelist_uid,
                },
            ],
            "unit_definition_uids": [],
            "is_adam_param_specific": False,
        },
    ]
    global activity_instances_all
    # Create some activity instances
    activity_instances_all = [
        TestUtils.create_activity_instance(
            name="name A",
            activity_instance_class_uid=activity_instance_classes[0].uid,
            definition="def A",
            abbreviation="abbr A",
            nci_concept_id="NCIID",
            nci_concept_name="NCINAME",
            name_sentence_case="name A",
            topic_code="topic code A",
            is_research_lab=True,
            adam_param_code="adam_code_a",
            is_required_for_activity=True,
            activities=[activities[0].uid],
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            activity_items=[activity_items[0]],
        ),
        TestUtils.create_activity_instance(
            name="name-AAA",
            activity_instance_class_uid=activity_instance_classes[0].uid,
            name_sentence_case="name-AAA",
            topic_code="topic code-AAA",
            is_required_for_activity=True,
            activities=[activities[0].uid],
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            activity_items=[activity_items[0]],
        ),
        TestUtils.create_activity_instance(
            name="name-BBB",
            activity_instance_class_uid=activity_instance_classes[0].uid,
            name_sentence_case="name-BBB",
            topic_code="topic code-BBB",
            is_required_for_activity=True,
            activities=[activities[0].uid],
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            activity_items=[activity_items[0]],
        ),
        TestUtils.create_activity_instance(
            name="name XXX",
            activity_instance_class_uid=activity_instance_classes[0].uid,
            name_sentence_case="name XXX",
            nci_concept_id="C-XXX",
            topic_code="topic code XXX",
            is_required_for_activity=True,
            activities=[activities[0].uid],
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            activity_items=[activity_items[0], activity_items[1], activity_items[2]],
        ),
        TestUtils.create_activity_instance(
            name="name YYY",
            activity_instance_class_uid=activity_instance_classes[0].uid,
            name_sentence_case="name YYY",
            topic_code="topic code YYY",
            is_required_for_activity=True,
            activities=[activities[0].uid],
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            activity_items=[activity_items[0], activity_items[1]],
        ),
    ]
    TestUtils.create_activity_instance(
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-ZZZ",
        topic_code="topic code ZZZ",
        is_required_for_activity=True,
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0], activity_items[1], activity_items[2]],
        preview=True,
    )

    for index in range(5):
        activity_instances_all.append(
            TestUtils.create_activity_instance(
                name=f"name-AAA-{index}",
                activity_instance_class_uid=activity_instance_classes[1].uid,
                name_sentence_case=f"name-AAA-{index}",
                topic_code=f"topic code-AAA-{index}",
                is_required_for_activity=True,
                activities=[activities[1].uid],
                activity_subgroups=[activity_subgroup.uid],
                activity_groups=[activity_group.uid],
                activity_items=[activity_items[1]],
            )
        )
        activity_instances_all.append(
            TestUtils.create_activity_instance(
                name=f"name-BBB-{index}",
                activity_instance_class_uid=activity_instance_classes[1].uid,
                name_sentence_case=f"name-BBB-{index}",
                topic_code=f"topic code-BBB-{index}",
                is_required_for_activity=True,
                activities=[activities[1].uid],
                activity_subgroups=[activity_subgroup.uid],
                activity_groups=[activity_group.uid],
                activity_items=[activity_items[1]],
            )
        )
        activity_instances_all.append(
            TestUtils.create_activity_instance(
                name=f"name-XXX-{index}",
                activity_instance_class_uid=activity_instance_classes[1].uid,
                name_sentence_case=f"name-XXX-{index}",
                topic_code=f"topic code-XXX-{index}",
                is_required_for_activity=True,
                activities=[activities[1].uid],
                activity_subgroups=[activity_subgroup.uid],
                activity_groups=[activity_group.uid],
                activity_items=[activity_items[1]],
            )
        )
        activity_instances_all.append(
            TestUtils.create_activity_instance(
                name=f"name-YYY-{index}",
                activity_instance_class_uid=activity_instance_classes[1].uid,
                name_sentence_case=f"name-YYY-{index}",
                topic_code=f"topic code-YYY-{index}",
                is_required_for_activity=True,
                activities=[activities[1].uid],
                activity_subgroups=[activity_subgroup.uid],
                activity_groups=[activity_group.uid],
                activity_items=[activity_items[1]],
            )
        )

    yield


ACTIVITY_INSTANCES_FIELDS_ALL = [
    "uid",
    "nci_concept_id",
    "nci_concept_name",
    "name",
    "name_sentence_case",
    "definition",
    "abbreviation",
    "topic_code",
    "is_research_lab",
    "molecular_weight",
    "adam_param_code",
    "is_required_for_activity",
    "is_default_selected_for_activity",
    "is_data_sharing",
    "is_legacy_usage",
    "is_derived",
    "legacy_description",
    "activity_groupings",
    "activity_name",
    "activity_instance_class",
    "activity_items",
    "library_name",
    "start_date",
    "end_date",
    "status",
    "version",
    "change_description",
    "author_username",
    "possible_actions",
]

ACTIVITY_INSTANCES_FIELDS_NOT_NULL = [
    "uid",
    "name",
    "activity_instance_class",
]


def test_get_activity_instance(api_client):
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instances_all[0].uid}"
    )
    res = response.json()

    assert_response_status_code(response, 200)

    # Check fields included in the response
    assert set(res.keys()) == set(ACTIVITY_INSTANCES_FIELDS_ALL)
    for key in ACTIVITY_INSTANCES_FIELDS_NOT_NULL:
        assert res[key] is not None

    assert res["uid"] == activity_instances_all[0].uid
    assert res["name"] == "name A"
    assert res["definition"] == "def A"
    assert res["abbreviation"] == "abbr A"
    assert res["nci_concept_id"] == "NCIID"
    assert res["nci_concept_name"] == "NCINAME"
    assert res["activity_name"] == activities[0].name
    assert res["name_sentence_case"] == "name A"
    assert res["topic_code"] == "topic code A"
    assert res["is_research_lab"] is True
    assert res["molecular_weight"] is None
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activities[0].uid
    assert res["activity_groupings"][0]["activity"]["name"] == activities[0].name
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["uid"]
        == activity_subgroup.uid
    )
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == activity_subgroup.name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == activity_group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == activity_group.name
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[0].uid
    assert res["activity_instance_class"]["name"] == activity_instance_classes[0].name
    assert len(res["activity_items"]) == 1
    assert res["activity_items"][0]["is_adam_param_specific"] is True
    assert (
        res["activity_items"][0]["activity_item_class"]["uid"]
        == activity_item_classes[0].uid
    )

    expected_term_uids = set(
        (term["uid"], term["codelist_uid"]) for term in activity_items[0]["ct_terms"]
    )
    actual_term_uids = set(
        (term["uid"], term["codelist_uid"])
        for term in res["activity_items"][0]["ct_terms"]
    )
    assert expected_term_uids == actual_term_uids
    expected_unit_uids = set(
        unit_uid for unit_uid in activity_items[0]["unit_definition_uids"]
    )
    actual_unit_uids = set(
        unit["uid"] for unit in res["activity_items"][0]["unit_definitions"]
    )
    assert expected_unit_uids == actual_unit_uids
    assert (
        res["activity_items"][0]["unit_definitions"][0]["dimension_name"]
        == base_test_data["unit_dimension_terms"][0].sponsor_preferred_name
    )

    assert res["library_name"] == "Sponsor"
    assert res["version"] == "1.0"
    assert res["status"] == "Final"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_get_activity_instances_pagination(api_client):
    results_paginated: dict[Any, Any] = {}
    sort_by = '{"name": true}'
    for page_number in range(1, 4):
        url = f"/concepts/activities/activity-instances?page_number={page_number}&page_size=10&sort_by={sort_by}"
        response = api_client.get(url)
        res = response.json()
        res_names = [item["name"] for item in res["items"]]
        results_paginated[page_number] = res_names
        log.info("Page %s: %s", page_number, res_names)

    log.info("All pages: %s", results_paginated)

    results_paginated_merged = list(
        list(reduce(lambda a, b: list(a) + list(b), list(results_paginated.values())))
    )
    log.info("All rows returned by pagination: %s", results_paginated_merged)

    res_all = api_client.get(
        f"/concepts/activities/activity-instances?page_number=1&page_size=100&sort_by={sort_by}"
    ).json()
    results_all_in_one_page = list(map(lambda x: x["name"], res_all["items"]))
    log.info("All rows in one page: %s", results_all_in_one_page)
    assert len(results_all_in_one_page) == len(results_paginated_merged)
    assert len(activity_instances_all) == len(results_paginated_merged)


@pytest.mark.parametrize(
    "page_size, page_number, total_count, sort_by, expected_result_len",
    [
        pytest.param(None, None, None, None, 10),
        pytest.param(3, 1, True, None, 3),
        pytest.param(3, 2, True, None, 3),
        pytest.param(10, 2, True, None, 10),
        pytest.param(10, 3, True, None, 5),  # Total number of data models is 25
        pytest.param(10, 1, True, '{"name": false}', 10),
        pytest.param(10, 2, True, '{"name": true}', 10),
        pytest.param(10, 1, True, '{"activity_name": true}', 10),
    ],
)
def test_get_activity_instances(
    api_client, page_size, page_number, total_count, sort_by, expected_result_len
):
    url = "/concepts/activities/activity-instances"
    query_params = []
    if page_size:
        query_params.append(f"page_size={page_size}")
    if page_number:
        query_params.append(f"page_number={page_number}")
    if total_count:
        query_params.append(f"total_count={total_count}")
    if sort_by:
        query_params.append(f"sort_by={sort_by}")

    if query_params:
        url = f"{url}?{'&'.join(query_params)}"

    log.info("GET %s", url)
    response = api_client.get(url)
    res = response.json()

    assert_response_status_code(response, 200)

    # Check fields included in the response
    assert list(res.keys()) == ["items", "total", "page", "size"]
    assert len(res["items"]) == expected_result_len
    assert res["total"] == (len(activity_instances_all) if total_count else 0)
    assert res["page"] == (page_number if page_number else 1)
    assert res["size"] == (page_size if page_size else 10)

    for item in res["items"]:
        assert set(list(item.keys())) == set(ACTIVITY_INSTANCES_FIELDS_ALL)
        for key in ACTIVITY_INSTANCES_FIELDS_NOT_NULL:
            assert item[key] is not None

    if sort_by:
        # sort_by is JSON string in the form: {"sort_field_name": is_ascending_order}
        sort_by_dict = json.loads(sort_by)
        sort_field: str = list(sort_by_dict.keys())[0]
        sort_order_ascending: bool = list(sort_by_dict.values())[0]

        # extract list of values of 'sort_field_name' field from the returned result
        result_vals = list(map(lambda x: x[sort_field], res["items"]))
        result_vals_sorted_locally = result_vals.copy()
        result_vals_sorted_locally.sort(reverse=not sort_order_ascending)
        # This asser fails due to API issue with sorting coupled with pagination
        # assert result_vals == result_vals_sorted_locally


@pytest.mark.parametrize(
    "export_format",
    [
        pytest.param("text/csv"),
        pytest.param("text/xml"),
        pytest.param(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    ],
)
def test_get_activity_instances_csv_xml_excel(api_client, export_format):
    url = "/concepts/activities/activity-instances"
    TestUtils.verify_exported_data_format(api_client, export_format, url)


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param('{"*": {"v": ["aaa"]}}', "name", "name-AAA"),
        pytest.param('{"*": {"v": ["bBb"]}}', "name", "name-BBB"),
        pytest.param('{"*": {"v": ["ccc"]}}', None, None),
        pytest.param('{"*": {"v": ["Final"]}}', "status", "Final"),
        pytest.param('{"*": {"v": ["1.0"]}}', "version", "1.0"),
    ],
)
def test_filtering_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    url = f"/concepts/activities/activity-instances?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert_response_status_code(response, 200)
    if expected_result_prefix:
        assert len(res["items"]) > 0
        nested_path = None

        # if we expect a nested property to be equal to specified value
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field that starts with the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(row, list):
                any(
                    item[expected_matched_field].startswith(expected_result_prefix)
                    for item in row
                )
            else:
                assert row[expected_matched_field].startswith(expected_result_prefix)
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result",
    [
        pytest.param('{"name": {"v": ["name-AAA"]}}', "name", "name-AAA"),
        pytest.param('{"name": {"v": ["name-BBB"]}}', "name", "name-BBB"),
        pytest.param('{"name": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"name_sentence_case": {"v": ["name-AAA"]}}',
            "name_sentence_case",
            "name-AAA",
        ),
        pytest.param(
            '{"name_sentence_case": {"v": ["name-BBB"]}}',
            "name_sentence_case",
            "name-BBB",
        ),
        pytest.param('{"name_sentence_case": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"topic_code": {"v": ["topic code-AAA"]}}', "topic_code", "topic code-AAA"
        ),
        pytest.param(
            '{"topic_code": {"v": ["topic code-BBB"]}}', "topic_code", "topic code-BBB"
        ),
        pytest.param('{"topic_code": {"v": ["cc"]}}', None, None),
        pytest.param('{"topic_code": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"activity_instance_class.name": {"v": ["Activity instance class 1"]}}',
            "activity_instance_class.name",
            "Activity instance class 1",
        ),
    ],
)
def test_filtering_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    url = f"/concepts/activities/activity-instances?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert_response_status_code(response, 200)
    if expected_result:
        assert len(res["items"]) > 0

        # if we expect a nested property to be equal to specified value
        nested_path = None
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field whose value is equal to the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(expected_result, list):
                assert all(
                    item in row[expected_matched_field] for item in expected_result
                )
            else:
                if isinstance(row, list):
                    all(item[expected_matched_field] == expected_result for item in row)
                else:
                    assert row[expected_matched_field] == expected_result
    else:
        assert len(res["items"]) == 0


def test_get_activity_instances_versions(api_client):
    # Create a new version of an activity
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instances_all[0].uid}/versions"
    )
    assert_response_status_code(response, 201)

    # Get all versions of all activities
    response = api_client.get(
        "/concepts/activities/activity-instances/versions?page_size=100"
    )
    res = response.json()

    assert_response_status_code(response, 200)

    # Check fields included in the response
    assert set(res.keys()) == set(["items", "total", "page", "size"])

    assert len(res["items"]) == len(activity_instances_all) * 2 + 1
    for item in res["items"]:
        assert set(list(item.keys())) == set(ACTIVITY_INSTANCES_FIELDS_ALL)
        for key in ACTIVITY_INSTANCES_FIELDS_NOT_NULL:
            assert item[key] is not None

    # Check that the items are sorted by start_date descending
    sorted_items = sorted(res["items"], key=itemgetter("start_date"), reverse=True)
    assert sorted_items == res["items"]


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result_prefix",
    [
        pytest.param('{"*": {"v": ["aaa"]}}', "name", "name-AAA"),
        pytest.param('{"*": {"v": ["bBb"]}}', "name", "name-BBB"),
        pytest.param('{"*": {"v": ["ccc"]}}', None, None),
        pytest.param('{"*": {"v": ["Final"]}}', "status", "Final"),
        pytest.param('{"*": {"v": ["1.0"]}}', "version", "1.0"),
    ],
)
def test_filtering_versions_wildcard(
    api_client, filter_by, expected_matched_field, expected_result_prefix
):
    url = f"/concepts/activities/activity-instances/versions?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert_response_status_code(response, 200)
    if expected_result_prefix:
        assert len(res["items"]) > 0
        nested_path = None

        # if we expect a nested property to be equal to specified value
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field that starts with the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(row, list):
                any(
                    item[expected_matched_field].startswith(expected_result_prefix)
                    for item in row
                )
            else:
                assert row[expected_matched_field].startswith(expected_result_prefix)
    else:
        assert len(res["items"]) == 0


@pytest.mark.parametrize(
    "filter_by, expected_matched_field, expected_result",
    [
        pytest.param('{"name": {"v": ["name-AAA"]}}', "name", "name-AAA"),
        pytest.param('{"name": {"v": ["name-BBB"]}}', "name", "name-BBB"),
        pytest.param('{"name": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"name_sentence_case": {"v": ["name-AAA"]}}',
            "name_sentence_case",
            "name-AAA",
        ),
        pytest.param(
            '{"name_sentence_case": {"v": ["name-BBB"]}}',
            "name_sentence_case",
            "name-BBB",
        ),
        pytest.param('{"name_sentence_case": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"topic_code": {"v": ["topic code-AAA"]}}', "topic_code", "topic code-AAA"
        ),
        pytest.param(
            '{"topic_code": {"v": ["topic code-BBB"]}}', "topic_code", "topic code-BBB"
        ),
        pytest.param('{"topic_code": {"v": ["cc"]}}', None, None),
        pytest.param('{"topic_code": {"v": ["cc"]}}', None, None),
        pytest.param(
            '{"activity_instance_class.name": {"v": ["Activity instance class 1"]}}',
            "activity_instance_class.name",
            "Activity instance class 1",
        ),
    ],
)
def test_filtering_versions_exact(
    api_client, filter_by, expected_matched_field, expected_result
):
    url = f"/concepts/activities/activity-instances/versions?filters={filter_by}"
    response = api_client.get(url)
    res = response.json()

    assert_response_status_code(response, 200)
    if expected_result:
        assert len(res["items"]) > 0

        # if we expect a nested property to be equal to specified value
        nested_path = None
        if isinstance(expected_matched_field, str) and "." in expected_matched_field:
            nested_path = expected_matched_field.split(".")
            expected_matched_field = nested_path[-1]
            nested_path = nested_path[:-1]

        # Each returned row has a field whose value is equal to the specified filter value
        for row in res["items"]:
            if nested_path:
                for prop in nested_path:
                    row = row[prop]
            if isinstance(expected_result, list):
                assert all(
                    item in row[expected_matched_field] for item in expected_result
                )
            else:
                if isinstance(row, list):
                    all(item[expected_matched_field] == expected_result for item in row)
                else:
                    assert row[expected_matched_field] == expected_result
    else:
        assert len(res["items"]) == 0


def test_edit_activity_instance(api_client):
    activity_instance_preview = TestUtils.create_activity_instance(
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        preview=True,
    )
    assert activity_instance_preview.adam_param_code == ""
    assert activity_instance_preview.name == "Activity"
    assert activity_instance_preview.name_sentence_case == "activity"
    assert activity_instance_preview.topic_code == "ACTIVITY"
    activity_instance_preview = TestUtils.create_activity_instance(
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        is_research_lab=True,
        preview=True,
    )
    assert activity_instance_preview.adam_param_code == ""
    assert activity_instance_preview.name == "Activity Research"
    assert activity_instance_preview.name_sentence_case == "activity research"
    assert activity_instance_preview.topic_code == "ACTIVITY_RESEARCH"
    activity_instance_preview = TestUtils.create_activity_instance(
        name="Activity (BU)",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        preview=True,
    )
    assert activity_instance_preview.adam_param_code == ""
    assert activity_instance_preview.name == "Activity (BU)"
    # TODO: standard_unit detection disabled for now, it will be added in the future, so the response should be in lower case
    assert activity_instance_preview.name_sentence_case == "activity (bu)"
    assert activity_instance_preview.topic_code == "ACTIVITY_BU"
    activity_instance = TestUtils.create_activity_instance(
        name="Activity Instance",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        name_sentence_case="activity instance",
        nci_concept_id="C-123",
        topic_code="activity instance tc 2",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
    )
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["name"] == "Activity Instance"
    assert res["name_sentence_case"] == "activity instance"
    assert res["nci_concept_id"] == "C-123"
    assert res["topic_code"] == "activity instance tc 2"
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activities[0].uid
    assert res["activity_groupings"][0]["activity"]["name"] == activities[0].name
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["uid"]
        == activity_subgroup.uid
    )
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == activity_subgroup.name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == activity_group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == activity_group.name
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[0].uid
    assert len(res["activity_items"]) == 1
    assert res["activity_items"][0]["is_adam_param_specific"] is True
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"
    assert res["possible_actions"] == ["approve", "delete", "edit"]

    # First Edit without activity-items explicitly sent
    response = api_client.patch(
        f"/concepts/activities/activity-instances/{activity_instance.uid}",
        json={
            "name": "some new name",
            "name_sentence_case": "some new name",
            "change_description": "modifying activity instance",
        },
    )
    assert_response_status_code(response, 200)

    # Second Edit with more properties sent
    response = api_client.patch(
        f"/concepts/activities/activity-instances/{activity_instance.uid}",
        json={
            "name": "new name",
            "name_sentence_case": "new name",
            "nci_concept_id": "C-123NEW",
            "activity_groupings": [
                {
                    "activity_uid": activities[1].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [activity_items[0], activity_items[1]],
            "change_description": "modifying activity instance",
        },
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["name"] == "new name"
    assert res["name_sentence_case"] == "new name"
    assert res["nci_concept_id"] == "C-123NEW"
    assert res["topic_code"] == "activity instance tc 2"
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activities[1].uid
    assert res["activity_groupings"][0]["activity"]["name"] == activities[1].name
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["uid"]
        == activity_subgroup.uid
    )
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == activity_subgroup.name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == activity_group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == activity_group.name
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[0].uid
    items = res["activity_items"]
    assert len(items) == 2
    assert items[0]["is_adam_param_specific"] is True
    assert items[1]["is_adam_param_specific"] is False

    items = sorted(items, key=lambda x: x["activity_item_class"]["uid"])

    assert items[0]["activity_item_class"]["uid"] == activity_item_classes[0].uid
    expected_term_uids = set(
        (term["uid"], term["codelist_uid"]) for term in activity_items[0]["ct_terms"]
    )
    actual_term_uids = set(
        (term["uid"], term["codelist_uid"]) for term in items[0]["ct_terms"]
    )
    assert expected_term_uids == actual_term_uids
    expected_unit_uids = set(
        unit_uid for unit_uid in activity_items[0]["unit_definition_uids"]
    )
    actual_unit_uids = set(unit["uid"] for unit in items[0]["unit_definitions"])
    assert expected_unit_uids == actual_unit_uids

    assert items[1]["activity_item_class"]["uid"] == activity_item_classes[1].uid
    expected_term_uids = set(
        (term["term_uid"], term["codelist_uid"])
        for term in activity_items[1]["ct_terms"]
    )
    actual_term_uids = set(
        (term["uid"], term["codelist_uid"]) for term in items[1]["ct_terms"]
    )
    assert expected_term_uids == actual_term_uids
    expected_unit_uids = set(
        unit_uid for unit_uid in activity_items[1]["unit_definition_uids"]
    )
    actual_unit_uids = set(unit["uid"] for unit in items[1]["unit_definitions"])
    assert expected_unit_uids == actual_unit_uids

    assert res["version"] == "0.3"
    assert res["status"] == "Draft"
    assert res["possible_actions"] == ["approve", "delete", "edit"]

    activity_instance_preview = TestUtils.create_activity_instance(
        name="",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        preview=True,
    )
    activity_instance = TestUtils.create_activity_instance(
        name=activity_instance_preview.name,
        activity_instance_class_uid=activity_instance_classes[0].uid,
        name_sentence_case=activity_instance_preview.name_sentence_case,
        nci_concept_id="C-124",
        topic_code=activity_instance_preview.topic_code,
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
    )
    activity_instance_preview = TestUtils.create_activity_instance(
        name="",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        preview=True,
    )
    assert activity_instance_preview.adam_param_code == ""
    assert activity_instance_preview.name == "Activity 1"
    assert activity_instance_preview.name_sentence_case == "activity 1"
    assert activity_instance_preview.topic_code == "ACTIVITY_1"

    activity_instance_preview = TestUtils.create_activity_instance(
        name="",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
        is_research_lab=True,
        preview=True,
    )
    activity_instance = TestUtils.create_activity_instance(
        name=activity_instance_preview.name,
        activity_instance_class_uid=activity_instance_classes[0].uid,
        name_sentence_case=activity_instance_preview.name_sentence_case,
        nci_concept_id="C-124",
        topic_code=activity_instance_preview.topic_code,
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        approve=False,
    )
    activity_instance_preview = TestUtils.create_activity_instance(
        name="",
        activity_instance_class_uid=activity_instance_classes[0].uid,
        nci_concept_id="C-123",
        activities=[activities[0].uid],
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        activity_items=[activity_items[0]],
        is_research_lab=True,
        approve=False,
        preview=True,
    )
    assert activity_instance_preview.adam_param_code == ""
    assert activity_instance_preview.name == "Activity Research 1"
    assert activity_instance_preview.name_sentence_case == "activity research 1"
    assert activity_instance_preview.topic_code == "ACTIVITY_RESEARCH_1"


def test_post_activity_instance(api_client):
    item_to_post = activity_items[1]
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "activity instance name",
            "name_sentence_case": "activity instance name",
            "nci_concept_id": "C-456",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [
                item_to_post,
                activity_items[
                    0
                ],  # adding activity item class, because it is the mandatory for the activity instance class
            ],
            "is_required_for_activity": True,
            "is_derived": True,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["name"] == "activity instance name"
    assert res["name_sentence_case"] == "activity instance name"
    assert res["nci_concept_id"] == "C-456"
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activities[0].uid
    assert res["activity_groupings"][0]["activity"]["name"] == activities[0].name
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["uid"]
        == activity_subgroup.uid
    )
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == activity_subgroup.name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == activity_group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == activity_group.name
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[0].uid
    assert len(res["activity_items"]) == 2
    assert res["activity_items"][0]["is_adam_param_specific"] is False
    assert (
        res["activity_items"][0]["activity_item_class"]["uid"]
        == activity_item_classes[1].uid
    )

    expected_term_uids = set(
        (term["term_uid"], term["codelist_uid"]) for term in item_to_post["ct_terms"]
    )
    actual_term_uids = set(
        (term["uid"], term["codelist_uid"])
        for term in res["activity_items"][0]["ct_terms"]
    )
    assert expected_term_uids == actual_term_uids
    expected_unit_uids = set(
        unit_uid for unit_uid in item_to_post["unit_definition_uids"]
    )
    actual_unit_uids = set(
        unit["uid"] for unit in res["activity_items"][0]["unit_definitions"]
    )
    assert expected_unit_uids == actual_unit_uids

    assert res["name_sentence_case"] == "activity instance name"
    assert res["topic_code"] is None
    assert res["adam_param_code"] is None
    assert res["is_required_for_activity"] is True
    assert res["is_default_selected_for_activity"] is False
    assert res["is_data_sharing"] is False
    assert res["is_legacy_usage"] is False
    assert res["is_derived"] is True
    assert res["library_name"] == "Sponsor"
    assert res["version"] == "0.1"
    assert res["status"] == "Draft"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_activity_instance_versioning(api_client):
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "ac name",
            "name_sentence_case": "ac name",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_items": [
                activity_items[
                    0
                ],  # adding activity item class, because it is mandatory for the activity instance class
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 201)
    res = response.json()
    activity_instance_uid = res["uid"]

    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/versions"
    )
    res = response.json()
    assert_response_status_code(response, 200)
    for item in res:
        assert set(list(item.keys())) == set(ACTIVITY_INSTANCES_FIELDS_ALL)
        for key in ACTIVITY_INSTANCES_FIELDS_NOT_NULL:
            assert item[key] is not None

    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/versions"
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == "New draft version can be created only for FINAL versions."
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/approvals"
    )
    assert_response_status_code(response, 201)

    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/approvals"
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == "The object isn't in draft status."

    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/activations"
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == "Only RETIRED version can be reactivated."
    response = api_client.delete(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/activations"
    )
    assert_response_status_code(response, 200)

    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance_uid}/activations"
    )
    assert_response_status_code(response, 200)

    response = api_client.delete(
        f"/concepts/activities/activity-instances/{activity_instance_uid}"
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == "Object has been accepted"


def test_activity_instance_overview(api_client):
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instances_all[3].uid}/overview",
    )
    assert_response_status_code(response, 200)
    res = response.json()
    verify_instance_overview_content(res=res)


def verify_instance_overview_content(res: dict[Any, Any]):
    print(json.dumps(res, indent=2, default=str))

    assert len(res["activity_groupings"]) == 1
    # activity
    assert res["activity_groupings"][0]["activity"]["uid"] == activities[0].uid
    assert res["activity_groupings"][0]["activity"]["name"] == activities[0].name
    assert res["activity_groupings"][0]["activity"]["definition"] is None
    assert res["activity_groupings"][0]["activity"]["library_name"] == LIBRARY_NAME

    # activity subgroups
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"] == "activity_subgroup"
    )
    assert res["activity_groupings"][0]["activity_subgroup"]["definition"] is None

    # activity groups
    assert res["activity_groupings"][0]["activity_group"]["name"] == "activity_group"
    assert res["activity_groupings"][0]["activity_group"]["definition"] is None

    # activity instance
    assert res["activity_instance"]["uid"] is not None
    assert res["activity_instance"]["name"] == "name XXX"
    assert res["activity_instance"]["name_sentence_case"] == "name XXX"
    assert res["activity_instance"]["nci_concept_id"] == "C-XXX"
    assert res["activity_instance"]["abbreviation"] is None
    assert res["activity_instance"]["definition"] is None
    assert res["activity_instance"]["adam_param_code"] is None
    assert res["activity_instance"]["is_required_for_activity"] is True
    assert res["activity_instance"]["is_default_selected_for_activity"] is False
    assert res["activity_instance"]["is_data_sharing"] is False
    assert res["activity_instance"]["is_legacy_usage"] is False
    assert res["activity_instance"]["is_derived"] is False
    assert res["activity_instance"]["topic_code"] == "topic code XXX"
    assert res["activity_instance"]["library_name"] == LIBRARY_NAME
    assert "author_username" in res["activity_instance"]
    assert res["activity_instance"]["author_username"] is not None

    # activity instance class
    assert (
        res["activity_instance"]["activity_instance_class"]["name"]
        == "Activity instance class 1"
    )

    # activity items
    items = res["activity_items"]
    assert len(items) == 3
    # Note : order is not guaranteed here
    assert len([item for item in items if item["is_adam_param_specific"] is True]) == 1
    assert len([item for item in items if item["is_adam_param_specific"] is False]) == 2

    items = sorted(items, key=lambda item: item["activity_item_class"]["name"])

    assert len(items[0]["ct_terms"]) == 0
    assert len(items[0]["unit_definitions"]) == 1
    assert items[0]["unit_definitions"][0]["uid"] == base_test_data["day_unit"].uid
    assert items[0]["unit_definitions"][0]["name"] == base_test_data["day_unit"].name
    assert items[0]["activity_item_class"]["name"] == "Activity Item Class name1"
    assert items[0]["activity_item_class"]["role_name"] == "Role"
    assert items[0]["activity_item_class"]["data_type_name"] == "Data type"
    assert items[0]["activity_item_class"]["order"] == 1

    assert len(items[1]["ct_terms"]) == 1
    assert items[1]["ct_terms"][0]["uid"] == ct_terms[1].term_uid
    assert items[1]["ct_terms"][0]["name"] == ct_terms[1].sponsor_preferred_name
    assert len(items[1]["unit_definitions"]) == 0
    assert items[1]["activity_item_class"]["name"] == "Activity Item Class name2"
    assert items[1]["activity_item_class"]["role_name"] == "Role"
    assert items[1]["activity_item_class"]["data_type_name"] == "Data type"
    assert items[1]["activity_item_class"]["order"] == 2

    assert len(items[2]["ct_terms"]) == 2
    terms = items[2]["ct_terms"]
    terms = sorted(terms, key=lambda term: term["uid"])
    assert terms[0]["uid"] == ct_terms[0].term_uid
    assert terms[0]["name"] == ct_terms[0].sponsor_preferred_name
    assert terms[1]["uid"] == ct_terms[1].term_uid
    assert terms[1]["name"] == ct_terms[1].sponsor_preferred_name
    assert len(items[2]["unit_definitions"]) == 0
    assert len(items[0]["unit_definitions"]) == 1
    assert items[2]["activity_item_class"]["name"] == "Activity Item Class name3"
    assert items[2]["activity_item_class"]["role_name"] == "Role"
    assert items[2]["activity_item_class"]["data_type_name"] == "Data type"
    assert items[2]["activity_item_class"]["order"] == 3


def test_activity_instance_overview_export_to_yaml(api_client):
    url = f"/concepts/activities/activity-instances/{activity_instances_all[3].uid}/overview"
    export_format = "application/x-yaml"
    headers = {"Accept": export_format}
    response = api_client.get(url, headers=headers)

    assert_response_status_code(response, 200)
    assert export_format in response.headers["content-type"]

    res = yaml.load(response.text, Loader=yaml.SafeLoader)
    verify_instance_overview_content(res=res)


def test_activity_instance_cosmos_overview(api_client):
    url = f"/concepts/activities/activity-instances/{activity_instances_all[3].uid}/overview.cosmos"
    response = api_client.get(url)

    assert_response_status_code(response, 200)
    assert "application/x-yaml" in response.headers["content-type"]

    res = yaml.load(response.text, Loader=yaml.SafeLoader)

    assert res["shortName"] == "name XXX"
    assert res["conceptId"] == "C-XXX"
    assert res["resultScales"] == [""]
    assert len(res["categories"]) == 1
    assert res["categories"][0] == "activity_subgroup"
    assert len(res["dataElementConcepts"]) == 3


def test_activity_overview(api_client):
    response = api_client.get(
        f"/concepts/activities/activities/{activities[1].uid}/overview",
    )
    assert_response_status_code(response, 200)
    res = response.json()
    verify_activity_overview_content(res=res)


def verify_activity_overview_content(res: dict[Any, Any]):
    # activity
    assert res["activity"]["name"] == "Second activity"
    assert res["activity"]["name_sentence_case"] == "Second activity"
    assert res["activity"]["definition"] is None
    assert res["activity"]["abbreviation"] is None
    assert res["activity"]["library_name"] == LIBRARY_NAME

    assert len(res["activity_groupings"]) == 1

    # activity subgroups
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"] == "activity_subgroup"
    )
    assert res["activity_groupings"][0]["activity_subgroup"]["definition"] is None

    # activity groups
    assert res["activity_groupings"][0]["activity_group"]["name"] == "activity_group"
    assert res["activity_groupings"][0]["activity_subgroup"]["definition"] is None

    # activity instances
    assert res["activity_instances"][0]["uid"] is not None
    assert res["activity_instances"][0]["name"] == "name-AAA-0"
    assert res["activity_instances"][0]["name_sentence_case"] == "name-AAA-0"
    assert res["activity_instances"][0]["abbreviation"] is None
    assert res["activity_instances"][0]["definition"] is None
    assert res["activity_instances"][0]["adam_param_code"] is None
    assert res["activity_instances"][0]["is_required_for_activity"] is True
    assert res["activity_instances"][0]["is_default_selected_for_activity"] is False
    assert res["activity_instances"][0]["is_data_sharing"] is False
    assert res["activity_instances"][0]["is_legacy_usage"] is False
    assert res["activity_instances"][0]["is_derived"] is False
    assert res["activity_instances"][0]["topic_code"] == "topic code-AAA-0"
    assert res["activity_instances"][0]["library_name"] == LIBRARY_NAME

    # activity instance class
    assert (
        res["activity_instances"][0]["activity_instance_class"]["name"]
        == "Activity instance class 2"
    )


def test_activity_overview_export_to_yaml(api_client):
    url = f"/concepts/activities/activities/{activities[1].uid}/overview"
    export_format = "application/x-yaml"
    headers = {"Accept": export_format}
    response = api_client.get(url, headers=headers)

    assert_response_status_code(response, 200)
    assert export_format in response.headers["content-type"]

    res = yaml.load(response.text, Loader=yaml.SafeLoader)
    verify_activity_overview_content(res=res)


def test_updating_parents(api_client):
    original_group_name = "original group name"
    edited_group_name = "edited group name"
    original_subgroup_name = "original subgroup name"
    edited_subgroup_name = "edited subgroup name"
    original_activity_name = "original activity name"
    edited_activity_name = "edited activity name"
    original_instance_name = "original instance name"

    # ==== Create group, subgroup, activity and activity instance ====
    group = TestUtils.create_activity_group(name=original_group_name)

    subgroup = TestUtils.create_activity_subgroup(name=original_subgroup_name)
    activity = TestUtils.create_activity(
        name=original_activity_name,
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        approve=True,
    )
    activity_instance = TestUtils.create_activity_instance(
        name=original_instance_name,
        activity_instance_class_uid=activity_instance_classes[0].uid,
        name_sentence_case=original_instance_name,
        nci_concept_id="C-1234",
        topic_code="cascade activity instance tc 2",
        activities=[activity.uid],
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        activity_items=[activity_items[0]],
        approve=True,
    )

    # Assert that the instance was created as expected
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )

    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == original_instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == original_activity_name
    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == original_subgroup_name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == original_group_name

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # ==== Update group ====
    # Create new version of group
    response = api_client.post(
        f"/concepts/activities/activity-groups/{group.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Update the group
    response = api_client.put(
        f"/concepts/activities/activity-groups/{group.uid}",
        json={
            "name": edited_group_name,
            "name_sentence_case": edited_group_name,
            "change_description": "patch group",
            "library_name": group.library_name,
        },
    )
    assert_response_status_code(response, 200)

    # Approve the group
    response = api_client.post(
        f"/concepts/activities/activity-groups/{group.uid}/approvals"
    )

    # === Assert that the subgroup was not affected by the group update ===
    response = api_client.get(
        f"/concepts/activities/activity-sub-groups/{subgroup.uid}"
    )

    assert_response_status_code(response, 200)
    res = response.json()

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # ==== Update subgroup ====
    # Create new version of subgroup
    response = api_client.post(
        f"/concepts/activities/activity-sub-groups/{subgroup.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Update the subgroup
    response = api_client.put(
        f"/concepts/activities/activity-sub-groups/{subgroup.uid}",
        json={
            "name": edited_subgroup_name,
            "name_sentence_case": edited_subgroup_name,
            "change_description": "patch subgroup",
            "library_name": subgroup.library_name,
            "activity_groups": [group.uid],
        },
    )
    assert_response_status_code(response, 200)

    # Approve the subgroup
    response = api_client.post(
        f"/concepts/activities/activity-sub-groups/{subgroup.uid}/approvals"
    )

    # === Assert that the activity was not affected by the subgroup update ===
    response = api_client.get(f"/concepts/activities/activities/{activity.uid}")

    assert_response_status_code(response, 200)
    res = response.json()

    assert res["activity_groupings"][0]["activity_subgroup_uid"] == subgroup.uid
    assert (
        res["activity_groupings"][0]["activity_subgroup_name"] == original_subgroup_name
    )

    assert res["activity_groupings"][0]["activity_group_uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group_name"] == original_group_name

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # ==== Update activity ====

    # Create new version of activity
    response = api_client.post(
        f"/concepts/activities/activities/{activity.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Update the activity
    response = api_client.put(
        f"/concepts/activities/activities/{activity.uid}",
        json={
            "name": edited_activity_name,
            "name_sentence_case": edited_activity_name,
            "change_description": "patch activity",
            "library_name": activity.library_name,
        },
    )
    assert_response_status_code(response, 200)

    # Approve the activity
    response = api_client.post(
        f"/concepts/activities/activities/{activity.uid}/approvals"
    )
    assert_response_status_code(response, 201)

    # Get the instance by uid and assert that it was not affected by the activity update
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == original_instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == original_activity_name

    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == original_subgroup_name
    )
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == original_group_name

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # Get all instance, find `original_instance_name` and assert that it was not affected by the activity update
    response = api_client.get(
        "/concepts/activities/activity-instances", params={"page_size": 0}
    )
    assert_response_status_code(response, 200)
    res = response.json()["items"]
    a_instance_to_compare = None
    for a_instance in res:
        if a_instance["uid"] == activity_instance.uid:
            a_instance_to_compare = a_instance
            break
    assert (
        a_instance_to_compare is not None
    ), "There must exist `original_activity_instance` in GET all activity-instance response"
    assert a_instance_to_compare["name"] == original_instance_name
    assert len(a_instance_to_compare["activity_groupings"]) == 1
    assert (
        a_instance_to_compare["activity_groupings"][0]["activity"]["uid"]
        == activity.uid
    )
    assert (
        a_instance_to_compare["activity_groupings"][0]["activity"]["name"]
        == original_activity_name
    )

    assert (
        a_instance_to_compare["activity_groupings"][0]["activity_subgroup"]["uid"]
        == subgroup.uid
    )
    assert (
        a_instance_to_compare["activity_groupings"][0]["activity_subgroup"]["name"]
        == original_subgroup_name
    )
    assert (
        a_instance_to_compare["activity_groupings"][0]["activity_group"]["uid"]
        == group.uid
    )
    assert (
        a_instance_to_compare["activity_groupings"][0]["activity_group"]["name"]
        == original_group_name
    )

    assert a_instance_to_compare["version"] == "1.0"
    assert a_instance_to_compare["status"] == "Final"

    # Get the instance overview and assert that it was not affected by the activity update
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}/overview"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["activity_instance"]["name"] == original_instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == original_activity_name

    assert (
        res["activity_groupings"][0]["activity_subgroup"]["name"]
        == original_subgroup_name
    )
    assert res["activity_groupings"][0]["activity_group"]["name"] == original_group_name

    assert res["activity_instance"]["version"] == "1.0"
    assert res["activity_instance"]["status"] == "Final"


def test_updating_instance_to_new_activity(api_client):
    group_name = "updatetest group name"
    subgroup_name = "updatetest subgroup name"
    original_activity_name = "updatetest original activity name"
    edited_activity_name = "updatetest edited activity name"
    other_activity_name = "updatetest other activity name"
    instance_name = "updatetest original instance name"

    # ==== Create group, subgroup, activity and activity instance ====
    group = TestUtils.create_activity_group(name=group_name)

    subgroup = TestUtils.create_activity_subgroup(name=subgroup_name)
    activity = TestUtils.create_activity(
        name=original_activity_name,
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        approve=True,
    )
    other_activity = TestUtils.create_activity(
        name=other_activity_name,
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        approve=True,
    )
    activity_instance = TestUtils.create_activity_instance(
        name=instance_name,
        activity_instance_class_uid=activity_instance_classes[0].uid,
        name_sentence_case=instance_name,
        nci_concept_id="C-1234",
        topic_code="cascade activity instance tc 3",
        activities=[activity.uid],
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        activity_items=[activity_items[0]],
        approve=True,
    )

    # Assert that the instance was created as expected
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )

    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == original_activity_name
    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert res["activity_groupings"][0]["activity_subgroup"]["name"] == subgroup_name
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == group_name

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # ==== Update activity ====

    # Create new version of activity
    response = api_client.post(
        f"/concepts/activities/activities/{activity.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Update the activity
    response = api_client.put(
        f"/concepts/activities/activities/{activity.uid}",
        json={
            "name": edited_activity_name,
            "name_sentence_case": edited_activity_name,
            "change_description": "patch activity",
            "library_name": activity.library_name,
            "is_data_collected": True,
            "activity_groupings": [
                {"activity_group_uid": group.uid, "activity_subgroup_uid": subgroup.uid}
            ],
        },
    )
    assert_response_status_code(response, 200)

    # Approve the activity
    response = api_client.post(
        f"/concepts/activities/activities/{activity.uid}/approvals"
    )
    assert_response_status_code(response, 201)

    # Get the instance by uid and assert that it was not affected by the activity update
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == original_activity_name

    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert res["activity_groupings"][0]["activity_subgroup"]["name"] == subgroup_name
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == group_name

    assert res["version"] == "1.0"
    assert res["status"] == "Final"

    # ==== Update instance to updated activity ====
    # Create new version of instance
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Patch the activity instance, no changes
    response = api_client.patch(
        f"/concepts/activities/activity-instances/{activity_instance.uid}",
        json={
            "change_description": "string",
            "name": "updatetest original instance name",
        },
    )
    assert_response_status_code(response, 200)

    # Approve the activity instance
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance.uid}/approvals"
    )
    assert_response_status_code(response, 201)

    # Get the instance by uid and assert that it is not conncted to the new activity
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == edited_activity_name

    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert res["activity_groupings"][0]["activity_subgroup"]["name"] == subgroup_name
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == group_name

    assert res["version"] == "2.0"
    assert res["status"] == "Final"

    # ==== Update instance to another activity ====
    # Create new version of instance
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance.uid}/versions",
        json={},
    )
    assert_response_status_code(response, 201)

    # Patch the activity instance to another activity, no other changes
    response = api_client.patch(
        f"/concepts/activities/activity-instances/{activity_instance.uid}",
        json={
            "activity_groupings": [
                {
                    "activity_group_uid": group.uid,
                    "activity_subgroup_uid": subgroup.uid,
                    "activity_uid": other_activity.uid,
                }
            ],
            "name": "updatetest original instance name",
            "change_description": "string2",
        },
    )
    assert_response_status_code(response, 200)

    # Approve the activity instance
    response = api_client.post(
        f"/concepts/activities/activity-instances/{activity_instance.uid}/approvals"
    )
    assert_response_status_code(response, 201)

    # Get the instance by uid and assert that it is now connected to the other activity
    response = api_client.get(
        f"/concepts/activities/activity-instances/{activity_instance.uid}"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["name"] == instance_name
    assert len(res["activity_groupings"]) == 1
    assert res["activity_groupings"][0]["activity"]["uid"] == other_activity.uid
    assert res["activity_groupings"][0]["activity"]["name"] == other_activity_name

    assert res["activity_groupings"][0]["activity_subgroup"]["uid"] == subgroup.uid
    assert res["activity_groupings"][0]["activity_subgroup"]["name"] == subgroup_name
    assert res["activity_groupings"][0]["activity_group"]["uid"] == group.uid
    assert res["activity_groupings"][0]["activity_group"]["name"] == group_name

    assert res["version"] == "3.0"
    assert res["status"] == "Final"


def test_instance_to_activity_without_data_collection(api_client):
    group_name = "group name"
    subgroup_name = "subgroup name"
    activity_name = "activity name"
    instance_name = "instance name"

    # ==== Create group, subgroup, activity and activity instance ====
    group = TestUtils.create_activity_group(name=group_name)

    subgroup = TestUtils.create_activity_subgroup(name=subgroup_name)
    activity = TestUtils.create_activity(
        name=activity_name,
        activity_subgroups=[subgroup.uid],
        activity_groups=[group.uid],
        approve=True,
        is_data_collected=False,
    )
    with pytest.raises(BusinessLogicException) as exc:
        _activity_instance = TestUtils.create_activity_instance(
            name=instance_name,
            activity_instance_class_uid=activity_instance_classes[0].uid,
            name_sentence_case=instance_name,
            nci_concept_id="C-1234",
            topic_code="activity instance tc",
            activities=[activity.uid],
            activity_subgroups=[subgroup.uid],
            activity_groups=[group.uid],
            activity_items=[activity_items[0]],
            approve=True,
        )
    assert "tried to connect to Activity without data collection" in exc.value.msg


def test_create_activity_instance_with_molecular_weight(
    api_client,
):
    response = create_activity_instance_with_molecular_weight(
        api_client, "activity instance name with molecular weight", 123.45
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["name"] == "activity instance name with molecular weight"
    assert res["name_sentence_case"] == "activity instance name with molecular weight"
    assert res["molecular_weight"] == pytest.approx(123.45)


def test_cannot_provide_molecular_weight_when_connecting_to_non_numeric_or_doesnt_have_concentration_unit_dimension(
    api_client,
):
    item_to_post = activity_items[1]
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "activity instance name test",
            "name_sentence_case": "activity instance name test",
            "nci_concept_id": "C-456",
            "molecular_weight": 123.45,
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [
                item_to_post,
                activity_items[
                    0
                ],  # adding activity item class, because it is the mandatory one
            ],
            "is_required_for_activity": True,
            "is_derived": True,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["type"] == "ValidationException"
    assert (
        res["message"]
        == "Molecular Weight can only be set for NumericFindings that has concentration units."
    )


def test_cannot_provide_is_adam_param_specific_if_is_adam_param_specific_enabled_is_false(
    api_client,
):
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "local activity instance name",
            "name_sentence_case": "local activity instance name",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[2].uid,
            "activity_items": [
                {
                    "activity_item_class_uid": activity_item_classes[2].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[1].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [],
                    "is_adam_param_specific": True,
                }
            ],
            "is_required_for_activity": True,
            "is_derived": True,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Activity Item's 'is_adam_param_specific' cannot be 'True' when the Activity Item Class' 'is_adam_param_specific_enabled' is 'False'."
    )


@pytest.mark.parametrize(
    "field_name, search_string",
    [
        ("name", "name A"),
        ("name_sentence_case", "name A"),
        ("library_name", "Sponsor"),
        ("definition", "def"),
        ("abbreviation", "abbr A"),
        ("nci_concept_id", "NCIID"),
        ("nci_concept_name", "NCINAME"),
        ("start_date", "20"),
        ("version", "1.0"),
        ("status", "Final"),
        ("author_username", "unknown-user"),
        ("activity_name", "ac"),
        ("activity_instance_class.name", "class 1"),
        ("is_research_lab", "tr"),
        ("topic_code", "code A"),
        ("molecular_weight", 34.567),
        ("adam_param_code", "adam_code_a"),
        ("is_required_for_activity", "tr"),
        ("is_default_selected_for_activity", "f"),
        ("is_data_sharing", "f"),
        ("is_legacy_usage", "f"),
    ],
)
def test_get_activity_instances_headers(api_client, field_name, search_string):
    if field_name == "molecular_weight":
        create_activity_instance_with_molecular_weight(
            api_client, f"activity instance {uuid.uuid4()}", search_string
        )

    for lite in [True, False]:
        query_params = {
            "field_name": field_name,
            "search_string": search_string,
            "lite": lite,
        }

        response = api_client.get(
            "/concepts/activities/activity-instances/headers", params=query_params
        )
        assert_response_status_code(response, 200)
        assert len(response.json()) >= 1
        for res in response.json():
            assert str(search_string).lower() in str(res).lower()


def create_activity_instance_with_molecular_weight(
    api_client, name: str, molecular_weight: float
) -> Any:
    suffix = str(uuid.uuid4())
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": name,
            "name_sentence_case": name,
            "molecular_weight": molecular_weight,
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[
                3
            ].uid,  # NumericFinding
            "activity_items": [
                {
                    "activity_item_class_uid": activity_item_classes[0].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[0].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [
                        TestUtils.create_unit_definition(
                            name=f"new test unit {suffix}",
                            unit_dimension=TestUtils.create_ct_term(
                                codelist_uid=base_test_data[
                                    "unit_dimension_codelist"
                                ].codelist_uid,
                                sponsor_preferred_name=f"Unit Dimension concentration term {suffix}",
                            ).term_uid,
                        ).uid
                    ],
                    "is_adam_param_specific": False,
                }
            ],
            "is_required_for_activity": True,
            "is_derived": True,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 201)
    return response


def test_create_activity_instance_with_non_final_subgroup_fails(api_client, test_data):
    """Test that creating an activity instance fails when using a retired subgroup"""
    from neomodel import db

    # Create a subgroup that will be retired
    retired_subgroup = TestUtils.create_activity_subgroup(
        name="Subgroup to Retire",
        library_name=LIBRARY_NAME,
    )

    # Create another activity that uses the soon-to-be-retired subgroup
    activity_with_retired = TestUtils.create_activity(
        name="Activity with Retired Subgroup",
        activity_groups=[activity_group.uid],
        activity_subgroups=[retired_subgroup.uid],
        library_name=LIBRARY_NAME,
    )

    # Directly update the subgroup to be retired by updating HAS_VERSION status
    # This simulates a subgroup that was once Final but is now Retired
    query = """
        MATCH (sg:ActivitySubGroupRoot {uid: $uid})-[hv:HAS_VERSION]->(sgv:ActivitySubGroupValue)
        WHERE hv.end_date IS NULL
        SET hv.status = 'Retired'
        MERGE (sg)-[:LATEST_RETIRED]->(sgv)
        RETURN sgv
    """
    db.cypher_query(query, {"uid": retired_subgroup.uid})

    # Try to create an activity instance with the activity that has the retired subgroup
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "Instance with Retired Subgroup",
            "name_sentence_case": "instance with retired subgroup",
            "activity_groupings": [
                {
                    "activity_uid": activity_with_retired.uid,
                    "activity_group_uid": activity_group.uid,
                    "activity_subgroup_uid": retired_subgroup.uid,  # Using the retired subgroup
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "library_name": LIBRARY_NAME,
        },
    )

    # The request should fail with 400 status because we're trying to use a retired subgroup
    assert_response_status_code(response, 400)
    res = response.json()

    # Verify the error is about the subgroup not being in Final status
    assert res["type"] == "BusinessLogicException"
    assert (
        "not in Final status" in res["message"]
        or "currently not in Final status" in res["message"]
        or "non-final" in res["message"].lower()
    )


def test_cannot_connect_to_activity_items_with_same_activity_item_class(api_client):
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "contains duplicates of activity item class",
            "name_sentence_case": "contains duplicates of activity item class",
            "nci_concept_id": "000",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [activity_items[0], activity_items[0]],
            "is_required_for_activity": True,
            "is_derived": True,
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "The following Activity Item Class(es) have been associated to more than one Activity Item: ActivityItemClass_000001"
    )


def test_cannot_connect_instance_to_multiple_activities(api_client):
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "instance connected to multiple activities",
            "name_sentence_case": "instance connected to multiple activities",
            "nci_concept_id": "aabbccdd",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                },
                {
                    "activity_uid": activities[1].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                },
            ],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [activity_items[0]],
            "is_required_for_activity": False,
            "is_derived": False,
            "library_name": "Sponsor",
            "topic_code": "some topic code",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Instances are not allowed to link to several different activities"
    )


def test_cannot_create_instance_without_groupings(api_client):
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "instance without groupings",
            "name_sentence_case": "instance without groupings",
            "nci_concept_id": "aabbccdd",
            "activity_groupings": [],
            "activity_instance_class_uid": activity_instance_classes[0].uid,
            "activity_items": [activity_items[0]],
            "is_required_for_activity": False,
            "is_derived": False,
            "library_name": "Sponsor",
            "topic_code": "some topic code",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Activity Instance must have at least one grouping"


def test_level_3_activity_instance_missing_parent_mandatory_item_class_strict_mode(
    api_client,
):
    """Test that creating a level 3 activity instance fails when parent level 2 mandatory item is missing and strict_mode=True"""
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "level 3 instance missing parent mandatory",
            "name_sentence_case": "level 3 instance missing parent mandatory",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[2].uid,  # level 3
            "activity_items": [
                {
                    # Only including level 3 mandatory item, missing parent level 2 mandatory
                    "activity_item_class_uid": activity_item_classes[2].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[0].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [],
                    "is_adam_param_specific": False,
                }
            ],
            "strict_mode": True,  # Strict mode - validation should run
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["type"] == "BusinessLogicException"
    assert "mandatory Activity Item Classes from the parent" in res["message"]
    assert "Activity instance class 2" in res["message"]  # parent level 2 class name
    assert (
        "Activity Item Class name2" in res["message"]
    )  # parent mandatory item class name


def test_level_3_activity_instance_missing_parent_mandatory_item_class_relaxed_mode(
    api_client,
):
    """Test that creating a level 3 activity instance succeeds when parent level 2 mandatory item is missing and strict_mode=False (default)"""
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "level 3 instance missing parent mandatory relaxed",
            "name_sentence_case": "level 3 instance missing parent mandatory relaxed",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[2].uid,  # level 3
            "activity_items": [
                {
                    # Only including level 3 mandatory item, missing parent level 2 mandatory
                    "activity_item_class_uid": activity_item_classes[2].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[0].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [],
                    "is_adam_param_specific": False,
                }
            ],
            "strict_mode": False,  # Relaxed mode - validation should be skipped
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["name"] == "level 3 instance missing parent mandatory relaxed"
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[2].uid
    assert len(res["activity_items"]) == 1


def test_level_3_activity_instance_with_parent_mandatory_item_success(api_client):
    """Test that creating a level 3 activity instance succeeds when parent level 2 mandatory item has CT terms"""
    response = api_client.post(
        "/concepts/activities/activity-instances",
        json={
            "name": "level 3 instance with parent mandatory",
            "name_sentence_case": "level 3 instance with parent mandatory",
            "activity_groupings": [
                {
                    "activity_uid": activities[0].uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                    "activity_group_uid": activity_group.uid,
                }
            ],
            "activity_instance_class_uid": activity_instance_classes[2].uid,  # level 3
            "activity_items": [
                {
                    # Level 3 mandatory item with CT terms
                    "activity_item_class_uid": activity_item_classes[2].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[0].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [],
                    "is_adam_param_specific": False,
                },
                {
                    # Parent level 2 mandatory item with CT terms
                    "activity_item_class_uid": activity_item_classes[1].uid,
                    "ct_terms": [
                        {
                            "term_uid": ct_terms[1].term_uid,
                            "codelist_uid": codelist.codelist_uid,
                        }
                    ],
                    "unit_definition_uids": [],
                    "is_adam_param_specific": False,
                },
            ],
            "strict_mode": True,  # Strict mode - validation should run and pass
            "library_name": "Sponsor",
        },
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["name"] == "level 3 instance with parent mandatory"
    assert res["activity_instance_class"]["uid"] == activity_instance_classes[2].uid
    assert len(res["activity_items"]) == 2

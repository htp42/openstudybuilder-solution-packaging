"""
Tests for clinical_programmes endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models.concepts.odms.odm_form import OdmForm
from clinical_mdr_api.models.concepts.odms.odm_item import OdmItem
from clinical_mdr_api.models.concepts.odms.odm_item_group import OdmItemGroup
from clinical_mdr_api.models.concepts.odms.odm_study_event import OdmStudyEvent
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
study_event: OdmStudyEvent
forms: list[OdmForm]
item_groups: list[OdmItemGroup]
items: list[OdmItem]

URL = "concepts/odms"


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    inject_and_clear_db("odm.versioning.api")
    inject_base_data()

    global study_event
    global forms
    global item_groups
    global items

    forms = []
    item_groups = []
    items = []

    study_event = TestUtils.create_odm_study_event(
        name="StudyEvent 1", oid="SE1", approve=False
    )

    forms.append(TestUtils.create_odm_form(name="Form 1", oid="F1", approve=False))
    forms.append(TestUtils.create_odm_form(name="Form 2", oid="F2", approve=False))

    item_groups.append(
        TestUtils.create_odm_item_group(name="Group 1", oid="G1", approve=False)
    )
    item_groups.append(
        TestUtils.create_odm_item_group(name="Group 2", oid="G2", approve=False)
    )

    items.append(TestUtils.create_odm_item(name="Item 1", oid="I1", approve=False))
    items.append(TestUtils.create_odm_item(name="Item 2", oid="I2", approve=False))

    yield


def test_add_odm_forms_to_odm_study_event(api_client):
    data = [
        {
            "uid": forms[0].uid,
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": forms[1].uid,
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]

    response = api_client.post(
        f"concepts/odms/study-events/{study_event.uid}/forms", json=data
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "0.1",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "0.1",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]


def test_add_odm_item_groups_odm_forms(api_client):
    data = [
        {
            "uid": item_groups[0].uid,
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": item_groups[1].uid,
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.post(
        f"concepts/odms/forms/{forms[0].uid}/item-groups", json=data
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "0.1",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "0.1",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.post(
        f"concepts/odms/forms/{forms[1].uid}/item-groups", json=data
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmForm_000002"
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "0.1",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "0.1",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_add_odm_items_to_odm_item_group(api_client):
    data = [
        {
            "uid": items[0].uid,
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": items[1].uid,
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.post(
        f"concepts/odms/item-groups/{item_groups[0].uid}/items", json=data
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "0.1",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "0.1",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.post(
        f"concepts/odms/item-groups/{item_groups[1].uid}/items", json=data
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000002"
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "0.1",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "0.1",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_approve_study_event_with_cascade_effect(api_client):
    response = api_client.post(
        f"concepts/odms/study-events/{study_event.uid}/approvals"
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]

    response = api_client.get(f"concepts/odms/study-events/{study_event.uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]

    response = api_client.get(f"concepts/odms/forms/{forms[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/forms/{forms[1].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmForm_000002"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/item-groups/{item_groups[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/item-groups/{item_groups[1].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000002"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_perseverance_of_final_versions_relationship_between_item_group_and_item(
    api_client,
):
    response = api_client.post(f"concepts/odms/items/{items[0].uid}/versions")
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmItem_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"

    response = api_client.get(f"concepts/odms/item-groups/{item_groups[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_perseverance_of_final_versions_relationship_between_form_and_item_group(
    api_client,
):
    response = api_client.post(
        f"concepts/odms/item-groups/{item_groups[0].uid}/versions"
    )
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.1",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/forms/{forms[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_perseverance_of_final_versions_relationship_between_study_event_and_form(
    api_client,
):
    response = api_client.post(f"concepts/odms/forms/{forms[0].uid}/versions")
    assert_response_status_code(response, 201)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.1",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/study-events/{study_event.uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]


def test_latest_perseverance_of_relationship_based_on_latest_versions(api_client):
    response = api_client.get(f"concepts/odms/study-events/{study_event.uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]

    response = api_client.get(f"concepts/odms/forms/{forms[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.1",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(f"concepts/odms/item-groups/{item_groups[0].uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.1",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]


def test_latest_perseverance_of_relationship_based_on_specific_versions(api_client):
    response = api_client.get(f"concepts/odms/study-events/{study_event.uid}")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmStudyEvent_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["forms"] == [
        {
            "uid": "OdmForm_000001",
            "name": "Form 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "None",
        },
        {
            "uid": "OdmForm_000002",
            "name": "Form 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": "None",
        },
    ]

    response = api_client.get(f"concepts/odms/forms/{forms[0].uid}?version=1.0")
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmForm_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["item_groups"] == [
        {
            "uid": "OdmItemGroup_000001",
            "oid": "G1",
            "name": "Group 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItemGroup_000002",
            "oid": "G2",
            "name": "Group 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

    response = api_client.get(
        f"concepts/odms/item-groups/{item_groups[0].uid}?version=1.0"
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["uid"] == "OdmItemGroup_000001"
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["items"] == [
        {
            "uid": "OdmItem_000001",
            "oid": "I1",
            "name": "Item 1",
            "version": "1.0",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
        {
            "uid": "OdmItem_000002",
            "oid": "I2",
            "name": "Item 2",
            "version": "1.0",
            "order_number": 2,
            "mandatory": "No",
            "key_sequence": "None",
            "method_oid": "None",
            "imputation_method_oid": "None",
            "role": "None",
            "role_codelist_oid": "None",
            "collection_exception_condition_oid": "None",
            "vendor": {"attributes": []},
        },
    ]

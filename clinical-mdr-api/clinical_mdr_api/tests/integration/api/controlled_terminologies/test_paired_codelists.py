"""
Tests for sponsor ct package
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import json
import logging

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
catalogue: str

URL = "/ct/codelists"


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "ct-paired-codelists.api"
    inject_and_clear_db(db_name)
    inject_base_data(inject_unit_subset=False)

    global catalogue
    catalogue = "SDTM CT"
    yield


def test_get_paired_codelist(api_client):
    codes_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="prelinked codes codelist",
        library_name="Sponsor",
        approve=True,
    )
    names_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="prelinked names codelist",
        library_name="Sponsor",
        approve=True,
        paired_codes_codelist_uid=codes_cl.codelist_uid,
    )

    # Check the codelist with names
    response = api_client.get(f"{URL}/{names_cl.codelist_uid}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["codes"]["codelist_uid"] == codes_cl.codelist_uid
    assert response_json["names"] is None

    response = api_client.get(
        URL,
        params={
            "filters": json.dumps(
                {"codelist_uid": {"v": [names_cl.codelist_uid], "op": "eq"}}
            )
        },
    )
    assert_response_status_code(response, 200)
    response_json = response.json()
    print(response_json)
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["paired_names_codelist_uid"] is None
    assert (
        response_json["items"][0]["paired_codes_codelist_uid"] == codes_cl.codelist_uid
    )

    # Check the codelist with codes
    response = api_client.get(f"{URL}/{codes_cl.codelist_uid}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["names"]["codelist_uid"] == names_cl.codelist_uid
    assert response_json["codes"] is None

    response = api_client.get(
        URL,
        params={
            "filters": json.dumps(
                {"codelist_uid": {"v": [codes_cl.codelist_uid], "op": "eq"}}
            )
        },
    )
    assert_response_status_code(response, 200)
    response_json = response.json()
    print(response_json)
    assert len(response_json["items"]) == 1
    assert (
        response_json["items"][0]["paired_names_codelist_uid"] == names_cl.codelist_uid
    )
    assert response_json["items"][0]["paired_codes_codelist_uid"] is None


def test_post_paired_codelist(api_client):
    codes_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="premade codes codelist",
        library_name="Sponsor",
        approve=True,
    )
    response = api_client.post(
        URL,
        json={
            "name": "posted names codelist",
            "definition": "This is a test codelist",
            "sponsor_preferred_name": "posted names codelist",
            "catalogue_names": [catalogue],
            "library_name": "Sponsor",
            "paired_codes_codelist_uid": codes_cl.codelist_uid,
            "submission_value": "DUMMYNAMES",
            "extensible": True,
            "is_ordinal": False,
            "template_parameter": False,
            "terms": [],
        },
    )
    assert_response_status_code(response, 201)
    names_cl = response.json()

    response = api_client.get(f"{URL}/{names_cl['codelist_uid']}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["codes"]["codelist_uid"] == codes_cl.codelist_uid
    assert response_json["names"] is None


def test_add_paired_codelist(api_client):
    codes_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="unlinked codes codelist",
        library_name="Sponsor",
        approve=True,
    )
    names_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="unlinked names codelist",
        library_name="Sponsor",
        approve=True,
    )

    response = api_client.patch(
        f"{URL}/{names_cl.codelist_uid}/paired",
        json={
            "paired_codes_codelist_uid": codes_cl.codelist_uid,
        },
    )
    assert_response_status_code(response, 200)

    response = api_client.get(f"{URL}/{names_cl.codelist_uid}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["codes"]["codelist_uid"] == codes_cl.codelist_uid
    assert response_json["names"] is None

    response = api_client.get(f"{URL}/{codes_cl.codelist_uid}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["names"]["codelist_uid"] == names_cl.codelist_uid
    assert response_json["codes"] is None


def test_unlink_paired_codelists(api_client):
    codes_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="to unlinked codes codelist",
        library_name="Sponsor",
        approve=True,
    )
    names_cl = TestUtils.create_ct_codelist(
        catalogue_name=catalogue,
        name="to unlinked names codelist",
        library_name="Sponsor",
        approve=True,
        paired_codes_codelist_uid=codes_cl.codelist_uid,
    )

    response = api_client.patch(
        f"{URL}/{names_cl.codelist_uid}/paired",
        json={
            "paired_codes_codelist_uid": None,
            "paired_names_codelist_uid": None,
        },
    )
    assert_response_status_code(response, 200)

    response = api_client.get(f"{URL}/{names_cl.codelist_uid}/paired")
    assert_response_status_code(response, 200)
    response_json = response.json()
    assert response_json["codes"] is None
    assert response_json["names"] is None

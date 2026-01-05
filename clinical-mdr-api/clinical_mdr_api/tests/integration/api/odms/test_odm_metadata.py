# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_ODM_CONDITIONS,
    STARTUP_ODM_FORMS,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("odm.metadata")
    db.cypher_query(STARTUP_ODM_FORMS)
    db.cypher_query(STARTUP_ODM_CONDITIONS)

    yield

    drop_db("odm.metadata")


@pytest.mark.parametrize(
    "value, expected_result_prefix, rs_length",
    [
        pytest.param("nAme1", {"name": "name1"}, 1),
        pytest.param("mE1", {"name": "name1"}, 1),
        pytest.param("cOntext1", {"context": "context1"}, 1),
        pytest.param("eXt1", {"context": "context1"}, 1),
        pytest.param("wrong", {}, 0),
    ],
)
def test_get_aliases(
    api_client, value: str, expected_result_prefix: dict[str, str], rs_length: int
):
    response = api_client.get(f"/concepts/odms/metadata/aliases?search={value}")
    data = response.json()

    assert_response_status_code(response, 200)

    assert len(data["items"]) == rs_length
    assert data["total"] == rs_length

    for item in data["items"]:
        for key, val in expected_result_prefix.items():
            assert item[key].startswith(val)


@pytest.mark.parametrize(
    "value, expected_result_prefix, rs_length",
    [
        pytest.param("nAme1", {"name": "name1"}, 1),
        pytest.param("mE1", {"name": "name1"}, 1),
        pytest.param("eNg", {"language": "eng"}, 1),
        pytest.param("Ng", {"language": "eng"}, 1),
        pytest.param("dEscription1", {"description": "description1"}, 1),
        pytest.param("ptIon1", {"description": "description1"}, 1),
        pytest.param("inStruction1", {"instruction": "instruction1"}, 1),
        pytest.param("ctIon1", {"instruction": "instruction1"}, 1),
        pytest.param(
            "spOnsor_instruction1", {"sponsor_instruction": "sponsor_instruction1"}, 1
        ),
        pytest.param(
            "_instrUction1", {"sponsor_instruction": "sponsor_instruction1"}, 1
        ),
        pytest.param("wrong", {}, 0),
    ],
)
def test_get_descriptions(
    api_client, value: str, expected_result_prefix: dict[str, str], rs_length: int
):
    response = api_client.get(f"/concepts/odms/metadata/descriptions?search={value}")
    data = response.json()

    assert_response_status_code(response, 200)

    assert len(data["items"]) == rs_length
    assert data["total"] == rs_length

    for item in data["items"]:
        for key, val in expected_result_prefix.items():
            assert item[key].startswith(val)


@pytest.mark.parametrize(
    "value, expected_result_prefix, rs_length",
    [
        pytest.param("cOntext1", {"context": "context1"}, 1),
        pytest.param("eXt1", {"context": "context1"}, 1),
        pytest.param("expreSsion1", {"expression": "expression1"}, 1),
        pytest.param("sIon1", {"expression": "expression1"}, 1),
        pytest.param("wrong", {}, 0),
    ],
)
def test_get_formal_expressions(
    api_client, value: str, expected_result_prefix: dict[str, str], rs_length: int
):
    response = api_client.get(
        f"/concepts/odms/metadata/formal-expressions?search={value}"
    )
    data = response.json()

    assert_response_status_code(response, 200)

    assert len(data["items"]) == rs_length
    assert data["total"] == rs_length

    for item in data["items"]:
        for key, val in expected_result_prefix.items():
            assert item[key].startswith(val)


def test_doesnt_return_aliases_that_are_only_connected_to_deleted_odms(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "to be deleted1",
        "oid": "oid",
        "sdtm_version": "0.1",
        "repeating": "No",
        "descriptions": [],
        "aliases": [{"context": "connected to deleted", "name": "deleted"}],
    }
    response = api_client.post("concepts/odms/forms", json=data)
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get("/concepts/odms/metadata/aliases?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["context"] == "connected to deleted" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.delete(f"concepts/odms/forms/{rs["uid"]}")
    assert_response_status_code(response, 204)

    response = api_client.get("/concepts/odms/metadata/aliases?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["context"] != "connected to deleted" for item in data["items"])
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_doesnt_return_descriptions_that_are_only_connected_to_deleted_odms(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "to be deleted2",
        "oid": "oid",
        "sdtm_version": "0.1",
        "repeating": "No",
        "descriptions": [
            {
                "name": "connected to deleted",
                "language": "eng",
                "description": "description",
                "instruction": "instruction",
                "sponsor_instruction": "sponsor_instruction",
            }
        ],
        "aliases": [],
    }
    response = api_client.post("concepts/odms/forms", json=data)
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get("/concepts/odms/metadata/descriptions?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["name"] == "connected to deleted" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.delete(f"concepts/odms/forms/{rs["uid"]}")
    assert_response_status_code(response, 204)

    response = api_client.get("/concepts/odms/metadata/descriptions?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["name"] != "connected to deleted" for item in data["items"])
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_doesnt_return_formal_expressions_that_are_only_connected_to_deleted_odms(
    api_client,
):
    data = {
        "library_name": "Sponsor",
        "name": "to be deleted1",
        "oid": "oid",
        "formal_expressions": [
            {"context": "connected to deleted", "expression": "expression"}
        ],
        "descriptions": [],
        "aliases": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get(
        "/concepts/odms/metadata/formal-expressions?page_size=1000"
    )
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["context"] == "connected to deleted" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.delete(f"concepts/odms/conditions/{rs["uid"]}")
    assert_response_status_code(response, 204)

    response = api_client.get(
        "/concepts/odms/metadata/formal-expressions?page_size=1000"
    )
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["context"] != "connected to deleted" for item in data["items"])
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_doesnt_return_aliases_that_are_not_connected_to_latest_odms(api_client):
    response = api_client.post(
        "concepts/odms/forms",
        json={
            "library_name": "Sponsor",
            "name": "to be updated1",
            "oid": "oid",
            "sdtm_version": "0.1",
            "repeating": "No",
            "descriptions": [],
            "aliases": [{"context": "connected to be renamed", "name": "renaming"}],
        },
    )
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get("/concepts/odms/metadata/aliases?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["context"] == "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.patch(
        f"concepts/odms/forms/{rs["uid"]}",
        json={
            "library_name": "Sponsor",
            "name": "to be updated1",
            "oid": "oid",
            "sdtm_version": "0.1",
            "repeating": "No",
            "descriptions": [],
            "aliases": [{"context": "done", "name": "renamed"}],
            "change_description": "Updating alias",
        },
    )
    assert_response_status_code(response, 200)

    response = api_client.get("/concepts/odms/metadata/aliases?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["context"] != "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_doesnt_return_descriptions_that_are_not_connected_to_latest_odms(api_client):
    response = api_client.post(
        "concepts/odms/forms",
        json={
            "library_name": "Sponsor",
            "name": "to be updated2",
            "oid": "oid",
            "sdtm_version": "0.1",
            "repeating": "No",
            "descriptions": [
                {
                    "name": "connected to be renamed",
                    "language": "eng",
                    "description": "description",
                    "instruction": "instruction",
                    "sponsor_instruction": "sponsor_instruction",
                }
            ],
            "aliases": [],
        },
    )
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get("/concepts/odms/metadata/descriptions?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["name"] == "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.patch(
        f"concepts/odms/forms/{rs["uid"]}",
        json={
            "library_name": "Sponsor",
            "name": "to be updated2",
            "oid": "oid",
            "sdtm_version": "0.1",
            "repeating": "No",
            "descriptions": [
                {
                    "name": "renamed",
                    "language": "eng",
                    "description": "description",
                    "instruction": "instruction",
                    "sponsor_instruction": "sponsor_instruction",
                }
            ],
            "aliases": [],
            "change_description": "Updating description",
        },
    )
    assert_response_status_code(response, 200)

    response = api_client.get("/concepts/odms/metadata/descriptions?page_size=1000")
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["name"] != "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_doesnt_return_formal_expressions_that_are_not_connected_to_latest_odms(
    api_client,
):
    response = api_client.post(
        "concepts/odms/conditions",
        json={
            "library_name": "Sponsor",
            "name": "to be renamed1",
            "oid": "oid",
            "formal_expressions": [
                {"context": "connected to be renamed", "expression": "renaming"}
            ],
            "descriptions": [],
            "aliases": [],
        },
    )
    assert_response_status_code(response, 201)
    rs = response.json()

    response = api_client.get(
        "/concepts/odms/metadata/formal-expressions?page_size=1000"
    )
    assert_response_status_code(response, 200)
    data = response.json()
    assert any(item["context"] == "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

    response = api_client.patch(
        f"concepts/odms/conditions/{rs["uid"]}",
        json={
            "library_name": "Sponsor",
            "name": "to be renamed1",
            "oid": "oid",
            "formal_expressions": [{"context": "renamed", "expression": "done"}],
            "descriptions": [],
            "aliases": [],
            "change_description": "Updating formal expression",
        },
    )
    assert_response_status_code(response, 200)

    response = api_client.get(
        "/concepts/odms/metadata/formal-expressions?page_size=1000"
    )
    assert_response_status_code(response, 200)
    data = response.json()
    assert all(item["context"] != "connected to be renamed" for item in data["items"])
    assert data["total"] == 2
    assert len(data["items"]) == 2

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

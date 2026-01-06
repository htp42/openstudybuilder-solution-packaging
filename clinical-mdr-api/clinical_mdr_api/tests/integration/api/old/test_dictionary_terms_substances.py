# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import json

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_DICTIONARY_CODELISTS_CYPHER,
    STARTUP_DICTIONARY_TERMS_CYPHER,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.dictionary.terms.substances")
    db.cypher_query(STARTUP_DICTIONARY_CODELISTS_CYPHER)
    db.cypher_query(STARTUP_DICTIONARY_TERMS_CYPHER)

    yield

    drop_db("old.json.test.dictionary.terms.substances")


def test_post_create_med_rt_dictionary_term_pharmacological_class(api_client):
    data = {
        "dictionary_id": "dictionary_id_pharma_class",
        "name": "name_pharma_class",
        "name_sentence_case": "name_pharma_class",
        "abbreviation": "abbreviation_pharma_class",
        "definition": "definition_pharma_class",
        "codelist_uid": "codelist_pclass_uid",
        "library_name": "MED-RT",
    }
    response = api_client.post("/dictionaries/terms", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000001"
    assert res["dictionary_id"] == "dictionary_id_pharma_class"
    assert res["name"] == "name_pharma_class"
    assert res["name_sentence_case"] == "name_pharma_class"
    assert res["abbreviation"] == "abbreviation_pharma_class"
    assert res["definition"] == "definition_pharma_class"
    assert res["library_name"] == "MED-RT"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_post_create_substance_dictionary_term(api_client):
    data = {
        "dictionary_id": "dictionary_id_substance",
        "name": "name_substance",
        "name_sentence_case": "name_substance",
        "abbreviation": "abbreviation_substance",
        "definition": "definition_substance",
        "codelist_uid": "codelist_unii_uid",
        "library_name": "UNII",
        "pclass_uid": "DictionaryTerm_000001",
    }
    response = api_client.post("/dictionaries/substances", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000002"
    assert res["dictionary_id"] == "dictionary_id_substance"
    assert res["name"] == "name_substance"
    assert res["name_sentence_case"] == "name_substance"
    assert res["abbreviation"] == "abbreviation_substance"
    assert res["definition"] == "definition_substance"
    assert res["library_name"] == "UNII"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["pclass"] == {
        "term_uid": "DictionaryTerm_000001",
        "name": "name_pharma_class",
        "dictionary_id": "dictionary_id_pharma_class",
    }


def test_post_create_substance_dictionary_term_without_pclass(api_client):
    data = {
        "dictionary_id": "dictionary_id_substance_without_pclass",
        "name": "name_substance_without_pclass",
        "name_sentence_case": "name_substance_without_pclass",
        "abbreviation": "abbreviation_substance_without_pclass",
        "definition": "definition_substance_without_pclass",
        "codelist_uid": "codelist_unii_uid",
        "library_name": "UNII",
    }
    response = api_client.post("/dictionaries/substances", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000003"
    assert res["dictionary_id"] == "dictionary_id_substance_without_pclass"
    assert res["name"] == "name_substance_without_pclass"
    assert res["name_sentence_case"] == "name_substance_without_pclass"
    assert res["abbreviation"] == "abbreviation_substance_without_pclass"
    assert res["definition"] == "definition_substance_without_pclass"
    assert res["library_name"] == "UNII"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["pclass"] is None


def test_get_substance_term(api_client):
    response = api_client.get("/dictionaries/substances/DictionaryTerm_000002")
    assert_response_status_code(response, 200)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000002"
    assert res["dictionary_id"] == "dictionary_id_substance"
    assert res["name"] == "name_substance"
    assert res["name_sentence_case"] == "name_substance"
    assert res["abbreviation"] == "abbreviation_substance"
    assert res["definition"] == "definition_substance"
    assert res["library_name"] == "UNII"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["pclass"] == {
        "term_uid": "DictionaryTerm_000001",
        "name": "name_pharma_class",
        "dictionary_id": "dictionary_id_pharma_class",
    }


def test_get_all_substance_dictionary_terms(api_client):
    response = api_client.get(
        '/dictionaries/substances?total_count=true&sort_by={"pclass.name":true}'
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["term_uid"] == "DictionaryTerm_000002"
    assert res["items"][0]["dictionary_id"] == "dictionary_id_substance"
    assert res["items"][0]["name"] == "name_substance"
    assert res["items"][0]["name_sentence_case"] == "name_substance"
    assert res["items"][0]["abbreviation"] == "abbreviation_substance"
    assert res["items"][0]["definition"] == "definition_substance"
    assert res["items"][0]["library_name"] == "UNII"
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.1"
    assert res["items"][0]["change_description"] == "Initial version"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["possible_actions"] == ["approve", "delete", "edit"]
    assert res["items"][0]["pclass"] == {
        "term_uid": "DictionaryTerm_000001",
        "name": "name_pharma_class",
        "dictionary_id": "dictionary_id_pharma_class",
    }


@pytest.mark.parametrize(
    "filter_by, expected_count",
    [
        (
            {"*": {"v": [""]}},
            2,
        ),
        (
            {"*": {"v": ["name_pharma_class"]}},
            1,
        ),
        (
            {"*": {"v": ["dictionary_id_pharma_class"]}},
            1,
        ),
        (
            {"*": {"v": ["name_substance"]}},
            2,
        ),
        (
            {"*": {"v": ["dictionary_id_substance"]}},
            2,
        ),
        (
            {"*": {"v": ["name_substance_without_pclass"]}},
            1,
        ),
        (
            {"*": {"v": ["dictionary_id_substance_without_pclass"]}},
            1,
        ),
        (
            {"*": {"v": ["ufghdsjkafhdsjakfhkjsdahfl"]}},
            0,
        ),
    ],
)
def test_get_substance_dictionary_terms_filtering(
    api_client, filter_by, expected_count
):
    response = api_client.get(
        "/dictionaries/substances",
        params={
            "filters": json.dumps(filter_by),
            "total_count": "true",
        },
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["total"] == expected_count


@pytest.mark.parametrize(
    "field_name",
    [
        "name",
        "dictionary_id",
        "abbreviation",
        "definition",
        "pclass",
        "pclass.name",
        "pclass.dictionary_id",
    ],
)
def test_get_substance_dictionary_terms_headers(api_client, field_name):
    response = api_client.get(
        "/dictionaries/substances/headers",
        params={"page_size": 100, "field_name": field_name},
    )

    assert_response_status_code(response, 200)

    res = response.json()

    if field_name == "name":
        assert set(res) == {"name_substance", "name_substance_without_pclass"}
    elif field_name == "dictionary_id":
        assert set(res) == {
            "dictionary_id_substance",
            "dictionary_id_substance_without_pclass",
        }
    elif field_name == "abbreviation":
        assert set(res) == {
            "abbreviation_substance",
            "abbreviation_substance_without_pclass",
        }
    elif field_name == "definition":
        assert set(res) == {
            "definition_substance",
            "definition_substance_without_pclass",
        }
    elif field_name == "pclass":
        assert res == [
            {
                "uid": "DictionaryTerm_000001",
                "dictionary_id": "dictionary_id_pharma_class",
                "name": "name_pharma_class",
            }
        ]
    elif field_name == "pclass.name":
        assert set(res) == {"name_pharma_class"}
    elif field_name == "pclass.dictionary_id":
        assert set(res) == {"dictionary_id_pharma_class"}


def test_patch_draft_term1(api_client):
    data = {
        "name": "term new name",
        "name_sentence_case": "Term new name",
        "definition": "new_definition",
        "change_description": "term patch",
    }
    response = api_client.patch(
        "/dictionaries/substances/DictionaryTerm_000002", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000002"
    assert res["dictionary_id"] == "dictionary_id_substance"
    assert res["name"] == "term new name"
    assert res["name_sentence_case"] == "Term new name"
    assert res["abbreviation"] == "abbreviation_substance"
    assert res["definition"] == "new_definition"
    assert res["library_name"] == "UNII"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["change_description"] == "term patch"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["pclass"] is None


def test_get_substance_term_after_update(api_client):
    response = api_client.get("/dictionaries/substances/DictionaryTerm_000002")
    assert_response_status_code(response, 200)

    res = response.json()

    assert res["term_uid"] == "DictionaryTerm_000002"
    assert res["dictionary_id"] == "dictionary_id_substance"
    assert res["name"] == "term new name"
    assert res["name_sentence_case"] == "Term new name"
    assert res["abbreviation"] == "abbreviation_substance"
    assert res["definition"] == "new_definition"
    assert res["library_name"] == "UNII"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["change_description"] == "term patch"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]
    assert res["pclass"] is None

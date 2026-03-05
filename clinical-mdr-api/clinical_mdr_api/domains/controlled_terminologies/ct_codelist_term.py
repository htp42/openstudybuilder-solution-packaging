from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

from clinical_mdr_api.domain_repositories.models._utils import convert_to_datetime
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus


@dataclass(frozen=True)
class CTCodelistTermVO:
    """
    The CTCodelistNameVO acts as the value object for a single CTCodelist name
    """

    term_uid: str
    sponsor_preferred_name: str
    sponsor_preferred_name_sentence_case: str
    name_status: LibraryItemStatus
    name_date: datetime
    start_date: datetime
    end_date: datetime | None
    attributes_status: LibraryItemStatus
    attributes_date: datetime
    submission_value: str
    order: int | None
    ordinal: float | None
    concept_id: str | None
    nci_preferred_name: str | None
    definition: str
    library_name: str | None

    @classmethod
    def from_result_dict(cls, result: dict[str, Any]) -> Self:
        ct_codelist_term_vo = cls(
            term_uid=result["term_uid"],
            sponsor_preferred_name=result["sponsor_preferred_name"],
            sponsor_preferred_name_sentence_case=result[
                "sponsor_preferred_name_sentence_case"
            ],
            name_status=LibraryItemStatus(result["name_status"]),
            name_date=convert_to_datetime(result["name_date"]),
            attributes_status=LibraryItemStatus(result["attributes_status"]),
            attributes_date=convert_to_datetime(result["attributes_date"]),
            submission_value=result["submission_value"],
            order=result.get("order"),
            ordinal=result.get("ordinal"),
            start_date=convert_to_datetime(result["start_date"]),
            end_date=convert_to_datetime(result.get("end_date")),
            concept_id=result.get("concept_id"),
            nci_preferred_name=result.get("nci_preferred_name"),
            definition=result["definition"],
            library_name=result.get("library_name"),
        )

        return ct_codelist_term_vo


@dataclass
class CTCodelistTermAR:
    _ct_codelist_term_vo: CTCodelistTermVO

    @property
    def ct_codelist_term_vo(self) -> CTCodelistTermVO:
        return self._ct_codelist_term_vo

    @classmethod
    def from_repository_values(
        cls,
        ct_codelist_term_vo: CTCodelistTermVO,
    ) -> Self:
        ct_codelist_term_ar = cls(
            _ct_codelist_term_vo=ct_codelist_term_vo,
        )
        return ct_codelist_term_ar

    @classmethod
    def from_result_dict(cls, result: dict[str, Any]) -> Self:
        return cls.from_repository_values(CTCodelistTermVO.from_result_dict(result))


@dataclass(frozen=True)
class CTSimpleCodelistTermVO:
    """
    The CTSimpleCodelistTermVO acts as the value object for a single CT simple codelist term
    """

    term_uid: str
    term_name: str
    submission_value: str
    preferred_term: str | None
    order: int | None
    ordinal: float | None
    codelist_uid: str | None
    codelist_name: str | None
    codelist_submission_value: str | None
    date_conflict: bool

    @classmethod
    def from_result_dict(cls, result: dict[str, Any]) -> Self:
        ct_simple_codelist_term_vo = cls(
            term_uid=result["term_uid"],
            term_name=result["term_name"],
            submission_value=result["submission_value"],
            preferred_term=result.get("preferred_term"),
            order=result.get("order"),
            ordinal=result.get("ordinal"),
            codelist_uid=result.get("codelist_uid"),
            codelist_name=result.get("codelist_name"),
            codelist_submission_value=result.get("codelist_submission_value"),
            date_conflict=result.get("date_conflict", False),
        )

        return ct_simple_codelist_term_vo


@dataclass
class CTSimpleCodelistTermAR:
    _ct_simple_codelist_term_vo: CTSimpleCodelistTermVO

    @property
    def ct_simple_codelist_term_vo(self) -> CTSimpleCodelistTermVO:
        return self._ct_simple_codelist_term_vo

    @classmethod
    def from_repository_values(
        cls,
        ct_simple_codelist_term_vo: CTSimpleCodelistTermVO,
    ) -> Self:
        ct_simple_codelist_term_ar = cls(
            _ct_simple_codelist_term_vo=ct_simple_codelist_term_vo,
        )
        return ct_simple_codelist_term_ar

    @classmethod
    def from_result_dict(cls, result: dict[str, Any]) -> Self:
        return cls.from_repository_values(
            CTSimpleCodelistTermVO.from_result_dict(result)
        )

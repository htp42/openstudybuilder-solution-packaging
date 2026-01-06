from datetime import datetime
from typing import Any, TypeVar

from neomodel import db

from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTCodelistRoot,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_codelist_attributes import (
    CTCodelistAttributesAR,
    CTCodelistAttributesVO,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_codelist_name import (
    CTCodelistNameAR,
    CTCodelistNameVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryVO
from clinical_mdr_api.models.controlled_terminologies.ct_codelist import (
    CTCodelist,
    CTCodelistCreateInput,
    CTCodelistNameAndAttributes,
    CTCodelistPaired,
    CTCodelistPairedInput,
    CTCodelistTerm,
)
from clinical_mdr_api.models.utils import GenericFilteringReturn
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository  # type: ignore
from clinical_mdr_api.services._utils import ensure_transaction, is_library_editable
from clinical_mdr_api.services.controlled_terminologies.ct_codelist_attributes import (
    CTCodelistAttributesService,
)
from clinical_mdr_api.services.controlled_terminologies.ct_codelist_name import (
    CTCodelistNameService,
)
from clinical_mdr_api.utils import normalize_string
from common.auth.user import user
from common.exceptions import (
    AlreadyExistsException,
    BusinessLogicException,
    NotFoundException,
)

_AggregateRootType = TypeVar("_AggregateRootType")


class CTCodelistService:
    _repos: MetaRepository
    author_id: str

    def __init__(self):
        self.author_id = user().id()
        self._repos = MetaRepository(self.author_id)

    def __del__(self):
        self._repos.close()

    def non_transactional_create(
        self,
        codelist_input: CTCodelistCreateInput,
        start_date: datetime | None = None,
        approve: bool = False,
    ) -> CTCodelist:
        """
        Method creates CTCodelistAttributesAR and saves that object to the database.
        When saving CTCodelistAttributesAR - CTCodelistRoot node is created that will become a root node for
        CTCodelistAttributes and CTCodelistName nodes.
        The uid for the CTCodelistRoot is assigned when the CTCodelistAttributesAR is being created.
        Created CTCodelistRoot uid is then passed to the CTCodelistNameAR.
        The uid of CTCodelistRoot node is used by CTCodelistName repository to create a
        relationship from CTCodelistRoot to CTCodelistName node when saving a CTCodelistNameAR.
        If terms are provided then the codelist will be approved and the terms will be connected to the codelist.
        When no terms are provided the codelist is created in draft state.
        :param codelist_input:
        :return codelist:CTCodelist
        """

        BusinessLogicException.raise_if_not(
            self._repos.library_repository.library_exists(
                normalize_string(codelist_input.library_name)
            ),
            msg=f"Library with Name '{codelist_input.library_name}' doesn't exist.",
        )

        library_vo = LibraryVO.from_input_values_2(
            library_name=codelist_input.library_name,
            is_library_editable_callback=is_library_editable,
        )

        ct_codelist_attributes_ar = CTCodelistAttributesAR.from_input_values(
            author_id=self.author_id,
            ct_codelist_attributes_vo=CTCodelistAttributesVO.from_input_values(
                name=codelist_input.name,
                parent_codelist_uid=codelist_input.parent_codelist_uid,
                catalogue_names=codelist_input.catalogue_names,
                submission_value=codelist_input.submission_value,
                preferred_term=codelist_input.nci_preferred_name,
                definition=codelist_input.definition,
                extensible=codelist_input.extensible,
                ordinal=codelist_input.ordinal,
                catalogue_exists_callback=self._repos.ct_catalogue_repository.catalogue_exists,
                codelist_exists_by_uid_callback=self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_uid,
                codelist_exists_by_name_callback=self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_name,
                codelist_exists_by_submission_value_callback=(
                    self._repos.ct_codelist_attribute_repository.codelist_attributes_exists_by_submission_value
                ),
            ),
            library=library_vo,
            start_date=start_date,
            generate_uid_callback=self._repos.ct_codelist_attribute_repository.generate_uid,
        )

        if codelist_input.terms or approve is True:
            ct_codelist_attributes_ar.approve(author_id=self.author_id)

        self._repos.ct_codelist_attribute_repository.save(ct_codelist_attributes_ar)

        # Link to paired codelist if provided
        if codelist_input.paired_codes_codelist_uid:
            BusinessLogicException.raise_if_not(
                self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_uid(
                    codelist_input.paired_codes_codelist_uid
                ),
                msg=f"The given paired codes codelist with UID '{codelist_input.paired_codes_codelist_uid}' doesn't exist.",
            )
            self._repos.ct_codelist_aggregated_repository.merge_link_to_codes_codelist(
                ct_codelist_attributes_ar.uid,
                codelist_input.paired_codes_codelist_uid,
            )
        if codelist_input.paired_names_codelist_uid:
            BusinessLogicException.raise_if_not(
                self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_uid(
                    codelist_input.paired_names_codelist_uid
                ),
                msg=f"The given paired names codelist with UID '{codelist_input.paired_names_codelist_uid}' doesn't exist.",
            )
            self._repos.ct_codelist_aggregated_repository.merge_link_to_codes_codelist(
                codelist_input.paired_names_codelist_uid,
                ct_codelist_attributes_ar.uid,
            )

        ct_codelist_name_ar = CTCodelistNameAR.from_input_values(
            author_id=self.author_id,
            ct_codelist_name_vo=CTCodelistNameVO.from_input_values(
                name=codelist_input.sponsor_preferred_name,
                catalogue_names=codelist_input.catalogue_names,
                is_template_parameter=codelist_input.template_parameter,
                catalogue_exists_callback=self._repos.ct_catalogue_repository.catalogue_exists,
                codelist_exists_by_name_callback=self._repos.ct_codelist_name_repository.codelist_specific_exists_by_name,
            ),
            library=library_vo,
            start_date=start_date,
            generate_uid_callback=lambda: ct_codelist_attributes_ar.uid,
        )

        if approve is True:
            ct_codelist_name_ar.approve(author_id=self.author_id)

        self._repos.ct_codelist_name_repository.save(ct_codelist_name_ar)

        if codelist_input.terms:
            parent_codelist_uid = (
                ct_codelist_attributes_ar.ct_codelist_vo.parent_codelist_uid
            )

            term_uids = [term.term_uid for term in codelist_input.terms]

            if parent_codelist_uid:
                sub_codelist_with_given_terms = (
                    self.get_sub_codelists_that_have_given_terms(
                        parent_codelist_uid, term_uids
                    )
                )

                AlreadyExistsException.raise_if(
                    sub_codelist_with_given_terms.items,
                    msg=f"""Sub codelists with these terms already exist.
                        Codelist UIDs ({[item.codelist_uid for item in sub_codelist_with_given_terms.items]})""",
                )

            for term in codelist_input.terms:
                BusinessLogicException.raise_if(
                    parent_codelist_uid
                    and len(
                        self._repos.ct_term_aggregated_repository.find_all_aggregated_result(
                            filter_by={
                                "codelists.codelist_uid": {
                                    "v": [parent_codelist_uid],
                                    "op": "eq",
                                },
                                "term_uid": {"v": [term.term_uid], "op": "eq"},
                            }
                        )[
                            0
                        ]
                    )
                    <= 0,
                    msg=f"Term with UID '{term.term_uid}' isn't in use by Parent Codelist with UID '{parent_codelist_uid}'.",
                )

                self._repos.ct_codelist_attribute_repository.add_term(
                    codelist_uid=ct_codelist_attributes_ar.uid,
                    term_uid=term.term_uid,
                    author_id=self.author_id,
                    order=term.order,
                    submission_value=term.submission_value,
                )

        if ct_codelist_name_ar is None or ct_codelist_attributes_ar is None:
            raise ValueError("CodelistNameAR or CodelistAttributesAR is None.")

        return CTCodelist.from_ct_codelist_ar(
            ct_codelist_name_ar,
            ct_codelist_attributes_ar,
            paired_codes_codelist_uid=codelist_input.paired_codes_codelist_uid,
            paired_names_codelist_uid=codelist_input.paired_names_codelist_uid,
        )

    @ensure_transaction(db)
    def create(
        self,
        codelist_input: CTCodelistCreateInput,
        start_date: datetime | None = None,
        approve: bool = False,
    ) -> CTCodelist:
        return self.non_transactional_create(
            codelist_input, start_date=start_date, approve=approve
        )

    def get_all_codelists(
        self,
        catalogue_name: str | None = None,
        library: str | None = None,
        package: str | None = None,
        is_sponsor: bool = False,
        sort_by: dict[str, bool] | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
        term_filter: dict[str, str | list[Any]] | None = None,
    ) -> GenericFilteringReturn[CTCodelistNameAndAttributes]:
        self.enforce_catalogue_library_package(catalogue_name, library, package)

        all_aggregated_codelists, total = (
            self._repos.ct_codelist_aggregated_repository.find_all_aggregated_result(
                catalogue_name=catalogue_name,
                library=library,
                package=package,
                is_sponsor=is_sponsor,
                total_count=total_count,
                sort_by=sort_by,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_number=page_number,
                page_size=page_size,
                term_filter=term_filter,
            )
        )

        items = [
            CTCodelistNameAndAttributes.from_ct_codelist_ar(
                ct_codelist_name_ar,
                ct_codelist_attributes_ar,
                paired_codes_codelist_uid=paired.paired_codes_codelist_uid,
                paired_names_codelist_uid=paired.paired_names_codelist_uid,
            )
            for ct_codelist_name_ar, ct_codelist_attributes_ar, paired in all_aggregated_codelists
        ]

        return GenericFilteringReturn(items=items, total=total)

    def get_sub_codelists_that_have_given_terms(
        self,
        codelist_uid: str,
        term_uids: list[str],
        catalogue_name: str | None = None,
        library: str | None = None,
        package: str | None = None,
        sort_by: dict[str, bool] | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[CTCodelistNameAndAttributes]:
        self.enforce_catalogue_library_package(catalogue_name, library, package)

        all_aggregated_sub_codelists, total = (
            self._repos.ct_codelist_aggregated_repository.find_all_aggregated_result(
                library=library,
                total_count=total_count,
                sort_by=sort_by,
                filter_by={"parent_codelist_uid": {"v": [codelist_uid], "op": "eq"}},
                filter_operator=filter_operator,
                page_number=page_number,
                page_size=page_size,
            )
        )

        uid_of_sub_codelist_with_terms = []

        for sub_codelist in all_aggregated_sub_codelists:
            all_aggregated_terms, _ = (
                self._repos.ct_term_aggregated_repository.find_all_aggregated_result(
                    codelist_uid=sub_codelist[1].uid,
                    codelist_name=None,
                    library=library,
                    package=package,
                    total_count=total_count,
                    sort_by=sort_by,
                    filter_by=filter_by,
                    filter_operator=filter_operator,
                    page_number=page_number,
                    page_size=page_size,
                )
            )

            if set(term_uids) == {term[1].uid for term in all_aggregated_terms}:
                uid_of_sub_codelist_with_terms.append(sub_codelist[1].uid)

        items = [
            CTCodelistNameAndAttributes.from_ct_codelist_ar(
                ct_codelist_name_ar,
                ct_codelist_attributes_ar,
                paired_codes_codelist_uid=paired.paired_codes_codelist_uid,
                paired_names_codelist_uid=paired.paired_names_codelist_uid,
            )
            for ct_codelist_name_ar, ct_codelist_attributes_ar, paired in all_aggregated_sub_codelists
            if ct_codelist_attributes_ar.uid in uid_of_sub_codelist_with_terms
        ]

        return GenericFilteringReturn(items=items, total=total)

    def get_distinct_values_for_header(
        self,
        catalogue_name: str | None,
        library: str | None,
        package: str | None,
        field_name: str,
        is_sponsor: bool = False,
        search_string: str = "",
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        page_size: int = 10,
    ):
        self.enforce_catalogue_library_package(catalogue_name, library, package)

        header_values = (
            self._repos.ct_codelist_aggregated_repository.get_distinct_headers(
                catalogue_name=catalogue_name,
                library=library,
                package=package,
                is_sponsor=is_sponsor,
                field_name=field_name,
                search_string=search_string,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_size=page_size,
            )
        )

        return header_values

    def non_transactional_add_term(
        self, codelist_uid: str, term_uid: str, order: int, submission_value: str
    ) -> CTCodelist:
        ct_codelist_attributes_ar = (
            self._repos.ct_codelist_attribute_repository.find_by_uid(
                codelist_uid=codelist_uid
            )
        )

        if ct_codelist_attributes_ar is not None:
            BusinessLogicException.raise_if(
                not ct_codelist_attributes_ar.library.is_editable
                and not ct_codelist_attributes_ar.ct_codelist_vo.extensible,
                msg=f"Codelist with UID '{codelist_uid}' isn't extensible.",
            )

            if ct_codelist_attributes_ar.ct_codelist_vo.ordinal and order is None:
                raise BusinessLogicException(
                    msg=f"Codelist identified by {codelist_uid} is ordinal and order is required"
                )

            parent_codelist_uid = (
                ct_codelist_attributes_ar.ct_codelist_vo.parent_codelist_uid
            )
            BusinessLogicException.raise_if(
                parent_codelist_uid
                and len(
                    self._repos.ct_term_aggregated_repository.find_all_aggregated_result(
                        filter_by={
                            "codelists.codelist_uid": {
                                "v": [parent_codelist_uid],
                                "op": "eq",
                            },
                            "term_uid": {"v": [term_uid], "op": "eq"},
                        }
                    )[
                        0
                    ]
                )
                <= 0,
                msg=f"Term with UID '{term_uid}' isn't in use by Parent Codelist with UID '{parent_codelist_uid}'.",
            )

        ct_codelist_name_ar = self._repos.ct_codelist_name_repository.find_by_uid(
            codelist_uid=codelist_uid
        )
        paired_codes_codelist_uid, paired_names_codelist_uid = (
            self._repos.ct_codelist_aggregated_repository.get_paired_codelist_uids(
                codelist_uid=codelist_uid
            )
        )
        self._repos.ct_codelist_attribute_repository.add_term(
            codelist_uid=codelist_uid,
            term_uid=term_uid,
            author_id=self.author_id,
            order=order,
            submission_value=submission_value,
        )

        if ct_codelist_attributes_ar is None or ct_codelist_name_ar is None:
            raise BusinessLogicException(
                msg=f"Codelist with UID '{codelist_uid}' doesn't exist."
            )

        return CTCodelist.from_ct_codelist_ar(
            ct_codelist_name_ar,
            ct_codelist_attributes_ar,
            paired_codes_codelist_uid=paired_codes_codelist_uid,
            paired_names_codelist_uid=paired_names_codelist_uid,
        )

    @db.transaction
    def add_term(
        self, codelist_uid: str, term_uid: str, order: int, submission_value: str
    ) -> CTCodelist:
        return self.non_transactional_add_term(
            codelist_uid, term_uid, order, submission_value
        )

    @db.transaction
    def remove_term(self, codelist_uid: str, term_uid: str) -> CTCodelist:
        ct_codelist_attributes_ar = (
            self._repos.ct_codelist_attribute_repository.find_by_uid(
                codelist_uid=codelist_uid
            )
        )
        if ct_codelist_attributes_ar is not None:
            BusinessLogicException.raise_if(
                not ct_codelist_attributes_ar.library.is_editable
                and not ct_codelist_attributes_ar.ct_codelist_vo.extensible,
                msg=f"Codelist with UID '{codelist_uid}' isn't extensible.",
            )

            child_codelist_uids = (
                ct_codelist_attributes_ar.ct_codelist_vo.child_codelist_uids
            )
            if child_codelist_uids:
                terms = self._repos.ct_term_aggregated_repository.find_all_aggregated_result(
                    filter_by={
                        "codelists.codelist_uid": {
                            "v": child_codelist_uids,
                            "op": "eq",
                        },
                        "term_uid": {"v": [term_uid], "op": "eq"},
                    }
                )[
                    0
                ]
                BusinessLogicException.raise_if(
                    len(terms) > 0,
                    msg=f"The term with UID '{term_uid}' is in use by child codelists"
                    f" with UIDs {[term[1]._ct_term_attributes_vo.codelist_uid for term in terms]}",
                )
        ct_codelist_name_ar = self._repos.ct_codelist_name_repository.find_by_uid(
            codelist_uid=codelist_uid
        )
        paired_codes_codelist_uid, paired_names_codelist_uid = (
            self._repos.ct_codelist_aggregated_repository.get_paired_codelist_uids(
                codelist_uid=codelist_uid
            )
        )

        self._repos.ct_codelist_attribute_repository.remove_term(
            codelist_uid=codelist_uid, term_uid=term_uid, author_id=self.author_id
        )

        if ct_codelist_attributes_ar is None or ct_codelist_name_ar is None:
            raise BusinessLogicException(
                msg=f"Codelist with UID '{codelist_uid}' doesn't exist."
            )

        return CTCodelist.from_ct_codelist_ar(
            ct_codelist_name_ar,
            ct_codelist_attributes_ar,
            paired_codes_codelist_uid=paired_codes_codelist_uid,
            paired_names_codelist_uid=paired_names_codelist_uid,
        )

    def enforce_catalogue_library_package(
        self,
        catalogue_name: str | None,
        library: str | None,
        package: str | None,
    ):
        NotFoundException.raise_if(
            catalogue_name is not None
            and not self._repos.ct_catalogue_repository.catalogue_exists(
                normalize_string(catalogue_name)
            ),
            "Catalogue",
            catalogue_name,
            "Name",
        )
        NotFoundException.raise_if(
            library is not None
            and not self._repos.library_repository.library_exists(
                normalize_string(library)
            ),
            "Library",
            library,
            "Name",
        )
        NotFoundException.raise_if(
            package is not None
            and not self._repos.ct_package_repository.package_exists(
                normalize_string(package)
            )
        )

    def list_terms(
        self,
        codelist_uid: str | None = None,
        codelist_submission_value: str | None = None,
        codelist_name: str | None = None,
        package: str | None = None,
        include_removed: bool | None = None,
        at_specific_date_time: datetime | None = None,
        sort_by: dict[str, bool] | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
    ) -> GenericFilteringReturn[CTCodelistTerm]:
        all_aggregated_terms, count = (
            self._repos.ct_codelist_aggregated_repository.find_all_terms_aggregated_result(
                package=package,
                include_removed=include_removed,
                at_specific_date_time=at_specific_date_time,
                codelist_uid=codelist_uid,
                codelist_submission_value=codelist_submission_value,
                codelist_name=codelist_name,
                total_count=total_count,
                sort_by=sort_by,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_number=page_number,
                page_size=page_size,
            )
        )

        items = [
            CTCodelistTerm.from_ct_codelist_term_ar(ct_codelist_term_ar)
            for ct_codelist_term_ar in all_aggregated_terms
        ]

        return GenericFilteringReturn.create(items=items, total=count)

    def get_distinct_term_values_for_header(
        self,
        codelist_uid: str,
        package: str | None,
        field_name: str,
        include_removed: bool | None = None,
        search_string: str | None = "",
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        page_size: int = 10,
    ):
        header_values = (
            self._repos.ct_codelist_aggregated_repository.get_distinct_term_headers(
                codelist_uid=codelist_uid,
                package=package,
                include_removed=include_removed,
                field_name=field_name,
                search_string=search_string,
                filter_by=filter_by,
                filter_operator=filter_operator,
                page_size=page_size,
            )
        )
        return header_values

    def get_paired_codelists(self, codelist_uid) -> CTCodelistPaired:
        ct_cl_root = CTCodelistRoot.nodes.filter(uid=codelist_uid).get_or_none()
        BusinessLogicException.raise_if(
            ct_cl_root is None,
            msg=f"There is no CTCodelistRoot identified by provided codelist_uid ({codelist_uid})",
        )
        codes_pair_root = ct_cl_root.has_paired_code_codelist.get_or_none()
        names_pair_root = ct_cl_root.has_paired_name_codelist.get_or_none()

        attributes_service = CTCodelistAttributesService()
        names_service = CTCodelistNameService()

        if codes_pair_root is not None:
            codes_attrs = attributes_service.get_by_uid(codes_pair_root.uid)
            codes_name = names_service.get_by_uid(codes_pair_root.uid)
        else:
            codes_attrs = None
            codes_name = None

        if names_pair_root is not None:
            names_attrs = attributes_service.get_by_uid(names_pair_root.uid)
            names_name = names_service.get_by_uid(names_pair_root.uid)
        else:
            names_attrs = None
            names_name = None

        return CTCodelistPaired.from_ct_codelists(
            paired_names_codelist_name=names_name,
            paired_names_codelist_attrs=names_attrs,
            paired_codes_codelist_name=codes_name,
            paired_codes_codelist_attrs=codes_attrs,
        )

    def update_paired_codelists(
        self, codelist_uid: str, paired_codelists: CTCodelistPairedInput
    ) -> CTCodelist:
        ct_cl_root = CTCodelistRoot.nodes.filter(uid=codelist_uid).get_or_none()
        BusinessLogicException.raise_if(
            ct_cl_root is None,
            msg=f"There is no CTCodelistRoot identified by provided codelist_uid ({codelist_uid})",
        )
        BusinessLogicException.raise_if(
            paired_codelists.paired_codes_codelist_uid is not None
            and paired_codelists.paired_names_codelist_uid is not None,
            msg=f"Not allowed to link both paired codes and names codelists to the same codelist ({codelist_uid}).",
        )

        if paired_codelists.paired_codes_codelist_uid:
            BusinessLogicException.raise_if_not(
                self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_uid(
                    paired_codelists.paired_codes_codelist_uid
                ),
                msg=f"The given paired codes codelist with UID '{paired_codelists.paired_codes_codelist_uid}' doesn't exist.",
            )
            self._repos.ct_codelist_aggregated_repository.merge_link_to_codes_codelist(
                codelist_uid, paired_codelists.paired_codes_codelist_uid
            )
        elif (
            paired_codelists.paired_codes_codelist_uid is None
            and "paired_codes_codelist_uid" in paired_codelists.model_fields_set
        ):
            self._repos.ct_codelist_aggregated_repository.remove_link_to_codes_codelist(
                codelist_uid
            )

        if paired_codelists.paired_names_codelist_uid:
            BusinessLogicException.raise_if_not(
                self._repos.ct_codelist_attribute_repository.codelist_specific_exists_by_uid(
                    paired_codelists.paired_names_codelist_uid
                ),
                msg=f"The given paired names codelist with UID '{paired_codelists.paired_names_codelist_uid}' doesn't exist.",
            )
            self._repos.ct_codelist_aggregated_repository.merge_link_to_codes_codelist(
                paired_codelists.paired_names_codelist_uid, codelist_uid
            )
        elif (
            paired_codelists.paired_names_codelist_uid is None
            and "paired_names_codelist_uid" in paired_codelists.model_fields_set
        ):
            self._repos.ct_codelist_aggregated_repository.remove_link_from_codes_codelist(
                codelist_uid
            )

        return self.get_paired_codelists(codelist_uid)

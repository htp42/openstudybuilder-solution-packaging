from typing import Any

from neomodel import db

from clinical_mdr_api.models.controlled_terminologies.ct_term import (
    SimpleCodelistTermModel,
)
from clinical_mdr_api.models.study_selections.study_selection import (
    StudySelectionDataSupplier,
    StudySelectionDataSupplierInput,
    StudySelectionDataSupplierNewOrder,
)
from clinical_mdr_api.repositories._utils import FilterOperator
from clinical_mdr_api.services._meta_repository import MetaRepository
from clinical_mdr_api.services._utils import (
    ensure_transaction,
    service_level_generic_filtering,
    service_level_generic_header_filtering,
)
from clinical_mdr_api.utils import db_result_to_list
from common.auth.user import user
from common.config import settings
from common.exceptions import BusinessLogicException, NotFoundException
from common.utils import convert_to_datetime


class StudyDataSupplierSelectionService:
    _repos: MetaRepository

    def __init__(self):
        self._repos = MetaRepository()
        self.author = user().id()

    @ensure_transaction(db)
    def get_all_selections(
        self,
        study_uid: str | None = None,
        sort_by: dict[str, bool] | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
        study_value_version: str | None = None,
    ):
        db_rs = self._repos.study_data_supplier_repository.retrieve(
            study_uid, study_value_version=study_value_version
        )

        items = []

        for rs in db_result_to_list(db_rs):
            change_type = ""
            for action in rs["change_type"]:
                if "StudyAction" not in action:
                    change_type = action
            rs["change_type"] = change_type
            rs["start_date"] = convert_to_datetime(rs["start_date"])
            rs["end_date"] = convert_to_datetime(rs["end_date"])
            rs["study_data_supplier_type"] = (
                SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                    rs["study_data_supplier_type_uid"],
                    settings.data_supplier_type_cl_submval,
                    find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
                    at_specific_date_time=convert_to_datetime(
                        rs["study_effective_date"]
                    ),
                )
            )
            items.append(StudySelectionDataSupplier(**rs))

        return service_level_generic_filtering(
            items=items,
            filter_by=filter_by,
            filter_operator=filter_operator,
            sort_by=sort_by,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
        )

    @ensure_transaction(db)
    def get_selection(self, study_uid: str, study_data_supplier_uid: str):
        db_rs = self._repos.study_data_supplier_repository.retrieve(
            study_uid, study_data_supplier_uid
        )

        try:
            rs = db_result_to_list(db_rs)[0]
        except IndexError as exc:
            raise NotFoundException(
                "Study Data Supplier", study_data_supplier_uid
            ) from exc

        change_type = ""
        for action in rs["change_type"]:
            if "StudyAction" not in action:
                change_type = action
        rs["change_type"] = change_type
        rs["start_date"] = convert_to_datetime(rs["start_date"])
        rs["end_date"] = convert_to_datetime(rs["end_date"])
        rs["study_data_supplier_type"] = (
            SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                rs["study_data_supplier_type_uid"],
                settings.data_supplier_type_cl_submval,
                find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
                at_specific_date_time=convert_to_datetime(rs["study_effective_date"]),
            )
        )

        return StudySelectionDataSupplier(**rs)

    @ensure_transaction(db)
    def get_audit_trail(
        self, study_uid: str, study_data_supplier_uid: str | None = None
    ):
        db_rs = self._repos.study_data_supplier_repository.retrieve_audit_trail(
            study_uid, study_data_supplier_uid
        )

        items = []

        for rs in db_result_to_list(db_rs):
            rs["study_uid"] = study_uid
            change_type = ""
            for action in rs["change_type"]:
                if "StudyAction" not in action:
                    change_type = action
            rs["change_type"] = change_type
            rs["start_date"] = convert_to_datetime(rs["start_date"])
            rs["end_date"] = convert_to_datetime(rs["end_date"])
            rs["study_data_supplier_type"] = (
                SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                    rs["study_data_supplier_type_uid"],
                    settings.data_supplier_type_cl_submval,
                    find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
                    at_specific_date_time=convert_to_datetime(
                        rs["study_effective_date"]
                    ),
                )
            )
            items.append(StudySelectionDataSupplier(**rs))

        return items

    @ensure_transaction(db)
    def get_distinct_values_for_header(
        self,
        field_name: str,
        study_uid: str | None = None,
        search_string: str = "",
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        page_size: int = 10,
        study_value_version: str | None = None,
    ):
        db_rs = self._repos.study_data_supplier_repository.retrieve(
            study_uid, study_value_version=study_value_version
        )

        items = []

        for rs in db_result_to_list(db_rs):
            change_type = ""
            for action in rs["change_type"]:
                if "StudyAction" not in action:
                    change_type = action
            rs["change_type"] = change_type
            rs["start_date"] = convert_to_datetime(rs["start_date"])
            rs["end_date"] = convert_to_datetime(rs["end_date"])
            rs["study_data_supplier_type"] = (
                SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                    rs["study_data_supplier_type_uid"],
                    settings.data_supplier_type_cl_submval,
                    find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
                    at_specific_date_time=convert_to_datetime(
                        rs["study_effective_date"]
                    ),
                )
            )
            items.append(StudySelectionDataSupplier(**rs))

        return service_level_generic_header_filtering(
            items=items,
            field_name=field_name,
            search_string=search_string,
            filter_by=filter_by,
            filter_operator=filter_operator,
            page_size=page_size,
        )

    @ensure_transaction(db)
    def make_selection(
        self,
        study_uid: str,
        selection_input: StudySelectionDataSupplierInput,
    ):
        if not self._repos.data_supplier_repository.exists_by(
            "uid", selection_input.data_supplier_uid, True
        ):
            raise BusinessLogicException(
                msg=f"DataSupplier with UID '{selection_input.data_supplier_uid}' doesn't exist."
            )

        db_rs = self._repos.study_data_supplier_repository.create(
            study_uid, selection_input
        )

        study_data_supplier_type_uid = (
            selection_input.study_data_supplier_type_uid or db_rs[0][0][8]
        )
        self._repos.study_data_supplier_repository.connect_data_supplier_type(
            study_uid, study_data_supplier_type_uid, db_rs[0][0][0]
        )

        rs = db_result_to_list(db_rs)[0]

        change_type = ""
        for action in rs["change_type"]:
            if "StudyAction" not in action:
                change_type = action
        rs["change_type"] = change_type
        rs["start_date"] = convert_to_datetime(rs["start_date"])
        rs["study_data_supplier_type"] = (
            SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                study_data_supplier_type_uid,
                settings.data_supplier_type_cl_submval,
                find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
            )
        )

        return StudySelectionDataSupplier(**rs)

    @ensure_transaction(db)
    def update_selection(
        self,
        study_uid: str,
        study_data_supplier_uid: str,
        selection_input: StudySelectionDataSupplierInput,
    ):
        if not self._repos.data_supplier_repository.exists_by(
            "uid", selection_input.data_supplier_uid, True
        ):
            raise BusinessLogicException(
                msg=f"DataSupplier with UID '{selection_input.data_supplier_uid}' doesn't exist."
            )

        db_rs = self._repos.study_data_supplier_repository.update(
            study_uid, study_data_supplier_uid, selection_input
        )

        try:
            rs = db_result_to_list(db_rs)[0]
        except IndexError as exc:
            raise NotFoundException(
                msg=f"There is no selection between the Study Data Supplier with UID '{study_data_supplier_uid}' and the study."
            ) from exc

        self._repos.study_data_supplier_repository.connect_data_supplier_type(
            study_uid,
            selection_input.study_data_supplier_type_uid,
            study_data_supplier_uid,
        )

        change_type = ""
        for action in rs["change_type"]:
            if "StudyAction" not in action:
                change_type = action
        rs["change_type"] = change_type
        rs["start_date"] = convert_to_datetime(rs["start_date"])
        rs["study_data_supplier_type"] = (
            SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                selection_input.study_data_supplier_type_uid,
                settings.data_supplier_type_cl_submval,
                find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
                at_specific_date_time=convert_to_datetime(rs["study_effective_date"]),
            )
        )

        return StudySelectionDataSupplier(**rs)

    @ensure_transaction(db)
    def delete_selection(self, study_uid: str, study_data_supplier_uid: str):
        return self._repos.study_data_supplier_repository.delete(
            study_uid, study_data_supplier_uid
        )

    @ensure_transaction(db)
    def set_order(
        self,
        study_uid: str,
        study_data_supplier_uid: str,
        order: StudySelectionDataSupplierNewOrder,
    ):
        db_rs = self._repos.study_data_supplier_repository.set_order(
            study_uid, study_data_supplier_uid, order.new_order
        )

        try:
            rs = db_result_to_list(db_rs)[0]
        except IndexError as exc:
            raise NotFoundException(
                msg=f"There is no selection between the Study Data Supplier with UID '{study_data_supplier_uid}' and the study."
            ) from exc

        change_type = ""
        for action in rs["change_type"]:
            if "StudyAction" not in action:
                change_type = action
        rs["change_type"] = change_type
        rs["start_date"] = convert_to_datetime(rs["start_date"])
        rs["study_data_supplier_type"] = (
            SimpleCodelistTermModel.from_term_uid_and_codelist_submval(
                rs["study_data_supplier_type_uid"],
                settings.data_supplier_type_cl_submval,
                find_codelist_term_by_uid_and_submission_value=self._repos.ct_codelist_name_repository.get_codelist_term_by_uid_and_submval,
            )
        )

        return StudySelectionDataSupplier(**rs)

from dataclasses import dataclass
from typing import Callable, Self

from clinical_mdr_api.domains.concepts.concept_base import ConceptVO
from clinical_mdr_api.domains.concepts.odms.odm_ar_base import OdmARBase
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmAliasModel,
    OdmDescriptionModel,
)
from common.exceptions import AlreadyExistsException
from common.utils import booltostr


@dataclass(frozen=True)
class OdmFormVO(ConceptVO):
    oid: str | None
    repeating: str | int | None
    sdtm_version: str | None
    descriptions: list[OdmDescriptionModel]
    aliases: list[OdmAliasModel]
    item_group_uids: list[str]
    vendor_attribute_uids: list[str]
    vendor_element_uids: list[str]
    vendor_element_attribute_uids: list[str]

    @classmethod
    def from_repository_values(
        cls,
        oid: str | None,
        name: str,
        sdtm_version: str | None,
        repeating: str | int | None,
        descriptions: list[OdmDescriptionModel],
        aliases: list[OdmAliasModel],
        item_group_uids: list[str],
        vendor_element_uids: list[str],
        vendor_attribute_uids: list[str],
        vendor_element_attribute_uids: list[str],
    ) -> Self:
        return cls(
            oid=oid,
            name=name,
            sdtm_version=sdtm_version,
            repeating=repeating,
            descriptions=descriptions,
            aliases=aliases,
            item_group_uids=item_group_uids,
            vendor_element_uids=vendor_element_uids,
            vendor_attribute_uids=vendor_attribute_uids,
            vendor_element_attribute_uids=vendor_element_attribute_uids,
            name_sentence_case=None,
            definition=None,
            abbreviation=None,
            is_template_parameter=False,
        )

    def validate(
        self,
        odm_object_exists_callback: Callable,
        odm_uid: str | None = None,
        library_name: str | None = None,
    ) -> None:
        data = {
            "library_name": library_name,
            "name": self.name,
            "oid": self.oid,
            "sdtm_version": self.sdtm_version,
            "repeating": bool(self.repeating),
        }
        if uids := odm_object_exists_callback(**data):
            if uids[0] != odm_uid:
                raise AlreadyExistsException(
                    msg=f"ODM Form already exists with UID ({uids[0]}) and data {data}"
                )


@dataclass
class OdmFormAR(OdmARBase):
    _concept_vo: OdmFormVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmFormVO:
        return self._concept_vo

    @concept_vo.setter
    def concept_vo(self, value: OdmFormVO) -> None:
        self._concept_vo = value

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmFormVO,
        library: LibraryVO,
        item_metadata: LibraryItemMetadataVO,
    ) -> Self:
        return cls(
            _uid=uid,
            _concept_vo=concept_vo,
            _library=library,
            _item_metadata=item_metadata,
        )

    @classmethod
    def from_input_values(
        cls,
        author_id: str,
        concept_vo: OdmFormVO,
        library: LibraryVO,
        generate_uid_callback: Callable[[], str] = lambda: "",
        odm_object_exists_callback: Callable = lambda _: True,
    ) -> Self:
        item_metadata = LibraryItemMetadataVO.get_initial_item_metadata(
            author_id=author_id
        )

        concept_vo.validate(
            odm_object_exists_callback=odm_object_exists_callback,
            library_name=library.name,
        )

        return cls(
            _uid=generate_uid_callback(),
            _item_metadata=item_metadata,
            _library=library,
            _concept_vo=concept_vo,
        )

    def edit_draft(
        self,
        author_id: str,
        change_description: str,
        concept_vo: OdmFormVO,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_object_exists_callback: Callable = lambda _: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            odm_object_exists_callback=odm_object_exists_callback,
            odm_uid=self.uid,
        )

        if self._concept_vo != concept_vo:
            super()._edit_draft(
                change_description=change_description, author_id=author_id
            )
            self._concept_vo = concept_vo


@dataclass(frozen=True)
class OdmFormRefVO:
    uid: str
    name: str
    version: str
    study_event_uid: str
    order_number: int
    mandatory: str
    locked: str
    collection_exception_condition_oid: str

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        name: str,
        version: str,
        study_event_uid: str,
        order_number: int,
        mandatory: bool,
        locked: bool,
        collection_exception_condition_oid: str,
    ) -> Self:
        return cls(
            uid=uid,
            name=name,
            version=version,
            study_event_uid=study_event_uid,
            order_number=order_number,
            mandatory=booltostr(mandatory),
            locked=booltostr(locked),
            collection_exception_condition_oid=collection_exception_condition_oid,
        )

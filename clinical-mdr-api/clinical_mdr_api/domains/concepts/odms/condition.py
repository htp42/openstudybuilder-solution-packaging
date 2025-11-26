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
    OdmFormalExpressionModel,
)
from common.exceptions import AlreadyExistsException


@dataclass(frozen=True)
class OdmConditionVO(ConceptVO):
    oid: str | None
    formal_expressions: list[OdmFormalExpressionModel]
    descriptions: list[OdmDescriptionModel]
    aliases: list[OdmAliasModel]

    @classmethod
    def from_repository_values(
        cls,
        oid: str | None,
        name: str,
        formal_expressions: list[OdmFormalExpressionModel],
        descriptions: list[OdmDescriptionModel],
        aliases: list[OdmAliasModel],
    ) -> Self:
        return cls(
            oid=oid,
            name=name,
            formal_expressions=formal_expressions,
            descriptions=descriptions,
            aliases=aliases,
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
        }
        if uids := odm_object_exists_callback(**data):
            if uids[0] != odm_uid:
                raise AlreadyExistsException(
                    msg=f"ODM Condition already exists with UID ({uids[0]}) and data {data}"
                )


@dataclass
class OdmConditionAR(OdmARBase):
    _concept_vo: OdmConditionVO

    @property
    def name(self) -> str:
        return self._concept_vo.name

    @property
    def concept_vo(self) -> OdmConditionVO:
        return self._concept_vo

    @concept_vo.setter
    def concept_vo(self, value: OdmConditionVO) -> None:
        self._concept_vo = value

    @classmethod
    def from_repository_values(
        cls,
        uid: str,
        concept_vo: OdmConditionVO,
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
        concept_vo: OdmConditionVO,
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
        concept_vo: OdmConditionVO,
        concept_exists_by_callback: Callable[
            [str, str, bool], bool
        ] = lambda x, y, z: True,
        odm_object_exists_callback: Callable = lambda _: True,
    ) -> None:
        """
        Creates a new draft version for the object.
        """
        concept_vo.validate(
            odm_object_exists_callback=odm_object_exists_callback, odm_uid=self.uid
        )

        super()._edit_draft(change_description=change_description, author_id=author_id)
        self._concept_vo = concept_vo

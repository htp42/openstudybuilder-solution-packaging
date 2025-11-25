from typing import Annotated, Callable, Self, overload

from pydantic import Field, field_validator

from clinical_mdr_api.descriptions.general import CHANGES_FIELD_DESC
from clinical_mdr_api.domains.concepts.odms.form import OdmFormAR, OdmFormRefVO
from clinical_mdr_api.domains.concepts.odms.item_group import OdmItemGroupRefVO
from clinical_mdr_api.domains.concepts.odms.vendor_attribute import (
    OdmVendorAttributeAR,
    OdmVendorAttributeRelationVO,
    OdmVendorElementAttributeRelationVO,
)
from clinical_mdr_api.domains.concepts.odms.vendor_element import (
    OdmVendorElementRelationVO,
)
from clinical_mdr_api.domains.concepts.utils import RelationType
from clinical_mdr_api.models.concepts.concept import (
    ConceptModel,
    ConceptPatchInput,
    ConceptPostInput,
)
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmAliasModel,
    OdmDescriptionModel,
    OdmRefVendorPostInput,
)
from clinical_mdr_api.models.concepts.odms.odm_item_group import OdmItemGroupRefModel
from clinical_mdr_api.models.concepts.odms.odm_vendor_attribute import (
    OdmVendorAttributeRelationModel,
    OdmVendorElementAttributeRelationModel,
)
from clinical_mdr_api.models.concepts.odms.odm_vendor_element import (
    OdmVendorElementRelationModel,
)
from clinical_mdr_api.models.utils import BaseModel, PostInputModel
from clinical_mdr_api.models.validators import has_english_description
from common.config import settings
from common.utils import booltostr


class OdmForm(ConceptModel):
    oid: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    repeating: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    sdtm_version: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = (
        None
    )
    descriptions: Annotated[list[OdmDescriptionModel], Field()]
    aliases: Annotated[list[OdmAliasModel], Field()]
    item_groups: Annotated[list[OdmItemGroupRefModel], Field()]
    vendor_elements: Annotated[list[OdmVendorElementRelationModel], Field()]
    vendor_attributes: Annotated[list[OdmVendorAttributeRelationModel], Field()]
    vendor_element_attributes: Annotated[
        list[OdmVendorElementAttributeRelationModel], Field()
    ]
    possible_actions: Annotated[list[str], Field()]

    @classmethod
    def from_odm_form_ar(
        cls,
        odm_form_ar: OdmFormAR,
        find_odm_item_group_by_uid_with_form_relation: Callable[
            [str, str, str], OdmItemGroupRefVO
        ],
        find_odm_vendor_attribute_by_uid: Callable[[str], OdmVendorAttributeAR | None],
        find_odm_vendor_element_by_uid_with_odm_element_relation: Callable[
            [str, str, str, RelationType], OdmVendorElementRelationVO
        ],
        find_odm_vendor_attribute_by_uid_with_odm_element_relation: Callable[
            [str, str, str, RelationType, bool],
            OdmVendorAttributeRelationVO | OdmVendorElementAttributeRelationVO,
        ],
    ) -> Self:
        return cls(
            uid=odm_form_ar._uid,
            oid=odm_form_ar.concept_vo.oid,
            name=odm_form_ar.name,
            sdtm_version=odm_form_ar.concept_vo.sdtm_version,
            repeating=booltostr(odm_form_ar.concept_vo.repeating),
            library_name=odm_form_ar.library.name,
            start_date=odm_form_ar.item_metadata.start_date,
            end_date=odm_form_ar.item_metadata.end_date,
            status=odm_form_ar.item_metadata.status.value,
            version=odm_form_ar.item_metadata.version,
            change_description=odm_form_ar.item_metadata.change_description,
            author_username=odm_form_ar.item_metadata.author_username,
            descriptions=sorted(
                odm_form_ar.concept_vo.descriptions, key=lambda item: item.name
            ),
            aliases=sorted(odm_form_ar.concept_vo.aliases, key=lambda item: item.name),
            item_groups=sorted(
                [
                    OdmItemGroupRefModel.from_odm_item_group_uid(
                        uid=item_group_uid,
                        form_uid=odm_form_ar._uid,
                        form_version=odm_form_ar.item_metadata.version,
                        find_odm_item_group_by_uid_with_form_relation=find_odm_item_group_by_uid_with_form_relation,
                        find_odm_vendor_attribute_by_uid=find_odm_vendor_attribute_by_uid,
                    )
                    for item_group_uid in odm_form_ar.concept_vo.item_group_uids
                ],
                key=lambda item: item.order_number or "",
            ),
            vendor_elements=sorted(
                [
                    OdmVendorElementRelationModel.from_uid(
                        uid=vendor_element_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_version=odm_form_ar.item_metadata.version,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_element_by_uid_with_odm_element_relation,
                    )
                    for vendor_element_uid in odm_form_ar.concept_vo.vendor_element_uids
                ],
                key=lambda item: item.name or "",
            ),
            vendor_attributes=sorted(
                [
                    OdmVendorAttributeRelationModel.from_uid(
                        uid=vendor_attribute_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_version=odm_form_ar.item_metadata.version,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_attribute_by_uid_with_odm_element_relation,  # type: ignore[arg-type]
                        vendor_element_attribute=False,
                    )
                    for vendor_attribute_uid in odm_form_ar.concept_vo.vendor_attribute_uids
                ],
                key=lambda item: item.name or "",
            ),
            vendor_element_attributes=sorted(
                [
                    OdmVendorElementAttributeRelationModel.from_uid(
                        uid=vendor_element_attribute_uid,
                        odm_element_uid=odm_form_ar._uid,
                        odm_element_version=odm_form_ar.item_metadata.version,
                        odm_element_type=RelationType.FORM,
                        find_by_uid_with_odm_element_relation=find_odm_vendor_attribute_by_uid_with_odm_element_relation,  # type: ignore[arg-type]
                    )
                    for vendor_element_attribute_uid in odm_form_ar.concept_vo.vendor_element_attribute_uids
                ],
                key=lambda item: item.name or "",
            ),
            possible_actions=sorted(
                [_.value for _ in odm_form_ar.get_possible_actions()]
            ),
        )


class OdmFormRefModel(BaseModel):
    @overload
    @classmethod
    def from_odm_form_uid(
        cls,
        uid: str,
        study_event_uid: str,
        study_event_version: str,
        find_odm_form_by_uid_with_study_event_relation: Callable[
            [str, str, str], OdmFormRefVO
        ],
    ) -> Self: ...
    @overload
    @classmethod
    def from_odm_form_uid(
        cls,
        uid: None,
        study_event_uid: str,
        study_event_version: str,
        find_odm_form_by_uid_with_study_event_relation: Callable[
            [str, str, str], OdmFormRefVO
        ],
    ) -> None: ...
    @classmethod
    def from_odm_form_uid(
        cls,
        uid: str | None,
        study_event_uid: str,
        study_event_version: str,
        find_odm_form_by_uid_with_study_event_relation: Callable[
            [str, str, str], OdmFormRefVO
        ],
    ) -> Self | None:
        odm_form_ref_model = None

        if uid is not None:
            odm_form_ref_vo = find_odm_form_by_uid_with_study_event_relation(
                uid, study_event_uid, study_event_version
            )
            if odm_form_ref_vo is not None:
                odm_form_ref_model = cls(
                    uid=uid,
                    name=odm_form_ref_vo.name,
                    version=odm_form_ref_vo.version,
                    order_number=odm_form_ref_vo.order_number,
                    mandatory=odm_form_ref_vo.mandatory,
                    locked=odm_form_ref_vo.locked,
                    collection_exception_condition_oid=odm_form_ref_vo.collection_exception_condition_oid,
                )
            else:
                odm_form_ref_model = cls(
                    uid=uid,
                    name=None,
                    version=None,
                    order_number=None,
                    mandatory=None,
                    locked=None,
                    collection_exception_condition_oid=None,
                )
        return odm_form_ref_model

    uid: Annotated[str, Field()]
    name: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    version: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    order_number: Annotated[int | None, Field(json_schema_extra={"nullable": True})] = (
        None
    )
    mandatory: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    locked: Annotated[str | None, Field(json_schema_extra={"nullable": True})] = None
    collection_exception_condition_oid: Annotated[
        str | None, Field(json_schema_extra={"nullable": True})
    ] = None


class OdmFormPostInput(ConceptPostInput):
    oid: Annotated[str | None, Field(min_length=1)] = None
    sdtm_version: Annotated[str | None, Field()] = None
    repeating: Annotated[str, Field(min_length=1)]
    descriptions: Annotated[list[OdmDescriptionModel], Field()]
    aliases: list[OdmAliasModel] = Field(default_factory=list)

    _english_description_validator = field_validator("descriptions")(
        has_english_description
    )


class OdmFormPatchInput(ConceptPatchInput):
    name: Annotated[str, Field(min_length=1)]
    oid: Annotated[str | None, Field(min_length=1)]
    sdtm_version: Annotated[str | None, Field()]
    repeating: Annotated[str | None, Field()]
    descriptions: Annotated[list[OdmDescriptionModel], Field()]
    aliases: list[OdmAliasModel] = Field(default_factory=list)

    _english_description_validator = field_validator("descriptions")(
        has_english_description
    )


class OdmFormItemGroupPostInput(PostInputModel):
    uid: Annotated[str, Field(min_length=1)]
    order_number: Annotated[int, Field(lt=settings.max_int_neo4j)]
    mandatory: Annotated[str, Field(min_length=1)]
    collection_exception_condition_oid: Annotated[str | None, Field()] = None
    vendor: Annotated[OdmRefVendorPostInput, Field()]


class OdmFormVersion(OdmForm):
    """
    Class for storing OdmForm and calculation of differences
    """

    changes: list[str] = Field(description=CHANGES_FIELD_DESC, default_factory=list)

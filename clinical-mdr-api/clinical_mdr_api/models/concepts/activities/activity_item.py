from typing import Annotated

from pydantic import ConfigDict, Field

from clinical_mdr_api.models.utils import BaseModel, PostInputModel


class CompactActivityItemClassForActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str, Field(json_schema_extra={"source": "has_activity_item_class.uid"})
    ]
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_activity_item_class.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class CompactCTTerm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_ct_term.has_selected_term.uid",
                "nullable": True,
            }
        ),
    ] = None
    codelist_uid: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_ct_term.has_selected_codelist.uid",
                "nullable": True,
            }
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_ct_term.has_selected_term.has_name_root.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None
    submission_value: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_ct_term.has_selected_term.has_term_root.submission_value",
                "nullable": True,
            },
        ),
    ] = None


class CompactUnitDefinition(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: Annotated[
        str | None,
        Field(
            json_schema_extra={"source": "has_unit_definition.uid", "nullable": True}
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_unit_definition.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None
    dimension_name: Annotated[
        str | None,
        Field(
            json_schema_extra={
                "source": "has_unit_definition.has_latest_value.has_ct_dimension.has_name_root.has_latest_value.name",
                "nullable": True,
            },
        ),
    ] = None


class ActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_item_class: Annotated[CompactActivityItemClassForActivityItem, Field()]
    ct_terms: list[CompactCTTerm] = Field(default_factory=list)
    unit_definitions: list[CompactUnitDefinition] = Field(default_factory=list)
    is_adam_param_specific: Annotated[bool, Field()]
    text_value: Annotated[str | None, Field()] = None


class ActivityItemCreateInput(PostInputModel):
    class CTTermsInput(PostInputModel):
        term_uid: Annotated[str, Field(min_length=1)]
        codelist_uid: Annotated[str, Field(min_length=1)]

    activity_item_class_uid: Annotated[str, Field(min_length=1)]
    ct_terms: Annotated[list[CTTermsInput], Field()]
    unit_definition_uids: Annotated[list[str], Field()]
    is_adam_param_specific: Annotated[bool, Field()]
    text_value: Annotated[str | None, Field()] = None

from typing import Any

from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.odms.odm_generic_repository import (
    OdmGenericRepository,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)
from clinical_mdr_api.domain_repositories.models.odm import (
    OdmConditionRoot,
    OdmConditionValue,
)
from clinical_mdr_api.domains.concepts.odms.condition import (
    OdmConditionAR,
    OdmConditionVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmAliasModel,
    OdmDescriptionModel,
    OdmFormalExpressionModel,
)
from clinical_mdr_api.models.concepts.odms.odm_condition import OdmCondition
from common.utils import convert_to_datetime


class ConditionRepository(OdmGenericRepository[OdmConditionAR]):
    root_class = OdmConditionRoot
    value_class = OdmConditionValue
    return_model = OdmCondition

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        **_kwargs,
    ) -> OdmConditionAR:
        return OdmConditionAR.from_repository_values(
            uid=root.uid,
            concept_vo=OdmConditionVO.from_repository_values(
                oid=value.oid,
                name=value.name,
                formal_expressions=[
                    OdmFormalExpressionModel(
                        context=formal_expression_value.context,
                        expression=formal_expression_value.expression,
                    )
                    for formal_expression_value in value.has_formal_expression.all()
                ],
                descriptions=[
                    OdmDescriptionModel(
                        name=description_value.name,
                        language=description_value.language,
                        description=description_value.description,
                        instruction=description_value.instruction,
                        sponsor_instruction=description_value.sponsor_instruction,
                    )
                    for description_value in value.has_description.all()
                ],
                aliases=[
                    OdmAliasModel(name=alias_value.name, context=alias_value.context)
                    for alias_value in value.has_alias.all()
                ],
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=lambda _: library.is_editable,
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict[str, Any]
    ) -> OdmConditionAR:
        major, minor = input_dict["version"].split(".")
        odm_condition_ar = OdmConditionAR.from_repository_values(
            uid=input_dict["uid"],
            concept_vo=OdmConditionVO.from_repository_values(
                oid=input_dict["oid"],
                name=input_dict["name"],
                formal_expressions=[
                    OdmFormalExpressionModel(
                        context=formal_expression["context"],
                        expression=formal_expression["expression"],
                    )
                    for formal_expression in input_dict["formal_expressions"]
                ],
                descriptions=[
                    OdmDescriptionModel(
                        name=description["name"],
                        language=description.get("language", None),
                        description=description.get("description", None),
                        instruction=description.get("instruction", None),
                        sponsor_instruction=description.get(
                            "sponsor_instruction", None
                        ),
                    )
                    for description in input_dict["descriptions"]
                ],
                aliases=[
                    OdmAliasModel(name=alias["name"], context=alias["context"])
                    for alias in input_dict["aliases"]
                ],
            ),
            library=LibraryVO.from_input_values_2(
                library_name=input_dict["library_name"],
                is_library_editable_callback=(
                    lambda _: input_dict["is_library_editable"]
                ),
            ),
            item_metadata=LibraryItemMetadataVO.from_repository_values(
                change_description=input_dict["change_description"],
                status=LibraryItemStatus(input_dict.get("status")),
                author_id=input_dict["author_id"],
                author_username=input_dict.get("author_username"),
                start_date=convert_to_datetime(value=input_dict["start_date"]),
                end_date=None,
                major_version=int(major),
                minor_version=int(minor),
            ),
        )

        return odm_condition_ar

    def specific_alias_clause(self, **kwargs) -> str:
        return """
WITH *,
concept_value.oid AS oid,

[(concept_value)-[:HAS_FORMAL_EXPRESSION]->(fev:OdmFormalExpression) | {context: fev.context, expression: fev.expression}] AS formal_expressions,

[(concept_value)-[:HAS_DESCRIPTION]->(dv:OdmDescription) |
{name: dv.name, language: dv.language, description: dv.description, instruction: dv.instruction, sponsor_instruction: dv.sponsor_instruction}] AS descriptions,

[(concept_value)-[:HAS_ALIAS]->(av:OdmAlias) | {name: av.name, context: av.context}] AS aliases
"""

    def _get_or_create_value(
        self, root: VersionRoot, ar: OdmConditionAR, force_new_value_node: bool = False
    ) -> VersionValue:
        new_value = super()._get_or_create_value(root, ar, force_new_value_node)

        self.connect_aliases(ar.concept_vo.aliases, new_value)
        self.connect_descriptions(ar.concept_vo.descriptions, new_value)
        self.connect_formal_expressions(ar.concept_vo.formal_expressions, new_value)

        return new_value

    def _create_new_value_node(self, ar: OdmConditionAR) -> OdmConditionValue:
        value_node = super()._create_new_value_node(ar=ar)

        value_node.save()

        value_node.oid = ar.concept_vo.oid

        return value_node

    def _has_data_changed(self, ar: OdmConditionAR, value: OdmConditionValue) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)

        formal_expression_nodes = {
            OdmFormalExpressionModel(
                context=formal_expression_node.context,
                expression=formal_expression_node.expression,
            )
            for formal_expression_node in value.has_formal_expression.all()
        }
        description_nodes = {
            OdmDescriptionModel(
                name=description_node.name,
                language=description_node.language,
                description=description_node.description,
                instruction=description_node.instruction,
                sponsor_instruction=description_node.sponsor_instruction,
            )
            for description_node in value.has_description.all()
        }
        alias_nodes = {
            OdmAliasModel(name=alias_node.name, context=alias_node.context)
            for alias_node in value.has_alias.all()
        }

        are_rels_changed = (
            set(ar.concept_vo.formal_expressions) != formal_expression_nodes
            or set(ar.concept_vo.descriptions) != description_nodes
            or set(ar.concept_vo.aliases) != alias_nodes
        )

        return (
            are_concept_properties_changed
            or are_rels_changed
            or ar.concept_vo.oid != value.oid
        )

    def set_all_collection_exception_condition_oid_properties_to_null(self, oid):
        db.cypher_query(
            """MATCH ()-[r:ITEM_GROUP_REF|ITEM_REF {collection_exception_condition_oid: $oid}]-()
                SET r.collection_exception_condition_oid = null""",
            {"oid": oid},
        )

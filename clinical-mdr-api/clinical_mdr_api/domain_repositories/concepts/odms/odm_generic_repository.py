from abc import ABC
from typing import Any

from neomodel import db

from clinical_mdr_api.domain_repositories._generic_repository_interface import (
    _AggregateRootType,
)
from clinical_mdr_api.domain_repositories.concepts.concept_generic_repository import (
    ConceptGenericRepository,
)
from clinical_mdr_api.domain_repositories.models.concepts import UnitDefinitionRoot
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import VersionValue
from clinical_mdr_api.domain_repositories.models.odm import (
    OdmAlias,
    OdmDescription,
    OdmFormalExpression,
    OdmFormRoot,
    OdmFormValue,
    OdmItemGroupRoot,
    OdmItemGroupValue,
    OdmItemRoot,
    OdmItemValue,
    OdmVendorAttributeRoot,
    OdmVendorAttributeValue,
    OdmVendorElementRoot,
    OdmVendorElementValue,
)
from clinical_mdr_api.domains.concepts.utils import RelationType
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmAliasModel,
    OdmDescriptionModel,
    OdmElementWithParentUid,
    OdmFormalExpressionModel,
)
from clinical_mdr_api.repositories._utils import (
    CypherQueryBuilder,
    FilterDict,
    FilterOperator,
    sb_clear_cache,
)
from common.exceptions import BusinessLogicException


class OdmGenericRepository(ConceptGenericRepository[_AggregateRootType], ABC):
    def find_all(
        self,
        library: str | None = None,
        sort_by: dict[str, bool] | None = None,
        page_number: int = 1,
        page_size: int = 0,
        filter_by: dict[str, dict[str, Any]] | None = None,
        filter_operator: FilterOperator = FilterOperator.AND,
        total_count: bool = False,
        return_all_versions: bool = False,
        **kwargs,
    ) -> tuple[list[_AggregateRootType], int]:
        """
        Method runs a cypher query to fetch all needed data to create objects of type AggregateRootType.
        In the case of the following repository it will be some Concept aggregates.

        It uses cypher instead of neomodel as neomodel approach triggered some performance issues, because it is needed
        to traverse many relationships to fetch all needed data and each traversal is separate database call when using
        neomodel.
        :param library:
        :param sort_by:
        :param page_number:
        :param page_size:
        :param filter_by:
        :param filter_operator:
        :param total_count:
        :param return_all_versions:
        :return GenericFilteringReturn[_AggregateRootType]:
        """
        match_clause = self.generic_match_clause(**kwargs)

        filter_statements, filter_query_parameters = self.create_query_filter_statement(
            library=library, **kwargs
        )
        match_clause += filter_statements

        alias_clause = (
            self.generic_alias_clause(**kwargs) + self.specific_alias_clause()
        )

        query = CypherQueryBuilder(
            match_clause=match_clause,
            alias_clause=alias_clause,
            sort_by=sort_by,
            page_number=page_number,
            page_size=page_size,
            filter_by=FilterDict.model_validate({"elements": filter_by}),
            filter_operator=filter_operator,
            total_count=total_count,
            return_model=self.return_model,
        )

        if kwargs.get("version", None) is not None:
            query.parameters.update({"requested_version": kwargs["version"]})

        query.parameters.update(filter_query_parameters)
        result_array, attributes_names = query.execute()
        extracted_items = self._retrieve_concepts_from_cypher_res(
            result_array, attributes_names
        )

        count_result, _ = db.cypher_query(
            query=query.count_query, params=query.parameters
        )
        total_amount = (
            count_result[0][0] if len(count_result) > 0 and total_count else 0
        )

        return extracted_items, total_amount

    @classmethod
    def _get_origin_and_relation_node(
        cls, uid: str, relation_uid: str | None, relationship_type: RelationType
    ):
        root_class_node = cls.root_class.nodes.get_or_none(uid=uid)
        value_class_node = root_class_node.has_latest_value.single()

        relation_mapping = {
            RelationType.ITEM_GROUP: (
                OdmItemGroupRoot,
                OdmItemGroupValue,
                "item_group_ref",
            ),
            RelationType.ITEM: (OdmItemRoot, OdmItemValue, "item_ref"),
            RelationType.FORM: (OdmFormRoot, OdmFormValue, "form_ref"),
            RelationType.TERM: (CTTermRoot, None, "has_codelist_term"),
            RelationType.UNIT_DEFINITION: (
                UnitDefinitionRoot,
                None,
                "has_unit_definition",
            ),
            RelationType.VENDOR_ELEMENT: (
                OdmVendorElementRoot,
                OdmVendorElementValue,
                "has_vendor_element",
            ),
            RelationType.VENDOR_ATTRIBUTE: (
                OdmVendorAttributeRoot,
                OdmVendorAttributeValue,
                "has_vendor_attribute",
            ),
            RelationType.VENDOR_ELEMENT_ATTRIBUTE: (
                OdmVendorAttributeRoot,
                OdmVendorAttributeValue,
                "has_vendor_element_attribute",
            ),
        }

        BusinessLogicException.raise_if(
            relationship_type not in relation_mapping, msg="Invalid relation type."
        )

        relation_node_root_cls, relation_node_value_cls, origin_label = (
            relation_mapping[relationship_type]
        )
        relation_node = relation_node_root_cls.nodes.get_or_none(uid=relation_uid)

        if relation_node is not None and relation_node_value_cls is not None:
            relation_node = relation_node.has_latest_value.single()

        BusinessLogicException.raise_if(
            not relation_node and relation_uid,
            msg=f"Object with UID '{relation_uid}' doesn't exist.",
        )

        return getattr(value_class_node, origin_label), relation_node

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def add_relation(
        self,
        uid: str,
        relation_uid: str,
        relationship_type: RelationType,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        origin, relation_node = self.__class__._get_origin_and_relation_node(
            uid, relation_uid, relationship_type
        )

        origin.disconnect(relation_node)

        if isinstance(parameters, dict):
            origin.connect(relation_node, parameters)
        else:
            origin.connect(relation_node)

    @sb_clear_cache(caches=["cache_store_item_by_uid"])
    def remove_relation(
        self,
        uid: str,
        relation_uid: str | None,
        relationship_type: RelationType,
        disconnect_all: bool = False,
    ) -> None:
        origin, relation_node = self.__class__._get_origin_and_relation_node(
            uid, relation_uid, relationship_type
        )

        if disconnect_all:
            origin.disconnect_all()
        else:
            origin.disconnect(relation_node)

    def has_active_relationships(
        self, uid: str, relationships: list[Any], all_exist: bool = False
    ) -> bool:
        """
        Checks if the node has active relationships.

        :param uid: The uid of the node to check relationships on.
        :param relationships: A list of relationship names to check the existence of.
        :param all_exist: If True, all provided relationships must exist on the node. If False, at least one of the provided relationships must exist.
        :return: Returns True, if the relationships exist, otherwise False.
        """
        root = self.root_class.nodes.get_or_none(uid=uid)
        value = root.has_latest_value.single()

        try:
            if not all_exist:
                for relationship in relationships:
                    if getattr(value, relationship):
                        return True

                return False
            for relationship in relationships:
                if not getattr(value, relationship):
                    return False

            return True
        except AttributeError as exc:
            raise AttributeError(
                f"{relationship} relationship was not found on {value}."
            ) from exc

    def get_active_relationships(
        self, uid: str, relationships: list[Any]
    ) -> dict[str, list[str]]:
        """
        Returns a key-pair value of target node's name and a list of uids of nodes connected to source node.

        :param uid: The uid of the source node to check relationships on.
        :param relationships: A list of relationship names to check the existence of.
        :return: Returns a dict.
        """
        root_node = self.root_class.nodes.get_or_none(uid=uid)
        source_node = root_node.has_latest_value.single()

        try:
            rs: dict[str, list[str]] = {}
            for relationship in relationships:
                rel = getattr(source_node, relationship)
                if rel:
                    for target_node in rel.all():
                        target_node_without_suffix = target_node.__label__.removesuffix(
                            "Value"
                        )
                        if target_node_without_suffix not in rs:
                            rs[target_node_without_suffix] = [
                                target_node.has_root.single().uid
                            ]
                        else:
                            rs[target_node_without_suffix].append(
                                target_node.has_root.single().uid
                            )
            return rs
        except AttributeError as exc:
            raise AttributeError(
                f"{relationship} relationship was not found on {source_node}."
            ) from exc

    def get_if_has_relationship(self, relationship: str):
        """
        Returns a list of ODM Element uid and name with their parent uids.
        """
        values = self.value_class.nodes.has(**{relationship: True})

        rs = []
        for value in values:
            parents = getattr(value, relationship).all()

            rs.append(
                OdmElementWithParentUid(
                    uid=value.has_root.single().uid,
                    name=value.name,
                    parent_uids=[parent.has_root.single().uid for parent in parents],
                )
            )

        return rs

    def odm_object_exists(
        self,
        library_name: str | None = None,
        sdtm_domain_uids: list[str] | None = None,
        term_uids: list[str] | None = None,
        unit_definition_uids: list[str] | None = None,
        codelist_uid: str | None = None,
        **value_attributes,
    ):
        """
        Checks whether an ODM object exists in the database based on various filtering criteria.
        This method constructs a Cypher query dynamically using the provided UID lists
        and additional value node attributes to search for matching objects in the database.

        Args:
            sdtm_domain_uids (list[str] | None): List of UIDs for SDTM Domains to match.
            term_uids (list[str] | None): List of UIDs for terms to match in CT Codelist Terms.
            unit_definition_uids (list[str] | None): List of UIDs for Unit Definitions to match.
            codelist_uid (str | None): UID for a CT Codelist to match.
            library_name (str | None): Name of the library to match.
            **value_attributes: Arbitrary key-value pairs to match against properties of the ODM object.

        Returns:
            list[str] | None: Returns a list of the UIDs of the matching ODM objects if it exist, otherwise returns `None`.
        """
        if not sdtm_domain_uids:
            sdtm_domain_uids = []
        if not term_uids:
            term_uids = []
        if not unit_definition_uids:
            unit_definition_uids = []

        query = f"""
            MATCH (root:{self.root_class.__label__})-[:LATEST]->(value:{self.value_class.__label__})
        """

        params: dict[str, Any] = {}

        if library_name:
            query += (
                " MATCH (:Library {name: $library_name})-[:CONTAINS_CONCEPT]->(root) "
            )
            params["library_name"] = library_name

        if sdtm_domain_uids:
            query += " MATCH (ct_term_root:CTTermRoot)<-[:HAS_SELECTED_TERM]-(:CTTermContext)<-[:HAS_SDTM_DOMAIN]-(value) "
            params["sdtm_domain_uids"] = sdtm_domain_uids

        if codelist_uid:
            query += " MATCH (:CTCodelistRoot {uid: $codelist_uid})<-[:HAS_CODELIST]-(value) "
            params["codelist_uid"] = codelist_uid

        if term_uids:
            params["term_uids"] = term_uids
            query += " MATCH (ct_term_root:CTTermRoot)<-[:HAS_SELECTED_TERM]-(:CTTermContext)<-[:HAS_CODELIST_TERM]-(value) "

        if unit_definition_uids:
            params["unit_definition_uids"] = unit_definition_uids
            query += " MATCH (unit_definition_root:UnitDefinitionRoot)<-[:HAS_UNIT_DEFINITION]-(value) "

        wheres = []
        for key, value in value_attributes.items():
            if value is not None:
                wheres.append(f"value.{key} = ${key}")

                params[key] = value
            else:
                wheres.append(f"value.{key} IS NULL")

        query += " WHERE " + " AND ".join(wheres)

        _where = []
        # pylint: disable=too-many-boolean-expressions
        if sdtm_domain_uids or term_uids or unit_definition_uids:
            query += " WITH root"

            if sdtm_domain_uids:
                query += ", apoc.coll.sort(COLLECT(DISTINCT ct_term_root.uid)) AS sdtm_domain_uids"
                _where.append("sdtm_domain_uids = apoc.coll.sort($sdtm_domain_uids)")

            if term_uids:
                query += (
                    ", apoc.coll.sort(COLLECT(DISTINCT ct_term_root.uid)) AS term_uids"
                )
                _where.append("term_uids = apoc.coll.sort($term_uids)")

            if unit_definition_uids:
                query += ", apoc.coll.sort(COLLECT(DISTINCT unit_definition_root.uid)) AS unit_definition_uids"
                _where.append(
                    "unit_definition_uids = apoc.coll.sort($unit_definition_uids)"
                )

        if _where:
            query += " WHERE " + " AND ".join(_where)

        query += " RETURN root.uid"

        rs = db.cypher_query(query=query, params=params)

        if rs[0]:
            return rs[0][0]

        return None

    def connect_descriptions(
        self, descriptions: list[OdmDescriptionModel], new_value: VersionValue
    ):
        new_value.has_description.disconnect_all()

        for description in descriptions:
            params: dict[str, Any] = {
                "name": description.name,
                "language": description.language,
            }
            for attr in ["description", "instruction", "sponsor_instruction"]:
                value = getattr(description, attr)
                if value is not None:
                    params[attr] = value
                else:
                    params[f"{attr}__isnull"] = True

            description_node = OdmDescription.nodes.get_or_none(**params)
            if not description_node:
                description_node = OdmDescription(
                    name=description.name,
                    language=description.language,
                    description=description.description,
                    instruction=description.instruction,
                    sponsor_instruction=description.sponsor_instruction,
                )
                description_node.save()
            new_value.has_description.connect(description_node)

    def connect_aliases(self, aliases: list[OdmAliasModel], new_value: VersionValue):
        new_value.has_alias.disconnect_all()

        for alias in aliases:
            alias_node = OdmAlias.nodes.get_or_none(
                name=alias.name, context=alias.context
            )
            if not alias_node:
                alias_node = OdmAlias(name=alias.name, context=alias.context)
                alias_node.save()
            new_value.has_alias.connect(alias_node)

    def connect_formal_expressions(
        self,
        formal_expressions: list[OdmFormalExpressionModel],
        new_value: VersionValue,
    ):
        new_value.has_formal_expression.disconnect_all()

        for formal_expression in formal_expressions:
            formal_expression_node = OdmFormalExpression.nodes.get_or_none(
                context=formal_expression.context,
                expression=formal_expression.expression,
            )
            if not formal_expression_node:
                formal_expression_node = OdmFormalExpression(
                    context=formal_expression.context,
                    expression=formal_expression.expression,
                )
                formal_expression_node.save()
            new_value.has_formal_expression.connect(formal_expression_node)

    def manage_vendor_relationships(
        self,
        current_latest: VersionValue,
        new_value: VersionValue,
        disconnect_old: bool,
    ) -> None:
        old_has_vendor_element_nodes = (
            current_latest.has_vendor_element.all() if current_latest else []
        )
        new_has_vendor_element_nodes = [
            old_vendor_element_root.has_latest_value.single()
            for old_has_vendor_element_node in old_has_vendor_element_nodes
            if (
                old_vendor_element_root := old_has_vendor_element_node.has_root.single()
            )
        ]

        old_has_vendor_attribute_nodes = (
            current_latest.has_vendor_attribute.all() if current_latest else []
        )
        new_has_vendor_attribute_nodes = [
            old_vendor_attribute_root.has_latest_value.single()
            for old_has_vendor_attribute_node in old_has_vendor_attribute_nodes
            if (
                old_vendor_attribute_root := old_has_vendor_attribute_node.has_root.single()
            )
        ]

        old_has_vendor_element_attribute_nodes = (
            current_latest.has_vendor_element_attribute.all() if current_latest else []
        )
        new_has_vendor_element_attribute_nodes = [
            old_vendor_element_attribute_root.has_latest_value.single()
            for old_has_vendor_element_attribute_node in old_has_vendor_element_attribute_nodes
            if (
                old_vendor_element_attribute_root := old_has_vendor_element_attribute_node.has_root.single()
            )
        ]

        for old_has_vendor_element_node, new_has_vendor_element_node in zip(
            old_has_vendor_element_nodes, new_has_vendor_element_nodes
        ):
            params = current_latest.has_vendor_element.relationship(
                old_has_vendor_element_node
            )
            new_value.has_vendor_element.connect(
                new_has_vendor_element_node,
                {"value": params.value},
            )

        for old_has_vendor_attribute_node, new_has_vendor_attribute_node in zip(
            old_has_vendor_attribute_nodes, new_has_vendor_attribute_nodes
        ):
            params = current_latest.has_vendor_attribute.relationship(
                old_has_vendor_attribute_node
            )
            new_value.has_vendor_attribute.connect(
                new_has_vendor_attribute_node,
                {"value": params.value},
            )

        for (
            old_has_vendor_element_attribute_node,
            new_has_vendor_element_attribute_node,
        ) in zip(
            old_has_vendor_element_attribute_nodes,
            new_has_vendor_element_attribute_nodes,
        ):
            params = current_latest.has_vendor_element_attribute.relationship(
                old_has_vendor_element_attribute_node
            )
            new_value.has_vendor_element_attribute.connect(
                new_has_vendor_element_attribute_node,
                {"value": params.value},
            )

        if disconnect_old:
            for old_has_vendor_element_node in old_has_vendor_element_nodes:
                current_latest.has_vendor_element.disconnect(
                    old_has_vendor_element_node
                )
            for old_has_vendor_attribute_node in old_has_vendor_attribute_nodes:
                current_latest.has_vendor_attribute.disconnect(
                    old_has_vendor_attribute_node
                )
            for (
                old_has_vendor_element_attribute_node
            ) in old_has_vendor_element_attribute_nodes:
                current_latest.has_vendor_element_attribute.disconnect(
                    old_has_vendor_element_attribute_node
                )

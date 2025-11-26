import json
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
    OdmVendorAttributeRoot,
    OdmVendorAttributeValue,
    OdmVendorElementRoot,
    OdmVendorNamespaceRoot,
)
from clinical_mdr_api.domains.concepts.odms.vendor_attribute import (
    OdmVendorAttributeAR,
    OdmVendorAttributeRelationVO,
    OdmVendorAttributeVO,
    OdmVendorElementAttributeRelationVO,
)
from clinical_mdr_api.domains.concepts.utils import RelationType
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.odms.odm_vendor_attribute import (
    OdmVendorAttribute,
)
from common.exceptions import BusinessLogicException
from common.utils import convert_to_datetime


class VendorAttributeRepository(OdmGenericRepository[OdmVendorAttributeAR]):
    root_class = OdmVendorAttributeRoot
    value_class = OdmVendorAttributeValue
    return_model = OdmVendorAttribute

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        **_kwargs,
    ) -> OdmVendorAttributeAR:
        vendor_namespace_value = value.belongs_to_vendor_namespace.get_or_none()
        vendor_element_value = value.belongs_to_vendor_element.get_or_none()
        return OdmVendorAttributeAR.from_repository_values(
            uid=root.uid,
            concept_vo=OdmVendorAttributeVO.from_repository_values(
                name=value.name,
                compatible_types=(
                    value.compatible_types if value.compatible_types else []
                ),
                data_type=value.data_type,
                value_regex=value.value_regex,
                vendor_namespace_uid=(
                    vendor_namespace_value.has_root.single().uid
                    if vendor_namespace_value
                    else None
                ),
                vendor_element_uid=(
                    vendor_element_value.has_root.single().uid
                    if vendor_element_value
                    else None
                ),
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=lambda _: library.is_editable,
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict[str, Any]
    ) -> OdmVendorAttributeAR:
        major, minor = input_dict["version"].split(".")
        odm_form_ar = OdmVendorAttributeAR.from_repository_values(
            uid=input_dict["uid"],
            concept_vo=OdmVendorAttributeVO.from_repository_values(
                name=input_dict["name"],
                compatible_types=json.loads(input_dict.get("compatible_types") or "[]"),
                data_type=input_dict.get("data_type"),
                value_regex=input_dict.get("value_regex"),
                vendor_namespace_uid=input_dict.get("vendor_namespace_uid"),
                vendor_element_uid=input_dict.get("vendor_element_uid"),
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

        return odm_form_ar

    def specific_alias_clause(self, **kwargs) -> str:
        return """
WITH *,
concept_value.compatible_types AS compatible_types,
concept_value.data_type AS data_type,
concept_value.value_regex AS value_regex,

head([(concept_value)<-[:HAS_VENDOR_ATTRIBUTE]-(vnv:OdmVendorNamespaceValue)<-[:HAS_VERSION]-(vnr:OdmVendorNamespaceRoot) |
{uid: vnr.uid, name: vnv.name, prefix: vnv.prefix, url: vnv.url}]) AS vendor_namespace,

head([(concept_value)<-[:HAS_VENDOR_ATTRIBUTE]-(xtv:OdmVendorElementValue)<-[:HAS_VERSION]-(xtr:OdmVendorElementRoot) |
{uid: xtr.uid, name: xtv.name}]) AS vendor_element


WITH *,
vendor_namespace.uid AS vendor_namespace_uid,
vendor_element.uid AS vendor_element_uid
"""

    def _get_or_create_value(
        self,
        root: VersionRoot,
        ar: OdmVendorAttributeAR,
        force_new_value_node: bool = False,
    ) -> VersionValue:
        new_value = super()._get_or_create_value(root, ar, force_new_value_node)

        new_value.belongs_to_vendor_namespace.disconnect_all()
        new_value.belongs_to_vendor_element.disconnect_all()

        if ar.concept_vo.vendor_namespace_uid is not None:
            vendor_namespace_root = OdmVendorNamespaceRoot.nodes.get_or_none(
                uid=ar.concept_vo.vendor_namespace_uid
            )
            vendor_namespace_value = (
                vendor_namespace_root.has_latest_value.get_or_none()
                if vendor_namespace_root
                else None
            )
            if vendor_namespace_value:
                new_value.belongs_to_vendor_namespace.connect(vendor_namespace_value)

        if ar.concept_vo.vendor_element_uid is not None:
            vendor_element_root = OdmVendorElementRoot.nodes.get_or_none(
                uid=ar.concept_vo.vendor_element_uid
            )
            vendor_element_value = (
                vendor_element_root.has_latest_value.get_or_none()
                if vendor_element_root
                else None
            )
            if vendor_element_value:
                new_value.belongs_to_vendor_element.connect(vendor_element_value)

        return new_value

    def _create_new_value_node(
        self, ar: OdmVendorAttributeAR
    ) -> OdmVendorAttributeValue:
        value_node = super()._create_new_value_node(ar=ar)

        value_node.save()

        value_node.compatible_types = ar.concept_vo.compatible_types
        value_node.data_type = ar.concept_vo.data_type
        value_node.value_regex = ar.concept_vo.value_regex

        return value_node

    def _has_data_changed(
        self, ar: OdmVendorAttributeAR, value: OdmVendorAttributeValue
    ) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)

        vendor_namespace_uid = (
            vendor_namespace_value.has_root.single().uid
            if (
                vendor_namespace_value := value.belongs_to_vendor_namespace.get_or_none()
            )
            else None
        )
        vendor_element_uid = (
            vendor_element_value.has_root.single().uid
            if (vendor_element_value := value.belongs_to_vendor_element.get_or_none())
            else None
        )

        are_rels_changed = (
            ar.concept_vo.vendor_namespace_uid != vendor_namespace_uid
            or ar.concept_vo.vendor_element_uid != vendor_element_uid
        )

        return (
            are_concept_properties_changed
            or are_rels_changed
            or ar.concept_vo.compatible_types != value.compatible_types
            or ar.concept_vo.data_type != value.data_type
            or ar.concept_vo.value_regex != value.value_regex
        )

    def find_by_uid_with_odm_element_relation(
        self,
        uid: str,
        odm_element_uid: str,
        odm_element_version: str,
        odm_element_type: RelationType,
        vendor_element_attribute: bool = True,
    ):
        if odm_element_type == RelationType.FORM:
            odm_element_root = "OdmFormRoot"
            odm_element_value = "OdmFormValue"
        elif odm_element_type == RelationType.ITEM_GROUP:
            odm_element_root = "OdmItemGroupRoot"
            odm_element_value = "OdmItemGroupValue"
        elif odm_element_type == RelationType.ITEM:
            odm_element_root = "OdmItemRoot"
            odm_element_value = "OdmItemValue"
        else:
            raise BusinessLogicException(msg="Invalid ODM element type.")

        if vendor_element_attribute:
            rs, _ = db.cypher_query(
                f"""
                MATCH (:{odm_element_root} {{uid: $odm_element_uid}})-[:HAS_VERSION {{version: $odm_element_version}}]->(:{odm_element_value})
                -[ref:HAS_VENDOR_ELEMENT_ATTRIBUTE]->(value:OdmVendorAttributeValue)<-[:HAS_VERSION]-(:OdmVendorAttributeRoot {{uid: $uid}})
                MATCH (value)<-[:HAS_VENDOR_ATTRIBUTE]-(:OdmVendorElementValue)<-[:HAS_VERSION]-(vendor_element_root:OdmVendorElementRoot)
                RETURN
                    value.name AS name,
                    value.data_type AS data_type,
                    value.value_regex AS value_regex,
                    ref.value AS value,
                    vendor_element_root.uid AS vendor_element_uid
                """,
                params={
                    "uid": uid,
                    "odm_element_uid": odm_element_uid,
                    "odm_element_version": odm_element_version,
                },
            )
            return OdmVendorElementAttributeRelationVO.from_repository_values(
                uid=uid,
                name=rs[0][0],
                data_type=rs[0][1],
                value_regex=rs[0][2],
                value=rs[0][3],
                vendor_element_uid=rs[0][4],
            )

        rs, _ = db.cypher_query(
            f"""
                MATCH (:{odm_element_root} {{uid: $odm_element_uid}})-[:HAS_VERSION {{version: $odm_element_version}}]->(:{odm_element_value})
                -[ref:HAS_VENDOR_ATTRIBUTE]->(value:OdmVendorAttributeValue)<-[:HAS_VERSION]-(:OdmVendorAttributeRoot {{uid: $uid}})
                MATCH (value)<-[:HAS_VENDOR_ATTRIBUTE]-(:OdmVendorNamespaceValue)<-[:HAS_VERSION]-(vendor_namespace_root:OdmVendorNamespaceRoot)
                RETURN
                    value.name AS name,
                    value.compatible_types AS compatible_types,
                    value.data_type AS data_type,
                    value.value_regex AS value_regex,
                    ref.value AS value,
                    vendor_namespace_root.uid AS vendor_namespace_uid
                """,
            params={
                "uid": uid,
                "odm_element_uid": odm_element_uid,
                "odm_element_version": odm_element_version,
            },
        )

        return OdmVendorAttributeRelationVO.from_repository_values(
            uid=uid,
            name=rs[0][0],
            compatible_types=json.loads(rs[0][1]),
            data_type=rs[0][2],
            value_regex=rs[0][3],
            value=rs[0][4],
            vendor_namespace_uid=rs[0][5],
        )

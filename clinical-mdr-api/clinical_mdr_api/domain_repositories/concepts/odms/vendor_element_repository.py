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
    OdmVendorElementRoot,
    OdmVendorElementValue,
    OdmVendorNamespaceRoot,
)
from clinical_mdr_api.domains.concepts.odms.vendor_element import (
    OdmVendorElementAR,
    OdmVendorElementRelationVO,
    OdmVendorElementVO,
)
from clinical_mdr_api.domains.concepts.utils import RelationType
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.odms.odm_vendor_element import OdmVendorElement
from common.exceptions import BusinessLogicException
from common.utils import convert_to_datetime


class VendorElementRepository(OdmGenericRepository[OdmVendorElementAR]):
    root_class = OdmVendorElementRoot
    value_class = OdmVendorElementValue
    return_model = OdmVendorElement

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        **_kwargs,
    ) -> OdmVendorElementAR:
        vendor_namespace_value = value.belongs_to_vendor_namespace.get_or_none()
        return OdmVendorElementAR.from_repository_values(
            uid=root.uid,
            concept_vo=OdmVendorElementVO.from_repository_values(
                name=value.name,
                compatible_types=value.compatible_types,
                vendor_namespace_uid=vendor_namespace_value.has_root.single().uid,
                vendor_attribute_uids=[
                    _root.uid
                    for vendor_attribute_value in value.has_vendor_attribute.all()
                    if (_root := vendor_attribute_value.has_root.single()) is not None
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
    ) -> OdmVendorElementAR:
        major, minor = input_dict["version"].split(".")
        odm_vendor_element_ar = OdmVendorElementAR.from_repository_values(
            uid=input_dict["uid"],
            concept_vo=OdmVendorElementVO.from_repository_values(
                name=input_dict["name"],
                compatible_types=json.loads(input_dict.get("compatible_types") or "[]"),
                vendor_namespace_uid=input_dict["vendor_namespace_uid"],
                vendor_attribute_uids=input_dict["vendor_attribute_uids"],
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

        return odm_vendor_element_ar

    def specific_alias_clause(self, **kwargs) -> str:
        return """
WITH *,
concept_value.compatible_types AS compatible_types,

head([(concept_value)<-[:HAS_VENDOR_ELEMENT]-(vnv:OdmVendorNamespaceValue)<-[:HAS_VERSION]-(vnr:OdmVendorNamespaceRoot) |
{uid: vnr.uid, name: vnv.name, prefix: vnv.prefix, url: vnv.url}]) AS vendor_namespace,

[(concept_value)-[:HAS_VENDOR_ATTRIBUTE]->(vav:OdmVendorAttributeValue)<-[:HAS_VERSION]-(var:OdmVendorAttributeRoot) |
{uid: var.uid, name: vav.name}] AS vendor_attributes

WITH *,
vendor_namespace.uid AS vendor_namespace_uid,
apoc.coll.toSet([vendor_attribute in vendor_attributes | vendor_attribute.uid]) AS vendor_attribute_uids
"""

    def _get_or_create_value(
        self,
        root: VersionRoot,
        ar: OdmVendorElementAR,
        force_new_value_node: bool = False,
    ) -> VersionValue:
        new_value = super()._get_or_create_value(root, ar, force_new_value_node)

        new_value.belongs_to_vendor_namespace.disconnect_all()

        if ar.concept_vo.vendor_namespace_uid is not None:
            vendor_namespace_root = OdmVendorNamespaceRoot.nodes.get_or_none(
                uid=ar.concept_vo.vendor_namespace_uid
            )
            vendor_namespace_value = (
                vendor_namespace_root.has_latest_value.get_or_none()
            )
            if vendor_namespace_value:
                new_value.belongs_to_vendor_namespace.connect(vendor_namespace_value)

        return new_value

    def _create_new_value_node(self, ar: OdmVendorElementAR) -> OdmVendorElementValue:
        value_node = super()._create_new_value_node(ar=ar)

        value_node.save()

        value_node.compatible_types = ar.concept_vo.compatible_types

        return value_node

    def _has_data_changed(
        self, ar: OdmVendorElementAR, value: OdmVendorElementValue
    ) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)

        vendor_namespace_uid = (
            vendor_namespace_value.has_root.single().uid
            if (
                vendor_namespace_value := value.belongs_to_vendor_namespace.get_or_none()
            )
            else None
        )

        are_rels_changed = ar.concept_vo.vendor_namespace_uid != vendor_namespace_uid

        return (
            are_concept_properties_changed
            or are_rels_changed
            or ar.concept_vo.compatible_types != value.compatible_types
        )

    def find_by_uid_with_odm_element_relation(
        self,
        uid: str,
        odm_element_uid: str,
        odm_element_version: str,
        odm_element_type: RelationType,
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

        rs, _ = db.cypher_query(
            f"""
            MATCH (:{odm_element_root} {{uid: $odm_element_uid}})-[:HAS_VERSION {{version: $odm_element_version}}]->(:{odm_element_value})
            -[ref:HAS_VENDOR_ELEMENT]->(value:OdmVendorElementValue)<-[:HAS_VERSION]-(:OdmVendorElementRoot {{uid: $uid}})
            RETURN
                value.name AS name,
                value.compatible_types AS compatible_types,
                ref.value AS value
            """,
            params={
                "uid": uid,
                "odm_element_uid": odm_element_uid,
                "odm_element_version": odm_element_version,
            },
        )

        return OdmVendorElementRelationVO.from_repository_values(
            uid=uid,
            name=rs[0][0],
            compatible_types=rs[0][1],
            value=rs[0][2],
        )

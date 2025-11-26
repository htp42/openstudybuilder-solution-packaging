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
from clinical_mdr_api.domain_repositories.models.odm import OdmFormRoot, OdmFormValue
from clinical_mdr_api.domains.concepts.odms.form import (
    OdmFormAR,
    OdmFormRefVO,
    OdmFormVO,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.odms.odm_common_models import (
    OdmAliasModel,
    OdmDescriptionModel,
)
from clinical_mdr_api.models.concepts.odms.odm_form import OdmForm
from clinical_mdr_api.services._utils import ensure_transaction
from common.utils import convert_to_datetime


class FormRepository(OdmGenericRepository[OdmFormAR]):
    root_class = OdmFormRoot
    value_class = OdmFormValue
    return_model = OdmForm

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: VersionRoot,
        library: Library,
        relationship: VersionRelationship,
        value: VersionValue,
        **_kwargs,
    ) -> OdmFormAR:
        return OdmFormAR.from_repository_values(
            uid=root.uid,
            concept_vo=OdmFormVO.from_repository_values(
                oid=value.oid,
                name=value.name,
                sdtm_version=value.sdtm_version,
                repeating=value.repeating,
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
                item_group_uids=[
                    item_group_root.uid
                    for item_group_value in value.item_group_ref.all()
                    if (item_group_root := item_group_value.has_root.single())
                ],
                vendor_element_uids=[
                    vendor_element_root.uid
                    for vendor_element_value in value.has_vendor_element.all()
                    if (vendor_element_root := vendor_element_value.has_root.single())
                ],
                vendor_attribute_uids=[
                    vendor_attribute_root.uid
                    for vendor_attribute_value in value.has_vendor_attribute.all()
                    if (
                        vendor_attribute_root := vendor_attribute_value.has_root.single()
                    )
                ],
                vendor_element_attribute_uids=[
                    vendor_element_attribute_root.uid
                    for vendor_element_attribute_value in value.has_vendor_element_attribute.all()
                    if (
                        vendor_element_attribute_root := vendor_element_attribute_value.has_root.single()
                    )
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
    ) -> OdmFormAR:
        major, minor = input_dict["version"].split(".")
        odm_form_ar = OdmFormAR.from_repository_values(
            uid=input_dict["uid"],
            concept_vo=OdmFormVO.from_repository_values(
                oid=input_dict.get("oid"),
                name=input_dict["name"],
                sdtm_version=input_dict.get("sdtm_version"),
                repeating=input_dict.get("repeating"),
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
                item_group_uids=input_dict["item_group_uids"],
                vendor_element_uids=input_dict["vendor_element_uids"],
                vendor_attribute_uids=input_dict["vendor_attribute_uids"],
                vendor_element_attribute_uids=input_dict[
                    "vendor_element_attribute_uids"
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

        return odm_form_ar

    def specific_alias_clause(self, **kwargs) -> str:
        return """
WITH *,
concept_value.oid AS oid,
toString(concept_value.repeating) AS repeating,
concept_value.sdtm_version AS sdtm_version,

[(concept_value)-[:HAS_DESCRIPTION]->(dv:OdmDescription) |
{name: dv.name, language: dv.language, description: dv.description, instruction: dv.instruction, sponsor_instruction: dv.sponsor_instruction}] AS descriptions,

[(concept_value)-[:HAS_ALIAS]->(av:OdmAlias) | {name: av.name, context: av.context}] AS aliases,

[(concept_value)-[igref:ITEM_GROUP_REF]->(igv:OdmItemGroupValue)<-[:HAS_VERSION]-(igr:OdmItemGroupRoot) |
{uid: igr.uid, name: igv.name, order: igref.order, mandatory: igref.mandatory}] AS item_groups,

[(concept_value)-[hve:HAS_VENDOR_ELEMENT]->(vev:OdmVendorElementValue)<-[:HAS_VERSION]-(ver:OdmVendorElementRoot) |
{uid: ver.uid, name: vev.name, value: hve.value}] AS vendor_elements,

[(concept_value)-[hva:HAS_VENDOR_ATTRIBUTE]->(vav:OdmVendorAttributeValue)<-[:HAS_VERSION]-(var:OdmVendorAttributeRoot) |
{uid: var.uid, name: vav.name, value: hva.value}] AS vendor_attributes,

[(concept_value)-[hvea:HAS_VENDOR_ELEMENT_ATTRIBUTE]->(vav:OdmVendorAttributeValue)<-[:HAS_VERSION]-(var:OdmVendorAttributeRoot) |
{uid: var.uid, name: vav.name, value: hvea.value}] AS vendor_element_attributes

WITH *,
apoc.coll.toSet([item_group in item_groups | item_group.uid]) AS item_group_uids,
apoc.coll.toSet([vendor_element in vendor_elements | vendor_element.uid]) AS vendor_element_uids,
apoc.coll.toSet([vendor_attribute in vendor_attributes | vendor_attribute.uid]) AS vendor_attribute_uids,
apoc.coll.toSet([vendor_element_attribute in vendor_element_attributes | vendor_element_attribute.uid]) AS vendor_element_attribute_uids
"""

    def _get_or_create_value(
        self,
        root: VersionRoot,
        ar: OdmFormAR,
        force_new_value_node: bool = False,
    ) -> VersionValue:
        current_latest = root.has_latest_value.single()
        old_item_group_ref_nodes = (
            current_latest.item_group_ref.all() if current_latest else []
        )
        new_item_group_ref_nodes = [
            old_item_group_root.has_latest_value.single()
            for old_item_group_ref_node in old_item_group_ref_nodes
            if (old_item_group_root := old_item_group_ref_node.has_root.single())
        ]

        new_value = super()._get_or_create_value(root, ar, force_new_value_node)

        for old_item_group_ref_node, new_item_group_ref_node in zip(
            old_item_group_ref_nodes, new_item_group_ref_nodes
        ):
            params = current_latest.item_group_ref.relationship(old_item_group_ref_node)
            new_value.item_group_ref.connect(
                new_item_group_ref_node,
                {
                    "order_number": params.order_number,
                    "mandatory": params.mandatory,
                    "collection_exception_condition_oid": params.collection_exception_condition_oid,
                    "vendor": params.vendor,
                },
            )

        if ar.should_disconnect_relationships:
            for old_item_group_ref_node in old_item_group_ref_nodes:
                current_latest.item_group_ref.disconnect(old_item_group_ref_node)

        self.manage_vendor_relationships(
            current_latest, new_value, ar.should_disconnect_relationships
        )
        self.connect_descriptions(ar.concept_vo.descriptions, new_value)
        self.connect_aliases(ar.concept_vo.aliases, new_value)

        return new_value

    def _create_new_value_node(self, ar: OdmFormAR) -> OdmFormValue:
        value_node = super()._create_new_value_node(ar=ar)

        value_node.save()

        value_node.oid = ar.concept_vo.oid
        value_node.sdtm_version = ar.concept_vo.sdtm_version
        value_node.repeating = ar.concept_vo.repeating

        return value_node

    def _has_data_changed(self, ar: OdmFormAR, value: OdmFormValue) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)

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
            set(ar.concept_vo.descriptions) != description_nodes
            or set(ar.concept_vo.aliases) != alias_nodes
        )

        return (
            are_concept_properties_changed
            or are_rels_changed
            or ar.concept_vo.oid != value.oid
            or ar.concept_vo.sdtm_version != value.sdtm_version
            or ar.concept_vo.repeating != value.repeating
        )

    def find_by_uid_with_study_event_relation(
        self, uid: str, study_event_uid: str, study_event_version: str
    ) -> OdmFormRefVO:
        rs, _ = db.cypher_query(
            """
            MATCH (:OdmStudyEventRoot {uid: $study_event_uid})-[:HAS_VERSION {version: $study_event_version}]->(:OdmStudyEventValue)
            -[ref:FORM_REF]->(value:OdmFormValue)<-[hv_rel:HAS_VERSION]-(:OdmFormRoot {uid: $uid})
            RETURN
                value.name AS name,
                hv_rel.version AS version,
                ref.order_number AS order_number,
                ref.mandatory AS mandatory,
                ref.locked AS locked,
                ref.collection_exception_condition_oid AS collection_exception_condition_oid
            """,
            params={
                "uid": uid,
                "study_event_uid": study_event_uid,
                "study_event_version": study_event_version,
            },
        )

        return OdmFormRefVO.from_repository_values(
            uid=uid,
            name=rs[0][0],
            version=rs[0][1],
            study_event_uid=study_event_uid,
            order_number=rs[0][2],
            mandatory=rs[0][3],
            locked=rs[0][4],
            collection_exception_condition_oid=rs[0][5],
        )

    @ensure_transaction(db)
    def _connect_relationships_to_new_value_node(
        self, root: VersionRoot, _: VersionValue
    ) -> None:
        """
        Upgrades all incoming FORM_REF relationships to the second latest version to point
        to the latest version of OdmFormValue, preserving relationship properties.
        """
        query = f"""
        MATCH (root:{self.root_class.__name__} {{uid: $root_uid}})-[ver_rel:HAS_VERSION]->(value:{self.value_class.__name__})

        WITH root, ver_rel, value
        ORDER BY ver_rel.start_date DESC
        LIMIT 2
        WITH root, collect(value) AS values
        WITH root, values[0] as latest_value, values[1] as second_latest_value

        MATCH (:OdmStudyEventRoot)-[p_ver_rel:HAS_VERSION]->(parent_value:OdmStudyEventValue)-[ref_rel:FORM_REF]->(second_latest_value)
        WHERE p_ver_rel.end_date IS NULL AND p_ver_rel.status = "Draft"

        WITH latest_value, ref_rel, parent_value,
            ref_rel.order_number AS order_number,
            ref_rel.mandatory AS mandatory,
            ref_rel.locked AS locked,
            ref_rel.collection_exception_condition_oid AS collection_exception_condition_oid

        CREATE (parent_value)-[new_ref_rel:FORM_REF]->(latest_value)

        SET new_ref_rel.order_number = order_number,
            new_ref_rel.mandatory = mandatory,
            new_ref_rel.locked = locked,
            new_ref_rel.collection_exception_condition_oid = collection_exception_condition_oid

        DELETE ref_rel
        """
        db.cypher_query(query, {"root_uid": root.uid})

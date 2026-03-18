from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.odms.item_group_repository import (
    ItemGroupRepository,
)
from clinical_mdr_api.domains.concepts.odms.item_group import (
    OdmItemGroupAR,
    OdmItemGroupVO,
)
from clinical_mdr_api.domains.concepts.utils import (
    RelationType,
    VendorAttributeCompatibleType,
    VendorElementCompatibleType,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from clinical_mdr_api.models.concepts.odms.odm_item_group import (
    OdmItemGroup,
    OdmItemGroupItemPostInput,
    OdmItemGroupPatchInput,
    OdmItemGroupPostInput,
    OdmItemGroupVersion,
)
from clinical_mdr_api.services._utils import ensure_transaction, get_input_or_new_value
from clinical_mdr_api.services.concepts.odms.odm_generic_service import (
    OdmGenericService,
)
from clinical_mdr_api.utils import normalize_string, to_dict
from common.exceptions import BusinessLogicException, NotFoundException
from common.utils import strtobool


class OdmItemGroupService(OdmGenericService[OdmItemGroupAR]):
    aggregate_class = OdmItemGroupAR
    version_class = OdmItemGroupVersion
    repository_interface = ItemGroupRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmItemGroupAR
    ) -> OdmItemGroup:
        return OdmItemGroup.from_odm_item_group_ar(
            odm_item_group_ar=item_ar,
            find_odm_vendor_attribute_by_uid=self._repos.odm_vendor_attribute_repository.find_by_uid_2,
            find_odm_item_by_uid_with_item_group_relation=self._repos.odm_item_repository.find_by_uid_with_item_group_relation,
            find_odm_vendor_element_by_uid_with_odm_element_relation=(
                self._repos.odm_vendor_element_repository.find_by_uid_with_odm_element_relation
            ),
            find_odm_vendor_attribute_by_uid_with_odm_element_relation=(
                self._repos.odm_vendor_attribute_repository.find_by_uid_with_odm_element_relation
            ),
        )

    def _create_aggregate_root(
        self, concept_input: OdmItemGroupPostInput, library
    ) -> OdmItemGroupAR:
        return OdmItemGroupAR.from_input_values(
            author_id=self.author_id,
            concept_vo=OdmItemGroupVO.from_repository_values(
                oid=get_input_or_new_value(concept_input.oid, "G.", concept_input.name),
                name=concept_input.name,
                repeating=strtobool(concept_input.repeating),
                is_reference_data=strtobool(concept_input.is_reference_data),
                sas_dataset_name=concept_input.sas_dataset_name,
                origin=concept_input.origin,
                purpose=concept_input.purpose,
                comment=concept_input.comment,
                translated_texts=concept_input.translated_texts,
                aliases=concept_input.aliases,
                sdtm_domain_uids=concept_input.sdtm_domain_uids,
                item_uids=[],
                vendor_element_uids=[],
                vendor_attribute_uids=[],
                vendor_element_attribute_uids=[],
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            odm_object_exists_callback=self._repos.odm_item_group_repository.odm_object_exists,
            find_term_callback=self._repos.ct_term_attributes_repository.find_by_uid,
        )

    def _edit_aggregate(
        self, item: OdmItemGroupAR, concept_edit_input: OdmItemGroupPatchInput
    ) -> OdmItemGroupAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmItemGroupVO.from_repository_values(
                oid=concept_edit_input.oid,
                name=concept_edit_input.name,
                repeating=strtobool(concept_edit_input.repeating),
                is_reference_data=strtobool(concept_edit_input.is_reference_data),
                sas_dataset_name=concept_edit_input.sas_dataset_name,
                origin=concept_edit_input.origin,
                purpose=concept_edit_input.purpose,
                comment=concept_edit_input.comment,
                translated_texts=concept_edit_input.translated_texts,
                aliases=concept_edit_input.aliases,
                sdtm_domain_uids=concept_edit_input.sdtm_domain_uids,
                item_uids=item.concept_vo.item_uids,
                vendor_element_uids=item.concept_vo.vendor_element_uids,
                vendor_attribute_uids=item.concept_vo.vendor_attribute_uids,
                vendor_element_attribute_uids=item.concept_vo.vendor_element_attribute_uids,
            ),
            odm_object_exists_callback=self._repos.odm_item_group_repository.odm_object_exists,
            find_term_callback=self._repos.ct_term_attributes_repository.find_by_uid,
        )
        return item

    @db.transaction
    def create(self, concept_input: OdmItemGroupPostInput) -> OdmItemGroup:
        item = super().create(concept_input)

        super().manage_vendors(
            item.uid,
            VendorElementCompatibleType.ITEM_GROUP_DEF,
            VendorAttributeCompatibleType.ITEM_GROUP_DEF,
            concept_input.vendor_elements,
            concept_input.vendor_element_attributes,
            concept_input.vendor_attributes,
            self._repos.odm_item_group_repository,
        )

        return self._transform_aggregate_root_to_pydantic_model(
            self._repos.odm_item_group_repository.find_by_uid_2(item.uid)
        )

    @db.transaction
    def edit_draft(
        self, uid: str, concept_edit_input: OdmItemGroupPatchInput
    ) -> OdmItemGroup:
        super().edit_draft(uid, concept_edit_input)

        super().manage_vendors(
            uid,
            VendorElementCompatibleType.ITEM_GROUP_DEF,
            VendorAttributeCompatibleType.ITEM_GROUP_DEF,
            concept_edit_input.vendor_elements,
            concept_edit_input.vendor_element_attributes,
            concept_edit_input.vendor_attributes,
            self._repos.odm_item_group_repository,
        )

        return self._transform_aggregate_root_to_pydantic_model(
            self._repos.odm_item_group_repository.find_by_uid_2(uid)
        )

    @ensure_transaction(db)
    def add_items(
        self,
        uid: str,
        odm_item_group_item_post_input: list[OdmItemGroupItemPostInput],
        override: bool = False,
    ) -> OdmItemGroup:
        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        BusinessLogicException.raise_if(
            odm_item_group_ar.item_metadata.status != LibraryItemStatus.DRAFT,
            msg=self.OBJECT_NOT_IN_DRAFT,
        )

        if override:
            self._repos.odm_item_group_repository.remove_relation(
                uid=uid,
                relation_uid=None,
                relationship_type=RelationType.ITEM,
                disconnect_all=True,
            )

        vendor_attribute_patterns = self.get_regex_patterns_of_attributes(
            [
                attribute.uid
                for input_attribute in odm_item_group_item_post_input
                if input_attribute.vendor
                for attribute in input_attribute.vendor.attributes
            ]
        )
        self.are_attributes_vendor_compatible(
            [
                vendor_attribute
                for item in odm_item_group_item_post_input
                for vendor_attribute in item.vendor.attributes
            ],
            VendorAttributeCompatibleType.ITEM_REF,
        )

        for item in odm_item_group_item_post_input:
            if item.vendor:
                self.can_connect_vendor_attributes(item.vendor.attributes)
                self.attribute_values_matches_their_regex(
                    item.vendor.attributes,
                    vendor_attribute_patterns,
                )

            self._repos.odm_item_group_repository.add_relation(
                uid=uid,
                relation_uid=item.uid,
                relationship_type=RelationType.ITEM,
                parameters={
                    "order_number": item.order_number,
                    "mandatory": strtobool(item.mandatory),
                    "key_sequence": item.key_sequence,
                    "method_oid": item.method_oid,
                    "imputation_method_oid": item.imputation_method_oid,
                    "role": item.role,
                    "role_codelist_oid": item.role_codelist_oid,
                    "collection_exception_condition_oid": item.collection_exception_condition_oid,
                    "vendor": to_dict(item.vendor),
                },
                zero_or_one_relation=True,
            )

        odm_item_group_ar = self._find_by_uid_or_raise_not_found(normalize_string(uid))

        return self._transform_aggregate_root_to_pydantic_model(odm_item_group_ar)

    @db.transaction
    def get_active_relationships(self, uid: str):
        NotFoundException.raise_if_not(
            self._repos.odm_item_group_repository.exists_by("uid", uid, True),
            "ODM Item Group",
            uid,
        )

        return self._repos.odm_item_group_repository.get_active_relationships(
            uid, ["item_group_ref"]
        )

    @db.transaction
    def get_item_groups_that_belongs_to_form(self):
        return self._repos.odm_item_group_repository.get_if_has_relationship(
            "item_group_ref"
        )

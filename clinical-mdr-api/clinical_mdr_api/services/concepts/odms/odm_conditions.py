from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.odms.condition_repository import (
    ConditionRepository,
)
from clinical_mdr_api.domains.concepts.odms.condition import (
    OdmConditionAR,
    OdmConditionVO,
)
from clinical_mdr_api.models.concepts.odms.odm_condition import (
    OdmCondition,
    OdmConditionPatchInput,
    OdmConditionPostInput,
    OdmConditionVersion,
)
from clinical_mdr_api.services.concepts.odms.odm_generic_service import (
    OdmGenericService,
)
from common.exceptions import NotFoundException


class OdmConditionService(OdmGenericService[OdmConditionAR]):
    aggregate_class = OdmConditionAR
    version_class = OdmConditionVersion
    repository_interface = ConditionRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmConditionAR
    ) -> OdmCondition:
        return OdmCondition.from_odm_condition_ar(odm_condition_ar=item_ar)

    def _create_aggregate_root(
        self, concept_input: OdmConditionPostInput, library
    ) -> OdmConditionAR:
        return OdmConditionAR.from_input_values(
            author_id=self.author_id,
            concept_vo=OdmConditionVO.from_repository_values(
                oid=concept_input.oid,
                name=concept_input.name,
                formal_expressions=concept_input.formal_expressions,
                descriptions=concept_input.descriptions,
                aliases=concept_input.aliases,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            odm_object_exists_callback=self._repos.odm_condition_repository.odm_object_exists,
        )

    def _edit_aggregate(
        self, item: OdmConditionAR, concept_edit_input: OdmConditionPatchInput
    ) -> OdmConditionAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmConditionVO.from_repository_values(
                oid=concept_edit_input.oid,
                name=concept_edit_input.name,
                formal_expressions=concept_edit_input.formal_expressions,
                descriptions=concept_edit_input.descriptions,
                aliases=concept_edit_input.aliases,
            ),
            odm_object_exists_callback=self._repos.odm_condition_repository.odm_object_exists,
        )
        return item

    @db.transaction
    def soft_delete(self, uid: str, cascade_delete: bool = False):
        """
        Works exactly as the parent soft_delete method.
        However, after deleting the ODM Condition, it also sets all collection_exception_condition_oid that use this ODM Condition to null.

        This method is temporary and should be removed when the database relationship between ODM Condition and its reference nodes is ready.
        """
        condition = self._find_by_uid_or_raise_not_found(uid, for_update=True)
        condition.soft_delete()
        self.repository.save(condition)

        if cascade_delete:
            self.cascade_delete(condition)

        self._repos.odm_condition_repository.set_all_collection_exception_condition_oid_properties_to_null(
            condition.concept_vo.oid
        )

    @db.transaction
    def get_active_relationships(self, uid: str):
        NotFoundException.raise_if_not(
            self._repos.odm_condition_repository.exists_by("uid", uid, True),
            "ODM Condition",
            uid,
        )

        return self._repos.odm_condition_repository.get_active_relationships(uid, [])

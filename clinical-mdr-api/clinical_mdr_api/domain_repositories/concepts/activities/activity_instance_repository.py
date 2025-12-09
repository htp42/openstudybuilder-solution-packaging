import datetime
from typing import Any

from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.concept_generic_repository import (
    ConceptGenericRepository,
)
from clinical_mdr_api.domain_repositories.controlled_terminologies.ct_codelist_attributes_repository import (
    CTCodelistAttributesRepository,
)
from clinical_mdr_api.domain_repositories.models._utils import ListDistinct
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityGrouping,
    ActivityInstanceRoot,
    ActivityInstanceValue,
    ActivityItem,
    ActivityRoot,
)
from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityInstanceClassRoot,
    ActivityItemClassRoot,
)
from clinical_mdr_api.domain_repositories.models.concepts import UnitDefinitionRoot
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    Library,
    VersionRelationship,
)
from clinical_mdr_api.domain_repositories.models.odm import (
    OdmFormRoot,
    OdmItemGroupRoot,
    OdmItemRoot,
)
from clinical_mdr_api.domains.concepts.activities.activity_instance import (
    ActivityInstanceAR,
    ActivityInstanceGroupingVO,
    ActivityInstanceVO,
)
from clinical_mdr_api.domains.concepts.activities.activity_item import (
    ActivityItemVO,
    CTTermItem,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemMetadataVO,
    LibraryItemStatus,
    LibraryVO,
)
from clinical_mdr_api.models.concepts.activities.activity_instance import (
    ActivityInstance,
)
from clinical_mdr_api.models.concepts.activities.activity_item import (
    CompactOdmForm,
    CompactOdmItem,
    CompactOdmItemGroup,
    CompactUnitDefinition,
)
from common.config import settings
from common.exceptions import BusinessLogicException
from common.utils import convert_to_datetime, version_string_to_tuple


class ActivityInstanceRepository(ConceptGenericRepository[ActivityInstanceAR]):
    root_class = ActivityInstanceRoot
    value_class = ActivityInstanceValue
    aggregate_class = ActivityInstanceAR
    value_object_class = ActivityInstanceVO
    return_model = ActivityInstance

    def _create_new_value_node(self, ar: ActivityInstanceAR) -> ActivityInstanceValue:
        value_node: ActivityInstanceValue = super()._create_new_value_node(ar=ar)
        value_node.is_research_lab = ar.concept_vo.is_research_lab
        value_node.molecular_weight = ar.concept_vo.molecular_weight
        value_node.topic_code = ar.concept_vo.topic_code
        value_node.adam_param_code = ar.concept_vo.adam_param_code
        value_node.is_required_for_activity = ar.concept_vo.is_required_for_activity
        value_node.is_default_selected_for_activity = (
            ar.concept_vo.is_default_selected_for_activity
        )
        value_node.is_data_sharing = ar.concept_vo.is_data_sharing
        value_node.is_legacy_usage = ar.concept_vo.is_legacy_usage
        value_node.is_derived = ar.concept_vo.is_derived
        value_node.legacy_description = ar.concept_vo.legacy_description

        value_node.save()

        activity_uids = {ag.activity_uid for ag in ar.concept_vo.activity_groupings}
        BusinessLogicException.raise_if(
            len(activity_uids) > 1,
            msg="Instances are not allowed to link to several different activities",
        )
        requested = ActivityRoot.nodes.filter(
            uid=next(iter(activity_uids)),
            has_library__name=settings.requested_library_name,
        )
        BusinessLogicException.raise_if(
            len(requested) > 0,
            msg="Activity instances are not allowed to link to activity requests or placeholders",
        )

        for activity_grouping in ar.concept_vo.activity_groupings:
            # find related ActivityGrouping node
            activity_grouping_node = ListDistinct(
                ActivityGrouping.nodes.filter(
                    in_subgroup__in_group__has_version__uid=activity_grouping.activity_group_uid,
                    in_subgroup__has_group__has_version__uid=activity_grouping.activity_subgroup_uid,
                    has_grouping__latest_final__uid=activity_grouping.activity_uid,
                ).resolve_subgraph()
            ).distinct()
            BusinessLogicException.raise_if(
                len(activity_grouping_node) == 0,
                msg=f"The ActivityValidGroup node wasn't found for Activity Subgroup with UID '{activity_grouping.activity_subgroup_uid}'"
                f" and Activity Group with UID '{activity_grouping.activity_group_uid}'.",
            )
            activity_grouping_node = activity_grouping_node[0]
            # link ActivityInstanceValue with ActivityGrouping node
            value_node.has_activity.connect(activity_grouping_node)

        activity_instance_class = ActivityInstanceClassRoot.nodes.get(
            uid=ar.concept_vo.activity_instance_class_uid
        )
        value_node.activity_instance_class.connect(activity_instance_class)

        for item in ar.concept_vo.activity_items:
            activity_item_class = ActivityItemClassRoot.nodes.get_or_none(
                uid=item.activity_item_class_uid
            )
            is_adam_param_specific = (
                item.is_adam_param_specific
                if getattr(
                    activity_item_class.has_activity_instance_class.relationship(
                        activity_instance_class
                    ),
                    "is_adam_param_specific_enabled",
                    False,
                )
                else False
            )
            activity_item_node = ActivityItem(
                is_adam_param_specific=is_adam_param_specific
            )
            activity_item_node.save()
            activity_item_node.has_activity_item_class.connect(activity_item_class)

            for term in item.ct_terms:
                ct_term_root = CTTermRoot.nodes.get_or_none(uid=term.uid)
                selected_term_node = (
                    CTCodelistAttributesRepository().get_or_create_selected_term(
                        ct_term_root,
                        codelist_uid=term.codelist_uid,
                    )
                )
                activity_item_node.has_ct_term.connect(selected_term_node)

            for unit in item.unit_definitions:
                unit_definition = UnitDefinitionRoot.nodes.get_or_none(uid=unit.uid)
                activity_item_node.has_unit_definition.connect(unit_definition)

            if item.odm_form and item.odm_form.uid:
                odm_form_root = OdmFormRoot.nodes.get_or_none(uid=item.odm_form.uid)
                odm_form_value = odm_form_root.has_latest_value.single()
                activity_item_node.has_odm_form.connect(odm_form_value)

            if item.odm_item_group and item.odm_item_group.uid:
                odm_item_group_root = OdmItemGroupRoot.nodes.get_or_none(
                    uid=item.odm_item_group.uid
                )
                odm_item_group_value = odm_item_group_root.has_latest_value.single()
                activity_item_node.has_odm_item_group.connect(odm_item_group_value)

            if item.odm_item and item.odm_item.uid:
                odm_item_root = OdmItemRoot.nodes.get_or_none(uid=item.odm_item.uid)
                odm_item_value = odm_item_root.has_latest_value.single()
                activity_item_node.has_odm_item.connect(odm_item_value)

            value_node.contains_activity_item.connect(activity_item_node)
        return value_node

    def _has_item_data_changed(self, ar_items, value_item_nodes):
        ar_activity_items = []
        for item in ar_items:
            ar_activity_items.append(
                {
                    "is_adam_param_specific": item.is_adam_param_specific,
                    "class": item.activity_item_class_uid,
                    "units": {unit.uid for unit in item.unit_definitions},
                    "terms": {(term.uid, term.codelist_uid) for term in item.ct_terms},
                    "odm_form": item.odm_form.uid if item.odm_form else None,
                    "odm_item_group": (
                        item.odm_item_group.uid if item.odm_item_group else None
                    ),
                    "odm_item": item.odm_item.uid if item.odm_item else None,
                }
            )

        value_activity_items = []
        for activity_item_node in value_item_nodes:
            item_class_uid = activity_item_node.has_activity_item_class.get().uid
            unit_nodes = activity_item_node.has_unit_definition.all()
            ct_terms = [
                {
                    "uid": term_context.has_selected_term.single().uid,
                    "codelist_uid": term_context.has_selected_codelist.single().uid,
                }
                for term_context in activity_item_node.has_ct_term.all()
            ]
            odm_form_node = activity_item_node.has_odm_form.single()
            odm_item_group_node = activity_item_node.has_odm_item_group.single()
            odm_item_node = activity_item_node.has_odm_item.single()
            value_activity_items.append(
                {
                    "is_adam_param_specific": activity_item_node.is_adam_param_specific,
                    "class": item_class_uid,
                    "units": {unit_node.uid for unit_node in unit_nodes},
                    "terms": {
                        (ct_term["uid"], ct_term["codelist_uid"])
                        for ct_term in ct_terms
                    },
                    "odm_form": (
                        odm_form_node.has_root.single().uid if odm_form_node else None
                    ),
                    "odm_item_group": (
                        odm_item_group_node.has_root.single().uid
                        if odm_item_group_node
                        else None
                    ),
                    "odm_item": (
                        odm_item_node.has_root.single().uid if odm_item_node else None
                    ),
                }
            )
        for item in ar_activity_items:
            if item not in value_activity_items:
                return True
        for item in value_activity_items:
            if item not in ar_activity_items:
                return True
        return False

    def _has_grouping_data_changed(self, ar_groupings, activity_instance_value):
        value_group_pairs = []
        for activity_grouping_node in activity_instance_value.has_activity.all():
            if not activity_grouping_node.has_grouping.get().has_latest_value.single():
                # The linked ActivityValue is not the latest.
                # We need to return True, so that the ActivityInstanceValue
                # gets updated to use the new ActivityValue.
                return True
            activity_valid_group_nodes = activity_grouping_node.in_subgroup.all()
            for activity_valid_group_node in activity_valid_group_nodes:
                value_group_pairs.append(
                    (
                        activity_grouping_node.has_grouping.get()
                        .has_version.single()
                        .uid,
                        activity_valid_group_node.has_group.get()
                        .has_version.single()
                        .uid,
                        activity_valid_group_node.in_group.get()
                        .has_version.single()
                        .uid,
                    )
                )

        ar_group_pairs = [
            (
                grouping.activity_uid,
                grouping.activity_subgroup_uid,
                grouping.activity_group_uid,
            )
            for grouping in ar_groupings
        ]
        for pair in ar_group_pairs:
            if pair not in value_group_pairs:
                return True
        for pair in value_group_pairs:
            if pair not in ar_group_pairs:
                return True
        return False

    def _has_data_changed(
        self, ar: ActivityInstanceAR, value: ActivityInstanceValue
    ) -> bool:
        are_concept_properties_changed = super()._has_data_changed(ar=ar, value=value)
        are_props_changed = (
            ar.concept_vo.molecular_weight != value.molecular_weight
            or ar.concept_vo.topic_code != value.topic_code
            or ar.concept_vo.adam_param_code != value.adam_param_code
            or bool(ar.concept_vo.is_research_lab) != bool(value.is_research_lab)
            or bool(ar.concept_vo.is_required_for_activity)
            != bool(value.is_required_for_activity)
            or bool(ar.concept_vo.is_default_selected_for_activity)
            != bool(value.is_default_selected_for_activity)
            or bool(ar.concept_vo.is_data_sharing) != bool(value.is_data_sharing)
            or bool(ar.concept_vo.is_legacy_usage) != bool(value.is_legacy_usage)
            or bool(ar.concept_vo.is_derived) != bool(value.is_derived)
            or ar.concept_vo.legacy_description != value.legacy_description
        )

        item_data_changed = self._has_item_data_changed(
            ar.concept_vo.activity_items, value.contains_activity_item.all()
        )

        # Is this a final version? If yes, we skip the grouping data check
        # to avoid creating new values nodes when just creating a new draft.
        root_for_final_value = value.has_version.match(
            status__in=[LibraryItemStatus.FINAL.value, LibraryItemStatus.RETIRED.value],
            end_date__isnull=True,
        )

        if not root_for_final_value:
            grouping_data_changed = self._has_grouping_data_changed(
                ar.concept_vo.activity_groupings, value
            )
        else:
            grouping_data_changed = False

        are_rels_changed = (
            ar.concept_vo.activity_instance_class_uid
            != value.activity_instance_class.get().uid
            or grouping_data_changed
            or item_data_changed
        )
        return are_concept_properties_changed or are_props_changed or are_rels_changed

    def copy_activity_instance_and_recreate_activity_groupings(
        self, activity_instance: ActivityInstanceAR, author_id: str
    ) -> None:
        query = """
            MATCH (concept_root:ActivityInstanceRoot {uid:$activity_instance_uid})-[status_relationship:LATEST]->(concept_value:ActivityInstanceValue)
            CALL apoc.refactor.cloneNodes([concept_value])
            YIELD input, output, error"""
        merge_query = f"""
            MERGE (concept_root)-[:LATEST]->(output)
            MERGE (concept_root)-[:LATEST_{activity_instance.item_metadata.status.value.upper()}]->(output)
            MERGE (concept_root)-[new_has_version:HAS_VERSION]->(output)"""
        query += self._update_versioning_relationship_query(
            status=activity_instance.item_metadata.status.value, merge_query=merge_query
        )
        query += """

            WITH library, concept_root, concept_value, output
            MATCH (concept_value)-[:ACTIVITY_INSTANCE_CLASS]->(activity_instance_class:ActivityInstanceClassRoot)
            OPTIONAL MATCH (concept_value)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item:ActivityItem)
            WITH library, concept_root, activity_item, activity_instance_class, output
            MERGE (output)-[:ACTIVITY_INSTANCE_CLASS]->(activity_instance_class)
            WITH library, concept_root, output, activity_item
            CALL apoc.do.case([
                activity_item IS NOT NULL,
                'MERGE (output)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item) RETURN output'
            ],
            '',
            {
                activity_item: activity_item,
                output: output
            })
            YIELD value
            UNWIND range(0, size($activity_uids)-1) AS idx
            MATCH (activity_grouping:ActivityGrouping)<-[:HAS_GROUPING]-(:ActivityValue)<-[:LATEST_FINAL]-(:ActivityRoot {uid:$activity_uids[idx]})
            MATCH (activity_grouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)-[:IN_GROUP]->(:ActivityGroupValue)<-[:HAS_VERSION]-(:ActivityGroupRoot {uid:$activity_group_uids[idx]})
            MATCH (activity_valid_group)<-[:HAS_GROUP]-(:ActivitySubGroupValue)<-[:HAS_VERSION]-(:ActivitySubGroupRoot {uid:$activity_subgroup_uids[idx]})
            WITH library, concept_root, output, activity_grouping
            MERGE (output)-[:HAS_ACTIVITY]->(activity_grouping)
            RETURN concept_root, output, library
        """

        db.cypher_query(
            query,
            params={
                "activity_instance_uid": activity_instance.uid,
                "new_status": activity_instance.item_metadata.status.value,
                "new_version": activity_instance.item_metadata.version,
                "start_date": datetime.datetime.now(datetime.timezone.utc),
                "change_description": "Copying previous ActivityInstanceValue node and updating ActivityGrouping nodes",
                "author_id": author_id,
                "activity_uids": [
                    activity_instance.activity_uid
                    for activity_instance in activity_instance.concept_vo.activity_groupings
                ],
                "activity_subgroup_uids": [
                    activity_instance.activity_subgroup_uid
                    for activity_instance in activity_instance.concept_vo.activity_groupings
                ],
                "activity_group_uids": [
                    activity_instance.activity_group_uid
                    for activity_instance in activity_instance.concept_vo.activity_groupings
                ],
            },
        )

    def _create_aggregate_root_instance_from_cypher_result(
        self, input_dict: dict[str, Any]
    ) -> ActivityInstanceAR:
        major, minor = input_dict["version"].split(".")
        activity_instance_ar = self.aggregate_class.from_repository_values(
            uid=input_dict["uid"],
            concept_vo=self.value_object_class.from_repository_values(
                nci_concept_id=input_dict.get("nci_concept_id"),
                nci_concept_name=input_dict.get("nci_concept_name"),
                name=input_dict["name"],
                name_sentence_case=input_dict["name_sentence_case"],
                activity_instance_class_uid=input_dict.get(
                    "activity_instance_class"
                ).get("uid"),
                activity_instance_class_name=input_dict.get(
                    "activity_instance_class"
                ).get("name"),
                definition=input_dict["definition"],
                abbreviation=input_dict.get("abbreviation"),
                is_research_lab=input_dict.get("is_research_lab", False),
                molecular_weight=input_dict.get("molecular_weight"),
                topic_code=input_dict["topic_code"],
                adam_param_code=input_dict.get("adam_param_code"),
                is_required_for_activity=input_dict.get(
                    "is_required_for_activity", False
                ),
                is_default_selected_for_activity=input_dict.get(
                    "is_default_selected_for_activity", False
                ),
                is_data_sharing=input_dict.get("is_data_sharing", False),
                is_legacy_usage=input_dict.get("is_legacy_usage", False),
                is_derived=input_dict.get("is_derived", False),
                legacy_description=input_dict.get("legacy_description"),
                activity_groupings=[
                    ActivityInstanceGroupingVO(
                        activity_group_uid=activity_grouping.get("activity_group").get(
                            "uid"
                        ),
                        activity_group_name=activity_grouping.get("activity_group").get(
                            "name"
                        ),
                        activity_group_version=f"{activity_grouping.get('activity_group').get('major_version')}.{activity_grouping.get('activity_group').get('minor_version')}",
                        activity_subgroup_uid=activity_grouping.get(
                            "activity_subgroup"
                        ).get("uid"),
                        activity_subgroup_name=activity_grouping.get(
                            "activity_subgroup"
                        ).get("name"),
                        activity_subgroup_version=f"{activity_grouping.get('activity_subgroup').get('major_version')}.{activity_grouping.get('activity_subgroup').get('minor_version')}",
                        activity_uid=activity_grouping.get("activity").get("uid"),
                        activity_name=activity_grouping.get("activity").get("name"),
                        activity_version=f"{activity_grouping.get('activity').get('major_version')}.{activity_grouping.get('activity').get('minor_version')}",
                    )
                    for activity_grouping in input_dict.get("activity_groupings")
                ],
                activity_items=[
                    ActivityItemVO.from_repository_values(
                        is_adam_param_specific=activity_item.get(
                            "is_adam_param_specific"
                        ),
                        activity_item_class_uid=activity_item.get(
                            "activity_item_class_uid"
                        ),
                        activity_item_class_name=activity_item.get(
                            "activity_item_class_name"
                        ),
                        ct_terms=[
                            CTTermItem(
                                uid=term["uid"],
                                name=term["name"],
                                codelist_uid=term["codelist_uid"],
                            )
                            for term in activity_item.get("ct_terms")
                        ],
                        unit_definitions=[
                            CompactUnitDefinition(
                                uid=unit["uid"],
                                name=unit["name"],
                                dimension_name=unit["dimension_name"],
                            )
                            for unit in activity_item.get("unit_definitions")
                        ],
                        odm_form=CompactOdmForm(
                            uid=(
                                activity_item["odm_form"]["uid"]
                                if activity_item["odm_form"]
                                else None
                            ),
                            oid=(
                                activity_item["odm_form"]["oid"]
                                if activity_item["odm_form"]
                                else None
                            ),
                            name=(
                                activity_item["odm_form"]["name"]
                                if activity_item["odm_form"]
                                else None
                            ),
                        ),
                        odm_item_group=CompactOdmItemGroup(
                            uid=(
                                activity_item["odm_item_group"]["uid"]
                                if activity_item["odm_item_group"]
                                else None
                            ),
                            oid=(
                                activity_item["odm_item_group"]["oid"]
                                if activity_item["odm_item_group"]
                                else None
                            ),
                            name=(
                                activity_item["odm_item_group"]["name"]
                                if activity_item["odm_item_group"]
                                else None
                            ),
                        ),
                        odm_item=CompactOdmItem(
                            uid=(
                                activity_item["odm_item"]["uid"]
                                if activity_item["odm_item"]
                                else None
                            ),
                            oid=(
                                activity_item["odm_item"]["oid"]
                                if activity_item["odm_item"]
                                else None
                            ),
                            name=(
                                activity_item["odm_item"]["name"]
                                if activity_item["odm_item"]
                                else None
                            ),
                        ),
                    )
                    for activity_item in input_dict.get("activity_items", [])
                ],
                activity_name=input_dict.get("activity_name"),
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
                end_date=convert_to_datetime(value=input_dict.get("end_date")),
                major_version=int(major),
                minor_version=int(minor),
            ),
        )
        return activity_instance_ar

    def _create_aggregate_root_instance_from_version_root_relationship_and_value(
        self,
        root: ActivityInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ActivityInstanceValue,
        **_kwargs,
    ) -> ActivityInstanceAR:
        activity_instance_class = value.activity_instance_class.get()
        activity_items = value.contains_activity_item.all()
        activity_item_vos = []
        for activity_item in activity_items:
            activity_item_class_root = (
                activity_item.has_activity_item_class.get_or_none()
            )
            ct_terms = []
            unit_definitions = []
            for unit in activity_item.has_unit_definition.all():
                if (
                    ct_dimension := unit.has_version.single()
                    .has_ct_dimension.single()
                    .has_selected_term.single()
                ):
                    dimension_name = (
                        ct_dimension.has_name_root.single()
                        .has_latest_value.single()
                        .name
                    )
                else:
                    dimension_name = None

                unit_definitions.append(
                    CompactUnitDefinition(
                        uid=unit.uid,
                        name=unit.has_version.single().name,
                        dimension_name=dimension_name,
                    )
                )
            for term_context in activity_item.has_ct_term.all():
                term_root = term_context.has_selected_term.single()
                ct_terms.append(
                    CTTermItem(
                        uid=term_root.uid,
                        name=term_root.has_name_root.single().has_version.single().name,
                        codelist_uid=term_context.has_selected_codelist.single().uid,
                    )
                )
            odm_form = None
            odm_form_value = activity_item.has_odm_form.single()
            if odm_form_value:
                odm_form_root = odm_form_value.has_root.single()
                if odm_form_root:
                    odm_form = CompactOdmForm(
                        uid=odm_form_root.uid,
                        oid=odm_form_value.oid,
                        name=odm_form_value.name,
                    )
            odm_item_group = None
            odm_item_group_value = activity_item.has_odm_item_group.single()
            if odm_item_group_value:
                odm_item_group_root = odm_item_group_value.has_root.single()
                if odm_item_group_root:
                    odm_item_group = CompactOdmItemGroup(
                        uid=odm_item_group_root.uid,
                        oid=odm_item_group_value.oid,
                        name=odm_item_group_value.name,
                    )
            odm_item = None
            odm_item_value = activity_item.has_odm_item.single()
            if odm_item_value:
                odm_item_root = odm_item_value.has_root.single()
                if odm_item_root:
                    odm_item = CompactOdmItem(
                        uid=odm_item_root.uid,
                        oid=odm_item_value.oid,
                        name=odm_item_value.name,
                    )
            activity_item_vos.append(
                ActivityItemVO.from_repository_values(
                    is_adam_param_specific=activity_item.is_adam_param_specific,
                    activity_item_class_uid=activity_item_class_root.uid,
                    activity_item_class_name=activity_item_class_root.has_latest_value.get_or_none().name,
                    ct_terms=ct_terms,
                    unit_definitions=unit_definitions,
                    odm_form=odm_form,
                    odm_item_group=odm_item_group,
                    odm_item=odm_item,
                )
            )
        activity_groupings_nodes = value.has_activity.all()
        activity_groupings = []
        activity_name = None
        for activity_grouping in activity_groupings_nodes:
            activity_value_node = activity_grouping.has_grouping.get()
            # ActivityInstance can only link to a single Activity node then it's safe to take a activity_name
            # from the random ActivityValue node related to any ActivityGroupings node linked to ActivityInstance
            activity_name = activity_value_node.name
            # Activity
            activity_root = activity_value_node.has_version.single()
            all_activity_rels = activity_value_node.has_version.all_relationships(
                activity_root
            )
            latest_activity = max(
                all_activity_rels, key=lambda r: version_string_to_tuple(r.version)
            )

            activity_valid_groups = activity_grouping.in_subgroup.all()
            for activity_valid_group in activity_valid_groups:
                # ActivityGroup
                activity_group_value = activity_valid_group.in_group.get()
                activity_group_root = activity_group_value.has_version.single()
                all_group_rels = activity_group_value.has_version.all_relationships(
                    activity_group_root
                )
                latest_group = max(
                    all_group_rels, key=lambda r: version_string_to_tuple(r.version)
                )
                # ActivitySubGroup
                activity_subgroup_value = activity_valid_group.has_group.get()
                activity_subgroup_root = activity_subgroup_value.has_version.single()
                all_subgroup_rels = (
                    activity_subgroup_value.has_version.all_relationships(
                        activity_subgroup_root
                    )
                )
                latest_subgroup = max(
                    all_subgroup_rels, key=lambda r: version_string_to_tuple(r.version)
                )

                activity_groupings.append(
                    ActivityInstanceGroupingVO(
                        activity_group_uid=activity_group_root.uid,
                        activity_group_version=latest_group.version,
                        activity_subgroup_uid=activity_subgroup_root.uid,
                        activity_subgroup_version=latest_subgroup.version,
                        activity_uid=activity_root.uid,
                        activity_version=latest_activity.version,
                    )
                )

        return self.aggregate_class.from_repository_values(
            uid=root.uid,
            concept_vo=self.value_object_class.from_repository_values(
                nci_concept_id=value.nci_concept_id,
                nci_concept_name=value.nci_concept_name,
                name=value.name,
                name_sentence_case=value.name_sentence_case,
                activity_instance_class_uid=activity_instance_class.uid,
                activity_instance_class_name=activity_instance_class.has_latest_value.get().name,
                definition=value.definition,
                abbreviation=value.abbreviation,
                is_research_lab=(
                    value.is_research_lab if value.is_research_lab else False
                ),
                molecular_weight=value.molecular_weight,
                topic_code=value.topic_code,
                adam_param_code=value.adam_param_code,
                is_required_for_activity=(
                    value.is_required_for_activity
                    if value.is_required_for_activity
                    else False
                ),
                is_default_selected_for_activity=(
                    value.is_default_selected_for_activity
                    if value.is_default_selected_for_activity
                    else False
                ),
                is_data_sharing=(
                    value.is_data_sharing if value.is_data_sharing else False
                ),
                is_legacy_usage=(
                    value.is_legacy_usage if value.is_legacy_usage else False
                ),
                is_derived=value.is_derived if value.is_derived else False,
                legacy_description=value.legacy_description,
                activity_groupings=activity_groupings,
                activity_items=activity_item_vos,
                activity_name=activity_name,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=lambda _: library.is_editable,
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def _create_ar(
        self,
        root: ActivityInstanceRoot,
        library: Library,
        relationship: VersionRelationship,
        value: ActivityInstanceValue,
        **_kwargs,
    ) -> ActivityInstanceAR:
        activity_instance_objects = _kwargs["activity_instance_root"]
        activity_instance_class = activity_instance_objects["activity_instance_class"]
        activity_item_vos = []
        for activity_item in activity_instance_objects["activity_items"]:
            ct_terms = []
            unit_definitions = []
            for unit in activity_item["unit_definitions"]:
                unit_definitions.append(
                    CompactUnitDefinition(
                        uid=unit["uid"],
                        name=unit["name"],
                    )
                )
            for term in activity_item["ct_terms"]:
                ct_terms.append(
                    CTTermItem(
                        uid=term["uid"],
                        name=term["name"],
                        codelist_uid=term["codelist_uid"],
                    )
                )
            odm_form = None
            if activity_item["odm_form"]:
                odm_form = CompactOdmForm(
                    uid=activity_item["odm_form"]["uid"],
                    oid=activity_item["odm_form"]["oid"],
                    name=activity_item["odm_form"]["name"],
                )
            odm_item_group = None
            if activity_item["odm_item_group"]:
                odm_item_group = CompactOdmItemGroup(
                    uid=activity_item["odm_item_group"]["uid"],
                    oid=activity_item["odm_item_group"]["oid"],
                    name=activity_item["odm_item_group"]["name"],
                )
            odm_item = None
            if activity_item["odm_item"]:
                odm_item = CompactOdmItem(
                    uid=activity_item["odm_item"]["uid"],
                    oid=activity_item["odm_item"]["oid"],
                    name=activity_item["odm_item"]["name"],
                )
            activity_item_vos.append(
                ActivityItemVO.from_repository_values(
                    is_adam_param_specific=activity_item["is_adam_param_specific"],
                    activity_item_class_uid=activity_item["activity_item_class_uid"],
                    activity_item_class_name=activity_item["activity_item_class_name"],
                    ct_terms=ct_terms,
                    unit_definitions=unit_definitions,
                    odm_form=odm_form,
                    odm_item_group=odm_item_group,
                    odm_item=odm_item,
                )
            )
        activity_groupings = []
        for activity_grouping in activity_instance_objects[
            "activity_instance_groupings"
        ]:
            activity_groupings.append(
                ActivityInstanceGroupingVO(
                    activity_group_uid=activity_grouping["activity_group"].get("uid"),
                    activity_group_name=activity_grouping["activity_group"].get("name"),
                    activity_group_version=f"{activity_grouping['activity_group'].get('major_version')}.{activity_grouping['activity_group'].get('minor_version')}",
                    activity_subgroup_uid=activity_grouping["activity_subgroup"].get(
                        "uid"
                    ),
                    activity_subgroup_name=activity_grouping["activity_subgroup"].get(
                        "name"
                    ),
                    activity_subgroup_version=f"{activity_grouping['activity_subgroup'].get('major_version')}.{activity_grouping['activity_subgroup'].get('minor_version')}",
                    activity_uid=activity_grouping["activity"].get("uid"),
                    activity_name=activity_grouping["activity"].get("name"),
                    activity_version=f"{activity_grouping['activity'].get('major_version')}.{activity_grouping['activity'].get('minor_version')}",
                )
            )
        return self.aggregate_class.from_repository_values(
            uid=root.uid,
            concept_vo=self.value_object_class.from_repository_values(
                nci_concept_id=value.nci_concept_id,
                nci_concept_name=value.nci_concept_name,
                name=value.name,
                name_sentence_case=value.name_sentence_case,
                activity_instance_class_uid=activity_instance_class[
                    "activity_instance_class_uid"
                ],
                activity_instance_class_name=activity_instance_class[
                    "activity_instance_class_name"
                ],
                definition=value.definition,
                abbreviation=value.abbreviation,
                is_research_lab=(
                    value.is_research_lab if value.is_research_lab else False
                ),
                molecular_weight=value.molecular_weight,
                topic_code=value.topic_code,
                adam_param_code=value.adam_param_code,
                is_required_for_activity=(
                    value.is_required_for_activity
                    if value.is_required_for_activity
                    else False
                ),
                is_default_selected_for_activity=(
                    value.is_default_selected_for_activity
                    if value.is_default_selected_for_activity
                    else False
                ),
                is_data_sharing=(
                    value.is_data_sharing if value.is_data_sharing else False
                ),
                is_legacy_usage=(
                    value.is_legacy_usage if value.is_legacy_usage else False
                ),
                is_derived=value.is_derived if value.is_derived else False,
                legacy_description=value.legacy_description,
                activity_groupings=activity_groupings,
                activity_items=activity_item_vos,
            ),
            library=LibraryVO.from_input_values_2(
                library_name=library.name,
                is_library_editable_callback=lambda _: library.is_editable,
            ),
            item_metadata=self._library_item_metadata_vo_from_relation(relationship),
        )

    def specific_alias_clause(self, **kwargs) -> str:
        return """
        WITH *,
            concept_value.nci_concept_name AS nci_concept_name,
            concept_value.molecular_weight AS molecular_weight,
            concept_value.topic_code AS topic_code,
            concept_value.adam_param_code AS adam_param_code,
            coalesce(concept_value.is_research_lab, false) AS is_research_lab,
            coalesce(concept_value.is_required_for_activity, false) AS is_required_for_activity,
            coalesce(concept_value.is_default_selected_for_activity, false) AS is_default_selected_for_activity,
            coalesce(concept_value.is_data_sharing, false) AS is_data_sharing,
            coalesce(concept_value.is_legacy_usage, false) AS is_legacy_usage,
            coalesce(concept_value.is_derived, false) AS is_derived,
            concept_value.legacy_description AS legacy_description,
            
            head([(concept_value)-[:ACTIVITY_INSTANCE_CLASS]->
            (activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
                | {uid:activity_instance_class_root.uid, name:activity_instance_class_value.name}]) AS activity_instance_class,
            [(concept_value)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item:ActivityItem)
            <-[:HAS_ACTIVITY_ITEM]-(activity_item_class_root:ActivityItemClassRoot)-[:LATEST]->
            (activity_item_class_value:ActivityItemClassValue)
                | {
                    activity_item_class_uid: activity_item_class_root.uid,
                    activity_item_class_name: activity_item_class_value.name,
                    ct_terms: COLLECT {
                        MATCH (activity_item)-[:HAS_CT_TERM]->(ct_term_context:CTTermContext)
                        -[:HAS_SELECTED_TERM]->(term_root:CTTermRoot)
                        -[:HAS_NAME_ROOT]->(term_name_root:CTTermNameRoot)
                        -[:LATEST]->(term_name_value:CTTermNameValue)
                        MATCH (ct_term_context)-[:HAS_SELECTED_CODELIST]->(codelist_root:CTCodelistRoot)
                        RETURN {uid: term_root.uid, name: term_name_value.name, codelist_uid: codelist_root.uid}
                    },
                    unit_definitions: [(activity_item)-[:HAS_UNIT_DEFINITION]->(unit_definition_root:UnitDefinitionRoot)-[:LATEST]->(unit_definition_value:UnitDefinitionValue)-[:HAS_CT_DIMENSION]-(:CTTermRoot)-[:HAS_NAME_ROOT]->(CTTermNamesRoot)-[:LATEST]->(dimension_value:CTTermNameValue) | {uid: unit_definition_root.uid, name: unit_definition_value.name, dimension_name: dimension_value.name}],
                    is_adam_param_specific: activity_item.is_adam_param_specific,
                    odm_form: head([(activity_item)-[:HAS_ODM_FORM]->(odm_form_value:OdmFormValue)<-[:HAS_VERSION]-(odm_form_root:OdmFormRoot) | {uid: odm_form_root.uid, oid: odm_form_value.oid, name: odm_form_value.name}]),
                    odm_item_group: head([(activity_item)-[:HAS_ODM_ITEM_GROUP]->(odm_item_group_value:OdmItemGroupValue)<-[:HAS_VERSION]-(odm_item_group_root:OdmItemGroupRoot) | {uid: odm_item_group_root.uid, oid: odm_item_group_value.oid, name: odm_item_group_value.name}]),
                    odm_item: head([(activity_item)-[:HAS_ODM_ITEM]->(odm_item_value:OdmItemValue)<-[:HAS_VERSION]-(odm_item_root:OdmItemRoot) | {uid: odm_item_root.uid, oid: odm_item_value.oid, name: odm_item_value.name}])
                }] AS activity_items,
            head([(concept_value)-[:HAS_ACTIVITY]->(activity_grouping)<-[:HAS_GROUPING]-(activity_value) | activity_value.name]) as activity_name,
            apoc.coll.toSet([(concept_value)-[:HAS_ACTIVITY]->(activity_grouping:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)
            <-[:HAS_GROUP]-(activity_subgroup_value)<-[:HAS_VERSION]-(activity_subgroup_root:ActivitySubGroupRoot)
            | {
                activity: head(apoc.coll.sortMulti([(activity_grouping)<-[:HAS_GROUPING]-(activity_value:ActivityValue)<-[has_version:HAS_VERSION]-
                    (activity_root:ActivityRoot) | 
                    {
                        uid: activity_root.uid,
                        name: activity_value.name,
                        major_version: toInteger(split(has_version.version,'.')[0]),
                        minor_version: toInteger(split(has_version.version,'.')[1])
                    }], ['major_version', 'minor_version'])),
                activity_subgroup: head(apoc.coll.sortMulti([(activity_valid_group)<-[:HAS_GROUP]-(activity_subgroup_value:ActivitySubGroupValue)<-[has_version:HAS_VERSION]-
                    (activity_subgroup_root:ActivitySubGroupRoot) | 
                    {
                        uid: activity_subgroup_root.uid,
                        name: activity_subgroup_value.name,
                        major_version: toInteger(split(has_version.version,'.')[0]),
                        minor_version: toInteger(split(has_version.version,'.')[1])
                    }], ['major_version', 'minor_version'])), 
                activity_group: head(apoc.coll.sortMulti([(activity_valid_group)-[:IN_GROUP]-(activity_group_value:ActivityGroupValue)<-[has_version:HAS_VERSION]-
                    (activity_group_root:ActivityGroupRoot) | 
                    {
                        uid: activity_group_root.uid,
                        name: activity_group_value.name,
                        major_version: toInteger(split(has_version.version,'.')[0]),
                        minor_version: toInteger(split(has_version.version,'.')[1])
                    }], ['major_version', 'minor_version']))
            }]) AS activity_groupings
        """

    def create_query_filter_statement(
        self, library: str | None = None, **kwargs
    ) -> tuple[str, dict[Any, Any]]:
        (
            filter_statements_from_concept,
            filter_query_parameters,
        ) = super().create_query_filter_statement(library=library, **kwargs)
        filter_parameters = []
        if kwargs.get("activity_instance_names") is not None:
            activity_instance_names = kwargs.get("activity_instance_names")
            filter_by_activity_instance_names = (
                "concept_value.name IN $activity_instance_names"
            )
            filter_parameters.append(filter_by_activity_instance_names)
            filter_query_parameters["activity_instance_names"] = activity_instance_names
        if kwargs.get("activity_names") is not None:
            activity_names = kwargs.get("activity_names")
            filter_by_activity_names = (
                "size([(concept_value)-[:HAS_ACTIVITY]->(:ActivityGrouping)<-[:HAS_GROUPING]-(activity_hierarchy_value) "
                "WHERE activity_hierarchy_value.name IN $activity_names | activity_hierarchy_value.name]) > 0"
            )
            filter_parameters.append(filter_by_activity_names)
            filter_query_parameters["activity_names"] = activity_names
        if kwargs.get("activity_subgroup_names") is not None:
            activity_subgroup_names = kwargs.get("activity_subgroup_names")
            filter_by_activity_subgroup_names = (
                "size([(concept_value)-[:HAS_ACTIVITY]->(:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)"
                "<-[:HAS_GROUP]-(activity_subgroup_value:ActivitySubGroupValue) "
                "WHERE activity_subgroup_value.name IN $activity_subgroup_names | activity_subgroup_value.name]) > 0"
            )
            filter_parameters.append(filter_by_activity_subgroup_names)
            filter_query_parameters["activity_subgroup_names"] = activity_subgroup_names
        if kwargs.get("activity_group_names") is not None:
            activity_group_names = kwargs.get("activity_group_names")
            filter_by_activity_group_names = (
                "size([(concept_value)-[:HAS_ACTIVITY]->(:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)"
                "-[:IN_GROUP]->(activity_group_value:ActivityGroupValue) "
                "WHERE activity_group_value.name IN $activity_group_names | activity_group_value.name]) > 0"
            )
            filter_parameters.append(filter_by_activity_group_names)
            filter_query_parameters["activity_group_names"] = activity_group_names
        if kwargs.get("activity_instance_class_names") is not None:
            instance_class_names = kwargs.get("activity_instance_class_names")
            filter_by_instance_classes = (
                "size([(concept_value)-[:ACTIVITY_INSTANCE_CLASS]->(:ActivityInstanceClassRoot)"
                "-[:LATEST]->(instance_class_value:ActivityInstanceClassValue)"
                "WHERE instance_class_value.name IN $activity_instance_class_names | instance_class_value.name]) > 0"
            )
            filter_parameters.append(filter_by_instance_classes)
            filter_query_parameters["activity_instance_class_names"] = (
                instance_class_names
            )
        extended_filter_statements = " AND ".join(filter_parameters)
        if filter_statements_from_concept != "":
            if len(extended_filter_statements) > 0:
                filter_statements_to_return = " AND ".join(
                    [filter_statements_from_concept, extended_filter_statements]
                )
            else:
                filter_statements_to_return = filter_statements_from_concept
        else:
            filter_statements_to_return = (
                "WHERE " + extended_filter_statements
                if len(extended_filter_statements) > 0
                else ""
            )
        return filter_statements_to_return, filter_query_parameters

    def get_activity_instance_overview(
        self, uid: str, version: str | None = None
    ) -> dict[str, Any]:
        if version:
            params = {"uid": uid, "version": version}
            match = """
                    MATCH (activity_instance_root:ActivityInstanceRoot {uid:$uid})
                    CALL {
                        WITH activity_instance_root
                        MATCH (activity_instance_root)-[hv:HAS_VERSION {version:$version}]->(aiv:ActivityInstanceValue)
                        WITH hv, aiv
                        ORDER BY
                            toInteger(split(hv.version, '.')[0]) ASC,
                            toInteger(split(hv.version, '.')[1]) ASC,
                            hv.end_date ASC,
                            hv.start_date ASC
                        WITH collect(hv) as hvs, collect (aiv) as aivs
                        RETURN last(hvs) as has_version, last(aivs) as activity_instance_value
                    }
                    """
        else:
            params = {"uid": uid}
            match = """
                    MATCH (activity_instance_root:ActivityInstanceRoot {uid:$uid})-[:LATEST]->(activity_instance_value:ActivityInstanceValue)
                    CALL {
                        WITH activity_instance_root, activity_instance_value
                        MATCH (activity_instance_root)-[hv:HAS_VERSION]-(activity_instance_value)
                        WITH hv
                        ORDER BY
                            toInteger(split(hv.version, '.')[0]) ASC,
                            toInteger(split(hv.version, '.')[1]) ASC,
                            hv.end_date ASC,
                            hv.start_date ASC
                        WITH collect(hv) as hvs
                        RETURN last(hvs) as has_version
                    }
                    """
        query = (
            match
            + """
        WITH activity_instance_root,activity_instance_value, has_version,
            head([(library)-[:CONTAINS_CONCEPT]->(activity_instance_root) | library.name]) AS instance_library_name,
            head([(activity_instance_value)-[:ACTIVITY_INSTANCE_CLASS]->
            (activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue) 
            | activity_instance_class_value]) AS activity_instance_class,
            [(activity_instance_root)-[versions:HAS_VERSION]->(:ActivityInstanceValue) | versions.version] as all_versions
        CALL {
            WITH activity_instance_value
            MATCH (activity_instance_value)-[:HAS_ACTIVITY]->(activity_grouping:ActivityGrouping)
            // Get the latest activity version for this grouping
            CALL {
                WITH activity_grouping
                MATCH (activity_grouping)<-[:HAS_GROUPING]-(av:ActivityValue)<-[hav:HAS_VERSION]-(ar:ActivityRoot)
                WITH av, hav, ar
                ORDER BY 
                    toInteger(split(hav.version, '.')[0]) DESC,
                    toInteger(split(hav.version, '.')[1]) DESC,
                    hav.start_date DESC
                WITH ar, collect(av) AS avs, collect(hav) AS havs
                WITH ar, head(avs) AS activity_value, head(havs) AS latest_version
                RETURN ar.uid AS activity_uid, activity_value, 
                       latest_version { .version, .status, .start_date, .end_date} AS activity_version_info
            }
            WITH activity_grouping, activity_uid, activity_value, activity_version_info,
                 [(activity_value)<-[hav:HAS_VERSION]-(activity_root:ActivityRoot) | hav { .version, .status, .start_date, .end_date}] AS activity_versions,
                 head([(activity_value)<-[:HAS_VERSION]-(:ActivityRoot)<-[:CONTAINS_CONCEPT]-(library) | library.name]) AS activity_library_name
            
            // Get the latest subgroup version using subquery
            CALL {
                WITH activity_grouping
                OPTIONAL MATCH (activity_grouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)<-[:HAS_GROUP]-(sgv:ActivitySubGroupValue)<-[sgv_rel:HAS_VERSION]-(sgr:ActivitySubGroupRoot)
                WITH sgr, sgv, sgv_rel
                ORDER BY 
                    toInteger(split(sgv_rel.version, '.')[0]) DESC,
                    toInteger(split(sgv_rel.version, '.')[1]) DESC,
                    sgv_rel.start_date DESC
                WITH sgr.uid AS subgroup_uid, 
                     collect(sgv)[0] AS subgroup_value,
                     collect(sgv_rel { .version, .status, .start_date, .end_date})[0] AS subgroup_version
                RETURN subgroup_uid, subgroup_value, subgroup_version
            }
            
            // Get the latest group version using subquery
            CALL {
                WITH activity_grouping
                OPTIONAL MATCH (activity_grouping)-[:IN_SUBGROUP]->(avg)-[:IN_GROUP]->(agv:ActivityGroupValue)<-[agv_rel:HAS_VERSION]-(agr:ActivityGroupRoot)
                WITH agr, agv, agv_rel
                ORDER BY 
                    toInteger(split(agv_rel.version, '.')[0]) DESC,
                    toInteger(split(agv_rel.version, '.')[1]) DESC,
                    agv_rel.start_date DESC
                WITH agr.uid AS group_uid,
                     collect(agv)[0] AS group_value,
                     collect(agv_rel { .version, .status, .start_date, .end_date})[0] AS group_version
                RETURN group_uid, group_value, group_version
            }
                 
            WITH activity_grouping, {
                    uid: activity_uid,
                    activity_value: activity_value,
                    activity_versions: activity_versions,
                    activity_library_name: activity_library_name,
                    selected_activity_version: activity_version_info,
                    activity_subgroup_value: subgroup_value,
                    activity_subgroup_uid: subgroup_uid,
                    activity_subgroup_versions: CASE WHEN subgroup_version IS NULL THEN [] ELSE [subgroup_version] END,
                    selected_subgroup_version: subgroup_version,
                    activity_group_value: group_value,
                    activity_group_uid: group_uid,
                    activity_group_versions: CASE WHEN group_version IS NULL THEN [] ELSE [group_version] END,
                    selected_group_version: group_version
                } AS hierarchy_item
            RETURN collect(hierarchy_item) AS hierarchy
        }
        WITH *,
            apoc.coll.toSet([(activity_instance_value)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item)
            <-[HAS_ACTIVITY_ITEM]-(activity_item_class_root)-[:LATEST]->(activity_item_class_value) | 
            {
                activity_item_class: activity_item_class_value,
                activity_item_class_role: head([(activity_item_class_value)-[:HAS_ROLE]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(role_value) | role_value.name]),
                activity_item_class_data_type: head([(activity_item_class_value)-[:HAS_DATA_TYPE]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(data_type_value) | data_type_value.name]),
                activity_item: activity_item,
                ct_terms: COLLECT {
                    MATCH (activity_item)-[:HAS_CT_TERM]->(ct_term_context:CTTermContext)
                    -[:HAS_SELECTED_TERM]->(term_root:CTTermRoot)
                    -[:HAS_NAME_ROOT]->(term_name_root:CTTermNameRoot)
                    -[:LATEST]->(term_name_value:CTTermNameValue)
                    MATCH (ct_term_context)-[:HAS_SELECTED_CODELIST]->(codelist_root:CTCodelistRoot)
                    RETURN {uid: term_root.uid, name: term_name_value.name, codelist_uid: codelist_root.uid}
                },
                unit_definitions: [
                    (activity_item)-[:HAS_UNIT_DEFINITION]->(unit_definition_root:UnitDefinitionRoot)-[:LATEST]->(unit_definition_value:UnitDefinitionValue)
                    -[:HAS_CT_DIMENSION]-(:CTTermContext)-[:HAS_SELECTED_TERM]-(:CTTermRoot)-[:HAS_NAME_ROOT]->(CTTermNamesRoot)-[:LATEST]->(dimension_value:CTTermNameValue)
                    | {uid: unit_definition_root.uid, name: unit_definition_value.name, dimension_name: dimension_value.name}
                ],
                is_adam_param_specific: activity_item.is_adam_param_specific,
                odm_form: head([(activity_item)-[:HAS_ODM_FORM]->(odm_form_value:OdmFormValue)<-[:HAS_VERSION]-(odm_form_root:OdmFormRoot) | {uid: odm_form_root.uid, oid: odm_form_value.oid, name: odm_form_value.name}]),
                odm_item_group: head([(activity_item)-[:HAS_ODM_ITEM_GROUP]->(odm_item_group_value:OdmItemGroupValue)<-[:HAS_VERSION]-(odm_item_group_root:OdmItemGroupRoot) | {uid: odm_item_group_root.uid, oid: odm_item_group_value.oid, name: odm_item_group_value.name}]),
                odm_item: head([(activity_item)-[:HAS_ODM_ITEM]->(odm_item_value:OdmItemValue)<-[:HAS_VERSION]-(odm_item_root:OdmItemRoot) | {uid: odm_item_root.uid, oid: odm_item_value.oid, name: odm_item_value.name}])
            }
            ]) AS activity_items
        WITH DISTINCT
            activity_instance_root,
            activity_instance_value,
            instance_library_name,
            activity_instance_class,
            hierarchy,
            activity_items,
            has_version,
            apoc.coll.dropDuplicateNeighbors(
                [v in apoc.coll.sortMulti(
                    [v in all_versions | {
                        version: v,
                        major: toInteger(split(v, '.')[0]),
                        minor: toInteger(split(v, '.')[1])
                    }],
                    ['major', 'minor']
                ) | v.version]
            ) AS all_versions
        RETURN *
        """
        )
        result_array, attribute_names = db.cypher_query(query=query, params=params)
        BusinessLogicException.raise_if(
            len(result_array) != 1,
            msg=f"The overview query returned broken data: {result_array}",
        )
        overview = result_array[0]
        overview_dict = {}
        for overview_prop, attribute_name in zip(overview, attribute_names):
            overview_dict[attribute_name] = overview_prop
        for item in overview_dict["hierarchy"]:
            # Use the selected versions from the subqueries
            item["version"] = item.get("selected_activity_version")
            item["activity_group_version"] = item.get("selected_group_version")
            item["activity_subgroup_version"] = item.get("selected_subgroup_version")
        return overview_dict

    def get_cosmos_activity_instance_overview(self, uid: str) -> dict[str, Any]:
        query = """
        MATCH (activity_instance_root:ActivityInstanceRoot {uid:$uid})-[:LATEST]->(activity_instance_value:ActivityInstanceValue)
        WITH activity_instance_root,activity_instance_value,
            head([(library)-[:CONTAINS_CONCEPT]->(activity_instance_root) | library.name]) AS instance_library_name,
            head([(activity_instance_value)-[:ACTIVITY_INSTANCE_CLASS]->
            (activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue) 
            | activity_instance_class_value.name]) AS activity_instance_class_name
        WITH *,
            [(activity_instance_value)-[:HAS_ACTIVITY]->(:ActivityGrouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)
            <-[:HAS_GROUP]-(activity_subgroup_value:ActivitySubGroupValue) | activity_subgroup_value.name] AS activity_subgroups,
            apoc.coll.toSet([(activity_instance_value)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item)
            <-[HAS_ACTIVITY_ITEM]-(activity_item_class_root)-[:LATEST]->(activity_item_class_value) | 
            {
                nci_concept_id: activity_item_class_value.nci_concept_id,
                name: activity_item_class_value.name,
                type: head([(activity_item_class_value)-[:HAS_DATA_TYPE]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(data_type_value) | data_type_value.name]),
                example_set: [(activity_item)-[:HAS_CT_TERM]->(term_root:CTTermRoot)-[:HAS_NAME_ROOT]->(term_name_root:CTTermNameRoot)-[:LATEST]->(term_name_value:CTTermNameValue) | {uid: term_root.uid, name: term_name_value.name}] + [(activity_item)-[:HAS_UNIT_DEFINITION]->(unit_definition_root:UnitDefinitionRoot)-[:LATEST]->(unit_definition_value:UnitDefinitionValue) | {uid: unit_definition_root.uid, name: unit_definition_value.name}]
            }
            ]) AS activity_items
        WITH DISTINCT
            {
                uid: activity_instance_root.uid,
                name: activity_instance_value.name,
                name_sentence_case: activity_instance_value.name_sentence_case,
                definition: activity_instance_value.definition,
                abbreviation: activity_instance_value.abbreviation,
                nci_concept_id: activity_instance_value.nci_concept_id,
                is_required_for_activity: activity_instance_value.is_required_for_activity,
                is_defaulted_for_activity: activity_instance_value.is_defaulted_for_activity
            } AS activity_instance_value,
            activity_instance_class_name,
            activity_subgroups,
            activity_items
        RETURN *
        """
        result_array, attribute_names = db.cypher_query(
            query=query, params={"uid": uid}
        )
        BusinessLogicException.raise_if(
            len(result_array) != 1,
            msg=f"The overview query returned broken data: {result_array}",
        )
        return {
            attribute_name: result_array[0][index]
            for index, attribute_name in enumerate(attribute_names)
        }

    def generic_match_clause_all_versions(self):
        return """
            MATCH (concept_root:ActivityInstanceRoot)-[version:HAS_VERSION]->(concept_value:ActivityInstanceValue)
            -[:HAS_ACTIVITY]->(activity_grouping:ActivityGrouping)<-[:HAS_GROUPING]-(activity_value:ActivityValue)
        """

    def get_all_activity_instances_for_activity_grouping(
        self,
        activity_uid: str,
        activity_subgroup_uid: str,
        activity_group_uid: str,
        filter_by_boolean_flags: bool = False,
    ) -> list[tuple[ActivityInstanceRoot, ActivityInstanceValue]]:
        query = """
            MATCH (activity_instance_root:ActivityInstanceRoot)-[:LATEST]->(activity_instance_value:ActivityInstanceValue)
            MATCH (activity_instance_root)-[:LATEST_FINAL]->(activity_instance_value)
            OPTIONAL MATCH (activity_instance_root)-[retired:HAS_VERSION {status: "Retired"}]->(activity_instance_value) WHERE retired.end_date IS NULL
            WITH activity_instance_root, activity_instance_value WHERE retired IS NULL
            MATCH (activity_instance_value)-[:HAS_ACTIVITY]->(activity_grouping:ActivityGrouping)<-[:HAS_GROUPING]-(:ActivityValue)<-[:HAS_VERSION]-(:ActivityRoot {uid:$activity_uid})
            MATCH (activity_grouping)-[:IN_SUBGROUP]->(activity_valid_group:ActivityValidGroup)<-[:HAS_GROUP]-(:ActivitySubGroupValue)<-[:HAS_VERSION]-(:ActivitySubGroupRoot {uid:$activity_subgroup_uid})
            MATCH (activity_valid_group)-[:IN_GROUP]->(:ActivityGroupValue)<-[:HAS_VERSION]-(:ActivityGroupRoot {uid:$activity_group_uid})
            WITH DISTINCT activity_instance_root, activity_instance_value
            ORDER BY activity_instance_value.is_required_for_activity DESC, activity_instance_value.is_defaulted_for_activity DESC
            RETURN activity_instance_root as root, activity_instance_value as value
        """
        nodes, _ = db.cypher_query(
            query,
            params={
                "activity_uid": activity_uid,
                "activity_subgroup_uid": activity_subgroup_uid,
                "activity_group_uid": activity_group_uid,
            },
            resolve_objects=True,
        )
        required_instances = []
        defaulted_instances: list[Any] = []
        other_instances: list[Any] = []
        all_instances = []
        for activity_instance in nodes:
            root: ActivityInstanceRoot = activity_instance[0]
            value: ActivityInstanceValue = activity_instance[1]
            all_instances.append((root, value))
            if value.is_required_for_activity:
                required_instances.append((root, value))
            elif (
                value.is_default_selected_for_activity and len(defaulted_instances) == 0
            ):
                defaulted_instances.append((root, value))
            elif len(other_instances) == 0:
                other_instances.append((root, value))
        if filter_by_boolean_flags:
            if required_instances:
                return required_instances
            if defaulted_instances:
                return defaulted_instances
            return other_instances
        return all_instances

    def specific_header_match_clause_lite(self, field_name: str) -> str | None:
        """This is a lightweight version of the header match clause.
        It should fetch only the required field, without supporting wildcard filtering.
        """

        if field_name == "activity_name":
            return """
                WITH concept_value,
                     head([(concept_value)-[:HAS_ACTIVITY]->(activity_grouping)<-[:HAS_GROUPING]-(activity_value) | activity_value.name]) as activity_name
                """

        if field_name == "activity_instance_class.name":
            return """
                WITH concept_value,
                     head([(concept_value)-[:ACTIVITY_INSTANCE_CLASS]->
                            (activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
                            | activity_instance_class_value.name]) AS activity_instance_class_name
                """

        return None

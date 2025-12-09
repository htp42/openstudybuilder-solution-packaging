import datetime
from dataclasses import dataclass
from typing import Any

from clinical_mdr_api.domain_repositories.generic_repository import (
    manage_previous_connected_study_selection_relationships,
)
from clinical_mdr_api.domain_repositories.models._utils import ListDistinct
from clinical_mdr_api.domain_repositories.models.activities import (
    ActivityInstanceRoot,
    ActivityInstanceValue,
)
from clinical_mdr_api.domain_repositories.models.study import StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import StudyAction
from clinical_mdr_api.domain_repositories.models.study_selections import (
    StudyActivity,
    StudyActivityInstance,
    StudySelection,
)
from clinical_mdr_api.domain_repositories.models.study_visit import StudyVisit
from clinical_mdr_api.domain_repositories.study_selections.study_activity_base_repository import (
    StudySelectionActivityBaseRepository,
)
from clinical_mdr_api.domain_repositories.study_selections.study_activity_schedule_repository import (
    StudyActivityScheduleRepository,
)
from clinical_mdr_api.domains.enums import LibraryItemStatus
from clinical_mdr_api.domains.study_selections.study_selection_activity_instance import (
    StudySelectionActivityInstanceAR,
    StudySelectionActivityInstanceVO,
)
from clinical_mdr_api.models.study_selections.study_visit import SimpleStudyVisit
from common.exceptions import BusinessLogicException, NotFoundException
from common.utils import convert_to_datetime


@dataclass
class SelectionHistory:
    """Class for selection history items"""

    study_selection_uid: str
    study_activity_uid: str
    # Activity properties
    activity_uid: str
    activity_name: str | None
    activity_library_name: str | None
    activity_is_data_collected: bool
    # ActivityInstance properties
    activity_instance_uid: str | None
    activity_instance_name: str | None
    activity_instance_topic_code: str | None
    activity_instance_adam_param_code: str | None
    activity_instance_class_uid: str | None
    activity_instance_class_name: str | None
    activity_instance_specimen: str | None
    activity_instance_test_name_code: str | None
    activity_instance_standard_unit: str | None
    activity_instance_version: str | None
    activity_instance_status: LibraryItemStatus | None
    activity_instance_is_default_selected_for_activity: bool
    activity_instance_is_required_for_activity: bool
    # StudyActivityGroupings
    study_activity_subgroup_uid: str | None
    activity_subgroup_uid: str | None
    activity_subgroup_name: str | None
    study_activity_group_uid: str | None
    activity_group_uid: str | None
    activity_group_name: str | None
    study_soa_group_uid: str | None
    soa_group_term_uid: str | None
    soa_group_term_name: str | None
    show_activity_instance_in_protocol_flowchart: bool
    is_important: bool
    baseline_visits: list[SimpleStudyVisit] | None
    author_id: str
    change_type: str
    start_date: datetime.datetime
    end_date: datetime.datetime | None


class StudySelectionActivityInstanceRepository(
    StudySelectionActivityBaseRepository[StudySelectionActivityInstanceAR]
):
    _aggregate_root_type = StudySelectionActivityInstanceAR

    def is_repository_based_on_ordered_selection(self):
        return False

    def _get_activity_items_from_activity_instance(
        self, activity_instance: dict[str, Any]
    ) -> tuple[str, str, str]:
        activity_instance_specimen: str | None = None
        activity_instance_test_name_code: str | None = None
        activity_instance_standard_unit: str | None = None
        for activity_item in activity_instance.get("activity_items"):
            if activity_item.get("activity_item_class_name") == "specimen":
                activity_instance_specimen = ",".join(activity_item.get("ct_terms"))
            if activity_item.get("activity_item_class_name") == "test_name_code":
                activity_instance_test_name_code = ",".join(
                    activity_item.get("ct_terms")
                )
            if activity_item.get("activity_item_class_name") == "standard_unit":
                activity_instance_standard_unit = ",".join(
                    activity_item.get("unit_definitions")
                )
        return (
            activity_instance_specimen,
            activity_instance_test_name_code,
            activity_instance_standard_unit,
        )

    def _create_value_object_from_repository(
        self, selection: dict[Any, Any], acv: bool
    ) -> StudySelectionActivityInstanceVO:
        baseline_visits = selection.get("baseline_visits") or []
        activity = selection.get("activity") or {}
        activity_instance = selection.get("activity_instance") or {}
        activity_instance_uid = activity_instance.get("uid")
        activity_instance_version = activity_instance.get("version")
        (
            activity_instance_specimen,
            activity_instance_test_name_code,
            activity_instance_standard_unit,
        ) = self._get_activity_items_from_activity_instance(
            activity_instance=activity_instance
        )
        activity_instance_class = activity_instance.get("activity_instance_class") or {}
        latest_activity_instance = selection.get("latest_activity_instance") or {}
        latest_activity_instance_class = (
            latest_activity_instance.get("activity_instance_class") or {}
        )
        latest_activity_instance_version = latest_activity_instance.get("version")

        study_activity_subgroup = selection.get("study_activity_subgroup") or {}
        study_activity_group = selection.get("study_activity_group") or {}
        study_soa_group = selection.get("study_soa_group") or {}
        return StudySelectionActivityInstanceVO.from_input_values(
            study_uid=selection["study_uid"],
            study_selection_uid=selection["study_selection_uid"],
            is_reviewed=selection["is_reviewed"],
            is_instance_removal_needed=activity.get(
                "is_instance_removal_needed", False
            ),
            study_activity_uid=selection["study_activity_uid"],
            study_activity_instance_baseline_visits=(
                [
                    {
                        "uid": baseline_visit.get("uid"),
                        "visit_name": baseline_visit.get("visit_name"),
                        "visit_type_name": baseline_visit.get("visit_type_name"),
                    }
                    for baseline_visit in baseline_visits
                ]
            ),
            show_activity_instance_in_protocol_flowchart=selection[
                "show_activity_instance_in_protocol_flowchart"
            ],
            keep_old_version=selection["keep_old_version"],
            keep_old_version_date=(
                convert_to_datetime(value=selection.get("keep_old_version_date"))
                if selection.get("keep_old_version_date")
                else None
            ),
            is_important=selection.get("is_important", False),
            activity_uid=activity["uid"],
            activity_name=activity.get("name"),
            activity_library_name=activity.get("library_name"),
            activity_is_data_collected=activity.get("is_data_collected") or False,
            activity_instance_uid=activity_instance_uid,
            activity_instance_name=activity_instance.get("name"),
            activity_instance_topic_code=activity_instance.get("topic_code"),
            activity_instance_adam_param_code=activity_instance.get("adam_param_code"),
            activity_instance_specimen=activity_instance_specimen,
            activity_instance_test_name_code=activity_instance_test_name_code,
            activity_instance_standard_unit=activity_instance_standard_unit,
            activity_instance_class_uid=activity_instance_class.get("uid"),
            activity_instance_class_name=activity_instance_class.get("name"),
            activity_instance_version=activity_instance_version,
            activity_instance_status=(
                LibraryItemStatus(activity_instance.get("status"))
                if activity_instance_uid
                else None
            ),
            activity_instance_is_default_selected_for_activity=activity_instance.get(
                "is_default_selected_for_activity"
            )
            or False,
            activity_instance_is_required_for_activity=activity_instance.get(
                "is_required_for_activity"
            )
            or False,
            latest_activity_instance_uid=latest_activity_instance.get("uid"),
            latest_activity_instance_name=latest_activity_instance.get("name"),
            latest_activity_instance_topic_code=latest_activity_instance.get(
                "topic_code"
            ),
            latest_activity_instance_class_uid=latest_activity_instance_class.get(
                "uid"
            ),
            latest_activity_instance_class_name=latest_activity_instance_class.get(
                "name"
            ),
            latest_activity_instance_version=latest_activity_instance_version,
            latest_activity_instance_status=(
                LibraryItemStatus(latest_activity_instance.get("status"))
                if latest_activity_instance_version
                else None
            ),
            latest_activity_instance_date=latest_activity_instance.get("date"),
            start_date=convert_to_datetime(value=selection["start_date"]),
            author_id=selection["author_id"],
            author_username=selection["author_username"],
            accepted_version=acv,
            study_activity_subgroup_uid=study_activity_subgroup.get("selection_uid"),
            activity_subgroup_uid=study_activity_subgroup.get("activity_subgroup_uid"),
            activity_subgroup_name=study_activity_subgroup.get(
                "activity_subgroup_name"
            ),
            study_activity_group_uid=study_activity_group.get("selection_uid"),
            activity_group_uid=study_activity_group.get("activity_group_uid"),
            activity_group_name=study_activity_group.get("activity_group_name"),
            study_soa_group_uid=study_soa_group.get("selection_uid"),
            soa_group_term_uid=study_soa_group.get("soa_group_uid"),
            soa_group_term_name=study_soa_group.get("soa_group_name"),
        )

    def _order_by_query(self):
        return """
            WITH DISTINCT *
            MATCH (sa)<-[:AFTER]-(sac:StudyAction)
        """

    def _versioning_query(self) -> str:
        return ""

    def _additional_match(self) -> str:
        return """
            WITH sr, sv
            MATCH (sv)-[:HAS_STUDY_ACTIVITY_INSTANCE]->(sa:StudyActivityInstance)
                <-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]-(study_activity:StudyActivity)<-[:HAS_STUDY_ACTIVITY]-(sv)
            WITH sr, sv, sa, study_activity
            CALL {
                WITH sa
                OPTIONAL MATCH (sa)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(aiv:ActivityInstanceValue)<-[ver:HAS_VERSION]-(air:ActivityInstanceRoot)
                WHERE ver.status IN ['Final']
                RETURN
                    {
                        uid:air.uid, name: aiv.name, topic_code: aiv.topic_code, adam_param_code:aiv.adam_param_code, version: ver.version, status: ver.status,
                        is_default_selected_for_activity: coalesce(aiv.is_default_selected_for_activity, false), 
                        is_required_for_activity: coalesce(aiv.is_required_for_activity, false),
                        activity_instance_class: head([(aiv)-[:ACTIVITY_INSTANCE_CLASS]->(activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
                            | {uid:activity_instance_class_root.uid, name:activity_instance_class_value.name}]),
                        activity_items: [(aiv)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item:ActivityItem)
                            <-[:HAS_ACTIVITY_ITEM]-(activity_item_class_root:ActivityItemClassRoot)-[:LATEST]->
                            (activity_item_class_value:ActivityItemClassValue)
                            WHERE activity_item_class_value.name IN ['specimen', 'test_name_code', 'standard_unit']
                                | {
                                    activity_item_class_name: activity_item_class_value.name,
                                    ct_terms: [(activity_item)-[:HAS_CT_TERM]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(term_name_value:CTTermNameValue) | term_name_value.name],
                                    unit_definitions: [(activity_item)-[:HAS_UNIT_DEFINITION]->(:UnitDefinitionRoot)-[:LATEST]->(unit_definition_value:UnitDefinitionValue) | unit_definition_value.name]
                                }
                        ]
                    } as activity_instance,
                    air as air,
                    aiv as aiv,
                    ver as selected_ver
                ORDER BY ver.start_date DESC
                LIMIT 1
            }
            CALL {
                WITH air, aiv, selected_ver
                OPTIONAL MATCH (air)-[:LATEST]->(latest_aiv:ActivityInstanceValue)
                OPTIONAL MATCH (air)-[ver:HAS_VERSION]->(latest_aiv)
                WHERE ver.end_date IS NULL AND ver<>selected_ver
                RETURN
                    {
                        uid:air.uid, name: latest_aiv.name, topic_code: latest_aiv.topic_code, version: ver.version, status: ver.status, date: ver.start_date,
                        activity_instance_class: head([(latest_aiv)-[:ACTIVITY_INSTANCE_CLASS]->(activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
                            | {uid:activity_instance_class_root.uid, name:activity_instance_class_value.name}])
                    } as latest_activity_instance
                ORDER BY ver.start_date DESC
                LIMIT 1
            }
            CALL{
                WITH study_activity
                MATCH (study_activity)-[:HAS_SELECTED_ACTIVITY]->(av:ActivityValue)<-[ver:HAS_VERSION]-(ar:ActivityRoot)<-[:CONTAINS_CONCEPT]-(library:Library)
                WHERE ver.status IN ['Final', 'Retired']
                RETURN 
                    {
                        uid:ar.uid, name: av.name, library_name: library.name, is_data_collected: av.is_data_collected,
                        is_instance_removal_needed: 
                        CASE WHEN 
                            size(apoc.coll.toSet([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]->(sai:StudyActivityInstance) 
                                WHERE NOT (sai)-[:BEFORE]-() AND NOT (sai)-[:AFTER]-(:Delete:StudyAction) | sai.uid])) > 1
                            AND av.is_multiple_selection_allowed = false
                            THEN TRUE
                            ELSE FALSE
                        END
                    }
                 as activity
                ORDER BY ver.start_date DESC
                LIMIT 1
            }
            CALL {
                WITH sa, sv
                OPTIONAL MATCH (sa)-[:HAS_BASELINE]->(baseline_visit:StudyVisit)<-[:HAS_STUDY_VISIT]-(sv)
                OPTIONAL MATCH (baseline_visit)-[:HAS_VISIT_NAME]->(visit_name_root:VisitNameRoot)-[:LATEST]->(visit_name_value:VisitNameValue)
                OPTIONAL MATCH (baseline_visit)-[:HAS_VISIT_TYPE]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(visit_type_root:CTTermRoot)-[:HAS_NAME_ROOT]-(:CTTermNameRoot)-[:LATEST]->(visit_type_value:CTTermNameValue)
                WITH CASE WHEN baseline_visit IS NOT NULL THEN {
                    uid: baseline_visit.uid,
                    visit_name: visit_name_value.name,
                    visit_type_name: visit_type_value.name
                } ELSE NULL END as baseline_visit
                RETURN baseline_visit
            }
            WITH sr, sv, sa, study_activity, activity, activity_instance, latest_activity_instance, collect(baseline_visit) as baseline_visits
        """

    def _filter_clause(self, query_parameters: dict[Any, Any], **kwargs) -> str:
        # Filter on Activity, ActivityGroup or ActivityGroupNames if provided as a specific filter
        # This improves performance vs full service level filter
        activity_names = kwargs.get("activity_names")
        activity_group_names = kwargs.get("activity_group_names")
        activity_subgroup_names = kwargs.get("activity_subgroup_names")
        activity_instance_names = kwargs.get("activity_instance_names")
        filter_query = ""
        if (
            activity_names is not None
            or activity_group_names is not None
            or activity_subgroup_names is not None
            or activity_instance_names is not None
        ):
            filter_query += " WHERE "
            filter_list = []
            if activity_names is not None:
                filter_list.append(
                    "head([(study_activity)-[:HAS_SELECTED_ACTIVITY]->(activity_value:ActivityValue) | activity_value.name]) IN $activity_names"
                )
                query_parameters["activity_names"] = activity_names
            if activity_subgroup_names is not None:
                filter_list.append(
                    "size([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(sas:StudyActivitySubGroup)-"
                    "[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value:ActivitySubGroupValue)"
                    "WHERE activity_subgroup_value.name IN $activity_subgroup_names | activity_subgroup_value.name]) > 0"
                )
                query_parameters["activity_subgroup_names"] = activity_subgroup_names
            if activity_group_names is not None:
                filter_list.append(
                    "size([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(sas:StudyActivityGroup)-"
                    "[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value:ActivityGroupValue)"
                    "WHERE activity_group_value.name IN $activity_group_names | activity_group_value.name]) > 0"
                )
                query_parameters["activity_group_names"] = activity_group_names
            if activity_instance_names is not None:
                filter_list.append(
                    "size([(sa)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(activity_instance_value:ActivityInstanceValue)"
                    "WHERE activity_instance_value.name IN $activity_instance_names | activity_instance_value.name]) > 0"
                )
                query_parameters["activity_instance_names"] = activity_instance_names
            filter_query += " AND ".join(filter_list)
        return filter_query

    def _return_clause(self) -> str:
        return """RETURN DISTINCT
                sr.uid AS study_uid,
                sa.uid AS study_selection_uid,
                coalesce(sa.is_reviewed, false) AS is_reviewed,
                coalesce(sa.show_activity_instance_in_protocol_flowchart, false) AS show_activity_instance_in_protocol_flowchart,
                coalesce(sa.keep_old_version, false) AS keep_old_version,
                sa.keep_old_version_date AS keep_old_version_date,
                coalesce(sa.is_important, false) AS is_important,
                study_activity.uid AS study_activity_uid,
                activity,
                activity_instance,
                latest_activity_instance,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(study_activity_subgroup_selection)
                    -[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value:ActivitySubGroupValue)<-[:HAS_VERSION]-(activity_subgroup_root:ActivitySubGroupRoot) | 
                    {
                        selection_uid: study_activity_subgroup_selection.uid, 
                        activity_subgroup_uid:activity_subgroup_root.uid,
                        activity_subgroup_name: activity_subgroup_value.name,
                        order: study_activity_subgroup_selection.order
                    }]) AS study_activity_subgroup,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(study_activity_group_selection)
                    -[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value:ActivityGroupValue)<-[:HAS_VERSION]-(activity_group_root:ActivityGroupRoot) | 
                    {
                        selection_uid: study_activity_group_selection.uid, 
                        activity_group_uid: activity_group_root.uid,
                        activity_group_name: activity_group_value.name,
                        order: study_activity_group_selection.order
                    }]) AS study_activity_group,
                head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_SOA_GROUP]->(study_soa_group_selection)
                    -[:HAS_FLOWCHART_GROUP]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(ct_term_root:CTTermRoot)-[:HAS_NAME_ROOT]-(:CTTermNameRoot)-[:LATEST]->(flowchart_value:CTTermNameValue) | 
                    {
                        selection_uid: study_soa_group_selection.uid, 
                        soa_group_uid: ct_term_root.uid,
                        soa_group_name: flowchart_value.name,
                        order: study_soa_group_selection.order
                    }]) AS study_soa_group,
                baseline_visits,
                sac.date AS start_date,
                sac.author_id AS author_id,
                COALESCE(head([(user:User)-[*0]-() WHERE user.user_id=sac.author_id | user.username]), sac.author_id) AS author_username,
                study_activity.order AS study_activity_order
                ORDER BY study_soa_group.order, study_activity_group.order, study_activity_subgroup.order, study_activity_order, activity_instance.name
        """

    def get_selection_history(
        self,
        selection: dict[Any, Any],
        change_type: str,
        end_date: datetime.datetime | None,
    ):
        activity = selection.get("activity", {})
        activity_instance = selection.get("activity_instance", {})
        activity_instance_class = activity_instance.get("activity_instance_class") or {}
        (
            activity_instance_specimen,
            activity_instance_test_name_code,
            activity_instance_standard_unit,
        ) = self._get_activity_items_from_activity_instance(
            activity_instance=activity_instance
        )
        study_activity_subgroup = selection.get("study_activity_subgroup") or {}
        study_activity_group = selection.get("study_activity_group") or {}
        study_soa_group = selection.get("study_soa_group") or {}
        return SelectionHistory(
            study_selection_uid=selection["study_selection_uid"],
            study_activity_uid=selection["study_activity_uid"],
            activity_uid=activity.get("uid"),
            activity_name=activity.get("name"),
            activity_library_name=activity.get("library_name"),
            activity_is_data_collected=activity.get("is_data_collected") or False,
            activity_instance_uid=activity_instance.get("uid"),
            activity_instance_name=activity_instance.get("name"),
            activity_instance_topic_code=activity_instance.get("topic_code"),
            activity_instance_adam_param_code=activity_instance.get("adam_param_code"),
            activity_instance_specimen=activity_instance_specimen,
            activity_instance_test_name_code=activity_instance_test_name_code,
            activity_instance_standard_unit=activity_instance_standard_unit,
            activity_instance_class_uid=activity_instance_class.get("uid"),
            activity_instance_class_name=activity_instance_class.get("name"),
            activity_instance_version=activity_instance.get("version"),
            activity_instance_status=(
                LibraryItemStatus(activity_instance.get("status"))
                if activity_instance.get("uid")
                else None
            ),
            activity_instance_is_default_selected_for_activity=activity_instance.get(
                "is_default_selected_for_activity"
            )
            or False,
            activity_instance_is_required_for_activity=activity_instance.get(
                "is_required_for_activity"
            )
            or False,
            study_activity_subgroup_uid=study_activity_subgroup.get("selection_uid"),
            activity_subgroup_uid=study_activity_subgroup.get("activity_subgroup_uid"),
            activity_subgroup_name=study_activity_subgroup.get(
                "activity_subgroup_name"
            ),
            study_activity_group_uid=study_activity_group.get("selection_uid"),
            activity_group_uid=study_activity_group.get("activity_group_uid"),
            activity_group_name=study_activity_group.get("activity_group_name"),
            study_soa_group_uid=study_soa_group.get("selection_uid"),
            soa_group_term_uid=study_soa_group.get("soa_group_uid"),
            soa_group_term_name=study_soa_group.get("soa_group_name"),
            author_id=selection["author_id"],
            change_type=change_type,
            start_date=convert_to_datetime(value=selection["start_date"]),
            show_activity_instance_in_protocol_flowchart=selection[
                "show_activity_instance_in_protocol_flowchart"
            ],
            is_important=selection.get("is_important", False),
            baseline_visits=(
                [
                    SimpleStudyVisit(
                        uid=baseline_visit.get("uid"),
                        visit_name=baseline_visit.get("visit_name"),
                        visit_type_name=baseline_visit.get("visit_type_name"),
                    )
                    for baseline_visit in (selection.get("baseline_visits"))
                ]
                if selection.get("baseline_visits")
                else None
            ),
            end_date=end_date,
        )

    def get_audit_trail_query(self, study_selection_uid: str | None):
        if study_selection_uid:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(sa:StudyActivityInstance {uid: $study_selection_uid})
            WITH sa
            MATCH (sa)-[:AFTER|BEFORE*0..]-(all_sa:StudyActivityInstance)
            WITH distinct(all_sa)
            """
        else:
            audit_trail_cypher = """
            MATCH (sr:StudyRoot { uid: $study_uid})-[:AUDIT_TRAIL]->(:StudyAction)-[:BEFORE|AFTER]->(all_sa:StudyActivityInstance)
            WITH DISTINCT all_sa
            """
        audit_trail_cypher += """

                    WITH DISTINCT all_sa
                    ORDER BY all_sa.uid ASC
                    WITH all_sa
                    // Get latest available version of given StudyActivity linked to StudyActivityInstance
                    CALL {
                        WITH all_sa
                        MATCH (all_sa)<-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_INSTANCE]-(study_activity:StudyActivity)-[:AFTER]-(action:StudyAction)
                        WITH study_activity, action
                        ORDER BY action.date ASC
                        WITH last(collect(study_activity)) as study_activity
                        RETURN study_activity
                    }
                    CALL {
                        WITH all_sa
                        OPTIONAL MATCH (all_sa)-[:HAS_SELECTED_ACTIVITY_INSTANCE]->(aiv:ActivityInstanceValue)<-[ver:HAS_VERSION]-(air:ActivityInstanceRoot)
                        WHERE ver.status IN ['Final']
                        RETURN
                            {
                                uid:air.uid, name: aiv.name, topic_code: aiv.topic_code, adam_param_code:aiv.adam_param_code, version: ver.version, status: ver.status,
                                is_default_selected_for_activity: coalesce(aiv.is_default_selected_for_activity, false), 
                                is_required_for_activity: coalesce(aiv.is_required_for_activity, false),
                                activity_instance_class: head([(aiv)-[:ACTIVITY_INSTANCE_CLASS]->(activity_instance_class_root:ActivityInstanceClassRoot)-[:LATEST]->(activity_instance_class_value:ActivityInstanceClassValue)
                                    | {uid:activity_instance_class_root.uid, name:activity_instance_class_value.name}]),
                                activity_items: [(aiv)-[:CONTAINS_ACTIVITY_ITEM]->(activity_item:ActivityItem)
                                    <-[:HAS_ACTIVITY_ITEM]-(activity_item_class_root:ActivityItemClassRoot)-[:LATEST]->
                                    (activity_item_class_value:ActivityItemClassValue)
                                    WHERE activity_item_class_value.name IN ['specimen', 'test_name_code', 'standard_unit']
                                        | {
                                            activity_item_class_name: activity_item_class_value.name,
                                            ct_terms: [(activity_item)-[:HAS_CT_TERM]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(:CTTermRoot)-[:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:LATEST]->(term_name_value:CTTermNameValue) | term_name_value.name],
                                            unit_definitions: [(activity_item)-[:HAS_UNIT_DEFINITION]->(unit_definition_root:UnitDefinitionRoot)-[:LATEST]->(unit_definition_value:UnitDefinitionValue) | unit_definition_value.name]
                                        }
                                ]
                            } as activity_instance,
                            air as air,
                            aiv as aiv
                        ORDER BY ver.start_date DESC
                        LIMIT 1
                    }
                    CALL{
                        WITH study_activity
                        MATCH (study_activity)-[:HAS_SELECTED_ACTIVITY]->(av:ActivityValue)<-[ver:HAS_VERSION]-(ar:ActivityRoot)<-[:CONTAINS_CONCEPT]-(library:Library)
                        WHERE ver.status IN ['Final', 'Retired']
                        RETURN 
                            {
                                uid:ar.uid, name: av.name, library_name: library.name, is_data_collected: av.is_data_collected
                            }
                        as activity
                        ORDER BY ver.start_date DESC
                        LIMIT 1
                    }
                    CALL {
                        WITH all_sa
                        OPTIONAL MATCH (all_sa)-[:HAS_BASELINE]->(baseline_visit:StudyVisit)
                        OPTIONAL MATCH (baseline_visit)-[:HAS_VISIT_NAME]->(visit_name_root:VisitNameRoot)-[:LATEST]->(visit_name_value:VisitNameValue)
                        OPTIONAL MATCH (baseline_visit)-[:HAS_VISIT_TYPE]->(:CTTermContext)-[:HAS_SELECTED_TERM]->(visit_type_root:CTTermRoot)-[:HAS_NAME_ROOT]-(:CTTermNameRoot)-[:LATEST]->(visit_type_value:CTTermNameValue)
                        WITH baseline_visit.uid AS baseline_visit_uid, CASE WHEN baseline_visit IS NOT NULL THEN {
                            uid: baseline_visit.uid,
                            visit_name: visit_name_value.name,
                            visit_type_name: visit_type_value.name
                        } ELSE NULL END as baseline_visit
                        WITH baseline_visit_uid, head(collect(baseline_visit)) as baseline_visit
                        RETURN baseline_visit
                    }
                    MATCH (all_sa)<-[:AFTER]-(asa:StudyAction)
                    OPTIONAL MATCH (all_sa)<-[:BEFORE]-(bsa:StudyAction)
                    WITH all_sa, study_activity, activity, activity_instance, asa, bsa, collect(baseline_visit) as baseline_visits
                    
                    ORDER BY all_sa.uid, asa.date DESC
                    RETURN
                        all_sa.uid AS study_selection_uid,
                        study_activity.uid as study_activity_uid,
                        activity,
                        activity_instance,
                        head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_SUBGROUP]->(study_activity_subgroup_selection)
                            -[:HAS_SELECTED_ACTIVITY_SUBGROUP]->(activity_subgroup_value:ActivitySubGroupValue)<-[:HAS_VERSION]-(activity_subgroup_root:ActivitySubGroupRoot) | 
                            {
                                selection_uid: study_activity_subgroup_selection.uid, 
                                activity_subgroup_uid:activity_subgroup_root.uid,
                                activity_subgroup_name: activity_subgroup_value.name
                            }]) AS study_activity_subgroup,
                        head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_ACTIVITY_GROUP]->(study_activity_group_selection)
                            -[:HAS_SELECTED_ACTIVITY_GROUP]->(activity_group_value:ActivityGroupValue)<-[:HAS_VERSION]-(activity_group_root:ActivityGroupRoot) | 
                            {
                                selection_uid: study_activity_group_selection.uid, 
                                activity_group_uid: activity_group_root.uid,
                                activity_group_name: activity_group_value.name
                            }]) AS study_activity_group,
                        head([(study_activity)-[:STUDY_ACTIVITY_HAS_STUDY_SOA_GROUP]->(study_soa_group_selection)
                            -[:HAS_FLOWCHART_GROUP]->(ct_term_root:CTTermRoot)-[:HAS_NAME_ROOT]-(:CTTermNameRoot)-[:LATEST]->(flowchart_value:CTTermNameValue) | 
                            {
                                selection_uid: study_soa_group_selection.uid, 
                                soa_group_uid: ct_term_root.uid,
                                soa_group_name: flowchart_value.name
                            }]) AS study_soa_group,
                        coalesce(all_sa.show_activity_instance_in_protocol_flowchart, false) AS show_activity_instance_in_protocol_flowchart,
                        coalesce(all_sa.is_important, false) AS is_important,
                        asa.date AS start_date,
                        asa.author_id AS author_id,
                        labels(asa) AS change_type,
                        bsa.date AS end_date,
                        baseline_visits
                    """
        return audit_trail_cypher

    def get_study_selection_node_from_latest_study_value(
        self, study_value: StudyValue, study_selection: StudySelection
    ):
        return study_value.has_study_activity_instance.get(
            uid=study_selection.study_selection_uid
        )

    def _add_new_selection(
        self,
        latest_study_value_node: StudyValue,
        order: int,
        selection: StudySelectionActivityInstanceVO,
        audit_node: StudyAction,
        last_study_selection_node: StudyActivityInstance,
        for_deletion: bool = False,
    ):
        # Create new activity selection
        study_activity_instance_selection_node = StudyActivityInstance(
            uid=selection.study_selection_uid,
            show_activity_instance_in_protocol_flowchart=selection.show_activity_instance_in_protocol_flowchart,
            keep_old_version=selection.keep_old_version,
            keep_old_version_date=selection.keep_old_version_date,
            is_reviewed=selection.is_reviewed,
            is_important=selection.is_important,
            accepted_version=selection.accepted_version,
        )
        study_activity_instance_selection_node.save()
        if not for_deletion:
            # Connect new node with study value
            latest_study_value_node.has_study_activity_instance.connect(
                study_activity_instance_selection_node
            )
        # Connect new node with audit trail
        audit_node.has_after.connect(study_activity_instance_selection_node)
        if selection.activity_instance_uid:
            # find the activity instance value
            activity_instance_root_node: ActivityInstanceRoot = (
                ActivityInstanceRoot.nodes.get(uid=selection.activity_instance_uid)
            )
            latest_activity_instance_value_node: ActivityInstanceValue
            if selection.activity_instance_version:
                latest_activity_instance_value_node = (
                    activity_instance_root_node.get_value_for_version(
                        selection.activity_instance_version
                    )
                )
            else:
                latest_activity_instance_value_node = (
                    activity_instance_root_node.has_latest_value.get()
                )
            # Connect new node with Activity value
            study_activity_instance_selection_node.has_selected_activity_instance.connect(
                latest_activity_instance_value_node
            )

        # Connect StudyActivityInstance with StudyActivity node
        study_activity_node = StudyActivity.nodes.has(has_before=False).get(
            uid=selection.study_activity_uid
        )
        study_activity_instance_selection_node.study_activity_has_study_activity_instance.connect(
            study_activity_node
        )

        # Handle baseline visit relationships
        for baseline_visit in selection.study_activity_instance_baseline_visits or []:
            baseline_visit_uid = baseline_visit["uid"]
            baseline_visit_node = latest_study_value_node.has_study_visit.get_or_none(
                uid=baseline_visit_uid
            )
            NotFoundException.raise_if(
                baseline_visit_node is None,
                "Study Visit",
                baseline_visit_uid,
            )

            # Validate that the StudyVisit corresponds to a current StudyActivitySchedule
            # for the parent StudyActivity
            schedule_repository = StudyActivityScheduleRepository()
            schedules = (
                schedule_repository.find_schedule_for_study_visit_and_study_activity(
                    study_uid=selection.study_uid,
                    study_activity_uid=selection.study_activity_uid,
                    study_visit_uid=baseline_visit_uid,
                )
            )
            BusinessLogicException.raise_if(
                not schedules or len(schedules) == 0,
                msg=f"The Study Visit with UID '{baseline_visit_uid}' does not correspond to a current StudyActivitySchedule for the parent StudyActivity with UID '{selection.study_activity_uid}'.",
            )

            # Connect baseline visit relationship
            study_activity_instance_selection_node.has_baseline.connect(
                baseline_visit_node
            )

        if last_study_selection_node:
            manage_previous_connected_study_selection_relationships(
                previous_item=last_study_selection_node,
                study_value_node=latest_study_value_node,
                new_item=study_activity_instance_selection_node,
                exclude_study_selection_relationships=[StudyActivity, StudyVisit],
            )

    def generate_uid(self) -> str:
        return StudyActivityInstance.get_next_free_uid_and_increment_counter()

    def close(self) -> None:
        pass

    def get_all_study_activity_instances_for_study_activity(
        self, study_uid: str, study_activity_uid
    ) -> list[StudyActivityInstance]:
        study_activity_instances = ListDistinct(
            StudyActivityInstance.nodes.filter(
                has_study_activity_instance__latest_value__uid=study_uid,
                study_activity_has_study_activity_instance__has_study_activity__latest_value__uid=study_uid,
                study_activity_has_study_activity_instance__uid=study_activity_uid,
            )
            .has(has_before=False)
            .resolve_subgraph()
        ).distinct()
        return study_activity_instances

    def get_all_study_activity_instances_impacted_by_schedule_deletion(
        self, study_uid: str, schedule_uid: str
    ) -> list[StudyActivityInstance]:
        study_activity_instances = ListDistinct(
            StudyActivityInstance.nodes.filter(
                has_study_activity_instance__latest_value__uid=study_uid,  # Verify instance is currently selected by study
                study_activity_has_study_activity_instance__study_activity_schedule__uid=schedule_uid,  # Verify instance is associated with the schedule through activity
                has_baseline__has_study_activity_schedule__uid=schedule_uid,  # Verify instance has the schedule's visit as a baseline
            )
            .has(has_before=False)
            .resolve_subgraph()
        ).distinct()
        return study_activity_instances

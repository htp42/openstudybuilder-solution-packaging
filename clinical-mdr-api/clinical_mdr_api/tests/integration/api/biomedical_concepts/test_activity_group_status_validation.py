"""Test validation of activity group and subgroup status when creating/editing activities."""

import pytest

from clinical_mdr_api.services.concepts.activities.activity_group_service import (
    ActivityGroupService,
)
from clinical_mdr_api.services.concepts.activities.activity_service import (
    ActivityService,
)
from clinical_mdr_api.services.concepts.activities.activity_sub_group_service import (
    ActivitySubGroupService,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from common.exceptions import BusinessLogicException


def test_create_activity_with_retired_activity_group_fails():
    """Test that creating an activity with a retired activity group fails."""
    # Create and approve an activity group
    activity_group_service = ActivityGroupService()
    activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "ActivityGroup-"),
        approve=True,
    )

    # Create and approve an activity subgroup
    activity_subgroup = TestUtils.create_activity_subgroup(
        name=TestUtils.random_str(20, "ActivitySubgroup-"),
        activity_groups=[activity_group.uid],
        approve=True,
    )

    # Inactivate (retire) the activity group
    activity_group_service.inactivate_final(uid=activity_group.uid)

    # Try to create an activity with the retired activity group
    with pytest.raises(BusinessLogicException) as exc_info:
        TestUtils.create_activity(
            name=TestUtils.random_str(20, "Activity-"),
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            approve=False,
        )

    assert "Activity Group" in str(exc_info.value)
    assert activity_group.uid in str(exc_info.value)
    assert "is in status 'Retired'" in str(exc_info.value)
    assert (
        "Activities can only be connected to Activity Groups in 'Final' status"
        in str(exc_info.value)
    )


def test_create_activity_with_retired_activity_subgroup_fails():
    """Test that creating an activity with a retired activity subgroup fails."""
    # Create and approve an activity group
    activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "ActivityGroup-"),
        approve=True,
    )

    # Create and approve an activity subgroup
    activity_subgroup_service = ActivitySubGroupService()
    activity_subgroup = TestUtils.create_activity_subgroup(
        name=TestUtils.random_str(20, "ActivitySubgroup-"),
        activity_groups=[activity_group.uid],
        approve=True,
    )

    # Inactivate (retire) the activity subgroup
    activity_subgroup_service.inactivate_final(uid=activity_subgroup.uid)

    # Try to create an activity with the retired activity subgroup
    with pytest.raises(BusinessLogicException) as exc_info:
        TestUtils.create_activity(
            name=TestUtils.random_str(20, "Activity-"),
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            approve=False,
        )

    assert "Activity Subgroup" in str(exc_info.value)
    assert activity_subgroup.uid in str(exc_info.value)
    assert "is in status 'Retired'" in str(exc_info.value)
    assert (
        "Activities can only be connected to Activity Subgroups in 'Final' status"
        in str(exc_info.value)
    )


def test_create_activity_with_draft_activity_group_fails():
    """Test that creating an activity with a draft activity group fails."""
    # Create an activity group but don't approve it (leaves it in Draft status)
    activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "ActivityGroup-"),
        approve=False,  # Keep in Draft status
    )

    # Create and approve an activity subgroup with a different group
    temp_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "TempActivityGroup-"),
        approve=True,
    )
    activity_subgroup = TestUtils.create_activity_subgroup(
        name=TestUtils.random_str(20, "ActivitySubgroup-"),
        activity_groups=[temp_group.uid],
        approve=True,
    )

    # Try to create an activity with the draft activity group
    with pytest.raises(BusinessLogicException) as exc_info:
        TestUtils.create_activity(
            name=TestUtils.random_str(20, "Activity-"),
            activity_subgroups=[activity_subgroup.uid],
            activity_groups=[activity_group.uid],
            approve=False,
        )

    assert "Activity Group" in str(exc_info.value)
    assert activity_group.uid in str(exc_info.value)
    assert "is in status 'Draft'" in str(exc_info.value)
    assert (
        "Activities can only be connected to Activity Groups in 'Final' status"
        in str(exc_info.value)
    )


def test_edit_activity_with_retired_activity_group_fails():
    """Test that editing an activity to use a retired activity group fails."""
    # Create and approve activity group and subgroup
    activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "ActivityGroup-"),
        approve=True,
    )

    activity_subgroup = TestUtils.create_activity_subgroup(
        name=TestUtils.random_str(20, "ActivitySubgroup-"),
        activity_groups=[activity_group.uid],
        approve=True,
    )

    # Create an activity with the approved group/subgroup
    activity = TestUtils.create_activity(
        name=TestUtils.random_str(20, "Activity-"),
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        approve=False,  # Keep in draft for editing
    )

    # Create a new activity group and retire it
    new_activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "NewActivityGroup-"),
        approve=True,
    )
    activity_group_service = ActivityGroupService()
    activity_group_service.inactivate_final(uid=new_activity_group.uid)

    # Try to edit the activity to use the retired group
    activity_service = ActivityService()

    with pytest.raises(BusinessLogicException) as exc_info:
        from clinical_mdr_api.models.concepts.activities.activity import (
            ActivityEditInput,
        )

        edit_input = ActivityEditInput(
            name=activity.name,
            name_sentence_case=activity.name_sentence_case,
            change_description="Update groupings",
            activity_groupings=[
                {
                    "activity_group_uid": new_activity_group.uid,
                    "activity_subgroup_uid": activity_subgroup.uid,
                }
            ],
        )
        activity_service.edit_draft(
            uid=activity.uid, concept_edit_input=edit_input, patch_mode=False
        )

    assert "Activity Group" in str(exc_info.value)
    assert new_activity_group.uid in str(exc_info.value)
    assert "is in status 'Retired'" in str(exc_info.value)
    assert (
        "Activities can only be connected to Activity Groups in 'Final' status"
        in str(exc_info.value)
    )


def test_create_activity_with_final_groups_succeeds():
    """Test that creating an activity with final (approved) groups succeeds."""
    # Create and approve activity group and subgroup
    activity_group = TestUtils.create_activity_group(
        name=TestUtils.random_str(20, "ActivityGroup-"),
        approve=True,
    )

    activity_subgroup = TestUtils.create_activity_subgroup(
        name=TestUtils.random_str(20, "ActivitySubgroup-"),
        activity_groups=[activity_group.uid],
        approve=True,
    )

    # Create an activity with the approved group/subgroup - should succeed
    activity = TestUtils.create_activity(
        name=TestUtils.random_str(20, "Activity-"),
        activity_subgroups=[activity_subgroup.uid],
        activity_groups=[activity_group.uid],
        approve=False,
    )

    assert activity is not None
    assert activity.uid is not None
    assert len(activity.activity_groupings) == 1
    assert activity.activity_groupings[0].activity_group_uid == activity_group.uid
    assert activity.activity_groupings[0].activity_subgroup_uid == activity_subgroup.uid

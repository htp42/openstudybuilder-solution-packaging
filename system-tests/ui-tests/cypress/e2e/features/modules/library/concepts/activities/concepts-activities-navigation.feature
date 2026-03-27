@REQ_ID:1070683 @smoke_test

Feature: Library - Concepts - Activities - Navigation
    As a user I want to navigate to each page

    Background: User must be logged in
        Given The user is logged in
        Then The '/library' page is opened

    Scenario: [Navigation] User must be able to navigate to the Activities page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        Then The current URL is '/library/activities/activities'

    Scenario: [Navigation] User must be able to navigate to the Activity Groups page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Groups' tab is selected
        Then The current URL is '/library/activities/activity-groups'

    Scenario: [Navigation] User must be able to navigate to the Activity Subgroups page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Subgroups' tab is selected
        Then The current URL is '/library/activities/activity-subgroups'
    
    Scenario: [Navigation] User must be able to navigate to the Activities by Grouping page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activities by Grouping' tab is selected
        Then The current URL is '/library/activities/activities-by-grouping'

    Scenario: [Navigation] User must be able to navigate to the Activities Instances page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Instances' tab is selected
        Then The current URL is '/library/activities/activity-instances'

    Scenario: [Navigation] User must be able to navigate to the Requested Activities page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Requested Activities' tab is selected
        Then The current URL is '/library/activities/requested-activities'

    Scenario: [Navigation] User must be able to navigate to the Activity Instance Classes page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Instance Classes' tab is selected
        Then The current URL is '/library/activities/activity-instance-classes'

    Scenario: [Navigation] User must be able to navigate to the Activity Item Classes page
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Item Classes' tab is selected
        Then The current URL is '/library/activities/activity-item-classes'
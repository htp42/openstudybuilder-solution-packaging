@REQ_ID:1070683

Feature: Library - Concepts - Activities - Requested Activities
    As a user, I want to manage Requested Activities in the Concepts Library
    
    Background: User must be logged in
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Requested Activities page
        Given The '/library' page is opened
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Requested Activities' tab is selected
        Then The current URL is '/library/activities/requested-activities'

    Scenario: [Table][Options] User must be able to see table with correct options
        Given The '/library/activities/requested-activities' page is opened
        Then A table is visible with following options
            | options                                                         |
            | Filters                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Show version history                                            |
            | Add select boxes to table to allow selection of rows for export |
            | search-field                                                    |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the columns list on the main page as below
        Given The '/library/activities/requested-activities' page is opened
        And A table is visible with following headers
            | headers                        |
            | Activity group                 |
            | Activity subgroup              |
            | Activity                       |
            | Sentence case name             |
            | Abbreviation                   |
            | Definition                     |
            | Rationale for activity request |
            | Modified                       |
            | Modified by                    |
            | Status                         |
            | Version                        |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/activities/requested-activities' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create] User must not be able to create activity request from library level
        Given The '/library/activities/requested-activities' page is opened
        Then The add activity request button is not available

    Scenario: [Actions][New version] User must be able to add a new version for the approved activity request
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And Requested activity is found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    Scenario: [Actions][Inactivate] User must be able to inactivate the approved version of the activity request
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And Requested activity is found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate the inactivated version of the activity request
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And [API] Requested activity is inactivated
        And Requested activity is found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Approve] User must be able to Approve the drafted version of the activity request
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And Requested activity is found
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    @manual_test
    Scenario: User must be able to handle and approve an activity placeholder request
        Given The '/library/activities/requested-activities' page is opened
        And The test activity request exists with a status as Final
        When The 'Handle placeholder request' option is clicked from the three dot menu list
        And The activity request is approved
        Then The new activity request is saved with a status as 'Retired'
        And The activity request appears as available activity in the study
        And The activity appears in sponsor library

    @manual_test
    Scenario: User must be able to handle and reject an activity placeholder request
        Given The '/library/activities/requested-activities' page is opened
        And The test activity request exists with a status as Final
        When The 'Handle placeholder request' option is clicked from the three dot menu list
        And The activity request is rejected
        Then The new activity request is saved with a status as 'Retired'
        And The activity request appears as rejected for study

    Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the requested activity
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And Requested activity is found
        And The item actions button is clicked
        Then 'Approve' action is available
        And 'History' action is available
        And 'Edit' action is not available

    Scenario: [Actions][Availability][Final item] User must only have access to new version, inactivate, history actions for Final version of the requested activity
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And Requested activity is found
        And The item actions button is clicked
        Then Only actions that should be avaiable for the Final item are displayed

    Scenario: [Actions][Availability][Retired item] User must only have access to reactivate, history actions for Retired version of the requested activity
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And [API] Requested activity is inactivated
        And Requested activity is found
        And The item actions button is clicked
        Then Only actions that should be avaiable for the Retired item are displayed

    Scenario: [Actions][Availability][Final item] User must have access to Handle placeholder request action for Final version of the requested activity
        Given The '/library/activities/requested-activities' page is opened
        And [API] Requested activity in status Draft exists
        And [API] Requested activity is approved
        And Requested activity is found
        And The item actions button is clicked
        Then 'Handle placeholder request' action is available

    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search created activity request
        Given The '/library/activities/requested-activities' page is opened
        When [API] First requested activity for search test is created
        And [API] Second requested activity for search test is created
        Then One activity request is found after performing full name search
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario: [Table][Search][Negative case] User must be able to search not existing activity request and table will correctly filtered
        Given The '/library/activities/requested-activities' page is opened
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        Given The '/library/activities/requested-activities' page is opened
        And User adds column 'Status' to filters
        When The user changes status filter value to 'Final'
        And The existing item is searched for by partial name
        And The item is not found and table is correctly filtered
        And The user changes status filter value to 'Draft'
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
        Given The '/library/activities/requested-activities' page is opened
        When The existing item in search by lowercased name
        And More than one result is found

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        Given The '/library/activities/requested-activities' page is opened
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
        | name                           |
        | Activity group                 |
        | Activity subgroup              |
        | Activity                       |
        | Sentence case name             |
        | Abbreviation                   |
        | Definition                     |
        | Rationale for activity request |
        | Modified by                    |
        | Version                        |
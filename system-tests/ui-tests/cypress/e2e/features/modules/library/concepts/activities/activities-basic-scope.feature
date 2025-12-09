@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activities - Basic Scope
    As a user, I want to manage every Activities in the Concepts Library

    Background: User must be logged in
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Activities page
        Given The '/library' page is opened
        When The 'Activities' submenu is clicked in the 'Concepts' section
        Then The current URL is '/library/activities/activities'

    Scenario: [Table][Options] User must be able to see table with correct options
        And The '/library/activities/activities' page is opened
        Then A table is visible with following options
            | options                                                         |
            | Add activity                                                    |
            | Filters                                                         |
            | Columns                                                         |
            | Export                                                          |
            | Show version history                                            |
            | Add select boxes to table to allow selection of rows for export |
            | search-field                                                    |

    @smoke_test
     Scenario: [Table][Columns][Names] User must be able to see the columns list on the main page as below
        And The '/library/activities/activities' page is opened
        And A table is visible with following headers
            | headers            |
            | Library            |
            | Activity group     |
            | Activity subgroup  |
            | Activity name      |
            | Sentence case name |
            | Synonyms           |     
            | NCI Concept ID     |
            | NCI Concept Name   |
            | Abbreviation       |
            | Data collection    |
            | Legacy usage       |
            | Modified           |
            | Modified by        |
            | Status             |
            | Version            |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table
        And The '/library/activities/activities' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Table][Pagination] User must be able to use table pagination
        And The '/library/activities/activities' page is opened
        When The user switches pages of the table
        Then The table page presents correct data

    @smoke_test
    Scenario: [Create][Positive case] User must be able to add a new activity
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        When The Add activity button is clicked
        And The activity form is filled with all data
        #TODO And The 'Multiple instance allowed' checkbox is set to true by default
        And Form save button is clicked
        Then Message confiriming activity creation is displayed
        And User waits for activity filter request to finish
        And Activity is searched for and found
        And The newly added activity is visible in the table
        And The item has status 'Draft' and version '0.1'

    @pending_implementation
    Scenario: [Create][Positive case] User must be able to add a new activity with no multiple instances allowed
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        When The Add activity button is clicked
        And The activity form is filled with all data
        And The 'Multiple instance allowed' checkbox is set to 'false' by user
        And Form save button is clicked
        Then Message confiriming activity creation is displayed
        And User waits for activity filter request to finish
        And Activity is searched for and found
        And The newly added activity is visible in the table
        And The item has status 'Draft' and version '0.1'

    Scenario: [Actions][Inactivate] User must be able to inactivate the approved version of the activity
        And [API] Activity in status Draft exists
        And [API] Activity is approved
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The item has status 'Retired' and version '1.0' 

    Scenario: [Actions][Reactivate] User must be able to reactivate the inactivated version of the activity
        And [API] Activity in status Draft exists
        And [API] Activity is approved
        And [API] Activity is inactivated
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0' 

    Scenario: [Actions][Edit][version 0.1] User must be able to edit the Drafted version of the activity
        And [API] Activity in status Draft exists
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'Edit' option is clicked from the three dot menu list
        And The activity edition form is filled with data
        And Form save button is clicked
        And Activity is searched for and found
        Then The item has status 'Draft' and version '0.2'

    Scenario: [Actions][Approve] User must be able to Approve the drafted version of the activity
        And [API] Activity in status Draft exists
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Delete] User must be able to Delete the intial created version of the activity
        And [API] Activity in status Draft exists
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'Delete' option is clicked from the three dot menu list
        Then Activity is searched for and not found

    Scenario: [Actions][New version] User must be able to add a new version for the approved activity
        And [API] Activity in status Draft exists
        And [API] Activity is approved
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        And Activity is searched for and found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search created activity
        When [API] First activity for search test is created
        And [API] Second activity for search test is created
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        Then Activity is searched for and found
        And The existing item is searched for by partial name
        Then More than one result is found 

    Scenario: [Table][Search][Negative case] User must be able to search not existing activity and table will correctly filtered
        And The '/library/activities/activities' page is opened
        And User sets status filter to 'all'
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        And The '/library/activities/activities' page is opened
        When User sets status filter to 'final'
        And The existing item is searched for by partial name
        And The item is not found and table is correctly filtered
        And User sets status filter to 'draft'
        And The existing item is searched for by partial name
        Then More than one result is found
    
    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
        And The '/library/activities/activities' page is opened
        When User sets status filter to 'all'
        When The existing item in search by lowercased name
        And More than one result is found

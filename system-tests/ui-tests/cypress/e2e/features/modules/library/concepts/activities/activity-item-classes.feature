@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Item Classes
    As a user, I want to manage every Activities in the Concepts Library

    Background: User must be logged in
        Given The user is logged in
        And The '/library/activities/activity-item-classes' page is opened

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Activity Subgroups page
        Given The '/library' page is opened
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Item Classes' tab is selected
        Then The current URL is '/library/activities/activity-item-classes'

    Scenario: [Table][Options] User must be able to see table with correct options
        And The '/library/activities/activities' page is opened
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
        And A table is visible with following headers
            | headers          |
            | Name             |
            | Definition       |
            | NCI Code         |
            | Modified         |
            | Modified by      |     
            | Version          |
            | Status           |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Table][Pagination] User must be able to use table pagination
        When The user switches pages of the table
        Then The table page presents correct data

    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search created activity instance
        Then Activity Item class is searched for and found
        And Activity Item class is searched for by partial name
        Then More than one result is found

    Scenario: [Table][Search][Negative case] User must be able to search not existing group and table will correctly filtered
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        And The user filters table by status 'Final'
        And Activity Item class is searched for by partial name
        Then More than one result is found

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
            | name          |
            | Name          |
            | Definition    |
            | NCI Code      |
            | Modified by   |
            | Version       |
            | Status        |
@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Groups
    As a user, I want to manage every Activity Groups in the Concepts Library
    
    Background: User must be logged in
        Given The user is logged in
        And The '/library/activities/activity-groups' page is opened
        And User sets status filter to 'all'
    
    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search created group
        When [API] First activity group for search test is created
        And [API] Second activity group for search test is created
        Then Activity group is searched for and found
        And The existing item is searched for by partial name
        Then More than one result is found 

    Scenario: [Table][Search][Negative case] User must be able to search not existing group and table will correctly filtered
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        When User sets status filter to 'final'
        And The existing item is searched for by partial name
        And The item is not found and table is correctly filtered
        And User sets status filter to 'draft'
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario: [Table][Filtering][Status selection] User must be able to see that Final status is selected by default
        And [API] Activity group in status Draft exists
        And The '/library/activities/activity-groups' page is opened
        And Activity group is searched for and not found
        And [API] Activity group is approved
        And The '/library/activities/activity-groups' page is opened
        And Activity group is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide draft activity group
        And [API] Activity group in status Draft exists
        When User sets status filter to 'final'
        And Activity group is searched for and not found
        When User sets status filter to 'draft'
        And Activity group is searched for and found
        When User sets status filter to 'retired'
        And Activity group is searched for and not found
        When User sets status filter to 'all'
        And Activity group is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide approved activity group
        And [API] Activity group in status Draft exists
        And [API] Activity group is approved
        When User sets status filter to 'draft'
        And Activity group is searched for and not found
        When User sets status filter to 'final'
        And Activity group is searched for and found
        When User sets status filter to 'retired'
        And Activity group is searched for and not found
        When User sets status filter to 'all'
        And Activity group is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide retired activity group
        And [API] Activity group in status Draft exists
        And [API] Activity group is approved
        And [API] Activity group is inactivated
        When User sets status filter to 'draft'
        And Activity group is searched for and not found
        When User sets status filter to 'retired'
        And Activity group is searched for and found
        When User sets status filter to 'final'
        And Activity group is searched for and not found
        When User sets status filter to 'all'
        And Activity group is searched for and found
    
    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide new version of activity group
        And [API] Activity group in status Draft exists
        And [API] Activity group is approved
        And [API] Activity group gets new version
        When User sets status filter to 'final'
        And Activity group is searched for and not found
        When User sets status filter to 'draft'
        And Activity group is searched for and found
        When User sets status filter to 'retired'
        And Activity group is searched for and not found
        When User sets status filter to 'all'
        And Activity group is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to see that status filter is not available after expanding column based filters
        Then The status filter is not available when expanding available filters

    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
        When The existing item in search by lowercased name
        And More than one result is found

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
        | name               |
        | Activity group     |
        | Sentence case name |
        | Abbreviation       |
        | Definition         |
        | Version            |
@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activities - Filtering
    As a user, I want to manage every Activities in the Concepts Library

    Background: User must be logged in
        Given The user is logged in

    Scenario: [Table][Filtering][Status selection] User must be able to see that Final status is selected by default
        When [API] Activity in status Draft exists
        And The '/library/activities/activities' page is opened
        And Activity is searched for and not found
        And [API] Activity is approved
        And The '/library/activities/activities' page is opened
        And Activity is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide draft activity
        When [API] Activity in status Draft exists
        Given The '/library/activities/activities' page is opened
        When User sets status filter to 'final'
        And Activity is searched for and not found
        When User sets status filter to 'draft'
        And Activity is searched for and found
        When User sets status filter to 'retired'
        And Activity is searched for and not found
        When User sets status filter to 'all'
        And Activity is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide approved activity
        When [API] Activity in status Draft exists
        And [API] Activity is approved
        Given The '/library/activities/activities' page is opened
        When User sets status filter to 'draft'
        And Activity is searched for and not found
        When User sets status filter to 'final'
        And Activity is searched for and found
        When User sets status filter to 'retired'
        And Activity is searched for and not found
        When User sets status filter to 'all'
        And Activity is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide retired activity
        When [API] Activity in status Draft exists
        And [API] Activity is approved
        And [API] Activity is inactivated
        Given The '/library/activities/activities' page is opened
        When User sets status filter to 'draft'
        And Activity is searched for and not found
        When User sets status filter to 'retired'
        And Activity is searched for and found
        When User sets status filter to 'final'
        And Activity is searched for and not found
        When User sets status filter to 'all'
        And Activity is searched for and found
    
    Scenario: [Table][Filtering][Status selection] User must be able to use status selection to find or hide new version of activity
        When [API] Activity in status Draft exists
        And [API] Activity is approved
        And [API] Activity new version is created
        Given The '/library/activities/activities' page is opened
        When User sets status filter to 'final'
        And Activity is searched for and not found
        When User sets status filter to 'draft'
        And Activity is searched for and found
        When User sets status filter to 'retired'
        And Activity is searched for and not found
        When User sets status filter to 'all'
        And Activity is searched for and found

    Scenario: [Table][Filtering][Status selection] User must be able to see that status filter is not available after expanding column based filters
        Given The '/library/activities/activities' page is opened
        Then The status filter is not available when expanding available filters

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        And The '/library/activities/activities' page is opened
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
        | name               |
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
        | Modified by        |
        | Version            |

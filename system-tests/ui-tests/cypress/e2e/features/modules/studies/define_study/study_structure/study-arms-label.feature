@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Manually Defined Study Arms

    As a system user,
    I want the system to ensure [Scenario],
    So that I must be able to make complete and consistent specification of study arms.

    Background: User is logged in and study has been selected
        Given The user is logged in
        When Get study 'CDISC DEV-9878' uid
        And Select study with uid saved in previous step
        Then The page 'study_structure/arms' is opened for selected study
    
    Scenario: [Test data] User must be able to delete all existing arms and cohorts before tests start
        And [API] Get all Study Arms within selected study
        And [API] Delete all Study Arms within selected study
        And [API] Get all Study Cohorts within selected study
        And [API] Delete all Study Cohorts within selected study

    Scenario: [Create][Default Label Value] User must be able to see that by default arm label is empty
        Given User intercepts and wait for the design class request
        And The plus button is clicked
        When User select manual study structure
        And User continues to next step of study structure stepper
        Then The Arm label is empty by default

    Scenario: [Create][Postive case] User must be able to add arm with study label
        Given User intercepts and wait for the design class request
        And The plus button is clicked
        When User select manual study structure
        And User continues to next step of study structure stepper
        And User fills arm mandatory data
        And User provides the study arm label
        And User saves and exits study structure stepper
        Then User searches for created arm and it is found in the table
        And The study arm label value is visible in the table

    Scenario: [Edit][Postive case] User must be able to edit study label via wizard
        When The pencil button is clicked
        And User provides the study arm label
        And User saves and exits study structure stepper
        Then User searches for created arm and it is found in the table
        And The study arm label value is visible in the table

    Scenario: [Create][Postive case] User must be able to add arm without study label
        Given [API] Get all Study Arms within selected study
        And [API] Delete all Study Arms within selected study
        When The page 'study_structure/arms' is opened for selected study
        And User intercepts and wait for the design class request
        And The plus button is clicked
        And User select manual study structure
        And User continues to next step of study structure stepper
        And User fills arm mandatory data
        And User saves and exits study structure stepper
        Then User searches for created arm and it is found in the table
        And The study arm label value is empty

    Scenario: [Edit][Postive case] User must be able to edit study label via form window
        Given User searches for created arm and it is found in the table
        When The 'Edit' option is clicked from the three dot menu list
        And User provides the study arm label
        And Form save button is clicked
        Then User searches for created arm and it is found in the table
        And The study arm label value is visible in the table

    Scenario: [Character limit] User must be add arm label with max 40 character length
        Given [API] Get all Study Arms within selected study
        And [API] Delete all Study Arms within selected study
        When The page 'study_structure/arms' is opened for selected study
        And User intercepts and wait for the design class request
        And The plus button is clicked
        And User select manual study structure
        And User continues to next step of study structure stepper
        And User provides the study arm label with 41 characters
        Then The warning message about arm label exceeding 40 characters is displayed
        And User fills arm mandatory data
        And User provides the study arm label with 40 characters
        And User saves and exits study structure stepper
        Then User searches for created arm and it is found in the table
        And The study arm label value is visible in the table

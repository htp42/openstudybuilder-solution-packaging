@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Study Visits - Non Visit

    See shared notes for study visits in file study-visit-intro-notes.txt

    Background: User is logged in and study has been selected
        Given The user is logged in
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        And [API] The epoch with type 'Pre Treatment' and subtype 'Run-in' exists in selected study

    Scenario: [Create][Non visit] User must be able to create non visit for given study
        When The page 'study_structure/visits' is opened for selected study
        And User waits for epochs to load
        When Add visit button is clicked
        And Visit scheduling type is selected as 'NON_VISIT'
        And Form continue button is clicked
        And Epoch 'Basic' is selected for the visit
        And Form continue button is clicked
        And Form save button is clicked
        And The pop up displays 'Visit added'
        When User searches for 'Non-visit'
        Then Study visit class is 'Non visit' and the timing is empty

    @BUG_ID:2776541
    Scenario: [EDIT][Special visit] User must not be able to edit non visit number
        When The page 'study_structure/visits' is opened for selected study
        When User searches for 'Non-visit'
        And The 'Edit' option is clicked from the three dot menu list
        And Form continue button is clicked
        And Form continue button is clicked 
        Then Visit number field is disabled
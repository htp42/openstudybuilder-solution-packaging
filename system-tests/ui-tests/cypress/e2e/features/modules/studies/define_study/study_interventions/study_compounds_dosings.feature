@REQ_ID:1074257
Feature: Studies - Define Study - Study Interventions - Study Compound Dosings

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    Scenario: [Navigaion] User must be able to navigate to the Study Compound Dosings page
        Given The '/studies' page is opened
        When The 'Study Interventions' submenu is clicked in the 'Define Study' section
        And The 'Study Compound Dosings' tab is selected
        Then The current URL is '/study_interventions/study_compound_dosings'

    Scenario: [Table][Columns][Names] User must be able to see the page table with correct columns
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        Then A table is visible with following headers
            | headers             |
            | #                   |
            | Study Element       |
            | Compound Name       |
            | Medicinal product   |
            | Compound Alias Name |
            | Preferred Alias     |
            | Dose Value          |
            | Dose Frequency      |

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create] User must be able to create a study compound dosings
        Given [API] Uids are fetched for element subtype 'Treatment'
        And [API] Element is created for the test study
        And The study compounds data is cleaned for testing purspose
        And The test study '/study_interventions/study_compounds' page is opened
        When User clicks add study compund button
        And User select first type of treatment
        And Form continue button is clicked
        And User select first compund
        And User select first medicinal product
        And Form continue button is clicked
        And User fills other information
        And User intercepts compund create request
        When Form save button is clicked
        And The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        And The user select first compund
        And Form continue button is clicked
        And The user select first dose value
        And The user intercepts study compund dosings create request
        When Form save button is clicked
        Then The study compound dosing is present in the compound dosings table

    Scenario: [Edit] User must be able to edit a study compound dosing
        Given The study compound dosing data is cleaned for testing purspose
        And The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        And The user select first compund
        And Form continue button is clicked
        And The user select first dose value
        And The user intercepts study compund dosings create request
        When Form save button is clicked
        And User waits for the table
        When The 'Edit' option is clicked from the three dot menu list
        And The user select last study element
        And Form continue button is clicked
        And The user select last compund
        And Form continue button is clicked
        And The user select last dose value
        When The user intercepts study compund dosings update request
        When Form save button is clicked
        Then The study compound dosing is present in the compound dosings table

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element order must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element order for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element type must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element type for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element subtype must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element subtype for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element name must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element name for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element short name be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element short name for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Element] Element description must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study elements request
        When The user clicks add study compund dosing
        And The user select first study element
        Then The element description for this element is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Compound] Compound order must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study compunds request
        And The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        When The user select first compund
        Then The compound order in dosings from for this compound is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Compound] Type of treatment must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study compunds request
        And The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        When The user select first compund
        Then The type of treatment in dosings from for this compound is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Compound] Compound name must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study compunds request
        And The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        When The user select first compund
        Then The compound name in dosings from for this compound is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Compound] Compound alias name be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study compunds request
        And The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        When The user select first compund
        Then The compound alias name in dosings from for this compound is automatically populated from library

    Scenario: [Create][Form behaviour][Compound Dosings][Compound] Preffered synonym must be automatically populated when selecting study compound
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        And The user intercepts study compunds request
        And The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        When The user select first compund
        Then The preferred synonim in dosings from for this compound is automatically populated from library

    Scenario: [Create] User must not be able to create a study compound dosing without the study element selected
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And Form continue button is clicked
        Then The user cannot save the form

    Scenario: [Create] User must not be able to create a study compound without the study compound selected
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        And Form continue button is clicked
        Then The user cannot save the form

    Scenario: [Create] User must be able to create a study compound without the dosing selected
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        And The user select first compund
        And Form continue button is clicked
        When Form save button is clicked
        Then The pop up displays 'Study compound dosing added'

    Scenario: [Delete] User must be able to delete a study compound
        Given The study compound dosing data is cleaned for testing purspose
        And The test study '/study_interventions/study_compound_dosings' page is opened
        When The user clicks add study compund dosing
        And The user select first study element
        And Form continue button is clicked
        And The user select first compund
        And Form continue button is clicked
        And The user select first dose value
        And The user intercepts study compund dosings create request
        When Form save button is clicked
        And User waits for the table
        When The 'Delete' option is clicked from the three dot menu list
        And The user intercepts study compound dosing delete request
        And Action is confirmed by clicking continue
        Then The study compound dosing is removed
        And The pop up displays 'Study compound dosing deleted'

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When User clicks table export button
        And User selects 'CSV' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompoundDosings' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When User clicks table export button
        And User selects 'JSON' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompoundDosings' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When User clicks table export button
        And User selects 'XML' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompoundDosings' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        Given The test study '/study_interventions/study_compound_dosings' page is opened
        When User clicks table export button
        And User selects 'EXCEL' format to export the table content
        And Action is confirmed by clicking continue
        Then The study specific 'StudyCompoundDosings' file is downloaded in 'xlsx' format


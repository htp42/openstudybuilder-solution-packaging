@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Manually Defined Study Arms

    As a system user,
    I want the system to ensure [Scenario],
    So that I must be able to make complete and consistent specification of study arms.

    Background: User is logged in and study has been selected
        Given The user is logged in
        And A test study is selected

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Study Arms page using side menu
        Given The '/studies' page is opened
        When The 'Study Structure' submenu is clicked in the 'Define Study' section
        And The 'Study Arms' tab is selected
        Then The current URL is '/study_structure/arms'

    Scenario: [Table][Options] User must be able to see the Study Arms table with following options
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        Then A table is visible with following options
            | options                                                         |
            | Cohorts Stepper                                                 |
            | Columns                                                         |
            | Export                                                          |
            | Show version history                                            |
            | Add select boxes to table to allow selection of rows for export |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Study Arms table with following columns
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And A table is visible with following headers
            | headers             |
            | #                   |
            | Type                |
            | Arm name            |
            | Arm short name      |
            | Random. group       |
            | Random. code        |
            | No. of participants |
            | Connected Branches  |
            | Description         |
            | Modified            |
            | Modified by         |

    Scenario: [Online help] User must be able to read online help for the page
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The online help button is clicked
        Then The online help panel shows 'Study Arms' panel with content "Specification of the planned investigational treatment arms. An arm is a planned 'path' of interventions through the trial, e.g. arm AB is treatment A followed by treatment B."

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    @smoke_test
    Scenario: [Create][Positive case] User must be able to add a new Study Arm
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The new study arm form is filled and saved
        Then The new study arm is visible within the study arms table

    Scenario: [Actions][Edit] User must be able to edit an existing Study Arm
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The arm data is edited and saved
        Then The study arm with updated values is visible within the study arms table

    Scenario: [Create][Mandatory fields] User must not be able to provide value less than zero for number of participants
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The value '-10' is entered for the field Number of subjects in the Study Arms form
        Then Validation message "Value can't be less than 0" is displayed

    Scenario: [Create][Mandatory fields] User must not be able to create a Study Arm without Study Arm Type, Arm Name and Arm Short Name provided in the Study Arms form
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The study arm type, arm name and arm short name is not populated
        Then The required field validation appears for the '3' empty fields

    Scenario: [Create][Uniqueness check][Name] User must not be able to create two Arms within one study using the same Arm name
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The two study arms are defined with the same name
        Then The system displays the message "Value 'UV1' in field Arm name is not unique for the study."

    Scenario: [Create][Uniqueness check][Short Name] User must not be able to create two Arms within one study using the same Arm short name
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The two study arms are defined with the same short name
        Then The system displays the message "Value 'UV2' in field Arm short name is not unique for the study."

    Scenario: [Create][Uniqueness check][Randomisation group] User must not be able to create two Arms within one study using the same Arm randomisation group
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The two study arms are defined with the same randomisation group
        Then The system displays the message "Value 'UV3' in field Arm Randomization code is not unique for the study."

    Scenario: [Create][Mandatory fields] User must not be able to use text longer than 20 characters for the Study Arm Arm Code field in the Study Arms form
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The study arm code is updated to exceed 20 characters
        Then The message 'This field must not exceed 20 characters' is displayed

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The user exports the data in 'CSV' format
        Then The study specific 'StudyArms' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The user exports the data in 'JSON' format
        Then The study specific 'StudyArms' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The user exports the data in 'XML' format
        Then The study specific 'StudyArms' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The user exports the data in 'EXCEL' format
        Then The study specific 'StudyArms' file is downloaded in 'xlsx' format

    @manual_test
    Scenario: User must be presented with the warning message when deleting Study Arm
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The study arm related to study branch arm and study design cell exists
        And The Study Arm is found
        When The 'Delete' option is clicked from the three dot menu list
        Then The warning message appears 'Removing this Study Arm will remove all related Study Cells and Branches'

    @manual_test
    Scenario: User must be able to delete all related items to Study Arm when Study arm is removed
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The study arm related to study branch arm and study design cell exists
        When The the study arm related to those elements is removed
        Then That study arm no longer exists
        And Related study design cells are deleted
        And Related study branch arms are deleted

    @manual_test
    Scenario: User must be able to read change history of output
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        When The user opens version history
        Then The user is presented with version history of the output containing timestamp and username

    @manual_test
    Scenario: User must be able to read change history of selected element
        Given The study for testing manually defined study structure is selected
        When The study 'arms' page is opened for that study
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames
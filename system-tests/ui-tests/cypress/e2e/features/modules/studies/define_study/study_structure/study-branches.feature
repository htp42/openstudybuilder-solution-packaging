@REQ_ID:1074254
Feature: Studies - Define Study - Study Structure - Manually Defined Study Branches

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study branch arms.

    Background: User is logged in
        Given The user is logged in
        And The study for testing manually defined study structure is selected
        And [API] Uid of study type 'Investigational Arm' is fetched
        And A study with Study Arms has been selected
        And The study 'branches' page is opened for that study
        And User waits for table to load

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Study Branches page using side menu
        Given A test study is selected
        Given The '/studies' page is opened
        When The 'Study Structure' submenu is clicked in the 'Define Study' section
        And The 'Study Branches' tab is selected
        Then The current URL is '/study_structure/branches'

    Scenario: [Table][Options] User must be able to see the Study Branches table with following options
        Then A table is visible with following options
            | options                                                         |
            | Columns                                                         |
            | Add select boxes to table to allow selection of rows for export |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Study Branches table with following columns
        And A table is visible with following headers
            | headers             |
            | #                   |
            | Arm name            |
            | Branch name         |
            | Short name          |
            | Cohort name         |
            | Cohort code         |
            | Random. group       |
            | Random. Code        |
            | No. of participants |
            | Modified            |
            | Modified by         |

    Scenario: [Online help] User must be able to read online help for the page
        And The online help button is clicked
        Then The online help panel shows 'Study Branches' panel with content "The decision points where subjects are divided into separate treatment groups. For a simple parallel or cross-over design subject are branched into treatment arms at randomisation. i.e. have one branch decision point. A study can have more branching points if e.g. subjects are assigned to a recover treatment after initial randomisation. This second decision point could be based on a responsiveness to treatment."

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Pre-condition][No Arms] User must be informed that no Study Arms are available
        When Get study 'CDISC DEV-9880' uid
        And Select study with uid saved in previous step
        When The page 'study_structure/branches' is opened for selected study
        Then The table display the note "No data available - Create Study Arm first"
        And The option to create branch arm is not visible

    @smoke_test
    Scenario: [Create][Existing Arm] User must be able to create a new study arm branch for existing arm
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And The form for new study branch arm is filled
        And Form save button is clicked
        And The Study Branch is found
        Then The study branch arm is visible within the table

    Scenario: [Actions][Edit] User must be able to edit the Study Branch Arm
        And The Study Branch is found
        And The 'Edit' option is clicked from the three dot menu list
        When The study branch arm is edited
        And Form save button is clicked
        And The form is closed
        Then The pop up displays 'Branch Arm updated'
        And The Study Branch is found
        Then The study branch arm is visible within the table

    Scenario: [Actions][Edit][Fields check] User must not be able to change the Study Arm for created Study Branch Arm
        And Add branch button is clicked
        And The first available arm is selected for the branch
        When The form for new study branch arm is filled
        And Form save button is clicked
        And The form is closed
        And The Study Branch is found
        And The 'Edit' option is clicked from the three dot menu list
        Then The stady arm field is disabled

    Scenario Outline: [Create][Fields check] User must not be able to provide value other than positive integer for Number of subjects
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And Planned number of subjects for branch is set as '<number>'
        Then The validation appears under the field in the Study Branch Arms form

        Examples:
            | number |
            | -123   |
            | -1     |
            | 0      |

    Scenario: [Create][Fields check] User must not be able to provide a value for number of subjects higher than the number defined for the study arm
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And Planned number of subjects for branch is set as '101'
        Then The message 'Number of subjects in a branch cannot exceed total number of subjects in the arm' is displayed

    Scenario: [Create][Mandatory fields] User must not be able to create a Study Branch Arm without Study Arm selected
        And Add branch button is clicked
        When The Study Arm field is not populated in the Study Branch Arms form
        And The Branch name field is not populated
        And The Branch short name field is not populated
        And Form save button is clicked
        Then The required field validation appears for the '3' empty fields
        And The form is not closed

    Scenario: [Create][Uniqueness check][Name] User must not be able to create two Branch Arms within one study using the same Branch Arm name
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And The form for new study branch arm is filled
        And Form save button is clicked
        And The form is closed
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And Another Study Branch Arm is created with the same arm name
        And Form save button is clicked
        Then The system displays the message "in field Branch Arm Name is not unique for the study"
        And The form is not closed

    Scenario: [Create][Uniqueness check][Short Name] User must not be able to create two Branch Arms within one study using the same Branch Arm short name
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And The form for new study branch arm is filled
        And Form save button is clicked
        And The form is closed
        And Add branch button is clicked
        And The first available arm is selected for the branch
        And Another Study Branch Arm is created with the same branch arm short name
        And Form save button is clicked
        Then The system displays the message "in field Branch Arm Short Name is not unique for the study"
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to use text longer than 20 characters for the Study Arm Arm Code field in the Study Arms form
        And Add branch button is clicked
        And For the Random. code a text longer than 20 characters is provided in the Study Branch Arms form
        And Form save button is clicked
        Then The message 'This field must not exceed 20 characters' is displayed

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        And The user exports the data in 'CSV' format
        Then The study specific 'StudyBranches' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        And The user exports the data in 'JSON' format
        Then The study specific 'StudyBranches' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        And The user exports the data in 'XML' format
        Then The study specific 'StudyBranches' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        And The user exports the data in 'EXCEL' format
        Then The study specific 'StudyBranches' file is downloaded in 'xlsx' format

    @manual_test
    Scenario: User must be able to remove the Study Branch Arm
        Given The test study '/study_structure/branches' page is opened
        And The test Study Branch Arm is available
        When The delete action is clicked for the test Study Branch Arm
        Then The test Study Branch Arm is no longer available
        And related Study Design Cell selections are cascade deleted

    @manual_test
    Scenario: User must be presented with the warning message when removing the last Study Branch Arm
        Given The test study '/study_structure/branches' page is opened
        And The test study branch arm is available
        And The test study arm is related to study design cell
        When The 'Delete' option is clicked from the three dot menu list
        Then The warning message appears 'Removing this Study Branch Arm will remove all related Study Cells'

    @manual_test
    Scenario: Deleting last Study Branch Arm for a Study Arm must update relationship to Study Design Cell
        Given a Study Arm has been defined for the study
        And only one Study Branch Arm exist related to this Study Arm
        And the Study Branch Arm have Study Design Cell relationships to Study Elements for a Study Epochs
        When The delete action is clicked for the Study Branch Arm
        Then The Study Design Cell selections will change their relationship from the Study Branch Arm to the related Study Arm

    @manual_test
    Scenario: User must be able to read change history of output
        Given The test study '/study_structure/branches' page is opened
        When The user opens version history
        Then The user is presented with version history of the output containing timestamp and username

    @manual_test
    Scenario: User must be able to read change history of selected element
        Given The test study '/study_structure/branches' page is opened
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames
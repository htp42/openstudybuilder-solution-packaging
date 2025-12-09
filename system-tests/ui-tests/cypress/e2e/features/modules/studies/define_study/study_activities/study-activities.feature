@REQ_ID:1074260
Feature: Studies - Define Study - Study Activities - Study Activities

    As a system user,
    I want the system to ensure [Scenario],
    So that I can make complete and consistent specification of study activities.

    Background: User is logged in and study has been selected
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to Study Activity page using side menu
        Given A test study is selected
        And The '/studies' page is opened
        When The 'Study Activities' submenu is clicked in the 'Define Study' section
        Then The current URL is '/activities/soa'

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the Study Activities table with options listed in this scenario
        Given The test study '/activities/list' page is opened
        Then A table is visible with following headers
            | headers           |
            #| #                 |
            | Library           |
            | SoA group         |
            | Activity group    |
            | Activity subgroup |
            | Activity          |
            | Data collection   |
            | Modified          |
            | Modified by       |

    Scenario: [Table][Columns][Visibility] User must be able to use column selection option
        Given The test study '/activities/list' page is opened
        And Study activities for selected study are loaded
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    @smoke_test
    Scenario: [Create][Existing Study][By Id] User must be able to create a Study Activity from an existing study by study id
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from studies is selected
        And Study with id value '999-3000' is selected
        And Form continue button is clicked
        And User selects first available activity
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        And The Study Activity is found
        Then The Study Activity is visible in table

    Scenario: [Actions][Delete][Activity] User must be able to delete a Study Activity
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity is searched for and found
        When The 'Remove Activity' option is clicked from the three dot menu list
        And Action is confirmed by clicking continue
        Then Activity is searched for and not found

    @smoke_test
    Scenario: [Create][Existing Study][By Acronym] User must be able to create a Study Activity from an existing study by study acronym
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from studies is selected
        And Study with acronym value 'DummyStudy 0' is selected
        And Form continue button is clicked
        And User selects first available activity
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        And The Study Activity is found
        Then The Study Activity is visible in table

    @smoke_test
    Scenario: [Create][From Library] User must be able to create a Study Activity from the library
        And The activity exists in the library
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User selects first available activity and SoA group
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        Then The Study Activity is visible in table

    @smoke_test
    Scenario: [Create][Placeholder] User must be able to create a Study Activity placeholder as an activity concept request
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        Then The Study Activity placeholder is visible within the Study Activities table

    Scenario: [Actions][Delete][Placeholder] User must be able to delete a Study Activity placeholder
        Given The test study '/activities/list' page is opened
        And Activity placeholder is found
        When The 'Remove Activity' option is clicked from the three dot menu list
        And Action is confirmed by clicking continue
        Then The Study Activity Placeholder is no longer available

    Scenario: [Actions][Edit][version 0.1][Activity] User must be able to edit a Study Activity
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        Given The test study '/activities/list' page is opened
        And Activity is searched for and found
        When The 'Edit' option is clicked from the three dot menu list
        And The SoA group can be changed
        And Modal window 'Save' button is clicked
        And The form is no longer available
        And Activity is searched for and found
        Then The edited Study Activity data is reflected within the Study Activity table

    # Note, currently only the SoA group can be changed, not the request, will be specified and updated in later release
    Scenario: [Actions][Edit][version 0.1][Placeholder] User must be able to edit a Study Activity placeholder
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Selected study id is saved
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        When The 'Edit' option is clicked from the three dot menu list
        And The SoA group can be changed
        And Modal window 'Save' button is clicked
        And The form is no longer available
        Then The pop up displays 'Study activity updated'
        And Activity placeholder is found
        Then The edited Study Activity data is reflected within the Study Activity table

    @BUG_ID:2722627
    Scenario: [Actions][Edit][version 0.1][Placeholder] User must be able to edit data collection flag
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        When Activity placeholder data is filled in
        And Data collection flag is unchecked
        And Form save button is clicked
        And The form is no longer available
        And Activity placeholder is found
        When The 'Edit' option is clicked from the three dot menu list
        And Data collection flag is checked
        And Modal window 'Save' button is clicked
        And The form is no longer available
        Then The pop up displays 'Study activity updated'
        And Activity placeholder is found
        Then The study activity table is displaying updated value for data collection

    Scenario: [Create][Mandatory fields][Activity] User must not be able to create Study Activity from studies without study selected
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        When Activity from studies is selected
        And Form continue button is clicked
        Then The validation appears and Create Activity form stays on Study Selection

    Scenario: [Create][Mandatory fields][Activity] User must not be able to create Study Activity from library without SoA group selected
        Given The test study '/activities/list' page is opened
        When Study activity add button is clicked
        When Activity from library is selected
        And Form continue button is clicked
        And The user tries to go further without SoA group chosen
        And Form save button is clicked
        Then The validation appears and Create Activity form stays on SoA group selection

    Scenario: [Create][Mandatory fields][Placeholder] User must not be able to create Study Activity placeholder without SoA group selected
        Given The test study '/activities/list' page is opened
        And Study activity add button is clicked
        And Activity from placeholder is selected
        And Form continue button is clicked
        And The user tries to go further in activity placeholder creation without SoA group chosen
        And Form save button is clicked
        Then The validation appears under empty SoA group selection

    Scenario: [Actions][Approve] User must be able to add newly created approved Activity
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        Given The test study '/activities/list' page is opened
        Then The Study Activity is found

    Scenario: [Create][Negative case][Draft Activity] User must mot be able to add newly created draft Activity
        Given The test study '/activities/list' page is opened
        And [API] Study Activity is created and not approved
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        When User tries to add Activity in Draft status
        Then The Activity in Draft status is not found

    @unstable_disabled
    Scenario: [Create][Negative case][Draft Group] User must not be able to add activity that has Draft group until it is approved
        Given The test study '/activities/list' page is opened
        And [API] Study Activity is created and group is drafted
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then Warning that 'Draft' 'groups' can not be added to the study is displayed
        And [API] Activity group is approved
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        Then The Study Activity is found
        
    Scenario: [Create][Negative case][Retired Group]  User must not be able to add activity that has Retired group until it is approved
        Given The test study '/activities/list' page is opened
        And [API] Study Activity is created and group is inactivated
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then Warning that 'Retired' 'groups' can not be added to the study is displayed
        And [API] Activity group is reactivated
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        Then The Study Activity is found

    @unstable_disabled    
    Scenario: [Create][Negative case][Draft Subgroup] User must not be able to add activity that has Draft subgroup until it is approved
        Given The test study '/activities/list' page is opened
        And [API] Study Activity is created and subgroup is drafted
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then Warning that 'Draft' 'subgroups' can not be added to the study is displayed
        And [API] Activity subgroup is approved
        And User waits for 1 seconds
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        Then The Study Activity is found
        
    Scenario: [Create][Negative case][Retired Subgroup] User must not be able to add activity that has Retired subgroup until it is approved
        Given The test study '/activities/list' page is opened
        And [API] Study Activity is created and subgroup is inactivated
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then Warning that 'Retired' 'subgroups' can not be added to the study is displayed
        And [API] Activity subgroup is reactivated
        And User waits for 1 seconds
        When Study activity add button is clicked
        And Activity from library is selected
        And Form continue button is clicked
        And User search and select activity created via API
        And Form save button is clicked
        Then The pop up displays 'Study activity added'
        Then The Study Activity is found

    Scenario: [Export][CSV] User must be able to export the data in CSV format
        Given The test study '/activities/list' page is opened
        And The user exports the data in 'CSV' format
        Then The study specific 'StudyActivities' file is downloaded in 'csv' format

    Scenario: [Export][Json] User must be able to export the data in JSON format
        Given The test study '/activities/list' page is opened
        And The user exports the data in 'JSON' format
        Then The study specific 'StudyActivities' file is downloaded in 'json' format

    Scenario: [Export][Xml] User must be able to export the data in XML format
        Given The test study '/activities/list' page is opened
        And The user exports the data in 'XML' format
        Then The study specific 'StudyActivities' file is downloaded in 'xml' format

    Scenario: [Export][Excel] User must be able to export the data in EXCEL format
        Given The test study '/activities/list' page is opened
        And The user exports the data in 'EXCEL' format
        Then The study specific 'StudyActivities' file is downloaded in 'xlsx' format

    Scenario: User must be presented with 'red bell' when activity group has been updated
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The red alert badge is not present
        When The activity group is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        Then The red alert badge is present

    @manual_test
    Scenario: User must be presented with 'red bell' when activity subgroup has been updated
        Given [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity with two subgroups available is added to the study
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The red alert badge is not present
        When The activity subgroup is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        Then The red alert badge is present

    Scenario: User must be presented with 'red bell' when activity name has been updated
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The red alert badge is not present
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        Then The red alert badge is present

    Scenario: User must be able to accept activity updates
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user accepts the changes
        And The Study Activity is found
        Then The changes are applied in the study activity
        Then The yellow alert badge is not present
        Then The red alert badge is not present

    Scenario: User must be able to decline activity updates
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user declines the changes
        Then The yellow alert badge is present

    Scenario: Yellow exclamation mark must be removed when activity changes has been accepted
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user declines the changes
        Then The yellow alert badge is present
        When The user accepts the changes
        And The Study Activity is found
        Then The changes are applied in the study activity
        Then The yellow alert badge is not present
        Then The red alert badge is not present

    Scenario: User must be able to filter by redbell status
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        When The user filters the table by red alert status
        Then The activities with red alert are present 

    Scenario: User must be able to filter by yellow alert status
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user declines the changes
        And The test study '/activities/list' page is opened
        When The user filters the table by yellow alert status
        Then The activities with yellow alert are present 

    @manual_test       
    Scenario: User must be able to see which activity name is present in detailed soa
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity name is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user opens bulk review changes window
        Then The icon indicates which activity name is present in detailed soa

    Scenario: User must be able to see which activity group is present in detailed soa
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity group is updated for that study activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user opens bulk review changes window
        Then The icon indicates which activity group is present in detailed soa

    @manual_test
    Scenario: User must be able to see which activity subgroup is present in detailed soa
        Given The study activity exists for selected study
        And The test study '/activities/list' page is opened
        When The activity has been updated
        And The user opens changes review window for that activity
        Then The icon indicates which activity subgroup is present in detailed soa

    @manual_test
    Scenario: User must be able to select group when previously linked group has been removed (multiple groups assigned)
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity group is removed from that activity
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user selects new activity group and accepts
        Then The the changes are applied to the activity

    Scenario: User must be presented with 'Decline' option when activity status has changed to retired
        And [API] Study Activity is created and approved
        And [API] Get SoA Group 'BIOMARKERS' id
        And [API] Activity is added to the study
        When The activity has been retired
        And The test study '/activities/list' page is opened
        And The Study Activity is found
        And The user opens changes review window for that activity
        And The 'Decline and keep' button is present
        
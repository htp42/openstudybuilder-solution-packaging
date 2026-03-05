@REQ_ID:1070683 @skip_on_prv_val
Feature: Library - Concepts - Activities - Activity Instances
    As a user, I want to manage every Activity Instances in the Concepts Library
    
    Background: User must be logged in
        Given The user is logged in
        And The '/library/activities/activity-instances' page is opened
        
    Scenario: [Feature flag] User must be able to turn on wizard stepper for activity instance creation
        When The '/administration/featureflags' page is opened
        Then Activity instance wizard feature flag is turned off

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Activities Instances page
        Given The '/library' page is opened
        When The 'Activities' submenu is clicked in the 'Concepts' section
        And The 'Activity Instances' tab is selected
        Then The current URL is '/library/activities/activity-instances'

    Scenario: [Table][Options] User must be able to see table with correct options
        Then A table is visible with following options
            | options                                                         |
            | Add activity instance                                           |
            | Select filters                                                  |
            | Select columns                                                  |
            | Export                                                          |
            | Show version history                                            |
            | Select rows                                                     |
            | Search                                                          |

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the columns list on the main page as below
        And A table is visible with following headers
            | headers                       |
            | Library                       |
            | Activity instance class       |
            | Activity                      |
            | Activity Instance             |
            | NCI Concept ID                |
            | NCI Concept Name              |
            | Research Lab                  |
            | Molecular Weight              |
            | Topic code                    |
            | ADaM parameter code           |
            | Required for activity         |
            | Default selected for activity |
            | Data sharing                  |
            | Legacy usage                  |
            | Modified                      |
            | Modified by                   |
            | Status                        |
            | Version                       |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    @smoke_test
    Scenario: [Create][Positive case] User must be able to add a new Activity Instance
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And The Activity instance mandatory data is filled in
        And The Activity instance optional data is filled in
        And User intercepts create instance request
        And Form save button is clicked
        Then The pop up displays 'Activity created'
        And User waits for activity instance to be created
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        And The newly added Activity Instance item is added in the table by default
        And The item has status 'Draft' and version '0.1'

    Scenario: [Create][Mandatory fields] User must not be able to continue Step 1 of new activity instance without mandatory fields of 'Activity' selection
        When The Add Activity Instance button is clicked
        And Form continue button is clicked
        Then The user is not able to continue
        And The validation message appears for Activity field
        When The Activity instance activity is selected
        And Form continue button is clicked
        Then The user is not able to continue
        And The pop up displays 'You need to choose at least one Activity Grouping'

    Scenario: [Create][Mandatory fields] User must not be able to continue Step 2 of new activity Instance without mandatory fields of 'Activity instance class'
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And Form continue button is clicked
        Then The user is not able to continue
        And The validation message appears for class field

    Scenario: [Create][Mandatory fields] User must not be able to save the fom of new activity instance without mandatory fields of 'Activity instance name', 'Sentence case name', 'Definition' and 'Topic code'
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And Form save button is clicked
        Then The validation message appears for activity instance name field
        And The validation message appears for definition field
        And The validation message appears for topic code field
        And The form is not closed

    Scenario: [Create][Sentence case name validation] System must default value for 'Sentence case name' to lower case value of 'Activity instance name'
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And The user enters a value for Activity instance name
        Then The field for Sentence case name will be defaulted to the lower case value of the Activity instance name

    Scenario: [Create][Sentence case name validation] System must ensure value of 'Sentence case name' independent of case is identical to the value of 'Activity instance name'
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And The user define a value for Sentence case name and it is not identical to the value of Activity instance name
        And Form save button is clicked
        Then The user is not able to save
        And The validation message appears for sentance case name that it is not identical to name

    Scenario: [Actions][Approve] User must be able to Approve the drafted version of the Activity Instance
        And [API] Activity Instance in status Draft exists
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][Inactivate] User must be able to inactivate the approved version of the Activity Instance
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate the inactivated version of the Activity Instance
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '1.0'

    Scenario: [Actions][New version] User must be able to add a new version for the approved Activity Instance
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'

    Scenario: [Actions][Delete] User must be able to Delete the intial created version of the activity Instance
        And [API] Activity Instance in status Draft exists
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Delete' option is clicked from the three dot menu list
        Then Activity Instance is searched for and not found
        
    Scenario: [Actions][Edit][version 0.1] User must be able to edit the drafted version of the Activity Instance
        And [API] Activity Instance in status Draft exists
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        And User waits for 1 seconds
        When The 'Edit' option is clicked from the three dot menu list
        And User waits for edition form to open
        And Linked Activity group and subgroup are loaded
        And Form continue button is clicked
        And Form continue button is clicked
        Then The user updates instance name
        And User intercepts update instance request
        And Form save button is clicked
        Then The pop up displays 'Activity updated'
        And User waits for activity instance to be updated
        And The item has status 'Draft' and version '0.2'

    Scenario: [Actions][Edit][version 1.1] User must be able to edit and approve new version of Activity Instance
        And [API] Activity Instance is approved
        And [API] Activity Instance new version is created
        And The page is reloaded
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Edit' option is clicked from the three dot menu list
        And User waits for edition form to open
        And Linked Activity group and subgroup are loaded
        And Form continue button is clicked
        And Form continue button is clicked
        And The user updates instance name
        And User intercepts update instance request
        And Form save button is clicked
        Then The pop up displays 'Activity updated'
        And User waits for activity instance to be updated
        Then The item has status 'Draft' and version '1.2'
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '2.0'

    Scenario: [Create][Negative case][Draft activity] User must not be able to create activity instance linked to Draft activity
        And [API] Study Activity is created
        And Activity name created through API is found
        And The Add Activity Instance button is clicked
        And The Activity instance group data is filled in with activity created via API
        And Form continue button is clicked
        And The validation error for 'Draft' activity in not allowed state is displayed when 'creating' instance

    Scenario: [Create][Negative case][Retired activity] User must not be able to create activity instance linked to Retired activity
        And [API] Study Activity is created
        And [API] Activity is approved
        And [API] Activity is inactivated
        And Activity name created through API is found
        And The Add Activity Instance button is clicked
        And The Activity instance group data is filled in with activity created via API
        And Form continue button is clicked
        And The validation error for 'Retired' activity in not allowed state is displayed when 'creating' instance

    @BUG_ID:2770472
    Scenario: [Create][Negative case][Draft activity] User must not be able to edit activity instance when linked activity is in DRAFT state
        Given [API] Activity Instance in status Draft exists
        And [API] Activity new version is created
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Edit' option is clicked from the three dot menu list 
        Then The validation error for 'Draft' activity in not allowed state is displayed when 'editing' instance 

    Scenario: [Cancel][Creation] User must be able to Cancel creation of the activity instance
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And The Activity instance mandatory data is filled in
        When Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        When User sets status filter to 'all'
        And Activity Instance is searched for and not found

    Scenario: [Cancel][Edition] User must be able to Cancel edition of the activity instance
        And [API] Activity Instance in status Draft exists
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        When The 'Edit' option is clicked from the three dot menu list
        And User waits for edition form to open
        And User waits for 1 seconds
        And Form continue button is clicked
        And Form continue button is clicked
        When The user updates instance name
        And Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        When User sets status filter to 'all'
        And Activity Instance is searched for and not found

    Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the activity instance
        Given [API] Activity Instance in status Draft exists
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Draft item are displayed

    Scenario: [Actions][Availability][Final item] User must only have access to new version, inactivate, history actions for Final version of the activity instance
        And [API] Activity Instance is approved
        And Activity Instance is searched for and found
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Final item are displayed

    Scenario: [Actions][Availability][Retired item] User must only have access to reactivate, history actions for Retired version of the activity instance
        And [API] Activity Instance is inactivated
        When User sets status filter to 'all'
        And Activity Instance is searched for and found
        Then The item actions button is clicked
        Then Only actions that should be avaiable for the Retired item are displayed

    Scenario: [Create][Uniqueness check][Topic code] User must not be able to create two activities instances with the same topic codes
        And [API] Activity Instance in status Draft exists
        When The Add Activity Instance button is clicked
        And The Activity instance group data is filled in
        And Form continue button is clicked
        And The Activity instance class data is filled in
        And Form continue button is clicked
        And The Activity instance mandatory data is filled in
        And User intercepts create instance request
        And Form save button is clicked
        Then The user is not able to save

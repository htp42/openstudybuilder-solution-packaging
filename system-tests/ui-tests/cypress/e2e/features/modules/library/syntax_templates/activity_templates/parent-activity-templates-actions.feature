@REQ_ID:1070684
Feature: Library - Syntax Templates - Activity Instructions - Parent

    As a user, I want to manage every Activity template under the Syntax Template Library
    Background: User must be logged in
        Given The user is logged in

    Scenario: [Actions][Delete] User must be able to delete the Draft Activity Instruction template in version below 1.0
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Delete' option is clicked from the three dot menu list
        Then The parent activity is no longer available

    Scenario: [Actions][Approve] User must be able to approve the Draft Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Approve' option is clicked from the three dot menu list
        Then The pop up displays 'Activity template is now in Final state'
        And The item has status 'Final' and version '1.0'

    Scenario: [Actions][Edit indexing] User must be able to edit indexing of Final Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        And Group name created through API is found
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Edit indexing' option is clicked from the three dot menu list
        And The activity group data is loaded in the edit indexing form
        And The indication indexes edition is initiated
        And Form save button is clicked
        And The pop up displays 'Indexing properties updated'
        And The activity instruction is searched and found
        And The 'Edit indexing' option is clicked from the three dot menu list
        And The activity group data is loaded in the edit indexing form
        Then The indication index is updated

    Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Activity Instruction template without: Change description
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Edit' option is clicked from the three dot menu list
        And User goes to Change description step
        And The template change description is cleared
        And Form save button is clicked
        Then The validation appears for change description field
        And The form is not closed

    Scenario: [Actions][New version] User must be able to add a new version of the Final Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'New version' option is clicked from the three dot menu list
        Then The pop up displays 'New version created'
        And The item has status 'Draft' and version '1.1'

    Scenario: [Actions][Edit][1.1 version] User must be able to edit new version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'
        When The 'Edit' option is clicked from the three dot menu list
        And The activity template metadata update is started
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are cleared and filled in
        And Form continue button is clicked
        And Template change description is provided
        And Form save button is clicked
        And The activity instruction is searched and found
        Then The item has status 'Draft' and version '1.2'
        When The 'Approve' option is clicked from the three dot menu list
        Then The item has status 'Final' and version '2.0'

    Scenario: [Actions][Inactivate] User must be able to inactivate the Final Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Inactivate' option is clicked from the three dot menu list
        Then The pop up displays 'Activity template retired'
        And The item has status 'Retired' and version '1.0'

    Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        And [API] Activity Instruction is inactivated
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The pop up displays 'Activity template is now in Final state'
        And The item has status 'Final' and version '1.0'

    @manual_test
    Scenario: User must be able to view the history for the Parent Activity template with a status as 'Retired'
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        And [API] Activity Instruction is inactivated
        Then User intercepts activity templates request
        And The 'library/activity_instruction_templates/parent' page is opened
        And User waits for activity templates request
        And The activity instruction is searched and found
        When The 'Reactivate' option is clicked from the three dot menu list
        Then The 'History for template' window is displayed with the following column list with values
            | Column | Header                 |
            | 1      | Indication or disorder |
            | 2      | Criterion category     |
            | 3      | Criterion sub-category |
            | 4      | Template               |
            | 5      | Guidance text          |
            | 6      | Status                 |
            | 7      | Version                |
            | 8      | Change type            |
            | 9      | User                   |
            | 10     | From                   |
            | 11     | To                     |

    @manual_test
    Scenario: User must be able to read change history of output
        Given The 'library/activity_instruction_templates/parent' page is opened
        When The user opens version history
        Then The user is presented with version history of the output containing timestamp and username

    @manual_test
    Scenario: User must be able to read change history of selected element
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The 'Show history' option is clicked from the three dot menu list
        When The user clicks on History for particular element
        Then The user is presented with history of changes for that element
        And The history contains timestamps and usernames

    Scenario: [Cancel][Creation] User must be able to Cancel creation of the Activity Instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity template edition form is filled with data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        When Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        And The parent activity is no longer available

    Scenario: [Cancel][Edition] User must be able to Cancel edition of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The 'Edit' option is clicked from the three dot menu list
        And The activity template edition form is filled with data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And Fullscreen wizard is closed by clicking cancel button
        And Action is confirmed by clicking continue
        Then The form is no longer available
        And The parent activity is no longer available

    Scenario: [Cancel][Indexing edtion] User must be able to Cancel indexes edition of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The 'Edit indexing' option is clicked from the three dot menu list
        When The indication indexes edition is initiated
        And Modal window form is closed by clicking cancel button
        Then The form is no longer available
        When The 'Edit indexing' option is clicked from the three dot menu list
        And The indexes are not updated

    Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The item actions button is clicked
        Then Only actions that should be avaiable for the Draft item are displayed

    Scenario: [Actions][Availability][Final item] User must only have access to new version, inactivate, history actions for Final version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The item actions button is clicked
        Then Only actions that should be avaiable for the Final item are displayed

    Scenario: [Actions][Availability][Final item] User must have access to edit indexing, create pre-instantiation actions for Final version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The item actions button is clicked
        Then 'Edit indexing' action is available
        And 'Create pre-instantiation' action is available

    Scenario: [Actions][Availability][Retired item]User must only have access to reactivate, history actions for Retired version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And [API] Activity Instruction is approved
        And [API] Activity Instruction is inactivated
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        And The item actions button is clicked
        Then Only actions that should be avaiable for the Retired item are displayed
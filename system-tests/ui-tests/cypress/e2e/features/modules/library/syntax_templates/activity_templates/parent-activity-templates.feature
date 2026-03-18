@REQ_ID:1070684
Feature: Library - Syntax Templates - Activity Instructions - Parent

    As a user, I want to manage every Activity template under the Syntax Template Library
    Background: User must be logged in
        Given The user is logged in

    @smoke_test
    Scenario: [Navigation] User must be able to navigate to the Activty Instruction template under the Syntax template Library
        Given The '/library' page is opened
        When The 'Activity Instructions' submenu is clicked in the 'Syntax Templates' section
        Then The current URL is '/library/activity_instruction_templates/parent'

    @smoke_test
    Scenario: [Table][Columns][Names] User must be able to see the table with correct columns
        Given The '/library/activity_instruction_templates/parent' page is opened
        And A table is visible with following headers
            | headers         |
            | Sequence number |
            | Activity        |
            | Parent template |
            | Modified        |
            | Status          |
            | Version         |

    Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
        Given The '/library/activity_instruction_templates/parent' page is opened
        When The first column is selected from Select Columns option for table with actions
        Then The table contain only selected column and actions column

    Scenario: [Create][Sequence number] System must generate sequence number for Activity Instruction Templates when they are created
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And The '/library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The latest sequence number is saved
        And [API] Activity Instruction in status Draft exists
        And The activity instruction is searched and found
        Then Sequence number is incremented

    @pending_implementation
    Scenario: Template Instantiations must be update when parent template has been updated
        Given The test Activity Parent Template exists with a status as 'Draft'
        When The'Approve' option is clicked from the three dot menu list
        Then all related activity template instantiations must be cascade updated to new version and approved
        And the displayed pop-up snack must include information on number of updated activity template instantiations

    @smoke_test
    Scenario: [Create][Positive case] User must be able to create Activity Instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And User intercepts activity templates request
        And Form save button is clicked
        And User waits for activity templates request
        And The activity instruction is searched and found
        Then The Activity Instruction template is visible in the table
        And The item has status 'Draft' and version '0.1'

    Scenario: [Create][N/A indexes] User must be able to create Activity Instruction template with NA indexes
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        When All Not Applicable checkboxes are checked
        And The mandatory indexes are filled
        And User intercepts activity templates request
        And Form save button is clicked
        And User waits for activity templates request
        And The activity instruction is searched and found
        Then The Activity Instruction template is visible in the table
        And The item has status 'Draft' and version '0.1'

    Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Activity Instruction template
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And The 'library/activity_instruction_templates/parent' page is opened
        And The activity instruction is searched and found
        When The 'Edit' option is clicked from the three dot menu list
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And Form continue button is clicked
        And Template change description is provided
        And User intercepts activity templates request
        And Form save button is clicked
        And User waits for activity templates request
        And The activity instruction is searched and found
        Then The Activity Instruction template is visible in the table
        And The item has status 'Draft' and version '0.2'

    Scenario: [Create][Mandatory fields] User must not be able to create Activity Instruction template without: Template Text
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        When Form continue button is clicked
        Then The validation appears for Template name
        And The form is not closed

    Scenario: [Create][Uniqueness check][Name] User must not be able to create Activity Instruction template with not unique Template Text
        Given [API] Activity in status Final with Final group and subgroub exists
        And [API] Activity Instruction in status Draft exists
        And The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with already existing name
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And Form save button is clicked
        Then The pop up displays 'already exists'
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Activity Instruction template without: Indication or Disorder
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        When Indication or Disorder index is cleared
        And Form save button is clicked
        Then The validation appears for Indication or Disorder field
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Activity Instruction template without: Activity Group
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And The Activity Group index is cleared
        And Form save button is clicked
        Then The validation appears for activity template group field
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Activity Instruction template without: Activity SubGroup
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And The Activity Subgroup index is cleared
        And Form save button is clicked
        Then The validation appears for activity template subgroup field
        And The form is not closed

    Scenario: [Create][Mandatory fields] User must not be able to create Activity Instruction template without: Activity
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        And The activity instruction template form is filled with base data
        And Form continue button is clicked
        And Form continue button is clicked
        And All activity instruction indexes are filled in
        And The Activity index is cleared
        And Form save button is clicked
        Then The validation appears for Activity field
        And The form is not closed

    Scenario: [Create][Syntax validation] User must be able to verify syntax when creating Activity Instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And The syntax is verified
        Then The pop up displays "This syntax is valid"

    Scenario: [Create][Hide parameters] User must be able to hide parameter of the Activity Instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And Form continue button is clicked
        And The user hides the parameter in the next step
        Then The parameter is not visible in the text representation

    Scenario: [Create][Select parameters] User must be able to select parameter of the Activity Instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        And The Add template button is clicked
        When The new template name is prepared with a parameters
        And Form continue button is clicked
        And The user picks the parameter from the dropdown list
        Then The parameter value is visible in the text representation

    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search created Activity Instruction template
       Given [API] Activity in status Final with Final group and subgroub exists
        When [API] Search Test - Create first activity instruction template
        And [API] Search Test - Create second activity instruction template
        Given The 'library/activity_instruction_templates/parent' page is opened
        Then The activity instruction is searched and found
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario: [Table][Search][Negative case] User must be able to search not existing Activity Instruction template and table will correctly filtered
        Given The 'library/activity_instruction_templates/parent' page is opened
        When The not existing item is searched for
        Then The item is not found and table is correctly filtered

    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
        Given The 'library/activity_instruction_templates/parent' page is opened
        When The existing item in search by lowercased name
        And More than one result is found

    Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
        Given The 'library/activity_instruction_templates/parent' page is opened
        When The user adds status to filters
        And The user changes status filter value to 'Final'
        And The existing item is searched for by partial name
        And The item is not found and table is correctly filtered
        And The user changes status filter value to 'Draft'
        And The existing item is searched for by partial name
        Then More than one result is found

    Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
        Given The 'library/activity_instruction_templates/parent' page is opened
        When The user filters field '<name>'
        Then The table is filtered correctly

        Examples:
            | name                   |
            | Indication or disorder |
            | Activity group         |
            | Activity subgroup     |

        Scenario: [Table][Pagination] User must be able to use table pagination        
        Given The '/library/activity_instruction_templates/parent' page is opened
        When The user switches pages of the table
        Then The table page presents correct data
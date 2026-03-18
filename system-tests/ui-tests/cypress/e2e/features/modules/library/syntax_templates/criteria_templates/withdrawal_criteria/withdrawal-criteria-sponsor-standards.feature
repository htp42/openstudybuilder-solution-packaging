@REQ_ID:1070684
Feature: Library - Syntax Templates - Criteria - Withdrawal - Parent

  As a user, I want to manage every Withdrawal Criteria template under the Syntax template Library
  Background: User must be logged in
    Given The user is logged in

  @smoke_test
  Scenario: [Navigation] User must be able to navigate to the Withdrawal Criteria template under the Syntax template Library
    Given The '/library' page is opened
    When The 'Criteria' submenu is clicked in the 'Syntax Templates' section
    And The 'Withdrawal' tab is selected
    Then The current URL is 'library/criteria_templates/Withdrawal/parent'

  @smoke_test
  Scenario: [Table][Columns][Names] User must be able to see the table with correct columns
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    Then A table is visible with following headers
      | headers         |
      | Sequence number |
      | Parent template |
      | Guidance text   |
      | Modified        |
      | Status          |
      | Version         |

  Scenario: [Table][Columns][Visibility] User must be able to select visibility of columns in the table 
    Given The '/library/criteria_templates/Withdrawal/parent' page is opened
    When The first column is selected from Select Columns option for table with actions
    Then The table contain only selected column and actions column

  Scenario: [Create][Sequence number] System must generate sequence number for Withdrawal Criteria Templates when they are created
    Given [API] 'Withdrawal' Criteria in status Draft exists
    And The 'library/criteria_templates/Withdrawal/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The latest sequence number is saved
    And [API] 'Withdrawal' Criteria in status Draft exists
    And The criteria is found
    Then Sequence number is incremented

  @smoke_test
  Scenario: [Create][Positive case] User must be able to create Withdrawal Criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When The criteria template form is filled with base data
    And Form continue button is clicked
    And Form continue button is clicked
    And Template indexes are set for 'criterion'
    And User intercept getCriteria request
    And Form save button is clicked
    And User awaits for the getCriteria request to finish
    And The criteria is found
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.1'

  Scenario: [Create][N/A indexes] User must be able to create Withdrawal Criteria template with NA indexes
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When The criteria template form is filled with base data
    And Form continue button is clicked
    And Form continue button is clicked
    And All Not Applicable checkboxes are checked
    And User intercept getCriteria request
    And Form save button is clicked
    And User awaits for the getCriteria request to finish
    And The criteria is found
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.1'

  Scenario: [Create][Mandatory fields] User must not be able to create Withdrawal Criteria template without: Template Text
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When Form continue button is clicked
    Then The validation appears for Template name
    And The form is not closed

  Scenario: [Create][Mandatory fields] User must not be able to create Withdrawal Criteria template without: Indication or Disorder
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    And The criteria template form is filled with base data
    And Form continue button is clicked
    And Form continue button is clicked
    When Template indexes are set for 'criterion'
    And Indication or Disorder index is cleared
    Then Form save button is clicked
    And The validation appears for Indication or Disorder field
    And The form is not closed

  Scenario: [Create][Mandatory fields] User must not be able to create Withdrawal Criteria template without: Criterion Category
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    And The criteria template form is filled with base data
    And Form continue button is clicked
    And Form continue button is clicked
    When Template indexes are set for 'criterion'
    And Category index is cleared for 'criterion' template
    Then Form save button is clicked
    And The validation appears for 'criterion' template category field
    And The form is not closed

  Scenario: [Create][Mandatory fields] User must not be able to create Withdrawal Criteria template without: Criterion Sub-Category
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    And The criteria template form is filled with base data
    And Form continue button is clicked
    And Form continue button is clicked
    When Template indexes are set for 'criterion'
    And Subcategory index is cleared for 'criterion' template
    Then Form save button is clicked
    And The validation appears for 'criterion' template subcategory field
    And The form is not closed

  Scenario: [Create][Syntax validation] User must be able to verify syntax when creating Withdrawal Criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When The new template name is prepared with a parameters
    And The syntax is verified
    Then The pop up displays "This syntax is valid"

  Scenario: [Create][Hide parameters] User must be able to hide parameter of the Withdrawal Criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When The new template name is prepared with a parameters
    And Form continue button is clicked
    And The user hides the parameter in the next step
    Then The parameter is not visible in the text representation

  Scenario: [Create][Select parameter] User must be able to select parameter of the Withdrawal Criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    When The new template name is prepared with a parameters
    And Form continue button is clicked
    And The user picks the parameter from the dropdown list
    Then The parameter value is visible in the text representation

  @manual_test
  Scenario: User must be able to view the history for the Withdrawal Criteria template with a status as 'Retired'
    Given [API] 'Withdrawal' Criteria in status Draft exists
    And [API] Criteria is approved
    And [API] Criteria is inactivated
    And The 'library/criteria_templates/Withdrawal/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
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
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    When The user opens version history
    Then The user is presented with version history of the output containing timestamp and username

  @manual_test
  Scenario: User must be able to read change history of selected element
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The 'Show history' option is clicked from the three dot menu list
    When The user clicks on History for particular element
    Then The user is presented with history of changes for that element
    And The history contains timestamps and usernames

  Scenario: [Cancel][Creation] User must be able to Cancel creation of the Withdrawal Criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And The Add template button is clicked
    And The criteria template edition form is filled with data
    And Form continue button is clicked
    And Form continue button is clicked
    And All Not Applicable checkboxes are checked
    When Fullscreen wizard is closed by clicking cancel button
    And Action is confirmed by clicking continue
    Then The form is no longer available
    And The criteria is not found

  Scenario: [Cancel][Edition] User must be able to Cancel edition of the Withdrawal Criteria template
    Given [API] 'Withdrawal' Criteria in status Draft exists
    And The 'library/criteria_templates/Withdrawal/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Edit' option is clicked from the three dot menu list
    And The criteria template edition form is filled with data
    And Form continue button is clicked
    And Form continue button is clicked
    And All Not Applicable checkboxes are checked
    And Fullscreen wizard is closed by clicking cancel button
    And Action is confirmed by clicking continue
    Then The form is no longer available
    And The criteria is not found

  Scenario: [Cancel][Indexing edtion] User must be able to Cancel indexes edition of the Withdrawal Criteria template
    Given [API] 'Withdrawal' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Withdrawal/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Edit indexing' option is clicked from the three dot menu list
    When The indication indexes edition is initiated
    And Modal window form is closed by clicking cancel button
    Then The form is no longer available
    When The 'Edit indexing' option is clicked from the three dot menu list
    And The indexes are not updated

  @smoke_test
  Scenario: [Table][Search][Postive case] User must be able to search created Withdrawal Criteria template
    When [API] Search Test - Create first 'Withdrawal' criteria template
    And [API] Search Test - Create second 'Withdrawal' criteria template
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    And The existing item is searched for by partial name
    Then More than one result is found

  Scenario: [Table][Search][Negative case] User must be able to search not existing Withdrawal Criteria and table will correctly filtered
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    When The not existing item is searched for
    Then The item is not found and table is correctly filtered

  Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    When The existing item in search by lowercased name
    And More than one result is found

  Scenario: [Table][Search][Filtering] User must be able to combine search and filters to narrow table results
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    When The user adds status to filters
    And The user changes status filter value to 'Final'
    And The existing item is searched for by partial name
    And The item is not found and table is correctly filtered
    And The user changes status filter value to 'Draft'
    And The existing item is searched for by partial name
    Then More than one result is found

  Scenario Outline: [Table][Filtering] User must be able to filter the table by text fields
    Given The 'library/criteria_templates/Withdrawal/parent' page is opened
    When The user filters field '<name>'
    Then The table is filtered correctly

    Examples:
      | name                   |
      | Indication or disorder |
      | Criterion category     |
      | Criterion sub-category |

  Scenario: [Table][Pagination] User must be able to use table pagination        
      Given The 'library/criteria_templates/Withdrawal/parent' page is opened
      When The user switches pages of the table
      Then The table page presents correct data
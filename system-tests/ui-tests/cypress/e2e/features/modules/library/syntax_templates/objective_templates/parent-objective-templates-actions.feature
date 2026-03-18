@REQ_ID:1070684
Feature: Library - Syntax Templates - Objectives - Parent

  As a user, I want to manage every Objective template under the Syntax Template Library
  Background: User must be logged in
    Given The user is logged in

  Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And The objective template is found
    When The 'Edit' option is clicked from the three dot menu list
    And The objective metadata update is started
    And Form continue button is clicked
    And Form continue button is clicked
    And Objective criteria specific indexes are updated
    And Form continue button is clicked
    And Template change description is provided
    And Form save button is clicked
    And The objective template is found
    Then The item has status 'Draft' and version '0.2'
    And The 'Edit' option is clicked from the three dot menu list
    And The objective template name is checked
    And User goes to Index template step
    And Objective indexes are verified

  Scenario: [Actions][Delete] User must be able to delete the Draft Objective template in version below 1.0
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And The objective template is found
    When The 'Delete' option is clicked from the three dot menu list
    Then The pop up displays "Template deleted"
    And The objective template is not found

  Scenario: [Actions][Approve] User must be able to approve the Draft Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And The objective template is found
    When The 'Approve' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Edit indexting] User must be able to edit indexing of Final Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The 'Edit indexing' option is clicked from the three dot menu list
    And Objective criteria specific indexes are cleared and updated
    And Form save button is clicked
    And The objective template is found
    And The 'Edit indexing' option is clicked from the three dot menu list
    And Objective indexes are verified

  Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Objective template without: Change description
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And The objective template is found
    When The 'Edit' option is clicked from the three dot menu list
    And User goes to Change description step
    And The template change description is cleared
    And Form save button is clicked
    Then The validation appears for change description field
    And The form is not closed

  Scenario: [Actions][New version] User must be able to add a new version of the Final Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The 'New version' option is clicked from the three dot menu list
    Then The pop up displays 'New version created'
    And The item has status 'Draft' and version '1.1'

  Scenario: [Actions][Edit][1.1 version] User must be able to edit new version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The 'New version' option is clicked from the three dot menu list
    Then The item has status 'Draft' and version '1.1'
    When The 'Edit' option is clicked from the three dot menu list
    And The objective metadata update is started
    And Form continue button is clicked
    And Form continue button is clicked
    And Objective criteria specific indexes are updated
    And Form continue button is clicked
    And Template change description is provided
    And Form save button is clicked
    And The objective template is found
    Then The item has status 'Draft' and version '1.2'
    When The 'Approve' option is clicked from the three dot menu list
    Then The item has status 'Final' and version '2.0'

  Scenario: [Actions][Inactivate] User must be able to inactivate the Final Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The 'Inactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template inactivated'
    And The item has status 'Retired' and version '1.0'

  Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And [API] Objective template is inactivated
    And The objective template is found
    When The 'Reactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And The objective template is found
    When The item actions button is clicked
    Then Only actions that should be avaiable for the Draft item are displayed

  Scenario: [Actions][Availability][Final item] User must only have access to new version, inactivate, history actions for Final version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The item actions button is clicked
    Then Only actions that should be avaiable for the Final item are displayed

  Scenario: [Actions][Availability][Final item] User must have access to edit indexing, create pre-instantiation actions for Final version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And The objective template is found
    When The item actions button is clicked
    Then 'Edit indexing' action is available
    And 'Create pre-instantiation' action is available

  Scenario: [Actions][Availability][Retired item]User must only have access to reactivate, history actions for Retired version of the Objective template
    Given The 'library/objective_templates' page is opened
    And [API] Create objective template
    And [API] Approve objective template
    And [API] Objective template is inactivated
    And The objective template is found
    And The item actions button is clicked
    Then Only actions that should be avaiable for the Retired item are displayed
    
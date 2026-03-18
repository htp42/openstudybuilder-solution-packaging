@REQ_ID:1070684
Feature: Library - Syntax Templates - Criteria - Randomisation - Parent

  As a user, I want to manage every Randomisation Criteria template under the Syntax template Library
  Background: User must be logged in
    Given The user is logged in

  Scenario: [Actions][Edit][0.1 version] User must be able to edit initial version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Edit' option is clicked from the three dot menu list
    And The criteria metadata update is initiated
    And Form continue button is clicked
    And Form continue button is clicked
    And Template indexes are cleared and updated for 'criterion'
    And Form continue button is clicked
    And Template change description is provided
    And User intercept getCriteria request
    And Form save button is clicked
    And User awaits for the getCriteria request to finish
    And The criteria is found
    Then The Criteria is visible in the Criteria Templates Table
    And The item has status 'Draft' and version '0.2'

  Scenario: [Actions][Delete] User must be able to delete the Draft Randomisation Criteria template in version below 1.0
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Delete' option is clicked from the three dot menu list
    Then The pop up displays "Template deleted"
    And The criteria is not found

  Scenario: [Actions][Approve] User must be able to approve the Draft Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Approve' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Edit indexing] User must be able to edit indexing of Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Edit indexing' option is clicked from the three dot menu list
    And Template indexes are cleared and updated for 'criterion'
    And Form save button is clicked
    And The criteria is found
    And The 'Edit indexing' option is clicked from the three dot menu list
    Then Template indexes are verified

  Scenario: [Actions][Edit][Mandatory fields] User must not be able to save changes to Randomisation Criteria template without: Change description
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Edit' option is clicked from the three dot menu list
    And User goes to Change description step
    And The template change description is cleared
    And Form save button is clicked
    Then The validation appears for change description field
    And The form is not closed

  Scenario: [Actions][New version] User must be able to add a new version of the Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'New version' option is clicked from the three dot menu list
    Then The pop up displays 'New version created'
    And The item has status 'Draft' and version '1.1'

  Scenario: [Actions][Edit][1.1 version] User must be able to edit new version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'New version' option is clicked from the three dot menu list
    Then The item has status 'Draft' and version '1.1'
    When The 'Edit' option is clicked from the three dot menu list
    And The criteria metadata update is initiated
    And Form continue button is clicked
    And Form continue button is clicked
    And Template indexes are cleared and updated for 'criterion'
    And Form continue button is clicked
    And Template change description is provided
    And User intercept getCriteria request
    And Form save button is clicked
    And The criteria is found
    Then The item has status 'Draft' and version '1.2'
    When The 'Approve' option is clicked from the three dot menu list
    Then The item has status 'Final' and version '2.0'

  Scenario: [Actions][Inactivate] User must be able to inactivate the Final Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Inactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template inactivated'
    And The item has status 'Retired' and version '1.0'

  Scenario: [Actions][Reactivate] User must be able to reactivate the Retired Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And [API] Criteria is inactivated
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The 'Reactivate' option is clicked from the three dot menu list
    Then The pop up displays 'Template is now in Final state'
    And The item has status 'Final' and version '1.0'

  Scenario: [Actions][Availability][Draft item] User must only have access to aprove, edit, delete, history actions for Drafted version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The item actions button is clicked
    Then Only actions that should be avaiable for the Draft item are displayed

  Scenario: [Actions][Availability][Final item] User must only have access to new version, inactivate, history actions for Final version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The item actions button is clicked
    Then Only actions that should be avaiable for the Final item are displayed

  Scenario: [Actions][Availability][Final item] User must have access to edit indexing, create pre-instantiation actions for Final version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    When The item actions button is clicked
    Then 'Edit indexing' action is available
    And 'Create pre-instantiation' action is available

  Scenario: [Actions][Availability][Retired item]User must only have access to reactivate, history actions for Retired version of the Randomisation Criteria template
    Given [API] 'Randomisation' Criteria in status Draft exists
    And [API] Criteria is approved
    And [API] Criteria is inactivated
    And The 'library/criteria_templates/Randomisation/parent' page is opened
    And User intercept getCriteria request
    And User awaits for the getCriteria request to finish
    And The criteria is found
    And The item actions button is clicked
    Then Only actions that should be avaiable for the Retired item are displayed

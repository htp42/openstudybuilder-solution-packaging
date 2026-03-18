@REQ_ID:1070683
Feature: Library - Data Collection Standards - CRF Builder - CRF Viewer

  As a user, I want to view CRFs from the data collections standards library as blank CRFs or with various annotations,
  So I can efficiently manage and maintain CRFs within the StudyBuilder Library.

  Background: User must be logged in
    Given The user is logged in

  Scenario: [Navigation] User must be able to navigate to CRF View page
    Given The '/library' page is opened
    When The 'CRF Builder' submenu is clicked in the 'Data Collection Standards' section
    And The 'CRF Viewer' tab is selected
    Then The current URL is '/library/crf-builder/odm-viewer'
 
   Scenario: Verify the HTML option in the Stylesheet dropdown works as expected
    Given The '/library/crf-builder/odm-viewer' page is opened
    When I select a value from the Form Name dropdown
    And I select HTML option from the Stylesheet dropdown list
    And keep all other fields as default
    And I click the GENERATE button
    Then The imported CRF view page should be displayed

  Scenario: Verifying that the Falcon downloadable option in the Stylesheet dropdown works as expected
    Given The '/library/crf-builder/odm-viewer' page is opened
    When I select a value from the Form Name dropdown
    And I select Downloadable Falcon in the Stylesheet dropdown list
    And keep all other fields as default
    And I click the GENERATE button
    Then The imported CRF view page should be displayed

@manual_test
  Scenario: Verify all highlighted text options/buttons in the CRF Viewer display page can be clicked and become un-highlighted
    Given The '/library/crf-builder/odm-viewer' page is opened
    When I select a value from the Form Name dropdown
    And keep all other fields as default
    And I click the GENERATE button
    Then The imported CRF view page should be displayed
    And all text options/buttons like 'Implementation Guidelines', 'Completion Guidelines', 'CDASH', 'SDTM', 'Topic Code', 'ADaM Code', and 'Keys' are highlighted
    When I click each text option/button one by one
    Then Each clicked text option/button should become un-highlighted
  
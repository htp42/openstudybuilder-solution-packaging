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

  @manual_test
  Scenario: Verify all highlighted text options/buttons in the CRF Viewer display page can be clicked and become un-highlighted
    Given The '/library/crf-builder/odm-viewer' page is opened
    When I select a value from the ODM Element Name dropdown
    And keep all other fields as default
    And I click the LOAD button
    Then The imported CRF view page should be displayed
    And all text options/buttons like 'Implementation Guidelines', 'Completion Guidelines', 'CDASH', 'SDTM', 'Topic Code', 'ADaM Code', and 'Keys' are highlighted
    When I click each text option/button one by one
    Then Each clicked text option/button should become un-highlighted
  
  @manual_test
  Scenario: Verifying that the Falcon downloadable option in the Stylesheet dropdown works as expected
    Given The '/library/crfbuilder/odm-viewer' page is opened
    And I select a value from the ODM Element Name dropdown
    And keep all other fields as default
    And I verify that there are two options in the Stylesheet dropdown list: 'CRF with Annotations' and 'Downloadable Falcon (Word)'
    And I click the 'Load' button
    And The imported CRF view page should be displayed
    And I select 'Downloadable Falcon (Word)' from the Stylesheet dropdown list
    And I click the LOAD button
    Then The imported CRF view page should be displayed
    When I click the 'Export data in HTML format' option
    Then The file should be downloaded successfully to the local machine
    When I open the downloaded file in Word format
    And I compare the downloaded file with the CRF view page
    Then The content and the format in both places should look exactly the same
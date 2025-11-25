@REQ_ID:1070683
Feature: Library - Data Collection Standards - CRF Viewer

  As a user, I want to view CRFs from the data collections standards library as blank CRFs or with various annotations,
  So I can efficiently use CRFs within the StudyBuilder Library.

  Background: User must be logged in
    Given The user is logged in

  Scenario: [Navigation] User must be able to navigate to CRF View page
    Given The '/library' page is opened
    When The 'CRF Viewer' submenu is clicked in the 'Data Collection Standards' section
    Then The current URL is '/library/crf-viewer/odm-viewer'
  
  @manual_test
  Scenario: Verifying Falcon downloadable option in the Stylesheet dropdown works as expected in the CRF Viewer menu
    Given The '/library/crfviewer/odm-viewer' page is opened
    When I select one or more values from the CRF collection dropdown
    And I select one or more values from the CRF Forms dropdown
    And I verify that there are two options in the Stylesheet dropdown list: 'CRF with annotations' and 'Downloadable Falcon (Word)'
    And I select 'Downloadable Falcon (Word)' in the Stylesheet dropdown list
    And I click the LOAD button
    Then The imported CRF view page should be displayed
    When I click the 'Export data in HTML format' option
    Then The file should be downloaded successfully on the local machine
    When I open the downloaded file in Word format
    And Compare the downloaded file with the CRF view page
    Then The content and the format in both places should look exactly the same

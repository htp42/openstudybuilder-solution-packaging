@REQ_ID:1070683

Feature: Library - Concepts - Activities - Activity Group Overview Page
    As a user, I want to verify that the Activity Group Overview Page in the Concepts Library, can display correctly.

    Background: 
        Given The user is logged in
        When [API] Activity Instance in status Final with Final group, subgroup and activity linked exists
        And Group, subgroup, activity and instance names created through API are found
        And Overview page for group created via API is opened
        And Group overview page is opened

    Scenario: [Navigation][Group] User must be able to navigate to activity group overview page by clicking its name in the group table
        Given The '/library/activities/activity-groups' page is opened
        When Group created via API is searched for and found
        When User goes to group overview page by clicking its name
        Then Group overview page is opened

    Scenario: [Navigation][Subgroup] User must be able to navigate to activity group overview page by clicking its name in the group overview page
        When The subgroup overview page can be opened by clicking the subgroup link in overview page
        Then Subgroup overview page is opened

    Scenario: [COSMoS YAML] Verify that the group overview page displays all sections correctly
        When I click on the COSMoS YAML tab
        Then The COSMoS YAML page should be opened with Download button and Close button displayed
        When The Download YAML content button is clicked
        Then The 'COSMoS-overview' file without timestamp is downloaded in 'yml' format
        # And the COSMoS YAML file should be saved with correct content (this step should be tested manually)
        When I click on the Close button in the COSMoS YAML page
        Then Group overview page is opened   

    Scenario: [Sections] Verify that the activity group overview page displays correctly
        And The 'Activity subgroups' table is displaying correct columns
        |  header     |
        |  Name       |
        |  Definition |
        |  Version    |
        |  Status     |
        And The linked subgroup is found in the Groups table with status 'Final' and version '1.0'
        And The free text search field should be displayed in the 'Activity subgroups' table

    Scenario: [History] Verify that the activity group overview page displays correctly
        When I click on the history button
        Then The history page is opened
    
    Scenario: [Linking] Verify that the activities group overview page can link to the correct subgroup
        When Version '0.1' is selected from the Version dropdown list
        And The status displayed on the summary has value 'Draft' and version is '0.1'
        And The Start date value is saved
        Then The correct End date should be displayed
        And The Activity subgroups table is empty
        When Version '1.0' is selected from the Version dropdown list
        And The status displayed on the summary has value 'Final' and version is '1.0'
        Then The linked subgroup is found in the Groups table with status 'Final' and version '1.0'

    Scenario: [Edit][1.1] Edit the Group
        When I click 'New version' button
        Then The status displayed on the summary has value 'Draft' and version is '1.1'
        And The linked subgroup is found in the Groups table with status 'Final' and version '1.0'
        When I click 'Edit' button 
        And Group name is changed
        And Form save button is clicked
        Then The status displayed on the summary has value 'Draft' and version is '1.2'
        And The Activity subgroups table is empty

    Scenario: [Approve] Approve the Group
        When I click 'Approve' button
        Then The status displayed on the summary has value 'Final' and version is '2.0'
        And The Activity subgroups table is empty

    Scenario: [Edit][2.1] Edit the Group
        When I click 'New version' button
        And The status displayed on the summary has value 'Draft' and version is '2.1'
        When I click 'Edit' button 
        And Group name is changed
        And Form save button is clicked
        And The status displayed on the summary has value 'Draft' and version is '2.2'
        When I click 'Approve' button
        And The status displayed on the summary has value 'Final' and version is '3.0'
        And The Activity subgroups table is empty
  
    Scenario: [Linking][New subgroup] Verify that the activities group overview page can link to the correct subgroup with different versions
        When The '/library/activities/activity-subgroups' page is opened
        And The Add activity subgroup button is clicked
        And I create a new subgroup and link it to the existing group
        And Form save button is clicked
        And Overview page for group created via API is opened
        And Group overview page is opened
        When Version '2.0' is selected from the Version dropdown list
        And The status displayed on the summary has value 'Final' and version is '3.0'
        Then The new linked subgroup is found in the Groups table with status 'Draft' and version '0.1'
        And The Activity subgroup created via API is not available in the table

    Scenario: [Table][Search][Negative case] User must be able to search not existing subgroup and table will be correctly filtered
        When User searches for non-existing item in 'Activity subgroups' table
        Then The Activity subgroups table is empty

    @smoke_test
    Scenario: [Table][Search][Postive case] User must be able to search subgroups connected to group
        When [API] A group connected to two subgroups is created
        And [API] Fetch names of group with two connected subgroups
        And Overview page for group created via API is opened
        And Group overview page is opened
        And User searches for subgroup in linked Subgroups table
        Then 1 result is present in the 'Activity subgroup' table
        And Subgroup name is present in first row of the Activity Subgroup table
        And User searches for subgroup by using partial name in linked Subgroups table
        Then 2 result is present in the 'Activity subgroup' table

    Scenario: [Table][Search][Case sensitivity] User must be able to search item ignoring case sensitivity in subroup table
        And User searches for subgroup by using lowecased name in linked Subgroups table
        Then 1 result is present in the 'Activity subgroup' table
        And Subgroup name is present in first row of the Activity Subgroup table

    Scenario: [Table][Filtering] User must have access to filters
        And Filters for the 'Activity subgroup' table are expanded
        Then Following filters are available in the table 'Activity subgroup'
        | filter by   |
        | Name        |
        | Definition  |
        | Version     |
        | Status      |

    Scenario: [Table][Filtering] User must be able to narrow down table result by using Name filter
        And User waits for linked 'Activity subgroup' table data to load
        And 2 result is present in the 'Activity subgroup' table
        And Filters for the 'Activity subgroup' table are expanded
        And Subgroup name is selected from filters
        Then 1 result is present in the 'Activity subgroup' table
        And Subgroup name is present in first row of the Activity Subgroup table

    Scenario: [Table][Filtering][Search] User must be able combine search and filters
        And User waits for linked 'Activity subgroup' table data to load
        And Filters for the 'Activity subgroup' table are expanded
        And Subgroup name is selected from filters
        When User searches for non-existing item in 'Activity subgroups' table
        Then The Activity subgroups table is empty
        And User searches for subgroup in linked Subgroups table
        Then 1 result is present in the 'Activity subgroup' table
        And Subgroup name is present in first row of the Activity Subgroup table

    @manual_test
    Scenario: Verify that the pagination works in the Activity subgroups table
        When I select 5 rows per page from dropdown list in the Activity subgroups table
        Then The Activity subgroups table should be displayed with 5 rows per page
        When I click on the next page button in the Activity subgroups table
        Then The Activity subgroups table should display the next page within 5 rows per page
         When I select 10 rows per page from dropdown list in the Activity subgroups table
        Then The Activity subgroups table should be displayed with 10 rows per page
        When I click on the next page button in the Activity subgroups table
        Then The Activity subgroups table should display the next page within 10 rows per page

    @manual_test
    Scenario: Verify that the export functionality work in the Activity subgroups table
        And The Export functionality works in the Activity subgroups table
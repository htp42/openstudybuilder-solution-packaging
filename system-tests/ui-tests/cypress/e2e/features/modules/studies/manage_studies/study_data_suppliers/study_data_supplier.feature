@REQ_ID:3459562
Feature: Study - Manage Study - Study Data Suppliers
    As a user, I want to manage the data suppliers in the Study
    Background:
        Given The user is logged in
        And A test study is selected

    @pending_implementation
    Scenario: [Navigation] User must be able to navigate to the List Study Data Supplier tab in the Study Data Suppliers page
        Given The '/studies' page is opened
        When The 'Study Data Suppliers' submenu is clicked in the 'Manage Study' section
        And The 'Overview' tab is selected
        Then The current URL is '/data-suppliers'

    @pending_implementation
    Scenario: [Table][Columns][Names] User must be able to see the Study Data Supplier Overview table with correct columns
        Given The '/studies' page is opened
        When The 'Study Data Suppliers' submenu is clicked in the 'Manage Study' section
        And The 'List Study Data Supplier' tab is selected
        And A table is visible with the following headers
            | headers            |
            | #                  |
            | Data supplier type |
            | Data supplier name |
            | Description        |
            | Library            |
            | Origin type        |
            | Origin Source      |
            | UI base URL        |
            | API base URL       |
            | Modified           |
            | Modified by        |

    @pending_implementation
    Scenario: [Add Existing][Positive case] User must be able to add existing data suppliers to the data supplier type
        Given The test study '/data-suppliers' page is opened
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        When I click on + button
        Then A new line of Supplier data type table including Data supplier dropdown menu is added
        And I can see REMOVE button beside the Data supplier dropdown menu
        And I can see + ADD USER DEFINED DATA SUPPLIER button under the Supplier data type table
        When I select the first value from the Data supplier dropdown menu
        Then The first value is selected and displayed in the Data supplier line
        When I click on + button
        Then A new line of Supplier data type table including Data supplier dropdown menu is added
        When I select the last value from the Data supplier dropdown menu
        Then The last value is selected and displayed in the Data supplier line
        When I click on the SAVE button
        Then The newly added data suppliers should be displayed in the corresponding Supplier data type table
        When I click on List Study Data Supplier tab
        Then The newly added data suppliers should be displayed in the table with correct data

    @pending_implementation
    Scenario: [Remove][Positive case] User must be able to remove the data supplier from data supplier type in study
        Given The test study '/data-suppliers' page is opened
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        When I click on REMOVE button beside the Data supplier dropdown menu
        Then The selected Data supplier value line is removed from the Supplier data type table
        When I click on the SAVE button
        Then The removed data suppliers should not exist in the corresponding Supplier data type table
        When I click on List Study Data Supplier tab
        Then The removed data suppliers should not exist in the table

    @pending_implementation
    Scenario: [Create New][Positive case] User must be able to create a new data supplier in Study
        Given The test study '/data-suppliers' page is opened
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        When I click on + button
        Then A new line of Supplier data type table including Data supplier dropdown menu is added
        When I click + ADD USER DEFINED DATA SUPPLIER button under the Supplier data type table
        Then The Add a new Data Supplier page is opened
        When I fill in the Name, Description field
        And I click on SAVE button
        Then It goes back to the Edit Study Data Supplier page
        When I click on the SAVE button
        Then The newly added data suppliers should be displayed under the corresponding Supplier data type table
        When I click on List Study Data Supplier tab
        Then The newly added data suppliers should be displayed in the table with correct data
        When The '/library/data-suppliers' page is opened
        Then The newly added data suppliers should be displayed in the Data Supplier Library table with correct data
        
    @pending_implementation
    Scenario: [Add Existing][Positive case] User must be able to add same existing data suppliers to the different data supplier type
        Given The test study '/data-suppliers' page is opened
        When The Edit button is clicked
        Then The Edit Study Data Supplier page is opened
        When I click on + button beside a supplier data type
        Then A new line of Supplier data type table including Data supplier dropdown menu is added
        When I select the first value from the Data supplier dropdown menu
        Then The first value is selected and displayed in the Data supplier line
        When I click on + button beside the next supplier data type
        Then A new line of Supplier data type table including Data supplier dropdown menu is added
        When I select the same value from the Data supplier dropdown menu
        Then The same value is selected and displayed in the Data supplier line
        When I click on the SAVE button
        Then The newly added same data supplier should be displayed in the two selected different Supplier data type tables
        When I click on List Study Data Supplier tab
        Then The newly added data suppliers should be displayed in the Data Supplier Library table with correct data
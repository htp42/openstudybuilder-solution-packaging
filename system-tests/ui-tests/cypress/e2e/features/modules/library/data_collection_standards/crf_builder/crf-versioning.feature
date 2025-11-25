@REQ_ID:1070683

Feature: Library - Data Collection Standards - CRF Versioning
    As a user, I want to manage versioning of CRFs, where a CRF is a hierarchy consisting of its Collections, Item Groups and Items in the CRF Library

    ########################################################################## CRF Versioning functionality Overview ############################################################################
    ##                                                                                                                                                                                         ##
    ## 1 Hierarchical Structure: CRF Collection → Forms → Item Groups → Items                                                                                                                  ##
    ## 2 Basic Business Rules:                                                                                                                                                                 ##           
    ##      2.1 Parent in Draft Status (Not locked) -> Parents always connect to the latest version of the child, updates in the child version automatically reflect on the parent connection. ##
    ##      2.2 Parent in Final Status (Locked) -> Parent connects to the old version of the child, updates in the child version do not affect the parent's connection.                        ##
    ## 3. Example Scenarios:                                                                                                                                                                   ##
    ##      3.1 Scenario:                                                                                                                                                                      ##
    ##          Given Parent in Draft status                                                                                                                                                   ##
    ##          When child is edited or a new version is created                                                                                                                               ##
    ##          Then Parent automatically connects to the latest version of the Child                                                                                                          ##
    ##      3.2 Scenario:                                                                                                                                                                      ##
    ##          Given Parent in Final status.                                                                                                                                                  ##
    ##          When child is edited or a new version is created                                                                                                                               ##
    ##          Then Parent still connected to the old version of the Child                                                                                                                    ##   
    ##      3.3 Scenario:                                                                                                                                                                      ##
    ##          Given Parent in Final status, still connected to the old version of the Child                                                                                                  ##
    ##          When Parent receives a new version, changing to Draft                                                                                                                          ##
    ##          Then Parent should automatically connect to the new version of the Child                                                                                                       ##
    ##                                                                                                                                                                                         ##
    ########################################################################## CRF Versioning functionality Overview ############################################################################

    Background: User must be logged in
        Given The user is logged in

    Scenario: Verify that the Edit of a Draft child element will impact the parent element in Draft status
        Given [API] A CRF Collection in status Draft exists linking a child Form, Item Group, and Item in Status Draft
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'Edit' option is clicked from the three dot menu list
        And I update the form and click on the Save button
        Then The item has status 'Draft' and version '0.2'
        When The '/library/crf-builder/item-groups' page is opened
        And I search for the existed item group
        When The 'Edit' option is clicked from the three dot menu list
        And I update the item group and click on the Save button
        And Form save button is clicked
        Then The item has status 'Draft' and version '0.2'
        When The '/library/crf-builder/items' page is opened
        And I search for the existed item
        When The 'Edit' option is clicked from the three dot menu list
        And I update the item and click on the Save button
        Then The item has status 'Draft' and version '0.2'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '0.2' and status 'Draft' of the linked child elements
        # Notification for editing action is under discussion
        # Then the 'Note, the following CRF Collections have references to this Form, Item Group, or Items, and if updates are saved this will apply to these CRF collections:' notification is presented to the user
        # And the list of affected CRF Collections are listed

    Scenario: Verify that the Approve of a Draft parent element will approve all child elements in Final status
        Given [API] A CRF Collection in status Draft exists linking a child Form, Item Group, and Item in Status Draft
        And The '/library/crf-builder/collections' page is opened
        When I search for the existed collection
        And The 'Approve' option is clicked from the three dot menu list
        Then The approval popup window is displayed
        And All the child elements should displayed in the notification page
        When Action is confirmed by clicking continue
        And The item has status 'Final' and version '1.0'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '1.0' and status 'Final' of the linked child elements

    Scenario: Verify that the New Version of a Final child element will impact the parent element in Draft status
        Given [API] A CRF Collection in status Draft exists linking a child Form, Item Group, and Item in Status Final
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        And The '/library/crf-builder/item-groups' page is opened
        When I search for the existed item group
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        And The '/library/crf-builder/items' page is opened
        When I search for the existed item
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '1.1' and status 'Draft' of the linked child elements

    Scenario: Verify that the New Version of a Final child element will not impact the parent element in Final status
        Given [API] A CRF Collection in status Final exists linking a child Form, Item Group, and Item in Status Final
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        And The '/library/crf-builder/item-groups' page is opened
        When I search for the existed item group
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        And The '/library/crf-builder/items' page is opened
        When I search for the existed item
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '1.0' and status 'Final' of the linked child elements


@manual_test
    Scenario: Verify that the Edit of a Draft child element will not impact the parent element in Final status
        Given [API] A CRF Collection in status Final exists linking a child Form, Item Group, and Item in Status Draft
        When I click on 'Edit' option from the three dot menu for the Form
        And I update the Form and click on the Save button
        Then The Form is in Draft status and a new version is created
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        When I approve the Form and make the Item Group be in Status Draft
        Then The Form is in status Final, and the Item Group is in Status Draft
        When I click on 'Edit' option from the three dot menu for the Item Group
        And I update the Item Group and click on the Save button
        Then The Item Group is in Draft status and a new version is created
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Form should still link to the old version of the linked Item Group
        When I approve the Item Group and make the Item be in Status Draft
        Then The Item Group is in status Final, and the child Item is in Status Draft
        When I click on 'Edit' option from the three dot menu for the Item
        And I update the Item and click on the Save button
        Then The Item is in Draft status and a new version is created
        When The '/library/crf-builder/crf-tree' page is opened
        Then Item Group should still link to the old version of the linked Item
        # Notification for editing action is under discussion
        # Then the 'Note, the following CRF Collections have references to this Form, Item Group, or Items, and if updates are saved this will apply to these CRF collections:' notification is presented to the user
        # And the list of affected CRF Collections are listed

@manual_test
    Scenario: Verify that the Approve of a Draft element will not impact either the parent nor child element in Final status
        Given A CRF Collection in status Final exists linking a Draft Form, a Final Item Group, and a Final Item
        When I click on 'Approve' option from the three dot menu for the Form
        Then The 'Approving the element will approve the following child elements' notification is displayed
        And 'No child items will be affected.' text should be displayed in the notification page
        When I click on 'APPROVE FORM' button 
        Then The Form is approved
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        And The linked Item Group and Item are still in Final status

@manual_test
    Scenario: Verify that the Inactive of a Final child element will impact the parent element in Draft status
        Given A CRF Collection in status Draft exists linking a Form, an Item Group, and an Item in Status Final
        When I click on 'Inactive' option from the three dot menu for the Form
        Then The Form is in Retired status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should automatically refer to the new latest version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Inactivate action

@manual_test
    Scenario: Verify that the Inactive of a Final child element will not impact the parent element in Final status
        Given A CRF Collection in status Final exists linking a Form in Status Final
        When I click on 'Inactive' option from the three dot menu for the Form
        Then The Form is in Retired status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Inactivate action

@manual_test
    Scenario: Verify that the Reactivate of a Retired child element will impact the parent element in Draft status
        Given A CRF Collection in status Retired exists linking a Form in Status Final
        When I click on 'Reactivate' option from the three dot menu for the Form
        Then The Form is in Final status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should automatically refer to the new latest version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Reactivate action

@manual_test
    Scenario: Verify that the Reactivate of a Retired child element will not impact the parent element in Final status
        Given A CRF Collection in status Retired exists linking a Form in Status Final
        When I click on 'Reactivate' option from the three dot menu for the Form
        Then The Form is in Final status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Reactivate action

# Define how we manage versions of other sub items, like Descriptions, Alias, Conditions, Method,... (this part is under discussion)
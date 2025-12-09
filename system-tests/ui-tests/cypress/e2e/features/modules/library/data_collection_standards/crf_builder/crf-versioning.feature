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

    Scenario: [Draft Parent][Edit Child] User must after editing a CRF child element for a CRF parent element in Draft see the parent CRF element refer to the this latest CRF child version on the CRF Tree page.   
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Item Group is created
        And [API] CRF Item is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Item Group is linked to the form
        And [API] CRF Item is linked to the group
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'Edit' option is clicked from the three dot menu list
        And I update the form and click on the Save button
        And Form save button is clicked
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
        And Form save button is clicked
        Then The item has status 'Draft' and version '0.2'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '0.2' and status 'Draft' of the linked child elements
        # Notification for editing action is under discussion
        # Then the 'Note, the following CRF Collections have references to this Form, Item Group, or Items, and if updates are saved this will apply to these CRF collections:' notification is presented to the user
        # And the list of affected CRF Collections are listed

    Scenario: [Draft Parent][New version Child] User must after creating new version of CRF child element for a CRF parent element in Draft see the parent CRF element refer to the this latest CRF child version on the CRF Tree page.  
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Item Group is created
        And [API] CRF Item is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Item Group is linked to the form
        And [API] CRF Item is linked to the group
        And [API] CRF Form is approved
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

    Scenario: Approve of a Draft CRF Library parent element will approve all child CRF Library elements to Final status
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Item Group is created
        And [API] CRF Item is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Item Group is linked to the form
        And [API] CRF Item is linked to the group
        And The '/library/crf-builder/collections' page is opened
        When I search for the existed collection
        And The 'Approve' option is clicked from the three dot menu list
        Then The approval popup window is displayed
        And All the child elements should displayed in the notification page
        When Action is confirmed by clicking continue
        And The item has status 'Final' and version '1.0'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '1.0' and status 'Final' of the linked child elements

     Scenario: [Final Parent][Edit Child] User must after editing a CRF child element for a CRF parent element in Final see the parent CRF element refer to the old CRF child version on the CRF Tree page.  
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Item Group is created
        And [API] CRF Item is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Item Group is linked to the form
        And [API] CRF Item is linked to the group
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'Edit' option is clicked from the three dot menu list
        And I update the form and click on the Save button
        And Form save button is clicked
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
        And Form save button is clicked
        Then The item has status 'Draft' and version '0.2'
        When The '/library/crf-builder/crf-tree' page is opened
        Then All the parent elements should refer to version '1.0' and status 'Final' of the linked child elements
        # Notification for editing action is under discussion
        # Then the 'Note, the following CRF Collections have references to this Form, Item Group, or Items, and if updates are saved this will apply to these CRF collections:' notification is presented to the user
        # And the list of affected CRF Collections are listed

    Scenario: [Final Parent][New version Child] User must after creating new version of CRF child element for a CRF parent element in Final see the parent CRF element refer to the old CRF child version on the CRF Tree page.  
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Item Group is created
        And [API] CRF Item is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Item Group is linked to the form
        And [API] CRF Item is linked to the group
        And [API] CRF Collection is approved
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

    Scenario: [Final Parent][Approve Child] User must after approving a CRF child element for a CRF parent element in Final see the parent CRF element refer to the old CRF child version on the CRF Tree page. 
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Collection is approved
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        When The 'Approve' option is clicked from the three dot menu list
        Then The approval popup window is displayed
        And No child elements should displayed in the notification page
        When Action is confirmed by clicking continue
        Then The item has status 'Final' and version '2.0'
        When The '/library/crf-builder/crf-tree' page is opened 
        Then Collection still link to the previous old version and Final status of the linked Form

    Scenario: [Final Parent][New version Parent] User must after creating new version of CRF parent element in Final see the parent CRF element refer to the latest CRF child version on the CRF Tree page. 
        Given [API] A CRF Collection is created
        And [API] A CRF Form is created
        And [API] CRF Form is linked to the collection
        And [API] CRF Collection is approved
        And The '/library/crf-builder/forms' page is opened
        When I search for the existed form
        And The 'New version' option is clicked from the three dot menu list
        Then The New version popup window is displayed
        When Action is confirmed by clicking continue
        Then The item has status 'Draft' and version '1.1'
        When The '/library/crf-builder/crf-tree' page is opened 
        Then Collection still link to the previous old version and Final status of the linked Form
        When The '/library/crf-builder/collections' page is opened
        And I search for the existed collection
        When The 'New version' option is clicked from the three dot menu list
        Then The item has status 'Draft' and version '1.1'
        When The '/library/crf-builder/crf-tree' page is opened
        Then Collection should refer to the latest version and status of the child elements

@manual_test
    Scenario: [Draft Parent][Inactive Child] User must after inactive CRF child element for a CRF parent element in Draft see the parent CRF element refer to the new CRF child version on the CRF Tree page.
        Given A CRF Collection in status Draft exists linking a Form, an Item Group, and an Item in Status Final
        When I click on 'Inactive' option from the three dot menu for the Form
        Then The Form is in Retired status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should automatically refer to the new latest version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Inactivate action

@manual_test
    Scenario: [Final Parent][Inactive Child] User must after inactive CRF child element for a CRF parent element in Final see the parent CRF element refer to the old CRF child version on the CRF Tree page.
        Given A CRF Collection in status Final exists linking a Form in Status Final
        When I click on 'Inactive' option from the three dot menu for the Form
        Then The Form is in Retired status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Inactivate action

@manual_test
    Scenario: [Draft Parent][Reactive Child] User must after reactive CRF child element for a CRF parent element in Draft see the parent CRF element refer to the new CRF child version on the CRF Tree page.
        Given A CRF Collection in status Draft exists linking a Form in Status Retired
        When I click on 'Reactivate' option from the three dot menu for the Form
        Then The Form is in Final status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should automatically refer to the new latest version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Reactivate action

@manual_test
    Scenario: [Final Parent][Reactive Child] User must after reactive CRF child element for a CRF parent element in Final see the parent CRF element refer to the old CRF child version on the CRF Tree page.
        Given A CRF Collection in status Final exists linking a Form in Status Retired
        When I click on 'Reactivate' option from the three dot menu for the Form
        Then The Form is in Final status
        When The '/library/crf-builder/crf-tree' page is opened 
        Then CRF Collection should still link to the old version of the linked Form
        # All scenarios related to CRF forms, Item Groups, and Items can be repeated for the Reactivate action

# Define how we manage versions of other sub items, like Descriptions, Alias, Conditions, Method,... (this part is under discussion)
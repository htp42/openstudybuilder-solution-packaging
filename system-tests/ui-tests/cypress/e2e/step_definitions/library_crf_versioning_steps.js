// cypress/support/step_definitions/library_crf_versioning_steps.js

const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

// Function to generate shorter unique names using base-36 encoding
const generateShortUniqueName = (prefix) => {
    const timestamp = Date.now().toString(36); // Convert timestamp to base-36
    return `${prefix}${timestamp}`; // Create the unique name
};

let collectionName, formName, itemGroupName, itemName
let collectionUid, formUid, itemGroupUid, itemUid


Given('[API] A CRF Collection in status Draft exists linking a child Form, Item Group, and Item in Status Draft', () => {
    collectionName = generateShortUniqueName('C_');
    formName = generateShortUniqueName('F_');
    itemGroupName = generateShortUniqueName('IG_');
    itemName = generateShortUniqueName('I_');
     // Step 1: Create a CRF Collection
    cy.createCrfCollectionByName(collectionName).then((collectionResponse) => {
        collectionUid = collectionResponse.uid; // Ensure to capture the UID, correct variable name
        cy.log(`Created CRF Collection with UID: ${collectionUid}`);

        // Step 2: Create a Form
        cy.createCrfFormByName(formName).then((formResponse) => {
            formUid = formResponse.uid; // Capture the UID of the created form
            cy.log(`Created Form with UID: ${formUid}`);

            // Log the UIDs to ensure they are valid
            cy.log(`Linking Form UID: ${formUid} to Collection UID: ${collectionUid}`);

            // Step 3: Link the Form to the Collection
            cy.linkFormToCollection(formUid, collectionUid).then(() => {
                cy.log(`Linked Form UID: ${formUid} to Collection UID: ${collectionUid}`);

                // Step 4: Create an Item Group
                cy.createCrfItemGroupByName(itemGroupName).then((itemGroupResponse) => {
                    itemGroupUid = itemGroupResponse.uid; // Capture the UID of the created item group

                    // Step 5: Link the Item Group to the Form
                    cy.linkItemGroupToForm(formUid, itemGroupUid).then(() => {
                        // Step 6: Create an Item
                        cy.createCrfItemByName(itemName).then((itemResponse) => {
                            itemUid = itemResponse.uid; // Capture the UID of the created item

                            // Step 7: Link the Item to the Item Group
                            cy.linkItemToItemGroup(itemGroupUid, itemUid).then(() => {
                            });
                        });
                    });
                });
            });
        });
    });
});

Given('[API] A CRF Collection in status Draft exists linking a child Form, Item Group, and Item in Status Final', () => {
    collectionName = generateShortUniqueName('C_');
    formName = generateShortUniqueName('F_');
    itemGroupName = generateShortUniqueName('IG_');
    itemName = generateShortUniqueName('I_');
     // Step 1: Create a CRF Collection
    cy.createCrfCollectionByName(collectionName).then((collectionResponse) => {
        collectionUid = collectionResponse.uid; // Ensure to capture the UID, correct variable name
        cy.log(`Created CRF Collection with UID: ${collectionUid}`);

        // Step 2: Create a Form
        cy.createCrfFormByName(formName).then((formResponse) => {
            formUid = formResponse.uid; // Capture the UID of the created form
            cy.log(`Created Form with UID: ${formUid}`);

            // Log the UIDs to ensure they are valid
            cy.log(`Linking Form UID: ${formUid} to Collection UID: ${collectionUid}`);

            // Step 3: Link the Form to the Collection
            cy.linkFormToCollection(formUid, collectionUid).then(() => {
                cy.log(`Linked Form UID: ${formUid} to Collection UID: ${collectionUid}`);

                // Step 4: Create an Item Group
                cy.createCrfItemGroupByName(itemGroupName).then((itemGroupResponse) => {
                    itemGroupUid = itemGroupResponse.uid; // Capture the UID of the created item group

                    // Step 5: Link the Item Group to the Form
                    cy.linkItemGroupToForm(formUid, itemGroupUid).then(() => {
                        // Step 6: Create an Item
                        cy.createCrfItemByName(itemName).then((itemResponse) => {
                            itemUid = itemResponse.uid; // Capture the UID of the created item

                            // Step 7: Link the Item to the Item Group
                            cy.linkItemToItemGroup(itemGroupUid, itemUid).then(() => {
                                cy.approveForm(formUid);
                            });
                        });
                    });
                });
            });
        });
    });
});


Given('[API] A CRF Collection in status Final exists linking a child Form, Item Group, and Item in Status Final', () => {
     collectionName = generateShortUniqueName('C_');
    formName = generateShortUniqueName('F_');
    itemGroupName = generateShortUniqueName('IG_');
    itemName = generateShortUniqueName('I_');
     // Step 1: Create a CRF Collection
    cy.createCrfCollectionByName(collectionName).then((collectionResponse) => {
        collectionUid = collectionResponse.uid; // Ensure to capture the UID, correct variable name
        cy.log(`Created CRF Collection with UID: ${collectionUid}`);

        // Step 2: Create a Form
        cy.createCrfFormByName(formName).then((formResponse) => {
            formUid = formResponse.uid; // Capture the UID of the created form
            cy.log(`Created Form with UID: ${formUid}`);

            // Log the UIDs to ensure they are valid
            cy.log(`Linking Form UID: ${formUid} to Collection UID: ${collectionUid}`);

            // Step 3: Link the Form to the Collection
            cy.linkFormToCollection(formUid, collectionUid).then(() => {
                cy.log(`Linked Form UID: ${formUid} to Collection UID: ${collectionUid}`);

                // Step 4: Create an Item Group
                cy.createCrfItemGroupByName(itemGroupName).then((itemGroupResponse) => {
                    itemGroupUid = itemGroupResponse.uid; // Capture the UID of the created item group

                    // Step 5: Link the Item Group to the Form
                    cy.linkItemGroupToForm(formUid, itemGroupUid).then(() => {
                        // Step 6: Create an Item
                        cy.createCrfItemByName(itemName).then((itemResponse) => {
                            itemUid = itemResponse.uid; // Capture the UID of the created item

                            // Step 7: Link the Item to the Item Group
                            cy.linkItemToItemGroup(itemGroupUid, itemUid).then(() => {
                                cy.approveCollection(collectionUid);
                            });
                        });
                    });
                });
            });
        });
    });
});


When('I search for the existed collection', () => {
    cy.searchAndCheckPresence(collectionName, true);
});

When('I search for the existed form', () => {
    cy.searchAndCheckPresence(formName, true);
});

When('I search for the existed item group', () => {
    cy.searchAndCheckPresence(itemGroupName, true);
});

When('I search for the existed item', () => {
    cy.searchAndCheckPresence(itemName, true);
});

When('I update the form and click on the Save button', () => {
    updateForm(formName)
    cy.clickButton('save-button');

});

When('I update the item group and click on the Save button', () => {
    updateItemGroup(itemGroupName)
    cy.clickButton('save-button');

});

When('I update the item and click on the Save button', () => {
    updateItem(itemName)
    cy.clickButton('save-button');

});

Then('All the parent elements should refer to version {string} and status {string} of the linked child elements', (version, status) => {
    verifyLinkedForm (collectionName, formName, itemGroupName, itemName, version, status);
});

Then('All the child elements should displayed in the notification page', () => {
    // Check that the dialog is visible
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible') // Assert that the dialog is visible
      .and('contain', formName) 
      .and('contain', itemGroupName)
      .and('contain', itemName);
});

function verifyLinkedForm (collectionName, formName, itemGroupName, itemName, version, status) {

    // Display all pages to ensure all collections are visible
        cy.get('.v-data-table-footer__items-per-page') // Target the container for items per page
            .find('.v-select__selection') // Find the selected area of the dropdown
            .click(); // Click to open the dropdown
        cy.waitForTable();
        cy.contains('All').click(); // Click on the "All" option

    cy.contains(collectionName).parents('tr').find('button.v-btn.v-btn--icon').first().click();
    cy.contains(formName).should('exist');
    cy.contains(version).should('exist');
    cy.contains(status).should('exist');

    cy.contains(formName).parents('tr').find('button.v-btn.v-btn--icon').first().click();
    cy.contains(itemGroupName).should('exist');
    cy.contains(version).should('exist');
    cy.contains(status).should('exist');

    cy.contains(itemGroupName).parents('tr').find('button.v-btn.v-btn--icon').first().click();
    cy.contains(itemName).should('exist');
    cy.contains(version).should('exist');
    cy.contains(status).should('exist');
    
}

function updateForm(formName) {
    const updatedFormName = `${formName} update`; 
    cy.fillInput('form-oid-name', updatedFormName);
}

function updateItemGroup(itemGroupName) {
    const updateditemGroupName = `${itemGroupName} update`; 
    cy.fillInput('item-group-name', updateditemGroupName);
}

function updateItem(itemName) {
    const updateditemName = `${itemName} update`; 
    cy.fillInput('item-name', updateditemName);
}




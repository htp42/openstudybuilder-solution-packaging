import { generateShortUniqueName } from "../../support/helper_functions";
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let collectionName, formName, itemGroupName, itemName
let collectionUid, formUid, itemGroupUid, itemUid

Given('[API] A CRF Collection is created', () => {
    collectionName = generateShortUniqueName('C_');
    cy.createCrfCollection(collectionName).then(collectionResponse => collectionUid = collectionResponse.body.uid)
})

Given('[API] A CRF Form is created', () => {
    formName = generateShortUniqueName('F_');
    cy.createCrfForm(formName).then(formResponse => formUid = formResponse.body.uid)
})

Given('[API] CRF Item Group is created', () => {
    itemGroupName = generateShortUniqueName('IG_');
    cy.createCrfItemGroup(itemGroupName).then(itemGroupResponse => itemGroupUid = itemGroupResponse.body.uid)
})

Given('[API] CRF Item is created', () => {
    itemName = generateShortUniqueName('I_');
    cy.createCrfItem(itemName).then((itemResponse) => itemUid = itemResponse.body.uid)
})

Given('[API] CRF Form is linked to the collection', () => cy.linkFormToCollection(formUid, collectionUid))

Given('[API] CRF Item Group is linked to the form', () => cy.linkItemGroupToForm(formUid, itemGroupUid))

Given('[API] CRF Item is linked to the group', () => cy.linkItemToItemGroup(itemGroupUid, itemUid))

Given('[API] CRF Form is approved', () => cy.approveForm(formUid))

Given('[API] CRF Collection is approved', () => cy.approveCollection(collectionUid))

When('I search for the existed collection', () => cy.searchAndCheckPresence(collectionName, true))

When('I search for the existed form', () => cy.searchAndCheckPresence(formName, true))

When('I search for the existed item group', () => cy.searchAndCheckPresence(itemGroupName, true))

When('I search for the existed item', () => cy.searchAndCheckPresence(itemName, true))

When('I update the form and click on the Save button', () => cy.fillInput('form-oid-name', `${formName} update`))

When('I update the item group and click on the Save button', () => cy.fillInput('item-group-name', `${itemGroupName} update`))

When('I update the item and click on the Save button', () => cy.fillInput('item-name', `${itemName} update`))

Then('All the parent elements should refer to version {string} and status {string} of the linked child elements', (version, status) => {
    verifyLinkedChildElement (collectionName, formName, itemGroupName, itemName, version, status);
})

Then('All the child elements should displayed in the notification page', () => {
    // Check that the dialog is visible
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible')
      .and('contain', formName) 
      .and('contain', itemGroupName)
      .and('contain', itemName);
});

Then('Collection still link to the previous old version and Final status of the linked Form', () => {
    verifyLinkedForm (collectionName, formName, '1.0', 'Final');
});

Then('Collection should refer to the latest version and status of the child elements', () => {
    verifyLinkedForm (collectionName, formName, '1.1', 'Draft');
});

Then('No child elements should displayed in the notification page', () => {
    // Check that the dialog is visible
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible') // Assert that the dialog is visible
      .and('contain', 'No child items will be affected.'); // Check that it contains the specific text
});


function verifyLinkedChildElement (collectionName, formName, itemGroupName, itemName, version, status) {
    // Display all pages to ensure all collections are visible
    cy.get('.v-data-table-footer__items-per-page') // Target the container for items per page
        .find('.v-select__selection').click();
    cy.waitForTable();
    cy.contains('All').click();

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

function verifyLinkedForm (collectionName, formName, version, status) {
    // Display all pages to ensure all collections are visible
    cy.get('.v-data-table-footer__items-per-page') // Target the container for items per page
        .find('.v-select__selection').click();
    cy.waitForTable();
    cy.contains('All').click();

    cy.contains(collectionName).parents('tr').find('button.v-btn.v-btn--icon').first().click();
    cy.contains(formName).should('exist');
    cy.contains(version).should('exist');
    cy.contains(status).should('exist');
}
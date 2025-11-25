const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let itemGroupNameDefault, itemGroupOidDefault

When('Created CRF Item Group is found', () => cy.searchAndCheckPresence(itemGroupNameDefault, true))

Then('The CRF Item Group is no longer available', () => cy.searchAndCheckPresence(itemGroupNameDefault, false))

When('The CRF Item Group definition container is filled with data', () => {
    itemGroupNameDefault = `CrfItemGroup${Date.now()}`
    itemGroupOidDefault = `Oid${Date.now()}`
    cy.fillInput('item-group-oid', itemGroupOidDefault)
    cy.fillInput('item-group-name', itemGroupNameDefault)
})

When('The CRF Item Group metadata are updated', () => {
    itemGroupNameDefault = `Update ${itemGroupNameDefault}`
    itemGroupOidDefault = `Update ${itemGroupNameDefault}`
    cy.fillInput('item-group-oid', itemGroupOidDefault)
    cy.fillInput('item-group-name', itemGroupNameDefault)
})

Then('The Item Group approval dialog is displayed', () => {
    // Selecting the dialog card based on its classes
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible') // Assert that the dialog is visible
      .and('contain', 'Approving the item group will approve the following child elements:'); // Assert that it contains specific text
});

When('The CRF Item Group definition is filled without name provided and the next button is clicked', () => {
    cy.clickButton('add-crf-item-group')
    cy.clickFormActionButton('continue')
})

Then('The validation appears for the CRF Item Group Name field', () => cy.get('.v-messages__message').should('be.visible'))
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

export let elementName

When('[API] Uids are fetched for element subtype {string}', (subtypeName) => cy.getElementTypeAndSubType(subtypeName))

When('[API] Element is created for the test study', () => {
    elementName = `El${Date.now()}`
    cy.addElementToStudy(Cypress.env('TEST_STUDY_UID'), elementName)
})

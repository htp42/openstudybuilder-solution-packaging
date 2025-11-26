const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let crfTemplateName, crfTemplateOid, effectiveDate = 10, retiredDate = 15

When('Created CRF Collection is found', () => cy.searchAndCheckPresence(crfTemplateName, true))

Then('The CRF Collection is no longer available', () => cy.searchAndCheckPresence(crfTemplateName, false))

Given('[API] The CRF Collection in draft status exists', () => {
    crfTemplateName = `API_CrfItem${Date.now()}`
    cy.createCrfCollection(crfTemplateName)
})

When('The CRF Collection definition container is filled with data and saved', () => {
    crfTemplateName = `CrfItem${Date.now()}`
    crfTemplateOid = `Oid${Date.now()}`
    fillNameAndOid()
    cy.selectDatePicker('crf-collection-effective-date', effectiveDate)
    cy.selectDatePicker('crf-collection-retired-date', retiredDate)
    saveCrfTemplate('created')
})

When('The CRF Collection metadata are updated and saved', () => {
    crfTemplateName += 'Update'
    crfTemplateOid += 'Update'
    effectiveDate += 1
    retiredDate += 1
    fillNameAndOid()
    cy.selectDatePicker('crf-collection-effective-date', effectiveDate)
    cy.selectDatePicker('crf-collection-retired-date', retiredDate)
    saveCrfTemplate('updated')
})

Then('The CRF Collection is visible in the table', () => {
    cy.checkRowByIndex(0, 'Name', crfTemplateName)
    cy.checkRowByIndex(0, 'OID', crfTemplateOid)
    cy.checkRowByIndex(0, 'Effective', effectiveDate)
    cy.checkRowByIndex(0, 'Obsolete', retiredDate)
})

When('The CRF Collection definition container is filled without name provided', () => cy.clickButton('save-button'))

Then('The validation appears for the CRF Collection Name field', () => cy.get('.v-messages__message').should('be.visible'))

Then('The approval popup window is displayed', () => {
    // Check that the dialog is visible
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible') // Assert that the dialog is visible
      .and('contain', 'Approving the element will approve the following child elements:'); // Check that it contains the specific text
});

function saveCrfTemplate(action) {
    cy.clickButton('save-button')
    cy.waitForFormSave()
    cy.checkSnackbarMessage(`${action}`)
}

function fillNameAndOid() {
    cy.fillInput('crf-collection-oid', crfTemplateOid)
    cy.fillInput('crf-collection-name', crfTemplateName)
}
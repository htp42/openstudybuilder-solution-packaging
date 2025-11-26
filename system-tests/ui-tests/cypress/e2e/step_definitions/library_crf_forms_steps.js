const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let formNameDefault, formOidDefault

Then('CRF {string} page is loaded', (tabName) => cy.get('button.v-tab-item--selected').should('have.text', tabName))

When('Created CRF form is found', () => cy.searchAndCheckPresence(formNameDefault, true))

Then('The CRF Form is no longer available', () => cy.searchAndCheckPresence(formOidDefault, false))

When('The Form definition container is filled with data', () => changeFormData(`CrfForm${Date.now()}`, `CrfForm${Date.now()}`))

When('The Form metadata are updated and saved', () => changeFormData(`Update ${formNameDefault}`, `Update ${formOidDefault}`))

Then('The New version popup window is displayed', () => {
    // Check that the dialog is visible
    cy.get('.v-card.v-theme--NNCustomLightTheme')
      .should('be.visible') // Assert that the dialog is visible
      .and('contain', 'Creating a new version can affect the following parent elements:'); // Check that it contains the specific text
});

function changeFormData(formName, formOid) {
    formOidDefault = formName
    formNameDefault = formOid
    cy.fillInput('form-oid-name', formNameDefault)
    cy.fillInput('form-oid', formOidDefault)
}
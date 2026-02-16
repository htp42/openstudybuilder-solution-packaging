const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('User sets row page to {int} in the settings menu', (rowsPerPage) => {
    cy.clickButton('topbar-admin-icon')
    cy.contains('.v-input', 'Rows per page').click()
    cy.contains('.v-list-item', `${rowsPerPage}`).click()
    cy.clickButton('save-settings-button')
})
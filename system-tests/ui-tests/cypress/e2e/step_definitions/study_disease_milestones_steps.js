const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('The new Study Disease Milestone is added', () => {
    cy.clickButton('create-disease-milestone')
    cy.selectAutoComplete('disease-milestone-type', 'Diagnosis of diabetes')
})

Then('The new Study Disease Milestone is visible within the study disease milestones table', () => {
    cy.checkRowByIndex(0, '#','1')
    cy.checkRowByIndex(0, 'Type', 'Diagnosis of diabetes')
    cy.checkRowByIndex(0, 'Definition', 'Initial diagnosis of')
    cy.checkRowByIndex(0, 'Repetition indicator', 'No')
})

Given('The test Study Disease Milestones exists', () => {
    cy.checkAndCreateDiseaseMilestone()
})

When('The Study Disease Milestones is edited', () => {
    cy.waitForTableData()
    cy.checkbox('repetition-indicator')
})

Then('The Study Disease Milestones with updated values is visible within the table', () => {
    cy.wait(500)
    cy.checkRowByIndex(0, 'Repetition indicator', 'Yes')
})

When('The user tries to close the form without Disease Milestone Type provided', () => {
    cy.waitForTableData()
    cy.clickButton('create-disease-milestone')
})

Then('The validation appears under that field in the Disease Milestones form', () => {
    cy.get('.v-messages__message').should('contain', 'This field is required')
})

When('New Disease Milestone Type is created with the same Disease Milestone Type', () => {
    cy.clickButton('create-disease-milestone')
    cy.selectAutoComplete('disease-milestone-type', 'Diagnosis of diabetes')
})

Then('The test Study Disease Milestones is no longer available', () => cy.contains('table tbody tr', 'Diagnosis of diabetes').should('not.exist'))
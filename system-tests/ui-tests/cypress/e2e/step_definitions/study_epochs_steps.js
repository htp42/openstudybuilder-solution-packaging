const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");

let epochDescription = `Epoch ${getShortUniqueId()}`

When('User intercepts epochs data', () => cy.intercept(`**/study-epochs**`).as('epochsRequests'))

When('User waits for epochs data', () => cy.wait('@epochsRequests'))

When('User waits for epochs to load', () => {
    cy.intercept(`**/study-epochs?page_size=0`).as('getEpochs')
    cy.wait('@getEpochs').its('response.statusCode').should('eq', 200)
})

When('Study Epoch is found', () => cy.searchAndCheckPresence(epochDescription, true))

When('Study Epoch is not available', () => cy.searchAndCheckPresence(epochDescription, false))

When('A new Study Epoch is added', () => {
    cy.clickButton('create-epoch')
    cy.selectAutoComplete('epoch-type', 'Post Treatment')
    cy.selectAutoComplete('epoch-subtype', 'Elimination')
    fillRulesAndDecscription('D10', 'D99')
})

Then('The new Study Epoch is available within the table', () => {
    cy.checkRowByIndex(0, 'Epoch name', 'Elimination')
    cy.checkRowByIndex(0, 'Epoch type', 'Post Treatment')
    cy.checkRowByIndex(0, 'Epoch subtype', 'Elimination')
    cy.checkRowByIndex(0, 'Start rule', 'D10')
    cy.checkRowByIndex(0, 'End rule', 'D99')
    cy.checkRowByIndex(0, 'Description', epochDescription)
})

When('The Study Epoch is edited', () => {
    epochDescription = `Edited epoch ${getShortUniqueId()}`
    cy.wait(1000)
    fillRulesAndDecscription('D22', 'D33')
})

Then('The Type and Subtype fields are disabled', () => {
    cy.checkIfInputDisabled('epoch-type')
    cy.checkIfInputDisabled('epoch-subtype')
})

Then('The edited Study Epoch with updated values is available within the table', () => {
    cy.checkRowByIndex(0, 'Description', epochDescription)
    cy.checkRowByIndex(0, 'Start rule', 'D22')
    cy.checkRowByIndex(0, 'End rule', 'D33')
})

function fillRulesAndDecscription(startRule, endRule) {
    cy.fillInput('description', epochDescription)
    cy.fillInput('epoch-start-rule', startRule)
    cy.fillInput('epoch-end-rule', endRule)
}
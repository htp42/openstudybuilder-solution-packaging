
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

Then('Important is set to {string} in the Study Activity Instance table', (expectedValue) => cy.checkRowByIndex(0, 'Important', expectedValue))

Then('Important is set to empty string in the Study Activity Instance table', () => cy.checkRowByIndex(0, 'Important', null))
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('The {string} button is clicked in Protocol Process page', (button) => {
    cy.get(`.v-card-text [data-cy="${button}"]`).click({force: true})
})
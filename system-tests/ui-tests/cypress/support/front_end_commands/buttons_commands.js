Cypress.Commands.add('clickFirstButton', (button, optionForce = false) => {
    cy.get('[data-cy="' + button + '"]')
        .first()
        .click({ force: optionForce })
})

Cypress.Commands.add('clickButton', (button, optionForce = true) => {
    cy.get('[data-cy="' + button + '"]').click({ force: optionForce })
})

Cypress.Commands.add('clickFormActionButton', (action) => {
    cy.get(`.v-card-actions [data-cy="${action.toLowerCase()}-button"]`).click({ force: true })
    cy.get(`.v-card-actions [data-cy="${action.toLowerCase()}-button"] .v-progress-circular`, { timeout: 30000 }).should('not.exist') 
    if (action != 'save') cy.wait(1500)
})

Cypress.Commands.add('clickByIndex', (button, index, optionForce = true) => {
    cy.get('[data-cy="' + button + '"]').eq(index).click({ force: optionForce })
})

Cypress.Commands.add('toggleButton', (button, optionForce = true, optionMultiple = false) => {
    cy.get('[data-cy="' + button + '"]').click({ force: optionForce, multiple: optionMultiple })
})

Cypress.Commands.add('toggleFirstButton', (button, optionForce = true, optionMultiple = false) => {
    cy.get('[data-cy="' + button + '"]').first().click({ force: optionForce, multiple: optionMultiple })
})

Cypress.Commands.add('clickTab', (tabName, optionForce = 'true') => {
    cy.contains('.v-tab', tabName).click({ force: optionForce })
})

Cypress.Commands.add('checkAllCheckboxes', () => {
    cy.get('[data-cy="not-applicable-checkbox"] input').each((btn) => cy.wrap(btn).check({ force: true }))
})

Cypress.Commands.add('uncheckAllCheckboxes', () => {
    cy.get('[data-cy="not-applicable-checkbox"] input').each((btn) => cy.wrap(btn).uncheck({ force: true }))
})

Cypress.Commands.add('checkbox', (button, optionForce = true, optionMultiple = false) => {
    cy.get('[data-cy="' + button + '"]').within(() => {
        cy.get('input').click({ force: optionForce, multiple: optionMultiple })
    })
})
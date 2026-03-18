const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('User waits for table to load', () => cy.waitForTable())

When('The {string} submenu is clicked in the {string} section', (submenu, section) => {
    cy.get('.v-navigation-drawer__content').within(() => {
        cy.clickButton(section).within(() => cy.clickButton(submenu))
    })
})

When('The {string} tab is selected', (tabName) => {
    cy.clickTab(tabName)
})

When('The {string} button is clicked', (button) => {
    cy.clickButton(button)
})

When('The {string} is clicked in the dropdown', (item) => cy.contains('.v-overlay__content .v-list-item', item).click())

When('The last available item from timeline is clicked', () => {
    cy.waitForTable()
    cy.get('[data-cy="timeline-date"]').last().click()
})

When('The {string} is clicked in the dropdown of {string} tile', (link, tileName) => {
    expandPagesDropdown(tileName)
    cy.contains('.v-overlay__content .v-list-item-title', link).click()
    cy.wait(1000);
})

When('The {string} is not listed after the dropdown {string} is clicked', (link, tileName) => {
    expandPagesDropdown(tileName)
    cy.contains('.v-overlay__content .v-list-item-title', link).should('not.exist')
    cy.wait(1000);
})

Then('The form is not closed', () => cy.get('[data-cy="form-body"]').should('be.visible'))

When('The online help button is clicked', () => {
    cy.get('.page-title').within(() => {
        cy.get('.mdi-help-circle-outline').click()
    })
})

Then('The online help panel shows {string} panel with content {string}', (panelName, helpText) => {
    cy.contains('.v-expansion-panel', panelName).then((el) => {
        cy.wrap(el).click()
        cy.wrap(el).within(() => {
            cy.get('.v-expansion-panel-text__wrapper div').invoke('text').then((text) => {
                expect(text.trim()).to.eq(helpText.trim());
            })
        })
    })
})

Then('All Not Applicable checkboxes are checked', () => cy.get('[data-cy="not-applicable-checkbox"] input').each((btn) => cy.wrap(btn).check()))

Then('The edit content button is clicked', () => {
    cy.clickButton('edit-content')
    cy.wait(1000)
})

Then('The pencil button is clicked', () => {
    cy.get('button .mdi-pencil-outline').click()
    cy.wait(1000)
})

Then('The pencil button is not available', () => cy.get('button .mdi-pencil-outline').should('not.exist'))

Then('The plus button is clicked', () => cy.get('button .mdi-plus').click())

Then('The new version plus button is clicked', () => cy.get('button .mdi-plus-circle-outline').click())

Then('The new version plus button is not available', () => cy.get('button .mdi-plus-circle-outline').should('not.exist'))

Then('The approve button is clicked', () => cy.get('button .mdi-check-decagram').click())

Then('The approve button is not available', () => cy.get('button .mdi-check-decagram').should('not.exist'))

Then('The inactivate button is clicked', () => cy.get('button .mdi-close-octagon-outline').click())

Then('The inactivate button is not available', () => cy.get('button .mdi-close-octagon-outline').should('not.exist'))

Then('The download button is clicked', () => cy.get('button .mdi-download-outline').filter(':visible').click())

Then('The close overview button is clicked', () => cy.get('button .mdi-close').filter(':visible').click())

Then('The history button is clicked', () => cy.get('button .mdi-history').click())

function expandPagesDropdown(tileName) {
    cy.wait(500)
    cy.get(`[data-cy="tiles-box"] [data-cy="${tileName}"] [data-cy="dropdown-button"]`).click()
    cy.wait(500)
}
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let data_supplier_name
let supplier_index
let current_version

Given('The data supplier is found', () => cy.searchAndCheckPresence(data_supplier_name, true))

Given('The user defines data supplier name, type, description, order, api url, frontend url, origin source and origin type', () => {
    data_supplier_name = `E2E ${Date.now()}`
    cy.fillInput('data-supplier-name', data_supplier_name)
    cy.selectVSelect('data-supplier-type-uid', 'EDC System')
    cy.fillInput('data-supplier-order', '2')
    cy.get('[data-cy="data-supplier-description"]').eq(0).type('Test Description')
    cy.get('[data-cy="data-supplier-description"]').eq(1).type('APIURL')
    cy.get('[data-cy="data-supplier-description"]').eq(2).type('UIURL')
    cy.selectVSelect('data-supplier-origin-source-uid', 'Clinical Study Sponsor')
    cy.selectVSelect('data-supplier-origin-type-uid', 'Assigned Value')
})

Then('The data supplier is created successfully', () => {
    cy.checkRowByIndex(0, 'Name', data_supplier_name)
    cy.checkRowByIndex(0, 'Order', '2')
    cy.checkRowByIndex(0, 'Description', 'Test Description')
    cy.checkRowByIndex(0, 'Name', data_supplier_name)
    cy.checkRowByIndex(0, 'API base URL', 'APIURL')
    cy.checkRowByIndex(0, 'UI base URL', 'UIURL')
    cy.checkRowByIndex(0, 'Type', 'EDC System')
    cy.checkRowByIndex(0, 'Origin Source', 'Clinical Study Sponsor')
    cy.checkRowByIndex(0, 'Origin Type', 'Assigned Value')
})


When('The user edits data supplier name, type, description, order, api url, frontend url, origin source and origin type', () => {
    data_supplier_name = `Update ${data_supplier_name}`
    cy.fillInput('data-supplier-name', data_supplier_name)
    cy.selectVSelect('data-supplier-type-uid', 'Lab Data Exchange Files')
    cy.get('[data-cy="data-supplier-description"]').eq(0).type('Test Update')
    cy.get('[data-cy="data-supplier-description"]').eq(1).type('APIURL1')
    cy.get('[data-cy="data-supplier-description"]').eq(2).type('UIURL1')
    cy.selectVSelect('data-supplier-origin-source-uid', 'Investigator')
    cy.selectVSelect('data-supplier-origin-type-uid', 'Collected Value')
})

Then('The data supplier is updated successfully', () => {
    cy.checkRowByIndex(0, 'Name', data_supplier_name)
    cy.checkRowByIndex(0, 'Order', '2')
    cy.checkRowByIndex(0, 'Description', 'Test Update')
    cy.checkRowByIndex(0, 'API base URL', 'APIURL1')
    cy.checkRowByIndex(0, 'UI base URL', 'UIURL1')
    cy.checkRowByIndex(0, 'Type', 'Lab Data Exchange Files')
    cy.checkRowByIndex(0, 'Origin Source', 'Investigator')
    cy.checkRowByIndex(0, 'Origin Type', 'Collected Value')
})

When('The user intercepts version history request', () => cy.intercept('**versions').as('versionHistory'))

Then('The changes history is presented to the user', () => {
    cy.wait('@versionHistory').then(req => {
        cy.get('[data-cy="version-history-window"]').within(() => {
            console.log(req.response.body)
        req.response.body.forEach((item, index) => {
        cy.checkRowByIndex(index, 'Name', item.name)
        cy.checkRowByIndex(index, 'Order', item.order)
        cy.checkRowByIndex(index, 'Version', item.version)
        })
        })
    })
})
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

export let selectedSupplierValue
let userDefinedSupplierValue, selectedSupplierType
let selectedSupplierValues = []

When('User intercepts data supplier request', () => cy.intercept('/api/studies/*/study-data-suppliers?*').as('dataSuppliers'))

When('Data supplier type is set to {string}', (dataSupplierType) => selectedSupplierType = dataSupplierType)

When('Data supplier is searched and found', () => cy.searchAndCheckPresence(selectedSupplierValue, true))

When('User defined data supplier is searched and not found', () => cy.searchAndCheckPresence(userDefinedSupplierValue, false))

When('User clicks ADD USER DEFINED DATA SUPPLIER button', () => cy.contains('button', 'Add user defined data supplier').click())

When('The Edit button is clicked', () => cy.get('button[title="Edit"]').click())

When('The Save button is clicked', () => cy.contains('button', 'Save').click())

Then('The Edit Study Data Supplier page is opened', () => cy.contains('.page-title', 'Edit Study Data Supplier').should('be.visible'))

When('The + button is clicked', () => cy.contains('.supplier-type-section', selectedSupplierType).find('button .mdi-plus').click())

When('The Remove button is clicked for user defined supplier', () => {
    cy.contains('.supplier-type-section', selectedSupplierType).contains('.mb-3', userDefinedSupplierValue).find('button:contains("Remove")').click()
})

When('All data suppliers are removed', () => {
    cy.wait('@dataSuppliers').then((request) => {
        if (request.response.body.total > 0) cy.get('button:contains("Remove")').each(el => cy.wrap(el).click())
    })
})

When('I select the value with index {int} from the Data supplier dropdown menu', (index) => {
    cy.contains('.supplier-type-section', selectedSupplierType).find('.v-select').last().find('.v-field[role="combobox"]').click()
    cy.get('.v-overlay__content .v-list-item').eq(index).then(el => {
        cy.wrap(el).invoke('text').then((val) => (selectedSupplierValue = val, selectedSupplierValues.push(val)))
        cy.wrap(el).click()
    })
});

When('I select the user defined value from the Data supplier dropdown menu', () => {
    cy.contains('.supplier-type-section', selectedSupplierType).find('.v-select').last().find('.v-field[role="combobox"]').click()
    cy.contains('.v-overlay__content .v-list-item', userDefinedSupplierValue).click()
});

Then('The selected Data supplier value is visible in the dropdown', () => {
    cy.contains('.supplier-type-section', selectedSupplierType).find('.v-select').last().find('.v-field[role="combobox"]').should('have.text', selectedSupplierValue)
})

Then('The user defined supplier type should be found in the table for {string} and {string}', (firstDataSupplier, secondDataSupplier) => {
    cy.searchAndCheckPresence(userDefinedSupplierValue, true)
    checkTableValues(0, firstDataSupplier, userDefinedSupplierValue)
    checkTableValues(1, secondDataSupplier, userDefinedSupplierValue)
})

Then('The newly added data supplier should be displayed in the table with correct data', () => checkTableValues(0, selectedSupplierType, selectedSupplierValue))

Then('Both data suppliers are searched and correct data is displayed in the table', () => {
    selectedSupplierValues.forEach(val => {
        cy.searchAndCheckPresence(val, true)
        checkTableValues(0, selectedSupplierType, val)
    })
})

Then('The selected Data supplier value line is removed from the Supplier data type table', () => {
    cy.contains('.supplier-type-section', selectedSupplierType).contains('.v-input', userDefinedSupplierValue).should('not.exist')
})

Then('Both data suppliers should be displayed on the overview page', () => selectedSupplierValues.forEach(val => checkIfSupplierValueAvailable(selectedSupplierType, val)))

Then('The newly added data supplier should be displayed', () => checkIfSupplierValueAvailable(selectedSupplierType, selectedSupplierValue))

Then('The user defined supplier value should be added for {string}', (dataSupplierType) => checkIfSupplierValueAvailable(dataSupplierType, userDefinedSupplierValue))

Then('The removed data suppliers should not exist in the corresponding Supplier data type table', () => {
    cy.contains('.supplier-type-section', selectedSupplierType).contains('.mb-3', userDefinedSupplierValue).should('not.exist')
})

Then('The Add User Defined Data Supplier form is opened', () => cy.contains('.dialog-title', 'Add a new Data Supplier').should('be.visible'))

When('I fill in the Name', () => {
    selectedSupplierValue = `DS_${String(Date.now()).slice(-6)}`
    userDefinedSupplierValue = selectedSupplierValue
    cy.get('[data-cy="data-supplier-name"] input').type(selectedSupplierValue)
})

function checkIfSupplierValueAvailable(dataSupplierType, expectedValue) {
    cy.contains('.supplier-type-section', dataSupplierType).contains('.mb-3', expectedValue).should('be.visible')
}

function checkTableValues(rowIndex, expectedType, expectedValue) {
    cy.checkRowByIndex(rowIndex, 'Study data supplier type', expectedType)
    cy.checkRowByIndex(rowIndex, 'Data supplier name', expectedValue)
}
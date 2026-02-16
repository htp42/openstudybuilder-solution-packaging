import { getCurrStudyUid } from '../../support/helper_functions'

const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('The identifiers are set with following data', (dataTable) => {
    //null on all
    cy.nullRegistryIdentifiersForStudy(getCurrStudyUid())
    cy.waitForTable()
    cy.clickButton('edit-content')
    cy.wait(1000)
    cy.uncheckAllCheckboxes()
    dataTable.hashes().forEach(element => cy.fillInput(element.identifier, element.value))
})

When('The not applicable is checked for all identifiers', () => {
    //null on all
    cy.nullRegistryIdentifiersForStudy(getCurrStudyUid())
    cy.waitForTable()
    cy.clickButton('edit-content')
    cy.wait(1000)
    cy.checkAllCheckboxes()
})

Then('The identifiers table is showing following data', (dataTable) => {
    cy.waitForTableData()
    dataTable.hashes().forEach(element => cy.contains('table tbody tr td', element.identifier).next().contains(element.value))
})

Then('The identifiers table is showing following data in column Reason for missing', (dataTable) => {
    cy.waitForTableData()
    dataTable.hashes().forEach(element => cy.contains('table tbody tr td', element.identifier).next().next().contains(element.value, { matchCase: false }))
})

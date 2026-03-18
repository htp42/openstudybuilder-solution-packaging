const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");

let crfItemName, crfItemOid

When('User waits for CRF Items data to load', () => {
    cy.intercept('/api/concepts/odms/items?*').as('getData')
    cy.wait('@getData', { timeout: 90000 })
})

When('Created CRF Item is found', () => cy.searchAndCheckPresence(crfItemName, true))

Then('The CRF Item is no longer available', () => cy.searchAndCheckPresence(crfItemName, false))

Given('[API] The CRF Item in draft status exists', () => {
    crfItemName = `API_CrfItem${getShortUniqueId()}`
    cy.createCrfItem(crfItemName)
})

Then("The CRF Item is visible in the table", () => {
    cy.checkRowByIndex(0, 'OID', crfItemOid)
    cy.checkRowByIndex(0, 'Name',crfItemName)
})

When('The CRF Item definition container is filled with data and saved', () => {
    crfItemName = `CrfItem${getShortUniqueId()}`
    crfItemOid = `Oid${getShortUniqueId()}`
    cy.fillInput('item-oid', crfItemOid)
    cy.fillInput('item-name', crfItemName)
    cy.selectVSelect('item-data-type', 'INTEGER')
})

When('The CRF Item metadata are updated and saved', () => {
    crfItemName += 'Update'
    crfItemOid += 'Update'
    cy.fillInput('item-oid', crfItemOid)
    cy.fillInput('item-name', crfItemName)
})

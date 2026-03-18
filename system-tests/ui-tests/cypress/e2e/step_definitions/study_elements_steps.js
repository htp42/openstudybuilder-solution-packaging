const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");
import { getCurrStudyUid } from '../../support/helper_functions.js'

export let elementName

When('[API] Uids are fetched for element subtype {string}', (subtypeName) => cy.getElementTypeAndSubType(subtypeName))

When('[API] Element is created for the test study', () => {
    elementName = `El${getShortUniqueId()}`
    cy.addElementToStudy(Cypress.env('TEST_STUDY_UID'), elementName)
})

Given('[API] Element is created for the current study', () => {
    elementName = `El${getShortUniqueId()}`
    cy.addElementToStudy(getCurrStudyUid(), elementName)
})

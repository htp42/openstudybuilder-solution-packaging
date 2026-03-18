const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getCurrStudyUid } = require("../../support/helper_functions");
const { getShortUniqueId } = require("../../support/helper_functions");

let cohortName, cohortCode, cohortShortName
let cohortDescription  = 'E2E Test Cohort'

Given('[API] Get all Study Cohorts within selected study', () => cy.getCohortsUids(getCurrStudyUid()))

Given('[API] Delete all Study Cohorts within selected study', () => cy.deleteCohorts(getCurrStudyUid()))

When('The Study Cohort is found', () => cy.searchAndCheckPresence(cohortName, true))

Then('Add cohort button is clicked', () => cy.clickButton('add-study-cohort'))

When('First available study arm is selected', () => cy.selectFirstMultipleSelect('study-arm'))

When('The form for new study cohort is filled', () => {
    cohortName =  `Cohort${getShortUniqueId()}`
    cohortCode = Math.floor(Math.random() * 100);
    cohortShortName =  `C${cohortCode}`
    fillCohortData(cohortName, cohortShortName, cohortCode)
    cy.fillInput('study-cohort-description', cohortDescription)
})

Then('The study cohort is visible within the table', () => {
    cy.tableContains(cohortName)
    cy.tableContains(cohortCode)
    cy.tableContains(cohortShortName)
    cy.tableContains(cohortDescription)
})

When('The study cohort is edited', () => {
    cy.get('[data-cy="study-cohort-name"] input').should('have.value', cohortName)
    cohortName =  `Update ${cohortName}`
    cohortShortName =  `Update ${cohortShortName}`
    cohortDescription =  `Update ${cohortDescription}`
    fillCohortData(cohortName, cohortShortName, cohortCode)
    cy.fillInput('study-cohort-description', cohortDescription)
})

Then('The fields of Arm and Branch arms in the cohort edit form are active for editing', () => {
    cy.get('[data-cy="study-arm"]').should('not.have.attr', 'disabled')
    cy.get('[data-cy="branch-arm"]').should('not.have.attr', 'disabled')
})

Then('The validation appears under the field in the Study Cohorts form', (lessThan) => {
  cy.get('.v-messages__message').should('contain', "Value can't be less than 1")
})

When('Planned number of subjects for cohort is set as {string}', (example) => cy.fillInput('study-cohort-planned-number-of-subjects', example))

When('Cohort name is set as string with length {int}', (number) => cy.fillInput('study-cohort-name', "x".repeat(number)))

When('Cohort short name is set as string with length {int}', (number) => cy.fillInput('study-cohort-short-name', "x".repeat(number)))

When('The Study Branch field is not populated in the Study Cohorts form', () => {
  cy.get('[data-cy="branch-arm"]').clear({ force: true })
})

When('The Cohort name field is not populated', () => cy.clearField('study-cohort-name'))

When('The Cohort short name field is not populated', () => cy.clearField('study-cohort-short-name'))

When('The Cohort code field is not populated', () => cy.clearField('study-cohort-code'))

When('Another Study Cohort is created with the same cohort name', () => fillCohortData(cohortName, 'Test', '10'))

When('Another Study Cohort is created with the same cohort short name', () => fillCohortData('Test', cohortShortName, '10'))

When('Another Study Cohort is created with the same cohort code', () => fillCohortData('Test', 'Test', cohortCode))

Then('The validation appears for cohort code field {string}', (message) => {
  cy.get('.v-messages__message').should('contain', message)
})

When('Cohort code is set as {string}', (number) => cy.fillInput('study-cohort-code', parseInt(number)))

When('[API] The Study Cohort is created within selected study', () => cy.createCohort(getCurrStudyUid()))

function fillCohortData(name, shortName, code) {
  cy.fillInput('study-cohort-name', name)
  cy.fillInput('study-cohort-short-name', shortName)
  cy.fillInput('study-cohort-code', code)
}
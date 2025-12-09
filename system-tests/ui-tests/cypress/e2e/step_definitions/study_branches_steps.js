const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let branchName, branchShortName, randomisationGroup
let branchDescription  = 'E2E Test Branch'

When('The Study Branch is found', () => cy.searchAndCheckPresence(branchName, true))

When('The Study Branch is no longer available', () => cy.searchAndCheckPresence(branchName, false))

Given('A study without Study Arms has been selected', () => cy.selectTestStudy('Study_000004'))

Given('The first available arm is selected for the branch', () => cy.selectFirstVSelect('study-arm'))

Then('The option to create branch arm is not visible', () => cy.get('[data-cy="add-study-branch-arm"]').should('not.exist'))

When('Add branch button is clicked', () => cy.clickButton('add-study-branch-arm'))

When('The form for new study branch arm is filled', () => {
    branchName =  `Branch${Date.now()}`
    branchShortName = `B${Math.floor(Math.random() * 100)}`
    randomisationGroup = 'B'
    cy.selectFirstVSelect('study-arm')
    fillBranchData(branchName, branchShortName, randomisationGroup)
    cy.fillInput('study-branch-arm-description', branchDescription)
})

Then('The study branch arm is visible within the table', () => {
    cy.checkRowByIndex(0, 'Branch name', branchName)
    cy.checkRowByIndex(0, 'Short name', branchShortName)
    cy.checkRowByIndex(0, 'Random. Code', randomisationGroup)
    cy.checkRowByIndex(0, 'Random. group', randomisationGroup)
})

When('The study branch arm is edited', () => {
    branchName =  `Update ${branchName}`
    branchShortName =  `Update ${branchShortName}`
    randomisationGroup = 'U'
    branchDescription =  `Update ${branchDescription}`
    fillBranchData(branchName, branchShortName, randomisationGroup)
    cy.fillInput('study-branch-arm-description', branchDescription)
})

Then('The stady arm field is disabled', () => cy.get('[data-cy="study-arm"]').should('have.class', 'v-input--disabled'))

When('Planned number of subjects for branch is set as {string}', (example) => cy.fillInput('study-branch-arm-planned-number-of-subjects', example))

Then('The validation appears under the field in the Study Branch Arms form', (lessThan) => {
    cy.get('.v-messages__message').should('contain', "Value can't be less than 1")
})

When('The Study Arm field is not populated in the Study Branch Arms form', () => cy.clearInput('study-arm'))

When('The Branch name field is not populated', () => cy.clearInput('study-branch-arm-name'))

When('The Branch short name field is not populated', () => cy.clearInput('study-branch-arm-short-name'))

When('Another Study Branch Arm is created with the same arm name', () => fillBranchData(branchName, Date.now(), Date.now()))

When('Another Study Branch Arm is created with the same branch arm short name', () => fillBranchData(Date.now(), branchShortName, Date.now()))

When('For the Random. code a text longer than 20 characters is provided in the Study Branch Arms form', () => {
    cy.fillInput('study-branch-arm-randomisation-group', 'valtest')
    cy.fillInput('study-branch-arm-code', 'a'.repeat(21))
})

function fillBranchData(branchName, branchShortName, randomisationGroup) {
    cy.fillInput('study-branch-arm-name', branchName)
    cy.fillInput('study-branch-arm-short-name', branchShortName)
    cy.fillInput('study-branch-arm-randomisation-group', randomisationGroup)
}
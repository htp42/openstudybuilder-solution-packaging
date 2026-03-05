const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getCurrStudyUid, generateShortUniqueName } = require("../../support/helper_functions");

let armName, armLabel

When('The Study Arm is found', () => cy.searchAndCheckPresence(armName, true))

When('The Study Arm is no longer available', () => cy.searchAndCheckPresence(armName, false))

Given('[API] Uid of study type {string} is fetched', (studyType) => cy.getArmTypeUid(studyType))

Given('[API] The Study Arm exists within the study', () => cy.createTestArmIfNoneExists(Cypress.env('TEST_STUDY_UID')))

Given('[API] The Study Arm exists within selected study', () => cy.createTestArm(getCurrStudyUid()))

Given('[API] The Study Arm with name {string} exists within selected study', (customName) => cy.createTestArm(getCurrStudyUid(), customName))

Given('[API] The Study Arm is created', () => cy.createTestArm(Cypress.env('TEST_STUDY_UID')))

Given('[API] Get all Study Arms within selected study', () => cy.getArmsUids(getCurrStudyUid()))

Given('[API] Delete all Study Arms within selected study', () => cy.deleteArms(getCurrStudyUid()))

When('User saves and exits study structure stepper', () => cy.clickButton('save-close-stepper'))

When('User select manual study structure', () => cy.clickButton('manual-study'))

When('User continues to next step of study structure stepper', () => cy.clickButton('continue-stepper'))

When('User searches for created arm and it is found in the table', () => cy.searchAndCheckPresence(armName, true))

When('The Arm label is empty by default', () => cy.get('[data-cy="arm-label"] input').should('have.text', ''))

When('User provides the study arm label', () => cy.get('[data-cy="arm-label"] input').clear().type(armLabel = Date.now()))

Then('User provides the study arm label with {int} characters', (numberOfCharacters) => {
    cy.get('[data-cy="arm-label"] input').clear().type(armLabel = 'x'.repeat(numberOfCharacters))
})

When('The study arm label value is visible in the table', () => cy.checkRowByIndex(0, 'Arm label', armLabel))

When('The study arm label value is empty', () => cy.checkRowByIndex(0, 'Arm label', ''))

Then('The warning message about arm label exceeding 40 characters is displayed', () => cy.contains('[role="alert"]', 'This field must not exceed 40 characters').should('be.visible'))

When('User fills arm mandatory data', () => {
    armName = `${generateShortUniqueName('Arm')}`
    cy.selectVSelect('arm-type', 'Placebo Arm')
    cy.fillInput('arm-name', armName)
    cy.fillInput('arm-short-name', `${armName.split(2, 6)}`)
})

When('User intercepts and wait for the design class request', () => {
    cy.intercept('**/study-design-classes').as('designClass')
    cy.wait('@designClass').then((req) => expect(req.response.statusCode).to.eq(200))
})

When('The new study arm form is filled and saved', () => {
    cy.clickButton('manual-study')
    cy.clickButton('continue-stepper')
    cy.selectVSelect('arm-type', 'Placebo Arm')
    cy.fillInput('arm-name', 'Test Placebo Arm')
    cy.fillInput('arm-short-name', 'PArm')
    cy.fillInput('randomization-group', 'RA')
    cy.fillInput('arm-code', 'A')
    cy.fillInput('arm-description', 'Test Arm A')
    cy.clickButton('arm-push')

    cy.get('[data-cy="arm-type"]').eq(1).click()
    cy.get('.v-list')
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.get('.v-list-item').first().click())
    cy.get('[data-cy="arm-name"]').eq(1).type('Test Arm Two')
    cy.get('[data-cy="arm-short-name"]').eq(1).type('CArm')
    cy.get('[data-cy="randomization-group"]').eq(1).type('RB')
    cy.get('[data-cy="arm-code"]').eq(1).type('B')
    cy.get('[data-cy="arm-description"]').eq(1).type('Test Arm B')
    cy.clickButton('arm-push')
    cy.get('[data-cy="arm-type"]').eq(2).click()
    cy.get('.v-list')
        .filter(':visible')
        .should('not.contain', 'No data available')
        .within(() => cy.get('.v-list-item').last().click())
    cy.get('[data-cy="arm-name"]').eq(2).type('Test Arm Three')
    cy.get('[data-cy="arm-short-name"]').eq(2).type('CArmX')
    cy.get('[data-cy="randomization-group"]').eq(2).type('RBX')
    cy.get('[data-cy="arm-code"]').eq(2).type('BX')
    cy.get('[data-cy="arm-description"]').eq(2).type('Test Arm BX')
    cy.clickButton('save-close-stepper')
    cy.wait(2000)

})

Then('The new study arm is visible within the study arms table', () => {
    cy.tableContains('Test Placebo Arm')
    cy.tableContains('PArm')
    cy.tableContains('RA')
    cy.tableContains('Test Arm A')
    cy.tableContains('Test Arm Two')
    cy.tableContains('CArm')
    cy.tableContains('RB')
    cy.tableContains('Test Arm B')
})

When('The arm data is edited and saved', () => {
    cy.get('[data-cy="arm-name"]').eq(0).clear().type('Test Arm Two 2')
    cy.get('[data-cy="arm-short-name"]').eq(0).clear().type('CArm2')
    cy.get('[data-cy="randomization-group"]').eq(0).clear().type('RB2')
    cy.get('[data-cy="arm-code"]').eq(0).clear().type('B2')
    cy.get('[data-cy="arm-description"]').eq(0).clear().type('Test Arm B2')

    cy.get('[data-cy="arm-name"]').eq(1).clear().type('Test Arm Two 1')
    cy.get('[data-cy="arm-short-name"]').eq(1).clear().type('BArm1')
    cy.get('[data-cy="randomization-group"]').eq(1).clear().type('RA1')
    cy.get('[data-cy="arm-code"]').eq(1).clear().type('A1')
    cy.get('[data-cy="arm-description"]').eq(1).clear().type('Test Arm A1')
    cy.clickButton('save-close-stepper')
    cy.wait(2000)
})

Then('The study arm with updated values is visible within the study arms table', () => {
    cy.tableContains('Test Arm Two 2')
    cy.tableContains('CArm2')
    cy.tableContains('RB2')
    cy.tableContains('B2')
    cy.tableContains('Test Arm B2')
    cy.tableContains('Test Arm Two 1')
    cy.tableContains('BArm1')
    cy.tableContains('A1')
})

When('The Randomisation Group is populated in the Add New Arm form', () => {
    cy.clickButton('add-study-arm')
    cy.fillInput('arm-randomisation-group', 'testOfValue')
})

When('no value is specified for the field Arm Code', () => {
    cy.get('[data-cy="arm-code"]').click({ force: true })
})

Then('The Arm code field is populated with value from Randomisation group field', () => {
    cy.get('[data-cy="arm-code"]').within(() => {
        cy.get('.v-field__input').should('have.attr', 'value', 'testOfValue')
    })
})

When('The value {string} is entered for the field Number of subjects in the Study Arms form', (value) => {
    cy.get('[data-cy="number-of-subjects"] input').eq(0).clear().type(value)
    cy.clickButton('save-close-stepper')
})

When('The study arm type, arm name and arm short name is not populated', () => {
    cy.get('[data-cy="arm-name"]').clear()
    cy.get('[aria-label="Clear Study arm type"]').eq(0).click()
    cy.get('[data-cy="arm-short-name"]').clear()
})

Then('The required field validation appears for the {string} empty fields', (count) => {
    cy.get('.v-messages__message').should('contain', 'This field is required').and('have.length', count)
})

When('The two study arms are defined with the same name', () => {
    cy.get('[data-cy="arm-name"]').eq(0).clear().type('UV1')
    cy.get('[data-cy="arm-name"]').eq(1).clear().type('UV1')
    cy.clickButton('save-close-stepper')
})

When('The two study arms are defined with the same short name', () => {
    cy.get('[data-cy="arm-short-name"]').eq(0).clear().type('UV2')
    cy.get('[data-cy="arm-short-name"]').eq(1).clear().type('UV2')
    cy.clickButton('save-close-stepper')
})

When('The two study arms are defined with the same randomisation group', () => {
    cy.get('[data-cy="randomization-group"]').eq(0).clear().type('UV3')
    cy.get('[data-cy="randomization-group"]').eq(1).clear().type('UV3')
    cy.clickButton('save-close-stepper')
})

When('The study arm code is updated to exceed 20 characters', () => {
    cy.get('[data-cy="arm-code"] input').eq(0).clear().type('a'.repeat(21), { delay: 0.1, force: true })
})

Then('The system displays the message {string}', (message) => {
    cy.checkSnackbarMessage(message)
})

Then('The message {string} is displayed', (message) => {
    cy.contains(message).should('exist')
})

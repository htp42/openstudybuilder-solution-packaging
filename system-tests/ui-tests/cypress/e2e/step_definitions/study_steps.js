const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let study_uid, studyNumber, studyAcronym

Given('A test study is selected', () => {
    cy.selectTestStudy(Cypress.env('TEST_STUDY_UID'))
})

Given('A {string} study is selected', (study_id) => {
    cy.selectStudyByStudyId(study_id)
})

Given('Get study {string} uid', (studyId) => cy.getStudyUidById(studyId).then(uid => study_uid = uid))

Given('Select study with uid saved in previous step', () => cy.selectTestStudy(study_uid))

When('The page {string} is opened for selected study', (page) => {
    cy.visit(`/studies/${study_uid}/${page}`)
    cy.waitForPage()
})

When('A new study is added', () => {
    studyAcronym = `AutomationTestStudy${Date.now()}`
    studyNumber = `${Math.floor(1000 + Math.random() * 9000)}`
    cy.waitForTable()
    cy.clickButton('add-study')
    cy.selectAutoComplete('project-id', 'CDISC DEV')
    cy.fillInput('study-number', studyNumber)
    cy.fillInput('study-acronym', studyAcronym)
    cy.clickButton('save-button')
    cy.wait(2500)
    cy.waitForTable()
})

Then('The study is visible within the table', () => {
    cy.checkRowByIndex(0, 'Study acronym', studyAcronym)
    cy.checkRowByIndex(0, 'Study number', studyNumber)
    cy.checkRowByIndex(0, 'Project ID', 'CDISC DEV')
})

When('Study is found', () => cy.searchAndCheckPresence(studyAcronym, true))

When('[API] Study uid is fetched', () => cy.getStudyUid(studyNumber).then(id => study_uid = id))

When('Go to created study', () => {
    cy.visit(`/studies/${study_uid}/activities/soa`)
    cy.waitForPage()
})

When('Go to {string} study page {string}', (studyNumber, page) => {
    cy.getStudyUidById(studyNumber).then(id => cy.visit(`/studies/${id}/${page}`))
    cy.waitForPage()
})
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let study_uid

Then('The current URL is {string}', (url) => cy.url().should('contain', url))

Given('The test study {string} page is opened', (url) => {
    let test_study_uid = Cypress.env('TEST_STUDY_UID')
    cy.visit(`studies/${test_study_uid}${url}`)
    cy.waitForPage()
})

When('The page {string} is opened for selected study', (page) => {
    cy.visit(`/studies/${study_uid}/${page}`)
    cy.waitForPage()
})

Given('The {string} page is opened', (url) => {
    cy.visit(url)
    cy.waitForPage()
})

Given('The homepage is opened', () => cy.visit('/'))

Given('The studies page is opened', () => cy.visit('/studies'))

Given('The page is reloaded', () => cy.reload())

Given('A test study is selected', () => cy.selectTestStudy(Cypress.env('TEST_STUDY_UID')))

Given('Select study with uid saved in previous step', () => cy.selectTestStudy(study_uid))

Given('Get study {string} uid', (studyId) => cy.getStudyUidById(studyId).then(uid => study_uid = uid))

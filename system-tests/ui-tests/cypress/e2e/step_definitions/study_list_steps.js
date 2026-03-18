const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");

let study_uid, studyNumber, studyAcronym

Given('The user selects to create study from existing study', () => cy.contains('Create a study from an existing study').click())

Given('The Add Study button is clicked', () => cy.clickButton('add-study'))

Given('The user intercepts study statistics request', () => cy.intercept('**structure-statistics').as('study_statistics'))

When('User intercepts cloning request', () => cy.intercept('**clone').as('clone_request'))

When('User waits for cloning request', () => cy.wait('@clone_request'))

Then('The user is presented study selection dropdown', () => {
    cy.contains('.dialog-title', 'Which study do you want to copy from?').should('exist')
    cy.get('.v-label').should('contain', 'Study ID')
    cy.get('.v-label').should('contain', 'Study acronym')
})

When('The user selects study to use for copy', () => {
    cy.get('.v-stepper-window-item .v-input').filter(':visible').eq(0).find('input').type('CDISC DEV-9866')
    cy.contains('.v-list-item__content', 'CDISC DEV-9866').click()
})

Then('The user is presented with visual representation of designated study structure', () => {
    cy.get('.dialog-sub-title').should('contain', 'Preview of study')
    
    cy.get('.arm').eq(0).should('have.attr', 'transform', 'translate(5, 36)').and('contain', 'Arm1')
    cy.get('.arm').eq(1).should('have.attr', 'transform', 'translate(5, 71)').and('contain', 'Arm2')
    cy.get('.arm').eq(2).should('have.attr', 'transform', 'translate(5, 106)').and('contain', 'Arm3')

    cy.get('.epoch').eq(0).should('have.attr', 'transform', 'translate(198, 5)').and('contain', 'Run-in')
    cy.get('.epoch').eq(1).should('have.attr', 'transform', 'translate(403, 5)').and('contain', 'Intervention')

    cy.get('.visit-type').eq(0).should('have.attr', 'transform', 'translate(198, 153)').and('contain', 'Pre-screening')
    cy.get('.visit-type').eq(1).should('have.attr', 'transform', 'translate(403, 153)').and('contain', 'Randomisation')

    cy.get('.visit-timing').eq(0).should('have.attr', 'transform', 'translate(198, 195)').and('contain', '0 days')
    cy.get('.visit-timing').eq(1).should('have.attr', 'transform', 'translate(403, 195)').and('contain', '14 days')

    cy.get('line.timeline-arrow').should('have.length', 2);
    cy.get('line.visit-arrow').should('have.length', 2);
})

When('The user selects {string} category to be copied', (category) => cy.contains('label', category).click())

Then('The {string} category with {string} derived from source study is presented for selection', (category, count) => {
    cy.get('@study_statistics').then((request) => {
        let statistic = request.response.body[count]
        cy.contains('label', category).should('have.text', `${category} (${statistic})`)
    })
    
})

Then('The {string} option is visible under {string} category showing appropiate {string} number', (option, category, count) => {
    cy.get('@study_statistics').then((request) => {
        let statistic = request.response.body[count]
        cy.contains('.pa-0', category).within(() => cy.contains(`${option} (${statistic})`).should('be.visible'))
   })
})

Then('The Design matrix category is presented for selection', () => cy.contains('label', 'Design matrix').should('exist'))

When('New study project id, study number and study acronym are filled in', () => {
    studyAcronym = `AutomationTestStudy${getShortUniqueId()}`
    studyNumber = `${Math.floor(1000 + Math.random() * 9000)}`
    cy.selectAutoComplete('project-id', 'CDISC DEV')
    cy.fillInput('study-number', studyNumber)
    cy.fillInput('study-acronym', studyAcronym)
})

When('The user selects study project and uses existing study number', () => {
    cy.selectAutoComplete('project-id', 'CDISC DEV')
    cy.fillInput('study-number', '9876')
    cy.fillInput('study-acronym', 'test')
})

Then('The study is visible within the table', () => {
    cy.checkRowByIndex(0, 'Study acronym', studyAcronym)
    cy.checkRowByIndex(0, 'Study number', studyNumber)
    cy.checkRowByIndex(0, 'Project ID', 'CDISC DEV')
})

When('Study is found', () => cy.searchAndCheckPresence(studyAcronym, true))

Then('The new study is created with selected data', () => {
    cy.get('@clone_request').then((req) => {
        expect(req.request.body.copy_study_arm).to.eq(true)
        expect(req.request.body.copy_study_arm).to.eq(true)
        expect(req.request.body.copy_study_branch_arm).to.eq(true)
        expect(req.request.body.copy_study_cohort).to.eq(true)
        expect(req.request.body.copy_study_design_matrix).to.eq(true)
        expect(req.request.body.copy_study_element).to.eq(true)
        expect(req.request.body.copy_study_epoch).to.eq(true)
        expect(req.request.body.copy_study_visit).to.eq(true)
        expect(req.request.body.project_number).to.eq('CDISC DEV')
        expect(req.request.body.study_acronym).to.eq(studyAcronym)
        expect(req.request.body.study_number).to.eq(studyNumber)
        expect(req.response.statusCode).to.eq(201)
    })
})

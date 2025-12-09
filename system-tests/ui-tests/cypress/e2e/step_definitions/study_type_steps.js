const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
import { stringToBoolean } from '../../support/helper_functions'

let studyType = 'Expanded Access', trialType = 'Adhesion Performance Study', phaseClassification = 'Phase 0 Trial'
let extensionStudy = 'Yes', adaptiveDesign = 'Yes', postAuthSafetyIndicator = 'Yes'
let confirmedResponseMinValue = '50', confirmedResponseUnit = 'days', stopRules = 'Test stop rule'

When('The study type is fully defined', () => {
    cy.nullStudyType(Cypress.env('TEST_STUDY_UID'))
    cy.wait(5000)
    cy.reload()
    cy.wait(3000)
    startEdition()
    cy.selectAutoComplete('study-type', studyType)
    cy.selectMultipleSelect('trial-type', trialType)
    cy.selectAutoComplete('study-phase-classification', phaseClassification)
    cy.selectRadio('extension-study', extensionStudy)
    cy.selectRadio('adaptive-design', adaptiveDesign)
    cy.contains('.v-checkbox', 'NONE').find('input').uncheck()
    cy.fillInput('stop-rule', stopRules)
    cy.setDuratinField('confirmed-resp-min-dur',confirmedResponseMinValue, confirmedResponseUnit)
    cy.selectRadio('post-auth-safety-indicator', postAuthSafetyIndicator)
})

Then('The study type data is reflected in the table', () => {
    cy.tableContains(studyType)
    cy.tableContains(trialType)
    cy.tableContains('Phase 0 Trial')
    cy.tableContains(stopRules)
    cy.tableContains(postAuthSafetyIndicator)
})

When('The Study Stop Rule NONE option is selected', () => {
    cy.nullStudyType(Cypress.env('TEST_STUDY_UID'))
    cy.wait(1000)
    cy.reload()
    cy.wait(1000)
    startEdition()
})

Then('The Study Stop Rule field is disabled', () => cy.get('[data-cy="stop-rule"] input').should('be.disabled'))

When('The Confirmed response minimum duration NA option is selected', () => {
    cy.nullStudyType(Cypress.env('TEST_STUDY_UID'))
    cy.wait(5000)
    cy.reload()
    startEdition()
    cy.get('[data-cy="not-applicable-checkbox"] input').check()
})

Then('The Confirmed response minimum duration field is disabled', () => {
    cy.get('[data-cy="duration-value"] input').should('be.disabled')
    cy.get('[data-cy="duration-unit"] input').should('be.disabled')
})

When('The study type is partially defined', () => {
    cy.nullStudyType(Cypress.env('TEST_STUDY_UID'))
    cy.wait(5000)
    cy.reload()
    startEdition()
    cy.selectAutoComplete('study-type', studyType)
    cy.setDuratinField('confirmed-resp-min-dur', confirmedResponseMinValue, confirmedResponseUnit)
    cy.selectRadio('post-auth-safety-indicator', type.post_auth_safety_indicator)
})

When('The study type is copied from another study without overwriting', () => {
    cy.clickButton('copy-from-study')
    cy.selectVSelect('study-id', 'CDISC DEV-1234')
    cy.clickButton('overwrite-no', true)
    cy.clickButton('ok-form')
    cy.clickButton('save-button')
    cy.wait(2000)
})

Then('Only the missing information is filled from another study in the study type form', () => {
    cy.get('@copyData').then(request => {
        cy.tableContains(studyType)
        if (request.body.current_metadata.high_level_study_design.trial_type_codes[0] !== undefined) {
            cy.tableContains(request.body.current_metadata.high_level_study_design.trial_type_codes[0].name);
        }
        cy.tableContains(stringToBoolean(request.body.current_metadata.high_level_study_design.is_extension_trial))
        cy.tableContains(stringToBoolean(request.body.current_metadata.high_level_study_design.is_adaptive_design))
        cy.tableContains(request.body.current_metadata.high_level_study_design.study_stop_rules)
    })
})

When('The study type is copied from another study with overwriting', () => {
    cy.clickButton('copy-from-study')
    cy.selectVSelect('study-id', 'CDISC DEV-1234')
    cy.clickButton('overwrite-yes', true)
    cy.clickButton('ok-form')
    cy.clickButton('save-button')
    cy.wait(2000)
})

Then('All the informations are overwritten in the study type', () => {
    cy.get('@copyData').then(request => {
        if (request.body.current_metadata.high_level_study_design.trial_type_codes[0] !== undefined) {
            cy.tableContains(request.body.current_metadata.high_level_study_design.trial_type_codes[0].name);
          }
        cy.tableContains(stringToBoolean(request.body.current_metadata.high_level_study_design.is_extension_trial))
        cy.tableContains(stringToBoolean(request.body.current_metadata.high_level_study_design.is_adaptive_design))
        cy.tableContains(request.body.current_metadata.high_level_study_design.study_stop_rules)
    })
})

function startEdition() {
    cy.clickButton('edit-content')
    cy.wait(1000)
}
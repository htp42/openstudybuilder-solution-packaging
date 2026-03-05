const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let intervetionType = 'Gene Therapy', studyIntentType = 'Cure', controlType = 'Active', intervetionModel = 'Crossover'
let isRandomised = 'Yes', addOnExistingTreatments = 'Yes', stratificationFactor = 'Test stratification factor', studyBindingSchema = 'Open Label'


When('The study intervention type is edited', () => {
    cy.wait(1000)
    cy.selectAutoComplete('Intervention type', intervetionType)
    cy.wait(1000)
    cy.selectMultipleSelect('Study intent type', studyIntentType)
    cy.selectAutoComplete('Control type', controlType)
    cy.selectAutoComplete('Intervention model', intervetionModel)
    cy.selectRadioButton('Study is randomised', isRandomised)
    cy.selectRadioButton('Add-on to existing treatments', addOnExistingTreatments)
    cy.selectAutoComplete('Study blinding schema', studyBindingSchema)
    cy.fillInput('Stratification factor', stratificationFactor)
    cy.setDuration('planned-study-length', '5', 'days')
})

Then('The study intervention type data is reflected in the table', () => {
    cy.tableContains(intervetionType)
    cy.tableContains(studyIntentType)
    cy.tableContains(addOnExistingTreatments)
    cy.tableContains(controlType)
    cy.tableContains(intervetionModel)
    cy.tableContains(isRandomised)
    cy.tableContains(stratificationFactor)
    cy.tableContains(studyBindingSchema)
})
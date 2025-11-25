const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");


let activityName, apiRequestedActivityName
let rationaleforrequest = "RFR", abbreviation = "ABB", definition = "DEF"

When('The Add activity request button is clicked', () => cy.clickButton('add-activity'))

Then('The add activity request button is not available', () => cy.get('add-activity').should('not.exist'))

When('The activity request container is filled with data and saved', () => addActivity())

When('The activity request form is filled with data', () => addActivity(false))

When('The requested activity edition form is filled with data', () => editActivity(false))

Then('The newly added activity request is visible in the the table', () => {  
    cy.searchAndCheckPresence(activityName, true)
    cy.checkRowByIndex(0, 'Activity', activityName)
    cy.checkRowByIndex(0, 'Sentence case name', activityName.toLowerCase())
    cy.checkRowByIndex(0, 'Abbreviation', abbreviation)
    cy.checkRowByIndex(0, 'Definition', definition)
    cy.checkRowByIndex(0, 'Rationale for activity request', rationaleforrequest)
})

When('The Activity group, Activity name, Sentence case name and Rationale for activity request fields are not filled with data', () => {
    cy.clickButton('save-button')
})

Then('The user is not able to save the acitivity request', () => {   
    cy.get('div[data-cy="form-body"]').should('be.visible');          
    cy.get('span.dialog-title').should('be.visible').should('contain', 'Add activity request'); 
})

Then('The validation message appears for requested activity group', () => cy.checkIfValidationAppears('requestedform-activity-group-class'))

Then('The validation message appears for requested activity name', () => cy.checkIfValidationAppears('requestedform-activity-name-class'))

Then('The validation message appears for requested activity rationale', () => cy.checkIfValidationAppears('requestedform-rationale-for-request-class'))

Then('The validation message appears for sentance case name', () => cy.checkIfValidationAppears('sentence-case-name-field'))

Then('The validation message appears for requested activity subgroup', () => cy.checkIfValidationAppears('requestedform-activity-subgroup-class'))

Then('The validation message does not appear for sentance case name', () => cy.checkIfValidationNotPresent('sentence-case-name-field'))

Then('The validation message does not appear for requested activity abbreviation', () => cy.checkIfValidationNotPresent('requestedform-abbreviation-field'))

Then('The validation message does not appear for requested activity definition', () => cy.checkIfValidationNotPresent('requestedform-definition-field'))


When('Input a value for Activity group field, but not for Activity subgroup field', () => {
    cy.clickButton('add-activity')
    cy.selectFirstVSelect('requestedform-activity-group-dropdown')
    cy.clickButton('save-button')
})

When('The user input a value for Activity name {string}', (name) => cy.fillInput('requestedform-activity-name-field', name))

When('The user clear default value from Sentance case name', () => cy.clearInput('sentence-case-name-field'))

When('The value for Sentence case name independent of case is not identical to the value of Activity name', () => {
    cy.fillInput('requestedform-activity-name-field', "TEST")
    cy.fillInput('sentence-case-name-field', "TEST2")
    cy.clickButton('save-button')
})

When('The activity request is edited', () => editActivity())

Then('The requested activity is no longer available', () => cy.searchAndCheckPresence(apiRequestedActivityName, false))

Then('The requested activity is not created', () => {
    cy.waitForTable()
    cy.searchAndCheckPresence(activityName, false)
})

Then('The requested activity is not edited', () => cy.searchAndCheckPresence(activityName, false))

Then('One activity request is found after performing full name search', () => cy.searchAndCheckPresence(apiRequestedActivityName, true))

Then('Requested activity is found', () => cy.searchAndCheckPresence(apiRequestedActivityName, true))

When('[API] Requested activity in status Draft exists', () => createRequestedActivityViaApi())

When('[API] Requested activity is approved', () => cy.approveRequestedActivity())

When('[API] Requested activity is inactivated', () => cy.inactivateRequestedActivity())

Given('[API] First requested activity for search test is created', () => createRequestedActivityViaApi(`SearchTest${Date.now()}`))

Given('[API] Second requested activity for search test is created', () => cy.createRequestedActivity(`SearchTest${Date.now()}`))

function addActivity(save = true, namePrefix ='Requested') {
    activityName = `${namePrefix}${Date.now()}`
    cy.clickButton('add-activity')
    cy.selectFirstVSelect('requestedform-activity-group-dropdown')
    cy.selectFirstVSelect('requestedform-activity-subgroup-dropdown')
    cy.fillInput('requestedform-activity-name-field', activityName)
    cy.fillInput('requestedform-abbreviation-field', abbreviation)
    cy.fillInput('requestedform-definition-field', definition)
    cy.fillInput('requestedform-rationale-for-request-field', rationaleforrequest)
    if (save) {
        cy.intercept('/api/concepts/activities/activities?page_number=1&page_size=0&*').as('getData')
        cy.clickButton('save-button')
        cy.checkSnackbarMessage('Activity created')
        cy.wait('@getData', {timeout: 20000})
    }
}

function editActivity(save = true) {
    activityName = `Update${apiRequestedActivityName}`
    cy.fillInput('requestedform-activity-name-field', activityName)
    cy.fillInput('requestedform-change-description-field', "e2e test")
    if (save) cy.clickButton('save-button')
}

function createRequestedActivityViaApi(customName = '') {
    cy.intercept('/api/concepts/activities/activities?page_number=1&*').as('getData')
    cy.getFinalGroupUid()
    cy.getFinalSubGroupUid()
    cy.createRequestedActivity(customName)
    cy.getRequestedActivityNameByUid().then(name => apiRequestedActivityName = name)
    cy.wait('@getData', {timeout: 20000})
}
import { activityName } from "./library_activities_steps";
import { activity_uid, subgroup_uid, group_uid, group_name } from "../../support/api_requests/library_activities";
import { getCurrentStudyId } from "./../../support/helper_functions";
const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");

export let activity_activity, current_activity_uid
let activity_placeholder_name, activity_library, activity_soa_group, activity_group, activity_sub_group, edit_placeholder_name, current_study, new_activity_name

When('Study activity add button is clicked', () => cy.clickButton('add-study-activity'))

Then('The Study Activity is found', () => cy.searchAndCheckPresence(activity_activity, true))

When('Activity placeholder is found', () => cy.searchAndCheckPresence(activity_placeholder_name, true))

Then('The Study Activity Placeholder is no longer available', () => cy.searchAndCheckPresence(activity_placeholder_name, false))

When('Activity placeholder is searched for', () => cy.searchForInPopUp(activity_placeholder_name))

Given('Study activities for selected study are loaded', () => {
    cy.intercept(`/api/studies/${Cypress.env('TEST_STUDY_UID')}/study-activities?*`).as('getData')
    cy.wait('@getData', { timeout: 30000 })
})

Given('The activity exists in the library', () => {
    cy.log('Handled by import script')
})

When('User tries to add Activity in Draft status', () => {
    cy.searchForInPopUp(activityName)
    cy.waitForTable()
})

When('User search and select activity created via API', () => addLibraryActivityByName())

When('User selects first available activity', () => selectActivityAndGetItsData())

When('User selects first available activity and SoA group', () => selectActivityAndGetItsData('INFORMED CONSENT'))

When('Study with id value {string} is selected', (value) => cy.selectVSelect('select-study-for-activity-by-id', value))

When('Study with acronym value {string} is selected', (value) => cy.selectVSelect('select-study-for-activity-by-acronym', value))

Then('The Study Activity is visible in table', () => checkIfTableContainsActivity())

Then('The Activity in Draft status is not found', () => cy.contains('.v-sheet table tbody tr', 'No data available'))

When('Activity placeholder data is filled in', () => fillPlaceholderData())

When('Selected study id is saved', () => current_study = getCurrentStudyId())

When('Data collection flag is unchecked', () => cy.get('input[aria-label="Data collection"]').uncheck())

When('Data collection flag is checked', () => cy.get('input[aria-label="Data collection"]').check())

Then('The Study Activity placeholder is visible within the Study Activities table', () => {
    cy.tableContains('Requested')
    cy.tableContains('INFORMED CONSENT')
    cy.tableContains('General')
    cy.tableContains(activity_placeholder_name)
})

Then('The edited Study Activity data is reflected within the Study Activity table', () => cy.tableContains('EFFICACY'))

When('Activity from studies is selected', () => cy.get('[data-cy="select-from-studies"] input').check())

When('Activity from library is selected', () => cy.get('[data-cy="select-from-library"] input').check({ force: true }))

When('Activity from placeholder is selected', () => cy.get('[data-cy="create-placeholder"] input').check())

When('Study by id is selected', () => cy.selectVSelect('select-study-for-activity-by-id', current_study))

Then('The validation appears and Create Activity form stays on Study Selection', () => {
    cy.elementContain('select-study-for-activity-by-acronym', 'This field is required')
    cy.elementContain('select-study-for-activity-by-id', 'This field is required')
})

When('The user tries to go further without SoA group chosen', () => {
    cy.get('.v-data-table__td--select-row input').not('[aria-disabled="true"]').eq(0).check()
})

When('The user tries to go further in activity placeholder creation without SoA group chosen', () => {
    cy.contains('.choice .text', 'Create a placeholder activity without submitting for approval').click()
    cy.fillInput('instance-name', `Placeholder Instance Name ${Date.now()}`)
    cy.fillInput('activity-rationale', 'Placeholder Test Rationale')
})

Then('The validation appears and Create Activity form stays on SoA group selection', () => {
    cy.get('.v-alert').should('contain', 'Every selected Activity needs SoA Group')
    cy.get('[data-cy="flowchart-group"]').should('be.visible')
})

Then('The validation appears under empty SoA group selection', () => {
    cy.get('[data-cy="flowchart-group"]').find('.v-messages').should('contain', 'This field is required')
})

Then('The SoA group can be changed', () => {
    cy.wait(1000)
    cy.selectAutoComplete('flowchart-group', 'EFFICACY')
})

Then('The study activity table is displaying updated value for data collection', () => {
    cy.getCellValue(0, 'Data collection').then(value => cy.wrap(value).should('equal', 'Yes'))
})

Then('Warning that {string} {string} can not be added to the study is displayed', (status, item) => {
    cy.get('.v-alert').should('contain', `has status ${status}. Only Final ${item} can be added to a study.`)
})

When('The existing activity request is selected', () => cy.get('[data-cy="select-activity"] input').check())

When('The study activity request is edited', () => {
    edit_placeholder_name = `Edit name ${Date.now()}`
    cy.fillInput('instance-name', edit_placeholder_name)
})

When('The study activity request SoA group field is edited', () => {
    cy.get('[data-cy="flowchart-group"]').click()
    cy.contains('.v-list-item', 'HIDDEN').click()
})

When('The study activity request data collection field is edited', () => {
    cy.get('[aria-label="Data collection"]').click()
})

When('The study activity request rationale for activity field is edited', () => {
    cy.fillInput('activity-rationale', "TEST OF UPDATE REDBELL")
})

Then('The updated notification icon and update option are not present', () => {
    cy.get('.v-badge__badge').should('not.exist')
})

When('The user is presented with the changes to request', () => {
    cy.get('[data-cy="form-body"]').should('contain', edit_placeholder_name)
})

Then('The activity request changes are applied', () => {
    cy.searchAndCheckPresence(edit_placeholder_name, true)
    cy.searchAndCheckPresence(activity_placeholder_name, false)
})

Then('The activity request changes not applied', () => {
    cy.searchAndCheckPresence(activity_placeholder_name, true)
})

Then('The activity request is removed from the study', () => {
    cy.searchAndCheckPresence(edit_placeholder_name, false)
    cy.searchAndCheckPresence(activity_placeholder_name, false)
})

Then('[API] All Activities are deleted from study', () => {
    cy.getExistingStudyActivities(Cypress.env('TEST_STUDY_UID')).then(uids => uids.forEach(uid => cy.deleteActivityFromStudy(Cypress.env('TEST_STUDY_UID'), uid)))
})

Then('[API] Get SoA Group {string} id', (name) => cy.getSoaGroupUid(name))

Then('[API] Activity is added to the study', () => {
    cy.addActivityToStudy(Cypress.env('TEST_STUDY_UID'), activity_uid, group_uid, subgroup_uid).then((response) => {
        activity_activity = response.body[0].content.activity.name
        current_activity_uid = response.body[0].content.activity.uid
    })
})

When('The activity has been retired', () => {
    cy.inactivateActivity(current_activity_uid)
})

Then('[API] Activity with two subgroups available is added to the study', () => {
    cy.createGroup()
    cy.approveGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.addActivityToStudy(Cypress.env('TEST_STUDY_UID'), activity_uid, group_uid, subgroup_uid).then((response) => {
        activity_activity = response.body[0].content.activity.name
        current_activity_uid = response.body[0].content.activity.uid
    })
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
    cy.createSubGroup()
    cy.approveSubGroup()
})

When('The activity group is updated for that study activity', () => {
    cy.activityNewVersion(current_activity_uid)
    cy.visit(`library/activities/activities/${current_activity_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.selectFirstVSelect('activityform-activity-group-dropdown')
    cy.selectFirstVSelect('activityform-activity-subgroup-dropdown')
    cy.clickButton('save-button')
})

When('The activity subgroup is updated for that study activity', () => {
    cy.activityNewVersion(current_activity_uid)
    cy.visit(`library/activities/activities/${current_activity_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.selectLastVSelect('activityform-activity-subgroup-dropdown')
    cy.clickButton('save-button')
})

When('The activity name is updated for that study activity', () => {
    cy.activityNewVersion(current_activity_uid)
    cy.visit(`library/activities/activities/${current_activity_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.fillInput('activityform-activity-name-field', new_activity_name = `NewName${Date.now()}`)
    cy.clickButton('save-button')
})

When('The user accepts the changes', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update activity version')
    cy.contains('button', 'Accept').click()
    activity_activity = new_activity_name
})

When('The user declines the changes', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update activity version')
    cy.contains('button', 'Decline').click()
})

When('The user opens bulk review changes window', () => {
    cy.contains('Review activity updates').click()
})

Then('The changes are applied in the study activity', () => {
    cy.tableContains(activity_activity)
})

When('The user filters the table by red alert status', () => {
    cy.get('[value="updated"]').click()
})

When('The user filters the table by yellow alert status', () => {
    cy.get('[value="reviewed"]').click()
})

Then('The activities with red alert are present', () => {
    cy.waitForTable()
    cy.get('tbody').within(() => {
        cy.get('tr').each($row => {
            cy.wrap($row).within(() => {
                cy.get('.mdi-alert-circle-outline').should('exist')
            })
        })
    })
})

Then('The activities with yellow alert are present', () => {
    cy.waitForTable()
    cy.get('tbody').within(() => {
        cy.get('tr').each($row => {
            cy.wrap($row).within(() => {
                cy.get('.mdi-alert-outline').should('exist')
            })
        })
    })
})

Then('The icon indicates which activity group is present in detailed soa', () => {
    cy.get('[data-cy="form-body"]').within(() => {
        cy.contains('.v-data-table__td', group_name).within(() => {
            cy.get('.mdi-eye-outline').should('exist')
        })
    })
})

Then('The icon indicates which activity name is present in detailed soa', () => {
    cy.get('[data-cy="form-body"]').within(() => {
        cy.contains('.v-data-table__td', new_activity_name).within(() => {
            cy.get('.mdi-eye-outline').should('exist')
        })
    })
})

When('The user opens changes review window for that activity', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update activity version')
})

When('The activity group is removed from that activity', () => {
    cy.visit(`library/activities/activities/${current_activity_uid}/overview`)

})

When('The user selects new activity group and accepts', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update activity version')

})

When('The activity group has been retired and has no replacement', () => {
    cy.inactivateGroup(group_uid)
    cy.wait(3000)
})

function getActivityData(rowIndex, getSoAGroupValue) {
    cy.getCellValueInPopUp(rowIndex, 'Library').then((text) => activity_library = text)
    if (getSoAGroupValue) cy.getCellValueInPopUp(rowIndex, 'SoA group').then((text) => activity_soa_group = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity group').then((text) => activity_group = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity subgroup').then((text) => activity_sub_group = text)
    cy.getCellValueInPopUp(rowIndex, 'Activity').then((text) => activity_activity = text.slice(0, 50))
}

function checkIfTableContainsActivity() {
    cy.wait(1000)
    cy.tableContains(activity_library)
    cy.tableContains(activity_soa_group)
    cy.tableContains(activity_group)
    cy.tableContains(activity_sub_group)
    cy.tableContains(activity_activity)
}

function addLibraryActivityByName() {
    activity_activity = activityName
    cy.waitForTable()
    cy.searchForInPopUp(activity_activity)
    cy.waitForTable()
    cy.get('[data-cy="select-activity"] input').check()
    cy.selectVSelect('flowchart-group', 'INFORMED CONSENT')
}

function selectActivityAndGetItsData(activity_soa_group = null) {
    if (activity_soa_group) activity_soa_group = 'INFORMED CONSENT'
    cy.get('.v-data-table__td--select-row input').each((el, index) => {
        if (el.is(':enabled')) {
            cy.wrap(el).check()
            if (activity_soa_group) {
                cy.get('[data-cy="flowchart-group"]').eq(index).click()
                cy.contains('.v-overlay .v-list-item-title', activity_soa_group).click({ force: true })
            }
            getActivityData(index, !activity_soa_group)
            return false
        }
    })
}

function fillPlaceholderData() {
    activity_placeholder_name = `Placeholder Instance Name ${Date.now()}`
    cy.contains('.choice .text', 'Create a placeholder activity without submitting for approval').click()
    cy.selectVSelect('flowchart-group', 'INFORMED CONSENT')
    cy.get('[data-cy="activity-group"] input').type('General')
    cy.selectFirstVSelect('activity-group')
    cy.selectFirstVSelect('activity-subgroup')
    cy.fillInput('instance-name', activity_placeholder_name)
    cy.fillInput('activity-rationale', 'Placeholder Test Rationale')
}

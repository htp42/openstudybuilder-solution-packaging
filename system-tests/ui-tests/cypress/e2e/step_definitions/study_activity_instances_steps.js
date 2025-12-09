import { activityInstance_uid } from "../../support/api_requests/library_activities";
const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

export let activity_activity, current_activity_uid

When('The activity instance with data-sharing set to {string}, required for activity set to {string} and default for activity set to {string} exists', (isDataSharing, isRequiredForActivity, isDefaultForActivity) => {
    cy.getClassUid()
    cy.createActivityInstance('', isDataSharing, isRequiredForActivity, isDefaultForActivity)
    cy.approveActivityInstance()

})

When('The user selects activity instance', () => {
    cy.get('[data-cy="form-body"]').within(() => {
        cy.get('tbody').within(() => {
            cy.get('.v-selection-control').first().click()
        })
    })

})

When('The user deselects one of activity instances', () => {
    cy.get('[data-cy="form-body"]').within(() => {
        cy.get('tbody').within(() => {
            cy.get('.v-selection-control').first().click()
        })
    })

})

When('The user selects multiple activity instances', () => [
    cy.get('[data-cy="form-body"]').within(() => {
        cy.get('tbody').within(() => {
            cy.get('.v-selection-control').click({multiple: true})
        })
    })
])

Then('The activity state is {string}', (state) => {
    cy.checkRowByIndex(0, 'State/Actions', state)

})

When('The {string} is clicked during review', (button) => {
    cy.contains(button).click()
})

Then('The reviewed checkbox is disabled', () => {
    cy.wait(1000)
    cy.get('tbody').within(() => {
        cy.get('td').eq(2).within(() => {
            cy.get('.v-input--disabled').should('exist')
        })
    })
})

Then('The review checkbox is marked as true', () => {
    cy.wait(1000)
    cy.get('tbody').within(() => {
        cy.get('td').eq(2).within(() => {
            cy.get('.mdi-checkbox-marked').should('exist')
        })
    })
})

Then('The user checks the review checkbox', () => {
    cy.wait(1000)
    cy.get('tbody').within(() => {
        cy.get('td').eq(2).within(() => {
            cy.get('input').click()
        })
    })
})

Then('The user unchecks the review checkbox', () => {
    cy.wait(1000)
    cy.get('tbody').within(() => {
        cy.get('td').eq(2).within(() => {
            cy.get('input').click()
        })
    })
})

When('The user removes the additional activities', () => { 
        cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').eq(2).click()
    })
    cy.contains('Delete Activity - Instance relationship').click()
    cy.contains('Delete').click()
})

Then('The button {string} is not present', (button) => {
    cy.contains(button).should('not.be.visible')
})

When('The activity instace name is updated', () => {
    cy.wait(1000)
    cy.activityInstanceNewVersion(activityInstance_uid)
    cy.visit(`/library/activities/activity-instances/${activityInstance_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.wait(1000)
    cy.clickFormActionButton('continue')
    cy.wait(1000)
    cy.clickFormActionButton('continue')
    cy.fillInput('instanceform-instancename-field', `NewName ${Date.now()}`)
    cy.clickFormActionButton('save')
})

When('The activity instace class is updated', () => {
    cy.wait(1000)
    cy.activityInstanceNewVersion(activityInstance_uid)
    cy.visit(`/library/activities/activity-instances/${activityInstance_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.wait(1000)
    cy.clickFormActionButton('continue')
    cy.selectVSelect('instanceform-instanceclass-dropdown', 'Event')
    cy.clickFormActionButton('continue')
    cy.clickFormActionButton('save')
})

When('The activity instace topic code is updated', () => {
    cy.wait(1000)
    cy.activityInstanceNewVersion(activityInstance_uid)
    cy.visit(`/library/activities/activity-instances/${activityInstance_uid}/overview`)
    cy.get('[title="Edit"]').click()
    cy.wait(1000)
    cy.clickFormActionButton('continue')
    cy.wait(1000)
    cy.clickFormActionButton('continue')
    cy.fillInput('instanceform-topiccode-field', Date.now())
    cy.clickFormActionButton('save')
})

When('The activity instace has been retired', () => {
    cy.inactivateActivityInstance(activityInstance_uid)
})

When('The user declines the activity instance changes', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update Instance to new version')
    cy.contains('button', 'Decline and keep').click()
})

When('The user accepts the activity instance changes', () => {
    cy.get('[data-cy="data-table"]').within(() => {
        cy.get('.mdi-dots-vertical').filter(':visible').click()
    })
    cy.clickButton('Update Instance to new version')
    cy.contains('button', 'Decline and keep').click()
})
import { activity_placeholder_name } from "./study_activities_steps";
import { selectedSupplierValue } from "./study_data_suppliers_steps";

const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");
const { getShortUniqueId } = require("../../support/helper_functions");

export let activity_activity, current_activity_uid
let originType, originSource

When('Library Instance Status is set to {string} in the edition form', (status) => {
    cy.get('.v-overlay table thead th').each((header, index) => {
        if (header.text() == 'Library Instance Status') {
            cy.get('.v-overlay table tbody tr td').eq(index).should('not.be.empty').invoke('text').then(text => status = text)
        }
    })
})

When('Origin Type and Origin Source are automatically populated in the edition form', () => {
    cy.get('.v-overlay table thead th').each((header, index) => {
        if (header.text() == 'Origin Source') {
            cy.get('.v-overlay table tbody tr td').eq(index).should('not.be.empty').invoke('text').then(text => originSource = text)
        }
        if (header.text() == 'Origin Type') {
            cy.get('.v-overlay table tbody tr td').eq(index).should('not.be.empty').invoke('text').then(text => originType = text)
        }
    })
})

When('Origin Type and Origin Source are automatically populated in the edition mode', () => {
    cy.get('table thead th').each((header, index) => {
        if (header.text() == 'Origin Source') {
            cy.get('table tbody tr td').eq(index).should('not.be.empty').invoke('text').then(text => originSource = text)
        }
        if (header.text() == 'Origin Type') {
            cy.get('table tbody tr td').eq(index).should('not.be.empty').invoke('text').then(text => originType = text)
        }
    })
})

When('{string} dropdown is activated in the edition form', (headerName) => {
    cy.get('.v-overlay table thead th').each((header, index) => {
        if (header.text() == headerName) {
            cy.get('.v-overlay table tbody tr td').eq(index).find('[role="combobox"]').click()
            return false
        }
    })
})

When('{string} dropdown is activated in the edition mode', (headerName) => {
    cy.get('table thead th').each((header, index) => {
        if (header.text() == headerName) {
            cy.get('table tbody tr td').eq(index).find('[role="combobox"]').click()
            return false
        }
    })
})

When('Important checkbox is checked in the edition form', () => {
    cy.get('.v-overlay table thead th').each((header, index) => {
        if (header.text() == 'Important') {
            cy.get('.v-overlay table tbody tr td').eq(index).find('input[type="checkbox"]').check()
            return false
        }
    })
})

When('Important checkbox is checked in the edition mode', () => {
    cy.get('table thead th').each((header, index) => {
        if (header.text() == 'Important') {
            cy.get('table tbody tr td').eq(index).find('input[type="checkbox"]').check()
            return false
        }
    })
})

When('Important checkbox is unchecked in the edition form', () => {
    cy.get('.v-overlay table thead th').each((header, index) => {
        if (header.text() == 'Important') {
            cy.get('.v-overlay table tbody tr td').eq(index).find('input[type="checkbox"]').uncheck()
            return false
        }
    })
})

When('Important checkbox is unchecked in the edition mode', () => {
    cy.get('table thead th').each((header, index) => {
        if (header.text() == 'Important') {
            cy.get('table tbody tr td').eq(index).find('input[type="checkbox"]').uncheck()
            return false
        }
    })
})

When('The Edition mode is enabled', () => cy.get('button .mdi-pencil').click())

When('The Edition mode is saved and closed', () => cy.contains('button', 'Save and Close').click())

When('The Edition mode is canceled and closed', () => cy.contains('button', 'Cancel').click())

When('Data is not available available for Instance Relationship', () => cy.contains('.v-overlay table tbody tr', 'No data available').should('be.visible'))

When('{string} visit is clicked from the dropdown', (visitName) => cy.contains('.v-overlay .v-list-item', visitName).click())

When('{string} visit is clicked from the dropdown in the edition mode', (visitName) => cy.contains('.v-list-item', visitName).click())

When('Previously added Data Supplier is clicked from the dropdown', () => cy.contains('.v-overlay .v-list-item', selectedSupplierValue).click())

When('Previously added Data Supplier is clicked from the dropdown in the edition mode', () => cy.contains('.v-list-item', selectedSupplierValue).click())

When('Baseline flag value is set to {string} in the table', (value) => cy.checkRowByIndex(0, 'Baseline visits', value))

When('Selected data supplier is visible in the table', () => cy.checkRowByIndex(0, 'Data Supplier', selectedSupplierValue))

When('Automatically populated Origin Type is visible in the table', () => cy.checkRowByIndex(0, 'Origin Type', originType))

When('Automatically populated Origin Source is visible in the table', () => cy.checkRowByIndex(0, 'Origin Source', originSource))

When('The activity instance with data-sharing set to {string}, required for activity set to {string} and default for activity set to {string} exists', (isDataSharing, isRequiredForActivity, isDefaultForActivity) => {
    createAndApproveParametrizedInstance(isDataSharing, isRequiredForActivity, isDefaultForActivity)
})

When('[API] The activity instance with isRequriedForActivity set to true is created and approved', () => createAndApproveParametrizedInstance(false, true, false))

When('[API] The activity instance with isDefaultForActivity set to true is created and approved', () => createAndApproveParametrizedInstance(false, false, true))

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

Then('The button {string} is disabled', (button) => cy.contains(button).should('be.disabled'))

When('The activity instace class is updated', () => cy.selectVSelect('instanceform-instanceclass-dropdown', 'Event'))

When('The activity instace topic code is updated', () => cy.fillInput('instanceform-topiccode-field', getShortUniqueId()))

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

Then('Correct placeholder data is visible in the study activity instances table', () => {
    cy.checkRowByIndex(0, 'Library', 'Requested')
    cy.checkRowByIndex(0, 'Activity', activity_placeholder_name)
    cy.checkRowByIndex(0, 'Activity instance', '')
})

function createAndApproveParametrizedInstance(isDataSharing, isRequiredForActivity, isDefaultForActivity) {
    cy.getClassUid()
    cy.createActivityInstance('', isDataSharing, isRequiredForActivity, isDefaultForActivity)
    cy.approveActivityInstance()
}
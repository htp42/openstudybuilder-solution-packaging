const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
import { getCurrStudyUid } from '../../support/helper_functions.js'

When ('The user clicks add study compund dosing', () => cy.clickButton('add-study-compound-dosing'))

When('The user select first study element', () => cy.selectFirstVSelect('study-element'))

When('The user select last study element', () => cy.selectLastVSelect('study-element'))

When('The user select first compund', () => cy.selectFirstVSelect('select-compound'))

When('The user select last compund', () => cy.selectLastVSelect('select-compound'))

When('The user select first dose value', () => cy.selectFirstVSelect('dose-value'))

When('The user select last dose value', () => cy.selectLastVSelect('dose-value'))

When('The user intercepts study compund dosings create request', () => cy.intercept('POST', '**/study-compound-dosings').as('createdDosing'))

When('The user intercepts study compund dosings update request', () => cy.intercept('PATCH', '**/study-compound-dosings').as('createdDosing'))

When('The user intercepts study compound dosing delete request', () => cy.intercept('**/study-compound-dosings/**').as('deleteRequest'))

When('The user intercepts study elements request', () => cy.intercept('**/study-elements**').as('elementsRequest'))

When('The user intercepts study compunds request', () => cy.intercept('**/study-compounds?**').as('compoundsRequest'))

Then('The study compound dosing is present in the compound dosings table', () => {
    cy.wait('@createdDosing').then((req) => {
        let dosingData = req.response.body
        cy.checkRowByIndex(dosingData.order - 1, '#', dosingData.order)
        cy.checkRowByIndex(dosingData.order - 1, 'Study Element', dosingData.study_element.name)
        cy.checkRowByIndex(dosingData.order - 1, 'Compound Name', dosingData.study_compound.compound.name)
        cy.checkRowByIndex(dosingData.order - 1, 'Medicinal product', dosingData.study_compound.medicinal_product.name)
        cy.checkRowByIndex(dosingData.order - 1, 'Compound Alias Name', dosingData.study_compound.compound_alias.name)
        cy.checkRowByIndex(dosingData.order - 1, 'Preferred Alias', dosingData.study_compound.compound_alias.is_preferred_synonym ? 'Yes' : 'No')
        cy.checkRowByIndex(dosingData.order - 1, 'Dose Value', `${dosingData.dose_value.value} ${dosingData.dose_value.unit_label}`)
        cy.checkRowByIndex(dosingData.order - 1, 'Dose Frequency', dosingData.study_compound.dose_frequency.term_name)
    })
})

Then('The element order for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-order', request.response.body.items[0].order)
    })
})

Then('The element type for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-type', request.response.body.items[0].element_type.term_name)
    })
})

Then('The element subtype for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-subtype', request.response.body.items[0].element_subtype.term_name)
    })
})

Then('The element name for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-name', request.response.body.items[0].name)
    })
})

Then('The element short name for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-short-name', request.response.body.items[0].short_name)
    })
})

Then('The element description for this element is automatically populated from library', () => {
    cy.wait('@elementsRequest').then((request) => {
        compareValue('study-element-description', request.response.body.items[0].description)
    })
})

Then('The compound order in dosings from for this compound is automatically populated from library', () => {
    cy.wait('@compoundsRequest').then((request) => {
        compareValue('compound-order', request.response.body.items[0].order)
    })
})

Then('The type of treatment in dosings from for this compound is automatically populated from library', () => {
    cy.wait('@compoundsRequest').then((request) => {
        compareValue('type-of-treatment', request.response.body.items[0].type_of_treatment.term_name)
    })
})

Then('The compound name in dosings from for this compound is automatically populated from library', () => {
    cy.wait('@compoundsRequest').then((request) => {
        compareValue('compound-name', request.response.body.items[0].compound.name)
    })
})

Then('The compound alias name in dosings from for this compound is automatically populated from library', () => {
    cy.wait('@compoundsRequest').then((request) => {
        compareValue('compound-alias-name', request.response.body.items[0].compound_alias.name)
    })
})

Then('The preferred synonim in dosings from for this compound is automatically populated from library', () => {
    cy.wait('@compoundsRequest').then((request) => {
        cy.get('[data-cy="is-preffered-synonym"]').within(() => {
            let radioSelection = request.response.body.items[0].compound_alias.is_preferred_synonym ? '[data-cy="radio-Yes"]' : '[data-cy="radio-No"]'
            cy.get(radioSelection).within(() => {
                cy.get('input').should('have.attr', 'checked')
            })
        })
    })
})

Then('The study compound dosing is removed', () => cy.wait('@deleteRequest').then((req) => expect(req.response.statusCode).to.eq(204)))

Given('The study compound dosing data is cleaned for testing purspose', () => {
    let currentStudy = getCurrStudyUid()
    cy.sendGetRequest(`/studies/${currentStudy}/study-compound-dosings`).then((response) => {
        if (response.body.items.length > 0) {
            response.body.items.forEach((item) => {
                cy.sendDeleteRequest(`/studies/${currentStudy}/study-compound-dosings/${item.study_compound_dosing_uid}`)
            })
        }
    })
})

function compareValue(selector, value) {
    cy.get(`[data-cy="${selector}"]`).within(() => {
        cy.get('input').should('have.value', value ? value : '')
    })
}
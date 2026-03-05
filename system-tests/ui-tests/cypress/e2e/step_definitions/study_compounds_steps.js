const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");
import { getCurrStudyUid } from '../../support/helper_functions.js'

Given('User clicks add study compund button', () => cy.clickButton('add-study-compound'))

Given('User fills other information', () => cy.fillInput('other-information', 'Testing Information'))

Given('User select first type of treatment', () => cy.selectFirstVSelect('type-of-treatment'))

Given('User select last type of treatment', () => cy.selectLastVSelect('type-of-treatment'))

Given('User select first compund', () => cy.selectFirstVSelect('compound'))

Given('User select last compund', () => cy.selectLastVSelect('compound'))

Given('User select first medicinal product', () => cy.selectFirstVSelect('medicinal-product'))

Given('User select last medicinal product', () => cy.selectLastVSelect('medicinal-product'))

Given('User intercepts compund create request', () => cy.intercept('POST', '**/study-compounds').as('createdCompound'))

Given('User intercepts compund update request', () => cy.intercept('PATCH', '**/study-compounds').as('createdCompound'))

Given('User intercepts compund delete request', () => cy.intercept('**/study-compounds/**').as('deleteRequest'))

Given('User intercepts compund aliases request', () => cy.intercept('**/concepts/compound-aliases**').as('compoundAliasesRequest'))

Given('User intercepts compunds request', () => cy.intercept('**/concepts/compounds/**').as('compoundRequest'))

Given('User intercepts medicial products request', () => cy.intercept('**/concepts/medicinal-products**').as('medicinalProductRequest'))

Given('User intercepts pharmaceutical products request', () => cy.intercept('**/concepts/pharmaceutical-products/**').as('pharmaceuticalProductRequest'))

Then('The study compound is present in the compounds table', () => {
    cy.wait('@createdCompound').then((req) => {
        let compoundData = req.response.body
        cy.checkRowByIndex(compoundData.order - 1, 'Type of treatment', compoundData.type_of_treatment.term_name)
        cy.checkRowByIndex(compoundData.order - 1, 'Compound', compoundData.compound.name)
        cy.checkRowByIndex(compoundData.order - 1, 'Sponsor compound', compoundData.is_sponsor_compound ? 'Yes' : 'No')
        cy.checkRowByIndex(compoundData.order - 1, 'Compound alias', compoundData.compound_alias.name)
        cy.checkRowByIndex(compoundData.order - 1, 'Medicinal product', compoundData.medicinal_product.name)
        cy.checkRowByIndex(compoundData.order - 1, 'Dose frequency', compoundData.dose_frequency.preferred_term)
    })
})

Then('The compound alias for this compound is automatically populated from library', () => {
    cy.wait('@compoundAliasesRequest').then((request) => {
        cy.get('[data-cy="compound-alias"]').should('contain', request.response.body.items[0].compound.name)
    })
})

Then('The other aliases for this compound is automatically populated from library', () => {
    cy.wait('@compoundAliasesRequest').then((request) => {
        let other_aliases = otherAliases(request.response.body.items)
        cy.get('[data-cy="other-aliases"]').within(() => {
            cy.get('input').should('have.value', other_aliases)
        })
    })
})

Then('The sponsor compound for this compound is automatically populated from library', () => {
    cy.wait('@compoundRequest').then((request) => {
        let radioSelection = request.response.body.is_sponsor_compound ? '[data-cy="radio-Yes"]' : '[data-cy="radio-No"]'
        cy.get(radioSelection).within(() => {
            cy.get('input').should('have.attr', 'checked')
        })
    })
})

Then('The compound definition for this compound is automatically populated from library', () => {
    cy.wait('@compoundRequest').then((request) => {
        cy.get('[data-cy="compound-definition"]').within(() => {
            cy.get('textarea').should('have.value', request.response.body.definition ? request.response.body.definition : '-')
        })
    })
})

Then('The dispensed in for this compound is automatically populated from library', () => {
    cy.wait('@medicinalProductRequest').then((request) => {
        let dispensed_in = request.response.body.items[0].dispenser.name
        cy.get('[data-cy="dispensed-in"]').within(() => {
            cy.get('input').should('have.value', dispensed_in ? dispensed_in : '-')
        })
    })
})

Then('The INN for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let active_substance = request.response.body.formulations[0].ingredients[0].active_substance.inn
        cy.get('[data-cy="active-substance"]').within(() => {
            cy.get('input').should('have.value', active_substance ? active_substance : '-')
        })
    })
})

Then('The analyte number for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let analyte_number = request.response.body.formulations[0].ingredients[0].active_substance.analyte_number
        cy.get('[data-cy="analyte-number"]').within(() => {
            cy.get('input').should('have.value', analyte_number ? analyte_number : '-')
        })
    })
})

Then('The substance id for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let long_number = request.response.body.formulations[0].ingredients[0].active_substance.long_number
        cy.get('[data-cy="long-number"]').within(() => {
            cy.get('input').should('have.value', long_number ? long_number : '-')
        })
    })
})

Then('The substance name for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let short_number = request.response.body.formulations[0].ingredients[0].active_substance.short_number
        cy.get('[data-cy="short-number"]').within(() => {
            cy.get('input').should('have.value', short_number ? short_number : '-')
        })
    })
})

Then('The UNII for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let substance_unii = request.response.body.formulations[0].ingredients[0].active_substance.unii.substance_unii
        cy.get('[data-cy="substance"]').within(() => {
            cy.get('input').should('have.value', substance_unii ? substance_unii : '-')
        })
    })
})

Then('The pharmacological class MED-RT for this compound is automatically populated from library', () => {
    cy.wait('@pharmaceuticalProductRequest').then((request) => {
        let pclass = request.response.body.formulations[0].ingredients[0].active_substance.unii.pclass_name
        let id = request.response.body.formulations[0].ingredients[0].active_substance.unii.pclass_id
        let pharmacological_class = `${pclass} (${id})`
        cy.get('[data-cy="pharmacological-class"]').within(() => {
            cy.get('input').should('have.value', pharmacological_class ? pharmacological_class : '-')
        })
    })
})

Then('The user cannot save the form', () => cy.get('.v-messages__message').should('contain', 'This field is required'))

Then('The study compound is removed', () => {
    cy.wait('@deleteRequest').then((req) => expect(req.response.statusCode).to.eq(204))
})

Given('The study compounds data is cleaned for testing purspose', () => {
    let currentStudy = getCurrStudyUid()
    cy.sendGetRequest(`/studies/${currentStudy}/study-compounds`).then((response) => {
        if (response.body.items.length > 0) {
            response.body.items.forEach((item) => {
                cy.sendDeleteRequest(`/studies/${currentStudy}/study-compounds/${item.study_compound_uid}`)
            })
        }

    })
    
})

function otherAliases(aliases) {
    const otherSynonyms = aliases.filter((item) => !item.is_preferred_synonym)
    return otherSynonyms.length
        ? otherSynonyms.map((item) => item.name).join(', ')
        : '-'
}
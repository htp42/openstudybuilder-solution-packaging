Cypress.Commands.add('createCrfCollection', (name) => {
    cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/study-events',
        body: `{"name":"${name}"}`
    })
    cy.reload()
})

Cypress.Commands.add('createCrfForm', (oid) => {
    cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/forms',
        body: '{"oid":"' + oid + '","repeating":"no","alias_uids":[],"name":"TestAutomated","descriptions":[{"library_name":"Sponsor","language":"ENG","name":"TestAutomated"}],"library_name":"Sponsor"}'
    })
    cy.reload()
})

Cypress.Commands.add('createCrfItemGroup', (oid) => {
    cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/item-groups',
        body: '{"oid":"' + oid + '","repeating":"no","is_reference_data":"no","locked":"no","alias_uids":[],"sdtm_domain_uids":[],"name":"AutomatedTestItemGroup","descriptions":[{"library_name":"Sponsor","language":"ENG","name":"AutomatedTestItemGroup"}],"library_name":"Sponsor"}'
    })
    cy.reload()
})

Cypress.Commands.add('createCrfItem', (name, oid) => {
    cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/items',
        body: `{"oid":"${oid}","alias_uids":[],"locked":"no","name":"${name}","datatype":"INTEGER","descriptions":[{"library_name":"Sponsor","language":"ENG","name":"${name}"}],"library_name":"Sponsor","codelist_uid":null,"unitDefinitions":[],"terms":[]}`
    })
    cy.reload()
})

// Command to create a CRF collection
Cypress.Commands.add('createCrfCollectionByName', (name) => {
    return cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/study-events',
        body: {
            name: name // Use the given name
        }
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
        return response.body; // Return the response body
    });
});

// Command to create a form
Cypress.Commands.add('createCrfFormByName', (name) => {
    return cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/forms',
        body: {
            name: name, // Use the given name
            repeating: "no",
            alias_uids: [],
            descriptions: [
                {
                    library_name: "Sponsor",
                    language: "ENG",
                    name: name // Use the same name for descriptions
                }
            ],
            library_name: "Sponsor"
        }
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
        return response.body; // Return the response body for further use if needed
    });
});

// Command to create an item group
Cypress.Commands.add('createCrfItemGroupByName', (name) => {
    return cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/item-groups',
        body: {
            name: name, // Use the given name
            repeating: "no",
            is_reference_data: "no",
            locked: "no",
            alias_uids: [],
            sdtm_domain_uids: [],
            descriptions: [
                {
                    library_name: "Sponsor",
                    language: "ENG",
                    name: name // Use the same name for descriptions
                }
            ],
            library_name: "Sponsor"
        }
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
        return response.body; // Return the response body for further use if needed
    });
});

// Command to create an item
Cypress.Commands.add('createCrfItemByName', (name) => {
    return cy.request({
        method: 'POST',
        url: Cypress.env('API') + '/concepts/odms/items',
        body: {
            name: name, // Use the given name
            alias_uids: [],
            locked: "no",
            datatype: "INTEGER", // Assuming a data type is needed
            descriptions: [
                {
                    library_name: "Sponsor",
                    language: "ENG",
                    name: name // Use the same name for descriptions
                }
            ],
            library_name: "Sponsor",
            codelist_uid: null,
            unitDefinitions: [],
            terms: []
        }
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
        return response.body; // Return the response body for further use if needed
    });
});

// Command to link a form to a collection
Cypress.Commands.add('linkFormToCollection', (formUid, collectionUid) => {
    return cy.request({
        method: 'POST',
        url: `${Cypress.env('API')}/concepts/odms/study-events/${collectionUid}/forms?override=true`,
        body: 
            [
                {
                    "uid": formUid,
                    "order_number": 1,
                    "mandatory": "No",
                    "locked": "No",
                    "collection_exception_condition_oid": null
                }
                ]

        
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful linking (201 Created)
        return response.body; // Return response body for further use
    });
});

// Command to link an item group to a form
Cypress.Commands.add('linkItemGroupToForm', (formUid, itemGroupUid) => {
    return cy.request({
        method: 'POST',
        url: `${Cypress.env('API')}/concepts/odms/forms/${formUid}/item-groups?override=true`, // URL to link the item group
        body: [
                {
                    "uid": itemGroupUid,
                    "order_number": 1,
                    "mandatory": "No",
                    "collection_exception_condition_oid": null,
                    "vendor": {
                    "attributes": []
                    }
                }
]
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful linking (201 Created)
        return response.body; // Return response body for further use if needed
    });
});

// Command to link an item to an item group
Cypress.Commands.add('linkItemToItemGroup', (itemGroupUid, itemUid) => {
    return cy.request({
        method: 'POST',
        url: `${Cypress.env('API')}/concepts/odms/item-groups/${itemGroupUid}/items?override=true`, // URL for linking
        body: [
                {
                    "uid": itemUid,
                    "order_number": 1,
                    "mandatory": "No",
                    "key_sequence": "No",
                    "method_oid": "null",
                    "imputation_method_oid": "null",
                    "role": "null",
                    "role_codelist_oid": "null",
                    "collection_exception_condition_oid": "null",
                    "vendor": {
                    "attributes": []
                    }
                }
]
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful linking (201 Created)
        return response.body; // Return the response body for further use
    });
});

Cypress.Commands.add('approveForm', (formUid) => {
    cy.request({
        method: 'POST',
        url: `${Cypress.env('API')}/concepts/odms/forms/${formUid}/approvals`,
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
         return response.body; // Return the response body for further use
    });               
})

Cypress.Commands.add('approveCollection', (collectionUid) => {
    cy.request({
        method: 'POST',
        url: `${Cypress.env('API')}/concepts/odms/study-events/${collectionUid}/approvals`,
    }).then((response) => {
        expect(response.status).to.eq(201); // Verify successful creation
         return response.body; // Return the response body for further use
    });               
})
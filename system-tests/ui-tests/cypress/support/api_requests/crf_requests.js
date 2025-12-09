const odmsStudyEventsUrl = '/concepts/odms/study-events'
const odmsFormsUrl = '/concepts/odms/forms'
const odmsItemUrl = '/concepts/odms/items'
const odmItemGroupUrl = '/concepts/odms/item-groups'
const odmLinkFormToCollectionUrl = (collectionUid) => `/concepts/odms/study-events/${collectionUid}/forms?override=true`
const odmLinkGroupToFormUrl = (formUid) => `/concepts/odms/forms/${formUid}/item-groups?override=true`
const odmLinkItemToGroupUrl = (itemGroupUid) => `/concepts/odms/item-groups/${itemGroupUid}/items?override=true`
const odmApproveFormUrl = (formUid) => `/concepts/odms/forms/${formUid}/approvals`
const odmApproveCollectionUrl = (collectionUid) => `/concepts/odms/study-events/${collectionUid}/approvals`

Cypress.Commands.add('createCrfCollection', (name) => { return cy.sendPostRequest(odmsStudyEventsUrl, {name:`${name}`}) })

Cypress.Commands.add('createCrfForm', (name) => { return cy.sendPostRequest(odmsFormsUrl, createCrfFormBody(name)) })

Cypress.Commands.add('createCrfItem', (name) => cy.sendPostRequest(odmsItemUrl, createCrfItemBody(name)))

Cypress.Commands.add('createCrfItemGroup', (name) => cy.sendPostRequest(odmItemGroupUrl, createCrfItemGroupBody(name)))

Cypress.Commands.add('linkFormToCollection', (nameformUid, collectionUid) => cy.sendPostRequest(odmLinkFormToCollectionUrl(collectionUid), linkFormToCollectionBody(nameformUid)))

Cypress.Commands.add('linkItemGroupToForm', (fromUid, groupItemUid) => cy.sendPostRequest(odmLinkGroupToFormUrl(fromUid), linkGroupToFormBody(groupItemUid)))

Cypress.Commands.add('linkItemToItemGroup', (itemGroupUid, itemUid) => cy.sendPostRequest(odmLinkItemToGroupUrl(itemGroupUid), linkItemToGroupBody(itemUid)))

Cypress.Commands.add('approveForm', (formUid) => cy.sendPostRequest(odmApproveFormUrl(formUid), {}))

Cypress.Commands.add('approveCollection', (collectionUid) => cy.sendPostRequest(odmApproveCollectionUrl(collectionUid), {}))

const createCrfFormBody = (name) => {
    return {
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
}

const createCrfItemBody = (name) => {
    return {
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
}

const createCrfItemGroupBody = (name) => {
    return {
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
}

const linkFormToCollectionBody = (formUid) => {
    return [
            {
            "uid": formUid,
            "order_number": 1,
            "mandatory": "No",
            "locked": "No",
            "collection_exception_condition_oid": null
        }
    ]
}

const linkGroupToFormBody = (itemGroupUid) => {
    return [
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
}

const linkItemToGroupBody = (itemUid) => {
    return [
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
}
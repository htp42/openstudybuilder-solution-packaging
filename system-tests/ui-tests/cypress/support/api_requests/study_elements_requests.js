let type_uid, subType_uid
const elementSubTypesUrl = `/study-elements/allowed-element-configs`
const createElementUrl = (study_uid) => `/studies/${study_uid}/study-elements`

Cypress.Commands.add('getElementTypeAndSubType', (subTypeName) => {
  cy.sendGetRequest(elementSubTypesUrl).then((response) => {
      subType_uid = response.body.find(item => item.subtype_name == subTypeName).subtype
      type_uid = response.body.find(item => item.subtype_name == subTypeName).type
  })
})

Cypress.Commands.add('addElementToStudy', (study_uid, element_name) => {
  cy.sendPostRequest(createElementUrl(study_uid), addElementBody(type_uid, subType_uid, element_name))
})

const addElementBody = (typeUid, subtypeUid, name) => {
  return {
        "planned_duration": null,
        "code": `${typeUid}`,
        "element_subtype_uid": `${subtypeUid}`,
        "name": `${name}`,
        "short_name": `${name}`.substring(0, 4),
        "element_colour": "#BDBDBD"
    }
}
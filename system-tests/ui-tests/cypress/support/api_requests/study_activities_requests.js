let soaGroup_uid
const studyActivityUrl = (study_uid, study_activity_uid) => `/studies/${study_uid}/study-activities/${study_activity_uid}`
const studyActivitiesUrl = (study_uid) => `/studies/${study_uid}/study-activities?page_number=1&page_size=0`
const studyActivityBatchUrl = (study_uid) => `/studies/${study_uid}/study-activities/batch`
const flowchartGroupUrl = () => '/ct/codelists/terms?page_size=100&codelist_submission_value=FLWCRTGRP'

Cypress.Commands.add('deleteActivityFromStudy', (study_uid, activity_uid) => cy.sendDeleteRequest(studyActivityUrl(study_uid, activity_uid)))

Cypress.Commands.add('getExistingStudyActivities', (study_uid) => {
  cy.sendGetRequest(studyActivitiesUrl(study_uid)).then((response) => {
    let uid_array = []
    response.body.items.forEach(item => uid_array.push(item.study_activity_uid))
    return uid_array
  })
})

Cypress.Commands.add('addActivityToStudy', (study_uid, activity_uid, activityGroup_uid, activitySubgroup_uid) => {
  cy.sendPostRequest(studyActivityBatchUrl(study_uid), addActivityToStudyBody(soaGroup_uid, activity_uid, activityGroup_uid, activitySubgroup_uid))
})

Cypress.Commands.add('getSoaGroupUid', (soaGroup_name) => {
    cy.sendGetRequest(flowchartGroupUrl()).then((response) => {
      soaGroup_uid = response.body.items.find(item => item.sponsor_preferred_name == soaGroup_name).term_uid
  })
})

const addActivityToStudyBody = (soaGroup_uid, activity_uid, activityGroup_uid, activitySubgroup_uid) => {
  return [
    {
      "method": "POST",
      "content": {
        "soa_group_term_uid": soaGroup_uid,
        "activity_uid": activity_uid,
        "order": null,
        "activity_group_uid":activityGroup_uid,
        "activity_subgroup_uid": activitySubgroup_uid
      }
    }
  ]
}
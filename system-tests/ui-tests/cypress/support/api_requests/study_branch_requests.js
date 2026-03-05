import { generateShortUniqueName } from "../helper_functions"
import { arm_uid } from "./study_arm_requests"

export let branch_uid
const createBranchUrl = (studyUid) => `/studies/${studyUid}/study-branch-arms` 

Cypress.Commands.add('createBranch', (study_uid) => {
    cy.sendPostRequest(createBranchUrl(study_uid), createBranchBody(arm_uid)).then(response => branch_uid = response.body.branch_arm_uid)
})

const createBranchBody = (armUid) => {
    let branchName = `${generateShortUniqueName('Branch')}`
    return {
        "name": branchName,
        "short_name": branchName,
        "randomization_group": `Random${Date.now()}`,
        "code": `Code${Date.now()}`,
        "number_of_subjects": '10',
        "description": 'TestBranch',
        "arm_uid": armUid
    }
}

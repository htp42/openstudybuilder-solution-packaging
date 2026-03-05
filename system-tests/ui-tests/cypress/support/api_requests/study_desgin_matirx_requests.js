import { arm_uid } from "./study_arm_requests"
import { branch_uid } from "./study_branch_requests"
import { element_uid } from "./study_elements_requests"
import { epoch_uid } from "./study_epochs_requests"

const createDesignMatrixRequest = (studyUid) => `/studies/${studyUid}/study-design-cells/batch` 

Cypress.Commands.add('createDesignMatrix', (study_uid) => {
    cy.sendPostRequest(createDesignMatrixRequest(study_uid), createDesignMatrixBody(arm_uid, epoch_uid, element_uid, branch_uid))
})

const createDesignMatrixBody = (armUid, epochUid, elementUid, branchUid) => {
    return [
        {
        "method": "POST",
            "content": {
                "study_arm_uid": null,
                "study_epoch_uid": epochUid,
                "study_element_uid": elementUid,
                "study_branch_arm_uid": branchUid,
                "transition_rule": "Testing E2E"
            }
        }
    ]
}

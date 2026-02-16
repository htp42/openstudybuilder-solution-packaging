import { activity_placeholder_name } from "./study_activities_steps";

const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

When('Row containing submitted placeholder is highlighted with yellow color in Operational SoA', () => cy.contains('tr.bg-yellow', activity_placeholder_name).should('be.visible'))

When('Row containing unsubmitted placeholder is highlighted with orange color in Operational SoA', () => cy.contains('tr.bg-warning', activity_placeholder_name).should('be.visible'))

When('User waits Operational SoA table', () => cy.get('table tbody tr').should('be.visible'))

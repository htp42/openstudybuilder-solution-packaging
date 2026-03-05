const { Given, When, Then } = require("@badeball/cypress-cucumber-preprocessor");


Given("The test study definition in status Released and version 1.1 is selected", () => cy.tableRowActions(1, 'Select'));

Given("The test study definition in status Locked and version 1 is selected", () => cy.tableRowActions(2, 'Select'));

Then("The {string} is displayed", (value) => cy.get("body").should("contain", value));

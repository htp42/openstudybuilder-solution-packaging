Cypress.Commands.add("selectTestStudy", (study) => {
  cy.request(Cypress.env("API") + "/studies/" + study).then((response) => {
    window.localStorage.setItem("selectedStudy", JSON.stringify(response.body));
  });
});

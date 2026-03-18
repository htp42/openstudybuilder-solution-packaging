Cypress.Commands.add('sendPostRequest', (url, body) => {
    cy.request('POST', Cypress.env('API') + url, body).then((response) => {
        expect(response.status).to.be.oneOf([200, 201, 207])
        return response;
    })
})

Cypress.Commands.add('sendUpdateRequest', (method, url, body) => {
    cy.request(method, Cypress.env('API') + url, body).then((response) => {
        expect(response.status).to.be.oneOf([200])
        return response;
    })
})

Cypress.Commands.add('sendDeleteRequest', (url) => {
    cy.request('DELETE', Cypress.env('API') + url, {}).then((response) => expect(response.status).to.be.oneOf([200, 204]))
})

Cypress.Commands.add('sendGetRequest', (url) => {
    cy.request('GET', Cypress.env('API') + url).then((response) => {
        expect(response.status).to.eq(200)
        return response;
    })
})

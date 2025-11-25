const { When, Then } = require("@badeball/cypress-cucumber-preprocessor");

let ODMElementName // Default value for ODM Element Name

Then('I verify there is {string} dropdown exist', (dropdown) => {
    cy.get('.v-input') // Get all elements with the class 'v-input'
      .contains(dropdown) // Check for presence of the specified dropdown label
      .should('exist'); // Assert that this dropdown exists
});


When('I select a value from the ODM Element Name dropdown', () => {
    // Click to open the dropdown
    cy.contains('ODM Element Name') // Find the label that matches 'ODM Element Name'
      .parents('.v-input') // Find the parent container that wraps the dropdown input
      .find('.v-field__append-inner .mdi-menu-down') // Find the dropdown toggle icon
      .click(); // Open the dropdown
    
    // Wait for dropdown items to become visible and ensure there are items
    cy.get('.v-list-item', { timeout: 30000 }) // Wait for the items to load
      .should('have.length.greaterThan', 0) // Ensure there are dropdown items
      .last() // Get the first item
      .then(($item) => {
          // Save the selected value in a variable
          ODMElementName = $item.text().trim(); // Trim and store the text
          
          // Scroll into view and click the first item
          cy.wrap($item) // Use cy.wrap to wrap the jQuery object
            .scrollIntoView() // Scroll to ensure it's visible
            .click(); // Click to select the item
      });
      
});

When ('keep all other fields as default', () => {
// No action needed, just a placeholder step
})

When ('I click the LOAD button', () => {   
    cy.get('.v-btn').contains('Load') // Find the button containing the text 'LOAD'
    .should('be.visible')             // Ensure the button is visible   
    .should('not.be.disabled')  // Ensure the button is not disabled
    .click();                        // Click the button
})

Then('The imported CRF view page should be displayed', () => {
    cy.get('body').contains(ODMElementName).should('be.visible'); 
})

When('I enable the XML Code toggle', () => {
    cy.contains('label', 'XML Code') // Find the label containing the text
    .click();                     // Click the label, which interacts with the checkbox
})

Then('The XML Code page should be displayed and formatted correctly', () => {
    // Check if the <pre> element's text starts with "<?xml"
    cy.get('pre') // Assuming the <pre> is directly accessible
      .invoke('text') // Get the text content of the <pre>
      .then((text) => {
          // Retrieve the first line by splitting the text into lines
          const firstLine = text.split('\n')[0]; // Get the first line
          
          // Assert that the first line starts with "<?xml"
          expect(firstLine.trimStart()).to.match(/^\s*<\?xml/);
      });
});







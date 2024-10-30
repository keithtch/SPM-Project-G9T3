describe('Manage My WFH Applications Page', () => {
    beforeEach(() => {
      cy.visit('http://localhost/SPM-Project-G9T3/ManageApplication/mapplication.html');
      localStorage.setItem("staffID", "140894"); 
    });
  
    it('Displays the page correctly', () => {
      // Check the page title and header
      cy.title().should('eq', 'Manage My WFH Applications');
      cy.get('h2').should('contain', 'Manage My WFH Applications');
  
      // Check the view indicator
      cy.get('.view-indicator').should('have.class', 'my-view');
  
      // Check the tab navigation
      cy.get('.nav-item').should('have.length', 3);
      cy.get('.nav-item').should('contain', 'My Approved Applications');
      cy.get('.nav-item').should('contain', 'My Pending Applications');
      cy.get('.nav-item').should('contain', 'My Rejected Applications');
    });

  });


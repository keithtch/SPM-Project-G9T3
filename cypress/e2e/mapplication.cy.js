describe('Manage My WFH Applications Page', () => {
    beforeEach(() => {
      cy.visit('http://localhost:8000/ManageApplication/mapplication.html');
      localStorage.setItem("staffID", "140894"); 
      localStorage.setItem("Reporting_Manager", "140001"); 
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

    it('should display my applications correctly', () => {
      // Check if table is present with correct columns
      cy.get('table').should('be.visible')
      cy.contains('th', 'Staff ID')
      cy.contains('th', 'Staff Name')
      cy.contains('th', 'Date Applied')
      cy.contains('th', 'Time of Day')
      cy.contains('th', 'Status')
    });

    it('should navigate back to home page', () => {
      // Click back button
      cy.contains('Go Back to Home Page').click()
      
      // Verify navigation
      cy.url().should('include', 'http://localhost:8000/Home/home.html')
    });

    it('should have all navigation tabs', () => {
      cy.get('.nav-item').should('have.length', 3)
      cy.contains('.nav-item', 'My Approved Applications')
      cy.contains('.nav-item', 'My Pending Applications')
      cy.contains('.nav-item', 'My Rejected Applications')
    });
    
  });


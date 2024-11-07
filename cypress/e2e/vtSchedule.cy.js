describe('View Team Schedule Page', () => {
    beforeEach(() => {

      // Add an event listener to handle uncaught exceptions
      cy.on('uncaught:exception', (err, runnable) => {
        // returning false here prevents Cypress from failing the test
        return false;
      });

      // Visit the page before each test
      cy.visit('http://localhost:8000/ViewTeamSchedule/vtSchedule.html');
      localStorage.setItem("staffID", "160008");
    });
  
    it('should load the page and display the title correctly', () => {
      cy.contains('h1', 'Team Schedule').should('be.visible');
    });
  
    it('should toggle between Team and Department filters', () => {
      cy.get('button').contains('Filter by Department').click();
      cy.get('#dept').should('exist');
      cy.get('button').contains('Filter by Team').click();
      cy.get('#team').should('exist');
    });
  
  
  });
  
describe('View Team Schedule Page', () => {
    beforeEach(() => {

      // Add an event listener to handle uncaught exceptions
      cy.on('uncaught:exception', (err, runnable) => {
        // returning false here prevents Cypress from failing the test
        return false;
      });

      // Visit the page before each test
      cy.visit('http://localhost:8000/ViewTeamSchedule/vtSchedule.html');
      localStorage.setItem("staffID", "140894");
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
  
    it('should toggle between daily and weekly view buttons', () => {

      cy.intercept('POST', 'http://localhost:5001/findTeam/*').as('getTeamData');
      cy.reload();
      cy.wait('@getTeamData');

      cy.get('.btn-group button').contains('Weekly View').click();
      cy.get('.card-title',{timeout: 10000}).contains('Weekly Team Information').should('be.visible');
      cy.get('.btn-group button').contains('Daily View').click();
      cy.get('.card-title',{timeout: 10000}).contains('Team Information').should('be.visible');
    });

    it('should toggle between daily and weekly view buttons and verify correct display', () => {

        cy.intercept('POST', 'http://localhost:5001/findTeam/*').as('getTeamData');
        cy.reload();
        cy.wait('@getTeamData');

        cy.get('.btn-group button').contains('Weekly View').click();
        cy.get('.card-title',{timeout: 10000}).contains('Weekly Team Information').should('be.visible');
        cy.get('.btn-group button').contains('Daily View').click();
        cy.get('.card-title',{timeout: 10000}).contains('Team Information').should('be.visible');
    });
  
  });
  
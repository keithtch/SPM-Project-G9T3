describe('WFH Schedule Page Tests', () => {
    beforeEach(() => {
      cy.visit('http://localhost/SPM-Project-G9T3/ViewOwnSchedule/voSchedule.html'); 
      cy.wait(1000); 
      localStorage.setItem("staffID", "140894"); 
    });

    it('Applies WFH and navigates to the application page', () => {
      cy.get('.button b-button')
        .contains('Apply WFH')
        .click();
  
      // Check if the page redirected correctly
      cy.url().should('include', 'http://localhost/SPM-Project-G9T3/Application/application.html');
    });
  
    it('Returns to the home page', () => {
      cy.get('.button b-button')
        .contains('Go Back to Home Page')
        .click();
  
      // Verify redirection to the home page
      cy.url().should('include', 'http://localhost/SPM-Project-G9T3/Home/home.html');
    });
  
  });
  
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

    it('Checks that the page title is correct', () => {
        cy.title().should('eq', 'My Schedule');
      });
    
      it('Displays the calendar correctly', () => {
        cy.get('#calendar').should('exist');
        cy.get('#calendar').should('be.visible');
      });
    
      it('Verifies WFH Schedule is shown in header', () => {
        cy.get('h1').should('contain.text', 'My WFH Schedule');
      });
    
      it('Ensures Apply WFH button is present and clickable', () => {
        cy.get('.button b-button')
          .contains('Apply WFH')
          .should('be.visible')
          .click();
    
        // Check if redirected correctly
        cy.url().should('include', 'http://localhost/SPM-Project-G9T3/Application/application.html');
      });
    
      it('Ensures Go Back to Home Page button is present and clickable', () => {
        cy.visit('http://localhost/SPM-Project-G9T3/ViewOwnSchedule/voSchedule.html');
        cy.get('.button b-button')
          .contains('Go Back to Home Page')
          .should('be.visible')
          .click();
    
        // Verify redirection to the home page
        cy.url().should('include', 'http://localhost/SPM-Project-G9T3/Home/home.html');
      });
    
      it('Ensures fetching and storing of staffID in localStorage', () => {
        cy.window().its('localStorage').invoke('getItem', 'staffID').should('eq', '140894');
      });
    
      it('Simulates applying for WFH and confirms redirection to application form', () => {
        cy.get('.button b-button')
          .contains('Apply WFH')
          .click();
    
        cy.url().should('include', 'Application/application.html');
      });
    
      it('Simulates going back to the Home page and verifies redirection', () => {
        cy.get('.button b-button')
          .contains('Go Back to Home Page')
          .click();
    
        cy.url().should('include', 'Home/home.html');
      });
    
      it('Confirms detailBox is hidden by default', () => {
        cy.get('#detailBox').should('not.be.visible');
      });
  
  });
  
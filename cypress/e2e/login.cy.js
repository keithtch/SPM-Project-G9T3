describe('All-In-One WFHMS Login Page', () => {
    beforeEach(() => {
        cy.visit('http://localhost/SPM-Project-G9T3/Login&Authentication/login.html'); // Adjust the URL 
    });

    it('Displays initial elements correctly', () => {
        // Check if page title and headers are correct
        cy.title().should('eq', 'All-In-One WFHMS Login Page');
        cy.get('h1').contains('All-In-One');
        cy.get('h3').contains('WFH Management System');

        // Check if input and button are present
        cy.get('.input-box input[type="text"]').should('have.attr', 'placeholder', 'Enter your StaffID');
        cy.get('.btn').should('be.disabled');
    });


    it('Successfully logs in and redirects on valid StaffID', () => {
        cy.intercept('GET', 'http://localhost:5000/employee', {
            body: {
                data: [['12345', '', '', '', '', '', '', 'Manager Name']], // Mock data with expected structure
            },
        });

        cy.get('.input-box input[type="text"]').type('12345');
        cy.get('.btn').click();

        cy.wait(500); // wait for loading screen to disappear if necessary
        cy.url().should('include', '/Home/home.html');
        cy.window().then((win) => {
            expect(win.localStorage.getItem('staffID')).to.eq('12345');
            expect(win.localStorage.getItem('Reporting_Manager')).to.eq('Manager Name');
        });
    });

    it('Displays error message on invalid StaffID', () => {
        cy.intercept('GET', 'http://localhost:5000/employee', {
            body: {
                data: [['67890', '', '', '', '', '', '', 'Manager Name']], 
            },
        });

        cy.get('.input-box input[type="text"]').type('12345');
        cy.get('.btn').click();

        cy.on('window:alert', (str) => {
            expect(str).to.equal('Invalid StaffID. Please try again.');
        });

        // Ensure loading state resets after invalid login
        cy.get('.loading-screen').should('not.exist');
        cy.get('.btn').should('not.be.disabled');
    });
});

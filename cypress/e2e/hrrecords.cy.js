describe('HR Records Page', () => {

    beforeEach(() => {
        // Visit the HR Records page
        cy.visit('http://localhost:8000/HRRecords/hrrecords.html');  // Replace with your actual URL or path
        localStorage.setItem("staffID", "160008"); // Set a valid staff ID
    });

    it('should display the page title correctly', () => {
        // Check if the title is correct
        cy.get('h1').should('contain.text', 'HR Records');
    });

    it('should display the Go Back to Home Page button', () => {
        // Verify that the "Go Back to Home Page" button is present
        cy.get('button').contains('Go Back to Home Page').should('be.visible');
    });

    it('should navigate to the home page when Go Back button is clicked', () => {
        // Click the "Go Back to Home Page" button and confirm redirection
        cy.get('button').contains('Go Back to Home Page').click();
        cy.url().should('include', 'http://localhost:8000/Home/home.html');
    });

    it('should fetch and display HR records data', () => {
        // Wait for the table data to load
        cy.intercept('GET', 'https://spm-project-g9-t3.vercel.app/getLogs').as('getRecords');
        cy.wait('@getRecords').then((interception) => {
            expect(interception.response.statusCode).to.eq(200);
            expect(interception.response.body.data).to.have.length.greaterThan(0);
        });

        // Verify table rows are rendered based on API response
        cy.get('table tbody tr').should('have.length.greaterThan', 0);
    });

    it('should display correct headers in the table', () => {
        // Check each header is present and accurate
        const headers = [
            'Database Record ID', 'Staff ID', 'WFH Date Applied', 'Time of Day',
            'Reporting Manager ID', 'Application Status', 
            'Reason for Application by Staff', 
            'Why Manager Rejected/Withdraw Reason (If Any)', 
            'Staff Withdraw Reason'
        ];
        cy.get('thead th').each((header, index) => {
            cy.wrap(header).should('contain.text', headers[index]);
        });
    });

    it('should display N/A for missing Manager or Staff Withdraw reasons', () => {
        // Check if 'N/A' appears in the cells for managerReason and staffWithdrawReason when they are empty
        cy.get('table tbody tr').each(($row) => {
            cy.wrap($row).within(() => {
                cy.get('td').eq(7).invoke('text').then((text) => {
                    if (text.trim() === '') {
                        cy.get('td').eq(7).should('contain.text', 'N/A');
                    }
                });
                cy.get('td').eq(8).invoke('text').then((text) => {
                    if (text.trim() === '') {
                        cy.get('td').eq(8).should('contain.text', 'N/A');
                    }
                });
            });
        });
    });

    it('should have text-wrapping enabled for long text in the table cells', () => {
        // Ensure that long text in table cells is wrapped
        cy.get('td.text-wrap').each(($cell) => {
            const cellWidth = $cell.width();
            cy.wrap($cell).invoke('height').should('be.gt', 20); // basic check that cell accommodates multi-line text
        });
    });
});

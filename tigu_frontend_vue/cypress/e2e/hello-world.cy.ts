describe('Hello World Test', () => {
    it('should display hello world message', () => {
        cy.visit('/');
        cy.contains('Hello World');
    });
});
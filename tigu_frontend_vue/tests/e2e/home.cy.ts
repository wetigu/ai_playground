describe('Home Page', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('displays the welcome message', () => {
    cy.contains('h1', 'Welcome to Tigu Platform');
  });

  it('navigates to About page when clicking the link', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
    cy.contains('h1', 'About Tigu Platform');
  });
});

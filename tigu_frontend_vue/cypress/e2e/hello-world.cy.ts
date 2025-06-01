/// <reference types="cypress" />

describe('Tigu Platform Home Page', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load the home page successfully', () => {
    // Check that the page loads and has basic structure
    cy.get('body').should('be.visible');
    cy.title().should('contain', 'Tigu');
  });

  it('should have navigation elements', () => {
    // Check for basic navigation or header elements
    cy.get('header').should('exist');
  });

  it('should display main content sections', () => {
    // Check for main content areas that should exist regardless of i18n
    cy.get('main, .home, .container').should('exist');
  });

  it('should have interactive elements', () => {
    // Check for buttons and links
    cy.get('button, a[href]').should('exist');
  });

  it('should be responsive', () => {
    // Test different viewport sizes
    cy.viewport(1280, 720);
    cy.get('body').should('be.visible');
    
    cy.viewport(768, 1024);
    cy.get('body').should('be.visible');
    
    cy.viewport(375, 667);
    cy.get('body').should('be.visible');
  });
});
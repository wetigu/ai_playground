const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4173', // Vite preview server port (matches CI)
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    // eslint-disable-next-line no-unused-vars
    setupNodeEvents(_on, _config) {
      // implement node event listeners here
    },
    video: false,
    screenshotOnRunFailure: false,
  },
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
  },
});
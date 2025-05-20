tigu_frontend_vue/
├── README.md                # Project documentation
├── index.html              # HTML entry point
├── package.json            # NPM dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── tsconfig.node.json      # TypeScript config for Node.js
├── vite.config.ts          # Vite build configuration
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── public/                 # Static assets
│   ├── favicon.ico         # Site favicon
│   └── robots.txt          # Search engine instructions
└── src/                    # Source code
    ├── main.ts             # Application entry point
    ├── App.vue             # Root Vue component
    ├── assets/             # Project assets
    │   └── styles/         # CSS/SCSS styles
    │       └── main.scss   # Main stylesheet
    ├── components/         # Reusable Vue components
    │   └── common/         # Common UI components
    │       └── Button.vue  # Button component
    ├── composables/        # Vue composition API hooks
    │   └── useApi.ts       # API interaction hook
    ├── router/             # Vue Router configuration
    │   └── index.ts        # Routes definition
    ├── services/           # External service integrations
    │   └── api.ts          # API client
    ├── store/              # Pinia state management
    │   ├── index.ts        # Store exports
    │   └── modules/        # Store modules
    │       └── counter.ts  # Counter store example
    ├── types/              # TypeScript type definitions
    │   └── index.ts        # Common types
    ├── utils/              # Utility functions
    │   └── index.ts        # Helpers and utilities
    └── views/              # Page components
        ├── HomeView.vue    # Home page
        └── AboutView.vue   # About page
├── tests/                  # Test files
    ├── unit/               # Unit tests
    │   └── Button.spec.ts  # Button component test
    └── e2e/                # End-to-end tests
        └── home.cy.ts      # Home page test

# tigu_platform_frontend

Vue.js + PWA frontend for the Tigu platform.
# npm install vue-i18@next need to run in order for the project to work
## Project Structure

- `public/`: Static assets that will be served as-is.
- `src/`: Main source code.
  - `assets/`: Static assets that will be processed by the build system.
  - `components/`: Reusable Vue components.
  - `views/`: Page components corresponding to routes.
  - `router/`: Vue Router configuration.
  - `store/`: Vuex/Pinia store for state management.
  - `composables/`: Vue composition API functions.
  - `services/`: API client services.
  - `types/`: TypeScript type definitions.
  - `utils/`: Utility functions.
- `tests/`: Test suite.
- `.env.example`: Example environment variables.
- `vite.config.ts`: Vite configuration.
- `tsconfig.json`: TypeScript configuration.

## Setup

1. Clone the repository.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env` and update the variables.
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Build for production:
   ```bash
   npm run build
   ```

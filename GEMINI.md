# Medible Project `GEMINI.md`

This document provides a comprehensive overview of the Medible project, its structure, and key development tasks. It is intended to be a quick-start guide for developers and for the Gemini CLI to understand the project context.

## 1. Project Overview

Medible is a full-stack web application designed to help users check for potential interactions between their medications and the foods they eat. The application allows users to register, manage a list of their current medications, and search for foods to see if they pose an interaction risk.

The project is architected as a decoupled frontend and backend:

-   **Backend:** A Python-based REST API built with Flask. It handles user authentication, medication management, and proxies requests to external services (OpenFDA and USDA) to fetch drug and food data.
-   **Frontend:** A modern single-page application (SPA) built with Vue.js 3 and Vite. It provides the user interface for all application features.
-   **Containerization:** The entire application stack is containerized using Docker and managed with Docker Compose for consistent development and production environments.

## 2. Core Technologies

| Area      | Technology                                    |
| :-------- | :-------------------------------------------- |
| **Backend** | Python 3.11+, Flask, SQLAlchemy, Gunicorn     |
| **Frontend**| Vue.js 3 (Composition API), Vite, TypeScript  |
| **Database**| PostgreSQL (Production), SQLite (Development) |
| **Styling** | Tailwind CSS                                  |
| **State**   | Pinia                                         |
| **Auth**    | JWT (via Flask-JWT-Extended)                  |
| **Testing** | Pytest (Backend), Vitest/Vue-TSC (Frontend)   |
| **Tooling** | Docker, Node.js 20+, Prettier, ESLint, Black  |

## 3. Project Structure

The project is a monorepo with two main directories: `backend` and `frontend`.

```
/
├── backend/            # Flask API
│   ├── app/            # Core application module
│   │   ├── models/     # SQLAlchemy DB models
│   │   ├── routes/     # API endpoints (Blueprints)
│   │   └── services/   # Business logic and external API clients
│   ├── migrations/     # Alembic database migrations
│   ├── tests/          # Pytest test suite
│   ├── requirements.txt# Python dependencies
│   └── run.py          # Application entrypoint
│
├── frontend/           # Vue.js SPA
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── views/      # Page-level components
│   │   ├── stores/     # Pinia state management stores
│   │   ├── services/   # Frontend API client
│   │   └── router/     # Vue Router configuration
│   ├── package.json    # Node.js dependencies and scripts
│   └── vite.config.ts  # Vite build configuration
│
├── docker-compose.yml  # Defines services for local development/prod
└── README.md           # Main project README
```

## 4. Running the Application

### Using Docker (Recommended)

The simplest way to run the entire application stack is with Docker Compose.

```bash
# Build and start all services in detached mode
docker-compose up --build -d
```

-   **Frontend** will be available at `http://localhost:80`
-   **Backend API** will be available at `http://localhost:5000`

To stop the services:
`docker-compose down`

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# You may need to add API keys to the .env file
flask db upgrade
python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 5. Backend Development

-   **Dependencies:** Managed with `pip` and `requirements.txt`.
-   **Code Style:** Use `black` and `flake8`.
-   **Testing:** Run tests with `pytest`.
    ```bash
    cd backend
    pytest
    ```
-   **Database Migrations:** Handled by `Flask-Migrate` (which uses Alembic).
    -   To create a new migration: `flask db migrate -m "Description of changes"`
    -   To apply migrations: `flask db upgrade`

## 6. Frontend Development

-   **Dependencies:** Managed with `npm` and `package.json`.
-   **Key `package.json` Scripts:**
    -   `npm run dev`: Start the development server with hot-reload.
    -   `npm run build`: Create a production-ready build of the app.
    -   `npm run lint`: Lint the codebase using ESLint.
    -   `npm run format`: Format the code using Prettier.
-   **Code Style:** Enforced by ESLint and Prettier. It's recommended to run `npm run lint` and `npm run format` before committing changes.
-   **Type Checking:** The project uses TypeScript. Use `npm run type-check` to run `vue-tsc`.

## Coding Preferences

## Frontend Rules

1. No Inline Styles
Never use style attributes or style bindings. Always use Tailwind CSS utility classes. For dynamic styles, use conditional classes with the cn utility function.

2. Prioritize UX and Accessibility
Design mobile-first starting with small screens then scaling up. Use semantic HTML elements like button, nav, main, and article. Add ARIA labels for interactive elements. Support keyboard navigation with proper focus states. Always include loading states, error states, and empty states for async operations.

3. Modular Component Structure
One component per file. Keep components under 200 lines and extract sub-components if larger. Keep functions under 50 lines. Organize components by feature not by type.

4. Type Safety and Constants
Use TypeScript everywhere with no any types. Define props and emits with TypeScript generics. Never hardcode strings or magic numbers. Extract all values to named constants.

5. State and Data Flow
Use Pinia stores for global state like auth and user data. Use composables for reusable logic. Follow props down and emits up pattern. Avoid prop drilling beyond 2 levels. Keep components stateless when possible.

6. Theme Aware Design
Support all 6 themes which are Light, Dark. Use CSS variables for theme colors. Test components in both light and dark modes. Use shadcn-vue components as the base since they are already theme-aware.

7. Performance Best Practices
Lazy load routes and heavy components. Use v-once for static content. Debounce search inputs. Avoid v-if and v-for on the same element. Always use key attribute in v-for loops.

8. Testing and Reliability
Write unit tests for components and composables. Test user interactions and edge cases. Mock API calls in tests. Test accessibility with screen reader compatibility. Ensure all forms have proper validation feedback.

## Backend Rules

1. Structured API Responses
Always return JSON with consistent structure. Include success boolean, data object, message string, and request ID for tracing. Use proper HTTP status codes. Never expose stack traces in error responses.

2. Separation of Concerns
Routes only handle HTTP request and response. Services contain business logic. Models define data structure and database interactions. Never put business logic in routes.

3. Error Handling and Logging
Create custom exception classes for different error types. Use a global error handler. Use structured logging with request context. Log at appropriate levels including debug, info, warning, and error. Never log sensitive data like passwords or tokens.

4. Security First
Validate all inputs for type, length, and format. Sanitize data before database queries. Use parameterized queries which SQLAlchemy handles automatically. Set proper JWT token expiration. Add rate limiting on authentication endpoints.

5. Database Best Practices
Use migrations for all schema changes. Add indexes on frequently queried columns. Use soft deletes with deleted_at timestamp for user data. Add created_at and updated_at timestamps on all models.

6. Testing and Reliability
Write unit tests for services. Write integration tests for routes. Test error cases not just happy paths. Mock external APIs like OpenFDA and USDA in tests.
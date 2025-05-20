# tigu_backend_fastapi

FastAPI backend for the Tigu platform.

## Project Structure

- `app/`: Main application code.
  - `api/`: API endpoints (routers).
  - `core/`: Core settings, security, logging.
  - `crud/`: Create, Read, Update, Delete operations.
  - `db/`: Database session and base models.
  - `models/`: SQLAlchemy ORM models.
  - `schemas/`: Pydantic schemas for data validation.
  - `services/`: Business logic services.
  - `utils/`: Utility functions.
- `migrations/`: Alembic database migration scripts.
- `scripts/`: Helper scripts (e.g., for starting the app, initializing DB).
- `tests/`: Test suite.
- `.env.example`: Example environment variables.
- `pyproject.toml`: Project metadata and dependencies (Poetry).
- `Dockerfile`: For containerizing the application.
- `alembic.ini`: Alembic configuration.

## Setup

1.  Clone the repository.
2.  Create a virtual environment and install dependencies:
    ```bash
    poetry install
    ```
3.  Copy `.env.example` to `.env` and update the variables.
4.  Run database migrations:
    ```bash
    alembic upgrade head
    ```
5.  Start the application:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```

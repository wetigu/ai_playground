# Start with a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for psycopg2 and other potential needs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.5.1 # Pin Poetry version for stable builds

# Copy only the files necessary for poetry to install dependencies
COPY pyproject.toml poetry.lock ./

# Install project dependencies
# --no-root: Do not install the project itself as editable, install from definition
# --no-dev: Do not install development dependencies (like pytest) in production image
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

# Copy the rest of the application code into the container
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./alembic.ini ./

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# It will look for an 'app' variable in 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

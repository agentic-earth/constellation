# Use the official Python image from the Docker Hub
ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION}

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
# FIXME: Remove the --reload flag for production
CMD ["poetry", "run", "uvicorn", "orchestrator.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
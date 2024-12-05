ARG PYTHON_VERSION=3.9-slim
FROM python:${PYTHON_VERSION}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry and configure it to install dependencies globally
RUN pip install poetry

# Install the dependencies
RUN poetry install --no-root 

# Copy the rest of the application code to the container
COPY . .

# Generate Prisma client
RUN poetry run prisma generate

# Expose port
EXPOSE 8000

# Run the application
# FIXME: Remove the --reload flag for production
CMD ["poetry", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Use Python 3.9-slim as the base image
ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION}

# Install necessary packages
RUN apt-get update && apt-get install -y \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages, including pillow for image processing
RUN pip install \
    dagster \
    dagster-postgres \
    dagster-docker \
    pandas 
    
RUN pip install gdown
RUN pip install dagster_aws

# Set the working directory
WORKDIR /opt/dagster/app

# Copy your application code into the container
COPY . /opt/dagster/app

# Expose the port and run the dagster gRPC server
EXPOSE 4000
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "./orchestrator/assets/repository.py"]

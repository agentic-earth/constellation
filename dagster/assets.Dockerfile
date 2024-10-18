# Use Python 3.9-slim as the base image
ARG PYTHON_VERSION=3.9-slim
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
    pandas \
    tensorflow \
    tensorflow_datasets \
    jax \
    flax \
    pillow

# Set the working directory
WORKDIR /opt/dagster/app

# Copy your application code into the container
COPY . /opt/dagster/app

# Copy the Python script to create the dataset
COPY create_dataset.py /opt/dagster/app/create_dataset.py

# Run the dataset creation script
RUN python /opt/dagster/app/create_dataset.py

# Set environment variable for dataset directory
ENV DATASET_DIR=/data/dataset

# Expose the port and run the dagster gRPC server
EXPOSE 4000
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "./orchestrator/assets/repository.py"]

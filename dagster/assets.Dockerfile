ARG PYTHON_VERSION=3.9-slim
FROM python:${PYTHON_VERSION}

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

RUN pip install \
    dagster \
    dagster-postgres \
    dagster-docker \
    pandas
# Add repository code

WORKDIR /opt/dagster/app

COPY . /opt/dagster/app

# Run dagster gRPC server on port 4000
EXPOSE 4000

# CMD allows this to be overridden from run launchers or executors that want
# to run other commands against your repository
# CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "repository.py"]
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "./orchestrator/assets/repository.py"]

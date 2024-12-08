# Dagster libraries to run both dagster-webserver and the dagster-daemon.
# Does not need to have access to any pipeline code.
ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION}

# Install necessary Python packages
RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker \
    pandas \
    gdown \
    dagster_aws

# Set DAGSTER_HOME and copy configuration files
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME
COPY dagster.yaml workspace.yaml $DAGSTER_HOME

# Copy the .env file into the image
COPY .env $DAGSTER_HOME/.env

# Copy the load_env.sh script into the image
COPY load_env.sh /usr/local/bin/load_env.sh
RUN chmod +x /usr/local/bin/load_env.sh

# Set working directory
WORKDIR $DAGSTER_HOME

# Run the load_env.sh script as the container's entrypoint
CMD ["/usr/local/bin/load_env.sh"]

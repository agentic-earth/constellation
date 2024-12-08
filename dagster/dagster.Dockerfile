# Dagster libraries to run both dagster-webserver and the dagster-daemon. Does not
# need to have access to any pipeline code.
ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION}

RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker \
    pandas 

RUN pip install gdown
RUN pip install dagster_aws
RUN pip install python-dotenv

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY dagster.yaml workspace.yaml $DAGSTER_HOME

ENV AWS_ACCESS_KEY_ID=AKIASE5KQ2YESPUIVLWS
ENV AWS_SECRET_ACCESS_KEY=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

WORKDIR $DAGSTER_HOME

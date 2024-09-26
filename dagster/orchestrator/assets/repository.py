from dagster import (
    Definitions,
    FilesystemIOManager,
    graph,
    job,
    op,
    repository,
    schedule,
    OpExecutionContext,
)

# from dagster_docker import docker_executor


@op(config_schema={"credentials": dict})
def import_s3(context: OpExecutionContext) -> str:
    credentials = context.op_config["credentials"]
    context.log.info(f"Importing data with credentials: {credentials}")
    data = "file data"
    context.log.info(f"Data imported: {data}")
    return data


@op(config_schema={"credentials": dict})
def export_s3(context: OpExecutionContext, data: str):
    credentials = context.op_config["credentials"]
    context.log.info(f"Exporting data with credentials: {credentials}")
    context.log.info(f"Data to export: {data}")
    context.log.info(f"Data exported: {data}")
    return data


@graph
def my_pipeline():
    data = import_s3()
    result = export_s3(data)
    return result


# Example usage
my_pipeline_job = my_pipeline.to_job(
    # executor_def=docker_executor,
    config={
        "ops": {
            "import_s3": {
                "config": {
                    "credentials": {
                        "access_key": "your_access_key",
                        "secret_key": "your_secret_key",
                    }
                }
            },
            "export_s3": {
                "config": {
                    "credentials": {
                        "access_key": "your_access_key",
                        "secret_key": "your_secret_key",
                    }
                }
            },
        }
    },
)


@repository
def deploy_docker_repository():
    return [my_pipeline_job]

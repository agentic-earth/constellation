from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

DAGSTER_GRAPHQL_URL = "http://dagster_webserver:3000/graphql"


@app.post("/execute")
async def run_dagster_job_with_config():
    """
    Run a Dagster job with a specific config for ops.
    """
    # Define the custom configuration for the ops
    job_config = {
        "ops": {
            "generate_dynamic_job_configs": {
                "config": {
                    "instructions": [
                        {
                            "operation": "write_csv",
                            "parameters": {
                                "result": {
                                    "operation": "math_block",
                                    "parameters": {
                                        "constant": 5,
                                        "data": {
                                            "operation": "mock_csv_data",
                                            "parameters": {},
                                        },
                                        "operand": "add",
                                    },
                                }
                            },
                        }
                    ]
                }
            }
        }
    }

    # Define the GraphQL mutation for launching the job with config
    graphql_query = {
        "query": """
        mutation($runConfig: RunConfigData) {
            launchPipelineExecution(
                executionParams: {
                    selector: {
                        pipelineName: "build_execute_job",
                        repositoryLocationName: "constellation",
                        repositoryName: "main"
                    },
                    runConfigData: $runConfig,
                    mode: "default"
                }
            ) {
                __typename
                ... on LaunchPipelineRunSuccess {
                    run {
                        runId
                    }
                }
                ... on PythonError {
                    message
                    stack
                }
            }
        }
        """,
        "variables": {
            "runConfig": job_config  # Pass the custom job config to the GraphQL query
        },
    }

    # Send a POST request to the Dagster GraphQL API
    try:
        response = requests.post(DAGSTER_GRAPHQL_URL, json=graphql_query)
        response_data = response.json()
        print(response_data)

        # Check if the job was successfully launched
        if (
            response_data.get("data", {})
            .get("launchPipelineExecution", {})
            .get("__typename")
            == "LaunchRunSuccess"
        ):
            run_id = response_data["data"]["launchPipelineExecution"]["run"]["runId"]
            return {"status": "success", "run_id": run_id}
        else:
            error_message = response_data["data"]["launchPipelineExecution"].get(
                "message", "Unknown error"
            )
            return {"status": "failure", "message": error_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

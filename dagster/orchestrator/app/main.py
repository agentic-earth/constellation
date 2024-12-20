from fastapi import FastAPI, HTTPException, Request
import requests
import uuid

app = FastAPI()

DAGSTER_GRAPHQL_URL = "http://dagster_webserver:3000/graphql"


@app.post("/execute")
async def run_dagster_job_with_config(request: Request):
    """
    Run a Dagster job with a specific config for ops.
    """
    # Parse the request body
    instructions = await request.json()
    instructions = instructions.get("instructions")

    if not instructions or not isinstance(instructions, list):
        raise HTTPException(status_code=400, detail="No instructions provided")

    # Generate a unique ID for the job
    unique_id = str(uuid.uuid4())

    # Define the custom configuration for the ops
    job_config = {
        "ops": {
            "generate_dynamic_job_configs": {
                "config": {"raw_input": instructions, "unique_id": unique_id}
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
                        pipelineName
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

        # Check if the job was successfully launched
        if (
            response_data.get("data", {})
            .get("launchPipelineExecution", {})
            .get("__typename")
            == "LaunchRunSuccess"
        ):
            return {
                "status": "success",
                "run_id": unique_id,
            }
        else:
            print(response_data)
            error_message = response_data["data"]["launchPipelineExecution"].get(
                "message", "Unknown error"
            )
            return {"status": "failure", "message": error_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


import uvicorn


def main():
    """
    Main function to launch the FastAPI application using Uvicorn.
    The API will be accessible at http://localhost:8082
    """
    # logger.log("main", "info", "Starting Dagster Orchestrator on port 8082.")
    uvicorn.run(
        "dagster.orchestrator.app.main:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()

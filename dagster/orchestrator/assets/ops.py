import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import base64
from dagster import Any, In, OpExecutionContext, Out, op, failure_hook, HookContext
import traceback
import requests
import pandas as pd
import operator
import zipfile
import os
import sys
import gdown


@op(
    name="import_from_google_drive",
    ins={"file_id": In(str)},
    out=Out(dict[str, Any]),
)
def import_from_google_drive(
    context: OpExecutionContext, file_id: str
) -> dict[str, Any]:
    # Import the data from Google Drive using gdown
    context.log.info("Starting import_from_google_drive...")
    download_url = f"https://drive.google.com/uc?id={file_id}"
    try:
        # Download the file using gdown
        output = "download.zip"
        gdown.download(download_url, output, quiet=False)
        context.log.info("Downloaded file successfully using gdown.")

        # Unzip the file
        with zipfile.ZipFile(output, "r") as zip_ref:
            zip_ref.extractall("data")

        # Save files to a dictionary structure
        data_dict = {}
        for root, dirs, files in os.walk("data"):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, "data")

                # Read the file in binary mode and store it in the dictionary
                with open(file_path, "rb") as f:
                    data_dict[relative_path] = f.read()

        context.log.info(f"Loaded {len(data_dict.values())} files into dictionary.")
        return data_dict

    except Exception as e:
        context.log.error(f"An error occurred: {e}")
        return {}


@op(
    name="dict_to_list",
    ins={"data": In(dict[str, Any])},
    out=Out(list[bytes]),
)
def dict_to_list(context: OpExecutionContext, data: dict[str, Any]) -> list[bytes]:
    return list(data.values())


@op(name="deploy_model", ins={"model": In(str)})
def deploy_model(context: OpExecutionContext, model: str) -> None:
    context.log.info(f"Deploying model: {model}")

    # Define the endpoint and payload
    MODEL_ENDPOINT = "http://model_api:8000"
    endpoint = f"{MODEL_ENDPOINT}/deploy?model_name={model}"
    payload = {"model_name": model}

    # Make a POST request to the endpoint
    response = requests.get(endpoint, json=payload)

    if response.status_code == 200:
        context.log.info(f"Model deployed successfully: {response.json()}")
    else:
        context.log.error(
            f"Failed to deploy model. Status code: {response.status_code}, Response: {response.text}"
        )
        raise Exception(
            f"Failed to deploy model. Status code: {response.status_code}, Response: {response.text}"
        )


@op(name="delete_model", ins={"model": In(str)})
def delete_model(context: OpExecutionContext, model: str) -> None:
    context.log.info(f"Deleting model service: {model}")

    # Define the endpoint and payload
    MODEL_ENDPOINT = "http://model_api:8000"
    endpoint = f"{MODEL_ENDPOINT}/delete?model_name={model}"
    payload = {"model_name": model}

    # Make a POST request to the endpoint
    response = requests.delete(endpoint, json=payload)

    if response.status_code == 200:
        context.log.info(f"Model service deleted successfully: {response.json()}")
    else:
        context.log.error(
            f"Failed to delete model service. Status code: {response.status_code}, Response: {response.text}"
        )


# Model infrence
@op(
    name="model_inference",
    ins={"data": In(list[bytes]), "model": In(str)},
    out=Out(dict[str, Any]),
)
def model_inference(
    context: OpExecutionContext,
    data: list[bytes],
    model: str,
) -> dict[str, Any]:
    context.log.info(f"Running inference on {len(data)} images")
    MODEL_ENDPOINT = f"http://model_api:8000"
    endpoint = f"{MODEL_ENDPOINT}/infer?model_name={model}"
    batch_size = 2
    batches = [
        data[i : min(len(data), i + batch_size)]
        for i in range(0, len(data), batch_size)
    ]

    results = []
    for batch in batches:
        payload = {"data": [base64.b64encode(image).decode("utf-8") for image in batch]}
        response = requests.post(endpoint, json=payload)
        context.log.info(f"Response: {response.text}")
        results.append(response.json().get("output"))

    if len(results) == len(batches):
        context.log.info(f"Model inference successful: {results}")
        return {"results": results}
    else:
        context.log.error(
            f"Failed to run model inference. Status code: {response.status_code}, Response: {response.text}"
        )
        return {}


@op(name="mock_csv_data", out=Out())
def mock_csv_data(context: OpExecutionContext) -> pd.DataFrame:
    data = [["column1", "column2", "column3"], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
    context.log.info(f"Mock data: {data}")

    df = pd.DataFrame(data[1:], columns=data[0])
    context.log.info(f"DataFrame created from mock data:\n{df}")

    return df


@op(name="write_csv", ins={"result": In(pd.DataFrame)}, out=Out(str))
def write_csv(context: OpExecutionContext, result: pd.DataFrame) -> str:
    context.log.info(f"Received data to write to CSV:\n{result}")

    result.to_csv("output.csv", index=False)

    context.log.info(f"Data written to output.csv")
    return "output.csv"


@op(
    name="math_block",
    ins={
        "data": In(pd.DataFrame),
        "operand": In(str),
        "constant": In(float),
    },
    out=Out(pd.DataFrame),
)
def math_block(
    context: OpExecutionContext,
    operand: str,
    constant: float,
    data: pd.DataFrame,
) -> pd.DataFrame:
    operation_func = getattr(operator, operand)
    context.log.info(
        f"Applying operation '{operand}' with constant {constant} to DataFrame."
    )
    result_df = data.map(lambda x: operation_func(x, constant))
    context.log.info(f"Resulting DataFrame:\n{result_df}")
    return result_df


@failure_hook(name="publish_failure")
def publish_failure(context: HookContext) -> None:
    """
    Publish the status of the job to the orchestrator.

    Args:
        context (HookContext): The context of the failure hook.
    """
    status = "failed"

    # Get run id from context
    run_id = context.run_id
    context.log.info(f"Publishing status: {status} for job: {run_id}")

    # Get the status from the context
    op_exception: BaseException = context.op_exception
    message = op_exception.__traceback__.format_exc()

    # Post to the status endpoint
    publish_status_helper(context, run_id, status, message)


@op(name="publish_success")
def publish_success(context: OpExecutionContext) -> None:
    status = "success"
    run_id = context.run_id
    publish_status_helper(context, run_id, status, "")


def publish_status_helper(
    context: HookContext, run_id: str, status: str, message: str
) -> None:
    """
    Publish the status of the job to the main API.

    Args:
        context (HookContext): The context of the failure hook.
        run_id (str): The id of the run.
        status (str): The status of the job.
        message (str): The message of the job.
    """
    MAIN_ENDPOINT = "http://main_api:8000"
    endpoint = f"{MAIN_ENDPOINT}/pipelines/status/{run_id}/{status}"
    payload = {"message": message}
    response = requests.put(endpoint, json=payload)
    context.log.info(f"Status published: {response.text}")

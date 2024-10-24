from dagster import Any, In, OpExecutionContext, Out, op
import requests
import pandas as pd
import operator
import zipfile
import os
import sys

from orchestrator.assets.constants import *
import gdown

# Adjust resource limits if not on macOS
if sys.platform != "darwin":
    import resource

    low, high = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (high, high))


@op(
    name="import_zip_from_google_drive",
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
                
                # Log the file structure
                context.log.info(f"Extracted file: {relative_path}")

                # Read the file in binary mode and store it in the dictionary
                with open(file_path, "rb") as f:
                    data_dict[relative_path] = f.read()

        context.log.info("Loaded files into dictionary.")
        return data_dict

    except Exception as e:
        context.log.error(f"An error occurred: {e}")
        return {}



@op(name="deploy_model", ins={"model": In(str)})
def deploy_model(context: OpExecutionContext, model: str) -> None:
    context.log.info(f"Deploying model: {model}")

    # Define the endpoint and payload
    MODEL_ENDPOINT = f"{MODEL_ENDPOINT}/deploy"
    payload = {"model_name": model, "service_name": f"{model}-service"}

    # Make a POST request to the endpoint
    response = requests.post(MODEL_ENDPOINT, json=payload)

    if response.status_code == 200:
        context.log.info(f"Model deployed successfully: {response.json()}")
    else:
        context.log.error(
            f"Failed to deploy model. Status code: {response.status_code}, Response: {response.text}"
        )


@op(name="delete_model", ins={"service_name": In(str)})
def delete_model(context: OpExecutionContext, service_name: str) -> None:
    context.log.info(f"Deleting model service: {service_name}")

    # Define the endpoint and payload
    MODEL_ENDPOINT = f"{MODEL_ENDPOINT}/delete"
    payload = {"service_name": service_name}

    # Make a POST request to the endpoint
    response = requests.post(MODEL_ENDPOINT, json=payload)

    if response.status_code == 200:
        context.log.info(f"Model service deleted successfully: {response.json()}")
    else:
        context.log.error(
            f"Failed to delete model service. Status code: {response.status_code}, Response: {response.text}"
        )


# Model infrence


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
    operand = getattr(operator, operand)

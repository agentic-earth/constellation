from pathlib import Path
import random
from typing import List
from dagster import (
    asset,
    Definitions,
    FilesystemIOManager,
    graph,
    job,
    op,
    repository,
    schedule,
    OpExecutionContext,
    define_asset_job,
)

@asset
def process_csv_data(context: OpExecutionContext) -> List[List[int]]:
    context.log.info(f"Current working directory: {Path.cwd()}") #Needed to figure out why code wasnt seeing file
    file_path = Path("orchestrator/assets/Test.csv")
    data = []
    context.log.info(f"Reading data from {file_path}")
    try:
        with file_path.open('r') as file:
            lines = file.readlines()
            for line in lines[1:]:  # Skip header
                data.append([int(value) for value in line.strip().split(',')])
        context.log.info(f"Data read: {data}")
    except FileNotFoundError:
        context.log.error(f"File not found: {file_path}")
    except Exception as e:
        context.log.error(f"Error reading file: {e}")
    return data

@asset
def write_result_to_csv(context: OpExecutionContext, result: List[List[int]]) -> List[List[int]]:
    context.log.info(f"Current working directory: {Path.cwd()}")
    output_file_path = Path("orchestrator/assets/Result.csv")
    context.log.info(f"Writing result to {output_file_path}")
    try:
        with output_file_path.open('w') as file:
            for sublist in result:
                file.write(','.join(map(str, sublist)) + '\n')
        context.log.info(f"Result written to {output_file_path}")
    except Exception as e:
        context.log.error(f"Error writing file: {e}")
    return result

@op
def choose_operations(context) -> List[str]:
    operations_sequence = ["multiply", "add", "subtract", "divide"]
    chosen_ops = random.sample(operations_sequence, 2)  # Dynamically picking 2 random ops
    context.log.info(f"Chosen operations: {chosen_ops}")
    return chosen_ops

@op
def multiply(nums: List[int]) -> List[int]:
    return [x * 2 for x in nums]

@op
def divide(nums: List[int]) -> List[int]:
    return [x // 2 if x != 0 else 0 for x in nums]  # Avoid division by zero

@op
def add(nums: List[int]) -> List[int]:
    return [x + 2 for x in nums]

@op
def subtract(nums: List[int]) -> List[int]:
    return [x - 2 for x in nums]

@op
def apply_operations(context, operations: List[str], data: List[List[int]]) -> List[List[int]]:
    """
    Applies a sequence of operations to each row in the CSV data.
    """
    context.log.info(f"Applying operations: {operations}")
    processed_data = data
    for operation in operations:
        context.log.info(f"Applying operation: {operation}")
        if operation == "multiply":
            processed_data = [multiply(row) for row in processed_data]
        elif operation == "divide":
            processed_data = [divide(row) for row in processed_data]
        elif operation == "add":
            processed_data = [add(row) for row in processed_data]
        elif operation == "subtract":
            processed_data = [subtract(row) for row in processed_data]
        else:
            raise ValueError(f"Unknown operation: {operation}")
        context.log.info(f"Data after {operation}: {processed_data}")
    return processed_data

@op(config_schema={"credentials": dict})
def import_s3(context: OpExecutionContext) -> int:
    credentials = context.op_config["credentials"]
    context.log.info(f"Importing data with credentials: {credentials}")
    data = 1  # Placeholder for actual S3 import logic
    context.log.info(f"Data imported: {data}")
    return data

@op(config_schema={"credentials": dict})
def export_s3(context: OpExecutionContext, data: int):
    credentials = context.op_config["credentials"]
    context.log.info(f"Exporting data with credentials: {credentials}")
    context.log.info(f"Data to export: {data}")
    # Placeholder for actual S3 export logic
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

@graph
def dynamic_math_operations():
    data = process_csv_data()
    operations = choose_operations()
    processed_data = apply_operations(operations, data)
    write_result_to_csv(processed_data)

dynamic_math_operations_job = dynamic_math_operations.to_job()

@repository
def deploy_docker_repository():
    return [my_pipeline_job, dynamic_math_operations_job]


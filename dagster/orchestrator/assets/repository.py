from dagster import (
    Field,
    Shape,
    graph,
    op,
    repository,
    OpExecutionContext,
)
from dataclasses import dataclass

from orchestrator.assets.ops import *
from orchestrator.assets.jobs import *


@dataclass
class CallableOperation:
    operation: str
    parameters: dict[str, any]


@op(
    config_schema=Shape(
        {
            "instructions": Field(
                Shape(
                    {
                        "operation": Field(
                            str,
                            description="Operation to be performed",
                            default_value="write_csv",
                        ),
                        "parameters": Field(
                            dict,
                            description="Parameters required for the operation",
                            default_value={
                                "result": {
                                    "operation": "math_block",
                                    "parameters": {
                                        "operand": "add",
                                        "constant": 10.0,
                                        "data": {"operation": "mock_csv_data"},
                                    },
                                }
                            },
                        ),
                    }
                ),
                description="Instructions to build the job",
                is_required=True,
            )
        }
    )
)
def job_assembler(context: OpExecutionContext) -> CallableOperation:
    context.log.info("Parsing instructions to create job")

    def parse_parameters(params):
        parsed_params = {}
        for key, value in params.items():
            if isinstance(value, dict) and "operation" in value:
                _ = globals()[value["operation"]]
                nested_params = value.get("parameters", {})

                context.log.info(f"Nested job: {value['operation']}")
                parsed_params[key] = CallableOperation(
                    value["operation"], parse_parameters(nested_params)
                )
            else:
                parsed_params[key] = value
        return parsed_params

    instruction = context.op_config["instructions"]
    if "operation" not in instruction:
        raise ValueError("Operation not found in instruction")
    _ = globals()[instruction["operation"]]

    parameters = {}
    if "parameters" in instruction:
        parameters = parse_parameters(instruction["parameters"])

    context.log.info(f"Instruction parsed: {instruction['operation']}")

    return CallableOperation(instruction["operation"], parameters)


@op
def job_executer(context: OpExecutionContext, operations: CallableOperation) -> None:
    context.log.info("Executing job operations")

    def execute_helper(operations):
        context.log.info(f"Executing operation: {operations.operation}")

        if operations.operation not in globals():
            raise ValueError(f"Operation {operations.operation} not found")

        computed_params = {}
        if operations.parameters:
            for key, value in operations.parameters.items():
                if isinstance(value, CallableOperation):
                    result = execute_helper(value)
                    computed_params[key] = result
                else:
                    computed_params[key] = value

        context.log.info(f"Executing operation: {operations.operation}")
        fn = globals()[operations.operation]
        return fn(ctx=context, **computed_params)

    execute_helper(operations)

    context.log.info("Job operations executed")


@graph()
def dynamic_math():
    instructions = job_assembler()
    job_executer(operations=instructions)


dynamic_math_job = dynamic_math.to_job(
    config={
        "ops": {
            "job_assembler": {
                "config": {
                    "instructions": {
                        "operation": "write_csv",
                        "parameters": {
                            "result": {
                                "operation": "math_block",
                                "parameters": {
                                    "operand": "add",
                                    "constant": 10.0,
                                    "data": {"operation": "mock_csv_data"},
                                },
                            },
                        },
                    }
                }
            }
        }
    }
)


dynamic_math_job = dynamic_math.to_job()


@repository
def deploy_docker_repository():
    return [dynamic_math_job]

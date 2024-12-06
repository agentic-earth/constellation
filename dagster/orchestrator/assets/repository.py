import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dagster import (
    mem_io_manager,
    in_process_executor,
    Any,
    DependencyDefinition,
    DynamicOut,
    DynamicOutput,
    Field,
    GraphDefinition,
    JobDefinition,
    NodeInvocation,
    job,
    repository,
    op,
    DagsterInvariantViolationError,
)
from dataclasses import dataclass
from typing import Any as TypingAny, Dict, Tuple, Optional

from orchestrator.assets.ops import *
from orchestrator.assets.jobs import *

OP_DEFS = [
    import_from_google_drive,
    deploy_model,
    delete_model,
    dict_to_list,
    model_inference,
    mock_csv_data,
    write_csv,
]


@dataclass
class CallableOperation:
    operation: str
    parameters: Dict[str, TypingAny]


def parse_instructions(input: dict) -> CallableOperation:
    if "operation" not in input:
        raise ValueError("Operation not found in instruction")

    operation = input["operation"]
    if operation not in [op.name for op in OP_DEFS]:
        raise ValueError(f"Operation '{operation}' is not defined in OP_DEFS.")

    parameters = {}

    for key, value in input.get("parameters", {}).items():
        if isinstance(value, dict) and "operation" in value:
            parameters[key] = parse_instructions(value)
        else:
            parameters[key] = value

    return CallableOperation(operation=operation, parameters=parameters)


def generate_dependencies_and_run_config(
    instruction: CallableOperation,
) -> Tuple[Dict, Dict]:
    result = {}
    run_config = {"ops": {}}
    alias_counter = [1]

    def traverse(node: CallableOperation) -> str:
        alias = f"{node.operation} ({alias_counter[0]})"
        alias_counter[0] += 1

        current_node = NodeInvocation(name=node.operation, alias=alias)

        dependencies = {}
        input_values = {}
        for key, param in node.parameters.items():
            if isinstance(param, CallableOperation):
                dep_alias = traverse(param)
                dependencies[key] = DependencyDefinition(dep_alias)
            else:
                input_values[key] = param

        if (
            input_values
        ):  # This addressed a config input format error that was causing the pipeline to fail
            run_config["ops"][alias] = {  # Retained copy of error if needed
                "inputs": {k: {"value": v} for k, v in input_values.items()}
            }

        result[current_node] = dependencies if dependencies else {}

        return alias

    traverse(instruction)
    return result, run_config


def define_composite_job(name: str, raw_input: dict) -> Tuple[JobDefinition, Dict]:
    instruction: CallableOperation = parse_instructions(input=raw_input)
    deps = {}
    run_config = {}
    deps, run_config = generate_dependencies_and_run_config(instruction)

    filtered_op_defs = [
        op
        for op in OP_DEFS
        if op.name in [key.name.split(" ")[0] for key in deps.keys()]
    ]

    graph = GraphDefinition(
        name=name,
        node_defs=filtered_op_defs,
        dependencies=deps,
    )

    return graph.to_job(), run_config


@op(config_schema={"raw_input": Field(Any)}, out=DynamicOut())
def generate_dynamic_job_configs(context: OpExecutionContext):
    raw_input = context.op_config["raw_input"]
    yield DynamicOutput(raw_input, mapping_key="dynamic_config")


@op
def parse_and_execute_job(context: OpExecutionContext, instructions: list):
    # Dynamically generate a job based on the input
    job_list = []
    for instruction in instructions:
        job, run_config = define_composite_job(
            name="dynamic_job", raw_input=instruction
        )
        context.log.info(f"Created dynamic job: {job.name}")
        job_list.append((job, run_config))

    for job, run_config in job_list:
        context.log.info(f"Executing dynamic job with run_config: {run_config}")
        result = job.execute_in_process(run_config=run_config)

        for event in result.all_events:
            context.log.info(f"Event: {event.message}")

        try:
            dynamic_result = result.output_value()
            context.log.info(f"Dynamic job result: {dynamic_result}")
        except DagsterInvariantViolationError:
            context.log.info("Dynamic job executed without outputs.")


@job(
    config={
        "ops": {
            "generate_dynamic_job_configs": {
                "config": {
                    "raw_input": [
                        {  # Wrap the dictionary in a list
                            "operation": "import_from_google_drive",
                            "parameters": {
                                "file_id": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ",  # Test Directory of photos from before I went to college... lol
                            },
                        }
                    ],
                }
            }
        }
    }
)
def build_execute_job():
    dynamic_configs = generate_dynamic_job_configs()
    dynamic_configs.map(parse_and_execute_job)


@job(
    config={
        "ops": {
            "import_from_google_drive": {
                "inputs": {
                    "file_id": {
                        "value": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ"
                    }  # Correctly pass the file_id under inputs
                }
            }
        }
    }
)
def test_import_from_google_drive_job():
    import_from_google_drive()


@repository(name="main")
def deploy_docker_repository():
    return [build_execute_job, test_import_from_google_drive_job]

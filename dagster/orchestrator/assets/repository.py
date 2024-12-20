import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dagster import (
    DagsterInstance,
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
from typing import Any as TypingAny, Dict, Tuple, Optional, List
import uuid

from dagster_aws.s3 import s3_resource

from orchestrator.assets.ops import *

OP_DEFS = [
    import_from_google_drive,
    export_to_s3,
    deploy_model,
    delete_model,
    dict_to_list,
    model_inference,
    mock_csv_data,
    write_csv,
    publish_success,
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
    instruction: CallableOperation, unique_id: str
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
        else:
            run_config["ops"][alias] = {}
            run_config["ops"][alias]["inputs"] = {}

        # Add unique_id to the run_config
        run_config["ops"][alias]["inputs"]["unique_id"] = {"value": unique_id}

        result[current_node] = dependencies if dependencies else {}

        return alias

    traverse(instruction)
    return result, run_config


def define_composite_job(
    name: str, raw_input: dict, unique_id: str
) -> Tuple[JobDefinition, Dict]:
    instruction: CallableOperation = parse_instructions(input=raw_input)
    deps = {}
    run_config = {}
    deps, run_config = generate_dependencies_and_run_config(
        instruction, unique_id=unique_id
    )

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

    return (
        graph.to_job(
            resource_defs={"s3_resource": s3_resource},
        ),
        run_config,
    )


@op(config_schema={"raw_input": Field(Any), "unique_id": Field(str)}, out=DynamicOut())
def generate_dynamic_job_configs(context: OpExecutionContext):
    raw_input = context.op_config["raw_input"]
    unique_id = context.op_config["unique_id"]
    yield DynamicOutput((raw_input, unique_id), mapping_key="dynamic_config")


@op
def parse_and_execute_job(
    context: OpExecutionContext, data: tuple[list, str]
) -> List[TypingAny]:
    instructions, unique_id = data
    job_list = []
    run_configs = []
    for instruction in instructions:
        job, run_config = define_composite_job(
            name="dynamic_job", raw_input=instruction, unique_id=unique_id
        )
        context.log.info(f"Created dynamic job: {job.name}")
        job_list.append(job)
        run_configs.append(run_config)

    # Add final op to publish success
    success_raw_input = {
        "operation": "publish_success",
        "parameters": {},
    }
    success_job, success_run_config = define_composite_job(
        name="publish_success", raw_input=success_raw_input, unique_id=unique_id
    )
    job_list.append(success_job)
    run_configs.append(success_run_config)

    all_results = []
    for job, run_config in zip(job_list, run_configs):
        context.log.info(f"Executing dynamic job with run_config: {run_config}")

        if run_config:
            result = job.execute_in_process(run_config=run_config)
        else:
            result = job.execute_in_process()

        for event in result.all_events:
            context.log.info(f"Event: {event.message}")
        try:
            dynamic_result = result.output_value()
            context.log.info(f"Dynamic job result: {dynamic_result}")
            all_results.append(dynamic_result)
        except DagsterInvariantViolationError:
            context.log.info("Dynamic job executed without outputs.")
            all_results.append(None)
    return all_results


@job(
    resource_defs={"s3_resource": s3_resource},
    config={
        "ops": {
            "generate_dynamic_job_configs": {
                "config": {
                    "raw_input": [
                        {
                            "operation": "import_from_google_drive",
                            "parameters": {
                                "file_id": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ",
                            },
                        }
                    ],
                    "unique_id": "123-123-123",
                },
            }
        }
    },
)
def build_execute_job():
    dynamic_configs = generate_dynamic_job_configs()
    dynamic_configs.map(parse_and_execute_job)


@job(
    resource_defs={"s3_resource": s3_resource},
    config={
        "ops": {
            "import_from_google_drive": {
                "inputs": {
                    "file_id": {
                        "value": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ",
                    },
                    "unique_id": {
                        "value": "123-123-123",
                    },
                }
            }
        }
    },
)
def test_import_from_google_drive_job():
    import_from_google_drive()


@repository(name="main")
def deploy_docker_repository():
    return [build_execute_job, test_import_from_google_drive_job]

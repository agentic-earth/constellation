from dagster import (
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
from typing import Any as TypingAny, Dict, Tuple

from orchestrator.assets.ops import *
from orchestrator.assets.jobs import *

OP_DEFS = [mock_csv_data, write_csv, math_block]


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

    graph = GraphDefinition(
        name=name,
        node_defs=OP_DEFS,
        dependencies=deps,
    )

    return graph.to_job(), run_config


@op(config_schema={"raw_input": Field(Any)}, out=DynamicOut())
def generate_dynamic_job_configs(context: OpExecutionContext):
    raw_input = context.op_config["raw_input"]
    yield DynamicOutput(raw_input, mapping_key="dynamic_config")


@op
def parse_and_execute_job(context: OpExecutionContext, raw_input: dict):
    # Dynamically generate a job based on the input
    job, run_config = define_composite_job(name="dynamic_job", raw_input=raw_input)
    context.log.info(f"Created dynamic job: {job.name}")

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
                    "raw_input": {
                        "operation": "write_csv",
                        "parameters": {
                            "result": {
                                "operation": "math_block",
                                "parameters": {
                                    "data": {
                                        "operation": "mock_csv_data",
                                        "parameters": {},
                                    },
                                    "operand": "add",
                                    "constant": 5,
                                },
                            },
                        },
                    }
                }
            }
        }
    }
)
def build_execute_job():
    dynamic_configs = generate_dynamic_job_configs()
    dynamic_configs.map(parse_and_execute_job)


@repository(name="main")
def deploy_docker_repository():
    return [build_execute_job]

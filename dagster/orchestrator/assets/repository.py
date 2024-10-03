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
)
from dataclasses import dataclass

from orchestrator.assets.ops import *
from orchestrator.assets.jobs import *

OP_DEFS = [mock_csv_data, write_csv, math_block]


@dataclass
class CallableOperation:
    operation: str
    parameters: dict[str, any]


def parse_instructions(input: dict) -> CallableOperation:
    if "operation" not in input:
        raise ValueError("Operation not found in instruction")

    # FIXME: Do some check to make sure exists

    operation = input["operation"]
    parameters = {}

    for key, value in input.get("parameters", {}).items():
        if isinstance(value, dict) and "operation" in value:
            parameters[key] = parse_instructions(value)

    return CallableOperation(operation=operation, parameters=parameters)


def generate_dependencies(instruction: CallableOperation, deps: dict) -> dict:
    result = {}
    alias_counter = [1]

    def traverse(node):
        alias = f"{node.operation} ({alias_counter[0]})"
        alias_counter[0] += 1

        current_node = NodeInvocation(name=node.operation, alias=alias)

        dependencies = {}
        for key, param_node in node.parameters.items():
            param_alias = traverse(param_node)
            dependencies[key] = DependencyDefinition(param_alias)

        result[current_node] = dependencies if dependencies else {}
        return alias

    traverse(instruction)
    return result


# TODO: Return both GraphDeinition and run_config
def define_composite_job(name: str, raw_input: dict) -> GraphDefinition:
    instruction: CallableOperation = parse_instructions(input=raw_input)
    deps: dict = generate_dependencies(instruction=instruction, deps={})
    print(deps)

    return GraphDefinition(
        name=name,
        node_defs=OP_DEFS,
        dependencies=deps,
    ).to_job()


@op(config_schema={"raw_input": Field(Any)}, out=DynamicOut())
def generate_dynamic_job_configs(context: OpExecutionContext):
    raw_input = context.op_config["raw_input"]
    yield DynamicOutput(raw_input, mapping_key="dynamic_config")


@op
def parse_and_execute_job(context: OpExecutionContext, raw_input: dict):
    # Dynamically generate a job based on the input
    job = define_composite_job(name="dynamic_job", raw_input=raw_input)
    context.log.info(f"Created dynamic job: {job.name}")

    context.log.info(f"Executing dynamic job")

    # TODO: Make run_config dynamic
    result = job.execute_in_process(
        run_config={
            "ops": {"math_block (2)": {"inputs": {"constant": 0.0, "operand": "add"}}}
        }
    )

    for event in result.all_events:
        context.log.info(f"Event: {event.message}")

    context.log.info(f"Dynamic job result: {result.output_value()}")


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


@repository
def deploy_docker_repository():
    return [build_execute_job]

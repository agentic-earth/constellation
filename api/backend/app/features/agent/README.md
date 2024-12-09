#LLM Subsystem Design, Architecture, and Usage

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
  - [API Invocation](#api-invocation)
  - [Manual Invocation](#manual-invocation)
- [LLMCrew and CrewProcess](#llmcrew-and-crewprocess)
  - [CrewProcess](#crewprocess)
  - [LLMCrew](#llmcrew)
  - [How It Works](#how-it-works)
- [Unit Testing](#unit-testing)
- [Areas of Future Improvement](#areas-of-future-improvement)
- [Developer Information](#developer-information)
  - [Adding New Agents or Models](#adding-new-agents-or-models)
  - [Adding New Dependencies](#adding-new-dependencies)


## Background
The LLM subsystem is responsible for connecting user queries and associated data blocks (datasets, models, etc.) to a Large Language Model (LLM) agent. Within the larger Agentic Earth software ecosystem, this subsystem transforms user input and accompanying metadata into a structured JSON output that can be consumed by the core, given to downstream services (such as the Dagster), and cointainerized by Docker for tasks like model deployment, data import, and inference execution.

This component leverages a CrewAI's abstraction to manage "agents" and "tasks." An agent (powered by an LLM) is configured to follow user instructions, and a task guides the agent with a detailed description of what to do with the user’s query and associated data blocks. The final output is a JSON structure that Dagster can then use to orchestrate dynamic pipelines. By separating the orchestration logic (handled by Dagster) from the language and reasoning capabilities (handled by the LLM subsystem), we maintain a clear boundary between concerns.

## Install

This subsystem is designed to run as a service within a dockerized environment. It is not meant to be executed independently but rather as part of a larger stack defined by the [Docker-Compose](../docker-compose.yml). 

From the project root directory:

```bash
docker-compose up --build
```
Once running, the LLM subsystem’s endpoint will be available at the configured internal network interface. Other services (e.g. front-end) will call into this subsystem to retrieve results.

## Usage

The LLM subsystem is primarily invoked via API calls from an upstream service, typically the FastAPI component that receives user input from the front-end interface. Manual invocations can be done for testing or debugging purposes.

## API Invocation

When a user submits a query (e.g., "Find me a model that can handle image classification tasks and a dataset that matches a particular keyword"), the front-end sends this query along with a list of data blocks to the API. The API then constructs a call to the LLM subsystem’s endpoint, providing:

-  The user query (query)
- A list of blocks representing models and datasets (each block contains fields like name, block_type, description, and filepath)

The LLM subsystem, using the CrewProcess class, will instantiate an agent (via LLMCrew) and create a Crew object configured with the given tasks. The agent’s underlying LLM (e.g., GPT-3.5-turbo) will then analyze the query and the blocks to determine which model and dataset match the query, and output a final JSON that fits the downstream Dagster pipeline’s expected format.

For example, a request might look like this (from another service’s perspective):

```json
{
    "query": "Find a model related to 'fire detection' and a relevant dataset.",
    "blocks": [
        {
            "name": "vit-fire-detection",
            "block_type": "model",
            "description": "A vision transformer model for detecting fires.",
            "filepath": ""
        },
        {
            "name": "wildfire_dataset",
            "block_type": "dataset",
            "description": "Images of wildfires for testing inference.",
            "filepath": "1aniasD6RcD3Zr7K8DSWiiqtXCRbFx7gU"
        }
    ]
}
```

On receiving this input, the LLM subsystem will return a structured JSON ready for a Dagster execution pipeline, substituting the {xxx} and {yyy} placeholders with the identified model name and dataset filepath.

## Manual Invocation

For testing, you can manually invoke the LLM subsystem’s endpoint (if exposed) using tools like curl or Postman. Since the subsystem is configured for inter-service communication, you may need to set up appropriate networking or run it in isolation for direct testing. Once accessible, you can POST a similar JSON payload as shown above and verify that the response is a properly formatted JSON pipeline configuration.

## CrewProcess and Crew 

CrewProcess
The CrewProcess class is responsible for instantiating and configuring a Crew object. Given a user query and a list of Block objects (representing models, datasets, and other resources):
- Builds an Agent (via LLMCrew) configured with a Large Language Model (LLM).
- Constructs a Task that guides the agent on how to interpret the query and blocks.
- Returns a Crew object that, when invoked, leverages the LLM to produce the required JSON structure (e.g., pipelines with deploy/execute/delete instructions).
LLMCrew

Crew
The Crew class encapsulates the logic required to:
- Define how an Agent should behave (including role, goal, and backstory).
- Construct a Task that instructs the agent on how to parse the user query and the provided blocks, ultimately producing a dynamic JSON pipeline configuration.

The LLMCrew uses a standard prompt template that instructs the LLM to identify which blocks are relevant to the query, extract the needed model and dataset information, and integrate them into a JSON template. The resulting JSON is intended for seamless integration with downstream services, particularly Dagster, to dynamically orchestrate data pipelines.

## How It Works

#Inputs:

- Query: A user-provided query asking for certain models or datasets.
- Blocks: A list of PrismaBlock objects containing metadata (name, type, description, and filepath).

#Process:

1. CrewProcess instantiates an LLM-backed Agent via LLMCrew.
2. A Task is built, embedding instructions into the agent’s context. These instructions detail how to:
- Identify relevant models and datasets from the block list.
- Insert the identified model and dataset into placeholders within a pre-defined JSON schema.
- Output only the final JSON structure without additional explanation.

#Outputs:

The LLM returns a structured JSON payload containing operations like deploy_model, import_from_google_drive, model_inference, and delete_model.
This JSON is then validated and passed downstream, e.g., to the Dagster subsystem, to execute the specified pipeline of operations.

Example Use Case:

For instance, if a user queries: "Find a model related to fire detection and a relevant dataset," and the Blocks include a model block named "vit-fire-detection" and a dataset block named "wildfire_dataset", the LLMCrew and CrewProcess will produce a JSON structure similar to:

```json
{
    "ops": {
        "generate_dynamic_job_configs": {
            "config": {
                "raw_input": [
                    {
                        "operation": "deploy_model",
                        "parameters": {
                            "model": "vit-fire-detection"
                        }
                    },
                    {
                        "operation": "export_to_s3",
                        "parameters": {
                            "inference_results": {
                                "operation": "model_inference",
                                "parameters": {
                                    "data": {
                                        "operation": "dict_to_list",
                                        "parameters": {
                                            "data": {
                                                "operation": "import_from_google_drive",
                                                "parameters": {
                                                    "file_id": "1aniasD6RcD3Zr7K8DSWiiqtXCRbFx7gU"
                                                }
                                            }
                                        }
                                    },
                                    "model": "vit-fire-detection"
                                }
                            }
                        }
                    },
                    {
                        "operation": "delete_model",
                        "parameters": {
                            "model": "vit-fire-detection"
                        }
                    }
                ]
            }
        }
    }
}
```
This JSON can then be passed to the Dagster subsystem to dynamically construct and execute the necessary pipeline steps.


## Unit Testing
Unit tests for the LLM subsystem should be written to ensure that the CrewProcess, LLMCrew, and underlying agents and tasks produce the correct output. To run tests:

```bash
pytest
```
We have implemented a set of unit tests in `test_crew.py` to ensure the `LLMCrew` and `CrewProcess` classes behave as expected. These tests cover:

- **Agent Creation**: Verifying that the agent is instantiated with the correct properties (role, goal, etc.).
- **Task Description Integrity**: Ensuring that the generated task description includes the user query, the blocks' details, and expected placeholders.
- **Crew Assembly**: Confirming that a `Crew` object is correctly constructed with the given agent and task.
- **JSON Structure Validation**: Checking that the final JSON structure and placeholders (`{xxx}` and `{yyy}`) appear as intended.

To run the tests, navigate to your project’s root directory and run:


## Developer Information

Adding New Agents or Models

Create a New Agent: 
- In Crew, add another method similar to build_agent() that configures a different LLM or adjusts parameters (e.g., temperature, model version).

Create a New Task:
- Add another method to Crew similar to build_task() for a different prompt structure, suited to another use case.

Register and Invoke:
- Update CrewProcess to optionally select between different agents or tasks based on configuration or user input.

## Adding New Dependencies

To add new Python dependencies, update the `pyproject.toml` file used by Poetry. Once you have specified the new dependencies there, run:

```bash
poetry update
```

## Areas of Future Improvement

- Multiple Models/Datasets & Error Handling: Vector similarity search can be used to handle scenarios with multiple matches or no obvious candidates. Documenting the thresholds and metrics used, as well as fallback strategies is probably good practice.

- Configuration Management: Introduce environment variables or configuration files for switching LLM providers or changing prompt templates without modifying code.

- Testing & Validation: Add test cases for edge scenarios, such as no matched blocks and multiple equally relevant matches.



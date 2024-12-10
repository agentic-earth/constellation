# test_crew.py
import pytest
from typing import List
from unittest.mock import MagicMock

from backend.app.features.agent.crews.crew import LLMCrew
from backend.app.features.agent.crews.crew_process import CrewProcess
from prisma.models import Block as PrismaBlock


@pytest.fixture
def mock_blocks() -> List[PrismaBlock]:
    """
    Creates toy blocks for us to test
    """
    block1 = MagicMock(spec=PrismaBlock)
    block1.name = "test_model"
    block1.block_type = "model"
    block1.description = "A test model that might match the query"
    block1.filepath = "/path/to/model"

    block2 = MagicMock(spec=PrismaBlock)
    block2.name = "test_dataset"
    block2.block_type = "dataset"
    block2.description = "A dataset containing relevant information"
    block2.filepath = "/path/to/dataset"

    return [block1, block2]


def test_build_agent():
    """
    Test that LLMCrew.build_agent() creates an Agent with the expected attributes.
    """
    agent = LLMCrew.build_agent()
    assert agent is not None, "Agent should not be None"
    assert hasattr(agent, "llm"), "Agent should have an LLM"
    assert agent.role == "Analyst", "Agent role should be 'Analyst'"
    assert (
        agent.goal == "Follow the instructions"
    ), "Agent goal should match the given string"


def test_build_task(mock_blocks):
    """
    Test that LLMCrew.build_task() returns a Task object with a description
    containing the query and references to model and dataset blocks.
    """
    agent = LLMCrew.build_agent()
    query = "Find relevant data"
    task = LLMCrew.build_task(query, mock_blocks, agent)
    assert task is not None, "Task should not be None"
    assert hasattr(task, "description"), "Task should have a description"
    assert (
        "Find relevant data" in task.description
    ), "Task description should contain the query"
    assert (
        "Block Type: model" in task.description
    ), "Task description should list model block"
    assert (
        "Block Type: dataset" in task.description
    ), "Task description should list dataset block"


def test_crew_process(mock_blocks):
    """
    Test that CrewProcess.make_crews() creates a Crew with one agent and one task,
    and that the task description includes the query.
    """
    cp = CrewProcess()
    crew = cp.make_crews("Find relevant data", mock_blocks)
    assert crew is not None
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
    assert crew.tasks[0].agent is crew.agents[0]
    assert (
        "Find relevant data" in crew.tasks[0].description
    ), "Crew's task description should contain the query"


def test_task_json_structure(mock_blocks):
    """
    Test that the final JSON structure in the task description contains the dataset and model placeholders
    """
    agent = LLMCrew.build_agent()
    query = "Find relevant data"
    task = LLMCrew.build_task(query, mock_blocks, agent)
    assert (
        "{xxx}" in task.description
    ), "Task description should contain the {xxx} placeholder for the model."
    assert (
        "{yyy}" in task.description
    ), "Task description should contain the {yyy} placeholder for the dataset file_id."
    assert '"ops": {' in task.description, "Expected 'ops' key in the JSON structure."
    assert (
        '"generate_dynamic_job_configs": {' in task.description
    ), "Expected 'generate_dynamic_job_configs' key in the JSON structure."
    assert (
        '"raw_input": [' in task.description
    ), "Expected 'raw_input' array in the JSON structure."

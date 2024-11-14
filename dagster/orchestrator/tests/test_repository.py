import pytest
from orchestrator.assets.repository import (
    define_composite_job,
    generate_dependencies_and_run_config,
    parse_instructions,
    CallableOperation,
    OP_DEFS,
)


def test_parse_instructions_valid():
    input_data = {
        "operation": "import_from_google_drive",
        "parameters": {"file_id": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ"},
    }
    result = parse_instructions(input_data)
    assert result.operation == "import_from_google_drive"
    assert result.parameters["file_id"] == "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ"


def test_parse_instructions_invalid_operation():
    input_data = {"operation": "invalid_operation", "parameters": {}}
    with pytest.raises(
        ValueError, match="Operation 'invalid_operation' is not defined in OP_DEFS."
    ):
        parse_instructions(input_data)


def test_generate_dependencies_and_run_config():
    instruction = CallableOperation(
        operation="import_from_google_drive",
        parameters={"file_id": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ"},
    )
    result, run_config = generate_dependencies_and_run_config(instruction)

    assert isinstance(result, dict)
    assert isinstance(run_config, dict)
    assert "ops" in run_config
    assert "import_from_google_drive (1)" in run_config["ops"]


def test_define_composite_job():
    raw_input = {
        "operation": "import_from_google_drive",
        "parameters": {"file_id": "1ulPG5mev9EuznRtOjjNgIZRcRrqfzreJ"},
    }
    job, run_config = define_composite_job(name="test_job", raw_input=raw_input)

    assert job.name == "dynamic_job"
    assert "ops" in run_config
    assert "import_from_google_drive (1)" in run_config["ops"]

from unittest import mock
import os
import sys
import pandas as pd
import operator
import base64

# Dynamically add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dagster import build_op_context

from orchestrator.assets.ops import (
    import_from_google_drive,
    dict_to_list,
    deploy_model,
    delete_model,
    model_inference,
    mock_csv_data,
    write_csv,
    math_block,
)

from orchestrator.assets.repository import (
    define_composite_job,
)

# Dummy data for testing
DUMMY_FILE_ID = "dummy_file_id"
DUMMY_MODEL_NAME = "dummy_model"
DUMMY_DATA_DICT = {"file1": b"data1", "file2": b"data2"}
DUMMY_DATA_LIST = [b"data1", b"data2"]
DUMMY_DF = pd.DataFrame({"A": [1, 2], "B": [3, 4]})


def test_dict_to_list_op():
    test_data = DUMMY_DATA_DICT
    context = build_op_context()

    output = dict_to_list(context, test_data)

    expected_output = list(test_data.values())
    assert (
        output == expected_output
    ), "dict_to_list did not return the expected list of values"


def test_math_block_op():
    data = DUMMY_DF.copy()
    operand = "add"
    constant = 10.0

    context = build_op_context()

    output_df = math_block(context, operand, constant, data)

    expected_df = data.map(lambda x: getattr(operator, operand)(x, constant))
    pd.testing.assert_frame_equal(output_df, expected_df)


def test_deploy_model_op():
    context = build_op_context()
    model_name = DUMMY_MODEL_NAME

    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Model deployed successfully"}
        mock_get.return_value = mock_response

        deploy_model(context, model_name)

        expected_url = f"http://model_api:8000/deploy?model_name={model_name}"
        mock_get.assert_called_once_with(expected_url, json={"model_name": model_name})


def test_delete_model_op():
    context = build_op_context()
    model_name = DUMMY_MODEL_NAME

    with mock.patch("requests.delete") as mock_delete:
        # Set up mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Model deleted successfully"}
        mock_delete.return_value = mock_response

        delete_model(context, model_name)

        expected_url = f"http://model_api:8000/delete?model_name={model_name}"
        mock_delete.assert_called_once_with(
            expected_url, json={"model_name": model_name}
        )


def test_model_inference_op():
    context = build_op_context()
    data = DUMMY_DATA_LIST
    model_name = DUMMY_MODEL_NAME

    with mock.patch("requests.post") as mock_post:
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"output": ["result1", "result2"]}
        mock_post.return_value = mock_response

        output = model_inference(context, data, model_name)

        expected_url = f"http://model_api:8000/infer?model_name={model_name}"
        payload = {"data": [base64.b64encode(image).decode("utf-8") for image in data]}
        mock_post.assert_called_with(expected_url, json=payload)

        expected_output = {"results": [["result1", "result2"]]}
        assert output == expected_output


def test_write_csv_op():
    context = build_op_context()
    data = DUMMY_DF.copy()

    with mock.patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
        output_file = write_csv(context, data)

        mock_to_csv.assert_called_once_with("output.csv", index=False)

        assert output_file == "output.csv"


def test_import_from_google_drive_op():
    context = build_op_context()
    file_id = DUMMY_FILE_ID

    with mock.patch("gdown.download") as mock_download, mock.patch(
        "zipfile.ZipFile"
    ) as mock_zipfile, mock.patch("os.walk") as mock_walk, mock.patch(
        "builtins.open", new_callable=mock.mock_open, read_data=b"file content"
    ):

        mock_download.return_value = None  # Assuming it returns None on success

        mock_zip_instance = mock_zipfile.return_value.__enter__.return_value
        mock_zip_instance.namelist.return_value = [
            "file1.txt",
            "file2.txt",
            "subdir/file3.txt",
        ]

        mock_walk.return_value = [
            ("data", ("subdir",), ("file1.txt", "file2.txt")),
            ("data/subdir", (), ("file3.txt",)),
        ]

        output = import_from_google_drive(context, file_id)

        download_url = f"https://drive.google.com/uc?id={file_id}"
        mock_download.assert_called_once_with(download_url, "download.zip", quiet=False)

        mock_zipfile.assert_called_once_with("download.zip", "r")

        mock_walk.assert_any_call("data")

        expected_files = ["file1.txt", "file2.txt", os.path.join("subdir", "file3.txt")]
        assert set(output.keys()) == set(expected_files)


def test_mock_csv_data_op():
    context = build_op_context()

    df = mock_csv_data(context)

    expected_data = {"column1": [1, 4, 7], "column2": [2, 5, 8], "column3": [3, 6, 9]}
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected_df)


# Composite job tests. Testing the functionality of our dynamic job generation. Tested multiple operations to ensure the correct job construction.


def test_define_composite_job_import_from_google_drive():
    """
    Test define_composite_job with the 'import_from_google_drive' operation to ensure correct job construction and execution.
    """
    raw_input = {
        "operation": "import_from_google_drive",
        "parameters": {"file_id": DUMMY_FILE_ID},
    }

    job, run_config = define_composite_job(name="import_job", raw_input=raw_input)

    assert job.name == "import_job", "Job name does not match the expected name."
    assert "ops" in run_config, "'ops' key not found in run_config."
    assert (
        "import_from_google_drive (1)" in run_config["ops"]
    ), "'import_from_google_drive (1)' op not found in run_config."
    assert (
        "inputs" in run_config["ops"]["import_from_google_drive (1)"]
    ), "'inputs' key not found for 'import_from_google_drive (1)' op."

    assert run_config["ops"]["import_from_google_drive (1)"]["inputs"] == {
        "file_id": {"value": DUMMY_FILE_ID},
    }, "Run config inputs do not match the expected value serialization."

    with mock.patch("gdown.download") as mock_download, mock.patch(
        "zipfile.ZipFile"
    ) as mock_zipfile, mock.patch("os.walk") as mock_walk, mock.patch(
        "builtins.open", new_callable=mock.mock_open, read_data=b"file content"
    ):

        mock_download.return_value = None

        mock_zip_instance = mock_zipfile.return_value.__enter__.return_value
        mock_zip_instance.namelist.return_value = [
            "file1.txt",
            "file2.txt",
            "subdir/file3.txt",
        ]

        mock_walk.return_value = [
            ("data", ("subdir",), ("file1.txt", "file2.txt")),
            ("data/subdir", (), ("file3.txt",)),
        ]

        result = job.execute_in_process(run_config=run_config)

        assert result.success, "Job execution failed."

        expected_download_url = f"https://drive.google.com/uc?id={DUMMY_FILE_ID}"
        mock_download.assert_called_once_with(
            expected_download_url, "download.zip", quiet=False
        )

        mock_zipfile.assert_called_once_with("download.zip", "r")

        mock_walk.assert_any_call("data")

        # Optionally, verify the output of the op if applicable
        # For example, if import_from_google_drive returns a dict of file paths:
        # output = result.output_for_node("import_from_google_drive (1)")
        # expected_output = {
        #     'file1.txt': b'file content',
        #     'file2.txt': b'file content',
        #     'subdir/file3.txt': b'file content',
        # }
        # assert output == expected_output, "The output of import_from_google_drive op does not match the expected output."


def test_define_composite_job_deploy_model():
    raw_input = {
        "operation": "deploy_model",
        "parameters": {"model": DUMMY_MODEL_NAME},
    }
    job, run_config = define_composite_job(name="deploy_model_job", raw_input=raw_input)

    assert job.name == "deploy_model_job"
    assert "ops" in run_config
    assert "deploy_model (1)" in run_config["ops"]
    assert "inputs" in run_config["ops"]["deploy_model (1)"]
    assert run_config["ops"]["deploy_model (1)"]["inputs"] == {
        "model": {"value": DUMMY_MODEL_NAME},
    }

    # Mock requests.get
    with mock.patch("requests.get") as mock_get:
        # Set up mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Model deployed successfully"}
        mock_get.return_value = mock_response

        # Execute the job
        result = job.execute_in_process(run_config=run_config)
        assert result.success


def test_define_composite_job_delete_model():
    raw_input = {
        "operation": "delete_model",
        "parameters": {"model": DUMMY_MODEL_NAME},
    }
    job, run_config = define_composite_job(name="delete_model_job", raw_input=raw_input)

    assert job.name == "delete_model_job"
    assert "ops" in run_config
    assert "delete_model (1)" in run_config["ops"]
    assert "inputs" in run_config["ops"]["delete_model (1)"]
    assert run_config["ops"]["delete_model (1)"]["inputs"] == {
        "model": {"value": DUMMY_MODEL_NAME},
    }

    # Mock requests.delete
    with mock.patch("requests.delete") as mock_delete:
        # Set up mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Model deleted successfully"}
        mock_delete.return_value = mock_response

        # Execute the job
        result = job.execute_in_process(run_config=run_config)
        assert result.success

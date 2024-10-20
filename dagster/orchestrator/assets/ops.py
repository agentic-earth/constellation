from dagster import Any, In, OpExecutionContext, Out, op, Field, fs_io_manager
import requests

import pandas as pd
import operator

# import tensorflow as tf
# import tensorflow_datasets as tfds
# import glob
# import os
import numpy as np
import zipfile
import os

# import jax
# import flax

# Adjust resource limits if not on macOS
import sys

if sys.platform != "darwin":
    import resource

    low, high = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (high, high))

# Define constants
MAX_IN_MEMORY = 200_000

# # Op to get dataset information
# @op(
#     name="get_dataset_info_op",
#     out=Out(dict),
#     config_schema={
#         "dataset": Field(str, description="Name or path of the dataset"),
#         "split": Field(str, description="Dataset split (e.g., 'train', 'test')"),
#         "tfds_data_dir": Field(str, default_value="", is_required=False, description="Directory for tfds data"),
#         "tfds_manual_dir": Field(str, default_value="", is_required=False, description="Manual directory for tfds data")
#     }
# )
# def get_dataset_info_op(context: OpExecutionContext) -> dict:
#     dataset = context.op_config["dataset"]
#     split = context.op_config["split"]
#     tfds_data_dir = context.op_config.get("tfds_data_dir", None)
#     tfds_manual_dir = context.op_config.get("tfds_manual_dir", None)

#     directory = os.path.join(dataset, split)
#     if os.path.isdir(directory):
#         # Dataset is in a directory
#         examples_glob = f'{directory}/*/*.jpg'
#         paths = glob.glob(examples_glob)
#         get_classname = lambda path: os.path.basename(os.path.dirname(path))
#         class_names = sorted(set(map(get_classname, paths)))
#         num_examples = len(paths)
#         num_classes = len(class_names)
#         int2str = {idx: name for idx, name in enumerate(class_names)}
#         dataset_info = {
#             "num_examples": num_examples,
#             "num_classes": num_classes,
#             "int2str": int2str,
#             "examples_glob": examples_glob,
#             "is_directory": True,
#             "dataset_path": dataset
#         }
#     else:
#         # Dataset is a tfds dataset
#         data_builder = tfds.builder(dataset, data_dir=tfds_data_dir)
#         data_builder.download_and_prepare(
#             download_config=tfds.download.DownloadConfig(
#                 manual_dir=tfds_manual_dir
#             )
#         )
#         num_examples = data_builder.info.splits[split].num_examples
#         num_classes = data_builder.info.features['label'].num_classes
#         int2str = {idx: data_builder.info.features['label'].int2str(idx) for idx in range(num_classes)}
#         dataset_info = {
#             "num_examples": num_examples,
#             "num_classes": num_classes,
#             "int2str": int2str,
#             "examples_glob": None,
#             "is_directory": False,
#             "data_builder": data_builder  # Include for later use
#         }
#     context.log.info(f"Dataset info: {dataset_info}")
#     return dataset_info

# # Op to load and preprocess data
# @op(
#     name="get_data_op",
#     ins={"dataset_info": In(dict)},
#     out={"train_dataset": Out(), "test_dataset": Out()},
#     config_schema={
#         "batch_size": Field(int, description="Batch size for training"),
#         "batch_size_eval": Field(int, description="Batch size for evaluation"),
#         "image_size": Field(int, description="Size to which images are resized"),
#         "shuffle_buffer": Field(int, default_value=10000, description="Size of the shuffle buffer"),
#         "prefetch_size": Field(int, default_value=1, description="Number of batches to prefetch"),
#         "num_devices": Field(int, default_value=0, is_required=False, description="Number of devices for sharding")
#     }
# )
# def get_data_op(context: OpExecutionContext, dataset_info: dict):
#     # Extract configuration
#     batch_size = context.op_config["batch_size"]
#     batch_size_eval = context.op_config["batch_size_eval"]
#     image_size = context.op_config["image_size"]
#     shuffle_buffer = context.op_config["shuffle_buffer"]
#     prefetch_size = context.op_config["prefetch_size"]
#     num_devices = context.op_config.get("num_devices", jax.local_device_count())

#     num_classes = dataset_info["num_classes"]

#     # Retrieve dataset_path from dataset_info
#     dataset_path = dataset_info.get("dataset_path")

#     # Define preprocessing function
#     def preprocess_image(image, label, mode):
#         if mode == 'train':
#             image = tf.image.random_crop(image, [image_size, image_size, 3])
#             image = tf.image.random_flip_left_right(image)
#         else:
#             image = tf.image.resize(image, [image_size, image_size])

#         image = image / 255
#         image = (image * 2) - 1

#         label = tf.one_hot(label, num_classes)
#         return image, label

#     # Function to create dataset from directory
#     def get_dataset_from_directory(directory, mode):
#         data = tf.data.Dataset.list_files(f'{directory}/*/*.jpg')
#         class_names = list(dataset_info["int2str"].values())

#         def parse_function(filename):
#             image = tf.io.read_file(filename)
#             image = tf.image.decode_jpeg(image, channels=3)
#             label_str = tf.strings.split(filename, os.sep)[-2]
#             label = tf.where(label_str == class_names)[0][0]
#             return image, label

#         data = data.map(parse_function, num_parallel_calls=tf.data.AUTOTUNE)
#         if mode == 'train':
#             data = data.shuffle(shuffle_buffer)
#         data = data.map(lambda x, y: preprocess_image(x, y, mode), num_parallel_calls=tf.data.AUTOTUNE)
#         data = data.batch(batch_size if mode == 'train' else batch_size_eval)
#         if num_devices:
#             data = data.shard(num_devices, jax.process_index())
#         data = data.prefetch(prefetch_size)
#         return data

#     # Function to create dataset from tfds
#     def get_dataset_from_tfds(data_builder, split, mode):
#         data = data_builder.as_dataset(split=split)
#         data = data.map(lambda x: (x['image'], x['label']), num_parallel_calls=tf.data.AUTOTUNE)
#         if mode == 'train':
#             data = data.shuffle(shuffle_buffer)
#         data = data.map(lambda x, y: preprocess_image(x, y, mode), num_parallel_calls=tf.data.AUTOTUNE)
#         data = data.batch(batch_size if mode == 'train' else batch_size_eval)
#         if num_devices:
#             data = data.shard(num_devices, jax.process_index())
#         data = data.prefetch(prefetch_size)
#         return data

#     def dataset_to_numpy(dataset):
#         for batch in dataset:
#             images, labels = batch
#             yield images.numpy(), labels.numpy()

#     if dataset_info["is_directory"]:
#         train_dir = os.path.join(dataset_info["dataset_path"], 'train')
#         test_dir = os.path.join(dataset_info["dataset_path"], 'test')
#         train_dataset = get_dataset_from_directory(train_dir, 'train')
#         test_dataset = get_dataset_from_directory(test_dir, 'test')
#     else:
#         data_builder = dataset_info["data_builder"]
#         train_dataset = get_dataset_from_tfds(data_builder, 'train', 'train')
#         test_dataset = get_dataset_from_tfds(data_builder, 'test', 'test')

#     # Convert the generator to a list before returning
#     return list(train_dataset), list(test_dataset)


# # Op to prefetch data (if necessary)
# @op(
#     name="prefetch_data_op",
#     ins={"dataset": In()},
#     out=Out(),
#     config_schema={
#         "n_prefetch": Field(int, default_value=0, description="Number of batches to prefetch to device")
#     }
# )
# def prefetch_data_op(context: OpExecutionContext, dataset):
#     n_prefetch = context.op_config["n_prefetch"]
#     ds_iter = iter(dataset)
#     ds_iter = map(lambda x: jax.tree_map(lambda t: np.asarray(t), x), ds_iter)

#     devices = jax.local_devices()

#     if len(devices) > 1 and n_prefetch:
#         # Use prefetching if multiple devices are available
#         ds_iter = flax.jax_utils.prefetch_to_device(ds_iter, n_prefetch)
#     else:
#         context.log.info(f"Only {len(devices)} device(s) available, skipping sharding.")

#     context.log.info("Data prefetched.")
#     return ds_iter


@op(
    name="import_zip_from_google_drive",
    ins={"file_id": In(str)},
    out=Out(dict[str, Any]),
)
def import_from_google_drive(
    context: OpExecutionContext, file_id: str
) -> dict[str, Any]:
    # Import the data from Google Drive
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Make a request to download the file
    response = requests.get(download_url)

    if response.status_code == 200:
        # Save the file
        with open("download.zip", "wb") as f:
            f.write(response.content)
        context.log.info("Downloaded file successfully.")

        # Unzip the file
        with zipfile.ZipFile("download.zip", "r") as zip_ref:
            zip_ref.extractall("data")

        # Save file to data to dict structure
        data_dict = {}
        for root, dirs, files in os.walk("data"):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, "rb") as f:
                    relative_path = os.path.relpath(file_path, "data")
                    data_dict[relative_path] = f.read()

        context.log.info("Loaded files into dictionary.")
        return data_dict

    else:
        context.log.error(
            f"Failed to download file. Status code: {response.status_code}"
        )

    return {}


@op(name="mock_csv_data", out=Out())
def mock_csv_data(context: OpExecutionContext) -> pd.DataFrame:
    data = [["column1", "column2", "column3"], [1, 2, 3], [4, 5, 6], [7, 8, 9]]
    context.log.info(f"Mock data: {data}")

    df = pd.DataFrame(data[1:], columns=data[0])
    context.log.info(f"DataFrame created from mock data:\n{df}")

    return df


@op(name="write_csv", ins={"result": In(pd.DataFrame)}, out=Out(str))
def write_csv(context: OpExecutionContext, result: pd.DataFrame) -> str:
    context.log.info(f"Received data to write to CSV:\n{result}")

    result.to_csv("output.csv", index=False)

    context.log.info(f"Data written to output.csv")
    return "output.csv"


@op(
    name="math_block",
    ins={
        "data": In(pd.DataFrame),
        "operand": In(str),
        "constant": In(float),
    },
    out=Out(pd.DataFrame),
)
def math_block(
    context: OpExecutionContext,
    operand: str,
    constant: float,
    data: pd.DataFrame,
) -> pd.DataFrame:
    operand = getattr(operator, operand)

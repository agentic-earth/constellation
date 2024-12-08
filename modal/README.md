# Modal Service Setup and Usage

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Unit Testing](#unit-testing)

## Background

The modal service facilitates deploying and managing machine learning model services. The system uses FastAPI for handling HTTP requests and leverages Modal for cloud deployment. The whole application is dockerized to be used together in the same network along with the dagster pipeline. The primary goal is to enable dynamic deployment and deletion of model inference services in the dagster pipeline.

## Install

This component is designed to be run within a docker container and is not designed to be run independently. View the [Docker-Compose](../docker-compose.yml) file for more information. By running the docker compose file, the modal API will be hosted at "http://localhost:8002/"

Navigate to the root directory of the project and run the following command to build and run the docker container.

```bash
docker-compose up --build
```

## Usage

Within the larger Agentic Earth pipeline, this service will be invoked by a HTTP request from the "dagster_service" service within the individual dagster opreations deploy and delete model as well as run model inference.

To build and the run the modal service on its own:

```bash
docker build -t modal-api .
docker run -p 8000:8000 modal-api:latest
```

After the containers have built, users can access the modal service by making HTTP requests at "http://127.0.0.1:8000/".

1. **Deploying the Model**  
   Use the output endpoint to deploy the model:

   ```bash
   http://127.0.0.1:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params of the GET request, specify the "model_name" which is the hugging face name. Eg. model_name as "EdBianchi/vit-fire-detection", "amyeroberts/swin-tiny-patch4-window7-224-finetuned-eurosat" or "victor/autotrain-satellite-image-classification-40975105875".

   If the model has been deployed successfully, the return response would be:

   ```bash
   {"message": "MODEL_NAME has been deployed succesfully!",
   "endpoint":  "https://wdorji--SERVICE_NAME-flask-app.modal.run/infer",
   "service_name": "SERVICE_NAME"}
   ```

   If the model has already been deployed successfully, the return response would be:

   ```bash
   {"message": "MODEL_NAME has already been deployed.",
   "endpoint":  "https://wdorji--SERVICE_NAME-flask-app.modal.run/infer",
   "service_name": "SERVICE_NAME"}
   ```

   If the model deployment fails, this would raise an error with the message:

   ```bash
   {"detail": "Issue with deploying model on modal"}
   ```

2. **Running Model Inference**  
    Once a model is successfully deployed, for inference use:

   ```bash
   http://127.0.0.1:8000/infer/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params, specify the "model_name" which is the hugging face name to run inference on. In the body of the POST request, specify "data" which is a list of images. The images must be in base 64 form. For example, if we have 1 image with the path "modal_creator/assets/forest.jpg":

   ```bash
   import requests
   import base64

   def convert_image_to_base64(image_path):
      with open(image_path, "rb") as image_file:
         return base64.b64encode(image_file.read()).decode('utf-8')

   requests.post(f"http://127.0.0.1:8000/infer/?model_name=EdBianchi/vit-fire-detection",
                  json={"data": [convert_image_to_base64("modal_creator/assets/forest.jpg")]})

   ```

   If the model has been deployed successfully, for a single image where the model outputs 2 possible labels for classification, the return response would look like:

   ```bash
   {"output": [[{"label":"label1","score":0.990},{"label":"label2","score":0.090}]]}
   ```

   If the model has not been deployed yet, the return response would be:

   ```bash
   {"message": "MODEL_NAME has not been deployed yet."}
   ```

   If the model has been deployed but no images are provided, the return response would be:

   ```bash
   {"output": "No images provided."}
   ```

   If the model has been deployed but model inference fails, this would raise an error with the message:

   ```bash
   {"detail": "Model inference failed"}
   ```

3. **Deleting a model deployment**  
   To delete the model endpoint, use:

   ```bash
   http://127.0.0.1:8000/delete/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params of the DELETE request, specify the "model_name" of the previously deployed model.

   If the model has not been deployed yet, the return response would be:

   ```bash
   {"message": "MODEL_NAME has not been deployed yet."}
   ```

   If the model has been deleted succesfuly, the return response would be:

   ```bash
   {"message": "MODEL_NAME has been deleted succesfully!"}
   ```

   If deleteion fails, this would raise an error with the message:

   ```bash
   {"detail": "Issue with deleting MODEL_NAME deployment: {ERROR MESSAGE}"}
   ```

### Unit-Testing

To run tests, run the following command in the modal_creator directory:

```bash
pytest
```

Tests are contained in tests/test_main.py

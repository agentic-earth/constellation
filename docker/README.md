# Deployment Instructions

## Running the Service

Download config.json in secrets and keys from notion and add to docker-service directory

To deploy the service, navigate to the docker directory and run:

```
python3 deploy_image_creator.py
```

This command output the endpoint to deploy a model using the model name from Hugging Face.

## Interacting with the Model on Postman

1. **Deploy the Model**  
   Use the output endpoint to deploy the model:

   ```
   http://54.236.243.146:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

2. **Check Deployment Status**  
   After deploying, check if the service is successfully deployed by accessing:

   ```
   http://54.236.243.146:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

3. **Invoke the Model**  
   If successfully deployed, it will return the endpoint to invoke the model:

   ```
   http://18.212.81.71:6419/infer
   ```

4. **Delete the Model Endpoint**  
   To delete the model endpoint, use:
   ```
   http://54.236.243.146:8000/delete/?model_name=EdBianchi/vit-fire-detection
   ```

## Deleting the Image Creator Service

To delete the image creator service, run:

```
python3 delete_image_creator.py
```

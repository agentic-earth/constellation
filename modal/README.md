# Deployment Instructions

Download config.json in secrets and keys from notion and add to modal directory.

## Setup

```
pip install modal
modal token set --token-id ak-GJnX5RxgeF3Qw8vx4bw7tE --token-secret as-Zamgcpei8gVnaEEu3kdFzl
```

When in the modal directory, deploy the modal creator using:

```
modal deploy main.py
```

Stop the modal creator using:

```
modal app stop modal-creator-app
```

## Interacting with the Model on Postman

1. **Deploy the Model**  
   Use the output endpoint to deploy the model:

   ```
   https://wdorji--modal-creator-app-flask-app.modal.run/deploy
   ```

   In the body of the POST request, specify the model_name which is the hugging face name and service_name. Currently use model_name as EdBianchi/vit-fire-detection and service_name could be anything like fire-model as long as its different from other model service names.

2. **Invoke the Model**  
    If successfully deployed, it will return the endpoint to invoke the model:

   ```
   {
    "message": "https://wdorji--fire-model-flask-app.modal.run/infer"
   }
   ```

   This endpoint takes in a POST request wtih s3_key in the body which is the location in the s3 bucket where intermediate tensors or numpy array were saved which is to be fed directly into the model. To test, you can set s3_key as preprocessed/processed_image.pt.

3. **Delete the Model Endpoint**  
   To delete the model endpoint, use:

   ```
   https://wdorji--modal-creator-app-flask-app.modal.run/delete
   ```

   In the body of the POST request, specify the service_name which was used previously to deploy the model

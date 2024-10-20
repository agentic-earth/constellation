## Testing locally

In modal directory:

```
docker build -t modal-api .
docker run -p 8000:8000 modal-api:latest

```

## Interacting with the Model on Postman

1. **Deploy the Model**  
   Use the output endpoint to deploy the model:

   ```
   http://127.0.0.1:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params of the POST request, specify the "model_name" which is the hugging face name. Eg. model_name as EdBianchi/vit-fire-detection

2. **Invoke the Model**  
    If successfully deployed, it will return the endpoint to invoke the model:

   ```
   {
    "message": "https://wdorji--fire-model-flask-app.modal.run/infer"
   }
   ```

   In the body of the POST request, specify "images" which is a list of images.

3. **Delete the Model Endpoint**  
   To delete the model endpoint, use:

   ```
   http://127.0.0.1:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params of the POST request, specify the "model_name" previously deployed

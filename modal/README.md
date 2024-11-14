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

   In the query params of the GET request, specify the "model_name" which is the hugging face name. Eg. model_name as EdBianchi/vit-fire-detection

2. **Invoke the Model**  
    Once the model is successfully deployed, for inference use:

   ```
   http://127.0.0.1:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

   In the body of the POST request, specify "data" which is a list of images.

   Some currently working model names are "EdBianchi/vit-fire-detection", "amyeroberts/swin-tiny-patch4-window7-224-finetuned-eurosat" and "victor/autotrain-satellite-image-classification-40975105875".

3. **Delete the Model Endpoint**  
   To delete the model endpoint, use:

   ```
   http://127.0.0.1:8000/deploy/?model_name=EdBianchi/vit-fire-detection
   ```

   In the query params of the DELETE request, specify the "model_name" previously deployed

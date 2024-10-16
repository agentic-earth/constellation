from fastapi import FastAPI, HTTPException
import uuid

from utils import check_build_status, delete_service, generate_dirs_files, push_model_image, stop_and_delete_task, upload_model_zip, get_model_id, check_ecr_repo_exists

app = FastAPI()

@app.post("/deploy")
async def deploy_model(model_name: str):
    
    try:

        model_id = get_model_id(model_name)
        
        if not check_ecr_repo_exists(model_id):

            generate_dirs_files(model_name, model_id)

            upload_model_zip(model_id)

            push_model_image(model_id)

            return {"message": f"{model_name} deployment has started"}

        return check_build_status(model_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deploying model: "+str(e))

@app.post("/delete")
async def delete_model_service(model_name: str):

    
    try:
        model_id = get_model_id(model_name)

        stop_and_delete_task(model_id)
        
        delete_service(model_id)

        return {"message": f"{model_id} service has been deleted"}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting model: "+str(e))
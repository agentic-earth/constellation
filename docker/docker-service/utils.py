from fastapi import HTTPException
import os
import boto3
import shutil
import json
import hashlib
import uuid

# Load the keys from the config file
with open('./config.json') as config_file:
    config = json.load(config_file)

access_key = config["AWS_ACCESS_KEY_ID"]
secret_key = config["AWS_SECRET_ACCESS_KEY"]
bucket_name = config["BUCKET_NAME"]
region = config["REGION"]
account_id = config["ACCOUNT_ID"]
codebuild_role_arn = config["CODEBUILD_ROLE_ARN"]
ecs_role_arn = config["ECS_ROLE_ARN"]
cluster_name = config["CLUSTER_NAME"]

def generate_port_number(model_name: str) -> int:
    # Create a hash of the model_name
    hash_object = hashlib.md5(model_name.encode())
    # Convert the hash to an integer
    port_number = int(hash_object.hexdigest(), 16) % 65536  # Ensure it's within the valid port range
    
    return port_number

def get_model_id(model_name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, model_name))

def check_ecr_repo_exists(model_id):
    ecr_client = boto3.client('ecr', 
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)

    try:
        # Describe repositories to check if the repo exists
        response = ecr_client.describe_repositories()
        repositories = response['repositories']

        # Check if any repository matches the model_id
        for repo in repositories:
            if repo['repositoryName'] == model_id:
                return True  # Repository exists

        return False  # Repository does not exist
    except Exception as e:
        print(f"Error checking ECR repositories: {e}")
        return False  # Return False in case of an error

def generate_dirs_files(pipe_name, model_id):

    port = str(generate_port_number(model_id))

     # Define the content for app.py
    app_content = f"""from fastapi import FastAPI
from transformers import pipeline
from fastapi import File, UploadFile, HTTPException
from PIL import Image
import io

# Create a new FastAPI app instance
app = FastAPI()

# Initialize the pipeline
pipe = pipeline("image-classification", model="{pipe_name}")

# Define a root endpoint
@app.get("/")
async def read_root():
    return {{"message": "Image Classification API is running!"}}

# Define a function to handle the POST request at `/infer`
@app.post("/infer")
async def infer(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Please upload a JPEG or PNG image.")
    
    try:
        # Read image file
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error processing the input image.")
    
    try:
        # Inference
        output = pipe(image)
        return {{"predicted_label": output}}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error during model inference.")
"""

    # Define the content for requirements.txt
    requirements_content = """fastapi
uvicorn
transformers
pillow
python-multipart
torch
torchvision
"""

    # Define the content for Dockerfile
    dockerfile_content = f"""# Use the official Python image as the base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port (default FastAPI port)
EXPOSE {port}

# Define the entry point
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{port}"]
"""


    # Create the directory if it doesn't exist
    os.makedirs("../"+model_id, exist_ok=True)

    # Write the files
    try:
        with open(f"../{model_id}/app.py", "w") as app_file:
            app_file.write(app_content)

        with open(f"../{model_id}/requirements.txt", "w") as req_file:
            req_file.write(requirements_content)

        with open(f"../{model_id}/Dockerfile", "w") as docker_file:
            docker_file.write(dockerfile_content)


    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating files." + str(e))

    

def upload_model_zip(model_id):

    # Specify the directory to be zipped
    directory_path = '../'+model_id

    # Specify the name of the output zip file
    output_filename = '../'+model_id

    # Create a zip file
    shutil.make_archive(output_filename, 'zip', directory_path)

    # Create an S3 client
    s3_client = boto3.client('s3', 
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
    
    file_path = f"../{model_id}.zip"
    s3_object_name = f"models/{model_id}.zip"

    try:
        # Upload the file
        s3_client.upload_file(file_path, bucket_name, s3_object_name)
        # Remove the created directory and local zip file
        shutil.rmtree(directory_path)
        os.remove(file_path)
    

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error pushing zip file to S3 bucket")
    
    
def push_model_image(model_id):

    

    inline_buildspec = f"""
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR....
      - aws --version
      - ACCOUNT_ID={account_id}
      - TIMESTAMP=$(date +%Y%m%d%H%M%S)
      - DOCKER_FOLDER="models"
      - BUCKET_NAME="{bucket_name}"
      - ECR_FOLDER="{model_id}"
      - REGION="{region}"
      - aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com
      - repo_exists=$(aws ecr describe-repositories --repository-names $ECR_FOLDER --output text --query 'repositories[0].repositoryName' || true)
      - echo "[${{repo_exists}}]"
      - echo "[${{ECR_FOLDER}}]"

      # Build the Docker image with the correct tag

      #       # Create the ECR repository if it doesn't exist
      - |
        if [ "$repo_exists" = "$ECR_FOLDER" ]; then
          echo "Repository already exists: $ECR_FOLDER";
        else
          aws ecr create-repository --repository-name $ECR_FOLDER;
        fi

      - REPOSITORY_URI=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_FOLDER

      # Fetch the Dockerfile and all the relevant code required for the application from S3
      - aws s3 cp s3://$BUCKET_NAME/$DOCKER_FOLDER/$ECR_FOLDER.zip .
      - unzip -o $ECR_FOLDER.zip

  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -t $REPOSITORY_URI:latest .
      - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI

  post_build:
    commands:
      - echo Build completed on `date`
      - echo pushing to repo
      - docker push $REPOSITORY_URI

"""
    
    # Create a CodeBuild client
    codebuild_client = boto3.client('codebuild', 
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)

    # Define the parameters for the CodeBuild project
    project_name = f'{model_id}_CodeBuildProject'
    source_location = f'{bucket_name}/models/{model_id}.zip'  # Replace with your S3 bucket and object key
    source_type = 'S3'

    # Create a CodeBuild project
    try:
        create_project_response = codebuild_client.create_project(
            name=project_name,
            source={
                'type': source_type,
                'location': source_location,
                'buildspec':inline_buildspec
                
            },
            artifacts={
                'type': 'NO_ARTIFACTS'
            },
            environment={
                'type': 'LINUX_CONTAINER',
                'image': 'aws/codebuild/amazonlinux2-x86_64-standard:5.0',  
                'computeType': 'BUILD_GENERAL1_SMALL',
            },
            logsConfig = {
                'cloudWatchLogs': {
                    'status': 'ENABLED',
                    'groupName': 'string',
                    'streamName': 'string'
                }
            },
            serviceRole = codebuild_role_arn,  
        )
        
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error building image and pushing docker image to ECR: " + str(e))

    # Start a build for the created project
    try:
        build_response = codebuild_client.start_build(
            projectName=project_name
        )
        build_id = build_response['build']['id']

        return build_id 
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to start the image build: " + str(e))

def get_fargate_task_public_ip(task_arn):
    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    
    ec2_client = boto3.client('ec2',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    # Step 1: Describe the task to get the network interface ID
    response = ecs_client.describe_tasks(
        cluster=cluster_name,
        tasks=[task_arn]
    )
    
    # Extract the ENI ID from the response
    eni_id = None
    attachments = response['tasks'][0]['attachments']
    for attachment in attachments:
        if attachment['type'] == 'ElasticNetworkInterface':
            for detail in attachment['details']:
                if detail['name'] == 'networkInterfaceId':
                    eni_id = detail['value']
                    break

    if not eni_id:
        print("No ENI found for the task.")
        return None

    # Step 2: Describe the network interface to get the public IP
    eni_response = ec2_client.describe_network_interfaces(
        NetworkInterfaceIds=[eni_id]
    )

    # Extract the public IP
    public_ip = eni_response['NetworkInterfaces'][0].get('Association', {}).get('PublicIp')

    if not public_ip:
        print("No public IP associated with the network interface.")
        return None

    return public_ip

def check_server_status(model_id):

    port = generate_port_number(model_id)

    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    
    existing_services = ecs_client.list_services(cluster=cluster_name)

    serviceArn = None
    for service in existing_services['serviceArns']:
         if model_id in service:
             serviceArn = service
             break

    if serviceArn:
        # If the service exists, get its status
        server_status = ecs_client.describe_services(cluster=cluster_name, services=[serviceArn])['services'][0]['deployments'][0]['rolloutState']

        if server_status == 'COMPLETED':

            task_arn = f'arn:aws:ecs:{region}:{account_id}:task/WebServices/' + ecs_client.describe_services(cluster=cluster_name,services=[serviceArn])['services'][0]['events'][-1]['message'].split('task ')[1].strip(').')
            public_ip = get_fargate_task_public_ip(task_arn)
            port = str(port)

            return {"message": f"Model server deployed on: http://{public_ip}:{port}/infer"}

        elif server_status == 'IN_PROGRESS':
             
             return {"message": f"Model server deployment in progress"}

        return {"message": f"Model server deployment failed"}


    else:
        # Create the service since it doesn't exist

        

        repo_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{model_id}:latest"
        task_name = f"{model_id}_task"

        task_registration_response = ecs_client.register_task_definition(
            containerDefinitions=[
                {
                    "name": task_name,
                    "image": repo_uri,
                    "cpu": 1024,
                    "memory":2000,
                    "memoryReservation":1000,
                    "portMappings": [{
                        "containerPort": port,
                        "hostPort": port,
                        "protocol": "tcp"
                    }],
                    "essential": True,
                    "environment": [],
                    "mountPoints": [],
                    "volumesFrom": [],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/{model_id}_app",
                            "awslogs-region": region,
                            "awslogs-stream-prefix": "ecs",
                            "awslogs-create-group": "True"
                        }
                    }
                }
            ],
            executionRoleArn=ecs_role_arn,
            family= f"{model_id}_app",
            networkMode="awsvpc",
            requiresCompatibilities= [
                "FARGATE"
            ],
            runtimePlatform={
                'cpuArchitecture': 'X86_64',
                'operatingSystemFamily': 'LINUX'
            },
            cpu= "1 vCPU",
            memory= "2 GB")

        taskDefinitionArn = task_registration_response["taskDefinition"]["taskDefinitionArn"]
        server_name = f"{model_id}_server"

        ecs_client.create_service(
            cluster=cluster_name, 
            serviceName=server_name,
            taskDefinition=taskDefinitionArn, 
            schedulingStrategy='REPLICA',
            desiredCount=1,
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'subnet-01285aac0bd02fda1','subnet-08dfab842552d28f0','subnet-0e028c93b044e4bb6',
                        'subnet-00341d1c140c97bb6','subnet-0d8df2cddc745b57f','subnet-043a994c92176717f'
                    ],
                    'assignPublicIp': 'ENABLED',
                    'securityGroups': ["sg-0cb2ef9fb02cb8bdd","sg-0643023534416aa63"]
                }
            },
            launchType='FARGATE',
        )

        return {"message": f"Model server deployment in progress"}

def check_build_status(model_id):

    codebuild_client = boto3.client('codebuild', 
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
    
    build_id = None

    try:
        build_id = codebuild_client.list_builds_for_project(projectName=model_id+"_CodeBuildProject")['ids'][0]
    except:
        return {"message": f"Model build not found"}

    response = codebuild_client.batch_get_builds(ids=[build_id])
    build_info = response['builds'][0]
    build_status = build_info['buildStatus']

    if build_status == "SUCCEEDED":
        return check_server_status(model_id)

    elif build_status == "IN_PROGRESS":

        return {"message": f"Model image build and push in progress"}

    return {"message": f"Model image push failed"}

def stop_and_delete_task(model_id):


    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    

    existing_services = ecs_client.list_services(cluster=cluster_name)

    serviceArn = None
    for service in existing_services['serviceArns']:
        if model_id in service:
            serviceArn = service
            break

    task_arn = f'arn:aws:ecs:{region}:{account_id}:task/WebServices/' + ecs_client.describe_services(cluster=cluster_name,services=[serviceArn])['services'][0]['events'][-1]['message'].split('task ')[1].strip(').')
            
    
    #Stop the ECS task
    try:
        stop_response = ecs_client.stop_task(
            cluster=cluster_name,
            task=task_arn,
            reason='Task is being stopped and deleted'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to stop the task:" + str(e))
    # Optionally, delete the task definition (if needed)
    # Uncomment this section if you want to deregister the task definition

    task_definition = stop_response['task']['taskDefinitionArn']
    try:
        deregister_response = ecs_client.deregister_task_definition(
            taskDefinition=task_definition
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to deregister the task definition:" + str(e))


def delete_service(model_id):

    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    service_name = f'arn:aws:ecs:{region}:{account_id}:service/WebServices/{model_id}_server' 
    
    # Update the service to set the desired count to 0 (stops running tasks)
    try:
        update_response = ecs_client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=0
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update the service:" + str(e))

    # Delete the ECS service
    try:
        delete_response = ecs_client.delete_service(
            cluster=cluster_name,
            service=service_name,
            force=True  # Force deletion even if there are running tasks
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete the service:" + str(e))
import boto3
import json
import time

# Load the keys from the config file
with open('docker-service/config.json') as config_file:
    config = json.load(config_file)

access_key = config["AWS_ACCESS_KEY_ID"]
secret_key = config["AWS_SECRET_ACCESS_KEY"]
bucket_name = config["BUCKET_NAME"]
region = config["REGION"]
account_id = config["ACCOUNT_ID"]
codebuild_role_arn = config["CODEBUILD_ROLE_ARN"]
ecs_role_arn = config["ECS_ROLE_ARN"]
cluster_name = config["CLUSTER_NAME"]

def stop_and_delete_task():


    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    

    serviceArn = f'arn:aws:ecs:{region}:{account_id}:service/WebServices/DockerAPIWebServer'

    task_arn = f'arn:aws:ecs:{region}:{account_id}:task/WebServices/' + ecs_client.describe_services(cluster=cluster_name,services=[serviceArn])['services'][0]['events'][-1]['message'].split('task ')[1].strip(').')
            
    
    #Stop the ECS task
    try:
        stop_response = ecs_client.stop_task(
            cluster=cluster_name,
            task=task_arn,
            reason='Task is being stopped and deleted'
        )

        print("Stopped Task")

    except Exception as e:
        raise print("Failed to stop the task:" + str(e))
    # Optionally, delete the task definition (if needed)
    # Uncomment this section if you want to deregister the task definition

    task_definition = stop_response['task']['taskDefinitionArn']
    try:
        deregister_response = ecs_client.deregister_task_definition(
            taskDefinition=task_definition
        )

        print("Deleted Task")

    except Exception as e:
        raise print("Failed to deregister the task definition:" + str(e))


def delete_service():

    ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    service_name = f'arn:aws:ecs:{region}:{account_id}:service/WebServices/DockerAPIWebServer' 
    
    # Update the service to set the desired count to 0 (stops running tasks)
    try:
        update_response = ecs_client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=0
        )

        print("Stopped Runnings Tasks")

    except Exception as e:
        raise print("Failed to update the service:" + str(e))

    # Delete the ECS service
    try:
        delete_response = ecs_client.delete_service(
            cluster=cluster_name,
            service=service_name,
            force=True  # Force deletion even if there are running tasks
        )

        print("Deleted Image Creator Service")

    except Exception as e:
        raise print("Failed to delete the service:" + str(e))
    
stop_and_delete_task()
delete_service()
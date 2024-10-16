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

ecs_client = boto3.client(
    'ecs',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)

portNum = 8000
model_name = "DockerAPI"
container_name = f"{model_name}_task"
image_uri =  f"{account_id}.dkr.ecr.{region}.amazonaws.com/image_creator_api:latest"

task_registration_response = ecs_client.register_task_definition(
        containerDefinitions=[
            {
                "name": container_name,
                "image": image_uri,
                "cpu": 1024,
                "memory":2000,
                "memoryReservation":1000,
                "portMappings": [{
                    "containerPort": portNum,
                    "hostPort": portNum,
                    "protocol": "tcp"
                }],
                "essential": True,
                "environment": [],
                "mountPoints": [],
                "volumesFrom": [],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": f"/ecs/{model_name}",
                        "awslogs-region": region,
                        "awslogs-stream-prefix": "ecs",
                        "awslogs-create-group": "True"
                    }
                }
            }
        ],
        executionRoleArn=ecs_role_arn,
        family= f"{model_name}_app",
        networkMode="awsvpc",
        requiresCompatibilities= [
            "FARGATE"
        ],
        runtimePlatform={
            'cpuArchitecture': 'ARM64',#'ARM64 for macOS bu,
            'operatingSystemFamily': 'LINUX'
        },
        cpu= "1 vCPU",
        memory= "2 GB")

print(json.dumps(task_registration_response, indent=4, default=str))

taskDefinitionArn = task_registration_response["taskDefinition"]["taskDefinitionArn"]

serviceName = f"{model_name}WebServer"
response = ecs_client.create_service(
                cluster=cluster_name, 
                serviceName= serviceName,
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
print(json.dumps(response, indent=4, default=str))

existing_services = ecs_client.list_services(cluster=cluster_name)

serviceArn = None
for service in existing_services['serviceArns']:
     if model_name in service:
         serviceArn = service
         break

server_status = ecs_client.describe_services(cluster=cluster_name, services=[serviceArn])['services'][0]['deployments'][0]['rolloutState']

while server_status == "IN_PROGRESS":
  server_status = ecs_client.describe_services(cluster=cluster_name, services=[serviceArn])['services'][0]['deployments'][0]['rolloutState']
  time.sleep(10)

if server_status == "COMPLETED":
    response = ecs_client.list_tasks(cluster=cluster_name)
    task_arn = f'arn:aws:ecs:{region}:{account_id}:task/WebServices/' + ecs_client.describe_services(cluster=cluster_name,services=[serviceArn])['services'][0]['events'][-1]['message'].split('task ')[1].strip(').')
    def get_fargate_task_public_ip(cluster_name, task_arn):
      ec2_client = boto3.client('ec2')
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

    # Example usage
    public_ip = get_fargate_task_public_ip(cluster_name, task_arn)

    if public_ip:
        print(f'The public IP of the task is: {public_ip}')
        print(f'Deploy models at http://{public_ip}:8000/deploy/?model_name=')
    else:
        print('Failed to retrieve the public IP.')

else:

  print("Model server deployment failed")
     

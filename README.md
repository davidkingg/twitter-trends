# Twitter Trends in Nigeria
this is a data engineering project that fetches the trending keyworks in nigeria every 15mins. \n
the trending data is saved to a data lake(google cloud storage). \n
with pyspark running in a docker container, a batch processing is done every 15mins to carry out the following functions \n
    - fetch the current day trending keywords from the data lake
    - extract top trending keywords by volume in the last 2 hours
    - extract newly emerging trending keywords in the last 1 hour
    - save both top trending and emerging trend to a data warehouse (bigquery)

# Dashbord link to visualize the trending tweets in nigeria
https://lookerstudio.google.com/reporting/9c44d5b0-c85e-4061-9d68-65c0ce5946d4


## setting up the project locally or on the cloud

### environment variables
The environment variables are sectioned into 3
1. prefect - this contains variables related to prefect 
2. GCP - this contains variabled related to google cloud platform e.g project_id
3. Twitter - this contains variable related to the twitter api e.g consumer_key

create a .env file with the following config
#### prefect blocks
GCP_CREDENTIALS_BLOCK_NAME=twitter-gcs-cred
TWITTER_BUCKET_BLOCK_NAME=twitter-gcs-cred
#### Google cloud platform
PROJECT_ID=*****
SERVICE_ACCOUNT_CREDENTIALS=./twitter_project.json
GCS_BUCKET_NAME=twitter_data_twitter-project-381411
#### twitter api
CONSUMER_KEY=76s*******************
CONSUMER_SECRET=BE*********************************************
ACCESS_TOKEN=2**************************************************
ACCESS_TOKEN_SECRET=********************************************


### installing docker
1. sudo apt-get update
2. sudo apt-get install docker.io
3. sudo groupadd docker
4. sudo gpasswd -a $USER docker
5. sudo service docker restart


### installing docker compose
on your home directory run the following commands
1. mkdir bin
2. cd bin
3. wget https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -O docker-compose
4. chmod +x docker-compose
5. cd ~
6. nano .bashrc
# add this line to the .bashrc to add the bin path to the environment variables
7. export PATH="${HOME}/bin:${PATH}"
8. which docker-compose


### Google setup
create a project on GCP
create a service account with cloud storage, bigquery permissions
download the service accouint credentials json and save it as twitter_project.json in the project roor directory
from project directory, run the following commands
1. export GOOGLE_APPLICATION_CREDENTIALS=./twitter_project.json
2. gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS


### terrafoam
insatlling terrafoam on the local machine or cloud platform
from the home directory
1. cd bin
2. wget https://releases.hashicorp.com/terraform/1.3.7/terraform_1.3.7_linux_amd64.zip
3. sudo apt install unzip
4. unzip terra*
5. rm terraform_*
cd to the project directory
6. in the terrform variables.tf file, replace the project default value with your gcp project id
7. from projec directory, run the following commands
    - terraform init
    - terraform plan
    - terraform apply



### pyspark
from project root directory
1. cd spark
2. source build.sh
3. docker compose up -d
4. chmod +x run-docker.sh


### install requirements
from project root directory run
1. sudo apt install python3-venv
2. python3 -m venv env
3. source env/bin/activate
5. pip install -r requirements.txt


### prefect
##### to run the prefect dashboard server
prefect orion start

##### register a gcp module
prefect block register -m prefect_gcp

##### create a storage block and credential block
python gcp_storage_block.py  

##### to create a prefect worker agent
prefect agent start --work-queue default

##### deploy the flow and tasks with a schedule to run every 15mins
prefect deployment build ./injest_tweet.py:etl_gcp -n 'scheduled_twitter_prefect_deployment' --cron "*/15 * * * *" -a




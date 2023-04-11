# Twitter Trends in Nigeria   ![twitter](https://github.com/davidkingg/twitter-trends/blob/main/utills/twitter-logo-2429%20(1).png)
## Data Engineer Zoomcamp Capstone Project 

This capstone project was developed under the scope of the [Data Engineer Zoomcamp by DataTalksClub](https://github.com/DataTalksClub/data-engineering-zoomcamp) (the biggest Data community in the internet - [DTC](https://datatalks.club/)).

This is a data engineering project fetches the trending keyworks in nigeria every 15mins.  

The trending data is gotten from twitter trends Api and saved to a data lake(google cloud storage).  

The trends are gotten every 15 minutes and this process is ochestrated with PREFECT.  

With pyspark running in a docker container, a batch process is submitted every 15mins to carry out the following functions:  
1. Fetch the current day trending keywords from the data lake
2. Extract top trending keywords by volume in the last 2 hours
3. Extract newly emerging trending keywords in the last 1 hour
4. Save both top trending and emerging trends to a data warehouse (bigquery)


## Used Technologies 🔨

For this project I decided to use the following tools:
- Docker - TO build containers for running the Spark master and workers;
- Prefect - For orchestrating the full pipeline;
- Terraform - As a Infrastructure-as-Code (IaC) tool;
- Google Cloud Storage (GCS) - for storage as Data Lake;
- BigQuery- for the project Data Warehouse;
- Spark - for Batch processing and data transformation;
- Google Data studio - for visualizations.


## Dashboard Preview

You can explore the final dashboard [here](https://lookerstudio.google.com/reporting/9c44d5b0-c85e-4061-9d68-65c0ce5946d4).

![Dashboard Page 1](https://github.com/davidkingg/twitter-trends/blob/main/utills/dashboard2.png)
</br>
![Dashboard Page 2](https://github.com/davidkingg/twitter-trends/blob/main/utills/dashboard1.png)

</br>
</br>


## Development Steps 🚧

### environment variables
The environment variables are sectioned into 3
1. prefect - this contains variables related to prefect 
2. GCP - this contains variabled related to google cloud platform e.g project_id
3. Twitter - this contains variable related to the twitter api e.g consumer_key

create a .env file with the following config
#### prefect blocks
GCP_CREDENTIALS_BLOCK_NAME=twitter-gcs-cred <br>
TWITTER_BUCKET_BLOCK_NAME=twitter-gcs-cred <br>
#### Google cloud platform
PROJECT_ID=*****
SERVICE_ACCOUNT_CREDENTIALS=./twitter_project.json
GCS_BUCKET_NAME=twitter_data_twitter-project-381411
#### twitter api
CONSUMER_KEY=76s******** <br>
CONSUMER_SECRET=Bd************<br>
ACCESS_TOKEN=2*****************<br>
ACCESS_TOKEN_SECRET=***********<br>


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
7. add this line to the .bashrc to export the bin path to the environment variables : export PATH="${HOME}/bin:${PATH}"
8. which docker-compose


### Google setup
create a project on GCP
create a service account with cloud storage, bigquery permissions <br>
download the service accouint credentials json and save it as twitter_project.json in the project roor directory <br>
from project directory, run the following commands <br>
1. export GOOGLE_APPLICATION_CREDENTIALS=./twitter_project.json <br>
2. gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS <br>


### terrafoam
insatlling terrafoam on the local machine or cloud platform
from the home directory
1. cd bin
2. wget https://releases.hashicorp.com/terraform/1.3.7/terraform_1.3.7_linux_amd64.zip
3. sudo apt install unzip
4. unzip terra*
5. rm terraform_*
6. cd to the project directory
7. in the terrform variables.tf file, replace the project default value with your gcp project id
8. from projec directory, run the following commands
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
#### to run the prefect dashboard server
prefect orion start

#### register a gcp module
prefect block register -m prefect_gcp

#### create a storage block and credential block
python gcp_storage_block.py  

#### to create a prefect worker agent
prefect agent start --work-queue default

#### deploy the flow and tasks with a schedule to run every 15mins
prefect deployment build ./injest_tweet.py:etl_gcp -n 'scheduled_twitter_prefect_deployment' --cron "*/15 * * * *" -a




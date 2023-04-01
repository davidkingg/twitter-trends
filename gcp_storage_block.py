from prefect_gcp import GcpCredentials, CloudRunJob, GcsBucket
from dotenv import load_dotenv
import os
load_dotenv()


# this reads the json credential files
with open(os.getenv('SERVICE_ACCOUNT_CREDENTIALS')) as f:
    service_account = f.read()

service_account_info = service_account


# creates a google credential block
GcpCredentials(
    service_account_info=service_account_info
).save(os.getenv('GCP_CREDENTIALS_BLOCK_NAME'))


# loads the credentials
gcp_credentials = GcpCredentials.load(os.getenv('GCP_CREDENTIALS_BLOCK_NAME'))


# create a bucket block
gcs_bucket = GcsBucket(
    bucket=os.getenv('GCS_BUCKET_NAME'),
    gcp_credentials=gcp_credentials,
)


gcs_bucket.save(os.getenv('TWITTER_BUCKET_BLOCK_NAME'), overwrite=True)


#python gcp_storage_block.py
#python gcp_storage_block.py  --json_path=hale-carport-376812-1526be656cce.json --name=dev --project_id=hale-carport-376812 --bucket=twitter_data_hale-carport-376812
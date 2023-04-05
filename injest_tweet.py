import pandas as pd
from time import time
from sqlalchemy import create_engine, text
import argparse
import os
from prefect   import flow, task
from  prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect_gcp.cloud_storage import GcsBucket
import os
from pathlib import Path
import tweepy
import datetime
import shutil
import pytz


from subprocess import call

from dotenv import load_dotenv
load_dotenv()

timezone = pytz.timezone('Africa/Lagos')

@task(log_prints=True, retries=2, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=3))
def auth(consumer_key: str, consumer_secret:str, access_token:str, access_token_secret:str) -> tweepy.api:
    authentication = tweepy.OAuth1UserHandler(
        consumer_key=consumer_key, 
        consumer_secret=consumer_secret, 
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    api = tweepy.API(authentication)
    return api

@task(log_prints=True, retries=2)
def extract(api: tweepy.api) -> list:
    info = api.get_place_trends('23424908')


    return info

@task(log_prints=True)
def transform(info: list) -> list:
    data = info[0]['trends']
    date = pd.to_datetime(info[0]['as_of']).tz_convert(timezone).date()
    hour = pd.to_datetime(info[0]['as_of']).tz_convert(timezone).hour
    minute = pd.to_datetime(info[0]['as_of']).tz_convert(timezone).minute

    df = pd.DataFrame(data).sort_values('tweet_volume', ascending=False)

    df['date'] = date
    df['hour'] = hour
    df['minute'] = minute

    newly_trending=df[(df['tweet_volume'].isna())&(df['name'].str[0]!='#')]
    trending = df[(df['tweet_volume'].notna())&(df['name'].str[0]!='#')]
    top_trending_by_volume = trending[trending['tweet_volume']>=trending['tweet_volume'].median()]
    low_trending_by_volume = trending[trending['tweet_volume']<trending['tweet_volume'].median()]
    hashtags = df[(df['name'].str[0]=='#')]

    return [newly_trending, trending, hashtags, top_trending_by_volume, low_trending_by_volume]


@task
def write_gcp(newly_trending: pd.DataFrame, trending: pd.DataFrame, hashtags: pd.DataFrame, top_trending_by_volume: pd.DataFrame, low_trending_by_volume: pd.DataFrame):
    """writing to gcp"""
    #f'./{color}/{color}_tripdata_{year}-{month}.parquet'

    date = str(datetime.datetime.now(tz = timezone).date())

    time_st = str(datetime.datetime.now(tz = timezone).hour)+'-h'+str(datetime.datetime.now(tz = timezone).minute)
    dfs=[newly_trending,trending, hashtags, top_trending_by_volume, low_trending_by_volume]
    folders = ['emerging_trends','trending', 'hashtags', 'top_trending', 'low_trending']
    for i in range(len(dfs)):
        gcp_bucket = GcsBucket.load(os.getenv('TWITTER_BUCKET_BLOCK_NAME'))

        path = f"./data/{date}/{folders[i]}"
        try:
            os.makedirs(path)
        except:
            pass
        path = f'{path}/{time_st}.parquet'
        dfs[i].to_parquet(path)
        gcp_bucket.upload_from_path(
            path, path
            )
    shutil.rmtree('data') 


@task(log_prints=True, retries=2)
def gcp_to_bigquery_spark():
    print('beginning to push to bigquery')
    os.chdir('./spark')
    print(os.getcwd())
    print(os.listdir())
    exit_code = call('./run-docker.sh',shell=True)
    print(exit_code)



@flow(log_prints=True, name='injest')
def etl_gcp(consumer_key: str = os.getenv('CONSUMER_KEY'),
            consumer_secret:str = os.getenv('CONSUMER_SECRET'),
            access_token:str = os.getenv('ACCESS_TOKEN'),
            access_token_secret:str = os.getenv('ACCESS_TOKEN_SECRET')):
    """main flow function"""
    api = auth(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)

    info = extract(api=api)

    dataframes = transform(info=info)

    write_gcp(dataframes[0], dataframes[1], dataframes[2], dataframes[3], dataframes[4])

    result = gcp_to_bigquery_spark()


if __name__=='__main__':
    etl_gcp()
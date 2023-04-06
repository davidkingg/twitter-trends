import warnings
warnings.filterwarnings("ignore")
import datetime
import pytz
import os

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F
import pyspark.pandas as ps

timezone = pytz.timezone('Africa/Lagos')

credentials_location = '/opt/workspace/twitter_project.json'

conf = SparkConf() \
    .setAppName('twitter') \
    .set("spark.jars", "/usr/bin/spark-3.3.2-bin-hadoop3/jars/gcs-connector-hadoop3-2.2.5.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location)


sc = SparkContext.getOrCreate(conf=conf)
hadoop_conf = sc._jsc.hadoopConfiguration()
hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)
hadoop_conf.set("fs.gs.auth.service.account.enable", "true")



spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate() 
spark.conf.set('temporaryGcsBucket', os.environ['GCS_BUCKET_NAME'])
spark.conf.set('parentProject', os.environ['PROJECT_ID'])
spark.conf.set('credentialsFile', credentials_location)

# get current date and hour
date = str(datetime.datetime.now(tz = timezone).date())
hour= datetime.datetime.now(tz = timezone).hour


# fetch data from datalake (google cloud storage)
hashtags = spark.read.parquet(f'gs://twitter_data_twitter-project-381411/data/{date}/hashtags') \
                .drop('__index_level_0__') 
hashtags = hashtags.filter((hashtags.hour==hour)|(hashtags.hour==hour-1))

top_trending = spark.read.parquet(f'gs://twitter_data_twitter-project-381411/data/{date}/top_trending') \
                .drop('__index_level_0__') 
top_trending = top_trending.filter((top_trending.hour==hour)|(top_trending.hour==hour-1))

low_trending = spark.read.parquet(f'gs://twitter_data_twitter-project-381411/data/{date}/low_trending') \
                .drop('__index_level_0__') 
low_trending = low_trending.filter((low_trending.hour==hour)|(low_trending.hour==hour-1))

emerging_trends = spark.read.parquet(f'gs://twitter_data_twitter-project-381411/data/{date}/emerging_trends/') \
                .drop('__index_level_0__') 
emerging_trends = emerging_trends.filter((emerging_trends.hour==hour)|(emerging_trends.hour==hour-1))


# getting the emerging trends in the last 1 hour
emerging_trends_1hr = emerging_trends.groupBy('name').agg({'minute':'count'}).withColumnRenamed('count(minute)','count')

# updating emerging to last 15mins
emerging_trends = emerging_trends.filter(emerging_trends.hour==hour)
emerging_trends = emerging_trends.filter((emerging_trends.hour==hour)&(emerging_trends.minute==emerging_trends.agg({'minute':'max'}).collect()[0][0])).sample(0.7)

# getting the top trends in the last 1 hour
top_trending_1hr = top_trending.groupBy('name').agg({'minute':'count'}).withColumnRenamed('count(minute)','count').sort('count',ascending=False)

# updating top trending to last 15mins
top_trending = top_trending.filter(top_trending.hour==hour)
top_trending = top_trending.filter((top_trending.hour==hour)&(top_trending.minute==top_trending.agg({'minute':'max'}).collect()[0][0])).sample(0.7)

# getting the low trends by volume in the last 1 hour
low_trending_1hr = low_trending.groupBy('name').agg({'minute':'count'}).withColumnRenamed('count(minute)','count').sort('count',ascending=False)

# updating low trends by volume to last 15mins
low_trending = low_trending.filter(low_trending.hour==hour)
low_trending = low_trending.filter((low_trending.hour==hour)&(low_trending.minute==low_trending.agg({'minute':'max'}).collect()[0][0])).sample(0.7)

# getting the hashtags in the last 1 hour
hashtags_1hr = hashtags.groupBy('name').agg({'minute':'count'}).withColumnRenamed('count(minute)','count')   

# updating hashatgs to last 15mins
hashtags = hashtags.filter(hashtags.hour==hour)
hashtags = hashtags.filter((hashtags.hour==hour)&(hashtags.minute==hashtags.agg({'minute':'max'}).collect()[0][0])).sample(0.6)


##################################### write to bigquery  ##############################################
hashtags.groupBy('name').agg({'date':'first', 'hour':'first', 'tweet_volume':'max'}).write.format('bigquery') \
  .option('table', 'twitter_data.hashtags') \
  .mode("overwrite") \
  .save()

top_trending.groupBy('name').agg({'date':'first', 'hour':'first', 'tweet_volume':'max'}).write.format('bigquery') \
  .option('table', 'twitter_data.top_trending') \
  .mode("overwrite") \
  .save()

low_trending.groupBy('name').agg({'date':'first', 'hour':'first', 'tweet_volume':'max'}).write.format('bigquery') \
  .option('table', 'twitter_data.low_trending') \
  .mode("overwrite") \
  .save()

emerging_trends.groupBy('name').agg({'date':'first', 'hour':'first', 'tweet_volume':'max'}).write.format('bigquery') \
  .option('table', 'twitter_data.emerging_trends') \
  .mode("overwrite") \
  .save()

# top_trending_15.to_spark().write.format('bigquery') \
#   .option('table', 'twitter_data.top_trending_15') \
#   .mode("overwrite") \
#   .save()

# emerging_trends_15.to_spark().write.format('bigquery') \
#   .option('table', 'twitter_data.emerging_trends_15') \
#   .mode("overwrite") \
#   .save()

# hashtags_15.to_spark().write.format('bigquery') \
#   .option('table', 'twitter_data.hashtags_15') \
#   .mode("overwrite") \
#   .save()

top_trending_1hr.withColumn('count', F.col('count') * 15/60).withColumnRenamed('count','hour').write.format('bigquery') \
  .option('table', 'twitter_data.top_trending_1hr') \
  .mode("overwrite") \
  .save()

low_trending_1hr.withColumn('count', F.col('count') * 15/60).withColumnRenamed('count','hour').write.format('bigquery') \
  .option('table', 'twitter_data.low_trending_1hr') \
  .mode("overwrite") \
  .save()

hashtags_1hr.withColumn('count', F.col('count') * 15/60).withColumnRenamed('count','hour').write.format('bigquery') \
  .option('table', 'twitter_data.hashtags_1hr') \
  .mode("overwrite") \
  .save()

emerging_trends_1hr.withColumn('count', F.col('count') * 15/60).withColumnRenamed('count','hour').write.format('bigquery') \
  .option('table', 'twitter_data.emerging_trends_1hr') \
  .mode("overwrite") \
  .save()

# python week5.py \
#     --input=fhvhv_tripdata_2021-06.csv.gz \
#     #--input_yellow=data/pq/yellow/2020/*/ \
#     --output=report-test_script


# ## using spark submit
# url="spark://david-HP-EliteBook-840-G6:7077"
# spark-submit --master="${url}" week5.py --inputt=homework --output=report-test_script

# spark-submit --master="spark://localhost:7077" pyspark_script.py

#source /usr/bin/spark-3.3.2-bin-hadoop3/bin/spark-submit --master="spark://spark-master:7077" /opt/workspace/pyspark_script.py

#docker exec -i -t -w="/opt/workspace"  spark-master /usr/bin/spark-3.3.2-bin-hadoop3/bin/spark-submit --master="spark://spark-master:7077" pyspark_script.py

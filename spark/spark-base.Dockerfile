FROM cluster-base

# -- Layer: Apache Spark

ARG spark_version=3.3.2
ARG hadoop_version=3

RUN apt-get update -y && \
    apt-get install -y curl && \
    curl https://archive.apache.org/dist/spark/spark-${spark_version}/spark-${spark_version}-bin-hadoop${hadoop_version}.tgz -o spark.tgz && \
    tar -xf spark.tgz && \
    mv spark-${spark_version}-bin-hadoop${hadoop_version} /usr/bin/ && \
    mkdir /usr/bin/spark-${spark_version}-bin-hadoop${hadoop_version}/logs && \
    rm spark.tgz

ENV SPARK_HOME /usr/bin/spark-${spark_version}-bin-hadoop${hadoop_version}
ENV SPARK_MASTER_HOST spark-master
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3

# -- Runtime

WORKDIR ${SPARK_HOME}
COPY ../twitter_project.json  /opt/workspace
COPY gcs-connector-hadoop3-2.2.5.jar ${SPARK_HOME}/jars
COPY spark-bigquery-latest_2.12.jar ${SPARK_HOME}/jars
COPY fhvhv_tripdata_2021-06.csv.gz /opt/workspace

RUN chmod 644 ${SPARK_HOME}/jars/gcs-connector-hadoop3-2.2.5.jar
RUN chmod 644 ${SPARK_HOME}/jars/spark-bigquery-latest_2.12.jar
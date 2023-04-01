# Reference from offical Apache Spark repository Dockerfile for Kubernetes
# https://github.com/apache/spark/blob/master/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/Dockerfile
ARG java_image_tag=17-jre
FROM eclipse-temurin:${java_image_tag}

# -- Layer: OS + Python

ARG shared_workspace=/opt/workspace

RUN mkdir -p ${shared_workspace} && \
    apt-get update -y && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pandas
RUN pip install pyarrow
ENV SHARED_WORKSPACE=${shared_workspace}
# -- Runtime

VOLUME ${shared_workspace}
CMD ["bash"]
#!/bin/bash

docker exec -w="/opt/workspace"  spark-master /usr/bin/spark-3.3.2-bin-hadoop3/bin/spark-submit --master="spark://spark-master:7077" pyspark_script.py
#docker exec -i -t -w="/opt/workspace"  spark-master /usr/bin/spark-3.3.2-bin-hadoop3/bin/spark-submit --master="spark://spark-master:7077" pyspark_script.py
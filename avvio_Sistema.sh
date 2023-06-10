#! /bin/bash
cd ./DockerFile/Spark/
docker build -t cluster-apache-spark:3.0.2 .
cd ../..
cd ./DockerFile/Grafana/
docker build -t grafkob .
cd ../..
docker-compose build
docker-compose up -d
docker exec master sh /home/data/avvio_hdfs.sh

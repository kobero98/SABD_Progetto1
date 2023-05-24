#! /bin/bash
cd ./DockerFile/Spark/
docker build -t cluster-apache-spark:3.0.2 .
cd ../..
docker-compose build
docker-compose up -d
docker exec master sh /home/data/avvio_hdfs.sh
docker logs nifi | grep Generated > profileNifi.txt

#! /bin/bash
sudo docker-compose build
cd ./DockerFile/Spark/
docker build -t cluster-apache-spark:3.0.2 .
cd ../..
sudo docker-compose up -d
sudo docker exec master sh /home/data/avvio_hdfs.sh
sudo docker logs nifi | grep Generated > profileNifi.txt

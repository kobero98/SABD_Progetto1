#! /bin/bash
x=1
while getops x: flag
do
    case "${flag}" in
        x) x=${OPTARG}
            ;;
    esac
done
cd ./DockerFile/Spark/
docker build -t cluster-apache-spark:3.0.2 .
cd ../..
cd ./DockerFile/Grafana/
docker build -t grafkob .
cd ../..
docker-compose build
docker-compose up -d --scale spark-worker-a=$x
docker exec master sh /home/data/avvio_hdfs.sh
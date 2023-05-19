#! /bin/bash
sudo docker-compose build
sudo docker-compose up -d
sudo docker exec master sh /home/data/avvio_hdfs.sh 

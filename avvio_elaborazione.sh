docker exec -it spark_master sh ../spark-apps/start_app.sh
sudo rm -r -d ./DockerFile/HDFS/cartellaResult
docker exec -it master hdfs dfs -get /cartellaResult /home/data 
sudo rm ./Results/*
mkdir Results
sudo mv ./DockerFile/HDFS/cartellaResult/Query1Result/*.csv ./Results/Query1.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query2ResultBot/*.csv ./Results/Query2Bot.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query2ResultTop/*.csv ./Results/Query2Top.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query3Result/*.csv  ./Results/Query3.csv
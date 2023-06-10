#docker exec -it spark_master /bin/bash ../spark-apps/start_app.sh
sudo rm -r -d ./DockerFile/HDFS/cartellaResult
docker exec -it master hdfs dfs -get /cartellaResult /home/data 
sudo rm -d -r ./Result
mkdir Result
sudo mv ./DockerFile/HDFS/cartellaResult/Query1Result/*.csv ./Result/Query1.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query2ResultBot/*.csv ./Result/Query2Bot.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query2ResultTop/*.csv ./Result/Query2Top.csv
sudo mv ./DockerFile/HDFS/cartellaResult/Query3Result/*.csv  ./Result/Query3.csv
python3 -m http.server 
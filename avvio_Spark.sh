cd ./DockerFile/Spark/
docker build -t cluster-apache-spark:3.0.2 .
cd ../..
docker-compose up -d
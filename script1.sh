docker network create --driver bridge hadoop_network

docker run -t -i -p 9864:9864 -d --network=hadoop_network --name=slave1 matnar/hadoop
#docker run -t -i -p 9863:9864 -d --network=hadoop_network --name=slave2 matnar/hadoop
#docker run -t -i -p 9862:9864 -d --network=hadoop_network --name=slave3 matnar/hadoop
#docker run -t -i -p 8443:8443 -d -v "$(pwd):/data" --network=hadoop_network --name=nifi apache/nifi:latest
docker run -t -i -p 9870:9870 --network=hadoop_network --name=master matnar/hadoop



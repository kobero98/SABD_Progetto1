docker run -d -t -i -p 8443:8443 -v "$(pwd):/data" --network=hadoop_network --name=nifi apache/nifi:latest

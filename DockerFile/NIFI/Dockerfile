FROM apache/nifi:latest
WORKDIR /app
COPY core-site.xml  /app/core-site.xml
COPY hdfs-site.xml  /app/hdfs-site.xml
EXPOSE 8443
ENTRYPOINT [ "/bin/bash" ]

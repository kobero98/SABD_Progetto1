#! /bin/sh
hdfs namenode -format
$HADOOP_HOME/sbin/start-dfs.sh
hdfs dfs -mkdir /cartellaNIFI
hdfs dfs -chmod u=rwx,g=rwx,o=rwx /cartellaNIFI
hdfs dfs -mkdir /cartellaResult
hdfs dfs -chmod u=rwx,g=rwx,o=rwx /cartellaResult
echo "terminato\n"

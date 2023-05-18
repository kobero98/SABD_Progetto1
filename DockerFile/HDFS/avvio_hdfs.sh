#! /bin/sh
hdfs namenode -format
./sbin/start-dfs.sh
echo "ciao\n"
/bin/bash 
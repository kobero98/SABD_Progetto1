echo "start query1"
/opt/spark/bin/spark-submit --master spark://spark-master:7077 ./query1.py
echo "start query2"
/opt/spark/bin/spark-submit --master spark://spark-master:7077 ./query2.py
echo "start query3"
/opt/spark/bin/spark-submit --master spark://spark-master:7077 ./query3.py

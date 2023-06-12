from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, count
import sys,logging
from datetime import datetime
import pandas as pd

# Logging configuration
formatter = logging.Formatter('[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
AppName = "Progetto 1 SABD"

def parse_map(f):
    x=f.split(sep=",")
    return [x[0], x[1], x[2], x[3], x[4]]

def main():

    #Creazione dello Spark Context
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    #Lettura del dataset da HDFS e trasformazione in dataframe
    logger.info("Reading CSV File")
    spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                      .map(parse_map)\
                      .toDF(schema=["id", "secType", "value", "time", "date"])\
                      .createOrReplaceTempView("trading")
    preproc = spark.sql("SELECT id, date, time, AVG(value) AS value FROM trading GROUP BY id, date, time ORDER BY date,id, time").cache()
    preproc.createOrReplaceTempView("preproc")
    spark.sql("WITH min(id, date, time, value) AS (SELECT tab1.id, tab1.date, tab1.time, tab1.value FROM preproc tab1\
                                                   INNER JOIN (SELECT id, date, MIN(time) AS time FROM preproc GROUP BY id, date)\
                                                   tab2 ON tab1.id = tab2.id AND tab1.date = tab2.date AND tab1.time = tab2.time),\
                    max(id, date, time, value) AS (SELECT tab1.id, tab1.date, tab1.time, tab1.value FROM preproc tab1\
                                                   INNER JOIN (SELECT id, date, MAX(time) AS time FROM preproc GROUP BY id, date)\
                                                   tab2 ON tab1.id = tab2.id AND tab1.date = tab2.date AND tab1.time = tab2.time),\
                    variazione(id, date, time1, time2, val1, val2, var) AS (SELECT t1.id, t1.date, t1.time, t2.time, t2.value, t1.value, t2.value-t1.value AS var FROM min t1\
                                                  JOIN max t2 ON t1.date = t2.date AND t1.id = t2.id\
                                                  WHERE t1.time<>t2.time\
                                                  ORDER BY var DESC)\
               SELECT RIGHT(id, 2) AS mercato, date, percentile_approx(var, 0.25) AS percentile25, percentile_approx(var, 0.50) AS percentile50, percentile_approx(var, 0.75) AS percentile75\
               FROM variazione GROUP BY RIGHT(id, 2), date")\
         .show(10)
   
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

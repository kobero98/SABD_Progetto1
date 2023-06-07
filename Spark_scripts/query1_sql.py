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
    spark.sql("WITH hourTable(idFr, value, shortTime, date) \
               AS (SELECT id, value, SUBSTR(time, 1, 2), date FROM trading WHERE secType='E' AND id LIKE concat('%','FR'))\
               SELECT date, shortTime, idFr, MIN(value) AS min, MAX(value) AS max, AVG(value) AS mean, COUNT(value) AS Eventi\
               FROM hourTable\
               GROUP BY idFr, date, shortTime\
               ORDER BY date, shortTime ASC")\
         .coalesce(1)\
         .write.mode('overwrite')\
         .option('header','true')\
         .csv("hdfs://master:54310/cartellaResult/Query1Result_sql")
    
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

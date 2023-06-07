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
    #calcolare variazione oraria poi per giornata calcolare media e varianza delle variazioni
    #prendi migliori e peggiori 5
    spark.sql("WITH splitHourTable(id, date, hour, residueTime, value) AS (SELECT id, date, SUBSTR(time, 1, 2), SUBSTR(time, 4, 9), value FROM trading),\
                    maxMin(id, date, variazione) AS (SELECT id, date, MAX(value)-MIN(value) FROM splitHourTable \
                                                     GROUP BY id, date, hour \
                                                     ORDER BY id, date, hour),\
                    stat(id, date, stddev, mean) AS (SELECT id, date, STDDEV(variazione) AS standardDev, AVG(variazione) FROM maxMin GROUP BY id, date)\
               SELECT * FROM stat ORDER BY mean ASC LIMIT 5\
              ")\
         .show(10)
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

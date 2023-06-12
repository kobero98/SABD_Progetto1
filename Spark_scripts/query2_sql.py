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
    var = spark.sql("WITH splitHourTable(id, date, hour, residueTime, value) AS (SELECT id, date, SUBSTR(time, 1, 2), SUBSTR(time, 4, 9), value FROM trading),\
                    maxMin(id, date, hour, residueTime, val) AS (SELECT id, date, hour, MAX(residueTime), AVG(value) FROM splitHourTable GROUP BY id, date, hour),\
                    variazione(id, date, time1, time2, var) AS (SELECT t1.id, t1.date, t1.hour, t2.hour, t2.val-t1.val FROM maxMin t1\
                                                  JOIN maxMin t2 ON t1.date = t2.date AND t1.id = t2.id AND t2.hour = t1.hour+1\
                                                  WHERE t1.hour<>t2.hour AND t1.residueTime<>t2.residueTime)\
                    SELECT id, date, STDDEV(var) AS dev, AVG(var) AS media, COUNT(var)*2 AS eventi FROM variazione GROUP BY id, date ORDER BY date, media ASC")\
         .cache()
    var.createOrReplaceTempView("statistiche")
    top = spark.sql("SELECT id, date, dev, media, eventi \
                     FROM \
                    (SELECT id, date, dev, media, eventi, ROW_NUMBER() OVER (PARTITION BY date ORDER BY media DESC) AS rn\
                    FROM statistiche) AS subquery WHERE rn <= 5")\
                .coalesce(1).write.mode('overwrite').option('header','true').csv("hdfs://master:54310/cartellaResult/Query2SqlResult")
    bottom = spark.sql("SELECT id, date, dev, media, eventi \
                        FROM \
                        (SELECT id, date, dev, media, eventi, ROW_NUMBER() OVER (PARTITION BY date ORDER BY media ASC) AS rn\
                        FROM statistiche) AS subquery WHERE rn <= 5")\
                  .coalesce(1).write.mode('overwrite').option('header','true').csv("hdfs://master:54310/cartellaResult/Query2SqlResult")

    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

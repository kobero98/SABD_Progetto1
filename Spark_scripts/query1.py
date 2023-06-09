from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, DateType

import sys,logging
from datetime import datetime
import pandas as pd

# Logging configuration
formatter = logging.Formatter('[%(asctime)s] %(levelname)s @ line %(lineno)d: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(handler)
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
AppName = "Progetto 1 SABD"

#TODO: Si può sostituire con una lambda
def query1filtrer(f):
    return f[1] == "FR" and f[2] == "E"

def parse_map(f):
    x=f.split(sep=",")
    app = x[0].split(".")
    hour = x[3].split(sep=":")
    if (len(app)>1):
        y=[app[0],app[1],x[1],float(x[2]),x[4],x[4]+"/"+hour[0]+"/"+app[0],x[3]]
    else:
        y=["Nome","paese",x[1],x[2],x[4],"data/ora/ID",x[3]]
    return y

def joined_val(f):
    x=f[0].split(sep="/")
    return [x[0], x[1], x[2]+".FR", str(f[1][0][0]), str(f[1][0][1]), str(f[1][1][0]), str(f[1][1][1])]

def main():
    #Creazione dello Spark Context
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    #Lettura del dataset da HDFS
    logger.info("Reading CSV File")
    rdd1 = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                             .map(parse_map)\
                             .filter(query1filtrer)\
                             .map(lambda f: [f[5],f[3]])\
                             .cache()
    
    #Calcolo minimo massimo e media
    min_val = rdd1.reduceByKey(min)
    max_val = rdd1.reduceByKey(max)
    mean_val = rdd1.combineByKey((lambda v: (v, 1)), (lambda C,v: (C[0]+v, C[1]+1)),(lambda C1,C2: (C1[0]+C2[0], C1[1]+C2[1])))\
                   .mapValues(lambda C: [C[0]/C[1], C[1]])
    
    #Aggregazione risultati e salvataggio output su HDFS
    result = min_val.fullOuterJoin(max_val)\
           .fullOuterJoin(mean_val)\
           .map(joined_val)
    #Salvataggio sull'HDFS
    df_schema = StructType([       
                            StructField('data', StringType(), True),
                            StructField('ora', StringType(), True),
                            StructField('azione', StringType(), True),
                            StructField('minimo', StringType(), True),
                            StructField('massimo', StringType(), True),
                            StructField('media', StringType(), True),
                            StructField('counter', StringType(), True),
                            ])
    result.toDF(df_schema)\
         .coalesce(1)\
         .write.mode('overwrite')\
         .option('header','true')\
         .csv("hdfs://master:54310/cartellaResult/Query1Result")
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

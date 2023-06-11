from operator import itemgetter
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
    return [x[4]+'.'+x[0], x[3], x[2]]

def variazione(f):
    daily_events = sorted(list(f[1]), key=itemgetter(1))
    var = float(daily_events[len(daily_events)-1][2])-float(daily_events[0][2])
    splitted = f[0].split(sep='.')
    return [splitted[0]+'_'+splitted[2], var, 2]

def percentili(f):
    count = 0
    splitted = f[0].split(sep = '_')
    entry = sorted(list(f[1]), key=itemgetter(1))
    entry_size = len(f[1]) 
    for i in entry:
        count += i[2]
    return [splitted[0], splitted[1], entry[int(entry_size * 0.25)][1], entry[int(entry_size * 0.50)][1], entry[int(entry_size * 0.75)][1], count]

def main():

    #Creazione dello Spark Context
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    #Lettura del dataset da HDFS e trasformazione in dataframe
    logger.info("Reading CSV File")

    #si crea l'rdd con [data.azione, ora, valore], si raggruppa per data.azione, 
    #si fa la map che calcola la variazione di prezzo per azione per giorno ed ha come output [data_borsa, variazione, count],
    #si ragruppa per data_borsa, si calcolano i percentili
    df = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                           .map(parse_map)\
                           .groupBy(lambda f:f[0])\
                           .filter(lambda f:len(f[1])>1)\
                           .map(variazione)\
                           .groupBy(lambda f:f[0])\
                           .map(percentili)\
                           .toDF(schema=["Data","Borsa", "precentile_25th", "percentile_50th", "percentile_75th", "Eventi"])\
                           .coalesce(1)\
                           .write.csv("hdfs://master:54310/cartellaResult/Query3Result", header=True, mode="overwrite")
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

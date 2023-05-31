from pyspark.sql import SparkSession
from pyspark.sql.functions import col,explode
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from pathlib import Path
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
# current time variable to be used for logging purpose
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# change it to your app name
AppName = "MyPySparkApp"

def query2Map(f):
    x=f.split(sep=",")
    if (x[0] != "ID"):
        y=[x[0],x[1],float(x[2]),x[3],x[4]]
    else:
        y=["",x[1],x[2],x[3],x[4]]
    return y
def calcoloLista(f):
    l=[]
    for i in f[1]:
        l.append([i[3],i[2]])
    m=max(l,key=lambda f:f[0])
    return [f[0],m]

def cambioChiave(f):
    x=f[0].split("/")
    return [x[0]+"/"+x[2],[x[1],f[1][1]]]
def funzioneTrasformazioneFinale(f):
    newArray=[]
    z=-1    
    c=0
    for i in f[1]:
        c=c+1
        if z!= -1:
            newArray.append(i[1]-z)
            z=i[1]
        else:
            z=i[1]
    return [f[0],c,newArray]
def statisticheFinali(f):
    somma=0.0
    sommaQuadra=0.0
    app=f[0].split("/")
    count = 0
    for i in f[2]:
        somma=somma+i
        sommaQuadra=sommaQuadra+i**2
        count = count +1
    media = somma/count
    mediaQuadra=sommaQuadra/count
    dev = (mediaQuadra - media**2)**0.5
    return [app[0],app[1],media,dev,f[1]]
def main():
    hdfs_dir = "/cartellaResult/Query2ResultBot/"
                

    # start spark code
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    logger.info("Reading CSV File")
    #il primo rdd viene creato a partire dal file che trova sull hdfs e lo converte in un formato utilizzabile filtrando le possibili righe nulle
    rdd1 = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                             .map(query2Map)\
                             .filter(lambda f: not (f[0]=="" or f[1]=="" or  f[3]=="" or f[4]==""))
    rdd2 = rdd1.groupBy(lambda f: f[4]+"/"+f[3].split(sep=":")[0]+"/"+f[0])\
                .map(calcoloLista)\
                .map(cambioChiave)\
                .groupByKey()\
                .map(funzioneTrasformazioneFinale)\
                .filter(lambda f: f[1]>1)\
                .map(statisticheFinali)\
                .groupBy(lambda f:f[0])\
                .cache()
    bot = rdd2.map(lambda f: [f[0],sorted(f[1],key=lambda f:f[2])[:5]])\
                .toDF(schema=["Date","col2"]).withColumn("col2",explode("col2"))
    resultBot = bot.select(bot["Date"],bot["col2"][1].alias("ID"),bot["col2"][2].alias("Mean"),bot["col2"][3].alias("StdDev"),bot["col2"][4].alias("Count"))
    top = rdd2.map(lambda f: [f[0],sorted(f[1],key=lambda f:f[2],reverse=True)[:5]])\
                .toDF(schema=["Date","col2"]).withColumn("col2",explode("col2"))
    resultTop = top.select(top["Date"],top["col2"][1].alias("ID"),top["col2"][2].alias("Mean"),top["col2"][3].alias("StdDev"),top["col2"][4].alias("Count"))
    resultBot.coalesce(1).write.csv("hdfs://master:54310"+"/cartellaResult/Query2ResultBot", header=True, mode="overwrite")
    resultTop.coalesce(1).write.csv("hdfs://master:54310/cartellaResult/Query2ResultTop", header=True, mode="overwrite")
    spark.stop()
    return None

# Starting point for PySpark
if __name__ == '__main__':
    main()
    sys.exit()

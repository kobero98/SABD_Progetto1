from pyspark.sql import SparkSession
from pyspark.sql.functions import col
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
# current time variable to be used for logging purpose
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# change it to your app name
AppName = "MyPySparkApp"

def query1filtrer(f):
    return f[1] == "FR" and f[2] == "E"
def query1map(f):
    x=f.split(sep=",")
    app = x[0].split(".")
    hour = x[3].split(sep=":")
    if (len(app)>1):
        y=[app[0],app[1],x[1],float(x[2]),x[4],x[4]+"/"+hour[0]+"/"+app[0],x[3]]
    else:
        y=["Nome","paese",x[1],x[2],x[4],"data/ora/ID",x[3]]
    return y
def query1Min(f,x):
    if f<x:
        return f
    else:
        return x
def query1Max(f,x):
    if f>x:
        return f
    else:
        return x
def funcQ1(f):
    x=f[0].split(sep="/")
    return [x[0],x[1],x[2]+".FR",f[1],f[3],f[2],f[4]]
def main():
    # start spark code
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    print("ciao\n")
    #do something here
    logger.info("Reading CSV File")
    rdd1 = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv").map(query1map).filter(query1filtrer).map(lambda f: [f[5],f[3]]).cache()
    minVal = rdd1.reduceByKey(query1Min)
    maxVal = rdd1.reduceByKey(query1Max)
    sommVal = rdd1.reduceByKey(lambda x,y:x+y)
    countVal = rdd1.map(lambda x: [x[0],1]).reduceByKey(lambda x,y:x+y)
    pars = minVal.fullOuterJoin(maxVal).fullOuterJoin(sommVal).fullOuterJoin(countVal).map(lambda f: [f[0],f[1][0][0][0],f[1][0][0][1],f[1][0][1]/f[1][1],f[1][1]])
    resultQ1 = pars.map(funcQ1)
    resultQ1.map(lambda f: f[0]+","+f[1]+","+f[2]+","+str(f[3])+","+str(f[4])+","+str(f[5])).saveAsTextFile("hdfs://master:54310/cartellaResult/Query1Result.csv") 
    spark.stop()
    return None

# Starting point for PySpark
if __name__ == '__main__':
    main()
    sys.exit()

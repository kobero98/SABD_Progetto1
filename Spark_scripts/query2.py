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
def query2Map(f):
    x=f.split(sep=",")
    if (x[0] != "ID"):
        y=[x[0],x[1],float(x[2]),x[3],x[4]]
    else:
        y=[x[0],x[1],x[2],x[3],x[4]]
    return y
def funcfilt(f):
    if f[0] == "" or f[1] == "" or f[3] == "" or f[4] == "":
        return False
    return True
def calcoloLista(f):
    l=[]
    for i in f[1]:
        l.append([i[3],i[2]])
    m=max(l,key=lambda f:f[0])
    #sorted(l,key=lambda f:f[0])
    return [f[0],m]
def cambioChiave(f):
    if not f[0].endswith("ID"):
        x=f[0].split("/")
        return [x[0]+"/"+x[2],[x[1],f[1][1]]]
    else:
        return ["Data/ID","hr/value"]
def funzioneTrasformazioneFinale(f):
    if f[0].startswith("Data"):
        return ["Data/ID","len","lista_differenze"]
    newArray=[]
    z=0.0
    for i in f[1]:
        newArray.append(i[1]-z)
        z=i[1]
    return [f[0],len(newArray),newArray]
def FinalQuery(f):
    if f[0].startswith("Data"):
        return ["Data","ID","Media","STD.DEV.","Count"]
    somma=0.0
    sommaQuadra=0.0
    app=f[0].split("/")
    if (len(f)<3):
        return ["Errore","Errore"]
    for i in f[2]:
        somma=somma+i
        sommaQuadra=sommaQuadra+i**2
    media = somma/f[1]
    mediaQuadra=sommaQuadra/f[1]
    dev = (mediaQuadra - media**2)**0.5
    return [app[0],app[1],media,dev,f[1]]
def main():
    # start spark code
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    #do something here
    logger.info("Reading CSV File")
    rdd1 = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv").map(query2Map).filter(funcfilt).cache()
    rdd2 = rdd1.groupBy(lambda f: f[4]+"/"+f[3].split(sep=":")[0]+"/"+f[0]).map(calcoloLista).map(cambioChiave).groupByKey().map(funzioneTrasformazioneFinale).cache()
    #resultQ2 = rdd2.map(FinalQuery)
    #resultQ2.map(lambda f: f[0]+","+f[1]+","+str(f[2])+","+str(f[3])+","+str(f[4])).saveAsTextFile("hdfs://master:54310/cartellaResult/Query2Result.csv") 
    rdd3 = rdd2.map(lambda f:[f[0],max(f[2])]).sortByKey(True,keyfunc=lambda f:f[0].split(sep ="/")[0])
    for i in rdd3.collect():
        print(i)
    rdd4 = rdd2.map(lambda f:[f[0],min(f[2])])
    spark.stop()
    return None

# Starting point for PySpark
if __name__ == '__main__':
    main()
    sys.exit()

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
    return [splitted[0], splitted[2], var, 2]


def main():

    #Creazione dello Spark Context
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    #Lettura del dataset da HDFS e trasformazione in dataframe
    logger.info("Reading CSV File")
    df = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                           .map(parse_map)\
                           .groupBy(lambda f:f[0])\
                           .filter(lambda f:len(f[1])>1)\
                           .map(variazione)\
                           .toDF(schema=["data", "borsa", "valore", "count"])
    
    #Calcolo percentili e eventi considerati con i dataframe
    df = df.groupBy(['data', 'borsa']).agg(expr("percentile_approx(valore, 0.25)").alias('Percentile25th'),\
                                           expr("percentile_approx(valore, 0.50)").alias('Percentile50th'),\
                                           expr("percentile_approx(valore, 0.75)").alias('Percentile75th'),\
                                           expr("sum(count) as total_count").alias('total_count'))\
                                      .coalesce(1).write.mode('overwrite').option('header','true').csv("hdfs://master:54310/cartellaResult/Query3Result")
                                     
    #pd.DataFrame(df.collect()).to_csv("hdfs://master:54310/cartellaResult/Query3Result", header=True)
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

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
    app = x[0].split(".")
    if (len(app)>1):
        y=[x[4], app[1], x[2]]
    else:
        y=[x[4],x[0],"paese"]
    return y

def main():

    #Creazione dello Spark Context
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")

    #Lettura del dataset da HDFS e trasformazione in dataframe
    logger.info("Reading CSV File")
    df = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")\
                           .map(parse_map)\
                           .toDF(schema=["data", "borsa", "valore"])
    
    #Calcolo percentili e eventi considerati con i dataframe
    df = df.groupBy(['data', 'borsa']).agg(expr("percentile_approx(valore, 0.25)").alias('Percentile25th'),\
                                           expr("percentile_approx(valore, 0.50)").alias('Percentile50th'),\
                                           expr("percentile_approx(valore, 0.75)").alias('Percentile75th'),\
                                           count('data'))\
                                      .sort(['data'])\
                                      .coalesce(1).write.mode('overwrite').option('header','true').csv("hdfs://master:54310/cartellaResult/Query3Result")
                                     
    #pd.DataFrame(df.collect()).to_csv("hdfs://master:54310/cartellaResult/Query3Result", header=True)
    
    spark.stop()
    return None

if __name__ == '__main__':
    main()
    sys.exit()

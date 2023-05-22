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
        y=[app[0],app[1],x[1],float(x[2]),x[4],x[4]+hour[0]+app[0],x[3]]
    else:
        y=["Nome","paese",x[1],x[2],x[4],"data-ora-ID",x[3]]
    return y
def query1Min(f,x):
    if f[3]<x[3]:
        return f[3]
    else:
        return x[3]
def query1Max(f,x):
    if f[3]>x[3]:
        return f[3]
    else:
        return x[3]
def minMap(f):
    for i in f[1]:
        m=i[3]
    return f[0],m;
def main():
    # start spark code
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    print("ciao\n")
    #do something here
    logger.info("Reading CSV File")
    #df_category = spark.read.option("header","true").csv("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")
    #print(df_category.dtypes)
    rdd1 = spark.sparkContext.textFile("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv").map(query1map).filter(query1filtrer)
    rdd2 = rdd1.groupBy(lambda f: f[5]).cache()
    minimoVal = rdd2.reduceByKey(query1Min).map(minMap)
    massimoVal = rdd2.reduceByKey(query1Max).map(minMap)
    mediaVal = rdd2.reduceByKey(lambda x,y: y+x[3])
    for i in mediaVal.collect():
        for j in i[1]:
            print(i,j)
    #max1 = rdd1.max(lambda f : f[3])
    # min1 = rdd1.min(lambda f : f[3])
    #print(type(max1),type(min1))
    # x = rdd1.collect()
    #for i in x: print(i)
    #df_category.createOrReplaceTempView("view1")
    #result = spark.sql("SELECT *,count(*)  FROM view1 where SecType='E' and ID LIKE '%.FR' GROUP BY 'Trading date','Trading time'")
    #result.show()
    # print(result)
    # df_category2 = df_category.filter(df_category.SecType == "E")
    # df_category3 = df_category2.loc[df_category2["ID"].str.endswith(".FR")]
    # logger.info("Previewing CSV File Data")
    # df_category3.show(truncate=False)
    # logger.info("Ending spark application")
    # end spark code
    spark.stop()
    return None

# Starting point for PySpark
if __name__ == '__main__':
    main()
    sys.exit()

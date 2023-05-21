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


def main():
    # start spark code
    spark = SparkSession.builder.appName(AppName+"_"+str(dt_string)).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    logger.info("Starting spark application")
    print("ciao\n")

    #do something here
    logger.info("Reading CSV File")
    df_category = spark.read.option("header","true").csv("hdfs://master:54310/cartellaNIFI/out500_combined+header.csv")
    df_category.createOrReplaceTempView("view1")
    result = spark.sql("SELECT ID,count(*)  FROM view1 where SecType='E' and ID LIKE '%.FR' GROUP BY ID")
    result.show()
    print(result)
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

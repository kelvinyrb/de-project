# --- Imports ---
import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.functions import floor, col, expr, from_unixtime, concat, concat_ws, lit, hour, minute, year
import subprocess

# --- Declare Variables ---
measure_code = 'MYH0036'
LOCAL_BASE_PATH = 'data'
measure_path = f'{LOCAL_BASE_PATH}/{measure_code}'
project_id = 'de-zoomcamp-project-377704'
bucket_name = f"de-project-bucket_{project_id}"
table_id = 'median_wait_time'
credentials_location = '/.gc/gc-key.json'

# --- Spark ---
conf = SparkConf() \
    .setMaster('local[*]') \
    .setAppName('test') \
    .set("spark.jars", "/home/spark-connectors/gcs-connector/gcs-connector-hadoop3-2.2.5.jar,/home/spark-connectors/bigquery-connector/spark-3.1-bigquery-0.28.0-preview.jar") \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location) \
    .set("spark.driver.extraClassPath", "/home/spark-connectors/gcs-connector/gcs-connector-hadoop3-2.2.5.jar") \
    .set("temporaryGcsBucket", bucket_name)
sc = SparkContext.getOrCreate(conf=conf)
hadoop_conf = sc._jsc.hadoopConfiguration()
hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)
hadoop_conf.set("fs.gs.auth.service.account.enable", "true")

spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()
print('scWebURL:', sc.uiWebUrl)

# CREATE SPARK DFs FROM GCS FILES AND JOIN
command = ['gsutil', 'ls', f'gs://{bucket_name}/{measure_path}/']
output = subprocess.check_output(command).decode().split('\n')
for line in output:
    if line.strip():
        print(line.strip())
df_values = spark.read.parquet(f'gs://{bucket_name}/{measure_path}/values.parquet')
df_reported_measures = spark.read.parquet(f'gs://{bucket_name}/{measure_path}/reported_measures.parquet')
df_reporting_units = spark.read.parquet(f'gs://{bucket_name}/{measure_path}/reporting_units.parquet')
df_datasets = spark.read.parquet(f'gs://{bucket_name}/{measure_path}/datasets.parquet')
df_join = df_values.join(df_reported_measures, on=['reported_measure_code'], how='inner')
df_join = df_join.join(df_reporting_units, on=['reporting_unit_code'], how='inner')
df_join = df_join.join(df_datasets, on=['data_set_id'], how='inner')

df_join = df_join.withColumnRenamed('value', 'median_wait_time_minutes')
df_join = df_join.withColumn('year', concat_ws('-', year('reporting_start_date'), year('reporting_end_date')))

# DELETE TABLE IF EXISTS
subprocess.run(['bq', 'rm', '-f', f'{project_id}:{measure_code}.{table_id}'])

# WRITE TO BIGQUERY
description = """"
The length of time spent in the emergency department (ED) from arrival to departure, including the median time patients spent in the emergency department (time until half of the patients (50%) had departed from the emergency department).
Data are presented for all patients, patients treated and admitted to the same hospital, and patients discharged from emergency department (whether discharged, left at their own risk or referred to another hospital).
"""
df_join.write.format('bigquery') \
    .mode('overwrite') \
    .option('table', f'{measure_code}.{table_id}') \
    .option('description', description) \
    .save()
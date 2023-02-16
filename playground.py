#!/usr/bin/env python
# coding: utf-8

import argparse

import requests
import pandas as pd
import time
import os

parser = argparse.ArgumentParser()

parser.add_argument('--bucket_name', required=True)
parser.add_argument('--filename', required=True)
parser.add_argument('--output_table', required=True)

args = parser.parse_args()

bucket_name = args.bucket_name
filename = args.filename
output_table = args.output_table

print('bucket_name:',bucket_name)
print('filename:',filename)
print('output_table:',output_table)

# SPARK
import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext

spark = SparkSession.builder \
    .appName('test2') \
    .getOrCreate()
print('scWebURL:', spark.sparkContext.uiWebUrl)

spark.conf.set('temporaryGcsBucket', 'dataproc-staging-australia-southeast2-45508436754-5cvn3fov')

# READ PARQUET FROM GCS
print("Reading...")
input_df = spark.read.parquet(f'gs://{bucket_name}/{filename}')
print("Read success.")

# WRITE TABLE TO BQ
print("Writing...")
input_df.write.format('bigquery') \
    .option('table', output_table) \
    .mode('overwrite') \
    .save()
print("Write success.")
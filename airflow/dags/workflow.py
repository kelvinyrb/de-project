# ============
# WORKFLOW DAG
# ============

# --- Imports ---
import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import requests
import json
import pandas as pd
import time
import os
import subprocess

# --- Declare Variables ---
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BASE_URL ='https://myhospitalsapi.aihw.gov.au//api/v1'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
measure_category_code = 'MYH-ED-TIME'
measure_code = 'MYH0036'
LOCAL_BASE_PATH = 'data'
project_id = 'de-zoomcamp-project-377704'
bucket_name = f"de-project-bucket_{project_id}"

# --- Functions ---
def ingest(BASE_URL: str, headers: dict, measure_category_code: str, measure_code: str, LOCAL_BASE_PATH: str, bucket_name: str):
    # CREATE VALUES TABLE
    value_response = requests.get(f'{BASE_URL}/measures/{measure_code}/data-items', headers=headers).json()
    value_list = []
    for result in value_response['result']:
        value_list.append([result['reported_measure_code'], result['reporting_unit_summary']['reporting_unit_code'], result['value'],result['data_set_id']])
    values_df = pd.DataFrame(data=value_list, columns=['reported_measure_code', 'reporting_unit_code', 'value', 'data_set_id'])
    values_df.name = 'values'
    
    # CREATE DATASETS TABLE
    dataset_response = requests.get(f'{BASE_URL}/datasets', headers=headers).json()
    dataset_list = []
    for result in dataset_response['result']:
        dataset_list.append([result['data_set_id'], result['data_set_name'], result['reporting_start_date'], result['reporting_end_date']])
    datasets_df = pd.DataFrame(data=dataset_list, columns=['data_set_id', 'data_set_name', 'reporting_start_date', 'reporting_end_date'])
    datasets_df.name = 'datasets'
    
    # CREATE REPORTED MEASURES TABLE
    reported_measure_code_list = list(values_df['reported_measure_code'].unique())
    reported_measure_list = []
    for reported_measure_code in reported_measure_code_list:
        reported_measure_response = requests.get(f'{BASE_URL}/reported-measures/{reported_measure_code}', headers=headers).json()
        reported_measure_list.append([reported_measure_code, reported_measure_response['result']['reported_measure_name']])
    reported_measures_df = pd.DataFrame(data=reported_measure_list, columns=['reported_measure_code', 'reported_measure_name'])
    reported_measures_df.name = 'reported_measures'
    
    # CREATE REPORTING UNITS TABLE
    reporting_unit_response = requests.get(f'{BASE_URL}/reporting-units', headers=headers).json()   

    reporting_unit_list = []
    for result in reporting_unit_response['result']:
        # GET STATE
        mapped_reporting_units = result['mapped_reporting_units']
        state = None
        for mapped_reporting_unit in mapped_reporting_units:
            if mapped_reporting_unit['map_type']['mapped_reporting_unit_code'] == "STATE_MAPPING":
                state = mapped_reporting_unit['mapped_reporting_unit']['reporting_unit_code']
                break # Set state as the first reporting_unit_code in mapped_reporting_units

        # GET REPORTING UNIT INFO
        reporting_unit_list.append([result['reporting_unit_code'], result['reporting_unit_name'], result['reporting_unit_type']['reporting_unit_type_code'], result['reporting_unit_type']['reporting_unit_type_name'], state, result['closed'], result['private'], result['latitude'], result['longitude']])

    reporting_units_df = pd.DataFrame(data=reporting_unit_list, columns=['reporting_unit_code', 'reporting_unit_name', 'reporting_unit_type_code', 'reporting_unit_type_name', 'state', 'closed', 'private', 'latitude', 'longitude'])
    reporting_units_df.name = 'reporting_units'
    
    # CREATE LIST OF DATAFRAMES
    df_list = [values_df, datasets_df, reported_measures_df, reporting_units_df]
    logging.info("Created df_list")
    
    # LOAD PANDAS DFs TO LOCAL DISK AS PARQUET
    measure_path = f'{LOCAL_BASE_PATH}/{measure_code}'
    if not os.path.exists(measure_path):
        os.makedirs(measure_path)
        logging.info('Made measure_path')
    else:
        logging.info('Measure_path already exists.')
    for df in df_list:
        file_path = os.path.join(f'{LOCAL_BASE_PATH}/{measure_code}', f'{df.name}.parquet')
        df.to_parquet(file_path)
        logging.info(f'{df.name}.parquet created.')
    
    # LOAD PARQUET FILES TO GCS
    subprocess.run(['gsutil', '-m', 'cp', '-r', LOCAL_BASE_PATH, f'gs://{bucket_name}/'])
    logging.info("Loaded to GCS")


# --- DAG ---
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023,2,20),
    'max_active_runs': 1,
    'depends_on_past': False,
    'catchup': False,
    'retries': 0
}
with DAG(
    dag_id='workflow',
    default_args=default_args,
    schedule_interval='@once',
) as dag:
    ingest_task = PythonOperator(
        task_id='ingest_task',
        python_callable=ingest,
        op_kwargs={
            'BASE_URL': BASE_URL,
            'headers': headers,
            'measure_category_code': measure_category_code,
            'measure_code': measure_code,
            'LOCAL_BASE_PATH': LOCAL_BASE_PATH,
            'bucket_name': bucket_name
        }
    )
    
    write_to_bigquery_task = BashOperator(
        task_id="write_to_bigquery_task",
        bash_command="python /opt/airflow/scripts/write_to_bigquery.py"
    )
    
    # Workflow
    ingest_task >> write_to_bigquery_task
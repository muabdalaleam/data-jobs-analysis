"""
This file runs the queries in the `queries` folder in an order so they don't raise an
   error. 

Important note: the queries that will be runned are DML queries.
"""

from google.cloud import bigquery
import pandas as pd
import os

dataset_id       :str = 'data_jobs_analysis_db'
project_id       :str = 'data-jobs-analysis-db'
credentials_path :str = '../credentials.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

def run_queries(query_path: str) -> None:
    
    print(f'\nStarted excuting {query_path.split("/")[-1]} query.')
    
    with open(query_path, 'r') as sql_file:
        queries = sql_file.read().split(';')[-1]

    client = bigquery.Client()

    for i, query in enumerate(queries):
        if query.strip():
            try:
                job_config = bigquery.QueryJobConfig()
                job_config.use_legacy_sql = False
                query_job = client.query(query, job_config=job_config)
                results = query_job.result()
                print(f'Query {i} in the current queries file executed succesfully.')

            except Exception as e:
                print(f'Error message: {str(e)}')


run_queries('queries/removing-nans.sql')
run_queries('queries/wrong-dtypes-fix.sql')
run_queries('queries/removing-useless-col.sql')
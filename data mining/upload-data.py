''' 
This files will take the CSV files in the data folder & upload them to BigQuerry
Replacing the other ones so you'll need to run the cleaning querries after saving
the data again. 

*(the cleaned data will be saved in the `cleaned-data` folder in the 
  data-engineering directory.)
'''

from google.cloud import bigquery
import pandas as pd
import os

dataset_id       :str = 'data_jobs_analysis_db'
project_id       :str = 'data-jobs-analysis-db'
credentials_path :str = '../credentials.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

dataframes = {
    'linkedin_jobs'   : pd.read_csv('data/linckedin_jobs.csv'),
    'guru_profiles'   : pd.read_csv('data/guru_freelancers.csv'),
    'upwork_profiles' : pd.read_csv('data/upwork_freelancers.csv')}



client = bigquery.Client(project=project_id)

for table_name, df in dataframes.items():
    table_id = f'{project_id}.{dataset_id}.{table_name}'

    job_config = bigquery.LoadJobConfig(write_disposition= 'WRITE_TRUNCATE')
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print(f'DataFrame \'{table_name}\' uploaded as table \'{table_id}\' in BigQuery.')

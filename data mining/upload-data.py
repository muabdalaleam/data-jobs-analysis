""" 
This files will take the CSV files in the data folder & upload them to BigQuerry
Replacing the other ones so you'll need to run the cleaning querries after saving
the data again. 

*(the cleaned data will be saved in the `cleaned-data` folder in the 
  data-engineering directory.)
"""

from google.cloud import bigquery
import pandas
import os

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../credentials.json'

with open('../credentials.json', 'r') as f:
    credentials = f.read()

client = bigquery.Client(credentials= credentials,  project= 'data-jobs-analysis-db')

# results = clie
# print()
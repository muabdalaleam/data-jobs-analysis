import os
import pandas as pd
from flask         import Flask, render_template, jsonify
from google.cloud  import bigquery

app = Flask(__name__, template_folder='templates')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../credentials.json'
client = bigquery.Client()

def execute_query(query):
    df   : pd.DataFrame = client.query(query).to_dataframe()
    data : dict         = df.to_dict()

    data = {key: list(inner_dict.values()) for key, inner_dict in data.items()}
    return data

#------------------------ Salary per job title Pictogram data------------------------
salary_per_job_title_query = '''
    SELECT AVG(salary) AS avg_salary,
        job_title
    FROM data_jobs_analysis_db.linkedin_jobs
    WHERE salary > 100 
    GROUP BY job_title
    ORDER BY avg_salary DESC;'''

salary_per_job_title_data = execute_query(salary_per_job_title_query)
# ------------------------------------------------------------------------------------



@app.route('/')
def index():
    return render_template('index.html')

@app.route("/data/salary_per_job_title_data")
def geo_code():
    return jsonify(salary_per_job_title_data)


if __name__ == '__main__':
    app.run(debug=True)

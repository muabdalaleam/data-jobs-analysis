import os
import pandas as pd
import numpy  as np

from collections   import Counter
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

data_formatter = lambda data: {key: list(inner_dict.values()) for key, inner_dict in data.items()}

#------------------------ Salary per job title Pictogram data------------------------
salary_per_job_title_query = '''
    SELECT AVG(salary) AS avg_salary,
        job_title
    FROM data_jobs_analysis_db.linkedin_jobs
    WHERE   salary > 100 AND
            salary < 200000
    GROUP BY job_title
    ORDER BY avg_salary DESC;'''

salary_per_job_title_data = execute_query(salary_per_job_title_query)
# ------------------------------------------------------------------------------------


#------------------------ Top Paid Skills vs Top Required skills Radial chart------------------------
paid_vs_required_skills_query = '''
    SELECT  *
    FROM data_jobs_analysis_db.linkedin_jobs
    WHERE   salary > 100 AND
            salary < 200000;'''

paid_vs_required_skills_data = execute_query(paid_vs_required_skills_query)

skills_list = np.concatenate(paid_vs_required_skills_data['skills'])
salary_list = paid_vs_required_skills_data['salary']

paid_vs_required_skills_data = pd.DataFrame({'skill': skills_list,
                                            'avg_salary': np.repeat(salary_list, [len(s) for s in paid_vs_required_skills_data['skills']]),
                                            'appending_count': np.ones(len(skills_list))})

paid_vs_required_skills_data = data_formatter(paid_vs_required_skills_data.groupby('skill').agg({
        'avg_salary': 'mean',
        'appending_count': 'sum'
    }).reset_index().to_dict()
)
# ------------------------------------------------------------------------------------


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/data/salary_per_job_title")
def route_1():
    return jsonify(salary_per_job_title_data)

@app.route("/data/paid_vs_required_skills")
def route_2():
    return jsonify(paid_vs_required_skills_data)

if __name__ == '__main__':
    app.run(debug=True)

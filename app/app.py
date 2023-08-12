import os
from flask         import Flask, render_template
from google.cloud  import bigquery

app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client()

@app.route('/')
def index():

    # ------------------Salary Per Job title data visualizaton-----------------
    salary_per_job_title_query = """
        SELECT AVG(salary) AS avg_salary,
            country,
            job_title
        FROM linkedin_jobs
        WHERE salary > 100 
        GROUP BY country, job_title
        ORDER BY avg_salary DESC;''')
    """

    salary_per_job_title_data = execute_query(salary_per_job_title_query)
    # --------------------------------------------------------------------------


    # ---------------Top 10 Paid & requird skills data visualization------------
    # top_paid_and_reqierd_skills_query = """

    # """

    # top_paid_and_reqierd_skills_data = execute_query(top_paid_and_reqierd_skills_query)
    # --------------------------------------------------------------------------

    return render_template('index.html',salary_per_job_title= salary_per_job_title_data,
                                        top_paid_and_reqierd_skills= None)


def execute_query(query):

    data = client.query(query).to_dataframe().to_dict()
    return data

if __name__ == '__main__':
    app.run(debug=True)

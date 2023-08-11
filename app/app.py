import os
from flask         import Flask, render_template
from google.cloud  import bigquery

app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client()

@app.route('/')
def index():

    query = """
        SELECT AVG(salary) AS avg_salary,
            country,
            job_title
        FROM linkedin_jobs
        WHERE salary > 100 
        GROUP BY country, job_title
        ORDER BY avg_salary DESC;''')
    """

    # query2 = """
    #     SELECT ...
    # """

    data = execute_query(query)
    # data2 = execute_query(query2)

    return render_template('index.html', data1= data) # , data2=data2


def execute_query(query):

    data = client.query(query).to_dataframe().to_dict()
    return data

if __name__ == '__main__':
    app.run(debug=True)

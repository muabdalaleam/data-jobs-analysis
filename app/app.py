import os

from flask         import Flask, render_template
from google.cloud  import bigquery

app = Flask(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client()

@app.route('/')
def index():
    query1 = """
        SELECT ...
    """

    query2 = """
        SELECT ...
    """

    data1 = execute_query(query1)
    data2 = execute_query(query2)

    return render_template('index.html', data1=data1, data2=data2)


def execute_query(query):

    query_job = client.query(query)
    results = query_job.result()

    data = []
    for row in results:
        data.append(dict(row))

    return data

if __name__ == '__main__':
    app.run(debug=True)

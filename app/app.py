import os
import pandas as pd
import numpy  as np

from collections   import Counter
from dotenv        import load_dotenv
from flask         import (Flask, render_template, request,
                            jsonify, send_from_directory)
from google.cloud  import bigquery

app = Flask(__name__, template_folder='templates')

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../credentials.json'
client = bigquery.Client()

data_formatter = lambda data: {key: list(inner_dict.values()) for key, inner_dict in data.items()}



def execute_query(query):
    df = client.query(query).to_dataframe()
    data = df.to_dict()
    data = {key: list(inner_dict.values()) for key, inner_dict in data.items()}

    return data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['POST'])
async def main():

    global selected_country
    global selected_job_title

    data = request.get_json()
    selected_country = data.get('country')
    selected_job_title = data.get('job_title')
    
    print(f"Selected country: {selected_country}")
    print(f"Selected job title: {selected_job_title}")


    #------------------------ Salary per job title bar chart data-------------------------
    salary_per_job_title_query = f'''
        SELECT AVG(salary) AS avg_salary,
            job_title
        FROM data_jobs_analysis_db.linkedin_jobs
        WHERE   salary > 100 AND
                salary < 200000 AND
                country = {selected_country}
        GROUP BY job_title
        ORDER BY avg_salary DESC;'''

    salary_per_job_title_data = await execute_query(salary_per_job_title_query)
    # ------------------------------------------------------------------------------------


    #------------------ Top Paid Skills vs Top Required skills Scatter plot---------------
    paid_vs_required_skills_query = f'''
        SELECT  *
        FROM data_jobs_analysis_db.linkedin_jobs
        WHERE   salary > 100 AND
                salary < 200000 AND 
                country = {selected_country} AND
                job_title = {selected_job_title};'''

    paid_vs_required_skills_data = await execute_query(paid_vs_required_skills_query)

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


    # -------------------Peoeple who earned money Pictogram (Upwork)-----------------------
    people_who_earned_money_query = f'''
        SELECT 
        SUM(CASE
                WHEN earnings_amount_new > 1000 THEN 1
                ELSE 0
            END)  / COUNT(*) * 100  AS people_earned_money_percentage,

        SUM(CASE 
                WHEN earnings_amount_new > 1000 THEN 0
                ELSE 1
            END) / COUNT(*) * 100  AS people_didnt_earn_money_percentage

        FROM `data-jobs-analysis-db.data_jobs_analysis_db.upwork_profiles`
        WHERE job_title = {selected_job_title};
    # '''

    people_who_earned_money_data = await execute_query(people_who_earned_money_query)
    # ------------------------------------------------------------------------------------


    # ------------------Total Jobs Per Industry Stacked column chart----------------------
    total_jobs_per_industry_query = f'''
        SELECT COUNT(*) AS total_jobs, industry
        FROM `data-jobs-analysis-db.data_jobs_analysis_db.linkedin_jobs`
        WHERE country = {selected_country} AND
            job_title = {selected_job_title}

        GROUP BY industry
        HAVING industry IS NOT NULL
        ORDER BY total_jobs DESC
        LIMIT 6;
    # '''

    total_jobs_per_industry_data = await execute_query(total_jobs_per_industry_query)
    # ------------------------------------------------------------------------------------


    return jsonify({"salary_per_job_title"    : salary_per_job_title_data,
                    "paid_vs_required_skills" : paid_vs_required_skills_data,
                    "people_who_earned_money" : people_who_earned_money_data,
                    "total_jobs_per_industry" : total_jobs_per_industry_data})


if __name__ == '__main__':
    app.run(debug=True)

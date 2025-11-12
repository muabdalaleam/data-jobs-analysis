import sqlite3
import pandas as pd

DB_URI           = "file:./data/clean_database.db?mode=ro"

with sqlite3.connect(DB_URI, uri=True) as con:
    linkedin_df = pd.read_sql_query("""
        SELECT 
            (salary_min + salary_max) / 2 AS salary,
            searched_job_title AS job_title,
            searched_country AS country,
            skills
        FROM linkedin
        WHERE pay_type = 'Annually' AND
            salary_min IS NOT NULL
        """, con)
    
    upwork_df = pd.read_sql_query("""
        SELECT hour_rate, skills, earnings, 
            searched_job_title AS job_title
        FROM upwork
        """, con)

linkedin_df.to_json("./dashboard/data/linkedin.json", orient="columns", double_precision=2)
upwork_df.to_json("./dashboard/data/upwork.json", orient="columns", double_precision=2)

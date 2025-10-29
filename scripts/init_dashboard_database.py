import sqlite3
import pandas as pd
import duckdb

DB_URI           = "file:./data/clean_database.db?mode=ro"
DASHBOARD_DB_URI = "file:./dashboard/data.sqlite"

with sqlite3.connect(DB_URI, uri=True) as con:
    linkedin_df = pd.read_sql_query("""
        SELECT 
            (salary_min + salary_max) / 2 AS salary,
            searched_job_title AS job_title,
            searched_country AS country,
            skills
        FROM linkedin
        """, con)
    
    upwork_df = pd.read_sql_query("""
        SELECT hour_rate, skills, earnings
        FROM upwork
        """, con)

with sqlite3.connect(DASHBOARD_DB_URI, uri=True) as con:
    linkedin_df.to_sql("linkedin", con, if_exists="replace", index=False)
    upwork_df.to_sql("upwork", con, if_exists="replace", index=False)

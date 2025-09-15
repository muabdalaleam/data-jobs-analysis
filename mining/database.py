import pandas as pd
import sqlite3

con = sqlite3.connect("./data/raw_database.db")

linkedin_df = pd.read_csv("./data/linkedin_jobs.csv") 
guru_df     = pd.read_csv("./data/guru_freelancers.csv") 
upwork_df   = pd.read_csv("./data/upwork_freelancers.csv") 

linkedin_df.to_sql("linkedin", con, if_exists="fail", index=False)
guru_df.to_sql("guru", con, if_exists="fail", index=False)
upwork_df.to_sql("upwork", con, if_exists="fail", index=False)

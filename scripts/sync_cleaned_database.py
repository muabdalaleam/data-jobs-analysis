import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from datetime import datetime, timedelta, date
from typing import Optional, Tuple, List
from IPython.display import display, Markdown
from ipywidgets import IntProgress
import sqlite3
import time
import ast
import sys
import re
import os


RAW_DB_URI = "file:./data/raw_database.db?mode=ro" # XXX
CLEAN_DB_PATH = "./data/clean_database.db"
QA_MODEL_NAME     = "deepset/tinyroberta-squad2"
QA_MODEL_PATH     = "./models/tinyroberta-squad2-model"
QA_TOKENIZER_PATH = "./models/tinyroberta-squad2-tokenizer"

with sqlite3.connect(RAW_DB_URI, uri=True) as con:
    # hardcoded i know and don't give a shit
    linkedin_df = pd.read_sql_query("""
        SELECT       *, "2025_09_15" as collection_date  FROM linkedin_jobs_2025_09_15
        UNION SELECT *, "2025_09_25" as collection_date  FROM linkedin_jobs_2025_09_25
    """, con)

    upwork_df = pd.read_sql_query("""
        SELECT       *, "2025_09_15" as collection_date FROM upwork_freelancers_2025_09_15 
        UNION SELECT *, "2025_09_25" as collection_date FROM upwork_freelancers_2025_09_25
        UNION SELECT *, "2025_10_06" as collection_date FROM upwork_freelancers_2025_10_06
    """, con)

    guru_df = pd.read_sql_query("""
        SELECT *, "2025_09_15" as collection_date FROM guru_freelancers_2025_09_15
    """, con)


# Firstly I should remove the duplicates before starting
linkedin_df = linkedin_df.drop_duplicates(subset=["id"], keep="first")
upwork_df   = upwork_df.drop_duplicates(subset=["id"], keep="first")
guru_df     = guru_df.drop_duplicates(subset=["url"], keep="first")


# Now let's remove the "Data entry" rules that was collected in the start of the project
linkedin_df = linkedin_df.loc[linkedin_df["searched_job_title"] != "Data entry"]
upwork_df   = upwork_df  .loc[upwork_df["searched_job_title"] != "Data entry"]
guru_df     = guru_df    .loc[guru_df["searched_job_title"] != "Data Entry"]


# ==================== LinkedIn jobs data cleaning =========================

# Fixing the `posted_since` column to use dates instead of days since the data was collected<br>
# NOTE: it will still be an approximatation because linkedin doesn't specify actual posting date

hour_pattern  = re.compile(r"^[0-9]+ hour")
day_pattern   = re.compile(r"^[0-9]+ day")
week_pattern  = re.compile(r"^[0-9]+ week")
month_pattern = re.compile(r"^[0-9]+ month")
year_pattern  = re.compile(r"^[0-9]+ year")

value_pattern = re.compile(r"^[0-9]+")

def parse_posted_since(row: pd.Series) -> date:
    posted_since    = row["posted_since"]
    collection_date = datetime.strptime(row["collection_date"], "%Y_%m_%d")

    if not(collection_date and posted_since):
        return None

    used_pattern: re.Pattern = None
    for pattern in [hour_pattern, day_pattern, week_pattern,
                    month_pattern, year_pattern]:
        if re.match(pattern, posted_since):
            used_pattern = pattern
            break

    interval_value = int(value_pattern.search(posted_since).group())
    interval_unit: timedelta = datetime.hour

    if used_pattern == hour_pattern:
        interval_unit = timedelta(hours=1)

    elif used_pattern == day_pattern:
        interval_unit = timedelta(days=1)

    elif used_pattern == week_pattern:
        interval_unit = timedelta(weeks=1)

    elif used_pattern == month_pattern:
        interval_unit = timedelta(days=29.53)

    elif  used_pattern == year_pattern:
        interval_unit = timedelta(days=365.25)

    else:
        return np.nan

    interval = interval_value * interval_unit

    return datetime.date(collection_date - interval)

linkedin_df["posted_since"] = linkedin_df.apply(
    lambda row: parse_posted_since(row), axis=1)


# Replacing the "Not Applicable" value in the `seniority_level` column with None
linkedin_df["seniority_level"] = linkedin_df["seniority_level"].replace(
    "Not Applicable", None)


# Extracting the salary using an extractive Q/A model + regex
if os.path.isfile(QA_MODEL_PATH) and \
   os.path.isfile(QA_TOKENIZER_PATH):
    model     = AutoModelForQuestionAnswering.from_pretrained(QA_MODEL_PATH)
    tokenizer = AutoTokenizer.from_pretrained(QA_TOKENIZER_PATH)
else:
    model     = AutoModelForQuestionAnswering.from_pretrained(QA_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(QA_MODEL_NAME)
    model    .save_pretrained(QA_MODEL_PATH)
    tokenizer.save_pretrained(QA_TOKENIZER_PATH)

qa_model = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer
)

def extract_salary_range(desc: str) -> Optional[Tuple]:
    """
    params: 
        desc: the job description as a string
    returns: an tuple of the salary range but it would return None if it wansn't found
    This function aims to eliminate "false positives", it's ok to have some true negatives

    NOTE: this function doesn't work well with job description from any language but 
    English
    """
    if not(isinstance(desc, str)):
        return None

    question = "What is the salary range for the role?"
    output = qa_model(question = question, context = desc)

    if output["score"] < 0.3: 
        return None

    matches = re.findall(
        r"[\$|€|-| ]([0-9,.k]+)",
        output["answer"],
        flags=re.IGNORECASE
    )

    if not(matches):
        return None
    if len(matches) > 2:
        matches = matches[:2]
    elif len(matches) == 1:
        matches = [matches[0], matches[0]]

    salary_range: list = [None, None] # will be converted into a tuple

    for i in range(2):
        is_hour_rate: bool = False
        mag: float = 1.0

        if "," in matches[i]:
            if len(matches[i].split(",")[1]) == 2:
                matches[i] = matches[i].replace(",", ".")
                is_hour_rate = True

        if "k" in matches[i].lower():
            mag = 1000.0

        matches[i] = matches[i].lower()
        matches[i] = matches[i].replace(",", "")
        matches[i] = matches[i].replace("k", "")

        salary_range[i] = float(matches[i]) * mag

    return tuple(salary_range)

def extract_and_update_progress(description: str):
    progress_bar.value += 1
    return extract_salary_range(description)

salary_ranges = linkedin_df["description"].apply(extract_and_update_progress)

linkedin_df["salary_min"] = salary_ranges.apply(lambda x: list(x)[0] if x is not None else x)
linkedin_df["salary_max"] = salary_ranges.apply(lambda x: list(x)[1] if x is not None else x)


# Seperating hour pays from annaul salaries
linkedin_df["pay_type"] = linkedin_df["salary_min"].apply(
    lambda s: None if np.isnan(s) else "Hourly" if s < 200 else "Annually"
)


# Extracting skills from the job descriptions
skills = [
    # Programming & Scripting
    "python", " r ", "java", "scala ", "c++", "c#", " go ", "bash", "sql", "nosql",
    "vba", "powershell", "scala,", " r,", " go,",

    # Data Handling & Databases
    "mysql", "postgresql", "sqlite", "oracle", "mssql", "mongodb", "cassandra",
    "dynamodb", "redis", "elasticsearch", "neo4j", "snowflake", "bigquery", 
    "redshift", "cosmosdb", "athena"

    # Data Processing & ETL
    "pandas", "numpy", "dask", "polars", "pyarrow", "koalas", 
    "airflow", "luigi", "prefect", " dbt", 
    "spark", "pyspark", "hive", "pig", "beam", "flink", "kafka",

    # Visualization & BI
    "matplotlib", "seaborn", "plotly", "bokeh", "altair",
    "powerbi", "tableau", "looker", "qlik",

    # Cloud & DevOps
    "aws", " gcp", "azure", "databricks", " emr", "sagemaker",
    "docker", "kubernetes", "terraform", "jenkins", "git", "github", "gitlab",
    "ci/cd",

    # Machine Learning
    "scikit learn", "scikit-learn", "xgboost", "lightgbm", "catboost", "mlflow",
    "pytorch", "tensorflow", "keras", "jax", "fastai", "onnx", 
    "opencv", "nltk", "spacy", "transformers", "huggingface",

    # Statistics & Math
    "statistics", "probability", "linear algebra", "calculus", "optimization",

    # Big Data & Distributed Systems
    "hadoop", "hdfs", "yarn", "mapreduce", "zookeeper", 

    # Data Engineering & Streaming
    " etl ", " elt ", "data pipeline", "streaming", "batch processing",

    # MLOps & Deployment
    "mlops", "model serving", "feature store", "kubeflow", "tfx", " ray", "nltk",
    "nlp",

    # General Skills
    "excel", "vba", "regex", "json", "xml", "yaml", "parquet", " orc", "avro",
    "api", " rest ", "grpc", "graphql",

    # Soft Skills / Business
    "communication", "storytelling", "problem solving",
    "teamwork", "critical thinking", "project management", "agile", "scrum"
]

def extract_skills(desc: str) -> List[str]:
    found_skills = []
    for skill in skills:
        if skill.lower() in desc.lower():
            found_skills.append(skill)

    return found_skills

linkedin_df["skills"] = linkedin_df["description"].apply(
    lambda s: ",".join(extract_skills(s))
)


# Extracting the required education from the job descriptions using the same model
def extract_required_education(desc: str) -> str:
    """
    params:
        takes the description of a job as a string
    returns:
        returns one of the following ["Bachelor", "Master's", "PhD", "High School", "Not mentioned"]
        based on regex matching
    """
    if not(isinstance(desc, str)):
        return "Not mentioned"

    if re.search(r"high school", desc, re.IGNORECASE):
       return "High School" 

    elif re.search(r"bachelor| b\.s | bs\.", desc, re.IGNORECASE): # bs for bachelor not bullshit (nvm they are the same thing)
        return "Bachelor"

    elif re.search(r"master\'s|masters", desc, re.IGNORECASE):
        return "Master's"

    elif re.search(r"phd|ph\.d", desc, re.IGNORECASE):
        return "PhD"

    else:
        return "Not mentioned"

linkedin_df["education"] = linkedin_df["description"].apply(extract_required_education)

# ==========================================================================


# =================== UpWork freelancers data clearning ====================

# Fixing the empty strings in the `skills` column
upwork_df["skills"] = upwork_df["skills"].apply(
    lambda list_: ", ".join((list(filter(lambda s: len(s) > 0, ast.literal_eval(list_)))))
)

# Now let's remove the clutter strings from some of the columns
def extract_value(s: str) -> int | None:
    value_pattern = re.compile("[0-9]+")

    if not(isinstance(s, str)):
        return None

    match = value_pattern.search(s)

    if not(match):
        return None

    return int(match.group())

for col in ["hours_worked", "hourly_jobs_done", "fixed_jobs_done"]:
    upwork_df[col] = upwork_df[col].apply(extract_value)

# Converting the money format from being a string into being a float for the `hour_rate` and `earnings`
# columns
hour_rate_pattern = re.compile(r"\$[0-9.]+")
earnings_pattern = re.compile(r"\$[0-9]+")

def extract_earnings(s: str) -> int | None:
    if not(isinstance(s, str)):
        return None

    match = earnings_pattern.search(s)
    if not(match):
        return None

    magnitude = 1
    if "K" in s:
        magnitude = 1000
    elif "M" in s:
        magnitude = 1000_000

    return int(match.group()[1:]) * magnitude

def extract_hour_rate(s: str) -> float | None:
    if not(isinstance(s, str)):
        return None

    match = hour_rate_pattern.search(s)

    if not(match):
        return None

    return float(match.group()[1:])

upwork_df["earnings"] = upwork_df["earnings"].apply(extract_earnings)
upwork_df["hour_rate"] = upwork_df["hour_rate"].apply(extract_hour_rate)
# ==========================================================================


# ==================== Guru freelancers data cleaning ======================

# Let's fix the `feedback_percent` and `earnings` format & dtype

def extract_feedback(s: str) -> float | None:
    pattern = re.compile(r"[0-9.,]+")

    if not(isinstance(s, str)):
        return None

    match = pattern.search(s)

    if not(match):
        return None

    return float(match.group())

def extract_earnings(s: str) -> int | None:
    pattern = re.compile(r"\$[0-9,,]+")

    if not(isinstance(s, str)):
        return None

    match = pattern.search(s)

    if not(match):
        return None

    magnitude = 1
    if "K" in s:
        magnitude = 1000
    elif "M" in s:
        magnitude = 1000_000

    earnings_str = match.group()[1:]
    earnings_str = earnings_str.replace(",", "")

    return float(earnings_str) * magnitude

guru_df["feedback_percent"] = guru_df["feedback_percent"].apply(extract_feedback)
guru_df["earnings"] = guru_df["earnings"].apply(extract_earnings)

guru_df[["feedback_percent", "earnings"]].head(5)
# ==========================================================================



# ========================= Storing the cleaned data =======================
with sqlite3.connect(CLEAN_DB_PATH) as con:
    linkedin_df.to_sql("linkedin", con, if_exists="fail", index=False)
    upwork_df.to_sql("upwork", con, if_exists="fail", index=False)
    guru_df.to_sql("guru", con, if_exists="fail", index=False)


# Data-field jobs and freelancing analysis

 [![License: MIT (shield)](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Chart showing most common data-field jobs in the E.U & USA maps (coolest chart I've done)](https://github.com/muabdalaleam/data-jobs-analysis/blob/main/screenshot.jpg?raw=true)

An inspection into the current market of data-field jobs *(data analysis, data science, ML development & data engineering)*
by looking into LinkedIn job postings and freelancers accounts on UpWork & Guru.

---

# Quick links


# Reproduction

## Setup



## Dataset

You can either download the dataset I made from [Kaggle](example.com#example.com#example.com#example.com), or run the scripts needed
to collect the data yourself

The data used in this project was collected using mining scripts in the `scripts` directory which are executed on various
days to collect different data, the output of those scripts are `.csv` files which got aggregated using 
`scripts/sync_raw_databasse.py` resulting in the SqlLite database `data/raw_database.db` which afterwards gets cleaned
using either `notebooks/cleaning.ipynb` or `scripts/sync_cleaned_database.py` which results in a new SqlLite  database
`data/clean_database.db` which is used in the analysis notebooks and interactive web report.

## Notebooks

- [Data-field freelacing analysis]()
- [Data-field jobs analysis]()
- [Cleaning raw data notebook]()


# Data-field jobs and freelancing analysis

 [![License: MIT (shield)](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Chart showing most common data-field jobs in the E.U & USA maps (coolest chart I've done)](https://github.com/muabdalaleam/data-jobs-analysis/blob/main/screenshot.jpg?raw=true)

An inspection into the current market of data-field jobs & freelancing *(data analysis, data science, ML development & data
engineering)* by looking into LinkedIn job postings and freelancers accounts on UpWork & Guru.

---

# Quick links

- [Interactive report](https://muabdalaleam.github.io/data-jobs-analysis/)
- [Job postings analysis notebook](https://nbviewer.org/github/muabdalaleam/data-jobs-analysis/blob/main/notebooks/jobs_analysis.ipynb)
- [Freelancers analysis notebook](https://nbviewer.org/github/muabdalaleam/data-jobs-analysis/blob/main/notebooks/freelancers_analysis.ipynb)
- [Kaggle dataset](https://example.com)*
- [Analysis PDF reports](https://github.com/muabdalaleam/data-jobs-analysis/tree/main/reports)

*: the kaggle dataset is mine for more look [here](#dataset)

# Reproducing

There's no need to reproduce the project if you just want to see it the results [quick links](#quick-links) should be enough
but if you want to see how it works and how it was made follow the steps below:

## Setup

The project was done using *Python 3.12.11* so if you want the exact same results I'd recommend using it but it probalby 
won't matter if you have a close python version.<br>

After you've cloned the repo and moved into it you should create a Python [`venv`](https://docs.python.org/3/library/venv.html)
and activate it *(how? depends on your OS)*. afterwards run:
```pip -r install requirements.txt```

Now you are done setting up the Python virtual environment for the project.

## Dataset

You can either download the dataset I made from [Kaggle](example.com#example.com#example.com#example.com) into `data` dir
or run the scripts needed to collect the data yourself into the `data` dir.

The data used in this project was collected using mining scripts in the `scripts` directory which are executed on various
days to collect different data, the output of those scripts are `.csv` files which got aggregated using 
`scripts/sync_raw_databasse.py` resulting in the SqlLite database `data/raw_database.db` which afterwards gets cleaned
using either `notebooks/cleaning.ipynb` or `scripts/sync_cleaned_database.py` which results in a new SqlLite  database
`data/clean_database.db` which is used in the analysis notebooks and interactive web report.<br>

If you chose to collect the data yourself here're the commands you need to run:

- `mkdir data`
- *Activate your python `venv`*
- `python scripts/mine_linkedin.py`
- `python scripts/upwork_linkedin.py` *remeber to check the cloudflare checkbox in the automated chromium instance*
- `python scripts/guru_linkedin.py`
- `python scripts/sync_raw_databasse.py`

Now you should have `data/raw_database.db` *(if that isn't the case make a github issue)*

Now you can **either** run:
- `./notebooks/cleaning.ipynb` *jupyter notebook*
- `./scripts/sync_cleaned_database.py` *cleaning script*

But know it's gonna take a long time because of the QA model that extracts salary.

And that's it if you any time wanted to update your data repeat all the steps we have done to create the clean database.

## Notebooks

You can execute any of the project's notebooks locally in the `notebooks` directory or just view them from the web viewer
in the links below

- [Data-field jobs analysis](https://nbviewer.org/github/muabdalaleam/data-jobs-analysis/blob/main/notebooks/jobs_analysis.ipynb)
- [Data-field freelacing analysis](https://nbviewer.org/github/muabdalaleam/data-jobs-analysis/blob/main/notebooks/freelancers_analysis.ipynb)
- [Cleaning raw data notebook](https://nbviewer.org/github/muabdalaleam/data-jobs-analysis/blob/main/notebooks/cleaning.ipynb)

## Interactive report

The interactive report is available as a github page [here](https://muabdalaleam.github.io/data-jobs-analysis/) but if you want to host it your self 
here are the steps:

- Make sure you have `data/clean_database.db`
- Activate your venv and execute `python scripts/sync_dashboard_database.py`
- Now you should have `dashboard/data/linkedin.json` & `dashboard/data/upwork.json`
- Initiate a local server at `localhost:5000` by running `python ./dashboard/app.py`

# Analysis findings

Here are some cool findings from the notebooks & the interactive report for more you can either look at the
[notebooks](#notebooks) or the [pdf reports](https://github.com/muabdalaleam/data-jobs-analysis/tree/main/reports).

- Over 50% of postings do not specify a degree requirement, indicating that many companies
are flexible about formal education, relying instead on skills and experience.

- Machine learning roles show strong demand for both junior and senior levels unlike Data analyst
roles which are less open to entry-level candidates, also we can see that data engineering roles
are the most demanding for senior roles.

- Most paid skills in job postings are the data engineering, or ML skills such as C++, PyTorch,
TensorFlow & R language

- Data engineers earn the highest amount per job, ML freelancers earn about half as much per job
as data engineers. time or effort per job is unknown, so earnings per job should not be interpreted
as earnings per hour.

### Thanks for looking into my project ❤️

# Data-field jobs and freelancing analysis

 [![License: MIT (shield)](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Chart showing most common data-field jobs in the E.U & USA maps (coolest chart I've done)](https://github.com/muabdalaleam/data-jobs-analysis/blob/main/screenshot.jpg?raw=true)

An inspection into the current market of data-field jobs *(data analysis, data science, ML development & data engineering)*
by looking into LinkedIn job postings and freelancers accounts on UpWork & Guru. hopefully we 

---

# Quick links

- [Interactive report](https://example.com)
- [Kaggle dataset](https://example.com)*
- [Job postings analysis notebook](https://example.com)
- [Freelancers analysis notebook](https://example.com)
<br>
*: the kaggle dataset is mine for more look [here](##Dataset)

# Reproducing

## Setup

The project was done using *Python 3.12.11* so if you want the exact same results I'd recommend using it but it probalby 
won't matter if you have a close python version.<br>

After you've cloned the repo and moved into it you should create a Python [`venv`](https://docs.python.org/3/library/venv.html)
and activate it *(how? depends on your OS)*. afterwards run:
```pip -r install requirements.txt```

Now you are done setting up the Python virtual environment for the project.

## Dataset

You can either download the dataset I made from [Kaggle](example.com#example.com#example.com#example.com), or run the scripts needed
to collect the data yourself

The data used in this project was collected using mining scripts in the `scripts` directory which are executed on various
days to collect different data, the output of those scripts are `.csv` files which got aggregated using 
`scripts/sync_raw_databasse.py` resulting in the SqlLite database `data/raw_database.db` which afterwards gets cleaned
using either `notebooks/cleaning.ipynb` or `scripts/sync_cleaned_database.py` which results in a new SqlLite  database
`data/clean_database.db` which is used in the analysis notebooks and interactive web report.<br>

If you chose to collect the data yourself here're the commands you need to run:

- *Activate your python `venv`*
- `mkdir data`
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

You can re execute any of the project's notebooks either using the 

- [Data-field freelacing analysis]()
- [Data-field jobs analysis]()
- [Cleaning raw data notebook]()


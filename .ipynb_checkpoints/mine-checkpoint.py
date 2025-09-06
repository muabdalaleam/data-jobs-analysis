import requests
from bs4 import BeautifulSoup

## Data job titles we are searching for
DATA_JOBS_TITLES = ['Data entry', 'Data engineer',
                    'Data scientist', 'Data analyst',
                    'ML developer']

COUNTRIES = ['European Union', 'United States']

def scrape_linkedin_jobs(country:  str, job_title: str, page: int) -> BeautifulSoup:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept-Encoding': '*',
        'Connection': 'keep-alive',
    }

    page: int = (page - 1) * 25
    url: str = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job_title}&' + \
    f'location={country}&geoId=90000084&trk=public_jobs_j%20obs-search-bar_search-submit&position=1&pageNum=0&start={page}'

    response = requests.get(url, headers= headers)
    soup = BeautifulSoup(response.content,'html.parser')

    return  soup

# https://www.linkedin.com/jobs/search?keywords={job_title}&location={country}&\geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0
# https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=United%20States&\geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0
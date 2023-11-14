# ====================== Importing Packeges & Read params ======================
import re
import sys
import json
import argparse
import warnings
import requests
import cloudscraper
import numpy             as np
import pandas            as pd
import seaborn           as sns
import matplotlib.pyplot as plt

from itertools                          import count
from bs4                                import BeautifulSoup
from selenium                           import webdriver
from google.cloud                       import bigquery
from urllib.request                     import urlopen
from selenium.webdriver.common.by       import By
from scrapy.utils.log                   import configure_logging
from selenium.webdriver.common.keys     import Keys
from IPython.display                    import set_matplotlib_formats
from selenium.webdriver.chrome.service  import Service
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.support.ui      import WebDriverWait
from webdriver_manager.chrome           import ChromeDriverManager
from selenium.webdriver.support         import expected_conditions as EC
# ==============================================================================


# ============================= Taking app params ==============================
parser = argparse.ArgumentParser(description= '''Collect jobs data and train a ChatBot on it and creates you a Streamlit
                                                 app to ask the ChatBot for jobs that fits you (FOR FREE !!!!) ''')

parser.add_argument('--country',       type= str, required= True,  help= 'Specify a valid country name or a geographic region.')
parser.add_argument('--job_title',     type= str, required= True,  help= 'Specify a job title to search for as a string.')
parser.add_argument('--location_type', type= str, required= False, help= 'Specify a location type from: [Remote, on-site, Hybrid] (defualt = \'Remote\')')
parser.add_argument('--max_pages',     type= int, required= False, help= 'Specify the max jobs pages you want the scraper to dive into (defualt = 10).')

args = parser.parse_args()

country       : str = args.country
job_title     : str = args.job_title
location_type : str = args.location_type
max_pages     : int = args.max_pages

if not max_pages:
    max_pages = 10

if not location_type:
    location_type = 'Remote'
# ==============================================================================


# ============================ Setting up scrapers =============================
def scrape_page_fast(url: str) -> BeautifulSoup:

    scraper = cloudscraper.create_scraper(delay= 10,browser= {
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True,
        'mobile': False}) 
    
    content = scraper.get(url).text 
    return BeautifulSoup(content)


def scrape_page(url: str, retrieve_new_url= None, user_agent= None) -> BeautifulSoup:

    driver = webdriver.Chrome()
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))


    html = BeautifulSoup(driver.page_source)

    if retrieve_new_url:
        new_url = driver.current_url

        driver.quit()
        return html, new_url
        
    driver.quit()
    return html


def linkedin_scraper(country:   str,
                     job_title: str,
                     page:      int) -> BeautifulSoup:
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept-Encoding': '*',
        'Connection': 'keep-alive'}

    page: int = (page - 1) * 25
    url: str = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job_title}&' + \
    f'location={country}&geoId=90000084&trk=public_jobs_j%20obs-search-bar_search-submit&position=1&pageNum=0&start={page}'

    response = requests.get(url, headers= headers)
    soup = BeautifulSoup(response.content,'html.parser')

    return  soup
# ==============================================================================


# ============================== Running the scrapers ==========================
full_soup : str = ''

for i in count(0):
    page = i + 1
    page_soup: BeautifulSoup = linkedin_scraper(country=   country,
                                                job_title= job_title,
                                                page=      i + page)
    full_soup += str(page_soup)
    full_soup += ' <br> '

    if (page_soup.find_all('li') is None) or (page == MAX_PAGES):
        break

full_soup  = BeautifulSoup(full_soup, 'html.parser')
job_blocks = full_soup.find_all('div', class_='job-info')

# Extract relevant information from each job block
for job_block in job_blocks:
    # Extract job title
    title = job_block.find('h2', class_='job-title').get_text(strip=True)
    job_titles.append(title)
    
    # Extract company name
    company = job_block.find('h3', class_='company-name').get_text(strip=True)
    company_names.append(company)
    
    # Extract job link
    link = job_block.find('a', href=True)['href']
    job_links.append(link)
    
    # Scrape job description from the job link
    job_page = requests.get(link)
    job_soup = BeautifulSoup(job_page.content, 'html.parser')
    description = job_soup.find('div', class_='description').get_text(strip=True)
    descriptions.append(description)

# Create a DataFrame from extracted data
jobs_df = pd.DataFrame({
    'Job_Title': job_titles,
    'Company_Name': company_names,
    'Description': descriptions,
    'Job_Link': job_links
})

# ==============================================================================
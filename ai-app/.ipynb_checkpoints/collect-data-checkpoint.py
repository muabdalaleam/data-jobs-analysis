import argparse
import json
import requests
import cloudscraper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np



def parse_arguments():
    
    parser = argparse.ArgumentParser(description='Collect job data and train a ChatBot to create a Streamlit app.')
    parser.add_argument('--country',    type=str,  required=True,   help='Specify a valid country name or a geographic region.')
    parser.add_argument('--job_title',  type=str,  required=True,   help='Specify a job title to search for as a string.')
    parser.add_argument('--max_pages',  type=int,  default= 1,      help='Specify the max jobs pages you want to scrape.')
    
    return parser.parse_args() 


def scrape_page_fast(url: str) -> BeautifulSoup:
    
    scraper = cloudscraper.create_scraper(delay=10, browser={'browser': 'chrome', 'platform': 'windows',
                                                             'desktop': True,     'mobile': False})
    content = scraper.get(url).text

    return BeautifulSoup(content, 'html.parser')


def linkedin_scraper(country: str, job_title: str, page: int) -> BeautifulSoup:
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept-Encoding': '*',
        'Connection': 'keep-alive'
    }

    page = (page - 1) * 25
    url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job_title}&' + \
          f'location={country}&geoId=90000084&trk=public_jobs_j%20obs-search-bar_search-submit&position=1&pageNum=0&start={page}'
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def extract_job_data(job_block: BeautifulSoup) -> tuple[str]:
    
    title   :str = job_block.find('h3', class_='base-search-card__title').get_text(strip=True)
    company :str = job_block.find('a', class_='hidden-nested-link').get_text(strip=True)
    link    :str = job_block.find('a', class_='base-card__full-link', href=True)['href']

    return title, company, link


def fetch_description(link: str) -> str:

    try:
        job_data = json.loads(scrape_page_fast(link).find('script', attrs={'type': 'application/ld+json'}).text)
        return job_data.get('description', '').strip()

    except:
        return np.nan


def scrape_jobs(inputs) -> None:

    full_soup = ''

    for i in range(inputs.max_pages):
        page_soup = linkedin_scraper(inputs.country, inputs.job_title, i + 1)
        full_soup += str(page_soup)
        full_soup += ' <br> '
        if page_soup.find_all('li') is None:
            break

    full_soup = BeautifulSoup(full_soup, 'html.parser')
    job_blocks = full_soup.find_all('div', class_='job-search-card')

    job_data = []

    for job_block in job_blocks:
        title, company, link = extract_job_data(job_block)
        description          = fetch_description(link)

        job_data.append({'job_title': title, 'company_name': company, 'job_link': link, 'desc': description})

    jobs_df = pd.DataFrame(job_data)
    jobs_df.to_csv('jobs_data.csv')


def main():
    inputs = parse_arguments()
    scrape_jobs(inputs)


if __name__ == "__main__":
    main()

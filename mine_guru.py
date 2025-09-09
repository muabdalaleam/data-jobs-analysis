from typing import NamedTuple, Dict, List
from bs4 import BeautifulSoup
import requests
import time
import csv
import re

DATA_JOBS_TITLES = [
    "Data Entry",
    "Data Engineering",
    "Data Science",
    "Data Analysis",
    "Machine Learning",
]
CSV_FIELDNAMES = [
    "url",
    "name",
    "location",
    "earnings",
    "feedback_percent",
    "skills",
    "transactions_completed",
    "employers_count",
    "member_since",
    "description",
    "searched_job_title"
]
MAX_PAGES   = 10 # by default it's 20 freelancers per page so 10 is more than enough
MAX_RETRIES = 5
TIMEOUT     = 60
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept-Encoding': '*',
    'Connection': 'keep-alive',
}

class Freelancer(NamedTuple):
    url: str
    name: str
    location: str
    earnings: str
    feedback_percent: str
    skills: list[str]
    transactions_completed: int
    employers_count:        int
    member_since: str
    description: str

def retrying_request(url: str) -> requests.Response:
    response = requests.get(url, params=HEADERS, timeout=TIMEOUT)
    retries = 0

    while response.status_code != 200:
        response = requests.get(url, params=HEADERS, timeout=TIMEOUT)
        print(f"Failed getting \"{url}\", Retrying ...")
        if retries >= MAX_RETRIES:
            raise requests.HTTPError("Exceeded max retries trying to request: ", url)
        retries += 1

    return response

def search_freelancer_urls(job_title : str, page: int) -> list[str]:
    response = retrying_request(
        url= f"https://www.guru.com/d/freelancers/skill/{job_title}/pg/{page}/"
    )

    soup = BeautifulSoup(response.content, 'html.parser')
    pattern = re.compile(r"^/freelancers")

    freelancers_headers = soup.find_all('a', href=pattern)
    freelancers_urls = set()

    for header in freelancers_headers:
        freelancers_urls.add(header['href'])

    return list(freelancers_urls)

def scrape_freelancer_data(url: str) -> Freelancer:
    response = requests.get(
        url=f"https://www.guru.com/{url}",
    )
    time.sleep(1) # just to not overload thier servers

    soup = BeautifulSoup(response.content, 'html.parser')

    try: name = (
        soup.find("h1", class_="profile-avatar__info__name")
            .find("strong").contents[0].strip())
    except: name = ""

    try: location = (
        soup.find("p", class_="profile-avatar__info__location")
            .find_all("span")[1].contents[0].strip())
    except: location = ""

    try: earnings = (
        soup.find_all("dd", class_="profile-attd__data")[0]
            .contents[0].strip())
    except: earnings = ""
    
    try: feedback_percent = (
        soup.find("p", class_="profile-avatar__info__earnings")
            .find("a", attrs={"id": "feedback-percent"})
            .find("strong").contents[0].strip())
    except: feedback_percent = ""

    try: skills = [skill.contents[0].strip() for skill in 
        soup.find_all("li", class_="skillsList__skill")
    ]
    except: skills = []
    
    try: transactions_completed = int(
        soup.find_all("dd", class_="profile-attd__data")[1]
            .contents[0].strip().replace(",", ""))
    except: transactions_completed = 0

    try: employers_count = int(
        soup.find_all("dd", class_="profile-attd__data")[2]
            .contents[0].strip().replace(",", ""))
    except: employers_count = 0

    try: member_since = (
        soup.find_all("dd", class_="profile-attd__data")[4]
            .contents[0].strip())
    except: member_since = ""

    try: description = (
        soup.find("div", class_="p-aboutUs").get_text(separator=' ', strip=True))
    except: description = ""

    # description: str

    return Freelancer(
        url= f"https://www.guru.com/{url}",
        name= name,
        location= location,
        earnings= earnings,
        feedback_percent= feedback_percent,
        skills= skills,
        transactions_completed=transactions_completed,
        employers_count= employers_count,
        member_since= member_since,
        description= description,
    )

def main():
    aggregated_freelancers: Dict[str, List[Freelancer]] = dict()

    for job_title in DATA_JOBS_TITLES:
        print(f"Scraping \"{job_title}\" freelancers.")
        aggregated_freelancers[job_title] = []

        current_page = 1
        while current_page <= MAX_PAGES:
            urls = search_freelancer_urls(job_title, current_page)
            aggregated_freelancers[job_title].extend([
                scrape_freelancer_data(url) for url in urls
            ])
            current_page += 1

        print(f"{job_title} URls: \n {urls} \n")

    print(f"Scraped {len(aggregated_freelancers[job_title]) * len(DATA_JOBS_TITLES)} freelancers.\n")

    with open("./data/guru_freelancers.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writerow(dict(zip(CSV_FIELDNAMES, CSV_FIELDNAMES))) # frist row is for column names
        
        for searched_job_title, freelancers in aggregated_freelancers.items():
            for freelancer in freelancers:
                writer.writerow({
                "url": freelancer.url,
                "name": freelancer.name,
                "location": freelancer.location,
                "earnings": freelancer.earnings,
                "feedback_percent": freelancer.feedback_percent,
                "skills": freelancer.skills,
                "transactions_completed": freelancer.transactions_completed,
                "employers_count": freelancer.employers_count,
                "member_since": freelancer.member_since,
                "description": freelancer.description,
                "searched_job_title": searched_job_title,
                })

if __name__ == "__main__":
    main()

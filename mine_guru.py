import requests
import re
from bs4 import BeautifulSoup
from typing import NamedTuple


DATA_JOBS_TITLES = ['Data entry', 'Data engineer',
                    'Data scientist', 'Data analyst',
                    'ML developer']

MAX_PAGES = 50

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


def search_freelancers(job_title : str, page: int) -> list[str]:
    response = requests.get(
        url= f"https://www.guru.com/d/freelancers/skill/{job_title}/pg/{page}/",
        params=HEADERS
    )

    if response.status_code != 200:
        raise requests.exceptions.HTTPError("Failed to search for guru freelancers.")

    soup = BeautifulSoup(response.content, 'html.parser')
    pattern = re.compile(r"^/freelancers")

    freelancers_headers = soup.find_all('a', href=pattern)
    freelancers_urls = set()

    for header in freelancers_headers:
        freelancers_urls.add(header['href'])

    return list(freelancers_urls)


def scrape_freelancer_data(url: str) -> Freelancer:
    response = requests.get(url= f"https://www.guru.com/{url}", params=HEADERS)

    if response.status_code != 200:
        raise requests.exceptions.HTTPError("Failed to scrape freelancer's data")

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
    # print(search_freelancers("Data Analysis", 1))

    freelancer_url = search_freelancers("Data Analysis", 1)[0]
    print("\n\nFreelancer's data: ", scrape_freelancer_data(freelancer_url))

if __name__ == "__main__":
    main()

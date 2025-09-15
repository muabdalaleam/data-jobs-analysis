# Fetches the linkedin api website and retrieves important job data then it
# stores the data in `./data/linkedin_jobs.csv`
import requests
import re
from typing import NamedTuple, Dict
import csv
from bs4 import BeautifulSoup, PageElement

DATA_JOBS_TITLES = [
    "Data entry",
    "Data engineer",
    "Data scientist",
    "Data analyst",
    "Machine learning",
]
CSV_FIELDNAMES   = [
    "id",
    "posting_title",
    "location",
    "posted_since",
    "company_name",
    "description",
    "job_url",
    "company_url",
    "applicants",
    "industries",
    "employment_type",
    "job_function",
    "seniority_level",
    "searched_country",
    "searched_job_title",
]
MAX_PAGES   = 10 # per job title and country each page containts 10 jobs
MAX_RETRIES = 6
TIMEOUT     = 60
COUNTRIES   = ['European Union', 'United States']
HEADERS     = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept-Encoding': '*',
    'Connection': 'keep-alive',
}

type JobId = str

class Job(NamedTuple):
    id:             str
    posting_title:  str
    location:           str
    posted_since:       str
    company_name:       str
    description:        str
    job_url:            str
    company_url:        str
    applicants:         str

    industries:         list[str]
    employment_type:    str
    job_function:       str
    seniority_level:    str


    def __str__(self):
        return f"""Job(
    job_id: \"{self.id}\"
    job_posting_title: \"{self.posting_title}\"
    location: \"{self.location}\"
    posted_since: \"{self.posted_since}\"
    company_name: \"{self.company_name}\"
    description: \"{self.description}\"
    job_url: \"{self.job_url}\"
    company_url: \"{self.company_url}\"
    applicants: \"{self.applicants}\"

    industries: \"{self.industries}\"
    employment_type: \"{self.employment_type}\"
    job_function: \"{self.job_function}\"
    seniority_level: \"{self.seniority_level}\"
    """

def search_jobs(country: str, job_title: str, page: int) -> list[JobId]:
    url= "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search" + \
         f"?keywords={job_title}&location={country}&position=1&page" + \
         f"Num=0&start={(page - 1) * 10}"

    failed_tries = 0
    try:
        response = requests.get(url=url, params=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        print("Retrining searching for jobs.")
        response = requests.get(url, params=HEADERS, timeout=TIMEOUT)
        failed_tries += 1
        if failed_tries > MAX_RETRIES:
            raise err

    if response.status_code != 200:
        return []
        # raise requests.exceptions.HTTPError("Recieved invalid response while searching for jobs.")

    soup = BeautifulSoup(response.content, 'html.parser')

    jobs_elements = soup.find_all("li")
    job_urls: list[str] = []
    for element in jobs_elements:
        if isinstance(element, PageElement):
            job_urls.append(
                element.find("a", attrs={"class": "base-card__full-link"})["href"])

    job_ids: list[JobId] = []
    pattern = re.compile(r"-[0-9]*\?")
    for url in job_urls:
        match = pattern.search(url)
        if match != None:
             # first and last char are not part of the id
            job_ids.append(match.group()[1:-1])

    return job_ids

def scrape_job_data(id: JobId) -> Job:
    url=f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}"

    failed_tries = 0
    try:
        response = requests.get(url=url, params=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError as err:
        print(f"Retrining scraping \"{id}\" job data.")
        response = requests.get(url, params=HEADERS, timeout=TIMEOUT)
        failed_tries += 1
        if failed_tries > MAX_RETRIES:
            raise err

    if response.status_code != 200:
        return []
        # raise requests.exceptions.HTTPError("Recieved invalid response while fetching job data possibly invalid id.")

    soup = BeautifulSoup(response.content, 'lxml')

    def scrape_content(tag: str, class_attr: str, def_val=None, get_href=False):
        content = soup.find(tag, attrs={"class": class_attr})

        if not(content): # not founded
            return def_val

        return content.get_text(separator="\n").strip()

    def scrape_criteria_item(title: str):
        job_criteria_subheader = soup.find(
            "h3",
            attrs={"class": "description__job-criteria-subheader"},
            string=lambda text: text and title.lower() in text.lower()
        )

        if not(job_criteria_subheader):
            return ""

        parent_item = job_criteria_subheader.parent
        contents = parent_item.find("span").contents

        total_content = ""
        for content in contents:
            if isinstance(content, str):
                total_content += content.strip()

        return total_content
    
    job = Job(
        id               = id,
        posting_title    = scrape_content("h2", "top-card-layout__title"),
        location         = scrape_content("span", "topcard__flavor--bullet"),
        posted_since     = scrape_content("span", "posted-time-ago__text"),
        company_name     = scrape_content("a", "topcard__org-name-link"),
        description      = scrape_content("div", "show-more-less-html__markup"),
        job_url          = soup.find("a", attrs={"class": "topcard__link"})["href"],
        company_url      = soup.find("a", attrs={"class": "topcard__org-name-link"})["href"],
        applicants       = scrape_content("figcaption", "num-applicants__caption"), # XXX:

        industries       = scrape_criteria_item("Industries"),
        employment_type  = scrape_criteria_item("Employment type"),
        job_function     = scrape_criteria_item("Job function"),
        seniority_level  = scrape_criteria_item("Seniority level"),
    )

    return job

def main():
    aggregated_jobs: Dict[str, Dict[str, list[Job]]] = dict()

    for country in COUNTRIES:
        aggregated_jobs[country] = dict()
        print(f"Scraping \"{country}\" jobs.")

        for job_title in DATA_JOBS_TITLES:
            aggregated_jobs[country][job_title] = []
            print(f"Scraping \"{job_title}\" positions.")

            current_page_index = 1
            while current_page_index <= MAX_PAGES:
                job_ids = search_jobs(country, job_title, current_page_index)
                jobs_data = list(map(scrape_job_data, job_ids))

                if len(jobs_data) == 0:
                    aggregated_jobs[country][job_title] = []
                    break

                aggregated_jobs[country][job_title].extend(jobs_data)
                current_page_index += 1

            print(f"Scraped {len(aggregated_jobs[country][job_title])} jobs.\n")

    with open("./data/linkedin_jobs.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writerow(dict(zip(CSV_FIELDNAMES, CSV_FIELDNAMES))) # frist row is for column names

        for searched_country, jobs_dict in aggregated_jobs.items():
            for searched_job_title, jobs in jobs_dict.items():
                for job in jobs:
                    if not(isinstance(job, Job)):
                        continue

                    writer.writerow({
                    "id":              job.id,
                    "posting_title":   job.posting_title,
                    "location":        job.location,
                    "posted_since":    job.posted_since,
                    "company_name":    job.company_name,
                    "description":     job.description,
                    "job_url":         job.job_url,
                    "company_url":     job.company_url,
                    "applicants":      job.applicants,

                    "industries":      job.industries,
                    "employment_type": job.employment_type,
                    "job_function":    job.job_function,
                    "seniority_level": job.seniority_level,
                    "searched_country":   searched_country,
                    "searched_job_title": searched_job_title,
                    })

if __name__ == "__main__":
    main()

# https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Data Analyst&location=United States&geoId=90000084&trk=public_jobs_j%20obs-search-bar_search-submit&position=1&pageNum=0&start=1

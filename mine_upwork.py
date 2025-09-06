from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
from typing import List, NamedTuple, Dict
import csv
import re

DATA_JOBS_TITLES = [
    # 'Data entry',
    # 'Data engineer',
    'Data scientist',
    # 'Data analyst',
    # 'Machine learning', XXX:
]
CSV_FIELDNAMES = [
    "id",
    "name",
    "location",
    "job_title",
    "description",
    "earnings",
    "feedback_percent",
    "skills",
    "hour_rate",
    "hours_worked",
    "hourly_jobs_done",
    "fixed_jobs_done",
]
CHROMIUM_VERSION = 141  # Adjust as needed
UPWORK_TIMEOUT = 90
MAX_PAGES = 5

class Freelancer(NamedTuple):
    id: str
    name: str
    location: str
    job_title: str
    description: str
    earnings: str
    feedback_percent: str
    skills: List[str]
    hour_rate: str
    hours_worked: str
    hourly_jobs_done: str
    fixed_jobs_done: str

    def __str__(self) -> str:
        skills_formatted = ', '.join(self.skills)
        return (f"Freelancer ID: {self.id}\n"
                f"Name: {self.name}\n"
                f"Location: {self.location}\n"
                f"Job Title: {self.job_title}\n"
                f"Description: {self.description}\n"
                f"Earnings: {self.earnings}\n"
                f"Feedback Percentage: {self.feedback_percent}\n"
                f"Skills: {skills_formatted}\n"
                f"Hourly Rate: {self.hour_rate}\n"
                f"Hours Worked: {self.hours_worked}\n"
                f"Hourly Jobs Done: {self.hourly_jobs_done}\n"
                f"Fixed Jobs Done: {self.fixed_jobs_done}")

def parse_freelancer_card(card: WebElement) -> Freelancer:
    def find_text(selector: str, attribute: str = "text", method="css") -> str:
        try:
            if method == "xpath":
                element = card.find_element(By.XPATH, selector)
            if method == "css":
                element = card.find_element(By.CSS_SELECTOR, selector)
            else:
                return ""
            if attribute == "text":
                return element.get_attribute('textContent').strip()
            else:
                return element.get_attribute(attribute) or ""

        except NoSuchElementException:
            return ""
    
    def safe_find_multiple_text(selector: str) -> List[str]:
        """Safely find multiple elements and return their text values."""
        try:
            elements = card.find_elements(By.CSS_SELECTOR, selector)
            return [el.text.strip() for el in elements if el.text.strip()]
        except NoSuchElementException:
            return []

    url = find_text("[class*=\"profile-link\"]", attribute="href")
    id = ""
    id_pattern = re.compile(r"\~[a-z0-9]*")
    if id_pattern.search(url):
        id = id_pattern.group()[1:]
    
    name = find_text("[class*=\"profile-link\"]")
    
    location = find_text("[class*=\"location\"]")

    job_title = find_text("h4 a[class*=\"profile-link\"]")

    description = find_text("div[class*=\"description text-body\"] > div")
    
    earnings = find_text("[data-test=\"freelancer-tile-earnings\"] strong")

    hour_rate = find_text("span[data-test=\"rate-per-hour\"]")
    
    feedback_percent = find_text( "[data-test=\"freelancer-tile-job-success\"] span > span:first-child")

    hourly_jobs_text = find_text("span[data-test*=\"popper\"] p.mb-0:nth-of-type(1)")

    fixed_jobs_text = find_text("span[data-test*=\"popper\"] p.mb-0:nth-of-type(2)")

    hours_worked_text = find_text("span[data-test*=\"popper\"] p.mb-0:nth-of-type(3)")

    skills_items = card.find_elements(By.CSS_SELECTOR, 
        "div[data-test=\"FreelancerTileSkills\"] div[role=\"listitem\"] button")
    skills = [item.text.strip() for item in skills_items]

    return Freelancer(
        id=id,  # ID would need to be extracted from href or data attributes
        name=name,
        location=location,
        job_title=job_title,
        description=description,
        earnings=earnings,
        feedback_percent=feedback_percent,
        skills=skills,
        hour_rate=hour_rate,
        hours_worked=hours_worked_text,
        hourly_jobs_done=hourly_jobs_text,
        fixed_jobs_done=fixed_jobs_text,
    )

def scrape_freelancer_cards(driver: WebDriver) -> List[WebElement]:
    wait = WebDriverWait(driver, timeout=UPWORK_TIMEOUT, poll_frequency=0.2)
    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 
            ".freelancer-tile, [data-qa='tile'], .up-card-section")))

    return cards

def move_to_next_page(driver: WebDriver):
    wait = WebDriverWait(driver, timeout=UPWORK_TIMEOUT, poll_frequency=0.2)
    next_page_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 
            "button[data-test=\"next-page\"]")))

    next_page_button.click()

def main():
    driver = uc.Chrome(use_subprocess=False, version_main=CHROMIUM_VERSION)
    
    # Scraping the data
    aggregated_freelancers: Dict[str, Freelancer] = dict()
    for job_title in DATA_JOBS_TITLES:
        current_page = 1
        aggregated_freelancers[job_title] = []

        driver.get(
            f"https://www.upwork.com/nx/search/talent/?page={current_page}&q={job_title}"
        )

        while current_page < MAX_PAGES:
            cards = scrape_freelancer_cards(driver)
            aggregated_freelancers[job_title].extend([
                 parse_freelancer_card(card) for card in cards
            ])

            move_to_next_page(driver)
            current_page += 1

    driver.quit()

    # Saving the data
    with open("./data/upwork_freelancers.csv") as f:
        writer = csv.DictWriter(f, CSV_FIELDNAMES)

        for searched_job_title, freelancers in aggregated_freelancers.items():
            for freelancer in freelancers:
                writer.writerow({
                "id":                freelancer.id,
                "name":              freelancer.name,
                "location":          freelancer.location,
                "job_title":         freelancer.job_title,
                "description":       freelancer.description,
                "earnings":          freelancer.earnings,
                "feedback_percent":  freelancer.feedback_percent,
                "skills":            freelancer.skills,
                "hour_rate":         freelancer.hour_rate,
                "hours_worked":      freelancer.hours_worked,
                "hourly_jobs_done":  freelancer.hourly_jobs_done,
                "fixed_jobs_done":   freelancer.fixed_jobs_done,
                })

if __name__ == "__main__":
    main()

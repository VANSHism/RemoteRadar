"""Web scraper for RemoteOK job listings."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime, timedelta

from entity.config import (
    BASE_URL,
    CATEGORIES,
    TOTAL_JOB_LIMIT,
    PAGE_LOAD_DELAY,
    SCROLL_DELAY,
    CATEGORY_DELAY_RANGE,
    MAX_SCROLLS_PER_CATEGORY,
)

from components.sqlite import init_db, job_exists, add_job


def create_driver():
    """Create and configure Chrome WebDriver."""
    import os

    options = Options()
    # Headless + sandbox opts for CI (GitHub Actions has Chrome pre-installed)
    if os.getenv("GITHUB_ACTIONS") or os.getenv("CHROME_BIN"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if os.getenv("CHROME_BIN"):
            options.binary_location = os.getenv("CHROME_BIN")
    else:
        options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def scrape_remoteok():
    """Scrape job listings from RemoteOK across configured categories."""
    init_db()
    driver = create_driver()
    all_jobs = []

    for category in CATEGORIES:
        if len(all_jobs) >= TOTAL_JOB_LIMIT:
            break

        url = BASE_URL.format(category)
        print(f"\nOpening category: {category.upper()}")
        driver.get(url)
        time.sleep(PAGE_LOAD_DELAY)

        # Scroll to load jobs
        for scroll in range(MAX_SCROLLS_PER_CATEGORY):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(SCROLL_DELAY)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_rows = soup.find_all("tr", class_="job")

            print(
                f"  Scroll {scroll + 1}: "
                f"{len(job_rows)} jobs loaded | "
                f"{len(all_jobs)} collected"
            )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_rows = soup.find_all("tr", class_="job")

        for job in job_rows:
            if len(all_jobs) >= TOTAL_JOB_LIMIT:
                break

            # Job URL (extract early for duplicate check)
            link_tag = job.find("a", class_="preventLink")
            job_url = (
                "https://remoteok.com" + link_tag["href"]
                if link_tag and link_tag.get("href", "").startswith("/")
                else "N/A"
            )

            if job_exists(job_url):
                continue  # Skip already-persisted jobs

            # ----------------- DATA EXTRACTION -----------------

            # Job title
            title = job.get("data-position")
            if not title:
                t = job.find("h2")
                title = t.get_text(strip=True) if t else None

            # Company name
            company = job.get("data-company")
            if not company:
                c = job.find("h3")
                company = c.get_text(strip=True) if c else None

            # Location (cleaned and de‑noised)
            location = job.get("data-location")
            if not location:
                loc_div = job.find("div", class_="location")
                if loc_div:
                    loc_text = loc_div.get_text(separator=" ", strip=True)
                else:
                    loc_text = ""

                # Remove promotional / non-location text such as
                # "ðŸ'° Upgrade to Premium to see salary"
                promo_patterns = [
                    "upgrade to premium to see salary",
                    "upgrade to premium",
                    "see salary",
                ]

                text_lower = loc_text.lower()
                if any(p in text_lower for p in promo_patterns):
                    # If there is a real location before separators like bullets (•, ·) or '|'
                    parts = re.split(r"[\u2022\u00b7\-|]", loc_text)
                    candidate = parts[0].strip() if parts else ""
                    location = candidate or "Remote"
                else:
                    location = loc_text or "Remote"
            else:
                location = location.strip()

            # Strip emojis / odd control chars and normalise whitespace
            location = re.sub(r"[^\x20-\x7E]+", " ", location)
            location = re.sub(r"\s+", " ", location).strip() or "Remote"

            # Tags / skills: use both data-tags attribute and visible tag elements
            tags = []

            raw_tags = job.get("data-tags")
            if raw_tags:
                tags.extend([t.strip() for t in raw_tags.split(",") if t.strip()])

            # Also collect visible tags rendered as pills/badges
            tag_elements = job.select(".tag, .tags span")
            existing_lower = {t.lower() for t in tags}
            for el in tag_elements:
                txt = el.get_text(strip=True)
                if txt and txt.lower() not in existing_lower:
                    tags.append(txt)
                    existing_lower.add(txt.lower())

            skills = ", ".join(tags) if tags else "N/A"

            # Job type: infer from tags and row text
            job_type = "N/A"
            type_keywords = {
                "full-time": "Full-time",
                "full time": "Full-time",
                "contract": "Contract",
                "part-time": "Part-time",
                "part time": "Part-time",
                "freelance": "Freelance",
                "internship": "Internship",
                "intern": "Internship",
                "temporary": "Temporary",
            }

            joined_tags_text = " ".join(tags).lower()
            for key, label in type_keywords.items():
                if key in joined_tags_text:
                    job_type = label
                    break

            if job_type == "N/A":
                row_text = job.get_text(separator=" ", strip=True).lower()
                for key, label in type_keywords.items():
                    if key in row_text:
                        job_type = label
                        break

            # Date posted
            time_tag = job.find("time")
            if time_tag:
                raw_time = time_tag.get_text(strip=True)

                match = re.search(r"(\d+)\s*d", raw_time)
                if match:
                    days_ago = int(match.group(1))
                    date_posted = (datetime.today() - timedelta(days=days_ago)).strftime("%d/%m/%y")
                else:
                    date_posted = "N/A"
            else:
                date_posted = "N/A"


            if not title or not company:
                continue

            job_record = {
                "Job Title": title,
                "Company Name": company,
                "Job Tags / Skills": skills,
                "Location": location,
                "Job Type": job_type,
                "Date Posted": date_posted,
                "Job URL": job_url,
            }
            if add_job(job_record):
                all_jobs.append(job_record)

        delay = random.uniform(*CATEGORY_DELAY_RANGE)
        print(f"Sleeping {delay:.2f}s before next category...")
        time.sleep(delay)

    driver.quit()
    return all_jobs

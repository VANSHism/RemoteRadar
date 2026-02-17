"""Discord webhook notifications for new job postings."""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_alert(new_jobs):
    """
    Send a summary of new jobs to Discord via webhook.

    Args:
        new_jobs: List of job dicts with keys Job Title, Company Name, Job URL
    """
    if not DISCORD_WEBHOOK_URL:
        print("No Discord Webhook URL found. Skipping notification.")
        return

    if not new_jobs:
        return

    # Support both scraper format (Job Title, Company Name, Job URL) and legacy (title, company, link)
    def _get(job, *keys):
        for k in keys:
            if k in job and job[k]:
                return job[k]
        return "N/A"

    description = ""
    for job in new_jobs[:10]:
        title = _get(job, "Job Title", "title")
        company = _get(job, "Company Name", "company")
        link = _get(job, "Job URL", "link")
        description += f"**{title}** at {company}\n[Apply Here]({link})\n\n"

    if len(new_jobs) > 10:
        description += f"...and {len(new_jobs) - 10} more!"

    payload = {
        "username": "Job Bot",
        "embeds": [{
            "title": f"Found {len(new_jobs)} New Jobs!",
            "description": description,
            "color": 5814783,
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Discord notification sent!")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")
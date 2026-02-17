"""Main entry point for RemoteOK job scraper and analysis."""

from components.scraper import scrape_remoteok
from components.data_handler import load_from_db
from components.analysis import run_analysis
from components.notification import send_discord_alert


def main():
    """Run the full scraping and analysis pipeline."""
    print("Starting Ethical RemoteOK Scraping Project...")

    # Step 1: Scrape new jobs (persisted to SQLite, no overwrites)
    jobs = scrape_remoteok()
    if jobs:
        print(f"\nAdded {len(jobs)} new jobs to database")
        send_discord_alert(jobs)
    else:
        print("\nNo new jobs to add (all already in database)")

    # Step 2: Load all jobs from database for analysis
    df = load_from_db()
    if df is None or len(df) == 0:
        print("No data in database. Exiting.")
        return

    # Step 3: Run analysis (no visualization)
    run_analysis(df)


if __name__ == "__main__":
    main()

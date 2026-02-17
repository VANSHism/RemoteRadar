# RemoteOK Job Scraper & Analysis

A Python project that scrapes remote job listings from [RemoteOK.com](https://remoteok.com), stores them in SQLite for persistence, runs analysis, and sends Discord notifications for new postings.

## Features

- **Web scraping** – Collects job listings across multiple categories (engineer, management, design, financial, marketing, support)
- **SQLite persistence** – Stores jobs in a local database; new runs add only new jobs (no overwrites)
- **Data analysis** – Skill frequency, job type distribution, top companies and titles
- **Discord notifications** – Sends an embed with new jobs when the scraper finds them
- **GitHub Actions** – Scheduled daily runs with automatic commit of updated database

## Project Structure

```
├── main.py                 # Entry point
├── requirements.txt
├── components/
│   ├── scraper.py          # Selenium-based web scraper
│   ├── data_handler.py     # Load/save data (DB + CSV)
│   ├── sqlite.py           # SQLite persistence
│   ├── analysis.py         # Job data analysis
│   └── notification.py     # Discord webhook notifications
├── entity/
│   └── config.py           # Configuration (URLs, categories, limits)
├── notebook/
│   └── TEAM_A.ipynb        # Jupyter notebook (exploratory)
└── .github/workflows/
    └── daily_scrape.yaml   # Daily scheduled scraping
```

## Prerequisites

- Python 3.9+
- Google Chrome or Chromium
- ChromeDriver (or let Selenium manage it)

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd TeamA
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file for optional Discord notifications:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

## Usage

Run the full pipeline (scrape → persist → notify → analyze):

```bash
python main.py
```

- **Scraping** – Visits RemoteOK categories, scrolls to load dynamic content, extracts job details
- **Persistence** – New jobs are stored in `jobs.db`; duplicates are skipped
- **Notifications** – If `DISCORD_WEBHOOK_URL` is set, new jobs are posted to Discord
- **Analysis** – Prints skill summary, job type distribution, and top companies/titles

## Configuration

Edit `entity/config.py` to adjust:

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | RemoteOK URL pattern | `https://remoteok.com/remote-{}-jobs` |
| `CATEGORIES` | Job categories to scrape | engineer, management, design, financial, marketing, support |
| `TOTAL_JOB_LIMIT` | Max jobs per run | 500 |
| `PAGE_LOAD_DELAY` | Seconds to wait after loading a page | 5 |
| `SCROLL_DELAY` | Seconds between scrolls | 3 |
| `MAX_SCROLLS_PER_CATEGORY` | Scrolls per category to load more jobs | 2 |

## GitHub Actions

The workflow runs daily at 08:00 UTC and on manual trigger.

**Setup:**
1. Add `DISCORD_WEBHOOK_URL` as a repository secret (Settings → Secrets and variables → Actions)
2. Ensure `jobs.db` exists and is committed for the first run (or run locally once to create it)

The workflow will:
1. Run the scraper
2. Commit and push updated `jobs.db` if there are changes

## License

MIT

"""SQLite persistence for RemoteOK job listings."""

import sqlite3
import pandas as pd

DB_PATH = "jobs.db"


def _get_connection():
    """Get a database connection (caller is responsible for closing)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _get_table_columns(conn):
    """Return list of column names for the jobs table, or empty if table doesn't exist."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
    )
    if cursor.fetchone() is None:
        return []
    cursor = conn.execute("PRAGMA table_info(jobs)")
    return [row[1] for row in cursor.fetchall()]


def init_db():
    """Create the jobs table if it does not exist. Migrates old schema if needed."""
    conn = _get_connection()
    try:
        columns = _get_table_columns(conn)
        if not columns:
            conn.execute("""
                CREATE TABLE jobs (
                    link TEXT PRIMARY KEY,
                    job_title TEXT,
                    company_name TEXT,
                    job_tags_skills TEXT,
                    location TEXT,
                    job_type TEXT,
                    date_posted TEXT
                )
            """)
            conn.commit()
            return

        # Migrate old schema (id, title, company, location, date_posted, link)
        if "job_title" not in columns and "title" in columns:
            conn.execute("ALTER TABLE jobs RENAME TO jobs_old")
            conn.execute("""
                CREATE TABLE jobs (
                    link TEXT PRIMARY KEY,
                    job_title TEXT,
                    company_name TEXT,
                    job_tags_skills TEXT,
                    location TEXT,
                    job_type TEXT,
                    date_posted TEXT
                )
            """)
            conn.execute("""
                INSERT OR IGNORE INTO jobs (link, job_title, company_name, job_tags_skills, location, job_type, date_posted)
                SELECT link, title, company, '', location, '', date_posted FROM jobs_old
            """)
            conn.execute("DROP TABLE jobs_old")
            conn.commit()
    finally:
        conn.close()


def job_exists(job_url):
    """Check if a job with the given URL already exists in the DB."""
    if not job_url or job_url == "N/A":
        return True  # Treat invalid URLs as "exists" to skip them
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT 1 FROM jobs WHERE link = ?", (job_url,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def add_job(job_data):
    """
    Insert a new job into the database.

    Args:
        job_data: Dict with keys Job Title, Company Name, Job Tags / Skills,
                  Location, Job Type, Date Posted, Job URL

    Returns:
        True if added, False if duplicate (IntegrityError)
    """
    job_url = job_data.get("Job URL", "")
    if not job_url or job_url == "N/A":
        return False

    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO jobs (link, job_title, company_name, job_tags_skills, location, job_type, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_url,
            job_data.get("Job Title", ""),
            job_data.get("Company Name", ""),
            job_data.get("Job Tags / Skills", ""),
            job_data.get("Location", ""),
            job_data.get("Job Type", ""),
            job_data.get("Date Posted", ""),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def load_all_jobs():
    """Load all jobs from the database as a DataFrame for analysis."""
    init_db()
    conn = _get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT link AS \"Job URL\", job_title AS \"Job Title\", company_name AS \"Company Name\", "
            "job_tags_skills AS \"Job Tags / Skills\", location AS \"Location\", "
            "job_type AS \"Job Type\", date_posted AS \"Date Posted\" FROM jobs",
            conn
        )
        return df
    finally:
        conn.close()        
"""Data loading and saving utilities for RemoteOK job listings."""

import pandas as pd

from components.sqlite import load_all_jobs


def load_from_db():
    """Load all jobs from SQLite database (primary persistence)."""
    df = load_all_jobs()
    if len(df) > 0:
        print(f"\nLoaded {len(df)} jobs from database (total stored)")
    return df


def save_data(jobs, filepath="remoteok_jobs.csv", append=False):
    """
    Export jobs to CSV (optional, for backup). Jobs are persisted in SQLite by default.

    Args:
        jobs: List of job dictionaries
        filepath: Output CSV file path
        append: If True, append to existing CSV; if False, overwrite

    Returns:
        DataFrame or None if no jobs
    """
    if not jobs:
        return None

    df = pd.DataFrame(jobs)
    mode = "a" if append else "w"
    header = not append
    df.to_csv(filepath, index=False, mode=mode, header=header)
    return df


def load_data(filepath="remoteok_jobs.csv"):
    """
    Load job data from CSV.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with job data
    """
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} jobs from {filepath}")
    return df

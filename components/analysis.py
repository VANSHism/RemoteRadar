"""Data analysis utilities for RemoteOK job listings (no visualization)."""

from collections import Counter
import pandas as pd


def extract_skill_counts(df):
    """
    Extract and count skills from the Job Tags / Skills column.

    Args:
        df: DataFrame with "Job Tags / Skills" column

    Returns:
        Counter object mapping skill names to frequencies
    """
    all_skills = []
    for skills_str in df["Job Tags / Skills"]:
        if pd.notna(skills_str) and skills_str != "N/A":
            skills_list = [s.strip() for s in str(skills_str).split(",")]
            all_skills.extend(skills_list)
    return Counter(all_skills)


def print_skill_summary(skill_counts):
    """Print skill count summary to console."""
    print(f"Total unique skills found: {len(skill_counts)}")
    print(f"\nTop 15 skills:")
    for skill, count in skill_counts.most_common(15):
        print(f"  {skill}: {count}")


def print_summary_statistics(df, skill_counts):
    """Print comprehensive summary statistics for job data."""
    print("=" * 60)
    print("REMOTE JOBS DATA SUMMARY")
    print("=" * 60)
    print(f"\nTotal Jobs Scraped: {len(df)}")
    print(f"Unique Companies: {df['Company Name'].nunique()}")
    print(f"Unique Job Titles: {df['Job Title'].nunique()}")
    print(f"Unique Skills: {len(skill_counts)}")
    print(f"Total Skill Mentions: {sum(skill_counts.values())}")

    print(f"\nJob Type Distribution:")
    for job_type, count in df["Job Type"].value_counts().items():
        percentage = (count / len(df)) * 100
        print(f"  {job_type}: {count} ({percentage:.1f}%)")

    print(f"\nTop 5 Most In-Demand Skills:")
    for skill, count in skill_counts.most_common(5):
        percentage = (count / len(df)) * 100
        print(f"  {skill}: {count} jobs ({percentage:.1f}%)")

    print(f"\nTop 5 Most Common Job Titles:")
    for title, count in df["Job Title"].value_counts().head(5).items():
        print(f"  {title}: {count} postings")

    print("\n" + "=" * 60)


def run_analysis(df):
    """
    Run full analysis pipeline on job data (skill extraction + summary stats).

    Args:
        df: DataFrame with job data

    Returns:
        Counter object with skill counts
    """
    skill_counts = extract_skill_counts(df)
    print_skill_summary(skill_counts)
    print()
    print_summary_statistics(df, skill_counts)
    return skill_counts

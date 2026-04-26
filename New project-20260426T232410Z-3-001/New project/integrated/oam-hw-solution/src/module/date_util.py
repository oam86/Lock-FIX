# Helper function to parse dates with default to today
from datetime import datetime


def parse_date_with_default(date_str):
    today = datetime.now()
    if not date_str:
        return today
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

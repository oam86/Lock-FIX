# Helper function to get recent detect with a limit
from datetime import datetime, timedelta


def get_recent_logs(model, days=7, limit=10):
    cutoff_date = datetime.now() - timedelta(days=days)
    return (
        model.query.filter(model.date >= cutoff_date)
        .order_by(model.date.desc())
        .limit(limit)
        .all()
    )
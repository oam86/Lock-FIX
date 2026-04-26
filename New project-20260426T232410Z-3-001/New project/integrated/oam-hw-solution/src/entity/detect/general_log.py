from datetime import datetime, timedelta

from src.database.database_manager import db


class GeneralLog(db.Model):
    __tablename__ = 'general_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    log_content = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),  # 날짜 형식을 지정
            "log_content": self.log_content
        }


def create_general_log(log_content):
    log = GeneralLog(log_content=log_content,
        date=datetime.now())
    db.session.add(log)
    db.session.commit()

def get_general_logs():
    return GeneralLog.query.all()

# 최근 N일 동안의 로그를 가져오고, 최대 갯수를 제한
def get_recent_general_logs(days=7, limit=10):
    cutoff_date = datetime.now() - timedelta(days=days)
    return (
        GeneralLog.query.filter(GeneralLog.date >= cutoff_date)
        .order_by(GeneralLog.date.desc())
        .limit(limit)
        .all()
    )
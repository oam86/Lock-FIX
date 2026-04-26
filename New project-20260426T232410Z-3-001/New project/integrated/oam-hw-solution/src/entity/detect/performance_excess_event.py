from datetime import datetime

from src.database.database_manager import db


class PerformanceExcessEvent(db.Model):
    __tablename__ = 'performance_excess_event'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    hardware_type = db.Column(db.Enum('CPU', 'MEMORY', 'DISK', 'HBA', 'NIC-RX', 'NIC-TX', 'SAS_CARD', name='hardware_type'))
    threshold = db.Column(db.Float)
    actual_value = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),  # 날짜 형식을 지정
            "hardware_type": self.hardware_type,
            "threshold": self.threshold,
            "actual_value": self.actual_value
        }

def create_performance_excess_event(hardware_type, threshold, actual_value):
    event = PerformanceExcessEvent(hardware_type=hardware_type, threshold=threshold, actual_value=actual_value,
        date=datetime.now())
    db.session.add(event)
    db.session.commit()

def get_performance_excess_events():
    return PerformanceExcessEvent.query.all()
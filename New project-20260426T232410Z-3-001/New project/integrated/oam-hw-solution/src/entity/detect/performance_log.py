from datetime import datetime, timedelta

from src.database.database_manager import db

class PerformanceLog(db.Model):
    __tablename__ = 'performance_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    cpu_usage = db.Column(db.Float)
    mem_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    network_inbound_usage = db.Column(db.Float)
    network_outbound_usage = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),  # 날짜 형식을 지정
            "cpu_usage": self.cpu_usage,
            "mem_usage": self.mem_usage,
            "disk_usage": self.disk_usage,
            "network_rx_usage": self.network_inbound_usage,
            "network_tx_usage": self.network_outbound_usage,
        }

def create_performance_log(cpu_usage, mem_usage, disk_usage, nic_rx_usage, nic_tx_usage):
    log = PerformanceLog(cpu_usage=cpu_usage, mem_usage=mem_usage, disk_usage=disk_usage,
                         network_inbound_usage=nic_rx_usage, network_outbound_usage=nic_tx_usage
                         ,date=datetime.now())
    db.session.add(log)
    db.session.commit()

# 최근 N일 동안의 로그를 가져오고, 최대 갯수를 제한
def get_recent_performance_logs(days=7, limit=10):
    cutoff_date = datetime.now() - timedelta(days=days)
    return (
        PerformanceLog.query.filter(PerformanceLog.date >= cutoff_date)
        .order_by(PerformanceLog.date.desc())
        .limit(limit)
        .all()
    )

def get_performance_logs():
    return PerformanceLog.query.all()



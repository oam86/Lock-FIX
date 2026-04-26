from datetime import datetime

from src.database.database_manager import db


class NetworkCardPerformanceLog(db.Model):
    __tablename__ = 'network_card_performance_log'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    nic_name = db.Column(db.String, nullable=False)
    rx_actual_value = db.Column(db.Float)
    tx_actual_value = db.Column(db.Float)
    bandwidth_kb = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "nic_name": self.nic_name,
            "rx_actual_value": self.rx_actual_value,
            "tx_actual_value": self.tx_actual_value,
            "bandwidth_kb": self.bandwidth_kb
        }


def create_network_card_performance_log(nic_name, rx_actual_value, tx_actual_value, bandwidth_kb):
    log = NetworkCardPerformanceLog(nic_name=nic_name, rx_actual_value=rx_actual_value, tx_actual_value=tx_actual_value, bandwidth_kb=bandwidth_kb, date=datetime.now())
    db.session.add(log)
    db.session.commit()


def get_network_card_performance_logs():
    return NetworkCardPerformanceLog.query.all()

def get_network_card_performance_log_by_nic(nic_name):
    """ 특정 NIC의 최근 5분 평균 성능 데이터 반환 """
    return NetworkCardPerformanceLog.query.filter_by(nic_name=nic_name).order_by(NetworkCardPerformanceLog.date.desc()).limit(5).all()
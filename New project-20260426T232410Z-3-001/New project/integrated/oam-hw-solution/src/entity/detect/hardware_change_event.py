from datetime import datetime

from src.database.database_manager import db
from src.module.logging_util import gaya_log


class HardwareChangeEvent(db.Model):
    __tablename__ = 'hardware_change_event'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)  # 최초 감지 시간
    last_updated = db.Column(db.DateTime, default=datetime.now)  # 최근 갱신 시간
    changed_model = db.Column(db.String(255))
    changed_serial_number = db.Column(db.String(255), nullable=True)
    hardware_type = db.Column(db.Enum('CPU', 'MEMORY', 'DISK', 'HBA', 'NIC', 'SAS_CARD', 'NIC-RX', 'NIC-TX', name='hardware_type'))
    change_type = db.Column(db.Enum('ADD', 'DELETE', name='change_type'))

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),  # 최초 감지 시간
            "last_updated": self.last_updated.strftime("%Y-%m-%d %H:%M:%S"),  # 최근 갱신 시간
            "changed_model": self.changed_model,
            "changed_serial_number": self.changed_serial_number,
            "hardware_type": self.hardware_type,
            "change_type": self.change_type
        }


def create_hardware_change_event(changed_model, changed_serial_number, hardware_type, change_type):
    """
    하드웨어 변경 이벤트를 생성하거나 동일한 데이터가 있으면 시간을 업데이트.
    """
    current_time = datetime.now()  # 현재 시간 저장

    # 기존 데이터 확인
    existing_event = HardwareChangeEvent.query.filter_by(
        changed_model=changed_model,
        changed_serial_number=changed_serial_number,
        hardware_type=hardware_type,
        change_type=change_type
    ).first()

    if existing_event:
        # 동일한 데이터가 있으면 마지막 갱신 시간만 업데이트
        existing_event.last_updated = current_time
        db.session.commit()
        gaya_log(f"Updated timestamp for existing event: Model({changed_model}) SN({changed_serial_number}) HW({hardware_type}) CH({change_type}) at {current_time}")
        return None
    else:
        # 동일한 데이터가 없으면 새 데이터 삽입
        event = HardwareChangeEvent(
            changed_model=changed_model,
            changed_serial_number=changed_serial_number,
            hardware_type=hardware_type,
            change_type=change_type,
            date=current_time,  # 최초 감지 시간
            last_updated=current_time  # 최근 갱신 시간
        )
        db.session.add(event)
        db.session.commit()
        gaya_log(f"Inserted new event: Model({changed_model}) SN({changed_serial_number}) HW({hardware_type}) CH({change_type}) at {current_time}")
        return event


def get_hardware_change_events():
    return HardwareChangeEvent.query.all()
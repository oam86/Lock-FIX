from datetime import datetime

from src.database.database_manager import db


class InitHardwareInfo(db.Model):
    __tablename__ = 'init_hardware_info'
    id = db.Column(db.Integer, primary_key=True)
    hardware_type = db.Column(db.Enum('CPU', 'MEMORY', 'DISK', 'HBA', 'NIC', 'SAS_CARD', name='hardware_type'))
    model_name = db.Column(db.String(255))
    serial_number = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "hardware_type": self.hardware_type if isinstance(self.hardware_type,  str) else self.hardware_type.value if self.hardware_type else None,
            "model_name": self.model_name,
            "serial_number": self.serial_number,
        }

# Create helper functions
def create_init_hardware_info(hardware_type, model_name, serial_number):
    info = InitHardwareInfo(hardware_type=hardware_type, model_name=model_name, serial_number=serial_number)
    db.session.add(info)
    db.session.commit()

def get_init_hardware_info():
    return InitHardwareInfo.query.all()
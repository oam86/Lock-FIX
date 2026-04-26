from datetime import datetime

from src.database.database_manager import db


class LicenseInfo(db.Model):
    __tablename__ = 'license_info'
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(255), unique=True, nullable=False)
    customer_name = db.Column(db.String(255))
    expiry_date = db.Column(db.DateTime)
    renewal_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "license_key": self.license_key,
            "customer_name": self.customer_name,
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d %H:%M:%S") if self.expiry_date else None,
            "renewal_date": self.renewal_date.strftime("%Y-%m-%d %H:%M:%S") if self.renewal_date else None,
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M:%S") if self.start_date else None,
        }


def create_license_info(license_key, customer_name, expiry_date, renewal_date, start_date):
    info = LicenseInfo(
        license_key=license_key,
        customer_name=customer_name,
        expiry_date=expiry_date,
        renewal_date=renewal_date,
        start_date=start_date,
    )
    db.session.add(info)
    db.session.commit()

def get_license_info():
    return LicenseInfo.query.all()
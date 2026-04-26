from flask_sqlalchemy import SQLAlchemy

from src.database import db
from src.module.logging_util import gaya_log


def load_database(app):
    gaya_log('테이블 생성 시작')
    db.init_app(app)
    with app.app_context():
        db.create_all()
        gaya_log('테이블 생성완료')



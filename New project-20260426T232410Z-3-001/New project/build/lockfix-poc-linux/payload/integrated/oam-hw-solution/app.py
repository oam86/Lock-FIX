import os
import sys

from flask import Flask
from flask_cors import CORS

from src.api.detect.detect_api import detect_bp
from src.api.general.general_api import general_bp
from src.api.license.license_api import license_bp
from src.api.log.log_to_excel_api import export_bp
from src.api.monitoring.monitoring_api import monitoring_bp
from src.api.network.newtork_monitoring_api import network_bp
from src.api.user.user_api import user_bp
from src.database.database_manager import load_database
from src.module.config_option import db_id, db_pw, db_port, db_ip
from src.module.logging_util import gaya_log
from src.worker.HardwareChangeDetectWorker import HardwareChangeDetectWorker
from src.worker.NetworkPacketCaptureWorker import NetworkPacketCaptureWorker
from src.worker.NetworkRealtime import NetworkMonitorThread
from src.worker.NetworkSummary import NetworkUsageSummaryThread
from src.worker.PerformanceLogWorker import PerformanceLogWorker


def create_app():

    # 현재 스크립트의 디렉토리 경로 가져오기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gaya_log(f'시스템 실행 경로 : {script_dir}')

    # 부모 디렉토리 경로 가져오기
    parent_dir = os.path.dirname(script_dir)

    # 부모 디렉토리 경로를 sys.path에 추가하여 모듈을 찾을 수 있도록 설정
    sys.path.insert(0, parent_dir)

    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_id}:{db_pw}@{db_ip}:{db_port}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    load_database(app)  # db 초기화 및 테이블 생성
    app.register_blueprint(general_bp)
    app.register_blueprint(license_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(network_bp)

    # 스레드 실행
    network_worker = NetworkMonitorThread(interval=1) # 1초 간격으로 네트워크 모니터링을 하는 대상
    network_worker.start()

    summary_worker = NetworkUsageSummaryThread(interval=600) # 5분 간격으로 네트워크 모니터링을 함
    summary_worker.start()

    # Flask 앱 설정에 worker 저장 (Blueprint에서 접근 가능)
    app.config["network_worker"] = network_worker
    app.config["summary_worker"] = summary_worker


    # Worker 초기화 및 Flask 앱 객체 전달
    # hardware_worker = HardwareChangeDetectWorker(interval=600, app=app)
    # hardware_worker.start()

    worker = PerformanceLogWorker(interval=600, cpu_threshold=80, mem_threshold=80, disk_threshold=90, app=app)
    worker.start()


    # 워커 프로세스에서 한 번만 실행
    with app.app_context():
        pass
        # create_license()

    return app

def stop_worker():
    """
    Worker 중지 함수: Flask 앱 종료 시 호출
    """
    global hardware_worker
    if hardware_worker and hardware_worker.is_alive():
        gaya_log("[Worker] Stopping hardware worker...")
        hardware_worker.stop()

if __name__ == '__main__':
    try:
        app = create_app()
        app.run(host='0.0.0.0', port=5001)

    except KeyboardInterrupt:
        gaya_log("[App] Shutting down...")
    finally:
        stop_worker()  # 앱 종료 시 Worker 중지
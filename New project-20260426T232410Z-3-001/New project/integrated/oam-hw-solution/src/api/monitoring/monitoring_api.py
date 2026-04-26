from datetime import datetime

import psutil
from sqlalchemy import func
from sqlalchemy.exc import ProgrammingError

from src.entity.detect.performance_log import PerformanceLog
from src.module.hw_performance_util import  get_current_cpu_usage, get_current_memory_usage, \
     get_total_disk_usage
from src.module.log_util import get_recent_logs
from flask import Blueprint, request, jsonify, current_app

from src.worker.NetworkRealtime import NetworkMonitorThread

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/flask_api')

# @monitoring_bp.route('/performance_logs', methods=['GET'])
# def get_performance_logs():
#     days = int(request.args.get('days', 7))  # Default: last 7 days
#     limit = int(request.args.get('limit', 10))  # Default: max 10 records
#     logs = get_recent_logs(PerformanceLog, days=days, limit=limit)
#     return jsonify([log.to_dict() for log in logs])


@monitoring_bp.route('/performance_logs', methods=['GET'])
def get_performance_logs():
    """
    특정 날짜 범위의 성능 로그 반환
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 기본값: 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = today
    if not end_date:
        end_date = today

    try:
        # 날짜 문자열을 파싱
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # 시작 날짜가 종료 날짜보다 뒤에 있을 경우 에러 처리
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # 로그를 필터링 (날짜만 비교)
        logs = PerformanceLog.query.filter(
            func.date(PerformanceLog.date) >= start_date.date(),
            func.date(PerformanceLog.date) <= end_date.date()
        ).order_by(PerformanceLog.date.asc()).all()

        # JSON 응답으로 변환
        return jsonify([log.to_dict() for log in logs])
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

@monitoring_bp.route('/current_status', methods=['GET'])
def get_current_status_endpoint():
    """
    현재 CPU, 메모리, 디스크 상태 반환
    """
    network_worker:NetworkMonitorThread = current_app.config.get("network_worker")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "date": current_time,
        "cpu_usage": get_current_cpu_usage(),
        "mem_usage": get_current_memory_usage(),
        "disk_usage": get_total_disk_usage(),
        "network_inbound_usage": network_worker.get_total_inbound_usage(),
    })
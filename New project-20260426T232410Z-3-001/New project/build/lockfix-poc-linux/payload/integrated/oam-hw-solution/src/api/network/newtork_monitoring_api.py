
from datetime import datetime

from flask import Blueprint, jsonify, current_app, request
from sqlalchemy import func

from src.entity.detect.network_card_performance_log import get_network_card_performance_log_by_nic, \
    NetworkCardPerformanceLog
from src.network.network_util import get_active_network_interfaces

network_bp = Blueprint('network', __name__, url_prefix='/flask_api/network')


@network_bp.route("/realtime", methods=["GET"])
def get_realtime_network_usage():
    """ 1초 간격 실시간 네트워크 사용량 반환 API """
    network_worker = current_app.config.get("network_worker")
    if network_worker:
        return jsonify(network_worker.get_network_usage())
    return jsonify({"error": "Network worker is not running"}), 500


@network_bp.route("/summary", methods=["GET"])
def get_network_summary():
    """ 5분 간격 전체 네트워크 사용량 요약 API """
    summary_worker = current_app.config.get("summary_worker")
    if summary_worker:
        return jsonify(summary_worker.get_network_summary())
    return jsonify({"error": "Summary worker is not running"}), 500


@network_bp.route("/cards", methods=["GET"])
def get_network_cards():
    """ 사용 가능한 네트워크 카드 목록 반환 API """
    summary_worker = current_app.config.get("summary_worker")
    if summary_worker:
        return jsonify({"network_cards": get_active_network_interfaces()})
    return jsonify({"error": "Summary worker is not running"}), 500

@network_bp.route("/card/<nic_name>", methods=["GET"])
def get_network_card_data(nic_name):
    """ 특정 네트워크 카드의 5분 평균 사용량 데이터 반환 API """

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
        logs = NetworkCardPerformanceLog.query.filter_by(nic_name=nic_name).filter(
            func.date(NetworkCardPerformanceLog.date) >= start_date.date(),
            func.date(NetworkCardPerformanceLog.date) <= end_date.date()
        ).order_by(NetworkCardPerformanceLog.date.asc()).all()

        # JSON 응답으로 변환
        return jsonify([log.to_dict() for log in logs])
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400


from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import func
from src.entity.detect.general_log import GeneralLog
from src.entity.detect.hardware_change_event import HardwareChangeEvent
from src.entity.detect.performance_excess_event import PerformanceExcessEvent
from src.entity.detect.performance_log import PerformanceLog
from src.module.date_util import parse_date_with_default

# Blueprint 정의
detect_bp = Blueprint('detect', __name__, url_prefix='/flask_api/detect')

@detect_bp.route('/all_logs', methods=['GET'])
def get_all_logs():
    """
    특정 날짜 범위 내 모든 로그를 가져옵니다.
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        # Ensure start_date is not after end_date
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # Filter logs by date range
        general_logs = GeneralLog.query.filter(
            func.date(GeneralLog.date) >= start_date.date(),
            func.date(GeneralLog.date) <= end_date.date()
        ).order_by(GeneralLog.date.desc()).all()

        hardware_change_events = HardwareChangeEvent.query.filter(
            func.date(HardwareChangeEvent.date) >= start_date.date(),
            func.date(HardwareChangeEvent.date) <= end_date.date()
        ).order_by(HardwareChangeEvent.date.desc()).all()

        performance_excess_events = PerformanceExcessEvent.query.filter(
            func.date(PerformanceExcessEvent.date) >= start_date.date(),
            func.date(PerformanceExcessEvent.date) <= end_date.date()
        ).order_by(PerformanceExcessEvent.date.desc()).all()

        # Merge all logs with identifiers
        all_logs = [
            {"type": "LOGS", "date": log.date, "content": log.log_content} for log in general_logs
        ] + [
            {"type": "DETECT", "date": event.date, "content": f"[{event.change_type}] ({event.hardware_type}) ({event.changed_model})"} for event in hardware_change_events
        ] + [
            {"type": "WARNING", "date": event.date, "content": f"[{event.hardware_type}] {event.actual_value}% (임계:{event.threshold}%)"} for event in performance_excess_events
        ]

        # Sort all logs by date (descending)
        all_logs.sort(key=lambda x: x['date'], reverse=True)

        return jsonify(all_logs)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



# API to get the count of logs for a specific date range
@detect_bp.route('/logs/count', methods=['GET'])
def get_logs_count():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        # Ensure start_date is not after end_date
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # Count logs in the date range
        performance_count = PerformanceLog.query.filter(
            func.date(PerformanceLog.date) >= start_date.date(),
            func.date(PerformanceLog.date) <= end_date.date()
        ).count()

        general_count = GeneralLog.query.filter(
            func.date(GeneralLog.date) >= start_date.date(),
            func.date(GeneralLog.date) <= end_date.date()
        ).count()

        hardware_change_count = HardwareChangeEvent.query.filter(
            func.date(HardwareChangeEvent.date) >= start_date.date(),
            func.date(HardwareChangeEvent.date) <= end_date.date()
        ).count()

        return jsonify({
            'performance_logs': performance_count,
            'general_logs': general_count,
            'hardware_change_events': hardware_change_count
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# General Log Routes
@detect_bp.route('/general_logs', methods=['GET'])
def get_general_logs():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        # Ensure start_date is not after end_date
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # Filter logs by date range
        logs = GeneralLog.query.filter(
            func.date(GeneralLog.date) >= start_date.date(),
            func.date(GeneralLog.date) <= end_date.date()
        ).order_by(GeneralLog.date.desc()).all()

        return jsonify([log.to_dict() for log in logs])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Hardware Change Event Routes
@detect_bp.route('/hardware_change_events', methods=['GET'])
def get_hardware_change_events():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        # Ensure start_date is not after end_date
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # Filter logs by date range
        events = HardwareChangeEvent.query.filter(
            func.date(HardwareChangeEvent.date) >= start_date.date(),
            func.date(HardwareChangeEvent.date) <= end_date.date()
        ).order_by(HardwareChangeEvent.date.desc()).all()

        return jsonify([event.to_dict() for event in events])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# Performance Excess Event Routes
@detect_bp.route('/performance_excess_events', methods=['GET'])
def get_performance_excess_events():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        # Ensure start_date is not after end_date
        if start_date > end_date:
            return jsonify({"error": "Start date must be earlier than or equal to end date."}), 400

        # Filter logs by date range
        events = PerformanceExcessEvent.query.filter(
            func.date(PerformanceExcessEvent.date) >= start_date.date(),
            func.date(PerformanceExcessEvent.date) <= end_date.date()
        ).order_by(PerformanceExcessEvent.date.desc()).all()

        return jsonify([event.to_dict() for event in events])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
from __future__ import annotations


def integrated_solution_summary() -> dict:
    return {
        "title": "우암전자 통합 운영 솔루션",
        "subtitle": "DataCenter + Hardware Web Solution 통합 PoC",
        "systems": [
            {
                "id": "datacenter",
                "name": "DataCenter",
                "role": "서버 자원 및 계정 운영",
                "status": "NORMAL",
                "endpoint": "112.148.194.115:3223",
                "features": ["서버 자원 모니터링", "스토리지/디스크 현황", "계정 확인", "실시간 상태"],
            },
            {
                "id": "hardware-web",
                "name": "Hardware Web Solution",
                "role": "하드웨어 관제 및 로그 운영",
                "status": "NORMAL",
                "endpoint": "112.148.194.115:3222",
                "features": ["Monitoring", "Dashboard", "Detect", "Notification", "Logs"],
            },
        ],
        "metrics": [
            {"name": "Server", "value": "2", "unit": "nodes", "level": "good"},
            {"name": "Memory", "value": "64", "unit": "GB", "level": "good"},
            {"name": "NIC", "value": "4", "unit": "ports", "level": "good"},
            {"name": "Disk", "value": "8", "unit": "slots", "level": "warn"},
        ],
        "modules": [
            {
                "name": "Monitoring",
                "description": "서버와 하드웨어 상태를 실시간으로 관제합니다.",
                "state": "ACTIVE",
            },
            {
                "name": "Dashboard",
                "description": "주요 상태, 자원 사용량, 감지 이벤트를 카드형으로 요약합니다.",
                "state": "ACTIVE",
            },
            {
                "name": "Detect History",
                "description": "감지 항목과 발생 시간을 기록하고 조회합니다.",
                "state": "READY",
            },
            {
                "name": "Notification",
                "description": "위험 상태와 장애 이벤트를 관리자에게 표시합니다.",
                "state": "READY",
            },
            {
                "name": "Logs / Download",
                "description": "운영 로그를 조회하고 다운로드 대상으로 관리합니다.",
                "state": "READY",
            },
            {
                "name": "Contact Service",
                "description": "원격지원 및 고객지원 연결 정보를 제공합니다.",
                "state": "READY",
            },
            {
                "name": "License",
                "description": "라이선스 키와 사용 기간, 갱신 상태를 확인합니다.",
                "state": "READY",
            },
            {
                "name": "Network Status",
                "description": "네트워크 연결 상태와 통신 가능 여부를 확인합니다.",
                "state": "ACTIVE",
            },
        ],
        "detections": [
            {"time": "2026-04-25 10:20", "source": "DataCenter", "event": "Disk usage watch", "severity": "INFO"},
            {"time": "2026-04-25 10:25", "source": "Hardware Web", "event": "Network heartbeat", "severity": "INFO"},
            {"time": "2026-04-25 10:31", "source": "LOCK-FIX", "event": "Mock isolation verified", "severity": "NORMAL"},
        ],
        "notifications": [
            {"level": "NORMAL", "message": "통합 UI가 mock 상태로 동작 중입니다."},
            {"level": "NOTICE", "message": "실제 장비 제어 전 dry_run 해제가 필요합니다."},
        ],
        "license": {
            "product": "LOCK-FIX Integrated PoC",
            "license_key": "POC-MOCK-LICENSE",
            "issued_at": "2026-04-25",
            "expires_at": "2026-07-25",
            "status": "VALID",
        },
        "network": [
            {"target": "DataCenter SSH", "address": "112.148.194.115:3223", "status": "CONNECTED"},
            {"target": "WebSolution SSH", "address": "112.148.194.115:3222", "status": "CONNECTED"},
            {"target": "Local Web UI", "address": "127.0.0.1:8088", "status": "CONNECTED"},
        ],
        "contact": {
            "name": "우암전자 고객지원",
            "remote_url": "https://www.oam.co.kr/remote",
            "description": "현장 장애 및 원격지원 요청 시 사용하는 고객지원 연결 정보입니다.",
        },
    }

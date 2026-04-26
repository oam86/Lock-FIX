import platform
import smtplib

import psutil
from gevent.resolver.dnspython import dns
from src.module.logging_util import gaya_log


def check_smtp_server(mx_record):
    """
    지정된 MX 레코드에 SMTP 연결 확인
    """
    if not isinstance(mx_record, str):
        gaya_log(f"Invalid MX record type: {type(mx_record)}. Expected a string.")
        raise ValueError("MX record must be a string.")

    gaya_log(f"Checking SMTP server: {mx_record}")
    try:
        with smtplib.SMTP(mx_record, 25, timeout=5) as server:
            server.noop()  # 연결 테스트
        gaya_log(f"SMTP server {mx_record} is reachable.")
        return True
    except Exception as e:
        gaya_log(f"General Exception: Failed to check SMTP server {mx_record}. Error: {str(e)}")
    return False


def get_mx_record(domain):
    """
    도메인의 MX 레코드를 반환
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_record = str(answers[0].exchange).rstrip('.')
        gaya_log(f"MX record for {domain}: {mx_record}")
        return mx_record
    except dns.resolver.NoAnswer:
        gaya_log(f"No MX record found for domain: {domain}")
        return None
    except dns.resolver.NXDOMAIN:
        gaya_log(f"Domain does not exist: {domain}")
        return None


def check_email_smtp(email):
    """
    이메일의 도메인을 기반으로 SMTP 상태를 확인
    """
    domain = email.split('@')[-1]
    gaya_log(f"Extracted domain from email: {domain}")

    # MX 레코드 확인
    mx_record = get_mx_record(domain)
    if not mx_record:
        gaya_log(f"No valid MX record found for domain: {domain}")
        return {"success": False, "message": f"{domain} 도메인에 메일을 보낼 수 없습니다(MX Record X)"}

    # SMTP 서버 상태 확인
    smtp_status = check_smtp_server(mx_record)
    if smtp_status:
        gaya_log(f"{domain} 도메인의 SMTP 서버 ({mx_record})에 연결할 수 있습니다.")
        return {"success": True, "message": f"{domain} 도메인의 SMTP 서버에 연결할 수 있습니다."}
    else:
        gaya_log(f"{domain} 도메인의 SMTP 서버 ({mx_record})에 연결할 수 없습니다.")
        return {"success": False, "message": f"{domain} 도메인의 SMTP 서버에 연결할 수 없습니다."}


def get_active_network_interfaces():
    """
    활성화된 네트워크 인터페이스만 반환 (가상 NIC 자동 필터링)
    - macOS: `utunX`, `awdl0`, `lo0`, `bridgeX`, `anpiX` 등 필터링
    - Linux: `lo`, `docker0`, `virbrX`, `brX`, `tapX` 등 필터링
    """
    net_info = psutil.net_if_stats()

    # 현재 OS 확인 (macOS / Linux)
    CURRENT_OS = platform.system().lower()

    # 필터링할 NIC 목록 (OS별 구분)
    if CURRENT_OS == "darwin":  # macOS
        exclude_nics = ["utun", "awdl", "lo", "bridge", "anpi"]
    else:  # Linux / Ubuntu
        exclude_nics = ["lo", "docker", "virbr", "br", "tap"]

    active_interfaces = [
        nic for nic, stats in net_info.items()
        if stats.isup and not any(x in nic for x in exclude_nics)
    ]
    return active_interfaces
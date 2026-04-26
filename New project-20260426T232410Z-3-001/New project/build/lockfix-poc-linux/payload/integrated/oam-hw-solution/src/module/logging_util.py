import logging
from datetime import datetime
import os

# 로그 디렉터리 설정
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 로그 포맷 설정
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 로거 생성 및 설정
logger = logging.getLogger("LogUtil")
logger.setLevel(logging.DEBUG)

# 콘솔 핸들러 추가
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(console_handler)

# 초기 파일 핸들러
current_log_file = None  # 현재 로그 파일 이름
file_handler = None  # 파일 핸들러 객체

def update_file_handler():
    global current_log_file, file_handler
    new_log_file = get_log_file_name()
    if current_log_file != new_log_file:  # 날짜가 변경되었는지 확인
        if file_handler:
            logger.removeHandler(file_handler)  # 기존 핸들러 제거
        current_log_file = new_log_file
        file_handler = logging.FileHandler(current_log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)  # 새로운 핸들러 추가

# 현재 날짜를 기준으로 로그 파일 이름 설정
def get_log_file_name():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")

# 로그 기록 함수
def gaya_log(message, level="info"):
    """
    메시지를 로그로 기록하고 콘솔에도 출력.

    :param message: 로그 메시지
    :param level: 로그 레벨 (default: "info")
    """
    update_file_handler()  # 날짜가 변경되었는지 확인하고 파일 핸들러 업데이트
    log_method = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical
    }.get(level.lower(), logger.info)  # 기본 레벨은 info

    log_method(message)
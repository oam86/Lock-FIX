import configparser
import sys
import os
import psutil
from src.module.logging_util import gaya_log
from src.network.network_util import get_active_network_interfaces

# configparser 객체 생성
config = configparser.ConfigParser()
config_path = 'config.ini'

try:
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
        gaya_log(f'설정 파일 경로: {config_path} 로딩완료')
    else:
        gaya_log(f'설정 파일을 찾을 수 없습니다 {config_path}')
except Exception as e:
    gaya_log(f'설정 파일을 로드하는 중 오류 발생: {e}')
    sys.exit(1)
# 기존 기능 유지
version = 'v1.0.1-2025-02-01'

gaya_log('-------------------------------------------------------')
gaya_log(f'현재 버전 : {version} 설정 파일 로딩')
gaya_log('-------------------------------------------------------')

# Network
external_ip = config['Network']['external_ip']
gaya_log(f'현재 외부 IP : {external_ip}')

# OAM Data Center
oam_data_center_ip = config['OAM']['data_center_ip']
oam_data_center_port = config['OAM']['data_center_port']
gaya_log(f'OAM DataCenter : {oam_data_center_ip}:{oam_data_center_port}')

OAM_DATA_CENTER_API_URL = f'http://{oam_data_center_ip}:{oam_data_center_port}'

# Database
db_ip = config['Database']['ip']
db_port = config['Database']['port']
db_id = config['Database']['id']
db_pw = config['Database']['pw']
gaya_log(f'Database Path : {db_ip}:{db_port} {db_id}/{db_pw}')

""" 네트워크 카드의 대역폭 설정을 로드하고, 누락된 경우 기본값 추가 """
if 'Network_Bandwidth' not in config:
    config['Network_Bandwidth'] = {}

available_nics = get_active_network_interfaces()
updated = False

DEFAULT_BANDWIDTH_KBPS = 200_000  # 200mbps

for nic in available_nics:
    if nic not in config['Network_Bandwidth']:
        config['Network_Bandwidth'][nic] = str(DEFAULT_BANDWIDTH_KBPS)
        gaya_log(f'[{nic}] 대역폭이 설정되지 않아 기본값({DEFAULT_BANDWIDTH_KBPS} kbps)으로 추가됨.')
        updated = True
    else:
        gaya_log(f'[{nic}] 대역폭 설정값: {config["Network_Bandwidth"][nic]}')

# 변경 사항이 있을 경우 설정 파일 저장
if updated:
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    gaya_log(f'네트워크 대역폭 설정이 업데이트됨. 파일에 저장됨: {config_path}')



def get_network_bandwidth(nic_name):
    """
    네트워크 카드(nic_name)의 대역폭을 kbps 단위로 반환.
    config.ini의 [Network_Bandwidth] 섹션에서 값을 찾고,
    없으면 기본값 (1Gbps) 반환.
    """
    try:
        bandwidth_kbps = config.getint('Network_Bandwidth', nic_name, fallback=DEFAULT_BANDWIDTH_KBPS)
        return bandwidth_kbps
    except Exception as e:
        gaya_log(f'[{nic_name}] 대역폭 설정 로드 중 오류 발생: {e}')
        return DEFAULT_BANDWIDTH_KBPS
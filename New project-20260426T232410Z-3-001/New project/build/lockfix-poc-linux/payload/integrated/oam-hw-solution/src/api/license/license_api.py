from datetime import datetime

import requests
from flask import Blueprint, request, jsonify
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from src.database import db
from src.entity.detect.hardware_change_event import HardwareChangeEvent
from src.entity.init_hardware_info import InitHardwareInfo
from src.entity.license_info import LicenseInfo
from src.module.config_option import OAM_DATA_CENTER_API_URL
from src.module.hw_info import get_all_hardware_info
from src.module.logging_util import gaya_log
license_bp = Blueprint('license', __name__, url_prefix='/flask_api')

# License Info Routes
@license_bp.route('/license_info', methods=['GET'])
def get_license_info():
    # LicenseInfo가 반드시 하나라고 가정
    license_info = LicenseInfo.query.first()

    if license_info is None:
        gaya_log('라이선스가 존재하지 않습니다')
        return jsonify({"success": False, "message": "No license found"}), 404

    try:
        # 외부 API 호출
        url = f'{OAM_DATA_CENTER_API_URL}/java_api/external/license/expireDate'
        payload = {"supportCode": license_info.license_key}
        gaya_log(f'url {url}')

        response = requests.post(url, json=payload, timeout=5)



        if response.status_code == 200:
            # 외부 API에서 만료일자 가져오기
            expiry_date = response.content.decode('utf-8')
            gaya_log(f"서버로 부터 전달받은 만료일자  {expiry_date}")

            if expiry_date:
                # 기존 데이터에 만료일자 업데이트
                license_info.renewal_date = datetime.now()
                license_info.expiry_date = datetime.fromisoformat(expiry_date)
                db.session.commit()
            else:
                pass

        if response.status_code == 400:
            # 이건 사용이 만료되었단거다
            gaya_log(f'만료된 라이선스거나 삭제된 라이선스 입니다')
            LicenseInfo.query.delete() # 라이선스 일괄 삭제
            db.session.commit()
            return jsonify({"success": False, "message": "사용 불가능한 라이선스 입니다"}), 401

    except Exception as e:
        db.session.rollback()
        gaya_log(f'우암전자 데이터 센터와의 라이선스 인증에 실패했습니다 {e}')
    finally:
        return jsonify(license_info.to_dict())

@license_bp.route('/license_input', methods=['POST'])
def license_input():
    # 요청에서 라이선스 키와 회사명을 가져옴
    data = request.get_json()
    support_code = data.get("licenseKey")
    customer_name = data.get("clientName")

    gaya_log(f'라이선스 등록 요청 {customer_name} SupportCode : {support_code}')

    if not support_code or not customer_name:
        gaya_log('데이터가 존재하지 않습니다')
        return jsonify({"success": False, "message": "License key and customer name are required"}), 400

    # 우암 데이터 센터와 연계해서 라이선스가 있는지 확인함
    try:
        # hardware_data = [
        #     {"Type": "CPU", "Model": "Intel(R) Xeon(R) CPU E5-2680 v3 @ 2.50GHz", "Serial": None},
        #     {"Type": "MEMORY", "Model": "HMA42GR7AFR4N-TF", "Serial": "265E8C1D"},
        #     {"Type": "MEMORY", "Model": "M393A2G40DB0-CPB", "Serial": "4122C53A"},
        #     {"Type": "DISK", "Model": "PERC H730P Mini", "Serial": "361866da0a70d7f002e585dd70b68f79d"},
        #     {"Type": "HBA", "Model": "LightPulse Fibre Channel Host Adapter", "Serial": None},
        #     {"Type": "NIC", "Model": "NetXtreme BCM5720 Gigabit Ethernet PCIe", "Serial": "18:66:da:fb:20:62"},
        #     {"Type": "SAS_CARD", "Model": "MegaRAID SAS-3 3108 [Invader]", "Serial": None}
        # ]

        hardware_data = get_all_hardware_info()

        payload = {
            "supportCode": support_code,
            "hardwareData": hardware_data
        }

        url = f"{OAM_DATA_CENTER_API_URL}/java_api/external/license/register"
        gaya_log(f'url {url}')
        gaya_log(f'서버측으로 라이선스 등록 요청 PAYLOAD : {payload}')

        response = requests.post(
            url,
            json=payload  # JSON 형식으로 데이터 전달,
            ,timeout=3
        )

        if response.status_code == 200:
            license_data = response.json()
            gaya_log(f'응답 완료 : ${license_data}')
            if license_data:

                # 기존 라이선스 데이터를 일괄 삭제
                LicenseInfo.query.delete()

                # Flask 데이터베이스에 새 데이터 삽입 전에 작업
                new_license = LicenseInfo(
                    license_key=license_data['support_code'],
                    customer_name=license_data['client']['name'],
                    expiry_date=license_data.get('expiration_at'),
                    renewal_date=license_data.get('updated_at'),
                    start_date=license_data.get('used_at')
                )

                # 초기 하드웨어 정보 일괄 삭제
                InitHardwareInfo.query.delete()

                # 하드웨어 변경 이벤트 일괄 삭제
                HardwareChangeEvent.query.delete()

                # 추가 데이터 삽입 (예: 초기 하드웨어 정보)
                init_hardware_info_list = []
                for hw in hardware_data:
                    init_info = InitHardwareInfo(
                        hardware_type=hw['Type'],
                        model_name=hw['Model'],
                        serial_number=hw['Serial']
                    )
                    init_hardware_info_list.append(init_info)

                try:
                    # 데이터베이스에 라이선스 및 하드웨어 정보 저장
                    db.session.add(new_license)
                    db.session.add_all(init_hardware_info_list)
                    db.session.commit()
                    return jsonify({"success": True, "message": "라이선스가 성공적으로 등록되었습니다"}), 200
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"success": False, "message": "Failed to add license key", "error": str(e)}), 500
        else:
            gaya_log(f'{support_code} 는 유효하지 않습니다')
            return jsonify({"success": False, "message": "유효하지 않은 라이선스 키 값입니다"}), 500

    except requests.exceptions.RequestException as e:
        gaya_log(e)
        return jsonify({"success": False, "message": "라이선스가 유효하지 않거나 이미 등록된 라이선스 입니다."}), 500

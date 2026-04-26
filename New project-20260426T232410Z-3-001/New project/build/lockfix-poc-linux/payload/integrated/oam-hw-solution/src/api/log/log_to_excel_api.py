import pandas as pd
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from io import BytesIO

from sqlalchemy import func

from src.database.database_manager import db
from src.entity.detect.performance_log import PerformanceLog
from src.entity.detect.hardware_change_event import HardwareChangeEvent
from src.entity.detect.general_log import GeneralLog, create_general_log
from src.entity.detect.performance_excess_event import PerformanceExcessEvent
from src.entity.init_hardware_info import InitHardwareInfo
from src.entity.license_info import LicenseInfo
from src.entity.user_info import UserInfo
from src.module.date_util import parse_date_with_default
from src.module.logging_util import gaya_log

export_bp = Blueprint('export', __name__, url_prefix='/flask_api')

ENTITY_MAPPING = {
    "성능 로그": PerformanceLog,
    "하드웨어 변경 감지 로그": HardwareChangeEvent,
    "일반 로그": GeneralLog,
    "초과 사용 로그": PerformanceExcessEvent,
    "초기 하드웨어 설정 정보": InitHardwareInfo,
    "라이선스 정보": LicenseInfo,
    "계정 정보": UserInfo,
}

@export_bp.route('/to_excel', methods=['POST'])
def export_all_to_excel():
    try:
        # 요청 파라미터 확인
        data = request.json
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")

        # Parse dates with default
        start_date = parse_date_with_default(start_date_str)
        end_date = parse_date_with_default(end_date_str)

        gaya_log(f'{start_date} ~ {end_date} 간의 로그 다운로드 요청이 들어왔습니다')

        # 엑셀 파일을 위한 메모리 스트림 생성
        output = BytesIO()

        # pandas ExcelWriter 생성
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_created = False  # 적어도 하나의 시트가 생성되었는지 확인하는 플래그

            for entity_name, entity_class in ENTITY_MAPPING.items():
                gaya_log(f'[PROCESSING] {entity_name} 엔터티 처리 시작')

                query = entity_class.query
                records = None

                if hasattr(entity_class, 'date'):
                    records = query.filter(
                        func.date(entity_class.date) >= start_date.date(),
                        func.date(entity_class.date) <= end_date.date()
                    ).order_by(entity_class.date.desc()).all()
                else:
                    records = query.all()

                if not records:
                    gaya_log(f'[INFO] {entity_name}에 데이터가 없습니다. 빈 시트를 생성합니다.')
                    # 데이터가 없는 경우 기본 메시지 포함
                    empty_df = pd.DataFrame({"Message": ["No data available in the requested period."]})
                    empty_df.to_excel(writer, index=False, sheet_name=entity_name)
                    gaya_log(f'[SHEET] {entity_name} 빈 시트 생성 완료')
                else:
                    gaya_log(f'[DATA] {entity_name}: {len(records)}개의 데이터가 존재합니다.')
                    data_list = [record.to_dict() for record in records]
                    df = pd.DataFrame(data_list)
                    df.to_excel(writer, index=False, sheet_name=entity_name)
                    gaya_log(f'[SHEET] {entity_name} 시트 생성 완료')

                sheet_created = True  # 적어도 하나의 시트가 생성됨

            # 모든 엔터티에 데이터가 없을 경우, "No Data" 시트 생성
            if not sheet_created:
                gaya_log('[INFO] 전체 엔터티에서 데이터가 없으므로 기본 메시지 시트를 생성합니다.')
                empty_df = pd.DataFrame({"Message": ["No data available across all entities."]})
                empty_df.to_excel(writer, index=False, sheet_name="No Data")

        # 메모리 스트림 위치를 처음으로 이동
        output.seek(0)

        gaya_log('[SUCCESS] 전체 로그를 반환합니다.')
        create_general_log(f"[{start_date} ~ {end_date}] 기간의 로그 추출 완료")

        # 파일 반환
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"all_logs_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        gaya_log(f'[ERROR] 로그 생성 실패: {e}')
        gaya_log(f'[TRACEBACK] {error_trace}')
        create_general_log(f"로그를 추출하는데 문제가 발생했습니다 : {str(e)}")
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}", "details": error_trace}), 500
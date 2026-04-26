from datetime import datetime

import requests
from flask import Blueprint, request, jsonify

from src.module.config_option import OAM_DATA_CENTER_API_URL
from src.database import db
from src.entity.detect.general_log import create_general_log
from src.entity.user_info import UserInfo
from src.module.logging_util import gaya_log
from src.network.network_util import check_email_smtp

user_bp = Blueprint('user', __name__, url_prefix='/flask_api')
# 전역 변수로 로그인 상태 관리
logged_in_users = []

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    모든 유저 정보를 가져오는 엔드포인트
    """
    try:
        users = UserInfo.query.all()

        if not users:
            return jsonify({"success": False, "message": "No users found"}), 404

        # 유저 데이터에 SMTP 상태 추가
        user_data = []
        for user in users:
            smtp_check = check_email_smtp(user.email)
            is_logged_in = user.email in logged_in_users
            user_data.append({
                **user.to_dict(),
                "smtp_status": smtp_check["success"],
                "smtp_message": smtp_check["message"],  # 상태 메시지 추가
                "network_connection": is_logged_in,  # 현재 로그인 상태 여부
            })

        return jsonify({
            "success": True,
            "data": user_data
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

import re

@user_bp.route('/register_user', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    support_code = data.get("support_code")
    gaya_log(f'email: {email}, password: {password} support code : {support_code} 회원가입요청')

    # 이메일 정규식
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    # 이메일 및 비밀번호 유효성 검사
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400
    if not re.match(email_regex, email):
        gaya_log('이메일 포맷이 잘못되었습니다')
        return jsonify({"success": False, "message": "Invalid email format"}), 400

    #SMTP 서버 상태 확인
    # smtp_check = check_email_smtp(email)
    # if not smtp_check["success"]:
    #     return jsonify({"success": False, "message": smtp_check["message"]}), 400

    # 외부 API 호출
    try:
        external_response = requests.post(
            f"{OAM_DATA_CENTER_API_URL}/java_api/external/user/register",
            params={"supportCode": support_code, "email": email, "password": password},
            timeout=5,
        )
        gaya_log('회원가입 요청 우암전자 전달')
        if external_response.status_code != 200:
            gaya_log(f'회원가입 실패 : {external_response.status_code}')
            return jsonify({"success": False, "message": "회원가입에 실패했습니다"}), 400
    except requests.exceptions.RequestException as e:
        gaya_log(f'email: {email}, password: {password} support code : {support_code} 회원가입 실패 - 우암전자 데이터 센터와의 연계 실패 {e}')
        return jsonify({"success": False, "message": '우암전자 데이터센터와의 연계에 실패했습니다'}), 400

    # DB에 사용자 저장
    new_user = UserInfo(email=email, password=password, last_login=datetime.now())
    try:
        db.session.add(new_user)
        db.session.commit()
        create_general_log(f"{email} 계정 회원가입 완료")
        return jsonify({"success": True, "message": "User registered successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to register user", "error": str(e)}), 400

@user_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    email = data.get("user_id")
    if email in logged_in_users:
        logged_in_users.remove(email)  # 이메일 제거
        gaya_log(f'email: {email} logged out')

    return jsonify({"success": True, "message": f"{email} logged out successfully"}), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    support_code = data.get("support_code")

    gaya_log(f'email: {email}, password: {password} support code : {support_code} 로그인 요청')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    user = UserInfo.query.filter_by(email=email).first()
    if not user or user.password != password:

        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # 외부 API 호출
    try:

        external_response = requests.post(
            f"{OAM_DATA_CENTER_API_URL}/java_api/external/user/login",
            params={"supportCode": support_code, "email": email, "password": password}
            ,timeout=2,
        )

        if external_response.status_code != 200:
            UserInfo.query.filter_by(email=email).delete()
            db.session.commit()  # 커밋 필수
            gaya_log(f'(로그인 요청)데이터 센터에서 반환한 {email} 계정 [사용불가]')
            return jsonify({"success": False, "message": "사용할 수 없는 계정입니다"})

        gaya_log(f'(로그인 요청)데이터 센터에서 반환한 결과값 : {external_response} [사용 가능]')

    except requests.exceptions.RequestException as e:
        gaya_log('우암전자 데이터센터와의 고객사 관리자 계정 연결에 실패했습니다')
        pass
        # return jsonify({"success": False, "message": str(e)}), 500

    # Update last login time
    user.last_login = datetime.now()
    try:
        db.session.commit()
        gaya_log(f'{email} 로그인 성공')
        # 로그인 상태에 이메일 추가
        if email not in logged_in_users:
            logged_in_users.append(email)

        return jsonify({"success": True, "message": "Login successful", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to update last login time", "error": str(e)}), 500
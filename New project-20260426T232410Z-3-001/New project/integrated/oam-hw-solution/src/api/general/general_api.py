from flask import Blueprint, jsonify

from src.entity.init_hardware_info import InitHardwareInfo


general_bp = Blueprint('general', __name__, url_prefix='/flask_api')
# Init Hardware Info Routes
@general_bp.route('/init_hardware_info', methods=['GET'])
def get_init_hardware_info():
    info = InitHardwareInfo.query.all()
    return jsonify([item.to_dict() for item in info])

# app/routes/api.py

from flask import Blueprint, jsonify
from flask_login import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
@login_required
def status():
    return jsonify({
        "status": "ok",
        "message": "API funcionando correctamente"
    })

# app/routes/admin.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import UserRole

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_home():
    if current_user.role != UserRole.ADMIN:
        return "Acceso denegado", 403
    return render_template('admin/dashboard.html', user=current_user)

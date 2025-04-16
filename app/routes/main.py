from flask import Blueprint, render_template
from flask_login import current_user
from app.models.user import UserRole

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("index.html", user=current_user, UserRole=UserRole)
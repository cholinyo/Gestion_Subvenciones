from enum import Enum
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Asegúrate de que 'db' está correctamente definido en app/__init__.py

class UserRole(Enum):
    ADMIN = "admin"
    GESTOR = "gestor"
    CONSULTA = "consulta"

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(
        db.Enum(UserRole, name="user_role", validate_strings=True),
        default=UserRole.CONSULTA,  # Corrección aquí
        nullable=False
    )
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def set_password(self, password):
        if not password:
            raise ValueError("Password must not be empty.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active

    def __repr__(self):
        return f"<User {self.username} - {self.role.value}>"

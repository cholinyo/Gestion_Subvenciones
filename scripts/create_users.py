import os
import sys
from werkzeug.security import generate_password_hash

# Asegura que la carpeta raíz esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User, UserRole

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            role=UserRole.ADMIN,
            active=True
        )
        admin.set_password('admin')
        db.session.add(admin)
        print("✅ Usuario admin creado.")
    else:
        print("ℹ️ Usuario admin ya existe.")

    if not User.query.filter_by(username='gestor').first():
        gestor = User(
            username='gestor',
            email='gestor@example.com',
            role=UserRole.GESTOR,
            active=True
        )
        gestor.set_password('gestor')
        db.session.add(gestor)
        print("✅ Usuario gestor creado.")
    else:
        print("ℹ️ Usuario gestor ya existe.")

    db.session.commit()
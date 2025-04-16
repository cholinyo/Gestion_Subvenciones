from app import create_app, db
from app.models.user import User, UserRole

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.drop_all()  # Be careful with this in production!
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role=UserRole.ADMIN,
            active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("Base de datos inicializada.")
        print("Usuario administrador creado:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    init_db()

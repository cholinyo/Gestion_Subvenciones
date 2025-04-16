from app import create_app, db
from app.models.user import User, UserRole

def check_db():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print("\nUsers in database:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Role type: {type(user.role)}")
            print(f"Active: {user.active}")
            print("-" * 50)

if __name__ == '__main__':
    check_db()
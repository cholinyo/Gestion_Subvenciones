from flask import Flask
from config import Config
from app.extensions import db, login_manager,migrate    
  


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)  # ✅ INICIALIZA Migrate con la app y db

    import app.models

    login_manager.init_app(flask_app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registro de blueprints
    from app.routes.auth import auth_bp
    flask_app.register_blueprint(auth_bp)

    from app.routes.main import main_bp
    flask_app.register_blueprint(main_bp)

    from app.routes.solicitudes import solicitudes_bp
    flask_app.register_blueprint(solicitudes_bp)

    # Contexto para Jinja
    from app.models.user import UserRole
    @flask_app.context_processor
    def inject_user_roles():
        return dict(UserRole=UserRole)
    

    return flask_app


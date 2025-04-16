import os

class Config:
    # Obtener el directorio base del proyecto
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para sesiones
    SECRET_KEY = 'tu-clave-secreta-aqui'  # Cambia esto en producción
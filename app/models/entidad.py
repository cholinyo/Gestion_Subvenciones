from app.extensions import db

class Entidad(db.Model):
    __tablename__ = 'entidad'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    solicitudes = db.relationship("SolicitudSubvencion", backref="entidad", lazy=True)

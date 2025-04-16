# models/historial_solicitud.py
from app.extensions import db
from datetime import datetime


class HistorialSolicitud(db.Model):
    __tablename__ = "historial_solicitud"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitud_subvencion.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    # Relaciones
    solicitud = db.relationship("SolicitudSubvencion", back_populates="historial")
    usuario = db.relationship("User", backref="cambios_realizados")

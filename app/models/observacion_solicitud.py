# models/observacion_solicitud.py
from app.extensions import db
from datetime import datetime


class ObservacionSolicitud(db.Model):
    __tablename__ = "observacion_solicitud"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("solicitud_subvencion.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # ← Nuevo campo
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    solicitud = db.relationship("SolicitudSubvencion", back_populates="observaciones")
    usuario = db.relationship("User", backref="observaciones_hechas")  # ← Asume modelo User existente


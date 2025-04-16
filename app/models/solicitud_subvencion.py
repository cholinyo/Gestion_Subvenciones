# models/solicitud_subvencion.py
from app.extensions import db
from enum import Enum
from datetime import datetime
from app.models.historial_solicitud import HistorialSolicitud
from app.models.observacion_solicitud import ObservacionSolicitud



class EstadoSolicitud(Enum):
    EN_TRAMITE = "en_tramite"
    NO_SOLICITADA = "no_solicitada"
    SOLICITADA = "solicitada"
    ALEGACIONES = "alegaciones"
    CONCEDIDA_PROVISIONAL = "concedida_provisional"
    CONCEDIDA = "concedida"
    DENEGADA = "denegada"


class SolicitudSubvencion(db.Model):
    __tablename__ = "solicitud_subvencion"

    id = db.Column(db.Integer, primary_key=True)

    # Campos obligatorios en todos los casos
    expediente_opensea = db.Column(db.String(120), nullable=False)
    expediente_subvencion = db.Column(db.String(120), nullable=False)
    entidad_id = db.Column(db.Integer, db.ForeignKey('entidad.id'), nullable=False)
    concepto = db.Column(db.String(200), nullable=False)
    tipo_fondo = db.Column(
        db.Enum("Europeo", "Nacional", "Autonómico", "Provincial", "Otros",
                name="tipo_fondo_enum", validate_strings=True),
        nullable=False
    )

    # Información económica (obligatoria excepto para "no_solicitada")
    importe_total = db.Column(db.Float)
    importe_subvencionado = db.Column(db.Float)
    fondos_propios = db.Column(db.Float)

    # Estado
    estado = db.Column(db.Enum(EstadoSolicitud, name="estado_solicitud", validate_strings=True),
                       nullable=False, default=EstadoSolicitud.EN_TRAMITE)
    motivo_no_solicitada = db.Column(db.String(255))  # Solo para estado no_solicitada
    motivo_denegada = db.Column(db.String(255))       # Solo si estado == denegada

    # Fechas clave
    fecha_limite_presentacion = db.Column(db.Date, nullable=False)  # Fecha límite de presentación Obligatorio
    fecha_presentacion_solicitud = db.Column(db.Date)
    fecha_resolucion_provisional = db.Column(db.Date)
    fecha_resolucion_definitiva = db.Column(db.Date)

    # Responsable
    gestor_responsable = db.Column(db.String(100))
    email_gestor = db.Column(db.String(120))


    # Documentación requerida
    doc_inicio_expediente = db.Column(db.Boolean, default=False)
    doc_informe_tecnico = db.Column(db.Boolean, default=False)
    doc_propuesta_jgl = db.Column(db.Boolean, default=False)
    doc_ficha_captacion = db.Column(db.Boolean, default=False)

    # Trazabilidad
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Al final del modelo SolicitudSubvencion

    observaciones = db.relationship(
    "ObservacionSolicitud",
     back_populates="solicitud",  # 👈 corrige aquí
    cascade="all, delete-orphan",
    lazy="dynamic"
    )


    historial = db.relationship(
    "HistorialSolicitud",
    back_populates="solicitud",
    cascade="all, delete-orphan"
    )

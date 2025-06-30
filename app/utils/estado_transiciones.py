from app.models.solicitud_subvencion import EstadoSolicitud
from datetime import datetime
from typing import Dict, List, Optional

class EstadoTransiciones:
    """Clase que maneja las transiciones de estado y sus reglas"""
    
    # Matriz de transiciones permitidas
    TRANSICIONES_PERMITIDAS: Dict[EstadoSolicitud, List[EstadoSolicitud]] = {
        EstadoSolicitud.EN_TRAMITE: [
            EstadoSolicitud.SOLICITADA,
            EstadoSolicitud.NO_SOLICITADA,
            EstadoSolicitud.DENEGADA
        ],
        EstadoSolicitud.SOLICITADA: [
            EstadoSolicitud.ALEGACIONES,
            EstadoSolicitud.CONCEDIDA_PROVISIONAL,
            EstadoSolicitud.DENEGADA
        ],
        EstadoSolicitud.ALEGACIONES: [
            EstadoSolicitud.CONCEDIDA_PROVISIONAL,
            EstadoSolicitud.DENEGADA
        ],
        EstadoSolicitud.CONCEDIDA_PROVISIONAL: [
            EstadoSolicitud.CONCEDIDA,
            EstadoSolicitud.DENEGADA
        ],
        EstadoSolicitud.CONCEDIDA: [],  # Estado final
        EstadoSolicitud.DENEGADA: [],   # Estado final
        EstadoSolicitud.NO_SOLICITADA: []  # Estado final
    }

    @staticmethod
    def validar_transicion(estado_actual: EstadoSolicitud, nuevo_estado: EstadoSolicitud) -> bool:
        """
        Valida si una transición entre estados es permitida
        """
        return nuevo_estado in EstadoTransiciones.TRANSICIONES_PERMITIDAS.get(estado_actual, [])

    @staticmethod
    def obtener_transiciones_posibles(estado_actual: EstadoSolicitud) -> List[EstadoSolicitud]:
        """
        Obtiene los estados a los que se puede transicionar desde el estado actual
        """
        return EstadoTransiciones.TRANSICIONES_PERMITIDAS.get(estado_actual, [])

    @staticmethod
    def registrar_transicion(
        solicitud_id: int,
        nuevo_estado: EstadoSolicitud,
        usuario_id: int,
        motivo: str,
        fecha: Optional[datetime] = None
    ):
        """
        Registra una transición de estado en el historial
        """
        from app.models.historial_solicitud import HistorialSolicitud
        from app import db
        
        if not fecha:
            fecha = datetime.utcnow()
            
        historial = HistorialSolicitud(
            solicitud_id=solicitud_id,
            estado=nuevo_estado,
            usuario_id=usuario_id,
            motivo=motivo,
            fecha_cambio=fecha
        )
        db.session.add(historial)
        db.session.commit()
        return historial

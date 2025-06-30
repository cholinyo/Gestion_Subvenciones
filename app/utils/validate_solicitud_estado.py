# Gestion_Subvenciones/app/utils/validate_solicitud_estado.py

from app.models.solicitud_subvencion import EstadoSolicitud
from flask import request
from datetime import datetime
from .estado_transiciones import EstadoTransiciones

def validate_solicitud_estado(solicitud, estado_anterior=None, usuario_id=None, motivo_transicion=None):
    """
    Valida que la instancia de SolicitudSubvencion cumpla las reglas de negocio
    según el estado al que se desea transicionar.

    :param solicitud: Instancia de SolicitudSubvencion con valores actualizados
    :param estado_anterior: Estado previo (Enum) de la solicitud
    :param usuario_id: ID del usuario que realiza la transición
    :param motivo_transicion: Motivo de la transición de estado
    :raises ValueError: Si la transición o los campos obligatorios no son válidos
    """

    estado_actual = solicitud.estado

    # Validación de tipo de estado
    if not isinstance(estado_actual, EstadoSolicitud):
        raise ValueError(f"Estado inválido: {estado_actual}. El valor no corresponde con un estado permitido.")

    # Validación de transición
    if estado_anterior and estado_anterior != estado_actual:
        if not EstadoTransiciones.validar_transicion(estado_anterior, estado_actual):
            raise ValueError(f"Transición no permitida: de {estado_anterior.value} a {estado_actual.value}")

    # Validación genérica
    if not solicitud.fecha_limite_presentacion:
        raise ValueError("La fecha límite de presentación es obligatoria.")

    # Validaciones específicas por estado
    if estado_actual == EstadoSolicitud.SOLICITADA:
        validar_estado_solicitada(solicitud)
    elif estado_actual == EstadoSolicitud.NO_SOLICITADA:
        validar_estado_no_solicitada(solicitud)
    elif estado_actual == EstadoSolicitud.ALEGACIONES:
        validar_estado_alegaciones(solicitud)
    elif estado_actual == EstadoSolicitud.CONCEDIDA_PROVISIONAL:
        validar_estado_concedida_provisional(solicitud)
    elif estado_actual == EstadoSolicitud.CONCEDIDA:
        validar_estado_concedida(solicitud)
    elif estado_actual == EstadoSolicitud.DENEGADA:
        validar_estado_denegada(solicitud)

    # Registrar transición si hay cambio de estado
    if estado_anterior and estado_anterior != estado_actual:
        EstadoTransiciones.registrar_transicion(
            solicitud_id=solicitud.id,
            nuevo_estado=estado_actual,
            usuario_id=usuario_id,
            motivo=motivo_transicion
        )

def validar_estado_solicitada(solicitud):
    """Validaciones específicas para el estado SOLICITADA"""
    if not solicitud.fecha_presentacion_solicitud:
        raise ValueError("Debe indicarse la fecha de presentación para el estado 'solicitada'.")
    
    if solicitud.fecha_presentacion_solicitud > solicitud.fecha_limite_presentacion:
        raise ValueError("La fecha de presentación no puede ser posterior a la fecha límite.")
    
    if not all([
        solicitud.doc_inicio_expediente,
        solicitud.doc_informe_tecnico,
        solicitud.doc_propuesta_jgl,
        solicitud.doc_ficha_captacion
    ]):
        raise ValueError("No se puede marcar como 'solicitada' si no están todos los documentos obligatorios completados.")
    
    if solicitud.importe_total is None:
        raise ValueError("Debe indicarse el importe total del proyecto para el estado 'solicitada'.")
    if solicitud.importe_subvencionado is None:
        raise ValueError("Debe indicarse el importe subvencionado para el estado 'solicitada'.")
    if solicitud.fondos_propios is None:
        raise ValueError("Debe indicarse el importe de los fondos propios para el estado 'solicitada'.")
    
    # Validación de consistencia financiera
    if solicitud.importe_total < solicitud.importe_subvencionado + solicitud.fondos_propios:
        raise ValueError("La suma de importe subvencionado y fondos propios debe ser menor o igual al importe total.")

def validar_estado_no_solicitada(solicitud):
    """Validaciones específicas para el estado NO_SOLICITADA"""
    if not solicitud.motivo_no_solicitada:
        raise ValueError("Debe especificarse el motivo por el cual no se ha solicitado la subvención.")

def validar_estado_alegaciones(solicitud):
    """Validaciones específicas para el estado ALEGACIONES"""
    if not solicitud.fecha_presentacion_solicitud:
        raise ValueError("Debe indicarse la fecha de presentación para el estado 'alegaciones'.")
    
    if not solicitud.fecha_resolucion_provisional:
        raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'alegaciones'.")

def validar_estado_concedida_provisional(solicitud):
    """Validaciones específicas para el estado CONCEDIDA_PROVISIONAL"""
    if not solicitud.fecha_presentacion_solicitud:
        raise ValueError("Debe indicarse la fecha de presentación para el estado 'concedida_provisional'.")
    if not solicitud.fecha_resolucion_provisional:
        raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'concedida_provisional'.")

def validar_estado_concedida(solicitud):
    """Validaciones específicas para el estado CONCEDIDA"""
    if not solicitud.fecha_presentacion_solicitud:
        raise ValueError("Debe indicarse la fecha de presentación para el estado 'concedida'.")
    if not solicitud.fecha_resolucion_provisional:
        raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'concedida'.")
    if not solicitud.fecha_resolucion_definitiva:
        raise ValueError("Debe indicarse la fecha de resolución definitiva para el estado 'concedida'.")

def validar_estado_denegada(solicitud):
    """Validaciones específicas para el estado DENEGADA"""
    if not solicitud.fecha_presentacion_solicitud:
        raise ValueError("Debe indicarse la fecha de presentación para el estado 'denegada'.")
    if not solicitud.fecha_resolucion_provisional:
        raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'denegada'.")
    if not solicitud.fecha_resolucion_definitiva:
        raise ValueError("Debe indicarse la fecha de resolución definitiva para el estado 'denegada'.")
    if not solicitud.motivo_denegada:
        raise ValueError("Debe indicarse el motivo de denegación para el estado 'denegada'.")
            raise ValueError("Debe indicarse la fecha de presentación para continuar con el estado 'concedida provisional'.")
        if not solicitud.fecha_resolucion_provisional:
            raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'concedida provisional'.")

    elif estado_actual == EstadoSolicitud.CONCEDIDA:
        if estado_anterior not in (
            EstadoSolicitud.SOLICITADA,
            EstadoSolicitud.ALEGACIONES,
            EstadoSolicitud.CONCEDIDA_PROVISIONAL
        ):
            raise ValueError("Solo se puede conceder una solicitud desde 'solicitada', 'alegaciones' o 'concedida provisionalmente'.")
        if not solicitud.fecha_presentacion_solicitud:
            raise ValueError("Debe indicarse la fecha de presentación para continuar con el estado 'concedida'.")
        if not solicitud.fecha_resolucion_definitiva:
            raise ValueError("Debe indicarse la fecha de resolución definitiva para el estado 'concedida'.")

    elif estado_actual == EstadoSolicitud.DENEGADA:
        if estado_anterior != EstadoSolicitud.SOLICITADA:
            raise ValueError("Solo se puede denegar una solicitud que haya sido previamente marcada como 'solicitada'.")
        if not solicitud.fecha_presentacion_solicitud:
            raise ValueError("Debe indicarse la fecha de presentación para continuar con el estado 'denegada'.")
        if not solicitud.fecha_resolucion_provisional:
            raise ValueError("Debe indicarse la fecha de resolución provisional para el estado 'denegada'.")
        if not solicitud.fecha_resolucion_definitiva:
            raise ValueError("Debe indicarse la fecha de resolución definitiva para el estado 'denegada'.")
        if not solicitud.motivo_denegada:
            raise ValueError("Debe especificarse el motivo de denegación para marcar la solicitud como 'denegada'.")

    elif estado_actual == EstadoSolicitud.ALEGACIONES:
        if not solicitud.fecha_presentacion_solicitud:
            raise ValueError("Debe indicarse la fecha de presentación para continuar con el estado 'alegaciones'.")

    elif estado_actual == EstadoSolicitud.EN_TRAMITE:
        pass  # No requiere validación adicional

    else:
        raise ValueError(f"Transición a estado '{estado_actual}' no contemplada explícitamente.")

    # Validación final: ¿el estado requiere bloqueo?
    if estado_actual in [EstadoSolicitud.CONCEDIDA, EstadoSolicitud.DENEGADA, EstadoSolicitud.NO_SOLICITADA]:
        solicitud.bloqueada = True  # Este atributo debe existir en el modelo y reflejarse en la lógica de la app


def parse_float(field_name):
    """
    Intenta convertir el valor de un campo de formulario a float.
    Devuelve None si el campo está vacío o no es un número válido.
    """
    valor = request.form.get(field_name)
    try:
        return float(valor) if valor.strip() != "" else None
    except (ValueError, TypeError):
        return None

# utils/validate_solicitud_estado.py
from app.models.solicitud_subvencion import EstadoSolicitud
from flask import request
from datetime import datetime



def validate_solicitud_estado(solicitud, nuevo_estado):
    errores = []

    # Siempre requeridos
    if not solicitud.expediente_opensea:
        errores.append("El campo expediente_opensea es obligatorio.")
    if not solicitud.expediente_subvencion:
        errores.append("El campo expediente_subvencion es obligatorio.")
    if not solicitud.entidad_id:
        errores.append("Debe especificarse una entidad.")
    if not solicitud.concepto:
        errores.append("El concepto es obligatorio.")
    if not solicitud.tipo_fondo:
        errores.append("El tipo de fondo es obligatorio.")

    
    #Se reuiere fecha de solicitu cuando para a solicitada
    if nuevo_estado == EstadoSolicitud.SOLICITADA and not solicitud.fecha_presentacion_solicitud:
        errores.append("La fecha de presentación de la solicitud es obligatoria en estado 'solicitada'.")

    # Requiere campos económicos en todos excepto no_solicitada
    if nuevo_estado != EstadoSolicitud.NO_SOLICITADA:
        if solicitud.importe_total is None:
            errores.append("El importe total del proyecto es obligatorio.")
        if solicitud.importe_subvencionado is None:
            errores.append("El importe subvencionado es obligatorio.")
        if solicitud.fondos_propios is None:
            errores.append("El importe de fondos propios es obligatorio.")
    else:
        if not solicitud.motivo_no_solicitada:
            errores.append("Debe indicar el motivo por el cual no se ha solicitado.")

    # Requiere documentación completa en estados críticos
    if nuevo_estado in [
        EstadoSolicitud.SOLICITADA,
        EstadoSolicitud.CONCEDIDA,
        EstadoSolicitud.CONCEDIDA_PROVISIONAL,
        EstadoSolicitud.DENEGADA,
        EstadoSolicitud.ALEGACIONES,
    ]:
        if not all([
            solicitud.doc_inicio_expediente,
            solicitud.doc_informe_tecnico,
            solicitud.doc_propuesta_jgl,
            solicitud.doc_ficha_captacion
        ]):
            errores.append("Debe marcarse toda la documentación requerida para este estado.")

    # Control de flujo: no se puede pasar a resolutivos sin haber estado en 'solicitada'
    if nuevo_estado in [
        EstadoSolicitud.CONCEDIDA_PROVISIONAL,
        EstadoSolicitud.CONCEDIDA,
        EstadoSolicitud.DENEGADA
    ]:
        if solicitud.estado != EstadoSolicitud.SOLICITADA:
            errores.append(f"No se puede pasar de '{solicitud.estado.value}' a '{nuevo_estado.value}'. Debe pasar antes por 'solicitada'.")

    return errores


def parse_float(field_name):
    valor = request.form.get(field_name)
    try:
        return float(valor) if valor.strip() != "" else None
    except (ValueError, TypeError):
        return None


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.models.solicitud_subvencion import SolicitudSubvencion
from app.models.observacion_solicitud import ObservacionSolicitud
from app.models.solicitud_subvencion import EstadoSolicitud
from app.utils.historial import registrar_historial
from app.utils.validate_solicitud_estado import parse_float, validate_solicitud_estado
from datetime import datetime


solicitudes_bp = Blueprint("solicitudes", __name__)

def parse_fecha(nombre_campo):
    valor = request.form.get(nombre_campo)
    return datetime.strptime(valor, "%Y-%m-%d").date() if valor else None

@solicitudes_bp.route("/solicitud/<int:solicitud_id>/editar", methods=["GET", "POST"])
@login_required
def editar_solicitud(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)

    estados_bloqueados = ["concedida", "denegada", "no_solicitada"]
    readonly = solicitud.estado.value in estados_bloqueados

    if request.method == "POST" and not readonly:
        solicitud.expediente_opensea = request.form.get("expediente_opensea")
        solicitud.expediente_subvencion = request.form.get("expediente_subvencion")
        solicitud.entidad_id = request.form.get("entidad_id")
        solicitud.concepto = request.form.get("concepto")
        solicitud.tipo_fondo = request.form.get("tipo_fondo")

        solicitud.importe_total = parse_float("importe_total")
        solicitud.importe_subvencionado = parse_float("importe_subvencionado")
        solicitud.fondos_propios = parse_float("fondos_propios")

        solicitud.doc_inicio_expediente = 'doc_inicio_expediente' in request.form
        solicitud.doc_informe_tecnico = 'doc_informe_tecnico' in request.form
        solicitud.doc_propuesta_jgl = 'doc_propuesta_jgl' in request.form
        solicitud.doc_ficha_captacion = 'doc_ficha_captacion' in request.form

        solicitud.fecha_limite_presentacion = parse_fecha("fecha_limite_presentacion")
        solicitud.fecha_presentacion_solicitud = parse_fecha("fecha_presentacion_solicitud")
        solicitud.fecha_resolucion_provisional = parse_fecha("fecha_resolucion_provisional")
        solicitud.fecha_resolucion_definitiva = parse_fecha("fecha_resolucion_definitiva")

        solicitud.gestor_responsable = request.form.get("gestor_responsable")
        solicitud.email_gestor = request.form.get("email_gestor")

        solicitud.motivo_no_solicitada = request.form.get("motivo_no_solicitada")
        solicitud.motivo_denegada = request.form.get("motivo_denegada")

        nuevo_estado_str = request.form.get("estado")
        if nuevo_estado_str:
            try:
                nuevo_estado = EstadoSolicitud(nuevo_estado_str)
                estado_anterior = solicitud.estado
                solicitud.estado = nuevo_estado

                validate_solicitud_estado(solicitud, estado_anterior=estado_anterior)

                if nuevo_estado != estado_anterior:
                    descripcion = f"Estado cambiado de {estado_anterior.value} a {nuevo_estado.value}"
                    registrar_historial(solicitud, current_user, descripcion)

            except ValueError as e:
                solicitud.estado = estado_anterior  # Revertir si falla
                flash(str(e), "danger")
                return render_template("solicitudes/editar.html", solicitud=solicitud, ObservacionSolicitud=ObservacionSolicitud)

        texto_observacion = request.form.get("observaciones")
        if texto_observacion:
            nueva_obs = ObservacionSolicitud(
                solicitud_id=solicitud.id,
                usuario_id=current_user.id,
                texto=texto_observacion,
                fecha=datetime.utcnow()
            )
            db.session.add(nueva_obs)

        db.session.commit()
        flash("Solicitud actualizada correctamente.", "success")
        return redirect(url_for("solicitudes.ver_solicitud", solicitud_id=solicitud.id))

    return render_template("solicitudes/editar.html", solicitud=solicitud, ObservacionSolicitud=ObservacionSolicitud)


@solicitudes_bp.route("/solicitudes")
@login_required
def lista_solicitudes():
    estado_filtrado = request.args.get("estado")
    if estado_filtrado:
        solicitudes = SolicitudSubvencion.query.filter_by(estado=estado_filtrado).all()
    else:
        solicitudes = SolicitudSubvencion.query.all()

    return render_template("solicitudes/lista.html", solicitudes=solicitudes, estado_filtrado=estado_filtrado)


@solicitudes_bp.route("/solicitud/nueva", methods=["GET", "POST"])
@login_required
def nueva_solicitud():
    if request.method == "POST":
        estado = request.form.get("estado")
        motivo_no_solicitada = request.form.get("motivo_no_solicitada")
        fecha_limite = parse_fecha("fecha_limite_presentacion")

        # Validación de campos obligatorios
        if not fecha_limite:
            flash("Debes indicar la fecha límite de presentación.", "danger")
            return render_template("solicitudes/nueva.html")

        if estado == "no_solicitada" and not motivo_no_solicitada:
            flash("Debes indicar el motivo por el que no se ha solicitado.", "danger")
            return render_template("solicitudes/nueva.html")

        solicitud = SolicitudSubvencion(
            expediente_opensea=request.form.get("expediente_opensea"),
            expediente_subvencion=request.form.get("expediente_subvencion"),
            entidad_id=request.form.get("entidad_id"),
            concepto=request.form.get("concepto"),
            tipo_fondo=request.form.get("tipo_fondo"),
            gestor_responsable=current_user.username,
            email_gestor=current_user.email,
            fecha_limite_presentacion=fecha_limite,
            motivo_no_solicitada=motivo_no_solicitada,
            estado=EstadoSolicitud(estado) if estado else EstadoSolicitud.EN_TRAMITE
        )

        # Guardamos solo si supera las validaciones
        db.session.add(solicitud)
        db.session.commit()
        flash("Solicitud creada correctamente.", "success")
        return redirect(url_for("solicitudes.editar_solicitud", solicitud_id=solicitud.id))

    return render_template("solicitudes/nueva.html")


@solicitudes_bp.route("/solicitud/<int:solicitud_id>")
@login_required
def ver_solicitud(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)
    historial = solicitud.historial  # Si tienes relación `historial = db.relationship(...)`

    return render_template(
        "solicitudes/ver.html",
        solicitud=solicitud,
        historial=historial,
        ObservacionSolicitud=ObservacionSolicitud
    )


@solicitudes_bp.route("/solicitud/<int:solicitud_id>/observacion", methods=["POST"])
@login_required
def añadir_observacion(solicitud_id):
    solicitud = SolicitudSubvencion.query.get_or_404(solicitud_id)
    texto = request.form.get("observacion", "").strip()

    if not texto:
        flash("La observación no puede estar vacía.", "warning")
        return redirect(url_for("solicitudes.ver", solicitud_id=solicitud.id))

    observacion = ObservacionSolicitud(
        solicitud_id=solicitud.id,
        usuario_id=current_user.id,
        texto=texto
    )

    db.session.add(observacion)
    db.session.commit()

    flash("Observación añadida correctamente.", "success")
    return redirect(url_for("solicitudes.ver", solicitud_id=solicitud.id))

